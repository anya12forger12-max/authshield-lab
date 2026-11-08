from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class QualityCheckCompleted:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    category: str = ""
    score: float = 0.0
    passed: bool = False
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class TestSuiteRun:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    suite_name: str = ""
    total: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    duration_ms: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class AuditCompleted:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    audit_name: str = ""
    standard: str = ""
    overall_score: float = 0.0
    violations: int = 0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class PerformanceBenchmarkCompleted:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    benchmark_name: str = ""
    value: float = 0.0
    threshold: float = 0.0
    passed: bool = False
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ReleaseReadinessChecked:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    release_id: str = ""
    version: str = ""
    overall_ready: bool = False
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class DiagnosticsCompleted:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    bundle_name: str = ""
    overall_status: str = ""
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
