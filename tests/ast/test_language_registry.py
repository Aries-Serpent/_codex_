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
    """Test cache clearing via public API behavior."""
    # Clear any existing cache first
    LanguageRegistry.clear_cache()
    
    # Clearing an empty cache should not raise
    LanguageRegistry.clear_cache()
    
    # The cache should be functional after clearing
    # (get_language may return None if tree-sitter not installed,
    # but should not raise an exception)
    try:
        LanguageRegistry.get_language("python")
    except Exception as e:
        pytest.fail(f"get_language raised unexpected exception after clear_cache: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
