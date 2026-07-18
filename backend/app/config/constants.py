"""Application constants."""

from __future__ import annotations

from enum import Enum


# ---------------------------------------------------------------------------
# Network constants
# ---------------------------------------------------------------------------

LOCALHOST_ADDRESSES: list[str] = ["127.0.0.1", "localhost", "::1", "[::1]", "0.0.0.0"]

BLOCKED_NETWORK_TARGETS: list[str] = [
    # Public DNS resolvers
    "8.8.8.8",
    "8.8.4.4",
    "1.1.1.1",
    "1.0.0.1",
    "9.9.9.9",
    "208.67.222.222",
    "208.67.220.220",
    # Common public IPs
    "0.0.0.0",
    "255.255.255.255",
    "10.0.0.1",
    "10.0.0.0",
    "172.16.0.0",
    "172.16.0.1",
    "192.168.0.0",
    "192.168.0.1",
    "192.168.1.0",
    "192.168.1.1",
    # Well-known domains
    "google.com",
    "github.com",
    "stackoverflow.com",
    "amazonaws.com",
    "cloudflare.com",
    "microsoft.com",
    "apple.com",
    "facebook.com",
    "twitter.com",
    "linkedin.com",
]

BLOCKED_URL_SCHEMES: list[str] = [
    "http",
    "https",
    "ftp",
    "ftps",
    "ssh",
    "telnet",
    "smtp",
    "imap",
]

# ---------------------------------------------------------------------------
# Application modes
# ---------------------------------------------------------------------------


class ApplicationMode(str, Enum):
    """Application operating modes."""

    DEMO = "demo"
    STUDENT = "student"
    INSTRUCTOR = "instructor"
    ADMINISTRATOR = "administrator"
    DEVELOPER = "developer"


# ---------------------------------------------------------------------------
# Log level names
# ---------------------------------------------------------------------------

class LogTagName(str, Enum):
    """Structlog tag names for event classification."""

    SECURITY = "security"
    AUDIT = "audit"
    PERFORMANCE = "performance"
    AUTH = "auth"
    NETWORK = "network"


# ---------------------------------------------------------------------------
# Cache keys
# ---------------------------------------------------------------------------

CACHE_KEY_PREFIX: str = "authshield:"
CACHE_KEY_SESSION: str = f"{CACHE_KEY_PREFIX}session:"
CACHE_KEY_RATE_LIMIT: str = f"{CACHE_KEY_PREFIX}ratelimit:"
CACHE_KEY_LOGIN_ATTEMPTS: str = f"{CACHE_KEY_PREFIX}login_attempts:"
CACHE_KEY_LOCKOUT: str = f"{CACHE_KEY_PREFIX}lockout:"
CACHE_KEY_TOKEN_BLACKLIST: str = f"{CACHE_KEY_PREFIX}token_blacklist:"
CACHE_KEY_USER_PERMS: str = f"{CACHE_KEY_PREFIX}user_perms:"

# ---------------------------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------------------------

RATE_LIMIT_LOGIN: str = "5/minute"
RATE_LIMIT_API_DEFAULT: str = "60/minute"
RATE_LIMIT_PASSWORD_RESET: str = "3/hour"
RATE_LIMIT_TOKEN_REFRESH: str = "10/hour"

# ---------------------------------------------------------------------------
# Password policy defaults
# ---------------------------------------------------------------------------

PASSWORD_MIN_LENGTH: int = 12
PASSWORD_MAX_LENGTH: int = 128
PASSWORD_REQUIRE_UPPERCASE: bool = True
PASSWORD_REQUIRE_LOWERCASE: bool = True
PASSWORD_REQUIRE_DIGIT: bool = True
PASSWORD_REQUIRE_SPECIAL: bool = True
PASSWORD_SPECIAL_CHARACTERS: str = "!@#$%^&*()_+-=[]{}|;':\",./<>?"

# ---------------------------------------------------------------------------
# Module names
# ---------------------------------------------------------------------------

MODULE_AUTH: str = "authentication"
MODULE_USERS: str = "users"
MODULE_SESSIONS: str = "sessions"
MODULE_AUDIT: str = "audit"
MODULE_SECURITY: str = "security"
MODULE_NETWORK: str = "network"
MODULE_REPORTS: str = "reports"
MODULE_THEMES: str = "themes"
MODULE_ACCESSIBILITY: str = "accessibility"
MODULE_ADMIN: str = "admin"
MODULE_HEALTH: str = "health"
MODULE_LAB: str = "lab"

# ---------------------------------------------------------------------------
# HTTP headers
# ---------------------------------------------------------------------------

HEADER_REQUEST_ID: str = "X-Request-ID"
HEADER_SECURITY_POLICY: str = "Content-Security-Policy"
HEADER_X_FRAME_OPTIONS: str = "X-Frame-Options"
HEADER_X_CONTENT_TYPE: str = "X-Content-Type-Options"
HEADER_X_XSS_PROTECTION: str = "X-XSS-Protection"
HEADER_STRICT_TRANSPORT: str = "Strict-Transport-Security"
HEADER_REFERRER_POLICY: str = "Referrer-Policy"
HEADER_PERMISSIONS_POLICY: str = "Permissions-Policy"

# ---------------------------------------------------------------------------
# JWT / token constants
# ---------------------------------------------------------------------------

JWT_ALGORITHM: str = "HS256"
JWT_ISSUER: str = "authshieldlab"
JWT_AUDIENCE: str = "authshieldlab-api"
TOKEN_TYPE_ACCESS: str = "access"
TOKEN_TYPE_REFRESH: str = "refresh"

# ---------------------------------------------------------------------------
# Pagination defaults
# ---------------------------------------------------------------------------

DEFAULT_PAGE: int = 1
DEFAULT_PER_PAGE: int = 20
MAX_PER_PAGE: int = 100
