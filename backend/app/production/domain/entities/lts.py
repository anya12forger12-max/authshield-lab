"""Long-term support version domain entities."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class LtsVersion:
    """A long-term support release track."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    version: str = ""
    release_date: str = ""
    end_of_support: str = ""
    status: str = "active"
    compatible_versions: list[str] = field(default_factory=list)
    migration_path: str = ""
    notes: str = ""


@dataclass
class MigrationStep:
    """A single step in a version migration path."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    from_version: str = ""
    to_version: str = ""
    step_number: int = 0
    description: str = ""
    requires_backup: bool = False
    estimated_minutes: int = 0
    rollback_available: bool = True


@dataclass
class CompatibilityMatrix:
    """Compatibility record between two specific versions."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    version_a: str = ""
    version_b: str = ""
    compatible: bool = True
    notes: str = ""
    checked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class DeprecationEntry:
    """Tracks deprecated features and their replacement roadmap."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    feature: str = ""
    deprecated_in_version: str = ""
    replacement: str = ""
    removal_version: str = ""
    announced_at: str = ""
