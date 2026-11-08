"""Multimedia asset domain entities for the Content Production Studio."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class AssetType(str, Enum):
    IMAGE = "image"
    SVG = "svg"
    AUDIO = "audio"
    CAPTION = "caption"
    TRANSCRIPT = "transcript"
    PDF = "pdf"
    SAMPLE_DOC = "sample_doc"
    SYNTHETIC_LOG = "synthetic_log"
    CONFIG_FILE = "config_file"
    ICON = "icon"


@dataclass
class MultimediaAsset:
    """A multimedia asset used in content (images, audio, documents, etc.)."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    asset_type: AssetType = AssetType.IMAGE
    description: str = ""
    file_path: str = ""
    alt_text: str = ""
    caption: str = ""
    transcript: str = ""
    accessible: bool = True
    metadata: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    version: int = 1

    def update_alt_text(self, alt_text: str) -> None:
        self.alt_text = alt_text
        self.accessible = bool(alt_text.strip()) if alt_text else False

    def update_caption(self, caption: str) -> None:
        self.caption = caption

    def update_transcript(self, transcript: str) -> None:
        self.transcript = transcript

    def mark_accessible(self) -> None:
        self.accessible = True

    def mark_inaccessible(self, reason: str = "") -> None:
        self.accessible = False
        if reason:
            self.metadata["inaccessibility_reason"] = reason

    def increment_version(self) -> None:
        self.version += 1

    def update_metadata(self, metadata: dict) -> None:
        self.metadata.update(metadata)

    def has_transcript(self) -> bool:
        return bool(self.transcript.strip())

    def has_alt_text(self) -> bool:
        return bool(self.alt_text.strip())

    def is_media_type(self) -> bool:
        return self.asset_type in {AssetType.AUDIO, AssetType.IMAGE, AssetType.SVG}

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "asset_type": self.asset_type.value,
            "description": self.description,
            "file_path": self.file_path,
            "alt_text": self.alt_text,
            "caption": self.caption,
            "transcript": self.transcript,
            "accessible": self.accessible,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "version": self.version,
        }


@dataclass
class AssetCollection:
    """A named collection grouping related multimedia assets."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    asset_ids: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def add_asset(self, asset_id: str) -> None:
        if asset_id not in self.asset_ids:
            self.asset_ids.append(asset_id)

    def remove_asset(self, asset_id: str) -> bool:
        if asset_id in self.asset_ids:
            self.asset_ids.remove(asset_id)
            return True
        return False

    def contains_asset(self, asset_id: str) -> bool:
        return asset_id in self.asset_ids

    def get_asset_count(self) -> int:
        return len(self.asset_ids)

    def clear(self) -> None:
        self.asset_ids.clear()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "asset_ids": list(self.asset_ids),
            "created_at": self.created_at.isoformat(),
            "asset_count": self.get_asset_count(),
        }


@dataclass
class AssetValidationResult:
    """Result of validating a multimedia asset for accessibility and integrity."""

    asset_id: str = ""
    valid: bool = True
    issues: list[str] = field(default_factory=list)
    checked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def add_issue(self, issue: str) -> None:
        self.issues.append(issue)
        self.valid = False

    def get_issue_count(self) -> int:
        return len(self.issues)

    def has_critical_issues(self) -> bool:
        return any("missing" in i.lower() or "invalid" in i.lower() for i in self.issues)

    def to_dict(self) -> dict:
        return {
            "asset_id": self.asset_id,
            "valid": self.valid,
            "issues": list(self.issues),
            "checked_at": self.checked_at.isoformat(),
            "issue_count": self.get_issue_count(),
        }
