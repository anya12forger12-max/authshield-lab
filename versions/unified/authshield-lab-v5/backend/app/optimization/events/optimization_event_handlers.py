"""Optimization domain event handlers."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class OptimizationEventHandler:
    """Handles optimization domain events for logging, auditing, and side effects."""

    def __init__(self) -> None:
        self._handlers_registered = False

    def register_handlers(self, event_bus: Any) -> None:
        """Register all optimization event handlers on the provided event bus."""
        if self._handlers_registered:
            return

        from ..domain.events.optimization_events import (
            AIGenerationRequested,
            BenchmarkCompleted,
            CompatibilityReportGenerated,
            ContentReviewCompleted,
            FeatureFlagToggled,
            OptimizationDashboardGenerated,
            ReleaseWorkflowAdvanced,
            SustainabilityReportGenerated,
        )

        event_bus.subscribe_benchmark_completed(self._on_benchmark_completed)
        event_bus.subscribe_optimization_dashboard_generated(self._on_dashboard_generated)
        event_bus.subscribe_compatibility_report_generated(self._on_compatibility_report)
        event_bus.subscribe_feature_flag_toggled(self._on_feature_flag_toggled)
        event_bus.subscribe_ai_generation_requested(self._on_ai_generation_requested)
        event_bus.subscribe_content_review_completed(self._on_content_review_completed)
        event_bus.subscribe_sustainability_report_generated(self._on_sustainability_report)
        event_bus.subscribe_release_workflow_advanced(self._on_release_workflow_advanced)

        self._handlers_registered = True
        logger.info("optimization_event_handlers_registered")

    def _on_benchmark_completed(self, event: Any) -> None:
        logger.info(
            "Optimization Event: Benchmark completed",
            extra={
                "benchmark_id": getattr(event, "benchmark_id", ""),
                "benchmark_name": getattr(event, "benchmark_name", ""),
                "category": getattr(event, "category", ""),
                "value": getattr(event, "value", 0.0),
                "passed": getattr(event, "passed", False),
                "event_id": getattr(event, "event_id", ""),
            },
        )

    def _on_dashboard_generated(self, event: Any) -> None:
        logger.info(
            "Optimization Event: Dashboard generated",
            extra={
                "dashboard_id": getattr(event, "dashboard_id", ""),
                "overall_health": getattr(event, "overall_health", ""),
                "event_id": getattr(event, "event_id", ""),
            },
        )

    def _on_compatibility_report(self, event: Any) -> None:
        logger.info(
            "Optimization Event: Compatibility report generated",
            extra={
                "report_id": getattr(event, "report_id", ""),
                "platforms_checked": getattr(event, "platforms_checked", 0),
                "overall_status": getattr(event, "overall_status", ""),
                "event_id": getattr(event, "event_id", ""),
            },
        )

    def _on_feature_flag_toggled(self, event: Any) -> None:
        logger.info(
            "Optimization Event: Feature flag toggled",
            extra={
                "flag_id": getattr(event, "flag_id", ""),
                "flag_name": getattr(event, "flag_name", ""),
                "enabled": getattr(event, "enabled", False),
                "event_id": getattr(event, "event_id", ""),
            },
        )

    def _on_ai_generation_requested(self, event: Any) -> None:
        logger.info(
            "Optimization Event: AI generation requested",
            extra={
                "content_id": getattr(event, "content_id", ""),
                "ai_type": getattr(event, "ai_type", ""),
                "event_id": getattr(event, "event_id", ""),
            },
        )

    def _on_content_review_completed(self, event: Any) -> None:
        logger.info(
            "Optimization Event: Content review completed",
            extra={
                "audit_id": getattr(event, "audit_id", ""),
                "content_id": getattr(event, "content_id", ""),
                "approved": getattr(event, "approved", False),
                "event_id": getattr(event, "event_id", ""),
            },
        )

    def _on_sustainability_report(self, event: Any) -> None:
        logger.info(
            "Optimization Event: Sustainability report generated",
            extra={
                "overall_score": getattr(event, "overall_score", 0.0),
                "health_label": getattr(event, "health_label", ""),
                "event_id": getattr(event, "event_id", ""),
            },
        )

    def _on_release_workflow_advanced(self, event: Any) -> None:
        logger.info(
            "Optimization Event: Release workflow advanced",
            extra={
                "workflow_id": getattr(event, "workflow_id", ""),
                "release_id": getattr(event, "release_id", ""),
                "previous_stage": getattr(event, "previous_stage", ""),
                "current_stage": getattr(event, "current_stage", ""),
                "event_id": getattr(event, "event_id", ""),
            },
        )
