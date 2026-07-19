"""Assessment analytics service – pass rates, question analysis, reliability, feedback."""

from __future__ import annotations

import math
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from ...shared.logging_config import get_logger
from ..domain.entities.analytics import AssessmentOutcome
from ..domain.interfaces import IAssessmentOutcomeRepository

logger = get_logger("analytics.assessment_analytics_service")


class AssessmentAnalyticsService:
    """Provides assessment-level analytics: pass rates, item analysis, reliability.

    Parameters
    ----------
    outcome_repo:
        Repository for assessment outcome persistence.
    """

    def __init__(self, outcome_repo: IAssessmentOutcomeRepository) -> None:
        self._outcome_repo = outcome_repo

    async def record_assessment_outcome(
        self,
        assessment_id: str,
        title: str = "",
        total_attempts: int = 0,
        passed: int = 0,
        failed: int = 0,
        question_scores: Optional[dict[str, list[float]]] = None,
    ) -> AssessmentOutcome:
        """Record an assessment outcome with optional per-question score data."""
        avg_score = 0.0
        pass_rate = (passed / total_attempts * 100) if total_attempts > 0 else 0.0

        question_difficulty: dict[str, float] = {}
        question_discrimination: dict[str, float] = {}

        if question_scores:
            question_difficulty = self._compute_question_difficulty(question_scores)
            question_discrimination = self._compute_question_discrimination(question_scores)
            all_scores = []
            for scores in question_scores.values():
                all_scores.extend(scores)
            if all_scores:
                avg_score = sum(all_scores) / len(all_scores)

        existing = await self._outcome_repo.get_by_assessment_id(assessment_id)
        if existing is not None:
            updated = await self._outcome_repo.update(assessment_id, {
                "title": title,
                "total_attempts": total_attempts,
                "passed": passed,
                "failed": failed,
                "avg_score": round(avg_score, 2),
                "pass_rate": round(pass_rate, 2),
                "question_difficulty": question_difficulty,
                "question_discrimination": question_discrimination,
            })
            return updated if updated else existing

        outcome = AssessmentOutcome(
            assessment_id=assessment_id,
            title=title,
            total_attempts=total_attempts,
            passed=passed,
            failed=failed,
            avg_score=round(avg_score, 2),
            pass_rate=round(pass_rate, 2),
            question_difficulty=question_difficulty,
            question_discrimination=question_discrimination,
        )
        created = await self._outcome_repo.create(outcome)
        logger.info(
            "assessment_outcome_recorded",
            assessment_id=assessment_id,
            pass_rate=pass_rate,
        )
        return created

    async def get_assessment_outcome(
        self, assessment_id: str
    ) -> Optional[AssessmentOutcome]:
        """Retrieve a specific assessment outcome by ID."""
        return await self._outcome_repo.get_by_assessment_id(assessment_id)

    async def list_all_outcomes(self) -> list[AssessmentOutcome]:
        """List all recorded assessment outcomes."""
        return await self._outcome_repo.get_all()

    async def compute_pass_rate_analysis(self) -> dict[str, Any]:
        """Compute aggregate pass rate analysis across all assessments."""
        outcomes = await self._outcome_repo.get_all()
        if not outcomes:
            return {
                "total_assessments": 0,
                "overall_pass_rate": 0.0,
                "avg_score": 0.0,
                "highest_pass_rate": 0.0,
                "lowest_pass_rate": 0.0,
                "needs_attention": [],
            }

        total_attempts = sum(o.total_attempts for o in outcomes)
        total_passed = sum(o.passed for o in outcomes)
        overall_pass_rate = (total_passed / total_attempts * 100) if total_attempts > 0 else 0.0
        avg_score = sum(o.avg_score for o in outcomes) / len(outcomes)
        pass_rates = [o.pass_rate for o in outcomes]

        needs_attention = [
            {"assessment_id": o.assessment_id, "title": o.title, "pass_rate": o.pass_rate}
            for o in outcomes
            if o.pass_rate < 60.0
        ]

        return {
            "total_assessments": len(outcomes),
            "total_attempts": total_attempts,
            "overall_pass_rate": round(overall_pass_rate, 2),
            "avg_score": round(avg_score, 2),
            "highest_pass_rate": round(max(pass_rates), 2),
            "lowest_pass_rate": round(min(pass_rates), 2),
            "needs_attention": needs_attention,
        }

    async def analyze_question_items(
        self, assessment_id: str
    ) -> dict[str, Any]:
        """Analyze individual question items for an assessment."""
        outcome = await self._outcome_repo.get_by_assessment_id(assessment_id)
        if outcome is None:
            return {"error": "Assessment not found"}

        difficulty = outcome.question_difficulty
        discrimination = outcome.question_discrimination

        easy_questions = [q for q, d in difficulty.items() if d > 0.8]
        hard_questions = [q for q, d in difficulty.items() if d < 0.3]
        poor_discrimination = [q for q, d in discrimination.items() if d < 0.2]

        return {
            "assessment_id": assessment_id,
            "total_questions": len(difficulty),
            "avg_difficulty": round(
                sum(difficulty.values()) / len(difficulty), 2
            ) if difficulty else 0.0,
            "avg_discrimination": round(
                sum(discrimination.values()) / len(discrimination), 2
            ) if discrimination else 0.0,
            "easy_questions": easy_questions,
            "hard_questions": hard_questions,
            "poor_discrimination_questions": poor_discrimination,
            "question_difficulty": difficulty,
            "question_discrimination": discrimination,
        }

    async def compute_reliability_index(
        self, assessment_id: str
    ) -> dict[str, Any]:
        """Compute a simplified reliability index (KR-20 approximation) for an assessment."""
        outcome = await self._outcome_repo.get_by_assessment_id(assessment_id)
        if outcome is None:
            return {"error": "Assessment not found", "reliability_index": 0.0}

        difficulty = outcome.question_difficulty
        if not difficulty:
            return {"reliability_index": 0.0, "question_count": 0}

        n = len(difficulty)
        p_values = list(difficulty.values())
        q_values = [1.0 - p for p in p_values]
        p_times_q = sum(p * q for p, q in zip(p_values, q_values))
        variance_estimate = sum(p * q for p, q in zip(p_values, q_values)) / n if n > 0 else 0.0

        total_variance = sum(
            (p - sum(p_values) / n) ** 2 for p in p_values
        ) / n if n > 1 else 1.0

        if total_variance == 0:
            reliability = 0.0
        else:
            reliability = round(1.0 - (p_times_q / (n * total_variance)), 4)

        return {
            "assessment_id": assessment_id,
            "reliability_index": max(0.0, reliability),
            "question_count": n,
            "interpretation": self._interpret_reliability(max(0.0, reliability)),
        }

    async def get_feedback_summary(
        self, assessment_id: str
    ) -> dict[str, Any]:
        """Generate a feedback summary for an assessment."""
        outcome = await self._outcome_repo.get_by_assessment_id(assessment_id)
        if outcome is None:
            return {"error": "Assessment not found"}

        difficulty = outcome.question_difficulty
        discrimination = outcome.question_discrimination

        feedback_items: list[str] = []

        if outcome.pass_rate < 50.0:
            feedback_items.append(
                f"Pass rate ({outcome.pass_rate:.1f}%) is critically low. "
                "Consider reviewing question difficulty and alignment with instruction."
            )
        elif outcome.pass_rate < 70.0:
            feedback_items.append(
                f"Pass rate ({outcome.pass_rate:.1f}%) is below target. "
                "Review content coverage and assessment scaffolding."
            )

        if difficulty:
            avg_diff = sum(difficulty.values()) / len(difficulty)
            if avg_diff > 0.85:
                feedback_items.append("Questions are generally too easy – consider adding challenge.")
            elif avg_diff < 0.35:
                feedback_items.append("Questions are generally too hard – review prerequisite instruction.")

        if discrimination:
            poor = [q for q, d in discrimination.items() if d < 0.2]
            if poor:
                feedback_items.append(
                    f"{len(poor)} question(s) have poor discrimination. "
                    "These items may not effectively differentiate learner understanding."
                )

        return {
            "assessment_id": assessment_id,
            "title": outcome.title,
            "pass_rate": outcome.pass_rate,
            "avg_score": outcome.avg_score,
            "feedback_items": feedback_items,
        }

    def _compute_question_difficulty(
        self, question_scores: dict[str, list[float]]
    ) -> dict[str, float]:
        """Compute difficulty (p-value) per question: proportion correct."""
        difficulty: dict[str, float] = {}
        for q_id, scores in question_scores.items():
            if not scores:
                difficulty[q_id] = 0.0
                continue
            max_score = max(scores) if scores else 1.0
            if max_score == 0:
                difficulty[q_id] = 0.0
                continue
            proportion_correct = sum(s / max_score for s in scores) / len(scores)
            difficulty[q_id] = round(proportion_correct, 4)
        return difficulty

    def _compute_question_discrimination(
        self, question_scores: dict[str, list[float]]
    ) -> dict[str, float]:
        """Compute discrimination index per question using point-biserial approximation."""
        discrimination: dict[str, float] = {}

        all_totals: list[float] = []
        per_question: dict[str, list[float]] = {}
        for q_id, scores in question_scores.items():
            per_question[q_id] = scores

        if not per_question:
            return discrimination

        num_questions = len(per_question)
        for i in range(num_questions):
            first_q_scores = list(per_question.values())[i]
            total_per_participant = [0.0] * len(first_q_scores)
            for q_id, scores in per_question.items():
                for j, s in enumerate(scores):
                    if j < len(total_per_participant):
                        total_per_participant[j] += s

        for q_id, scores in question_scores.items():
            if len(scores) < 2:
                discrimination[q_id] = 0.0
                continue

            mean_total = sum(total_per_participant) / len(total_per_participant) if total_per_participant else 0.0
            sq_diffs = [(t - mean_total) ** 2 for t in total_per_participant]
            std_total = math.sqrt(sum(sq_diffs) / len(sq_diffs)) if sq_diffs else 1.0
            if std_total == 0:
                discrimination[q_id] = 0.0
                continue

            n = len(scores)
            sum_xy = sum(
                scores[i] * (total_per_participant[i] - mean_total)
                for i in range(n)
                if i < len(total_per_participant)
            )
            max_score_q = max(scores) if scores else 1.0
            if max_score_q == 0:
                discrimination[q_id] = 0.0
                continue

            rpb = sum_xy / (n * std_total * (max_score_q / 2)) if std_total > 0 else 0.0
            discrimination[q_id] = round(min(max(rpb, -1.0), 1.0), 4)

        return discrimination

    @staticmethod
    def _interpret_reliability(index: float) -> str:
        """Interpret a reliability index value."""
        if index >= 0.9:
            return "Excellent reliability"
        elif index >= 0.8:
            return "Good reliability"
        elif index >= 0.7:
            return "Acceptable reliability"
        elif index >= 0.6:
            return "Questionable reliability"
        elif index >= 0.5:
            return "Poor reliability"
        return "Unacceptable reliability"
