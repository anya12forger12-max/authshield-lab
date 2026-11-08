from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class ApplicationMetric:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    value: float = 0.0
    unit: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tags: dict[str, str] = field(default_factory=dict)


@dataclass
class MemoryUsage:
    used_mb: float = 0.0
    available_mb: float = 0.0
    percentage: float = 0.0
    peak_mb: float = 0.0


@dataclass
class CpuUsage:
    percentage: float = 0.0
    cores: int = 1
    load_average: list[float] = field(default_factory=list)


@dataclass
class DatabaseStats:
    total_size_mb: float = 0.0
    table_count: int = 0
    record_counts: dict[str, int] = field(default_factory=dict)
    query_time_avg_ms: float = 0.0


@dataclass
class CacheStats:
    hits: int = 0
    misses: int = 0
    hit_rate: float = 0.0
    size: int = 0
    max_size: int = 0


@dataclass
class PluginStatus:
    name: str = ""
    enabled: bool = False
    healthy: bool = False
    last_error: str = ""


@dataclass
class ObservabilitySnapshot:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    memory: MemoryUsage | None = None
    cpu: CpuUsage | None = None
    database: DatabaseStats | None = None
    cache: CacheStats | None = None
    plugins: list[PluginStatus] = field(default_factory=list)
    startup_time_ms: float = 0.0
    active_sessions: int = 0
    captured_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
