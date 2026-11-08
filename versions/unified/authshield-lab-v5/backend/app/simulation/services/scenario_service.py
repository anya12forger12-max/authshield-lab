"""Scenario service for CRUD and lifecycle operations."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from ..domain.entities.scenario import Scenario, ScenarioStatus
from ..domain.interfaces import ScenarioRepositoryInterface
from ...shared.events.event_bus import EventBus, DomainEvent, EventType, get_event_bus


class ScenarioService:
    """Service layer for scenario management.

    Provides CRUD operations, lifecycle transitions, and event publishing
    for simulation scenarios.
    """

    def __init__(
        self,
        repository: ScenarioRepositoryInterface,
        event_bus: EventBus | None = None,
    ) -> None:
        self._repo = repository
        self._event_bus = event_bus or get_event_bus()

    async def create_scenario(
        self,
        title: str,
        description: str,
        difficulty: str = "beginner",
        learning_objectives: list[str] | None = None,
        prerequisites: list[str] | None = None,
        estimated_duration_minutes: int = 30,
        target_audience: str = "",
        required_competencies: list[str] | None = None,
        tags: list[str] | None = None,
        scenario_type: str = "AuthenticationReview",
        created_by: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> Scenario:
        """Create and persist a new scenario."""
        scenario = Scenario(
            id=str(uuid.uuid4()),
            title=title,
            description=description,
            difficulty=difficulty,
            learning_objectives=learning_objectives or [],
            prerequisites=prerequisites or [],
            estimated_duration_minutes=estimated_duration_minutes,
            target_audience=target_audience,
            required_competencies=required_competencies or [],
            tags=tags or [],
            scenario_type=scenario_type,
            created_by=created_by,
            scenario_metadata=metadata or {},
            status=ScenarioStatus.DRAFT,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        errors = scenario.validate()
        if errors:
            raise ValueError(f"Scenario validation failed: {'; '.join(errors)}")

        created = await self._repo.create(scenario)

        event = DomainEvent(
            event_type=EventType.AUDIT_EVENT,
            module="simulation",
            message=f"Scenario created: {created.title}",
            metadata={"scenario_id": created.id, "title": created.title},
        )
        await self._event_bus.publish(event)
        return created

    async def get_scenario(self, scenario_id: str) -> Optional[Scenario]:
        """Retrieve a scenario by ID."""
        return await self._repo.get_by_id(scenario_id)

    async def list_scenarios(
        self, page: int = 1, per_page: int = 20
    ) -> dict[str, Any]:
        """List all scenarios with pagination."""
        return await self._repo.get_all(page=page, per_page=per_page)

    async def update_scenario(
        self, scenario_id: str, data: dict[str, Any]
    ) -> Optional[Scenario]:
        """Update an existing scenario."""
        scenario = await self._repo.get_by_id(scenario_id)
        if scenario is None:
            return None
        data["updated_at"] = datetime.now(timezone.utc)
        return await self._repo.update(scenario_id, data)

    async def delete_scenario(self, scenario_id: str) -> bool:
        """Delete a scenario by ID."""
        return await self._repo.delete(scenario_id)

    async def publish_scenario(self, scenario_id: str) -> Scenario:
        """Transition a scenario to published status."""
        scenario = await self._repo.get_by_id(scenario_id)
        if scenario is None:
            raise ValueError(f"Scenario {scenario_id} not found")
        scenario.publish()
        updated = await self._repo.update(
            scenario_id,
            {"status": scenario.status, "updated_at": scenario.updated_at},
        )
        if updated is None:
            raise ValueError("Failed to update scenario status")

        event = DomainEvent(
            event_type=EventType.AUDIT_EVENT,
            module="simulation",
            message=f"Scenario published: {updated.title}",
            metadata={"scenario_id": updated.id, "version": updated.version},
        )
        await self._event_bus.publish(event)
        return updated

    async def archive_scenario(self, scenario_id: str) -> Scenario:
        """Transition a scenario to archived status."""
        scenario = await self._repo.get_by_id(scenario_id)
        if scenario is None:
            raise ValueError(f"Scenario {scenario_id} not found")
        scenario.archive()
        updated = await self._repo.update(
            scenario_id,
            {"status": scenario.status, "updated_at": scenario.updated_at},
        )
        if updated is None:
            raise ValueError("Failed to update scenario status")

        event = DomainEvent(
            event_type=EventType.AUDIT_EVENT,
            module="simulation",
            message=f"Scenario archived: {updated.title}",
            metadata={"scenario_id": updated.id},
        )
        await self._event_bus.publish(event)
        return updated

    async def clone_scenario(self, scenario_id: str) -> Scenario:
        """Clone a scenario with a new ID and draft status."""
        scenario = await self._repo.get_by_id(scenario_id)
        if scenario is None:
            raise ValueError(f"Scenario {scenario_id} not found")
        cloned = scenario.clone()
        return await self._repo.create(cloned)

    async def search_scenarios(
        self, query: str, page: int = 1, per_page: int = 20
    ) -> dict[str, Any]:
        """Search scenarios by query string."""
        return await self._repo.search(query, page=page, per_page=per_page)

    async def get_by_status(self, status: str) -> list[Scenario]:
        """Return all scenarios with the given status."""
        return await self._repo.get_by_status(status)
