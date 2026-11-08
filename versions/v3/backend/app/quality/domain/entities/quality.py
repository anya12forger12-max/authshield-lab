from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal


@dataclass
class QualityScore:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    category: str = ""
    score: float = 0.0
    max_score: float = 100.0
    grade: str = ""
    meets_threshold: bool = False
    checked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class QualityDashboard:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    overall_score: float = 0.0
    test_coverage: float = 0.0
    code_quality: float = 0.0
    a11y_compliance: float = 0.0
    doc_coverage: float = 0.0
    performance_score: float = 0.0
    security_score: float = 0.0
    localization_coverage: float = 0.0
    release_readiness: bool = False
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ModuleHealth:
    module_name: str = ""
    status: Literal["healthy", "degraded", "unhealthy"] = "healthy"
    last_check: str = ""
    response_time_ms: float = 0.0
    error_rate: float = 0.0
