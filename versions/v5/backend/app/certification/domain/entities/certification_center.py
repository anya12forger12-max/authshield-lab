"""Certification center domain entities."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class CertificationStatus(str, Enum):
    """Lifecycle states for a platform certification."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    CERTIFIED = "certified"
    FAILED = "failed"
    EXPIRED = "expired"


@dataclass
class PlatformCertification:
    """A single certification record tracking lifecycle from application to award."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    cert_type: str = ""
    status: CertificationStatus = CertificationStatus.PENDING
    certified_at: datetime | None = None
    expires_at: datetime | None = None
    validation_results: dict = field(default_factory=dict)
    evidence: list[str] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)
    findings: list[str] = field(default_factory=list)
    corrective_actions: list[str] = field(default_factory=list)
    approved_by: str | None = None
    approved_at: datetime | None = None

    def is_active(self) -> bool:
        """Return ``True`` when the certification is currently valid."""
        if self.status != CertificationStatus.CERTIFIED:
            return False
        if self.expires_at is None:
            return True
        return datetime.now(timezone.utc) < self.expires_at

    def add_evidence(self, item: str) -> None:
        """Append an evidence item if not already recorded."""
        if item not in self.evidence:
            self.evidence.append(item)

    def add_finding(self, finding: str) -> None:
        """Append a finding."""
        self.findings.append(finding)

    def add_corrective_action(self, action: str) -> None:
        """Append a corrective action."""
        self.corrective_actions.append(action)

    def approve(self, approver: str) -> None:
        """Transition to certified state."""
        self.status = CertificationStatus.CERTIFIED
        self.approved_by = approver
        self.approved_at = datetime.now(timezone.utc)
        self.certified_at = self.approved_at

    def revoke(self) -> None:
        """Transition to failed state."""
        self.status = CertificationStatus.FAILED

    def expire(self) -> None:
        """Transition to expired state."""
        self.status = CertificationStatus.EXPIRED

    def mark_in_progress(self) -> None:
        """Transition from pending to in_progress."""
        self.status = CertificationStatus.IN_PROGRESS

    def completion_ratio(self, total_requirements: int) -> float:
        """Return the fraction of evidence items against *total_requirements*."""
        if total_requirements <= 0:
            return 0.0
        return len(self.evidence) / total_requirements

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "cert_type": self.cert_type,
            "status": self.status.value,
            "certified_at": self.certified_at.isoformat() if self.certified_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "validation_results": dict(self.validation_results),
            "evidence": list(self.evidence),
            "metrics": dict(self.metrics),
            "findings": list(self.findings),
            "corrective_actions": list(self.corrective_actions),
            "approved_by": self.approved_by,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
        }


@dataclass
class CertificationRequirement:
    """A single prerequisite that must be satisfied for a certification."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    certification_id: str = ""
    requirement: str = ""
    description: str = ""
    met: bool = False
    evidence: str = ""

    def fulfill(self, evidence_text: str = "") -> None:
        """Mark the requirement as met."""
        self.met = True
        self.evidence = evidence_text

    def unfulfill(self) -> None:
        """Mark the requirement as not met."""
        self.met = False
        self.evidence = ""

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "id": self.id,
            "certification_id": self.certification_id,
            "requirement": self.requirement,
            "description": self.description,
            "met": self.met,
            "evidence": self.evidence,
        }


@dataclass
class PlatformCertificationReport:
    """Aggregated report across multiple certifications."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    certifications: list[PlatformCertification] = field(default_factory=list)
    overall_status: str = "pending"
    score: float = 0.0
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def compute_score(self) -> float:
        """Derive ``score`` from the proportion of certified items."""
        if not self.certifications:
            self.score = 0.0
            return self.score
        certified = sum(
            1 for c in self.certifications if c.status == CertificationStatus.CERTIFIED
        )
        self.score = (certified / len(self.certifications)) * 100.0
        return self.score

    def compute_overall_status(self) -> str:
        """Derive ``overall_status`` from child certification states."""
        if not self.certifications:
            self.overall_status = "pending"
            return self.overall_status
        statuses = [c.status for c in self.certifications]
        if all(s == CertificationStatus.CERTIFIED for s in statuses):
            self.overall_status = "certified"
        elif any(s == CertificationStatus.FAILED for s in statuses):
            self.overall_status = "failed"
        elif any(s == CertificationStatus.IN_PROGRESS for s in statuses):
            self.overall_status = "in_progress"
        else:
            self.overall_status = "pending"
        return self.overall_status

    def active_certifications(self) -> list[PlatformCertification]:
        """Return only certifications that are currently active."""
        return [c for c in self.certifications if c.is_active()]

    def expired_certifications(self) -> list[PlatformCertification]:
        """Return only certifications that have expired."""
        return [c for c in self.certifications if c.status == CertificationStatus.EXPIRED]

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "certifications": [c.to_dict() for c in self.certifications],
            "overall_status": self.overall_status,
            "score": self.score,
            "generated_at": self.generated_at.isoformat(),
        }
