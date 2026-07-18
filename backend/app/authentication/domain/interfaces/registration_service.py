"""Registration service interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..entities.authentication_result import AuthenticationResult
from ..models.request_models import RegistrationRequest


class IRegistrationService(ABC):
    """Interface for new-user registration operations."""

    @abstractmethod
    async def register(
        self, request: RegistrationRequest, correlation_id: str = ""
    ) -> AuthenticationResult:
        """Register a new user account.

        Parameters
        ----------
        request:
            Registration payload with credentials and profile info.
        correlation_id:
            Optional request correlation ID.

        Returns
        -------
        AuthenticationResult
        """
        ...

    @abstractmethod
    async def check_username_availability(self, username: str) -> bool:
        """Return True if the username is available for registration."""
        ...

    @abstractmethod
    async def check_email_availability(self, email: str) -> bool:
        """Return True if the email is available for registration."""
        ...
