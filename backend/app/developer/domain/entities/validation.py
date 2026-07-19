"""ValidationRule, ValidationResult, and ValidationReport entities."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone


class ValidationRule:
    """Defines a single validation check that can be executed."""

    def __init__(
        self,
        id: str | None = None,
        name: str = "",
        rule_type: str = "schema",
        description: str = "",
        severity: str = "error",
        check_fn: str = "",
    ) -> None:
        self.id: str = id or str(uuid.uuid4())
        self.name: str = name
        self.rule_type: str = rule_type
        self.description: str = description
        self.severity: str = severity
        self.check_fn: str = check_fn

    def is_blocking(self) -> bool:
        """Return True when this rule has error or critical severity."""
        return self.severity in ("error", "critical")

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "rule_type": self.rule_type,
            "description": self.description,
            "severity": self.severity,
            "check_fn": self.check_fn,
        }


class ValidationResult:
    """Outcome of running a single validation rule against a target."""

    def __init__(
        self,
        id: str | None = None,
        rule_id: str = "",
        target_id: str = "",
        target_type: str = "",
        passed: bool = False,
        message: str = "",
        evidence: list[str] | None = None,
        checked_at: datetime | None = None,
    ) -> None:
        self.id: str = id or str(uuid.uuid4())
        self.rule_id: str = rule_id
        self.target_id: str = target_id
        self.target_type: str = target_type
        self.passed: bool = passed
        self.message: str = message
        self.evidence: list[str] = evidence if evidence is not None else []
        self.checked_at: datetime = checked_at or datetime.now(timezone.utc)

    def add_evidence(self, item: str) -> None:
        """Record an evidence item supporting this result."""
        self.evidence.append(item)

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "id": self.id,
            "rule_id": self.rule_id,
            "target_id": self.target_id,
            "target_type": self.target_type,
            "passed": self.passed,
            "message": self.message,
            "evidence": list(self.evidence),
            "checked_at": self.checked_at.isoformat(),
        }


class ValidationReport:
    """Aggregated report from validating many rules against a target."""

    def __init__(
        self,
        id: str | None = None,
        name: str = "",
        target_type: str = "",
        results: list[ValidationResult] | None = None,
        overall_status: str = "pending",
        score: float = 0.0,
        generated_at: datetime | None = None,
    ) -> None:
        self.id: str = id or str(uuid.uuid4())
        self.name: str = name
        self.target_type: str = target_type
        self.results: list[ValidationResult] = results if results is not None else []
        self.overall_status: str = overall_status
        self.score: float = score
        self.generated_at: datetime = generated_at or datetime.now(timezone.utc)

    def add_result(self, result: ValidationResult) -> None:
        """Append a validation result to this report."""
        self.results.append(result)

    def compute_score(self) -> float:
        """Calculate the pass-rate score (0.0 – 1.0) from stored results."""
        if not self.results:
            self.score = 0.0
            return self.score
        passed = sum(1 for r in self.results if r.passed)
        self.score = round(passed / len(self.results), 4)
        return self.score

    def compute_overall_status(self) -> str:
        """Derive overall status from contained results."""
        if not self.results:
            self.overall_status = "empty"
            return self.overall_status
        all_passed = all(r.passed for r in self.results)
        any_failed = any(not r.passed for r in self.results)
        if all_passed:
            self.overall_status = "passed"
        elif any_failed:
            self.overall_status = "failed"
        else:
            self.overall_status = "warning"
        return self.overall_status

    def failed_results(self) -> list[ValidationResult]:
        """Return only the results that did not pass."""
        return [r for r in self.results if not r.passed]

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "target_type": self.target_type,
            "results": [r.to_dict() for r in self.results],
            "overall_status": self.overall_status,
            "score": self.score,
            "generated_at": self.generated_at.isoformat(),
        }
