"""SQLAlchemy ORM models for the Developer Platform module."""

from __future__ import annotations

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base_model import Base, TimestampMixin, UUIDPrimaryKeyMixin


# ---------------------------------------------------------------------------
# SDK Models
# ---------------------------------------------------------------------------


class SdKModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """ORM model for SDK records."""

    __tablename__ = "developer_sdks"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str] = mapped_column(String(10), nullable=False, default="1.0")
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    author: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    compatibility_version: Mapped[str] = mapped_column(String(50), nullable=False, default="1.0")
    modules: Mapped[str] = mapped_column(Text, nullable=False, default="")
    deprecated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    min_platform_version: Mapped[str] = mapped_column(String(50), nullable=False, default="1.0")


class SdKModuleModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """ORM model for SDK module records."""

    __tablename__ = "developer_sdk_modules"

    sdk_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    api_classes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    version: Mapped[str] = mapped_column(String(50), nullable=False, default="1.0.0")


# ---------------------------------------------------------------------------
# Extension Models
# ---------------------------------------------------------------------------


class ExtensionModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """ORM model for Extension records."""

    __tablename__ = "developer_extensions"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False, default="1.0.0")
    author: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    extension_type: Mapped[str] = mapped_column(String(50), nullable=False, default="plugin")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="uninstalled")
    installed_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
    permissions: Mapped[str] = mapped_column(Text, nullable=False, default="")
    dependencies: Mapped[str] = mapped_column(Text, nullable=False, default="")
    compatibility: Mapped[str] = mapped_column(String(50), nullable=False, default=">=1.0")
    checksum: Mapped[str] = mapped_column(String(128), nullable=False, default="")


class InstalledExtensionModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """ORM model for InstalledExtension records."""

    __tablename__ = "developer_installed_extensions"

    extension_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(50), nullable=False, default="1.0.0")
    installed_by: Mapped[str] = mapped_column(String(36), nullable=False, default="")
    installed_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    config: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


# ---------------------------------------------------------------------------
# Automation Models
# ---------------------------------------------------------------------------


class AutomationWorkflowModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """ORM model for AutomationWorkflow records."""

    __tablename__ = "developer_automation_workflows"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    workflow_type: Mapped[str] = mapped_column(String(50), nullable=False, default="custom")
    steps: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    schedule: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_run: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
    next_run: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="idle")


class WorkflowRunModel(UUIDPrimaryKeyMixin, Base):
    """ORM model for WorkflowRun records."""

    __tablename__ = "developer_workflow_runs"

    workflow_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    started_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)
    ended_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    results: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    errors: Mapped[str] = mapped_column(Text, nullable=False, default="[]")


# ---------------------------------------------------------------------------
# API Explorer Models
# ---------------------------------------------------------------------------


class ApiEndpointModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """ORM model for ApiEndpoint records."""

    __tablename__ = "developer_api_endpoints"

    path: Mapped[str] = mapped_column(String(512), nullable=False)
    method: Mapped[str] = mapped_column(String(10), nullable=False, default="GET")
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    parameters: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    response_schema: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    category: Mapped[str] = mapped_column(String(100), nullable=False, default="general")
    version: Mapped[str] = mapped_column(String(20), nullable=False, default="1.0")
    deprecated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    auth_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


# ---------------------------------------------------------------------------
# Validation Models
# ---------------------------------------------------------------------------


class ValidationReportModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """ORM model for ValidationReport records."""

    __tablename__ = "developer_validation_reports"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    target_type: Mapped[str] = mapped_column(String(100), nullable=False)
    results: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    overall_status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    generated_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)


# ---------------------------------------------------------------------------
# Package Builder Models
# ---------------------------------------------------------------------------


class PackageManifestModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """ORM model for PackageManifest records."""

    __tablename__ = "developer_package_manifests"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False, default="1.0.0")
    author: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    package_type: Mapped[str] = mapped_column(String(50), nullable=False, default="extension")
    dependencies: Mapped[str] = mapped_column(Text, nullable=False, default="")
    license: Mapped[str] = mapped_column(String(100), nullable=False, default="MIT")
    compatibility: Mapped[str] = mapped_column(String(50), nullable=False, default=">=1.0")
    checksum: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    bundle_size: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class PackageBuildResultModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """ORM model for BuildResult records."""

    __tablename__ = "developer_package_build_results"

    config_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    output_path: Mapped[str] = mapped_column(String(1024), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    checksum: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    built_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_seconds: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
