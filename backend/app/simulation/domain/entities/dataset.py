"""Dataset domain entities for synthetic data management."""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class DatasetArtifactType(str, Enum):
    """Types of artifacts that can exist within a synthetic dataset."""

    AUTH_LOG = "auth_log"
    AUDIT_LOG = "audit_log"
    SESSION_RECORD = "session_record"
    USER_PROFILE = "user_profile"
    ROLE_ASSIGNMENT = "role_assignment"
    CONFIG_SNAPSHOT = "config_snapshot"
    SECURITY_POLICY = "security_policy"
    COMPLIANCE_REPORT = "compliance_report"
    INCIDENT_REPORT = "incident_report"
    BACKUP_REPORT = "backup_report"
    ACCESSIBILITY_REPORT = "accessibility_report"


@dataclass
class DatasetArtifact:
    """A single artifact within a synthetic dataset."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    artifact_type: DatasetArtifactType = DatasetArtifactType.AUTH_LOG
    name: str = ""
    content: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "artifact_type": self.artifact_type.value,
            "name": self.name,
            "content": self.content,
            "metadata": self.metadata,
        }


@dataclass
class DatasetMetadata:
    """Metadata about how and when a dataset was generated."""

    creator: str = "system"
    generation_date: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    total_records: int = 0
    checksum: str = ""

    def compute_checksum(self, data: Any) -> str:
        """Compute SHA-256 checksum of provided data."""
        serialized = json.dumps(data, sort_keys=True, default=str)
        self.checksum = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        return self.checksum

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "creator": self.creator,
            "generation_date": self.generation_date,
            "total_records": self.total_records,
            "checksum": self.checksum,
        }


@dataclass
class SyntheticDataset:
    """A complete synthetic dataset containing multiple artifacts.

    Generated deterministically from a seed value to ensure
    reproducibility across runs.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    seed: int = 42
    artifacts: list[DatasetArtifact] = field(default_factory=list)
    metadata: DatasetMetadata = field(default_factory=DatasetMetadata)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    version: int = 1

    def get_artifact_count(self) -> int:
        """Return total number of artifacts in this dataset."""
        return len(self.artifacts)

    def get_records_by_type(self, artifact_type: DatasetArtifactType) -> list[DatasetArtifact]:
        """Return all artifacts matching the given type."""
        return [a for a in self.artifacts if a.artifact_type == artifact_type]

    def add_artifact(self, artifact: DatasetArtifact) -> None:
        """Add an artifact to the dataset."""
        self.artifacts.append(artifact)
        self.metadata.total_records = sum(
            len(a.content.get("records", [])) for a in self.artifacts
        )

    def update_metadata_checksum(self) -> str:
        """Recompute the metadata checksum over all artifact contents."""
        all_content = [a.content for a in self.artifacts]
        return self.metadata.compute_checksum(all_content)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "seed": self.seed,
            "artifacts": [a.to_dict() for a in self.artifacts],
            "metadata": self.metadata.to_dict(),
            "created_at": self.created_at.isoformat(),
            "version": self.version,
        }
