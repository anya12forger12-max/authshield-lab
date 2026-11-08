"""Tests for content entities — Course, Lesson, Quiz, QuizQuestion, MediaAsset, KnowledgeNode."""

from __future__ import annotations

from datetime import datetime, timezone

from app.content.domain.entities.content import (
    Course,
    CourseStatus,
    KnowledgeNode,
    KnowledgeNodeType,
    Lesson,
    MediaAsset,
    QuestionType,
    Quiz,
    QuizQuestion,
)


class TestCourse:
    def test_default_values(self):
        c = Course()
        assert c.status == "draft"
        assert c.difficulty == "beginner"
        assert c.version == 1

    def test_publish_changes_status(self):
        c = Course()
        assert c.status == CourseStatus.DRAFT.value
        c.publish()
        assert c.status == CourseStatus.PUBLISHED.value

    def test_archive_changes_status(self):
        c = Course()
        c.publish()
        c.archive()
        assert c.status == CourseStatus.ARCHIVED.value

    def test_clone_creates_draft_copy(self):
        c = Course(title="Original", description="Desc", learning_objectives=["obj1"], estimated_hours=10)
        cloned = c.clone()
        assert cloned.id != c.id
        assert cloned.status == CourseStatus.DRAFT.value
        assert cloned.title == "Original (Copy)"
        assert cloned.learning_objectives == c.learning_objectives

    def test_clone_with_custom_title(self):
        c = Course(title="Original", description="Desc")
        cloned = c.clone(new_title="Custom Copy")
        assert cloned.title == "Custom Copy"

    def test_validate_returns_errors_for_missing_fields(self):
        c = Course()
        errors = c.validate()
        assert "Course title is required." in errors
        assert "Course description is required." in errors
        assert "At least one learning objective is required." in errors

    def test_validate_passes_with_valid_data(self):
        c = Course(title="Title", description="Desc", learning_objectives=["obj1"])
        errors = c.validate()
        assert errors == []

    def test_update_version_increments(self):
        c = Course()
        old = c.version
        c.update_version()
        assert c.version == old + 1

    def test_to_dict_structure(self):
        c = Course(title="Test", status="published")
        d = c.__dict__
        assert d["title"] == "Test"
        assert d["status"] == "published"


class TestLesson:
    def test_default_values(self):
        l = Lesson()
        assert l.lesson_type == "theory"
        assert l.order == 0
        assert l.accessible is True
        assert l.version == 1

    def test_custom_lesson(self):
        l = Lesson(title="Intro", lesson_type="lab", order=1, estimated_minutes=45, accessible=False)
        assert l.title == "Intro"
        assert l.lesson_type == "lab"
        assert l.estimated_minutes == 45
        assert l.accessible is False

    def test_has_unique_id(self):
        l1 = Lesson()
        l2 = Lesson()
        assert l1.id != l2.id


class TestQuiz:
    def test_defaults(self):
        q = Quiz()
        assert q.passing_score == 70.0
        assert q.time_limit_minutes == 30
        assert q.shuffle_questions is False
        assert q.status == "draft"

    def test_add_questions_to_quiz(self):
        q = Quiz(title="Midterm")
        q1 = QuizQuestion(question_text="Q1", correct_answer="A")
        q2 = QuizQuestion(question_text="Q2", correct_answer="B", points=2.0)
        q.questions = [q1, q2]
        assert len(q.questions) == 2
        assert q.questions[0].correct_answer == "A"
        assert q.questions[1].points == 2.0


class TestQuizQuestion:
    def test_default_values(self):
        q = QuizQuestion()
        assert q.question_type == QuestionType.MCQ.value
        assert q.points == 1.0
        assert q.difficulty == "medium"

    def test_custom_question(self):
        q = QuizQuestion(
            question_text="What is X?",
            question_type=QuestionType.TRUE_FALSE.value,
            correct_answer="True",
            points=2.0,
        )
        assert q.question_text == "What is X?"
        assert q.question_type == "true_false"
        assert q.correct_answer == "True"


class TestMediaAsset:
    def test_default_values(self):
        m = MediaAsset()
        assert m.media_type == "image"
        assert m.accessible is True
        assert m.alt_text == ""

    def test_custom_asset(self):
        m = MediaAsset(title="Logo", media_type="video", uri="/videos/logo.mp4", alt_text="Company logo")
        assert m.title == "Logo"
        assert m.uri == "/videos/logo.mp4"


class TestKnowledgeNode:
    def test_defaults(self):
        kn = KnowledgeNode()
        assert kn.node_type == KnowledgeNodeType.CONCEPT.value

    def test_with_competencies(self):
        kn = KnowledgeNode(title="Encryption", node_type="principle", competencies=["SEC-101", "SEC-102"])
        assert kn.title == "Encryption"
        assert len(kn.competencies) == 2

    def test_related_nodes(self):
        kn = KnowledgeNode(related_nodes=["n1", "n2"])
        assert "n1" in kn.related_nodes
