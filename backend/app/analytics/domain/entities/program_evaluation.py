"""Program evaluation domain entities."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class ProgramEvaluation:
    """Comprehensive program evaluation result."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    program_name: str = ""
    period: str = ""
    effectiveness_score: float = 0.0
    competency_coverage: float = 0.0
    course_performance: dict[str, float] = field(default_factory=dict)
    resource_utilization: float = 0.0
    instructor_workload: dict[str, float] = field(default_factory=dict)
    certification_outcomes: dict[str, float] = field(default_factory=dict)
    a11y_readiness: float = 0.0
    governance_compliance: float = 0.0
    doc_health: float = 0.0
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ExecutiveSummary:
    """High-level executive summary for program stakeholders."""

    overall_health: float = 0.0
    key_findings: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    priorities: list[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
