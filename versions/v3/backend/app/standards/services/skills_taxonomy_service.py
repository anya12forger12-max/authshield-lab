"""Service layer for skills taxonomy CRUD, relationships, versioning, and search."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from app.standards.domain.entities.skills_taxonomy import (
    SkillCategory,
    SkillRelationship,
    SkillTaxonomy,
    TaxonomySkill,
    TaxonomyVersion,
)
from app.standards.domain.interfaces.standards_interfaces import (
    AbstractSkillCategoryRepository,
    AbstractSkillRelationshipRepository,
    AbstractSkillTaxonomyRepository,
    AbstractTaxonomySkillRepository,
    AbstractTaxonomyVersionRepository,
)
from app.standards.validators.standards_validator import StandardsValidator

logger = logging.getLogger(__name__)


class SkillsTaxonomyService:
    """Manages skills taxonomies and their relationships."""

    def __init__(
        self,
        taxonomy_repo: AbstractSkillTaxonomyRepository | None = None,
        skill_repo: AbstractTaxonomySkillRepository | None = None,
        category_repo: AbstractSkillCategoryRepository | None = None,
        relationship_repo: AbstractSkillRelationshipRepository | None = None,
        version_repo: AbstractTaxonomyVersionRepository | None = None,
    ) -> None:
        from app.standards.repositories.standards_repository_impl import (
            InMemorySkillCategoryRepository,
            InMemorySkillRelationshipRepository,
            InMemorySkillTaxonomyRepository,
            InMemoryTaxonomySkillRepository,
            InMemoryTaxonomyVersionRepository,
        )

        self._taxonomies = taxonomy_repo or InMemorySkillTaxonomyRepository()
        self._skills = skill_repo or InMemoryTaxonomySkillRepository()
        self._categories = category_repo or InMemorySkillCategoryRepository()
        self._relationships = relationship_repo or InMemorySkillRelationshipRepository()
        self._versions = version_repo or InMemoryTaxonomyVersionRepository()
        self._validator = StandardsValidator()

    # ------------------------------------------------------------------
    # Taxonomy CRUD
    # ------------------------------------------------------------------

    def create_taxonomy(
        self,
        name: str,
        description: str = "",
        version: str = "1.0",
    ) -> SkillTaxonomy:
        self._validator.validate_non_empty(name, "name")
        tax = SkillTaxonomy(name=name, description=description, version=version)
        self._taxonomies.save(tax)
        logger.info("Taxonomy created: id=%s name=%s", tax.id, tax.name)
        return tax

    def get_taxonomy(self, taxonomy_id: str) -> SkillTaxonomy | None:
        return self._taxonomies.get_by_id(taxonomy_id)

    def list_taxonomies(self) -> list[SkillTaxonomy]:
        return self._taxonomies.list_all()

    def update_taxonomy(
        self,
        taxonomy_id: str,
        name: str | None = None,
        description: str | None = None,
    ) -> SkillTaxonomy | None:
        tax = self._taxonomies.get_by_id(taxonomy_id)
        if tax is None:
            return None
        if name is not None:
            tax.name = name
        if description is not None:
            tax.description = description
        tax._touch()
        self._taxonomies.save(tax)
        return tax

    def delete_taxonomy(self, taxonomy_id: str) -> bool:
        return self._taxonomies.delete(taxonomy_id)

    # ------------------------------------------------------------------
    # Skills
    # ------------------------------------------------------------------

    def add_skill(
        self,
        taxonomy_id: str,
        name: str,
        description: str = "",
        category: str = "",
        parent_id: str | None = None,
        aliases: list[str] | None = None,
        level: str = "",
    ) -> TaxonomySkill | None:
        tax = self._taxonomies.get_by_id(taxonomy_id)
        if tax is None:
            return None
        self._validator.validate_non_empty(name, "name")
        skill = TaxonomySkill(
            taxonomy_id=taxonomy_id,
            name=name,
            description=description,
            category=category,
            parent_id=parent_id,
            aliases=aliases or [],
            level=level,
        )
        tax.add_skill(skill)
        self._taxonomies.save(tax)
        self._skills.save(skill)
        if hasattr(self._relationships, 'set_taxonomy_index'):
            self._relationships.set_taxonomy_index(skill.id, taxonomy_id)
        return skill

    def get_skill(self, skill_id: str) -> TaxonomySkill | None:
        return self._skills.get_by_id(skill_id)

    def list_skills(self, taxonomy_id: str) -> list[TaxonomySkill]:
        return self._skills.list_by_taxonomy(taxonomy_id)

    def search_skills(self, query: str) -> list[TaxonomySkill]:
        return self._skills.search(query)

    def update_skill(
        self,
        skill_id: str,
        name: str | None = None,
        description: str | None = None,
        level: str | None = None,
    ) -> TaxonomySkill | None:
        skill = self._skills.get_by_id(skill_id)
        if skill is None:
            return None
        if name is not None:
            skill.name = name
        if description is not None:
            skill.description = description
        if level is not None:
            skill.level = level
        skill.bump_version()
        self._skills.save(skill)
        return skill

    def remove_skill(self, taxonomy_id: str, skill_id: str) -> bool:
        tax = self._taxonomies.get_by_id(taxonomy_id)
        if tax is None:
            return False
        removed = tax.remove_skill(skill_id)
        if removed:
            self._taxonomies.save(tax)
            self._skills.delete(skill_id)
        return removed

    # ------------------------------------------------------------------
    # Categories
    # ------------------------------------------------------------------

    def add_category(
        self,
        taxonomy_id: str,
        name: str,
        description: str = "",
        parent_id: str | None = None,
    ) -> SkillCategory | None:
        tax = self._taxonomies.get_by_id(taxonomy_id)
        if tax is None:
            return None
        self._validator.validate_non_empty(name, "name")
        cat = SkillCategory(
            taxonomy_id=taxonomy_id,
            name=name,
            description=description,
            parent_id=parent_id,
        )
        self._categories.save(cat)
        return cat

    def list_categories(self, taxonomy_id: str) -> list[SkillCategory]:
        return self._categories.list_by_taxonomy(taxonomy_id)

    def remove_category(self, category_id: str) -> bool:
        return self._categories.delete(category_id)

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    def add_relationship(
        self,
        source_skill_id: str,
        target_skill_id: str,
        relationship_type: str,
        weight: float = 1.0,
        taxonomy_id: str = "",
    ) -> SkillRelationship:
        self._validator.validate_non_empty(source_skill_id, "source_skill_id")
        self._validator.validate_non_empty(target_skill_id, "target_skill_id")
        self._validator.validate_non_empty(relationship_type, "relationship_type")
        rel = SkillRelationship(
            source_skill_id=source_skill_id,
            target_skill_id=target_skill_id,
            relationship_type=relationship_type,
            weight=weight,
        )
        rel.validate_weight()
        self._relationships.save(rel)
        if taxonomy_id:
            tax = self._taxonomies.get_by_id(taxonomy_id)
            if tax is not None:
                tax.add_relationship(rel)
                self._taxonomies.save(tax)
            if hasattr(self._relationships, 'set_taxonomy_index'):
                self._relationships.set_taxonomy_index(source_skill_id, taxonomy_id)
                self._relationships.set_taxonomy_index(target_skill_id, taxonomy_id)
        return rel

    def list_relationships(self, taxonomy_id: str) -> list[SkillRelationship]:
        return self._relationships.list_by_taxonomy(taxonomy_id)

    def list_relationships_for_skill(self, skill_id: str) -> list[SkillRelationship]:
        return self._relationships.list_by_skill(skill_id)

    def remove_relationship(self, source_id: str, target_id: str) -> bool:
        return self._relationships.delete(source_id, target_id)

    # ------------------------------------------------------------------
    # Versioning
    # ------------------------------------------------------------------

    def create_version(
        self,
        taxonomy_id: str,
        version: str,
        changes: list[str] | None = None,
    ) -> TaxonomyVersion | None:
        tax = self._taxonomies.get_by_id(taxonomy_id)
        if tax is None:
            return None
        self._validator.validate_non_empty(version, "version")
        tv = TaxonomyVersion(
            taxonomy_id=taxonomy_id,
            version=version,
            changes=changes or [],
        )
        self._versions.save(tv)
        tax.version = version
        tax._touch()
        self._taxonomies.save(tax)
        return tv

    def list_versions(self, taxonomy_id: str) -> list[TaxonomyVersion]:
        return self._versions.list_by_taxonomy(taxonomy_id)
