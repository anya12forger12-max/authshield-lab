"""Session management service interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..models.response_models import SessionResponse


class ISessionService(ABC):
    """Interface for user session lifecycle operations."""

    @abstractmethod
    async def create_session(
        self, user_id: str, auth_method: str = "password", **kwargs: object
    ) -> str:
        """Create a new session and return the session ID.

        Parameters
        ----------
        user_id:
            The ID of the user owning the session.
        auth_method:
            How the session was established (e.g. ``password``, ``token``).
        **kwargs:
            Additional context (device_id, platform, etc.).

        Returns
        -------
        str
            The newly created session ID.
        """
        ...

    @abstractmethod
    async def validate_session(self, session_id: str) -> bool:
        """Return True if the session exists, is not expired, and is usable."""
        ...

    @abstractmethod
    async def renew_session(self, session_id: str) -> bool:
        """Extend the timeout of an active session.

        Returns True on success, False if the session is not found or not renewable.
        """
        ...

    @abstractmethod
    async def terminate_session(self, session_id: str) -> bool:
        """Terminate (revoke) a single session.

        Returns True if the session was found and terminated.
        """
        ...

    @abstractmethod
    async def terminate_all_user_sessions(self, user_id: str) -> int:
        """Terminate all active sessions for a user.

        Returns the number of sessions terminated.
        """
        ...

    @abstractmethod
    async def get_user_sessions(
        self, user_id: str, include_expired: bool = False
    ) -> list[SessionResponse]:
        """Return session information for a user."""
        ...

    @abstractmethod
    async def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions and return the count removed."""
        ...
