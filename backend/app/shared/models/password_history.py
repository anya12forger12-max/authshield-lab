"""Password history model for future password policy enforcement."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import String, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column

from ..base_model import Base, TimestampMixin, UUIDPrimaryKeyMixin
from ..logging_config import get_logger

logger = get_logger(__name__)


class PasswordHistory(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    """Maintains a rolling history of password hashes per user.

    Used to enforce password-reuse policies and to detect credential
    stuffing across password rotations.
    """

    __tablename__ = "password_history"

    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    hash_algorithm: Mapped[str] = mapped_column(String(32), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    __table_args__ = (
        Index("ix_password_history_user_version", "user_id", "version"),
    )

    def to_dict(self, include_hash: bool = False) -> dict:
        """Serialize the history entry to a dictionary.

        Parameters
        ----------
        include_hash:
            When ``True`` the ``password_hash`` field is included in the
            output.  Defaults to ``False`` for safety.
        """
        result: dict = {
            "id": self.id,
            "user_id": self.user_id,
            "hash_algorithm": self.hash_algorithm,
            "version": self.version,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_hash:
            result["password_hash"] = self.password_hash
        return result

    def __repr__(self) -> str:
        return (
            f"<PasswordHistory id={self.id!r} user_id={self.user_id!r} "
            f"version={self.version}>"
        )
