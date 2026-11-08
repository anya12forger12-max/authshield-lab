"""Domain entities for skills taxonomies."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class SkillRelationship:
    """A weighted relationship between two skills."""

    source_skill_id: str = ""
    target_skill_id: str = ""
    relationship_type: str = ""
    weight: float = 1.0

    def validate_weight(self) -> None:
        if not 0.0 <= self.weight <= 1.0:
            raise ValueError("Weight must be between 0.0 and 1.0")

    def to_dict(self) -> dict:
        return {
            "source_skill_id": self.source_skill_id,
            "target_skill_id": self.target_skill_id,
            "relationship_type": self.relationship_type,
            "weight": self.weight,
        }


@dataclass
class TaxonomySkill:
    """A single skill inside a taxonomy."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    taxonomy_id: str = ""
    name: str = ""
    description: str = ""
    category: str = ""
    parent_id: str | None = None
    aliases: list[str] = field(default_factory=list)
    level: str = ""
    version: int = 1

    def add_alias(self, alias: str) -> None:
        if alias not in self.aliases:
            self.aliases.append(alias)

    def remove_alias(self, alias: str) -> bool:
        if alias in self.aliases:
            self.aliases.remove(alias)
            return True
        return False

    def bump_version(self) -> None:
        self.version += 1

    def is_root(self) -> bool:
        return self.parent_id is None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "taxonomy_id": self.taxonomy_id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "parent_id": self.parent_id,
            "aliases": list(self.aliases),
            "level": self.level,
            "version": self.version,
        }


@dataclass
class SkillCategory:
    """A hierarchical category for grouping skills."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    taxonomy_id: str = ""
    name: str = ""
    description: str = ""
    parent_id: str | None = None
    skill_count: int = 0

    def increment_count(self) -> None:
        self.skill_count += 1

    def decrement_count(self) -> None:
        if self.skill_count > 0:
            self.skill_count -= 1

    def is_root(self) -> bool:
        return self.parent_id is None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "taxonomy_id": self.taxonomy_id,
            "name": self.name,
            "description": self.description,
            "parent_id": self.parent_id,
            "skill_count": self.skill_count,
        }


@dataclass
class TaxonomyVersion:
    """Record of a taxonomy version change."""

    taxonomy_id: str = ""
    version: str = ""
    changes: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def add_change(self, change: str) -> None:
        self.changes.append(change)

    def to_dict(self) -> dict:
        return {
            "taxonomy_id": self.taxonomy_id,
            "version": self.version,
            "changes": list(self.changes),
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class SkillTaxonomy:
    """Root aggregate for a skills taxonomy."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    version: str = ""
    skills: list[TaxonomySkill] = field(default_factory=list)
    relationships: list[SkillRelationship] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def add_skill(self, skill: TaxonomySkill) -> None:
        skill.taxonomy_id = self.id
        self.skills.append(skill)
        self._touch()

    def remove_skill(self, skill_id: str) -> bool:
        for idx, s in enumerate(self.skills):
            if s.id == skill_id:
                self.skills.pop(idx)
                self._touch()
                return True
        return False

    def find_skill(self, skill_id: str) -> TaxonomySkill | None:
        for s in self.skills:
            if s.id == skill_id:
                return s
        return None

    def find_skill_by_name(self, name: str) -> TaxonomySkill | None:
        for s in self.skills:
            if s.name == name:
                return s
        return None

    def add_relationship(self, relationship: SkillRelationship) -> None:
        relationship.validate_weight()
        self.relationships.append(relationship)
        self._touch()

    def remove_relationship(self, source_id: str, target_id: str) -> bool:
        for idx, rel in enumerate(self.relationships):
            if rel.source_skill_id == source_id and rel.target_skill_id == target_id:
                self.relationships.pop(idx)
                self._touch()
                return True
        return False

    def get_relationships_for(self, skill_id: str) -> list[SkillRelationship]:
        return [
            r for r in self.relationships
            if r.source_skill_id == skill_id or r.target_skill_id == skill_id
        ]

    def get_prerequisites(self, skill_id: str) -> list[SkillRelationship]:
        return [
            r for r in self.relationships
            if r.target_skill_id == skill_id and r.relationship_type == "prerequisite"
        ]

    def search_skills(self, query: str) -> list[TaxonomySkill]:
        q = query.lower()
        return [
            s for s in self.skills
            if q in s.name.lower() or q in s.description.lower()
            or any(q in alias.lower() for alias in s.aliases)
        ]

    def skills_by_category(self, category: str) -> list[TaxonomySkill]:
        return [s for s in self.skills if s.category == category]

    def skills_by_level(self, level: str) -> list[TaxonomySkill]:
        return [s for s in self.skills if s.level == level]

    def skill_count(self) -> int:
        return len(self.skills)

    def relationship_count(self) -> int:
        return len(self.relationships)

    def _touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "skills": [s.to_dict() for s in self.skills],
            "relationships": [r.to_dict() for r in self.relationships],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
