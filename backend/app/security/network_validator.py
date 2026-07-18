"""Network validation for AuthShieldLab security boundary enforcement."""

from __future__ import annotations

import ipaddress
import re
from urllib.parse import urlparse

from app.config.constants import (
    BLOCKED_NETWORK_TARGETS,
    BLOCKED_URL_SCHEMES,
    LOCALHOST_ADDRESSES,
)


class SecurityViolationError(Exception):
    """Raised when a network operation targets a non-localhost address."""

    def __init__(self, target: str, message: str | None = None) -> None:
        self.target = target
        self.message = message or self._default_message(target)
        super().__init__(self.message)

    @staticmethod
    def _default_message(target: str) -> str:
        return (
            f"Security violation: target '{target}' is not a localhost address. "
            "AuthShieldLab enforces a strict localhost-only network policy for all "
            "operations. External network access is prohibited in this environment."
        )


class NetworkValidator:
    """Validates that all network targets are confined to localhost.

    This validator is a core security boundary for AuthShieldLab. It ensures
    that no outbound or inbound connections escape the local machine, preventing
    accidental or intentional network access during security training exercises.

    Example::

        validator = NetworkValidator()
        assert validator.validate_target("127.0.0.1")
        assert validator.validate_target("localhost")
        validator.validate_target("8.8.8.8")  # raises SecurityViolationError
    """

    _IPV4_LOOPBACK = ipaddress.IPv4Address("127.0.0.1")
    _IPV6_LOOPBACK = ipaddress.IPv6Address("::1")

    def __init__(
        self,
        extra_blocked: list[str] | None = None,
        extra_allowed: list[str] | None = None,
    ) -> None:
        self._blocked: set[str] = {t.lower() for t in BLOCKED_NETWORK_TARGETS}
        self._allowed: set[str] = {a.lower() for a in LOCALHOST_ADDRESSES}
        if extra_blocked:
            self._blocked.update(t.lower() for t in extra_blocked)
        if extra_allowed:
            self._allowed.update(a.lower() for a in extra_allowed)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def validate_target(self, target: str) -> bool:
        """Validate that *target* resolves to a localhost address.

        Parameters
        ----------
        target:
            An IP address, hostname, URL, or domain string.

        Returns
        -------
        bool
            ``True`` if the target is localhost-only.

        Raises
        ------
        SecurityViolationError
            If the target is not localhost or is a blocked address.
        """
        target = target.strip()
        if not target:
            raise SecurityViolationError(target, "Target must not be empty.")

        if self._is_url(target):
            return self._validate_url(target)

        if target.lower() in self._blocked:
            raise SecurityViolationError(
                target,
                self.get_security_warning()
                + f"\nBlocked target: '{target}' is on the explicit blocklist.",
            )

        if self._is_localhost_address(target):
            return True

        raise SecurityViolationError(target)

    def is_localhost_only(self, target: str) -> bool:
        """Return ``True`` if *target* is localhost, without raising."""
        try:
            return self.validate_target(target)
        except SecurityViolationError:
            return False

    def get_security_warning(self) -> str:
        """Return an educational warning message about network boundaries."""
        return (
            "⚠ SECURITY WARNING: AuthShieldLab operates in a sandboxed "
            "localhost-only environment. All network operations must target "
            "127.0.0.1, ::1, or localhost. External network access (public IPs, "
            "private LAN addresses, domains, URLs) is strictly prohibited. "
            "This policy prevents accidental data exfiltration and ensures "
            "training exercises remain contained within the local machine."
        )

    def validate_url(self, url: str) -> bool:
        """Public wrapper for URL validation (alias for validate_target on URLs)."""
        return self.validate_target(url)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _is_url(value: str) -> bool:
        """Detect whether the value looks like a URL."""
        return bool(re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", value))

    def _validate_url(self, url: str) -> bool:
        """Parse and validate a URL target."""
        try:
            parsed = urlparse(url)
        except Exception as exc:
            raise SecurityViolationError(
                url, f"Unable to parse URL: {exc}"
            ) from exc

        scheme = parsed.scheme.lower()
        if scheme in BLOCKED_URL_SCHEMES and scheme in ("http", "https", "ftp", "ftps"):
            raise SecurityViolationError(
                url,
                self.get_security_warning()
                + f"\nURL scheme '{scheme}' is not permitted for external resources.",
            )

        hostname = (parsed.hostname or "").lower()
        if not hostname:
            raise SecurityViolationError(url, "URL has no hostname.")

        if hostname in self._blocked:
            raise SecurityViolationError(
                url,
                self.get_security_warning()
                + f"\nHostname '{hostname}' is on the explicit blocklist.",
            )

        if not self._is_localhost_address(hostname):
            raise SecurityViolationError(url)

        return True

    @staticmethod
    def _is_localhost_address(value: str) -> bool:
        """Check whether *value* represents a loopback address."""
        value = value.lower().strip("[]")

        if value in ("localhost", "0.0.0.0"):
            return True

        try:
            addr = ipaddress.ip_address(value)
            return addr.is_loopback or addr.is_unspecified
        except ValueError:
            pass

        # Allow port-stripped forms like "127.0.0.1:8000"
        host_part = value.split(":")[0].strip("[]")
        try:
            addr = ipaddress.ip_address(host_part)
            return addr.is_loopback or addr.is_unspecified
        except ValueError:
            return False
