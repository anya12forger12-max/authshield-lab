"""Publishing domain entities for the Content Production Studio."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class PublishStatus(str, Enum):
    PENDING = "pending"
    VALIDATING = "validating"
    VALIDATED = "validated"
    PUBLISHED = "published"
    REJECTED = "rejected"
    ROLLED_BACK = "rolled_back"


@dataclass
class PublishRequest:
    """A request to publish content through the pipeline."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str = ""
    content_type: str = ""
    version: int = 1
    requested_by: str = ""
    requested_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    validation_results: dict = field(default_factory=dict)
    a11y_check_results: dict = field(default_factory=dict)
    localization_results: dict = field(default_factory=dict)
    dependency_results: dict = field(default_factory=dict)
    digital_signature: str = ""
    release_notes: str = ""
    status: PublishStatus = PublishStatus.PENDING

    def update_status(self, new_status: PublishStatus) -> None:
        self.status = new_status

    def set_validation_results(self, results: dict) -> None:
        self.validation_results = results

    def set_a11y_results(self, results: dict) -> None:
        self.a11y_check_results = results

    def set_localization_results(self, results: dict) -> None:
        self.localization_results = results

    def set_dependency_results(self, results: dict) -> None:
        self.dependency_results = results

    def sign(self, signature: str) -> None:
        self.digital_signature = signature

    def set_release_notes(self, notes: str) -> None:
        self.release_notes = notes

    def is_ready_to_publish(self) -> bool:
        return self.status == PublishStatus.VALIDATED and bool(self.digital_signature)

    def mark_validating(self) -> None:
        self.status = PublishStatus.VALIDATING

    def mark_validated(self) -> None:
        self.status = PublishStatus.VALIDATED

    def mark_published(self) -> None:
        self.status = PublishStatus.PUBLISHED

    def mark_rejected(self, reason: str = "") -> None:
        self.status = PublishStatus.REJECTED
        if reason:
            self.validation_results["rejection_reason"] = reason

    def mark_rolled_back(self, reason: str = "") -> None:
        self.status = PublishStatus.ROLLED_BACK
        if reason:
            self.validation_results["rollback_reason"] = reason

    def get_validation_summary(self) -> dict:
        total_checks = 0
        passed_checks = 0
        failed_checks = 0
        for result_set in (
            self.validation_results,
            self.a11y_check_results,
            self.localization_results,
            self.dependency_results,
        ):
            if isinstance(result_set, dict):
                total_checks += result_set.get("total", 0)
                passed_checks += result_set.get("passed", 0)
                failed_checks += result_set.get("failed", 0)
        return {
            "total": total_checks,
            "passed": passed_checks,
            "failed": failed_checks,
            "pass_rate": round(passed_checks / total_checks * 100, 2) if total_checks > 0 else 0.0,
        }

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "content_id": self.content_id,
            "content_type": self.content_type,
            "version": self.version,
            "requested_by": self.requested_by,
            "requested_at": self.requested_at.isoformat(),
            "validation_results": self.validation_results,
            "a11y_check_results": self.a11y_check_results,
            "localization_results": self.localization_results,
            "dependency_results": self.dependency_results,
            "digital_signature": self.digital_signature,
            "release_notes": self.release_notes,
            "status": self.status.value,
        }


@dataclass
class PublishHistory:
    """Records an action taken on a content publish lifecycle."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str = ""
    version: int = 1
    action: str = ""
    performed_by: str = ""
    performed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    details: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "content_id": self.content_id,
            "version": self.version,
            "action": self.action,
            "performed_by": self.performed_by,
            "performed_at": self.performed_at.isoformat(),
            "details": self.details,
        }


@dataclass
class ContentVersion:
    """Tracks versioned snapshots of content with checksums."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str = ""
    version: int = 1
    changes: list[str] = field(default_factory=list)
    author: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    checksum: str = ""

    def add_change(self, change_description: str) -> None:
        self.changes.append(change_description)

    def set_checksum(self, checksum: str) -> None:
        self.checksum = checksum

    def get_change_count(self) -> int:
        return len(self.changes)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "content_id": self.content_id,
            "version": self.version,
            "changes": list(self.changes),
            "author": self.author,
            "created_at": self.created_at.isoformat(),
            "checksum": self.checksum,
            "change_count": self.get_change_count(),
        }
