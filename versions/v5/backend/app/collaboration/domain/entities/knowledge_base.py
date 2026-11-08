"""Knowledge base domain entities."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum


class ArticleStatus(str, Enum):
    draft = "draft"
    published = "published"
    archived = "archived"


class KnowledgeArticle:
    def __init__(
        self,
        title: str,
        content: str,
        category: str,
        author: str,
        tags: list[str] | None = None,
        version: int = 1,
        status: ArticleStatus = ArticleStatus.draft,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self.id = str(uuid.uuid4())
        self.title = title
        self.content = content
        self.category = category
        self.tags = tags or []
        self.author = author
        self.version = version
        self.status = status
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)


class KnowledgeCategory:
    def __init__(
        self,
        name: str,
        description: str,
        parent_id: str | None = None,
        article_count: int = 0,
    ) -> None:
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.parent_id = parent_id
        self.article_count = article_count


class ArticleVersion:
    def __init__(
        self,
        article_id: str,
        version: int,
        content: str,
        author: str,
        created_at: datetime | None = None,
    ) -> None:
        self.article_id = article_id
        self.version = version
        self.content = content
        self.author = author
        self.created_at = created_at or datetime.now(timezone.utc)


class ArticleCitation:
    def __init__(
        self,
        source_id: str,
        target_id: str,
        citation_type: str,
    ) -> None:
        self.id = str(uuid.uuid4())
        self.source_id = source_id
        self.target_id = target_id
        self.citation_type = citation_type


class ArticleSearchResult:
    def __init__(
        self,
        article_id: str,
        title: str,
        snippet: str,
        category: str,
        relevance: float = 0.0,
    ) -> None:
        self.article_id = article_id
        self.title = title
        self.snippet = snippet
        self.category = category
        self.relevance = relevance
