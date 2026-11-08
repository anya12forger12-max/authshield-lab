"""Competency domain entities for the LMS module."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class CompetencyLevel(str, Enum):
    """Mastery level for a competency."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class CompetencyStatus(str, Enum):
    """Progress status for a learner's competency tracking."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    ACHIEVED = "achieved"
    MASTERED = "mastered"


@dataclass
class Competency:
    """A single skill or knowledge area that can be assessed."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    domain: str = ""
    level: CompetencyLevel = CompetencyLevel.BEGINNER
    framework_id: Optional[str] = None

    @property
    def level_value(self) -> int:
        """Return a numeric value for ordering competencies by level."""
        ordering = {
            CompetencyLevel.BEGINNER: 1,
            CompetencyLevel.INTERMEDIATE: 2,
            CompetencyLevel.ADVANCED: 3,
            CompetencyLevel.EXPERT: 4,
        }
        return ordering.get(self.level, 0)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "domain": self.domain,
            "level": self.level.value,
            "framework_id": self.framework_id,
        }


@dataclass
class CompetencyFramework:
    """A named collection of related competencies with versioning."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    version: str = "1.0"
    competencies: list[Competency] = field(default_factory=list)

    def add_competency(self, competency: Competency) -> None:
        """Add a competency to the framework."""
        competency.framework_id = self.id
        self.competencies.append(competency)

    def remove_competency(self, competency_id: str) -> bool:
        """Remove a competency by ID. Returns ``True`` if found and removed."""
        for i, c in enumerate(self.competencies):
            if c.id == competency_id:
                self.competencies.pop(i)
                return True
        return False

    def get_competency(self, competency_id: str) -> Optional[Competency]:
        """Return a competency by ID, or ``None``."""
        for c in self.competencies:
            if c.id == competency_id:
                return c
        return None

    def get_by_domain(self, domain: str) -> list[Competency]:
        """Return all competencies in the given domain."""
        return [c for c in self.competencies if c.domain == domain]

    def get_by_level(self, level: CompetencyLevel) -> list[Competency]:
        """Return all competencies at the given level."""
        return [c for c in self.competencies if c.level == level]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "competencies": [c.to_dict() for c in self.competencies],
        }


@dataclass
class LearnerCompetencyProgress:
    """Tracks a learner's progress on a specific competency."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    learner_id: str = ""
    competency_id: str = ""
    status: CompetencyStatus = CompetencyStatus.NOT_STARTED
    evidence: list[str] = field(default_factory=list)
    assessed_at: Optional[datetime] = None
    assessor_id: Optional[str] = None

    def start(self) -> None:
        """Transition to in-progress."""
        if self.status != CompetencyStatus.NOT_STARTED:
            raise ValueError(f"Cannot start competency in '{self.status.value}' status.")
        self.status = CompetencyStatus.IN_PROGRESS

    def achieve(self, assessor_id: Optional[str] = None) -> None:
        """Mark the competency as achieved."""
        if self.status not in (CompetencyStatus.NOT_STARTED, CompetencyStatus.IN_PROGRESS):
            raise ValueError(f"Cannot achieve competency in '{self.status.value}' status.")
        self.status = CompetencyStatus.ACHIEVED
        self.assessed_at = datetime.now(timezone.utc)
        if assessor_id:
            self.assessor_id = assessor_id

    def master(self, assessor_id: Optional[str] = None) -> None:
        """Mark the competency as mastered (highest level)."""
        if self.status not in (CompetencyStatus.ACHIEVED, CompetencyStatus.IN_PROGRESS):
            raise ValueError(f"Cannot master competency in '{self.status.value}' status.")
        self.status = CompetencyStatus.MASTERED
        self.assessed_at = datetime.now(timezone.utc)
        if assessor_id:
            self.assessor_id = assessor_id

    def add_evidence(self, description: str) -> None:
        """Add an evidence item to the progress record."""
        if not description.strip():
            raise ValueError("Evidence description cannot be empty.")
        self.evidence.append(description.strip())

    @property
    def is_completed(self) -> bool:
        """Return ``True`` if the status is achieved or mastered."""
        return self.status in (CompetencyStatus.ACHIEVED, CompetencyStatus.MASTERED)

    @property
    def evidence_count(self) -> int:
        return len(self.evidence)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "learner_id": self.learner_id,
            "competency_id": self.competency_id,
            "status": self.status.value,
            "evidence": list(self.evidence),
            "assessed_at": self.assessed_at.isoformat() if self.assessed_at else None,
            "assessor_id": self.assessor_id,
            "is_completed": self.is_completed,
            "evidence_count": self.evidence_count,
        }
