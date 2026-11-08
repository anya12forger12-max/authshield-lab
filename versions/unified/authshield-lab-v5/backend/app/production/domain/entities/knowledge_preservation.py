"""Knowledge preservation domain entities."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class ArchitectureDecisionRecord:
    """Records a key architectural decision and its rationale."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    status: str = "proposed"
    context: str = ""
    decision: str = ""
    consequences: str = ""
    alternatives: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    reviewed_at: datetime | None = None


@dataclass
class MigrationHistory:
    """Tracks a completed or in-progress version migration."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    from_version: str = ""
    to_version: str = ""
    migration_date: str = ""
    status: str = ""
    steps_completed: int = 0
    total_steps: int = 0
    notes: str = ""


@dataclass
class ReleaseHistory:
    """A historical record of a published release."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    release_id: str = ""
    version: str = ""
    release_date: str = ""
    summary: str = ""


@dataclass
class KnowledgeEntry:
    """A documented piece of project knowledge."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    category: str = ""
    content: str = ""
    tags: list[str] = field(default_factory=list)
    version: str = ""
    author: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class CodingStandard:
    """A documented coding standard with examples and references."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    category: str = ""
    description: str = ""
    examples: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)
