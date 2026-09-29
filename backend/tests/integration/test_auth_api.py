"""End-to-end HTTP tests for the authentication API.

Every other auth test in this suite stops at the Pydantic layer: no test
constructed a real service or issued an HTTP request. That blind spot is why a
fully non-functional auth stack shipped green —

* ``configure_dependencies()`` was never called, so all 10 ``/api/v1/auth/*``
  routes answered **503 "… service not configured."**;
* ``RegistrationService`` wrote ``hashed_password``/``status``, which do not
  exist on the ``User`` model, so a register request returned **500**;
* ``LoginService`` called ``.get()`` on an ORM object, so login returned an
  unhandled **500**.

These tests drive the real router through ``TestClient`` so any of those
regressions fails loudly.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.authentication.api.routes import configure_dependencies
from app.authentication.events.event_publisher import AuthenticationEventPublisher
from app.authentication.repositories.authentication_repository_impl import (
    InMemorySessionRepository,
    InMemoryUserRepository,
)
from app.authentication.services.authentication_service import AuthenticationService
from app.authentication.services.login_service import LoginService
from app.authentication.services.logout_service import LogoutService
from app.authentication.services.password_policy_service import PasswordPolicyService
from app.authentication.services.password_verification_service import (
    PasswordVerificationService,
)
from app.authentication.services.registration_service import RegistrationService
from app.authentication.services.session_service import SessionService
from app.main import app

PASSWORD = "Str0ng!Passw0rd#2026"
REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"


@pytest.fixture(autouse=True)
def auth_services():
    """Wire real services over fresh in-memory repositories.

    Uses the router's own ``configure_dependencies`` seam, so the tests exercise
    the production wiring path and get full isolation between tests. Against the
    pre-fix code this fixture cannot even be reached, because the routes answer
    503 with no services wired at all.
    """
    user_repo = InMemoryUserRepository()
    publisher = AuthenticationEventPublisher()
    session_service = SessionService(InMemorySessionRepository(), publisher)
    hasher = PasswordVerificationService()
    policy = PasswordPolicyService()

    configure_dependencies(
        AuthenticationService(
            LoginService(user_repo, hasher, session_service, publisher),
            LogoutService(session_service, publisher),
            session_service,
        ),
        RegistrationService(user_repo, hasher, policy, publisher),
        policy,
    )
    yield
    configure_dependencies(None, None, None)


@pytest.fixture
def client():
    """A client with the application lifespan intentionally skipped.

    ``TestClient(app)`` is deliberately NOT used as a context manager: entering
    it would run the lifespan and open the SQLite database, which these
    in-memory auth tests do not need.
    """
    return TestClient(app)


def _payload(**overrides: object) -> dict:
    payload: dict = {
        "username": "alice",
        "password": PASSWORD,
        "confirm_password": PASSWORD,
        "display_name": "Alice Example",
        "email": "alice@example.com",
        "privacy_policy_accepted": True,
    }
    payload.update(overrides)
    return payload


class TestRegisterEndpoint:
    def test_register_returns_201(self, client):
        response = client.post(REGISTER_URL, json=_payload())

        assert response.status_code == 201, response.text
        assert response.json()["data"]["username"] == "alice"
        assert response.json()["data"]["user_id"]

    def test_register_is_not_503(self, client):
        """Regression: every auth route used to answer 503 (unwired DI)."""
        assert client.post(REGISTER_URL, json=_payload()).status_code != 503

    def test_register_is_not_500(self, client):
        """Regression: ``hashed_password`` key made the insert raise TypeError."""
        assert client.post(REGISTER_URL, json=_payload()).status_code != 500

    def test_duplicate_username_returns_409(self, client):
        client.post(REGISTER_URL, json=_payload())

        response = client.post(REGISTER_URL, json=_payload(email="other@example.com"))

        assert response.status_code == 409
        assert response.json()["detail"]["error_code"] == "USERNAME_TAKEN"

    def test_duplicate_email_returns_409(self, client):
        client.post(REGISTER_URL, json=_payload())

        response = client.post(REGISTER_URL, json=_payload(username="bobby"))

        assert response.status_code == 409
        assert response.json()["detail"]["error_code"] == "EMAIL_TAKEN"

    def test_privacy_policy_must_be_accepted(self, client):
        response = client.post(REGISTER_URL, json=_payload(privacy_policy_accepted=False))

        assert response.status_code == 400
        assert response.json()["detail"]["error_code"] == "PRIVACY_POLICY_NOT_ACCEPTED"

    def test_missing_privacy_policy_field_is_422(self, client):
        payload = _payload()
        del payload["privacy_policy_accepted"]

        assert client.post(REGISTER_URL, json=payload).status_code == 422

    def test_weak_password_returns_422(self, client):
        # Passes the Pydantic 8-char floor, fails the real policy.
        response = client.post(
            REGISTER_URL, json=_payload(password="weakpass1", confirm_password="weakpass1")
        )

        assert response.status_code == 422
        assert response.json()["detail"]["error_code"] == "PASSWORD_POLICY_VIOLATION"

    def test_password_mismatch_returns_400(self, client):
        response = client.post(
            REGISTER_URL, json=_payload(confirm_password="Different!Passw0rd#2026")
        )

        assert response.status_code == 400
        assert response.json()["detail"]["error_code"] == "PASSWORD_MISMATCH"

    def test_username_availability_endpoint(self, client):
        free = client.get(f"{REGISTER_URL}/check-username/nobody")
        assert free.json()["data"]["available"] is True

        client.post(REGISTER_URL, json=_payload())

        taken = client.get(f"{REGISTER_URL}/check-username/alice")
        assert taken.json()["data"]["available"] is False

    def test_email_availability_endpoint(self, client):
        free = client.get(f"{REGISTER_URL}/check-email/free@example.com")
        assert free.json()["data"]["available"] is True

        client.post(REGISTER_URL, json=_payload())

        taken = client.get(f"{REGISTER_URL}/check-email/alice@example.com")
        assert taken.json()["data"]["available"] is False


class TestLoginEndpoint:
    def test_login_after_register_returns_200(self, client):
        """The core flow that did not work at all before this fix."""
        client.post(REGISTER_URL, json=_payload())

        response = client.post(LOGIN_URL, json={"username": "alice", "password": PASSWORD})

        assert response.status_code == 200, response.text
        data = response.json()["data"]
        assert data["session_id"]
        assert data["user"]["username"] == "alice"

    def test_login_is_not_503(self, client):
        client.post(REGISTER_URL, json=_payload())

        response = client.post(LOGIN_URL, json={"username": "alice", "password": PASSWORD})
        assert response.status_code != 503

    def test_login_is_not_500(self, client):
        """Regression: ``.get()`` on an ORM user raised AttributeError."""
        client.post(REGISTER_URL, json=_payload())

        response = client.post(LOGIN_URL, json={"username": "alice", "password": PASSWORD})

        assert response.status_code != 500

    def test_unknown_user_returns_401(self, client):
        response = client.post(LOGIN_URL, json={"username": "ghost", "password": PASSWORD})

        assert response.status_code == 401
        assert response.json()["detail"]["error_code"] == "INVALID_CREDENTIALS"

    def test_wrong_password_returns_401(self, client):
        client.post(REGISTER_URL, json=_payload())

        response = client.post(
            LOGIN_URL, json={"username": "alice", "password": "Wr0ng!Passw0rd#2026"}
        )

        assert response.status_code == 401
        assert response.json()["detail"]["error_code"] == "INVALID_CREDENTIALS"

    def test_missing_credentials_return_422(self, client):
        assert client.post(LOGIN_URL, json={}).status_code == 422

    def test_session_is_usable_after_login(self, client):
        client.post(REGISTER_URL, json=_payload())
        session_id = client.post(
            LOGIN_URL, json={"username": "alice", "password": PASSWORD}
        ).json()["data"]["session_id"]

        response = client.post("/api/v1/auth/session/validate", json={"session_id": session_id})

        assert response.status_code == 200
        assert response.json()["data"]["success"] is True


class TestPasswordEndpoints:
    def test_policy_endpoint_is_served(self, client):
        response = client.get("/api/v1/auth/password/policy")

        assert response.status_code == 200
        assert response.json()["data"]["min_length"] == 12
