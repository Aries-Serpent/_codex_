"""Tests for enhanced MLflow tracking writers."""

import importlib
import tempfile
from unittest.mock import Mock, patch


class TestMLflowMetricWriter:
    """Test enhanced MLflow metric writer."""

    def test_graceful_degradation_without_mlflow(self):
        """Writer should not crash when MLflow unavailable."""
        # Direct import to avoid dependency issues
        with patch.dict("sys.modules", {"torch": Mock()}):
            from codex_ml.tracking import writers

            importlib.reload(writers)

            with patch.object(writers, "MLFLOW_CLIENT_AVAILABLE", False):
                writer = writers.MLflowMetricWriter()
                result = writer.write({"loss": 0.5}, step=1)
                assert result is False

    @patch("codex_ml.tracking.writers.MLFLOW_CLIENT_AVAILABLE", True)
    @patch("codex_ml.tracking.writers.mlflow")
    def test_write_metrics_success(self, mock_mlflow):
        """Test writing metrics successfully."""
        from codex_ml.tracking.writers import MLflowMetricWriter

        # Setup mock
        mock_mlflow.active_run.return_value = Mock()
        mock_mlflow.set_tracking_uri = Mock()
        mock_mlflow.set_experiment = Mock()

        writer = MLflowMetricWriter()
        writer._initialized = True

        result = writer.write({"loss": 0.5, "accuracy": 0.9}, step=10)

        assert result is True
        mock_mlflow.log_metrics.assert_called_once_with({"loss": 0.5, "accuracy": 0.9}, step=10)

    @patch("codex_ml.tracking.writers.MLFLOW_CLIENT_AVAILABLE", True)
    @patch("codex_ml.tracking.writers.mlflow")
    def test_write_metric_single(self, mock_mlflow):
        """Test writing single metric."""
        from codex_ml.tracking.writers import MLflowMetricWriter

        mock_mlflow.active_run.return_value = Mock()
        mock_mlflow.set_tracking_uri = Mock()
        mock_mlflow.set_experiment = Mock()

        writer = MLflowMetricWriter()
        writer._initialized = True

        result = writer.write_metric("accuracy", 0.95, step=5)

        assert result is True
        mock_mlflow.log_metrics.assert_called_once_with({"accuracy": 0.95}, step=5)

    @patch("codex_ml.tracking.writers.MLFLOW_CLIENT_AVAILABLE", True)
    @patch("codex_ml.tracking.writers.mlflow")
    def test_write_batch(self, mock_mlflow):
        """Test batch writing."""
        from codex_ml.tracking.writers import MLflowMetricWriter

        mock_mlflow.active_run.return_value = Mock()
        mock_mlflow.set_tracking_uri = Mock()
        mock_mlflow.set_experiment = Mock()

        writer = MLflowMetricWriter()
        writer._initialized = True

        batch = [
            {"metrics": {"loss": 0.5}, "step": 1},
            {"metrics": {"loss": 0.4}, "step": 2},
        ]

        success_count = writer.write_batch(batch)

        assert success_count == 2
        assert mock_mlflow.log_metrics.call_count == 2


class TestMLflowParamWriter:
    """Test parameter writer."""

    @patch("codex_ml.tracking.writers.MLFLOW_CLIENT_AVAILABLE", True)
    @patch("codex_ml.tracking.writers.mlflow")
    def test_write_params(self, mock_mlflow):
        """Test writing parameters."""
        from codex_ml.tracking.writers import MLflowMetricWriter, MLflowParamWriter

        mock_mlflow.active_run.return_value = Mock()
        mock_mlflow.set_tracking_uri = Mock()
        mock_mlflow.set_experiment = Mock()

        metric_writer = MLflowMetricWriter()
        metric_writer._initialized = True

        param_writer = MLflowParamWriter(metric_writer)

        result = param_writer.write_params({"lr": 0.001, "epochs": 10})

        assert result is True
        mock_mlflow.log_params.assert_called_once_with({"lr": "0.001", "epochs": "10"})

    @patch("codex_ml.tracking.writers.MLFLOW_CLIENT_AVAILABLE", True)
    @patch("codex_ml.tracking.writers.mlflow")
    def test_write_config_flattened(self, mock_mlflow):
        """Test writing nested config."""
        from codex_ml.tracking.writers import MLflowMetricWriter, MLflowParamWriter

        mock_mlflow.active_run.return_value = Mock()
        mock_mlflow.set_tracking_uri = Mock()
        mock_mlflow.set_experiment = Mock()

        metric_writer = MLflowMetricWriter()
        metric_writer._initialized = True

        param_writer = MLflowParamWriter(metric_writer)

        config = {
            "model": {"type": "gpt2", "layers": 12},
            "training": {"lr": 0.001},
        }

        result = param_writer.write_config(config)

        assert result is True
        # Check that params were flattened
        call_args = mock_mlflow.log_params.call_args[0][0]
        assert "model.type" in call_args
        assert "model.layers" in call_args
        assert "training.lr" in call_args


class TestMLflowArtifactWriter:
    """Test artifact writer."""

    @patch("codex_ml.tracking.writers.MLFLOW_CLIENT_AVAILABLE", True)
    @patch("codex_ml.tracking.writers.mlflow")
    def test_log_artifact(self, mock_mlflow):
        """Test logging artifact."""
        from codex_ml.tracking.writers import MLflowArtifactWriter, MLflowMetricWriter

        mock_mlflow.active_run.return_value = Mock()
        mock_mlflow.set_tracking_uri = Mock()
        mock_mlflow.set_experiment = Mock()

        metric_writer = MLflowMetricWriter()
        metric_writer._initialized = True

        artifact_writer = MLflowArtifactWriter(metric_writer)

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("test artifact")
            temp_path = f.name

        try:
            result = artifact_writer.log_artifact(temp_path)

            assert result is True
            mock_mlflow.log_artifact.assert_called_once()
        finally:
            # Clean up temporary file
            import os

            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestMLflowRunManager:
    """Test MLflow run manager."""

    @patch("codex_ml.tracking.writers.MLFLOW_CLIENT_AVAILABLE", False)
    def test_context_manager_without_mlflow(self):
        """Context manager should work without MLflow."""
        from codex_ml.tracking.writers import MLflowRunManager

        manager = MLflowRunManager()
        with manager.start_run():
            assert manager.run_id is None

    @patch("codex_ml.tracking.writers.MLFLOW_CLIENT_AVAILABLE", True)
    @patch("codex_ml.tracking.writers.mlflow")
    def test_context_manager_with_mlflow(self, mock_mlflow):
        """Test context manager with MLflow."""
        from codex_ml.tracking.writers import MLflowRunManager

        # Setup mock run
        mock_run = Mock()
        mock_run.info.run_id = "test_run_123"
        mock_run.__enter__ = Mock(return_value=mock_run)
        mock_run.__exit__ = Mock(return_value=False)

        mock_mlflow.start_run.return_value = mock_run
        mock_mlflow.set_tracking_uri = Mock()
        mock_mlflow.set_experiment = Mock()

        manager = MLflowRunManager(run_name="test_run")
        manager.metric_writer._initialized = True

        with manager.start_run():
            assert manager.run_id == "test_run_123"

    @patch("codex_ml.tracking.writers.MLFLOW_CLIENT_AVAILABLE", True)
    @patch("codex_ml.tracking.writers.mlflow")
    def test_convenience_methods(self, mock_mlflow):
        """Test convenience logging methods."""
        from codex_ml.tracking.writers import MLflowRunManager

        mock_mlflow.active_run.return_value = Mock()
        mock_mlflow.set_tracking_uri = Mock()
        mock_mlflow.set_experiment = Mock()

        manager = MLflowRunManager()
        manager.metric_writer._initialized = True

        # Test log_metrics
        result = manager.log_metrics({"loss": 0.5}, step=1)
        assert result is True

        # Test log_params
        result = manager.log_params({"lr": 0.001})
        assert result is True


class TestCreateMLflowTracker:
    """Test factory function."""

    def test_create_tracker(self):
        """Test creating tracker."""
        from codex_ml.tracking.writers import create_mlflow_tracker

        tracker = create_mlflow_tracker(
            experiment_name="test_exp",
            run_name="test_run",
        )

        assert tracker.run_name == "test_run"
        assert tracker.metric_writer.experiment_name == "test_exp"

    def test_tracker_has_all_writers(self):
        """Test tracker has all writer types."""
        from codex_ml.tracking.writers import create_mlflow_tracker

        tracker = create_mlflow_tracker()

        assert hasattr(tracker, "metric_writer")
        assert hasattr(tracker, "param_writer")
        assert hasattr(tracker, "artifact_writer")
