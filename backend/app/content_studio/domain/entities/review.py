"""Review and editorial workflow domain entities."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class ReviewStage(str, Enum):
    DRAFT = "draft"
    PEER_REVIEW = "peer_review"
    TECHNICAL_REVIEW = "technical_review"
    A11Y_REVIEW = "a11y_review"
    EDUCATIONAL_REVIEW = "educational_review"
    LOCALIZATION_REVIEW = "localization_review"
    APPROVAL = "approval"
    PUBLICATION = "publication"
    ARCHIVE = "archive"


STAGE_ORDER: dict[ReviewStage, int] = {
    ReviewStage.DRAFT: 0,
    ReviewStage.PEER_REVIEW: 1,
    ReviewStage.TECHNICAL_REVIEW: 2,
    ReviewStage.A11Y_REVIEW: 3,
    ReviewStage.EDUCATIONAL_REVIEW: 4,
    ReviewStage.LOCALIZATION_REVIEW: 5,
    ReviewStage.APPROVAL: 6,
    ReviewStage.PUBLICATION: 7,
    ReviewStage.ARCHIVE: 8,
}


class ReviewDecisionType(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"


@dataclass
class EditorialReview:
    """Tracks an editorial review process for content."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str = ""
    content_type: str = ""
    current_stage: ReviewStage = ReviewStage.DRAFT
    submitter: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def advance_stage(self) -> ReviewStage | None:
        current_idx = STAGE_ORDER.get(self.current_stage, 0)
        stages = sorted(STAGE_ORDER.items(), key=lambda x: x[1])
        for stage, idx in stages:
            if idx > current_idx:
                self.current_stage = stage
                return stage
        return None

    def set_stage(self, stage: ReviewStage) -> None:
        self.current_stage = stage

    def is_past_stage(self, target: ReviewStage) -> bool:
        return STAGE_ORDER.get(self.current_stage, 0) > STAGE_ORDER.get(target, 0)

    def is_at_or_past_stage(self, target: ReviewStage) -> bool:
        return STAGE_ORDER.get(self.current_stage, 0) >= STAGE_ORDER.get(target, 0)

    def is_complete(self) -> bool:
        return self.current_stage in {ReviewStage.PUBLICATION, ReviewStage.ARCHIVE}

    def get_stage_progress_pct(self) -> float:
        current = STAGE_ORDER.get(self.current_stage, 0)
        total = len(STAGE_ORDER) - 1
        if total == 0:
            return 0.0
        return round(current / total * 100, 1)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "content_id": self.content_id,
            "content_type": self.content_type,
            "current_stage": self.current_stage.value,
            "submitter": self.submitter,
            "created_at": self.created_at.isoformat(),
            "progress_pct": self.get_stage_progress_pct(),
        }


@dataclass
class ReviewComment:
    """A comment left during editorial review."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    review_id: str = ""
    author: str = ""
    stage: ReviewStage = ReviewStage.DRAFT
    comment: str = ""
    severity: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def is_critical(self) -> bool:
        return self.severity == "critical"

    def is_suggestion(self) -> bool:
        return self.severity == "suggestion"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "review_id": self.review_id,
            "author": self.author,
            "stage": self.stage.value,
            "comment": self.comment,
            "severity": self.severity,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class ReviewDecision:
    """A formal decision made by a reviewer on content."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    review_id: str = ""
    stage: ReviewStage = ReviewStage.DRAFT
    reviewer: str = ""
    decision: ReviewDecisionType = ReviewDecisionType.APPROVED
    comments: str = ""
    decided_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def is_approved(self) -> bool:
        return self.decision == ReviewDecisionType.APPROVED

    def is_rejected(self) -> bool:
        return self.decision == ReviewDecisionType.REJECTED

    def needs_revision(self) -> bool:
        return self.decision == ReviewDecisionType.NEEDS_REVISION

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "review_id": self.review_id,
            "stage": self.stage.value,
            "reviewer": self.reviewer,
            "decision": self.decision.value,
            "comments": self.comments,
            "decided_at": self.decided_at.isoformat(),
        }


@dataclass
class ReviewEvent:
    """An event emitted during the review workflow."""

    review_id: str = ""
    stage: ReviewStage = ReviewStage.DRAFT
    action: str = ""
    actor: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "review_id": self.review_id,
            "stage": self.stage.value,
            "action": self.action,
            "actor": self.actor,
            "timestamp": self.timestamp.isoformat(),
        }
