"""Operations domain entities: service health, platform status, ecosystem dashboard."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class ServiceHealthStatus(str, Enum):
    """Possible health states for a single service."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class ServiceStatus:
    """Snapshot of a single internal service's health."""

    name: str = ""
    status: ServiceHealthStatus = ServiceHealthStatus.HEALTHY
    last_check: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    response_time_ms: float = 0.0
    error_rate: float = 0.0

    def is_operational(self) -> bool:
        """Return ``True`` when the service is healthy."""
        return self.status == ServiceHealthStatus.HEALTHY

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "name": self.name,
            "status": self.status.value,
            "last_check": self.last_check.isoformat(),
            "response_time_ms": self.response_time_ms,
            "error_rate": self.error_rate,
        }


@dataclass
class PlatformHealth:
    """Aggregated health picture across every registered service."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    services: list[ServiceStatus] = field(default_factory=list)
    overall_status: str = "healthy"
    uptime_hours: float = 0.0
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def recalculate_overall(self) -> None:
        """Derive ``overall_status`` from the worst individual service status."""
        if not self.services:
            self.overall_status = "healthy"
            return
        statuses = [s.status for s in self.services]
        if ServiceHealthStatus.UNHEALTHY in statuses:
            self.overall_status = "unhealthy"
        elif ServiceHealthStatus.DEGRADED in statuses:
            self.overall_status = "degraded"
        else:
            self.overall_status = "healthy"

    def unhealthy_count(self) -> int:
        """Return the number of services that are not healthy."""
        return sum(1 for s in self.services if s.status != ServiceHealthStatus.HEALTHY)

    def average_response_time_ms(self) -> float:
        """Mean response time across all services."""
        if not self.services:
            return 0.0
        return sum(s.response_time_ms for s in self.services) / len(self.services)

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "id": self.id,
            "services": [s.to_dict() for s in self.services],
            "overall_status": self.overall_status,
            "uptime_hours": self.uptime_hours,
            "generated_at": self.generated_at.isoformat(),
        }


@dataclass
class ModuleInventory:
    """Record of a single platform module and its metadata."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    version: str = "0.1.0"
    status: str = "active"
    enabled: bool = True
    dependencies: list[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def has_dependency(self, dep_name: str) -> bool:
        """Check whether *dep_name* is listed as a dependency."""
        return dep_name in self.dependencies

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "status": self.status,
            "enabled": self.enabled,
            "dependencies": list(self.dependencies),
            "last_updated": self.last_updated.isoformat(),
        }


@dataclass
class PackageHealth:
    """Integrity / compatibility assessment for an installed package."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    version: str = ""
    integrity: bool = True
    compatibility: bool = True
    health_score: float = 100.0
    last_validated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def is_healthy(self) -> bool:
        """Return ``True`` when integrity and compatibility both pass."""
        return self.integrity and self.compatibility

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "integrity": self.integrity,
            "compatibility": self.compatibility,
            "health_score": self.health_score,
            "last_validated": self.last_validated.isoformat(),
        }


@dataclass
class EcosystemDashboard:
    """Top-level dashboard aggregating all operational health indicators."""

    platform_health: PlatformHealth = field(default_factory=PlatformHealth)
    module_inventory: list[ModuleInventory] = field(default_factory=list)
    extension_status: list[dict] = field(default_factory=list)
    package_health: list[PackageHealth] = field(default_factory=list)
    doc_status: float = 0.0
    a11y_score: float = 0.0
    security_score: float = 0.0
    performance_score: float = 0.0
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def overall_score(self) -> float:
        """Compute a weighted average across the four numeric scores."""
        scores = [self.doc_status, self.a11y_score, self.security_score, self.performance_score]
        valid = [s for s in scores if s > 0]
        return sum(valid) / len(valid) if valid else 0.0

    def enabled_modules(self) -> list[ModuleInventory]:
        """Return only modules whose ``enabled`` flag is ``True``."""
        return [m for m in self.module_inventory if m.enabled]

    def unhealthy_packages(self) -> list[PackageHealth]:
        """Return packages that failed integrity or compatibility checks."""
        return [p for p in self.package_health if not p.is_healthy()]

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "platform_health": self.platform_health.to_dict(),
            "module_inventory": [m.to_dict() for m in self.module_inventory],
            "extension_status": list(self.extension_status),
            "package_health": [p.to_dict() for p in self.package_health],
            "doc_status": self.doc_status,
            "a11y_score": self.a11y_score,
            "security_score": self.security_score,
            "performance_score": self.performance_score,
            "overall_score": self.overall_score(),
            "generated_at": self.generated_at.isoformat(),
        }
