"""Tests for MLflow integration."""
import pytest

pytest.importorskip("mlflow")

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

from codex_ml.training.mlflow_integration import (
    MLflowTracker,
    init_mlflow,
    is_mlflow_available,
)


def test_is_mlflow_available():
    """Test MLflow availability check."""
    # This will return True if mlflow is installed, False otherwise
    available = is_mlflow_available()
    assert isinstance(available, bool)


@pytest.mark.skipif(not is_mlflow_available(), reason="MLflow not installed")
def test_mlflow_tracker_initialization():
    """Test MLflowTracker initialization with MLflow available."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tracker = MLflowTracker(
            experiment_name="test_exp",
            tracking_uri=tmpdir,
        )

        assert tracker.experiment_name == "test_exp", "experiment_name is not valid"
        assert tracker.tracking_uri == tmpdir, "tracking_uri is not valid"
        assert tracker.active is True, "active is not valid"


def test_mlflow_tracker_graceful_degradation():
    """Test MLflowTracker gracefully handles missing MLflow."""
    with patch("codex_ml.training.mlflow_integration.MLFLOW_AVAILABLE", False):
        tracker = MLflowTracker(
            experiment_name="test_exp",
            tracking_uri="./mlruns",
        )

        # Should initialize but not be active
        assert tracker.active is False, "active is not valid"

        # These should not raise errors even when inactive
        tracker.log_metrics({"loss": 0.5}, step=1)
        tracker.log_params({"lr": 0.001})
        with tempfile.NamedTemporaryFile() as temp_file:
            tracker.log_artifact(temp_file.name)


def test_mlflow_tracker_sets_file_store_env_for_local_uri():
    """Test local-path tracking enables file-store compatibility flag."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch("codex_ml.training.mlflow_integration.MLFLOW_AVAILABLE", True):
            with patch("codex_ml.training.mlflow_integration.mlflow") as mlflow_mock:
                with patch.dict(os.environ, {"MLFLOW_ALLOW_FILE_STORE": "placeholder"}):
                    del os.environ["MLFLOW_ALLOW_FILE_STORE"]
                    tracker = MLflowTracker("test_exp", tracking_uri=tmpdir)

                    assert os.environ["MLFLOW_ALLOW_FILE_STORE"] == "true", "Condition must be true"
                    assert tracker.active is True, "active is not valid"
                    mlflow_mock.set_tracking_uri.assert_called_once_with(tmpdir)


def test_mlflow_tracker_sets_file_store_env_for_file_scheme_uri():
    """Test file:// URI tracking enables file-store compatibility flag."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tracking_uri = Path(tmpdir).resolve().as_uri()
        with patch("codex_ml.training.mlflow_integration.MLFLOW_AVAILABLE", True):
            with patch("codex_ml.training.mlflow_integration.mlflow") as mlflow_mock:
                with patch.dict(os.environ, {"MLFLOW_ALLOW_FILE_STORE": "placeholder"}):
                    del os.environ["MLFLOW_ALLOW_FILE_STORE"]
                    tracker = MLflowTracker("test_exp", tracking_uri=tracking_uri)

                    assert os.environ["MLFLOW_ALLOW_FILE_STORE"] == "true", "Condition must be true"
                    assert tracker.active is True, "active is not valid"
                    mlflow_mock.set_tracking_uri.assert_called_once_with(tracking_uri)


def test_mlflow_tracker_does_not_set_file_store_env_for_remote_uri():
    """Test remote tracking URI does not enable file-store compatibility flag."""
    with patch("codex_ml.training.mlflow_integration.MLFLOW_AVAILABLE", True):
        with patch("codex_ml.training.mlflow_integration.mlflow") as mlflow_mock:
            with patch.dict(os.environ, {"MLFLOW_ALLOW_FILE_STORE": "placeholder"}):
                del os.environ["MLFLOW_ALLOW_FILE_STORE"]
                tracker = MLflowTracker("test_exp", tracking_uri="http://localhost:5000")

                assert "MLFLOW_ALLOW_FILE_STORE" not in os.environ, "Condition must be true"
                assert tracker.active is True, "active is not valid"
                mlflow_mock.set_tracking_uri.assert_called_once_with("http://localhost:5000")


def test_mlflow_tracker_preserves_existing_file_store_env():
    """Test pre-set file-store compatibility flag is preserved."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch("codex_ml.training.mlflow_integration.MLFLOW_AVAILABLE", True):
            with patch("codex_ml.training.mlflow_integration.mlflow"):
                with patch.dict(os.environ, {"MLFLOW_ALLOW_FILE_STORE": "true"}):
                    tracker = MLflowTracker("test_exp", tracking_uri=tmpdir)

                    assert os.environ["MLFLOW_ALLOW_FILE_STORE"] == "true", "Condition must be true"
                    assert tracker.active is True, "active is not valid"


def test_mlflow_tracker_preserves_non_true_file_store_env():
    """Test non-true pre-set file-store flag value is preserved."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch("codex_ml.training.mlflow_integration.MLFLOW_AVAILABLE", True):
            with patch("codex_ml.training.mlflow_integration.mlflow"):
                with patch.dict(os.environ, {"MLFLOW_ALLOW_FILE_STORE": "false"}):
                    tracker = MLflowTracker("test_exp", tracking_uri=tmpdir)

                    assert os.environ["MLFLOW_ALLOW_FILE_STORE"] == "false", "Condition must be true"
                    assert tracker.active is True, "active is not valid"


@pytest.mark.skipif(not is_mlflow_available(), reason="MLflow not installed")
def test_mlflow_tracker_context_manager():
    """Test MLflowTracker as context manager."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with MLflowTracker("test_exp", tracking_uri=tmpdir) as tracker:
            assert tracker.active is True, "active is not valid"
            tracker.log_params({"batch_size": 32})
            tracker.log_metrics({"accuracy": 0.95}, step=0)

        # Run should be ended
        assert tracker.run_id is None, "run_id is not valid"


@pytest.mark.skipif(not is_mlflow_available(), reason="MLflow not installed")
def test_mlflow_tracker_log_operations():
    """Test MLflow logging operations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tracker = MLflowTracker("test_exp", tracking_uri=tmpdir)
        tracker.start_run(run_name="test_run")

        # Log params
        tracker.log_params(
            {
                "lr": 0.001,
                "batch_size": 32,
                "epochs": 10,
            }
        )

        # Log metrics
        tracker.log_metrics({"loss": 0.5, "accuracy": 0.9}, step=0)
        tracker.log_metrics({"loss": 0.3, "accuracy": 0.92}, step=1)

        # Log tags
        tracker.set_tags({"model": "gpt2", "dataset": "wiki"})

        tracker.end_run()


def test_init_mlflow_function():
    """Test init_mlflow convenience function."""
    with patch("codex_ml.training.mlflow_integration.MLFLOW_AVAILABLE", True):
        with patch("codex_ml.training.mlflow_integration.mlflow"):
            tracker = init_mlflow(
                experiment_name="test",
                run_name="run1",
                auto_start=False,
            )

            assert tracker.experiment_name == "test", "experiment_name is not valid"
            assert tracker.run_name == "run1", "run_name is not valid"


@pytest.mark.skipif(not is_mlflow_available(), reason="MLflow not installed")
def test_mlflow_tracker_artifact_logging():
    """Test artifact logging."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a test file
        test_file = Path(tmpdir) / "test.txt"
        test_file.write_text("test content")

        tracker = MLflowTracker("test_exp", tracking_uri=tmpdir)
        tracker.start_run()

        # Log single artifact
        tracker.log_artifact(str(test_file))

        # Create directory with multiple files
        artifact_dir = Path(tmpdir) / "artifacts"
        artifact_dir.mkdir()
        (artifact_dir / "file1.txt").write_text("content1")
        (artifact_dir / "file2.txt").write_text("content2")

        # Log directory
        tracker.log_artifacts(str(artifact_dir))

        tracker.end_run()


def test_mlflow_tracker_error_handling():
    """Test error handling in MLflow operations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tracker = MLflowTracker("test_exp", tracking_uri=tmpdir)

        # Try to log artifact that doesn't exist
        tracker.log_artifact("/nonexistent/file.txt")  # Should log warning, not raise

        # Try to log directory that doesn't exist
        tracker.log_artifacts("/nonexistent/dir")  # Should log warning, not raise
