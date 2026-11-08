"""SQLAlchemy ORM models for the Standards module."""

from __future__ import annotations

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base_model import Base, TimestampMixin, UUIDPrimaryKeyMixin


# ---------------------------------------------------------------------------
# Framework Models
# ---------------------------------------------------------------------------


class FrameworkModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """ORM model for CompetencyFramework records."""

    __tablename__ = "standards_frameworks"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False, default="1.0")
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    categories_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    domains_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    competencies_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    learning_objectives_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    skills_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    knowledge_areas_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    references_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    revision_history_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")


class FrameworkCompetencyModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """ORM model for FrameworkCompetency records."""

    __tablename__ = "standards_framework_competencies"

    framework_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    domain_id: Mapped[str] = mapped_column(String(36), nullable=False, default="")
    level: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    skills_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")


class FrameworkDomainModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """ORM model for FrameworkDomain records."""

    __tablename__ = "standards_framework_domains"

    framework_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    category_ids_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")


class FrameworkCategoryModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """ORM model for FrameworkCategory records."""

    __tablename__ = "standards_framework_categories"

    framework_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    competency_ids_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")


class LearningObjectiveModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """ORM model for LearningObjective records."""

    __tablename__ = "standards_learning_objectives"

    framework_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    competency_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    level: Mapped[str] = mapped_column(String(50), nullable=False, default="")


class SkillModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """ORM model for Skill records."""

    __tablename__ = "standards_skills"

    framework_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    parent_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    aliases_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    category: Mapped[str] = mapped_column(String(100), nullable=False, default="")


class KnowledgeAreaModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """ORM model for KnowledgeArea records."""

    __tablename__ = "standards_knowledge_areas"

    framework_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    skill_ids_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")


class FrameworkReferenceModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """ORM model for FrameworkReference records."""

    __tablename__ = "standards_framework_references"

    framework_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[str] = mapped_column(String(1024), nullable=False, default="")
    reference_type: Mapped[str] = mapped_column(String(100), nullable=False, default="")


# ---------------------------------------------------------------------------
# Mapping Models
# ---------------------------------------------------------------------------


class CurriculumMappingModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """ORM model for CurriculumMapping records."""

    __tablename__ = "standards_curriculum_mappings"

    source_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(100), nullable=False)
    target_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(100), nullable=False)
    coverage_level: Mapped[str] = mapped_column(String(50), nullable=False, default="partial")
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    review_status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    evidence_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    instructor_notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    related_competencies_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")


class CoverageReportModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """ORM model for CoverageReport records."""

    __tablename__ = "standards_coverage_reports"

    framework_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    total_items: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    mapped_items: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    coverage_pct: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    gaps_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    generated_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)


# ---------------------------------------------------------------------------
# Skills Taxonomy Models
# ---------------------------------------------------------------------------


class SkillTaxonomyModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """ORM model for SkillTaxonomy records."""

    __tablename__ = "standards_skill_taxonomies"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    version: Mapped[str] = mapped_column(String(50), nullable=False, default="1.0")
    skills_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    relationships_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")


class TaxonomySkillModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """ORM model for TaxonomySkill records."""

    __tablename__ = "standards_taxonomy_skills"

    taxonomy_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    category: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    parent_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    aliases_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    level: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class SkillCategoryModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """ORM model for SkillCategory records."""

    __tablename__ = "standards_skill_categories"

    taxonomy_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    parent_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    skill_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class SkillRelationshipModel(UUIDPrimaryKeyMixin, Base):
    """ORM model for SkillRelationship records."""

    __tablename__ = "standards_skill_relationships"

    source_skill_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    target_skill_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    relationship_type: Mapped[str] = mapped_column(String(100), nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)


class TaxonomyVersionModel(UUIDPrimaryKeyMixin, Base):
    """ORM model for TaxonomyVersion records."""

    __tablename__ = "standards_taxonomy_versions"

    taxonomy_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    changes_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)


# ---------------------------------------------------------------------------
# Evidence Models
# ---------------------------------------------------------------------------


class EvidenceCollectionModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """ORM model for EvidenceCollection records."""

    __tablename__ = "standards_evidence_collections"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    framework_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    collected: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    pending: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class EvidenceItemModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """ORM model for EvidenceItem records."""

    __tablename__ = "standards_evidence_items"

    collection_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    evidence_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    source_id: Mapped[str] = mapped_column(String(36), nullable=False, default="")
    source_type: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    date_collected: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    reviewed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


# ---------------------------------------------------------------------------
# Quality Models
# ---------------------------------------------------------------------------


class AcademicQualityDashboardModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """ORM model for AcademicQualityDashboard records."""

    __tablename__ = "standards_quality_dashboards"

    curriculum_balance: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    competency_distribution_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    skills_progression_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    assessment_distribution_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    a11y_health: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    doc_quality: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    localization_readiness: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    content_freshness: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    review_completion: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    generated_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)


class ReadinessReviewModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """ORM model for ReadinessReview records."""

    __tablename__ = "standards_readiness_reviews"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    framework_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    current_stage: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    created_by: Mapped[str] = mapped_column(String(36), nullable=False, default="")
    completed_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
    events_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")


class FrameworkComparisonModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """ORM model for FrameworkComparison records."""

    __tablename__ = "standards_framework_comparisons"

    framework_a_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    framework_b_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    added_competencies_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    removed_competencies_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    renamed_elements_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    changed_relationships_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    coverage_differences_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    generated_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)


class LearningOutcomeValidationModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """ORM model for LearningOutcomeValidation records."""

    __tablename__ = "standards_outcome_validations"

    framework_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    missing_outcomes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    duplicate_outcomes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    unmapped_outcomes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    weak_coverage: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    assessment_gaps: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    doc_gaps: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    a11y_gaps: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    recommendations_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    validated_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)
