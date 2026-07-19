"""Release center domain entities."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class ReleaseStatus(str, Enum):
    """Lifecycle status of a software release."""

    IN_DEVELOPMENT = "in_development"
    RELEASE_CANDIDATE = "release_candidate"
    STABLE = "stable"
    DEPRECATED = "deprecated"
    END_OF_LIFE = "end_of_life"


@dataclass
class BuildInfo:
    """Metadata about a specific build artifact."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    version: str = ""
    build_number: str = ""
    built_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    build_environment: str = ""
    python_version: str = ""
    platform: str = ""
    checksum: str = ""


@dataclass
class Release:
    """A versioned software release with changelog information."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    version: str = ""
    name: str = ""
    status: ReleaseStatus = ReleaseStatus.IN_DEVELOPMENT
    build_info: BuildInfo = field(default_factory=BuildInfo)
    release_date: datetime | None = None
    release_notes: list[str] = field(default_factory=list)
    features: list[str] = field(default_factory=list)
    bug_fixes: list[str] = field(default_factory=list)
    known_issues: list[str] = field(default_factory=list)
    deprecations: list[str] = field(default_factory=list)
    minimum_platform_version: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ReleasePackage:
    """A distributable package associated with a release."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    release_id: str = ""
    name: str = ""
    package_type: str = "installer"
    platform: str = ""
    checksum: str = ""
    file_size: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
