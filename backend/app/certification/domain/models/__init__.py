"""SQLAlchemy ORM models for the Certification / Operations module."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base_model import Base, TimestampMixin, UUIDPrimaryKeyMixin


# ── Operations ──────────────────────────────────────────────────────


class ServiceStatusModel(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "cert_service_status"

    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), default="healthy")
    last_check: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    response_time_ms: Mapped[float] = mapped_column(Float, default=0.0)
    error_rate: Mapped[float] = mapped_column(Float, default=0.0)


class PlatformHealthModel(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "cert_platform_health"

    overall_status: Mapped[str] = mapped_column(String(20), default="healthy")
    uptime_hours: Mapped[float] = mapped_column(Float, default=0.0)
    services_json: Mapped[str] = mapped_column(Text, default="[]")
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class ModuleInventoryModel(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "cert_module_inventory"

    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(50), default="0.1.0")
    status: Mapped[str] = mapped_column(String(50), default="active")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    dependencies_json: Mapped[str] = mapped_column(Text, default="[]")
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class PackageHealthModel(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "cert_package_health"

    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(50), default="")
    integrity: Mapped[bool] = mapped_column(Boolean, default=True)
    compatibility: Mapped[bool] = mapped_column(Boolean, default=True)
    health_score: Mapped[float] = mapped_column(Float, default=100.0)
    last_validated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class EcosystemDashboardModel(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "cert_ecosystem_dashboard"

    platform_health_json: Mapped[str] = mapped_column(Text, default="{}")
    module_inventory_json: Mapped[str] = mapped_column(Text, default="[]")
    extension_status_json: Mapped[str] = mapped_column(Text, default="[]")
    package_health_json: Mapped[str] = mapped_column(Text, default="[]")
    doc_status: Mapped[float] = mapped_column(Float, default=0.0)
    a11y_score: Mapped[float] = mapped_column(Float, default=0.0)
    security_score: Mapped[float] = mapped_column(Float, default=0.0)
    performance_score: Mapped[float] = mapped_column(Float, default=0.0)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


# ── Certification Center ────────────────────────────────────────────


class PlatformCertificationModel(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "cert_platform_certification"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    cert_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    certified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    validation_results_json: Mapped[str] = mapped_column(Text, default="{}")
    evidence_json: Mapped[str] = mapped_column(Text, default="[]")
    metrics_json: Mapped[str] = mapped_column(Text, default="{}")
    findings_json: Mapped[str] = mapped_column(Text, default="[]")
    corrective_actions_json: Mapped[str] = mapped_column(Text, default="[]")
    approved_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class CertificationRequirementModel(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "cert_certification_requirement"

    certification_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    requirement: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    met: Mapped[bool] = mapped_column(Boolean, default=False)
    evidence: Mapped[str] = mapped_column(Text, default="")


class PlatformCertificationReportModel(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "cert_certification_report"

    title: Mapped[str] = mapped_column(String(300), nullable=False)
    certifications_json: Mapped[str] = mapped_column(Text, default="[]")
    overall_status: Mapped[str] = mapped_column(String(20), default="pending")
    score: Mapped[float] = mapped_column(Float, default=0.0)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


# ── Sustainability ──────────────────────────────────────────────────


class DependencyLifecycleModel(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "cert_dependency_lifecycle"

    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(50), default="")
    end_of_life_date: Mapped[str | None] = mapped_column(String(30), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="supported")
    update_available: Mapped[bool] = mapped_column(Boolean, default=False)
    latest_version: Mapped[str] = mapped_column(String(50), default="")


class APIStabilityModel(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "cert_api_stability"

    version: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    endpoints: Mapped[int] = mapped_column(Integer, default=0)
    deprecated: Mapped[int] = mapped_column(Integer, default=0)
    breaking_changes: Mapped[int] = mapped_column(Integer, default=0)
    stability_score: Mapped[float] = mapped_column(Float, default=100.0)


class ModuleOwnershipModel(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "cert_module_ownership"

    module: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    owner: Mapped[str] = mapped_column(String(200), nullable=False)
    last_reviewed: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    health: Mapped[float] = mapped_column(Float, default=100.0)


class DocumentationFreshnessModel(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "cert_documentation_freshness"

    component: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    days_stale: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="fresh")


class SustainabilityDashboardModel(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "cert_sustainability_dashboard"

    dependencies_json: Mapped[str] = mapped_column(Text, default="[]")
    api_stability_json: Mapped[str] = mapped_column(Text, default="{}")
    ownership_json: Mapped[str] = mapped_column(Text, default="[]")
    documentation_json: Mapped[str] = mapped_column(Text, default="[]")
    technical_debt_hours: Mapped[float] = mapped_column(Float, default=0.0)
    maintenance_score: Mapped[float] = mapped_column(Float, default=0.0)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class MaintenanceRoadmapModel(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "cert_maintenance_roadmap"

    title: Mapped[str] = mapped_column(String(300), nullable=False)
    items_json: Mapped[str] = mapped_column(Text, default="[]")
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    estimated_hours: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


# ── Release Engineering ─────────────────────────────────────────────


class ReleasePlanModel(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "cert_release_plan"

    version: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    code_name: Mapped[str] = mapped_column(String(100), default="")
    status: Mapped[str] = mapped_column(String(20), default="planning")
    end_date: Mapped[str] = mapped_column(String(30), default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class ReleaseValidationModel(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "cert_release_validation"

    release_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    validation_type: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    details: Mapped[str] = mapped_column(Text, default="")
    validated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class PackagingResultModel(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "cert_packaging_result"

    release_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    platform: Mapped[str] = mapped_column(String(100), nullable=False)
    package_type: Mapped[str] = mapped_column(String(50), default="")
    output_path: Mapped[str] = mapped_column(String(500), default="")
    checksum: Mapped[str] = mapped_column(String(128), default="")
    built_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class RegressionResultModel(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "cert_regression_result"

    release_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    tests_run: Mapped[int] = mapped_column(Integer, default=0)
    passed: Mapped[int] = mapped_column(Integer, default=0)
    failed: Mapped[int] = mapped_column(Integer, default=0)
    skipped: Mapped[int] = mapped_column(Integer, default=0)
    coverage: Mapped[float] = mapped_column(Float, default=0.0)
    run_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class ReleaseHistoryEntryModel(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "cert_release_history_entry"

    version: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    release_date: Mapped[str] = mapped_column(String(30), default="")
    summary: Mapped[str] = mapped_column(Text, default="")
    highlights_json: Mapped[str] = mapped_column(Text, default="[]")
    known_issues_json: Mapped[str] = mapped_column(Text, default="[]")
    status: Mapped[str] = mapped_column(String(20), default="published")


# ── Disaster Recovery ───────────────────────────────────────────────


class BackupValidationModel(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "cert_backup_validation"

    backup_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    backup_type: Mapped[str] = mapped_column(String(50), default="")
    size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    integrity: Mapped[bool] = mapped_column(Boolean, default=True)
    restorable: Mapped[bool] = mapped_column(Boolean, default=True)
    validated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class RestoreTestModel(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "cert_restore_test"

    test_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    backup_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    data_integrity: Mapped[bool] = mapped_column(Boolean, default=True)
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class ArchiveRecoveryModel(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "cert_archive_recovery"

    archive_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    items_recovered: Mapped[int] = mapped_column(Integer, default=0)
    completeness: Mapped[float] = mapped_column(Float, default=0.0)
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class RecoveryReadinessReportModel(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "cert_recovery_readiness_report"

    backup_health: Mapped[float] = mapped_column(Float, default=0.0)
    restore_success_rate: Mapped[float] = mapped_column(Float, default=0.0)
    archive_recovery: Mapped[float] = mapped_column(Float, default=0.0)
    config_recovery: Mapped[float] = mapped_column(Float, default=0.0)
    doc_recovery: Mapped[float] = mapped_column(Float, default=0.0)
    overall_readiness: Mapped[float] = mapped_column(Float, default=0.0)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


# ── Platform Validation ─────────────────────────────────────────────


class ValidationCheckModel(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "cert_validation_check"

    subsystem: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    check_name: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    details: Mapped[str] = mapped_column(Text, default="")
    evidence: Mapped[str] = mapped_column(Text, default="")
    checked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class SubsystemValidationModel(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "cert_subsystem_validation"

    subsystem: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    checks_json: Mapped[str] = mapped_column(Text, default="[]")
    passed: Mapped[int] = mapped_column(Integer, default=0)
    failed: Mapped[int] = mapped_column(Integer, default=0)
    skipped: Mapped[int] = mapped_column(Integer, default=0)
    compliance_pct: Mapped[float] = mapped_column(Float, default=0.0)
    validated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class PlatformValidationReportModel(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "cert_platform_validation_report"

    name: Mapped[str] = mapped_column(String(300), nullable=False)
    subsystems_json: Mapped[str] = mapped_column(Text, default="[]")
    overall_passed: Mapped[int] = mapped_column(Integer, default=0)
    overall_failed: Mapped[int] = mapped_column(Integer, default=0)
    overall_compliance: Mapped[float] = mapped_column(Float, default=0.0)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class FinalAcceptanceTestModel(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "cert_final_acceptance_test"

    version: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    results_json: Mapped[str] = mapped_column(Text, default="{}")
    overall_status: Mapped[str] = mapped_column(String(20), default="pending")
    sign_off_required_json: Mapped[str] = mapped_column(Text, default="[]")
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
