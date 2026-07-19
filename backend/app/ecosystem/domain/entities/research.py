"""Research domain entities."""

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
        title: str,
        description: str = "",
        status: ResearchStatus = ResearchStatus.active,
    ) -> None:
        self.id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.status = status
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)


class LiteratureEntry:
    def __init__(
        self,
        project_id: str,
        title: str,
        author: str = "",
        year: int = 0,
        source: str = "",
        abstract: str = "",
        keywords: list[str] | None = None,
        notes: str = "",
        read_status: ReadStatus = ReadStatus.unread,
    ) -> None:
        self.id = str(uuid.uuid4())
        self.project_id = project_id
        self.title = title
        self.author = author
        self.year = year
        self.source = source
        self.abstract = abstract
        self.keywords = keywords or []
        self.notes = notes
        self.read_status = read_status
        self.added_at = datetime.now(timezone.utc)


class ResearchNote:
    def __init__(
        self,
        entry_id: str,
        content: str,
    ) -> None:
        self.id = str(uuid.uuid4())
        self.entry_id = entry_id
        self.content = content
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)


class KnowledgeConcept:
    def __init__(
        self,
        map_id: str,
        name: str,
        description: str = "",
        category: str = "",
    ) -> None:
        self.id = str(uuid.uuid4())
        self.map_id = map_id
        self.name = name
        self.description = description
        self.category = category


class KnowledgeLink:
    def __init__(
        self,
        source_id: str,
        target_id: str,
        relationship: str = "",
        weight: float = 1.0,
    ) -> None:
        self.id = str(uuid.uuid4())
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
        entries: list[str] | None = None,
    ) -> None:
        self.id = str(uuid.uuid4())
        self.project_id = project_id
        self.name = name
        self.entries = entries or []
        self.created_at = datetime.now(timezone.utc)


class Bibliography:
    def __init__(
        self,
        project_id: str,
        name: str = "default",
        entries: list[str] | None = None,
        format: str = "apa",
    ) -> None:
        self.id = str(uuid.uuid4())
        self.project_id = project_id
        self.name = name
        self.entries = entries or []
        self.format = format
        self.generated_at = datetime.now(timezone.utc)
