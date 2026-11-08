"""Release engineering domain entities."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class ReleasePhase(str, Enum):
    """Lifecycle phases for a release."""

    PLANNING = "planning"
    DEVELOPMENT = "development"
    RC = "rc"
    STABLE = "stable"
    LTS = "lts"


@dataclass
class ReleasePlan:
    """Plans a single release from planning through to LTS."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    version: str = ""
    code_name: str = ""
    status: ReleasePhase = ReleasePhase.PLANNING
    end_date: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def advance(self) -> None:
        """Move the release to the next phase."""
        phases = list(ReleasePhase)
        idx = phases.index(self.status)
        if idx < len(phases) - 1:
            self.status = phases[idx + 1]

    def is_complete(self) -> bool:
        """Return ``True`` when the release has reached stable or LTS."""
        return self.status in (ReleasePhase.STABLE, ReleasePhase.LTS)

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "id": self.id,
            "version": self.version,
            "code_name": self.code_name,
            "status": self.status.value,
            "end_date": self.end_date,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class ReleaseValidation:
    """Result of a single validation check run against a release."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    release_id: str = ""
    validation_type: str = ""
    status: str = "pending"
    details: str = ""
    validated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def mark_passed(self, details_text: str = "") -> None:
        """Record a passing result."""
        self.status = "passed"
        self.details = details_text
        self.validated_at = datetime.now(timezone.utc)

    def mark_failed(self, details_text: str = "") -> None:
        """Record a failing result."""
        self.status = "failed"
        self.details = details_text
        self.validated_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "id": self.id,
            "release_id": self.release_id,
            "validation_type": self.validation_type,
            "status": self.status,
            "details": self.details,
            "validated_at": self.validated_at.isoformat(),
        }


@dataclass
class PackagingResult:
    """Outcome of building a distributable package for a release."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    release_id: str = ""
    platform: str = ""
    package_type: str = ""
    output_path: str = ""
    checksum: str = ""
    built_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "id": self.id,
            "release_id": self.release_id,
            "platform": self.platform,
            "package_type": self.package_type,
            "output_path": self.output_path,
            "checksum": self.checksum,
            "built_at": self.built_at.isoformat(),
        }


@dataclass
class RegressionResult:
    """Summary of a regression test run for a release."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    release_id: str = ""
    tests_run: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    coverage: float = 0.0
    run_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def pass_rate(self) -> float:
        """Fraction of tests that passed."""
        if self.tests_run <= 0:
            return 0.0
        return self.passed / self.tests_run

    def is_green(self) -> bool:
        """Return ``True`` when there are zero failures."""
        return self.failed == 0

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "id": self.id,
            "release_id": self.release_id,
            "tests_run": self.tests_run,
            "passed": self.passed,
            "failed": self.failed,
            "skipped": self.skipped,
            "coverage": self.coverage,
            "run_at": self.run_at.isoformat(),
        }


@dataclass
class ReleaseHistoryEntry:
    """Historical record of a published release."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    version: str = ""
    release_date: str = ""
    summary: str = ""
    highlights: list[str] = field(default_factory=list)
    known_issues: list[str] = field(default_factory=list)
    status: str = "published"

    def add_highlight(self, text: str) -> None:
        """Append a highlight entry."""
        if text not in self.highlights:
            self.highlights.append(text)

    def add_known_issue(self, text: str) -> None:
        """Append a known issue."""
        if text not in self.known_issues:
            self.known_issues.append(text)

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "id": self.id,
            "version": self.version,
            "release_date": self.release_date,
            "summary": self.summary,
            "highlights": list(self.highlights),
            "known_issues": list(self.known_issues),
            "status": self.status,
        }
