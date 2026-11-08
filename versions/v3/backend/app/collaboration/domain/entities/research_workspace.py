"""Research workspace domain entities."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum


class ResearchStatus(str, Enum):
    active = "active"
    paused = "paused"
    completed = "completed"


class ReadStatus(str, Enum):
    unread = "unread"
    reading = "reading"
    read = "read"


class ResearchProject:
    def __init__(
        self,
        name: str,
        description: str,
        principal_investigator: str,
        status: ResearchStatus = ResearchStatus.active,
        team: list[str] | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.status = status
        self.principal_investigator = principal_investigator
        self.team = team or []
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)


class LiteratureEntry:
    def __init__(
        self,
        title: str,
        author: str,
        year: int,
        source: str,
        abstract: str,
        keywords: list[str] | None = None,
        notes: str = "",
        read_status: ReadStatus = ReadStatus.unread,
    ) -> None:
        self.id = str(uuid.uuid4())
        self.title = title
        self.author = author
        self.year = year
        self.source = source
        self.abstract = abstract
        self.keywords = keywords or []
        self.notes = notes
        self.read_status = read_status


class LiteratureCollection:
    def __init__(
        self,
        project_id: str,
        name: str,
        entries: list[LiteratureEntry] | None = None,
    ) -> None:
        self.id = str(uuid.uuid4())
        self.project_id = project_id
        self.name = name
        self.entries = entries or []


class ResearchNote:
    def __init__(
        self,
        entry_id: str,
        content: str,
        created_by: str,
        created_at: datetime | None = None,
    ) -> None:
        self.id = str(uuid.uuid4())
        self.entry_id = entry_id
        self.content = content
        self.created_by = created_by
        self.created_at = created_at or datetime.now(timezone.utc)


class Citation:
    def __init__(
        self,
        source_id: str,
        target_id: str,
        citation_type: str,
        page: int = 0,
        note: str = "",
    ) -> None:
        self.id = str(uuid.uuid4())
        self.source_id = source_id
        self.target_id = target_id
        self.citation_type = citation_type
        self.page = page
        self.note = note


class KnowledgeConcept:
    def __init__(
        self,
        name: str,
        description: str,
        category: str,
    ) -> None:
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.category = category


class KnowledgeLink:
    def __init__(
        self,
        source_id: str,
        target_id: str,
        relationship: str,
        weight: float = 1.0,
    ) -> None:
        self.source_id = source_id
        self.target_id = target_id
        self.relationship = relationship
        self.weight = weight


class KnowledgeMap:
    def __init__(
        self,
        project_id: str,
        name: str,
        concepts: list[KnowledgeConcept] | None = None,
        links: list[KnowledgeLink] | None = None,
    ) -> None:
        self.id = str(uuid.uuid4())
        self.project_id = project_id
        self.name = name
        self.concepts = concepts or []
        self.links = links or []


class ReadingList:
    def __init__(
        self,
        project_id: str,
        name: str,
        item_ids: list[str] | None = None,
        created_at: datetime | None = None,
    ) -> None:
        self.id = str(uuid.uuid4())
        self.project_id = project_id
        self.name = name
        self.item_ids = item_ids or []
        self.created_at = created_at or datetime.now(timezone.utc)


class Bibliography:
    def __init__(
        self,
        project_id: str,
        name: str,
        entries: list[str] | None = None,
        format: str = "apa",
        generated_at: datetime | None = None,
    ) -> None:
        self.id = str(uuid.uuid4())
        self.project_id = project_id
        self.name = name
        self.entries = entries or []
        self.format = format
        self.generated_at = generated_at or datetime.now(timezone.utc)
