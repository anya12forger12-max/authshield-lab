"""Session service implementation."""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from ...shared.logging_config import get_logger
from ...config.constants import MODULE_AUTH
from ..domain.interfaces.event_publisher import IAuthenticationEventPublisher
from ..domain.interfaces.repository_interfaces import ISessionRepository
from ..domain.interfaces.session_service import ISessionService
from ..domain.models.response_models import SessionResponse

logger = get_logger(MODULE_AUTH)

# Default session timeout (minutes)
_DEFAULT_SESSION_TIMEOUT_MINUTES = 60
_DEFAULT_IDLE_TIMEOUT_MINUTES = 30


class SessionService(ISessionService):
    """Manages the full lifecycle of user sessions.

    Parameters
    ----------
    session_repository:
        Persistence layer for session records.
    event_publisher:
        Publishes session lifecycle events.
    session_timeout_minutes:
        Absolute session lifetime in minutes.
    idle_timeout_minutes:
        Idle timeout in minutes (renewed on activity).
    """

    def __init__(
        self,
        session_repository: ISessionRepository,
        event_publisher: IAuthenticationEventPublisher,
        session_timeout_minutes: int = _DEFAULT_SESSION_TIMEOUT_MINUTES,
        idle_timeout_minutes: int = _DEFAULT_IDLE_TIMEOUT_MINUTES,
    ) -> None:
        self._session_repo = session_repository
        self._event_publisher = event_publisher
        self._session_timeout = session_timeout_minutes
        self._idle_timeout = idle_timeout_minutes

    async def create_session(
        self, user_id: str, auth_method: str = "password", **kwargs: object
    ) -> str:
        """Create a new session for the given user.

        Generates a cryptographically secure session ID, stores the session
        record, and returns the session ID.

        Parameters
        ----------
        user_id:
            The ID of the user owning the session.
        auth_method:
            How the session was established.
        **kwargs:
            Optional context: ``device_id``, ``platform``.

        Returns
        -------
        str
            The newly created session ID.
        """
        now = datetime.now(timezone.utc)
        session_id = secrets.token_urlsafe(32)
        device_id = str(kwargs.get("device_id", "") or "")
        platform = str(kwargs.get("platform", "") or "")

        session_data: dict[str, Any] = {
            "session_id": session_id,
            "user_id": user_id,
            "status": "active",
            "authentication_method": auth_method,
            "created_at": now,
            "expires_at": now + timedelta(minutes=self._session_timeout),
            "last_activity": now,
            "device_id": device_id,
            "platform": platform,
        }

        await self._session_repo.create(session_data)

        logger.info(
            "session_created",
            session_id=session_id,
            user_id=user_id,
            auth_method=auth_method,
        )

        return session_id

    async def validate_session(self, session_id: str) -> bool:
        """Check whether a session exists, is not expired, and is usable.

        Parameters
        ----------
        session_id:
            The session token to validate.

        Returns
        -------
        bool
            True if the session is valid and active.
        """
        session = await self._session_repo.get_by_id(session_id)

        if session is None:
            return False

        status = self._get_field(session, "status")
        if status not in ("active", "idle"):
            return False

        expires_at = self._get_field(session, "expires_at")
        if isinstance(expires_at, datetime):
            if datetime.now(timezone.utc) > expires_at:
                await self._expire_session(session_id, self._get_field(session, "user_id"))
                return False

        last_activity = self._get_field(session, "last_activity")
        if isinstance(last_activity, datetime):
            idle_cutoff = datetime.now(timezone.utc) - timedelta(
                minutes=self._idle_timeout
            )
            if last_activity < idle_cutoff:
                return False

        return True

    async def renew_session(self, session_id: str) -> bool:
        """Extend the timeout of an active session.

        Parameters
        ----------
        session_id:
            The session to renew.

        Returns
        -------
        bool
            True if the session was found and renewed.
        """
        session = await self._session_repo.get_by_id(session_id)

        if session is None:
            return False

        status = self._get_field(session, "status")
        if status not in ("active", "idle"):
            return False

        now = datetime.now(timezone.utc)
        update_data: dict[str, Any] = {
            "last_activity": now,
            "expires_at": now + timedelta(minutes=self._session_timeout),
            "status": "active",
        }

        await self._session_repo.update(session_id, update_data)

        logger.debug("session_renewed", session_id=session_id)
        return True

    async def terminate_session(self, session_id: str) -> bool:
        """Terminate (revoke) a single session.

        Parameters
        ----------
        session_id:
            The session to terminate.

        Returns
        -------
        bool
            True if the session was found and terminated.
        """
        session = await self._session_repo.get_by_id(session_id)

        if session is None:
            return False

        user_id = self._get_field(session, "user_id")
        await self._session_repo.update(session_id, {"status": "revoked"})

        await self._event_publisher.publish_session_destroyed(session_id, str(user_id))

        logger.info("session_terminated", session_id=session_id, user_id=user_id)
        return True

    async def terminate_all_user_sessions(self, user_id: str) -> int:
        """Terminate all active sessions for a user.

        Parameters
        ----------
        user_id:
            The user whose sessions should be terminated.

        Returns
        -------
        int
            The number of sessions terminated.
        """
        active_sessions = await self._session_repo.get_active_by_user(user_id)
        count = 0

        for session in active_sessions:
            session_id = self._get_field(session, "session_id") or self._get_field(session, "id")
            if session_id:
                await self._session_repo.update(str(session_id), {"status": "revoked"})
                await self._event_publisher.publish_session_destroyed(
                    str(session_id), user_id
                )
                count += 1

        if count > 0:
            logger.info(
                "all_sessions_terminated",
                user_id=user_id,
                count=count,
            )

        return count

    async def get_user_sessions(
        self, user_id: str, include_expired: bool = False
    ) -> list[SessionResponse]:
        """Return session information for a user.

        Parameters
        ----------
        user_id:
            The user whose sessions to retrieve.
        include_expired:
            When True, include expired/revoked sessions.

        Returns
        -------
        list[SessionResponse]
        """
        sessions = await self._session_repo.get_active_by_user(user_id)
        result: list[SessionResponse] = []

        for session in sessions:
            status = self._get_field(session, "status")

            if not include_expired and status not in ("active", "idle"):
                continue

            session_id = str(self._get_field(session, "session_id") or self._get_field(session, "id") or "")
            created_at = self._get_field(session, "created_at") or datetime.now(timezone.utc)
            expires_at = self._get_field(session, "expires_at") or datetime.now(timezone.utc)
            last_activity = self._get_field(session, "last_activity") or datetime.now(timezone.utc)

            result.append(
                SessionResponse(
                    session_id=session_id,
                    user_id=user_id,
                    created_at=created_at,
                    expires_at=expires_at,
                    last_activity=last_activity,
                    status=status or "unknown",
                    authentication_method=self._get_field(session, "authentication_method"),
                    platform=self._get_field(session, "platform"),
                    is_current=False,
                )
            )

        return result

    async def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions and return the count removed.

        Returns
        -------
        int
            The number of expired sessions deleted.
        """
        count = await self._session_repo.delete_expired()

        if count > 0:
            logger.info("expired_sessions_cleaned", count=count)

        return count

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def _expire_session(self, session_id: str, user_id: str | None) -> None:
        """Mark a session as expired and publish the event."""
        await self._session_repo.update(session_id, {"status": "expired"})

        await self._event_publisher.publish_session_expired(
            session_id, str(user_id) if user_id else ""
        )

    @staticmethod
    def _get_field(obj: Any, field_name: str) -> Any:  # noqa: ANN401
        """Extract a field from either an ORM model or a dict."""
        if isinstance(obj, dict):
            return obj.get(field_name)
        return getattr(obj, field_name, None)
