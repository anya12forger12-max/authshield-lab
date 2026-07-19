"""In-memory repository implementations for production entities."""

from __future__ import annotations

from typing import Optional
import copy

from ..domain.interfaces import (
    IReleaseRepository,
    IReleasePackageRepository,
    IBuildInfoRepository,
    ILtsVersionRepository,
    IMigrationStepRepository,
    ICompatibilityMatrixRepository,
    IDeprecationEntryRepository,
    IGovernanceReviewRepository,
    IGovernancePolicyRepository,
    IArchitectureAuditRepository,
    IGovernanceReportRepository,
    ICertificationRepository,
    ICertificationRequirementRepository,
    IProductionValidationRepository,
    IProjectHealthRepository,
    IArchitectureDecisionRecordRepository,
    IMigrationHistoryRepository,
    IReleaseHistoryRepository,
    IKnowledgeEntryRepository,
    ICodingStandardRepository,
)
from ..domain.entities.release_center import Release, ReleasePackage, BuildInfo
from ..domain.entities.lts import LtsVersion, MigrationStep, CompatibilityMatrix, DeprecationEntry
from ..domain.entities.governance import (
    GovernanceReview,
    GovernancePolicy,
    ArchitectureAudit,
    GovernanceReport,
)
from ..domain.entities.certification import (
    Certification,
    CertificationRequirement,
    ProductionValidation,
    ProjectHealth,
)
from ..domain.entities.knowledge_preservation import (
    ArchitectureDecisionRecord,
    MigrationHistory,
    ReleaseHistory,
    KnowledgeEntry,
    CodingStandard,
)


class InMemoryReleaseRepository(IReleaseRepository):
    """In-memory store for Release entities."""

    def __init__(self) -> None:
        self._store: dict[str, Release] = {}

    async def create(self, release: Release) -> Release:
        self._store[release.id] = copy.deepcopy(release)
        return self._store[release.id]

    async def get_by_id(self, release_id: str) -> Optional[Release]:
        item = self._store.get(release_id)
        return copy.deepcopy(item) if item else None

    async def get_all(self, page: int = 1, per_page: int = 20) -> dict:
        items = list(self._store.values())
        total = len(items)
        start = (page - 1) * per_page
        end = start + per_page
        pages = max(1, (total + per_page - 1) // per_page) if per_page > 0 else 1
        return {
            "items": [copy.deepcopy(i) for i in items[start:end]],
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages,
        }

    async def get_by_version(self, version: str) -> Optional[Release]:
        for item in self._store.values():
            if item.version == version:
                return copy.deepcopy(item)
        return None

    async def update(self, release_id: str, data: dict) -> Optional[Release]:
        item = self._store.get(release_id)
        if item is None:
            return None
        for key, value in data.items():
            if hasattr(item, key):
                setattr(item, key, value)
        return copy.deepcopy(item)

    async def delete(self, release_id: str) -> bool:
        if release_id in self._store:
            del self._store[release_id]
            return True
        return False


class InMemoryReleasePackageRepository(IReleasePackageRepository):
    """In-memory store for ReleasePackage entities."""

    def __init__(self) -> None:
        self._store: dict[str, ReleasePackage] = {}

    async def create(self, package: ReleasePackage) -> ReleasePackage:
        self._store[package.id] = copy.deepcopy(package)
        return self._store[package.id]

    async def get_by_id(self, package_id: str) -> Optional[ReleasePackage]:
        item = self._store.get(package_id)
        return copy.deepcopy(item) if item else None

    async def get_by_release_id(self, release_id: str) -> list[ReleasePackage]:
        return [
            copy.deepcopy(p)
            for p in self._store.values()
            if p.release_id == release_id
        ]

    async def delete(self, package_id: str) -> bool:
        if package_id in self._store:
            del self._store[package_id]
            return True
        return False


class InMemoryBuildInfoRepository(IBuildInfoRepository):
    """In-memory store for BuildInfo entities."""

    def __init__(self) -> None:
        self._store: dict[str, BuildInfo] = {}

    async def create(self, build_info: BuildInfo) -> BuildInfo:
        self._store[build_info.id] = copy.deepcopy(build_info)
        return self._store[build_info.id]

    async def get_by_id(self, build_info_id: str) -> Optional[BuildInfo]:
        item = self._store.get(build_info_id)
        return copy.deepcopy(item) if item else None

    async def get_by_version(self, version: str) -> Optional[BuildInfo]:
        for item in self._store.values():
            if item.version == version:
                return copy.deepcopy(item)
        return None


class InMemoryLtsVersionRepository(ILtsVersionRepository):
    """In-memory store for LtsVersion entities."""

    def __init__(self) -> None:
        self._store: dict[str, LtsVersion] = {}

    async def create(self, lts: LtsVersion) -> LtsVersion:
        self._store[lts.id] = copy.deepcopy(lts)
        return self._store[lts.id]

    async def get_by_id(self, lts_id: str) -> Optional[LtsVersion]:
        item = self._store.get(lts_id)
        return copy.deepcopy(item) if item else None

    async def get_by_version(self, version: str) -> Optional[LtsVersion]:
        for item in self._store.values():
            if item.version == version:
                return copy.deepcopy(item)
        return None

    async def get_all(self, page: int = 1, per_page: int = 20) -> dict:
        items = list(self._store.values())
        total = len(items)
        start = (page - 1) * per_page
        end = start + per_page
        pages = max(1, (total + per_page - 1) // per_page) if per_page > 0 else 1
        return {
            "items": [copy.deepcopy(i) for i in items[start:end]],
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages,
        }

    async def update(self, lts_id: str, data: dict) -> Optional[LtsVersion]:
        item = self._store.get(lts_id)
        if item is None:
            return None
        for key, value in data.items():
            if hasattr(item, key):
                setattr(item, key, value)
        return copy.deepcopy(item)

    async def delete(self, lts_id: str) -> bool:
        if lts_id in self._store:
            del self._store[lts_id]
            return True
        return False


class InMemoryMigrationStepRepository(IMigrationStepRepository):
    """In-memory store for MigrationStep entities."""

    def __init__(self) -> None:
        self._store: dict[str, MigrationStep] = {}

    async def create(self, step: MigrationStep) -> MigrationStep:
        self._store[step.id] = copy.deepcopy(step)
        return self._store[step.id]

    async def get_by_id(self, step_id: str) -> Optional[MigrationStep]:
        item = self._store.get(step_id)
        return copy.deepcopy(item) if item else None

    async def get_by_version_pair(
        self, from_version: str, to_version: str
    ) -> list[MigrationStep]:
        steps = [
            copy.deepcopy(s)
            for s in self._store.values()
            if s.from_version == from_version and s.to_version == to_version
        ]
        return sorted(steps, key=lambda s: s.step_number)

    async def delete(self, step_id: str) -> bool:
        if step_id in self._store:
            del self._store[step_id]
            return True
        return False


class InMemoryCompatibilityMatrixRepository(ICompatibilityMatrixRepository):
    """In-memory store for CompatibilityMatrix entities."""

    def __init__(self) -> None:
        self._store: dict[str, CompatibilityMatrix] = {}

    async def create(self, entry: CompatibilityMatrix) -> CompatibilityMatrix:
        self._store[entry.id] = copy.deepcopy(entry)
        return self._store[entry.id]

    async def get_by_id(self, entry_id: str) -> Optional[CompatibilityMatrix]:
        item = self._store.get(entry_id)
        return copy.deepcopy(item) if item else None

    async def check_compatibility(
        self, version_a: str, version_b: str
    ) -> Optional[CompatibilityMatrix]:
        for item in self._store.values():
            if (item.version_a == version_a and item.version_b == version_b) or (
                item.version_a == version_b and item.version_b == version_a
            ):
                return copy.deepcopy(item)
        return None

    async def get_all(self) -> list[CompatibilityMatrix]:
        return [copy.deepcopy(i) for i in self._store.values()]


class InMemoryDeprecationEntryRepository(IDeprecationEntryRepository):
    """In-memory store for DeprecationEntry entities."""

    def __init__(self) -> None:
        self._store: dict[str, DeprecationEntry] = {}

    async def create(self, entry: DeprecationEntry) -> DeprecationEntry:
        self._store[entry.id] = copy.deepcopy(entry)
        return self._store[entry.id]

    async def get_by_id(self, entry_id: str) -> Optional[DeprecationEntry]:
        item = self._store.get(entry_id)
        return copy.deepcopy(item) if item else None

    async def get_by_feature(self, feature: str) -> Optional[DeprecationEntry]:
        for item in self._store.values():
            if item.feature == feature:
                return copy.deepcopy(item)
        return None

    async def get_all(self) -> list[DeprecationEntry]:
        return [copy.deepcopy(i) for i in self._store.values()]

    async def delete(self, entry_id: str) -> bool:
        if entry_id in self._store:
            del self._store[entry_id]
            return True
        return False


class InMemoryGovernanceReviewRepository(IGovernanceReviewRepository):
    """In-memory store for GovernanceReview entities."""

    def __init__(self) -> None:
        self._store: dict[str, GovernanceReview] = {}

    async def create(self, review: GovernanceReview) -> GovernanceReview:
        self._store[review.id] = copy.deepcopy(review)
        return self._store[review.id]

    async def get_by_id(self, review_id: str) -> Optional[GovernanceReview]:
        item = self._store.get(review_id)
        return copy.deepcopy(item) if item else None

    async def get_all(self, page: int = 1, per_page: int = 20) -> dict:
        items = list(self._store.values())
        total = len(items)
        start = (page - 1) * per_page
        end = start + per_page
        pages = max(1, (total + per_page - 1) // per_page) if per_page > 0 else 1
        return {
            "items": [copy.deepcopy(i) for i in items[start:end]],
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages,
        }

    async def get_by_area(self, area: str) -> list[GovernanceReview]:
        return [
            copy.deepcopy(r)
            for r in self._store.values()
            if (r.area.value == area if hasattr(r.area, "value") else r.area == area)
        ]

    async def update(self, review_id: str, data: dict) -> Optional[GovernanceReview]:
        item = self._store.get(review_id)
        if item is None:
            return None
        for key, value in data.items():
            if hasattr(item, key):
                setattr(item, key, value)
        return copy.deepcopy(item)

    async def delete(self, review_id: str) -> bool:
        if review_id in self._store:
            del self._store[review_id]
            return True
        return False


class InMemoryGovernancePolicyRepository(IGovernancePolicyRepository):
    """In-memory store for GovernancePolicy entities."""

    def __init__(self) -> None:
        self._store: dict[str, GovernancePolicy] = {}

    async def create(self, policy: GovernancePolicy) -> GovernancePolicy:
        self._store[policy.id] = copy.deepcopy(policy)
        return self._store[policy.id]

    async def get_by_id(self, policy_id: str) -> Optional[GovernancePolicy]:
        item = self._store.get(policy_id)
        return copy.deepcopy(item) if item else None

    async def get_by_area(self, area: str) -> list[GovernancePolicy]:
        return [
            copy.deepcopy(p)
            for p in self._store.values()
            if (p.area.value == area if hasattr(p.area, "value") else p.area == area)
        ]

    async def get_all(self) -> list[GovernancePolicy]:
        return [copy.deepcopy(i) for i in self._store.values()]

    async def update(self, policy_id: str, data: dict) -> Optional[GovernancePolicy]:
        item = self._store.get(policy_id)
        if item is None:
            return None
        for key, value in data.items():
            if hasattr(item, key):
                setattr(item, key, value)
        return copy.deepcopy(item)


class InMemoryArchitectureAuditRepository(IArchitectureAuditRepository):
    """In-memory store for ArchitectureAudit entities."""

    def __init__(self) -> None:
        self._store: dict[str, ArchitectureAudit] = {}

    async def create(self, audit: ArchitectureAudit) -> ArchitectureAudit:
        self._store[audit.id] = copy.deepcopy(audit)
        return self._store[audit.id]

    async def get_by_id(self, audit_id: str) -> Optional[ArchitectureAudit]:
        item = self._store.get(audit_id)
        return copy.deepcopy(item) if item else None

    async def get_all(self, page: int = 1, per_page: int = 20) -> dict:
        items = list(self._store.values())
        total = len(items)
        start = (page - 1) * per_page
        end = start + per_page
        pages = max(1, (total + per_page - 1) // per_page) if per_page > 0 else 1
        return {
            "items": [copy.deepcopy(i) for i in items[start:end]],
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages,
        }


class InMemoryGovernanceReportRepository(IGovernanceReportRepository):
    """In-memory store for GovernanceReport entities."""

    def __init__(self) -> None:
        self._store: dict[str, GovernanceReport] = {}

    async def create(self, report: GovernanceReport) -> GovernanceReport:
        self._store[report.id] = copy.deepcopy(report)
        return self._store[report.id]

    async def get_by_id(self, report_id: str) -> Optional[GovernanceReport]:
        item = self._store.get(report_id)
        return copy.deepcopy(item) if item else None

    async def get_all(self, page: int = 1, per_page: int = 20) -> dict:
        items = list(self._store.values())
        total = len(items)
        start = (page - 1) * per_page
        end = start + per_page
        pages = max(1, (total + per_page - 1) // per_page) if per_page > 0 else 1
        return {
            "items": [copy.deepcopy(i) for i in items[start:end]],
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages,
        }


class InMemoryCertificationRepository(ICertificationRepository):
    """In-memory store for Certification entities."""

    def __init__(self) -> None:
        self._store: dict[str, Certification] = {}

    async def create(self, cert: Certification) -> Certification:
        self._store[cert.id] = copy.deepcopy(cert)
        return self._store[cert.id]

    async def get_by_id(self, cert_id: str) -> Optional[Certification]:
        item = self._store.get(cert_id)
        return copy.deepcopy(item) if item else None

    async def get_all(self, page: int = 1, per_page: int = 20) -> dict:
        items = list(self._store.values())
        total = len(items)
        start = (page - 1) * per_page
        end = start + per_page
        pages = max(1, (total + per_page - 1) // per_page) if per_page > 0 else 1
        return {
            "items": [copy.deepcopy(i) for i in items[start:end]],
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages,
        }

    async def get_by_type(self, cert_type: str) -> list[Certification]:
        return [
            copy.deepcopy(c)
            for c in self._store.values()
            if (c.cert_type.value == cert_type if hasattr(c.cert_type, "value") else c.cert_type == cert_type)
        ]

    async def update(self, cert_id: str, data: dict) -> Optional[Certification]:
        item = self._store.get(cert_id)
        if item is None:
            return None
        for key, value in data.items():
            if hasattr(item, key):
                setattr(item, key, value)
        return copy.deepcopy(item)

    async def delete(self, cert_id: str) -> bool:
        if cert_id in self._store:
            del self._store[cert_id]
            return True
        return False


class InMemoryCertificationRequirementRepository(ICertificationRequirementRepository):
    """In-memory store for CertificationRequirement entities."""

    def __init__(self) -> None:
        self._store: dict[str, CertificationRequirement] = {}

    async def create(self, req: CertificationRequirement) -> CertificationRequirement:
        self._store[req.id] = copy.deepcopy(req)
        return self._store[req.id]

    async def get_by_id(self, req_id: str) -> Optional[CertificationRequirement]:
        item = self._store.get(req_id)
        return copy.deepcopy(item) if item else None

    async def get_by_certification_id(
        self, cert_id: str
    ) -> list[CertificationRequirement]:
        return [
            copy.deepcopy(r)
            for r in self._store.values()
            if r.certification_id == cert_id
        ]

    async def update(self, req_id: str, data: dict) -> Optional[CertificationRequirement]:
        item = self._store.get(req_id)
        if item is None:
            return None
        for key, value in data.items():
            if hasattr(item, key):
                setattr(item, key, value)
        return copy.deepcopy(item)


class InMemoryProductionValidationRepository(IProductionValidationRepository):
    """In-memory store for ProductionValidation entities."""

    def __init__(self) -> None:
        self._store: dict[str, ProductionValidation] = {}

    async def create(self, val: ProductionValidation) -> ProductionValidation:
        self._store[val.id] = copy.deepcopy(val)
        return self._store[val.id]

    async def get_by_id(self, val_id: str) -> Optional[ProductionValidation]:
        item = self._store.get(val_id)
        return copy.deepcopy(item) if item else None

    async def get_by_subsystem(self, subsystem: str) -> list[ProductionValidation]:
        return [
            copy.deepcopy(v)
            for v in self._store.values()
            if v.subsystem == subsystem
        ]

    async def get_all(self) -> list[ProductionValidation]:
        return [copy.deepcopy(i) for i in self._store.values()]


class InMemoryProjectHealthRepository(IProjectHealthRepository):
    """In-memory store for ProjectHealth entities."""

    def __init__(self) -> None:
        self._store: dict[str, ProjectHealth] = {}
        self._latest_id: str | None = None

    async def create(self, health: ProjectHealth) -> ProjectHealth:
        self._store[health.id] = copy.deepcopy(health)
        self._latest_id = health.id
        return self._store[health.id]

    async def get_latest(self) -> Optional[ProjectHealth]:
        if self._latest_id and self._latest_id in self._store:
            return copy.deepcopy(self._store[self._latest_id])
        return None

    async def get_all(self) -> list[ProjectHealth]:
        return [copy.deepcopy(i) for i in self._store.values()]


class InMemoryArchitectureDecisionRecordRepository(IArchitectureDecisionRecordRepository):
    """In-memory store for ArchitectureDecisionRecord entities."""

    def __init__(self) -> None:
        self._store: dict[str, ArchitectureDecisionRecord] = {}

    async def create(self, adr: ArchitectureDecisionRecord) -> ArchitectureDecisionRecord:
        self._store[adr.id] = copy.deepcopy(adr)
        return self._store[adr.id]

    async def get_by_id(self, adr_id: str) -> Optional[ArchitectureDecisionRecord]:
        item = self._store.get(adr_id)
        return copy.deepcopy(item) if item else None

    async def get_all(self, page: int = 1, per_page: int = 20) -> dict:
        items = list(self._store.values())
        total = len(items)
        start = (page - 1) * per_page
        end = start + per_page
        pages = max(1, (total + per_page - 1) // per_page) if per_page > 0 else 1
        return {
            "items": [copy.deepcopy(i) for i in items[start:end]],
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages,
        }

    async def update(
        self, adr_id: str, data: dict
    ) -> Optional[ArchitectureDecisionRecord]:
        item = self._store.get(adr_id)
        if item is None:
            return None
        for key, value in data.items():
            if hasattr(item, key):
                setattr(item, key, value)
        return copy.deepcopy(item)

    async def delete(self, adr_id: str) -> bool:
        if adr_id in self._store:
            del self._store[adr_id]
            return True
        return False


class InMemoryMigrationHistoryRepository(IMigrationHistoryRepository):
    """In-memory store for MigrationHistory entities."""

    def __init__(self) -> None:
        self._store: dict[str, MigrationHistory] = {}

    async def create(self, history: MigrationHistory) -> MigrationHistory:
        self._store[history.id] = copy.deepcopy(history)
        return self._store[history.id]

    async def get_by_id(self, history_id: str) -> Optional[MigrationHistory]:
        item = self._store.get(history_id)
        return copy.deepcopy(item) if item else None

    async def get_all(self) -> list[MigrationHistory]:
        return [copy.deepcopy(i) for i in self._store.values()]


class InMemoryReleaseHistoryRepository(IReleaseHistoryRepository):
    """In-memory store for ReleaseHistory entities."""

    def __init__(self) -> None:
        self._store: dict[str, ReleaseHistory] = {}

    async def create(self, history: ReleaseHistory) -> ReleaseHistory:
        self._store[history.id] = copy.deepcopy(history)
        return self._store[history.id]

    async def get_by_id(self, history_id: str) -> Optional[ReleaseHistory]:
        item = self._store.get(history_id)
        return copy.deepcopy(item) if item else None

    async def get_all(self) -> list[ReleaseHistory]:
        return [copy.deepcopy(i) for i in self._store.values()]


class InMemoryKnowledgeEntryRepository(IKnowledgeEntryRepository):
    """In-memory store for KnowledgeEntry entities."""

    def __init__(self) -> None:
        self._store: dict[str, KnowledgeEntry] = {}

    async def create(self, entry: KnowledgeEntry) -> KnowledgeEntry:
        self._store[entry.id] = copy.deepcopy(entry)
        return self._store[entry.id]

    async def get_by_id(self, entry_id: str) -> Optional[KnowledgeEntry]:
        item = self._store.get(entry_id)
        return copy.deepcopy(item) if item else None

    async def get_all(self, page: int = 1, per_page: int = 20) -> dict:
        items = list(self._store.values())
        total = len(items)
        start = (page - 1) * per_page
        end = start + per_page
        pages = max(1, (total + per_page - 1) // per_page) if per_page > 0 else 1
        return {
            "items": [copy.deepcopy(i) for i in items[start:end]],
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages,
        }

    async def search(self, query: str) -> list[KnowledgeEntry]:
        q = query.lower()
        return [
            copy.deepcopy(e)
            for e in self._store.values()
            if q in e.title.lower()
            or q in e.content.lower()
            or q in e.category.lower()
            or any(q in tag.lower() for tag in e.tags)
        ]

    async def update(self, entry_id: str, data: dict) -> Optional[KnowledgeEntry]:
        item = self._store.get(entry_id)
        if item is None:
            return None
        for key, value in data.items():
            if hasattr(item, key):
                setattr(item, key, value)
        return copy.deepcopy(item)

    async def delete(self, entry_id: str) -> bool:
        if entry_id in self._store:
            del self._store[entry_id]
            return True
        return False


class InMemoryCodingStandardRepository(ICodingStandardRepository):
    """In-memory store for CodingStandard entities."""

    def __init__(self) -> None:
        self._store: dict[str, CodingStandard] = {}

    async def create(self, standard: CodingStandard) -> CodingStandard:
        self._store[standard.id] = copy.deepcopy(standard)
        return self._store[standard.id]

    async def get_by_id(self, standard_id: str) -> Optional[CodingStandard]:
        item = self._store.get(standard_id)
        return copy.deepcopy(item) if item else None

    async def get_all(self) -> list[CodingStandard]:
        return [copy.deepcopy(i) for i in self._store.values()]

    async def update(
        self, standard_id: str, data: dict
    ) -> Optional[CodingStandard]:
        item = self._store.get(standard_id)
        if item is None:
            return None
        for key, value in data.items():
            if hasattr(item, key):
                setattr(item, key, value)
        return copy.deepcopy(item)

    async def delete(self, standard_id: str) -> bool:
        if standard_id in self._store:
            del self._store[standard_id]
            return True
        return False
