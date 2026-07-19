"""Tests for developer entities and services — Extension, SdK, PluginManifest, ExtensionService."""

from __future__ import annotations

from app.developer.domain.entities.extension import Extension, ExtensionStatus, ExtensionType, InstalledExtension
from app.developer.domain.entities.sdk import PluginManifest, SdK, SdKVersion
from app.developer.services.extension_service import ExtensionService


class TestExtension:
    def test_default_values(self):
        e = Extension()
        assert e.status == ExtensionStatus.UNINSTALLED
        assert e.compatibility == ">=1.0"
        assert len(e.permissions) == 0

    def test_install(self):
        e = Extension()
        e.install()
        assert e.status == ExtensionStatus.INSTALLED
        assert e.installed_at is not None

    def test_uninstall(self):
        e = Extension()
        e.install()
        e.uninstall()
        assert e.status == ExtensionStatus.UNINSTALLED
        assert e.installed_at is None

    def test_disable_and_enable(self):
        e = Extension()
        e.install()
        e.disable()
        assert e.status == ExtensionStatus.DISABLED
        e.enable()
        assert e.status == ExtensionStatus.INSTALLED

    def test_has_permission(self):
        e = Extension(permissions=["read", "write"])
        assert e.has_permission("read") is True
        assert e.has_permission("admin") is False

    def test_depends_on(self):
        e = Extension(dependencies=["ext-1", "ext-2"])
        assert e.depends_on("ext-1") is True
        assert e.depends_on("ext-3") is False

    def test_to_dict(self):
        e = Extension(name="Test", author="Me")
        d = e.to_dict()
        assert d["name"] == "Test"
        assert d["status"] == "uninstalled"


class TestSdK:
    def test_default_version(self):
        s = SdK()
        assert s.version == SdKVersion.V1

    def test_is_compatible(self):
        s = SdK(min_platform_version="2.0")
        assert s.is_compatible_with("3.0") is True
        assert s.is_compatible_with("1.0") is False

    def test_add_module(self):
        s = SdK()
        s.add_module("auth")
        assert "auth" in s.modules

    def test_deprecate(self):
        s = SdK()
        s.deprecate()
        assert s.deprecated is True


class TestPluginManifest:
    def test_defaults(self):
        m = PluginManifest()
        assert m.license == "MIT"
        assert m.compatibility == ">=1.0"

    def test_has_permission(self):
        m = PluginManifest(permissions=["network"])
        assert m.has_permission("network") is True
        assert m.has_permission("files") is False

    def test_requires_dependency(self):
        m = PluginManifest(dependencies=["dep-a"])
        assert m.requires_dependency("dep-a") is True

    def test_compute_checksum(self):
        m = PluginManifest()
        checksum = m.compute_checksum(b"hello")
        assert len(checksum) == 64
        assert m.checksum == checksum


class TestExtensionService:
    def test_register_extension(self):
        service = ExtensionService()
        ext = service.register_extension("Test", "1.0", "Author", "Desc")
        assert ext.name == "Test"
        assert ext.author == "Author"

    def test_get_extension(self):
        service = ExtensionService()
        ext = service.register_extension("Test")
        result = service.get_extension(ext.id)
        assert result is not None
        assert result.name == "Test"

    def test_list_extensions(self):
        service = ExtensionService()
        service.register_extension("A")
        service.register_extension("B")
        assert len(service.list_extensions()) == 2

    def test_install_extension(self):
        service = ExtensionService()
        ext = service.register_extension("Test")
        result = service.install_extension(ext.id, "user1")
        assert result is not None
        assert result.extension_id == ext.id
        assert ext.status == ExtensionStatus.INSTALLED

    def test_install_extension_nonexistent(self):
        service = ExtensionService()
        result = service.install_extension("nonexistent")
        assert result is None

    def test_install_already_installed_returns_none(self):
        service = ExtensionService()
        ext = service.register_extension("Test")
        service.install_extension(ext.id)
        result = service.install_extension(ext.id)
        assert result is None

    def test_uninstall_extension(self):
        service = ExtensionService()
        ext = service.register_extension("Test")
        service.install_extension(ext.id)
        assert service.uninstall_extension(ext.id) is True
        assert ext.status == ExtensionStatus.UNINSTALLED

    def test_uninstall_nonexistent(self):
        service = ExtensionService()
        assert service.uninstall_extension("bad") is False

    def test_search_extensions(self):
        service = ExtensionService()
        service.register_extension("Alpha")
        service.register_extension("Beta")
        results = service.search_extensions("Alpha")
        assert len(results) == 1
        assert results[0].name == "Alpha"

    def test_validate_extension(self):
        service = ExtensionService()
        ext = service.register_extension("Test", "1.0", "Author")
        result = service.validate_extension(ext.id)
        assert result["valid"] is True

    def test_validate_extension_fails_for_missing_name(self):
        service = ExtensionService()
        ext = Extension(name="", author="A")
        service._extensions[ext.id] = ext
        result = service.validate_extension(ext.id)
        assert result["valid"] is False
