"""Test fixtures for MLflow and wandb experiment tracking integration."""

from __future__ import annotations

import logging
import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator, Optional
from unittest.mock import MagicMock, patch

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


# Inference Pipeline Fixtures
@pytest.fixture
def model_config() -> dict[str, Any]:
    """Return configuration for the test model."""
    return {
        "model_name": "distilbert-base-uncased",
        "max_seq_length": 128,
        "batch_size": 8,
        "num_samples": 16,
    }


@pytest.fixture
def test_texts() -> list[str]:
    """Generate synthetic text samples for inference testing."""
    return [
        "The quick brown fox jumps over the lazy dog.",
        "Machine learning models require careful training and evaluation.",
        "Natural language processing is a complex field of AI.",
        "This is a test sentence for tokenization and inference.",
        "PyTorch provides excellent support for deep neural networks.",
        "Transformers have revolutionized the field of NLP.",
        "Text embeddings are useful for similarity matching.",
        "Model evaluation metrics help us understand performance.",
        "Batch processing improves inference throughput significantly.",
        "GPU acceleration can speed up tensor operations.",
        "Memory management is critical for large models.",
        "Distributed inference enables handling massive datasets.",
        "Token embeddings capture semantic information in text.",
        "Attention mechanisms allow models to focus on relevant parts.",
        "Gradual model loading prevents memory overflow issues.",
        "Performance profiling helps identify optimization opportunities.",
    ]


@pytest.fixture
def batch_test_texts() -> list[list[str]]:
    """Generate batches of text samples for batch inference testing."""
    texts = [
        "The quick brown fox jumps over the lazy dog.",
        "Machine learning models require careful training and evaluation.",
        "Natural language processing is a complex field of AI.",
        "This is a test sentence for tokenization and inference.",
        "PyTorch provides excellent support for deep neural networks.",
        "Transformers have revolutionized the field of NLP.",
        "Text embeddings are useful for similarity matching.",
        "Model evaluation metrics help us understand performance.",
    ]
    
    # Create batches
    batch_size = 4
    batches = [texts[i : i + batch_size] for i in range(0, len(texts), batch_size)]
    return batches


@pytest.fixture
def device_info() -> dict[str, Any]:
    """Get information about the available device."""
    info = {"cuda_available": False, "device": "cpu", "device_name": "CPU"}
    
    try:
        import torch
        if torch.cuda.is_available():
            info["cuda_available"] = True
            info["device"] = "cuda"
            info["device_name"] = torch.cuda.get_device_name(0)
            info["cuda_version"] = torch.version.cuda
    except Exception:
        pass
    
    return info


@pytest.fixture
def performance_tracker() -> Generator[dict[str, Any], None, None]:
    """Track performance metrics during inference."""
    
    metrics = {
        "inference_times_ms": [],
        "total_samples": 0,
        "total_time_sec": 0.0,
        "min_latency_ms": float("inf"),
        "max_latency_ms": 0.0,
        "mean_latency_ms": 0.0,
        "throughput_samples_per_sec": 0.0,
    }
    
    yield metrics


@pytest.fixture
def inference_test_config() -> dict[str, Any]:
    """Comprehensive configuration for inference pipeline tests."""
    def _cuda_available() -> bool:
        try:
            import torch
            return torch.cuda.is_available()
        except Exception:
            return False
    
    return {
        "model_name": "distilbert-base-uncased",
        "max_seq_length": 128,
        "batch_sizes": [1, 4, 8],
        "num_samples": 16,
        "device": "cuda" if _cuda_available() else "cpu",
        "timeout_seconds": 300,
        "latency_threshold_ms": 100.0,
        "memory_threshold_gb": 5.0,
    }
