"""JWT and secure token management."""

from __future__ import annotations

import secrets
import time
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt

from app.config.constants import JWT_ALGORITHM, JWT_AUDIENCE, JWT_ISSUER


class TokenManager:
    """Generates, validates, and manages JWT and random tokens.

    Parameters
    ----------
    secret_key:
        HMAC key used for JWT signing.
    algorithm:
        JWT signing algorithm (default ``HS256``).
    access_token_expiry_minutes:
        Lifetime of access tokens in minutes.
    refresh_token_expiry_minutes:
        Lifetime of refresh tokens in minutes.
    issuer:
        ``iss`` claim value.
    audience:
        ``aud`` claim value.

    Example::

        tm = TokenManager(secret_key="s3cret", access_token_expiry_minutes=30)
        token = tm.create_access_token(subject="user-123", extra={"role": "student"})
        payload = tm.validate_token(token)
        assert payload["sub"] == "user-123"
    """

    def __init__(
        self,
        secret_key: str,
        algorithm: str = JWT_ALGORITHM,
        access_token_expiry_minutes: int = 30,
        refresh_token_expiry_expiry_minutes: int = 10080,
        issuer: str = JWT_ISSUER,
        audience: str = JWT_AUDIENCE,
    ) -> None:
        if not secret_key:
            raise ValueError("secret_key must not be empty.")
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._access_expiry = access_token_expiry_minutes
        self._refresh_expiry = refresh_token_expiry_expiry_minutes
        self._issuer = issuer
        self._audience = audience

    # ------------------------------------------------------------------
    # Random tokens
    # ------------------------------------------------------------------

    @staticmethod
    def generate_secure_token(length: int = 64) -> str:
        """Generate a cryptographically secure random URL-safe token.

        Parameters
        ----------
        length:
            Number of random bytes (output string is ~4/3 longer due to
            base64 encoding).

        Returns
        -------
        str
            URL-safe token string.
        """
        return secrets.token_urlsafe(length)

    @staticmethod
    def generate_hex_token(length: int = 32) -> str:
        """Generate a random hex-encoded token."""
        return secrets.token_hex(length)

    @staticmethod
    def generate_numeric_token(digits: int = 6) -> str:
        """Generate a numeric one-time token (e.g. for TOTP backup codes)."""
        upper = 10**digits
        return str(secrets.randbelow(upper)).zfill(digits)

    # ------------------------------------------------------------------
    # JWT tokens
    # ------------------------------------------------------------------

    def create_access_token(
        self,
        subject: str,
        extra: dict[str, Any] | None = None,
        expires_at: datetime | None = None,
    ) -> str:
        """Create a signed JWT access token.

        Parameters
        ----------
        subject:
            The ``sub`` claim (typically a user ID).
        extra:
            Additional claims to embed.
        expires_at:
            Override the default expiry time.

        Returns
        -------
        str
            Encoded JWT string.
        """
        now = datetime.now(timezone.utc)
        if expires_at is None:
            expires_at = now + timedelta(minutes=self._access_expiry)

        claims: dict[str, Any] = {
            "sub": subject,
            "iat": now,
            "exp": expires_at,
            "nbf": now,
            "iss": self._issuer,
            "aud": self._audience,
            "type": "access",
            "jti": self.generate_hex_token(16),
        }
        if extra:
            claims.update(extra)

        return jwt.encode(claims, self._secret_key, algorithm=self._algorithm)

    def create_refresh_token(
        self,
        subject: str,
        extra: dict[str, Any] | None = None,
    ) -> str:
        """Create a signed JWT refresh token with a longer expiry."""
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=self._refresh_expiry)

        claims: dict[str, Any] = {
            "sub": subject,
            "iat": now,
            "exp": expires_at,
            "nbf": now,
            "iss": self._issuer,
            "aud": self._audience,
            "type": "refresh",
            "jti": self.generate_hex_token(16),
        }
        if extra:
            claims.update(extra)

        return jwt.encode(claims, self._secret_key, algorithm=self._algorithm)

    def validate_token(self, token: str) -> dict[str, Any]:
        """Decode and validate a JWT token.

        Parameters
        ----------
        token:
            The encoded JWT string.

        Returns
        -------
        dict
            Decoded claims payload.

        Raises
        ------
        ValueError
            If the token is expired, malformed, or has invalid claims.
        """
        try:
            payload = jwt.decode(
                token,
                self._secret_key,
                algorithms=[self._algorithm],
                issuer=self._issuer,
                audience=self._audience,
                options={
                    "require": ["exp", "iss", "aud", "sub", "jti"],
                },
            )
        except JWTError as exc:
            raise ValueError(f"Invalid token: {exc}") from exc

        return payload

    def extract_token_type(self, token: str) -> str | None:
        """Return the ``type`` claim from a token without full validation."""
        try:
            unverified = jwt.get_unverified_claims(token)
            return unverified.get("type")
        except JWTError:
            return None

    def extract_subject(self, token: str) -> str | None:
        """Return the ``sub`` claim from a token without full validation."""
        try:
            unverified = jwt.get_unverified_claims(token)
            return unverified.get("sub")
        except JWTError:
            return None

    def get_token_expiry(self, token: str) -> datetime | None:
        """Return the expiry datetime from a token."""
        try:
            payload = self.validate_token(token)
            exp = payload.get("exp")
            if isinstance(exp, (int, float)):
                return datetime.fromtimestamp(exp, tz=timezone.utc)
            if isinstance(exp, datetime):
                return exp
        except (ValueError, JWTError):
            pass
        return None

    def is_token_expired(self, token: str) -> bool:
        """Check whether a token has expired."""
        expiry = self.get_token_expiry(token)
        if expiry is None:
            return True
        return datetime.now(timezone.utc) > expiry

    def regenerate_token(
        self,
        old_token: str,
        extra: dict[str, Any] | None = None,
    ) -> str:
        """Create a new access token from an existing one (session regeneration).

        Extracts the subject and non-expired claims from *old_token* and
        issues a fresh token with a new ``jti`` and ``iat``.

        Parameters
        ----------
        old_token:
            The existing JWT to replace.
        extra:
            Additional claims to merge.

        Returns
        -------
        str
            A new, freshly-signed JWT.

        Raises
        ------
        ValueError
            If the old token is invalid or expired.
        """
        payload = self.validate_token(old_token)

        new_extra: dict[str, Any] = {}
        skip_keys = {"sub", "iat", "exp", "nbf", "iss", "aud", "jti", "type"}
        for key, val in payload.items():
            if key not in skip_keys:
                new_extra[key] = val
        if extra:
            new_extra.update(extra)

        subject: str = payload["sub"]
        token_type: str = payload.get("type", "access")

        now = datetime.now(timezone.utc)
        if token_type == "refresh":
            expires_at = now + timedelta(minutes=self._refresh_expiry)
        else:
            expires_at = now + timedelta(minutes=self._access_expiry)

        claims: dict[str, Any] = {
            "sub": subject,
            "iat": now,
            "exp": expires_at,
            "nbf": now,
            "iss": self._issuer,
            "aud": self._audience,
            "type": token_type,
            "jti": self.generate_hex_token(16),
        }
        if new_extra:
            claims.update(new_extra)

        return jwt.encode(claims, self._secret_key, algorithm=self._algorithm)

    def create_token_pair(
        self,
        subject: str,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, str]:
        """Create both an access and refresh token for the given subject.

        Returns
        -------
        dict
            ``{"access_token": "...", "refresh_token": "...", "token_type": "Bearer"}``
        """
        return {
            "access_token": self.create_access_token(subject, extra),
            "refresh_token": self.create_refresh_token(subject, extra),
            "token_type": "Bearer",
        }

    def blacklisted_claims(self, token: str) -> dict[str, Any] | None:
        """Extract minimal claims useful for building a blacklist entry."""
        try:
            payload = self.validate_token(token)
            return {
                "jti": payload.get("jti"),
                "sub": payload.get("sub"),
                "exp": payload.get("exp"),
                "type": payload.get("type"),
            }
        except (ValueError, JWTError):
            return None
