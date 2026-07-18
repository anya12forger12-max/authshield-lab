"""Tests for LocalizationManager: set_language, t(), fallback."""

import pytest

from app.shared.localization.manager import LocalizationManager


@pytest.fixture
def localization():
    return LocalizationManager()


@pytest.fixture
def te_localization():
    loc = LocalizationManager()
    loc.set_language("te")
    return loc


class TestSetLanguage:
    def test_default_language(self, localization):
        assert localization.get_language() == "en"

    def test_set_language(self, localization):
        localization.set_language("te")
        assert localization.get_language() == "te"

    def test_set_invalid_language(self, localization):
        with pytest.raises(KeyError, match="not available"):
            localization.set_language("xyz")

    def test_available_languages(self, localization):
        langs = localization.get_available_languages()
        assert "en" in langs
        assert "te" in langs
        assert "hi" in langs


class TestTranslate:
    def test_translate_existing_key(self, localization):
        result = localization.t("auth.login.success")
        assert result == "Login successful"

    def test_translate_missing_key_returns_key(self, localization):
        result = localization.t("nonexistent.key")
        assert result == "nonexistent.key"

    def test_translate_with_kwargs(self, localization):
        result = localization.t(
            "validation.username.length", min=4, max=32
        )
        assert "4" in result
        assert "32" in result

    def test_translate_wrong_kwargs_returns_raw_string(self, localization):
        result = localization.t(
            "validation.username.length", wrong="param"
        )
        assert isinstance(result, str)
        assert len(result) > 0


class TestFallback:
    def test_fallback_to_english(self, te_localization):
        te_localization.set_language("te")
        te_localization._strings["te"].pop("test.fallback.key", None)
        te_localization._strings.setdefault("en", {})["test.fallback.key"] = "Fallback value"
        result = te_localization.t("test.fallback.key")
        assert result == "Fallback value"
        te_localization._strings["en"].pop("test.fallback.key", None)

    def test_telugu_key_available(self, te_localization):
        te_localization.set_language("te")
        result = te_localization.t("auth.login.success")
        assert result == "లాగిన్ విజయవంతమైంది"

    def test_hindi_key_available(self, localization):
        localization.set_language("hi")
        result = localization.t("auth.login.success")
        assert result == "लॉगिन सफल"

    def test_missing_in_all_returns_key(self, localization):
        result = localization.t("totally.missing.key")
        assert result == "totally.missing.key"


class TestHasTranslation:
    def test_exists_for_current_language(self, localization):
        assert localization.has_translation("auth.login.success") is True

    def test_not_exists(self, localization):
        assert localization.has_translation("nonexistent") is False

    def test_exists_for_specific_language(self, localization):
        assert localization.has_translation("auth.login.success", language="hi") is True

    def test_not_exists_for_specific_language(self, localization):
        result = localization.has_translation("nonexistent.dummy.key", language="te")
        assert result is False


class TestGetMissingKeys:
    def test_en_has_no_missing_keys(self, localization):
        missing = localization.get_missing_keys("en")
        assert len(missing) == 0

    def test_other_lang_has_missing_keys(self, localization):
        missing = localization.get_missing_keys("te")
        assert isinstance(missing, list)
