"""Timeline service for CRUD and branching operations."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from ..domain.entities.timeline import Timeline, TimelineEvent, BranchPath
from ..domain.interfaces import TimelineRepositoryInterface
from ...shared.events.event_bus import EventBus, DomainEvent, EventType, get_event_bus


class TimelineService:
    """Service layer for timeline management.

    Handles creation, event manipulation, branching, and lifecycle
    of simulation timelines.
    """

    def __init__(
        self,
        repository: TimelineRepositoryInterface,
        event_bus: EventBus | None = None,
    ) -> None:
        self._repo = repository
        self._event_bus = event_bus or get_event_bus()

    async def create_timeline(
        self,
        name: str,
        scenario_id: str,
    ) -> Timeline:
        """Create and persist a new timeline."""
        timeline = Timeline(
            id=str(uuid.uuid4()),
            name=name,
            scenario_id=scenario_id,
            created_at=datetime.now(timezone.utc),
        )
        created = await self._repo.create(timeline)

        event = DomainEvent(
            event_type=EventType.AUDIT_EVENT,
            module="simulation",
            message=f"Timeline created: {created.name}",
            metadata={"timeline_id": created.id, "scenario_id": scenario_id},
        )
        await self._event_bus.publish(event)
        return created

    async def get_timeline(self, timeline_id: str) -> Optional[Timeline]:
        """Retrieve a timeline by ID."""
        return await self._repo.get_by_id(timeline_id)

    async def list_timelines(
        self, page: int = 1, per_page: int = 20
    ) -> dict[str, Any]:
        """List all timelines with pagination."""
        return await self._repo.get_all(page=page, per_page=per_page)

    async def update_timeline(
        self, timeline_id: str, data: dict[str, Any]
    ) -> Optional[Timeline]:
        """Update an existing timeline."""
        return await self._repo.update(timeline_id, data)

    async def delete_timeline(self, timeline_id: str) -> bool:
        """Delete a timeline by ID."""
        return await self._repo.delete(timeline_id)

    async def add_event(
        self,
        timeline_id: str,
        event_type: str,
        timestamp_offset_ms: int,
        data: dict[str, Any] | None = None,
        milestone: bool = False,
        instructor_annotation: str = "",
        learner_checkpoint: bool = False,
        replay_marker: bool = False,
    ) -> TimelineEvent:
        """Add an event to a timeline."""
        timeline = await self._repo.get_by_id(timeline_id)
        if timeline is None:
            raise ValueError(f"Timeline {timeline_id} not found")

        timeline_event = TimelineEvent(
            id=str(uuid.uuid4()),
            event_type=event_type,
            timestamp_offset_ms=timestamp_offset_ms,
            data=data or {},
            milestone=milestone,
            instructor_annotation=instructor_annotation,
            learner_checkpoint=learner_checkpoint,
            replay_marker=replay_marker,
        )
        timeline.add_event(timeline_event)
        await self._repo.update(
            timeline_id,
            {
                "events": timeline.events,
                "branches": timeline.branches,
                "total_duration_ms": timeline.total_duration_ms,
            },
        )
        return timeline_event

    async def remove_event(self, timeline_id: str, event_id: str) -> bool:
        """Remove an event from a timeline."""
        timeline = await self._repo.get_by_id(timeline_id)
        if timeline is None:
            raise ValueError(f"Timeline {timeline_id} not found")

        removed = timeline.remove_event(event_id)
        if removed:
            await self._repo.update(
                timeline_id,
                {
                    "events": timeline.events,
                    "branches": timeline.branches,
                    "total_duration_ms": timeline.total_duration_ms,
                },
            )
        return removed

    async def reorder_events(
        self, timeline_id: str, event_ids: list[str]
    ) -> Timeline:
        """Reorder events in a timeline."""
        timeline = await self._repo.get_by_id(timeline_id)
        if timeline is None:
            raise ValueError(f"Timeline {timeline_id} not found")

        timeline.reorder_events(event_ids)
        await self._repo.update(
            timeline_id,
            {
                "events": timeline.events,
                "branches": timeline.branches,
                "total_duration_ms": timeline.total_duration_ms,
            },
        )
        return timeline

    async def add_branch(
        self,
        timeline_id: str,
        source_event_id: str,
        target_event_id: str,
        condition: str = "",
    ) -> BranchPath:
        """Add a branch path to a timeline."""
        timeline = await self._repo.get_by_id(timeline_id)
        if timeline is None:
            raise ValueError(f"Timeline {timeline_id} not found")

        branch = BranchPath(
            id=str(uuid.uuid4()),
            source_event_id=source_event_id,
            target_event_id=target_event_id,
            condition=condition,
        )
        timeline.add_branch(branch)
        await self._repo.update(
            timeline_id,
            {"events": timeline.events, "branches": timeline.branches},
        )
        return branch

    async def remove_branch(self, timeline_id: str, branch_id: str) -> bool:
        """Remove a branch from a timeline."""
        timeline = await self._repo.get_by_id(timeline_id)
        if timeline is None:
            raise ValueError(f"Timeline {timeline_id} not found")

        removed = timeline.remove_branch(branch_id)
        if removed:
            await self._repo.update(
                timeline_id,
                {"events": timeline.events, "branches": timeline.branches},
            )
        return removed

    async def get_milestones(self, timeline_id: str) -> list[TimelineEvent]:
        """Return all milestone events in a timeline."""
        timeline = await self._repo.get_by_id(timeline_id)
        if timeline is None:
            raise ValueError(f"Timeline {timeline_id} not found")
        return timeline.get_milestones()

    async def get_checkpoints(self, timeline_id: str) -> list[TimelineEvent]:
        """Return all learner checkpoint events in a timeline."""
        timeline = await self._repo.get_by_id(timeline_id)
        if timeline is None:
            raise ValueError(f"Timeline {timeline_id} not found")
        return timeline.get_checkpoints()

    async def get_by_scenario_id(self, scenario_id: str) -> list[Timeline]:
        """Return all timelines for a given scenario."""
        return await self._repo.get_by_scenario_id(scenario_id)

    async def get_events_in_window(
        self, timeline_id: str, start_ms: int, end_ms: int
    ) -> list[TimelineEvent]:
        """Return events within a time window."""
        timeline = await self._repo.get_by_id(timeline_id)
        if timeline is None:
            raise ValueError(f"Timeline {timeline_id} not found")
        return timeline.get_events_in_window(start_ms, end_ms)
