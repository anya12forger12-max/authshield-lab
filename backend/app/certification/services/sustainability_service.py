"""Sustainability service: dependency tracking, API stability, ownership, docs freshness, roadmaps."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from ..domain.entities.sustainability import (
    APIStabilityReport,
    DependencyLifecycle,
    DependencyStatus,
    DocumentationFreshness,
    MaintenanceRoadmap,
    ModuleOwnership,
    RoadmapItem,
    SustainabilityDashboard,
)
from ..domain.interfaces import (
    APIStabilityRepository,
    DependencyLifecycleRepository,
    DocumentationFreshnessRepository,
    MaintenanceRoadmapRepository,
    ModuleOwnershipRepository,
    SustainabilityDashboardRepository,
)


class SustainabilityService:
    """Tracks long-term platform health: dependencies, API stability, ownership, docs, roadmaps."""

    def __init__(
        self,
        dep_repo: DependencyLifecycleRepository,
        api_repo: APIStabilityRepository,
        ownership_repo: ModuleOwnershipRepository,
        doc_repo: DocumentationFreshnessRepository,
        dashboard_repo: SustainabilityDashboardRepository,
        roadmap_repo: MaintenanceRoadmapRepository,
    ) -> None:
        self._dep_repo = dep_repo
        self._api_repo = api_repo
        self._ownership_repo = ownership_repo
        self._doc_repo = doc_repo
        self._dashboard_repo = dashboard_repo
        self._roadmap_repo = roadmap_repo

    # ── Dependencies ────────────────────────────────────────────────

    async def register_dependency(
        self,
        name: str,
        version: str,
        end_of_life_date: str | None = None,
        status: str = "supported",
        update_available: bool = False,
        latest_version: str = "",
    ) -> DependencyLifecycle:
        """Register or update a dependency."""
        try:
            dep_status = DependencyStatus(status)
        except ValueError:
            dep_status = DependencyStatus.SUPPORTED
        existing = self._dep_repo.find_by_name(name)
        if existing is not None:
            existing.version = version
            existing.end_of_life_date = end_of_life_date
            existing.status = dep_status
            existing.update_available = update_available
            existing.latest_version = latest_version
            return self._dep_repo.save(existing)
        dep = DependencyLifecycle(
            name=name,
            version=version,
            end_of_life_date=end_of_life_date,
            status=dep_status,
            update_available=update_available,
            latest_version=latest_version,
        )
        return self._dep_repo.save(dep)

    async def get_dependency(self, name: str) -> Optional[DependencyLifecycle]:
        """Retrieve a dependency by name."""
        return self._dep_repo.find_by_name(name)

    async def list_dependencies(self) -> list[DependencyLifecycle]:
        """Return all tracked dependencies."""
        return self._dep_repo.find_all()

    async def remove_dependency(self, name: str) -> bool:
        """Remove a dependency from tracking."""
        return self._dep_repo.delete(name)

    # ── API Stability ───────────────────────────────────────────────

    async def record_api_stability(
        self,
        version: str,
        endpoints: int = 0,
        deprecated: int = 0,
        breaking_changes: int = 0,
    ) -> APIStabilityReport:
        """Record an API stability report for a version."""
        report = APIStabilityReport(
            version=version,
            endpoints=endpoints,
            deprecated=deprecated,
            breaking_changes=breaking_changes,
        )
        report.recalculate_score()
        return self._api_repo.save(report)  # type: ignore[return-value]

    async def get_latest_api_stability(self) -> Optional[APIStabilityReport]:
        """Return the most recent API stability report."""
        result = self._api_repo.find_latest()
        return result  # type: ignore[return-value]

    async def get_api_stability_by_version(self, version: str) -> Optional[APIStabilityReport]:
        """Return API stability for a specific version."""
        result = self._api_repo.find_by_version(version)
        return result  # type: ignore[return-value]

    # ── Module Ownership ────────────────────────────────────────────

    async def set_module_owner(
        self,
        module: str,
        owner: str,
        health: float = 100.0,
    ) -> ModuleOwnership:
        """Register or update module ownership."""
        existing = self._ownership_repo.find_by_module(module)
        if existing is not None:
            existing.owner = owner
            existing.health = health
            existing.last_reviewed = datetime.now(timezone.utc)
            return self._ownership_repo.save(existing)
        ownership = ModuleOwnership(module=module, owner=owner, health=health)
        return self._ownership_repo.save(ownership)

    async def get_module_ownership(self, module: str) -> Optional[ModuleOwnership]:
        """Retrieve ownership for a module."""
        return self._ownership_repo.find_by_module(module)

    async def list_ownership(self) -> list[ModuleOwnership]:
        """Return ownership records for all modules."""
        return self._ownership_repo.find_all()

    # ── Documentation Freshness ─────────────────────────────────────

    async def record_doc_freshness(
        self,
        component: str,
        last_updated: datetime | None = None,
    ) -> DocumentationFreshness:
        """Record or refresh documentation freshness for a component."""
        doc = DocumentationFreshness(
            component=component,
            last_updated=last_updated or datetime.now(timezone.utc),
        )
        doc.recalculate()
        existing = self._doc_repo.find_by_component(component)
        if existing is not None:
            existing.last_updated = doc.last_updated
            existing.days_stale = doc.days_stale
            existing.status = doc.status
            return self._doc_repo.save(existing)
        return self._doc_repo.save(doc)

    async def get_doc_freshness(self, component: str) -> Optional[DocumentationFreshness]:
        """Retrieve freshness for a component."""
        return self._doc_repo.find_by_component(component)

    async def list_doc_freshness(self) -> list[DocumentationFreshness]:
        """Return freshness records for all components."""
        return self._doc_repo.find_all()

    # ── Sustainability Dashboard ────────────────────────────────────

    async def generate_dashboard(
        self,
        technical_debt_hours: float = 0.0,
    ) -> SustainabilityDashboard:
        """Assemble a sustainability dashboard from current data."""
        deps = self._dep_repo.find_all()
        api_stability = self._api_repo.find_latest()
        ownership = self._ownership_repo.find_all()
        docs = self._doc_repo.find_all()

        dashboard = SustainabilityDashboard(
            dependencies=deps,
            api_stability=api_stability if api_stability is not None else APIStabilityReport(),  # type: ignore[arg-type]
            ownership=ownership,
            documentation=docs,
            technical_debt_hours=technical_debt_hours,
        )
        dashboard.compute_maintenance_score()
        return self._dashboard_repo.save(dashboard)

    async def get_latest_dashboard(self) -> Optional[SustainabilityDashboard]:
        """Return the most recent sustainability dashboard."""
        return self._dashboard_repo.find_latest()

    # ── Maintenance Roadmap ─────────────────────────────────────────

    async def create_roadmap(
        self,
        title: str,
        priority: str = "medium",
    ) -> MaintenanceRoadmap:
        """Create a new maintenance roadmap."""
        roadmap = MaintenanceRoadmap(title=title, priority=priority)
        return self._roadmap_repo.save(roadmap)

    async def get_roadmap(self, roadmap_id: str) -> Optional[MaintenanceRoadmap]:
        """Retrieve a roadmap by ID."""
        return self._roadmap_repo.find_by_id(roadmap_id)

    async def list_roadmaps(self) -> list[MaintenanceRoadmap]:
        """Return all roadmaps."""
        return self._roadmap_repo.find_all()

    async def add_roadmap_item(
        self,
        roadmap_id: str,
        description: str,
        category: str = "",
        effort_hours: float = 0.0,
        status: str = "planned",
        target_date: str = "",
    ) -> Optional[MaintenanceRoadmap]:
        """Add an item to an existing roadmap."""
        roadmap = self._roadmap_repo.find_by_id(roadmap_id)
        if roadmap is None:
            return None
        item = RoadmapItem(
            description=description,
            category=category,
            effort_hours=effort_hours,
            status=status,
            target_date=target_date,
        )
        roadmap.add_item(item)
        return self._roadmap_repo.save(roadmap)

    async def update_roadmap_item_status(
        self,
        roadmap_id: str,
        item_index: int,
        new_status: str,
    ) -> Optional[MaintenanceRoadmap]:
        """Update the status of a specific roadmap item."""
        roadmap = self._roadmap_repo.find_by_id(roadmap_id)
        if roadmap is None:
            return None
        if 0 <= item_index < len(roadmap.items):
            roadmap.items[item_index].status = new_status
        return self._roadmap_repo.save(roadmap)

    async def delete_roadmap(self, roadmap_id: str) -> bool:
        """Remove a roadmap."""
        return self._roadmap_repo.delete(roadmap_id)
