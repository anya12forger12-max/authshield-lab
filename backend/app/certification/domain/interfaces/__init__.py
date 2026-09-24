"""Abstract repository interfaces for the Certification / Operations module."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from ..entities.certification_center import (
    CertificationRequirement,
    PlatformCertification,
    PlatformCertificationReport,
)
from ..entities.disaster_recovery import (
    ArchiveRecovery,
    BackupValidation,
    RecoveryReadinessReport,
    RestoreTest,
)
from ..entities.operations import (
    EcosystemDashboard,
    ModuleInventory,
    PackageHealth,
    PlatformHealth,
    ServiceStatus,
)
from ..entities.platform_validation import (
    FinalAcceptanceTest,
    PlatformValidationReport,
    SubsystemValidation,
    ValidationCheck,
)
from ..entities.release_engineering import (
    PackagingResult,
    RegressionResult,
    ReleaseHistoryEntry,
    ReleasePlan,
    ReleaseValidation,
)
from ..entities.sustainability import (
    DependencyLifecycle,
    DocumentationFreshness,
    MaintenanceRoadmap,
    ModuleOwnership,
    SustainabilityDashboard,
)

# ── Operations ──────────────────────────────────────────────────────


class ServiceStatusRepository(ABC):
    @abstractmethod
    def save(self, status: ServiceStatus) -> ServiceStatus: ...

    @abstractmethod
    def find_by_name(self, name: str) -> ServiceStatus | None: ...

    @abstractmethod
    def find_all(self) -> list[ServiceStatus]: ...


class PlatformHealthRepository(ABC):
    @abstractmethod
    def save(self, health: PlatformHealth) -> PlatformHealth: ...

    @abstractmethod
    def find_latest(self) -> PlatformHealth | None: ...

    @abstractmethod
    def find_all(self) -> list[PlatformHealth]: ...


class ModuleInventoryRepository(ABC):
    @abstractmethod
    def save(self, module: ModuleInventory) -> ModuleInventory: ...

    @abstractmethod
    def find_by_name(self, name: str) -> ModuleInventory | None: ...

    @abstractmethod
    def find_all(self) -> list[ModuleInventory]: ...

    @abstractmethod
    def delete(self, module_id: str) -> bool: ...


class PackageHealthRepository(ABC):
    @abstractmethod
    def save(self, pkg: PackageHealth) -> PackageHealth: ...

    @abstractmethod
    def find_by_name(self, name: str) -> PackageHealth | None: ...

    @abstractmethod
    def find_all(self) -> list[PackageHealth]: ...


class EcosystemDashboardRepository(ABC):
    @abstractmethod
    def save(self, dashboard: EcosystemDashboard) -> EcosystemDashboard: ...

    @abstractmethod
    def find_latest(self) -> EcosystemDashboard | None: ...


# ── Certification Center ────────────────────────────────────────────


class PlatformCertificationRepository(ABC):
    @abstractmethod
    def save(self, cert: PlatformCertification) -> PlatformCertification: ...

    @abstractmethod
    def find_by_id(self, cert_id: str) -> PlatformCertification | None: ...

    @abstractmethod
    def find_all(self) -> list[PlatformCertification]: ...

    @abstractmethod
    def find_by_type(self, cert_type: str) -> list[PlatformCertification]: ...

    @abstractmethod
    def find_by_status(self, status: str) -> list[PlatformCertification]: ...

    @abstractmethod
    def update(self, cert_id: str, data: dict) -> PlatformCertification | None: ...

    @abstractmethod
    def delete(self, cert_id: str) -> bool: ...


class CertificationRequirementRepository(ABC):
    @abstractmethod
    def save(self, req: CertificationRequirement) -> CertificationRequirement: ...

    @abstractmethod
    def find_by_id(self, req_id: str) -> CertificationRequirement | None: ...

    @abstractmethod
    def find_by_certification_id(self, cert_id: str) -> list[CertificationRequirement]: ...

    @abstractmethod
    def update(self, req_id: str, data: dict) -> CertificationRequirement | None: ...

    @abstractmethod
    def delete(self, req_id: str) -> bool: ...


class CertificationReportRepository(ABC):
    @abstractmethod
    def save(self, report: PlatformCertificationReport) -> PlatformCertificationReport: ...

    @abstractmethod
    def find_latest(self) -> PlatformCertificationReport | None: ...

    @abstractmethod
    def find_all(self) -> list[PlatformCertificationReport]: ...


# ── Sustainability ──────────────────────────────────────────────────


class DependencyLifecycleRepository(ABC):
    @abstractmethod
    def save(self, dep: DependencyLifecycle) -> DependencyLifecycle: ...

    @abstractmethod
    def find_by_name(self, name: str) -> DependencyLifecycle | None: ...

    @abstractmethod
    def find_all(self) -> list[DependencyLifecycle]: ...

    @abstractmethod
    def delete(self, name: str) -> bool: ...


class APIStabilityRepository(ABC):
    @abstractmethod
    def save(self, report: object) -> object: ...

    @abstractmethod
    def find_by_version(self, version: str) -> object | None: ...

    @abstractmethod
    def find_latest(self) -> object | None: ...


class ModuleOwnershipRepository(ABC):
    @abstractmethod
    def save(self, ownership: ModuleOwnership) -> ModuleOwnership: ...

    @abstractmethod
    def find_by_module(self, module: str) -> ModuleOwnership | None: ...

    @abstractmethod
    def find_all(self) -> list[ModuleOwnership]: ...


class DocumentationFreshnessRepository(ABC):
    @abstractmethod
    def save(self, doc: DocumentationFreshness) -> DocumentationFreshness: ...

    @abstractmethod
    def find_by_component(self, component: str) -> DocumentationFreshness | None: ...

    @abstractmethod
    def find_all(self) -> list[DocumentationFreshness]: ...


class SustainabilityDashboardRepository(ABC):
    @abstractmethod
    def save(self, dashboard: SustainabilityDashboard) -> SustainabilityDashboard: ...

    @abstractmethod
    def find_latest(self) -> SustainabilityDashboard | None: ...


class MaintenanceRoadmapRepository(ABC):
    @abstractmethod
    def save(self, roadmap: MaintenanceRoadmap) -> MaintenanceRoadmap: ...

    @abstractmethod
    def find_by_id(self, roadmap_id: str) -> MaintenanceRoadmap | None: ...

    @abstractmethod
    def find_all(self) -> list[MaintenanceRoadmap]: ...

    @abstractmethod
    def delete(self, roadmap_id: str) -> bool: ...


# ── Release Engineering ─────────────────────────────────────────────


class ReleasePlanRepository(ABC):
    @abstractmethod
    def save(self, plan: ReleasePlan) -> ReleasePlan: ...

    @abstractmethod
    def find_by_id(self, plan_id: str) -> ReleasePlan | None: ...

    @abstractmethod
    def find_by_version(self, version: str) -> ReleasePlan | None: ...

    @abstractmethod
    def find_all(self) -> list[ReleasePlan]: ...

    @abstractmethod
    def update(self, plan_id: str, data: dict) -> ReleasePlan | None: ...

    @abstractmethod
    def delete(self, plan_id: str) -> bool: ...


class ReleaseValidationRepository(ABC):
    @abstractmethod
    def save(self, val: ReleaseValidation) -> ReleaseValidation: ...

    @abstractmethod
    def find_by_id(self, val_id: str) -> ReleaseValidation | None: ...

    @abstractmethod
    def find_by_release_id(self, release_id: str) -> list[ReleaseValidation]: ...


class PackagingResultRepository(ABC):
    @abstractmethod
    def save(self, pkg: PackagingResult) -> PackagingResult: ...

    @abstractmethod
    def find_by_id(self, pkg_id: str) -> PackagingResult | None: ...

    @abstractmethod
    def find_by_release_id(self, release_id: str) -> list[PackagingResult]: ...


class RegressionResultRepository(ABC):
    @abstractmethod
    def save(self, result: RegressionResult) -> RegressionResult: ...

    @abstractmethod
    def find_by_id(self, result_id: str) -> RegressionResult | None: ...

    @abstractmethod
    def find_by_release_id(self, release_id: str) -> list[RegressionResult]: ...


class ReleaseHistoryRepository(ABC):
    @abstractmethod
    def save(self, entry: ReleaseHistoryEntry) -> ReleaseHistoryEntry: ...

    @abstractmethod
    def find_by_id(self, entry_id: str) -> ReleaseHistoryEntry | None: ...

    @abstractmethod
    def find_by_version(self, version: str) -> ReleaseHistoryEntry | None: ...

    @abstractmethod
    def find_all(self) -> list[ReleaseHistoryEntry]: ...


# ── Disaster Recovery ───────────────────────────────────────────────


class BackupValidationRepository(ABC):
    @abstractmethod
    def save(self, validation: BackupValidation) -> BackupValidation: ...

    @abstractmethod
    def find_by_id(self, val_id: str) -> BackupValidation | None: ...

    @abstractmethod
    def find_by_backup_id(self, backup_id: str) -> list[BackupValidation]: ...

    @abstractmethod
    def find_all(self) -> list[BackupValidation]: ...


class RestoreTestRepository(ABC):
    @abstractmethod
    def save(self, test: RestoreTest) -> RestoreTest: ...

    @abstractmethod
    def find_by_id(self, test_id: str) -> RestoreTest | None: ...

    @abstractmethod
    def find_by_backup_id(self, backup_id: str) -> list[RestoreTest]: ...

    @abstractmethod
    def find_all(self) -> list[RestoreTest]: ...


class ArchiveRecoveryRepository(ABC):
    @abstractmethod
    def save(self, recovery: ArchiveRecovery) -> ArchiveRecovery: ...

    @abstractmethod
    def find_by_id(self, recovery_id: str) -> ArchiveRecovery | None: ...

    @abstractmethod
    def find_all(self) -> list[ArchiveRecovery]: ...


class RecoveryReadinessRepository(ABC):
    @abstractmethod
    def save(self, report: RecoveryReadinessReport) -> RecoveryReadinessReport: ...

    @abstractmethod
    def find_latest(self) -> RecoveryReadinessReport | None: ...

    @abstractmethod
    def find_all(self) -> list[RecoveryReadinessReport]: ...


# ── Platform Validation ─────────────────────────────────────────────


class ValidationCheckRepository(ABC):
    @abstractmethod
    def save(self, check: ValidationCheck) -> ValidationCheck: ...

    @abstractmethod
    def find_by_id(self, check_id: str) -> ValidationCheck | None: ...

    @abstractmethod
    def find_by_subsystem(self, subsystem: str) -> list[ValidationCheck]: ...

    @abstractmethod
    def find_all(self) -> list[ValidationCheck]: ...


class SubsystemValidationRepository(ABC):
    @abstractmethod
    def save(self, sv: SubsystemValidation) -> SubsystemValidation: ...

    @abstractmethod
    def find_by_id(self, sv_id: str) -> SubsystemValidation | None: ...

    @abstractmethod
    def find_by_subsystem(self, subsystem: str) -> SubsystemValidation | None: ...

    @abstractmethod
    def find_all(self) -> list[SubsystemValidation]: ...


class PlatformValidationReportRepository(ABC):
    @abstractmethod
    def save(self, report: PlatformValidationReport) -> PlatformValidationReport: ...

    @abstractmethod
    def find_latest(self) -> PlatformValidationReport | None: ...

    @abstractmethod
    def find_all(self) -> list[PlatformValidationReport]: ...


class FinalAcceptanceTestRepository(ABC):
    @abstractmethod
    def save(self, fat: FinalAcceptanceTest) -> FinalAcceptanceTest: ...

    @abstractmethod
    def find_by_id(self, fat_id: str) -> FinalAcceptanceTest | None: ...

    @abstractmethod
    def find_by_version(self, version: str) -> FinalAcceptanceTest | None: ...

    @abstractmethod
    def find_all(self) -> list[FinalAcceptanceTest]: ...
