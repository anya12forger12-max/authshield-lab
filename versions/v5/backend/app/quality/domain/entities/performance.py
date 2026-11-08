from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Benchmark:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    category: str = ""
    value: float = 0.0
    unit: str = ""
    threshold: float = 0.0
    passed: bool = False
    measured_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class PerformanceReport:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    benchmarks: list[Benchmark] = field(default_factory=list)
    overall_score: float = 0.0
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class BenchmarkHistory:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    benchmark_name: str = ""
    measurements: list[tuple[datetime, float]] = field(default_factory=list)
    trend: str = ""
    regression_detected: bool = False
