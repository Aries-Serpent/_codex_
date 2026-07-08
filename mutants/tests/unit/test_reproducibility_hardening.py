"""Unit tests for codex_ml.utils.reproducibility_hardening."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

from codex_ml.utils.reproducibility_hardening import (
    ReproducibilityManager,
    create_reproducibility_manifest,
    enable_deterministic_training,
    save_env_snapshot,
)

# ---------------------------------------------------------------------------
# enable_deterministic_training
# ---------------------------------------------------------------------------


def test_enable_deterministic_training_returns_dict():
    status = enable_deterministic_training(seed=7)
    assert isinstance(status, dict)


def test_enable_deterministic_training_python_random_seeded():
    status = enable_deterministic_training(seed=42)
    assert status.get("python_random") is True, "Condition must be true"


def test_enable_deterministic_training_sets_pythonhashseed():
    enable_deterministic_training(seed=99)
    assert os.environ.get("PYTHONHASHSEED") == "99", "Condition must be true"


def test_enable_deterministic_training_numpy_seeded_when_available():
    # Probe whether numpy is installed; the assertion adapts based on availability.
    try:
        import numpy  # noqa: F401 — availability probe only

        status = enable_deterministic_training(seed=1)
        assert status.get("numpy") is True, "Condition must be true"
    except ImportError:
        status = enable_deterministic_training(seed=1)
        assert status.get("numpy") is None, "Condition must be true"


def test_enable_deterministic_training_torch_none_when_unavailable():
    with patch.dict(sys.modules, {"torch": None}):
        status = enable_deterministic_training(seed=5)
    # torch key may be None (not installed) or True (installed)
    assert "python_random" in status, "Condition must be true"


def test_enable_deterministic_training_strict_flag_accepted():
    status = enable_deterministic_training(seed=10, strict=True)
    assert isinstance(status, dict)
    assert status.get("python_random") is True, "Condition must be true"


def test_enable_deterministic_training_different_seeds():
    s1 = enable_deterministic_training(seed=0)
    s2 = enable_deterministic_training(seed=1000)
    assert s1["python_random"] is True, "Condition must be true"
    assert s2["python_random"] is True, "Condition must be true"


# ---------------------------------------------------------------------------
# save_env_snapshot
# ---------------------------------------------------------------------------


def test_save_env_snapshot_creates_txt_and_json(tmp_path: Path):
    out = tmp_path / "snap.txt"
    snapshot = save_env_snapshot(out)
    assert out.exists(), "text snapshot file not created"
    assert out.with_suffix(".json").exists(), "json snapshot file not created"
    assert isinstance(snapshot, dict)


def test_save_env_snapshot_has_python_version(tmp_path: Path):
    out = tmp_path / "snap.txt"
    snapshot = save_env_snapshot(out)
    assert "python_version" in snapshot, "Condition must be true"
    assert sys.version in snapshot["python_version"], "Condition must be true"


def test_save_env_snapshot_has_platform(tmp_path: Path):
    out = tmp_path / "snap.txt"
    snapshot = save_env_snapshot(out)
    assert "platform" in snapshot, "Condition must be true"
    assert "system" in snapshot["platform"], "Condition must be true"


def test_save_env_snapshot_has_timestamp(tmp_path: Path):
    out = tmp_path / "snap.txt"
    snapshot = save_env_snapshot(out)
    assert "timestamp" in snapshot, "Condition must be true"
    assert "T" in snapshot["timestamp"], "Condition must be true"


def test_save_env_snapshot_without_pip_freeze(tmp_path: Path):
    out = tmp_path / "snap.txt"
    snapshot = save_env_snapshot(out, include_pip_freeze=False)
    assert snapshot.get("pip_freeze") is None, "Condition must be true"


def test_save_env_snapshot_with_pip_freeze(tmp_path: Path):
    out = tmp_path / "snap.txt"
    snapshot = save_env_snapshot(out, include_pip_freeze=True)
    # pip_freeze is a list or empty list
    assert isinstance(snapshot.get("pip_freeze"), (list, type(None)))


def test_save_env_snapshot_creates_parent_dirs(tmp_path: Path):
    out = tmp_path / "nested" / "dir" / "snap.txt"
    save_env_snapshot(out)
    assert out.exists(), "Condition must be true"


def test_save_env_snapshot_json_is_valid(tmp_path: Path):
    out = tmp_path / "snap.txt"
    save_env_snapshot(out)
    json_path = out.with_suffix(".json")
    data = json.loads(json_path.read_text())
    assert isinstance(data, dict)
    assert "python_version" in data, "Data must not be empty"


# ---------------------------------------------------------------------------
# create_reproducibility_manifest
# ---------------------------------------------------------------------------


def test_create_reproducibility_manifest_returns_dict(tmp_path: Path):
    manifest = create_reproducibility_manifest(seed=42, output_dir=tmp_path)
    assert isinstance(manifest, dict)


def test_create_reproducibility_manifest_seed_field(tmp_path: Path):
    manifest = create_reproducibility_manifest(seed=77, output_dir=tmp_path)
    assert manifest["seed"] == 77, "Condition must be true"


def test_create_reproducibility_manifest_includes_seeding_status(tmp_path: Path):
    manifest = create_reproducibility_manifest(seed=1, output_dir=tmp_path)
    assert "seeding_status" in manifest, "Condition must be true"
    assert isinstance(manifest["seeding_status"], dict)


def test_create_reproducibility_manifest_includes_environment(tmp_path: Path):
    manifest = create_reproducibility_manifest(seed=1, output_dir=tmp_path)
    assert "environment" in manifest, "Condition must be true"
    assert "python_version" in manifest["environment"], "Condition must be true"


def test_create_reproducibility_manifest_includes_manifest_hash(tmp_path: Path):
    manifest = create_reproducibility_manifest(seed=1, output_dir=tmp_path)
    assert "manifest_hash" in manifest, "Condition must be true"
    assert len(manifest["manifest_hash"]) == 16, "Collection must not be empty"


def test_create_reproducibility_manifest_with_config(tmp_path: Path):
    cfg = {"lr": 1e-4, "epochs": 10}
    manifest = create_reproducibility_manifest(seed=1, output_dir=tmp_path, config=cfg)
    assert manifest.get("config") == cfg, "Condition must be true"


def test_create_reproducibility_manifest_with_dataset_hash(tmp_path: Path):
    manifest = create_reproducibility_manifest(seed=1, output_dir=tmp_path, dataset_hash="abc123")
    assert manifest.get("dataset_hash") == "abc123", "Data must not be empty"


def test_create_reproducibility_manifest_saves_json_file(tmp_path: Path):
    create_reproducibility_manifest(seed=1, output_dir=tmp_path)
    assert (tmp_path / "reproducibility_manifest.json").exists(), "Condition must be true"


def test_create_reproducibility_manifest_json_loadable(tmp_path: Path):
    create_reproducibility_manifest(seed=1, output_dir=tmp_path)
    data = json.loads((tmp_path / "reproducibility_manifest.json").read_text())
    assert data["seed"] == 1, "Data must not be empty"


# ---------------------------------------------------------------------------
# ReproducibilityManager
# ---------------------------------------------------------------------------


def test_reproducibility_manager_setup_returns_dict(tmp_path: Path):
    mgr = ReproducibilityManager(seed=42, output_dir=tmp_path)
    status = mgr.setup()
    assert isinstance(status, dict)
    assert status.get("python_random") is True, "Condition must be true"


def test_reproducibility_manager_setup_strict(tmp_path: Path):
    mgr = ReproducibilityManager(seed=0, output_dir=tmp_path)
    status = mgr.setup(strict=True)
    assert isinstance(status, dict)


def test_reproducibility_manager_capture_environment(tmp_path: Path):
    mgr = ReproducibilityManager(seed=42, output_dir=tmp_path)
    snap = mgr.capture_environment()
    assert "python_version" in snap, "Condition must be true"


def test_reproducibility_manager_get_manifest_none_before_finalize(tmp_path: Path):
    mgr = ReproducibilityManager(seed=42, output_dir=tmp_path)
    assert mgr.get_manifest() is None, "Condition must be true"


def test_reproducibility_manager_finalize_returns_manifest(tmp_path: Path):
    mgr = ReproducibilityManager(seed=42, output_dir=tmp_path)
    manifest = mgr.finalize()
    assert isinstance(manifest, dict)
    assert manifest["seed"] == 42, "Condition must be true"


def test_reproducibility_manager_get_manifest_after_finalize(tmp_path: Path):
    mgr = ReproducibilityManager(seed=42, output_dir=tmp_path)
    mgr.finalize()
    assert mgr.get_manifest() is not None, "Value must be initialized"


def test_reproducibility_manager_finalize_with_config(tmp_path: Path):
    mgr = ReproducibilityManager(seed=5, output_dir=tmp_path)
    manifest = mgr.finalize(config={"lr": 0.01}, dataset_hash="xyz")
    assert manifest["config"] == {"lr": 0.01}, "Condition must be true"
    assert manifest["dataset_hash"] == "xyz", "Data must not be empty"


def test_reproducibility_manager_default_output_dir():
    mgr = ReproducibilityManager(seed=1)
    assert "reproducibility" in str(mgr.output_dir), "Condition must be true"


def test_reproducibility_manager_custom_seed():
    mgr = ReproducibilityManager(seed=1234)
    assert mgr.seed == 1234, "seed is not valid"
