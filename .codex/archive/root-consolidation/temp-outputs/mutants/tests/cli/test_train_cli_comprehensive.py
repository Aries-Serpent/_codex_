"""Comprehensive tests for src/codex_ml/cli/train.py module.

Tests cover:
- Configuration handling and conversion
- Path utilities
- Sequence coercion functions
- Training pipeline integration
"""

from pathlib import Path
from unittest.mock import patch

import pytest


class TestPathConversion:
    """Tests for _to_path() function."""

    def test_to_path_with_none(self):
        """Test _to_path returns None for None input."""
        from codex_ml.cli.train import _to_path

        assert _to_path(None) is None, "Condition must be true"

    def test_to_path_with_string(self):
        """Test _to_path converts string to Path."""
        with patch("codex_ml.cli.train.to_absolute_path", return_value="/abs/path"):
            from codex_ml.cli.train import _to_path

            result = _to_path("relative/path")
            assert isinstance(result, Path)
            assert str(result) == "/abs/path", "Result must not be empty"

    def test_to_path_with_path_object(self):
        """Test _to_path handles Path objects."""
        with patch("codex_ml.cli.train.to_absolute_path", return_value="/abs/path"):
            from codex_ml.cli.train import _to_path

            result = _to_path(Path("relative/path"))
            assert isinstance(result, Path)


class TestConfigConversion:
    """Tests for configuration conversion functions."""

    def test_cfg_to_dict_with_regular_dict(self):
        """Test _cfg_to_dict with regular dict."""
        from codex_ml.cli.train import _cfg_to_dict

        input_dict = {"key": "value", "nested": {"inner": 1}}
        result = _cfg_to_dict(input_dict)
        assert result == input_dict, "Result must not be empty"
        assert isinstance(result, dict)

    def test_cfg_to_dict_with_none(self):
        """Test _cfg_to_dict with None returns empty dict."""
        from codex_ml.cli.train import _cfg_to_dict

        result = _cfg_to_dict(None)
        assert result == {}, "Result must not be empty"

    def test_cfg_to_dict_with_omegaconf(self):
        """Test _cfg_to_dict with OmegaConf DictConfig."""
        try:
            from omegaconf import OmegaConf

            cfg = OmegaConf.create({"model": "gpt2", "epochs": 10})
            from codex_ml.cli.train import _cfg_to_dict

            result = _cfg_to_dict(cfg)
            assert isinstance(result, dict)
            assert result.get("model") == "gpt2", "Result must not be empty"
        except ImportError:
            pytest.skip("OmegaConf not available")

    def test_cfg_to_list_with_regular_list(self):
        """Test _cfg_to_list with regular list."""
        from codex_ml.cli.train import _cfg_to_list

        input_list = [1, 2, 3]
        result = _cfg_to_list(input_list)
        assert result == input_list, "Result must not be empty"
        assert isinstance(result, list)

    def test_cfg_to_list_with_none(self):
        """Test _cfg_to_list with None returns empty list."""
        from codex_ml.cli.train import _cfg_to_list

        result = _cfg_to_list(None)
        assert result == [], "Result must not be empty"

    def test_cfg_to_list_with_single_value(self):
        """Test _cfg_to_list with single value wraps in list."""
        from codex_ml.cli.train import _cfg_to_list

        result = _cfg_to_list("single_value")
        assert result == ["single_value"], "Result must not be empty"


class TestSequenceCoercion:
    """Tests for _coerce_sequence function."""

    def test_coerce_sequence_with_none(self):
        """Test _coerce_sequence returns None for None."""
        from codex_ml.cli.train import _coerce_sequence

        assert _coerce_sequence(None) is None, "Condition must be true"

    def test_coerce_sequence_with_list(self):
        """Test _coerce_sequence preserves list."""
        from codex_ml.cli.train import _coerce_sequence

        result = _coerce_sequence([1, 2, 3])
        assert result == [1, 2, 3]

    def test_coerce_sequence_with_tuple(self):
        """Test _coerce_sequence converts tuple to list."""
        from codex_ml.cli.train import _coerce_sequence

        result = _coerce_sequence((1, 2, 3))
        assert result == [1, 2, 3]
        assert isinstance(result, list)

    def test_coerce_sequence_with_set(self):
        """Test _coerce_sequence converts set to list."""
        from codex_ml.cli.train import _coerce_sequence

        result = _coerce_sequence({1, 2, 3})
        assert isinstance(result, list)
        assert set(result) == {1, 2, 3}

    def test_coerce_sequence_with_string(self):
        """Test _coerce_sequence wraps string in list."""
        from codex_ml.cli.train import _coerce_sequence

        result = _coerce_sequence("hello")
        assert result == ["hello"], "Result must not be empty"

    def test_coerce_sequence_with_invalid_type(self):
        """Test _coerce_sequence returns None for invalid types."""
        from codex_ml.cli.train import _coerce_sequence

        result = _coerce_sequence(123)
        assert result is None, "Result must not be empty"


class TestSanitizePromptSequence:
    """Tests for _sanitize_prompt_sequence function."""

    def test_sanitize_prompt_sequence_basic(self):
        """Test _sanitize_prompt_sequence with basic strings."""
        from codex_ml.cli.train import _sanitize_prompt_sequence

        result, _changed = _sanitize_prompt_sequence(["hello", "world"])
        assert isinstance(result, list)
        assert len(result) == 2, "Result must not be empty"

    def test_sanitize_prompt_sequence_empty(self):
        """Test _sanitize_prompt_sequence with empty list."""
        from codex_ml.cli.train import _sanitize_prompt_sequence

        result, changed = _sanitize_prompt_sequence([])
        assert result == [], "Result must not be empty"
        assert changed is False, "changed is not valid"

    def test_sanitize_prompt_sequence_mixed_types(self):
        """Test _sanitize_prompt_sequence with mixed types."""
        from codex_ml.cli.train import _sanitize_prompt_sequence

        result, _changed = _sanitize_prompt_sequence(["text", 123, {"key": "value"}])
        assert isinstance(result, list)
        assert len(result) == 3, "Result must not be empty"


class TestTrainCLIIntegration:
    """Integration tests for train CLI module."""

    def test_module_imports(self):
        """Test that module can be imported."""
        from codex_ml.cli import train

        assert hasattr(train, "_to_path")
        assert hasattr(train, "_cfg_to_dict")
        assert hasattr(train, "_cfg_to_list")
        assert hasattr(train, "_coerce_sequence")
        assert hasattr(train, "_sanitize_prompt_sequence")

    def test_logger_configured(self):
        """Test that logger is properly configured."""
        from codex_ml.cli import train

        assert hasattr(train, "LOGGER")

    def test_hydra_import_fallback(self):
        """Test that module handles hydra import errors gracefully."""
        # Module should be importable even if hydra is missing
        try:
            import importlib

            importlib.reload(__import__("codex_ml.cli.train"))
        except (ValueError, TypeError) as e:
            # Only fail if it's not an expected import error
            if "hydra" not in str(e).lower():
                pytest.fail(f"Unexpected import error: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
