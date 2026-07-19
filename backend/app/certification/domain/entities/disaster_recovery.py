"""Disaster recovery domain entities."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class BackupValidation:
    """Result of validating a backup's integrity and restorability."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    backup_id: str = ""
    backup_type: str = ""
    size_bytes: int = 0
    integrity: bool = True
    restorable: bool = True
    validated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def is_healthy(self) -> bool:
        """Return ``True`` when both integrity and restorability pass."""
        return self.integrity and self.restorable

    def size_mb(self) -> float:
        """Return backup size in megabytes."""
        return self.size_bytes / (1024 * 1024)

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "id": self.id,
            "backup_id": self.backup_id,
            "backup_type": self.backup_type,
            "size_bytes": self.size_bytes,
            "integrity": self.integrity,
            "restorable": self.restorable,
            "validated_at": self.validated_at.isoformat(),
        }


@dataclass
class RestoreTest:
    """Record of an attempted restore from a backup."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    test_id: str = ""
    backup_id: str = ""
    status: str = "pending"
    duration_ms: int = 0
    data_integrity: bool = True
    completed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def mark_success(self, duration: int = 0) -> None:
        """Record a successful restore."""
        self.status = "success"
        self.duration_ms = duration
        self.data_integrity = True
        self.completed_at = datetime.now(timezone.utc)

    def mark_failure(self, duration: int = 0, integrity: bool = False) -> None:
        """Record a failed restore."""
        self.status = "failed"
        self.duration_ms = duration
        self.data_integrity = integrity
        self.completed_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "id": self.id,
            "test_id": self.test_id,
            "backup_id": self.backup_id,
            "status": self.status,
            "duration_ms": self.duration_ms,
            "data_integrity": self.data_integrity,
            "completed_at": self.completed_at.isoformat(),
        }


@dataclass
class ArchiveRecovery:
    """Tracks recovery progress from an archived data set."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    archive_id: str = ""
    status: str = "pending"
    items_recovered: int = 0
    completeness: float = 0.0
    completed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def mark_complete(self, recovered: int, total: int) -> None:
        """Mark recovery as complete with final counts."""
        self.status = "complete"
        self.items_recovered = recovered
        self.completeness = (recovered / total * 100.0) if total > 0 else 0.0
        self.completed_at = datetime.now(timezone.utc)

    def mark_failed(self) -> None:
        """Mark recovery as failed."""
        self.status = "failed"
        self.completed_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "id": self.id,
            "archive_id": self.archive_id,
            "status": self.status,
            "items_recovered": self.items_recovered,
            "completeness": self.completeness,
            "completed_at": self.completed_at.isoformat(),
        }


@dataclass
class RecoveryReadinessReport:
    """High-level readiness summary across all recovery dimensions."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    backup_health: float = 0.0
    restore_success_rate: float = 0.0
    archive_recovery: float = 0.0
    config_recovery: float = 0.0
    doc_recovery: float = 0.0
    overall_readiness: float = 0.0
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def compute_overall(self) -> float:
        """Derive ``overall_readiness`` as the average of sub-scores."""
        scores = [
            self.backup_health,
            self.restore_success_rate,
            self.archive_recovery,
            self.config_recovery,
            self.doc_recovery,
        ]
        valid = [s for s in scores if s > 0]
        self.overall_readiness = sum(valid) / len(valid) if valid else 0.0
        return self.overall_readiness

    def is_ready(self, threshold: float = 80.0) -> bool:
        """Return ``True`` when overall readiness meets *threshold*."""
        return self.overall_readiness >= threshold

    def weakest_dimension(self) -> str:
        """Return the name of the dimension with the lowest score."""
        dims = {
            "backup_health": self.backup_health,
            "restore_success_rate": self.restore_success_rate,
            "archive_recovery": self.archive_recovery,
            "config_recovery": self.config_recovery,
            "doc_recovery": self.doc_recovery,
        }
        if not dims:
            return "unknown"
        return min(dims, key=dims.get)  # type: ignore[arg-type]

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "id": self.id,
            "backup_health": self.backup_health,
            "restore_success_rate": self.restore_success_rate,
            "archive_recovery": self.archive_recovery,
            "config_recovery": self.config_recovery,
            "doc_recovery": self.doc_recovery,
            "overall_readiness": self.overall_readiness,
            "generated_at": self.generated_at.isoformat(),
        }
