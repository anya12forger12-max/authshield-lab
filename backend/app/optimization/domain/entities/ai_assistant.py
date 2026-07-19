"""AI assistant domain entities for content authoring support."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class SuggestionType(str, Enum):
    """Types of AI-generated authoring suggestions."""

    OUTLINE = "outline"
    QUIZ_QUESTION = "quiz_question"
    GLOSSARY = "glossary"
    READING_LEVEL = "reading_level"
    ACCESSIBILITY = "accessibility"
    CONSISTENCY = "consistency"
    MAPPING = "mapping"
    METADATA = "metadata"
    TAGS = "tags"
    OBJECTIVES = "objectives"


@dataclass
class AuthoringSuggestion:
    """An AI-generated suggestion for content authoring."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    suggestion_type: SuggestionType = SuggestionType.OUTLINE
    content: str = ""
    source_material: str = ""
    confidence: float = 0.0
    reviewed: bool = False
    accepted: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    reviewed_at: datetime | None = None

    def accept(self) -> None:
        """Mark the suggestion as reviewed and accepted."""
        self.reviewed = True
        self.accepted = True
        self.reviewed_at = datetime.now(timezone.utc)

    def reject(self) -> None:
        """Mark the suggestion as reviewed but not accepted."""
        self.reviewed = True
        self.accepted = False
        self.reviewed_at = datetime.now(timezone.utc)

    def is_high_confidence(self, threshold: float = 0.8) -> bool:
        """Return True if the confidence meets or exceeds the threshold."""
        return self.confidence >= threshold

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "suggestion_type": self.suggestion_type.value,
            "content": self.content,
            "source_material": self.source_material,
            "confidence": self.confidence,
            "reviewed": self.reviewed,
            "accepted": self.accepted,
            "created_at": self.created_at.isoformat(),
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
        }


class GradeLevel(str, Enum):
    """Approximate US grade levels for reading difficulty."""

    ELEMENTARY = "elementary"
    MIDDLE_SCHOOL = "middle_school"
    HIGH_SCHOOL = "high_school"
    COLLEGE = "college"
    GRADUATE = "graduate"


@dataclass
class ReadingLevelAnalysis:
    """Computed readability statistics for a text."""

    text: str = ""
    flesch_kincaid: float = 0.0
    gunning_fog: float = 0.0
    coleman_liau: float = 0.0
    grade_level: str = ""
    word_count: int = 0
    sentence_count: int = 0
    syllable_count: int = 0

    def classify_grade(self) -> str:
        """Classify the Flesch-Kincaid score into a grade-level label."""
        avg = self.flesch_kincaid
        if avg <= 6.0:
            self.grade_level = GradeLevel.ELEMENTARY.value
        elif avg <= 9.0:
            self.grade_level = GradeLevel.MIDDLE_SCHOOL.value
        elif avg <= 12.0:
            self.grade_level = GradeLevel.HIGH_SCHOOL.value
        elif avg <= 16.0:
            self.grade_level = GradeLevel.COLLEGE.value
        else:
            self.grade_level = GradeLevel.GRADUATE.value
        return self.grade_level

    def is_accessible(self, max_grade: int = 12) -> bool:
        """Return True if the text is accessible at or below the given grade."""
        return self.flesch_kincaid <= float(max_grade)

    def to_dict(self) -> dict:
        return {
            "text_length": len(self.text),
            "flesch_kincaid": round(self.flesch_kincaid, 2),
            "gunning_fog": round(self.gunning_fog, 2),
            "coleman_liau": round(self.coleman_liau, 2),
            "grade_level": self.grade_level,
            "word_count": self.word_count,
            "sentence_count": self.sentence_count,
            "syllable_count": self.syllable_count,
        }


@dataclass
class GlossaryTerm:
    """A single glossary term extracted from content."""

    term: str = ""
    definition: str = ""
    category: str = ""
    source: str = ""
    confidence: float = 0.0

    def is_reliable(self, threshold: float = 0.7) -> bool:
        """Return True if confidence meets the threshold."""
        return self.confidence >= threshold

    def to_dict(self) -> dict:
        return {
            "term": self.term,
            "definition": self.definition,
            "category": self.category,
            "source": self.source,
            "confidence": self.confidence,
        }


@dataclass
class CurriculumMappingSuggestion:
    """Suggested mapping between two curriculum entities."""

    source_id: str = ""
    source_type: str = ""
    target_id: str = ""
    target_type: str = ""
    relationship: str = ""
    confidence: float = 0.0

    def is_reliable(self, threshold: float = 0.6) -> bool:
        """Return True if confidence exceeds the threshold."""
        return self.confidence >= threshold

    def to_dict(self) -> dict:
        return {
            "source_id": self.source_id,
            "source_type": self.source_type,
            "target_id": self.target_id,
            "target_type": self.target_type,
            "relationship": self.relationship,
            "confidence": self.confidence,
        }


@dataclass
class ConsistencyIssue:
    """A single inconsistency found in content."""

    location: str = ""
    issue_type: str = ""
    description: str = ""
    suggestion: str = ""
    severity: str = "info"

    def to_dict(self) -> dict:
        return {
            "location": self.location,
            "issue_type": self.issue_type,
            "description": self.description,
            "suggestion": self.suggestion,
            "severity": self.severity,
        }


@dataclass
class ContentConsistencyResult:
    """Aggregated consistency check results."""

    issues: list[ConsistencyIssue] = field(default_factory=list)
    score: float = 1.0
    checked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def calculate_score(self) -> float:
        """Compute a consistency score (1.0 = perfect, 0.0 = many issues)."""
        if not self.issues:
            self.score = 1.0
            return self.score
        severity_weights = {"critical": 3.0, "warning": 2.0, "info": 1.0}
        total_weight = sum(
            severity_weights.get(i.severity, 1.0) for i in self.issues
        )
        max_possible = len(self.issues) * 3.0
        self.score = max(0.0, 1.0 - (total_weight / max_possible))
        return round(self.score, 3)

    def critical_count(self) -> int:
        """Return the number of critical-severity issues."""
        return len([i for i in self.issues if i.severity == "critical"])

    def has_critical(self) -> bool:
        """Return True if any critical issues exist."""
        return self.critical_count() > 0

    def to_dict(self) -> dict:
        return {
            "issues": [i.to_dict() for i in self.issues],
            "score": self.score,
            "checked_at": self.checked_at.isoformat(),
            "critical_count": self.critical_count(),
        }


@dataclass
class MetadataSuggestion:
    """Suggested metadata values with confidence scores."""

    content_id: str = ""
    metadata_type: str = ""
    suggestions: dict[str, float] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def top_suggestion(self) -> tuple[str, float]:
        """Return the metadata key with the highest confidence."""
        if not self.suggestions:
            return ("", 0.0)
        key = max(self.suggestions, key=self.suggestions.get)  # type: ignore[arg-type]
        return (key, self.suggestions[key])

    def filter_confident(self, threshold: float = 0.5) -> dict[str, float]:
        """Return only suggestions above the confidence threshold."""
        return {k: v for k, v in self.suggestions.items() if v >= threshold}

    def to_dict(self) -> dict:
        return {
            "content_id": self.content_id,
            "metadata_type": self.metadata_type,
            "suggestions": dict(self.suggestions),
            "generated_at": self.generated_at.isoformat(),
        }


@dataclass
class AIGenerationAudit:
    """Audit record for an AI-generated content piece."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str = ""
    ai_type: str = ""
    input_hash: str = ""
    output_hash: str = ""
    model_version: str = ""
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    instructor_reviewed: bool = False
    reviewed_at: datetime | None = None

    def mark_reviewed(self, approved: bool = True) -> None:
        """Mark the audit record as instructor-reviewed."""
        self.instructor_reviewed = approved
        self.reviewed_at = datetime.now(timezone.utc)

    def is_pending_review(self) -> bool:
        """Return True if the record still needs instructor review."""
        return not self.instructor_reviewed

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "content_id": self.content_id,
            "ai_type": self.ai_type,
            "input_hash": self.input_hash,
            "output_hash": self.output_hash,
            "model_version": self.model_version,
            "generated_at": self.generated_at.isoformat(),
            "instructor_reviewed": self.instructor_reviewed,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
        }
