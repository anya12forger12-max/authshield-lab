from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal

ReleaseStatus = Literal["in_development", "rc", "stable", "deprecated"]


@dataclass
class Release:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    version: str = ""
    code_name: str = ""
    status: ReleaseStatus = "in_development"
    release_date: str = ""
    features: list[str] = field(default_factory=list)
    bug_fixes: list[str] = field(default_factory=list)
    known_issues: list[str] = field(default_factory=list)
    compatibility: str = ""


@dataclass
class ReleaseReadiness:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    release_id: str = ""
    functional_completeness: bool = False
    a11y_compliance: bool = False
    doc_coverage: bool = False
    localization_completeness: bool = False
    performance_targets: bool = False
    security_checks: bool = False
    backup_verification: bool = False
    extension_compatibility: bool = False
    sdk_stability: bool = False
    overall_ready: bool = False
    checked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ReleaseNote:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    release_id: str = ""
    section: str = ""
    content: str = ""
