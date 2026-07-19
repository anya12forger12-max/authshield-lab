"""Domain events for the Developer Platform module."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone


class _BaseEvent:
    """Shared event fields."""

    def __init__(self, name: str, payload: dict | None = None) -> None:
        self.event_id: str = str(uuid.uuid4())
        self.name: str = name
        self.timestamp: datetime = datetime.now(timezone.utc)
        self.payload: dict = payload if payload is not None else {}

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "event_id": self.event_id,
            "name": self.name,
            "timestamp": self.timestamp.isoformat(),
            "payload": dict(self.payload),
        }


class ExtensionInstalled(_BaseEvent):
    """Emitted when an extension is successfully installed."""

    def __init__(
        self,
        extension_id: str,
        extension_name: str,
        version: str,
        installed_by: str = "",
    ) -> None:
        super().__init__(
            name="extension.installed",
            payload={
                "extension_id": extension_id,
                "extension_name": extension_name,
                "version": version,
                "installed_by": installed_by,
            },
        )
        self.extension_id: str = extension_id
        self.extension_name: str = extension_name
        self.version: str = version


class ExtensionRemoved(_BaseEvent):
    """Emitted when an extension is uninstalled."""

    def __init__(
        self,
        extension_id: str,
        extension_name: str,
        removed_by: str = "",
    ) -> None:
        super().__init__(
            name="extension.removed",
            payload={
                "extension_id": extension_id,
                "extension_name": extension_name,
                "removed_by": removed_by,
            },
        )
        self.extension_id: str = extension_id
        self.extension_name: str = extension_name


class ExtensionUpdated(_BaseEvent):
    """Emitted when an extension is updated to a new version."""

    def __init__(
        self,
        extension_id: str,
        extension_name: str,
        old_version: str,
        new_version: str,
    ) -> None:
        super().__init__(
            name="extension.updated",
            payload={
                "extension_id": extension_id,
                "extension_name": extension_name,
                "old_version": old_version,
                "new_version": new_version,
            },
        )
        self.extension_id: str = extension_id
        self.old_version: str = old_version
        self.new_version: str = new_version


class WorkflowStarted(_BaseEvent):
    """Emitted when an automation workflow begins execution."""

    def __init__(self, workflow_id: str, workflow_name: str, run_id: str) -> None:
        super().__init__(
            name="workflow.started",
            payload={
                "workflow_id": workflow_id,
                "workflow_name": workflow_name,
                "run_id": run_id,
            },
        )
        self.workflow_id: str = workflow_id
        self.run_id: str = run_id


class WorkflowCompleted(_BaseEvent):
    """Emitted when an automation workflow finishes execution."""

    def __init__(
        self,
        workflow_id: str,
        run_id: str,
        status: str,
        duration_seconds: float,
    ) -> None:
        super().__init__(
            name="workflow.completed",
            payload={
                "workflow_id": workflow_id,
                "run_id": run_id,
                "status": status,
                "duration_seconds": duration_seconds,
            },
        )
        self.workflow_id: str = workflow_id
        self.run_id: str = run_id
        self.status: str = status


class PackageBuilt(_BaseEvent):
    """Emitted when a package build completes."""

    def __init__(
        self,
        manifest_id: str,
        package_name: str,
        build_result_id: str,
        status: str,
    ) -> None:
        super().__init__(
            name="package.built",
            payload={
                "manifest_id": manifest_id,
                "package_name": package_name,
                "build_result_id": build_result_id,
                "status": status,
            },
        )
        self.manifest_id: str = manifest_id
        self.build_result_id: str = build_result_id


class ValidationCompleted(_BaseEvent):
    """Emitted when a validation report is finalized."""

    def __init__(
        self,
        report_id: str,
        target_type: str,
        target_id: str,
        overall_status: str,
        score: float,
    ) -> None:
        super().__init__(
            name="validation.completed",
            payload={
                "report_id": report_id,
                "target_type": target_type,
                "target_id": target_id,
                "overall_status": overall_status,
                "score": score,
            },
        )
        self.report_id: str = report_id
        self.overall_status: str = overall_status
        self.score: float = score


class ApiEndpointRegistered(_BaseEvent):
    """Emitted when a new API endpoint is registered in the explorer."""

    def __init__(
        self,
        endpoint_id: str,
        path: str,
        method: str,
        category: str,
    ) -> None:
        super().__init__(
            name="api_endpoint.registered",
            payload={
                "endpoint_id": endpoint_id,
                "path": path,
                "method": method,
                "category": category,
            },
        )
        self.endpoint_id: str = endpoint_id
        self.path: str = path
        self.method: str = method
