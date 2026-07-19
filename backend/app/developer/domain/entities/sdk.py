"""SDK, SDK Module, Plugin Manifest, and SDK Template entities."""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from enum import Enum


class SdKVersion(str, Enum):
    """Supported SDK major versions."""

    V1 = "1.0"
    V2 = "2.0"
    V3 = "3.0"


class SdK:
    """Represents a software development kit distributed with the platform."""

    def __init__(
        self,
        id: str | None = None,
        name: str = "",
        version: SdKVersion = SdKVersion.V1,
        description: str = "",
        author: str = "",
        compatibility_version: str = "1.0",
        modules: list[str] | None = None,
        created_at: datetime | None = None,
        deprecated: bool = False,
        min_platform_version: str = "1.0",
    ) -> None:
        self.id: str = id or str(uuid.uuid4())
        self.name: str = name
        self.version: SdKVersion = version
        self.description: str = description
        self.author: str = author
        self.compatibility_version: str = compatibility_version
        self.modules: list[str] = modules if modules is not None else []
        self.created_at: datetime = created_at or datetime.now(timezone.utc)
        self.deprecated: bool = deprecated
        self.min_platform_version: str = min_platform_version

    def is_compatible_with(self, platform_version: str) -> bool:
        """Check if this SDK is compatible with a given platform version."""
        return self.min_platform_version <= platform_version

    def add_module(self, module_name: str) -> None:
        """Register a module name under this SDK."""
        if module_name not in self.modules:
            self.modules.append(module_name)

    def remove_module(self, module_name: str) -> None:
        """Remove a module name from this SDK."""
        if module_name in self.modules:
            self.modules.remove(module_name)

    def deprecate(self) -> None:
        """Mark this SDK as deprecated."""
        self.deprecated = True

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version.value,
            "description": self.description,
            "author": self.author,
            "compatibility_version": self.compatibility_version,
            "modules": list(self.modules),
            "created_at": self.created_at.isoformat(),
            "deprecated": self.deprecated,
            "min_platform_version": self.min_platform_version,
        }


class SdKModule:
    """A single module (sub-package) within an SDK."""

    def __init__(
        self,
        id: str | None = None,
        sdk_id: str = "",
        name: str = "",
        description: str = "",
        api_classes: list[str] | None = None,
        version: str = "1.0.0",
    ) -> None:
        self.id: str = id or str(uuid.uuid4())
        self.sdk_id: str = sdk_id
        self.name: str = name
        self.description: str = description
        self.api_classes: list[str] = api_classes if api_classes is not None else []
        self.version: str = version

    def add_api_class(self, class_name: str) -> None:
        """Register an API class exposed by this module."""
        if class_name not in self.api_classes:
            self.api_classes.append(class_name)

    def remove_api_class(self, class_name: str) -> None:
        """Remove an API class from this module."""
        if class_name in self.api_classes:
            self.api_classes.remove(class_name)

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "id": self.id,
            "sdk_id": self.sdk_id,
            "name": self.name,
            "description": self.description,
            "api_classes": list(self.api_classes),
            "version": self.version,
        }


class PluginManifest:
    """Metadata manifest for a plugin package."""

    def __init__(
        self,
        id: str | None = None,
        name: str = "",
        version: str = "1.0.0",
        author: str = "",
        description: str = "",
        dependencies: list[str] | None = None,
        permissions: list[str] | None = None,
        compatibility: str = ">=1.0",
        license: str = "MIT",
        checksum: str = "",
        signature: str = "",
    ) -> None:
        self.id: str = id or str(uuid.uuid4())
        self.name: str = name
        self.version: str = version
        self.author: str = author
        self.description: str = description
        self.dependencies: list[str] = dependencies if dependencies is not None else []
        self.permissions: list[str] = permissions if permissions is not None else []
        self.compatibility: str = compatibility
        self.license: str = license
        self.checksum: str = checksum
        self.signature: str = signature

    def compute_checksum(self, payload: bytes) -> str:
        """Compute SHA-256 checksum for the given payload and store it."""
        self.checksum = hashlib.sha256(payload).hexdigest()
        return self.checksum

    def has_permission(self, permission: str) -> bool:
        """Check whether the manifest declares a given permission."""
        return permission in self.permissions

    def requires_dependency(self, dep_name: str) -> bool:
        """Check whether the manifest lists a given dependency."""
        return dep_name in self.dependencies

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "dependencies": list(self.dependencies),
            "permissions": list(self.permissions),
            "compatibility": self.compatibility,
            "license": self.license,
            "checksum": self.checksum,
            "signature": self.signature,
        }


class SdKTemplate:
    """A starter template shipped inside an SDK."""

    def __init__(
        self,
        id: str | None = None,
        name: str = "",
        template_type: str = "project",
        description: str = "",
        content: dict | None = None,
        category: str = "general",
        version: str = "1.0.0",
    ) -> None:
        self.id: str = id or str(uuid.uuid4())
        self.name: str = name
        self.template_type: str = template_type
        self.description: str = description
        self.content: dict = content if content is not None else {}
        self.category: str = category
        self.version: str = version

    def update_content(self, new_content: dict) -> None:
        """Replace template content entirely."""
        self.content = dict(new_content)

    def merge_content(self, extra: dict) -> None:
        """Merge additional keys into existing content."""
        self.content.update(extra)

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "template_type": self.template_type,
            "description": self.description,
            "content": dict(self.content),
            "category": self.category,
            "version": self.version,
        }
