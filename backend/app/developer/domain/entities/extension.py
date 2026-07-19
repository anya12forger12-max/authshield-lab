"""Extension, ExtensionVersion, and InstalledExtension entities."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum


class ExtensionType(str, Enum):
    """Types of extensions the platform supports."""

    PLUGIN = "plugin"
    THEME = "theme"
    LOCALIZATION_PACK = "localization_pack"
    COURSE_COLLECTION = "course_collection"
    SCENARIO_COLLECTION = "scenario_collection"
    REPORT_TEMPLATE = "report_template"
    DOC_PACK = "doc_pack"
    ACCESSIBILITY_PROFILE = "accessibility_profile"


class ExtensionStatus(str, Enum):
    """Lifecycle status of an extension."""

    INSTALLED = "installed"
    UNINSTALLED = "uninstalled"
    DISABLED = "disabled"
    ERROR = "error"


class Extension:
    """A platform extension that can be installed to add functionality."""

    def __init__(
        self,
        id: str | None = None,
        name: str = "",
        version: str = "1.0.0",
        author: str = "",
        description: str = "",
        extension_type: ExtensionType = ExtensionType.PLUGIN,
        status: ExtensionStatus = ExtensionStatus.UNINSTALLED,
        installed_at: datetime | None = None,
        permissions: list[str] | None = None,
        dependencies: list[str] | None = None,
        compatibility: str = ">=1.0",
        checksum: str = "",
    ) -> None:
        self.id: str = id or str(uuid.uuid4())
        self.name: str = name
        self.version: str = version
        self.author: str = author
        self.description: str = description
        self.extension_type: ExtensionType = extension_type
        self.status: ExtensionStatus = status
        self.installed_at: datetime | None = installed_at
        self.permissions: list[str] = permissions if permissions is not None else []
        self.dependencies: list[str] = dependencies if dependencies is not None else []
        self.compatibility: str = compatibility
        self.checksum: str = checksum

    def install(self) -> None:
        """Mark the extension as installed."""
        self.status = ExtensionStatus.INSTALLED
        self.installed_at = datetime.now(timezone.utc)

    def uninstall(self) -> None:
        """Mark the extension as uninstalled."""
        self.status = ExtensionStatus.UNINSTALLED
        self.installed_at = None

    def disable(self) -> None:
        """Disable the extension without removing it."""
        self.status = ExtensionStatus.DISABLED

    def enable(self) -> None:
        """Re-enable a disabled extension."""
        self.status = ExtensionStatus.INSTALLED

    def mark_error(self) -> None:
        """Mark the extension as being in an error state."""
        self.status = ExtensionStatus.ERROR

    def has_permission(self, permission: str) -> bool:
        """Check whether this extension declares a given permission."""
        return permission in self.permissions

    def depends_on(self, extension_id: str) -> bool:
        """Check whether this extension depends on another extension."""
        return extension_id in self.dependencies

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "extension_type": self.extension_type.value,
            "status": self.status.value,
            "installed_at": self.installed_at.isoformat() if self.installed_at else None,
            "permissions": list(self.permissions),
            "dependencies": list(self.dependencies),
            "compatibility": self.compatibility,
            "checksum": self.checksum,
        }


class ExtensionVersion:
    """Tracks released versions of an extension."""

    def __init__(
        self,
        id: str | None = None,
        extension_id: str = "",
        version: str = "1.0.0",
        changes: list[str] | None = None,
        released_at: datetime | None = None,
        compatibility: str = ">=1.0",
    ) -> None:
        self.id: str = id or str(uuid.uuid4())
        self.extension_id: str = extension_id
        self.version: str = version
        self.changes: list[str] = changes if changes is not None else []
        self.released_at: datetime = released_at or datetime.now(timezone.utc)
        self.compatibility: str = compatibility

    def add_change(self, change: str) -> None:
        """Append a changelog entry."""
        self.changes.append(change)

    def is_compatible_with(self, platform_version: str) -> bool:
        """Rudimentary compatibility check against platform version."""
        return platform_version >= self.compatibility.lstrip(">=")

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "id": self.id,
            "extension_id": self.extension_id,
            "version": self.version,
            "changes": list(self.changes),
            "released_at": self.released_at.isoformat(),
            "compatibility": self.compatibility,
        }


class InstalledExtension:
    """Represents an extension that has been installed by a specific user."""

    def __init__(
        self,
        id: str | None = None,
        extension_id: str = "",
        version: str = "1.0.0",
        installed_by: str = "",
        installed_at: datetime | None = None,
        enabled: bool = True,
        config: dict | None = None,
    ) -> None:
        self.id: str = id or str(uuid.uuid4())
        self.extension_id: str = extension_id
        self.version: str = version
        self.installed_by: str = installed_by
        self.installed_at: datetime = installed_at or datetime.now(timezone.utc)
        self.enabled: bool = enabled
        self.config: dict = config if config is not None else {}

    def enable(self) -> None:
        """Enable this installed extension."""
        self.enabled = True

    def disable(self) -> None:
        """Disable this installed extension."""
        self.enabled = False

    def update_config(self, key: str, value: object) -> None:
        """Set a single configuration key."""
        self.config[key] = value

    def remove_config(self, key: str) -> None:
        """Remove a configuration key."""
        self.config.pop(key, None)

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "id": self.id,
            "extension_id": self.extension_id,
            "version": self.version,
            "installed_by": self.installed_by,
            "installed_at": self.installed_at.isoformat(),
            "enabled": self.enabled,
            "config": dict(self.config),
        }
