"""Release management service."""

from __future__ import annotations

import hashlib
import platform
import sys
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from ...shared.logging_config import get_logger
from ...shared.events.event_bus import EventBus
from ..domain.entities.release_center import (
    BuildInfo,
    Release,
    ReleasePackage,
    ReleaseStatus,
)
from ..domain.interfaces import (
    IReleaseRepository,
    IReleasePackageRepository,
    IBuildInfoRepository,
)
from ..domain.events.production_events import (
    ReleaseCreatedEvent,
    ReleasePublishedEvent,
)

logger = get_logger("production.release_service")


class ReleaseService:
    """Manages the full lifecycle of software releases.

    Parameters
    ----------
    release_repo:
        Repository for release persistence.
    package_repo:
        Repository for release package persistence.
    build_info_repo:
        Repository for build info persistence.
    event_bus:
        Optional event bus for domain events.
    """

    def __init__(
        self,
        release_repo: IReleaseRepository,
        package_repo: IReleasePackageRepository,
        build_info_repo: IBuildInfoRepository,
        event_bus: Optional[EventBus] = None,
    ) -> None:
        self._release_repo = release_repo
        self._package_repo = package_repo
        self._build_info_repo = build_info_repo
        self._event_bus = event_bus

    async def _publish_event(self, event: Any) -> None:
        if self._event_bus is not None:
            await self._event_bus.publish(event)

    async def create_release(
        self,
        version: str,
        name: str,
        release_notes: Optional[list[str]] = None,
        features: Optional[list[str]] = None,
        bug_fixes: Optional[list[str]] = None,
        known_issues: Optional[list[str]] = None,
        deprecations: Optional[list[str]] = None,
        minimum_platform_version: str = "",
    ) -> Release:
        """Create a new release in development status."""
        release = Release(
            id=str(uuid.uuid4()),
            version=version,
            name=name,
            status=ReleaseStatus.IN_DEVELOPMENT,
            release_notes=release_notes or [],
            features=features or [],
            bug_fixes=bug_fixes or [],
            known_issues=known_issues or [],
            deprecations=deprecations or [],
            minimum_platform_version=minimum_platform_version,
            created_at=datetime.now(timezone.utc),
        )
        await self._release_repo.create(release)

        await self._publish_event(
            ReleaseCreatedEvent(
                release_id=release.id,
                version=version,
                name=name,
                module="production",
            )
        )
        logger.info("release_created", release_id=release.id, version=version)
        return release

    async def get_release(self, release_id: str) -> Optional[Release]:
        """Retrieve a release by ID."""
        return await self._release_repo.get_by_id(release_id)

    async def get_release_by_version(self, version: str) -> Optional[Release]:
        """Retrieve a release by its version string."""
        return await self._release_repo.get_by_version(version)

    async def list_releases(
        self, page: int = 1, per_page: int = 20
    ) -> dict:
        """List all releases with pagination."""
        return await self._release_repo.get_all(page=page, per_page=per_page)

    async def update_release_status(
        self, release_id: str, new_status: ReleaseStatus
    ) -> Optional[Release]:
        """Transition a release to a new lifecycle status."""
        release = await self._release_repo.get_by_id(release_id)
        if release is None:
            logger.warning("release_not_found", release_id=release_id)
            return None

        valid_transitions: dict[ReleaseStatus, list[ReleaseStatus]] = {
            ReleaseStatus.IN_DEVELOPMENT: [ReleaseStatus.RELEASE_CANDIDATE],
            ReleaseStatus.RELEASE_CANDIDATE: [ReleaseStatus.STABLE, ReleaseStatus.IN_DEVELOPMENT],
            ReleaseStatus.STABLE: [ReleaseStatus.DEPRECATED],
            ReleaseStatus.DEPRECATED: [ReleaseStatus.END_OF_LIFE],
            ReleaseStatus.END_OF_LIFE: [],
        }

        allowed = valid_transitions.get(release.status, [])
        if new_status not in allowed:
            logger.warning(
                "invalid_status_transition",
                release_id=release_id,
                from_status=release.status.value,
                to_status=new_status.value,
            )
            raise ValueError(
                f"Cannot transition from {release.status.value} to {new_status.value}"
            )

        data: dict[str, Any] = {"status": new_status}
        if new_status == ReleaseStatus.STABLE:
            data["release_date"] = datetime.now(timezone.utc)

        updated = await self._release_repo.update(release_id, data)
        if updated is not None and new_status == ReleaseStatus.STABLE:
            await self._publish_event(
                ReleasePublishedEvent(
                    release_id=release_id,
                    version=updated.version,
                    status=new_status.value,
                    module="production",
                )
            )
        logger.info(
            "release_status_updated",
            release_id=release_id,
            new_status=new_status.value,
        )
        return updated

    async def update_release(
        self, release_id: str, data: dict[str, Any]
    ) -> Optional[Release]:
        """Update arbitrary fields on a release."""
        release = await self._release_repo.get_by_id(release_id)
        if release is None:
            return None
        return await self._release_repo.update(release_id, data)

    async def delete_release(self, release_id: str) -> bool:
        """Remove a release record."""
        result = await self._release_repo.delete(release_id)
        if result:
            logger.info("release_deleted", release_id=release_id)
        return result

    async def create_build_info(
        self,
        version: str,
        build_number: str,
        build_environment: str = "local",
        python_version: str | None = None,
        platform_name: str | None = None,
    ) -> BuildInfo:
        """Record build metadata for a version."""
        checksum_source = f"{version}:{build_number}:{datetime.now(timezone.utc).isoformat()}"
        checksum = hashlib.sha256(checksum_source.encode()).hexdigest()

        build_info = BuildInfo(
            id=str(uuid.uuid4()),
            version=version,
            build_number=build_number,
            built_at=datetime.now(timezone.utc),
            build_environment=build_environment,
            python_version=python_version or sys.version.split()[0],
            platform=platform_name or platform.platform(),
            checksum=checksum,
        )
        await self._build_info_repo.create(build_info)
        logger.info("build_info_created", version=version, build_number=build_number)
        return build_info

    async def get_build_info(self, version: str) -> Optional[BuildInfo]:
        """Retrieve build info for a specific version."""
        return await self._build_info_repo.get_by_version(version)

    async def link_build_to_release(
        self, release_id: str, build_info_id: str
    ) -> Optional[Release]:
        """Associate a build info record with a release."""
        return await self._release_repo.update(
            release_id, {"build_info_id": build_info_id}
        )

    async def create_package(
        self,
        release_id: str,
        name: str,
        package_type: str = "installer",
        platform: str = "",
        checksum: str = "",
        file_size: int = 0,
    ) -> ReleasePackage:
        """Create a distributable package for a release."""
        package = ReleasePackage(
            id=str(uuid.uuid4()),
            release_id=release_id,
            name=name,
            package_type=package_type,
            platform=platform,
            checksum=checksum,
            file_size=file_size,
            created_at=datetime.now(timezone.utc),
        )
        await self._package_repo.create(package)
        logger.info("package_created", package_id=package.id, release_id=release_id)
        return package

    async def get_packages_for_release(
        self, release_id: str
    ) -> list[ReleasePackage]:
        """List all packages associated with a release."""
        return await self._package_repo.get_by_release_id(release_id)

    async def delete_package(self, package_id: str) -> bool:
        """Remove a release package."""
        return await self._package_repo.delete(package_id)
