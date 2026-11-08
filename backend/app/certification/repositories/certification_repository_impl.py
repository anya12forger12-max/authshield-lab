"""In-memory repository implementations for all Certification module entities."""

from __future__ import annotations

import math
from typing import Any, Optional

from ..domain.entities.operations import (
    EcosystemDashboard,
    ModuleInventory,
    PackageHealth,
    PlatformHealth,
    ServiceStatus,
)
from ..domain.entities.certification_center import (
    CertificationRequirement,
    PlatformCertification,
    PlatformCertificationReport,
)
from ..domain.entities.sustainability import (
    APIStabilityReport,
    DependencyLifecycle,
    DocumentationFreshness,
    MaintenanceRoadmap,
    ModuleOwnership,
    SustainabilityDashboard,
)
from ..domain.entities.release_engineering import (
    PackagingResult,
    RegressionResult,
    ReleaseHistoryEntry,
    ReleasePlan,
    ReleaseValidation,
)
from ..domain.entities.disaster_recovery import (
    ArchiveRecovery,
    BackupValidation,
    RecoveryReadinessReport,
    RestoreTest,
)
from ..domain.entities.platform_validation import (
    FinalAcceptanceTest,
    PlatformValidationReport,
    SubsystemValidation,
    ValidationCheck,
)
from ..domain.interfaces import (
    APIStabilityRepository,
    ArchiveRecoveryRepository,
    BackupValidationRepository,
    CertificationReportRepository,
    CertificationRequirementRepository,
    DependencyLifecycleRepository,
    DocumentationFreshnessRepository,
    EcosystemDashboardRepository,
    FinalAcceptanceTestRepository,
    MaintenanceRoadmapRepository,
    ModuleInventoryRepository,
    ModuleOwnershipRepository,
    PackageHealthRepository,
    PackagingResultRepository,
    PlatformCertificationRepository,
    PlatformHealthRepository,
    PlatformValidationReportRepository,
    RecoveryReadinessRepository,
    RegressionResultRepository,
    ReleaseHistoryRepository,
    ReleasePlanRepository,
    ReleaseValidationRepository,
    RestoreTestRepository,
    ServiceStatusRepository,
    SubsystemValidationRepository,
    SustainabilityDashboardRepository,
    ValidationCheckRepository,
)


# ── Operations ──────────────────────────────────────────────────────


class InMemoryServiceStatusRepository(ServiceStatusRepository):
    def __init__(self) -> None:
        self._store: dict[str, ServiceStatus] = {}

    def save(self, status: ServiceStatus) -> ServiceStatus:
        self._store[status.name] = status
        return status

    def find_by_name(self, name: str) -> Optional[ServiceStatus]:
        return self._store.get(name)

    def find_all(self) -> list[ServiceStatus]:
        return list(self._store.values())


class InMemoryPlatformHealthRepository(PlatformHealthRepository):
    def __init__(self) -> None:
        self._store: list[PlatformHealth] = []

    def save(self, health: PlatformHealth) -> PlatformHealth:
        self._store.append(health)
        return health

    def find_latest(self) -> Optional[PlatformHealth]:
        return self._store[-1] if self._store else None

    def find_all(self) -> list[PlatformHealth]:
        return list(self._store)


class InMemoryModuleInventoryRepository(ModuleInventoryRepository):
    def __init__(self) -> None:
        self._store: dict[str, ModuleInventory] = {}

    def save(self, module: ModuleInventory) -> ModuleInventory:
        self._store[module.name] = module
        return module

    def find_by_name(self, name: str) -> Optional[ModuleInventory]:
        return self._store.get(name)

    def find_all(self) -> list[ModuleInventory]:
        return list(self._store.values())

    def delete(self, module_id: str) -> bool:
        for name, mod in self._store.items():
            if mod.id == module_id:
                del self._store[name]
                return True
        return False


class InMemoryPackageHealthRepository(PackageHealthRepository):
    def __init__(self) -> None:
        self._store: dict[str, PackageHealth] = {}

    def save(self, pkg: PackageHealth) -> PackageHealth:
        self._store[pkg.name] = pkg
        return pkg

    def find_by_name(self, name: str) -> Optional[PackageHealth]:
        return self._store.get(name)

    def find_all(self) -> list[PackageHealth]:
        return list(self._store.values())


class InMemoryEcosystemDashboardRepository(EcosystemDashboardRepository):
    def __init__(self) -> None:
        self._store: list[EcosystemDashboard] = []

    def save(self, dashboard: EcosystemDashboard) -> EcosystemDashboard:
        self._store.append(dashboard)
        return dashboard

    def find_latest(self) -> Optional[EcosystemDashboard]:
        return self._store[-1] if self._store else None


# ── Certification Center ────────────────────────────────────────────


class InMemoryPlatformCertificationRepository(PlatformCertificationRepository):
    def __init__(self) -> None:
        self._store: dict[str, PlatformCertification] = {}

    def save(self, cert: PlatformCertification) -> PlatformCertification:
        self._store[cert.id] = cert
        return cert

    def find_by_id(self, cert_id: str) -> Optional[PlatformCertification]:
        return self._store.get(cert_id)

    def find_all(self) -> list[PlatformCertification]:
        return list(self._store.values())

    def find_by_type(self, cert_type: str) -> list[PlatformCertification]:
        return [c for c in self._store.values() if c.cert_type == cert_type]

    def find_by_status(self, status: str) -> list[PlatformCertification]:
        return [c for c in self._store.values() if c.status.value == status]

    def update(self, cert_id: str, data: dict) -> Optional[PlatformCertification]:
        cert = self._store.get(cert_id)
        if cert is None:
            return None
        for key, value in data.items():
            if hasattr(cert, key):
                setattr(cert, key, value)
        return cert

    def delete(self, cert_id: str) -> bool:
        if cert_id in self._store:
            del self._store[cert_id]
            return True
        return False


class InMemoryCertificationRequirementRepository(CertificationRequirementRepository):
    def __init__(self) -> None:
        self._store: dict[str, CertificationRequirement] = {}

    def save(self, req: CertificationRequirement) -> CertificationRequirement:
        self._store[req.id] = req
        return req

    def find_by_id(self, req_id: str) -> Optional[CertificationRequirement]:
        return self._store.get(req_id)

    def find_by_certification_id(self, cert_id: str) -> list[CertificationRequirement]:
        return [r for r in self._store.values() if r.certification_id == cert_id]

    def update(self, req_id: str, data: dict) -> Optional[CertificationRequirement]:
        req = self._store.get(req_id)
        if req is None:
            return None
        for key, value in data.items():
            if hasattr(req, key):
                setattr(req, key, value)
        return req

    def delete(self, req_id: str) -> bool:
        if req_id in self._store:
            del self._store[req_id]
            return True
        return False


class InMemoryCertificationReportRepository(CertificationReportRepository):
    def __init__(self) -> None:
        self._store: list[PlatformCertificationReport] = []

    def save(self, report: PlatformCertificationReport) -> PlatformCertificationReport:
        self._store.append(report)
        return report

    def find_latest(self) -> Optional[PlatformCertificationReport]:
        return self._store[-1] if self._store else None

    def find_all(self) -> list[PlatformCertificationReport]:
        return list(self._store)


# ── Sustainability ──────────────────────────────────────────────────


class InMemoryDependencyLifecycleRepository(DependencyLifecycleRepository):
    def __init__(self) -> None:
        self._store: dict[str, DependencyLifecycle] = {}

    def save(self, dep: DependencyLifecycle) -> DependencyLifecycle:
        self._store[dep.name] = dep
        return dep

    def find_by_name(self, name: str) -> Optional[DependencyLifecycle]:
        return self._store.get(name)

    def find_all(self) -> list[DependencyLifecycle]:
        return list(self._store.values())

    def delete(self, name: str) -> bool:
        if name in self._store:
            del self._store[name]
            return True
        return False


class InMemoryAPIStabilityRepository(APIStabilityRepository):
    def __init__(self) -> None:
        self._store: dict[str, APIStabilityReport] = {}

    def save(self, report: APIStabilityReport) -> APIStabilityReport:
        self._store[report.version] = report
        return report

    def find_by_version(self, version: str) -> Optional[APIStabilityReport]:
        return self._store.get(version)

    def find_latest(self) -> Optional[APIStabilityReport]:
        if not self._store:
            return None
        latest_key = max(self._store.keys())
        return self._store[latest_key]


class InMemoryModuleOwnershipRepository(ModuleOwnershipRepository):
    def __init__(self) -> None:
        self._store: dict[str, ModuleOwnership] = {}

    def save(self, ownership: ModuleOwnership) -> ModuleOwnership:
        self._store[ownership.module] = ownership
        return ownership

    def find_by_module(self, module: str) -> Optional[ModuleOwnership]:
        return self._store.get(module)

    def find_all(self) -> list[ModuleOwnership]:
        return list(self._store.values())


class InMemoryDocumentationFreshnessRepository(DocumentationFreshnessRepository):
    def __init__(self) -> None:
        self._store: dict[str, DocumentationFreshness] = {}

    def save(self, doc: DocumentationFreshness) -> DocumentationFreshness:
        self._store[doc.component] = doc
        return doc

    def find_by_component(self, component: str) -> Optional[DocumentationFreshness]:
        return self._store.get(component)

    def find_all(self) -> list[DocumentationFreshness]:
        return list(self._store.values())


class InMemorySustainabilityDashboardRepository(SustainabilityDashboardRepository):
    def __init__(self) -> None:
        self._store: list[SustainabilityDashboard] = []

    def save(self, dashboard: SustainabilityDashboard) -> SustainabilityDashboard:
        self._store.append(dashboard)
        return dashboard

    def find_latest(self) -> Optional[SustainabilityDashboard]:
        return self._store[-1] if self._store else None


class InMemoryMaintenanceRoadmapRepository(MaintenanceRoadmapRepository):
    def __init__(self) -> None:
        self._store: dict[str, MaintenanceRoadmap] = {}

    def save(self, roadmap: MaintenanceRoadmap) -> MaintenanceRoadmap:
        self._store[roadmap.id] = roadmap
        return roadmap

    def find_by_id(self, roadmap_id: str) -> Optional[MaintenanceRoadmap]:
        return self._store.get(roadmap_id)

    def find_all(self) -> list[MaintenanceRoadmap]:
        return list(self._store.values())

    def delete(self, roadmap_id: str) -> bool:
        if roadmap_id in self._store:
            del self._store[roadmap_id]
            return True
        return False


# ── Release Engineering ─────────────────────────────────────────────


class InMemoryReleasePlanRepository(ReleasePlanRepository):
    def __init__(self) -> None:
        self._store: dict[str, ReleasePlan] = {}

    def save(self, plan: ReleasePlan) -> ReleasePlan:
        self._store[plan.id] = plan
        return plan

    def find_by_id(self, plan_id: str) -> Optional[ReleasePlan]:
        return self._store.get(plan_id)

    def find_by_version(self, version: str) -> Optional[ReleasePlan]:
        for plan in self._store.values():
            if plan.version == version:
                return plan
        return None

    def find_all(self) -> list[ReleasePlan]:
        return list(self._store.values())

    def update(self, plan_id: str, data: dict) -> Optional[ReleasePlan]:
        plan = self._store.get(plan_id)
        if plan is None:
            return None
        for key, value in data.items():
            if hasattr(plan, key):
                setattr(plan, key, value)
        return plan

    def delete(self, plan_id: str) -> bool:
        if plan_id in self._store:
            del self._store[plan_id]
            return True
        return False


class InMemoryReleaseValidationRepository(ReleaseValidationRepository):
    def __init__(self) -> None:
        self._store: dict[str, ReleaseValidation] = {}

    def save(self, val: ReleaseValidation) -> ReleaseValidation:
        self._store[val.id] = val
        return val

    def find_by_id(self, val_id: str) -> Optional[ReleaseValidation]:
        return self._store.get(val_id)

    def find_by_release_id(self, release_id: str) -> list[ReleaseValidation]:
        return [v for v in self._store.values() if v.release_id == release_id]


class InMemoryPackagingResultRepository(PackagingResultRepository):
    def __init__(self) -> None:
        self._store: dict[str, PackagingResult] = {}

    def save(self, pkg: PackagingResult) -> PackagingResult:
        self._store[pkg.id] = pkg
        return pkg

    def find_by_id(self, pkg_id: str) -> Optional[PackagingResult]:
        return self._store.get(pkg_id)

    def find_by_release_id(self, release_id: str) -> list[PackagingResult]:
        return [p for p in self._store.values() if p.release_id == release_id]


class InMemoryRegressionResultRepository(RegressionResultRepository):
    def __init__(self) -> None:
        self._store: dict[str, RegressionResult] = {}

    def save(self, result: RegressionResult) -> RegressionResult:
        self._store[result.id] = result
        return result

    def find_by_id(self, result_id: str) -> Optional[RegressionResult]:
        return self._store.get(result_id)

    def find_by_release_id(self, release_id: str) -> list[RegressionResult]:
        return [r for r in self._store.values() if r.release_id == release_id]


class InMemoryReleaseHistoryRepository(ReleaseHistoryRepository):
    def __init__(self) -> None:
        self._store: dict[str, ReleaseHistoryEntry] = {}

    def save(self, entry: ReleaseHistoryEntry) -> ReleaseHistoryEntry:
        self._store[entry.id] = entry
        return entry

    def find_by_id(self, entry_id: str) -> Optional[ReleaseHistoryEntry]:
        return self._store.get(entry_id)

    def find_by_version(self, version: str) -> Optional[ReleaseHistoryEntry]:
        for entry in self._store.values():
            if entry.version == version:
                return entry
        return None

    def find_all(self) -> list[ReleaseHistoryEntry]:
        return list(self._store.values())


# ── Disaster Recovery ───────────────────────────────────────────────


class InMemoryBackupValidationRepository(BackupValidationRepository):
    def __init__(self) -> None:
        self._store: dict[str, BackupValidation] = {}

    def save(self, validation: BackupValidation) -> BackupValidation:
        self._store[validation.id] = validation
        return validation

    def find_by_id(self, val_id: str) -> Optional[BackupValidation]:
        return self._store.get(val_id)

    def find_by_backup_id(self, backup_id: str) -> list[BackupValidation]:
        return [v for v in self._store.values() if v.backup_id == backup_id]

    def find_all(self) -> list[BackupValidation]:
        return list(self._store.values())


class InMemoryRestoreTestRepository(RestoreTestRepository):
    def __init__(self) -> None:
        self._store: dict[str, RestoreTest] = {}

    def save(self, test: RestoreTest) -> RestoreTest:
        self._store[test.id] = test
        return test

    def find_by_id(self, test_id: str) -> Optional[RestoreTest]:
        return self._store.get(test_id)

    def find_by_backup_id(self, backup_id: str) -> list[RestoreTest]:
        return [t for t in self._store.values() if t.backup_id == backup_id]

    def find_all(self) -> list[RestoreTest]:
        return list(self._store.values())


class InMemoryArchiveRecoveryRepository(ArchiveRecoveryRepository):
    def __init__(self) -> None:
        self._store: dict[str, ArchiveRecovery] = {}

    def save(self, recovery: ArchiveRecovery) -> ArchiveRecovery:
        self._store[recovery.id] = recovery
        return recovery

    def find_by_id(self, recovery_id: str) -> Optional[ArchiveRecovery]:
        return self._store.get(recovery_id)

    def find_all(self) -> list[ArchiveRecovery]:
        return list(self._store.values())


class InMemoryRecoveryReadinessRepository(RecoveryReadinessRepository):
    def __init__(self) -> None:
        self._store: list[RecoveryReadinessReport] = []

    def save(self, report: RecoveryReadinessReport) -> RecoveryReadinessReport:
        self._store.append(report)
        return report

    def find_latest(self) -> Optional[RecoveryReadinessReport]:
        return self._store[-1] if self._store else None

    def find_all(self) -> list[RecoveryReadinessReport]:
        return list(self._store)


# ── Platform Validation ─────────────────────────────────────────────


class InMemoryValidationCheckRepository(ValidationCheckRepository):
    def __init__(self) -> None:
        self._store: dict[str, ValidationCheck] = {}

    def save(self, check: ValidationCheck) -> ValidationCheck:
        self._store[check.id] = check
        return check

    def find_by_id(self, check_id: str) -> Optional[ValidationCheck]:
        return self._store.get(check_id)

    def find_by_subsystem(self, subsystem: str) -> list[ValidationCheck]:
        return [c for c in self._store.values() if c.subsystem == subsystem]

    def find_all(self) -> list[ValidationCheck]:
        return list(self._store.values())


class InMemorySubsystemValidationRepository(SubsystemValidationRepository):
    def __init__(self) -> None:
        self._store: dict[str, SubsystemValidation] = {}

    def save(self, sv: SubsystemValidation) -> SubsystemValidation:
        self._store[sv.subsystem] = sv
        return sv

    def find_by_id(self, sv_id: str) -> Optional[SubsystemValidation]:
        for sv in self._store.values():
            if sv.id == sv_id:
                return sv
        return None

    def find_by_subsystem(self, subsystem: str) -> Optional[SubsystemValidation]:
        return self._store.get(subsystem)

    def find_all(self) -> list[SubsystemValidation]:
        return list(self._store.values())


class InMemoryPlatformValidationReportRepository(PlatformValidationReportRepository):
    def __init__(self) -> None:
        self._store: list[PlatformValidationReport] = []

    def save(self, report: PlatformValidationReport) -> PlatformValidationReport:
        self._store.append(report)
        return report

    def find_latest(self) -> Optional[PlatformValidationReport]:
        return self._store[-1] if self._store else None

    def find_all(self) -> list[PlatformValidationReport]:
        return list(self._store)


class InMemoryFinalAcceptanceTestRepository(FinalAcceptanceTestRepository):
    def __init__(self) -> None:
        self._store: dict[str, FinalAcceptanceTest] = {}

    def save(self, fat: FinalAcceptanceTest) -> FinalAcceptanceTest:
        self._store[fat.id] = fat
        return fat

    def find_by_id(self, fat_id: str) -> Optional[FinalAcceptanceTest]:
        return self._store.get(fat_id)

    def find_by_version(self, version: str) -> Optional[FinalAcceptanceTest]:
        for fat in self._store.values():
            if fat.version == version:
                return fat
        return None

    def find_all(self) -> list[FinalAcceptanceTest]:
        return list(self._store.values())
