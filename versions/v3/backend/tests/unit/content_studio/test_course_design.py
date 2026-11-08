"""Tests for content studio entities and services — CourseDesign, ContentBlock, LessonDesign, VirtualLab, MultimediaAsset, ContentTemplate, PublishRequest, A11yCheck, EditorialReview."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.content_studio.domain.entities.course_designer import (
    BlockType,
    ContentBlock,
    CourseDesign,
    CourseStatus,
    InteractiveActivity,
    LessonDesign,
    ModuleDesign,
    Program,
    ProgramStatus,
    UnitDesign,
)
from app.content_studio.domain.entities.virtual_lab import LabStep, VirtualLab, LabStatus, LabTemplate
from app.content_studio.domain.entities.multimedia import AssetCollection, AssetType, MultimediaAsset, AssetValidationResult
from app.content_studio.domain.entities.template_studio import ContentTemplate, TemplateType, TemplateInstance, TemplateVersion
from app.content_studio.domain.entities.publishing import ContentVersion, PublishHistory, PublishRequest, PublishStatus
from app.content_studio.domain.entities.a11y_validator import A11yCheck, A11yRemediation, A11yValidationReport
from app.content_studio.domain.entities.review import EditorialReview, ReviewComment, ReviewDecision, ReviewDecisionType, ReviewStage


class TestContentBlock:
    def test_defaults(self):
        b = ContentBlock()
        assert b.block_type == BlockType.TEXT
        assert b.accessible is True

    def test_mark_inaccessible(self):
        b = ContentBlock()
        b.mark_inaccessible("missing alt")
        assert b.accessible is False
        assert b.metadata["inaccessibility_reason"] == "missing alt"


class TestLessonDesign:
    def test_add_block(self):
        l = LessonDesign(name="Intro")
        b = ContentBlock(content="Hello")
        l.add_content_block(b)
        assert l.get_block_count() == 1
        assert b.order == 0

    def test_remove_block(self):
        l = LessonDesign(name="Intro")
        b = ContentBlock(content="Hello")
        l.add_content_block(b)
        assert l.remove_content_block(b.id) is True
        assert l.get_block_count() == 0

    def test_calculate_estimated_minutes(self):
        l = LessonDesign(name="Test")
        l.add_content_block(ContentBlock())
        l.add_content_block(ContentBlock())
        l.add_activity(InteractiveActivity())
        assert l.calculate_estimated_minutes() == (2 * 3) + (1 * 10)


class TestCourseDesign:
    def test_defaults(self):
        c = CourseDesign()
        assert c.status == CourseStatus.DRAFT
        assert c.version == 1

    def test_add_unit(self):
        c = CourseDesign(name="Test")
        u = UnitDesign(name="Unit 1")
        c.add_unit(u)
        assert len(c.units) == 1

    def test_increment_version(self):
        c = CourseDesign()
        c.increment_version()
        assert c.version == 2

    def test_update_status(self):
        c = CourseDesign()
        c.update_status(CourseStatus.PUBLISHED)
        assert c.status == CourseStatus.PUBLISHED


class TestProgram:
    def test_add_course(self):
        p = Program(name="Prog")
        p.add_course("c1")
        assert p.get_course_count() == 1

    def test_remove_course(self):
        p = Program(name="Prog")
        p.add_course("c1")
        assert p.remove_course("c1") is True
        assert p.get_course_count() == 0


class TestVirtualLab:
    def test_add_step(self):
        v = VirtualLab(name="Lab1")
        s = LabStep(title="Step 1")
        v.add_step(s)
        assert v.get_step_count() == 1

    def test_remove_step(self):
        v = VirtualLab(name="Lab1")
        s = LabStep(title="Step 1")
        v.add_step(s)
        assert v.remove_step(s.id) is True
        assert v.get_step_count() == 0

    def test_reorder_steps(self):
        v = VirtualLab(name="Lab1")
        s1 = LabStep(title="A")
        s2 = LabStep(title="B")
        v.add_step(s1)
        v.add_step(s2)
        assert v.reorder_steps([s2.id, s1.id]) is True
        assert v.steps[0].title == "B"


class TestLabTemplate:
    def test_create_lab(self):
        t = LabTemplate(name="T", template_type="hands_on")
        lab = t.create_lab_from_template("MyLab")
        assert lab.name == "MyLab"
        assert lab.steps == []

    def test_add_step_template(self):
        t = LabTemplate(name="T")
        t.add_step_template({"title": "S1"})
        assert t.get_step_count() == 1


class TestMultimediaAsset:
    def test_defaults(self):
        m = MultimediaAsset()
        assert m.asset_type == AssetType.IMAGE
        assert m.accessible is True

    def test_update_alt_text(self):
        m = MultimediaAsset()
        m.update_alt_text("description")
        assert m.alt_text == "description"
        assert m.accessible is True

    def test_has_alt_text(self):
        m = MultimediaAsset()
        assert m.has_alt_text() is False
        m.update_alt_text("alt")
        assert m.has_alt_text() is True

    def test_is_media_type(self):
        m = MultimediaAsset(asset_type=AssetType.AUDIO)
        assert m.is_media_type() is True
        m.asset_type = AssetType.PDF
        assert m.is_media_type() is False


class TestAssetValidationResult:
    def test_add_issue(self):
        r = AssetValidationResult(asset_id="a1")
        r.add_issue("missing alt")
        assert r.valid is False
        assert r.get_issue_count() == 1

    def test_has_critical_issues(self):
        r = AssetValidationResult(asset_id="a1")
        assert r.has_critical_issues() is False
        r.add_issue("invalid format")
        assert r.has_critical_issues() is True


class TestContentTemplate:
    def test_defaults(self):
        t = ContentTemplate()
        assert t.template_type == TemplateType.LESSON
        assert t.version == 1

    def test_update_structure(self):
        t = ContentTemplate()
        t.set_structure_key("required_fields", ["title"])
        assert t.get_required_fields() == ["title"]


class TestPublishRequest:
    def test_defaults(self):
        p = PublishRequest()
        assert p.status == PublishStatus.PENDING
        assert p.digital_signature == ""

    def test_mark_published(self):
        p = PublishRequest()
        mark = MagicMock()
        p.sign("sig")
        p.mark_validated()
        assert p.is_ready_to_publish() is True

    def test_mark_rejected(self):
        p = PublishRequest()
        p.mark_rejected("bad content")
        assert p.status == PublishStatus.REJECTED
        assert p.validation_results["rejection_reason"] == "bad content"


class TestA11yCheck:
    def test_defaults(self):
        c = A11yCheck()
        assert c.passed is False
        assert c.severity == "error"

    def test_mark_passed(self):
        c = A11yCheck()
        c.mark_passed()
        assert c.passed is True

    def test_mark_failed(self):
        c = A11yCheck(severity="critical")
        c.mark_failed("add alt text")
        assert c.is_critical() is True
        assert c.remediation == "add alt text"


class TestA11yValidationReport:
    def test_add_check(self):
        r = A11yValidationReport()
        c = A11yCheck(check_type="alt_text")
        c.mark_passed()
        r.add_check(c)
        assert r.passed == 1

    def test_get_critical_failures(self):
        r = A11yValidationReport()
        c = A11yCheck(check_type="contrast", severity="critical")
        r.add_check(c)
        assert len(r.get_critical_failures()) == 1

    def test_has_critical_failures(self):
        r = A11yValidationReport()
        c = A11yCheck(check_type="contrast", severity="critical")
        r.add_check(c)
        assert r.has_critical_failures() is True


class TestEditorialReview:
    def test_defaults(self):
        r = EditorialReview()
        assert r.current_stage == ReviewStage.DRAFT

    def test_advance_stage(self):
        r = EditorialReview()
        r.advance_stage()
        assert r.current_stage == ReviewStage.PEER_REVIEW

    def test_is_complete(self):
        r = EditorialReview(current_stage=ReviewStage.PUBLICATION)
        assert r.is_complete() is True

    def test_get_stage_progress(self):
        r = EditorialReview()
        assert r.get_stage_progress_pct() == 0.0


class TestCourseDesignerService:
    def test_create_program(self):
        from app.content_studio.services.course_designer_service import CourseDesignerService
        repo = MagicMock()
        repo.create = MagicMock(return_value={"id": "p1"})
        service = CourseDesignerService(repo, MagicMock())
        result = service.create_program({"name": "Test"})
        assert result["id"] == "p1"

    def test_get_program(self):
        from app.content_studio.services.course_designer_service import CourseDesignerService
        repo = MagicMock()
        repo.get_by_id = MagicMock(return_value={"id": "p1", "name": "Test"})
        service = CourseDesignerService(repo, MagicMock())
        result = service.get_program("p1")
        assert result["name"] == "Test"

    def test_delete_program_not_found(self):
        from app.content_studio.services.course_designer_service import CourseDesignerService
        repo = MagicMock()
        repo.get_by_id = MagicMock(return_value=None)
        service = CourseDesignerService(repo, MagicMock())
        with pytest.raises(ValueError, match="not found"):
            service.delete_program("bad")


class TestPublishingCenterService:
    def test_request_publish(self):
        from app.content_studio.services.publishing_center_service import PublishingCenterService
        pub_repo = MagicMock()
        pub_repo.create = MagicMock(return_value={"id": "r1"})
        hist_repo = MagicMock()
        hist_repo.create = MagicMock()
        ver_repo = MagicMock()
        service = PublishingCenterService(pub_repo, hist_repo, ver_repo)
        result = service.request_publish("c1", "course", "user1")
        assert result["id"] == "r1"

    def test_get_publish_request(self):
        from app.content_studio.services.publishing_center_service import PublishingCenterService
        pub_repo = MagicMock()
        pub_repo.get_by_id = MagicMock(return_value={"id": "r1", "status": "pending"})
        service = PublishingCenterService(pub_repo, MagicMock(), MagicMock())
        result = service.get_publish_request("r1")
        assert result["status"] == "pending"


class TestTemplateStudioService:
    def test_create_template(self):
        from app.content_studio.services.template_studio_service import TemplateStudioService
        repo = MagicMock()
        repo.create = MagicMock(return_value={"id": "t1"})
        repo.get_by_id = MagicMock(return_value=None)
        service = TemplateStudioService(repo)
        result = service.create_template({"name": "Test", "template_type": "lesson"})
        assert result["id"] == "t1"

    def test_get_template(self):
        from app.content_studio.services.template_studio_service import TemplateStudioService
        repo = MagicMock()
        repo.get_by_id = MagicMock(return_value={"id": "t1"})
        service = TemplateStudioService(repo)
        result = service.get_template("t1")
        assert result["id"] == "t1"
