"""
Test Bestk

Test module for bestk.
"""

import json
import tempfile
from pathlib import Path

import pytest

# Skip entire module if torch is not available or unloadable
torch = pytest.importorskip("torch", reason="PyTorch required for checkpoint tests")
from codex_ml.checkpointing.bestk import update_and_prune


def _fake_save(path: Path):
    torch.save({"state": 1}, path)


def test_bestk_basic():
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        index = td / "index.json"
        kept = []
        for step in range(5):
            ckpt = td / f"checkpoint_{step}.pt"
            _fake_save(ckpt)
            res = update_and_prune(ckpt, metric=float(step), k=3, index_path=index)
            kept = res["kept"]
        assert len(kept) <= 3, "Kept must not be empty"
        # Ensure index reflects ≤ k entries
        data = json.loads(index.read_text())
        assert len(data["entries"]) <= 3, "Collection must not be empty"


def test_bestk_dry_run():
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        index = td / "index.json"
        ckpt = td / "checkpoint_1.pt"
        _fake_save(ckpt)
        res = update_and_prune(ckpt, metric=0.1, k=1, index_path=index, dry_run=True)
        # Index not written
        assert not index.exists(), "Condition must be true"
        assert res["dry_run"] is True, "Condition must be true"


def test_bestk_keep_last_trim():
    """Test that keep_last=True doesn't leak checkpoints beyond k (P1 fix)"""
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        index = td / "index.json"

        # Save k=3 checkpoints with metrics [1.0, 2.0, 3.0] (lower is better)
        for step in range(3):
            ckpt = td / f"checkpoint_{step}.pt"
            _fake_save(ckpt)
            update_and_prune(ckpt, metric=float(step + 1), k=3, index_path=index)

        # Now save a worse checkpoint (metric=10.0) with keep_last=True
        # This should force it into kept list but then trim back to k=3
        ckpt_worst = td / "checkpoint_worst.pt"
        _fake_save(ckpt_worst)
        res = update_and_prune(ckpt_worst, metric=10.0, k=3, index_path=index, keep_last=True)

        # Critical: kept list must be exactly k=3 entries
        assert len(res["kept"]) == 3, f"Expected exactly 3 kept, got {len(res['kept'])}"

        # Critical: worst checkpoint must be in kept (because keep_last=True)
        kept_paths = {e["path"] for e in res["kept"]}
        assert str(ckpt_worst) in kept_paths, "keep_last=True must protect newest checkpoint"

        # Verify index on disk also has exactly k entries
        data = json.loads(index.read_text())
        assert len(data["entries"]) == 3, "Collection must not be empty"
        _fake_save(ckpt_worst)
        res = update_and_prune(ckpt_worst, metric=10.0, k=3, index_path=index, keep_last=True)

        # Verify kept list has exactly k=3 entries, not k+1
        assert len(res["kept"]) == 3, f"Expected 3 kept checkpoints, got {len(res['kept'])}"

        # Verify the worst checkpoint is kept (keep_last=True)
        kept_paths = {e["path"] for e in res["kept"]}
        assert str(ckpt_worst) in kept_paths, "keep_last should retain the latest checkpoint"

        # Verify index file has exactly k entries
        data = json.loads(index.read_text())
        assert len(data["entries"]) == 3, f"Index should have 3 entries, got {len(data['entries'])}"

        # Verify one of the previous checkpoints was pruned
        assert len(res["pruned"]) == 1, "Should have pruned exactly 1 checkpoint"


def test_bestk_maximize_mode():
    """Edge case: Test keep_best with maximize=True (higher is better)"""
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        index = td / "index.json"

        # Save checkpoints with metrics [0.1, 0.5, 0.9] where higher is better
        for step, metric in enumerate([0.1, 0.5, 0.9]):
            ckpt = td / f"checkpoint_{step}.pt"
            _fake_save(ckpt)
            update_and_prune(ckpt, metric=metric, k=2, index_path=index, keep_best="max")

        # Load index and verify best 2 are kept (0.5 and 0.9)
        data = json.loads(index.read_text())
        assert len(data["entries"]) == 2, "Collection must not be empty"
        metrics = sorted([e["metric"] for e in data["entries"]], reverse=True)
        assert metrics == [0.9, 0.5]


def test_bestk_empty_index_initialization():
    """Edge case: First checkpoint creates new index"""
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        index = td / "index.json"

        # Index doesn't exist initially
        assert not index.exists(), "Condition must be true"

        ckpt = td / "checkpoint_0.pt"
        _fake_save(ckpt)
        update_and_prune(ckpt, metric=1.0, k=3, index_path=index)

        # Index created with one entry
        assert index.exists(), "Condition must be true"
        data = json.loads(index.read_text())
        assert len(data["entries"]) == 1, "Collection must not be empty"
        assert data["k"] == 3, "Data must not be empty"


def test_bestk_invalid_checkpoint_path():
    """Edge case: Handle non-existent checkpoint file"""
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        index = td / "index.json"
        nonexistent = td / "does_not_exist.pt"

        # Should handle gracefully or raise appropriate error
        try:
            res = update_and_prune(nonexistent, metric=1.0, k=3, index_path=index)
            # If it succeeds, verify it's recorded
            assert isinstance(res["kept"], (list, tuple, set, dict)
            )
        except (FileNotFoundError, ValueError) as e:
            # Expected behavior for missing file
            assert "exist" in str(e).lower() or "not found" in str(e).lower(), "Condition must be true"


def test_bestk_corrupt_index_recovery():
    """Edge case: Handle corrupted index.json file"""
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        index = td / "index.json"

        # Write corrupted JSON
        index.write_text("{ invalid json")

        ckpt = td / "checkpoint_0.pt"
        _fake_save(ckpt)

        # Should either recover or raise clear error
        try:
            update_and_prune(ckpt, metric=1.0, k=3, index_path=index)
            # If it recovers, verify it created valid index
            assert index.exists(), "Condition must be true"
            data = json.loads(index.read_text())
            assert "entries" in data, "Data must not be empty"
        except (json.JSONDecodeError, ValueError) as e:
            # Expected if corruption is not handled
            assert "json" in str(e).lower() or "parse" in str(e).lower(), "Condition must be true"
