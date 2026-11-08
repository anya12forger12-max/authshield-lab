"""Platform validation domain entities."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class ValidationCheck:
    """Result of a single validation check within a subsystem."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    subsystem: str = ""
    check_name: str = ""
    status: str = "pending"
    details: str = ""
    evidence: str = ""
    checked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def mark_passed(self, details_text: str = "", evidence_text: str = "") -> None:
        """Record a passing check."""
        self.status = "passed"
        self.details = details_text
        self.evidence = evidence_text
        self.checked_at = datetime.now(timezone.utc)

    def mark_failed(self, details_text: str = "", evidence_text: str = "") -> None:
        """Record a failing check."""
        self.status = "failed"
        self.details = details_text
        self.evidence = evidence_text
        self.checked_at = datetime.now(timezone.utc)

    def mark_skipped(self, reason: str = "") -> None:
        """Record a skipped check."""
        self.status = "skipped"
        self.details = reason
        self.checked_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "id": self.id,
            "subsystem": self.subsystem,
            "check_name": self.check_name,
            "status": self.status,
            "details": self.details,
            "evidence": self.evidence,
            "checked_at": self.checked_at.isoformat(),
        }


@dataclass
class SubsystemValidation:
    """Aggregated validation result for a single subsystem."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    subsystem: str = ""
    checks: list[ValidationCheck] = field(default_factory=list)
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    compliance_pct: float = 0.0
    validated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def add_check(self, check: ValidationCheck) -> None:
        """Append a check and refresh counters."""
        self.checks.append(check)
        self._recalculate()

    def _recalculate(self) -> None:
        """Recount pass/fail/skip and compliance percentage."""
        self.passed = sum(1 for c in self.checks if c.status == "passed")
        self.failed = sum(1 for c in self.checks if c.status == "failed")
        self.skipped = sum(1 for c in self.checks if c.status == "skipped")
        evaluated = self.passed + self.failed
        self.compliance_pct = (self.passed / evaluated * 100.0) if evaluated > 0 else 0.0

    def is_compliant(self, threshold: float = 100.0) -> bool:
        """Return ``True`` when compliance meets *threshold*."""
        return self.compliance_pct >= threshold

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "id": self.id,
            "subsystem": self.subsystem,
            "checks": [c.to_dict() for c in self.checks],
            "passed": self.passed,
            "failed": self.failed,
            "skipped": self.skipped,
            "compliance_pct": self.compliance_pct,
            "validated_at": self.validated_at.isoformat(),
        }


@dataclass
class PlatformValidationReport:
    """Platform-wide validation report aggregating all subsystem results."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    subsystems: list[SubsystemValidation] = field(default_factory=list)
    overall_passed: int = 0
    overall_failed: int = 0
    overall_compliance: float = 0.0
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def aggregate(self) -> None:
        """Recount totals across all subsystems."""
        self.overall_passed = sum(s.passed for s in self.subsystems)
        self.overall_failed = sum(s.failed for s in self.subsystems)
        evaluated = self.overall_passed + self.overall_failed
        self.overall_compliance = (
            (self.overall_passed / evaluated * 100.0) if evaluated > 0 else 0.0
        )

    def failing_subsystems(self) -> list[SubsystemValidation]:
        """Return subsystems that have at least one failed check."""
        return [s for s in self.subsystems if s.failed > 0]

    def passing_subsystems(self) -> list[SubsystemValidation]:
        """Return subsystems with zero failures."""
        return [s for s in self.subsystems if s.failed == 0]

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "subsystems": [s.to_dict() for s in self.subsystems],
            "overall_passed": self.overall_passed,
            "overall_failed": self.overall_failed,
            "overall_compliance": self.overall_compliance,
            "generated_at": self.generated_at.isoformat(),
        }


@dataclass
class FinalAcceptanceTest:
    """Final gate that aggregates subsystem results for release acceptance."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    version: str = ""
    results: dict[str, SubsystemValidation] = field(default_factory=dict)
    overall_status: str = "pending"
    sign_off_required: list[str] = field(default_factory=list)
    completed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def run(self) -> str:
        """Evaluate all subsystem results and derive ``overall_status``."""
        if not self.results:
            self.overall_status = "pending"
            return self.overall_status
        all_pass = all(s.failed == 0 for s in self.results.values())
        any_fail = any(s.failed > 0 for s in self.results.values())
        if all_pass:
            self.overall_status = "passed"
        elif any_fail:
            self.overall_status = "failed"
        else:
            self.overall_status = "pending"
        self.completed_at = datetime.now(timezone.utc)
        return self.overall_status

    def missing_signoffs(self) -> list[str]:
        """Return required sign-offs that have not yet been provided."""
        signed = {
            name for name, sv in self.results.items() if sv.is_compliant(100.0)
        }
        return [s for s in self.sign_off_required if s not in signed]

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "id": self.id,
            "version": self.version,
            "results": {k: v.to_dict() for k, v in self.results.items()},
            "overall_status": self.overall_status,
            "sign_off_required": list(self.sign_off_required),
            "completed_at": self.completed_at.isoformat(),
        }
