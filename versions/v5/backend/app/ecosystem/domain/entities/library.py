"""Library domain entities."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum


class LibraryItemType(str, Enum):
    book = "book"
    manual = "manual"
    whitepaper = "whitepaper"
    documentation = "documentation"
    architecture_ref = "architecture_ref"
    compliance_ref = "compliance_ref"
    a11y_guide = "a11y_guide"
    research_paper = "research_paper"
    policy = "policy"
    technical_standard = "technical_standard"


class LibraryItem:
    def __init__(
        self,
        title: str,
        author: str,
        item_type: LibraryItemType,
        description: str = "",
        tags: list[str] | None = None,
        category: str = "",
        format: str = "pdf",
        file_path: str = "",
        page_count: int = 0,
        bookmarked: bool = False,
    ) -> None:
        self.id = str(uuid.uuid4())
        self.title = title
        self.author = author
        self.item_type = item_type
        self.description = description
        self.tags = tags or []
        self.category = category
        self.format = format
        self.file_path = file_path
        self.page_count = page_count
        self.bookmarked = bookmarked
        self.created_at = datetime.now(timezone.utc)
        self.accessed_at = None


class Bookmark:
    def __init__(
        self,
        item_id: str,
        user_id: str,
        note: str = "",
        page: int = 0,
    ) -> None:
        self.id = str(uuid.uuid4())
        self.item_id = item_id
        self.user_id = user_id
        self.note = note
        self.page = page
        self.created_at = datetime.now(timezone.utc)


class Annotation:
    def __init__(
        self,
        item_id: str,
        user_id: str,
        text: str,
        highlight: str = "",
        page: int = 0,
    ) -> None:
        self.id = str(uuid.uuid4())
        self.item_id = item_id
        self.user_id = user_id
        self.text = text
        self.highlight = highlight
        self.page = page
        self.created_at = datetime.now(timezone.utc)


class Citation:
    def __init__(
        self,
        source_item_id: str,
        target_item_id: str,
        citation_type: str,
        page: int = 0,
        note: str = "",
    ) -> None:
        self.id = str(uuid.uuid4())
        self.source_item_id = source_item_id
        self.target_item_id = target_item_id
        self.citation_type = citation_type
        self.page = page
        self.note = note
