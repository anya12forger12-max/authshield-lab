"""Tests for Scenario entity and ScenarioService."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.simulation.domain.entities.scenario import Scenario, ScenarioDifficulty, ScenarioStatus, ScenarioType


class TestScenarioEntity:
    def test_default_values(self):
        s = Scenario()
        assert s.status == ScenarioStatus.DRAFT
        assert s.difficulty == ScenarioDifficulty.BEGINNER
        assert s.version == 1
        assert s.estimated_duration_minutes == 30

    def test_publish_from_draft(self):
        s = Scenario()
        s.publish()
        assert s.status == ScenarioStatus.PUBLISHED

    def test_publish_from_non_draft_raises(self):
        s = Scenario(status=ScenarioStatus.ARCHIVED)
        with pytest.raises(ValueError, match="Cannot publish"):
            s.publish()

    def test_archive_from_published(self):
        s = Scenario()
        s.publish()
        s.archive()
        assert s.status == ScenarioStatus.ARCHIVED

    def test_archive_from_draft_raises(self):
        s = Scenario()
        with pytest.raises(ValueError, match="Cannot archive"):
            s.archive()

    def test_clone_creates_draft_copy(self):
        s = Scenario(title="Original", description="Desc")
        cloned = s.clone()
        assert cloned.id != s.id
        assert cloned.status == ScenarioStatus.DRAFT
        assert cloned.version == 1
        assert cloned.title == "Original"

    def test_update_version_increments(self):
        s = Scenario()
        old = s.version
        s.update_version()
        assert s.version == old + 1

    def test_validate_returns_errors_for_missing(self):
        s = Scenario()
        errors = s.validate()
        assert "Title is required" in errors
        assert "Description is required" in errors
        assert "At least one learning objective is required" in errors
        assert "Target audience is required" in errors

    def test_validate_passes_with_valid_data(self):
        s = Scenario(
            title="Test Scenario",
            description="A test description",
            learning_objectives=["LO1"],
            target_audience="Students",
            estimated_duration_minutes=60,
        )
        errors = s.validate()
        assert errors == []

    def test_to_dict_includes_keys(self):
        s = Scenario(title="T", description="D")
        d = s.to_dict()
        assert d["title"] == "T"
        assert d["status"] == "draft"
        assert d["difficulty"] == "beginner"

    def test_custom_difficulty_and_type(self):
        s = Scenario(difficulty=ScenarioDifficulty.ADVANCED, scenario_type=ScenarioType.AUDIT_LOG_ANALYSIS)
        assert s.difficulty == ScenarioDifficulty.ADVANCED
        assert s.scenario_type == ScenarioType.AUDIT_LOG_ANALYSIS


class TestScenarioService:
    @pytest.fixture
    def repo(self):
        r = MagicMock()
        r.create = AsyncMock()
        r.get_by_id = AsyncMock()
        r.get_all = AsyncMock()
        r.update = AsyncMock()
        r.delete = AsyncMock()
        r.search = AsyncMock()
        r.get_by_status = AsyncMock()
        return r

    @pytest.fixture
    def service(self, repo):
        from app.simulation.services.scenario_service import ScenarioService
        return ScenarioService(repository=repo, event_bus=MagicMock(publish=AsyncMock()))

    @pytest.mark.asyncio
    async def test_create_scenario(self, service, repo):
        created = Scenario(id="s1", title="Test", description="Desc", target_audience="All", learning_objectives=["LO1"])
        repo.create.return_value = created
        result = await service.create_scenario("Test", "Desc", target_audience="All", learning_objectives=["LO1"])
        assert result.title == "Test"

    @pytest.mark.asyncio
    async def test_create_scenario_validation_fails(self, service, repo):
        with pytest.raises(ValueError, match="validation failed"):
            await service.create_scenario("", "")

    @pytest.mark.asyncio
    async def test_get_scenario(self, service, repo):
        repo.get_by_id.return_value = Scenario(id="s1", title="T")
        result = await service.get_scenario("s1")
        assert result.title == "T"

    @pytest.mark.asyncio
    async def test_get_nonexistent_scenario(self, service, repo):
        repo.get_by_id.return_value = None
        result = await service.get_scenario("bad")
        assert result is None

    @pytest.mark.asyncio
    async def test_publish_scenario(self, service, repo):
        s = Scenario(id="s1")
        repo.get_by_id.return_value = s
        updated = Scenario(id="s1", title=s.title)
        updated.status = ScenarioStatus.PUBLISHED
        repo.update.return_value = updated
        result = await service.publish_scenario("s1")
        assert result.status == ScenarioStatus.PUBLISHED

    @pytest.mark.asyncio
    async def test_publish_scenario_missing_raises(self, service, repo):
        repo.get_by_id.return_value = None
        with pytest.raises(ValueError, match="not found"):
            await service.publish_scenario("bad")

    @pytest.mark.asyncio
    async def test_archive_scenario(self, service, repo):
        s = Scenario(id="s1")
        s.publish()
        repo.get_by_id.return_value = s
        updated = Scenario(id="s1", title=s.title)
        updated.status = ScenarioStatus.ARCHIVED
        repo.update.return_value = updated
        result = await service.archive_scenario("s1")
        assert result.status == ScenarioStatus.ARCHIVED

    @pytest.mark.asyncio
    async def test_clone_scenario(self, service, repo):
        s = Scenario(id="s1", title="Original", description="Desc", target_audience="All", learning_objectives=["LO1"])
        repo.get_by_id.return_value = s
        cloned = s.clone()
        repo.create.return_value = cloned
        result = await service.clone_scenario("s1")
        assert result.id != s.id
        assert result.title == "Original"

    @pytest.mark.asyncio
    async def test_list_scenarios(self, service, repo):
        repo.get_all.return_value = {"items": [{"id": "s1"}], "total": 1}
        result = await service.list_scenarios()
        assert result["total"] == 1
