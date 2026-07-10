"""Advanced experiment tracking fixtures for full profile validation.

Provides comprehensive fixtures for testing MLflow and wandb at production scale.
"""

from __future__ import annotations

import json
import logging
import os
import tempfile
from pathlib import Path
from typing import Generator, Optional
from unittest.mock import MagicMock, patch

import pytest

logger = logging.getLogger(__name__)


@pytest.fixture
def mlflow_temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for MLflow artifacts and runs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir)
        (path / "mlruns").mkdir(exist_ok=True)
        (path / "artifacts").mkdir(exist_ok=True)
        (path / "models").mkdir(exist_ok=True)
        yield path


@pytest.fixture
def mlflow_tracking_uri_full(mlflow_temp_dir: Path) -> str:
    """Get SQLite-based tracking URI for full profile testing."""
    db_path = mlflow_temp_dir / "mlruns" / "mlruns.db"
    uri = f"sqlite:///{db_path}"
    return uri


@pytest.fixture
def mlflow_client_full(mlflow_tracking_uri_full: str):
    """Create MLflow client for full profile testing."""
    try:
        import mlflow
        from mlflow.tracking import MlflowClient

        mlflow.set_tracking_uri(mlflow_tracking_uri_full)
        client = MlflowClient(tracking_uri=mlflow_tracking_uri_full)
        yield client
    except ImportError:
        pytest.skip("MLflow not installed")


@pytest.fixture
def parent_experiment(mlflow_client_full):
    """Create a parent experiment for nested experiment testing."""
    try:
        import mlflow

        parent_name = "parent_experiment_full"
        experiment = None
        try:
            experiment = mlflow_client_full.get_experiment_by_name(parent_name)
        except Exception:
            pass

        if experiment is None:
            parent_id = mlflow_client_full.create_experiment(parent_name)
        else:
            parent_id = experiment.experiment_id

        yield {
            "id": parent_id,
            "name": parent_name,
        }
    except ImportError:
        pytest.skip("MLflow not installed")


@pytest.fixture
def child_experiment(mlflow_client_full, parent_experiment):
    """Create a child experiment for nested experiment hierarchy."""
    try:
        import mlflow

        child_name = f"{parent_experiment['name']}_child"
        experiment = None
        try:
            experiment = mlflow_client_full.get_experiment_by_name(child_name)
        except Exception:
            pass

        if experiment is None:
            child_id = mlflow_client_full.create_experiment(child_name)
        else:
            child_id = experiment.experiment_id

        yield {
            "id": child_id,
            "name": child_name,
            "parent_id": parent_experiment["id"],
        }
    except ImportError:
        pytest.skip("MLflow not installed")


@pytest.fixture
def parent_run(mlflow_client_full, parent_experiment):
    """Create a parent run for nested run hierarchy."""
    try:
        import mlflow

        exp_id = parent_experiment["id"]
        run = mlflow_client_full.create_run(
            experiment_id=exp_id,
            tags={"run_type": "parent", "test_suite": "full_profile"},
        )

        yield {
            "id": run.info.run_id,
            "experiment_id": exp_id,
            "status": "RUNNING",
        }

        # Cleanup
        try:
            mlflow_client_full.set_terminated(run.info.run_id)
        except Exception:
            pass
    except ImportError:
        pytest.skip("MLflow not installed")


@pytest.fixture
def child_run(mlflow_client_full, parent_experiment, parent_run):
    """Create a child run within parent run for nested run testing."""
    try:
        import mlflow

        exp_id = parent_experiment["id"]
        run = mlflow_client_full.create_run(
            experiment_id=exp_id,
            parent_run_id=parent_run["id"],
            tags={"run_type": "child", "parent": parent_run["id"]},
        )

        yield {
            "id": run.info.run_id,
            "experiment_id": exp_id,
            "parent_run_id": parent_run["id"],
            "status": "RUNNING",
        }

        # Cleanup
        try:
            mlflow_client_full.set_terminated(run.info.run_id)
        except Exception:
            pass
    except ImportError:
        pytest.skip("MLflow not installed")


@pytest.fixture
def multi_metric_run(mlflow_client_full, parent_experiment):
    """Create a run for multi-metric tracking (100+ metrics)."""
    try:
        import mlflow

        exp_id = parent_experiment["id"]
        run = mlflow_client_full.create_run(
            experiment_id=exp_id,
            tags={"test_type": "multi_metric", "metric_count": "150"},
        )

        # Log 150 metrics
        for i in range(150):
            mlflow_client_full.log_metric(
                run.info.run_id, f"metric_{i:03d}", float(i) * 1.5, step=0
            )

        yield {
            "id": run.info.run_id,
            "experiment_id": exp_id,
            "metric_count": 150,
        }

        # Cleanup
        try:
            mlflow_client_full.set_terminated(run.info.run_id)
        except Exception:
            pass
    except ImportError:
        pytest.skip("MLflow not installed")


@pytest.fixture
def artifact_run(mlflow_client_full, parent_experiment, mlflow_temp_dir):
    """Create a run for artifact management testing."""
    try:
        import mlflow

        exp_id = parent_experiment["id"]
        run = mlflow_client_full.create_run(
            experiment_id=exp_id,
            tags={"test_type": "artifact", "artifact_count": "5"},
        )

        # Create some test artifacts
        artifacts_dir = mlflow_temp_dir / "test_artifacts"
        artifacts_dir.mkdir(exist_ok=True)

        for i in range(5):
            artifact_path = artifacts_dir / f"artifact_{i}.txt"
            artifact_path.write_text(f"Test artifact content {i}\n" * 100)

        # Log artifacts would happen in the test
        yield {
            "id": run.info.run_id,
            "experiment_id": exp_id,
            "artifacts_dir": str(artifacts_dir),
        }

        # Cleanup
        try:
            mlflow_client_full.set_terminated(run.info.run_id)
        except Exception:
            pass
    except ImportError:
        pytest.skip("MLflow not installed")


@pytest.fixture
def sweep_run_set(mlflow_client_full, parent_experiment):
    """Create multiple runs for hyperparameter sweep logging."""
    try:
        import mlflow

        exp_id = parent_experiment["id"]
        runs = []

        # Create 10 runs with different hyperparameters
        hyperparams = [
            {"lr": 0.001, "batch_size": 32, "epochs": 10},
            {"lr": 0.001, "batch_size": 64, "epochs": 10},
            {"lr": 0.001, "batch_size": 128, "epochs": 10},
            {"lr": 0.01, "batch_size": 32, "epochs": 10},
            {"lr": 0.01, "batch_size": 64, "epochs": 10},
            {"lr": 0.01, "batch_size": 128, "epochs": 10},
            {"lr": 0.1, "batch_size": 32, "epochs": 10},
            {"lr": 0.1, "batch_size": 64, "epochs": 10},
            {"lr": 0.1, "batch_size": 128, "epochs": 10},
            {"lr": 0.001, "batch_size": 32, "epochs": 20},
        ]

        for params in hyperparams:
            run = mlflow_client_full.create_run(
                experiment_id=exp_id,
                tags={"test_type": "hyperparameter_sweep"},
            )

            # Log hyperparameters
            for key, value in params.items():
                mlflow_client_full.log_param(run.info.run_id, key, value)

            # Log some dummy metrics
            accuracy = 0.85 + (params["lr"] * 0.1) - (params["batch_size"] / 1000)
            mlflow_client_full.log_metric(run.info.run_id, "accuracy", accuracy)

            runs.append(
                {
                    "id": run.info.run_id,
                    "experiment_id": exp_id,
                    "hyperparams": params,
                }
            )

        yield runs

        # Cleanup
        for run in runs:
            try:
                mlflow_client_full.set_terminated(run["id"])
            except Exception:
                pass
    except ImportError:
        pytest.skip("MLflow not installed")


@pytest.fixture
def distributed_run_set(mlflow_client_full, parent_experiment):
    """Create multiple runs for distributed logging testing."""
    try:
        import mlflow

        exp_id = parent_experiment["id"]
        runs = []

        # Create 5 runs simulating distributed training
        for i in range(5):
            run = mlflow_client_full.create_run(
                experiment_id=exp_id,
                tags={
                    "test_type": "distributed",
                    "rank": str(i),
                    "world_size": "5",
                },
            )

            # Log metrics from different ranks
            for step in range(10):
                metric_value = (i + 1) * (step + 1) * 0.1
                mlflow_client_full.log_metric(
                    run.info.run_id, f"rank_{i}_loss", metric_value, step=step
                )

            runs.append(
                {
                    "id": run.info.run_id,
                    "experiment_id": exp_id,
                    "rank": i,
                }
            )

        yield runs

        # Cleanup
        for run in runs:
            try:
                mlflow_client_full.set_terminated(run["id"])
            except Exception:
                pass
    except ImportError:
        pytest.skip("MLflow not installed")


@pytest.fixture
def model_registry_run(mlflow_client_full, parent_experiment):
    """Create a run for model registry testing."""
    try:
        import mlflow
        import tempfile
        from pathlib import Path

        exp_id = parent_experiment["id"]
        run = mlflow_client_full.create_run(
            experiment_id=exp_id,
            tags={"test_type": "model_registry"},
        )

        # Create a mock model artifact
        with tempfile.TemporaryDirectory() as tmpdir:
            model_dir = Path(tmpdir) / "model"
            model_dir.mkdir()
            (model_dir / "model.pkl").write_text("mock model data")
            (model_dir / "config.json").write_text(
                json.dumps({"framework": "sklearn"})
            )

            yield {
                "id": run.info.run_id,
                "experiment_id": exp_id,
                "model_dir": str(model_dir),
            }

        # Cleanup
        try:
            mlflow_client_full.set_terminated(run.info.run_id)
        except Exception:
            pass
    except ImportError:
        pytest.skip("MLflow not installed")


@pytest.fixture
def export_import_run(mlflow_client_full, parent_experiment):
    """Create a run for export/import testing."""
    try:
        import mlflow

        exp_id = parent_experiment["id"]
        run = mlflow_client_full.create_run(
            experiment_id=exp_id,
            tags={"test_type": "export_import"},
        )

        # Log some data for export
        mlflow_client_full.log_param(run.info.run_id, "param1", "value1")
        mlflow_client_full.log_metric(run.info.run_id, "metric1", 0.95)
        mlflow_client_full.log_metric(run.info.run_id, "metric1", 0.97, step=1)

        yield {
            "id": run.info.run_id,
            "experiment_id": exp_id,
            "data": {"params": {"param1": "value1"}, "metrics": {"metric1": 0.97}},
        }

        # Cleanup
        try:
            mlflow_client_full.set_terminated(run.info.run_id)
        except Exception:
            pass
    except ImportError:
        pytest.skip("MLflow not installed")
