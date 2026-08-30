"""Comprehensive tests for checkpointing and resume capability.

Tests cover:
- RNG/optimizer/scheduler state validation
- Checksum/hash verification
- Best-k retention enforcement
- Corruption auto-heal
"""

from __future__ import annotations

import hashlib
import json
import tempfile
import time
from pathlib import Path
from typing import Any

import pytest

pytest.importorskip("hypothesis")


pytest.importorskip("hypothesis", reason="hypothesis required for property tests")

from hypothesis import given, settings
from hypothesis import strategies as st

# --- RNG State Tests ---


class RNGState:
    """Random number generator state container."""

    def __init__(self, python_state: Any = None, numpy_state: Any = None, torch_state: Any = None):
        self.python_state = python_state
        self.numpy_state = numpy_state
        self.torch_state = torch_state
        self.timestamp = time.time()

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "python_state": self.python_state,
            "numpy_state": self.numpy_state,
            "torch_state": self.torch_state,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RNGState":
        """Deserialize from dictionary."""
        state = cls(
            python_state=data.get("python_state"),
            numpy_state=data.get("numpy_state"),
            torch_state=data.get("torch_state"),
        )
        state.timestamp = data.get("timestamp", time.time())
        return state

    def validate(self) -> list[str]:
        """Validate RNG state completeness."""
        errors = []
        if self.python_state is None:
            errors.append("Missing python_state")
        return errors


class TestRNGState:
    """Tests for RNG state management."""

    def test_create_rng_state(self):
        """Create RNG state."""
        state = RNGState(python_state=[1, 2, 3])
        assert state.python_state == [1, 2, 3]

    def test_serialize_rng_state(self):
        """Serialize RNG state to dict."""
        state = RNGState(python_state="test_state")
        data = state.to_dict()
        assert data["python_state"] == "test_state", "Data must not be empty"

    def test_deserialize_rng_state(self):
        """Deserialize RNG state from dict."""
        data = {"python_state": "test", "numpy_state": "np_test"}
        state = RNGState.from_dict(data)
        assert state.python_state == "test", "python_state is not valid"
        assert state.numpy_state == "np_test", "numpy_state is not valid"

    def test_validate_complete_state(self):
        """Complete state should pass validation."""
        state = RNGState(python_state=[1, 2, 3])
        errors = state.validate()
        assert len(errors) == 0, "Errors must not be empty"

    def test_validate_incomplete_state(self):
        """Incomplete state should report errors."""
        state = RNGState()
        errors = state.validate()
        assert len(errors) > 0, "Errors must not be empty"


# --- Optimizer State Tests ---


class OptimizerState:
    """Optimizer state container."""

    def __init__(self):
        self.state: dict[str, Any] = {}
        self.param_groups: list[dict[str, Any]] = []

    def add_param_group(self, group: dict[str, Any]) -> None:
        """Add parameter group."""
        self.param_groups.append(group)

    def save_state(self, key: str, value: Any) -> None:
        """Save optimizer state for a parameter."""
        self.state[key] = value

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {"state": self.state, "param_groups": self.param_groups}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OptimizerState":
        """Deserialize from dictionary."""
        opt = cls()
        opt.state = data.get("state", {})
        opt.param_groups = data.get("param_groups", [])
        return opt

    def validate(self) -> list[str]:
        """Validate optimizer state."""
        errors = []
        if not self.param_groups:
            errors.append("No param_groups defined")
        return errors


class TestOptimizerState:
    """Tests for optimizer state management."""

    def test_create_optimizer_state(self):
        """Create optimizer state."""
        state = OptimizerState()
        state.add_param_group({"lr": 0.001, "weight_decay": 0.01})
        assert len(state.param_groups) == 1, "Collection must not be empty"

    def test_save_state(self):
        """Save parameter state."""
        state = OptimizerState()
        state.save_state("param_0", {"step": 100, "exp_avg": [0.1, 0.2]})
        assert "param_0" in state.state, "Condition must be true"

    def test_serialize_optimizer(self):
        """Serialize optimizer state."""
        state = OptimizerState()
        state.add_param_group({"lr": 0.001})
        state.save_state("p0", {"step": 1})
        data = state.to_dict()
        assert "state" in data, "Data must not be empty"
        assert "param_groups" in data, "Data must not be empty"

    def test_deserialize_optimizer(self):
        """Deserialize optimizer state."""
        data = {"state": {"p0": {"step": 1}}, "param_groups": [{"lr": 0.001}]}
        state = OptimizerState.from_dict(data)
        assert state.state["p0"]["step"] == 1, "Condition must be true"


# --- Scheduler State Tests ---


class SchedulerState:
    """Learning rate scheduler state."""

    def __init__(self):
        self.last_epoch = 0
        self.base_lrs: list[float] = []
        self._step_count = 0

    def step(self) -> None:
        """Step scheduler."""
        self._step_count += 1
        self.last_epoch += 1

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "last_epoch": self.last_epoch,
            "base_lrs": self.base_lrs,
            "_step_count": self._step_count,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SchedulerState":
        """Deserialize from dictionary."""
        sched = cls()
        sched.last_epoch = data.get("last_epoch", 0)
        sched.base_lrs = data.get("base_lrs", [])
        sched._step_count = data.get("_step_count", 0)
        return sched


class TestSchedulerState:
    """Tests for scheduler state management."""

    def test_create_scheduler(self):
        """Create scheduler state."""
        sched = SchedulerState()
        sched.base_lrs = [0.01, 0.001]
        assert len(sched.base_lrs) == 2, "Collection must not be empty"

    def test_step_scheduler(self):
        """Step scheduler increments epoch."""
        sched = SchedulerState()
        sched.step()
        sched.step()
        assert sched.last_epoch == 2, "last_epoch is not valid"
        assert sched._step_count == 2, "Count must be greater than zero"

    def test_serialize_scheduler(self):
        """Serialize scheduler state."""
        sched = SchedulerState()
        sched.last_epoch = 5
        sched.base_lrs = [0.01]
        data = sched.to_dict()
        assert data["last_epoch"] == 5, "Data must not be empty"

    def test_deserialize_scheduler(self):
        """Deserialize scheduler state."""
        data = {"last_epoch": 10, "base_lrs": [0.001], "_step_count": 10}
        sched = SchedulerState.from_dict(data)
        assert sched.last_epoch == 10, "last_epoch is not valid"


# --- Checkpoint Checksum Tests ---


def compute_checkpoint_checksum(data: dict[str, Any]) -> str:
    """Compute checksum of checkpoint data."""
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class CheckpointValidator:
    """Validate checkpoint integrity."""

    def __init__(self):
        self.required_keys = ["epoch", "model_state", "optimizer_state"]

    def validate(self, checkpoint: dict[str, Any]) -> list[str]:
        """Validate checkpoint structure."""
        errors = []
        for key in self.required_keys:
            if key not in checkpoint:
                errors.append(f"Missing required key: {key}")
        return errors

    def verify_checksum(self, checkpoint: dict[str, Any], expected: str) -> bool:
        """Verify checkpoint checksum."""
        actual = compute_checkpoint_checksum(checkpoint)
        return actual == expected


class TestCheckpointChecksum:
    """Tests for checkpoint checksum validation."""

    def test_compute_checksum(self):
        """Compute checkpoint checksum."""
        data = {"epoch": 1, "loss": 0.5}
        checksum = compute_checkpoint_checksum(data)
        assert len(checksum) == 64, "Checksum must not be empty"

    def test_checksum_deterministic(self):
        """Checksum should be deterministic."""
        data = {"epoch": 1, "loss": 0.5}
        h1 = compute_checkpoint_checksum(data)
        h2 = compute_checkpoint_checksum(data)
        assert h1 == h2, "h1 is not valid"

    def test_different_data_different_checksum(self):
        """Different data should have different checksums."""
        h1 = compute_checkpoint_checksum({"epoch": 1})
        h2 = compute_checkpoint_checksum({"epoch": 2})
        assert h1 != h2, "h1 is not valid"

    def test_validator_valid(self):
        """Valid checkpoint passes validation."""
        validator = CheckpointValidator()
        checkpoint = {"epoch": 1, "model_state": {}, "optimizer_state": {}}
        errors = validator.validate(checkpoint)
        assert len(errors) == 0, "Errors must not be empty"

    def test_validator_missing_keys(self):
        """Missing keys should be reported."""
        validator = CheckpointValidator()
        checkpoint = {"epoch": 1}
        errors = validator.validate(checkpoint)
        assert len(errors) == 2, "Errors must not be empty"

    @given(st.dictionaries(st.text(min_size=1, max_size=10), st.integers()))
    @settings(max_examples=30)
    def test_checksum_deterministic_property(self, data: dict):
        """Property: checksum is deterministic."""
        h1 = compute_checkpoint_checksum(data)
        h2 = compute_checkpoint_checksum(data)
        assert h1 == h2, "h1 is not valid"


# --- Best-K Retention Tests ---


class BestKCheckpointManager:
    """Manage best-k checkpoint retention."""

    def __init__(self, k: int = 3, metric: str = "loss", mode: str = "min"):
        self.k = k
        self.metric = metric
        self.mode = mode
        self.checkpoints: list[dict[str, Any]] = []

    def add_checkpoint(self, path: str, metrics: dict[str, float]) -> bool:
        """Add checkpoint and return if it should be kept."""
        value = metrics.get(self.metric, float("inf") if self.mode == "min" else float("-inf"))
        self.checkpoints.append({"path": path, "value": value, "metrics": metrics})
        self._sort_checkpoints()
        return path in [c["path"] for c in self.checkpoints[: self.k]]

    def _sort_checkpoints(self) -> None:
        """Sort checkpoints by metric."""
        reverse = self.mode == "max"
        self.checkpoints.sort(key=lambda x: x["value"], reverse=reverse)

    def get_checkpoints_to_delete(self) -> list[str]:
        """Get checkpoints to delete."""
        if len(self.checkpoints) <= self.k:
            return []
        return [c["path"] for c in self.checkpoints[self.k :]]

    def get_best_checkpoint(self) -> str | None:
        """Get best checkpoint path."""
        if not self.checkpoints:
            return None
        return self.checkpoints[0]["path"]


class TestBestKRetention:
    """Tests for best-k checkpoint retention."""

    def test_keep_k_checkpoints(self):
        """Only k checkpoints should be kept."""
        manager = BestKCheckpointManager(k=3)
        for i in range(5):
            manager.add_checkpoint(f"ckpt_{i}", {"loss": float(i)})
        to_delete = manager.get_checkpoints_to_delete()
        assert len(to_delete) == 2, "To_delete must not be empty"

    def test_best_checkpoint_min(self):
        """Best checkpoint for min mode."""
        manager = BestKCheckpointManager(k=3, mode="min")
        manager.add_checkpoint("ckpt_1", {"loss": 0.5})
        manager.add_checkpoint("ckpt_2", {"loss": 0.3})
        manager.add_checkpoint("ckpt_3", {"loss": 0.7})
        assert manager.get_best_checkpoint() == "ckpt_2", "Condition must be true"

    def test_best_checkpoint_max(self):
        """Best checkpoint for max mode."""
        manager = BestKCheckpointManager(k=3, metric="accuracy", mode="max")
        manager.add_checkpoint("ckpt_1", {"accuracy": 0.8})
        manager.add_checkpoint("ckpt_2", {"accuracy": 0.9})
        manager.add_checkpoint("ckpt_3", {"accuracy": 0.7})
        assert manager.get_best_checkpoint() == "ckpt_2", "Condition must be true"


# --- Corruption Detection and Auto-Heal Tests ---


class CorruptionDetector:
    """Detect and handle checkpoint corruption."""

    def __init__(self):
        self.valid_magic = b"CKPT"

    def check_magic_bytes(self, data: bytes) -> bool:
        """Check magic bytes at start of checkpoint."""
        return data[:4] == self.valid_magic

    def detect_corruption(
        self, checkpoint: dict[str, Any], checksum: str | None = None
    ) -> list[str]:
        """Detect corruption in checkpoint."""
        issues = []

        # Check required structure
        if "epoch" not in checkpoint:
            issues.append("Missing epoch field")
        if "model_state" not in checkpoint:
            issues.append("Missing model_state")

        # Check checksum if provided
        if checksum:
            actual = compute_checkpoint_checksum(checkpoint)
            if actual != checksum:
                issues.append("Checksum mismatch")

        return issues


class AutoHealManager:
    """Auto-heal corrupted checkpoints."""

    def __init__(self, backup_dir: Path):
        self.backup_dir = backup_dir
        self.heal_history: list[dict[str, Any]] = []

    def find_backup(self, checkpoint_path: str) -> str | None:
        """Find backup for corrupted checkpoint."""
        backup_path = self.backup_dir / f"{Path(checkpoint_path).stem}.backup"
        if backup_path.exists():
            return str(backup_path)
        return None

    def heal(self, checkpoint_path: str, issues: list[str]) -> dict[str, Any]:
        """Attempt to heal corrupted checkpoint."""
        backup = self.find_backup(checkpoint_path)
        result = {
            "original": checkpoint_path,
            "issues": issues,
            "backup_found": backup is not None,
            "healed": backup is not None,
        }
        self.heal_history.append(result)
        return result


class TestCorruptionHandling:
    """Tests for corruption detection and healing."""

    def test_detect_missing_epoch(self):
        """Detect missing epoch field."""
        detector = CorruptionDetector()
        checkpoint = {"model_state": {}}
        issues = detector.detect_corruption(checkpoint)
        assert "Missing epoch field" in issues, "in is not valid"

    def test_detect_checksum_mismatch(self):
        """Detect checksum mismatch."""
        detector = CorruptionDetector()
        checkpoint = {"epoch": 1, "model_state": {}}
        issues = detector.detect_corruption(checkpoint, checksum="wrong_checksum")
        assert "Checksum mismatch" in issues, "in is not valid"

    def test_valid_checkpoint_no_issues(self):
        """Valid checkpoint should have no issues."""
        detector = CorruptionDetector()
        checkpoint = {"epoch": 1, "model_state": {}}
        checksum = compute_checkpoint_checksum(checkpoint)
        issues = detector.detect_corruption(checkpoint, checksum=checksum)
        assert len(issues) == 0, "Issues must not be empty"

    def test_auto_heal_with_backup(self):
        """Auto-heal should find backup."""
        with tempfile.TemporaryDirectory() as tmp:
            backup_dir = Path(tmp)
            backup_file = backup_dir / "ckpt_1.backup"
            backup_file.write_text("backup data")

            healer = AutoHealManager(backup_dir)
            result = healer.heal("ckpt_1.pt", ["corruption"])
            assert result["backup_found"], "Result must not be empty"
            assert result["healed"], "Result must not be empty"


# --- Checkpoint Manifest Tests ---


class CheckpointManifest:
    """Manifest tracking all checkpoints."""

    def __init__(self):
        self.entries: dict[str, dict[str, Any]] = {}

    def add_entry(self, path: str, epoch: int, checksum: str, metrics: dict[str, float]) -> None:
        """Add checkpoint to manifest."""
        self.entries[path] = {
            "epoch": epoch,
            "checksum": checksum,
            "metrics": metrics,
            "created_at": time.time(),
        }

    def get_entry(self, path: str) -> dict[str, Any] | None:
        """Get manifest entry."""
        return self.entries.get(path)

    def list_by_epoch(self, epoch: int) -> list[str]:
        """List checkpoints for epoch."""
        return [p for p, e in self.entries.items() if e["epoch"] == epoch]

    def to_json(self) -> str:
        """Export manifest as JSON."""
        return json.dumps(self.entries, indent=2)


class TestCheckpointManifest:
    """Tests for checkpoint manifest."""

    def test_add_entry(self):
        """Add checkpoint to manifest."""
        manifest = CheckpointManifest()
        manifest.add_entry("ckpt_1.pt", epoch=1, checksum="abc123", metrics={"loss": 0.5})
        entry = manifest.get_entry("ckpt_1.pt")
        assert entry is not None, "entry must be initialized"
        assert entry["epoch"] == 1, "Condition must be true"

    def test_list_by_epoch(self):
        """List checkpoints by epoch."""
        manifest = CheckpointManifest()
        manifest.add_entry("ckpt_1.pt", epoch=1, checksum="abc", metrics={})
        manifest.add_entry("ckpt_2.pt", epoch=1, checksum="def", metrics={})
        manifest.add_entry("ckpt_3.pt", epoch=2, checksum="ghi", metrics={})
        epoch_1_ckpts = manifest.list_by_epoch(1)
        assert len(epoch_1_ckpts) == 2, "Epoch_1_ckpts must not be empty"

    def test_export_json(self):
        """Export manifest as JSON."""
        manifest = CheckpointManifest()
        manifest.add_entry("ckpt_1.pt", epoch=1, checksum="abc", metrics={})
        output = manifest.to_json()
        parsed = json.loads(output)
        assert "ckpt_1.pt" in parsed, "Condition must be true"
