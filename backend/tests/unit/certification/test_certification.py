"""Tests for certification entities and services — PlatformCertification, ValidationCheck, DependencyLifecycle, SustainabilityDashboard, CertificationService, PlatformValidationService, SustainabilityService."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.certification.domain.entities.certification_center import (
    CertificationRequirement,
    CertificationStatus,
    PlatformCertification,
    PlatformCertificationReport,
)
from app.certification.domain.entities.platform_validation import (
    FinalAcceptanceTest,
    PlatformValidationReport,
    SubsystemValidation,
    ValidationCheck,
)
from app.certification.domain.entities.sustainability import (
    APIStabilityReport,
    DependencyLifecycle,
    DependencyStatus,
    DocumentationFreshness,
    MaintenanceRoadmap,
    ModuleOwnership,
    RoadmapItem,
    SustainabilityDashboard,
)


class TestPlatformCertification:
    def test_defaults(self):
        c = PlatformCertification()
        assert c.status == CertificationStatus.PENDING

    def test_is_active_when_certified(self):
        c = PlatformCertification(status=CertificationStatus.CERTIFIED)
        assert c.is_active() is True

    def test_is_active_when_failed(self):
        c = PlatformCertification(status=CertificationStatus.FAILED)
        assert c.is_active() is False

    def test_approve(self):
        c = PlatformCertification()
        c.approve("admin")
        assert c.status == CertificationStatus.CERTIFIED
        assert c.approved_by == "admin"

    def test_add_evidence(self):
        c = PlatformCertification()
        c.add_evidence("audit.pdf")
        assert "audit.pdf" in c.evidence

    def test_completion_ratio(self):
        c = PlatformCertification()
        c.add_evidence("e1")
        c.add_evidence("e2")
        assert c.completion_ratio(4) == 0.5

    def test_completion_ratio_zero_requirements(self):
        c = PlatformCertification()
        assert c.completion_ratio(0) == 0.0


class TestCertificationRequirement:
    def test_fulfill(self):
        r = CertificationRequirement()
        r.fulfill("done")
        assert r.met is True
        assert r.evidence == "done"

    def test_unfulfill(self):
        r = CertificationRequirement(met=True, evidence="done")
        r.unfulfill()
        assert r.met is False
        assert r.evidence == ""


class TestPlatformCertificationReport:
    def test_compute_score(self):
        c1 = PlatformCertification(status=CertificationStatus.CERTIFIED)
        c2 = PlatformCertification(status=CertificationStatus.PENDING)
        r = PlatformCertificationReport(certifications=[c1, c2])
        assert r.compute_score() == 50.0

    def test_compute_overall_status(self):
        c1 = PlatformCertification(status=CertificationStatus.CERTIFIED)
        c2 = PlatformCertification(status=CertificationStatus.CERTIFIED)
        r = PlatformCertificationReport(certifications=[c1, c2])
        assert r.compute_overall_status() == "certified"

    def test_compute_overall_status_failed(self):
        c1 = PlatformCertification(status=CertificationStatus.CERTIFIED)
        c2 = PlatformCertification(status=CertificationStatus.FAILED)
        r = PlatformCertificationReport(certifications=[c1, c2])
        assert r.compute_overall_status() == "failed"

    def test_active_certifications(self):
        c1 = PlatformCertification(status=CertificationStatus.CERTIFIED)
        c2 = PlatformCertification(status=CertificationStatus.EXPIRED)
        r = PlatformCertificationReport(certifications=[c1, c2])
        assert len(r.active_certifications()) == 1


class TestValidationCheck:
    def test_mark_passed(self):
        v = ValidationCheck()
        v.mark_passed("ok")
        assert v.status == "passed"

    def test_mark_failed(self):
        v = ValidationCheck()
        v.mark_failed("error")
        assert v.status == "failed"

    def test_mark_skipped(self):
        v = ValidationCheck()
        v.mark_skipped("not needed")
        assert v.status == "skipped"


class TestSubsystemValidation:
    def test_add_check(self):
        sv = SubsystemValidation(subsystem="auth")
        c = ValidationCheck(subsystem="auth", check_name="config")
        c.mark_passed()
        sv.add_check(c)
        assert sv.passed == 1

    def test_is_compliant(self):
        sv = SubsystemValidation(subsystem="auth")
        c = ValidationCheck(subsystem="auth", check_name="config")
        c.mark_passed()
        sv.add_check(c)
        assert sv.is_compliant(100.0) is True


class TestPlatformValidationReport:
    def test_failing_subsystems(self):
        sv1 = SubsystemValidation(subsystem="auth")
        sv2 = SubsystemValidation(subsystem="bad")
        c = ValidationCheck(subsystem="bad", check_name="test")
        c.mark_failed("fail")
        sv2.add_check(c)
        report = PlatformValidationReport(subsystems=[sv1, sv2])
        assert len(report.failing_subsystems()) == 1


class TestFinalAcceptanceTest:
    def test_run_all_pass(self):
        sv = SubsystemValidation(subsystem="auth")
        c = ValidationCheck(check_name="c1")
        c.mark_passed()
        sv.add_check(c)
        fat = FinalAcceptanceTest(version="1.0", results={"auth": sv})
        assert fat.run() == "passed"

    def test_run_any_fail(self):
        sv = SubsystemValidation(subsystem="auth")
        c = ValidationCheck(check_name="c1")
        c.mark_failed("err")
        sv.add_check(c)
        fat = FinalAcceptanceTest(version="1.0", results={"auth": sv})
        assert fat.run() == "failed"

    def test_run_empty(self):
        fat = FinalAcceptanceTest(version="1.0")
        assert fat.run() == "pending"


class TestDependencyLifecycle:
    def test_is_active(self):
        d = DependencyLifecycle(name="pkg", version="1.0", status=DependencyStatus.SUPPORTED)
        assert d.is_active() is True

    def test_needs_action(self):
        d = DependencyLifecycle(name="pkg", version="1.0", update_available=True)
        assert d.needs_action() is True

    def test_deprecated_needs_action(self):
        d = DependencyLifecycle(name="pkg", version="1.0", status=DependencyStatus.DEPRECATED)
        assert d.needs_action() is True


class TestAPIStabilityReport:
    def test_recalculate_score(self):
        r = APIStabilityReport(version="1.0", endpoints=100, deprecated=10, breaking_changes=2)
        score = r.recalculate_score()
        assert score < 100.0

    def test_recalculate_empty(self):
        r = APIStabilityReport()
        assert r.recalculate_score() == 100.0


class TestModuleOwnership:
    def test_needs_review(self):
        from datetime import datetime, timezone, timedelta
        m = ModuleOwnership(module="auth", owner="alice",
                            last_reviewed=datetime.now(timezone.utc) - timedelta(days=60))
        assert m.needs_review(30) is True

    def test_recent_review(self):
        m = ModuleOwnership(module="auth", owner="alice")
        assert m.needs_review(30) is False


class TestDocumentationFreshness:
    def test_recalculate_fresh(self):
        from datetime import datetime, timezone
        d = DocumentationFreshness(component="api", last_updated=datetime.now(timezone.utc))
        d.recalculate()
        assert d.status == "fresh"

    def test_recalculate_stale(self):
        from datetime import datetime, timezone, timedelta
        d = DocumentationFreshness(
            component="api",
            last_updated=datetime.now(timezone.utc) - timedelta(days=60),
        )
        d.recalculate()
        assert d.status == "stale"

    def test_recalculate_critical(self):
        from datetime import datetime, timezone, timedelta
        d = DocumentationFreshness(
            component="api",
            last_updated=datetime.now(timezone.utc) - timedelta(days=200),
        )
        d.recalculate()
        assert d.status == "critical"


class TestSustainabilityDashboard:
    def test_compute_maintenance_score(self):
        dep = DependencyLifecycle(name="pkg", version="1.0", status=DependencyStatus.SUPPORTED)
        api = APIStabilityReport(endpoints=100, stability_score=90.0)
        doc = DocumentationFreshness(component="api")
        doc.recalculate()
        d = SustainabilityDashboard(
            dependencies=[dep],
            api_stability=api,
            documentation=[doc],
        )
        score = d.compute_maintenance_score()
        assert 0 <= score <= 100

    def test_deprecated_dependencies(self):
        dep_supported = DependencyLifecycle(name="pkg1", version="1.0", status=DependencyStatus.SUPPORTED)
        dep_eol = DependencyLifecycle(name="pkg2", version="1.0", status=DependencyStatus.END_OF_LIFE)
        d = SustainabilityDashboard(dependencies=[dep_supported, dep_eol])
        assert len(d.deprecated_dependencies()) == 1


class TestCertificationService:
    @pytest.mark.asyncio
    async def test_create_certification(self):
        from app.certification.services.certification_service import CertificationService
        cert_repo = MagicMock()
        cert_repo.save = MagicMock(side_effect=lambda x: x)
        service = CertificationService(cert_repo, MagicMock(), MagicMock())
        result = await service.create_certification("Test", "security")
        assert result.name == "Test"

    @pytest.mark.asyncio
    async def test_get_certification(self):
        from app.certification.services.certification_service import CertificationService
        cert_repo = MagicMock()
        c = PlatformCertification(id="c1")
        cert_repo.find_by_id = MagicMock(return_value=c)
        service = CertificationService(cert_repo, MagicMock(), MagicMock())
        result = await service.get_certification("c1")
        assert result.id == "c1"

    @pytest.mark.asyncio
    async def test_add_requirement(self):
        from app.certification.services.certification_service import CertificationService
        cert_repo = MagicMock()
        cert_repo.find_by_id = MagicMock(return_value=PlatformCertification(id="c1"))
        req_repo = MagicMock()
        req_repo.save = MagicMock(side_effect=lambda x: x)
        service = CertificationService(cert_repo, req_repo, MagicMock())
        req = await service.add_requirement("c1", "Must pass audit")
        assert req.requirement == "Must pass audit"

    @pytest.mark.asyncio
    async def test_issue_certification(self):
        from app.certification.services.certification_service import CertificationService
        cert_repo = MagicMock()
        c = PlatformCertification(id="c1")
        cert_repo.find_by_id = MagicMock(return_value=c)
        cert_repo.save = MagicMock(side_effect=lambda x: x)
        service = CertificationService(cert_repo, MagicMock(), MagicMock())
        result = await service.issue_certification("c1", "admin")
        assert result.status == CertificationStatus.CERTIFIED

    @pytest.mark.asyncio
    async def test_revoke_certification(self):
        from app.certification.services.certification_service import CertificationService
        cert_repo = MagicMock()
        c = PlatformCertification(id="c1")
        cert_repo.find_by_id = MagicMock(return_value=c)
        cert_repo.save = MagicMock(side_effect=lambda x: x)
        service = CertificationService(cert_repo, MagicMock(), MagicMock())
        result = await service.revoke_certification("c1")
        assert result.status == CertificationStatus.FAILED


class TestPlatformValidationService:
    @pytest.mark.asyncio
    async def test_run_check_passed(self):
        from app.certification.services.platform_validation_service import PlatformValidationService
        check_repo = MagicMock()
        check_repo.save = MagicMock(side_effect=lambda x: x)
        service = PlatformValidationService(check_repo, MagicMock(), MagicMock(), MagicMock())
        check = await service.run_check("auth", "config")
        assert check.status == "passed"

    @pytest.mark.asyncio
    async def test_run_check_failed(self):
        from app.certification.services.platform_validation_service import PlatformValidationService
        check_repo = MagicMock()
        check_repo.save = MagicMock(side_effect=lambda x: x)
        service = PlatformValidationService(check_repo, MagicMock(), MagicMock(), MagicMock())
        check = await service.run_check("auth", "config", status="failed", details="error")
        assert check.status == "failed"

    @pytest.mark.asyncio
    async def test_validate_subsystem(self):
        from app.certification.services.platform_validation_service import PlatformValidationService
        check_repo = MagicMock()
        check_repo.save = MagicMock(side_effect=lambda x: x)
        sub_repo = MagicMock()
        sub_repo.find_by_subsystem = MagicMock(return_value=None)
        sub_repo.save = MagicMock(side_effect=lambda x: x)
        service = PlatformValidationService(check_repo, sub_repo, MagicMock(), MagicMock())
        sv = await service.validate_subsystem("auth")
        assert sv.subsystem == "auth"
        assert sv.passed == 4

    @pytest.mark.asyncio
    async def test_run_acceptance_test(self):
        from app.certification.services.platform_validation_service import PlatformValidationService
        check_repo = MagicMock()
        check_repo.save = MagicMock(side_effect=lambda x: x)
        sub_repo = MagicMock()
        check = ValidationCheck(subsystem="auth", check_name="config")
        check.mark_passed()
        sv = SubsystemValidation(subsystem="auth", checks=[check])
        sv._recalculate()
        sub_repo.find_all = MagicMock(return_value=[sv])
        sub_repo.find_by_subsystem = MagicMock(return_value=None)
        sub_repo.save = MagicMock(side_effect=lambda x: x)
        report_repo = MagicMock()
        report_repo.save = MagicMock(side_effect=lambda x: x)
        fat_repo = MagicMock()
        fat_repo.save = MagicMock(side_effect=lambda x: x)
        service = PlatformValidationService(check_repo, sub_repo, report_repo, fat_repo)
        fat = await service.run_acceptance_test("1.0", sign_off_required=["auth"])
        assert fat.version == "1.0"


class TestSustainabilityService:
    @pytest.mark.asyncio
    async def test_register_dependency(self):
        from app.certification.services.sustainability_service import SustainabilityService
        dep_repo = MagicMock()
        dep_repo.find_by_name = MagicMock(return_value=None)
        dep_repo.save = MagicMock(side_effect=lambda x: x)
        service = SustainabilityService(dep_repo, MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock())
        dep = await service.register_dependency("pkg", "1.0")
        assert dep.name == "pkg"

    @pytest.mark.asyncio
    async def test_record_api_stability(self):
        from app.certification.services.sustainability_service import SustainabilityService
        api_repo = MagicMock()
        api_repo.save = MagicMock(side_effect=lambda x: x)
        service = SustainabilityService(MagicMock(), api_repo, MagicMock(), MagicMock(), MagicMock(), MagicMock())
        report = await service.record_api_stability("1.0", endpoints=100, deprecated=5)
        assert report.version == "1.0"
        assert report.stability_score < 100.0

    @pytest.mark.asyncio
    async def test_generate_dashboard(self):
        from app.certification.services.sustainability_service import SustainabilityService
        dep_repo = MagicMock()
        dep_repo.find_all = MagicMock(return_value=[])
        api_repo = MagicMock()
        api_repo.find_latest = MagicMock(return_value=None)
        own_repo = MagicMock()
        own_repo.find_all = MagicMock(return_value=[])
        doc_repo = MagicMock()
        doc_repo.find_all = MagicMock(return_value=[])
        dashboard_repo = MagicMock()
        dashboard_repo.save = MagicMock(side_effect=lambda x: x)
        service = SustainabilityService(dep_repo, api_repo, own_repo, doc_repo, dashboard_repo, MagicMock())
        dashboard = await service.generate_dashboard()
        assert isinstance(dashboard, SustainabilityDashboard)
