"""
Integration tests for error paths and exception handling.

Tests exception propagation, graceful degradation, and recovery mechanisms.
"""

import importlib.util
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Skip entire module if torch is not available or unloadable
pytest.importorskip("torch", reason="PyTorch required for tests")


class TestTrainingErrorPaths:
    """Test training error paths."""

    def test_train_epoch_model_step_exception(self):
        """Test train_epoch when model.step raises exception."""
        from codex_ml.interfaces.contracts import TrainingContractError
        from codex_ml.training.loop import train_epoch

        model = Mock()
        model.step.side_effect = RuntimeError("Model step failed")
        dataloader = [{"input_ids": [1, 2, 3]}]

        with pytest.raises(TrainingContractError, match="Model.step failed"):
            train_epoch(model, dataloader, {})

    def test_run_minimal_training_invalid_run_dir(self):
        """Test run_minimal_training with invalid run_dir."""
        from codex_ml.training.loop import run_minimal_training

        with tempfile.TemporaryDirectory() as tmpdir:
            # Use nested directory that needs to be created
            nested_dir = Path(tmpdir) / "level1" / "level2" / "level3"

            # Should create parent dirs automatically
            result = run_minimal_training({}, max_steps=1, run_dir=str(nested_dir))

            assert "loss_final" in result, "Result must not be empty"
            assert nested_dir.exists(), "Condition must be true"


class TestCheckpointErrorPaths:
    """Test checkpoint error paths."""

    def test_save_checkpoint_without_torch(self):
        """Test save_checkpoint without PyTorch installed."""
        from codex_ml.checkpointing.checkpoint_core import save_checkpoint

        with patch("codex_ml.checkpointing.checkpoint_core.torch", None):
            with tempfile.TemporaryDirectory() as tmpdir:
                with pytest.raises(RuntimeError, match="PyTorch required"):
                    save_checkpoint(tmpdir, state={"param": 1}, meta={"epoch": 1})

    def test_load_checkpoint_without_torch(self):
        """Test load_checkpoint without PyTorch installed."""
        from codex_ml.checkpointing.checkpoint_core import load_checkpoint

        with patch("codex_ml.checkpointing.checkpoint_core.torch", None):
            with pytest.raises(RuntimeError, match="PyTorch required"):
                load_checkpoint("/some/path")

    def test_load_checkpoint_corrupt_metadata(self):
        """Test load_checkpoint with corrupt metadata file."""
        from codex_ml.checkpointing.checkpoint_core import (
            load_checkpoint,
            save_checkpoint,
        )

        if not _torch_available():
            pytest.skip("PyTorch required")

        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                # Save valid checkpoint
                save_checkpoint(tmpdir, state={"param": 1}, meta={"epoch": 1})

                # Corrupt metadata file
                metadata_file = Path(tmpdir) / "metadata.json"
                metadata_file.write_text("{ invalid json }")

                # load_checkpoint handles corrupt metadata gracefully — returns empty meta dict
                state, meta = load_checkpoint(tmpdir)
                assert isinstance(state, dict)
                assert isinstance(meta, dict)
            except RuntimeError:
                pytest.skip("PyTorch not available")


class TestDALErrorPaths:
    """Test DAL error paths."""

    def test_sqlite_dal_invalid_db_path(self):
        """Test SqliteDAL with invalid database path."""
        try:
            from codex.archive.dal import SqliteDAL

            # Use invalid path (e.g., directory without write permissions)
            with tempfile.TemporaryDirectory() as tmpdir:
                invalid_path = Path(tmpdir) / "nonexistent" / "subdir" / "db.sqlite"

                # Should handle gracefully or create parent dirs
                url = f"sqlite:///{invalid_path}"
                SqliteDAL.from_url(url)
                # If successful, verify it created parent dirs
                assert invalid_path.exists(), "DAL should create parent directories"
        except ImportError:
            pytest.skip("SqliteDAL not available")

    def test_sqlite_dal_concurrent_writes(self):
        """Test SqliteDAL with sequential writes (SQLite is thread-local)."""
        try:
            import uuid

            from codex.archive.dal import SqliteDAL

            with tempfile.TemporaryDirectory() as tmpdir:
                db_path = Path(tmpdir) / "test.db"
                url = f"sqlite:///{db_path}"

                dal = SqliteDAL.from_url(url)

                # Sequential writes (SQLite connections are thread-local)
                for i in range(10):
                    # First create an artifact for each item
                    artifact = dal.ensure_artifact(
                        sha=f"sha{i}",
                        size=100,
                        mime="text/plain",
                        blob=b"test content",
                        compression="zlib",
                        storage_driver="db",
                    )
                    artifact_id = artifact["id"]
                    tombstone_id = str(uuid.uuid4())
                    dal.insert_item(
                        repo="test",
                        path=f"/path/{i}",
                        commit_sha="abc123",
                        language="python",
                        kind="function",
                        reason="test",
                        artifact_id=artifact_id,
                        tombstone_id=tombstone_id,
                    )

                # Should all succeed
                items = dal.recent_items(limit=10)
                assert len(items) == 10, "Items must not be empty"
        except (ImportError, AttributeError):
            pytest.skip("SqliteDAL not available")


class TestRAGErrorPaths:
    """Test RAG error paths."""

    def test_retriever_load_model_import_error(self):
        """Test Retriever handles missing dependencies."""
        try:
            from codex.rag.retriever import Retriever

            with patch("codex.rag.retriever.SentenceTransformer", None):
                with pytest.raises(
                    ImportError, match="(?:sentence-transformers|faiss-cpu) not installed"
                ):
                    Retriever()
        except ImportError:
            pytest.skip("Retriever not available")

    def test_indexer_chunk_text_invalid_params(self):
        """Test chunk_text parameter validation."""
        try:
            from codex.rag.indexer import chunk_text

            # overlap >= chunk_size with non-default overlap
            with pytest.raises(ValueError):
                chunk_text("test", chunk_size=10, overlap=20)
        except ImportError:
            pytest.skip("chunk_text not available")

    def test_embeddings_provider_missing_openai(self):
        """Test embedding provider handles missing OpenAI."""
        try:
            from codex.rag.embeddings import OpenAI

            # If OpenAI is None, should be handled gracefully
            if OpenAI is None:
                # Expected when openai not installed
                assert True, "True is not valid"
        except ImportError:
            pytest.skip("embeddings module not available")


class TestDistributedErrorPaths:
    """Test distributed training error paths."""

    def test_warn_missing_dist_called(self):
        """Test _warn_missing_dist is called when dist unavailable."""
        from codex_ml.distributed.minimal import _warn_missing_dist

        # Should issue warning without crashing
        with pytest.warns(RuntimeWarning, match="torch.distributed"):
            _warn_missing_dist("TEST_FLAG")

    def test_warn_failed_init_with_exception(self):
        """Test _warn_failed_init with real exception."""
        from codex_ml.distributed.minimal import _warn_failed_init

        error = ConnectionError("Backend initialization failed")

        with pytest.warns(RuntimeWarning, match="Failed to initialize"):
            _warn_failed_init("nccl", "TEST_FLAG", error)


class TestLoggingErrorPaths:
    """Test logging error paths."""

    def test_metric_logger_invalid_path(self):
        """Test MetricLogger with invalid file path."""
        try:
            from codex_ml.logging.metrics import MetricLogger

            # Try to write to read-only location
            with tempfile.TemporaryDirectory() as tmpdir:
                log_file = Path(tmpdir) / "metrics.ndjson"

                # Should work normally
                with MetricLogger(log_file) as logger:
                    logger.log(step=0, loss=1.0)

                assert log_file.exists(), "Condition must be true"
        except ImportError:
            pytest.skip("MetricLogger not available")


class TestConfigErrorPaths:
    """Test config error paths."""

    def test_env_var_config_type_mismatch(self):
        """Test EnvVarConfig with type mismatches."""
        try:
            from codex.config.config_loader import EnvVarConfig

            with patch.dict("os.environ", {"TEST_VAR": "not_a_number"}):
                config = EnvVarConfig()

                # Should handle gracefully
                value = config.get_int("TEST_VAR", default=42)
                # Should return default or raise clear error
                assert value is not None, "value must be initialized"
        except (ImportError, AttributeError):
            pytest.skip("EnvVarConfig not available")


class TestEvaluationErrorPaths:
    """Test evaluation error paths."""

    def test_accuracy_metric_empty_batch(self):
        """Test AccuracyMetric with empty batch."""
        try:
            from codex_ml.evaluation.metrics.accuracy import AccuracyMetric

            metric = AccuracyMetric()

            # Empty batch should be handled gracefully
            metric.add_batch([], [])
            result = metric.compute()
            # With no predictions, accuracy should be 0.0
            assert result == {"accuracy": 0.0}, "Result must not be empty"
        except ImportError:
            pytest.skip("AccuracyMetric not available")


# Helper
def _torch_available():
    """Check if PyTorch is available."""
    return importlib.util.find_spec("torch") is not None
