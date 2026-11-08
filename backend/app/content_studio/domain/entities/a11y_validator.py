"""Accessibility validator domain entities."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class A11yCheck:
    """A single accessibility check result."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    check_type: str = ""
    description: str = ""
    passed: bool = False
    element: str = ""
    evidence: str = ""
    remediation: str | None = None
    severity: str = "error"

    def mark_passed(self) -> None:
        self.passed = True

    def mark_failed(self, remediation: str | None = None) -> None:
        self.passed = False
        if remediation:
            self.remediation = remediation

    def is_critical(self) -> bool:
        return self.severity == "critical" and not self.passed

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "check_type": self.check_type,
            "description": self.description,
            "passed": self.passed,
            "element": self.element,
            "evidence": self.evidence,
            "remediation": self.remediation,
            "severity": self.severity,
        }


@dataclass
class A11yValidationReport:
    """Aggregated report of all accessibility checks for a piece of content."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str = ""
    checks: list[A11yCheck] = field(default_factory=list)
    total: int = 0
    passed: int = 0
    failed: int = 0
    na: int = 0
    compliance_pct: float = 0.0
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def add_check(self, check: A11yCheck) -> None:
        self.checks.append(check)
        self._recalculate()

    def add_checks(self, checks: list[A11yCheck]) -> None:
        self.checks.extend(checks)
        self._recalculate()

    def get_failed_checks(self) -> list[A11yCheck]:
        return [c for c in self.checks if not c.passed]

    def get_critical_failures(self) -> list[A11yCheck]:
        return [c for c in self.checks if not c.passed and c.severity == "critical"]

    def get_checks_by_type(self, check_type: str) -> list[A11yCheck]:
        return [c for c in self.checks if c.check_type == check_type]

    def is_compliant(self, threshold: float = 100.0) -> bool:
        return self.compliance_pct >= threshold

    def has_critical_failures(self) -> bool:
        return len(self.get_critical_failures()) > 0

    def _recalculate(self) -> None:
        self.total = len(self.checks)
        self.passed = sum(1 for c in self.checks if c.passed)
        self.failed = sum(1 for c in self.checks if not c.passed)
        self.na = self.total - self.passed - self.failed
        checkable = self.total - self.na
        self.compliance_pct = round(self.passed / checkable * 100, 2) if checkable > 0 else 0.0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "content_id": self.content_id,
            "checks": [c.to_dict() for c in self.checks],
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "na": self.na,
            "compliance_pct": self.compliance_pct,
            "generated_at": self.generated_at.isoformat(),
        }


@dataclass
class A11yRemediation:
    """Tracks a remediation action for a failed accessibility check."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    report_id: str = ""
    check_id: str = ""
    action: str = ""
    priority: str = "high"
    status: str = "open"
    assignee: str = ""

    def start(self) -> None:
        self.status = "in_progress"

    def complete(self) -> None:
        self.status = "completed"

    def dismiss(self, reason: str = "") -> None:
        self.status = "dismissed"

    def reassign(self, new_assignee: str) -> None:
        self.assignee = new_assignee

    def update_priority(self, priority: str) -> None:
        self.priority = priority

    def is_open(self) -> bool:
        return self.status in {"open", "in_progress"}

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "report_id": self.report_id,
            "check_id": self.check_id,
            "action": self.action,
            "priority": self.priority,
            "status": self.status,
            "assignee": self.assignee,
        }
