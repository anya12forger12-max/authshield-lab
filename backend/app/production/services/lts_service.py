"""LTS version management service."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from ...shared.logging_config import get_logger
from ...shared.events.event_bus import EventBus
from ..domain.entities.lts import (
    CompatibilityMatrix,
    DeprecationEntry,
    LtsVersion,
    MigrationStep,
)
from ..domain.interfaces import (
    ICompatibilityMatrixRepository,
    IDeprecationEntryRepository,
    ILtsVersionRepository,
    IMigrationStepRepository,
)
from ..domain.events.production_events import MigrationCompletedEvent

logger = get_logger("production.lts_service")


class LtsService:
    """Manages LTS versions, migration paths, compatibility, and deprecations.

    Parameters
    ----------
    lts_repo:
        Repository for LTS version persistence.
    migration_step_repo:
        Repository for migration step persistence.
    compat_repo:
        Repository for compatibility matrix persistence.
    deprecation_repo:
        Repository for deprecation entry persistence.
    event_bus:
        Optional event bus for domain events.
    """

    def __init__(
        self,
        lts_repo: ILtsVersionRepository,
        migration_step_repo: IMigrationStepRepository,
        compat_repo: ICompatibilityMatrixRepository,
        deprecation_repo: IDeprecationEntryRepository,
        event_bus: Optional[EventBus] = None,
    ) -> None:
        self._lts_repo = lts_repo
        self._migration_step_repo = migration_step_repo
        self._compat_repo = compat_repo
        self._deprecation_repo = deprecation_repo
        self._event_bus = event_bus

    async def _publish_event(self, event: Any) -> None:
        if self._event_bus is not None:
            await self._event_bus.publish(event)

    async def create_lts_version(
        self,
        version: str,
        release_date: str,
        end_of_support: str,
        compatible_versions: Optional[list[str]] = None,
        migration_path: str = "",
        notes: str = "",
    ) -> LtsVersion:
        """Register a new LTS version track."""
        lts = LtsVersion(
            id=str(uuid.uuid4()),
            version=version,
            release_date=release_date,
            end_of_support=end_of_support,
            status="active",
            compatible_versions=compatible_versions or [],
            migration_path=migration_path,
            notes=notes,
        )
        await self._lts_repo.create(lts)
        logger.info("lts_version_created", lts_id=lts.id, version=version)
        return lts

    async def get_lts_version(self, lts_id: str) -> Optional[LtsVersion]:
        """Retrieve an LTS version by ID."""
        return await self._lts_repo.get_by_id(lts_id)

    async def get_lts_by_version(self, version: str) -> Optional[LtsVersion]:
        """Retrieve an LTS version by its version string."""
        return await self._lts_repo.get_by_version(version)

    async def list_lts_versions(
        self, page: int = 1, per_page: int = 20
    ) -> dict:
        """List all LTS versions with pagination."""
        return await self._lts_repo.get_all(page=page, per_page=per_page)

    async def update_lts_status(
        self, lts_id: str, new_status: str
    ) -> Optional[LtsVersion]:
        """Transition an LTS version to a new status."""
        lts = await self._lts_repo.get_by_id(lts_id)
        if lts is None:
            return None

        valid = {"active", "extended", "end_of_life"}
        if new_status not in valid:
            raise ValueError(f"Invalid LTS status: {new_status}")

        return await self._lts_repo.update(lts_id, {"status": new_status})

    async def update_lts(
        self, lts_id: str, data: dict[str, Any]
    ) -> Optional[LtsVersion]:
        """Update arbitrary fields on an LTS version."""
        return await self._lts_repo.update(lts_id, data)

    async def delete_lts_version(self, lts_id: str) -> bool:
        """Remove an LTS version record."""
        return await self._lts_repo.delete(lts_id)

    async def add_migration_step(
        self,
        from_version: str,
        to_version: str,
        step_number: int,
        description: str,
        requires_backup: bool = False,
        estimated_minutes: int = 0,
        rollback_available: bool = True,
    ) -> MigrationStep:
        """Define a migration step between two versions."""
        step = MigrationStep(
            id=str(uuid.uuid4()),
            from_version=from_version,
            to_version=to_version,
            step_number=step_number,
            description=description,
            requires_backup=requires_backup,
            estimated_minutes=estimated_minutes,
            rollback_available=rollback_available,
        )
        await self._migration_step_repo.create(step)
        logger.info(
            "migration_step_created",
            step_id=step.id,
            from_version=from_version,
            to_version=to_version,
        )
        return step

    async def get_migration_steps(
        self, from_version: str, to_version: str
    ) -> list[MigrationStep]:
        """Retrieve ordered migration steps for a version pair."""
        return await self._migration_step_repo.get_by_version_pair(
            from_version, to_version
        )

    async def get_migration_path(
        self, from_version: str, to_version: str
    ) -> dict:
        """Return a complete migration plan for a version pair."""
        steps = await self.get_migration_steps(from_version, to_version)
        total_minutes = sum(s.estimated_minutes for s in steps)
        backup_required = any(s.requires_backup for s in steps)
        rollback_possible = all(s.rollback_available for s in steps)

        return {
            "from_version": from_version,
            "to_version": to_version,
            "steps": [
                {
                    "step_number": s.step_number,
                    "description": s.description,
                    "requires_backup": s.requires_backup,
                    "estimated_minutes": s.estimated_minutes,
                    "rollback_available": s.rollback_available,
                }
                for s in steps
            ],
            "total_steps": len(steps),
            "estimated_total_minutes": total_minutes,
            "backup_required": backup_required,
            "rollback_possible": rollback_possible,
        }

    async def check_compatibility(
        self, version_a: str, version_b: str
    ) -> CompatibilityMatrix:
        """Check and record compatibility between two versions."""
        existing = await self._compat_repo.check_compatibility(
            version_a, version_b
        )
        if existing is not None:
            return existing

        entry = CompatibilityMatrix(
            id=str(uuid.uuid4()),
            version_a=version_a,
            version_b=version_b,
            compatible=True,
            notes="Default compatibility check",
            checked_at=datetime.now(timezone.utc),
        )
        await self._compat_repo.create(entry)
        logger.info(
            "compatibility_checked",
            version_a=version_a,
            version_b=version_b,
        )
        return entry

    async def update_compatibility(
        self,
        version_a: str,
        version_b: str,
        compatible: bool,
        notes: str = "",
    ) -> CompatibilityMatrix:
        """Update the compatibility status between two versions."""
        existing = await self._compat_repo.check_compatibility(
            version_a, version_b
        )
        if existing is not None:
            existing.compatible = compatible
            existing.notes = notes
            existing.checked_at = datetime.now(timezone.utc)
            return existing

        entry = CompatibilityMatrix(
            id=str(uuid.uuid4()),
            version_a=version_a,
            version_b=version_b,
            compatible=compatible,
            notes=notes,
            checked_at=datetime.now(timezone.utc),
        )
        await self._compat_repo.create(entry)
        return entry

    async def get_compatibility_matrix(self) -> list[CompatibilityMatrix]:
        """Retrieve the full compatibility matrix."""
        return await self._compat_repo.get_all()

    async def add_deprecation(
        self,
        feature: str,
        deprecated_in_version: str,
        replacement: str = "",
        removal_version: str = "",
        announced_at: str = "",
    ) -> DeprecationEntry:
        """Record a feature deprecation."""
        entry = DeprecationEntry(
            id=str(uuid.uuid4()),
            feature=feature,
            deprecated_in_version=deprecated_in_version,
            replacement=replacement,
            removal_version=removal_version,
            announced_at=announced_at
            or datetime.now(timezone.utc).isoformat(),
        )
        await self._deprecation_repo.create(entry)
        logger.info("deprecation_added", feature=feature, version=deprecated_in_version)
        return entry

    async def get_deprecation(self, feature: str) -> Optional[DeprecationEntry]:
        """Look up a deprecation by feature name."""
        return await self._deprecation_repo.get_by_feature(feature)

    async def list_deprecations(self) -> list[DeprecationEntry]:
        """List all recorded deprecations."""
        return await self._deprecation_repo.get_all()

    async def remove_deprecation(self, entry_id: str) -> bool:
        """Remove a deprecation record."""
        return await self._deprecation_repo.delete(entry_id)
