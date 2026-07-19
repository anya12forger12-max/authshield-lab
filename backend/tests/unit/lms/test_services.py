"""Tests for LMS services — ClassroomService, EnrollmentService, GradebookService, CompetencyService."""

from __future__ import annotations

from unittest.mock import MagicMock

from app.lms.domain.entities.classroom import Classroom, ClassroomRole, ClassroomStatus
from app.lms.domain.entities.enrollment import Enrollment, EnrollmentStatus
from app.lms.domain.entities.competency import Competency, CompetencyLevel, LearnerCompetencyProgress
from app.lms.domain.entities.gradebook import GradeItem, GradeScale, GradingCategory
from app.lms.domain.entities.assessment_lms import LmsAssessment


class TestClassroomService:
    def test_create_classroom(self):
        from app.lms.services.classroom_service import ClassroomService
        repo = MagicMock()
        repo.create = MagicMock(return_value={"id": "c1", "name": "CS101", "description": "Intro to CS", "capacity": 50, "instructor_id": "ins1"})
        service = ClassroomService(repo)
        c = service.create_classroom({"name": "CS101", "description": "Intro to CS", "capacity": 50, "instructor_id": "ins1"})
        assert c["name"] == "CS101"
        assert c["description"] == "Intro to CS"
        assert c["capacity"] == 50
        assert c["instructor_id"] == "ins1"
        repo.create.assert_called_once()

    def test_get_classroom(self):
        from app.lms.services.classroom_service import ClassroomService
        repo = MagicMock()
        repo.get_by_id = MagicMock(return_value={"id": "c1", "name": "CS101"})
        service = ClassroomService(repo)
        result = service.get_classroom("c1")
        assert result["name"] == "CS101"

    def test_get_classroom_missing_returns_none(self):
        from app.lms.services.classroom_service import ClassroomService
        repo = MagicMock()
        repo.get_by_id = MagicMock(return_value=None)
        service = ClassroomService(repo)
        result = service.get_classroom("missing")
        assert result is None

    def test_list_classrooms(self):
        from app.lms.services.classroom_service import ClassroomService
        repo = MagicMock()
        repo.get_all = MagicMock(return_value={"items": [{"name": "A"}, {"name": "B"}], "total": 2})
        service = ClassroomService(repo)
        result = service.list_classrooms()
        assert result["total"] == 2

    def test_delete_classroom(self):
        from app.lms.services.classroom_service import ClassroomService
        repo = MagicMock()
        repo.get_by_id = MagicMock(return_value={"id": "c1"})
        repo.delete = MagicMock(return_value=True)
        service = ClassroomService(repo)
        result = service.delete_classroom("c1")
        assert result is True


class TestEnrollmentService:
    def test_enroll_student(self):
        from app.lms.services.enrollment_service import EnrollmentService
        repo = MagicMock()
        repo.get_by_learner = MagicMock(return_value=[])
        repo.create = MagicMock(return_value={"id": "e1", "learner_id": "learner1", "course_id": "course1", "status": "pending"})
        service = EnrollmentService(repo)
        e = service.create_enrollment({"learner_id": "learner1", "course_id": "course1"})
        assert e["learner_id"] == "learner1"
        assert e["course_id"] == "course1"
        assert e["status"] == "pending"

    def test_activate_enrollment(self):
        from app.lms.services.enrollment_service import EnrollmentService
        repo = MagicMock()
        repo.get_by_id = MagicMock(return_value={"id": "e1", "learner_id": "l1", "status": "pending"})
        repo.update = MagicMock(return_value={"id": "e1", "learner_id": "l1", "status": "active"})
        service = EnrollmentService(repo)
        result = service.activate_enrollment("e1")
        assert result["status"] == "active"

    def test_drop_enrollment(self):
        from app.lms.services.enrollment_service import EnrollmentService
        repo = MagicMock()
        repo.get_by_id = MagicMock(return_value={"id": "e1", "learner_id": "l1", "status": "active"})
        repo.update = MagicMock(return_value={"id": "e1", "learner_id": "l1", "status": "dropped"})
        service = EnrollmentService(repo)
        result = service.drop_enrollment("e1")
        assert result["status"] == "dropped"

    def test_list_enrollments(self):
        from app.lms.services.enrollment_service import EnrollmentService
        repo = MagicMock()
        repo.get_all = MagicMock(return_value={"items": [{"id": "e1"}], "total": 1})
        service = EnrollmentService(repo)
        result = service.list_enrollments("course1")
        assert result["total"] == 1


class TestGradebookService:
    def test_create_gradebook(self):
        from app.lms.services.gradebook_service import GradebookService
        repo = MagicMock()
        repo.get_by_course = MagicMock(return_value=None)
        repo.create = MagicMock(return_value={"id": "gb1", "course_id": "course1"})
        service = GradebookService(repo)
        gb = service.create_gradebook("course1")
        assert gb["course_id"] == "course1"

    def test_add_grade_item(self):
        from app.lms.services.gradebook_service import GradebookService
        repo = MagicMock()
        repo.get_by_id = MagicMock(return_value={"id": "gb1", "course_id": "c1"})
        item_data = {"name": "Midterm", "category": "exam", "points_possible": 100.0, "weight": 1.0}
        repo.add_grade_item = MagicMock(return_value={"id": "gi1", "name": "Midterm", "category": "exam"})
        service = GradebookService(repo)
        item = service.add_grade_item("gb1", item_data)
        assert item["name"] == "Midterm"

    def test_get_gradebook_by_course(self):
        from app.lms.services.gradebook_service import GradebookService
        repo = MagicMock()
        gb = {"id": "gb1", "course_id": "c1"}
        repo.get_by_course = MagicMock(return_value=gb)
        service = GradebookService(repo)
        result = service.get_gradebook_by_course("c1")
        assert result["course_id"] == "c1"


class TestCompetencyService:
    def test_create_competency(self):
        from app.lms.services.competency_service import CompetencyService
        repo = MagicMock()
        repo.create_competency = MagicMock(return_value={"id": "comp1", "name": "Secure Coding", "level": "advanced"})
        service = CompetencyService(repo)
        c = service.create_competency({"name": "Secure Coding", "domain": "Cybersec", "level": "advanced"})
        assert c["name"] == "Secure Coding"
        assert c["level"] == "advanced"

    def test_get_competency(self):
        from app.lms.services.competency_service import CompetencyService
        repo = MagicMock()
        repo.get_competency = MagicMock(return_value={"id": "comp1", "name": "Testing"})
        service = CompetencyService(repo)
        result = service.get_competency("comp1")
        assert result["name"] == "Testing"

    def test_list_competencies(self):
        from app.lms.services.competency_service import CompetencyService
        repo = MagicMock()
        repo.get_all_competencies = MagicMock(return_value=[{"name": "A"}, {"name": "B"}])
        service = CompetencyService(repo)
        result = service.list_competencies()
        assert len(result) == 2

    def test_delete_competency(self):
        from app.lms.services.competency_service import CompetencyService
        repo = MagicMock()
        repo.get_competency = MagicMock(return_value={"id": "c1"})
        repo.delete = MagicMock(return_value=True)
        service = CompetencyService(repo)
        assert service.delete_competency("c1") is True
