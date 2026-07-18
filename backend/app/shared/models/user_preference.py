"""User preferences database model."""

from __future__ import annotations

from sqlalchemy import String, JSON, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from ..base_model import Base, TimestampMixin, UUIDPrimaryKeyMixin
from ..logging_config import get_logger

logger = get_logger(__name__)


class UserPreference(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    """Stores per-user UI, accessibility, notification, and privacy preferences."""

    __tablename__ = "user_preferences"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), unique=True, nullable=False, index=True
    )

    # --- Theme ---
    theme: Mapped[str] = mapped_column(String(32), nullable=False, default="dark")
    accent_color: Mapped[str] = mapped_column(
        String(16), nullable=False, default="#3b82f6"
    )

    # --- Language ---
    language: Mapped[str] = mapped_column(String(10), nullable=False, default="en")

    # --- Accessibility ---
    high_contrast: Mapped[bool] = mapped_column(nullable=False, default=False)
    reduced_motion: Mapped[bool] = mapped_column(nullable=False, default=False)
    font_size: Mapped[str] = mapped_column(String(16), nullable=False, default="medium")
    font_family: Mapped[str] = mapped_column(
        String(64), nullable=False, default="default"
    )
    dyslexia_font: Mapped[bool] = mapped_column(nullable=False, default=False)
    zoom_level: Mapped[int] = mapped_column(nullable=False, default=100)
    line_spacing: Mapped[int] = mapped_column(nullable=False, default=100)
    letter_spacing: Mapped[int] = mapped_column(nullable=False, default=100)
    screen_reader_optimized: Mapped[bool] = mapped_column(nullable=False, default=False)
    keyboard_shortcut_profile: Mapped[str] = mapped_column(
        String(32), nullable=False, default="default"
    )
    color_blind_palette: Mapped[str] = mapped_column(
        String(32), nullable=False, default="none"
    )

    # --- Notifications ---
    notifications_enabled: Mapped[bool] = mapped_column(nullable=False, default=True)
    notification_sound: Mapped[bool] = mapped_column(nullable=False, default=True)

    # --- Dashboard ---
    dashboard_layout: Mapped[str] = mapped_column(
        String(32), nullable=False, default="default"
    )

    # --- Developer ---
    developer_mode: Mapped[bool] = mapped_column(nullable=False, default=False)

    # --- Privacy ---
    analytics_enabled: Mapped[bool] = mapped_column(nullable=False, default=False)

    # --- Extensibility ---
    custom_preferences: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    def to_dict(self) -> dict:
        """Serialize the preference record to a dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "theme": self.theme,
            "accent_color": self.accent_color,
            "language": self.language,
            "high_contrast": self.high_contrast,
            "reduced_motion": self.reduced_motion,
            "font_size": self.font_size,
            "font_family": self.font_family,
            "dyslexia_font": self.dyslexia_font,
            "zoom_level": self.zoom_level,
            "line_spacing": self.line_spacing,
            "letter_spacing": self.letter_spacing,
            "screen_reader_optimized": self.screen_reader_optimized,
            "keyboard_shortcut_profile": self.keyboard_shortcut_profile,
            "color_blind_palette": self.color_blind_palette,
            "notifications_enabled": self.notifications_enabled,
            "notification_sound": self.notification_sound,
            "dashboard_layout": self.dashboard_layout,
            "developer_mode": self.developer_mode,
            "analytics_enabled": self.analytics_enabled,
            "custom_preferences": self.custom_preferences,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        return f"<UserPreference id={self.id!r} user_id={self.user_id!r} theme={self.theme!r}>"
