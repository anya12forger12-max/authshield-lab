"""Domain entities for competency frameworks."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class FrameworkCompetency:
    """A single competency within a framework."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    framework_id: str = ""
    name: str = ""
    description: str = ""
    domain_id: str = ""
    level: str = ""
    skills: list[str] = field(default_factory=list)

    def add_skill(self, skill_id: str) -> None:
        if skill_id not in self.skills:
            self.skills.append(skill_id)

    def remove_skill(self, skill_id: str) -> bool:
        if skill_id in self.skills:
            self.skills.remove(skill_id)
            return True
        return False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "framework_id": self.framework_id,
            "name": self.name,
            "description": self.description,
            "domain_id": self.domain_id,
            "level": self.level,
            "skills": list(self.skills),
        }


@dataclass
class FrameworkCategory:
    """A category grouping competencies inside a framework."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    framework_id: str = ""
    name: str = ""
    description: str = ""
    competency_ids: list[str] = field(default_factory=list)

    def add_competency(self, competency_id: str) -> None:
        if competency_id not in self.competency_ids:
            self.competency_ids.append(competency_id)

    def remove_competency(self, competency_id: str) -> bool:
        if competency_id in self.competency_ids:
            self.competency_ids.remove(competency_id)
            return True
        return False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "framework_id": self.framework_id,
            "name": self.name,
            "description": self.description,
            "competency_ids": list(self.competency_ids),
        }


@dataclass
class FrameworkDomain:
    """A domain grouping categories inside a framework."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    framework_id: str = ""
    name: str = ""
    description: str = ""
    category_ids: list[str] = field(default_factory=list)

    def add_category(self, category_id: str) -> None:
        if category_id not in self.category_ids:
            self.category_ids.append(category_id)

    def remove_category(self, category_id: str) -> bool:
        if category_id in self.category_ids:
            self.category_ids.remove(category_id)
            return True
        return False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "framework_id": self.framework_id,
            "name": self.name,
            "description": self.description,
            "category_ids": list(self.category_ids),
        }


@dataclass
class LearningObjective:
    """A learning objective tied to a competency."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    framework_id: str = ""
    competency_id: str = ""
    description: str = ""
    level: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "framework_id": self.framework_id,
            "competency_id": self.competency_id,
            "description": self.description,
            "level": self.level,
        }


@dataclass
class Skill:
    """A skill definition within a framework."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    framework_id: str = ""
    name: str = ""
    description: str = ""
    parent_id: str | None = None
    aliases: list[str] = field(default_factory=list)
    category: str = ""

    def add_alias(self, alias: str) -> None:
        if alias not in self.aliases:
            self.aliases.append(alias)

    def remove_alias(self, alias: str) -> bool:
        if alias in self.aliases:
            self.aliases.remove(alias)
            return True
        return False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "framework_id": self.framework_id,
            "name": self.name,
            "description": self.description,
            "parent_id": self.parent_id,
            "aliases": list(self.aliases),
            "category": self.category,
        }


@dataclass
class KnowledgeArea:
    """A knowledge area grouping skills."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    framework_id: str = ""
    name: str = ""
    description: str = ""
    skill_ids: list[str] = field(default_factory=list)

    def add_skill(self, skill_id: str) -> None:
        if skill_id not in self.skill_ids:
            self.skill_ids.append(skill_id)

    def remove_skill(self, skill_id: str) -> bool:
        if skill_id in self.skill_ids:
            self.skill_ids.remove(skill_id)
            return True
        return False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "framework_id": self.framework_id,
            "name": self.name,
            "description": self.description,
            "skill_ids": list(self.skill_ids),
        }


@dataclass
class FrameworkReference:
    """An external reference attached to a framework."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    framework_id: str = ""
    title: str = ""
    url: str = ""
    reference_type: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "framework_id": self.framework_id,
            "title": self.title,
            "url": self.url,
            "reference_type": self.reference_type,
        }


@dataclass
class CompetencyFramework:
    """Root aggregate for a competency framework."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    version: str = ""
    description: str = ""
    status: str = "active"
    categories: list[FrameworkCategory] = field(default_factory=list)
    domains: list[FrameworkDomain] = field(default_factory=list)
    competencies: list[FrameworkCompetency] = field(default_factory=list)
    learning_objectives: list[LearningObjective] = field(default_factory=list)
    skills: list[Skill] = field(default_factory=list)
    knowledge_areas: list[KnowledgeArea] = field(default_factory=list)
    references: list[FrameworkReference] = field(default_factory=list)
    revision_history: list[dict] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def add_competency(self, competency: FrameworkCompetency) -> None:
        competency.framework_id = self.id
        self.competencies.append(competency)
        self._touch()

    def remove_competency(self, competency_id: str) -> bool:
        for idx, comp in enumerate(self.competencies):
            if comp.id == competency_id:
                self.competencies.pop(idx)
                self._touch()
                return True
        return False

    def add_domain(self, domain: FrameworkDomain) -> None:
        domain.framework_id = self.id
        self.domains.append(domain)
        self._touch()

    def remove_domain(self, domain_id: str) -> bool:
        for idx, dom in enumerate(self.domains):
            if dom.id == domain_id:
                self.domains.pop(idx)
                self._touch()
                return True
        return False

    def add_category(self, category: FrameworkCategory) -> None:
        category.framework_id = self.id
        self.categories.append(category)
        self._touch()

    def remove_category(self, category_id: str) -> bool:
        for idx, cat in enumerate(self.categories):
            if cat.id == category_id:
                self.categories.pop(idx)
                self._touch()
                return True
        return False

    def add_learning_objective(self, objective: LearningObjective) -> None:
        objective.framework_id = self.id
        self.learning_objectives.append(objective)
        self._touch()

    def remove_learning_objective(self, objective_id: str) -> bool:
        for idx, obj in enumerate(self.learning_objectives):
            if obj.id == objective_id:
                self.learning_objectives.pop(idx)
                self._touch()
                return True
        return False

    def add_skill(self, skill: Skill) -> None:
        skill.framework_id = self.id
        self.skills.append(skill)
        self._touch()

    def remove_skill(self, skill_id: str) -> bool:
        for idx, s in enumerate(self.skills):
            if s.id == skill_id:
                self.skills.pop(idx)
                self._touch()
                return True
        return False

    def add_knowledge_area(self, area: KnowledgeArea) -> None:
        area.framework_id = self.id
        self.knowledge_areas.append(area)
        self._touch()

    def remove_knowledge_area(self, area_id: str) -> bool:
        for idx, a in enumerate(self.knowledge_areas):
            if a.id == area_id:
                self.knowledge_areas.pop(idx)
                self._touch()
                return True
        return False

    def add_reference(self, reference: FrameworkReference) -> None:
        reference.framework_id = self.id
        self.references.append(reference)
        self._touch()

    def remove_reference(self, reference_id: str) -> bool:
        for idx, ref in enumerate(self.references):
            if ref.id == reference_id:
                self.references.pop(idx)
                self._touch()
                return True
        return False

    def update_status(self, new_status: str) -> None:
        valid = {"active", "deprecated", "draft"}
        if new_status not in valid:
            raise ValueError(f"Invalid status: {new_status}. Must be one of {valid}")
        old = self.status
        self.status = new_status
        self._touch()
        self.revision_history.append({
            "field": "status",
            "old_value": old,
            "new_value": new_status,
            "changed_at": datetime.now(timezone.utc).isoformat(),
        })

    def bump_version(self, new_version: str) -> None:
        old = self.version
        self.version = new_version
        self._touch()
        self.revision_history.append({
            "field": "version",
            "old_value": old,
            "new_value": new_version,
            "changed_at": datetime.now(timezone.utc).isoformat(),
        })

    def find_competency(self, competency_id: str) -> FrameworkCompetency | None:
        for c in self.competencies:
            if c.id == competency_id:
                return c
        return None

    def find_skill(self, skill_id: str) -> Skill | None:
        for s in self.skills:
            if s.id == skill_id:
                return s
        return None

    def find_domain(self, domain_id: str) -> FrameworkDomain | None:
        for d in self.domains:
            if d.id == domain_id:
                return d
        return None

    def find_category(self, category_id: str) -> FrameworkCategory | None:
        for c in self.categories:
            if c.id == category_id:
                return c
        return None

    def competency_count(self) -> int:
        return len(self.competencies)

    def skill_count(self) -> int:
        return len(self.skills)

    def domain_count(self) -> int:
        return len(self.domains)

    def _touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "status": self.status,
            "categories": [c.to_dict() for c in self.categories],
            "domains": [d.to_dict() for d in self.domains],
            "competencies": [c.to_dict() for c in self.competencies],
            "learning_objectives": [o.to_dict() for o in self.learning_objectives],
            "skills": [s.to_dict() for s in self.skills],
            "knowledge_areas": [a.to_dict() for a in self.knowledge_areas],
            "references": [r.to_dict() for r in self.references],
            "revision_history": list(self.revision_history),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
