"""Knowledge preservation service for ADRs, standards, and knowledge entries."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from ...shared.logging_config import get_logger
from ...shared.events.event_bus import EventBus
from ..domain.entities.knowledge_preservation import (
    ArchitectureDecisionRecord,
    CodingStandard,
    KnowledgeEntry,
    MigrationHistory,
    ReleaseHistory,
)
from ..domain.interfaces import (
    IArchitectureDecisionRecordRepository,
    ICodingStandardRepository,
    IKnowledgeEntryRepository,
    IMigrationHistoryRepository,
    IReleaseHistoryRepository,
)
from ..domain.events.production_events import KnowledgeEntryCreatedEvent

logger = get_logger("production.knowledge_service")


class KnowledgeService:
    """Manages ADRs, coding standards, knowledge entries, and migration history.

    Parameters
    ----------
    adr_repo:
        Repository for architecture decision records.
    knowledge_repo:
        Repository for knowledge entries.
    coding_standard_repo:
        Repository for coding standards.
    migration_history_repo:
        Repository for migration history.
    release_history_repo:
        Repository for release history.
    event_bus:
        Optional event bus for domain events.
    """

    def __init__(
        self,
        adr_repo: IArchitectureDecisionRecordRepository,
        knowledge_repo: IKnowledgeEntryRepository,
        coding_standard_repo: ICodingStandardRepository,
        migration_history_repo: IMigrationHistoryRepository,
        release_history_repo: IReleaseHistoryRepository,
        event_bus: Optional[EventBus] = None,
    ) -> None:
        self._adr_repo = adr_repo
        self._knowledge_repo = knowledge_repo
        self._coding_standard_repo = coding_standard_repo
        self._migration_history_repo = migration_history_repo
        self._release_history_repo = release_history_repo
        self._event_bus = event_bus

    async def _publish_event(self, event: Any) -> None:
        if self._event_bus is not None:
            await self._event_bus.publish(event)

    # ------------------------------------------------------------------
    # Architecture Decision Records
    # ------------------------------------------------------------------

    async def create_adr(
        self,
        title: str,
        context: str,
        decision: str,
        consequences: str = "",
        alternatives: str = "",
    ) -> ArchitectureDecisionRecord:
        """Propose a new architecture decision record."""
        adr = ArchitectureDecisionRecord(
            id=str(uuid.uuid4()),
            title=title,
            status="proposed",
            context=context,
            decision=decision,
            consequences=consequences,
            alternatives=alternatives,
            created_at=datetime.now(timezone.utc),
        )
        await self._adr_repo.create(adr)
        logger.info("adr_created", adr_id=adr.id, title=title)
        return adr

    async def get_adr(self, adr_id: str) -> Optional[ArchitectureDecisionRecord]:
        """Retrieve an ADR by ID."""
        return await self._adr_repo.get_by_id(adr_id)

    async def list_adrs(
        self, page: int = 1, per_page: int = 20
    ) -> dict:
        """List all ADRs with pagination."""
        return await self._adr_repo.get_all(page=page, per_page=per_page)

    async def update_adr_status(
        self, adr_id: str, new_status: str
    ) -> Optional[ArchitectureDecisionRecord]:
        """Transition an ADR to a new status."""
        adr = await self._adr_repo.get_by_id(adr_id)
        if adr is None:
            return None

        valid = {"proposed", "accepted", "deprecated", "superseded"}
        if new_status not in valid:
            raise ValueError(f"Invalid ADR status: {new_status}")

        data: dict[str, Any] = {"status": new_status}
        if new_status == "accepted":
            data["reviewed_at"] = datetime.now(timezone.utc)

        return await self._adr_repo.update(adr_id, data)

    async def update_adr(
        self, adr_id: str, data: dict[str, Any]
    ) -> Optional[ArchitectureDecisionRecord]:
        """Update arbitrary fields on an ADR."""
        return await self._adr_repo.update(adr_id, data)

    async def delete_adr(self, adr_id: str) -> bool:
        """Remove an ADR."""
        return await self._adr_repo.delete(adr_id)

    # ------------------------------------------------------------------
    # Knowledge Entries
    # ------------------------------------------------------------------

    async def create_knowledge_entry(
        self,
        title: str,
        category: str,
        content: str,
        tags: Optional[list[str]] = None,
        version: str = "",
        author: str = "",
    ) -> KnowledgeEntry:
        """Add a new knowledge entry."""
        entry = KnowledgeEntry(
            id=str(uuid.uuid4()),
            title=title,
            category=category,
            content=content,
            tags=tags or [],
            version=version,
            author=author,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        await self._knowledge_repo.create(entry)
        await self._publish_event(
            KnowledgeEntryCreatedEvent(
                entry_id=entry.id,
                title=title,
                category=category,
                module="production",
            )
        )
        logger.info("knowledge_entry_created", entry_id=entry.id, title=title)
        return entry

    async def get_knowledge_entry(
        self, entry_id: str
    ) -> Optional[KnowledgeEntry]:
        """Retrieve a knowledge entry by ID."""
        return await self._knowledge_repo.get_by_id(entry_id)

    async def list_knowledge_entries(
        self, page: int = 1, per_page: int = 20
    ) -> dict:
        """List knowledge entries with pagination."""
        return await self._knowledge_repo.get_all(page=page, per_page=per_page)

    async def search_knowledge_entries(self, query: str) -> list[KnowledgeEntry]:
        """Search knowledge entries by text query."""
        return await self._knowledge_repo.search(query)

    async def update_knowledge_entry(
        self, entry_id: str, data: dict[str, Any]
    ) -> Optional[KnowledgeEntry]:
        """Update a knowledge entry."""
        data["updated_at"] = datetime.now(timezone.utc)
        return await self._knowledge_repo.update(entry_id, data)

    async def delete_knowledge_entry(self, entry_id: str) -> bool:
        """Remove a knowledge entry."""
        return await self._knowledge_repo.delete(entry_id)

    # ------------------------------------------------------------------
    # Coding Standards
    # ------------------------------------------------------------------

    async def create_coding_standard(
        self,
        name: str,
        category: str,
        description: str,
        examples: Optional[list[str]] = None,
        references: Optional[list[str]] = None,
    ) -> CodingStandard:
        """Register a new coding standard."""
        standard = CodingStandard(
            id=str(uuid.uuid4()),
            name=name,
            category=category,
            description=description,
            examples=examples or [],
            references=references or [],
        )
        await self._coding_standard_repo.create(standard)
        logger.info("coding_standard_created", standard_id=standard.id, name=name)
        return standard

    async def get_coding_standard(
        self, standard_id: str
    ) -> Optional[CodingStandard]:
        """Retrieve a coding standard by ID."""
        return await self._coding_standard_repo.get_by_id(standard_id)

    async def list_coding_standards(self) -> list[CodingStandard]:
        """List all coding standards."""
        return await self._coding_standard_repo.get_all()

    async def update_coding_standard(
        self, standard_id: str, data: dict[str, Any]
    ) -> Optional[CodingStandard]:
        """Update a coding standard."""
        return await self._coding_standard_repo.update(standard_id, data)

    async def delete_coding_standard(self, standard_id: str) -> bool:
        """Remove a coding standard."""
        return await self._coding_standard_repo.delete(standard_id)

    # ------------------------------------------------------------------
    # Migration History
    # ------------------------------------------------------------------

    async def record_migration(
        self,
        from_version: str,
        to_version: str,
        status: str,
        steps_completed: int,
        total_steps: int,
        notes: str = "",
    ) -> MigrationHistory:
        """Record a completed or in-progress migration."""
        history = MigrationHistory(
            id=str(uuid.uuid4()),
            from_version=from_version,
            to_version=to_version,
            migration_date=datetime.now(timezone.utc).isoformat(),
            status=status,
            steps_completed=steps_completed,
            total_steps=total_steps,
            notes=notes,
        )
        await self._migration_history_repo.create(history)
        logger.info(
            "migration_recorded",
            history_id=history.id,
            from_version=from_version,
            to_version=to_version,
        )
        return history

    async def get_migration_history(self) -> list[MigrationHistory]:
        """List all migration history records."""
        return await self._migration_history_repo.get_all()

    # ------------------------------------------------------------------
    # Release History
    # ------------------------------------------------------------------

    async def record_release_history(
        self,
        release_id: str,
        version: str,
        summary: str,
    ) -> ReleaseHistory:
        """Record a release in the historical archive."""
        history = ReleaseHistory(
            id=str(uuid.uuid4()),
            release_id=release_id,
            version=version,
            release_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            summary=summary,
        )
        await self._release_history_repo.create(history)
        logger.info(
            "release_history_recorded",
            history_id=history.id,
            version=version,
        )
        return history

    async def get_release_history(self) -> list[ReleaseHistory]:
        """List all release history records."""
        return await self._release_history_repo.get_all()
