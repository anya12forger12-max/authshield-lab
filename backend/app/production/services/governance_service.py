"""Governance service for reviews, audits, policies, and reports."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from ...shared.logging_config import get_logger
from ...shared.events.event_bus import EventBus
from ..domain.entities.governance import (
    ArchitectureAudit,
    AuditCheck,
    GovernanceArea,
    GovernancePolicy,
    GovernanceReport,
    GovernanceReview,
)
from ..domain.interfaces import (
    IArchitectureAuditRepository,
    IGovernancePolicyRepository,
    IGovernanceReportRepository,
    IGovernanceReviewRepository,
)
from ..domain.events.production_events import GovernanceReviewCompletedEvent

logger = get_logger("production.governance_service")


class GovernanceService:
    """Manages governance reviews, policies, audits, and reports.

    Parameters
    ----------
    review_repo:
        Repository for governance review persistence.
    policy_repo:
        Repository for governance policy persistence.
    audit_repo:
        Repository for architecture audit persistence.
    report_repo:
        Repository for governance report persistence.
    event_bus:
        Optional event bus for domain events.
    """

    def __init__(
        self,
        review_repo: IGovernanceReviewRepository,
        policy_repo: IGovernancePolicyRepository,
        audit_repo: IArchitectureAuditRepository,
        report_repo: IGovernanceReportRepository,
        event_bus: Optional[EventBus] = None,
    ) -> None:
        self._review_repo = review_repo
        self._policy_repo = policy_repo
        self._audit_repo = audit_repo
        self._report_repo = report_repo
        self._event_bus = event_bus

    async def _publish_event(self, event: Any) -> None:
        if self._event_bus is not None:
            await self._event_bus.publish(event)

    async def schedule_review(
        self,
        area: GovernanceArea,
        title: str,
        description: str,
        reviewer: str,
        scheduled_at: Optional[datetime] = None,
    ) -> GovernanceReview:
        """Schedule a new governance review."""
        review = GovernanceReview(
            id=str(uuid.uuid4()),
            area=area,
            title=title,
            description=description,
            status="pending",
            reviewer=reviewer,
            scheduled_at=scheduled_at or datetime.now(timezone.utc),
        )
        await self._review_repo.create(review)
        logger.info("review_scheduled", review_id=review.id, area=area.value)
        return review

    async def get_review(self, review_id: str) -> Optional[GovernanceReview]:
        """Retrieve a governance review by ID."""
        return await self._review_repo.get_by_id(review_id)

    async def list_reviews(
        self, page: int = 1, per_page: int = 20
    ) -> dict:
        """List all governance reviews with pagination."""
        return await self._review_repo.get_all(page=page, per_page=per_page)

    async def get_reviews_by_area(self, area: str) -> list[GovernanceReview]:
        """List reviews filtered by governance area."""
        return await self._review_repo.get_by_area(area)

    async def complete_review(
        self,
        review_id: str,
        status: str,
        recommendations: Optional[list[str]] = None,
    ) -> Optional[GovernanceReview]:
        """Mark a review as completed with a status and recommendations."""
        review = await self._review_repo.get_by_id(review_id)
        if review is None:
            return None

        valid_statuses = {"approved", "rejected", "needs_revision"}
        if status not in valid_statuses:
            raise ValueError(f"Invalid review status: {status}")

        data: dict[str, Any] = {
            "status": status,
            "completed_at": datetime.now(timezone.utc),
        }
        if recommendations is not None:
            data["recommendations"] = recommendations

        updated = await self._review_repo.update(review_id, data)
        if updated is not None:
            await self._publish_event(
                GovernanceReviewCompletedEvent(
                    review_id=review_id,
                    area=review.area.value if hasattr(review.area, "value") else str(review.area),
                    status=status,
                    module="production",
                )
            )
        logger.info("review_completed", review_id=review_id, status=status)
        return updated

    async def create_policy(
        self,
        area: GovernanceArea,
        name: str,
        description: str,
        requirements: Optional[list[str]] = None,
        review_frequency_days: int = 30,
    ) -> GovernancePolicy:
        """Register a new governance policy."""
        policy = GovernancePolicy(
            id=str(uuid.uuid4()),
            area=area,
            name=name,
            description=description,
            requirements=requirements or [],
            review_frequency_days=review_frequency_days,
        )
        await self._policy_repo.create(policy)
        logger.info("policy_created", policy_id=policy.id, name=name)
        return policy

    async def get_policy(self, policy_id: str) -> Optional[GovernancePolicy]:
        """Retrieve a governance policy by ID."""
        return await self._policy_repo.get_by_id(policy_id)

    async def list_policies(self) -> list[GovernancePolicy]:
        """List all governance policies."""
        return await self._policy_repo.get_all()

    async def get_policies_by_area(self, area: str) -> list[GovernancePolicy]:
        """List policies filtered by area."""
        return await self._policy_repo.get_by_area(area)

    async def update_policy(
        self, policy_id: str, data: dict[str, Any]
    ) -> Optional[GovernancePolicy]:
        """Update a governance policy."""
        return await self._policy_repo.update(policy_id, data)

    async def mark_policy_reviewed(self, policy_id: str) -> Optional[GovernancePolicy]:
        """Mark a policy as recently reviewed."""
        return await self._policy_repo.update(
            policy_id, {"last_reviewed_at": datetime.now(timezone.utc)}
        )

    async def get_policies_needing_review(self) -> list[GovernancePolicy]:
        """Find policies whose review frequency has elapsed."""
        now = datetime.now(timezone.utc)
        all_policies = await self._policy_repo.get_all()
        overdue: list[GovernancePolicy] = []
        for policy in all_policies:
            if policy.last_reviewed_at is None:
                overdue.append(policy)
                continue
            elapsed = (now - policy.last_reviewed_at).days
            if elapsed >= policy.review_frequency_days:
                overdue.append(policy)
        return overdue

    async def run_architecture_audit(
        self, name: str, checks: Optional[list[dict[str, str]]] = None
    ) -> ArchitectureAudit:
        """Execute an architecture audit with the given checks."""
        audit_checks: list[AuditCheck] = []
        if checks:
            for check_data in checks:
                audit_checks.append(
                    AuditCheck(
                        name=check_data.get("name", ""),
                        category=check_data.get("category", ""),
                        status=check_data.get("status", "pass"),
                        details=check_data.get("details", ""),
                    )
                )

        total = len(audit_checks)
        passed = sum(1 for c in audit_checks if c.status == "pass")
        warnings = sum(1 for c in audit_checks if c.status == "warning")
        score = (passed / total * 100) if total > 0 else 0.0

        if all(c.status == "pass" for c in audit_checks):
            overall = "pass"
        elif any(c.status == "fail" for c in audit_checks):
            overall = "fail"
        else:
            overall = "warning"

        audit = ArchitectureAudit(
            id=str(uuid.uuid4()),
            name=name,
            checks=audit_checks,
            overall_status=overall,
            score=score,
            generated_at=datetime.now(timezone.utc),
        )
        await self._audit_repo.create(audit)
        logger.info(
            "architecture_audit_completed",
            audit_id=audit.id,
            score=score,
            status=overall,
        )
        return audit

    async def get_audit(self, audit_id: str) -> Optional[ArchitectureAudit]:
        """Retrieve an architecture audit by ID."""
        return await self._audit_repo.get_by_id(audit_id)

    async def list_audits(
        self, page: int = 1, per_page: int = 20
    ) -> dict:
        """List all architecture audits with pagination."""
        return await self._audit_repo.get_all(page=page, per_page=per_page)

    async def generate_report(
        self,
        title: str,
        area: GovernanceArea,
        findings: Optional[list[str]] = None,
        recommendations: Optional[list[str]] = None,
    ) -> GovernanceReport:
        """Generate a governance report for an area."""
        reviews_result = await self._review_repo.get_all(page=1, per_page=1000)
        area_reviews = [
            r
            for r in reviews_result.get("items", [])
            if (r.area.value if hasattr(r.area, "value") else r.area) == area.value
        ]

        approved = sum(1 for r in area_reviews if r.status == "approved")
        total = len(area_reviews)
        score = (approved / total * 100) if total > 0 else 100.0

        report = GovernanceReport(
            id=str(uuid.uuid4()),
            title=title,
            area=area,
            reviews=area_reviews,
            findings=findings or [],
            recommendations=recommendations or [],
            score=score,
            generated_at=datetime.now(timezone.utc),
        )
        await self._report_repo.create(report)
        logger.info("governance_report_generated", report_id=report.id, area=area.value)
        return report

    async def get_report(self, report_id: str) -> Optional[GovernanceReport]:
        """Retrieve a governance report by ID."""
        return await self._report_repo.get_by_id(report_id)

    async def list_reports(
        self, page: int = 1, per_page: int = 20
    ) -> dict:
        """List all governance reports with pagination."""
        return await self._report_repo.get_all(page=page, per_page=per_page)
