"""In-memory repository implementations for the Standards module."""

from __future__ import annotations

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
from app.standards.domain.interfaces.standards_interfaces import (
    AbstractAcademicQualityDashboardRepository,
    AbstractCoverageReportRepository,
    AbstractCurriculumMappingRepository,
    AbstractEvidenceCollectionRepository,
    AbstractEvidenceItemRepository,
    AbstractFrameworkCategoryRepository,
    AbstractFrameworkCompetencyRepository,
    AbstractFrameworkComparisonRepository,
    AbstractFrameworkDomainRepository,
    AbstractFrameworkReferenceRepository,
    AbstractFrameworkRepository,
    AbstractKnowledgeAreaRepository,
    AbstractLearningObjectiveRepository,
    AbstractLearningOutcomeValidationRepository,
    AbstractMappingBulkResultRepository,
    AbstractReadinessReviewRepository,
    AbstractSkillCategoryRepository,
    AbstractSkillRelationshipRepository,
    AbstractSkillRepository,
    AbstractSkillTaxonomyRepository,
    AbstractTaxonomySkillRepository,
    AbstractTaxonomyVersionRepository,
)


# ---------------------------------------------------------------------------
# Framework Repositories
# ---------------------------------------------------------------------------


class InMemoryFrameworkRepository(AbstractFrameworkRepository):
    """In-memory CompetencyFramework repository."""

    def __init__(self) -> None:
        self._store: dict[str, CompetencyFramework] = {}

    def get_by_id(self, framework_id: str) -> CompetencyFramework | None:
        return self._store.get(framework_id)

    def list_all(self) -> list[CompetencyFramework]:
        return list(self._store.values())

    def list_by_status(self, status: str) -> list[CompetencyFramework]:
        return [f for f in self._store.values() if f.status == status]

    def save(self, framework: CompetencyFramework) -> CompetencyFramework:
        self._store[framework.id] = framework
        return framework

    def delete(self, framework_id: str) -> bool:
        return self._store.pop(framework_id, None) is not None


class InMemoryFrameworkCompetencyRepository(AbstractFrameworkCompetencyRepository):
    """In-memory FrameworkCompetency repository."""

    def __init__(self) -> None:
        self._store: dict[str, FrameworkCompetency] = {}

    def get_by_id(self, competency_id: str) -> FrameworkCompetency | None:
        return self._store.get(competency_id)

    def list_by_framework(self, framework_id: str) -> list[FrameworkCompetency]:
        return [c for c in self._store.values() if c.framework_id == framework_id]

    def list_by_domain(self, domain_id: str) -> list[FrameworkCompetency]:
        return [c for c in self._store.values() if c.domain_id == domain_id]

    def save(self, competency: FrameworkCompetency) -> FrameworkCompetency:
        self._store[competency.id] = competency
        return competency

    def delete(self, competency_id: str) -> bool:
        return self._store.pop(competency_id, None) is not None


class InMemoryFrameworkDomainRepository(AbstractFrameworkDomainRepository):
    """In-memory FrameworkDomain repository."""

    def __init__(self) -> None:
        self._store: dict[str, FrameworkDomain] = {}

    def get_by_id(self, domain_id: str) -> FrameworkDomain | None:
        return self._store.get(domain_id)

    def list_by_framework(self, framework_id: str) -> list[FrameworkDomain]:
        return [d for d in self._store.values() if d.framework_id == framework_id]

    def save(self, domain: FrameworkDomain) -> FrameworkDomain:
        self._store[domain.id] = domain
        return domain

    def delete(self, domain_id: str) -> bool:
        return self._store.pop(domain_id, None) is not None


class InMemoryFrameworkCategoryRepository(AbstractFrameworkCategoryRepository):
    """In-memory FrameworkCategory repository."""

    def __init__(self) -> None:
        self._store: dict[str, FrameworkCategory] = {}

    def get_by_id(self, category_id: str) -> FrameworkCategory | None:
        return self._store.get(category_id)

    def list_by_framework(self, framework_id: str) -> list[FrameworkCategory]:
        return [c for c in self._store.values() if c.framework_id == framework_id]

    def save(self, category: FrameworkCategory) -> FrameworkCategory:
        self._store[category.id] = category
        return category

    def delete(self, category_id: str) -> bool:
        return self._store.pop(category_id, None) is not None


class InMemoryLearningObjectiveRepository(AbstractLearningObjectiveRepository):
    """In-memory LearningObjective repository."""

    def __init__(self) -> None:
        self._store: dict[str, LearningObjective] = {}

    def get_by_id(self, objective_id: str) -> LearningObjective | None:
        return self._store.get(objective_id)

    def list_by_framework(self, framework_id: str) -> list[LearningObjective]:
        return [o for o in self._store.values() if o.framework_id == framework_id]

    def list_by_competency(self, competency_id: str) -> list[LearningObjective]:
        return [o for o in self._store.values() if o.competency_id == competency_id]

    def save(self, objective: LearningObjective) -> LearningObjective:
        self._store[objective.id] = objective
        return objective

    def delete(self, objective_id: str) -> bool:
        return self._store.pop(objective_id, None) is not None


class InMemorySkillRepository(AbstractSkillRepository):
    """In-memory Skill repository."""

    def __init__(self) -> None:
        self._store: dict[str, Skill] = {}

    def get_by_id(self, skill_id: str) -> Skill | None:
        return self._store.get(skill_id)

    def list_by_framework(self, framework_id: str) -> list[Skill]:
        return [s for s in self._store.values() if s.framework_id == framework_id]

    def search(self, query: str) -> list[Skill]:
        q = query.lower()
        return [
            s for s in self._store.values()
            if q in s.name.lower() or q in s.description.lower()
            or any(q in a.lower() for a in s.aliases)
        ]

    def save(self, skill: Skill) -> Skill:
        self._store[skill.id] = skill
        return skill

    def delete(self, skill_id: str) -> bool:
        return self._store.pop(skill_id, None) is not None


class InMemoryKnowledgeAreaRepository(AbstractKnowledgeAreaRepository):
    """In-memory KnowledgeArea repository."""

    def __init__(self) -> None:
        self._store: dict[str, KnowledgeArea] = {}

    def get_by_id(self, area_id: str) -> KnowledgeArea | None:
        return self._store.get(area_id)

    def list_by_framework(self, framework_id: str) -> list[KnowledgeArea]:
        return [a for a in self._store.values() if a.framework_id == framework_id]

    def save(self, area: KnowledgeArea) -> KnowledgeArea:
        self._store[area.id] = area
        return area

    def delete(self, area_id: str) -> bool:
        return self._store.pop(area_id, None) is not None


class InMemoryFrameworkReferenceRepository(AbstractFrameworkReferenceRepository):
    """In-memory FrameworkReference repository."""

    def __init__(self) -> None:
        self._store: dict[str, FrameworkReference] = {}

    def get_by_id(self, reference_id: str) -> FrameworkReference | None:
        return self._store.get(reference_id)

    def list_by_framework(self, framework_id: str) -> list[FrameworkReference]:
        return [r for r in self._store.values() if r.framework_id == framework_id]

    def save(self, reference: FrameworkReference) -> FrameworkReference:
        self._store[reference.id] = reference
        return reference

    def delete(self, reference_id: str) -> bool:
        return self._store.pop(reference_id, None) is not None


# ---------------------------------------------------------------------------
# Mapping Repositories
# ---------------------------------------------------------------------------


class InMemoryCurriculumMappingRepository(AbstractCurriculumMappingRepository):
    """In-memory CurriculumMapping repository."""

    def __init__(self) -> None:
        self._store: dict[str, CurriculumMapping] = {}

    def get_by_id(self, mapping_id: str) -> CurriculumMapping | None:
        return self._store.get(mapping_id)

    def list_all(self) -> list[CurriculumMapping]:
        return list(self._store.values())

    def list_by_source(self, source_id: str) -> list[CurriculumMapping]:
        return [m for m in self._store.values() if m.source_id == source_id]

    def list_by_target(self, target_id: str) -> list[CurriculumMapping]:
        return [m for m in self._store.values() if m.target_id == target_id]

    def save(self, mapping: CurriculumMapping) -> CurriculumMapping:
        self._store[mapping.id] = mapping
        return mapping

    def delete(self, mapping_id: str) -> bool:
        return self._store.pop(mapping_id, None) is not None


class InMemoryCoverageReportRepository(AbstractCoverageReportRepository):
    """In-memory CoverageReport repository."""

    def __init__(self) -> None:
        self._store: list[CoverageReport] = []

    def save(self, report: CoverageReport) -> CoverageReport:
        self._store.append(report)
        return report

    def find_latest(self, framework_id: str) -> CoverageReport | None:
        matches = [r for r in self._store if r.framework_id == framework_id]
        if not matches:
            return None
        return matches[-1]

    def find_all(self) -> list[CoverageReport]:
        return list(self._store)


class InMemoryMappingBulkResultRepository(AbstractMappingBulkResultRepository):
    """In-memory MappingBulkResult repository."""

    def __init__(self) -> None:
        self._store: list[MappingBulkResult] = []

    def save(self, result: MappingBulkResult) -> MappingBulkResult:
        self._store.append(result)
        return result

    def find_all(self) -> list[MappingBulkResult]:
        return list(self._store)


# ---------------------------------------------------------------------------
# Skills Taxonomy Repositories
# ---------------------------------------------------------------------------


class InMemorySkillTaxonomyRepository(AbstractSkillTaxonomyRepository):
    """In-memory SkillTaxonomy repository."""

    def __init__(self) -> None:
        self._store: dict[str, SkillTaxonomy] = {}

    def get_by_id(self, taxonomy_id: str) -> SkillTaxonomy | None:
        return self._store.get(taxonomy_id)

    def list_all(self) -> list[SkillTaxonomy]:
        return list(self._store.values())

    def save(self, taxonomy: SkillTaxonomy) -> SkillTaxonomy:
        self._store[taxonomy.id] = taxonomy
        return taxonomy

    def delete(self, taxonomy_id: str) -> bool:
        return self._store.pop(taxonomy_id, None) is not None


class InMemoryTaxonomySkillRepository(AbstractTaxonomySkillRepository):
    """In-memory TaxonomySkill repository."""

    def __init__(self) -> None:
        self._store: dict[str, TaxonomySkill] = {}

    def get_by_id(self, skill_id: str) -> TaxonomySkill | None:
        return self._store.get(skill_id)

    def list_by_taxonomy(self, taxonomy_id: str) -> list[TaxonomySkill]:
        return [s for s in self._store.values() if s.taxonomy_id == taxonomy_id]

    def search(self, query: str) -> list[TaxonomySkill]:
        q = query.lower()
        return [
            s for s in self._store.values()
            if q in s.name.lower() or q in s.description.lower()
            or any(q in a.lower() for a in s.aliases)
        ]

    def save(self, skill: TaxonomySkill) -> TaxonomySkill:
        self._store[skill.id] = skill
        return skill

    def delete(self, skill_id: str) -> bool:
        return self._store.pop(skill_id, None) is not None


class InMemorySkillCategoryRepository(AbstractSkillCategoryRepository):
    """In-memory SkillCategory repository."""

    def __init__(self) -> None:
        self._store: dict[str, SkillCategory] = {}

    def get_by_id(self, category_id: str) -> SkillCategory | None:
        return self._store.get(category_id)

    def list_by_taxonomy(self, taxonomy_id: str) -> list[SkillCategory]:
        return [c for c in self._store.values() if c.taxonomy_id == taxonomy_id]

    def save(self, category: SkillCategory) -> SkillCategory:
        self._store[category.id] = category
        return category

    def delete(self, category_id: str) -> bool:
        return self._store.pop(category_id, None) is not None


class InMemorySkillRelationshipRepository(AbstractSkillRelationshipRepository):
    """In-memory SkillRelationship repository."""

    def __init__(self) -> None:
        self._store: list[SkillRelationship] = []
        self._taxonomy_index: dict[str, str] = {}  # skill_id -> taxonomy_id

    def set_taxonomy_index(self, skill_id: str, taxonomy_id: str) -> None:
        self._taxonomy_index[skill_id] = taxonomy_id

    def list_by_taxonomy(self, taxonomy_id: str) -> list[SkillRelationship]:
        return [
            r for r in self._store
            if self._taxonomy_index.get(r.source_skill_id) == taxonomy_id
            or self._taxonomy_index.get(r.target_skill_id) == taxonomy_id
        ]

    def list_by_skill(self, skill_id: str) -> list[SkillRelationship]:
        return [
            r for r in self._store
            if r.source_skill_id == skill_id or r.target_skill_id == skill_id
        ]

    def save(self, relationship: SkillRelationship) -> SkillRelationship:
        self._store.append(relationship)
        return relationship

    def delete(self, source_id: str, target_id: str) -> bool:
        for idx, r in enumerate(self._store):
            if r.source_skill_id == source_id and r.target_skill_id == target_id:
                self._store.pop(idx)
                return True
        return False


class InMemoryTaxonomyVersionRepository(AbstractTaxonomyVersionRepository):
    """In-memory TaxonomyVersion repository."""

    def __init__(self) -> None:
        self._store: list[TaxonomyVersion] = []

    def list_by_taxonomy(self, taxonomy_id: str) -> list[TaxonomyVersion]:
        return [v for v in self._store if v.taxonomy_id == taxonomy_id]

    def save(self, version: TaxonomyVersion) -> TaxonomyVersion:
        self._store.append(version)
        return version


# ---------------------------------------------------------------------------
# Evidence Repositories
# ---------------------------------------------------------------------------


class InMemoryEvidenceCollectionRepository(AbstractEvidenceCollectionRepository):
    """In-memory EvidenceCollection repository."""

    def __init__(self) -> None:
        self._store: dict[str, EvidenceCollection] = {}

    def get_by_id(self, collection_id: str) -> EvidenceCollection | None:
        return self._store.get(collection_id)

    def list_by_framework(self, framework_id: str) -> list[EvidenceCollection]:
        return [c for c in self._store.values() if c.framework_id == framework_id]

    def list_all(self) -> list[EvidenceCollection]:
        return list(self._store.values())

    def save(self, collection: EvidenceCollection) -> EvidenceCollection:
        self._store[collection.id] = collection
        return collection

    def delete(self, collection_id: str) -> bool:
        return self._store.pop(collection_id, None) is not None


class InMemoryEvidenceItemRepository(AbstractEvidenceItemRepository):
    """In-memory EvidenceItem repository."""

    def __init__(self) -> None:
        self._store: dict[str, EvidenceItem] = {}

    def get_by_id(self, item_id: str) -> EvidenceItem | None:
        return self._store.get(item_id)

    def list_by_collection(self, collection_id: str) -> list[EvidenceItem]:
        return [i for i in self._store.values() if i.collection_id == collection_id]

    def search(self, query: str) -> list[EvidenceItem]:
        q = query.lower()
        return [
            i for i in self._store.values()
            if q in i.description.lower()
        ]

    def save(self, item: EvidenceItem) -> EvidenceItem:
        self._store[item.id] = item
        return item

    def delete(self, item_id: str) -> bool:
        return self._store.pop(item_id, None) is not None


# ---------------------------------------------------------------------------
# Quality Repositories
# ---------------------------------------------------------------------------


class InMemoryAcademicQualityDashboardRepository(AbstractAcademicQualityDashboardRepository):
    """In-memory AcademicQualityDashboard repository."""

    def __init__(self) -> None:
        self._store: list[AcademicQualityDashboard] = []

    def save(self, dashboard: AcademicQualityDashboard) -> AcademicQualityDashboard:
        self._store.append(dashboard)
        return dashboard

    def find_latest(self) -> AcademicQualityDashboard | None:
        return self._store[-1] if self._store else None

    def find_all(self) -> list[AcademicQualityDashboard]:
        return list(self._store)


class InMemoryReadinessReviewRepository(AbstractReadinessReviewRepository):
    """In-memory ReadinessReview repository."""

    def __init__(self) -> None:
        self._store: dict[str, ReadinessReview] = {}

    def get_by_id(self, review_id: str) -> ReadinessReview | None:
        return self._store.get(review_id)

    def list_by_framework(self, framework_id: str) -> list[ReadinessReview]:
        return [r for r in self._store.values() if r.framework_id == framework_id]

    def list_all(self) -> list[ReadinessReview]:
        return list(self._store.values())

    def save(self, review: ReadinessReview) -> ReadinessReview:
        self._store[review.id] = review
        return review

    def delete(self, review_id: str) -> bool:
        return self._store.pop(review_id, None) is not None


class InMemoryFrameworkComparisonRepository(AbstractFrameworkComparisonRepository):
    """In-memory FrameworkComparison repository."""

    def __init__(self) -> None:
        self._store: dict[str, FrameworkComparison] = {}

    def save(self, comparison: FrameworkComparison) -> FrameworkComparison:
        self._store[comparison.id] = comparison
        return comparison

    def get_by_id(self, comparison_id: str) -> FrameworkComparison | None:
        return self._store.get(comparison_id)

    def find_all(self) -> list[FrameworkComparison]:
        return list(self._store.values())


class InMemoryLearningOutcomeValidationRepository(AbstractLearningOutcomeValidationRepository):
    """In-memory LearningOutcomeValidation repository."""

    def __init__(self) -> None:
        self._store: dict[str, LearningOutcomeValidation] = {}

    def save(self, validation: LearningOutcomeValidation) -> LearningOutcomeValidation:
        self._store[validation.id] = validation
        return validation

    def get_by_id(self, validation_id: str) -> LearningOutcomeValidation | None:
        return self._store.get(validation_id)

    def list_by_framework(self, framework_id: str) -> list[LearningOutcomeValidation]:
        return [v for v in self._store.values() if v.framework_id == framework_id]
