"""Tests for LMS entities — Classroom, Enrollment, GradebookEntry, Competency, LmsAssessment."""

from __future__ import annotations

from datetime import datetime, timezone

from app.lms.domain.entities.classroom import Classroom, ClassroomMember, ClassroomRole, ClassroomStatus
from app.lms.domain.entities.enrollment import Enrollment, EnrollmentStatus
from app.lms.domain.entities.competency import Competency, CompetencyLevel, LearnerCompetencyProgress, CompetencyStatus
from app.lms.domain.entities.gradebook import GradebookEntry, GradeItem, GradeScale, GradingCategory
from app.lms.domain.entities.assessment_lms import (
    AssessmentAttempt,
    AssessmentStatus,
    AssessmentType,
    LmsAssessment,
    QuestionGroup,
)


class TestClassroom:
    def test_default_values(self):
        c = Classroom()
        assert c.capacity == 30
        assert c.status == ClassroomStatus.ACTIVE

    def test_add_member(self):
        c = Classroom(name="CS101")
        member = c.add_member("user1", ClassroomRole.LEARNER)
        assert member.user_id == "user1"
        assert c.member_count == 1

    def test_add_member_duplicate_raises(self):
        c = Classroom(name="CS101")
        c.add_member("user1")
        import pytest
        with pytest.raises(ValueError, match="already an active member"):
            c.add_member("user1")

    def test_add_member_when_full_raises(self):
        c = Classroom(name="CS101", capacity=1)
        c.add_member("user1")
        import pytest
        with pytest.raises(ValueError, match="capacity"):
            c.add_member("user2")

    def test_remove_member(self):
        c = Classroom(name="CS101")
        c.add_member("user1")
        assert c.remove_member("user1") is True
        assert c.member_count == 0

    def test_active_members(self):
        c = Classroom()
        m = c.add_member("user1")
        with_observer = c.add_member("user2", ClassroomRole.OBSERVER)
        assert len(c.active_members) == 2

    def test_available_seats(self):
        c = Classroom(capacity=10)
        c.add_member("user1")
        assert c.available_seats == 9


class TestEnrollment:
    def test_default_values(self):
        e = Enrollment()
        assert e.status == EnrollmentStatus.PENDING

    def test_activate(self):
        e = Enrollment()
        e.activate()
        assert e.status == EnrollmentStatus.ACTIVE

    def test_activate_non_pending_raises(self):
        e = Enrollment(status=EnrollmentStatus.ACTIVE)
        import pytest
        with pytest.raises(ValueError):
            e.activate()

    def test_complete(self):
        e = Enrollment(status=EnrollmentStatus.ACTIVE)
        e.complete(grade="A")
        assert e.status == EnrollmentStatus.COMPLETED
        assert e.grade == "A"

    def test_drop(self):
        e = Enrollment(status=EnrollmentStatus.ACTIVE)
        e.drop()
        assert e.status == EnrollmentStatus.DROPPED


class TestCompetency:
    def test_default_values(self):
        c = Competency()
        assert c.level == CompetencyLevel.BEGINNER

    def test_level_value(self):
        c = Competency(level=CompetencyLevel.ADVANCED)
        assert c.level_value == 3

    def test_to_dict(self):
        c = Competency(name="Security", domain="Cybersec", level=CompetencyLevel.INTERMEDIATE)
        d = c.to_dict()
        assert d["name"] == "Security"
        assert d["level"] == "intermediate"

    def test_completency_progress_lifecycle(self):
        p = LearnerCompetencyProgress()
        assert p.status == CompetencyStatus.NOT_STARTED
        p.start()
        assert p.status == CompetencyStatus.IN_PROGRESS
        p.achieve()
        assert p.is_completed is True
        p.master()
        assert p.status == CompetencyStatus.MASTERED


class TestLmsAssessment:
    def test_default_values(self):
        a = LmsAssessment()
        assert a.status == AssessmentStatus.DRAFT
        assert a.passing_score == 70.0

    def test_publish(self):
        a = LmsAssessment()
        a.publish()
        assert a.status == AssessmentStatus.PUBLISHED

    def test_close(self):
        a = LmsAssessment()
        a.publish()
        a.close()
        assert a.status == AssessmentStatus.CLOSED

    def test_is_passed(self):
        a = LmsAssessment(passing_score=60.0)
        assert a.is_passed(75.0) is True
        assert a.is_passed(50.0) is False

    def test_attempt_submit(self):
        att = AssessmentAttempt()
        att.submit(85.0, "Great job")
        assert att.is_submitted is True
        assert att.score == 85.0


class TestGradebook:
    def test_add_item(self):
        g = GradebookEntry()
        item = GradeItem(name="Midterm", points_possible=100.0, weight=1.5)
        g.add_item(item)
        assert len(g.items) == 1
        assert item.gradebook_id == g.id

    def test_weighted_average(self):
        g = GradebookEntry()
        i1 = GradeItem(name="Quiz 1", points_possible=10.0, weight=1.0)
        i2 = GradeItem(name="Quiz 2", points_possible=20.0, weight=2.0)
        g.add_item(i1)
        g.add_item(i2)
        from app.lms.domain.entities.gradebook import GradeEntry
        entries = [
            GradeEntry(grade_item_id=i1.id, score=8.0),
            GradeEntry(grade_item_id=i2.id, score=16.0),
        ]
        avg = g.calculate_weighted_average(entries)
        assert avg > 0

    def test_letter_grade(self):
        scale = GradeScale(name="Default")
        scale.scale = {"A": (90.0, 100.0), "B": (80.0, 89.99), "C": (70.0, 79.99)}
        g = GradebookEntry()
        i = GradeItem(name="Final", points_possible=100.0, weight=1.0)
        g.add_item(i)
        from app.lms.domain.entities.gradebook import GradeEntry
        entries = [GradeEntry(grade_item_id=i.id, score=92.0)]
        letter = g.calculate_letter_grade(entries, scale)
        assert letter == "A"


class TestQuestionGroup:
    def test_add_question(self):
        qg = QuestionGroup(name="Group A")
        qg.add_question({"id": "q1", "text": "Q?"})
        assert qg.question_count == 1

    def test_remove_question(self):
        qg = QuestionGroup(name="Group A")
        qg.add_question({"id": "q1"})
        qg.remove_question(0)
        assert qg.question_count == 0
