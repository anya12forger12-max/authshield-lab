"""Event handlers for Certification module domain events."""

from __future__ import annotations

import logging
from typing import Any, Callable

from ..domain.events.certification_events import (
    CertificationCompleted,
    CertificationFailed,
    PlatformValidated,
    RecoveryTested,
    ReleaseEngineered,
    SustainabilityReportGenerated,
    ValidationCompleted,
)

logger = logging.getLogger(__name__)


def handle_certification_completed(event: CertificationCompleted) -> None:
    """Log successful certification completion."""
    logger.info(
        "Certification completed: id=%s type=%s name=%s approved_by=%s",
        event.certification_id,
        event.cert_type,
        event.name,
        event.approved_by,
    )


def handle_certification_failed(event: CertificationFailed) -> None:
    """Log certification failure."""
    logger.warning(
        "Certification failed: id=%s type=%s name=%s reason=%s",
        event.certification_id,
        event.cert_type,
        event.name,
        event.reason,
    )


def handle_platform_validated(event: PlatformValidated) -> None:
    """Log platform validation completion."""
    logger.info(
        "Platform validated: report_id=%s compliance=%.1f%% passed=%d failed=%d",
        event.report_id,
        event.overall_compliance,
        event.subsystems_passed,
        event.subsystems_failed,
    )


def handle_release_engineered(event: ReleaseEngineered) -> None:
    """Log release engineering completion."""
    logger.info(
        "Release engineered: id=%s version=%s code_name=%s status=%s",
        event.release_id,
        event.version,
        event.code_name,
        event.status,
    )


def handle_recovery_tested(event: RecoveryTested) -> None:
    """Log disaster recovery test completion."""
    logger.info(
        "Recovery tested: test_id=%s backup_id=%s status=%s integrity=%s duration=%dms",
        event.test_id,
        event.backup_id,
        event.status,
        event.data_integrity,
        event.duration_ms,
    )


def handle_sustainability_report_generated(event: SustainabilityReportGenerated) -> None:
    """Log sustainability report generation."""
    logger.info(
        "Sustainability report: score=%.1f debt=%.1fh deprecated_deps=%d",
        event.maintenance_score,
        event.technical_debt_hours,
        event.deprecated_deps,
    )


def handle_validation_completed(event: ValidationCompleted) -> None:
    """Log subsystem validation completion."""
    logger.info(
        "Validation completed: subsystem=%s passed=%d failed=%d compliance=%.1f%%",
        event.subsystem,
        event.checks_passed,
        event.checks_failed,
        event.compliance_pct,
    )


class EventBus:
    """Lightweight synchronous event bus for certification domain events."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[Callable[..., None]]] = {}

    def register(self, event_type: str, handler: Callable[..., None]) -> None:
        """Subscribe *handler* to events of *event_type*."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def dispatch(self, event: Any) -> None:
        """Dispatch *event* to all registered handlers by class name."""
        event_type = type(event).__name__
        handlers = self._handlers.get(event_type, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception:
                logger.exception(
                    "Handler %s failed for event %s", handler.__qualname__, event_type
                )


_default_bus = EventBus()
_default_bus.register("CertificationCompleted", handle_certification_completed)
_default_bus.register("CertificationFailed", handle_certification_failed)
_default_bus.register("PlatformValidated", handle_platform_validated)
_default_bus.register("ReleaseEngineered", handle_release_engineered)
_default_bus.register("RecoveryTested", handle_recovery_tested)
_default_bus.register("SustainabilityReportGenerated", handle_sustainability_report_generated)
_default_bus.register("ValidationCompleted", handle_validation_completed)


def get_event_bus() -> EventBus:
    """Return the module-level event bus singleton."""
    return _default_bus
