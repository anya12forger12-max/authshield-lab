"""Developer tools service: API browser, schema explorer, config inspector, log viewer, performance dashboard."""

from __future__ import annotations

import time
from datetime import datetime, timezone


class DeveloperToolsService:
    """Provides developer utility tools for browsing APIs, inspecting schemas, configuration, logs, and performance."""

    def __init__(self) -> None:
        self._api_registry: list[dict] = []
        self._schema_store: dict[str, dict] = {}
        self._config_store: dict[str, object] = {}
        self._log_buffer: list[dict] = []
        self._metrics: list[dict] = []
        self._max_log_entries: int = 1000

    # -- API Browser ---------------------------------------------------------

    def register_api_route(
        self,
        path: str,
        method: str,
        handler_name: str,
        tags: list[str] | None = None,
        description: str = "",
    ) -> dict:
        """Register an API route in the browser."""
        route = {
            "path": path,
            "method": method.upper(),
            "handler_name": handler_name,
            "tags": tags if tags is not None else [],
            "description": description,
            "registered_at": datetime.now(timezone.utc).isoformat(),
        }
        self._api_registry.append(route)
        return route

    def browse_api(
        self,
        method: str | None = None,
        tag: str | None = None,
        search: str | None = None,
    ) -> list[dict]:
        """Browse registered API routes with optional filters."""
        results = list(self._api_registry)
        if method is not None:
            results = [r for r in results if r["method"] == method.upper()]
        if tag is not None:
            results = [r for r in results if tag in r["tags"]]
        if search is not None:
            q = search.lower()
            results = [
                r for r in results
                if q in r["path"].lower() or q in r["description"].lower() or q in r["handler_name"].lower()
            ]
        return results

    def get_api_route(self, path: str, method: str) -> dict | None:
        """Look up a specific API route."""
        method_upper = method.upper()
        for route in self._api_registry:
            if route["path"] == path and route["method"] == method_upper:
                return route
        return None

    def list_api_tags(self) -> list[str]:
        """Return all unique tags across registered routes."""
        tags: set[str] = set()
        for route in self._api_registry:
            tags.update(route["tags"])
        return sorted(tags)

    def get_api_stats(self) -> dict:
        """Return summary statistics for the API registry."""
        total = len(self._api_registry)
        methods: dict[str, int] = {}
        for route in self._api_registry:
            methods[route["method"]] = methods.get(route["method"], 0) + 1
        return {
            "total_routes": total,
            "methods": methods,
            "tags": self.list_api_tags(),
        }

    # -- Schema Explorer -----------------------------------------------------

    def register_schema(self, name: str, schema: dict) -> dict:
        """Register a schema definition."""
        entry = {
            "name": name,
            "schema": dict(schema),
            "registered_at": datetime.now(timezone.utc).isoformat(),
        }
        self._schema_store[name] = entry
        return entry

    def get_schema(self, name: str) -> dict | None:
        """Retrieve a schema by name."""
        return self._schema_store.get(name)

    def list_schemas(self) -> list[dict]:
        """Return all registered schemas."""
        return list(self._schema_store.values())

    def search_schemas(self, query: str) -> list[dict]:
        """Search schemas by name."""
        q = query.lower()
        return [s for s in self._schema_store.values() if q in s["name"].lower()]

    def update_schema(self, name: str, schema: dict) -> dict | None:
        """Update a registered schema."""
        entry = self._schema_store.get(name)
        if entry is None:
            return None
        entry["schema"] = dict(schema)
        entry["updated_at"] = datetime.now(timezone.utc).isoformat()
        return entry

    def delete_schema(self, name: str) -> bool:
        """Remove a schema."""
        if name in self._schema_store:
            del self._schema_store[name]
            return True
        return False

    # -- Config Inspector ----------------------------------------------------

    def set_config(self, key: str, value: object) -> None:
        """Set a configuration value."""
        self._config_store[key] = value

    def get_config(self, key: str, default: object = None) -> object:
        """Retrieve a configuration value."""
        return self._config_store.get(key, default)

    def list_config(self) -> dict:
        """Return all configuration values."""
        return dict(self._config_store)

    def search_config(self, query: str) -> dict:
        """Search configuration keys by substring."""
        q = query.lower()
        return {k: v for k, v in self._config_store.items() if q in k.lower()}

    def delete_config(self, key: str) -> bool:
        """Remove a configuration value."""
        if key in self._config_store:
            del self._config_store[key]
            return True
        return False

    def export_config(self) -> dict:
        """Export the entire configuration store."""
        return dict(self._config_store)

    # -- Log Viewer ----------------------------------------------------------

    def append_log(self, level: str, message: str, source: str = "system") -> dict:
        """Append a log entry to the buffer."""
        entry = {
            "level": level.upper(),
            "message": message,
            "source": source,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._log_buffer.append(entry)
        if len(self._log_buffer) > self._max_log_entries:
            self._log_buffer = self._log_buffer[-self._max_log_entries:]
        return entry

    def get_logs(
        self,
        level: str | None = None,
        source: str | None = None,
        limit: int = 100,
    ) -> list[dict]:
        """Retrieve log entries with optional filtering."""
        logs = list(self._log_buffer)
        if level is not None:
            logs = [l for l in logs if l["level"] == level.upper()]
        if source is not None:
            logs = [l for l in logs if l["source"] == source]
        return logs[-limit:]

    def clear_logs(self) -> int:
        """Clear all log entries. Returns the number of entries removed."""
        count = len(self._log_buffer)
        self._log_buffer.clear()
        return count

    def get_log_stats(self) -> dict:
        """Return summary statistics for the log buffer."""
        levels: dict[str, int] = {}
        sources: dict[str, int] = {}
        for entry in self._log_buffer:
            levels[entry["level"]] = levels.get(entry["level"], 0) + 1
            sources[entry["source"]] = sources.get(entry["source"], 0) + 1
        return {
            "total_entries": len(self._log_buffer),
            "by_level": levels,
            "by_source": sources,
        }

    # -- Performance Dashboard -----------------------------------------------

    def record_metric(
        self,
        name: str,
        value: float,
        unit: str = "",
        tags: dict | None = None,
    ) -> dict:
        """Record a performance metric."""
        entry = {
            "name": name,
            "value": value,
            "unit": unit,
            "tags": tags if tags is not None else {},
            "recorded_at": datetime.now(timezone.utc).isoformat(),
        }
        self._metrics.append(entry)
        return entry

    def get_metrics(self, name: str | None = None, limit: int = 100) -> list[dict]:
        """Retrieve metrics, optionally filtered by name."""
        if name is None:
            return list(self._metrics[-limit:])
        return [m for m in self._metrics if m["name"] == name][-limit:]

    def get_metric_summary(self, name: str) -> dict:
        """Compute summary statistics for a named metric."""
        values = [m["value"] for m in self._metrics if m["name"] == name]
        if not values:
            return {"name": name, "count": 0, "min": 0, "max": 0, "avg": 0}
        return {
            "name": name,
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": round(sum(values) / len(values), 4),
        }

    def clear_metrics(self) -> int:
        """Clear all metrics. Returns the number of entries removed."""
        count = len(self._metrics)
        self._metrics.clear()
        return count

    def get_dashboard(self) -> dict:
        """Return a consolidated dashboard view."""
        return {
            "api_stats": self.get_api_stats(),
            "schema_count": len(self._schema_store),
            "config_count": len(self._config_store),
            "log_stats": self.get_log_stats(),
            "metric_count": len(self._metrics),
        }
