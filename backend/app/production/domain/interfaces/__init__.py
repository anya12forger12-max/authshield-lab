"""Abstract repository interfaces for production entities."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from ..entities.release_center import Release, ReleasePackage, BuildInfo
from ..entities.lts import LtsVersion, MigrationStep, CompatibilityMatrix, DeprecationEntry
from ..entities.governance import (
    GovernanceReview,
    GovernancePolicy,
    ArchitectureAudit,
    GovernanceReport,
)
from ..entities.certification import (
    Certification,
    CertificationRequirement,
    ProductionValidation,
    ProjectHealth,
)
from ..entities.knowledge_preservation import (
    ArchitectureDecisionRecord,
    MigrationHistory,
    ReleaseHistory,
    KnowledgeEntry,
    CodingStandard,
)


class IReleaseRepository(ABC):
    """Interface for release data access."""

    @abstractmethod
    async def create(self, release: Release) -> Release:
        ...

    @abstractmethod
    async def get_by_id(self, release_id: str) -> Optional[Release]:
        ...

    @abstractmethod
    async def get_all(self, page: int = 1, per_page: int = 20) -> dict:
        ...

    @abstractmethod
    async def get_by_version(self, version: str) -> Optional[Release]:
        ...

    @abstractmethod
    async def update(self, release_id: str, data: dict) -> Optional[Release]:
        ...

    @abstractmethod
    async def delete(self, release_id: str) -> bool:
        ...


class IReleasePackageRepository(ABC):
    """Interface for release package data access."""

    @abstractmethod
    async def create(self, package: ReleasePackage) -> ReleasePackage:
        ...

    @abstractmethod
    async def get_by_id(self, package_id: str) -> Optional[ReleasePackage]:
        ...

    @abstractmethod
    async def get_by_release_id(self, release_id: str) -> list[ReleasePackage]:
        ...

    @abstractmethod
    async def delete(self, package_id: str) -> bool:
        ...


class IBuildInfoRepository(ABC):
    """Interface for build info data access."""

    @abstractmethod
    async def create(self, build_info: BuildInfo) -> BuildInfo:
        ...

    @abstractmethod
    async def get_by_id(self, build_info_id: str) -> Optional[BuildInfo]:
        ...

    @abstractmethod
    async def get_by_version(self, version: str) -> Optional[BuildInfo]:
        ...


class ILtsVersionRepository(ABC):
    """Interface for LTS version data access."""

    @abstractmethod
    async def create(self, lts: LtsVersion) -> LtsVersion:
        ...

    @abstractmethod
    async def get_by_id(self, lts_id: str) -> Optional[LtsVersion]:
        ...

    @abstractmethod
    async def get_by_version(self, version: str) -> Optional[LtsVersion]:
        ...

    @abstractmethod
    async def get_all(self, page: int = 1, per_page: int = 20) -> dict:
        ...

    @abstractmethod
    async def update(self, lts_id: str, data: dict) -> Optional[LtsVersion]:
        ...

    @abstractmethod
    async def delete(self, lts_id: str) -> bool:
        ...


class IMigrationStepRepository(ABC):
    """Interface for migration step data access."""

    @abstractmethod
    async def create(self, step: MigrationStep) -> MigrationStep:
        ...

    @abstractmethod
    async def get_by_id(self, step_id: str) -> Optional[MigrationStep]:
        ...

    @abstractmethod
    async def get_by_version_pair(
        self, from_version: str, to_version: str
    ) -> list[MigrationStep]:
        ...

    @abstractmethod
    async def delete(self, step_id: str) -> bool:
        ...


class ICompatibilityMatrixRepository(ABC):
    """Interface for compatibility matrix data access."""

    @abstractmethod
    async def create(self, entry: CompatibilityMatrix) -> CompatibilityMatrix:
        ...

    @abstractmethod
    async def get_by_id(self, entry_id: str) -> Optional[CompatibilityMatrix]:
        ...

    @abstractmethod
    async def check_compatibility(
        self, version_a: str, version_b: str
    ) -> Optional[CompatibilityMatrix]:
        ...

    @abstractmethod
    async def get_all(self) -> list[CompatibilityMatrix]:
        ...


class IDeprecationEntryRepository(ABC):
    """Interface for deprecation entry data access."""

    @abstractmethod
    async def create(self, entry: DeprecationEntry) -> DeprecationEntry:
        ...

    @abstractmethod
    async def get_by_id(self, entry_id: str) -> Optional[DeprecationEntry]:
        ...

    @abstractmethod
    async def get_by_feature(self, feature: str) -> Optional[DeprecationEntry]:
        ...

    @abstractmethod
    async def get_all(self) -> list[DeprecationEntry]:
        ...

    @abstractmethod
    async def delete(self, entry_id: str) -> bool:
        ...


class IGovernanceReviewRepository(ABC):
    """Interface for governance review data access."""

    @abstractmethod
    async def create(self, review: GovernanceReview) -> GovernanceReview:
        ...

    @abstractmethod
    async def get_by_id(self, review_id: str) -> Optional[GovernanceReview]:
        ...

    @abstractmethod
    async def get_all(self, page: int = 1, per_page: int = 20) -> dict:
        ...

    @abstractmethod
    async def get_by_area(self, area: str) -> list[GovernanceReview]:
        ...

    @abstractmethod
    async def update(self, review_id: str, data: dict) -> Optional[GovernanceReview]:
        ...

    @abstractmethod
    async def delete(self, review_id: str) -> bool:
        ...


class IGovernancePolicyRepository(ABC):
    """Interface for governance policy data access."""

    @abstractmethod
    async def create(self, policy: GovernancePolicy) -> GovernancePolicy:
        ...

    @abstractmethod
    async def get_by_id(self, policy_id: str) -> Optional[GovernancePolicy]:
        ...

    @abstractmethod
    async def get_by_area(self, area: str) -> list[GovernancePolicy]:
        ...

    @abstractmethod
    async def get_all(self) -> list[GovernancePolicy]:
        ...

    @abstractmethod
    async def update(self, policy_id: str, data: dict) -> Optional[GovernancePolicy]:
        ...


class IArchitectureAuditRepository(ABC):
    """Interface for architecture audit data access."""

    @abstractmethod
    async def create(self, audit: ArchitectureAudit) -> ArchitectureAudit:
        ...

    @abstractmethod
    async def get_by_id(self, audit_id: str) -> Optional[ArchitectureAudit]:
        ...

    @abstractmethod
    async def get_all(self, page: int = 1, per_page: int = 20) -> dict:
        ...


class IGovernanceReportRepository(ABC):
    """Interface for governance report data access."""

    @abstractmethod
    async def create(self, report: GovernanceReport) -> GovernanceReport:
        ...

    @abstractmethod
    async def get_by_id(self, report_id: str) -> Optional[GovernanceReport]:
        ...

    @abstractmethod
    async def get_all(self, page: int = 1, per_page: int = 20) -> dict:
        ...


class ICertificationRepository(ABC):
    """Interface for certification data access."""

    @abstractmethod
    async def create(self, cert: Certification) -> Certification:
        ...

    @abstractmethod
    async def get_by_id(self, cert_id: str) -> Optional[Certification]:
        ...

    @abstractmethod
    async def get_all(self, page: int = 1, per_page: int = 20) -> dict:
        ...

    @abstractmethod
    async def get_by_type(self, cert_type: str) -> list[Certification]:
        ...

    @abstractmethod
    async def update(self, cert_id: str, data: dict) -> Optional[Certification]:
        ...

    @abstractmethod
    async def delete(self, cert_id: str) -> bool:
        ...


class ICertificationRequirementRepository(ABC):
    """Interface for certification requirement data access."""

    @abstractmethod
    async def create(self, req: CertificationRequirement) -> CertificationRequirement:
        ...

    @abstractmethod
    async def get_by_id(self, req_id: str) -> Optional[CertificationRequirement]:
        ...

    @abstractmethod
    async def get_by_certification_id(
        self, cert_id: str
    ) -> list[CertificationRequirement]:
        ...

    @abstractmethod
    async def update(self, req_id: str, data: dict) -> Optional[CertificationRequirement]:
        ...


class IProductionValidationRepository(ABC):
    """Interface for production validation data access."""

    @abstractmethod
    async def create(self, val: ProductionValidation) -> ProductionValidation:
        ...

    @abstractmethod
    async def get_by_id(self, val_id: str) -> Optional[ProductionValidation]:
        ...

    @abstractmethod
    async def get_by_subsystem(self, subsystem: str) -> list[ProductionValidation]:
        ...

    @abstractmethod
    async def get_all(self) -> list[ProductionValidation]:
        ...


class IProjectHealthRepository(ABC):
    """Interface for project health data access."""

    @abstractmethod
    async def create(self, health: ProjectHealth) -> ProjectHealth:
        ...

    @abstractmethod
    async def get_latest(self) -> Optional[ProjectHealth]:
        ...

    @abstractmethod
    async def get_all(self) -> list[ProjectHealth]:
        ...


class IArchitectureDecisionRecordRepository(ABC):
    """Interface for ADR data access."""

    @abstractmethod
    async def create(self, adr: ArchitectureDecisionRecord) -> ArchitectureDecisionRecord:
        ...

    @abstractmethod
    async def get_by_id(self, adr_id: str) -> Optional[ArchitectureDecisionRecord]:
        ...

    @abstractmethod
    async def get_all(self, page: int = 1, per_page: int = 20) -> dict:
        ...

    @abstractmethod
    async def update(
        self, adr_id: str, data: dict
    ) -> Optional[ArchitectureDecisionRecord]:
        ...

    @abstractmethod
    async def delete(self, adr_id: str) -> bool:
        ...


class IMigrationHistoryRepository(ABC):
    """Interface for migration history data access."""

    @abstractmethod
    async def create(self, history: MigrationHistory) -> MigrationHistory:
        ...

    @abstractmethod
    async def get_by_id(self, history_id: str) -> Optional[MigrationHistory]:
        ...

    @abstractmethod
    async def get_all(self) -> list[MigrationHistory]:
        ...


class IReleaseHistoryRepository(ABC):
    """Interface for release history data access."""

    @abstractmethod
    async def create(self, history: ReleaseHistory) -> ReleaseHistory:
        ...

    @abstractmethod
    async def get_by_id(self, history_id: str) -> Optional[ReleaseHistory]:
        ...

    @abstractmethod
    async def get_all(self) -> list[ReleaseHistory]:
        ...


class IKnowledgeEntryRepository(ABC):
    """Interface for knowledge entry data access."""

    @abstractmethod
    async def create(self, entry: KnowledgeEntry) -> KnowledgeEntry:
        ...

    @abstractmethod
    async def get_by_id(self, entry_id: str) -> Optional[KnowledgeEntry]:
        ...

    @abstractmethod
    async def get_all(self, page: int = 1, per_page: int = 20) -> dict:
        ...

    @abstractmethod
    async def search(self, query: str) -> list[KnowledgeEntry]:
        ...

    @abstractmethod
    async def update(self, entry_id: str, data: dict) -> Optional[KnowledgeEntry]:
        ...

    @abstractmethod
    async def delete(self, entry_id: str) -> bool:
        ...


class ICodingStandardRepository(ABC):
    """Interface for coding standard data access."""

    @abstractmethod
    async def create(self, standard: CodingStandard) -> CodingStandard:
        ...

    @abstractmethod
    async def get_by_id(self, standard_id: str) -> Optional[CodingStandard]:
        ...

    @abstractmethod
    async def get_all(self) -> list[CodingStandard]:
        ...

    @abstractmethod
    async def update(
        self, standard_id: str, data: dict
    ) -> Optional[CodingStandard]:
        ...

    @abstractmethod
    async def delete(self, standard_id: str) -> bool:
        ...
