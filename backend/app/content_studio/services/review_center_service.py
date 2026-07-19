"""Review center service — editorial workflow, stages, comments, decisions."""

from __future__ import annotations

import logging
from typing import Any, Optional

from ..domain.entities.review import (
    EditorialReview,
    ReviewComment,
    ReviewDecision,
    ReviewDecisionType,
    ReviewEvent,
    ReviewStage,
)
from ..domain.events.content_studio_events import ReviewAdvanced
from ..domain.interfaces.content_studio_interfaces import (
    IEditorialReviewRepository,
    IReviewCommentRepository,
    IReviewDecisionRepository,
)

logger = logging.getLogger(__name__)


class ReviewCenterService:
    """Service for the editorial review workflow."""

    def __init__(
        self,
        review_repo: IEditorialReviewRepository,
        comment_repo: IReviewCommentRepository,
        decision_repo: IReviewDecisionRepository,
    ) -> None:
        self._review_repo = review_repo
        self._comment_repo = comment_repo
        self._decision_repo = decision_repo

    def create_review(
        self,
        content_id: str,
        content_type: str,
        submitter: str,
    ) -> dict[str, Any]:
        existing = self._review_repo.get_by_content(content_id)
        if existing:
            raise ValueError(f"Review already exists for content '{content_id}'.")

        review = EditorialReview(
            content_id=content_id,
            content_type=content_type,
            submitter=submitter,
        )
        result = self._review_repo.create({
            "id": review.id,
            "content_id": content_id,
            "content_type": content_type,
            "current_stage": review.current_stage.value,
            "submitter": submitter,
        })
        logger.info("editorial_review_created", extra={"review_id": result["id"], "content_id": content_id})
        return result

    def get_review(self, review_id: str) -> Optional[dict[str, Any]]:
        return self._review_repo.get_by_id(review_id)

    def get_review_by_content(self, content_id: str) -> Optional[dict[str, Any]]:
        return self._review_repo.get_by_content(content_id)

    def list_reviews(
        self, page: int = 1, per_page: int = 20, stage: Optional[str] = None
    ) -> dict[str, Any]:
        return self._review_repo.get_all(page=page, per_page=per_page, stage=stage)

    def advance_review(self, review_id: str) -> dict[str, Any]:
        existing = self._review_repo.get_by_id(review_id)
        if not existing:
            raise ValueError(f"Review '{review_id}' not found.")

        current_stage = ReviewStage(existing.get("current_stage", "draft"))
        if current_stage in {ReviewStage.PUBLICATION, ReviewStage.ARCHIVE}:
            raise ValueError(f"Review is already at terminal stage '{current_stage.value}'.")

        stages = sorted(ReviewStage.__members__.values(), key=lambda s: list(ReviewStage).index(s))
        current_idx = stages.index(current_stage) if current_stage in stages else -1
        if current_idx < len(stages) - 1:
            next_stage = stages[current_idx + 1]
        else:
            next_stage = current_stage

        updated = self._review_repo.update(review_id, {"current_stage": next_stage.value})

        event = ReviewAdvanced(
            review_id=review_id,
            content_id=existing.get("content_id", ""),
            from_stage=current_stage.value,
            to_stage=next_stage.value,
        )
        logger.info("review_advanced", extra={
            "review_id": review_id,
            "from_stage": current_stage.value,
            "to_stage": next_stage.value,
            "event_id": event.event_id,
        })
        return updated or existing

    def set_stage(self, review_id: str, stage: str) -> dict[str, Any]:
        existing = self._review_repo.get_by_id(review_id)
        if not existing:
            raise ValueError(f"Review '{review_id}' not found.")

        valid_stages = {s.value for s in ReviewStage}
        if stage not in valid_stages:
            raise ValueError(f"Invalid stage '{stage}'. Must be one of: {valid_stages}")

        updated = self._review_repo.update(review_id, {"current_stage": stage})
        return updated or existing

    def add_comment(
        self,
        review_id: str,
        author: str,
        comment_text: str,
        severity: str | None = None,
    ) -> dict[str, Any]:
        existing = self._review_repo.get_by_id(review_id)
        if not existing:
            raise ValueError(f"Review '{review_id}' not found.")

        current_stage = ReviewStage(existing.get("current_stage", "draft"))
        comment = ReviewComment(
            review_id=review_id,
            author=author,
            stage=current_stage,
            comment=comment_text,
            severity=severity,
        )
        result = self._comment_repo.create({
            "id": comment.id,
            "review_id": review_id,
            "author": author,
            "stage": current_stage.value,
            "comment": comment_text,
            "severity": severity,
        })
        logger.info("review_comment_added", extra={"review_id": review_id, "comment_id": result["id"]})
        return result

    def get_comments(self, review_id: str) -> list[dict[str, Any]]:
        return self._comment_repo.get_by_review(review_id)

    def add_decision(
        self,
        review_id: str,
        reviewer: str,
        decision_type: str,
        comments: str = "",
    ) -> dict[str, Any]:
        existing = self._review_repo.get_by_id(review_id)
        if not existing:
            raise ValueError(f"Review '{review_id}' not found.")

        valid_decisions = {d.value for d in ReviewDecisionType}
        if decision_type not in valid_decisions:
            raise ValueError(f"Invalid decision '{decision_type}'. Must be one of: {valid_decisions}")

        current_stage = ReviewStage(existing.get("current_stage", "draft"))
        decision = ReviewDecision(
            review_id=review_id,
            stage=current_stage,
            reviewer=reviewer,
            decision=ReviewDecisionType(decision_type),
            comments=comments,
        )
        result = self._decision_repo.create({
            "id": decision.id,
            "review_id": review_id,
            "stage": current_stage.value,
            "reviewer": reviewer,
            "decision": decision_type,
            "comments": comments,
            "decided_at": decision.decided_at.isoformat(),
        })

        if decision_type == "approved":
            self.advance_review(review_id)
        elif decision_type == "needs_revision":
            self._review_repo.update(review_id, {"current_stage": ReviewStage.DRAFT.value})

        logger.info("review_decision_added", extra={
            "review_id": review_id,
            "decision": decision_type,
            "reviewer": reviewer,
        })
        return result

    def get_decisions(self, review_id: str) -> list[dict[str, Any]]:
        return self._decision_repo.get_by_review(review_id)

    def get_latest_decision(self, review_id: str) -> Optional[dict[str, Any]]:
        return self._decision_repo.get_latest(review_id)

    def get_review_progress(self, review_id: str) -> dict[str, Any]:
        existing = self._review_repo.get_by_id(review_id)
        if not existing:
            raise ValueError(f"Review '{review_id}' not found.")

        current_stage = ReviewStage(existing.get("current_stage", "draft"))
        stages_order = list(ReviewStage)
        current_idx = stages_order.index(current_stage) if current_stage in stages_order else 0

        comments = self._comment_repo.get_by_review(review_id)
        decisions = self._decision_repo.get_by_review(review_id)
        critical_comments = [c for c in comments if c.get("severity") == "critical"]

        return {
            "review_id": review_id,
            "current_stage": current_stage.value,
            "total_stages": len(stages_order),
            "completed_stages": current_idx,
            "progress_pct": round(current_idx / (len(stages_order) - 1) * 100, 1) if len(stages_order) > 1 else 0,
            "total_comments": len(comments),
            "critical_comments": len(critical_comments),
            "total_decisions": len(decisions),
            "has_rejections": any(d.get("decision") == "rejected" for d in decisions),
        }
