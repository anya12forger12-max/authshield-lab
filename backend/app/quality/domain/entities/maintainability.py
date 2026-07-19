from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class MaintainabilityIndex:
    score: float = 0.0
    grade: str = ""


@dataclass
class TechnicalDebtItem:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    category: str = ""
    description: str = ""
    severity: str = ""
    estimated_hours: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ComplexityMetric:
    file_path: str = ""
    cyclomatic_complexity: int = 0
    cognitive_complexity: int = 0
    class_count: int = 0
    function_count: int = 0


@dataclass
class DependencyInfo:
    name: str = ""
    version: str = ""
    latest_version: str = ""
    update_available: bool = False
    vulnerabilities: int = 0
    license: str = ""


@dataclass
class BuildHealth:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: str = ""
    tests_passed: int = 0
    tests_failed: int = 0
    duration_seconds: float = 0.0
    built_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
