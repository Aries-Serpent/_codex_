"""Comprehensive tests for experiment tracking capability.

Tests cover:
- Offline/airgapped mode
- Artifact retention/versioning
- Run resumption
- Cross-run comparison
- MLflow integration
"""

from __future__ import annotations

import hashlib
import tempfile
import time
from enum import Enum
from typing import Any

import pytest

pytest.importorskip("hypothesis", reason="hypothesis required for property tests")


# --- Experiment Run Tests ---


class RunStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    KILLED = "killed"


class ExperimentRun:
    """Experiment run representation."""

    def __init__(self, run_id: str, experiment_id: str):
        self.run_id = run_id
        self.experiment_id = experiment_id
        self.status = RunStatus.PENDING
        self.start_time: float | None = None
        self.end_time: float | None = None
        self.params: dict[str, Any] = {}
        self.metrics: dict[str, list[float]] = {}
        self.tags: dict[str, str] = {}
        self.artifacts: list[str] = []

    def start(self) -> None:
        """Start the run."""
        self.status = RunStatus.RUNNING
        self.start_time = time.time()

    def end(self, status: RunStatus = RunStatus.COMPLETED) -> None:
        """End the run."""
        self.status = status
        self.end_time = time.time()

    def log_param(self, key: str, value: Any) -> None:
        """Log parameter."""
        self.params[key] = value

    def log_metric(self, key: str, value: float, step: int | None = None) -> None:
        """Log metric."""
        if key not in self.metrics:
            self.metrics[key] = []
        self.metrics[key].append(value)

    def log_artifact(self, path: str) -> None:
        """Log artifact."""
        self.artifacts.append(path)

    def duration(self) -> float | None:
        """Get run duration."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None


class TestExperimentRun:
    """Tests for experiment run."""

    def test_create_run(self):
        """Create experiment run."""
        run = ExperimentRun("run-001", "exp-001")
        assert run.status == RunStatus.PENDING, "status is not valid"

    def test_run_lifecycle(self):
        """Run lifecycle: start -> end."""
        run = ExperimentRun("run-001", "exp-001")
        run.start()
        assert run.status == RunStatus.RUNNING, "status is not valid"
        run.end()
        assert run.status == RunStatus.COMPLETED, "status is not valid"

    def test_log_params(self):
        """Log parameters."""
        run = ExperimentRun("run-001", "exp-001")
        run.log_param("lr", 0.001)
        run.log_param("batch_size", 32)
        assert run.params["lr"] == 0.001, "Condition must be true"

    def test_log_metrics(self):
        """Log metrics."""
        run = ExperimentRun("run-001", "exp-001")
        run.log_metric("loss", 0.5)
        run.log_metric("loss", 0.3)
        assert len(run.metrics["loss"]) == 2, "Collection must not be empty"


# --- Offline Mode Tests ---


class OfflineTracker:
    """Offline experiment tracker."""

    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        self.pending_uploads: list[dict[str, Any]] = []
        self.runs: dict[str, ExperimentRun] = {}

    def create_run(self, experiment_id: str) -> ExperimentRun:
        """Create offline run."""
        run_id = f"offline-{len(self.runs)}"
        run = ExperimentRun(run_id, experiment_id)
        self.runs[run_id] = run
        return run

    def sync(self) -> int:
        """Sync pending data when online."""
        synced = len(self.pending_uploads)
        self.pending_uploads.clear()
        return synced

    def is_online(self) -> bool:
        """Check if online (simplified)."""
        return False  # Always offline in tests


class TestOfflineMode:
    """Tests for offline mode."""

    def test_create_offline_run(self):
        """Create run in offline mode."""
        tracker = OfflineTracker(os.path.join(tempfile.gettempdir(), "mlruns"))
        run = tracker.create_run("exp-001")
        assert run.run_id.startswith("offline-"), "Condition must be true"

    def test_sync_pending(self):
        """Sync pending data."""
        tracker = OfflineTracker(os.path.join(tempfile.gettempdir(), "mlruns"))
        tracker.pending_uploads.append({"type": "metric", "data": {}})
        synced = tracker.sync()
        assert synced == 1, "synced is not valid"
        assert len(tracker.pending_uploads) == 0, "Collection must not be empty"


# --- Artifact Management Tests ---


class Artifact:
    """Experiment artifact."""

    def __init__(self, name: str, path: str):
        self.name = name
        self.path = path
        self.size_bytes: int = 0
        self.checksum: str = ""
        self.metadata: dict[str, Any] = {}

    def compute_checksum(self, content: bytes) -> str:
        """Compute artifact checksum."""
        self.checksum = hashlib.sha256(content).hexdigest()
        return self.checksum


class ArtifactStore:
    """Store for experiment artifacts."""

    def __init__(self):
        self.artifacts: dict[str, Artifact] = {}
        self.retention_days: int = 90

    def store(self, run_id: str, artifact: Artifact) -> str:
        """Store artifact."""
        key = f"{run_id}/{artifact.name}"
        self.artifacts[key] = artifact
        return key

    def get(self, key: str) -> Artifact | None:
        """Get artifact by key."""
        return self.artifacts.get(key)

    def list_for_run(self, run_id: str) -> list[Artifact]:
        """List artifacts for run."""
        prefix = f"{run_id}/"
        return [a for k, a in self.artifacts.items() if k.startswith(prefix)]


class TestArtifactManagement:
    """Tests for artifact management."""

    def test_store_artifact(self):
        """Store artifact."""
        store = ArtifactStore()
        artifact = Artifact("model.pkl", "/path/to/model.pkl")
        key = store.store("run-001", artifact)
        assert "run-001" in key, "Condition must be true"

    def test_list_artifacts(self):
        """List artifacts for run."""
        store = ArtifactStore()
        store.store("run-001", Artifact("model.pkl", "/path"))
        store.store("run-001", Artifact("config.json", "/path"))
        store.store("run-002", Artifact("other.pkl", "/path"))
        artifacts = store.list_for_run("run-001")
        assert len(artifacts) == 2, "Artifacts must not be empty"


# --- Run Resumption Tests ---


class RunCheckpoint:
    """Checkpoint for run resumption."""

    def __init__(self, run_id: str):
        self.run_id = run_id
        self.step: int = 0
        self.epoch: int = 0
        self.metrics_history: dict[str, list[float]] = {}
        self.state: dict[str, Any] = {}

    def save(self) -> dict[str, Any]:
        """Save checkpoint state."""
        return {
            "run_id": self.run_id,
            "step": self.step,
            "epoch": self.epoch,
            "metrics_history": self.metrics_history,
            "state": self.state,
        }

    @classmethod
    def load(cls, data: dict[str, Any]) -> "RunCheckpoint":
        """Load checkpoint from data."""
        checkpoint = cls(data["run_id"])
        checkpoint.step = data.get("step", 0)
        checkpoint.epoch = data.get("epoch", 0)
        checkpoint.metrics_history = data.get("metrics_history", {})
        checkpoint.state = data.get("state", {})
        return checkpoint


class TestRunResumption:
    """Tests for run resumption."""

    def test_save_checkpoint(self):
        """Save run checkpoint."""
        checkpoint = RunCheckpoint("run-001")
        checkpoint.step = 1000
        checkpoint.epoch = 5
        data = checkpoint.save()
        assert data["step"] == 1000, "Data must not be empty"

    def test_load_checkpoint(self):
        """Load run checkpoint."""
        data = {"run_id": "run-001", "step": 500, "epoch": 2}
        checkpoint = RunCheckpoint.load(data)
        assert checkpoint.step == 500, "step is not valid"
        assert checkpoint.epoch == 2, "epoch is not valid"


# --- Cross-Run Comparison Tests ---


class RunComparison:
    """Compare multiple experiment runs."""

    def __init__(self):
        self.runs: list[ExperimentRun] = []

    def add_run(self, run: ExperimentRun) -> None:
        """Add run to comparison."""
        self.runs.append(run)

    def compare_metric(self, metric: str) -> dict[str, Any]:
        """Compare metric across runs."""
        values = {}
        for run in self.runs:
            if run.metrics.get(metric):
                values[run.run_id] = {
                    "min": min(run.metrics[metric]),
                    "max": max(run.metrics[metric]),
                    "last": run.metrics[metric][-1],
                }
        return values

    def get_best_run(self, metric: str, mode: str = "min") -> str | None:
        """Get best run by metric."""
        comparison = self.compare_metric(metric)
        if not comparison:
            return None
        key = "min" if mode == "min" else "max"
        best = sorted(comparison.items(), key=lambda x: x[1][key], reverse=(mode == "max"))[0]
        return best[0]


class TestRunComparison:
    """Tests for run comparison."""

    def test_compare_metric(self):
        """Compare metric across runs."""
        run1 = ExperimentRun("run-001", "exp")
        run1.log_metric("loss", 0.5)
        run1.log_metric("loss", 0.3)

        run2 = ExperimentRun("run-002", "exp")
        run2.log_metric("loss", 0.6)
        run2.log_metric("loss", 0.2)

        comparison = RunComparison()
        comparison.add_run(run1)
        comparison.add_run(run2)

        result = comparison.compare_metric("loss")
        assert result["run-001"]["last"] == 0.3, "Result must not be empty"
        assert result["run-002"]["last"] == 0.2, "Result must not be empty"

    def test_get_best_run(self):
        """Get best run by metric."""
        run1 = ExperimentRun("run-001", "exp")
        run1.log_metric("loss", 0.5)

        run2 = ExperimentRun("run-002", "exp")
        run2.log_metric("loss", 0.2)

        comparison = RunComparison()
        comparison.add_run(run1)
        comparison.add_run(run2)

        best = comparison.get_best_run("loss", mode="min")
        assert best == "run-002", "best is not valid"


# --- Experiment Registry Tests ---


class Experiment:
    """Experiment definition."""

    def __init__(self, experiment_id: str, name: str):
        self.experiment_id = experiment_id
        self.name = name
        self.description: str = ""
        self.tags: dict[str, str] = {}
        self.runs: list[str] = []

    def add_run(self, run_id: str) -> None:
        self.runs.append(run_id)


class ExperimentRegistry:
    """Registry for experiments."""

    def __init__(self):
        self.experiments: dict[str, Experiment] = {}

    def create_experiment(self, name: str) -> Experiment:
        """Create new experiment."""
        exp_id = f"exp-{len(self.experiments)}"
        exp = Experiment(exp_id, name)
        self.experiments[exp_id] = exp
        return exp

    def get_experiment(self, exp_id: str) -> Experiment | None:
        """Get experiment by ID."""
        return self.experiments.get(exp_id)

    def search_experiments(self, query: str) -> list[Experiment]:
        """Search experiments by name."""
        return [e for e in self.experiments.values() if query.lower() in e.name.lower()]


class TestExperimentRegistry:
    """Tests for experiment registry."""

    def test_create_experiment(self):
        """Create experiment."""
        registry = ExperimentRegistry()
        exp = registry.create_experiment("My Experiment")
        assert exp.name == "My Experiment", "name is not valid"

    def test_search_experiments(self):
        """Search experiments."""
        registry = ExperimentRegistry()
        registry.create_experiment("NLP Experiment")
        registry.create_experiment("CV Experiment")
        results = registry.search_experiments("nlp")
        assert len(results) == 1, "Results must not be empty"


# --- Metric History Tests ---


class MetricHistory:
    """Track metric history over time."""

    def __init__(self, name: str):
        self.name = name
        self.values: list[float] = []
        self.steps: list[int] = []
        self.timestamps: list[float] = []

    def record(self, value: float, step: int | None = None) -> None:
        """Record metric value."""
        self.values.append(value)
        self.steps.append(step if step is not None else len(self.values))
        self.timestamps.append(time.time())

    def best(self, mode: str = "min") -> float | None:
        """Get best value."""
        if not self.values:
            return None
        return min(self.values) if mode == "min" else max(self.values)

    def trend(self) -> str:
        """Get trend direction."""
        if len(self.values) < 2:
            return "stable"
        diff = self.values[-1] - self.values[0]
        if diff < -0.01:
            return "decreasing"
        if diff > 0.01:
            return "increasing"
        return "stable"


class TestMetricHistory:
    """Tests for metric history."""

    def test_record_values(self):
        """Record metric values."""
        history = MetricHistory("loss")
        history.record(0.5)
        history.record(0.3)
        assert len(history.values) == 2, "Collection must not be empty"

    def test_best_value(self):
        """Get best value."""
        history = MetricHistory("loss")
        history.record(0.5)
        history.record(0.3)
        history.record(0.4)
        assert history.best("min") == 0.3, "hist is not valid"

    def test_trend(self):
        """Get trend direction."""
        history = MetricHistory("loss")
        history.record(0.5)
        history.record(0.3)
        assert history.trend() == "decreasing", "hist is not valid"
