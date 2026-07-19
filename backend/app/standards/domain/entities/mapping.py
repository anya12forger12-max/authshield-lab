"""Domain entities for curriculum mappings and coverage analysis."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class MappingEvidence:
    """A piece of evidence supporting a curriculum mapping."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    mapping_id: str = ""
    evidence_type: str = ""
    description: str = ""
    reference_id: str = ""
    added_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "mapping_id": self.mapping_id,
            "evidence_type": self.evidence_type,
            "description": self.description,
            "reference_id": self.reference_id,
            "added_at": self.added_at.isoformat(),
        }


@dataclass
class CurriculumMapping:
    """Maps a source element to a target element across frameworks."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_id: str = ""
    source_type: str = ""
    target_id: str = ""
    target_type: str = ""
    coverage_level: str = "partial"
    confidence: float = 0.0
    review_status: str = "pending"
    evidence: list[MappingEvidence] = field(default_factory=list)
    instructor_notes: str = ""
    related_competencies: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def add_evidence(self, evidence_item: MappingEvidence) -> None:
        evidence_item.mapping_id = self.id
        self.evidence.append(evidence_item)
        self._touch()

    def remove_evidence(self, evidence_id: str) -> bool:
        for idx, ev in enumerate(self.evidence):
            if ev.id == evidence_id:
                self.evidence.pop(idx)
                self._touch()
                return True
        return False

    def set_review_status(self, status: str) -> None:
        valid = {"pending", "approved", "rejected", "needs_revision"}
        if status not in valid:
            raise ValueError(f"Invalid review status: {status}. Must be one of {valid}")
        self.review_status = status
        self._touch()

    def update_confidence(self, confidence: float) -> None:
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        self.confidence = confidence
        self._touch()

    def add_related_competency(self, competency_id: str) -> None:
        if competency_id not in self.related_competencies:
            self.related_competencies.append(competency_id)
            self._touch()

    def remove_related_competency(self, competency_id: str) -> bool:
        if competency_id in self.related_competencies:
            self.related_competencies.remove(competency_id)
            self._touch()
            return True
        return False

    def update_notes(self, notes: str) -> None:
        self.instructor_notes = notes
        self._touch()

    def evidence_count(self) -> int:
        return len(self.evidence)

    def _touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "source_id": self.source_id,
            "source_type": self.source_type,
            "target_id": self.target_id,
            "target_type": self.target_type,
            "coverage_level": self.coverage_level,
            "confidence": self.confidence,
            "review_status": self.review_status,
            "evidence": [e.to_dict() for e in self.evidence],
            "instructor_notes": self.instructor_notes,
            "related_competencies": list(self.related_competencies),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class MappingGap:
    """Represents a gap found during mapping analysis."""

    item_id: str = ""
    item_name: str = ""
    gap_type: str = ""
    severity: str = "low"
    recommendation: str = ""

    def to_dict(self) -> dict:
        return {
            "item_id": self.item_id,
            "item_name": self.item_name,
            "gap_type": self.gap_type,
            "severity": self.severity,
            "recommendation": self.recommendation,
        }


@dataclass
class MappingBulkResult:
    """Result of a bulk mapping operation."""

    total: int = 0
    mapped: int = 0
    unmapped: int = 0
    gaps: list[str] = field(default_factory=list)

    def coverage_pct(self) -> float:
        if self.total == 0:
            return 0.0
        return (self.mapped / self.total) * 100.0

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "mapped": self.mapped,
            "unmapped": self.unmapped,
            "coverage_pct": self.coverage_pct(),
            "gaps": list(self.gaps),
        }


@dataclass
class CoverageReport:
    """Report showing how well a framework is covered by mappings."""

    framework_id: str = ""
    total_items: int = 0
    mapped_items: int = 0
    coverage_pct: float = 0.0
    gaps: list[MappingGap] = field(default_factory=list)
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def calculate_coverage(self) -> None:
        if self.total_items == 0:
            self.coverage_pct = 0.0
        else:
            self.coverage_pct = (self.mapped_items / self.total_items) * 100.0

    def add_gap(self, gap: MappingGap) -> None:
        self.gaps.append(gap)

    def gaps_by_severity(self, severity: str) -> list[MappingGap]:
        return [g for g in self.gaps if g.severity == severity]

    def to_dict(self) -> dict:
        return {
            "framework_id": self.framework_id,
            "total_items": self.total_items,
            "mapped_items": self.mapped_items,
            "coverage_pct": self.coverage_pct,
            "gaps": [g.to_dict() for g in self.gaps],
            "generated_at": self.generated_at.isoformat(),
        }
