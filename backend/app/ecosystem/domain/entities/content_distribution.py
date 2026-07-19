"""Content distribution domain entities."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone


class DistributionPackage:
    def __init__(
        self,
        name: str,
        description: str = "",
        content_type: str = "",
        version: str = "1.0.0",
        checksum: str = "",
        signature: str = "",
        created_by: str = "",
        exported: bool = False,
        imported: bool = False,
    ) -> None:
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.content_type = content_type
        self.version = version
        self.checksum = checksum
        self.signature = signature
        self.created_by = created_by
        self.created_at = datetime.now(timezone.utc)
        self.exported = exported
        self.imported = imported


class DistributionItem:
    def __init__(
        self,
        name: str,
        path: str,
        size: int = 0,
        checksum: str = "",
        item_type: str = "file",
    ) -> None:
        self.name = name
        self.path = path
        self.size = size
        self.checksum = checksum
        self.item_type = item_type


class DistributionManifest:
    def __init__(
        self,
        package_id: str,
        items: list[DistributionItem] | None = None,
        total_size: int = 0,
        compatibility: str = "",
    ) -> None:
        self.id = str(uuid.uuid4())
        self.package_id = package_id
        self.items = items or []
        self.total_size = total_size
        self.compatibility = compatibility


class ImportRecord:
    def __init__(
        self,
        package_id: str,
        imported_by: str,
        status: str = "pending",
        conflicts: list[str] | None = None,
    ) -> None:
        self.id = str(uuid.uuid4())
        self.package_id = package_id
        self.imported_by = imported_by
        self.imported_at = datetime.now(timezone.utc)
        self.status = status
        self.conflicts = conflicts or []


class SyncOperation:
    def __init__(
        self,
        name: str,
        source: str,
        destination: str,
        status: str = "pending",
        items_processed: int = 0,
        items_conflict: int = 0,
    ) -> None:
        self.id = str(uuid.uuid4())
        self.name = name
        self.source = source
        self.destination = destination
        self.status = status
        self.items_processed = items_processed
        self.items_conflict = items_conflict
        self.started_at = datetime.now(timezone.utc)
        self.completed_at = None
