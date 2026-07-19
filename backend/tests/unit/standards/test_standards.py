"""Tests for standards entities and services."""

from __future__ import annotations

from app.standards.domain.entities.framework import CompetencyFramework, FrameworkCompetency
from app.standards.domain.entities.mapping import CurriculumMapping
from app.standards.domain.entities.skills_taxonomy import SkillTaxonomy, TaxonomySkill
from app.standards.services.framework_service import FrameworkService
from app.standards.services.mapping_service import MappingService
from app.standards.services.skills_taxonomy_service import SkillsTaxonomyService


class _FakeRepo:
    def __init__(self):
        self._store: dict = {}
        self._next_id = 0

    def _gen_id(self) -> str:
        self._next_id += 1
        return f"id-{self._next_id}"

    def get_by_id(self, id: str):
        return self._store.get(id)

    def list_all(self):
        return list(self._store.values())

    def list_by_status(self, status: str):
        return [e for e in self._store.values() if getattr(e, "status", None) == status]

    def save(self, entity):
        if not getattr(entity, "id", None):
            entity.id = self._gen_id()
        self._store[entity.id] = entity
        return entity

    def delete(self, id: str) -> bool:
        if id in self._store:
            del self._store[id]
            return True
        return False


class TestCompetencyFramework:
    def test_create_framework(self):
        fw = CompetencyFramework(
            name="SecOps Framework",
            description="Security Operations",
            version="1.0",
            status="active",
        )
        assert fw.name == "SecOps Framework"
        assert fw.version == "1.0"
        assert fw.competencies == []

    def test_add_competency(self):
        fw = CompetencyFramework(name="Test", description="", version="1.0", status="active")
        comp = FrameworkCompetency(
            framework_id=fw.id,
            name="Authentication",
            description="Auth basics",
            domain_id="",
            level="beginner",
            skills=["password_hashing"],
        )
        fw.competencies.append(comp)
        assert len(fw.competencies) == 1
        assert fw.competencies[0].name == "Authentication"

    def test_to_dict(self):
        fw = CompetencyFramework(name="F", description="D", version="1.0", status="active")
        d = fw.to_dict()
        assert d["name"] == "F"
        assert "competencies" in d

    def test_update_status(self):
        fw = CompetencyFramework(name="F", description="", version="1.0", status="draft")
        fw.status = "active"
        assert fw.status == "active"


class TestCurriculumMapping:
    def test_create_mapping(self):
        m = CurriculumMapping(
            source_id="course-1",
            source_type="course",
            target_id="comp-1",
            target_type="competency",
            coverage_level="full",
            confidence=0.9,
            review_status="pending",
        )
        assert m.source_id == "course-1"
        assert m.confidence == 0.9

    def test_default_values(self):
        m = CurriculumMapping(
            source_id="s", source_type="t", target_id="t", target_type="t",
        )
        assert m.evidence == []
        assert m.related_competencies == []


class TestSkillTaxonomy:
    def test_create_taxonomy(self):
        t = SkillTaxonomy(name="Cyber Skills", description="Security skills", version="1.0")
        assert t.name == "Cyber Skills"
        assert t.skills == []

    def test_add_skill(self):
        t = SkillTaxonomy(name="T", description="", version="1.0")
        skill = TaxonomySkill(
            taxonomy_id=t.id,
            name="Python",
            description="Programming",
            category="technical",
            level="beginner",
            aliases=[],
            version=1,
        )
        t.skills.append(skill)
        assert len(t.skills) == 1


class TestFrameworkService:
    def test_create_framework(self):
        repo = _FakeRepo()
        svc = FrameworkService(repo)
        fw = svc.create_framework("Test FW", "1.0", "A test framework")
        assert fw.name == "Test FW"
        assert fw.version == "1.0"

    def test_get_framework(self):
        repo = _FakeRepo()
        svc = FrameworkService(repo)
        fw = svc.create_framework("F", "1.0", "desc")
        found = svc.get_framework(fw.id)
        assert found is not None
        assert found.name == "F"

    def test_list_frameworks(self):
        repo = _FakeRepo()
        svc = FrameworkService(repo)
        svc.create_framework("A", "1.0", "")
        svc.create_framework("B", "1.0", "")
        result = svc.list_frameworks()
        assert len(result) == 2

    def test_update_framework(self):
        repo = _FakeRepo()
        svc = FrameworkService(repo)
        fw = svc.create_framework("Old", "1.0", "")
        updated = svc.update_framework(fw.id, name="New")
        assert updated.name == "New"

    def test_delete_framework(self):
        repo = _FakeRepo()
        svc = FrameworkService(repo)
        fw = svc.create_framework("Del", "1.0", "")
        svc.delete_framework(fw.id)
        assert svc.get_framework(fw.id) is None


class _FakeMappingRepo:
    def __init__(self):
        self._store: dict = {}
        self._next_id = 0

    def _gen_id(self) -> str:
        self._next_id += 1
        return f"map-{self._next_id}"

    def get_by_id(self, id: str):
        return self._store.get(id)

    def list_all(self):
        return list(self._store.values())

    def list_by_source(self, source_id: str):
        return [e for e in self._store.values() if e.source_id == source_id]

    def list_by_target(self, target_id: str):
        return [e for e in self._store.values() if e.target_id == target_id]

    def save(self, entity):
        if not getattr(entity, "id", None):
            entity.id = self._gen_id()
        self._store[entity.id] = entity
        return entity

    def delete(self, id: str) -> bool:
        if id in self._store:
            del self._store[id]
            return True
        return False


class _FakeCoverageRepo:
    def save(self, report):
        return report

    def find_latest(self, framework_id):
        return None

    def find_all(self):
        return []


class _FakeBulkRepo:
    def __init__(self):
        self._store = []

    def save(self, result):
        self._store.append(result)
        return result

    def find_all(self):
        return list(self._store)


class TestMappingService:
    def test_create_mapping(self):
        repo = _FakeMappingRepo()
        svc = MappingService(mapping_repo=repo)
        m = svc.create_mapping("c1", "course", "comp1", "competency")
        assert m.source_id == "c1"

    def test_list_mappings(self):
        repo = _FakeMappingRepo()
        svc = MappingService(mapping_repo=repo)
        svc.create_mapping("a", "course", "b", "comp")
        assert len(svc.list_mappings()) == 1

    def test_delete_mapping(self):
        repo = _FakeMappingRepo()
        svc = MappingService(mapping_repo=repo)
        m = svc.create_mapping("s", "t", "t", "t")
        svc.delete_mapping(m.id)
        assert len(svc.list_mappings()) == 0


class _FakeTaxonomyRepo:
    def __init__(self):
        self._store: dict = {}
        self._next_id = 0

    def _gen_id(self) -> str:
        self._next_id += 1
        return f"tax-{self._next_id}"

    def get_by_id(self, id: str):
        return self._store.get(id)

    def list_all(self):
        return list(self._store.values())

    def save(self, entity):
        if not getattr(entity, "id", None):
            entity.id = self._gen_id()
        self._store[entity.id] = entity
        return entity

    def delete(self, id: str) -> bool:
        if id in self._store:
            del self._store[id]
            return True
        return False


class TestSkillsTaxonomyService:
    def test_create_taxonomy(self):
        repo = _FakeTaxonomyRepo()
        svc = SkillsTaxonomyService(taxonomy_repo=repo)
        t = svc.create_taxonomy("Sec Skills", "Description", "1.0")
        assert t.name == "Sec Skills"

    def test_get_taxonomy(self):
        repo = _FakeTaxonomyRepo()
        svc = SkillsTaxonomyService(taxonomy_repo=repo)
        t = svc.create_taxonomy("T", "", "1.0")
        found = svc.get_taxonomy(t.id)
        assert found is not None

    def test_list_taxonomies(self):
        repo = _FakeTaxonomyRepo()
        svc = SkillsTaxonomyService(taxonomy_repo=repo)
        svc.create_taxonomy("A", "", "1.0")
        assert len(svc.list_taxonomies()) == 1
