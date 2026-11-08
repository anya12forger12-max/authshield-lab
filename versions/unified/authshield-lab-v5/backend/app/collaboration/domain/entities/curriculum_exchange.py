"""Curriculum exchange domain entities."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum


class PackageType(str, Enum):
    course = "course"
    learning_path = "learning_path"
    module = "module"
    lesson = "lesson"
    assessment = "assessment"
    simulation = "simulation"
    documentation = "documentation"
    a11y_profile = "a11y_profile"
    localization_pack = "localization_pack"
    template = "template"


class ExchangePackage:
    def __init__(
        self,
        name: str,
        description: str,
        package_type: PackageType,
        version: str,
        author: str,
        source_institution: str,
        checksum: str,
        signature: str,
        license: str,
        compatibility: str,
        dependencies: list[str] | None = None,
        metadata: dict | None = None,
        created_at: datetime | None = None,
    ) -> None:
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.package_type = package_type
        self.version = version
        self.author = author
        self.source_institution = source_institution
        self.checksum = checksum
        self.signature = signature
        self.license = license
        self.compatibility = compatibility
        self.dependencies = dependencies or []
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.now(timezone.utc)


class ExchangeItem:
    def __init__(
        self,
        name: str,
        path: str,
        size: int,
        checksum: str,
        item_type: str,
    ) -> None:
        self.name = name
        self.path = path
        self.size = size
        self.checksum = checksum
        self.item_type = item_type


class ExchangeManifest:
    def __init__(
        self,
        package_id: str,
        items: list[ExchangeItem] | None = None,
        total_size: int = 0,
        checksum: str = "",
    ) -> None:
        self.id = str(uuid.uuid4())
        self.package_id = package_id
        self.items = items or []
        self.total_size = total_size
        self.checksum = checksum


class PackageValidationReport:
    def __init__(
        self,
        package_id: str,
        integrity: bool = False,
        compatibility: bool = False,
        a11y: bool = False,
        localization: bool = False,
        documentation: bool = False,
        dependencies: bool = False,
        licensing: bool = False,
        score: float = 0.0,
        issues: list[str] | None = None,
        validated_at: datetime | None = None,
    ) -> None:
        self.id = str(uuid.uuid4())
        self.package_id = package_id
        self.integrity = integrity
        self.compatibility = compatibility
        self.a11y = a11y
        self.localization = localization
        self.documentation = documentation
        self.dependencies = dependencies
        self.licensing = licensing
        self.score = score
        self.issues = issues or []
        self.validated_at = validated_at or datetime.now(timezone.utc)


class ExchangeHistory:
    def __init__(
        self,
        package_id: str,
        action: str,
        performed_by: str,
        details: dict | None = None,
        performed_at: datetime | None = None,
    ) -> None:
        self.id = str(uuid.uuid4())
        self.package_id = package_id
        self.action = action
        self.performed_by = performed_by
        self.performed_at = performed_at or datetime.now(timezone.utc)
        self.details = details or {}
