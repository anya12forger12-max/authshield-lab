"""Tests for release and LTS entities and services — Release, ReleasePackage, LtsVersion, ReleaseService, LtsService."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.production.domain.entities.release_center import Release, ReleasePackage, ReleaseStatus
from app.production.domain.entities.lts import LtsVersion, MigrationStep, CompatibilityMatrix


class TestRelease:
    def test_default_values(self):
        r = Release()
        assert r.status == ReleaseStatus.IN_DEVELOPMENT
        assert r.release_notes == []

    def test_custom_release(self):
        r = Release(version="2.0.0", name="Neptune", status=ReleaseStatus.STABLE)
        assert r.version == "2.0.0"
        assert r.name == "Neptune"
        assert r.status == ReleaseStatus.STABLE


class TestReleasePackage:
    def test_default_values(self):
        p = ReleasePackage()
        assert p.package_type == "installer"
        assert p.file_size == 0

    def test_custom_package(self):
        p = ReleasePackage(name="installer.exe", platform="windows", file_size=1024)
        assert p.name == "installer.exe"
        assert p.file_size == 1024


class TestLtsVersion:
    def test_default_values(self):
        l = LtsVersion()
        assert l.status == "active"
        assert l.compatible_versions == []

    def test_custom_lts(self):
        l = LtsVersion(version="3.0", status="extended", compatible_versions=["2.0", "2.5"])
        assert l.status == "extended"
        assert len(l.compatible_versions) == 2


class TestMigrationStep:
    def test_default_values(self):
        m = MigrationStep()
        assert m.step_number == 0
        assert m.rollback_available is True
        assert m.requires_backup is False

    def test_custom_step(self):
        m = MigrationStep(from_version="1.0", to_version="2.0", step_number=1, description="DB migration")
        assert m.from_version == "1.0"
        assert m.description == "DB migration"


class TestCompatibilityMatrix:
    def test_default_values(self):
        c = CompatibilityMatrix()
        assert c.compatible is True


class TestReleaseService:
    @pytest.fixture
    def repos(self):
        return MagicMock(), MagicMock(), MagicMock()

    @pytest.fixture
    def service(self, repos):
        from app.production.services.release_service import ReleaseService
        return ReleaseService(*repos)

    def test_create_release(self, service, repos):
        release_repo, package_repo, build_repo = repos
        release_repo.create = AsyncMock()
        import asyncio
        result = asyncio.run(service.create_release("1.0.0", "Alpha"))
        assert result.version == "1.0.0"
        assert result.name == "Alpha"

    def test_get_release(self, service, repos):
        release_repo, _, _ = repos
        r = Release(id="r1")
        release_repo.get_by_id = AsyncMock(return_value=r)
        import asyncio
        result = asyncio.run(service.get_release("r1"))
        assert result.id == "r1"

    def test_get_release_nonexistent(self, service, repos):
        release_repo, _, _ = repos
        release_repo.get_by_id = AsyncMock(return_value=None)
        import asyncio
        result = asyncio.run(service.get_release("bad"))
        assert result is None

    def test_update_release_status(self, service, repos):
        release_repo, _, _ = repos
        r = Release(id="r1", status=ReleaseStatus.IN_DEVELOPMENT)
        release_repo.get_by_id = AsyncMock(return_value=r)
        updated_release = Release(id="r1", status=ReleaseStatus.RELEASE_CANDIDATE)
        release_repo.update = AsyncMock(return_value=updated_release)
        import asyncio
        result = asyncio.run(service.update_release_status("r1", ReleaseStatus.RELEASE_CANDIDATE))
        assert result.status == ReleaseStatus.RELEASE_CANDIDATE

    def test_update_release_status_invalid(self, service, repos):
        release_repo, _, _ = repos
        r = Release(id="r1", status=ReleaseStatus.IN_DEVELOPMENT)
        release_repo.get_by_id = AsyncMock(return_value=r)
        import asyncio
        with pytest.raises(ValueError, match="Cannot transition"):
            asyncio.run(service.update_release_status("r1", ReleaseStatus.STABLE))

    def test_create_package(self, service, repos):
        _, package_repo, _ = repos
        package_repo.create = AsyncMock()
        import asyncio
        pkg = asyncio.run(service.create_package("r1", "installer.exe", "installer", "windows"))
        assert pkg.release_id == "r1"
        assert pkg.platform == "windows"


class TestLtsService:
    @pytest.fixture
    def repos(self):
        return MagicMock(), MagicMock(), MagicMock(), MagicMock()

    @pytest.fixture
    def service(self, repos):
        from app.production.services.lts_service import LtsService
        return LtsService(*repos)

    def test_create_lts_version(self, service, repos):
        lts_repo, _, _, _ = repos
        lts_repo.create = AsyncMock()
        import asyncio
        result = asyncio.run(service.create_lts_version("3.0", "2026-01-01", "2030-01-01"))
        assert result.version == "3.0"
        assert result.status == "active"

    def test_get_lts_version(self, service, repos):
        lts_repo, _, _, _ = repos
        l = LtsVersion(id="l1", version="2.0")
        lts_repo.get_by_id = AsyncMock(return_value=l)
        import asyncio
        result = asyncio.run(service.get_lts_version("l1"))
        assert result.version == "2.0"

    def test_get_lts_nonexistent(self, service, repos):
        lts_repo, _, _, _ = repos
        lts_repo.get_by_id = AsyncMock(return_value=None)
        import asyncio
        result = asyncio.run(service.get_lts_version("bad"))
        assert result is None

    def test_update_lts_status(self, service, repos):
        lts_repo, _, _, _ = repos
        l = LtsVersion(id="l1", status="active")
        lts_repo.get_by_id = AsyncMock(return_value=l)
        updated_lts = LtsVersion(id="l1", status="extended")
        lts_repo.update = AsyncMock(return_value=updated_lts)
        import asyncio
        result = asyncio.run(service.update_lts_status("l1", "extended"))
        assert result.status == "extended"

    def test_update_lts_invalid_status_raises(self, service, repos):
        lts_repo, _, _, _ = repos
        l = LtsVersion(id="l1")
        lts_repo.get_by_id = AsyncMock(return_value=l)
        import asyncio
        with pytest.raises(ValueError, match="Invalid LTS status"):
            asyncio.run(service.update_lts_status("l1", "bogus"))

    def test_add_migration_step(self, service, repos):
        _, migration_repo, _, _ = repos
        migration_repo.create = AsyncMock()
        import asyncio
        step = asyncio.run(service.add_migration_step("1.0", "2.0", 1, "Migration step"))
        assert step.from_version == "1.0"
        assert step.step_number == 1

    def test_check_compatibility(self, service, repos):
        _, _, compat_repo, _ = repos
        compat_repo.check_compatibility = AsyncMock(return_value=None)
        compat_repo.create = AsyncMock()
        import asyncio
        result = asyncio.run(service.check_compatibility("1.0", "2.0"))
        assert result.compatible is True
