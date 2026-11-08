"""Replay service for timeline playback, highlighting, and comparison."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from ..domain.entities.timeline import Timeline, TimelineEvent
from ..domain.interfaces import TimelineRepositoryInterface
from ...shared.events.event_bus import EventBus, DomainEvent, EventType, get_event_bus


class ReplayService:
    """Service for replaying simulation timelines.

    Supports playback at configurable speeds, event highlighting,
    and timeline comparison for educational review.
    """

    def __init__(
        self,
        timeline_repository: TimelineRepositoryInterface,
        event_bus: EventBus | None = None,
    ) -> None:
        self._timeline_repo = timeline_repository
        self._event_bus = event_bus or get_event_bus()

    async def start_replay(
        self,
        timeline_id: str,
        initiated_by: str = "",
        speed_multiplier: float = 1.0,
        highlighted_event_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        """Start a replay session for a timeline."""
        timeline = await self._timeline_repo.get_by_id(timeline_id)
        if timeline is None:
            raise ValueError(f"Timeline {timeline_id} not found")

        event = DomainEvent(
            event_type=EventType.AUDIT_EVENT,
            module="simulation",
            message=f"Replay started for timeline {timeline_id}",
            metadata={
                "timeline_id": timeline_id,
                "initiated_by": initiated_by,
                "speed_multiplier": speed_multiplier,
            },
        )
        await self._event_bus.publish(event)

        return {
            "replay_id": str(uuid.uuid4()),
            "timeline_id": timeline_id,
            "timeline_name": timeline.name,
            "scenario_id": timeline.scenario_id,
            "total_events": len(timeline.events),
            "total_duration_ms": timeline.total_duration_ms,
            "speed_multiplier": speed_multiplier,
            "highlighted_events": highlighted_event_ids or [],
            "started_at": datetime.now(timezone.utc).isoformat(),
        }

    async def get_playback_state(
        self,
        timeline_id: str,
        current_offset_ms: int,
    ) -> dict[str, Any]:
        """Get the playback state at a specific time offset."""
        timeline = await self._timeline_repo.get_by_id(timeline_id)
        if timeline is None:
            raise ValueError(f"Timeline {timeline_id} not found")

        visible_events = [
            e for e in timeline.events
            if e.timestamp_offset_ms <= current_offset_ms
        ]

        milestones_hit = [e for e in visible_events if e.milestone]
        checkpoints_hit = [e for e in visible_events if e.learner_checkpoint]

        return {
            "timeline_id": timeline_id,
            "current_offset_ms": current_offset_ms,
            "total_duration_ms": timeline.total_duration_ms,
            "progress": (
                current_offset_ms / timeline.total_duration_ms
                if timeline.total_duration_ms > 0
                else 0.0
            ),
            "visible_events": [e.to_dict() for e in visible_events],
            "milestones_hit": [e.to_dict() for e in milestones_hit],
            "checkpoints_hit": [e.to_dict() for e in checkpoints_hit],
        }

    async def get_events_at_offset(
        self,
        timeline_id: str,
        offset_ms: int,
        tolerance_ms: int = 500,
    ) -> list[TimelineEvent]:
        """Return events near a specific time offset within tolerance."""
        timeline = await self._timeline_repo.get_by_id(timeline_id)
        if timeline is None:
            raise ValueError(f"Timeline {timeline_id} not found")

        return [
            e for e in timeline.events
            if abs(e.timestamp_offset_ms - offset_ms) <= tolerance_ms
        ]

    async def highlight_events(
        self,
        timeline_id: str,
        event_ids: list[str],
    ) -> dict[str, Any]:
        """Return timeline data with specified events highlighted."""
        timeline = await self._timeline_repo.get_by_id(timeline_id)
        if timeline is None:
            raise ValueError(f"Timeline {timeline_id} not found")

        highlighted: list[dict[str, Any]] = []
        all_events: list[dict[str, Any]] = []
        for event in timeline.events:
            event_dict = event.to_dict()
            event_dict["highlighted"] = event.id in event_ids
            all_events.append(event_dict)
            if event.id in event_ids:
                highlighted.append(event_dict)

        return {
            "timeline_id": timeline_id,
            "total_events": len(timeline.events),
            "highlighted_count": len(highlighted),
            "events": all_events,
        }

    async def compare_timelines(
        self,
        timeline_id_a: str,
        timeline_id_b: str,
    ) -> dict[str, Any]:
        """Compare two timelines and return differences."""
        timeline_a = await self._timeline_repo.get_by_id(timeline_id_a)
        timeline_b = await self._timeline_repo.get_by_id(timeline_id_b)

        if timeline_a is None:
            raise ValueError(f"Timeline {timeline_id_a} not found")
        if timeline_b is None:
            raise ValueError(f"Timeline {timeline_id_b} not found")

        events_a = {e.event_type: e for e in timeline_a.events}
        events_b = {e.event_type: e for e in timeline_b.events}

        types_a = set(events_a.keys())
        types_b = set(events_b.keys())

        only_in_a = types_a - types_b
        only_in_b = types_b - types_a
        common = types_a & types_b

        duration_diff = timeline_a.total_duration_ms - timeline_b.total_duration_ms

        return {
            "timeline_a": {
                "id": timeline_a.id,
                "name": timeline_a.name,
                "total_events": len(timeline_a.events),
                "total_duration_ms": timeline_a.total_duration_ms,
            },
            "timeline_b": {
                "id": timeline_b.id,
                "name": timeline_b.name,
                "total_events": len(timeline_b.events),
                "total_duration_ms": timeline_b.total_duration_ms,
            },
            "differences": {
                "event_types_only_in_a": list(only_in_a),
                "event_types_only_in_b": list(only_in_b),
                "common_event_types": list(common),
                "duration_difference_ms": duration_diff,
                "event_count_difference": len(timeline_a.events) - len(timeline_b.events),
                "branch_count_difference": len(timeline_a.branches) - len(timeline_b.branches),
            },
        }

    async def get_milestone_summary(
        self, timeline_id: str
    ) -> dict[str, Any]:
        """Return a summary of all milestones in a timeline."""
        timeline = await self._timeline_repo.get_by_id(timeline_id)
        if timeline is None:
            raise ValueError(f"Timeline {timeline_id} not found")

        milestones = timeline.get_milestones()
        return {
            "timeline_id": timeline_id,
            "total_milestones": len(milestones),
            "milestones": [m.to_dict() for m in milestones],
            "total_duration_ms": timeline.total_duration_ms,
        }

    async def get_checkpoints_summary(
        self, timeline_id: str
    ) -> dict[str, Any]:
        """Return a summary of all learner checkpoints in a timeline."""
        timeline = await self._timeline_repo.get_by_id(timeline_id)
        if timeline is None:
            raise ValueError(f"Timeline {timeline_id} not found")

        checkpoints = timeline.get_checkpoints()
        return {
            "timeline_id": timeline_id,
            "total_checkpoints": len(checkpoints),
            "checkpoints": [c.to_dict() for c in checkpoints],
        }

    async def export_replay_data(
        self, timeline_id: str
    ) -> dict[str, Any]:
        """Export complete replay data for a timeline."""
        timeline = await self._timeline_repo.get_by_id(timeline_id)
        if timeline is None:
            raise ValueError(f"Timeline {timeline_id} not found")

        return {
            "timeline": timeline.to_dict(),
            "milestones": [m.to_dict() for m in timeline.get_milestones()],
            "checkpoints": [c.to_dict() for c in timeline.get_checkpoints()],
            "branches": [b.to_dict() for b in timeline.branches],
            "exported_at": datetime.now(timezone.utc).isoformat(),
        }
