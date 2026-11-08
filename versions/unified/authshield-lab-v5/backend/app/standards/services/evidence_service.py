"""Service layer for evidence collection and review."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from app.standards.domain.entities.evidence import (
    EvidenceCollection,
    EvidenceItem,
    EvidenceSearchResult,
    VALID_EVIDENCE_TYPES,
)
from app.standards.domain.events.standards_events import EvidenceCollected
from app.standards.domain.interfaces.standards_interfaces import (
    AbstractEvidenceCollectionRepository,
    AbstractEvidenceItemRepository,
)
from app.standards.events.standards_event_handlers import get_event_bus
from app.standards.validators.standards_validator import StandardsValidator

logger = logging.getLogger(__name__)


class EvidenceService:
    """Manages evidence collection, search, and review."""

    def __init__(
        self,
        collection_repo: AbstractEvidenceCollectionRepository | None = None,
        item_repo: AbstractEvidenceItemRepository | None = None,
    ) -> None:
        from app.standards.repositories.standards_repository_impl import (
            InMemoryEvidenceCollectionRepository,
            InMemoryEvidenceItemRepository,
        )

        self._collections = collection_repo or InMemoryEvidenceCollectionRepository()
        self._items = item_repo or InMemoryEvidenceItemRepository()
        self._validator = StandardsValidator()
        self._bus = get_event_bus()

    # ------------------------------------------------------------------
    # Collection CRUD
    # ------------------------------------------------------------------

    def create_collection(
        self,
        name: str,
        framework_id: str,
    ) -> EvidenceCollection:
        self._validator.validate_non_empty(name, "name")
        self._validator.validate_non_empty(framework_id, "framework_id")
        collection = EvidenceCollection(name=name, framework_id=framework_id)
        self._collections.save(collection)
        return collection

    def get_collection(self, collection_id: str) -> EvidenceCollection | None:
        return self._collections.get_by_id(collection_id)

    def list_collections(self) -> list[EvidenceCollection]:
        return self._collections.list_all()

    def list_collections_by_framework(self, framework_id: str) -> list[EvidenceCollection]:
        return self._collections.list_by_framework(framework_id)

    def delete_collection(self, collection_id: str) -> bool:
        return self._collections.delete(collection_id)

    # ------------------------------------------------------------------
    # Evidence Items
    # ------------------------------------------------------------------

    def add_evidence(
        self,
        collection_id: str,
        evidence_type: str,
        description: str,
        source_id: str = "",
        source_type: str = "",
    ) -> EvidenceItem | None:
        collection = self._collections.get_by_id(collection_id)
        if collection is None:
            return None
        self._validator.validate_evidence_type(evidence_type)
        self._validator.validate_non_empty(description, "description")
        item = EvidenceItem(
            collection_id=collection_id,
            evidence_type=evidence_type,
            description=description,
            source_id=source_id,
            source_type=source_type,
        )
        item.validate_type()
        collection.add_item(item)
        self._collections.save(collection)
        self._items.save(item)
        event = EvidenceCollected(
            collection_id=collection_id,
            evidence_item_id=item.id,
            evidence_type=evidence_type,
        )
        self._bus.dispatch(event)
        logger.info("Evidence added: collection=%s type=%s", collection_id, evidence_type)
        return item

    def get_evidence_item(self, item_id: str) -> EvidenceItem | None:
        return self._items.get_by_id(item_id)

    def list_evidence_items(self, collection_id: str) -> list[EvidenceItem]:
        return self._items.list_by_collection(collection_id)

    def review_evidence(self, item_id: str) -> EvidenceItem | None:
        item = self._items.get_by_id(item_id)
        if item is None:
            return None
        item.mark_reviewed()
        self._items.save(item)
        return item

    def remove_evidence(self, collection_id: str, item_id: str) -> bool:
        collection = self._collections.get_by_id(collection_id)
        if collection is None:
            return False
        removed = collection.remove_item(item_id)
        if removed:
            self._collections.save(collection)
            self._items.delete(item_id)
        return removed

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search_evidence(self, query: str) -> list[EvidenceSearchResult]:
        items = self._items.search(query)
        results: list[EvidenceSearchResult] = []
        for item in items:
            results.append(EvidenceSearchResult(
                item_id=item.id,
                title=item.description[:80],
                type=item.evidence_type,
                snippet=item.description[:200],
                relevance=1.0,
            ))
        return results

    def search_collection(self, collection_id: str, query: str) -> list[EvidenceSearchResult]:
        collection = self._collections.get_by_id(collection_id)
        if collection is None:
            return []
        return collection.search(query)

    # ------------------------------------------------------------------
    # Aggregate helpers
    # ------------------------------------------------------------------

    def get_collection_stats(self, collection_id: str) -> dict | None:
        collection = self._collections.get_by_id(collection_id)
        if collection is None:
            return None
        items = self._items.list_by_collection(collection_id)
        reviewed = sum(1 for i in items if i.reviewed)
        by_type: dict[str, int] = {}
        for item in items:
            by_type[item.evidence_type] = by_type.get(item.evidence_type, 0) + 1
        return {
            "collection_id": collection_id,
            "total": collection.total,
            "collected": collection.collected,
            "pending": collection.pending,
            "reviewed": reviewed,
            "unreviewed": len(items) - reviewed,
            "by_type": by_type,
            "coverage_pct": collection.coverage_pct(),
        }

    def get_evidence_types(self) -> list[str]:
        return sorted(VALID_EVIDENCE_TYPES)
