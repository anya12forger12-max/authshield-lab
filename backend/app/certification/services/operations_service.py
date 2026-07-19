"""Operations service: platform health, module inventory, ecosystem dashboard."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from ..domain.entities.operations import (
    EcosystemDashboard,
    ModuleInventory,
    PackageHealth,
    PlatformHealth,
    ServiceHealthStatus,
    ServiceStatus,
)
from ..domain.interfaces import (
    EcosystemDashboardRepository,
    ModuleInventoryRepository,
    PackageHealthRepository,
    PlatformHealthRepository,
    ServiceStatusRepository,
)


class OperationsService:
    """Manages platform health monitoring, module inventory, and ecosystem dashboards."""

    def __init__(
        self,
        service_repo: ServiceStatusRepository,
        health_repo: PlatformHealthRepository,
        module_repo: ModuleInventoryRepository,
        package_repo: PackageHealthRepository,
        dashboard_repo: EcosystemDashboardRepository,
    ) -> None:
        self._service_repo = service_repo
        self._health_repo = health_repo
        self._module_repo = module_repo
        self._package_repo = package_repo
        self._dashboard_repo = dashboard_repo

    async def register_service(
        self,
        name: str,
        status: ServiceHealthStatus = ServiceHealthStatus.HEALTHY,
        response_time_ms: float = 0.0,
        error_rate: float = 0.0,
    ) -> ServiceStatus:
        """Register or update a service in the inventory."""
        existing = self._service_repo.find_by_name(name)
        if existing is not None:
            existing.status = status
            existing.last_check = datetime.now(timezone.utc)
            existing.response_time_ms = response_time_ms
            existing.error_rate = error_rate
            return self._service_repo.save(existing)
        svc = ServiceStatus(
            name=name,
            status=status,
            response_time_ms=response_time_ms,
            error_rate=error_rate,
        )
        return self._service_repo.save(svc)

    async def get_service_status(self, name: str) -> Optional[ServiceStatus]:
        """Retrieve the status for a single service."""
        return self._service_repo.find_by_name(name)

    async def list_services(self) -> list[ServiceStatus]:
        """Return all registered services."""
        return self._service_repo.find_all()

    async def generate_platform_health(self, uptime_hours: float = 0.0) -> PlatformHealth:
        """Build a new PlatformHealth snapshot from current service statuses."""
        services = self._service_repo.find_all()
        health = PlatformHealth(services=services, uptime_hours=uptime_hours)
        health.recalculate_overall()
        return self._health_repo.save(health)

    async def get_latest_platform_health(self) -> Optional[PlatformHealth]:
        """Return the most recent PlatformHealth snapshot."""
        return self._health_repo.find_latest()

    async def register_module(
        self,
        name: str,
        version: str = "0.1.0",
        status: str = "active",
        enabled: bool = True,
        dependencies: list[str] | None = None,
    ) -> ModuleInventory:
        """Register or update a module in the inventory."""
        existing = self._module_repo.find_by_name(name)
        if existing is not None:
            existing.version = version
            existing.status = status
            existing.enabled = enabled
            existing.dependencies = dependencies or []
            existing.last_updated = datetime.now(timezone.utc)
            return self._module_repo.save(existing)
        mod = ModuleInventory(
            name=name,
            version=version,
            status=status,
            enabled=enabled,
            dependencies=dependencies or [],
        )
        return self._module_repo.save(mod)

    async def get_module(self, name: str) -> Optional[ModuleInventory]:
        """Retrieve a module by name."""
        return self._module_repo.find_by_name(name)

    async def list_modules(self) -> list[ModuleInventory]:
        """Return all registered modules."""
        return self._module_repo.find_all()

    async def remove_module(self, module_id: str) -> bool:
        """Remove a module from the inventory."""
        return self._module_repo.delete(module_id)

    async def register_package(
        self,
        name: str,
        version: str = "",
        integrity: bool = True,
        compatibility: bool = True,
        health_score: float = 100.0,
    ) -> PackageHealth:
        """Register or update package health."""
        existing = self._package_repo.find_by_name(name)
        if existing is not None:
            existing.version = version
            existing.integrity = integrity
            existing.compatibility = compatibility
            existing.health_score = health_score
            existing.last_validated = datetime.now(timezone.utc)
            return self._package_repo.save(existing)
        pkg = PackageHealth(
            name=name,
            version=version,
            integrity=integrity,
            compatibility=compatibility,
            health_score=health_score,
        )
        return self._package_repo.save(pkg)

    async def list_packages(self) -> list[PackageHealth]:
        """Return all tracked packages."""
        return self._package_repo.find_all()

    async def generate_ecosystem_dashboard(
        self,
        doc_status: float = 0.0,
        a11y_score: float = 0.0,
        security_score: float = 0.0,
        performance_score: float = 0.0,
    ) -> EcosystemDashboard:
        """Assemble a full ecosystem dashboard from current data."""
        services = self._service_repo.find_all()
        health = PlatformHealth(services=services)
        health.recalculate_overall()

        modules = self._module_repo.find_all()
        packages = self._package_repo.find_all()

        dashboard = EcosystemDashboard(
            platform_health=health,
            module_inventory=modules,
            package_health=packages,
            doc_status=doc_status,
            a11y_score=a11y_score,
            security_score=security_score,
            performance_score=performance_score,
        )
        return self._dashboard_repo.save(dashboard)

    async def get_latest_dashboard(self) -> Optional[EcosystemDashboard]:
        """Return the most recent ecosystem dashboard."""
        return self._dashboard_repo.find_latest()
