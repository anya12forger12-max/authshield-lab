"""Marketplace domain entities."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum


class PackageCategory(str, Enum):
    course = "course"
    learning_path = "learning_path"
    plugin = "plugin"
    theme = "theme"
    template = "template"
    assessment_pack = "assessment_pack"
    scenario_collection = "scenario_collection"
    doc_pack = "doc_pack"
    accessibility_profile = "accessibility_profile"
    localization_pack = "localization_pack"


class InstallStatus(str, Enum):
    installed = "installed"
    uninstalled = "uninstalled"
    error = "error"


class LocalPackage:
    def __init__(
        self,
        name: str,
        version: str,
        author: str,
        description: str,
        category: PackageCategory,
        tags: list[str] | None = None,
        checksum: str = "",
        signature: str = "",
        license: str = "",
        compatibility: str = "",
        dependencies: list[str] | None = None,
        file_size: int = 0,
        installed: bool = False,
        favorite: bool = False,
        rating: int = 0,
        review_count: int = 0,
        created_at: datetime | None = None,
        installed_at: datetime | None = None,
    ) -> None:
        self.id = str(uuid.uuid4())
        self.name = name
        self.version = version
        self.author = author
        self.description = description
        self.category = category
        self.tags = tags or []
        self.checksum = checksum
        self.signature = signature
        self.license = license
        self.compatibility = compatibility
        self.dependencies = dependencies or []
        self.file_size = file_size
        self.installed = installed
        self.favorite = favorite
        self.rating = rating
        self.review_count = review_count
        self.created_at = created_at or datetime.now(timezone.utc)
        self.installed_at = installed_at


class PackageSearch:
    def __init__(
        self,
        query: str = "",
        category: PackageCategory | None = None,
        tags: list[str] | None = None,
        sort_by: str = "name",
        limit: int = 20,
        offset: int = 0,
    ) -> None:
        self.query = query
        self.category = category
        self.tags = tags or []
        self.sort_by = sort_by
        self.limit = limit
        self.offset = offset


class InstallationRecord:
    def __init__(
        self,
        package_id: str,
        installed_by: str,
        version: str,
        status: InstallStatus = InstallStatus.installed,
        config: dict | None = None,
        installed_at: datetime | None = None,
    ) -> None:
        self.id = str(uuid.uuid4())
        self.package_id = package_id
        self.installed_by = installed_by
        self.installed_at = installed_at or datetime.now(timezone.utc)
        self.version = version
        self.status = status
        self.config = config or {}
