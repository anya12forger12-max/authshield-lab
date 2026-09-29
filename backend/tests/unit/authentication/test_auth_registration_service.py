"""Tests for :class:`RegistrationService` against the real repositories.

These tests deliberately avoid ``MagicMock`` repositories. A mock fabricates
any attribute on demand, so the original defects (a ``user_data`` dict keyed on
``hashed_password`` / ``status`` instead of the model's ``password_hash`` /
``account_status``) were invisible to the suite. Here a key mismatch is a hard
failure because the service is exercised against the real in-memory repository
*and* a real SQLAlchemy ``User`` instance.
"""

from __future__ import annotations

import pytest

from app.authentication.domain.entities.authentication_result import (
    AuthenticationOutcome,
    FailureReason,
)
from app.authentication.domain.models.request_models import RegistrationRequest
from app.authentication.events.event_publisher import AuthenticationEventPublisher
from app.authentication.repositories.authentication_repository_impl import (
    InMemoryUserRepository,
)
from app.authentication.services.password_policy_service import PasswordPolicyService
from app.authentication.services.password_verification_service import (
    PasswordVerificationService,
)
from app.authentication.services.registration_service import RegistrationService
from app.shared.models.user import User

STRONG_PASSWORD = "Str0ng!Passw0rd#2026"


@pytest.fixture
def user_repo() -> InMemoryUserRepository:
    return InMemoryUserRepository()


@pytest.fixture
def service(user_repo: InMemoryUserRepository) -> RegistrationService:
    return RegistrationService(
        user_repo,
        PasswordVerificationService(),
        PasswordPolicyService(),
        AuthenticationEventPublisher(),
    )


def _payload(**overrides: object) -> dict:
    payload: dict = {
        "username": "alice",
        "password": STRONG_PASSWORD,
        "confirm_password": STRONG_PASSWORD,
        "display_name": "Alice Example",
        "email": "alice@example.com",
        "privacy_policy_accepted": True,
    }
    payload.update(overrides)
    return payload


class TestRegistrationSuccess:
    async def test_registers_new_user(self, service):
        result = await service.register(RegistrationRequest(**_payload()))

        assert result.outcome is AuthenticationOutcome.SUCCESS
        assert result.username == "alice"
        assert result.user_id

    async def test_persists_user_with_model_column_names(self, service, user_repo):
        """Regression: the service must key on the real ``User`` columns.

        The previous ``hashed_password`` / ``status`` keys raised
        ``TypeError: 'hashed_password' is an invalid keyword argument for User``
        against ``BaseRepository`` and surfaced as HTTP 500.
        """
        await service.register(RegistrationRequest(**_payload()))

        stored = await user_repo.get_by_username("alice")
        assert stored is not None
        assert stored["password_hash"].startswith("$argon2id$")
        assert stored["account_status"] == "active"
        assert stored["display_name"] == "Alice Example"
        assert stored["email"] == "alice@example.com"
        assert "hashed_password" not in stored
        assert "status" not in stored

    async def test_creates_record_acceptable_by_the_orm_model(self, service, user_repo):
        """The stored mapping must instantiate the real SQLAlchemy model."""
        await service.register(RegistrationRequest(**_payload()))

        stored = await user_repo.get_by_username("alice")
        # Same failure mode as BaseRepository.create() -> self._model(**data)
        orm_user = User(**stored)

        assert orm_user.username == "alice"
        assert orm_user.password_hash.startswith("$argon2id$")
        assert orm_user.account_status == "active"

    async def test_stores_password_hash_not_plaintext(self, service, user_repo):
        await service.register(RegistrationRequest(**_payload()))

        stored = await user_repo.get_by_username("alice")
        assert STRONG_PASSWORD not in stored["password_hash"]

    async def test_round_trips_into_login_service(self, service, user_repo):
        """The hash written here must be verifiable by the hashing service."""
        await service.register(RegistrationRequest(**_payload()))

        stored = await user_repo.get_by_username("alice")
        assert await PasswordVerificationService().verify_password(
            STRONG_PASSWORD, stored["password_hash"]
        )

    async def test_username_availability_reflects_registration(self, service):
        await service.register(RegistrationRequest(**_payload()))

        assert await service.check_username_availability("alice") is False
        assert await service.check_username_availability("nobody") is True

    async def test_email_availability_reflects_registration(self, service):
        await service.register(RegistrationRequest(**_payload()))

        assert await service.check_email_availability("alice@example.com") is False
        assert await service.check_email_availability("free@example.com") is True


class TestRegistrationFailures:
    async def test_rejects_missing_privacy_consent(self, service, user_repo):
        result = await service.register(
            RegistrationRequest(**_payload(privacy_policy_accepted=False))
        )

        assert result.outcome is AuthenticationOutcome.FAILURE
        assert result.error_code == "PRIVACY_POLICY_NOT_ACCEPTED"
        assert await user_repo.get_by_username("alice") is None

    async def test_rejects_password_mismatch(self, service, user_repo):
        result = await service.register(
            RegistrationRequest(**_payload(confirm_password="Different!Passw0rd#2026"))
        )

        assert result.error_code == "PASSWORD_MISMATCH"
        assert await user_repo.get_by_username("alice") is None

    async def test_rejects_weak_password_against_real_policy(self, service, user_repo):
        """Uses the production policy, not a local fake.

        ``weakpass1`` clears the Pydantic floor of 8 characters but violates the
        real ``PasswordPolicyService`` (needs >= 12 chars plus an uppercase and
        a special character). The previous suite defined its own permissive fake
        policy, so the enforced rules were never actually exercised.
        """
        result = await service.register(
            RegistrationRequest(**_payload(password="weakpass1", confirm_password="weakpass1"))
        )

        assert result.error_code == "PASSWORD_POLICY_VIOLATION"
        assert result.failure_reason is FailureReason.PASSWORD_POLICY_VIOLATION
        assert result.metadata["policy_errors"]
        assert await user_repo.get_by_username("alice") is None

    async def test_rejects_duplicate_username(self, service):
        await service.register(RegistrationRequest(**_payload()))

        result = await service.register(RegistrationRequest(**_payload(email="other@example.com")))

        assert result.error_code == "USERNAME_TAKEN"

    async def test_rejects_duplicate_email(self, service):
        await service.register(RegistrationRequest(**_payload()))

        result = await service.register(RegistrationRequest(**_payload(username="bobby")))

        assert result.error_code == "EMAIL_TAKEN"

    async def test_duplicate_username_is_case_insensitive(self, service):
        await service.register(RegistrationRequest(**_payload()))

        result = await service.register(RegistrationRequest(**_payload(username="ALICE")))

        assert result.error_code == "USERNAME_TAKEN"

    async def test_username_is_not_created_when_availability_check_passes_only(self, service):
        result = await service.register(RegistrationRequest(**_payload()))

        assert result.outcome is AuthenticationOutcome.SUCCESS
        assert await service.check_username_availability("alice") is False
