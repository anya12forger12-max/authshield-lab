"""Extended observability service — traces, timelines, storage analytics."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Optional

from ..domain.entities.optimization import DiagnosticTrace, TraceSpan
from ..domain.interfaces.optimization_interfaces import IDiagnosticTraceRepository

logger = logging.getLogger(__name__)


class ObservabilityExtendedService:
    """Manages event timelines, diagnostic traces, background tasks, and storage analytics."""

    def __init__(self, trace_repo: IDiagnosticTraceRepository) -> None:
        self._trace_repo = trace_repo
        self._event_timelines: dict[str, list[dict[str, Any]]] = {}
        self._background_tasks: dict[str, dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # Event Timelines
    # ------------------------------------------------------------------

    def record_event(self, timeline_id: str, event_data: dict[str, Any]) -> dict[str, Any]:
        """Record an event on a named timeline."""
        import uuid as _uuid
        event_entry = {
            "event_id": event_data.get("event_id") or str(_uuid.uuid4()),
            "event_type": event_data.get("event_type", ""),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": event_data.get("details", {}),
            "source_module": event_data.get("source_module", ""),
        }
        self._event_timelines.setdefault(timeline_id, []).append(event_entry)
        logger.info("event_recorded", extra={"timeline_id": timeline_id, "event_type": event_entry["event_type"]})
        return event_entry

    def get_timeline(self, timeline_id: str, limit: int = 100) -> dict[str, Any]:
        """Return events from a timeline."""
        events = self._event_timelines.get(timeline_id, [])
        recent = events[-limit:]
        return {
            "timeline_id": timeline_id,
            "events": recent,
            "total_count": len(events),
        }

    def list_timelines(self) -> list[str]:
        """Return all known timeline IDs."""
        return list(self._event_timelines.keys())

    def clear_timeline(self, timeline_id: str) -> bool:
        """Clear all events from a timeline."""
        if timeline_id in self._event_timelines:
            self._event_timelines[timeline_id] = []
            return True
        return False

    def search_events(
        self, timeline_id: str, event_type: Optional[str] = None, keyword: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Search events on a timeline by type or keyword."""
        events = self._event_timelines.get(timeline_id, [])
        results = events
        if event_type:
            results = [e for e in results if e.get("event_type") == event_type]
        if keyword:
            kw = keyword.lower()
            results = [
                e for e in results
                if kw in str(e.get("details", {})).lower()
                or kw in e.get("event_type", "").lower()
            ]
        return results

    # ------------------------------------------------------------------
    # Diagnostic Traces
    # ------------------------------------------------------------------

    def create_trace(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new diagnostic trace."""
        trace = DiagnosticTrace(
            name=data.get("name", ""),
        )
        for span_data in data.get("spans", []):
            span = TraceSpan(
                name=span_data.get("name", ""),
                start_ms=float(span_data.get("start_ms", 0.0)),
                end_ms=float(span_data.get("end_ms", 0.0)),
                module=span_data.get("module", ""),
                details=span_data.get("details", {}),
            )
            trace.add_span(span)
        result = self._trace_repo.create(trace.to_dict())
        logger.info("trace_created", extra={"trace_id": result["id"], "name": trace.name})
        return result

    def get_trace(self, trace_id: str) -> Optional[dict[str, Any]]:
        return self._trace_repo.get_by_id(trace_id)

    def list_traces(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._trace_repo.get_all(limit=limit)

    def delete_trace(self, trace_id: str) -> bool:
        return self._trace_repo.delete(trace_id)

    def add_span_to_trace(self, trace_id: str, span_data: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Add a span to an existing trace."""
        trace_dict = self._trace_repo.get_by_id(trace_id)
        if not trace_dict:
            return None
        spans = trace_dict.get("spans", [])
        spans.append({
            "name": span_data.get("name", ""),
            "start_ms": float(span_data.get("start_ms", 0.0)),
            "end_ms": float(span_data.get("end_ms", 0.0)),
            "module": span_data.get("module", ""),
            "details": span_data.get("details", {}),
            "duration_ms": round(
                float(span_data.get("end_ms", 0.0)) - float(span_data.get("start_ms", 0.0)), 3
            ),
        })
        all_starts = [s.get("start_ms", 0.0) for s in spans]
        all_ends = [s.get("end_ms", 0.0) for s in spans]
        total_ms = max(0.0, max(all_ends) - min(all_starts)) if spans else 0.0
        return self._trace_repo.update(trace_id, {
            "spans_json": str(spans),
            "total_duration_ms": total_ms,
        })

    def traces_by_module(self, module: str) -> list[dict[str, Any]]:
        """Return all traces that contain spans from the given module."""
        all_traces = self._trace_repo.get_all(limit=200)
        matched: list[dict[str, Any]] = []
        for trace in all_traces:
            spans = trace.get("spans", [])
            if any(s.get("module") == module for s in spans):
                matched.append(trace)
        return matched

    # ------------------------------------------------------------------
    # Background Tasks
    # ------------------------------------------------------------------

    def register_task(self, task_id: str, name: str, description: str = "") -> dict[str, Any]:
        """Register a background task."""
        task = {
            "task_id": task_id,
            "name": name,
            "description": description,
            "status": "registered",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": None,
        }
        self._background_tasks[task_id] = task
        return task

    def start_task(self, task_id: str) -> Optional[dict[str, Any]]:
        """Mark a background task as started."""
        task = self._background_tasks.get(task_id)
        if not task:
            return None
        task["status"] = "running"
        return task

    def complete_task(self, task_id: str) -> Optional[dict[str, Any]]:
        """Mark a background task as completed."""
        task = self._background_tasks.get(task_id)
        if not task:
            return None
        task["status"] = "completed"
        task["completed_at"] = datetime.now(timezone.utc).isoformat()
        return task

    def fail_task(self, task_id: str, error: str = "") -> Optional[dict[str, Any]]:
        """Mark a background task as failed."""
        task = self._background_tasks.get(task_id)
        if not task:
            return None
        task["status"] = "failed"
        task["error"] = error
        return task

    def get_task(self, task_id: str) -> Optional[dict[str, Any]]:
        return self._background_tasks.get(task_id)

    def list_tasks(self, status: Optional[str] = None) -> list[dict[str, Any]]:
        tasks = list(self._background_tasks.values())
        if status:
            tasks = [t for t in tasks if t.get("status") == status]
        return tasks

    # ------------------------------------------------------------------
    # Storage Analytics
    # ------------------------------------------------------------------

    def analyze_storage(self, data: dict[str, Any]) -> dict[str, Any]:
        """Analyze storage usage from raw data."""
        total = float(data.get("total_mb", 0.0))
        used = float(data.get("used_mb", 0.0))
        by_module = data.get("by_module", {})
        backups = float(data.get("backup_mb", 0.0))
        archives = float(data.get("archive_mb", 0.0))

        free = max(0.0, total - used) if total > 0 else 0.0
        usage_pct = (used / total * 100.0) if total > 0 else 0.0

        top_module = ""
        top_usage = 0.0
        for mod_name, mod_usage in by_module.items():
            if float(mod_usage) > top_usage:
                top_usage = float(mod_usage)
                top_module = mod_name

        recommendations: list[str] = []
        if usage_pct > 80:
            recommendations.append("Storage usage is above 80% — consider cleanup or expansion.")
        if backups > total * 0.2:
            recommendations.append("Backups consume more than 20% of storage — review backup retention policy.")
        if archives > total * 0.3:
            recommendations.append("Archives exceed 30% of storage — consider moving cold data offsite.")

        return {
            "total_mb": total,
            "used_mb": used,
            "free_mb": round(free, 2),
            "usage_percentage": round(usage_pct, 2),
            "by_module": dict(by_module),
            "backup_mb": backups,
            "archive_mb": archives,
            "top_module": top_module,
            "top_module_usage_mb": top_usage,
            "recommendations": recommendations,
        }
