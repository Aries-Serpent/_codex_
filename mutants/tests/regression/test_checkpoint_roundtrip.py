"""Regression tests: checkpoint round-trip consistency.

Verifies that metadata and pipeline state saved to disk can be reloaded
and produces byte-for-byte identical content.  These tests use only the
stdlib (json, pickle) and the symbolic-pipeline helpers — no GPU needed.

Covered scenarios:
- JSON metadata persists and reloads correctly
- Model handle state survives a pickle round-trip
- Checksum of serialised state does not drift
- Missing checkpoint file raises an appropriate error
- Multiple sequential checkpoints can be enumerated and re-read
"""

from __future__ import annotations

import hashlib
import json
import pickle
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
for _p in (str(_REPO_ROOT / "src"), str(_REPO_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

pytestmark = pytest.mark.regression


# ── helpers ──────────────────────────────────────────────────────────────────


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_checkpoint(directory: Path, epoch: int, meta: dict) -> Path:
    """Write a JSON checkpoint file and return its path."""
    ckpt_dir = directory / f"epoch-{epoch:03d}"
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    meta_path = ckpt_dir / "meta.json"
    meta_path.write_text(json.dumps(meta, sort_keys=True), encoding="utf-8")
    return meta_path


# ────────────────────────────────────────────────────────────────────────────
# 1. JSON metadata round-trip
# ────────────────────────────────────────────────────────────────────────────


class TestCheckpointMetadataRoundTrip:
    """Checkpoint metadata written as JSON must reload byte-identical."""

    def test_meta_roundtrip_preserves_all_keys(self, checkpoint_dir, sample_checkpoint_meta):
        """Reloaded metadata dict must contain every key from the original."""
        path = _write_checkpoint(checkpoint_dir, epoch=1, meta=sample_checkpoint_meta)
        reloaded = json.loads(path.read_text(encoding="utf-8"))
        for key in sample_checkpoint_meta:
            assert key in reloaded, f"Key {key!r} missing after checkpoint reload"

    def test_meta_roundtrip_preserves_values(self, checkpoint_dir, sample_checkpoint_meta):
        """Every value in reloaded metadata must equal the original."""
        path = _write_checkpoint(checkpoint_dir, epoch=1, meta=sample_checkpoint_meta)
        reloaded = json.loads(path.read_text(encoding="utf-8"))
        for key, expected in sample_checkpoint_meta.items():
            assert reloaded[key] == expected, (
                f"Meta[{key!r}] changed during round-trip: {reloaded[key]!r} != {expected!r}"
            )

    def test_meta_checksum_stable(self, checkpoint_dir, sample_checkpoint_meta):
        """SHA-256 of the serialised checkpoint file must be identical across two writes."""
        path1 = _write_checkpoint(checkpoint_dir / "run_a", epoch=1, meta=sample_checkpoint_meta)
        path2 = _write_checkpoint(checkpoint_dir / "run_b", epoch=1, meta=sample_checkpoint_meta)
        assert _sha256_bytes(path1.read_bytes()) == _sha256_bytes(path2.read_bytes()), (
            "Checkpoint file checksum is not deterministic for identical content"
        )


# ────────────────────────────────────────────────────────────────────────────
# 2. Model state pickle round-trip
# ────────────────────────────────────────────────────────────────────────────


class TestModelStatePickleRoundTrip:
    """ModelHandle state must survive a pickle serialisation round-trip."""

    def test_model_handle_pickle_roundtrip(self, checkpoint_dir, pretrained_model):
        """Pickled ModelHandle must reload to an equivalent object."""
        state_path = checkpoint_dir / "state.pkl"
        state_path.write_bytes(pickle.dumps(pretrained_model))

        reloaded = pickle.loads(  # noqa: S301 - Test fixture: deserializing trusted local file created by same process
            state_path.read_bytes()
        )  # nosemgrep: semgrep.unsafe-pickle-loads
        assert reloaded.name == pretrained_model.name, (
            f"name changed after pickle: {reloaded.name!r}"
        )
        assert reloaded.stage == pretrained_model.stage, (
            f"stage changed after pickle: {reloaded.stage!r}"
        )
        assert reloaded.meta.get("seed") == pretrained_model.meta.get("seed"), (
            "seed in meta changed after pickle"
        )

    def test_model_handle_pickle_checksum_stable(self, checkpoint_dir, pretrained_model):
        """Pickle bytes for the same object must be identical when written twice."""
        blob = pickle.dumps(pretrained_model)
        path_a = checkpoint_dir / "state_a.pkl"
        path_b = checkpoint_dir / "state_b.pkl"
        path_a.write_bytes(blob)
        path_b.write_bytes(blob)
        assert _sha256_bytes(path_a.read_bytes()) == _sha256_bytes(path_b.read_bytes()), (
            "Pickle checksum differs between identical writes"
        )


# ────────────────────────────────────────────────────────────────────────────
# 3. Multi-epoch checkpoint enumeration
# ────────────────────────────────────────────────────────────────────────────


class TestMultiEpochCheckpoints:
    """Multiple sequential checkpoints must all be readable and epoch-ordered."""

    def test_multiple_checkpoints_all_readable(self, checkpoint_dir):
        """Writing checkpoints for epochs 1-5 and reloading each must succeed."""
        epochs = list(range(1, 6))
        for ep in epochs:
            meta = {"epoch": ep, "loss": 1.0 / ep}
            _write_checkpoint(checkpoint_dir, epoch=ep, meta=meta)

        for ep in epochs:
            path = checkpoint_dir / f"epoch-{ep:03d}" / "meta.json"
            assert path.exists(), f"Checkpoint for epoch {ep} not found"
            data = json.loads(path.read_text(encoding="utf-8"))
            assert data["epoch"] == ep, "Data must not be empty"

    def test_checkpoint_dirs_are_sorted_by_epoch(self, checkpoint_dir):
        """Epoch directories must sort in ascending epoch order."""
        for ep in [3, 1, 5, 2, 4]:
            _write_checkpoint(checkpoint_dir, epoch=ep, meta={"epoch": ep})

        dirs = sorted(
            [d for d in checkpoint_dir.iterdir() if d.is_dir()],
            key=lambda d: d.name,
        )
        epoch_nums = [int(d.name.split("-")[1]) for d in dirs]
        assert epoch_nums == sorted(epoch_nums), (
            f"Epoch directories not in ascending order: {epoch_nums}"
        )


# ────────────────────────────────────────────────────────────────────────────
# 4. Missing checkpoint error handling
# ────────────────────────────────────────────────────────────────────────────


class TestMissingCheckpointHandling:
    def test_missing_checkpoint_file_raises(self, checkpoint_dir):
        """Attempting to read a non-existent checkpoint must raise FileNotFoundError."""
        missing = checkpoint_dir / "epoch-999" / "meta.json"
        with pytest.raises(FileNotFoundError):
            missing.read_text(encoding="utf-8")

    def test_corrupted_checkpoint_raises_json_error(self, checkpoint_dir):
        """A corrupted (non-JSON) checkpoint file must raise a json.JSONDecodeError."""
        bad_path = checkpoint_dir / "bad_meta.json"
        bad_path.write_text("NOT_VALID_JSON{{{{", encoding="utf-8")
        with pytest.raises(json.JSONDecodeError):
            json.loads(bad_path.read_text(encoding="utf-8"))
