"""Quiz management and grading service."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from ..domain.entities.content import Quiz, QuizQuestion
from ..domain.events.content_events import QuizCreated, QuizGraded
from ..domain.interfaces.content_repository import QuizRepository
from ..validators.content_validator import ContentValidator


class QuizService:
    """Service for creating, managing, and grading quizzes.

    Parameters
    ----------
    repo:
        Repository for quiz persistence.
    validator:
        Content validation rules.
    """

    def __init__(self, repo: QuizRepository, validator: ContentValidator | None = None) -> None:
        self._repo = repo
        self._validator = validator or ContentValidator()
        self._results: dict[str, dict[str, Any]] = {}
        self._events: list[Any] = []

    def _record_event(self, event: Any) -> None:
        self._events.append(event)

    async def create_quiz(
        self,
        course_id: str,
        title: str,
        passing_score: float = 70.0,
        time_limit_minutes: int = 30,
        shuffle_questions: bool = False,
    ) -> Quiz:
        """Create a new quiz and persist it."""
        if not title or not title.strip():
            raise ValueError("Quiz title is required.")
        quiz = Quiz(
            course_id=course_id,
            title=title,
            passing_score=passing_score,
            time_limit_minutes=time_limit_minutes,
            shuffle_questions=shuffle_questions,
        )
        await self._repo.save(quiz)
        event = QuizCreated(
            quiz_id=quiz.id,
            course_id=quiz.course_id,
            title=quiz.title,
            correlation_id=quiz.id,
            message=f"Quiz '{quiz.title}' created for course {quiz.course_id}.",
        )
        self._record_event(event)
        return quiz

    async def get_quiz(self, quiz_id: str) -> Optional[Quiz]:
        """Retrieve a quiz by ID."""
        return await self._repo.find_by_id(quiz_id)

    async def add_question(
        self,
        quiz_id: str,
        question_text: str,
        question_type: str = "mcq",
        choices: list[str] | None = None,
        correct_answer: str = "",
        explanation: str = "",
        points: float = 1.0,
        difficulty: str = "medium",
    ) -> Quiz:
        """Add a question to a quiz."""
        quiz = await self._repo.find_by_id(quiz_id)
        if quiz is None:
            raise ValueError(f"Quiz {quiz_id} not found.")
        if not question_text or not question_text.strip():
            raise ValueError("Question text is required.")
        if not correct_answer:
            raise ValueError("Correct answer is required.")
        question = QuizQuestion(
            quiz_id=quiz_id,
            question_text=question_text,
            question_type=question_type,
            choices=choices or [],
            correct_answer=correct_answer,
            explanation=explanation,
            points=points,
            difficulty=difficulty,
        )
        quiz.questions.append(question)
        quiz.version += 1
        await self._repo.save(quiz)
        return quiz

    async def remove_question(self, quiz_id: str, question_id: str) -> Quiz:
        """Remove a question from a quiz."""
        quiz = await self._repo.find_by_id(quiz_id)
        if quiz is None:
            raise ValueError(f"Quiz {quiz_id} not found.")
        original_len = len(quiz.questions)
        quiz.questions = [q for q in quiz.questions if q.id != question_id]
        if len(quiz.questions) == original_len:
            raise ValueError(f"Question {question_id} not found in quiz {quiz_id}.")
        quiz.version += 1
        await self._repo.save(quiz)
        return quiz

    async def update_question(self, quiz_id: str, question_id: str, updates: dict[str, Any]) -> Quiz:
        """Update fields on an existing question within a quiz."""
        quiz = await self._repo.find_by_id(quiz_id)
        if quiz is None:
            raise ValueError(f"Quiz {quiz_id} not found.")
        target: QuizQuestion | None = None
        for q in quiz.questions:
            if q.id == question_id:
                target = q
                break
        if target is None:
            raise ValueError(f"Question {question_id} not found in quiz {quiz_id}.")
        allowed_fields = {
            "question_text",
            "question_type",
            "choices",
            "correct_answer",
            "explanation",
            "points",
            "difficulty",
        }
        for key, value in updates.items():
            if key in allowed_fields:
                setattr(target, key, value)
        quiz.version += 1
        await self._repo.save(quiz)
        return quiz

    async def grade_quiz(self, quiz_id: str, answers: dict[str, str]) -> dict[str, Any]:
        """Grade a quiz submission.

        Parameters
        ----------
        quiz_id:
            The quiz to grade.
        answers:
            Mapping of ``question_id`` → ``submitted_answer``.
        """
        quiz = await self._repo.find_by_id(quiz_id)
        if quiz is None:
            raise ValueError(f"Quiz {quiz_id} not found.")
        if not quiz.questions:
            raise ValueError("Quiz has no questions to grade.")
        score, total_possible, details = self.calculate_score(quiz, answers)
        percentage = (score / total_possible * 100) if total_possible > 0 else 0.0
        passed = percentage >= quiz.passing_score
        result_id = str(uuid.uuid4())
        result: dict[str, Any] = {
            "result_id": result_id,
            "quiz_id": quiz_id,
            "score": round(score, 2),
            "total_possible": round(total_possible, 2),
            "percentage": round(percentage, 2),
            "passing_score": quiz.passing_score,
            "passed": passed,
            "details": details,
            "graded_at": datetime.now(timezone.utc).isoformat(),
        }
        self._results[result_id] = result
        event = QuizGraded(
            quiz_id=quiz_id,
            score=percentage,
            passing_score=quiz.passing_score,
            passed=passed,
            correlation_id=quiz_id,
            message=f"Quiz '{quiz.title}' graded: {percentage:.1f}% ({'PASSED' if passed else 'FAILED'}).",
        )
        self._record_event(event)
        return result

    def calculate_score(
        self, quiz: Quiz, answers: dict[str, str]
    ) -> tuple[float, float, list[dict[str, Any]]]:
        """Calculate the raw score for a set of answers.

        Returns
        -------
        A tuple of ``(earned_points, total_points, detail_list)``.
        """
        total_possible = 0.0
        earned = 0.0
        details: list[dict[str, Any]] = []
        for question in quiz.questions:
            total_possible += question.points
            submitted = answers.get(question.id, "")
            is_correct = submitted.strip().lower() == question.correct_answer.strip().lower()
            if is_correct:
                earned += question.points
            details.append(
                {
                    "question_id": question.id,
                    "question_text": question.question_text,
                    "submitted_answer": submitted,
                    "correct_answer": question.correct_answer,
                    "is_correct": is_correct,
                    "points_possible": question.points,
                    "points_earned": question.points if is_correct else 0.0,
                    "explanation": question.explanation,
                }
            )
        return earned, total_possible, details

    async def get_quiz_results(self, quiz_id: str) -> list[dict[str, Any]]:
        """Return all graded results for a given quiz."""
        return [r for r in self._results.values() if r["quiz_id"] == quiz_id]

    async def validate_quiz(self, quiz_id: str) -> dict[str, Any]:
        """Validate a quiz's structure and return findings."""
        quiz = await self._repo.find_by_id(quiz_id)
        if quiz is None:
            raise ValueError(f"Quiz {quiz_id} not found.")
        errors: list[str] = []
        warnings: list[str] = []
        if not quiz.title or not quiz.title.strip():
            errors.append("Quiz title is required.")
        if not quiz.questions:
            errors.append("Quiz must have at least one question.")
        if quiz.passing_score < 0 or quiz.passing_score > 100:
            errors.append("Passing score must be between 0 and 100.")
        question_dicts = []
        for q in quiz.questions:
            q_dict: dict[str, Any] = {
                "question_text": q.question_text,
                "question_type": q.question_type,
                "choices": q.choices,
                "correct_answer": q.correct_answer,
                "points": q.points,
            }
            question_dicts.append(q_dict)
        if question_dicts:
            q_result = self._validator.validate_quiz_questions(question_dicts)
            if not q_result.is_valid:
                errors.extend(e.message for e in q_result.errors)
            if q_result.warnings:
                warnings.extend(w.message for w in q_result.warnings)
        total_points = sum(q.points for q in quiz.questions)
        if total_points <= 0:
            warnings.append("Total question points should be greater than zero.")
        return {
            "quiz_id": quiz.id,
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "question_count": len(quiz.questions),
            "total_points": total_points,
        }
