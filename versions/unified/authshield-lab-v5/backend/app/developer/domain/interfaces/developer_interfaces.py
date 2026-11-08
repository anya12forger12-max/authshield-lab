"""Abstract repository interfaces for the Developer Platform."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

    from app.developer.domain.entities.api_explorer import (
        ApiDocumentation,
        ApiEndpoint,
        ApiSchema,
    )
    from app.developer.domain.entities.automation import (
        AutomationWorkflow,
        WorkflowRun,
    )
    from app.developer.domain.entities.extension import (
        Extension,
        ExtensionVersion,
        InstalledExtension,
    )
    from app.developer.domain.entities.package_builder import (
        BuildConfig,
        BuildResult,
        PackageManifest,
    )
    from app.developer.domain.entities.sdk import PluginManifest, SdK, SdKModule, SdKTemplate
    from app.developer.domain.entities.validation import (
        ValidationReport,
        ValidationResult,
        ValidationRule,
    )


# ---------------------------------------------------------------------------
# SDK Repository
# ---------------------------------------------------------------------------


class AbstractSdKRepository(ABC):
    """Interface for SDK persistence."""

    @abstractmethod
    def get_by_id(self, sdk_id: str) -> SdK | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_name(self, name: str) -> SdK | None:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[SdK]:
        raise NotImplementedError

    @abstractmethod
    def save(self, sdk: SdK) -> SdK:
        raise NotImplementedError

    @abstractmethod
    def delete(self, sdk_id: str) -> bool:
        raise NotImplementedError


class AbstractSdKModuleRepository(ABC):
    """Interface for SDK module persistence."""

    @abstractmethod
    def get_by_id(self, module_id: str) -> SdKModule | None:
        raise NotImplementedError

    @abstractmethod
    def list_by_sdk(self, sdk_id: str) -> list[SdKModule]:
        raise NotImplementedError

    @abstractmethod
    def save(self, module: SdKModule) -> SdKModule:
        raise NotImplementedError

    @abstractmethod
    def delete(self, module_id: str) -> bool:
        raise NotImplementedError


class AbstractPluginManifestRepository(ABC):
    """Interface for plugin manifest persistence."""

    @abstractmethod
    def get_by_id(self, manifest_id: str) -> PluginManifest | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_name(self, name: str) -> PluginManifest | None:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[PluginManifest]:
        raise NotImplementedError

    @abstractmethod
    def save(self, manifest: PluginManifest) -> PluginManifest:
        raise NotImplementedError

    @abstractmethod
    def delete(self, manifest_id: str) -> bool:
        raise NotImplementedError


class AbstractSdKTemplateRepository(ABC):
    """Interface for SDK template persistence."""

    @abstractmethod
    def get_by_id(self, template_id: str) -> SdKTemplate | None:
        raise NotImplementedError

    @abstractmethod
    def list_by_category(self, category: str) -> list[SdKTemplate]:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[SdKTemplate]:
        raise NotImplementedError

    @abstractmethod
    def save(self, template: SdKTemplate) -> SdKTemplate:
        raise NotImplementedError

    @abstractmethod
    def delete(self, template_id: str) -> bool:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Extension Repository
# ---------------------------------------------------------------------------


class AbstractExtensionRepository(ABC):
    """Interface for Extension persistence."""

    @abstractmethod
    def get_by_id(self, extension_id: str) -> Extension | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_name(self, name: str) -> Extension | None:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[Extension]:
        raise NotImplementedError

    @abstractmethod
    def list_by_type(self, extension_type: str) -> list[Extension]:
        raise NotImplementedError

    @abstractmethod
    def save(self, extension: Extension) -> Extension:
        raise NotImplementedError

    @abstractmethod
    def delete(self, extension_id: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def search(self, query: str) -> list[Extension]:
        raise NotImplementedError


class AbstractExtensionVersionRepository(ABC):
    """Interface for ExtensionVersion persistence."""

    @abstractmethod
    def get_by_id(self, version_id: str) -> ExtensionVersion | None:
        raise NotImplementedError

    @abstractmethod
    def list_by_extension(self, extension_id: str) -> list[ExtensionVersion]:
        raise NotImplementedError

    @abstractmethod
    def get_latest(self, extension_id: str) -> ExtensionVersion | None:
        raise NotImplementedError

    @abstractmethod
    def save(self, version: ExtensionVersion) -> ExtensionVersion:
        raise NotImplementedError


class AbstractInstalledExtensionRepository(ABC):
    """Interface for InstalledExtension persistence."""

    @abstractmethod
    def get_by_id(self, installed_id: str) -> InstalledExtension | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_extension(self, extension_id: str) -> InstalledExtension | None:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[InstalledExtension]:
        raise NotImplementedError

    @abstractmethod
    def save(self, installed: InstalledExtension) -> InstalledExtension:
        raise NotImplementedError

    @abstractmethod
    def delete(self, installed_id: str) -> bool:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Automation Repository
# ---------------------------------------------------------------------------


class AbstractAutomationWorkflowRepository(ABC):
    """Interface for AutomationWorkflow persistence."""

    @abstractmethod
    def get_by_id(self, workflow_id: str) -> AutomationWorkflow | None:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[AutomationWorkflow]:
        raise NotImplementedError

    @abstractmethod
    def list_enabled(self) -> list[AutomationWorkflow]:
        raise NotImplementedError

    @abstractmethod
    def save(self, workflow: AutomationWorkflow) -> AutomationWorkflow:
        raise NotImplementedError

    @abstractmethod
    def delete(self, workflow_id: str) -> bool:
        raise NotImplementedError


class AbstractWorkflowRunRepository(ABC):
    """Interface for WorkflowRun persistence."""

    @abstractmethod
    def get_by_id(self, run_id: str) -> WorkflowRun | None:
        raise NotImplementedError

    @abstractmethod
    def list_by_workflow(self, workflow_id: str) -> list[WorkflowRun]:
        raise NotImplementedError

    @abstractmethod
    def save(self, run: WorkflowRun) -> WorkflowRun:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# API Explorer Repository
# ---------------------------------------------------------------------------


class AbstractApiEndpointRepository(ABC):
    """Interface for ApiEndpoint persistence."""

    @abstractmethod
    def get_by_id(self, endpoint_id: str) -> ApiEndpoint | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_path(self, path: str, method: str) -> ApiEndpoint | None:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[ApiEndpoint]:
        raise NotImplementedError

    @abstractmethod
    def list_by_category(self, category: str) -> list[ApiEndpoint]:
        raise NotImplementedError

    @abstractmethod
    def save(self, endpoint: ApiEndpoint) -> ApiEndpoint:
        raise NotImplementedError

    @abstractmethod
    def delete(self, endpoint_id: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def search(self, query: str) -> list[ApiEndpoint]:
        raise NotImplementedError


class AbstractApiSchemaRepository(ABC):
    """Interface for ApiSchema persistence."""

    @abstractmethod
    def get_by_id(self, schema_id: str) -> ApiSchema | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_name(self, name: str) -> ApiSchema | None:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[ApiSchema]:
        raise NotImplementedError

    @abstractmethod
    def save(self, schema: ApiSchema) -> ApiSchema:
        raise NotImplementedError

    @abstractmethod
    def delete(self, schema_id: str) -> bool:
        raise NotImplementedError


class AbstractApiDocumentationRepository(ABC):
    """Interface for ApiDocumentation persistence."""

    @abstractmethod
    def get_by_id(self, doc_id: str) -> ApiDocumentation | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_endpoint(self, endpoint_id: str) -> ApiDocumentation | None:
        raise NotImplementedError

    @abstractmethod
    def save(self, doc: ApiDocumentation) -> ApiDocumentation:
        raise NotImplementedError

    @abstractmethod
    def delete(self, doc_id: str) -> bool:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Validation Repository
# ---------------------------------------------------------------------------


class AbstractValidationRuleRepository(ABC):
    """Interface for ValidationRule persistence."""

    @abstractmethod
    def get_by_id(self, rule_id: str) -> ValidationRule | None:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[ValidationRule]:
        raise NotImplementedError

    @abstractmethod
    def list_by_type(self, rule_type: str) -> list[ValidationRule]:
        raise NotImplementedError

    @abstractmethod
    def save(self, rule: ValidationRule) -> ValidationRule:
        raise NotImplementedError

    @abstractmethod
    def delete(self, rule_id: str) -> bool:
        raise NotImplementedError


class AbstractValidationResultRepository(ABC):
    """Interface for ValidationResult persistence."""

    @abstractmethod
    def get_by_id(self, result_id: str) -> ValidationResult | None:
        raise NotImplementedError

    @abstractmethod
    def list_by_target(self, target_id: str, target_type: str) -> list[ValidationResult]:
        raise NotImplementedError

    @abstractmethod
    def save(self, result: ValidationResult) -> ValidationResult:
        raise NotImplementedError


class AbstractValidationReportRepository(ABC):
    """Interface for ValidationReport persistence."""

    @abstractmethod
    def get_by_id(self, report_id: str) -> ValidationReport | None:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[ValidationReport]:
        raise NotImplementedError

    @abstractmethod
    def save(self, report: ValidationReport) -> ValidationReport:
        raise NotImplementedError

    @abstractmethod
    def delete(self, report_id: str) -> bool:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Package Builder Repository
# ---------------------------------------------------------------------------


class AbstractPackageManifestRepository(ABC):
    """Interface for PackageManifest persistence."""

    @abstractmethod
    def get_by_id(self, manifest_id: str) -> PackageManifest | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_name(self, name: str) -> PackageManifest | None:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[PackageManifest]:
        raise NotImplementedError

    @abstractmethod
    def save(self, manifest: PackageManifest) -> PackageManifest:
        raise NotImplementedError

    @abstractmethod
    def delete(self, manifest_id: str) -> bool:
        raise NotImplementedError


class AbstractBuildConfigRepository(ABC):
    """Interface for BuildConfig persistence."""

    @abstractmethod
    def get_by_id(self, config_id: str) -> BuildConfig | None:
        raise NotImplementedError

    @abstractmethod
    def list_by_manifest(self, manifest_id: str) -> list[BuildConfig]:
        raise NotImplementedError

    @abstractmethod
    def save(self, config: BuildConfig) -> BuildConfig:
        raise NotImplementedError

    @abstractmethod
    def delete(self, config_id: str) -> bool:
        raise NotImplementedError


class AbstractBuildResultRepository(ABC):
    """Interface for BuildResult persistence."""

    @abstractmethod
    def get_by_id(self, result_id: str) -> BuildResult | None:
        raise NotImplementedError

    @abstractmethod
    def list_by_config(self, config_id: str) -> list[BuildResult]:
        raise NotImplementedError

    @abstractmethod
    def save(self, result: BuildResult) -> BuildResult:
        raise NotImplementedError
