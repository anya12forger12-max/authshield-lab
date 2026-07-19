"""Peer review domain entities."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum


class ReviewStage(str, Enum):
    draft = "draft"
    internal_review = "internal_review"
    a11y_review = "a11y_review"
    technical_review = "technical_review"
    educational_review = "educational_review"
    approval = "approval"
    publication = "publication"
    archive = "archive"


class ReviewDecisionType(str, Enum):
    approved = "approved"
    rejected = "rejected"
    needs_revision = "needs_revision"


class PeerReview:
    def __init__(
        self,
        title: str,
        content_id: str,
        content_type: str,
        submitter: str,
        current_stage: ReviewStage = ReviewStage.draft,
        created_at: datetime | None = None,
    ) -> None:
        self.id = str(uuid.uuid4())
        self.title = title
        self.content_id = content_id
        self.content_type = content_type
        self.current_stage = current_stage
        self.submitter = submitter
        self.created_at = created_at or datetime.now(timezone.utc)


class ReviewComment:
    def __init__(
        self,
        review_id: str,
        author: str,
        stage: ReviewStage,
        comment: str,
        severity: str | None = None,
        created_at: datetime | None = None,
    ) -> None:
        self.id = str(uuid.uuid4())
        self.review_id = review_id
        self.author = author
        self.stage = stage
        self.comment = comment
        self.severity = severity
        self.created_at = created_at or datetime.now(timezone.utc)


class ReviewDecision:
    def __init__(
        self,
        review_id: str,
        stage: ReviewStage,
        reviewer: str,
        decision: ReviewDecisionType,
        comments: str = "",
        decided_at: datetime | None = None,
    ) -> None:
        self.id = str(uuid.uuid4())
        self.review_id = review_id
        self.stage = stage
        self.reviewer = reviewer
        self.decision = decision
        self.comments = comments
        self.decided_at = decided_at or datetime.now(timezone.utc)


class ReviewRevision:
    def __init__(
        self,
        review_id: str,
        revision_number: int,
        changes: list[str] | None = None,
        author: str = "",
        created_at: datetime | None = None,
    ) -> None:
        self.id = str(uuid.uuid4())
        self.review_id = review_id
        self.revision_number = revision_number
        self.changes = changes or []
        self.author = author
        self.created_at = created_at or datetime.now(timezone.utc)


class ReviewEvent:
    def __init__(
        self,
        stage: ReviewStage,
        action: str,
        actor: str,
        timestamp: datetime | None = None,
        details: str = "",
    ) -> None:
        self.stage = stage
        self.action = action
        self.actor = actor
        self.timestamp = timestamp or datetime.now(timezone.utc)
        self.details = details


class ReviewHistory:
    def __init__(
        self,
        review_id: str,
        events: list[ReviewEvent] | None = None,
    ) -> None:
        self.id = str(uuid.uuid4())
        self.review_id = review_id
        self.events = events or []
