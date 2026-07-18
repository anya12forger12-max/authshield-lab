"""Password verification service - wraps the security.password_hasher module."""

from __future__ import annotations

from typing import Any

from ...security.password_hasher import PasswordHasher
from ..domain.interfaces.password_service import IPasswordHashingService


class PasswordVerificationService(IPasswordHashingService):
    """Concrete implementation of ``IPasswordHashingService``.

    Wraps :class:`PasswordHasher` from ``app.security`` to provide
    an async-friendly interface that fits the domain service pattern.

    Parameters
    ----------
    hasher:
        An optional pre-configured ``PasswordHasher`` instance. If ``None``,
        a default instance is created.
    """

    def __init__(self, hasher: PasswordHasher | None = None) -> None:
        self._hasher = hasher or PasswordHasher()

    async def hash_password(
        self, password: str, algorithm: str | None = None
    ) -> str:
        """Hash a password using the specified algorithm.

        Parameters
        ----------
        password:
            The plaintext password.
        algorithm:
            Algorithm identifier (``argon2id``, ``bcrypt``, ``pbkdf2_sha256``, ``sha256``).
            Defaults to ``argon2id``.

        Returns
        -------
        str
            The hashed password string.
        """
        return self._hasher.hash_password(password, algorithm=algorithm)

    async def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a plaintext password against a stored hash.

        Parameters
        ----------
        password:
            The plaintext password to check.
        hashed_password:
            The stored hash to verify against.

        Returns
        -------
        bool
            True if the password matches.
        """
        return self._hasher.verify_password(password, hashed_password)

    def get_algorithm_info(self, algorithm: str) -> dict[str, Any]:
        """Return educational information about the given algorithm."""
        return self._hasher.get_algorithm_info(algorithm)

    def get_recommended_algorithm(self) -> str:
        """Return the name of the recommended hashing algorithm."""
        return PasswordHasher.get_recommended_algorithm()

    def get_supported_algorithms(self) -> list[str]:
        """Return all supported algorithm identifiers."""
        return PasswordHasher.supported_algorithms()
