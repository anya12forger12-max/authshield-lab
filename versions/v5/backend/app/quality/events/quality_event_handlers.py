from __future__ import annotations

import logging
from typing import Callable

from app.quality.domain.events.quality_events import (
    AuditCompleted,
    DiagnosticsCompleted,
    PerformanceBenchmarkCompleted,
    QualityCheckCompleted,
    ReleaseReadinessChecked,
    TestSuiteRun,
)

logger = logging.getLogger(__name__)


def handle_quality_check(event: QualityCheckCompleted) -> None:
    logger.info(
        "Quality check completed: category=%s score=%.2f passed=%s",
        event.category,
        event.score,
        event.passed,
    )


def handle_test_suite_run(event: TestSuiteRun) -> None:
    logger.info(
        "Test suite '%s' completed: %d total, %d passed, %d failed, %d skipped",
        event.suite_name,
        event.total,
        event.passed,
        event.failed,
        event.skipped,
    )


def handle_audit_completed(event: AuditCompleted) -> None:
    logger.info(
        "Audit '%s' (%s): score=%.2f violations=%d",
        event.audit_name,
        event.standard,
        event.overall_score,
        event.violations,
    )


def handle_performance_benchmark(event: PerformanceBenchmarkCompleted) -> None:
    logger.info(
        "Benchmark '%s': value=%.2f threshold=%.2f passed=%s",
        event.benchmark_name,
        event.value,
        event.threshold,
        event.passed,
    )


def handle_release_readiness(event: ReleaseReadinessChecked) -> None:
    logger.info(
        "Release %s readiness: overall_ready=%s",
        event.release_id,
        event.overall_ready,
    )


def handle_diagnostics_completed(event: DiagnosticsCompleted) -> None:
    logger.info(
        "Diagnostics '%s': status=%s passed=%d failed=%d warnings=%d",
        event.bundle_name,
        event.overall_status,
        event.passed,
        event.failed,
        event.warnings,
    )


class EventBus:
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
                logger.exception("Handler %s failed for event %s", handler.__name__, event_type)


_default_bus = EventBus()

_default_bus.register("QualityCheckCompleted", handle_quality_check)
_default_bus.register("TestSuiteRun", handle_test_suite_run)
_default_bus.register("AuditCompleted", handle_audit_completed)
_default_bus.register("PerformanceBenchmarkCompleted", handle_performance_benchmark)
_default_bus.register("ReleaseReadinessChecked", handle_release_readiness)
_default_bus.register("DiagnosticsCompleted", handle_diagnostics_completed)


def get_event_bus() -> EventBus:
    return _default_bus
