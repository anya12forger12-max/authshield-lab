"""Educational Content Studio module for AuthShieldLab.

Provides course management, lesson authoring, quiz creation,
media asset management, publishing workflows, and knowledge mapping
for the cybersecurity educational platform.
"""

from __future__ import annotations

from .services.course_service import CourseService
from .services.lesson_service import LessonService
from .services.quiz_service import QuizService
from .services.media_service import MediaService
from .services.publishing_service import PublishingService
from .services.knowledge_service import KnowledgeService
from .validators.content_validator import ContentValidator
from .domain.entities.content import (
    Course,
    Lesson,
    Quiz,
    QuizQuestion,
    MediaAsset,
    KnowledgeNode,
)
from .domain.entities.assessment import (
    Assessment,
    Rubric,
    AssessmentCriteria,
    GradingScale,
)
from .domain.events.content_events import (
    CourseCreated,
    CoursePublished,
    CourseArchived,
    LessonCreated,
    QuizCreated,
    QuizGraded,
    MediaUploaded,
    AssessmentCompleted,
    ContentVersioned,
    AccessibilityReviewCompleted,
)
from .api.content_routes import router as content_router

__all__ = [
    "CourseService",
    "LessonService",
    "QuizService",
    "MediaService",
    "PublishingService",
    "KnowledgeService",
    "ContentValidator",
    "Course",
    "Lesson",
    "Quiz",
    "QuizQuestion",
    "MediaAsset",
    "KnowledgeNode",
    "Assessment",
    "Rubric",
    "AssessmentCriteria",
    "GradingScale",
    "CourseCreated",
    "CoursePublished",
    "CourseArchived",
    "LessonCreated",
    "QuizCreated",
    "QuizGraded",
    "MediaUploaded",
    "AssessmentCompleted",
    "ContentVersioned",
    "AccessibilityReviewCompleted",
    "content_router",
]
