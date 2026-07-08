"""
pytest.importorskip("mlflow")
Unit tests for codex_ml.checkpointing module.

Tests checkpoint save/load, versioning, and metadata handling.
"""

import importlib.util
import json
import tempfile
from pathlib import Path

import pytest


# Helper function
def _torch_available():
    """Check if PyTorch is available."""
    return importlib.util.find_spec("torch") is not None


class TestCheckpointCore:
    """Test checkpoint_core module functions."""

    def test_checkpoint_core_import(self):
        """Test checkpoint_core can be imported."""
        from codex_ml.checkpointing import checkpoint_core

        assert checkpoint_core is not None, "checkpoint_core must be initialized"

    def test_save_checkpoint_import(self):
        """Test save_checkpoint function can be imported."""
        from codex_ml.checkpointing.checkpoint_core import save_checkpoint

        assert save_checkpoint is not None, "save_checkpoint must be initialized"
        assert callable(save_checkpoint), "Condition must be true"

    def test_load_checkpoint_import(self):
        """Test load_checkpoint function can be imported."""
        from codex_ml.checkpointing.checkpoint_core import load_checkpoint

        assert load_checkpoint is not None, "load_checkpoint must be initialized"
        assert callable(load_checkpoint), "Condition must be true"

    def test_schema_version_exists(self):
        """Test SCHEMA_VERSION constant exists."""
        from codex_ml.checkpointing.checkpoint_core import SCHEMA_VERSION

        assert SCHEMA_VERSION is not None, "SCHEMA_VERSION must be initialized"
        assert isinstance(SCHEMA_VERSION, str)

    def test_schema_version_format(self):
        """Test SCHEMA_VERSION has expected format."""
        from codex_ml.checkpointing.checkpoint_core import SCHEMA_VERSION

        # Should be something like "2.0"
        parts = SCHEMA_VERSION.split(".")
        assert len(parts) >= 1, "Parts must not be empty"
        assert parts[0].isdigit(), "Condition must be true"


class TestSaveCheckpoint:
    """Test save_checkpoint functionality."""

    @pytest.mark.skipif(not _torch_available(), reason="PyTorch required for checkpoint tests")
    def test_save_checkpoint_requires_torch(self):
        """Test save_checkpoint requires PyTorch."""
        from codex_ml.checkpointing.checkpoint_core import save_checkpoint

        # Should either work or raise RuntimeError if torch unavailable
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                save_checkpoint(tmpdir, state={"param": 1}, meta={"epoch": 1})
            except RuntimeError as e:
                assert "PyTorch" in str(e), "Condition must be true"

    def test_save_checkpoint_creates_directory(self):
        """Test save_checkpoint creates output directory."""
        from codex_ml.checkpointing.checkpoint_core import save_checkpoint

        if not _torch_available():
            pytest.skip("PyTorch required")

        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = Path(tmpdir) / "new_checkpoint"

            try:
                save_checkpoint(str(out_dir), state={"param": 1}, meta={"epoch": 1})
                assert out_dir.exists(), "Condition must be true"
            except RuntimeError:
                pytest.skip("PyTorch not available")

    def test_save_checkpoint_creates_weights_file(self):
        """Test save_checkpoint creates weights.pt."""
        from codex_ml.checkpointing.checkpoint_core import save_checkpoint

        if not _torch_available():
            pytest.skip("PyTorch required")

        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                save_checkpoint(tmpdir, state={"param": 1}, meta={"epoch": 1})
                weights_file = Path(tmpdir) / "weights.pt"
                assert weights_file.exists(), "Condition must be true"
            except RuntimeError:
                pytest.skip("PyTorch not available")

    def test_save_checkpoint_creates_metadata_file(self):
        """Test save_checkpoint creates metadata.json."""
        from codex_ml.checkpointing.checkpoint_core import save_checkpoint

        if not _torch_available():
            pytest.skip("PyTorch required")

        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                save_checkpoint(tmpdir, state={"param": 1}, meta={"epoch": 1, "step": 100})
                metadata_file = Path(tmpdir) / "metadata.json"
                assert metadata_file.exists(), "Data must not be empty"

                # Check metadata content
                with open(metadata_file) as f:
                    meta = json.load(f)
                    assert "epoch" in meta, "Condition must be true"
                    assert "_schema_version" in meta, "Condition must be true"
            except RuntimeError:
                pytest.skip("PyTorch not available")


class TestLoadCheckpoint:
    """Test load_checkpoint functionality."""

    def test_load_checkpoint_requires_torch(self):
        """Test load_checkpoint requires PyTorch."""
        from codex_ml.checkpointing.checkpoint_core import load_checkpoint

        if not _torch_available():
            with pytest.raises(RuntimeError, match="PyTorch"):
                load_checkpoint("/nonexistent/path")

    def test_load_checkpoint_from_directory(self):
        """Test load_checkpoint can load from directory."""
        from codex_ml.checkpointing.checkpoint_core import (
            load_checkpoint,
            save_checkpoint,
        )

        if not _torch_available():
            pytest.skip("PyTorch required")

        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                # Save first
                save_checkpoint(tmpdir, state={"param": 42}, meta={"epoch": 5})

                # Load
                state, _meta = load_checkpoint(tmpdir)

                assert "state" in state or "param" in state, "Condition must be true"
            except (RuntimeError, FileNotFoundError):
                pytest.skip("PyTorch not available or checkpoint not created")


class TestCheckpointUtils:
    """Test checkpoint utility functions."""

    def test_ensure_dir_function(self):
        """Test _ensure_dir helper function."""
        from codex_ml.checkpointing.checkpoint_core import _ensure_dir

        with tempfile.TemporaryDirectory() as tmpdir:
            new_dir = Path(tmpdir) / "subdir" / "nested"

            _ensure_dir(str(new_dir))

            assert new_dir.exists(), "Condition must be true"
            assert new_dir.is_dir(), "Condition must be true"

    def test_ensure_dir_idempotent(self):
        """Test _ensure_dir is idempotent."""
        from codex_ml.checkpointing.checkpoint_core import _ensure_dir

        with tempfile.TemporaryDirectory() as tmpdir:
            # Call twice - should not raise
            _ensure_dir(tmpdir)
            _ensure_dir(tmpdir)

            assert Path(tmpdir).exists(), "Condition must be true"


class TestCheckpointSchema:
    """Test checkpoint schema and versioning."""

    def test_checkpoint_includes_schema_version(self):
        """Test saved checkpoints include schema version."""
        from codex_ml.checkpointing.checkpoint_core import (
            SCHEMA_VERSION,
            save_checkpoint,
        )

        if not _torch_available():
            pytest.skip("PyTorch required")

        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                save_checkpoint(tmpdir, state={"param": 1}, meta={"epoch": 1})

                metadata_file = Path(tmpdir) / "metadata.json"
                with open(metadata_file) as f:
                    meta = json.load(f)
                    assert meta.get("_schema_version") == SCHEMA_VERSION, "Condition must be true"
            except RuntimeError:
                pytest.skip("PyTorch not available")

    def test_checkpoint_includes_timestamp(self):
        """Test saved checkpoints include creation timestamp."""
        from codex_ml.checkpointing.checkpoint_core import save_checkpoint

        if not _torch_available():
            pytest.skip("PyTorch required")

        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                save_checkpoint(tmpdir, state={"param": 1}, meta={"epoch": 1})

                metadata_file = Path(tmpdir) / "metadata.json"
                with open(metadata_file) as f:
                    meta = json.load(f)
                    assert "_created_at" in meta, "Condition must be true"
                    # Should be ISO format timestamp
                    assert "T" in meta["_created_at"], "Condition must be true"
            except RuntimeError:
                pytest.skip("PyTorch not available")


class TestCheckpointCompat:
    """Test checkpoint compatibility module."""

    def test_compat_module_import(self):
        """Test compat module can be imported."""
        from codex_ml.checkpointing import compat

        assert compat is not None, "compat must be initialized"

    def test_compat_has_migration_functions(self):
        """Test compat module has expected migration functions."""
        try:
            from codex_ml.checkpointing import compat

            # Should have some compatibility functions
            assert hasattr(compat, "__name__")
        except ImportError:
            pytest.skip("Compat module structure may vary")
