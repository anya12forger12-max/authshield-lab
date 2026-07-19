from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal

A11yAuditStatus = Literal["pass", "fail", "na"]


@dataclass
class A11yProfile:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    features: dict[str, bool] = field(default_factory=dict)


@dataclass
class A11yFeature:
    name: str = ""
    description: str = ""
    enabled: bool = False
    config: dict = field(default_factory=dict)


@dataclass
class A11yAuditResult:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    standard: str = ""
    element: str = ""
    requirement: str = ""
    status: A11yAuditStatus = "na"
    severity: str = ""
    evidence: str = ""


@dataclass
class A11yAudit:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    results: list[A11yAuditResult] = field(default_factory=list)
    overall_score: float = 0.0
    violations_count: int = 0
    passed_count: int = 0
    na_count: int = 0
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class A11yScorecard:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    category: str = ""
    score: float = 0.0
    max_score: float = 100.0
    issues: list[str] = field(default_factory=list)


@dataclass
class KeyboardShortcut:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    action: str = ""
    shortcut: str = ""
    description: str = ""
    scope: str = ""
