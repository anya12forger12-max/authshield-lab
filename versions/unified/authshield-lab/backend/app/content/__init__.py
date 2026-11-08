"""Educational Content Studio module for AuthShieldLab.

Provides course management, lesson authoring, quiz creation,
media asset management, publishing workflows, and knowledge mapping
for the cybersecurity educational platform.
"""

from __future__ import annotations

from .api.content_routes import router as content_router
from .domain.entities.assessment import (
    Assessment,
    AssessmentCriteria,
    GradingScale,
    Rubric,
)
from .domain.entities.content import (
    Course,
    KnowledgeNode,
    Lesson,
    MediaAsset,
    Quiz,
    QuizQuestion,
)
from .domain.events.content_events import (
    AccessibilityReviewCompleted,
    AssessmentCompleted,
    ContentVersioned,
    CourseArchived,
    CourseCreated,
    CoursePublished,
    LessonCreated,
    MediaUploaded,
    QuizCreated,
    QuizGraded,
)
from .services.course_service import CourseService
from .services.knowledge_service import KnowledgeService
from .services.lesson_service import LessonService
from .services.media_service import MediaService
from .services.publishing_service import PublishingService
from .services.quiz_service import QuizService
from .validators.content_validator import ContentValidator

__all__ = [
    "AccessibilityReviewCompleted",
    "Assessment",
    "AssessmentCompleted",
    "AssessmentCriteria",
    "ContentValidator",
    "ContentVersioned",
    "Course",
    "CourseArchived",
    "CourseCreated",
    "CoursePublished",
    "CourseService",
    "GradingScale",
    "KnowledgeNode",
    "KnowledgeService",
    "Lesson",
    "LessonCreated",
    "LessonService",
    "MediaAsset",
    "MediaService",
    "MediaUploaded",
    "PublishingService",
    "Quiz",
    "QuizCreated",
    "QuizGraded",
    "QuizQuestion",
    "QuizService",
    "Rubric",
    "content_router",
]
