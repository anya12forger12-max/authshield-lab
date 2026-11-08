"""Developer module validators."""

from __future__ import annotations

from app.developer.domain.entities.api_explorer import ApiEndpoint
from app.developer.domain.entities.automation import AutomationWorkflow
from app.developer.domain.entities.extension import Extension
from app.developer.domain.entities.package_builder import BuildConfig, PackageManifest
from app.developer.domain.entities.sdk import PluginManifest, SdK, SdKModule, SdKTemplate
from app.developer.domain.entities.validation import ValidationReport, ValidationResult, ValidationRule


class DeveloperValidator:
    """Centralised validation logic for all Developer Platform entities."""

    def __init__(self) -> None:
        self._errors: list[str] = []
        self._warnings: list[str] = []

    # -- SDK validation ------------------------------------------------------

    def validate_sdk(self, sdk: SdK) -> dict:
        """Validate an SDK entity."""
        self._errors.clear()
        self._warnings.clear()
        if not sdk.name:
            self._errors.append("SDK name is required")
        if not sdk.name.isidentifier():
            self._warnings.append("SDK name should be a valid identifier")
        if not sdk.description:
            self._warnings.append("SDK description is recommended")
        if not sdk.author:
            self._errors.append("SDK author is required")
        if not sdk.version:
            self._errors.append("SDK version is required")
        if not sdk.min_platform_version:
            self._warnings.append("Min platform version should be set")
        return {"valid": len(self._errors) == 0, "errors": list(self._errors), "warnings": list(self._warnings)}

    def validate_sdk_module(self, module: SdKModule) -> dict:
        """Validate an SDK module."""
        self._errors.clear()
        self._warnings.clear()
        if not module.name:
            self._errors.append("Module name is required")
        if not module.sdk_id:
            self._errors.append("Module must belong to an SDK (sdk_id required)")
        if not module.version:
            self._warnings.append("Module version is recommended")
        return {"valid": len(self._errors) == 0, "errors": list(self._errors), "warnings": list(self._warnings)}

    # -- Plugin manifest validation ------------------------------------------

    def validate_plugin_manifest(self, manifest: PluginManifest) -> dict:
        """Validate a plugin manifest."""
        self._errors.clear()
        self._warnings.clear()
        if not manifest.name:
            self._errors.append("Manifest name is required")
        if not manifest.version:
            self._errors.append("Manifest version is required")
        if not manifest.author:
            self._warnings.append("Manifest author is recommended")
        if not manifest.license:
            self._warnings.append("Manifest license is recommended")
        for dep in manifest.dependencies:
            if ":" not in dep and "@" not in dep:
                self._warnings.append(f"Dependency '{dep}' may not follow expected format")
        return {"valid": len(self._errors) == 0, "errors": list(self._errors), "warnings": list(self._warnings)}

    # -- SDK template validation ---------------------------------------------

    def validate_sdk_template(self, template: SdKTemplate) -> dict:
        """Validate an SDK template."""
        self._errors.clear()
        self._warnings.clear()
        if not template.name:
            self._errors.append("Template name is required")
        if not template.template_type:
            self._warnings.append("Template type should be specified")
        if not template.content:
            self._warnings.append("Template content is empty")
        if not template.version:
            self._warnings.append("Template version is recommended")
        return {"valid": len(self._errors) == 0, "errors": list(self._errors), "warnings": list(self._warnings)}

    # -- Extension validation ------------------------------------------------

    def validate_extension(self, extension: Extension) -> dict:
        """Validate an Extension entity."""
        self._errors.clear()
        self._warnings.clear()
        if not extension.name:
            self._errors.append("Extension name is required")
        if not extension.version:
            self._errors.append("Extension version is required")
        if not extension.author:
            self._errors.append("Extension author is required")
        if not extension.description:
            self._warnings.append("Extension description is recommended")
        if not extension.extension_type:
            self._errors.append("Extension type is required")
        if not extension.compatibility:
            self._warnings.append("Compatibility string should be set")
        for perm in extension.permissions:
            if not perm:
                self._warnings.append("Empty permission string found")
        return {"valid": len(self._errors) == 0, "errors": list(self._errors), "warnings": list(self._warnings)}

    # -- Automation workflow validation --------------------------------------

    def validate_workflow(self, workflow: AutomationWorkflow) -> dict:
        """Validate an AutomationWorkflow entity."""
        self._errors.clear()
        self._warnings.clear()
        if not workflow.name:
            self._errors.append("Workflow name is required")
        if not workflow.workflow_type:
            self._warnings.append("Workflow type should be specified")
        if not workflow.steps:
            self._warnings.append("Workflow has no steps")
        for step in workflow.steps:
            if not step.action:
                self._errors.append(f"Step '{step.id}' has no action defined")
            if step.on_failure not in ("stop", "continue", "retry", "skip"):
                self._warnings.append(f"Step '{step.id}' has unexpected on_failure value: {step.on_failure}")
        return {"valid": len(self._errors) == 0, "errors": list(self._errors), "warnings": list(self._warnings)}

    # -- API endpoint validation ---------------------------------------------

    def validate_api_endpoint(self, endpoint: ApiEndpoint) -> dict:
        """Validate an ApiEndpoint entity."""
        self._errors.clear()
        self._warnings.clear()
        if not endpoint.path:
            self._errors.append("Endpoint path is required")
        elif not endpoint.path.startswith("/"):
            self._errors.append("Endpoint path must start with /")
        if not endpoint.method:
            self._errors.append("HTTP method is required")
        elif endpoint.method not in ("GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"):
            self._warnings.append(f"Unusual HTTP method: {endpoint.method}")
        if not endpoint.description:
            self._warnings.append("Endpoint description is recommended")
        if not endpoint.version:
            self._warnings.append("Endpoint version should be set")
        for param in endpoint.parameters:
            if not param.name:
                self._errors.append("Parameter name is required")
            if param.type not in ("string", "integer", "boolean", "number", "array", "object"):
                self._warnings.append(f"Parameter '{param.name}' has unusual type: {param.type}")
        return {"valid": len(self._errors) == 0, "errors": list(self._errors), "warnings": list(self._warnings)}

    # -- Package manifest validation -----------------------------------------

    def validate_package_manifest(self, manifest: PackageManifest) -> dict:
        """Validate a PackageManifest entity."""
        self._errors.clear()
        self._warnings.clear()
        if not manifest.name:
            self._errors.append("Package name is required")
        if not manifest.version:
            self._errors.append("Package version is required")
        if not manifest.author:
            self._warnings.append("Package author is recommended")
        if not manifest.license:
            self._warnings.append("Package license is recommended")
        if not manifest.compatibility:
            self._warnings.append("Compatibility string should be set")
        if manifest.bundle_size < 0:
            self._errors.append("Bundle size must be non-negative")
        return {"valid": len(self._errors) == 0, "errors": list(self._errors), "warnings": list(self._warnings)}

    # -- Build config validation ---------------------------------------------

    def validate_build_config(self, config: BuildConfig) -> dict:
        """Validate a BuildConfig entity."""
        self._errors.clear()
        self._warnings.clear()
        if not config.manifest_id:
            self._errors.append("Build config must reference a manifest_id")
        if not config.sources:
            self._warnings.append("No source paths specified")
        if config.output_format not in ("zip", "tar.gz", "wheel", "egg"):
            self._warnings.append(f"Unusual output format: {config.output_format}")
        return {"valid": len(self._errors) == 0, "errors": list(self._errors), "warnings": list(self._warnings)}

    # -- Validation rule & result validation ---------------------------------

    def validate_validation_rule(self, rule: ValidationRule) -> dict:
        """Validate a ValidationRule entity."""
        self._errors.clear()
        self._warnings.clear()
        if not rule.name:
            self._errors.append("Rule name is required")
        if not rule.rule_type:
            self._warnings.append("Rule type should be specified")
        if rule.severity not in ("info", "warning", "error", "critical"):
            self._warnings.append(f"Unusual severity: {rule.severity}")
        if not rule.check_fn:
            self._warnings.append("Check function identifier is empty")
        return {"valid": len(self._errors) == 0, "errors": list(self._errors), "warnings": list(self._warnings)}

    def validate_validation_result(self, result: ValidationResult) -> dict:
        """Validate a ValidationResult entity."""
        self._errors.clear()
        self._warnings.clear()
        if not result.rule_id:
            self._errors.append("Result must reference a rule_id")
        if not result.target_id:
            self._errors.append("Result must reference a target_id")
        if not result.target_type:
            self._errors.append("Result must specify a target_type")
        if not result.message:
            self._warnings.append("Result message is empty")
        return {"valid": len(self._errors) == 0, "errors": list(self._errors), "warnings": list(self._warnings)}

    def validate_validation_report(self, report: ValidationReport) -> dict:
        """Validate a ValidationReport entity."""
        self._errors.clear()
        self._warnings.clear()
        if not report.name:
            self._errors.append("Report name is required")
        if not report.target_type:
            self._errors.append("Report target_type is required")
        if not report.results:
            self._warnings.append("Report has no results")
        if report.overall_status not in ("pending", "passed", "failed", "warning", "empty"):
            self._warnings.append(f"Unusual overall_status: {report.overall_status}")
        if not (0.0 <= report.score <= 1.0):
            self._errors.append("Score must be between 0.0 and 1.0")
        return {"valid": len(self._errors) == 0, "errors": list(self._errors), "warnings": list(self._warnings)}
