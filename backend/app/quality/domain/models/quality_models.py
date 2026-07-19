from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base_model import Base, TimestampMixin, UUIDPrimaryKeyMixin


class QualityScoreModel(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "quality_scores"

    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    score: Mapped[float] = mapped_column(Float, default=0.0)
    max_score: Mapped[float] = mapped_column(Float, default=100.0)
    grade: Mapped[str] = mapped_column(String(10), default="")
    meets_threshold: Mapped[bool] = mapped_column(Boolean, default=False)
    checked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )


class TestCaseModel(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "test_cases"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    test_type: Mapped[str] = mapped_column(String(50), nullable=False)
    module: Mapped[str] = mapped_column(String(100), default="")
    steps: Mapped[str] = mapped_column(Text, default="[]")
    expected_result: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(20), default="not_run")
    execution_time_ms: Mapped[float] = mapped_column(Float, default=0.0)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    assertions: Mapped[int] = mapped_column(Integer, default=0)


class TestSuiteModel(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "test_suites"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    total: Mapped[int] = mapped_column(Integer, default=0)
    passed: Mapped[int] = mapped_column(Integer, default=0)
    failed: Mapped[int] = mapped_column(Integer, default=0)
    skipped: Mapped[int] = mapped_column(Integer, default=0)
    coverage: Mapped[float] = mapped_column(Float, default=0.0)
    run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class CoverageReportModel(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "coverage_reports"

    total_statements: Mapped[int] = mapped_column(Integer, default=0)
    covered_statements: Mapped[int] = mapped_column(Integer, default=0)
    percentage: Mapped[float] = mapped_column(Float, default=0.0)
    by_module: Mapped[str] = mapped_column(Text, default="{}")
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )


class ApplicationMetricModel(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "application_metrics"

    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    value: Mapped[float] = mapped_column(Float, default=0.0)
    unit: Mapped[str] = mapped_column(String(50), default="")
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    tags: Mapped[str] = mapped_column(Text, default="{}")


class AuditResultModel(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "audit_results"

    audit_name: Mapped[str] = mapped_column(String(200), nullable=False)
    standard: Mapped[str] = mapped_column(String(50), default="")
    element: Mapped[str] = mapped_column(String(200), default="")
    requirement: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(10), default="na")
    severity: Mapped[str] = mapped_column(String(50), default="")
    evidence: Mapped[str] = mapped_column(Text, default="")
    overall_score: Mapped[float] = mapped_column(Float, default=0.0)
    violations_count: Mapped[int] = mapped_column(Integer, default=0)
    passed_count: Mapped[int] = mapped_column(Integer, default=0)
    na_count: Mapped[int] = mapped_column(Integer, default=0)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )


class DiagnosticCheckModel(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "diagnostic_checks"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(100), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(20), default="skipped")
    details: Mapped[str] = mapped_column(Text, default="")
    checked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )


class BenchmarkModel(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "benchmarks"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(100), default="")
    value: Mapped[float] = mapped_column(Float, default=0.0)
    unit: Mapped[str] = mapped_column(String(50), default="")
    threshold: Mapped[float] = mapped_column(Float, default=0.0)
    passed: Mapped[bool] = mapped_column(Boolean, default=False)
    measured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )


class ReleaseModel(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "releases"

    version: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    code_name: Mapped[str] = mapped_column(String(100), default="")
    status: Mapped[str] = mapped_column(String(20), default="in_development")
    release_date: Mapped[str] = mapped_column(String(20), default="")
    features: Mapped[str] = mapped_column(Text, default="[]")
    bug_fixes: Mapped[str] = mapped_column(Text, default="[]")
    known_issues: Mapped[str] = mapped_column(Text, default="[]")
    compatibility: Mapped[str] = mapped_column(Text, default="")


class ReleaseReadinessModel(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "release_readiness"

    release_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    functional_completeness: Mapped[bool] = mapped_column(Boolean, default=False)
    a11y_compliance: Mapped[bool] = mapped_column(Boolean, default=False)
    doc_coverage: Mapped[bool] = mapped_column(Boolean, default=False)
    localization_completeness: Mapped[bool] = mapped_column(Boolean, default=False)
    performance_targets: Mapped[bool] = mapped_column(Boolean, default=False)
    security_checks: Mapped[bool] = mapped_column(Boolean, default=False)
    backup_verification: Mapped[bool] = mapped_column(Boolean, default=False)
    extension_compatibility: Mapped[bool] = mapped_column(Boolean, default=False)
    sdk_stability: Mapped[bool] = mapped_column(Boolean, default=False)
    overall_ready: Mapped[bool] = mapped_column(Boolean, default=False)
    checked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
