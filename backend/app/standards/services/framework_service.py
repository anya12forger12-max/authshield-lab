"""Service layer for competency framework CRUD, versioning, comparison, and import/export."""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone

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
from app.standards.domain.events.standards_events import FrameworkCreated, FrameworkUpdated
from app.standards.domain.interfaces.standards_interfaces import (
    AbstractFrameworkCategoryRepository,
    AbstractFrameworkCompetencyRepository,
    AbstractFrameworkDomainRepository,
    AbstractFrameworkReferenceRepository,
    AbstractFrameworkRepository,
    AbstractKnowledgeAreaRepository,
    AbstractLearningObjectiveRepository,
    AbstractSkillRepository,
)
from app.standards.events.standards_event_handlers import get_event_bus
from app.standards.validators.standards_validator import StandardsValidator

logger = logging.getLogger(__name__)


class FrameworkService:
    """Manages the lifecycle of competency frameworks."""

    def __init__(
        self,
        framework_repo: AbstractFrameworkRepository | None = None,
        competency_repo: AbstractFrameworkCompetencyRepository | None = None,
        domain_repo: AbstractFrameworkDomainRepository | None = None,
        category_repo: AbstractFrameworkCategoryRepository | None = None,
        objective_repo: AbstractLearningObjectiveRepository | None = None,
        skill_repo: AbstractSkillRepository | None = None,
        knowledge_repo: AbstractKnowledgeAreaRepository | None = None,
        reference_repo: AbstractFrameworkReferenceRepository | None = None,
    ) -> None:
        from app.standards.repositories.standards_repository_impl import (
            InMemoryFrameworkCategoryRepository,
            InMemoryFrameworkCompetencyRepository,
            InMemoryFrameworkDomainRepository,
            InMemoryFrameworkReferenceRepository,
            InMemoryFrameworkRepository,
            InMemoryKnowledgeAreaRepository,
            InMemoryLearningObjectiveRepository,
            InMemorySkillRepository,
        )

        self._frameworks = framework_repo or InMemoryFrameworkRepository()
        self._competencies = competency_repo or InMemoryFrameworkCompetencyRepository()
        self._domains = domain_repo or InMemoryFrameworkDomainRepository()
        self._categories = category_repo or InMemoryFrameworkCategoryRepository()
        self._objectives = objective_repo or InMemoryLearningObjectiveRepository()
        self._skills = skill_repo or InMemorySkillRepository()
        self._knowledge_areas = knowledge_repo or InMemoryKnowledgeAreaRepository()
        self._references = reference_repo or InMemoryFrameworkReferenceRepository()
        self._validator = StandardsValidator()
        self._bus = get_event_bus()

    # ------------------------------------------------------------------
    # Framework CRUD
    # ------------------------------------------------------------------

    def create_framework(
        self,
        name: str,
        version: str = "1.0",
        description: str = "",
        status: str = "active",
    ) -> CompetencyFramework:
        self._validator.validate_non_empty(name, "name")
        self._validator.validate_framework_status(status)
        fw = CompetencyFramework(
            name=name,
            version=version,
            description=description,
            status=status,
        )
        self._frameworks.save(fw)
        event = FrameworkCreated(
            framework_id=fw.id,
            name=fw.name,
            version=fw.version,
        )
        self._bus.dispatch(event)
        logger.info("Framework created: id=%s name=%s", fw.id, fw.name)
        return fw

    def get_framework(self, framework_id: str) -> CompetencyFramework | None:
        return self._frameworks.get_by_id(framework_id)

    def list_frameworks(self) -> list[CompetencyFramework]:
        return self._frameworks.list_all()

    def list_frameworks_by_status(self, status: str) -> list[CompetencyFramework]:
        return self._frameworks.list_by_status(status)

    def update_framework(
        self,
        framework_id: str,
        name: str | None = None,
        description: str | None = None,
        status: str | None = None,
    ) -> CompetencyFramework | None:
        fw = self._frameworks.get_by_id(framework_id)
        if fw is None:
            return None
        changes: list[str] = []
        if name is not None:
            fw.name = name
            changes.append("name")
        if description is not None:
            fw.description = description
            changes.append("description")
        if status is not None:
            fw.update_status(status)
            changes.append("status")
        fw.updated_at = datetime.now(timezone.utc)
        self._frameworks.save(fw)
        if changes:
            event = FrameworkUpdated(framework_id=fw.id, changes=changes)
            self._bus.dispatch(event)
        return fw

    def delete_framework(self, framework_id: str) -> bool:
        return self._frameworks.delete(framework_id)

    def bump_framework_version(self, framework_id: str, new_version: str) -> CompetencyFramework | None:
        fw = self._frameworks.get_by_id(framework_id)
        if fw is None:
            return None
        fw.bump_version(new_version)
        self._frameworks.save(fw)
        return fw

    # ------------------------------------------------------------------
    # Competencies
    # ------------------------------------------------------------------

    def add_competency(
        self,
        framework_id: str,
        name: str,
        description: str = "",
        domain_id: str = "",
        level: str = "",
        skills: list[str] | None = None,
    ) -> FrameworkCompetency | None:
        fw = self._frameworks.get_by_id(framework_id)
        if fw is None:
            return None
        self._validator.validate_non_empty(name, "name")
        comp = FrameworkCompetency(
            framework_id=framework_id,
            name=name,
            description=description,
            domain_id=domain_id,
            level=level,
            skills=skills or [],
        )
        fw.add_competency(comp)
        self._frameworks.save(fw)
        self._competencies.save(comp)
        return comp

    def update_competency(
        self,
        competency_id: str,
        name: str | None = None,
        description: str | None = None,
        level: str | None = None,
    ) -> FrameworkCompetency | None:
        comp = self._competencies.get_by_id(competency_id)
        if comp is None:
            return None
        if name is not None:
            comp.name = name
        if description is not None:
            comp.description = description
        if level is not None:
            comp.level = level
        self._competencies.save(comp)
        return comp

    def remove_competency(self, framework_id: str, competency_id: str) -> bool:
        fw = self._frameworks.get_by_id(framework_id)
        if fw is None:
            return False
        removed = fw.remove_competency(competency_id)
        if removed:
            self._frameworks.save(fw)
            self._competencies.delete(competency_id)
        return removed

    def list_competencies(self, framework_id: str) -> list[FrameworkCompetency]:
        return self._competencies.list_by_framework(framework_id)

    # ------------------------------------------------------------------
    # Domains
    # ------------------------------------------------------------------

    def add_domain(
        self,
        framework_id: str,
        name: str,
        description: str = "",
    ) -> FrameworkDomain | None:
        fw = self._frameworks.get_by_id(framework_id)
        if fw is None:
            return None
        self._validator.validate_non_empty(name, "name")
        dom = FrameworkDomain(framework_id=framework_id, name=name, description=description)
        fw.add_domain(dom)
        self._frameworks.save(fw)
        self._domains.save(dom)
        return dom

    def remove_domain(self, framework_id: str, domain_id: str) -> bool:
        fw = self._frameworks.get_by_id(framework_id)
        if fw is None:
            return False
        removed = fw.remove_domain(domain_id)
        if removed:
            self._frameworks.save(fw)
            self._domains.delete(domain_id)
        return removed

    def list_domains(self, framework_id: str) -> list[FrameworkDomain]:
        return self._domains.list_by_framework(framework_id)

    # ------------------------------------------------------------------
    # Categories
    # ------------------------------------------------------------------

    def add_category(
        self,
        framework_id: str,
        name: str,
        description: str = "",
    ) -> FrameworkCategory | None:
        fw = self._frameworks.get_by_id(framework_id)
        if fw is None:
            return None
        self._validator.validate_non_empty(name, "name")
        cat = FrameworkCategory(framework_id=framework_id, name=name, description=description)
        fw.add_category(cat)
        self._frameworks.save(fw)
        self._categories.save(cat)
        return cat

    def remove_category(self, framework_id: str, category_id: str) -> bool:
        fw = self._frameworks.get_by_id(framework_id)
        if fw is None:
            return False
        removed = fw.remove_category(category_id)
        if removed:
            self._frameworks.save(fw)
            self._categories.delete(category_id)
        return removed

    def list_categories(self, framework_id: str) -> list[FrameworkCategory]:
        return self._categories.list_by_framework(framework_id)

    # ------------------------------------------------------------------
    # Learning Objectives
    # ------------------------------------------------------------------

    def add_learning_objective(
        self,
        framework_id: str,
        competency_id: str,
        description: str = "",
        level: str = "",
    ) -> LearningObjective | None:
        fw = self._frameworks.get_by_id(framework_id)
        if fw is None:
            return None
        self._validator.validate_non_empty(description, "description")
        obj = LearningObjective(
            framework_id=framework_id,
            competency_id=competency_id,
            description=description,
            level=level,
        )
        fw.add_learning_objective(obj)
        self._frameworks.save(fw)
        self._objectives.save(obj)
        return obj

    def list_learning_objectives(self, framework_id: str) -> list[LearningObjective]:
        return self._objectives.list_by_framework(framework_id)

    def remove_learning_objective(self, framework_id: str, objective_id: str) -> bool:
        fw = self._frameworks.get_by_id(framework_id)
        if fw is None:
            return False
        removed = fw.remove_learning_objective(objective_id)
        if removed:
            self._frameworks.save(fw)
            self._objectives.delete(objective_id)
        return removed

    # ------------------------------------------------------------------
    # Skills
    # ------------------------------------------------------------------

    def add_skill(
        self,
        framework_id: str,
        name: str,
        description: str = "",
        parent_id: str | None = None,
        aliases: list[str] | None = None,
        category: str = "",
    ) -> Skill | None:
        fw = self._frameworks.get_by_id(framework_id)
        if fw is None:
            return None
        self._validator.validate_non_empty(name, "name")
        skill = Skill(
            framework_id=framework_id,
            name=name,
            description=description,
            parent_id=parent_id,
            aliases=aliases or [],
            category=category,
        )
        fw.add_skill(skill)
        self._frameworks.save(fw)
        self._skills.save(skill)
        return skill

    def list_skills(self, framework_id: str) -> list[Skill]:
        return self._skills.list_by_framework(framework_id)

    def search_skills(self, query: str) -> list[Skill]:
        return self._skills.search(query)

    def remove_skill(self, framework_id: str, skill_id: str) -> bool:
        fw = self._frameworks.get_by_id(framework_id)
        if fw is None:
            return False
        removed = fw.remove_skill(skill_id)
        if removed:
            self._frameworks.save(fw)
            self._skills.delete(skill_id)
        return removed

    # ------------------------------------------------------------------
    # Knowledge Areas
    # ------------------------------------------------------------------

    def add_knowledge_area(
        self,
        framework_id: str,
        name: str,
        description: str = "",
    ) -> KnowledgeArea | None:
        fw = self._frameworks.get_by_id(framework_id)
        if fw is None:
            return None
        self._validator.validate_non_empty(name, "name")
        area = KnowledgeArea(framework_id=framework_id, name=name, description=description)
        fw.add_knowledge_area(area)
        self._frameworks.save(fw)
        self._knowledge_areas.save(area)
        return area

    def list_knowledge_areas(self, framework_id: str) -> list[KnowledgeArea]:
        return self._knowledge_areas.list_by_framework(framework_id)

    # ------------------------------------------------------------------
    # References
    # ------------------------------------------------------------------

    def add_reference(
        self,
        framework_id: str,
        title: str,
        url: str = "",
        reference_type: str = "",
    ) -> FrameworkReference | None:
        fw = self._frameworks.get_by_id(framework_id)
        if fw is None:
            return None
        self._validator.validate_non_empty(title, "title")
        ref = FrameworkReference(
            framework_id=framework_id,
            title=title,
            url=url,
            reference_type=reference_type,
        )
        fw.add_reference(ref)
        self._frameworks.save(fw)
        self._references.save(ref)
        return ref

    def list_references(self, framework_id: str) -> list[FrameworkReference]:
        return self._references.list_by_framework(framework_id)

    # ------------------------------------------------------------------
    # Comparison
    # ------------------------------------------------------------------

    def compare_frameworks(
        self,
        framework_a_id: str,
        framework_b_id: str,
    ) -> dict:
        fw_a = self._frameworks.get_by_id(framework_a_id)
        fw_b = self._frameworks.get_by_id(framework_b_id)
        if fw_a is None or fw_b is None:
            raise ValueError("Both frameworks must exist")
        a_names = {c.name for c in fw_a.competencies}
        b_names = {c.name for c in fw_b.competencies}
        added = list(b_names - a_names)
        removed = list(a_names - b_names)
        common = a_names & b_names
        renamed: list[dict] = []
        changed_rels: list[dict] = []
        for name in common:
            a_comp = next(c for c in fw_a.competencies if c.name == name)
            b_comp = next(c for c in fw_b.competencies if c.name == name)
            if a_comp.description != b_comp.description:
                changed_rels.append({
                    "name": name,
                    "field": "description",
                    "old": a_comp.description,
                    "new": b_comp.description,
                })
            if a_comp.level != b_comp.level:
                changed_rels.append({
                    "name": name,
                    "field": "level",
                    "old": a_comp.level,
                    "new": b_comp.level,
                })
        return {
            "framework_a_id": framework_a_id,
            "framework_b_id": framework_b_id,
            "added_competencies": added,
            "removed_competencies": removed,
            "renamed_elements": renamed,
            "changed_relationships": changed_rels,
        }

    # ------------------------------------------------------------------
    # Import / Export
    # ------------------------------------------------------------------

    def export_framework(self, framework_id: str) -> dict | None:
        fw = self._frameworks.get_by_id(framework_id)
        if fw is None:
            return None
        return fw.to_dict()

    def import_framework(self, data: dict) -> CompetencyFramework:
        name = data.get("name", "")
        self._validator.validate_non_empty(name, "name")
        fw = CompetencyFramework(
            name=name,
            version=data.get("version", "1.0"),
            description=data.get("description", ""),
            status=data.get("status", "active"),
        )
        for c_data in data.get("competencies", []):
            comp = FrameworkCompetency(
                framework_id=fw.id,
                name=c_data.get("name", ""),
                description=c_data.get("description", ""),
                domain_id=c_data.get("domain_id", ""),
                level=c_data.get("level", ""),
                skills=c_data.get("skills", []),
            )
            fw.add_competency(comp)
            self._competencies.save(comp)
        for d_data in data.get("domains", []):
            dom = FrameworkDomain(
                framework_id=fw.id,
                name=d_data.get("name", ""),
                description=d_data.get("description", ""),
                category_ids=d_data.get("category_ids", []),
            )
            fw.add_domain(dom)
            self._domains.save(dom)
        for cat_data in data.get("categories", []):
            cat = FrameworkCategory(
                framework_id=fw.id,
                name=cat_data.get("name", ""),
                description=cat_data.get("description", ""),
                competency_ids=cat_data.get("competency_ids", []),
            )
            fw.add_category(cat)
            self._categories.save(cat)
        for o_data in data.get("learning_objectives", []):
            obj = LearningObjective(
                framework_id=fw.id,
                competency_id=o_data.get("competency_id", ""),
                description=o_data.get("description", ""),
                level=o_data.get("level", ""),
            )
            fw.add_learning_objective(obj)
            self._objectives.save(obj)
        for s_data in data.get("skills", []):
            skill = Skill(
                framework_id=fw.id,
                name=s_data.get("name", ""),
                description=s_data.get("description", ""),
                parent_id=s_data.get("parent_id"),
                aliases=s_data.get("aliases", []),
                category=s_data.get("category", ""),
            )
            fw.add_skill(skill)
            self._skills.save(skill)
        for a_data in data.get("knowledge_areas", []):
            area = KnowledgeArea(
                framework_id=fw.id,
                name=a_data.get("name", ""),
                description=a_data.get("description", ""),
                skill_ids=a_data.get("skill_ids", []),
            )
            fw.add_knowledge_area(area)
            self._knowledge_areas.save(area)
        for r_data in data.get("references", []):
            ref = FrameworkReference(
                framework_id=fw.id,
                title=r_data.get("title", ""),
                url=r_data.get("url", ""),
                reference_type=r_data.get("reference_type", ""),
            )
            fw.add_reference(ref)
            self._references.save(ref)
        self._frameworks.save(fw)
        event = FrameworkCreated(framework_id=fw.id, name=fw.name, version=fw.version)
        self._bus.dispatch(event)
        return fw
