"""Tests for :class:`LoginService` against the real repositories.

Two regressions are pinned here:

1. The service previously read fields as
   ``getattr(user, name, None) or user.get(name, default)``, which evaluates
   ``.get()`` whenever the object has no such attribute. Against a SQLAlchemy
   ``User`` this raised ``AttributeError: 'User' object has no attribute 'get'``
   on every login, before the password was even checked.
2. It read ``status`` / ``hashed_password`` / ``failed_login_attempts``, none of
   which exist on the model (``account_status`` / ``password_hash`` /
   ``failed_login_count``). The status check silently fell through to the
   ``"active"`` default and the lockout counter was never persisted.
"""

from __future__ import annotations

import pytest

from app.authentication.domain.entities.account_status import AccountStatus
from app.authentication.domain.entities.authentication_result import AuthenticationOutcome
from app.authentication.domain.models.request_models import LoginRequest, RegistrationRequest
from app.authentication.events.event_publisher import AuthenticationEventPublisher
from app.authentication.repositories.authentication_repository_impl import (
    InMemorySessionRepository,
    InMemoryUserRepository,
)
from app.authentication.services.login_service import LoginService
from app.authentication.services.password_policy_service import PasswordPolicyService
from app.authentication.services.password_verification_service import (
    PasswordVerificationService,
)
from app.authentication.services.registration_service import RegistrationService
from app.authentication.services.session_service import SessionService
from app.shared.models.user import User

PASSWORD = "Str0ng!Passw0rd#2026"


@pytest.fixture
def user_repo() -> InMemoryUserRepository:
    return InMemoryUserRepository()


@pytest.fixture
def session_repo() -> InMemorySessionRepository:
    return InMemorySessionRepository()


@pytest.fixture
async def registered(user_repo: InMemoryUserRepository) -> str:
    """Register a real user through the real RegistrationService."""
    service = RegistrationService(
        user_repo,
        PasswordVerificationService(),
        PasswordPolicyService(),
        AuthenticationEventPublisher(),
    )
    result = await service.register(
        RegistrationRequest(
            username="alice",
            password=PASSWORD,
            confirm_password=PASSWORD,
            display_name="Alice Example",
            email="alice@example.com",
            privacy_policy_accepted=True,
        )
    )
    assert result.outcome is AuthenticationOutcome.SUCCESS
    return str(result.user_id)


def _make_service(user_repo: InMemoryUserRepository, session_repo, max_attempts: int = 5):
    publisher = AuthenticationEventPublisher()
    session_service = SessionService(session_repo, publisher)
    return LoginService(
        user_repo, PasswordVerificationService(), session_service, publisher, max_attempts
    )


def _login(username: str = "alice", password: str = PASSWORD) -> LoginRequest:
    return LoginRequest(username=username, password=password)


class OrmShapedUserRepository(InMemoryUserRepository):
    """Returns real SQLAlchemy ``User`` instances instead of dicts.

    This is the container the production ``UserRepository`` hands back, and it
    is where the original ``getattr(user, name, None) or user.get(name, ...)``
    idiom raised ``AttributeError: 'User' object has no attribute 'get'``.
    """

    async def get_by_username(self, username: str):
        stored = await super().get_by_username(username)
        return User(**stored) if stored is not None else None

    async def get_by_id(self, user_id: str):
        stored = await super().get_by_id(user_id)
        return User(**stored) if stored is not None else None


@pytest.mark.usefixtures("registered")
class TestLoginSuccess:
    async def test_authenticates_registered_user(self, user_repo, session_repo):
        result = await _make_service(user_repo, session_repo).authenticate(_login())

        assert result.outcome is AuthenticationOutcome.SUCCESS
        assert result.username == "alice"
        assert result.session_id

    async def test_authenticates_against_a_sqlalchemy_user_instance(self, user_repo, session_repo):
        """Regression: ORM-shaped users must not crash field extraction.

        Before the fix the service read fields with
        ``getattr(user, name, None) or user.get(name, default)``. Against a
        SQLAlchemy ``User`` the attribute lookup misses, so Python evaluated
        ``.get()`` and every login died with
        ``AttributeError: 'User' object has no attribute 'get'`` before the
        password was ever checked.
        """
        orm_repo = OrmShapedUserRepository()
        await orm_repo.create((await user_repo.get_by_username("alice")) | {})

        result = await _make_service(orm_repo, session_repo).authenticate(_login())

        assert result.outcome is AuthenticationOutcome.SUCCESS
        assert result.session_id

    async def test_wrong_password_against_sqlalchemy_user_is_rejected_cleanly(
        self, user_repo, session_repo
    ):
        """Same regression on the failure path: a 401, never a 500."""
        orm_repo = OrmShapedUserRepository()
        await orm_repo.create((await user_repo.get_by_username("alice")) | {})

        result = await _make_service(orm_repo, session_repo).authenticate(
            _login(password="Wr0ng!Passw0rd#2026")
        )

        assert result.error_code == "INVALID_CREDENTIALS"

    async def test_locked_sqlalchemy_account_is_refused(self, user_repo, session_repo):
        """ORM path must honour account_status, not fall through to 'active'."""
        orm_repo = OrmShapedUserRepository()
        stored = await user_repo.get_by_username("alice")
        await orm_repo.create({**stored, "account_status": AccountStatus.LOCKED.value})

        result = await _make_service(orm_repo, session_repo).authenticate(_login())

        assert result.error_code == "ACCOUNT_LOCKED"
        assert result.session_id is None

    async def test_returns_display_name_in_metadata(self, user_repo, session_repo):
        result = await _make_service(user_repo, session_repo).authenticate(_login())

        assert result.metadata["display_name"] == "Alice Example"

    async def test_unknown_username_fails_cleanly(self, user_repo, session_repo):
        """Uniform failure: must not reveal that the username is unknown."""
        result = await _make_service(user_repo, session_repo).authenticate(
            _login(username="nobody")
        )

        assert result.outcome is AuthenticationOutcome.FAILURE
        assert result.error_code == "INVALID_CREDENTIALS"
        assert result.message == "Invalid username or password."


@pytest.mark.usefixtures("registered")
class TestLoginFailures:
    async def test_wrong_password_is_rejected(self, user_repo, session_repo):
        result = await _make_service(user_repo, session_repo).authenticate(
            _login(password="Wr0ng!Passw0rd#2026")
        )

        assert result.error_code == "INVALID_CREDENTIALS"

    async def test_wrong_password_increments_failed_login_count(self, user_repo, session_repo):
        service = _make_service(user_repo, session_repo)

        await service.authenticate(_login(password="Wr0ng!Passw0rd#2026"))

        stored = await user_repo.get_by_username("alice")
        assert stored["failed_login_count"] == 1

    async def test_successful_login_resets_failed_login_count(self, user_repo, session_repo):
        service = _make_service(user_repo, session_repo)
        await service.authenticate(_login(password="Wr0ng!Passw0rd#2026"))
        await service.authenticate(_login())

        stored = await user_repo.get_by_username("alice")
        assert stored["failed_login_count"] == 0

    async def test_account_locks_after_max_failed_attempts(self, user_repo, session_repo):
        """Regression: the lockout wrote ``status``/``failed_login_attempts``.

        ``BaseRepository.update`` filters unknown keys, so the counter never
        persisted and the account never locked.
        """
        service = _make_service(user_repo, session_repo, max_attempts=3)

        for _ in range(3):
            await service.authenticate(_login(password="Wr0ng!Passw0rd#2026"))

        stored = await user_repo.get_by_username("alice")
        assert stored["failed_login_count"] == 3
        assert stored["account_status"] == AccountStatus.LOCKED.value

    async def test_locked_account_cannot_log_in_even_with_correct_password(
        self, user_repo, session_repo
    ):
        service = _make_service(user_repo, session_repo, max_attempts=2)
        for _ in range(2):
            await service.authenticate(_login(password="Wr0ng!Passw0rd#2026"))

        result = await service.authenticate(_login())

        assert result.error_code == "ACCOUNT_LOCKED"
        assert result.session_id is None

    @pytest.mark.parametrize(
        ("status", "expected"),
        [
            (AccountStatus.DISABLED.value, "ACCOUNT_DISABLED"),
            (AccountStatus.SUSPENDED.value, "ACCOUNT_SUSPENDED"),
        ],
    )
    async def test_non_active_accounts_are_refused(self, user_repo, session_repo, status, expected):
        """Regression: the status check fell through to the ``"active"`` default."""
        stored = await user_repo.get_by_username("alice")
        await user_repo.update(stored["id"], {"account_status": status})

        result = await _make_service(user_repo, session_repo).authenticate(_login())

        assert result.error_code == expected
        assert result.session_id is None
