"""In-memory repository implementations for the Developer Platform."""

from __future__ import annotations

from app.developer.domain.entities.api_explorer import (
    ApiDocumentation,
    ApiEndpoint,
    ApiSchema,
)
from app.developer.domain.entities.automation import AutomationWorkflow, WorkflowRun
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
from app.developer.domain.interfaces.developer_interfaces import (
    AbstractApiDocumentationRepository,
    AbstractApiEndpointRepository,
    AbstractApiSchemaRepository,
    AbstractAutomationWorkflowRepository,
    AbstractBuildConfigRepository,
    AbstractBuildResultRepository,
    AbstractExtensionRepository,
    AbstractExtensionVersionRepository,
    AbstractInstalledExtensionRepository,
    AbstractPackageManifestRepository,
    AbstractPluginManifestRepository,
    AbstractSdKModuleRepository,
    AbstractSdKRepository,
    AbstractSdKTemplateRepository,
    AbstractValidationReportRepository,
    AbstractValidationResultRepository,
    AbstractValidationRuleRepository,
    AbstractWorkflowRunRepository,
)


# ---------------------------------------------------------------------------
# SDK Repositories
# ---------------------------------------------------------------------------


class InMemorySdKRepository(AbstractSdKRepository):
    """In-memory implementation of the SDK repository."""

    def __init__(self) -> None:
        self._store: dict[str, SdK] = {}

    def get_by_id(self, sdk_id: str) -> SdK | None:
        return self._store.get(sdk_id)

    def get_by_name(self, name: str) -> SdK | None:
        for sdk in self._store.values():
            if sdk.name == name:
                return sdk
        return None

    def list_all(self) -> list[SdK]:
        return list(self._store.values())

    def save(self, sdk: SdK) -> SdK:
        self._store[sdk.id] = sdk
        return sdk

    def delete(self, sdk_id: str) -> bool:
        return self._store.pop(sdk_id, None) is not None


class InMemorySdKModuleRepository(AbstractSdKModuleRepository):
    """In-memory implementation of the SDK module repository."""

    def __init__(self) -> None:
        self._store: dict[str, SdKModule] = {}

    def get_by_id(self, module_id: str) -> SdKModule | None:
        return self._store.get(module_id)

    def list_by_sdk(self, sdk_id: str) -> list[SdKModule]:
        return [m for m in self._store.values() if m.sdk_id == sdk_id]

    def save(self, module: SdKModule) -> SdKModule:
        self._store[module.id] = module
        return module

    def delete(self, module_id: str) -> bool:
        return self._store.pop(module_id, None) is not None


class InMemoryPluginManifestRepository(AbstractPluginManifestRepository):
    """In-memory implementation of the plugin manifest repository."""

    def __init__(self) -> None:
        self._store: dict[str, PluginManifest] = {}

    def get_by_id(self, manifest_id: str) -> PluginManifest | None:
        return self._store.get(manifest_id)

    def get_by_name(self, name: str) -> PluginManifest | None:
        for m in self._store.values():
            if m.name == name:
                return m
        return None

    def list_all(self) -> list[PluginManifest]:
        return list(self._store.values())

    def save(self, manifest: PluginManifest) -> PluginManifest:
        self._store[manifest.id] = manifest
        return manifest

    def delete(self, manifest_id: str) -> bool:
        return self._store.pop(manifest_id, None) is not None


class InMemorySdKTemplateRepository(AbstractSdKTemplateRepository):
    """In-memory implementation of the SDK template repository."""

    def __init__(self) -> None:
        self._store: dict[str, SdKTemplate] = {}

    def get_by_id(self, template_id: str) -> SdKTemplate | None:
        return self._store.get(template_id)

    def list_by_category(self, category: str) -> list[SdKTemplate]:
        return [t for t in self._store.values() if t.category == category]

    def list_all(self) -> list[SdKTemplate]:
        return list(self._store.values())

    def save(self, template: SdKTemplate) -> SdKTemplate:
        self._store[template.id] = template
        return template

    def delete(self, template_id: str) -> bool:
        return self._store.pop(template_id, None) is not None


# ---------------------------------------------------------------------------
# Extension Repositories
# ---------------------------------------------------------------------------


class InMemoryExtensionRepository(AbstractExtensionRepository):
    """In-memory implementation of the Extension repository."""

    def __init__(self) -> None:
        self._store: dict[str, Extension] = {}

    def get_by_id(self, extension_id: str) -> Extension | None:
        return self._store.get(extension_id)

    def get_by_name(self, name: str) -> Extension | None:
        for ext in self._store.values():
            if ext.name == name:
                return ext
        return None

    def list_all(self) -> list[Extension]:
        return list(self._store.values())

    def list_by_type(self, extension_type: str) -> list[Extension]:
        return [e for e in self._store.values() if e.extension_type.value == extension_type]

    def save(self, extension: Extension) -> Extension:
        self._store[extension.id] = extension
        return extension

    def delete(self, extension_id: str) -> bool:
        return self._store.pop(extension_id, None) is not None

    def search(self, query: str) -> list[Extension]:
        q = query.lower()
        return [
            e for e in self._store.values()
            if q in e.name.lower() or q in e.description.lower()
        ]


class InMemoryExtensionVersionRepository(AbstractExtensionVersionRepository):
    """In-memory implementation of the ExtensionVersion repository."""

    def __init__(self) -> None:
        self._store: dict[str, ExtensionVersion] = {}

    def get_by_id(self, version_id: str) -> ExtensionVersion | None:
        return self._store.get(version_id)

    def list_by_extension(self, extension_id: str) -> list[ExtensionVersion]:
        return [v for v in self._store.values() if v.extension_id == extension_id]

    def get_latest(self, extension_id: str) -> ExtensionVersion | None:
        versions = self.list_by_extension(extension_id)
        if not versions:
            return None
        return max(versions, key=lambda v: v.version)

    def save(self, version: ExtensionVersion) -> ExtensionVersion:
        self._store[version.id] = version
        return version


class InMemoryInstalledExtensionRepository(AbstractInstalledExtensionRepository):
    """In-memory implementation of the InstalledExtension repository."""

    def __init__(self) -> None:
        self._store: dict[str, InstalledExtension] = {}

    def get_by_id(self, installed_id: str) -> InstalledExtension | None:
        return self._store.get(installed_id)

    def get_by_extension(self, extension_id: str) -> InstalledExtension | None:
        for inst in self._store.values():
            if inst.extension_id == extension_id:
                return inst
        return None

    def list_all(self) -> list[InstalledExtension]:
        return list(self._store.values())

    def save(self, installed: InstalledExtension) -> InstalledExtension:
        self._store[installed.id] = installed
        return installed

    def delete(self, installed_id: str) -> bool:
        return self._store.pop(installed_id, None) is not None


# ---------------------------------------------------------------------------
# Automation Repositories
# ---------------------------------------------------------------------------


class InMemoryAutomationWorkflowRepository(AbstractAutomationWorkflowRepository):
    """In-memory implementation of the AutomationWorkflow repository."""

    def __init__(self) -> None:
        self._store: dict[str, AutomationWorkflow] = {}

    def get_by_id(self, workflow_id: str) -> AutomationWorkflow | None:
        return self._store.get(workflow_id)

    def list_all(self) -> list[AutomationWorkflow]:
        return list(self._store.values())

    def list_enabled(self) -> list[AutomationWorkflow]:
        return [w for w in self._store.values() if w.enabled]

    def save(self, workflow: AutomationWorkflow) -> AutomationWorkflow:
        self._store[workflow.id] = workflow
        return workflow

    def delete(self, workflow_id: str) -> bool:
        return self._store.pop(workflow_id, None) is not None


class InMemoryWorkflowRunRepository(AbstractWorkflowRunRepository):
    """In-memory implementation of the WorkflowRun repository."""

    def __init__(self) -> None:
        self._store: dict[str, WorkflowRun] = {}

    def get_by_id(self, run_id: str) -> WorkflowRun | None:
        return self._store.get(run_id)

    def list_by_workflow(self, workflow_id: str) -> list[WorkflowRun]:
        return [r for r in self._store.values() if r.workflow_id == workflow_id]

    def save(self, run: WorkflowRun) -> WorkflowRun:
        self._store[run.id] = run
        return run


# ---------------------------------------------------------------------------
# API Explorer Repositories
# ---------------------------------------------------------------------------


class InMemoryApiEndpointRepository(AbstractApiEndpointRepository):
    """In-memory implementation of the ApiEndpoint repository."""

    def __init__(self) -> None:
        self._store: dict[str, ApiEndpoint] = {}

    def get_by_id(self, endpoint_id: str) -> ApiEndpoint | None:
        return self._store.get(endpoint_id)

    def get_by_path(self, path: str, method: str) -> ApiEndpoint | None:
        method_upper = method.upper()
        for ep in self._store.values():
            if ep.path == path and ep.method == method_upper:
                return ep
        return None

    def list_all(self) -> list[ApiEndpoint]:
        return list(self._store.values())

    def list_by_category(self, category: str) -> list[ApiEndpoint]:
        return [ep for ep in self._store.values() if ep.category == category]

    def save(self, endpoint: ApiEndpoint) -> ApiEndpoint:
        self._store[endpoint.id] = endpoint
        return endpoint

    def delete(self, endpoint_id: str) -> bool:
        return self._store.pop(endpoint_id, None) is not None

    def search(self, query: str) -> list[ApiEndpoint]:
        q = query.lower()
        return [
            ep for ep in self._store.values()
            if q in ep.path.lower() or q in ep.description.lower()
        ]


class InMemoryApiSchemaRepository(AbstractApiSchemaRepository):
    """In-memory implementation of the ApiSchema repository."""

    def __init__(self) -> None:
        self._store: dict[str, ApiSchema] = {}

    def get_by_id(self, schema_id: str) -> ApiSchema | None:
        return self._store.get(schema_id)

    def get_by_name(self, name: str) -> ApiSchema | None:
        for s in self._store.values():
            if s.name == name:
                return s
        return None

    def list_all(self) -> list[ApiSchema]:
        return list(self._store.values())

    def save(self, schema: ApiSchema) -> ApiSchema:
        self._store[schema.id] = schema
        return schema

    def delete(self, schema_id: str) -> bool:
        return self._store.pop(schema_id, None) is not None


class InMemoryApiDocumentationRepository(AbstractApiDocumentationRepository):
    """In-memory implementation of the ApiDocumentation repository."""

    def __init__(self) -> None:
        self._store: dict[str, ApiDocumentation] = {}

    def get_by_id(self, doc_id: str) -> ApiDocumentation | None:
        return self._store.get(doc_id)

    def get_by_endpoint(self, endpoint_id: str) -> ApiDocumentation | None:
        for doc in self._store.values():
            if doc.endpoint_id == endpoint_id:
                return doc
        return None

    def save(self, doc: ApiDocumentation) -> ApiDocumentation:
        self._store[doc.id] = doc
        return doc

    def delete(self, doc_id: str) -> bool:
        return self._store.pop(doc_id, None) is not None


# ---------------------------------------------------------------------------
# Validation Repositories
# ---------------------------------------------------------------------------


class InMemoryValidationRuleRepository(AbstractValidationRuleRepository):
    """In-memory implementation of the ValidationRule repository."""

    def __init__(self) -> None:
        self._store: dict[str, ValidationRule] = {}

    def get_by_id(self, rule_id: str) -> ValidationRule | None:
        return self._store.get(rule_id)

    def list_all(self) -> list[ValidationRule]:
        return list(self._store.values())

    def list_by_type(self, rule_type: str) -> list[ValidationRule]:
        return [r for r in self._store.values() if r.rule_type == rule_type]

    def save(self, rule: ValidationRule) -> ValidationRule:
        self._store[rule.id] = rule
        return rule

    def delete(self, rule_id: str) -> bool:
        return self._store.pop(rule_id, None) is not None


class InMemoryValidationResultRepository(AbstractValidationResultRepository):
    """In-memory implementation of the ValidationResult repository."""

    def __init__(self) -> None:
        self._store: dict[str, ValidationResult] = {}

    def get_by_id(self, result_id: str) -> ValidationResult | None:
        return self._store.get(result_id)

    def list_by_target(self, target_id: str, target_type: str) -> list[ValidationResult]:
        return [
            r for r in self._store.values()
            if r.target_id == target_id and r.target_type == target_type
        ]

    def save(self, result: ValidationResult) -> ValidationResult:
        self._store[result.id] = result
        return result


class InMemoryValidationReportRepository(AbstractValidationReportRepository):
    """In-memory implementation of the ValidationReport repository."""

    def __init__(self) -> None:
        self._store: dict[str, ValidationReport] = {}

    def get_by_id(self, report_id: str) -> ValidationReport | None:
        return self._store.get(report_id)

    def list_all(self) -> list[ValidationReport]:
        return list(self._store.values())

    def save(self, report: ValidationReport) -> ValidationReport:
        self._store[report.id] = report
        return report

    def delete(self, report_id: str) -> bool:
        return self._store.pop(report_id, None) is not None


# ---------------------------------------------------------------------------
# Package Builder Repositories
# ---------------------------------------------------------------------------


class InMemoryPackageManifestRepository(AbstractPackageManifestRepository):
    """In-memory implementation of the PackageManifest repository."""

    def __init__(self) -> None:
        self._store: dict[str, PackageManifest] = {}

    def get_by_id(self, manifest_id: str) -> PackageManifest | None:
        return self._store.get(manifest_id)

    def get_by_name(self, name: str) -> PackageManifest | None:
        for m in self._store.values():
            if m.name == name:
                return m
        return None

    def list_all(self) -> list[PackageManifest]:
        return list(self._store.values())

    def save(self, manifest: PackageManifest) -> PackageManifest:
        self._store[manifest.id] = manifest
        return manifest

    def delete(self, manifest_id: str) -> bool:
        return self._store.pop(manifest_id, None) is not None


class InMemoryBuildConfigRepository(AbstractBuildConfigRepository):
    """In-memory implementation of the BuildConfig repository."""

    def __init__(self) -> None:
        self._store: dict[str, BuildConfig] = {}

    def get_by_id(self, config_id: str) -> BuildConfig | None:
        return self._store.get(config_id)

    def list_by_manifest(self, manifest_id: str) -> list[BuildConfig]:
        return [c for c in self._store.values() if c.manifest_id == manifest_id]

    def save(self, config: BuildConfig) -> BuildConfig:
        self._store[config.id] = config
        return config

    def delete(self, config_id: str) -> bool:
        return self._store.pop(config_id, None) is not None


class InMemoryBuildResultRepository(AbstractBuildResultRepository):
    """In-memory implementation of the BuildResult repository."""

    def __init__(self) -> None:
        self._store: dict[str, BuildResult] = {}

    def get_by_id(self, result_id: str) -> BuildResult | None:
        return self._store.get(result_id)

    def list_by_config(self, config_id: str) -> list[BuildResult]:
        return [r for r in self._store.values() if r.config_id == config_id]

    def save(self, result: BuildResult) -> BuildResult:
        self._store[result.id] = result
        return result
