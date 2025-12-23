"""Tests for language registry."""
import pytest

from codex.ast.language_registry import LanguageRegistry


def test_supported_languages():
    """Test that core languages are listed."""
    langs = LanguageRegistry.list_languages()
    assert "python" in langs
    assert "yaml" in langs
    assert "json" in langs


def test_is_supported():
    """Test language support checking."""
    assert LanguageRegistry.is_supported("python")
    assert LanguageRegistry.is_supported("yaml")
    assert not LanguageRegistry.is_supported("cobol")


def test_unsupported_language():
    """Test handling of unsupported languages."""
    result = LanguageRegistry.get_language("klingon")
    assert result is None


def test_clear_cache():
    """Test cache clearing."""
    # Should not raise
    LanguageRegistry.clear_cache()
    assert LanguageRegistry._cache == {}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
