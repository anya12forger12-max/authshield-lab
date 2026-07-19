"""Domain events for the collaboration module."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from dataclasses import dataclass, field


@dataclass
class DomainEvent:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class PackageExchanged(DomainEvent):
    package_id: str = ""
    package_name: str = ""
    version: str = ""
    source_institution: str = ""
    performed_by: str = ""


@dataclass
class ReviewSubmitted(DomainEvent):
    review_id: str = ""
    title: str = ""
    submitter: str = ""
    content_type: str = ""


@dataclass
class ReviewApproved(DomainEvent):
    review_id: str = ""
    title: str = ""
    stage: str = ""
    reviewer: str = ""


@dataclass
class ResearchProjectCreated(DomainEvent):
    project_id: str = ""
    name: str = ""
    principal_investigator: str = ""


@dataclass
class KnowledgeArticlePublished(DomainEvent):
    article_id: str = ""
    title: str = ""
    author: str = ""
    category: str = ""


@dataclass
class ResourceImported(DomainEvent):
    resource_id: str = ""
    package_id: str = ""
    imported_by: str = ""
    status: str = ""


@dataclass
class PublicationQueued(DomainEvent):
    item_id: str = ""
    content_id: str = ""
    content_type: str = ""
    title: str = ""
    submitted_by: str = ""
