"""Academic hub domain entities."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum


class ProjectStatus(str, Enum):
    active = "active"
    paused = "paused"
    completed = "completed"


class ReviewStatus(str, Enum):
    draft = "draft"
    in_review = "in_review"
    approved = "approved"
    rejected = "rejected"


class InstitutionalProject:
    def __init__(
        self,
        name: str,
        description: str,
        department: str,
        lead: str,
        status: ProjectStatus = ProjectStatus.active,
        members: list[str] | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.status = status
        self.department = department
        self.lead = lead
        self.members = members or []
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)


class SharedCurriculumPackage:
    def __init__(
        self,
        title: str,
        source_institution: str,
        version: str,
        content_type: str,
        checksum: str,
        signature: str,
        compatibility: str,
        accessibility_report: dict | None = None,
        localization_report: dict | None = None,
        created_at: datetime | None = None,
    ) -> None:
        self.id = str(uuid.uuid4())
        self.title = title
        self.source_institution = source_institution
        self.version = version
        self.content_type = content_type
        self.checksum = checksum
        self.signature = signature
        self.compatibility = compatibility
        self.accessibility_report = accessibility_report or {}
        self.localization_report = localization_report or {}
        self.created_at = created_at or datetime.now(timezone.utc)


class ImportedResource:
    def __init__(
        self,
        package_id: str,
        imported_by: str,
        status: str,
        validation_results: dict | None = None,
        imported_at: datetime | None = None,
    ) -> None:
        self.id = str(uuid.uuid4())
        self.package_id = package_id
        self.imported_by = imported_by
        self.imported_at = imported_at or datetime.now(timezone.utc)
        self.status = status
        self.validation_results = validation_results or {}


class ReviewRequest:
    def __init__(
        self,
        title: str,
        request_type: str,
        submitter: str,
        assignees: list[str] | None = None,
        status: ReviewStatus = ReviewStatus.draft,
        due_date: str = "",
        created_at: datetime | None = None,
    ) -> None:
        self.id = str(uuid.uuid4())
        self.title = title
        self.request_type = request_type
        self.submitter = submitter
        self.assignees = assignees or []
        self.status = status
        self.created_at = created_at or datetime.now(timezone.utc)
        self.due_date = due_date


class PublicationQueueItem:
    def __init__(
        self,
        content_id: str,
        content_type: str,
        title: str,
        version: str,
        submitted_by: str,
        status: str = "queued",
        submitted_at: datetime | None = None,
    ) -> None:
        self.id = str(uuid.uuid4())
        self.content_id = content_id
        self.content_type = content_type
        self.title = title
        self.version = version
        self.submitted_by = submitted_by
        self.submitted_at = submitted_at or datetime.now(timezone.utc)
        self.status = status


class VersionHistory:
    def __init__(
        self,
        entity_id: str,
        entity_type: str,
        version: str,
        changes: list[str] | None = None,
        author: str = "",
        created_at: datetime | None = None,
    ) -> None:
        self.id = str(uuid.uuid4())
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.version = version
        self.changes = changes or []
        self.author = author
        self.created_at = created_at or datetime.now(timezone.utc)


class AcademicHubDashboard:
    def __init__(
        self,
        total_projects: int = 0,
        shared_packages: int = 0,
        imported_resources: int = 0,
        pending_reviews: int = 0,
        publications_this_month: int = 0,
        generated_at: datetime | None = None,
    ) -> None:
        self.total_projects = total_projects
        self.shared_packages = shared_packages
        self.imported_resources = imported_resources
        self.pending_reviews = pending_reviews
        self.publications_this_month = publications_this_month
        self.generated_at = generated_at or datetime.now(timezone.utc)
