"""Package building, validation, installation, and rollback service."""

from __future__ import annotations

import hashlib
import time
from datetime import datetime, timezone

from app.developer.domain.entities.package_builder import (
    BuildConfig,
    BuildResult,
    PackageManifest,
)


class PackageService:
    """Manages package manifests, builds, validation, installation, and rollback."""

    def __init__(self) -> None:
        self._manifests: dict[str, PackageManifest] = {}
        self._configs: dict[str, BuildConfig] = {}
        self._results: dict[str, BuildResult] = {}
        self._install_history: list[dict] = []

    # -- Manifest management -------------------------------------------------

    def create_manifest(
        self,
        name: str,
        version: str = "1.0.0",
        author: str = "",
        description: str = "",
        package_type: str = "extension",
        dependencies: list[str] | None = None,
        license: str = "MIT",
        compatibility: str = ">=1.0",
    ) -> PackageManifest:
        """Create a new package manifest."""
        manifest = PackageManifest(
            name=name,
            version=version,
            author=author,
            description=description,
            package_type=package_type,
            dependencies=dependencies,
            license=license,
            compatibility=compatibility,
        )
        self._manifests[manifest.id] = manifest
        return manifest

    def get_manifest(self, manifest_id: str) -> PackageManifest | None:
        """Retrieve a manifest by ID."""
        return self._manifests.get(manifest_id)

    def list_manifests(self) -> list[PackageManifest]:
        """Return all manifests."""
        return list(self._manifests.values())

    def update_manifest(
        self,
        manifest_id: str,
        version: str | None = None,
        description: str | None = None,
        dependencies: list[str] | None = None,
    ) -> PackageManifest | None:
        """Update mutable fields on a manifest."""
        manifest = self._manifests.get(manifest_id)
        if manifest is None:
            return None
        if version is not None:
            manifest.version = version
        if description is not None:
            manifest.description = description
        if dependencies is not None:
            manifest.dependencies = list(dependencies)
        return manifest

    def delete_manifest(self, manifest_id: str) -> bool:
        """Remove a manifest."""
        if manifest_id in self._manifests:
            del self._manifests[manifest_id]
            return True
        return False

    # -- Build config --------------------------------------------------------

    def create_build_config(
        self,
        manifest_id: str,
        sources: list[str] | None = None,
        include_docs: bool = True,
        include_tests: bool = False,
        output_format: str = "zip",
    ) -> BuildConfig | None:
        """Create a build configuration for a manifest."""
        if manifest_id not in self._manifests:
            return None
        config = BuildConfig(
            manifest_id=manifest_id,
            sources=sources,
            include_docs=include_docs,
            include_tests=include_tests,
            output_format=output_format,
        )
        self._configs[config.id] = config
        return config

    def get_build_config(self, config_id: str) -> BuildConfig | None:
        """Retrieve a build config by ID."""
        return self._configs.get(config_id)

    # -- Build operations ----------------------------------------------------

    def build_package(self, config_id: str) -> BuildResult | None:
        """Execute a build (simulated). Returns the build result."""
        config = self._configs.get(config_id)
        if config is None:
            return None
        manifest = self._manifests.get(config.manifest_id)
        start_time = time.monotonic()
        result = BuildResult(config_id=config_id)
        try:
            checksum_payload = f"{manifest.name if manifest else ''}:{config.id}".encode()
            checksum = hashlib.sha256(checksum_payload).hexdigest()
            duration = round(time.monotonic() - start_time, 4)
            output_path = f"/builds/{config.output_format}/{config.id}.{config.output_format}"
            result.mark_success(output_path=output_path, checksum=checksum, duration=duration)
            if manifest is not None:
                manifest.bundle_size = len(checksum_payload)
                manifest.checksum = checksum
        except Exception:
            result.mark_failure()
        self._results[result.id] = result
        return result

    def get_build_result(self, result_id: str) -> BuildResult | None:
        """Retrieve a build result by ID."""
        return self._results.get(result_id)

    def list_build_results(self, config_id: str | None = None) -> list[BuildResult]:
        """Return build results, optionally filtered by config."""
        if config_id is None:
            return list(self._results.values())
        return [r for r in self._results.values() if r.config_id == config_id]

    # -- Validation ----------------------------------------------------------

    def validate_manifest(self, manifest_id: str) -> dict:
        """Run basic validation checks on a manifest."""
        manifest = self._manifests.get(manifest_id)
        if manifest is None:
            return {"valid": False, "errors": ["Manifest not found"]}
        errors: list[str] = []
        if not manifest.name:
            errors.append("Name is required")
        if not manifest.version:
            errors.append("Version is required")
        if not manifest.author:
            errors.append("Author is required")
        if manifest.bundle_size < 0:
            errors.append("Bundle size must be non-negative")
        return {"valid": len(errors) == 0, "errors": errors}

    def validate_build_result(self, result_id: str) -> dict:
        """Validate that a build result is usable."""
        result = self._results.get(result_id)
        if result is None:
            return {"valid": False, "errors": ["Build result not found"]}
        errors: list[str] = []
        if result.status != "success":
            errors.append(f"Build status is '{result.status}', expected 'success'")
        if not result.checksum:
            errors.append("Missing checksum")
        if not result.output_path:
            errors.append("Missing output path")
        return {"valid": len(errors) == 0, "errors": errors}

    # -- Installation & rollback ---------------------------------------------

    def install_package(self, manifest_id: str, installed_by: str = "system") -> dict:
        """Simulate installing a package from a manifest."""
        manifest = self._manifests.get(manifest_id)
        if manifest is None:
            return {"success": False, "error": "Manifest not found"}
        record = {
            "manifest_id": manifest_id,
            "version": manifest.version,
            "installed_by": installed_by,
            "installed_at": datetime.now(timezone.utc).isoformat(),
        }
        self._install_history.append(record)
        return {"success": True, "record": record}

    def rollback_package(self, manifest_id: str) -> dict:
        """Roll back the last installation of a package."""
        manifest = self._manifests.get(manifest_id)
        if manifest is None:
            return {"success": False, "error": "Manifest not found"}
        relevant = [
            i for i, rec in enumerate(self._install_history)
            if rec["manifest_id"] == manifest_id
        ]
        if not relevant:
            return {"success": False, "error": "No installation history found"}
        last_index = relevant[-1]
        removed = self._install_history.pop(last_index)
        return {"success": True, "rolled_back": removed}

    def get_install_history(self, manifest_id: str | None = None) -> list[dict]:
        """Return installation history, optionally filtered by manifest."""
        if manifest_id is None:
            return list(self._install_history)
        return [r for r in self._install_history if r["manifest_id"] == manifest_id]
