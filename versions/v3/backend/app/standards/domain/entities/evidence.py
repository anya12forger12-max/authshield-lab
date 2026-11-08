"""Domain entities for evidence collection and review."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal

EvidenceType = Literal[
    "assessment_result",
    "practical_exercise",
    "project",
    "reflection",
    "instructor_review",
    "documentation",
    "a11y_report",
    "audit_report",
]

VALID_EVIDENCE_TYPES: set[str] = {
    "assessment_result",
    "practical_exercise",
    "project",
    "reflection",
    "instructor_review",
    "documentation",
    "a11y_report",
    "audit_report",
}


@dataclass
class EvidenceItem:
    """A single piece of evidence within a collection."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    collection_id: str = ""
    evidence_type: str = "assessment_result"
    description: str = ""
    source_id: str = ""
    source_type: str = ""
    date_collected: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    version: int = 1
    reviewed: bool = False

    def validate_type(self) -> None:
        if self.evidence_type not in VALID_EVIDENCE_TYPES:
            raise ValueError(
                f"Invalid evidence_type: {self.evidence_type}. "
                f"Must be one of {VALID_EVIDENCE_TYPES}"
            )

    def mark_reviewed(self) -> None:
        self.reviewed = True

    def bump_version(self) -> None:
        self.version += 1

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "collection_id": self.collection_id,
            "evidence_type": self.evidence_type,
            "description": self.description,
            "source_id": self.source_id,
            "source_type": self.source_type,
            "date_collected": self.date_collected.isoformat(),
            "version": self.version,
            "reviewed": self.reviewed,
        }


@dataclass
class EvidenceSearchResult:
    """A single search result for evidence items."""

    item_id: str = ""
    title: str = ""
    type: str = ""
    snippet: str = ""
    relevance: float = 0.0

    def to_dict(self) -> dict:
        return {
            "item_id": self.item_id,
            "title": self.title,
            "type": self.type,
            "snippet": self.snippet,
            "relevance": self.relevance,
        }


@dataclass
class EvidenceCollection:
    """A collection of evidence items tied to a framework."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    framework_id: str = ""
    evidence: list[EvidenceItem] = field(default_factory=list)
    total: int = 0
    collected: int = 0
    pending: int = 0

    def add_item(self, item: EvidenceItem) -> None:
        item.collection_id = self.id
        self.evidence.append(item)
        self.total = len(self.evidence)
        self._recalc_counts()

    def remove_item(self, item_id: str) -> bool:
        for idx, item in enumerate(self.evidence):
            if item.id == item_id:
                self.evidence.pop(idx)
                self.total = len(self.evidence)
                self._recalc_counts()
                return True
        return False

    def find_item(self, item_id: str) -> EvidenceItem | None:
        for item in self.evidence:
            if item.id == item_id:
                return item
        return None

    def items_by_type(self, evidence_type: str) -> list[EvidenceItem]:
        return [i for i in self.evidence if i.evidence_type == evidence_type]

    def reviewed_items(self) -> list[EvidenceItem]:
        return [i for i in self.evidence if i.reviewed]

    def unreviewed_items(self) -> list[EvidenceItem]:
        return [i for i in self.evidence if not i.reviewed]

    def search(self, query: str) -> list[EvidenceSearchResult]:
        q = query.lower()
        results: list[EvidenceSearchResult] = []
        for item in self.evidence:
            if q in item.description.lower():
                results.append(EvidenceSearchResult(
                    item_id=item.id,
                    title=item.description[:80],
                    type=item.evidence_type,
                    snippet=item.description[:200],
                    relevance=1.0 if q in item.description.lower() else 0.5,
                ))
        return results

    def coverage_pct(self) -> float:
        if self.total == 0:
            return 0.0
        return (self.collected / self.total) * 100.0 if self.total > 0 else 0.0

    def _recalc_counts(self) -> None:
        self.collected = len(self.evidence)
        self.pending = max(0, self.total - self.collected)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "framework_id": self.framework_id,
            "evidence": [e.to_dict() for e in self.evidence],
            "total": self.total,
            "collected": self.collected,
            "pending": self.pending,
            "coverage_pct": self.coverage_pct(),
        }
