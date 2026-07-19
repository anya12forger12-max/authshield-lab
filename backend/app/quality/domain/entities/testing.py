from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Literal


class TestType(str, Enum):
    unit = "unit"
    integration = "integration"
    e2e = "e2e"
    ui = "ui"
    a11y = "a11y"
    localization = "localization"
    performance = "performance"
    regression = "regression"
    backup_restore = "backup_restore"
    plugin_compat = "plugin_compat"
    package_validation = "package_validation"


TestStatus = Literal["not_run", "passed", "failed", "skipped"]


@dataclass
class TestCase:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    test_type: TestType = TestType.unit
    module: str = ""
    steps: list[str] = field(default_factory=list)
    expected_result: str = ""
    status: TestStatus = "not_run"
    execution_time_ms: float = 0.0
    last_run_at: datetime | None = None
    assertions: int = 0


@dataclass
class TestSuite:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    test_cases: list[TestCase] = field(default_factory=list)
    total: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    coverage: float = 0.0
    run_at: datetime | None = None


@dataclass
class CoverageReport:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    total_statements: int = 0
    covered_statements: int = 0
    percentage: float = 0.0
    by_module: dict[str, float] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
