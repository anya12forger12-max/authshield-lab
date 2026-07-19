"""Abstract repository interfaces for the Standards module."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

    from app.standards.domain.entities.evidence import EvidenceCollection, EvidenceItem
    from app.standards.domain.entities.framework import (
        CompetencyFramework,
        FrameworkCategory,
        FrameworkCompetency,
        FrameworkDomain,
        FrameworkReference,
        KnowledgeArea,
        LearningObjective,
        Skill,
    )
    from app.standards.domain.entities.mapping import (
        CoverageReport,
        CurriculumMapping,
        MappingBulkResult,
    )
    from app.standards.domain.entities.quality import (
        AcademicQualityDashboard,
        FrameworkComparison,
        LearningOutcomeValidation,
        ReadinessReview,
    )
    from app.standards.domain.entities.skills_taxonomy import (
        SkillCategory,
        SkillRelationship,
        SkillTaxonomy,
        TaxonomySkill,
        TaxonomyVersion,
    )


# ---------------------------------------------------------------------------
# Framework Repositories
# ---------------------------------------------------------------------------


class AbstractFrameworkRepository(ABC):
    """Interface for CompetencyFramework persistence."""

    @abstractmethod
    def get_by_id(self, framework_id: str) -> CompetencyFramework | None:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[CompetencyFramework]:
        raise NotImplementedError

    @abstractmethod
    def list_by_status(self, status: str) -> list[CompetencyFramework]:
        raise NotImplementedError

    @abstractmethod
    def save(self, framework: CompetencyFramework) -> CompetencyFramework:
        raise NotImplementedError

    @abstractmethod
    def delete(self, framework_id: str) -> bool:
        raise NotImplementedError


class AbstractFrameworkCompetencyRepository(ABC):
    """Interface for FrameworkCompetency persistence."""

    @abstractmethod
    def get_by_id(self, competency_id: str) -> FrameworkCompetency | None:
        raise NotImplementedError

    @abstractmethod
    def list_by_framework(self, framework_id: str) -> list[FrameworkCompetency]:
        raise NotImplementedError

    @abstractmethod
    def list_by_domain(self, domain_id: str) -> list[FrameworkCompetency]:
        raise NotImplementedError

    @abstractmethod
    def save(self, competency: FrameworkCompetency) -> FrameworkCompetency:
        raise NotImplementedError

    @abstractmethod
    def delete(self, competency_id: str) -> bool:
        raise NotImplementedError


class AbstractFrameworkDomainRepository(ABC):
    """Interface for FrameworkDomain persistence."""

    @abstractmethod
    def get_by_id(self, domain_id: str) -> FrameworkDomain | None:
        raise NotImplementedError

    @abstractmethod
    def list_by_framework(self, framework_id: str) -> list[FrameworkDomain]:
        raise NotImplementedError

    @abstractmethod
    def save(self, domain: FrameworkDomain) -> FrameworkDomain:
        raise NotImplementedError

    @abstractmethod
    def delete(self, domain_id: str) -> bool:
        raise NotImplementedError


class AbstractFrameworkCategoryRepository(ABC):
    """Interface for FrameworkCategory persistence."""

    @abstractmethod
    def get_by_id(self, category_id: str) -> FrameworkCategory | None:
        raise NotImplementedError

    @abstractmethod
    def list_by_framework(self, framework_id: str) -> list[FrameworkCategory]:
        raise NotImplementedError

    @abstractmethod
    def save(self, category: FrameworkCategory) -> FrameworkCategory:
        raise NotImplementedError

    @abstractmethod
    def delete(self, category_id: str) -> bool:
        raise NotImplementedError


class AbstractLearningObjectiveRepository(ABC):
    """Interface for LearningObjective persistence."""

    @abstractmethod
    def get_by_id(self, objective_id: str) -> LearningObjective | None:
        raise NotImplementedError

    @abstractmethod
    def list_by_framework(self, framework_id: str) -> list[LearningObjective]:
        raise NotImplementedError

    @abstractmethod
    def list_by_competency(self, competency_id: str) -> list[LearningObjective]:
        raise NotImplementedError

    @abstractmethod
    def save(self, objective: LearningObjective) -> LearningObjective:
        raise NotImplementedError

    @abstractmethod
    def delete(self, objective_id: str) -> bool:
        raise NotImplementedError


class AbstractSkillRepository(ABC):
    """Interface for Skill persistence."""

    @abstractmethod
    def get_by_id(self, skill_id: str) -> Skill | None:
        raise NotImplementedError

    @abstractmethod
    def list_by_framework(self, framework_id: str) -> list[Skill]:
        raise NotImplementedError

    @abstractmethod
    def search(self, query: str) -> list[Skill]:
        raise NotImplementedError

    @abstractmethod
    def save(self, skill: Skill) -> Skill:
        raise NotImplementedError

    @abstractmethod
    def delete(self, skill_id: str) -> bool:
        raise NotImplementedError


class AbstractKnowledgeAreaRepository(ABC):
    """Interface for KnowledgeArea persistence."""

    @abstractmethod
    def get_by_id(self, area_id: str) -> KnowledgeArea | None:
        raise NotImplementedError

    @abstractmethod
    def list_by_framework(self, framework_id: str) -> list[KnowledgeArea]:
        raise NotImplementedError

    @abstractmethod
    def save(self, area: KnowledgeArea) -> KnowledgeArea:
        raise NotImplementedError

    @abstractmethod
    def delete(self, area_id: str) -> bool:
        raise NotImplementedError


class AbstractFrameworkReferenceRepository(ABC):
    """Interface for FrameworkReference persistence."""

    @abstractmethod
    def get_by_id(self, reference_id: str) -> FrameworkReference | None:
        raise NotImplementedError

    @abstractmethod
    def list_by_framework(self, framework_id: str) -> list[FrameworkReference]:
        raise NotImplementedError

    @abstractmethod
    def save(self, reference: FrameworkReference) -> FrameworkReference:
        raise NotImplementedError

    @abstractmethod
    def delete(self, reference_id: str) -> bool:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Mapping Repositories
# ---------------------------------------------------------------------------


class AbstractCurriculumMappingRepository(ABC):
    """Interface for CurriculumMapping persistence."""

    @abstractmethod
    def get_by_id(self, mapping_id: str) -> CurriculumMapping | None:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[CurriculumMapping]:
        raise NotImplementedError

    @abstractmethod
    def list_by_source(self, source_id: str) -> list[CurriculumMapping]:
        raise NotImplementedError

    @abstractmethod
    def list_by_target(self, target_id: str) -> list[CurriculumMapping]:
        raise NotImplementedError

    @abstractmethod
    def save(self, mapping: CurriculumMapping) -> CurriculumMapping:
        raise NotImplementedError

    @abstractmethod
    def delete(self, mapping_id: str) -> bool:
        raise NotImplementedError


class AbstractCoverageReportRepository(ABC):
    """Interface for CoverageReport persistence."""

    @abstractmethod
    def save(self, report: CoverageReport) -> CoverageReport:
        raise NotImplementedError

    @abstractmethod
    def find_latest(self, framework_id: str) -> CoverageReport | None:
        raise NotImplementedError

    @abstractmethod
    def find_all(self) -> list[CoverageReport]:
        raise NotImplementedError


class AbstractMappingBulkResultRepository(ABC):
    """Interface for MappingBulkResult persistence."""

    @abstractmethod
    def save(self, result: MappingBulkResult) -> MappingBulkResult:
        raise NotImplementedError

    @abstractmethod
    def find_all(self) -> list[MappingBulkResult]:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Skills Taxonomy Repositories
# ---------------------------------------------------------------------------


class AbstractSkillTaxonomyRepository(ABC):
    """Interface for SkillTaxonomy persistence."""

    @abstractmethod
    def get_by_id(self, taxonomy_id: str) -> SkillTaxonomy | None:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[SkillTaxonomy]:
        raise NotImplementedError

    @abstractmethod
    def save(self, taxonomy: SkillTaxonomy) -> SkillTaxonomy:
        raise NotImplementedError

    @abstractmethod
    def delete(self, taxonomy_id: str) -> bool:
        raise NotImplementedError


class AbstractTaxonomySkillRepository(ABC):
    """Interface for TaxonomySkill persistence."""

    @abstractmethod
    def get_by_id(self, skill_id: str) -> TaxonomySkill | None:
        raise NotImplementedError

    @abstractmethod
    def list_by_taxonomy(self, taxonomy_id: str) -> list[TaxonomySkill]:
        raise NotImplementedError

    @abstractmethod
    def search(self, query: str) -> list[TaxonomySkill]:
        raise NotImplementedError

    @abstractmethod
    def save(self, skill: TaxonomySkill) -> TaxonomySkill:
        raise NotImplementedError

    @abstractmethod
    def delete(self, skill_id: str) -> bool:
        raise NotImplementedError


class AbstractSkillCategoryRepository(ABC):
    """Interface for SkillCategory persistence."""

    @abstractmethod
    def get_by_id(self, category_id: str) -> SkillCategory | None:
        raise NotImplementedError

    @abstractmethod
    def list_by_taxonomy(self, taxonomy_id: str) -> list[SkillCategory]:
        raise NotImplementedError

    @abstractmethod
    def save(self, category: SkillCategory) -> SkillCategory:
        raise NotImplementedError

    @abstractmethod
    def delete(self, category_id: str) -> bool:
        raise NotImplementedError


class AbstractSkillRelationshipRepository(ABC):
    """Interface for SkillRelationship persistence."""

    @abstractmethod
    def list_by_taxonomy(self, taxonomy_id: str) -> list[SkillRelationship]:
        raise NotImplementedError

    @abstractmethod
    def list_by_skill(self, skill_id: str) -> list[SkillRelationship]:
        raise NotImplementedError

    @abstractmethod
    def save(self, relationship: SkillRelationship) -> SkillRelationship:
        raise NotImplementedError

    @abstractmethod
    def delete(self, source_id: str, target_id: str) -> bool:
        raise NotImplementedError


class AbstractTaxonomyVersionRepository(ABC):
    """Interface for TaxonomyVersion persistence."""

    @abstractmethod
    def list_by_taxonomy(self, taxonomy_id: str) -> list[TaxonomyVersion]:
        raise NotImplementedError

    @abstractmethod
    def save(self, version: TaxonomyVersion) -> TaxonomyVersion:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Evidence Repositories
# ---------------------------------------------------------------------------


class AbstractEvidenceCollectionRepository(ABC):
    """Interface for EvidenceCollection persistence."""

    @abstractmethod
    def get_by_id(self, collection_id: str) -> EvidenceCollection | None:
        raise NotImplementedError

    @abstractmethod
    def list_by_framework(self, framework_id: str) -> list[EvidenceCollection]:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[EvidenceCollection]:
        raise NotImplementedError

    @abstractmethod
    def save(self, collection: EvidenceCollection) -> EvidenceCollection:
        raise NotImplementedError

    @abstractmethod
    def delete(self, collection_id: str) -> bool:
        raise NotImplementedError


class AbstractEvidenceItemRepository(ABC):
    """Interface for EvidenceItem persistence."""

    @abstractmethod
    def get_by_id(self, item_id: str) -> EvidenceItem | None:
        raise NotImplementedError

    @abstractmethod
    def list_by_collection(self, collection_id: str) -> list[EvidenceItem]:
        raise NotImplementedError

    @abstractmethod
    def search(self, query: str) -> list[EvidenceItem]:
        raise NotImplementedError

    @abstractmethod
    def save(self, item: EvidenceItem) -> EvidenceItem:
        raise NotImplementedError

    @abstractmethod
    def delete(self, item_id: str) -> bool:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Quality Repositories
# ---------------------------------------------------------------------------


class AbstractAcademicQualityDashboardRepository(ABC):
    """Interface for AcademicQualityDashboard persistence."""

    @abstractmethod
    def save(self, dashboard: AcademicQualityDashboard) -> AcademicQualityDashboard:
        raise NotImplementedError

    @abstractmethod
    def find_latest(self) -> AcademicQualityDashboard | None:
        raise NotImplementedError

    @abstractmethod
    def find_all(self) -> list[AcademicQualityDashboard]:
        raise NotImplementedError


class AbstractReadinessReviewRepository(ABC):
    """Interface for ReadinessReview persistence."""

    @abstractmethod
    def get_by_id(self, review_id: str) -> ReadinessReview | None:
        raise NotImplementedError

    @abstractmethod
    def list_by_framework(self, framework_id: str) -> list[ReadinessReview]:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[ReadinessReview]:
        raise NotImplementedError

    @abstractmethod
    def save(self, review: ReadinessReview) -> ReadinessReview:
        raise NotImplementedError

    @abstractmethod
    def delete(self, review_id: str) -> bool:
        raise NotImplementedError


class AbstractFrameworkComparisonRepository(ABC):
    """Interface for FrameworkComparison persistence."""

    @abstractmethod
    def save(self, comparison: FrameworkComparison) -> FrameworkComparison:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, comparison_id: str) -> FrameworkComparison | None:
        raise NotImplementedError

    @abstractmethod
    def find_all(self) -> list[FrameworkComparison]:
        raise NotImplementedError


class AbstractLearningOutcomeValidationRepository(ABC):
    """Interface for LearningOutcomeValidation persistence."""

    @abstractmethod
    def save(self, validation: LearningOutcomeValidation) -> LearningOutcomeValidation:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, validation_id: str) -> LearningOutcomeValidation | None:
        raise NotImplementedError

    @abstractmethod
    def list_by_framework(self, framework_id: str) -> list[LearningOutcomeValidation]:
        raise NotImplementedError
