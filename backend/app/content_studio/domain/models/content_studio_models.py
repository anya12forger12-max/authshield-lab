"""Content Production Studio SQLAlchemy ORM models."""

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


# ---------------------------------------------------------------------------
# Program & Course Design
# ---------------------------------------------------------------------------

class ProgramModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, Base):
    __tablename__ = "cs_programs"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    department: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    courses_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")


class CourseDesignModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, Base):
    __tablename__ = "cs_course_designs"

    program_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    learning_objectives_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    estimated_hours: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    competencies_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    prerequisites_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    a11y_notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    localization_status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    course_status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    created_by: Mapped[str] = mapped_column(String(36), nullable=False, default="")


class UnitDesignModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "cs_unit_designs"

    course_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class ModuleDesignModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "cs_module_designs"

    unit_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class LessonDesignModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "cs_lesson_designs"

    module_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    estimated_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    learning_objectives_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class ContentBlockModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "cs_content_blocks"

    lesson_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    block_type: Mapped[str] = mapped_column(String(30), nullable=False, default="text")
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    accessible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    localized: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class InteractiveActivityModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "cs_interactive_activities"

    lesson_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    activity_type: Mapped[str] = mapped_column(String(30), nullable=False, default="mcq")
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    content_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    scoring_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


# ---------------------------------------------------------------------------
# Virtual Labs
# ---------------------------------------------------------------------------

class VirtualLabModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, Base):
    __tablename__ = "cs_virtual_labs"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    lab_type: Mapped[str] = mapped_column(String(50), nullable=False, default="hands_on")
    learning_objectives_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    prerequisites_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    expected_outcomes_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    reflection_questions_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    assessment_criteria_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    a11y_instructions: Mapped[str] = mapped_column(Text, nullable=False, default="")
    estimated_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    lab_status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class LabStepModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "cs_lab_steps"

    lab_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    step_number: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    instructions: Mapped[str] = mapped_column(Text, nullable=False, default="")
    hints_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    expected_result: Mapped[str] = mapped_column(Text, nullable=False, default="")
    validation_rules_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class LabTemplateModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "cs_lab_templates"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    template_type: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    steps_template_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


# ---------------------------------------------------------------------------
# Multimedia Assets
# ---------------------------------------------------------------------------

class MultimediaAssetModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "cs_multimedia_assets"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    asset_type: Mapped[str] = mapped_column(String(30), nullable=False, default="image")
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    file_path: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    alt_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    caption: Mapped[str] = mapped_column(Text, nullable=False, default="")
    transcript: Mapped[str] = mapped_column(Text, nullable=False, default="")
    accessible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class AssetCollectionModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "cs_asset_collections"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    asset_ids_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")


class AssetValidationResultModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "cs_asset_validations"

    asset_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    valid: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    issues_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    checked_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

class ContentTemplateModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, Base):
    __tablename__ = "cs_content_templates"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    template_type: Mapped[str] = mapped_column(String(20), nullable=False, default="lesson")
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    structure_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    author: Mapped[str] = mapped_column(String(36), nullable=False, default="")
    inherit_from: Mapped[str | None] = mapped_column(String(36), nullable=True, default=None)


class TemplateVersionModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "cs_template_versions"

    template_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    changes_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")


class TemplateInstanceModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "cs_template_instances"

    template_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    customizations_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_by: Mapped[str] = mapped_column(String(36), nullable=False, default="")


# ---------------------------------------------------------------------------
# Publishing
# ---------------------------------------------------------------------------

class PublishRequestModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "cs_publish_requests"

    content_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    requested_by: Mapped[str] = mapped_column(String(36), nullable=False)
    requested_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)
    validation_results_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    a11y_check_results_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    localization_results_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    dependency_results_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    digital_signature: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    release_notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    publish_status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")


class PublishHistoryModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "cs_publish_history"

    content_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    performed_by: Mapped[str] = mapped_column(String(36), nullable=False)
    performed_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)
    details_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class ContentVersionModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "cs_content_versions"

    content_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    changes_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    author: Mapped[str] = mapped_column(String(36), nullable=False, default="")
    checksum: Mapped[str] = mapped_column(String(64), nullable=False, default="")


# ---------------------------------------------------------------------------
# Review
# ---------------------------------------------------------------------------

class EditorialReviewModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "cs_editorial_reviews"

    content_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    current_stage: Mapped[str] = mapped_column(String(30), nullable=False, default="draft")
    submitter: Mapped[str] = mapped_column(String(36), nullable=False)


class ReviewCommentModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "cs_review_comments"

    review_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    author: Mapped[str] = mapped_column(String(36), nullable=False)
    stage: Mapped[str] = mapped_column(String(30), nullable=False)
    comment: Mapped[str] = mapped_column(Text, nullable=False, default="")
    severity: Mapped[str | None] = mapped_column(String(20), nullable=True, default=None)


class ReviewDecisionModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "cs_review_decisions"

    review_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    stage: Mapped[str] = mapped_column(String(30), nullable=False)
    reviewer: Mapped[str] = mapped_column(String(36), nullable=False)
    decision: Mapped[str] = mapped_column(String(20), nullable=False)
    comments: Mapped[str] = mapped_column(Text, nullable=False, default="")
    decided_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)


# ---------------------------------------------------------------------------
# Accessibility
# ---------------------------------------------------------------------------

class A11yCheckModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "cs_a11y_checks"

    report_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    check_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    element: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    evidence: Mapped[str] = mapped_column(Text, nullable=False, default="")
    remediation: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="error")


class A11yValidationReportModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "cs_a11y_validation_reports"

    content_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    passed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    na: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    compliance_pct: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    generated_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)


class A11yRemediationModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "cs_a11y_remediations"

    report_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    check_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    action: Mapped[str] = mapped_column(Text, nullable=False, default="")
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="high")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="open")
    assignee: Mapped[str] = mapped_column(String(36), nullable=False, default="")
