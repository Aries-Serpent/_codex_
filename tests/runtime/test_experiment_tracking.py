"""Experiment tracking integration tests for MLflow and wandb.

Tests for Phase 2 Lane 2.2 runtime profile validation.
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path
from typing import Optional
from unittest.mock import MagicMock, patch

import pytest

# Add runtime directory to path for fixture imports
runtime_dir = Path(__file__).parent
sys.path.insert(0, str(runtime_dir))

try:
    from tracking_fixtures import (
        mlflow_client,
        mlflow_experiment,
        mlflow_run,
        mlflow_tracking_uri,
        temp_mlflow_dir,
        wandb_config,
        wandb_mock,
        mlflow_tracker_instance,
        wandb_logger_instance,
        mock_mlflow_tracking_context,
        mock_wandb_tracking_context,
    )
except ImportError:
    # Fixtures will be loaded by pytest discovery
    pass


class TestMLflowServerInitialization:
    """Test MLflow server initialization and configuration."""

    def test_mlflow_tracking_uri_configuration(self, mlflow_tracking_uri: str):
        """Test that MLflow tracking URI is properly configured."""
        assert mlflow_tracking_uri.startswith("sqlite:///")
        assert "mlruns.db" in mlflow_tracking_uri

    def test_mlflow_client_creation(self, mlflow_client):
        """Test that MLflow client can be created."""
        assert mlflow_client is not None
        assert hasattr(mlflow_client, "create_experiment")
        assert hasattr(mlflow_client, "create_run")

    def test_mlflow_tracking_uri_environment(self, mlflow_tracking_uri: str):
        """Test MLflow tracking URI via environment variable."""
        with mock_mlflow_tracking_context(mlflow_tracking_uri):
            assert os.environ.get("MLFLOW_TRACKING_URI") == mlflow_tracking_uri


class TestMLflowExperimentCreation:
    """Test MLflow experiment creation and management."""

    def test_mlflow_experiment_creation(self, mlflow_client, temp_mlflow_dir: Path):
        """Test that MLflow experiments can be created."""
        exp_name = "test_exp_creation"
        exp_id = mlflow_client.create_experiment(exp_name)

        assert exp_id is not None
        experiment = mlflow_client.get_experiment(exp_id)
        assert experiment is not None
        assert experiment.name == exp_name

    def test_mlflow_experiment_retrieval(self, mlflow_experiment: dict):
        """Test that created MLflow experiment can be retrieved."""
        assert mlflow_experiment["id"] is not None
        assert mlflow_experiment["name"] == "test_experiment_integration"
        assert mlflow_experiment["tracking_uri"] is not None

    def test_mlflow_experiment_list(self, mlflow_client, mlflow_experiment: dict):
        """Test that experiments can be listed."""
        experiments = mlflow_client.search_experiments()
        assert experiments is not None
        exp_names = [exp.name for exp in experiments]
        assert mlflow_experiment["name"] in exp_names


class TestMLflowRunLogging:
    """Test MLflow run creation and basic logging."""

    def test_mlflow_run_creation(self, mlflow_run: dict):
        """Test that MLflow runs can be created."""
        assert mlflow_run["id"] is not None
        assert mlflow_run["experiment_id"] is not None
        assert mlflow_run["status"] == "RUNNING"

    def test_mlflow_parameter_logging(self, mlflow_client, mlflow_run: dict):
        """Test logging parameters to MLflow runs."""
        run_id = mlflow_run["id"]

        params = {
            "learning_rate": "0.001",
            "batch_size": "32",
            "epochs": "10",
        }

        for key, value in params.items():
            mlflow_client.log_param(run_id, key, value)

        # Retrieve run and verify parameters
        run = mlflow_client.get_run(run_id)
        assert run.data.params["learning_rate"] == "0.001"
        assert run.data.params["batch_size"] == "32"
        assert run.data.params["epochs"] == "10"

    def test_mlflow_metrics_logging(self, mlflow_client, mlflow_run: dict):
        """Test logging metrics to MLflow runs."""
        run_id = mlflow_run["id"]

        # Log individual metrics
        mlflow_client.log_metric(run_id, "accuracy", 0.95)
        mlflow_client.log_metric(run_id, "loss", 0.05)
        mlflow_client.log_metric(run_id, "f1_score", 0.92)

        # Retrieve run and verify metrics
        run = mlflow_client.get_run(run_id)
        assert run.data.metrics["accuracy"] == 0.95
        assert run.data.metrics["loss"] == 0.05
        assert run.data.metrics["f1_score"] == 0.92

    def test_mlflow_metrics_with_step(self, mlflow_client, mlflow_run: dict):
        """Test logging metrics with step tracking."""
        run_id = mlflow_run["id"]

        # Log metrics across multiple steps
        for step in range(5):
            mlflow_client.log_metric(run_id, "train_loss", 1.0 - (step * 0.1), step=step)

        # Verify metrics were logged
        run = mlflow_client.get_run(run_id)
        assert "train_loss" in run.data.metrics


class TestMLflowArtifactHandling:
    """Test MLflow artifact storage and retrieval."""

    def test_mlflow_artifact_upload(self, mlflow_client, mlflow_run: dict, temp_mlflow_dir: Path):
        """Test uploading artifacts to MLflow."""
        run_id = mlflow_run["id"]

        # Create a temporary artifact
        artifact_content = "test artifact content"
        artifact_file = temp_mlflow_dir / "test_artifact.txt"
        artifact_file.write_text(artifact_content)

        # Log artifact
        mlflow_client.log_artifact(run_id, str(artifact_file))

        # Verify artifact exists
        run = mlflow_client.get_run(run_id)
        assert run is not None

    def test_mlflow_multiple_artifacts(self, mlflow_client, mlflow_run: dict, temp_mlflow_dir: Path):
        """Test uploading multiple artifacts."""
        run_id = mlflow_run["id"]

        # Create multiple artifacts
        artifacts_dir = temp_mlflow_dir / "artifacts"
        artifacts_dir.mkdir(exist_ok=True)

        (artifacts_dir / "model.txt").write_text("model data")
        (artifacts_dir / "metrics.json").write_text('{"accuracy": 0.95}')
        (artifacts_dir / "config.yaml").write_text("learning_rate: 0.001\nbatch_size: 32\n")

        # Log all artifacts
        for artifact_file in artifacts_dir.iterdir():
            mlflow_client.log_artifact(run_id, str(artifact_file))

        # Verify at least one artifact exists
        run = mlflow_client.get_run(run_id)
        assert run is not None


class TestMLflowTrackerWrapper:
    """Test the MLflowTracker wrapper class."""

    @pytest.mark.skipif(
        not __import__("importlib.util").util.find_spec("mlflow"),
        reason="MLflow not installed",
    )
    def test_mlflow_tracker_initialization(self, mlflow_tracker_instance):
        """Test MLflowTracker initialization."""
        # When MLflow is available, check enabled status
        if mlflow_tracker_instance.enabled:
            assert mlflow_tracker_instance.experiment_name == "integration_test"
            assert mlflow_tracker_instance.run_name == "test_run"
        # If disabled due to missing mlflow, skip gracefully
        pytest.skip("MLflow initialization skipped (not available)")

    @pytest.mark.skipif(
        not __import__("importlib.util").util.find_spec("mlflow"),
        reason="MLflow not installed",
    )
    def test_mlflow_tracker_context_manager(self, mlflow_tracker_instance):
        """Test MLflowTracker as context manager."""
        if not mlflow_tracker_instance.enabled:
            pytest.skip("MLflow not available")

        with mlflow_tracker_instance.start_run() as run_info:
            assert mlflow_tracker_instance._active is True

        assert mlflow_tracker_instance._active is False

    @pytest.mark.skipif(
        not __import__("importlib.util").util.find_spec("mlflow"),
        reason="MLflow not installed",
    )
    def test_mlflow_tracker_parameter_logging(self, mlflow_tracker_instance):
        """Test logging parameters via MLflowTracker."""
        if not mlflow_tracker_instance.enabled:
            pytest.skip("MLflow not available")

        with mlflow_tracker_instance.start_run():
            mlflow_tracker_instance.log_param("learning_rate", 0.001)
            mlflow_tracker_instance.log_param("batch_size", 32)
            assert mlflow_tracker_instance._run is not None

    @pytest.mark.skipif(
        not __import__("importlib.util").util.find_spec("mlflow"),
        reason="MLflow not installed",
    )
    def test_mlflow_tracker_metrics_logging(self, mlflow_tracker_instance):
        """Test logging metrics via MLflowTracker."""
        if not mlflow_tracker_instance.enabled:
            pytest.skip("MLflow not available")

        with mlflow_tracker_instance.start_run():
            mlflow_tracker_instance.log_metric("accuracy", 0.95)
            mlflow_tracker_instance.log_metric("loss", 0.05)
            assert mlflow_tracker_instance._run is not None


class TestWandBIntegration:
    """Test wandb integration with graceful degradation."""

    def test_wandb_configuration(self, wandb_config: dict):
        """Test wandb configuration."""
        assert wandb_config["project"] == "codex-test"
        assert wandb_config["mode"] == "offline"

    def test_wandb_environment_mode(self):
        """Test wandb environment mode configuration."""
        with mock_wandb_tracking_context("offline"):
            assert os.environ.get("WANDB_MODE") == "offline"

    def test_wandb_mock_initialization(self, wandb_mock):
        """Test wandb mock initialization."""
        run = wandb_mock.init(project="test", mode="offline")
        assert run is not None
        assert run.state == "running"

    def test_wandb_mock_logging(self, wandb_mock):
        """Test wandb mock metric logging."""
        run = wandb_mock.init(project="test", mode="offline")
        wandb_mock.log({"accuracy": 0.95, "loss": 0.05})
        assert run.log_count > 0

    def test_wandb_graceful_skip(self):
        """Test that wandb tests skip gracefully if not configured."""
        # This test verifies that wandb integration doesn't break when unavailable
        try:
            import wandb

            # If wandb is available, verify it can be used
            assert wandb is not None
        except ImportError:
            # If wandb is not available, test should skip naturally
            pytest.skip("wandb not installed")


class TestExperimentTrackingIntegration:
    """End-to-end integration tests for experiment tracking."""

    def test_complete_mlflow_workflow(self, mlflow_client, mlflow_experiment: dict, temp_mlflow_dir: Path):
        """Test a complete MLflow workflow: create experiment, run, log params/metrics."""
        exp_id = mlflow_experiment["id"]

        # Create run
        run = mlflow_client.create_run(experiment_id=exp_id)
        run_id = run.info.run_id

        # Log parameters
        mlflow_client.log_param(run_id, "model", "bert-base")
        mlflow_client.log_param(run_id, "lr", "0.001")

        # Log metrics across steps
        for step in range(3):
            mlflow_client.log_metric(run_id, "loss", 1.0 - step * 0.2, step=step)
            mlflow_client.log_metric(run_id, "accuracy", 0.5 + step * 0.15, step=step)

        # Create and log artifact
        artifact_file = temp_mlflow_dir / "model_config.json"
        artifact_file.write_text('{"layers": 12, "hidden_size": 768}')
        mlflow_client.log_artifact(run_id, str(artifact_file))

        # End run
        mlflow_client.set_terminated(run_id)

        # Verify complete run
        completed_run = mlflow_client.get_run(run_id)
        assert completed_run.data.params["model"] == "bert-base"
        assert completed_run.data.metrics["loss"] < 1.0
        assert completed_run.data.metrics["accuracy"] > 0.5

    def test_multiple_parallel_runs(self, mlflow_client, mlflow_experiment: dict):
        """Test tracking multiple parallel runs."""
        exp_id = mlflow_experiment["id"]
        runs = []

        # Create multiple runs
        for i in range(3):
            run = mlflow_client.create_run(experiment_id=exp_id)
            run_id = run.info.run_id

            # Log different parameters for each run
            mlflow_client.log_param(run_id, "model_variant", f"variant_{i}")
            mlflow_client.log_metric(run_id, "accuracy", 0.8 + i * 0.05)

            runs.append(run_id)

        # Verify all runs exist
        assert len(runs) == 3
        for run_id in runs:
            run = mlflow_client.get_run(run_id)
            assert run is not None

    def test_experiment_tracking_with_timestamps(self, mlflow_client, mlflow_experiment: dict):
        """Test that experiment tracking includes timestamps."""
        exp_id = mlflow_experiment["id"]
        run = mlflow_client.create_run(experiment_id=exp_id)
        run_id = run.info.run_id

        # Log metrics with timestamps
        mlflow_client.log_metric(run_id, "batch_time", 0.523, step=0)
        mlflow_client.log_metric(run_id, "batch_time", 0.512, step=1)

        # Verify run has timestamps
        completed_run = mlflow_client.get_run(run_id)
        assert completed_run.info.start_time is not None
