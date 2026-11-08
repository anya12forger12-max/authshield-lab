"""Simulation domain event handlers."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from ...shared.events.event_bus import EventBus, EventType, DomainEvent, get_event_bus

logger = logging.getLogger(__name__)


class SimulationEventHandler:
    """Handles simulation domain events and performs side-effect processing.

    Subscribes to relevant event types on the shared EventBus and
    performs logging, metric aggregation, and cross-module notifications.
    """

    def __init__(self, event_bus: EventBus | None = None) -> None:
        self._event_bus = event_bus or get_event_bus()
        self._event_log: list[dict[str, Any]] = []

    def register(self) -> None:
        """Subscribe all handler methods to their respective event types."""
        self._event_bus.subscribe(
            EventType.AUDIT_EVENT, self._handle_simulation_event
        )
        logger.info("Simulation event handlers registered")

    async def _handle_simulation_event(self, event: DomainEvent) -> None:
        """Route simulation audit events to specific handlers."""
        if event.module != "simulation":
            return

        entry = {
            "event_id": event.event_id,
            "event_type": event.event_type.value,
            "message": event.message,
            "metadata": event.metadata,
            "timestamp": event.timestamp.isoformat(),
            "processed_at": datetime.now(timezone.utc).isoformat(),
        }
        self._event_log.append(entry)

        metadata = event.metadata or {}

        if "scenario_id" in metadata and "title" in metadata:
            self._on_scenario_event(event, metadata)
        elif "timeline_id" in metadata and "scenario_id" in metadata:
            self._on_timeline_event(event, metadata)
        elif "exercise_id" in metadata and "session_id" in metadata:
            self._on_exercise_event(event, metadata)
        elif "result_id" in metadata:
            self._on_result_event(event, metadata)
        elif "dataset_id" in metadata:
            self._on_dataset_event(event, metadata)
        else:
            self._on_generic_event(event, metadata)

    def _on_scenario_event(
        self, event: DomainEvent, metadata: dict[str, Any]
    ) -> None:
        """Handle scenario-related events."""
        scenario_id = metadata.get("scenario_id", "unknown")
        title = metadata.get("title", "unknown")
        logger.info(
            "simulation.scenario_event | id=%s title=%s message=%s",
            scenario_id,
            title,
            event.message,
        )

    def _on_timeline_event(
        self, event: DomainEvent, metadata: dict[str, Any]
    ) -> None:
        """Handle timeline-related events."""
        timeline_id = metadata.get("timeline_id", "unknown")
        scenario_id = metadata.get("scenario_id", "unknown")
        logger.info(
            "simulation.timeline_event | timeline=%s scenario=%s message=%s",
            timeline_id,
            scenario_id,
            event.message,
        )

    def _on_exercise_event(
        self, event: DomainEvent, metadata: dict[str, Any]
    ) -> None:
        """Handle exercise and session events."""
        exercise_id = metadata.get("exercise_id", "unknown")
        session_id = metadata.get("session_id", "unknown")
        logger.info(
            "simulation.exercise_event | exercise=%s session=%s message=%s",
            exercise_id,
            session_id,
            event.message,
        )

    def _on_result_event(
        self, event: DomainEvent, metadata: dict[str, Any]
    ) -> None:
        """Handle result calculation events."""
        result_id = metadata.get("result_id", "unknown")
        overall_score = metadata.get("overall_score", 0.0)
        logger.info(
            "simulation.result_event | result=%s score=%.2f message=%s",
            result_id,
            overall_score,
            event.message,
        )

    def _on_dataset_event(
        self, event: DomainEvent, metadata: dict[str, Any]
    ) -> None:
        """Handle dataset generation events."""
        dataset_id = metadata.get("dataset_id", "unknown")
        logger.info(
            "simulation.dataset_event | dataset=%s message=%s",
            dataset_id,
            event.message,
        )

    def _on_generic_event(
        self, event: DomainEvent, metadata: dict[str, Any]
    ) -> None:
        """Handle any unclassified simulation events."""
        logger.info(
            "simulation.generic_event | event_id=%s message=%s metadata=%s",
            event.event_id,
            event.message,
            metadata,
        )

    def get_event_log(self, limit: int = 100) -> list[dict[str, Any]]:
        """Return recent event log entries."""
        return list(reversed(self._event_log[-limit:]))

    def clear_log(self) -> None:
        """Clear the event log."""
        self._event_log.clear()

    def get_log_count(self) -> int:
        """Return total number of logged events."""
        return len(self._event_log)


_global_handler: SimulationEventHandler | None = None


def get_simulation_event_handler() -> SimulationEventHandler:
    """Return the global SimulationEventHandler instance."""
    global _global_handler  # noqa: PLW0603
    if _global_handler is None:
        _global_handler = SimulationEventHandler()
        _global_handler.register()
    return _global_handler


def reset_simulation_event_handler() -> None:
    """Reset the global handler (useful in tests)."""
    global _global_handler  # noqa: PLW0603
    _global_handler = None
