"""
Unit tests for edge cases across all modules.

Tests boundary conditions, invalid inputs, and error handling.
"""

import importlib.util
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest


class TestPathUtilsEdgeCases:
    """Test path_utils edge cases."""

    def test_windows_safe_timestamp_invalid_format(self):
        """Test windows_safe_timestamp with invalid format raises."""
        from codex.utils.path_utils import windows_safe_timestamp

        with pytest.raises(ValueError, match="Unknown format"):
            windows_safe_timestamp(fmt="invalid_format")

    def test_windows_safe_timestamp_without_seconds(self):
        """Test windows_safe_timestamp without seconds."""
        from codex.utils.path_utils import windows_safe_timestamp

        result = windows_safe_timestamp(fmt="iso", include_seconds=False)

        # Should not include seconds
        assert result.endswith("Z"), "Result must not be empty"
        assert result.count("-") >= 3, "Value must be greater than zero"

    def test_sanitize_filename_empty_string(self):
        """Test sanitize_filename with empty string."""
        from codex.utils.path_utils import sanitize_filename

        result = sanitize_filename("")

        # Should handle gracefully
        assert isinstance(result, str)

    def test_sanitize_filename_only_illegal_chars(self):
        """Test sanitize_filename with only illegal characters."""
        from codex.utils.path_utils import sanitize_filename

        result = sanitize_filename('<>:"/\\|?*')

        # All should be replaced
        assert "<" not in result, "Result must not be empty"
        assert ">" not in result, "Result must not be empty"
        assert ":" not in result, "Result must not be empty"

    def test_sanitize_filename_unicode(self):
        """Test sanitize_filename with unicode characters."""
        from codex.utils.path_utils import sanitize_filename

        result = sanitize_filename("файл_测试_テスト.txt")

        # Should preserve unicode
        assert isinstance(result, str)


class TestDALEdgeCases:
    """Test DAL edge cases."""

    def test_decode_json_field_invalid_json(self):
        """Test _decode_json_field with invalid JSON."""
        from codex.archive.dal import _decode_json_field

        result = _decode_json_field("{invalid json}")

        # Should return empty dict
        assert result == {}, "Result must not be empty"

    def test_decode_json_field_non_dict_json(self):
        """Test _decode_json_field with non-dict JSON."""
        from codex.archive.dal import _decode_json_field

        result = _decode_json_field('["array", "not", "dict"]')

        # Should return empty dict
        assert result == {}, "Result must not be empty"

    def test_decode_json_field_bytes(self):
        """Test _decode_json_field with bytes."""
        from codex.archive.dal import _decode_json_field

        result = _decode_json_field(b'{"key": "value"}')

        # Should decode and parse
        assert result == {"key": "value"}, "Result must not be empty"

    def test_decode_json_field_none(self):
        """Test _decode_json_field with None."""
        from codex.archive.dal import _decode_json_field

        result = _decode_json_field(None)

        # Should return empty dict
        assert result == {}, "Result must not be empty"


class TestTrainingEdgeCases:
    """Test training loop edge cases."""

    def test_train_one_step_zero_loss(self):
        """Test train_one_step with zero loss."""
        from codex_ml.training.loop import train_one_step

        result = train_one_step(0.0)

        # Should still apply decay
        assert result == 0.0, "Result must not be empty"

    def test_train_one_step_negative_loss(self):
        """Test train_one_step with negative loss."""
        from codex_ml.training.loop import train_one_step

        result = train_one_step(-10.0)

        # Should handle negative values
        assert result < 0, "Result must not be empty"

    def test_train_epoch_single_batch(self):
        """Test train_epoch with single batch."""
        from codex_ml.training.loop import train_epoch

        model = Mock()
        model.step.return_value = {"loss": 1.5}
        dataloader = [{"input_ids": [1, 2, 3]}]

        result = train_epoch(model, dataloader, {})

        assert result["num_batches"] == 1, "Result must not be empty"
        assert result["loss_mean"] == 1.5, "Result must not be empty"

    def test_run_minimal_training_max_steps_zero(self):
        """Test run_minimal_training with max_steps=0."""
        from codex_ml.training.loop import run_minimal_training

        with tempfile.TemporaryDirectory() as tmpdir:
            result = run_minimal_training({}, max_steps=0, run_dir=tmpdir)

            # Should execute at least 1 step (max(1, 0))
            assert "loss_final" in result, "Result must not be empty"


class TestCheckpointEdgeCases:
    """Test checkpoint edge cases."""

    def test_ensure_dir_existing_directory(self):
        """Test _ensure_dir with existing directory."""
        from codex_ml.checkpointing.checkpoint_core import _ensure_dir

        with tempfile.TemporaryDirectory() as tmpdir:
            # Should not raise when directory exists
            _ensure_dir(tmpdir)
            _ensure_dir(tmpdir)  # Call again

            assert Path(tmpdir).exists(), "Condition must be true"

    def test_load_checkpoint_nonexistent_path(self):
        """Test load_checkpoint with nonexistent path."""
        from codex_ml.checkpointing.checkpoint_core import load_checkpoint

        if not _torch_available():
            pytest.skip("PyTorch required")

        with pytest.raises((FileNotFoundError, RuntimeError)):
            load_checkpoint("/nonexistent/checkpoint/path")


class TestDistributedEdgeCases:
    """Test distributed training edge cases."""

    @patch.dict("os.environ", {"TEST_FLAG": ""}, clear=False)
    def test_parse_env_int_empty_string(self):
        """Test _parse_env_int with empty string."""
        from codex_ml.distributed.minimal import _parse_env_int

        with pytest.warns(RuntimeWarning):
            result = _parse_env_int("TEST_FLAG")
            assert result is None, "Result must not be empty"

    @patch.dict("os.environ", {"TEST_FLAG": "abc123"}, clear=False)
    def test_parse_env_int_mixed_string(self):
        """Test _parse_env_int with mixed alphanumeric."""
        from codex_ml.distributed.minimal import _parse_env_int

        with pytest.warns(RuntimeWarning):
            result = _parse_env_int("TEST_FLAG")
            assert result is None, "Result must not be empty"

    @patch.dict("os.environ", {"TEST_FLAG": "99999999999"}, clear=False)
    def test_parse_env_int_large_number(self):
        """Test _parse_env_int with very large number."""
        from codex_ml.distributed.minimal import _parse_env_int

        result = _parse_env_int("TEST_FLAG")

        assert result == 99999999999, "Result must not be empty"


class TestRAGIndexingEdgeCases:
    """Test RAG indexing edge cases."""

    def test_chunk_text_single_char(self):
        """Test chunk_text with single character."""
        try:
            from codex.rag.indexer import chunk_text

            chunks = chunk_text("A", chunk_size=100, overlap=10)

            assert len(chunks) == 1, "Chunks must not be empty"
            assert chunks[0][2] == "A", "Condition must be true"
        except ImportError:
            pytest.skip("RAG indexer not available")

    def test_chunk_text_exact_chunk_size(self):
        """Test chunk_text with text exactly chunk_size."""
        try:
            from codex.rag.indexer import chunk_text

            text = "A" * 100
            chunks = chunk_text(text, chunk_size=100, overlap=0)

            assert len(chunks) >= 1, "Chunks must not be empty"
        except ImportError:
            pytest.skip("RAG indexer not available")

    def test_chunk_text_zero_overlap(self):
        """Test chunk_text with zero overlap."""
        try:
            from codex.rag.indexer import chunk_text

            text = "A" * 200
            chunks = chunk_text(text, chunk_size=100, overlap=0)

            # Should create non-overlapping chunks
            assert len(chunks) >= 2, "Chunks must not be empty"
        except ImportError:
            pytest.skip("RAG indexer not available")


class TestConfigEdgeCases:
    """Test config loader edge cases."""

    def test_environment_manager_missing_key(self):
        """Test EnvironmentManager with missing environment variable."""
        try:
            from codex.config.config_loader import EnvironmentManager

            manager = EnvironmentManager()

            # Should handle missing keys gracefully
            result = manager.get("NONEXISTENT_VAR", default="fallback")
            assert result == "fallback", "Result must not be empty"
        except (ImportError, AttributeError):
            pytest.skip("EnvironmentManager not available")


# Helper
def _torch_available():
    """Check if PyTorch is available."""
    return importlib.util.find_spec("torch") is not None
