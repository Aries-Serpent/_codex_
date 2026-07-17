"""Test fixtures for MLflow and wandb experiment tracking integration."""

from __future__ import annotations

import logging
import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional
from unittest.mock import patch

import pytest

logger = logging.getLogger(__name__)


@pytest.fixture
def temp_mlflow_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for MLflow artifacts and runs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir)
        (path / "mlruns").mkdir(exist_ok=True)
        (path / "artifacts").mkdir(exist_ok=True)
        yield path


@pytest.fixture
def mlflow_tracking_uri(temp_mlflow_dir: Path) -> str:
    """Get SQLite-based tracking URI for testing."""
    db_path = temp_mlflow_dir / "mlruns" / "mlruns.db"
    uri = f"sqlite:///{db_path}"
    return uri


@pytest.fixture
def mlflow_client(mlflow_tracking_uri: str):
    """Create MLflow client for testing."""
    try:
        import mlflow
        from mlflow.tracking import MlflowClient

        mlflow.set_tracking_uri(mlflow_tracking_uri)
        client = MlflowClient(tracking_uri=mlflow_tracking_uri)
        yield client
    except ImportError:
        pytest.skip("MLflow not installed")


@pytest.fixture
def mlflow_experiment(mlflow_client):
    """Create an MLflow experiment for testing."""
    try:
        import mlflow

        experiment_name = "test_experiment_integration"
        # Check if experiment exists
        experiment = None
        try:
            experiment = mlflow_client.get_experiment_by_name(experiment_name)
        except Exception:
            pass

        if experiment is None:
            exp_id = mlflow_client.create_experiment(experiment_name)
        else:
            exp_id = experiment.experiment_id

        yield {
            "id": exp_id,
            "name": experiment_name,
            "tracking_uri": mlflow_client.tracking_uri,
        }
    except ImportError:
        pytest.skip("MLflow not installed")


@pytest.fixture
def mlflow_run(mlflow_client, mlflow_experiment):
    """Create an MLflow run for testing."""
    try:
        import mlflow

        exp_id = mlflow_experiment["id"]
        run = mlflow_client.create_run(experiment_id=exp_id)

        yield {
            "id": run.info.run_id,
            "experiment_id": exp_id,
            "status": "RUNNING",
        }

        # Cleanup: end the run
        try:
            mlflow_client.set_terminated(run.info.run_id)
        except Exception:
            pass
    except ImportError:
        pytest.skip("MLflow not installed")


@pytest.fixture
def wandb_config() -> dict:
    """Get wandb configuration for testing."""
    return {
        "project": "codex-test",
        "entity": None,
        "mode": "offline",
        "dir": None,
    }


@pytest.fixture
def wandb_mock():
    """Create a mock wandb module for testing."""

    class MockRun:
        """Mock wandb Run object."""

        def __init__(self):
            self.id = "mock_run_id"
            self.name = "mock_run"
            self.state = "running"
            self.config = {}
            self.summary = {}
            self.log_frequency = 0
            self.log_count = 0

        def log(self, data: dict, step: Optional[int] = None, commit: bool = True):
            """Mock log method."""
            self.summary.update(data)
            self.log_count += 1

        def finish(self, exit_code: int = 0):
            """Mock finish method."""
            self.state = "finished"

    class MockWandB:
        """Mock wandb module."""

        def __init__(self):
            self.current_run = None

        def init(self, **kwargs):
            """Mock init method."""
            self.current_run = MockRun()
            self.current_run.config = kwargs
            return self.current_run

        def log(self, data: dict, step: Optional[int] = None, commit: bool = True):
            """Mock log method."""
            if self.current_run:
                self.current_run.log(data, step, commit)

        def finish(self, exit_code: int = 0):
            """Mock finish method."""
            if self.current_run:
                self.current_run.finish(exit_code)

        def config(self):
            """Mock config property."""
            return self.current_run.config if self.current_run else {}

    return MockWandB()


@pytest.fixture
def mlflow_tracker_instance(mlflow_tracking_uri: str):
    """Create an instance of MLflowTracker for testing."""
    try:
        from codex_ml.tracking.mlflow_wrapper import MLflowTracker

        tracker = MLflowTracker(
            enabled=True,
            tracking_uri=mlflow_tracking_uri,
            experiment_name="integration_test",
            run_name="test_run",
        )
        yield tracker

        # Cleanup
        try:
            if tracker._active:
                tracker.end_run()
        except Exception:
            pass
    except ImportError:
        pytest.skip("codex_ml.tracking.mlflow_wrapper not available")


@pytest.fixture
def wandb_logger_instance(wandb_mock):
    """Create an instance of WandBLogger for testing."""
    try:
        from codex_ml.utils.wandb_logger import WandBLogger

        # Patch wandb module
        with patch.dict("sys.modules", {"wandb": wandb_mock}):
            logger = WandBLogger(
                project="test_project",
                name="test_run",
                config={"learning_rate": 0.001, "batch_size": 32},
            )
            yield logger
    except ImportError:
        pytest.skip("codex_ml.utils.wandb_logger not available")


@contextmanager
def mock_mlflow_tracking_context(tracking_uri: str):
    """Context manager for mocking MLflow tracking configuration."""
    old_uri = os.environ.get("MLFLOW_TRACKING_URI")
    try:
        os.environ["MLFLOW_TRACKING_URI"] = tracking_uri
        yield
    finally:
        if old_uri is not None:
            os.environ["MLFLOW_TRACKING_URI"] = old_uri
        else:
            os.environ.pop("MLFLOW_TRACKING_URI", None)


@contextmanager
def mock_wandb_tracking_context(mode: str = "offline"):
    """Context manager for mocking wandb tracking configuration."""
    old_mode = os.environ.get("WANDB_MODE")
    old_disabled = os.environ.get("WANDB_DISABLED")
    try:
        os.environ["WANDB_MODE"] = mode
        os.environ.pop("WANDB_DISABLED", None)
        yield
    finally:
        if old_mode is not None:
            os.environ["WANDB_MODE"] = old_mode
        else:
            os.environ.pop("WANDB_MODE", None)
        if old_disabled is not None:
            os.environ["WANDB_DISABLED"] = old_disabled
        else:
            os.environ.pop("WANDB_DISABLED", None)
