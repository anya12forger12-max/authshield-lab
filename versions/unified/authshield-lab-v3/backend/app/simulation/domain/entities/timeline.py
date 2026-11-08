"""Timeline domain entity for simulation event sequencing."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class TimelineEvent:
    """A single event within a simulation timeline."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    timestamp_offset_ms: int = 0
    data: dict[str, Any] = field(default_factory=dict)
    milestone: bool = False
    instructor_annotation: str = ""
    learner_checkpoint: bool = False
    replay_marker: bool = False
    order: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "event_type": self.event_type,
            "timestamp_offset_ms": self.timestamp_offset_ms,
            "data": self.data,
            "milestone": self.milestone,
            "instructor_annotation": self.instructor_annotation,
            "learner_checkpoint": self.learner_checkpoint,
            "replay_marker": self.replay_marker,
            "order": self.order,
        }


@dataclass
class BranchPath:
    """A conditional branch connecting two timeline events."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_event_id: str = ""
    target_event_id: str = ""
    condition: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "source_event_id": self.source_event_id,
            "target_event_id": self.target_event_id,
            "condition": self.condition,
        }


@dataclass
class Timeline:
    """A timeline of events for a simulation scenario.

    Supports branching paths, milestone tracking, and learner checkpoints
    for structured replay and assessment.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    scenario_id: str = ""
    events: list[TimelineEvent] = field(default_factory=list)
    branches: list[BranchPath] = field(default_factory=list)
    total_duration_ms: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def add_event(self, event: TimelineEvent) -> None:
        """Add an event and recalculate the timeline."""
        event.order = len(self.events)
        self.events.append(event)
        self._sort_events()
        self.calculate_duration()

    def remove_event(self, event_id: str) -> bool:
        """Remove an event by ID. Returns True if found and removed."""
        original_len = len(self.events)
        self.events = [e for e in self.events if e.id != event_id]
        if len(self.events) < original_len:
            self._reindex_events()
            self.branches = [
                b
                for b in self.branches
                if b.source_event_id != event_id and b.target_event_id != event_id
            ]
            self.calculate_duration()
            return True
        return False

    def reorder_events(self, event_ids: list[str]) -> None:
        """Reorder events to match the given ID sequence.

        Only includes IDs that exist in the timeline; unknown IDs are ignored.
        """
        event_map = {e.id: e for e in self.events}
        reordered: list[TimelineEvent] = []
        for eid in event_ids:
            if eid in event_map:
                reordered.append(event_map[eid])
        for eid, event in event_map.items():
            if eid not in event_ids:
                reordered.append(event)
        self.events = reordered
        self._reindex_events()
        self.calculate_duration()

    def get_milestones(self) -> list[TimelineEvent]:
        """Return all events marked as milestones."""
        return [e for e in self.events if e.milestone]

    def get_checkpoints(self) -> list[TimelineEvent]:
        """Return all events marked as learner checkpoints."""
        return [e for e in self.events if e.learner_checkpoint]

    def calculate_duration(self) -> int:
        """Calculate total timeline duration from event offsets.

        Updates ``total_duration_ms`` and returns the computed value.
        """
        if not self.events:
            self.total_duration_ms = 0
            return 0
        max_offset = max(e.timestamp_offset_ms for e in self.events)
        self.total_duration_ms = max_offset
        return self.total_duration_ms

    def get_events_in_window(
        self, start_ms: int, end_ms: int
    ) -> list[TimelineEvent]:
        """Return events whose offset falls within the given window."""
        return [
            e
            for e in self.events
            if start_ms <= e.timestamp_offset_ms <= end_ms
        ]

    def get_branches_from(self, event_id: str) -> list[BranchPath]:
        """Return all branches originating from the given event."""
        return [b for b in self.branches if b.source_event_id == event_id]

    def add_branch(self, branch: BranchPath) -> None:
        """Add a branch path to the timeline."""
        self.branches.append(branch)

    def remove_branch(self, branch_id: str) -> bool:
        """Remove a branch by ID. Returns True if found and removed."""
        original_len = len(self.branches)
        self.branches = [b for b in self.branches if b.id != branch_id]
        return len(self.branches) < original_len

    def _sort_events(self) -> None:
        """Sort events by timestamp offset."""
        self.events.sort(key=lambda e: e.timestamp_offset_ms)

    def _reindex_events(self) -> None:
        """Reassign sequential order numbers to all events."""
        for idx, event in enumerate(self.events):
            event.order = idx

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "scenario_id": self.scenario_id,
            "events": [e.to_dict() for e in self.events],
            "branches": [b.to_dict() for b in self.branches],
            "total_duration_ms": self.total_duration_ms,
            "created_at": self.created_at.isoformat(),
        }
