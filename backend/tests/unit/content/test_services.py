"""Tests for content services — CourseService, QuizService, LessonService."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.content.domain.entities.content import Course, Lesson, Quiz, QuizQuestion
from app.content.services.course_service import CourseService
from app.content.services.lesson_service import LessonService
from app.content.services.quiz_service import QuizService


class TestCourseService:
    @pytest.fixture
    def repo(self):
        r = MagicMock()
        r.save = AsyncMock()
        r.find_by_id = AsyncMock()
        r.find_all = AsyncMock()
        r.count = AsyncMock()
        r.search = AsyncMock()
        return r

    @pytest.fixture
    def service(self, repo):
        return CourseService(repo=repo)

    def test_create_course_raises_on_invalid(self, service, repo):
        with pytest.raises(ValueError, match="Course validation failed"):
            import asyncio
            asyncio.run(service.create_course(title="", description=""))

    def test_get_course_returns_none_on_missing(self, service, repo):
        repo.find_by_id.return_value = None
        import asyncio
        result = asyncio.run(service.get_course("nonexistent"))
        assert result is None

    def test_get_course_returns_course(self, service, repo):
        c = Course(id="c1", title="Test")
        repo.find_by_id.return_value = c
        import asyncio
        result = asyncio.run(service.get_course("c1"))
        assert result.title == "Test"

    def test_update_course_raises_on_missing(self, service, repo):
        repo.find_by_id.return_value = None
        with pytest.raises(ValueError, match="not found"):
            import asyncio
            asyncio.run(service.update_course("bad", {}))

    def test_publish_course_raises_on_missing(self, service, repo):
        repo.find_by_id.return_value = None
        with pytest.raises(ValueError, match="not found"):
            import asyncio
            asyncio.run(service.publish_course("bad"))

    def test_archive_course_raises_on_missing(self, service, repo):
        repo.find_by_id.return_value = None
        with pytest.raises(ValueError, match="not found"):
            import asyncio
            asyncio.run(service.archive_course("bad"))

    def test_clone_course_raises_on_missing(self, service, repo):
        repo.find_by_id.return_value = None
        with pytest.raises(ValueError, match="not found"):
            import asyncio
            asyncio.run(service.clone_course("bad"))


class TestQuizService:
    @pytest.fixture
    def repo(self):
        r = MagicMock()
        r.save = AsyncMock()
        r.find_by_id = AsyncMock()
        return r

    @pytest.fixture
    def service(self, repo):
        return QuizService(repo=repo)

    def test_create_quiz_raises_with_empty_title(self, service, repo):
        import asyncio
        with pytest.raises(ValueError, match="Quiz title is required"):
            asyncio.run(service.create_quiz(course_id="c1", title=""))

    def test_get_quiz_returns_none_on_missing(self, service, repo):
        repo.find_by_id.return_value = None
        import asyncio
        result = asyncio.run(service.get_quiz("bad"))
        assert result is None

    def test_add_question_raises_on_missing_quiz(self, service, repo):
        repo.find_by_id.return_value = None
        import asyncio
        with pytest.raises(ValueError, match="not found"):
            asyncio.run(service.add_question("bad", "Q?"))

    def test_grade_quiz_raises_on_missing(self, service, repo):
        repo.find_by_id.return_value = None
        import asyncio
        with pytest.raises(ValueError, match="not found"):
            asyncio.run(service.grade_quiz("bad", {}))

    def test_grade_quiz_raises_on_empty(self, service, repo):
        q = Quiz(id="q1", questions=[])
        repo.find_by_id.return_value = q
        import asyncio
        with pytest.raises(ValueError, match="no questions"):
            asyncio.run(service.grade_quiz("q1", {}))

    def test_calculate_score_all_correct(self, service, repo):
        q = Quiz(id="q1")
        q1 = QuizQuestion(id="a", question_text="Q1", correct_answer="A", points=1.0)
        q2 = QuizQuestion(id="b", question_text="Q2", correct_answer="B", points=2.0)
        q.questions = [q1, q2]
        earned, total, details = service.calculate_score(q, {"a": "A", "b": "B"})
        assert earned == 3.0
        assert total == 3.0
        assert details[0]["is_correct"] is True
        assert details[1]["is_correct"] is True

    def test_calculate_score_partial(self, service, repo):
        q = Quiz(id="q1")
        q1 = QuizQuestion(id="a", question_text="Q1", correct_answer="A", points=1.0)
        q2 = QuizQuestion(id="b", question_text="Q2", correct_answer="B", points=2.0)
        q.questions = [q1, q2]
        earned, total, details = service.calculate_score(q, {"a": "Wrong", "b": "B"})
        assert earned == 2.0
        assert total == 3.0
        assert details[0]["is_correct"] is False
        assert details[1]["is_correct"] is True


class TestLessonService:
    @pytest.fixture
    def repo(self):
        r = MagicMock()
        r.save = AsyncMock()
        r.find_by_id = AsyncMock()
        r.find_by_course = AsyncMock()
        r.reorder = AsyncMock()
        return r

    @pytest.fixture
    def service(self, repo):
        from app.content.validators.content_validator import ContentValidator
        return LessonService(repo=repo, validator=ContentValidator())

    def test_create_lesson_raises_on_empty_title(self, service, repo):
        import asyncio
        with pytest.raises(ValueError, match="Lesson validation failed"):
            asyncio.run(service.create_lesson(course_id="c1", title=""))

    def test_get_lesson_returns_none_on_missing(self, service, repo):
        repo.find_by_id.return_value = None
        import asyncio
        result = asyncio.run(service.get_lesson("bad"))
        assert result is None

    def test_reorder_lessons(self, service, repo):
        repo.find_by_course.return_value = [Lesson(id="a", order=0), Lesson(id="b", order=1)]
        repo.reorder.return_value = True
        import asyncio
        result = asyncio.run(service.reorder_lessons("c1", ["b", "a"]))
        assert result is True

    def test_attach_media(self, service, repo):
        l = Lesson(id="a", title="L")
        repo.find_by_id.return_value = l
        import asyncio
        result = asyncio.run(service.attach_media("a", "m1"))
        assert "m1" in result.media_refs

    def test_remove_media(self, service, repo):
        l = Lesson(id="a", media_refs=["m1"])
        repo.find_by_id.return_value = l
        import asyncio
        result = asyncio.run(service.remove_media("a", "m1"))
        assert "m1" not in result.media_refs
