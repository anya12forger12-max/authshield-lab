"""Certification service: manage certifications, requirements, validation, reports."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from ..domain.entities.certification_center import (
    CertificationRequirement,
    CertificationStatus,
    PlatformCertification,
    PlatformCertificationReport,
)
from ..domain.interfaces import (
    CertificationReportRepository,
    CertificationRequirementRepository,
    PlatformCertificationRepository,
)


class CertificationService:
    """Runs certifications, validates requirements, issues and revokes certs, generates reports."""

    def __init__(
        self,
        cert_repo: PlatformCertificationRepository,
        requirement_repo: CertificationRequirementRepository,
        report_repo: CertificationReportRepository,
    ) -> None:
        self._cert_repo = cert_repo
        self._requirement_repo = requirement_repo
        self._report_repo = report_repo

    async def create_certification(
        self,
        name: str,
        cert_type: str,
        approved_by: str | None = None,
    ) -> PlatformCertification:
        """Initiate a new certification."""
        cert = PlatformCertification(
            name=name,
            cert_type=cert_type,
            approved_by=approved_by,
        )
        return self._cert_repo.save(cert)

    async def get_certification(self, cert_id: str) -> Optional[PlatformCertification]:
        """Retrieve a certification by ID."""
        return self._cert_repo.find_by_id(cert_id)

    async def list_certifications(self) -> list[PlatformCertification]:
        """Return all certifications."""
        return self._cert_repo.find_all()

    async def list_certifications_by_type(self, cert_type: str) -> list[PlatformCertification]:
        """Return certifications filtered by type."""
        return self._cert_repo.find_by_type(cert_type)

    async def list_certifications_by_status(self, status: str) -> list[PlatformCertification]:
        """Return certifications filtered by status."""
        return self._cert_repo.find_by_status(status)

    async def update_certification(
        self, cert_id: str, data: dict[str, Any]
    ) -> Optional[PlatformCertification]:
        """Update arbitrary fields on a certification."""
        return self._cert_repo.update(cert_id, data)

    async def delete_certification(self, cert_id: str) -> bool:
        """Remove a certification record."""
        return self._cert_repo.delete(cert_id)

    async def start_certification(self, cert_id: str) -> Optional[PlatformCertification]:
        """Transition certification to in_progress."""
        cert = self._cert_repo.find_by_id(cert_id)
        if cert is None:
            return None
        cert.mark_in_progress()
        return self._cert_repo.save(cert)

    async def add_requirement(
        self,
        certification_id: str,
        requirement: str,
        description: str = "",
    ) -> CertificationRequirement:
        """Add a requirement to a certification."""
        cert = self._cert_repo.find_by_id(certification_id)
        if cert is None:
            raise ValueError(f"Certification not found: {certification_id}")
        req = CertificationRequirement(
            certification_id=certification_id,
            requirement=requirement,
            description=description,
        )
        return self._requirement_repo.save(req)

    async def get_requirements(self, certification_id: str) -> list[CertificationRequirement]:
        """List all requirements for a certification."""
        return self._requirement_repo.find_by_certification_id(certification_id)

    async def fulfill_requirement(
        self, requirement_id: str, evidence: str = ""
    ) -> Optional[CertificationRequirement]:
        """Mark a requirement as fulfilled."""
        req = self._requirement_repo.find_by_id(requirement_id)
        if req is None:
            return None
        req.fulfill(evidence)
        return self._requirement_repo.save(req)

    async def unfulfill_requirement(
        self, requirement_id: str
    ) -> Optional[CertificationRequirement]:
        """Mark a requirement as no longer met."""
        req = self._requirement_repo.find_by_id(requirement_id)
        if req is None:
            return None
        req.unfulfill()
        return self._requirement_repo.save(req)

    async def delete_requirement(self, requirement_id: str) -> bool:
        """Remove a requirement."""
        return self._requirement_repo.delete(requirement_id)

    async def evaluate_certification(
        self, certification_id: str
    ) -> Optional[PlatformCertification]:
        """Evaluate a certification against its requirements.

        When all requirements are met the certification transitions to certified.
        """
        cert = self._cert_repo.find_by_id(certification_id)
        if cert is None:
            return None

        requirements = self._requirement_repo.find_by_certification_id(certification_id)
        if not requirements:
            return cert

        total = len(requirements)
        met = sum(1 for r in requirements if r.met)
        all_met = met == total

        if all_met:
            cert.approve(cert.approved_by or "system")
        else:
            cert.mark_in_progress()

        return self._cert_repo.save(cert)

    async def issue_certification(
        self,
        cert_id: str,
        approver: str,
        expires_at: datetime | None = None,
        evidence: list[str] | None = None,
        metrics: dict[str, float] | None = None,
    ) -> Optional[PlatformCertification]:
        """Directly issue (approve) a certification."""
        cert = self._cert_repo.find_by_id(cert_id)
        if cert is None:
            return None
        cert.approve(approver)
        if expires_at is not None:
            cert.expires_at = expires_at
        if evidence is not None:
            for item in evidence:
                cert.add_evidence(item)
        if metrics is not None:
            cert.metrics.update(metrics)
        return self._cert_repo.save(cert)

    async def revoke_certification(self, cert_id: str) -> Optional[PlatformCertification]:
        """Revoke a previously granted certification."""
        cert = self._cert_repo.find_by_id(cert_id)
        if cert is None:
            return None
        cert.revoke()
        return self._cert_repo.save(cert)

    async def expire_certification(self, cert_id: str) -> Optional[PlatformCertification]:
        """Mark a certification as expired."""
        cert = self._cert_repo.find_by_id(cert_id)
        if cert is None:
            return None
        cert.expire()
        return self._cert_repo.save(cert)

    async def add_finding(self, cert_id: str, finding: str) -> Optional[PlatformCertification]:
        """Add a finding to a certification."""
        cert = self._cert_repo.find_by_id(cert_id)
        if cert is None:
            return None
        cert.add_finding(finding)
        return self._cert_repo.save(cert)

    async def add_corrective_action(
        self, cert_id: str, action: str
    ) -> Optional[PlatformCertification]:
        """Add a corrective action to a certification."""
        cert = self._cert_repo.find_by_id(cert_id)
        if cert is None:
            return None
        cert.add_corrective_action(action)
        return self._cert_repo.save(cert)

    async def generate_report(self, title: str = "Certification Report") -> PlatformCertificationReport:
        """Generate an aggregated certification report."""
        certs = self._cert_repo.find_all()
        report = PlatformCertificationReport(title=title, certifications=certs)
        report.compute_score()
        report.compute_overall_status()
        return self._report_repo.save(report)

    async def get_latest_report(self) -> Optional[PlatformCertificationReport]:
        """Return the most recent certification report."""
        return self._report_repo.find_latest()

    async def list_reports(self) -> list[PlatformCertificationReport]:
        """Return all generated certification reports."""
        return self._report_repo.find_all()
