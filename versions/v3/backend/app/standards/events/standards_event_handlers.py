"""Domain event handlers for the Standards module."""

from __future__ import annotations

import logging
from typing import Callable

from app.standards.domain.events.standards_events import (
    BulkMappingCompleted,
    EvidenceCollected,
    FrameworkCreated,
    FrameworkUpdated,
    MappingCreated,
    QualityDashboardGenerated,
    ReadinessReviewAdvanced,
)

logger = logging.getLogger(__name__)


def handle_framework_created(event: FrameworkCreated) -> None:
    logger.info(
        "Framework created: id=%s name=%s version=%s",
        event.framework_id,
        event.name,
        event.version,
    )


def handle_framework_updated(event: FrameworkUpdated) -> None:
    logger.info(
        "Framework updated: id=%s changes=%s",
        event.framework_id,
        event.changes,
    )


def handle_mapping_created(event: MappingCreated) -> None:
    logger.info(
        "Mapping created: id=%s source=%s target=%s coverage=%s",
        event.mapping_id,
        event.source_id,
        event.target_id,
        event.coverage_level,
    )


def handle_bulk_mapping_completed(event: BulkMappingCompleted) -> None:
    logger.info(
        "Bulk mapping completed: total=%d mapped=%d unmapped=%d gaps=%d",
        event.total,
        event.mapped,
        event.unmapped,
        len(event.gaps),
    )


def handle_readiness_review_advanced(event: ReadinessReviewAdvanced) -> None:
    logger.info(
        "Readiness review advanced: review_id=%s %s -> %s by %s",
        event.review_id,
        event.old_stage,
        event.new_stage,
        event.actor,
    )


def handle_evidence_collected(event: EvidenceCollected) -> None:
    logger.info(
        "Evidence collected: collection=%s item=%s type=%s",
        event.collection_id,
        event.evidence_item_id,
        event.evidence_type,
    )


def handle_quality_dashboard_generated(event: QualityDashboardGenerated) -> None:
    logger.info(
        "Quality dashboard generated: id=%s overall=%.2f status=%s",
        event.dashboard_id,
        event.overall_score,
        event.health_status,
    )


class EventBus:
    """Simple in-process event bus for dispatching standards events."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[Callable]] = {}

    def register(self, event_type: str, handler: Callable) -> None:
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def dispatch(self, event: object) -> None:
        event_type = type(event).__name__
        handlers = self._handlers.get(event_type, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception:
                logger.exception(
                    "Handler %s failed for event %s",
                    handler.__name__,
                    event_type,
                )


_default_bus = EventBus()

_default_bus.register("FrameworkCreated", handle_framework_created)
_default_bus.register("FrameworkUpdated", handle_framework_updated)
_default_bus.register("MappingCreated", handle_mapping_created)
_default_bus.register("BulkMappingCompleted", handle_bulk_mapping_completed)
_default_bus.register("ReadinessReviewAdvanced", handle_readiness_review_advanced)
_default_bus.register("EvidenceCollected", handle_evidence_collected)
_default_bus.register("QualityDashboardGenerated", handle_quality_dashboard_generated)


def get_event_bus() -> EventBus:
    return _default_bus
