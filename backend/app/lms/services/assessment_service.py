"""Assessment management service for the LMS module."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Optional

from ..domain.entities.assessment_lms import AssessmentStatus
from ..domain.events.lms_events import AssessmentAttempted
from ..domain.interfaces.lms_interfaces import IAssessmentRepository
from ..validators.lms_validator import validate_assessment_data

logger = logging.getLogger(__name__)


class AssessmentLmsService:
    """Service for managing assessments, attempts, submissions, and question groups."""

    def __init__(self, assessment_repo: IAssessmentRepository) -> None:
        self._repo = assessment_repo

    def create_assessment(self, data: dict[str, Any]) -> dict[str, Any]:
        validation = validate_assessment_data(data)
        if not validation.is_valid:
            raise ValueError(f"Validation failed: {validation.to_dict()}")
        return self._repo.create(data)

    def get_assessment(self, assessment_id: str) -> Optional[dict[str, Any]]:
        return self._repo.get_by_id(assessment_id)

    def list_assessments_by_course(self, course_id: str) -> list[dict[str, Any]]:
        return self._repo.get_by_course(course_id)

    def update_assessment(
        self, assessment_id: str, data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
        existing = self._repo.get_by_id(assessment_id)
        if not existing:
            raise ValueError(f"Assessment '{assessment_id}' not found.")
        return self._repo.update(assessment_id, data)

    def delete_assessment(self, assessment_id: str) -> bool:
        if not self._repo.get_by_id(assessment_id):
            raise ValueError(f"Assessment '{assessment_id}' not found.")
        return self._repo.delete(assessment_id)

    def publish_assessment(self, assessment_id: str) -> dict[str, Any]:
        assessment = self._repo.get_by_id(assessment_id)
        if not assessment:
            raise ValueError(f"Assessment '{assessment_id}' not found.")
        if assessment.get("status") != "draft":
            raise ValueError(f"Cannot publish assessment in '{assessment.get('status')}' status.")
        updated = self._repo.update(assessment_id, {"status": "published"})
        return updated or assessment

    def close_assessment(self, assessment_id: str) -> dict[str, Any]:
        assessment = self._repo.get_by_id(assessment_id)
        if not assessment:
            raise ValueError(f"Assessment '{assessment_id}' not found.")
        if assessment.get("status") != "published":
            raise ValueError(f"Cannot close assessment in '{assessment.get('status')}' status.")
        updated = self._repo.update(assessment_id, {"status": "closed"})
        return updated or assessment

    def start_attempt(self, assessment_id: str, learner_id: str) -> dict[str, Any]:
        assessment = self._repo.get_by_id(assessment_id)
        if not assessment:
            raise ValueError(f"Assessment '{assessment_id}' not found.")
        if assessment.get("status") != "published":
            raise ValueError("Assessment is not published.")

        attempts = self._repo.get_attempts(assessment_id, learner_id)
        attempts_allowed = assessment.get("attempts_allowed", 1)
        if len(attempts) >= attempts_allowed:
            raise ValueError(
                f"Learner '{learner_id}' has used all {attempts_allowed} attempt(s)."
            )

        attempt_number = len(attempts) + 1
        attempt = self._repo.create_attempt({
            "assessment_id": assessment_id,
            "learner_id": learner_id,
            "attempt_number": attempt_number,
        })
        logger.info(
            "assessment_attempt_started",
            extra={"attempt_id": attempt["id"], "learner_id": learner_id},
        )
        return attempt

    def submit_attempt(
        self,
        attempt_id: str,
        score: float,
        feedback: Optional[str] = None,
    ) -> dict[str, Any]:
        attempt = self._find_attempt(attempt_id)
        if not attempt:
            raise ValueError(f"Attempt '{attempt_id}' not found.")
        if attempt.get("submitted_at") is not None:
            raise ValueError("This attempt has already been submitted.")

        now = datetime.now(timezone.utc).isoformat()
        updated = self._repo.update_attempt(attempt_id, {
            "submitted_at": now,
            "score": score,
            "feedback": feedback,
        })

        result = updated or attempt
        event = AssessmentAttempted(
            attempt_id=attempt_id,
            assessment_id=attempt.get("assessment_id", ""),
            learner_id=attempt.get("learner_id", ""),
            attempt_number=attempt.get("attempt_number", 0),
            score=score,
        )
        logger.info(
            "assessment_attempt_submitted",
            extra={"attempt_id": attempt_id, "event_id": event.event_id},
        )
        return result

    def get_attempts(
        self, assessment_id: str, learner_id: Optional[str] = None
    ) -> list[dict[str, Any]]:
        return self._repo.get_attempts(assessment_id, learner_id)

    def check_passed(self, assessment_id: str, attempt_id: str) -> bool:
        assessment = self._repo.get_by_id(assessment_id)
        if not assessment:
            raise ValueError(f"Assessment '{assessment_id}' not found.")
        attempt = self._find_attempt(attempt_id)
        if not attempt or attempt.get("score") is None:
            return False
        passing_score = assessment.get("passing_score", 70.0)
        return attempt["score"] >= passing_score

    def create_submission(
        self, attempt_id: str, content: str, attachments: Optional[list[str]] = None
    ) -> dict[str, Any]:
        attempt = self._find_attempt(attempt_id)
        if not attempt:
            raise ValueError(f"Attempt '{attempt_id}' not found.")
        return self._repo.create_submission({
            "attempt_id": attempt_id,
            "content": content,
            "attachments": attachments or [],
        })

    def get_submissions(self, attempt_id: str) -> list[dict[str, Any]]:
        return self._repo.get_submissions(attempt_id)

    def create_question_group(
        self, assessment_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        assessment = self._repo.get_by_id(assessment_id)
        if not assessment:
            raise ValueError(f"Assessment '{assessment_id}' not found.")
        data["assessment_id"] = assessment_id
        return self._repo.create_question_group(data)

    def get_question_groups(self, assessment_id: str) -> list[dict[str, Any]]:
        return self._repo.get_question_groups(assessment_id)

    def get_assessment_statistics(self, assessment_id: str) -> dict[str, Any]:
        assessment = self._repo.get_by_id(assessment_id)
        if not assessment:
            raise ValueError(f"Assessment '{assessment_id}' not found.")

        attempts = self._repo.get_attempts(assessment_id)
        scores = [a["score"] for a in attempts if a.get("score") is not None]

        if not scores:
            return {
                "assessment_id": assessment_id,
                "total_attempts": 0,
                "average_score": 0.0,
                "min_score": 0.0,
                "max_score": 0.0,
                "pass_rate": 0.0,
                "passing_score": assessment.get("passing_score", 70.0),
            }

        passing_score = assessment.get("passing_score", 70.0)
        passed = sum(1 for s in scores if s >= passing_score)

        return {
            "assessment_id": assessment_id,
            "total_attempts": len(attempts),
            "average_score": round(sum(scores) / len(scores), 2),
            "min_score": min(scores),
            "max_score": max(scores),
            "pass_rate": round((passed / len(scores)) * 100.0, 2),
            "passing_score": passing_score,
        }

    def _find_attempt(self, attempt_id: str) -> Optional[dict[str, Any]]:
        for attempt_list in self._repo.get_attempts("", None):
            for attempt in attempt_list:
                if attempt.get("id") == attempt_id:
                    return attempt

        all_assessments = [a for a in self._repo.get_by_course("")]
        for assessment in all_assessments:
            attempts = self._repo.get_attempts(assessment["id"])
            for attempt in attempts:
                if attempt.get("id") == attempt_id:
                    return attempt
        return None
