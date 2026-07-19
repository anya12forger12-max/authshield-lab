"""Certification module domain events."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class CertificationCompleted:
    """Emitted when a certification process completes successfully."""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    certification_id: str = ""
    cert_type: str = ""
    name: str = ""
    approved_by: str = ""
    module: str = "certification"
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "event_id": self.event_id,
            "certification_id": self.certification_id,
            "cert_type": self.cert_type,
            "name": self.name,
            "approved_by": self.approved_by,
            "module": self.module,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class CertificationFailed:
    """Emitted when a certification process fails."""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    certification_id: str = ""
    cert_type: str = ""
    name: str = ""
    reason: str = ""
    module: str = "certification"
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "event_id": self.event_id,
            "certification_id": self.certification_id,
            "cert_type": self.cert_type,
            "name": self.name,
            "reason": self.reason,
            "module": self.module,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class PlatformValidated:
    """Emitted when platform-wide validation completes."""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    report_id: str = ""
    overall_compliance: float = 0.0
    subsystems_passed: int = 0
    subsystems_failed: int = 0
    module: str = "certification"
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "event_id": self.event_id,
            "report_id": self.report_id,
            "overall_compliance": self.overall_compliance,
            "subsystems_passed": self.subsystems_passed,
            "subsystems_failed": self.subsystems_failed,
            "module": self.module,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ReleaseEngineered:
    """Emitted when a release reaches a stable state."""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    release_id: str = ""
    version: str = ""
    code_name: str = ""
    status: str = ""
    module: str = "certification"
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "event_id": self.event_id,
            "release_id": self.release_id,
            "version": self.version,
            "code_name": self.code_name,
            "status": self.status,
            "module": self.module,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class RecoveryTested:
    """Emitted when a disaster recovery test completes."""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    test_id: str = ""
    backup_id: str = ""
    status: str = ""
    data_integrity: bool = True
    duration_ms: int = 0
    module: str = "certification"
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "event_id": self.event_id,
            "test_id": self.test_id,
            "backup_id": self.backup_id,
            "status": self.status,
            "data_integrity": self.data_integrity,
            "duration_ms": self.duration_ms,
            "module": self.module,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class SustainabilityReportGenerated:
    """Emitted when a sustainability dashboard is produced."""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    maintenance_score: float = 0.0
    technical_debt_hours: float = 0.0
    deprecated_deps: int = 0
    module: str = "certification"
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "event_id": self.event_id,
            "maintenance_score": self.maintenance_score,
            "technical_debt_hours": self.technical_debt_hours,
            "deprecated_deps": self.deprecated_deps,
            "module": self.module,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ValidationCompleted:
    """Emitted when a subsystem or full validation cycle finishes."""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    subsystem: str = ""
    checks_passed: int = 0
    checks_failed: int = 0
    compliance_pct: float = 0.0
    module: str = "certification"
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "event_id": self.event_id,
            "subsystem": self.subsystem,
            "checks_passed": self.checks_passed,
            "checks_failed": self.checks_failed,
            "compliance_pct": self.compliance_pct,
            "module": self.module,
            "timestamp": self.timestamp.isoformat(),
        }
