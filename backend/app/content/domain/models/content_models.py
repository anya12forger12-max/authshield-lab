"""SQLAlchemy ORM models for the Content Studio."""

from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Float,
    Integer,
    String,
    Text,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column

from ....shared.base_model import (
    AuditMixin,
    Base,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class CourseModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, Base):
    """ORM model for courses."""

    __tablename__ = "content_courses"

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False, default="beginner")
    learning_objectives: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)
    prerequisites: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)
    estimated_hours: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    target_audience: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    required_competencies: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    tags: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)


class LessonModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """ORM model for lessons."""

    __tablename__ = "content_lessons"

    course_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    lesson_type: Mapped[str] = mapped_column(String(20), nullable=False, default="theory")
    estimated_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    learning_objectives: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)
    media_refs: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)
    accessible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    localized: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class QuizModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """ORM model for quizzes."""

    __tablename__ = "content_quizzes"

    course_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    passing_score: Mapped[float] = mapped_column(Float, nullable=False, default=70.0)
    time_limit_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    shuffle_questions: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")


class QuizQuestionModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """ORM model for quiz questions."""

    __tablename__ = "content_quiz_questions"

    quiz_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(String(20), nullable=False, default="mcq")
    choices: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)
    correct_answer: Mapped[str] = mapped_column(Text, nullable=False, default="")
    explanation: Mapped[str] = mapped_column(Text, nullable=False, default="")
    points: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")


class MediaAssetModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """ORM model for media assets."""

    __tablename__ = "content_media_assets"

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    media_type: Mapped[str] = mapped_column(String(20), nullable=False, default="image")
    uri: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    alt_text: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    caption: Mapped[str] = mapped_column(Text, nullable=False, default="")
    transcript: Mapped[str] = mapped_column(Text, nullable=False, default="")
    accessible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class KnowledgeNodeModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """ORM model for knowledge graph nodes."""

    __tablename__ = "content_knowledge_nodes"

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    node_type: Mapped[str] = mapped_column(String(20), nullable=False, default="concept")
    related_nodes: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)
    prerequisites: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)
    competencies: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)
