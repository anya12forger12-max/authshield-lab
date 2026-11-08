"""Extension management service."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone

from app.developer.domain.entities.extension import (
    Extension,
    ExtensionStatus,
    ExtensionType,
    ExtensionVersion,
    InstalledExtension,
)


class ExtensionService:
    """Manages the full lifecycle of extensions: install, uninstall, update, enable, disable, search, validate."""

    def __init__(self) -> None:
        self._extensions: dict[str, Extension] = {}
        self._versions: dict[str, ExtensionVersion] = {}
        self._installed: dict[str, InstalledExtension] = {}

    def register_extension(
        self,
        name: str,
        version: str = "1.0.0",
        author: str = "",
        description: str = "",
        extension_type: ExtensionType = ExtensionType.PLUGIN,
        permissions: list[str] | None = None,
        dependencies: list[str] | None = None,
        compatibility: str = ">=1.0",
    ) -> Extension:
        """Register a new extension in the catalogue."""
        ext = Extension(
            name=name,
            version=version,
            author=author,
            description=description,
            extension_type=extension_type,
            permissions=permissions,
            dependencies=dependencies,
            compatibility=compatibility,
        )
        self._extensions[ext.id] = ext
        return ext

    def get_extension(self, extension_id: str) -> Extension | None:
        """Retrieve an extension by ID."""
        return self._extensions.get(extension_id)

    def list_extensions(self) -> list[Extension]:
        """Return all registered extensions."""
        return list(self._extensions.values())

    def list_by_type(self, extension_type: ExtensionType) -> list[Extension]:
        """Return extensions filtered by type."""
        return [e for e in self._extensions.values() if e.extension_type == extension_type]

    def search_extensions(self, query: str) -> list[Extension]:
        """Search extensions by name or description substring."""
        q = query.lower()
        return [
            e
            for e in self._extensions.values()
            if q in e.name.lower() or q in e.description.lower()
        ]

    def install_extension(
        self,
        extension_id: str,
        installed_by: str = "",
        config: dict | None = None,
    ) -> InstalledExtension | None:
        """Install an extension for a user."""
        ext = self._extensions.get(extension_id)
        if ext is None:
            return None
        if ext.status == ExtensionStatus.INSTALLED:
            return None
        ext.install()
        record = InstalledExtension(
            extension_id=extension_id,
            version=ext.version,
            installed_by=installed_by,
            config=config,
        )
        self._installed[record.id] = record
        return record

    def uninstall_extension(self, extension_id: str) -> bool:
        """Uninstall an extension."""
        ext = self._extensions.get(extension_id)
        if ext is None:
            return False
        ext.uninstall()
        to_remove = [
            inst_id
            for inst_id, inst in self._installed.items()
            if inst.extension_id == extension_id
        ]
        for inst_id in to_remove:
            del self._installed[inst_id]
        return True

    def enable_extension(self, extension_id: str) -> bool:
        """Enable a disabled extension."""
        ext = self._extensions.get(extension_id)
        if ext is None:
            return False
        ext.enable()
        for inst in self._installed.values():
            if inst.extension_id == extension_id:
                inst.enable()
        return True

    def disable_extension(self, extension_id: str) -> bool:
        """Disable an installed extension."""
        ext = self._extensions.get(extension_id)
        if ext is None:
            return False
        ext.disable()
        for inst in self._installed.values():
            if inst.extension_id == extension_id:
                inst.disable()
        return True

    def update_extension(self, extension_id: str, new_version: str) -> Extension | None:
        """Bump an extension to a new version."""
        ext = self._extensions.get(extension_id)
        if ext is None:
            return None
        old_version = ext.version
        ext.version = new_version
        for inst in self._installed.values():
            if inst.extension_id == extension_id:
                inst.version = new_version
        return ext

    def add_version(
        self,
        extension_id: str,
        version: str,
        changes: list[str] | None = None,
        compatibility: str = ">=1.0",
    ) -> ExtensionVersion | None:
        """Record a new release version entry."""
        if extension_id not in self._extensions:
            return None
        ev = ExtensionVersion(
            extension_id=extension_id,
            version=version,
            changes=changes,
            compatibility=compatibility,
        )
        self._versions[ev.id] = ev
        return ev

    def list_versions(self, extension_id: str) -> list[ExtensionVersion]:
        """Return all recorded versions for an extension."""
        return [v for v in self._versions.values() if v.extension_id == extension_id]

    def list_installed(self) -> list[InstalledExtension]:
        """Return all installation records."""
        return list(self._installed.values())

    def get_installed(self, installed_id: str) -> InstalledExtension | None:
        """Retrieve an installation record by its ID."""
        return self._installed.get(installed_id)

    def update_installed_config(
        self, installed_id: str, key: str, value: object
    ) -> InstalledExtension | None:
        """Update a single config key on an installed extension."""
        inst = self._installed.get(installed_id)
        if inst is None:
            return None
        inst.update_config(key, value)
        return inst

    def validate_extension(self, extension_id: str) -> dict:
        """Run basic validation checks on an extension."""
        ext = self._extensions.get(extension_id)
        if ext is None:
            return {"valid": False, "errors": ["Extension not found"]}
        errors: list[str] = []
        if not ext.name:
            errors.append("Name is required")
        if not ext.version:
            errors.append("Version is required")
        if not ext.author:
            errors.append("Author is required")
        return {"valid": len(errors) == 0, "errors": errors}

    def compute_checksum(self, extension_id: str, payload: bytes) -> str:
        """Compute and store a SHA-256 checksum for an extension."""
        ext = self._extensions.get(extension_id)
        if ext is None:
            return ""
        checksum = hashlib.sha256(payload).hexdigest()
        ext.checksum = checksum
        return checksum

    def delete_extension(self, extension_id: str) -> bool:
        """Permanently remove an extension from the catalogue."""
        if extension_id not in self._extensions:
            return False
        del self._extensions[extension_id]
        to_remove = [
            inst_id
            for inst_id, inst in self._installed.items()
            if inst.extension_id == extension_id
        ]
        for inst_id in to_remove:
            del self._installed[inst_id]
        return True
