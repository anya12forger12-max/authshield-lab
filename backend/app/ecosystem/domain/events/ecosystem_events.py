"""Domain events for the ecosystem module."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from dataclasses import dataclass, field


@dataclass
class DomainEvent:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class PackageInstalled(DomainEvent):
    package_id: str = ""
    package_name: str = ""
    version: str = ""
    installed_by: str = ""


@dataclass
class PackageRemoved(DomainEvent):
    package_id: str = ""
    package_name: str = ""
    version: str = ""
    removed_by: str = ""


@dataclass
class LibraryItemAdded(DomainEvent):
    item_id: str = ""
    title: str = ""
    item_type: str = ""
    added_by: str = ""


@dataclass
class ResearchProjectCreated(DomainEvent):
    project_id: str = ""
    title: str = ""
    created_by: str = ""


@dataclass
class DistributionExported(DomainEvent):
    package_id: str = ""
    package_name: str = ""
    exported_by: str = ""


@dataclass
class DistributionImported(DomainEvent):
    package_id: str = ""
    package_name: str = ""
    imported_by: str = ""
    status: str = ""


@dataclass
class OrganizationCreated(DomainEvent):
    org_id: str = ""
    org_name: str = ""
    org_type: str = ""
    created_by: str = ""
