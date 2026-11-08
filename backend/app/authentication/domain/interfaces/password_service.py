"""Password hashing and policy service interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod


class IPasswordHashingService(ABC):
    """Interface for password hashing and verification."""

    @abstractmethod
    async def hash_password(
        self, password: str, algorithm: str | None = None
    ) -> str:
        """Hash a password using the specified (or default) algorithm."""
        ...

    @abstractmethod
    async def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a plaintext password against a stored hash."""
        ...

    @abstractmethod
    def get_algorithm_info(self, algorithm: str) -> dict:
        """Return educational information about the given algorithm."""
        ...

    @abstractmethod
    def get_recommended_algorithm(self) -> str:
        """Return the name of the recommended hashing algorithm."""
        ...

    @abstractmethod
    def get_supported_algorithms(self) -> list[str]:
        """Return all supported algorithm identifiers."""
        ...


class IPasswordPolicyService(ABC):
    """Interface for password policy enforcement."""

    @abstractmethod
    def validate_password(self, password: str, username: str = "") -> dict:
        """Validate a password against the current policy.

        Returns a dict with ``is_valid`` bool, ``errors`` list, and ``warnings`` list.
        """
        ...

    @abstractmethod
    def check_strength(self, password: str) -> dict:
        """Evaluate password strength on a 0-100 scale.

        Returns a dict with ``score``, ``level``, and ``feedback`` fields.
        """
        ...

    @abstractmethod
    def get_policy_config(self) -> dict:
        """Return the current password policy configuration."""
        ...
