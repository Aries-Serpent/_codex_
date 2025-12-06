"""Tests for MLflow integration."""
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from codex_ml.training.mlflow_integration import (
    MLflowTracker,
    is_mlflow_available,
    init_mlflow,
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
        
        assert tracker.experiment_name == "test_exp"
        assert tracker.tracking_uri == tmpdir
        assert tracker.active is True


def test_mlflow_tracker_graceful_degradation():
    """Test MLflowTracker gracefully handles missing MLflow."""
    with patch('codex_ml.training.mlflow_integration.MLFLOW_AVAILABLE', False):
        tracker = MLflowTracker(
            experiment_name="test_exp",
            tracking_uri="./mlruns",
        )
        
        # Should initialize but not be active
        assert tracker.active is False
        
        # These should not raise errors even when inactive
        tracker.log_metrics({"loss": 0.5}, step=1)
        tracker.log_params({"lr": 0.001})
        tracker.log_artifact("/tmp/test.txt")


@pytest.mark.skipif(not is_mlflow_available(), reason="MLflow not installed")
def test_mlflow_tracker_context_manager():
    """Test MLflowTracker as context manager."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with MLflowTracker("test_exp", tracking_uri=tmpdir) as tracker:
            assert tracker.active is True
            tracker.log_params({"batch_size": 32})
            tracker.log_metrics({"accuracy": 0.95}, step=0)
        
        # Run should be ended
        assert tracker.run_id is None


@pytest.mark.skipif(not is_mlflow_available(), reason="MLflow not installed")
def test_mlflow_tracker_log_operations():
    """Test MLflow logging operations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tracker = MLflowTracker("test_exp", tracking_uri=tmpdir)
        tracker.start_run(run_name="test_run")
        
        # Log params
        tracker.log_params({
            "lr": 0.001,
            "batch_size": 32,
            "epochs": 10,
        })
        
        # Log metrics
        tracker.log_metrics({"loss": 0.5, "accuracy": 0.9}, step=0)
        tracker.log_metrics({"loss": 0.3, "accuracy": 0.92}, step=1)
        
        # Log tags
        tracker.set_tags({"model": "gpt2", "dataset": "wiki"})
        
        tracker.end_run()


def test_init_mlflow_function():
    """Test init_mlflow convenience function."""
    with patch('codex_ml.training.mlflow_integration.MLFLOW_AVAILABLE', True):
        with patch('codex_ml.training.mlflow_integration.mlflow'):
            tracker = init_mlflow(
                experiment_name="test",
                run_name="run1",
                auto_start=False,
            )
            
            assert tracker.experiment_name == "test"
            assert tracker.run_name == "run1"


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
