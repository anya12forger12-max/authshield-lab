"""Event handlers for Developer Platform domain events."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from app.developer.domain.events.developer_events import (
    ApiEndpointRegistered,
    ExtensionInstalled,
    ExtensionRemoved,
    ExtensionUpdated,
    PackageBuilt,
    ValidationCompleted,
    WorkflowCompleted,
    WorkflowStarted,
)

logger = logging.getLogger(__name__)


class DeveloperEventHandler:
    """Handles domain events emitted by developer platform services."""

    def __init__(self) -> None:
        self._event_log: list[dict] = []

    def _record(self, event_name: str, payload: dict) -> None:
        """Persist an event to the internal log."""
        self._event_log.append({
            "event": event_name,
            "payload": payload,
            "handled_at": datetime.now(timezone.utc).isoformat(),
        })

    def get_event_log(self, limit: int = 100) -> list[dict]:
        """Return the most recent events."""
        return self._event_log[-limit:]

    def clear_event_log(self) -> int:
        """Clear the event log. Returns the number of entries removed."""
        count = len(self._event_log)
        self._event_log.clear()
        return count

    # -- Extension events ----------------------------------------------------

    def on_extension_installed(self, event: ExtensionInstalled) -> None:
        """Handle an ExtensionInstalled event."""
        logger.info(
            "Extension '%s' v%s installed by %s",
            event.extension_name,
            event.version,
            event.payload.get("installed_by", "unknown"),
        )
        self._record(event.name, event.to_dict())

    def on_extension_removed(self, event: ExtensionRemoved) -> None:
        """Handle an ExtensionRemoved event."""
        logger.info(
            "Extension '%s' removed by %s",
            event.extension_name,
            event.payload.get("removed_by", "unknown"),
        )
        self._record(event.name, event.to_dict())

    def on_extension_updated(self, event: ExtensionUpdated) -> None:
        """Handle an ExtensionUpdated event."""
        logger.info(
            "Extension '%s' updated from v%s to v%s",
            event.payload.get("extension_name", ""),
            event.old_version,
            event.new_version,
        )
        self._record(event.name, event.to_dict())

    # -- Workflow events -----------------------------------------------------

    def on_workflow_started(self, event: WorkflowStarted) -> None:
        """Handle a WorkflowStarted event."""
        logger.info(
            "Workflow '%s' started (run %s)",
            event.payload.get("workflow_name", ""),
            event.run_id,
        )
        self._record(event.name, event.to_dict())

    def on_workflow_completed(self, event: WorkflowCompleted) -> None:
        """Handle a WorkflowCompleted event."""
        logger.info(
            "Workflow %s completed with status '%s' in %.2fs",
            event.workflow_id,
            event.status,
            event.payload.get("duration_seconds", 0),
        )
        self._record(event.name, event.to_dict())

    # -- Package events ------------------------------------------------------

    def on_package_built(self, event: PackageBuilt) -> None:
        """Handle a PackageBuilt event."""
        logger.info(
            "Package '%s' (manifest %s) build %s",
            event.payload.get("package_name", ""),
            event.manifest_id,
            event.payload.get("status", ""),
        )
        self._record(event.name, event.to_dict())

    # -- Validation events ---------------------------------------------------

    def on_validation_completed(self, event: ValidationCompleted) -> None:
        """Handle a ValidationCompleted event."""
        logger.info(
            "Validation report %s completed: status=%s, score=%.2f",
            event.report_id,
            event.overall_status,
            event.score,
        )
        self._record(event.name, event.to_dict())

    # -- API endpoint events -------------------------------------------------

    def on_api_endpoint_registered(self, event: ApiEndpointRegistered) -> None:
        """Handle an ApiEndpointRegistered event."""
        logger.info(
            "API endpoint registered: %s %s (category=%s)",
            event.method,
            event.path,
            event.payload.get("category", ""),
        )
        self._record(event.name, event.to_dict())
