"""PackageManifest, BuildConfig, and BuildResult entities."""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone


class PackageManifest:
    """Metadata describing a distributable package."""

    def __init__(
        self,
        id: str | None = None,
        name: str = "",
        version: str = "1.0.0",
        author: str = "",
        description: str = "",
        package_type: str = "extension",
        dependencies: list[str] | None = None,
        license: str = "MIT",
        compatibility: str = ">=1.0",
        checksum: str = "",
        bundle_size: int = 0,
        created_at: datetime | None = None,
    ) -> None:
        self.id: str = id or str(uuid.uuid4())
        self.name: str = name
        self.version: str = version
        self.author: str = author
        self.description: str = description
        self.package_type: str = package_type
        self.dependencies: list[str] = dependencies if dependencies is not None else []
        self.license: str = license
        self.compatibility: str = compatibility
        self.checksum: str = checksum
        self.bundle_size: int = bundle_size
        self.created_at: datetime = created_at or datetime.now(timezone.utc)

    def compute_checksum(self, payload: bytes) -> str:
        """Compute SHA-256 checksum over the given payload."""
        self.checksum = hashlib.sha256(payload).hexdigest()
        return self.checksum

    def has_dependency(self, dep_name: str) -> bool:
        """Check whether a dependency is listed."""
        return dep_name in self.dependencies

    def add_dependency(self, dep_name: str) -> None:
        """Add a dependency if not already present."""
        if dep_name not in self.dependencies:
            self.dependencies.append(dep_name)

    def remove_dependency(self, dep_name: str) -> None:
        """Remove a dependency."""
        if dep_name in self.dependencies:
            self.dependencies.remove(dep_name)

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "package_type": self.package_type,
            "dependencies": list(self.dependencies),
            "license": self.license,
            "compatibility": self.compatibility,
            "checksum": self.checksum,
            "bundle_size": self.bundle_size,
            "created_at": self.created_at.isoformat(),
        }


class BuildConfig:
    """Configuration for building a package from source."""

    def __init__(
        self,
        id: str | None = None,
        manifest_id: str = "",
        sources: list[str] | None = None,
        include_docs: bool = True,
        include_tests: bool = False,
        output_format: str = "zip",
    ) -> None:
        self.id: str = id or str(uuid.uuid4())
        self.manifest_id: str = manifest_id
        self.sources: list[str] = sources if sources is not None else []
        self.include_docs: bool = include_docs
        self.include_tests: bool = include_tests
        self.output_format: str = output_format

    def add_source(self, source_path: str) -> None:
        """Register a source directory or file."""
        if source_path not in self.sources:
            self.sources.append(source_path)

    def remove_source(self, source_path: str) -> None:
        """Remove a registered source path."""
        if source_path in self.sources:
            self.sources.remove(source_path)

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "id": self.id,
            "manifest_id": self.manifest_id,
            "sources": list(self.sources),
            "include_docs": self.include_docs,
            "include_tests": self.include_tests,
            "output_format": self.output_format,
        }


class BuildResult:
    """Outcome of a package build operation."""

    def __init__(
        self,
        id: str | None = None,
        config_id: str = "",
        output_path: str = "",
        status: str = "pending",
        checksum: str = "",
        built_at: datetime | None = None,
        duration_seconds: float = 0.0,
    ) -> None:
        self.id: str = id or str(uuid.uuid4())
        self.config_id: str = config_id
        self.output_path: str = output_path
        self.status: str = status
        self.checksum: str = checksum
        self.built_at: datetime = built_at or datetime.now(timezone.utc)
        self.duration_seconds: float = duration_seconds

    def mark_success(self, output_path: str, checksum: str, duration: float) -> None:
        """Record a successful build."""
        self.status = "success"
        self.output_path = output_path
        self.checksum = checksum
        self.duration_seconds = duration
        self.built_at = datetime.now(timezone.utc)

    def mark_failure(self) -> None:
        """Record a failed build."""
        self.status = "failed"
        self.built_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "id": self.id,
            "config_id": self.config_id,
            "output_path": self.output_path,
            "status": self.status,
            "checksum": self.checksum,
            "built_at": self.built_at.isoformat(),
            "duration_seconds": self.duration_seconds,
        }
