"""Content domain entities – core dataclasses for the Content Studio."""

from __future__ import annotations

import copy
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class CourseStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class LessonType(str, Enum):
    THEORY = "theory"
    LAB = "lab"
    QUIZ = "quiz"
    DISCUSSION = "discussion"


class QuestionType(str, Enum):
    MCQ = "mcq"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    MATCHING = "matching"


class MediaContentType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"


class KnowledgeNodeType(str, Enum):
    CONCEPT = "concept"
    TOPIC = "topic"
    PRINCIPLE = "principle"
    FRAMEWORK = "framework"


class ContentStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


@dataclass
class Course:
    """Represents a cybersecurity training course."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    difficulty: str = "beginner"
    learning_objectives: list[str] = field(default_factory=list)
    prerequisites: list[str] = field(default_factory=list)
    estimated_hours: float = 0.0
    target_audience: str = ""
    required_competencies: list[str] = field(default_factory=list)
    status: str = CourseStatus.DRAFT.value
    version: int = 1
    tags: list[str] = field(default_factory=list)
    created_by: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def clone(self, new_title: str | None = None) -> Course:
        """Return a deep copy of this course with a fresh ID and draft status."""
        cloned = copy.deepcopy(self)
        cloned.id = str(uuid.uuid4())
        cloned.title = new_title or f"{self.title} (Copy)"
        cloned.status = CourseStatus.DRAFT.value
        cloned.version = 1
        cloned.created_at = datetime.now(timezone.utc)
        cloned.updated_at = datetime.now(timezone.utc)
        return cloned

    def publish(self) -> Course:
        """Transition the course to published status."""
        self.status = CourseStatus.PUBLISHED.value
        self.updated_at = datetime.now(timezone.utc)
        return self

    def archive(self) -> Course:
        """Transition the course to archived status."""
        self.status = CourseStatus.ARCHIVED.value
        self.updated_at = datetime.now(timezone.utc)
        return self

    def update_version(self) -> Course:
        """Increment the version counter and touch the updated_at timestamp."""
        self.version += 1
        self.updated_at = datetime.now(timezone.utc)
        return self

    def validate(self) -> list[str]:
        """Return a list of validation error messages (empty if valid)."""
        errors: list[str] = []
        if not self.title or not self.title.strip():
            errors.append("Course title is required.")
        if len(self.title) > 200:
            errors.append("Course title must be 200 characters or fewer.")
        if not self.description or not self.description.strip():
            errors.append("Course description is required.")
        if len(self.description) > 5000:
            errors.append("Course description must be 5000 characters or fewer.")
        if not self.learning_objectives:
            errors.append("At least one learning objective is required.")
        if self.estimated_hours < 0:
            errors.append("Estimated hours must be non-negative.")
        valid_difficulties = {"beginner", "intermediate", "advanced", "expert"}
        if self.difficulty not in valid_difficulties:
            errors.append(f"Difficulty must be one of: {', '.join(sorted(valid_difficulties))}")
        return errors


@dataclass
class Lesson:
    """A single lesson within a course."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    course_id: str = ""
    title: str = ""
    content: str = ""
    order: int = 0
    lesson_type: str = LessonType.THEORY.value
    estimated_minutes: int = 30
    learning_objectives: list[str] = field(default_factory=list)
    media_refs: list[str] = field(default_factory=list)
    accessible: bool = True
    localized: bool = False
    version: int = 1
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Quiz:
    """Quiz attached to a course or lesson."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    course_id: str = ""
    title: str = ""
    questions: list[QuizQuestion] = field(default_factory=list)
    passing_score: float = 70.0
    time_limit_minutes: int = 30
    shuffle_questions: bool = False
    version: int = 1
    status: str = ContentStatus.DRAFT.value


@dataclass
class QuizQuestion:
    """A single question within a quiz."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    quiz_id: str = ""
    question_text: str = ""
    question_type: str = QuestionType.MCQ.value
    choices: list[str] = field(default_factory=list)
    correct_answer: str = ""
    explanation: str = ""
    points: float = 1.0
    difficulty: str = "medium"


@dataclass
class MediaAsset:
    """Represents a media asset (image, video, audio, document)."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    media_type: str = MediaContentType.IMAGE.value
    uri: str = ""
    alt_text: str = ""
    caption: str = ""
    transcript: str = ""
    accessible: bool = True
    version: int = 1
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class KnowledgeNode:
    """A node in the knowledge graph representing a concept, topic, principle, or framework."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    node_type: str = KnowledgeNodeType.CONCEPT.value
    related_nodes: list[str] = field(default_factory=list)
    prerequisites: list[str] = field(default_factory=list)
    competencies: list[str] = field(default_factory=list)
