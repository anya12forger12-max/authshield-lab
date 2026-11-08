"""In-memory repository implementations for all Content Studio repository interfaces."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from ..domain.interfaces.content_studio_interfaces import (
    IA11yCheckRepository,
    IA11yRemediationRepository,
    IA11yValidationReportRepository,
    IAssetCollectionRepository,
    IContentTemplateRepository,
    IContentVersionRepository,
    ICourseDesignRepository,
    IEditorialReviewRepository,
    IMultimediaAssetRepository,
    IProgramRepository,
    IPublishHistoryRepository,
    IPublishRequestRepository,
    IReviewCommentRepository,
    IReviewDecisionRepository,
    IVirtualLabRepository,
    ILabTemplateRepository,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Program Repository
# ---------------------------------------------------------------------------

class InMemoryProgramRepository(IProgramRepository):
    def __init__(self) -> None:
        self._items: dict[str, dict[str, Any]] = {}

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        item_id = data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        item = {
            "id": item_id,
            "name": data.get("name", ""),
            "description": data.get("description", ""),
            "department": data.get("department", ""),
            "status": data.get("status", "draft"),
            "version": data.get("version", 1),
            "courses": data.get("courses", []),
            "created_at": now,
            "updated_at": now,
        }
        self._items[item_id] = item
        return item

    def get_by_id(self, item_id: str) -> dict[str, Any] | None:
        return self._items.get(item_id)

    def get_all(
        self, page: int = 1, per_page: int = 20, status: Optional[str] = None
    ) -> dict[str, Any]:
        items = list(self._items.values())
        if status:
            items = [i for i in items if i["status"] == status]
        items.sort(key=lambda i: i.get("created_at", ""), reverse=True)
        total = len(items)
        pages = max(1, (total + per_page - 1) // per_page)
        offset = (page - 1) * per_page
        return {"items": items[offset:offset + per_page], "total": total, "page": page, "per_page": per_page, "pages": pages}

    def update(self, item_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        item = self._items.get(item_id)
        if not item:
            return None
        for key in ("name", "description", "department", "status", "version", "courses"):
            if key in data:
                item[key] = data[key]
        item["updated_at"] = datetime.now(timezone.utc).isoformat()
        return item

    def delete(self, item_id: str) -> bool:
        return self._items.pop(item_id, None) is not None


# ---------------------------------------------------------------------------
# Course Design Repository
# ---------------------------------------------------------------------------

class InMemoryCourseDesignRepository(ICourseDesignRepository):
    def __init__(self) -> None:
        self._items: dict[str, dict[str, Any]] = {}

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        item_id = data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        item = {
            "id": item_id,
            "program_id": data.get("program_id", ""),
            "name": data.get("name", ""),
            "description": data.get("description", ""),
            "units": data.get("units", []),
            "learning_objectives": data.get("learning_objectives", []),
            "estimated_hours": data.get("estimated_hours", 0.0),
            "competencies": data.get("competencies", []),
            "prerequisites": data.get("prerequisites", []),
            "a11y_notes": data.get("a11y_notes", ""),
            "localization_status": data.get("localization_status", "pending"),
            "version": data.get("version", 1),
            "status": data.get("status", "draft"),
            "created_by": data.get("created_by", ""),
            "created_at": now,
            "updated_at": now,
        }
        self._items[item_id] = item
        return item

    def get_by_id(self, item_id: str) -> dict[str, Any] | None:
        return self._items.get(item_id)

    def get_all(
        self, page: int = 1, per_page: int = 20, status: Optional[str] = None
    ) -> dict[str, Any]:
        items = list(self._items.values())
        if status:
            items = [i for i in items if i["status"] == status]
        items.sort(key=lambda i: i.get("created_at", ""), reverse=True)
        total = len(items)
        pages = max(1, (total + per_page - 1) // per_page)
        offset = (page - 1) * per_page
        return {"items": items[offset:offset + per_page], "total": total, "page": page, "per_page": per_page, "pages": pages}

    def update(self, item_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        item = self._items.get(item_id)
        if not item:
            return None
        for key in ("name", "description", "units", "learning_objectives", "estimated_hours",
                     "competencies", "prerequisites", "a11y_notes", "localization_status",
                     "version", "status", "created_by", "program_id"):
            if key in data:
                item[key] = data[key]
        item["updated_at"] = datetime.now(timezone.utc).isoformat()
        return item

    def delete(self, item_id: str) -> bool:
        return self._items.pop(item_id, None) is not None

    def search(self, query: str, page: int = 1, per_page: int = 20) -> dict[str, Any]:
        q = query.lower()
        items = [i for i in self._items.values()
                 if q in i.get("name", "").lower() or q in i.get("description", "").lower()]
        items.sort(key=lambda i: i.get("created_at", ""), reverse=True)
        total = len(items)
        pages = max(1, (total + per_page - 1) // per_page)
        offset = (page - 1) * per_page
        return {"items": items[offset:offset + per_page], "total": total, "page": page, "per_page": per_page, "pages": pages}

    def get_by_program(self, program_id: str) -> list[dict[str, Any]]:
        return [i for i in self._items.values() if i.get("program_id") == program_id]


# ---------------------------------------------------------------------------
# Virtual Lab Repository
# ---------------------------------------------------------------------------

class InMemoryVirtualLabRepository(IVirtualLabRepository):
    def __init__(self) -> None:
        self._items: dict[str, dict[str, Any]] = {}

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        item_id = data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        item = {
            "id": item_id,
            "name": data.get("name", ""),
            "description": data.get("description", ""),
            "lab_type": data.get("lab_type", "hands_on"),
            "learning_objectives": data.get("learning_objectives", []),
            "prerequisites": data.get("prerequisites", []),
            "steps": data.get("steps", []),
            "expected_outcomes": data.get("expected_outcomes", []),
            "reflection_questions": data.get("reflection_questions", []),
            "assessment_criteria": data.get("assessment_criteria", {}),
            "a11y_instructions": data.get("a11y_instructions", ""),
            "estimated_minutes": data.get("estimated_minutes", 60),
            "status": data.get("status", "draft"),
            "version": data.get("version", 1),
            "created_at": now,
            "updated_at": now,
        }
        self._items[item_id] = item
        return item

    def get_by_id(self, item_id: str) -> dict[str, Any] | None:
        return self._items.get(item_id)

    def get_all(
        self, page: int = 1, per_page: int = 20, status: Optional[str] = None
    ) -> dict[str, Any]:
        items = list(self._items.values())
        if status:
            items = [i for i in items if i["status"] == status]
        items.sort(key=lambda i: i.get("created_at", ""), reverse=True)
        total = len(items)
        pages = max(1, (total + per_page - 1) // per_page)
        offset = (page - 1) * per_page
        return {"items": items[offset:offset + per_page], "total": total, "page": page, "per_page": per_page, "pages": pages}

    def update(self, item_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        item = self._items.get(item_id)
        if not item:
            return None
        for key in ("name", "description", "lab_type", "learning_objectives", "prerequisites",
                     "steps", "expected_outcomes", "reflection_questions", "assessment_criteria",
                     "a11y_instructions", "estimated_minutes", "status", "version"):
            if key in data:
                item[key] = data[key]
        item["updated_at"] = datetime.now(timezone.utc).isoformat()
        return item

    def delete(self, item_id: str) -> bool:
        return self._items.pop(item_id, None) is not None

    def search(self, query: str, page: int = 1, per_page: int = 20) -> dict[str, Any]:
        q = query.lower()
        items = [i for i in self._items.values()
                 if q in i.get("name", "").lower() or q in i.get("description", "").lower()]
        items.sort(key=lambda i: i.get("created_at", ""), reverse=True)
        total = len(items)
        pages = max(1, (total + per_page - 1) // per_page)
        offset = (page - 1) * per_page
        return {"items": items[offset:offset + per_page], "total": total, "page": page, "per_page": per_page, "pages": pages}


# ---------------------------------------------------------------------------
# Lab Template Repository
# ---------------------------------------------------------------------------

class InMemoryLabTemplateRepository(ILabTemplateRepository):
    def __init__(self) -> None:
        self._items: dict[str, dict[str, Any]] = {}

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        item_id = data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        item = {
            "id": item_id,
            "name": data.get("name", ""),
            "template_type": data.get("template_type", ""),
            "description": data.get("description", ""),
            "steps_template": data.get("steps_template", []),
            "metadata": data.get("metadata", {}),
            "created_at": now,
        }
        self._items[item_id] = item
        return item

    def get_by_id(self, item_id: str) -> dict[str, Any] | None:
        return self._items.get(item_id)

    def get_all(self) -> list[dict[str, Any]]:
        return list(self._items.values())

    def update(self, item_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        item = self._items.get(item_id)
        if not item:
            return None
        for key in ("name", "template_type", "description", "steps_template", "metadata"):
            if key in data:
                item[key] = data[key]
        return item

    def delete(self, item_id: str) -> bool:
        return self._items.pop(item_id, None) is not None


# ---------------------------------------------------------------------------
# Multimedia Asset Repository
# ---------------------------------------------------------------------------

class InMemoryMultimediaAssetRepository(IMultimediaAssetRepository):
    def __init__(self) -> None:
        self._items: dict[str, dict[str, Any]] = {}

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        item_id = data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        item = {
            "id": item_id,
            "name": data.get("name", ""),
            "asset_type": data.get("asset_type", "image"),
            "description": data.get("description", ""),
            "file_path": data.get("file_path", ""),
            "alt_text": data.get("alt_text", ""),
            "caption": data.get("caption", ""),
            "transcript": data.get("transcript", ""),
            "accessible": data.get("accessible", True),
            "metadata": data.get("metadata", {}),
            "version": data.get("version", 1),
            "created_at": now,
        }
        self._items[item_id] = item
        return item

    def get_by_id(self, item_id: str) -> dict[str, Any] | None:
        return self._items.get(item_id)

    def get_all(
        self, page: int = 1, per_page: int = 20, asset_type: Optional[str] = None
    ) -> dict[str, Any]:
        items = list(self._items.values())
        if asset_type:
            items = [i for i in items if i["asset_type"] == asset_type]
        items.sort(key=lambda i: i.get("created_at", ""), reverse=True)
        total = len(items)
        pages = max(1, (total + per_page - 1) // per_page)
        offset = (page - 1) * per_page
        return {"items": items[offset:offset + per_page], "total": total, "page": page, "per_page": per_page, "pages": pages}

    def update(self, item_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        item = self._items.get(item_id)
        if not item:
            return None
        for key in ("name", "asset_type", "description", "file_path", "alt_text",
                     "caption", "transcript", "accessible", "metadata", "version"):
            if key in data:
                item[key] = data[key]
        return item

    def delete(self, item_id: str) -> bool:
        return self._items.pop(item_id, None) is not None

    def search(self, query: str, page: int = 1, per_page: int = 20) -> dict[str, Any]:
        q = query.lower()
        items = [i for i in self._items.values()
                 if q in i.get("name", "").lower() or q in i.get("description", "").lower()]
        items.sort(key=lambda i: i.get("created_at", ""), reverse=True)
        total = len(items)
        pages = max(1, (total + per_page - 1) // per_page)
        offset = (page - 1) * per_page
        return {"items": items[offset:offset + per_page], "total": total, "page": page, "per_page": per_page, "pages": pages}


# ---------------------------------------------------------------------------
# Asset Collection Repository
# ---------------------------------------------------------------------------

class InMemoryAssetCollectionRepository(IAssetCollectionRepository):
    def __init__(self) -> None:
        self._items: dict[str, dict[str, Any]] = {}

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        item_id = data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        item = {
            "id": item_id,
            "name": data.get("name", ""),
            "description": data.get("description", ""),
            "asset_ids": data.get("asset_ids", []),
            "created_at": now,
        }
        self._items[item_id] = item
        return item

    def get_by_id(self, item_id: str) -> dict[str, Any] | None:
        return self._items.get(item_id)

    def get_all(self) -> list[dict[str, Any]]:
        return list(self._items.values())

    def update(self, item_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        item = self._items.get(item_id)
        if not item:
            return None
        for key in ("name", "description", "asset_ids"):
            if key in data:
                item[key] = data[key]
        return item

    def delete(self, item_id: str) -> bool:
        return self._items.pop(item_id, None) is not None


# ---------------------------------------------------------------------------
# Content Template Repository
# ---------------------------------------------------------------------------

class InMemoryContentTemplateRepository(IContentTemplateRepository):
    def __init__(self) -> None:
        self._items: dict[str, dict[str, Any]] = {}

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        item_id = data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        item = {
            "id": item_id,
            "name": data.get("name", ""),
            "template_type": data.get("template_type", "lesson"),
            "description": data.get("description", ""),
            "structure": data.get("structure", {}),
            "version": data.get("version", 1),
            "author": data.get("author", ""),
            "inherit_from": data.get("inherit_from"),
            "created_at": now,
        }
        self._items[item_id] = item
        return item

    def get_by_id(self, item_id: str) -> dict[str, Any] | None:
        return self._items.get(item_id)

    def get_all(
        self, page: int = 1, per_page: int = 20, template_type: Optional[str] = None
    ) -> dict[str, Any]:
        items = list(self._items.values())
        if template_type:
            items = [i for i in items if i["template_type"] == template_type]
        items.sort(key=lambda i: i.get("created_at", ""), reverse=True)
        total = len(items)
        pages = max(1, (total + per_page - 1) // per_page)
        offset = (page - 1) * per_page
        return {"items": items[offset:offset + per_page], "total": total, "page": page, "per_page": per_page, "pages": pages}

    def update(self, item_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        item = self._items.get(item_id)
        if not item:
            return None
        for key in ("name", "template_type", "description", "structure", "version", "author", "inherit_from"):
            if key in data:
                item[key] = data[key]
        return item

    def delete(self, item_id: str) -> bool:
        return self._items.pop(item_id, None) is not None


# ---------------------------------------------------------------------------
# Publish Request Repository
# ---------------------------------------------------------------------------

class InMemoryPublishRequestRepository(IPublishRequestRepository):
    def __init__(self) -> None:
        self._items: dict[str, dict[str, Any]] = {}

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        item_id = data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        item = {
            "id": item_id,
            "content_id": data.get("content_id", ""),
            "content_type": data.get("content_type", ""),
            "version": data.get("version", 1),
            "requested_by": data.get("requested_by", ""),
            "requested_at": data.get("requested_at", now),
            "validation_results": data.get("validation_results", {}),
            "a11y_check_results": data.get("a11y_check_results", {}),
            "localization_results": data.get("localization_results", {}),
            "dependency_results": data.get("dependency_results", {}),
            "digital_signature": data.get("digital_signature", ""),
            "release_notes": data.get("release_notes", ""),
            "status": data.get("status", "pending"),
        }
        self._items[item_id] = item
        return item

    def get_by_id(self, item_id: str) -> dict[str, Any] | None:
        return self._items.get(item_id)

    def get_all(
        self, page: int = 1, per_page: int = 20, status: Optional[str] = None
    ) -> dict[str, Any]:
        items = list(self._items.values())
        if status:
            items = [i for i in items if i["status"] == status]
        items.sort(key=lambda i: i.get("requested_at", ""), reverse=True)
        total = len(items)
        pages = max(1, (total + per_page - 1) // per_page)
        offset = (page - 1) * per_page
        return {"items": items[offset:offset + per_page], "total": total, "page": page, "per_page": per_page, "pages": pages}

    def update(self, item_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        item = self._items.get(item_id)
        if not item:
            return None
        for key in ("validation_results", "a11y_check_results", "localization_results",
                     "dependency_results", "digital_signature", "release_notes", "status"):
            if key in data:
                item[key] = data[key]
        return item

    def delete(self, item_id: str) -> bool:
        return self._items.pop(item_id, None) is not None

    def get_by_content(self, content_id: str) -> list[dict[str, Any]]:
        return [i for i in self._items.values() if i.get("content_id") == content_id]


# ---------------------------------------------------------------------------
# Publish History Repository
# ---------------------------------------------------------------------------

class InMemoryPublishHistoryRepository(IPublishHistoryRepository):
    def __init__(self) -> None:
        self._items: dict[str, dict[str, Any]] = {}

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        item_id = data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        item = {
            "id": item_id,
            "content_id": data.get("content_id", ""),
            "version": data.get("version", 1),
            "action": data.get("action", ""),
            "performed_by": data.get("performed_by", ""),
            "performed_at": data.get("performed_at", now),
            "details": data.get("details", {}),
        }
        self._items[item_id] = item
        return item

    def get_by_id(self, item_id: str) -> dict[str, Any] | None:
        return self._items.get(item_id)

    def get_by_content(self, content_id: str) -> list[dict[str, Any]]:
        items = [i for i in self._items.values() if i.get("content_id") == content_id]
        items.sort(key=lambda i: i.get("performed_at", ""), reverse=True)
        return items

    def get_all(
        self, page: int = 1, per_page: int = 20
    ) -> dict[str, Any]:
        items = list(self._items.values())
        items.sort(key=lambda i: i.get("performed_at", ""), reverse=True)
        total = len(items)
        pages = max(1, (total + per_page - 1) // per_page)
        offset = (page - 1) * per_page
        return {"items": items[offset:offset + per_page], "total": total, "page": page, "per_page": per_page, "pages": pages}


# ---------------------------------------------------------------------------
# Content Version Repository
# ---------------------------------------------------------------------------

class InMemoryContentVersionRepository(IContentVersionRepository):
    def __init__(self) -> None:
        self._items: dict[str, dict[str, Any]] = {}

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        item_id = data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        item = {
            "id": item_id,
            "content_id": data.get("content_id", ""),
            "version": data.get("version", 1),
            "changes": data.get("changes", []),
            "author": data.get("author", ""),
            "created_at": now,
            "checksum": data.get("checksum", ""),
        }
        self._items[item_id] = item
        return item

    def get_by_id(self, item_id: str) -> dict[str, Any] | None:
        return self._items.get(item_id)

    def get_latest(self, content_id: str) -> dict[str, Any] | None:
        items = [i for i in self._items.values() if i.get("content_id") == content_id]
        if not items:
            return None
        return max(items, key=lambda i: i.get("version", 0))

    def get_all_for_content(self, content_id: str) -> list[dict[str, Any]]:
        items = [i for i in self._items.values() if i.get("content_id") == content_id]
        items.sort(key=lambda i: i.get("version", 0), reverse=True)
        return items


# ---------------------------------------------------------------------------
# Editorial Review Repository
# ---------------------------------------------------------------------------

class InMemoryEditorialReviewRepository(IEditorialReviewRepository):
    def __init__(self) -> None:
        self._items: dict[str, dict[str, Any]] = {}

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        item_id = data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        item = {
            "id": item_id,
            "content_id": data.get("content_id", ""),
            "content_type": data.get("content_type", ""),
            "current_stage": data.get("current_stage", "draft"),
            "submitter": data.get("submitter", ""),
            "created_at": now,
        }
        self._items[item_id] = item
        return item

    def get_by_id(self, item_id: str) -> dict[str, Any] | None:
        return self._items.get(item_id)

    def get_by_content(self, content_id: str) -> dict[str, Any] | None:
        for item in self._items.values():
            if item.get("content_id") == content_id:
                return item
        return None

    def get_all(
        self, page: int = 1, per_page: int = 20, stage: Optional[str] = None
    ) -> dict[str, Any]:
        items = list(self._items.values())
        if stage:
            items = [i for i in items if i["current_stage"] == stage]
        items.sort(key=lambda i: i.get("created_at", ""), reverse=True)
        total = len(items)
        pages = max(1, (total + per_page - 1) // per_page)
        offset = (page - 1) * per_page
        return {"items": items[offset:offset + per_page], "total": total, "page": page, "per_page": per_page, "pages": pages}

    def update(self, item_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        item = self._items.get(item_id)
        if not item:
            return None
        for key in ("current_stage", "submitter", "content_type"):
            if key in data:
                item[key] = data[key]
        return item


# ---------------------------------------------------------------------------
# Review Comment Repository
# ---------------------------------------------------------------------------

class InMemoryReviewCommentRepository(IReviewCommentRepository):
    def __init__(self) -> None:
        self._items: dict[str, dict[str, Any]] = {}

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        item_id = data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        item = {
            "id": item_id,
            "review_id": data.get("review_id", ""),
            "author": data.get("author", ""),
            "stage": data.get("stage", "draft"),
            "comment": data.get("comment", ""),
            "severity": data.get("severity"),
            "created_at": now,
        }
        self._items[item_id] = item
        return item

    def get_by_review(self, review_id: str) -> list[dict[str, Any]]:
        return [i for i in self._items.values() if i.get("review_id") == review_id]

    def delete(self, item_id: str) -> bool:
        return self._items.pop(item_id, None) is not None


# ---------------------------------------------------------------------------
# Review Decision Repository
# ---------------------------------------------------------------------------

class InMemoryReviewDecisionRepository(IReviewDecisionRepository):
    def __init__(self) -> None:
        self._items: dict[str, dict[str, Any]] = {}

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        item_id = data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        item = {
            "id": item_id,
            "review_id": data.get("review_id", ""),
            "stage": data.get("stage", "draft"),
            "reviewer": data.get("reviewer", ""),
            "decision": data.get("decision", "approved"),
            "comments": data.get("comments", ""),
            "decided_at": data.get("decided_at", now),
        }
        self._items[item_id] = item
        return item

    def get_by_review(self, review_id: str) -> list[dict[str, Any]]:
        items = [i for i in self._items.values() if i.get("review_id") == review_id]
        items.sort(key=lambda i: i.get("decided_at", ""), reverse=True)
        return items

    def get_latest(self, review_id: str) -> dict[str, Any] | None:
        items = self.get_by_review(review_id)
        return items[0] if items else None


# ---------------------------------------------------------------------------
# A11y Check Repository
# ---------------------------------------------------------------------------

class InMemoryA11yCheckRepository(IA11yCheckRepository):
    def __init__(self) -> None:
        self._items: dict[str, dict[str, Any]] = {}

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        item_id = data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        item = {
            "id": item_id,
            "report_id": data.get("report_id", ""),
            "check_type": data.get("check_type", ""),
            "description": data.get("description", ""),
            "passed": data.get("passed", False),
            "element": data.get("element", ""),
            "evidence": data.get("evidence", ""),
            "remediation": data.get("remediation"),
            "severity": data.get("severity", "error"),
            "created_at": now,
        }
        self._items[item_id] = item
        return item

    def get_by_report(self, report_id: str) -> list[dict[str, Any]]:
        return [i for i in self._items.values() if i.get("report_id") == report_id]


# ---------------------------------------------------------------------------
# A11y Validation Report Repository
# ---------------------------------------------------------------------------

class InMemoryA11yValidationReportRepository(IA11yValidationReportRepository):
    def __init__(self) -> None:
        self._items: dict[str, dict[str, Any]] = {}

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        item_id = data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        item = {
            "id": item_id,
            "content_id": data.get("content_id", ""),
            "total": data.get("total", 0),
            "passed": data.get("passed", 0),
            "failed": data.get("failed", 0),
            "na": data.get("na", 0),
            "compliance_pct": data.get("compliance_pct", 0.0),
            "generated_at": data.get("generated_at", now),
        }
        self._items[item_id] = item
        return item

    def get_by_id(self, item_id: str) -> dict[str, Any] | None:
        return self._items.get(item_id)

    def get_by_content(self, content_id: str) -> dict[str, Any] | None:
        for item in self._items.values():
            if item.get("content_id") == content_id:
                return item
        return None

    def get_all(
        self, page: int = 1, per_page: int = 20
    ) -> dict[str, Any]:
        items = list(self._items.values())
        items.sort(key=lambda i: i.get("generated_at", ""), reverse=True)
        total = len(items)
        pages = max(1, (total + per_page - 1) // per_page)
        offset = (page - 1) * per_page
        return {"items": items[offset:offset + per_page], "total": total, "page": page, "per_page": per_page, "pages": pages}


# ---------------------------------------------------------------------------
# A11y Remediation Repository
# ---------------------------------------------------------------------------

class InMemoryA11yRemediationRepository(IA11yRemediationRepository):
    def __init__(self) -> None:
        self._items: dict[str, dict[str, Any]] = {}

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        item_id = data.get("id", str(uuid.uuid4()))
        now = datetime.now(timezone.utc).isoformat()
        item = {
            "id": item_id,
            "report_id": data.get("report_id", ""),
            "check_id": data.get("check_id", ""),
            "action": data.get("action", ""),
            "priority": data.get("priority", "high"),
            "status": data.get("status", "open"),
            "assignee": data.get("assignee", ""),
            "created_at": now,
        }
        self._items[item_id] = item
        return item

    def get_by_id(self, item_id: str) -> dict[str, Any] | None:
        return self._items.get(item_id)

    def get_by_report(self, report_id: str) -> list[dict[str, Any]]:
        return [i for i in self._items.values() if i.get("report_id") == report_id]

    def get_open(self) -> list[dict[str, Any]]:
        return [i for i in self._items.values() if i.get("status") in ("open", "in_progress")]

    def update(self, item_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        item = self._items.get(item_id)
        if not item:
            return None
        for key in ("action", "priority", "status", "assignee"):
            if key in data:
                item[key] = data[key]
        return item
