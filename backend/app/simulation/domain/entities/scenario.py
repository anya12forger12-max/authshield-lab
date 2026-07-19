"""Scenario domain entity."""

from __future__ import annotations

import copy
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class ScenarioDifficulty(str, Enum):
    """Difficulty levels for simulation scenarios."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ScenarioStatus(str, Enum):
    """Lifecycle status of a scenario."""

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ScenarioType(str, Enum):
    """Types of simulation scenarios."""

    AUTHENTICATION_REVIEW = "AuthenticationReview"
    ACCOUNT_LOCKOUT_INVESTIGATION = "AccountLockoutInvestigation"
    AUDIT_LOG_ANALYSIS = "AuditLogAnalysis"
    POLICY_VALIDATION = "PolicyValidation"
    BACKUP_VERIFICATION = "BackupVerification"
    SECURE_CONFIGURATION_REVIEW = "SecureConfigurationReview"
    GOVERNANCE_REVIEW = "GovernanceReview"
    COMPLIANCE_REVIEW = "ComplianceReview"
    PRIVACY_ASSESSMENT = "PrivacyAssessment"
    SECURE_ARCHITECTURE_REVIEW = "SecureArchitectureReview"


_VALID_STATUS_TRANSITIONS: dict[ScenarioStatus, set[ScenarioStatus]] = {
    ScenarioStatus.DRAFT: {ScenarioStatus.PUBLISHED},
    ScenarioStatus.PUBLISHED: {ScenarioStatus.ARCHIVED, ScenarioStatus.DRAFT},
    ScenarioStatus.ARCHIVED: {ScenarioStatus.DRAFT},
}


@dataclass
class Scenario:
    """Core scenario entity representing a cybersecurity training scenario.

    Contains all metadata needed to describe, categorize, and manage
    the lifecycle of a training scenario within the Simulation Studio.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    difficulty: ScenarioDifficulty = ScenarioDifficulty.BEGINNER
    learning_objectives: list[str] = field(default_factory=list)
    prerequisites: list[str] = field(default_factory=list)
    estimated_duration_minutes: int = 30
    target_audience: str = ""
    required_competencies: list[str] = field(default_factory=list)
    accessibility_status: str = "pending_review"
    localization_status: str = "en"
    version: int = 1
    tags: list[str] = field(default_factory=list)
    scenario_type: ScenarioType = ScenarioType.AUTHENTICATION_REVIEW
    status: ScenarioStatus = ScenarioStatus.DRAFT
    created_by: str = ""
    scenario_metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # ------------------------------------------------------------------
    # Lifecycle transitions
    # ------------------------------------------------------------------

    def publish(self) -> None:
        """Transition scenario to published status.

        Raises
        ------
        ValueError
            If the current status does not allow publishing.
        """
        allowed = _VALID_STATUS_TRANSITIONS.get(self.status, set())
        if ScenarioStatus.PUBLISHED not in allowed:
            raise ValueError(
                f"Cannot publish scenario from '{self.status.value}' status. "
                f"Allowed transitions: {[s.value for s in allowed]}"
            )
        self.status = ScenarioStatus.PUBLISHED
        self.updated_at = datetime.now(timezone.utc)

    def archive(self) -> None:
        """Transition scenario to archived status.

        Raises
        ------
        ValueError
            If the current status does not allow archiving.
        """
        allowed = _VALID_STATUS_TRANSITIONS.get(self.status, set())
        if ScenarioStatus.ARCHIVED not in allowed:
            raise ValueError(
                f"Cannot archive scenario from '{self.status.value}' status. "
                f"Allowed transitions: {[s.value for s in allowed]}"
            )
        self.status = ScenarioStatus.ARCHIVED
        self.updated_at = datetime.now(timezone.utc)

    def clone(self) -> Scenario:
        """Create a deep copy of this scenario with a new ID and draft status.

        Returns a new Scenario entity that is an independent copy with
        version reset to 1 and status set to draft.
        """
        cloned = copy.deepcopy(self)
        cloned.id = str(uuid.uuid4())
        cloned.status = ScenarioStatus.DRAFT
        cloned.version = 1
        cloned.created_at = datetime.now(timezone.utc)
        cloned.updated_at = datetime.now(timezone.utc)
        return cloned

    def update_version(self) -> None:
        """Increment the version number and update the timestamp."""
        self.version += 1
        self.updated_at = datetime.now(timezone.utc)

    def validate(self) -> list[str]:
        """Validate the scenario and return a list of error messages.

        Returns an empty list if the scenario is valid.
        """
        errors: list[str] = []

        if not self.title or not self.title.strip():
            errors.append("Title is required")
        elif len(self.title) > 256:
            errors.append("Title must be at most 256 characters")

        if not self.description or not self.description.strip():
            errors.append("Description is required")
        elif len(self.description) > 4096:
            errors.append("Description must be at most 4096 characters")

        if self.estimated_duration_minutes < 1:
            errors.append("Estimated duration must be at least 1 minute")
        elif self.estimated_duration_minutes > 1440:
            errors.append("Estimated duration must be at most 1440 minutes (24 hours)")

        if not self.learning_objectives:
            errors.append("At least one learning objective is required")

        if not self.target_audience or not self.target_audience.strip():
            errors.append("Target audience is required")

        if self.version < 1:
            errors.append("Version must be at least 1")

        return errors

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        diff = self.difficulty.value if hasattr(self.difficulty, "value") else self.difficulty
        stype = self.scenario_type.value if hasattr(self.scenario_type, "value") else self.scenario_type
        stat = self.status.value if hasattr(self.status, "value") else self.status
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "difficulty": diff,
            "learning_objectives": list(self.learning_objectives),
            "prerequisites": list(self.prerequisites),
            "estimated_duration_minutes": self.estimated_duration_minutes,
            "target_audience": self.target_audience,
            "required_competencies": list(self.required_competencies),
            "accessibility_status": self.accessibility_status,
            "localization_status": self.localization_status,
            "version": self.version,
            "tags": list(self.tags),
            "scenario_type": stype,
            "status": stat,
            "created_by": self.created_by,
            "metadata": dict(self.scenario_metadata),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
