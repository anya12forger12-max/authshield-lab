"""Event publisher interface for authentication domain events."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..entities.authentication_result import AuthenticationResult


class IAuthenticationEventPublisher(ABC):
    """Interface for publishing authentication lifecycle events.

    Implementations translate domain-level actions into events dispatched
    through the shared event bus.
    """

    @abstractmethod
    async def publish_authentication_requested(
        self, username: str, correlation_id: str
    ) -> None:
        ...

    @abstractmethod
    async def publish_authentication_succeeded(
        self, result: AuthenticationResult
    ) -> None:
        ...

    @abstractmethod
    async def publish_authentication_failed(
        self, result: AuthenticationResult
    ) -> None:
        ...

    @abstractmethod
    async def publish_registration_requested(
        self, username: str, correlation_id: str
    ) -> None:
        ...

    @abstractmethod
    async def publish_registration_completed(
        self, result: AuthenticationResult
    ) -> None:
        ...

    @abstractmethod
    async def publish_session_created(
        self, session_id: str, user_id: str, correlation_id: str
    ) -> None:
        ...

    @abstractmethod
    async def publish_session_expired(self, session_id: str, user_id: str) -> None:
        ...

    @abstractmethod
    async def publish_session_destroyed(
        self, session_id: str, user_id: str
    ) -> None:
        ...

    @abstractmethod
    async def publish_logout(
        self, user_id: str, session_id: str, correlation_id: str
    ) -> None:
        ...
