from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal

DiagStatus = Literal["pass", "fail", "warning", "skipped"]


@dataclass
class DiagnosticCheck:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    category: str = ""
    description: str = ""
    status: DiagStatus = "skipped"
    details: str = ""
    checked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class DiagnosticBundle:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    checks: list[DiagnosticCheck] = field(default_factory=list)
    overall_status: str = ""
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    platform: str = ""
    version: str = ""
    includes_sensitive: bool = False


@dataclass
class DiagnosticCategory:
    name: str = ""
    description: str = ""
    checks_count: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
