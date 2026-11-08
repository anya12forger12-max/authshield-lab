"""SDK management service."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.developer.domain.entities.sdk import PluginManifest, SdK, SdKModule, SdKTemplate, SdKVersion


class SdKService:
    """Provides SDK lifecycle operations: create, update, deprecate, version tracking, compatibility checks."""

    def __init__(self) -> None:
        self._sdks: dict[str, SdK] = {}
        self._modules: dict[str, SdKModule] = {}
        self._manifests: dict[str, PluginManifest] = {}
        self._templates: dict[str, SdKTemplate] = {}

    def create_sdk(
        self,
        name: str,
        version: SdKVersion = SdKVersion.V1,
        description: str = "",
        author: str = "",
        compatibility_version: str = "1.0",
        modules: list[str] | None = None,
        min_platform_version: str = "1.0",
    ) -> SdK:
        """Create and register a new SDK."""
        sdk = SdK(
            name=name,
            version=version,
            description=description,
            author=author,
            compatibility_version=compatibility_version,
            modules=modules,
            min_platform_version=min_platform_version,
        )
        self._sdks[sdk.id] = sdk
        return sdk

    def get_sdk(self, sdk_id: str) -> SdK | None:
        """Retrieve an SDK by its ID."""
        return self._sdks.get(sdk_id)

    def get_sdk_by_name(self, name: str) -> SdK | None:
        """Retrieve an SDK by its unique name."""
        for sdk in self._sdks.values():
            if sdk.name == name:
                return sdk
        return None

    def list_sdks(self) -> list[SdK]:
        """Return all registered SDKs."""
        return list(self._sdks.values())

    def list_active_sdks(self) -> list[SdK]:
        """Return SDKs that are not deprecated."""
        return [sdk for sdk in self._sdks.values() if not sdk.deprecated]

    def update_sdk(
        self,
        sdk_id: str,
        name: str | None = None,
        description: str | None = None,
        author: str | None = None,
    ) -> SdK | None:
        """Update mutable fields on an SDK."""
        sdk = self._sdks.get(sdk_id)
        if sdk is None:
            return None
        if name is not None:
            sdk.name = name
        if description is not None:
            sdk.description = description
        if author is not None:
            sdk.author = author
        return sdk

    def deprecate_sdk(self, sdk_id: str) -> SdK | None:
        """Mark an SDK as deprecated."""
        sdk = self._sdks.get(sdk_id)
        if sdk is None:
            return None
        sdk.deprecate()
        return sdk

    def delete_sdk(self, sdk_id: str) -> bool:
        """Remove an SDK from the registry."""
        if sdk_id in self._sdks:
            del self._sdks[sdk_id]
            return True
        return False

    def check_compatibility(self, sdk_id: str, platform_version: str) -> bool:
        """Check whether a given SDK is compatible with the supplied platform version."""
        sdk = self._sdks.get(sdk_id)
        if sdk is None:
            return False
        return sdk.is_compatible_with(platform_version)

    # -- Module management ---------------------------------------------------

    def register_module(
        self,
        sdk_id: str,
        name: str,
        description: str = "",
        api_classes: list[str] | None = None,
        version: str = "1.0.0",
    ) -> SdKModule | None:
        """Register a module under an existing SDK."""
        sdk = self._sdks.get(sdk_id)
        if sdk is None:
            return None
        module = SdKModule(
            sdk_id=sdk_id,
            name=name,
            description=description,
            api_classes=api_classes,
            version=version,
        )
        self._modules[module.id] = module
        sdk.add_module(name)
        return module

    def get_module(self, module_id: str) -> SdKModule | None:
        """Retrieve a module by its ID."""
        return self._modules.get(module_id)

    def list_modules(self, sdk_id: str) -> list[SdKModule]:
        """Return all modules belonging to a given SDK."""
        return [m for m in self._modules.values() if m.sdk_id == sdk_id]

    def delete_module(self, module_id: str, sdk_id: str) -> bool:
        """Remove a module from its SDK."""
        module = self._modules.pop(module_id, None)
        if module is None:
            return False
        sdk = self._sdks.get(sdk_id)
        if sdk is not None:
            sdk.remove_module(module.name)
        return True

    # -- Manifest management -------------------------------------------------

    def register_manifest(
        self,
        name: str,
        version: str = "1.0.0",
        author: str = "",
        description: str = "",
        dependencies: list[str] | None = None,
        permissions: list[str] | None = None,
        compatibility: str = ">=1.0",
        license: str = "MIT",
    ) -> PluginManifest:
        """Register a plugin manifest."""
        manifest = PluginManifest(
            name=name,
            version=version,
            author=author,
            description=description,
            dependencies=dependencies,
            permissions=permissions,
            compatibility=compatibility,
            license=license,
        )
        self._manifests[manifest.id] = manifest
        return manifest

    def get_manifest(self, manifest_id: str) -> PluginManifest | None:
        """Retrieve a manifest by its ID."""
        return self._manifests.get(manifest_id)

    def list_manifests(self) -> list[PluginManifest]:
        """Return all registered plugin manifests."""
        return list(self._manifests.values())

    def delete_manifest(self, manifest_id: str) -> bool:
        """Remove a manifest from the registry."""
        if manifest_id in self._manifests:
            del self._manifests[manifest_id]
            return True
        return False

    # -- Template management -------------------------------------------------

    def create_template(
        self,
        name: str,
        template_type: str = "project",
        description: str = "",
        content: dict | None = None,
        category: str = "general",
        version: str = "1.0.0",
    ) -> SdKTemplate:
        """Create a new SDK template."""
        template = SdKTemplate(
            name=name,
            template_type=template_type,
            description=description,
            content=content,
            category=category,
            version=version,
        )
        self._templates[template.id] = template
        return template

    def get_template(self, template_id: str) -> SdKTemplate | None:
        """Retrieve a template by its ID."""
        return self._templates.get(template_id)

    def list_templates(self, category: str | None = None) -> list[SdKTemplate]:
        """Return all templates, optionally filtered by category."""
        if category is None:
            return list(self._templates.values())
        return [t for t in self._templates.values() if t.category == category]

    def update_template(self, template_id: str, content: dict) -> SdKTemplate | None:
        """Replace the content of a template."""
        template = self._templates.get(template_id)
        if template is None:
            return None
        template.update_content(content)
        return template

    def delete_template(self, template_id: str) -> bool:
        """Remove a template."""
        if template_id in self._templates:
            del self._templates[template_id]
            return True
        return False
