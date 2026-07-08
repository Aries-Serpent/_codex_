"""Tests for enhanced MLflow tracking writers."""

import importlib
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
                assert result is False, "Result must not be empty"

    @patch("codex_ml.tracking.writers.MLFLOW_CLIENT_AVAILABLE", True)
    @patch.dict("sys.modules", {"mlflow": Mock()})
    def test_write_metrics_success(self):
        """Test writing metrics successfully."""
        import sys

        from codex_ml.tracking.writers import MLflowMetricWriter

        # Setup mock mlflow module
        mock_mlflow = sys.modules["mlflow"]
        mock_mlflow.active_run.return_value = Mock()
        mock_mlflow.set_tracking_uri = Mock()
        mock_mlflow.set_experiment = Mock()
        mock_mlflow.log_metrics = Mock()

        writer = MLflowMetricWriter()
        writer._initialized = True

        result = writer.write({"loss": 0.5, "accuracy": 0.9}, step=10)

        assert result is True, "Result must not be empty"
        mock_mlflow.log_metrics.assert_called_once_with({"loss": 0.5, "accuracy": 0.9}, step=10)

    @patch("codex_ml.tracking.writers.MLFLOW_CLIENT_AVAILABLE", True)
    @patch.dict("sys.modules", {"mlflow": Mock()})
    def test_write_metric_single(self):
        """Test writing single metric."""
        import sys

        from codex_ml.tracking.writers import MLflowMetricWriter

        mock_mlflow = sys.modules["mlflow"]
        mock_mlflow.active_run.return_value = Mock()
        mock_mlflow.set_tracking_uri = Mock()
        mock_mlflow.set_experiment = Mock()
        mock_mlflow.log_metric = Mock()

        writer = MLflowMetricWriter()
        writer._initialized = True

        result = writer.write_metric("accuracy", 0.95, step=5)

        assert result is True, "Result must not be empty"
        mock_mlflow.log_metrics.assert_called_once_with({"accuracy": 0.95}, step=5)

    @patch("codex_ml.tracking.writers.MLFLOW_CLIENT_AVAILABLE", True)
    @patch.dict("sys.modules", {"mlflow": Mock()})
    def test_write_batch(self):
        """Test batch writing."""
        import sys

        from codex_ml.tracking.writers import MLflowMetricWriter

        mock_mlflow = sys.modules["mlflow"]
        mock_mlflow.active_run.return_value = Mock()
        mock_mlflow.set_tracking_uri = Mock()
        mock_mlflow.set_experiment = Mock()
        mock_mlflow.log_metrics = Mock()

        writer = MLflowMetricWriter()
        writer._initialized = True

        batch = [
            {"metrics": {"loss": 0.5}, "step": 1},
            {"metrics": {"loss": 0.4}, "step": 2},
        ]

        success_count = writer.write_batch(batch)

        assert success_count == 2, "Count must be greater than zero"
        assert mock_mlflow.log_metrics.call_count == 2, "Count must be greater than zero"


class TestMLflowParamWriter:
    """Test parameter writer."""

    @patch("codex_ml.tracking.writers.MLFLOW_CLIENT_AVAILABLE", True)
    @patch.dict("sys.modules", {"mlflow": Mock()})
    def test_write_params(self):
        """Test writing parameters."""
        import sys

        from codex_ml.tracking.writers import MLflowMetricWriter, MLflowParamWriter

        mock_mlflow = sys.modules["mlflow"]
        mock_mlflow.active_run.return_value = Mock()
        mock_mlflow.set_tracking_uri = Mock()
        mock_mlflow.set_experiment = Mock()
        mock_mlflow.log_params = Mock()

        metric_writer = MLflowMetricWriter()
        metric_writer._initialized = True

        param_writer = MLflowParamWriter(metric_writer)

        result = param_writer.write_params({"lr": 0.001, "epochs": 10})

        assert result is True, "Result must not be empty"
        mock_mlflow.log_params.assert_called_once_with({"lr": "0.001", "epochs": "10"})

    @patch("codex_ml.tracking.writers.MLFLOW_CLIENT_AVAILABLE", True)
    @patch.dict("sys.modules", {"mlflow": Mock()})
    def test_write_config_flattened(self):
        """Test writing nested config."""
        import sys

        from codex_ml.tracking.writers import MLflowMetricWriter, MLflowParamWriter

        mock_mlflow = sys.modules["mlflow"]
        mock_mlflow.active_run.return_value = Mock()
        mock_mlflow.set_tracking_uri = Mock()
        mock_mlflow.set_experiment = Mock()
        mock_mlflow.log_params = Mock()

        metric_writer = MLflowMetricWriter()
        metric_writer._initialized = True

        param_writer = MLflowParamWriter(metric_writer)

        config = {
            "model": {"type": "gpt2", "layers": 12},
            "training": {"lr": 0.001},
        }

        result = param_writer.write_config(config)

        assert result is True, "Result must not be empty"
        # Check that params were flattened
        call_args = mock_mlflow.log_params.call_args[0][0]
        assert "model.type" in call_args, "Condition must be true"
        assert "model.layers" in call_args, "Condition must be true"
        assert "training.lr" in call_args, "Condition must be true"


class TestMLflowArtifactWriter:
    """Test artifact writer."""

    @patch("codex_ml.tracking.writers.MLFLOW_CLIENT_AVAILABLE", True)
    @patch.dict("sys.modules", {"mlflow": Mock()})
    def test_log_artifact(self, tmp_path):
        """Test artifact logging with proper cleanup using pytest tmp_path."""
        import sys

        from codex_ml.tracking.writers import MLflowArtifactWriter, MLflowMetricWriter

        mock_mlflow = sys.modules["mlflow"]
        mock_mlflow.active_run.return_value = Mock()
        mock_mlflow.set_tracking_uri = Mock()
        mock_mlflow.set_experiment = Mock()
        mock_mlflow.log_artifact = Mock()

        metric_writer = MLflowMetricWriter()
        metric_writer._initialized = True

        artifact_writer = MLflowArtifactWriter(metric_writer)

        # Use pytest's tmp_path fixture (auto-cleanup)
        tmp_file = tmp_path / "test_artifact.txt"
        tmp_file.write_text("test content")

        result = artifact_writer.log_artifact(str(tmp_file))

        assert result is True, "Result must not be empty"
        mock_mlflow.log_artifact.assert_called_once()


class TestMLflowRunManager:
    """Test MLflow run manager."""

    @patch("codex_ml.tracking.writers.MLFLOW_CLIENT_AVAILABLE", False)
    def test_context_manager_without_mlflow(self):
        """Context manager should work without MLflow."""
        from codex_ml.tracking.writers import MLflowRunManager

        manager = MLflowRunManager()
        with manager.start_run():
            assert manager.run_id is None, "run_id is not valid"

    @patch("codex_ml.tracking.writers.MLFLOW_CLIENT_AVAILABLE", True)
    @patch.dict("sys.modules", {"mlflow": Mock()})
    def test_context_manager_with_mlflow(self):
        """Test context manager with MLflow."""
        import sys

        from codex_ml.tracking.writers import MLflowRunManager

        mock_mlflow = sys.modules["mlflow"]
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
            assert manager.run_id == "test_run_123", "run_id is not valid"

    @patch("codex_ml.tracking.writers.MLFLOW_CLIENT_AVAILABLE", True)
    @patch.dict("sys.modules", {"mlflow": Mock()})
    def test_convenience_methods(self):
        """Test convenience logging methods."""
        import sys

        from codex_ml.tracking.writers import MLflowRunManager

        mock_mlflow = sys.modules["mlflow"]
        mock_mlflow.active_run.return_value = Mock()
        mock_mlflow.set_tracking_uri = Mock()
        mock_mlflow.set_experiment = Mock()
        mock_mlflow.log_metrics = Mock()

        manager = MLflowRunManager()
        manager.metric_writer._initialized = True

        # Test log_metrics
        result = manager.log_metrics({"loss": 0.5}, step=1)
        assert result is True, "Result must not be empty"

        # Test log_params
        result = manager.log_params({"lr": 0.001})
        assert result is True, "Result must not be empty"


class TestCreateMLflowTracker:
    """Test factory function."""

    def test_create_tracker(self):
        """Test creating tracker."""
        from codex_ml.tracking.writers import create_mlflow_tracker

        tracker = create_mlflow_tracker(
            experiment_name="test_exp",
            run_name="test_run",
        )

        assert tracker.run_name == "test_run", "run_name is not valid"
        assert tracker.metric_writer.experiment_name == "test_exp", "experiment_name is not valid"

    def test_tracker_has_all_writers(self):
        """Test tracker has all writer types."""
        from codex_ml.tracking.writers import create_mlflow_tracker

        tracker = create_mlflow_tracker()

        assert hasattr(tracker, "metric_writer")
        assert hasattr(tracker, "param_writer")
        assert hasattr(tracker, "artifact_writer")
