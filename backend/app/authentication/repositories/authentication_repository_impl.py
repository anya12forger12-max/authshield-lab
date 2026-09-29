"""In-memory repository implementations for the authentication domain.

The authentication domain is the only module in the service layer that never
received a concrete persistence implementation, which left ``configure_dependencies()``
uninvoked and every ``/api/v1/auth/*`` route answering 503. These in-memory
implementations follow the same pattern as the sibling modules (see
``app.lms.repositories.lms_repository_impl``) while storing records under the
**SQLAlchemy column names** declared on ``app.shared.models.user.User``
(``password_hash``, ``account_status``, ``failed_login_count``) so the domain
services and the database-backed repository speak one vocabulary.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from ..domain.interfaces.repository_interfaces import ISessionRepository, IUserRepository

#: Every column of ``app.shared.models.user.User`` (plus the mixin bookkeeping
#: columns) that a record may carry.
_USER_FIELDS = frozenset(
    {
        "id",
        "username",
        "display_name",
        "email",
        "password_hash",
        "hash_algorithm",
        "password_version",
        "account_status",
        "role",
        "failed_login_count",
        "last_failed_login",
        "last_login",
        "last_password_change",
        "login_count",
        "security_score",
        "preferred_language",
        "preferred_theme",
        "timezone",
        "profile_picture",
        "bio",
        "mfa_enabled",
        "mfa_secret",
        "is_deleted",
        "deleted_at",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    }
)

#: Fields that a caller is allowed to overwrite via ``update``.
_USER_UPDATABLE_FIELDS = frozenset(_USER_FIELDS - {"id", "created_at", "created_by"})


def _now() -> datetime:
    return datetime.now(UTC)


class InMemoryUserRepository(IUserRepository):
    """In-memory implementation of the user repository.

    Mirrors the column layout of :class:`app.shared.models.user.User` and
    honours its soft-delete semantics: soft-deleted users are invisible to
    every read path, so a deleted account cannot authenticate.
    """

    def __init__(self) -> None:
        self._users: dict[str, dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    async def create(self, user_data: dict[str, Any]) -> dict[str, Any]:
        """Insert a new user and return the stored record.

        Raises
        ------
        ValueError
            If ``user_data`` carries a key that is not a ``User`` column. This
            mirrors ``BaseRepository.create`` (``self._model(**data)``), which
            raises ``TypeError`` on an unknown keyword. Without this check the
            in-memory repository would silently drop a mistyped key and hide
            the exact class of bug this repository exists to catch.
        """
        unknown = set(user_data) - _USER_FIELDS
        if unknown:
            raise ValueError(
                "Unknown user field(s): "
                f"{', '.join(sorted(unknown))}. "
                f"Valid fields: {', '.join(sorted(_USER_FIELDS))}"
            )

        now = _now()
        user_id = str(user_data.get("id") or uuid.uuid4())
        # Every key below maps 1:1 onto a column of
        # app.shared.models.user.User, so ``User(**user)`` always succeeds.
        user: dict[str, Any] = {
            "id": user_id,
            # --- Authentication ---
            "username": user_data.get("username", ""),
            "display_name": user_data.get("display_name", ""),
            "email": user_data.get("email"),
            "password_hash": user_data.get("password_hash", ""),
            "hash_algorithm": user_data.get("hash_algorithm", "argon2id"),
            "password_version": user_data.get("password_version", 1),
            # --- Account status ---
            "account_status": user_data.get("account_status", "active"),
            "role": user_data.get("role", "student"),
            # --- Security metadata ---
            "failed_login_count": user_data.get("failed_login_count", 0),
            "last_failed_login": user_data.get("last_failed_login"),
            "last_login": user_data.get("last_login"),
            "last_password_change": user_data.get("last_password_change"),
            "login_count": user_data.get("login_count", 0),
            "security_score": user_data.get("security_score", 50),
            # --- Preferences ---
            "preferred_language": user_data.get("preferred_language", "en"),
            "preferred_theme": user_data.get("preferred_theme", "dark"),
            "timezone": user_data.get("timezone", "UTC"),
            # --- Profile ---
            "profile_picture": user_data.get("profile_picture"),
            "bio": user_data.get("bio"),
            # --- Multi-factor ---
            "mfa_enabled": user_data.get("mfa_enabled", False),
            "mfa_secret": user_data.get("mfa_secret"),
            # --- Bookkeeping (mixins) ---
            "is_deleted": False,
            "deleted_at": None,
            "created_at": now,
            "updated_at": now,
            "created_by": user_data.get("created_by"),
            "updated_by": user_data.get("updated_by"),
        }
        self._users[user_id] = user
        return user

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    async def get_by_id(self, user_id: str) -> dict[str, Any] | None:
        return self._active(self._users.get(user_id))

    async def get_by_username(self, username: str) -> dict[str, Any] | None:
        for user in self._users.values():
            if self._is_deleted(user):
                continue
            if user["username"].lower() == (username or "").lower():
                return user
        return None

    async def get_by_email(self, email: str) -> dict[str, Any] | None:
        target = (email or "").lower()
        if not target:
            return None
        for user in self._users.values():
            if self._is_deleted(user):
                continue
            stored = (user.get("email") or "").lower()
            if stored and stored == target:
                return user
        return None

    # ------------------------------------------------------------------
    # Update / delete
    # ------------------------------------------------------------------

    async def update(self, user_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        user = self._users.get(user_id)
        if user is None or self._is_deleted(user):
            return None
        # Mirrors BaseRepository.update, which filters to known columns; being
        # explicit here keeps a mistyped key from being silently discarded.
        for key, value in data.items():
            if key not in _USER_FIELDS:
                raise ValueError(f"Unknown user field: {key}")
            if key in _USER_UPDATABLE_FIELDS:
                user[key] = value
        user["updated_at"] = _now()
        return user

    async def delete(self, user_id: str) -> bool:
        """Soft-delete a user. Returns True when a record was transitioned."""
        user = self._users.get(user_id)
        if user is None or self._is_deleted(user):
            return False
        user["is_deleted"] = True
        user["deleted_at"] = _now()
        user["account_status"] = "disabled"
        user["updated_at"] = _now()
        return True

    # ------------------------------------------------------------------
    # Existence checks
    # ------------------------------------------------------------------

    async def exists_by_username(self, username: str) -> bool:
        return await self.get_by_username(username) is not None

    async def exists_by_email(self, email: str) -> bool:
        return await self.get_by_email(email) is not None

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    async def search(
        self,
        query: str,
        filters: dict | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> dict:
        """Search users by username / display name / email with pagination."""
        filters = filters or {}
        needle = (query or "").strip().lower()
        items = [u for u in self._users.values() if not self._is_deleted(u)]

        if needle:
            items = [
                u
                for u in items
                if needle in u["username"].lower()
                or needle in (u.get("display_name") or "").lower()
                or needle in (u.get("email") or "").lower()
            ]
        for key, value in filters.items():
            if key in {"account_status", "role", "username", "email", "display_name"}:
                items = [u for u in items if str(u.get(key, "")) == str(value)]

        items.sort(key=lambda u: u["created_at"], reverse=True)

        total = len(items)
        pages = max(1, (total + per_page - 1) // per_page)
        safe_per_page = max(1, per_page)
        offset = max(0, (page - 1) * safe_per_page)
        return {
            "items": items[offset : offset + safe_per_page],
            "total": total,
            "page": page,
            "per_page": safe_per_page,
            "pages": pages,
        }

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    @staticmethod
    def _is_deleted(user: dict[str, Any]) -> bool:
        return bool(user.get("is_deleted"))

    def _active(self, user: dict[str, Any] | None) -> dict[str, Any] | None:
        if user is None or self._is_deleted(user):
            return None
        return user


class InMemorySessionRepository(ISessionRepository):
    """In-memory implementation of the session repository.

    Mirrors the column layout of :class:`app.shared.models.session.Session`
    for the subset the domain services rely on.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, dict[str, Any]] = {}

    async def create(self, session_data: dict[str, Any]) -> dict[str, Any]:
        now = _now()
        session_id = str(session_data.get("session_id") or uuid.uuid4())
        idle_timeout = int(session_data.get("idle_timeout_minutes", 30))
        expires_at = session_data.get("expires_at") or (now + timedelta(minutes=60))
        session: dict[str, Any] = {
            "id": str(uuid.uuid4()),
            "session_id": session_id,
            "user_id": str(session_data.get("user_id", "")),
            "status": session_data.get("status", "active"),
            "authentication_method": session_data.get("authentication_method", "password"),
            "platform": session_data.get("platform"),
            "device_id": session_data.get("device_id"),
            "remember_me": bool(session_data.get("remember_me", False)),
            "security_level": int(session_data.get("security_level", 1)),
            "idle_timeout_minutes": idle_timeout,
            "expires_at": expires_at,
            "last_activity": session_data.get("last_activity") or now,
            "created_at": now,
            "updated_at": now,
        }
        self._sessions[session_id] = session
        return session

    async def get_by_id(self, session_id: str) -> dict[str, Any] | None:
        return self._sessions.get(session_id)

    async def get_active_by_user(self, user_id: str) -> list[dict[str, Any]]:
        now = _now()
        return [
            s
            for s in self._sessions.values()
            if s["user_id"] == str(user_id) and s["status"] == "active" and s["expires_at"] > now
        ]

    async def update(self, session_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        session = self._sessions.get(session_id)
        if session is None:
            return None
        for key, value in data.items():
            if key != "id":
                session[key] = value
        session["updated_at"] = _now()
        return session

    async def delete(self, session_id: str) -> bool:
        return self._sessions.pop(session_id, None) is not None

    async def delete_expired(self) -> int:
        now = _now()
        expired = [sid for sid, s in self._sessions.items() if s["expires_at"] <= now]
        for sid in expired:
            del self._sessions[sid]
        return len(expired)

    async def delete_all_user_sessions(self, user_id: str) -> int:
        target = str(user_id)
        doomed = [sid for sid, s in self._sessions.items() if s["user_id"] == target]
        for sid in doomed:
            del self._sessions[sid]
        return len(doomed)
