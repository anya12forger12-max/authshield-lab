"""Certification management service."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from ...shared.logging_config import get_logger
from ...shared.events.event_bus import EventBus
from ..domain.entities.certification import (
    Certification,
    CertificationRequirement,
    CertificationType,
)
from ..domain.interfaces import (
    ICertificationRepository,
    ICertificationRequirementRepository,
)
from ..domain.events.production_events import CertificationCompletedEvent

logger = get_logger("production.certification_service")


class CertificationService:
    """Manages certifications, requirements, and validation checks.

    Parameters
    ----------
    cert_repo:
        Repository for certification persistence.
    requirement_repo:
        Repository for certification requirement persistence.
    event_bus:
        Optional event bus for domain events.
    """

    def __init__(
        self,
        cert_repo: ICertificationRepository,
        requirement_repo: ICertificationRequirementRepository,
        event_bus: Optional[EventBus] = None,
    ) -> None:
        self._cert_repo = cert_repo
        self._requirement_repo = requirement_repo
        self._event_bus = event_bus

    async def _publish_event(self, event: Any) -> None:
        if self._event_bus is not None:
            await self._event_bus.publish(event)

    async def create_certification(
        self,
        name: str,
        cert_type: CertificationType,
        approved_by: str = "",
    ) -> Certification:
        """Initiate a new certification process."""
        cert = Certification(
            id=str(uuid.uuid4()),
            name=name,
            cert_type=cert_type,
            status="pending",
            approved_by=approved_by,
        )
        await self._cert_repo.create(cert)
        logger.info("certification_created", cert_id=cert.id, name=name)
        return cert

    async def get_certification(self, cert_id: str) -> Optional[Certification]:
        """Retrieve a certification by ID."""
        return await self._cert_repo.get_by_id(cert_id)

    async def list_certifications(
        self, page: int = 1, per_page: int = 20
    ) -> dict:
        """List all certifications with pagination."""
        return await self._cert_repo.get_all(page=page, per_page=per_page)

    async def get_certifications_by_type(
        self, cert_type: str
    ) -> list[Certification]:
        """List certifications filtered by type."""
        return await self._cert_repo.get_by_type(cert_type)

    async def add_requirement(
        self,
        certification_id: str,
        requirement: str,
        description: str = "",
    ) -> CertificationRequirement:
        """Add a requirement to a certification."""
        cert = await self._cert_repo.get_by_id(certification_id)
        if cert is None:
            raise ValueError(f"Certification not found: {certification_id}")

        req = CertificationRequirement(
            id=str(uuid.uuid4()),
            certification_id=certification_id,
            requirement=requirement,
            description=description,
            met=False,
        )
        await self._requirement_repo.create(req)
        logger.info(
            "requirement_added",
            req_id=req.id,
            certification_id=certification_id,
        )
        return req

    async def get_requirements(
        self, certification_id: str
    ) -> list[CertificationRequirement]:
        """List all requirements for a certification."""
        return await self._requirement_repo.get_by_certification_id(certification_id)

    async def fulfill_requirement(
        self,
        requirement_id: str,
        evidence: str = "",
    ) -> Optional[CertificationRequirement]:
        """Mark a certification requirement as fulfilled."""
        req = await self._requirement_repo.get_by_id(requirement_id)
        if req is None:
            return None
        return await self._requirement_repo.update(
            requirement_id, {"met": True, "evidence": evidence}
        )

    async def evaluate_certification(
        self, certification_id: str
    ) -> Optional[Certification]:
        """Evaluate a certification based on its requirements."""
        cert = await self._cert_repo.get_by_id(certification_id)
        if cert is None:
            return None

        requirements = await self.get_requirements(certification_id)
        if not requirements:
            return cert

        total = len(requirements)
        met = sum(1 for r in requirements if r.met)
        all_met = met == total

        new_status = "certified" if all_met else "in_progress"
        data: dict[str, Any] = {
            "status": new_status,
        }

        if all_met:
            data["certified_at"] = datetime.now(timezone.utc)
            await self._publish_event(
                CertificationCompletedEvent(
                    certification_id=certification_id,
                    cert_type=(
                        cert.cert_type.value
                        if hasattr(cert.cert_type, "value")
                        else str(cert.cert_type)
                    ),
                    status=new_status,
                    module="production",
                )
            )

        updated = await self._cert_repo.update(certification_id, data)
        logger.info(
            "certification_evaluated",
            cert_id=certification_id,
            status=new_status,
            met=met,
            total=total,
        )
        return updated

    async def revoke_certification(
        self, certification_id: str
    ) -> Optional[Certification]:
        """Revoke a previously granted certification."""
        cert = await self._cert_repo.get_by_id(certification_id)
        if cert is None:
            return None

        updated = await self._cert_repo.update(
            certification_id, {"status": "failed"}
        )
        logger.info("certification_revoked", cert_id=certification_id)
        return updated

    async def update_certification(
        self, certification_id: str, data: dict[str, Any]
    ) -> Optional[Certification]:
        """Update arbitrary fields on a certification."""
        return await self._cert_repo.update(certification_id, data)

    async def delete_certification(self, certification_id: str) -> bool:
        """Remove a certification record."""
        return await self._cert_repo.delete(certification_id)
