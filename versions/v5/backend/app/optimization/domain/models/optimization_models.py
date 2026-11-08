"""Optimization SQLAlchemy ORM models."""

from __future__ import annotations

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ....shared.base_model import (
    AuditMixin,
    Base,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class PerformanceMetricModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "optimization_performance_metrics"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    value: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    unit: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    threshold: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class BenchmarkResultModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "optimization_benchmark_results"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    value: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    unit: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    threshold: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    baseline_value: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    regression_pct: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)


class OptimizationDashboardModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "optimization_dashboards"

    startup_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    memory_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    storage_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    search_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    rendering_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    module_load_times_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    plugin_performance_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    overall_health: Mapped[str] = mapped_column(String(20), nullable=False, default="unknown")


class FeatureFlagModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "optimization_feature_flags"

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    default_value: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    rollout_date: Mapped[str] = mapped_column(String(30), nullable=False, default="")
    removal_date: Mapped[str] = mapped_column(String(30), nullable=False, default="")


class ConfigProfileModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "optimization_config_profiles"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    target_audience: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    settings_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    version: Mapped[str] = mapped_column(String(20), nullable=False, default="1.0")


class CompatibilityReportModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "optimization_compatibility_reports"

    results_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    platforms_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    overall_status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")


class SustainabilityMetricModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "optimization_sustainability_metrics"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    max_score: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)
    trend: Mapped[str] = mapped_column(String(20), nullable=False, default="stable")


class TechnicalDebtItemModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "optimization_technical_debt"

    category: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="low")
    estimated_hours: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    resolved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    resolved_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)


class ReleaseWorkflowModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "optimization_release_workflows"

    release_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    current_stage: Mapped[str] = mapped_column(String(50), nullable=False, default="planning")
    stage_history_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    created_by: Mapped[str] = mapped_column(String(36), nullable=False, default="")
    completed_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)


class ReleaseApprovalModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "optimization_release_approvals"

    workflow_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    stage: Mapped[str] = mapped_column(String(50), nullable=False)
    approver: Mapped[str] = mapped_column(String(36), nullable=False, default="")
    approved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    comments: Mapped[str] = mapped_column(Text, nullable=False, default="")
    approved_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)


class ReleaseGateModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "optimization_release_gates"

    release_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    gate_type: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    evidence: Mapped[str] = mapped_column(Text, nullable=False, default="")
    checked_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)


class ReleaseChecklistItemModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "optimization_release_checklist"

    release_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    item: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    category: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    assignee: Mapped[str] = mapped_column(String(36), nullable=False, default="")
    due_date: Mapped[str] = mapped_column(String(30), nullable=False, default="")
    completed_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)


class AIGenerationAuditModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "optimization_ai_generation_audits"

    content_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    ai_type: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    input_hash: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    output_hash: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    model_version: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    instructor_reviewed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    reviewed_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)


class DiagnosticTraceModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "optimization_diagnostic_traces"

    name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    spans_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    total_duration_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
