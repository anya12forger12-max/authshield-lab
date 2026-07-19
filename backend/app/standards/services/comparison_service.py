"""Service layer for comparing frameworks, detecting changes, and generating migration reports."""

from __future__ import annotations

import logging

from app.standards.domain.entities.framework import CompetencyFramework
from app.standards.domain.entities.quality import FrameworkComparison
from app.standards.domain.interfaces.standards_interfaces import (
    AbstractFrameworkComparisonRepository,
    AbstractFrameworkRepository,
)
from app.standards.validators.standards_validator import StandardsValidator

logger = logging.getLogger(__name__)


class ComparisonService:
    """Compares two frameworks and generates migration reports."""

    def __init__(
        self,
        framework_repo: AbstractFrameworkRepository | None = None,
        comparison_repo: AbstractFrameworkComparisonRepository | None = None,
    ) -> None:
        from app.standards.repositories.standards_repository_impl import (
            InMemoryFrameworkComparisonRepository,
            InMemoryFrameworkRepository,
        )

        self._frameworks = framework_repo or InMemoryFrameworkRepository()
        self._comparisons = comparison_repo or InMemoryFrameworkComparisonRepository()
        self._validator = StandardsValidator()

    def compare(
        self,
        framework_a_id: str,
        framework_b_id: str,
    ) -> FrameworkComparison:
        fw_a = self._frameworks.get_by_id(framework_a_id)
        fw_b = self._frameworks.get_by_id(framework_b_id)
        if fw_a is None:
            raise ValueError(f"Framework A {framework_a_id} not found")
        if fw_b is None:
            raise ValueError(f"Framework B {framework_b_id} not found")
        return self._diff(fw_a, fw_b)

    def compare_versions(
        self,
        framework_id: str,
        version_a: str,
        version_b: str,
    ) -> FrameworkComparison:
        fw = self._frameworks.get_by_id(framework_id)
        if fw is None:
            raise ValueError(f"Framework {framework_id} not found")
        fw_a = self._clone_framework_for_version(fw, version_a)
        fw_b = self._clone_framework_for_version(fw, version_b)
        return self._diff(fw_a, fw_b)

    def detect_changes(
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
        a_skills = {s.name for s in fw_a.skills}
        b_skills = {s.name for s in fw_b.skills}
        a_domains = {d.name for d in fw_a.domains}
        b_domains = {d.name for d in fw_b.domains}
        return {
            "added_competencies": list(b_names - a_names),
            "removed_competencies": list(a_names - b_names),
            "added_skills": list(b_skills - a_skills),
            "removed_skills": list(a_skills - b_skills),
            "added_domains": list(b_domains - a_domains),
            "removed_domains": list(a_domains - b_domains),
        }

    def generate_migration_report(
        self,
        framework_a_id: str,
        framework_b_id: str,
    ) -> dict:
        fw_a = self._frameworks.get_by_id(framework_a_id)
        fw_b = self._frameworks.get_by_id(framework_b_id)
        if fw_a is None or fw_b is None:
            raise ValueError("Both frameworks must exist")
        comparison = self._diff(fw_a, fw_b)
        self._comparisons.save(comparison)
        migration_steps: list[dict] = []
        for added in comparison.added_competencies:
            migration_steps.append({
                "action": "add",
                "element": "competency",
                "name": added,
                "description": f"Add new competency '{added}' from {fw_b.name}",
            })
        for removed in comparison.removed_competencies:
            migration_steps.append({
                "action": "remove",
                "element": "competency",
                "name": removed,
                "description": f"Remove competency '{removed}' no longer in {fw_b.name}",
            })
        for changed in comparison.changed_relationships:
            migration_steps.append({
                "action": "update",
                "element": "competency",
                "name": changed.get("name", ""),
                "description": f"Update {changed.get('field', '')} from '{changed.get('old', '')}' to '{changed.get('new', '')}'",
            })
        return {
            "comparison_id": comparison.id,
            "framework_a": {"id": fw_a.id, "name": fw_a.name, "version": fw_a.version},
            "framework_b": {"id": fw_b.id, "name": fw_b.name, "version": fw_b.version},
            "summary": {
                "added": len(comparison.added_competencies),
                "removed": len(comparison.removed_competencies),
                "changed": len(comparison.changed_relationships),
                "total_changes": comparison.change_count(),
            },
            "migration_steps": migration_steps,
        }

    def list_comparisons(self) -> list[FrameworkComparison]:
        return self._comparisons.find_all()

    def get_comparison(self, comparison_id: str) -> FrameworkComparison | None:
        return self._comparisons.get_by_id(comparison_id)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _diff(self, fw_a: CompetencyFramework, fw_b: CompetencyFramework) -> FrameworkComparison:
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
            if set(a_comp.skills) != set(b_comp.skills):
                changed_rels.append({
                    "name": name,
                    "field": "skills",
                    "old": a_comp.skills,
                    "new": b_comp.skills,
                })
        coverage_diffs: dict[str, float] = {}
        total_a = len(fw_a.competencies)
        total_b = len(fw_b.competencies)
        if total_a > 0 or total_b > 0:
            coverage_diffs["competency_count_diff"] = float(total_b - total_a)
        coverage_diffs["skill_count_diff"] = float(len(fw_b.skills) - len(fw_a.skills))
        coverage_diffs["domain_count_diff"] = float(len(fw_b.domains) - len(fw_a.domains))
        comparison = FrameworkComparison(
            framework_a_id=fw_a.id,
            framework_b_id=fw_b.id,
            added_competencies=added,
            removed_competencies=removed,
            renamed_elements=renamed,
            changed_relationships=changed_rels,
            coverage_differences=coverage_diffs,
        )
        self._comparisons.save(comparison)
        return comparison

    def _clone_framework_for_version(
        self,
        fw: CompetencyFramework,
        version: str,
    ) -> CompetencyFramework:
        clone = CompetencyFramework(
            id=fw.id,
            name=fw.name,
            version=version,
            description=fw.description,
            status=fw.status,
        )
        for comp in fw.competencies:
            from app.standards.domain.entities.framework import FrameworkCompetency
            clone.competencies.append(FrameworkCompetency(
                id=comp.id,
                framework_id=clone.id,
                name=comp.name,
                description=comp.description,
                domain_id=comp.domain_id,
                level=comp.level,
                skills=list(comp.skills),
            ))
        for skill in fw.skills:
            from app.standards.domain.entities.framework import Skill
            clone.skills.append(Skill(
                id=skill.id,
                framework_id=clone.id,
                name=skill.name,
                description=skill.description,
                parent_id=skill.parent_id,
                aliases=list(skill.aliases),
                category=skill.category,
            ))
        for dom in fw.domains:
            from app.standards.domain.entities.framework import FrameworkDomain
            clone.domains.append(FrameworkDomain(
                id=dom.id,
                framework_id=clone.id,
                name=dom.name,
                description=dom.description,
                category_ids=list(dom.category_ids),
            ))
        return clone
