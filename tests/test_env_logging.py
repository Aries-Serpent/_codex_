"""
pytest.importorskip("tensorboard")
Test Env Logging

Test module for env logging.
"""

import json

import pytest

from codex.training import run_functional_training
from codex_utils.repro import log_env_info

pytest.importorskip("omegaconf")
pytest.importorskip("transformers")
torch = pytest.importorskip("torch")


def test_log_env_info(tmp_path, monkeypatch):
    path = tmp_path / "env.json"

    # Mock _codex_sample_system to return JSON-serializable data
    def mock_sample_system():
        return {
            "python": "3.10.0",
            "platform": "Linux",
            "git_commit": "abc123",
        }

    # Patch _codex_sample_system before calling log_env_info
    try:
        from codex_ml.monitoring import codex_logging

        monkeypatch.setattr(codex_logging, "_codex_sample_system", mock_sample_system)
    except ImportError:
        _ = None  # Module may not be available in all test environments

    log_env_info(path)
    data = json.loads(path.read_text())
    assert data.get("git_commit"), "Data must not be empty"
    assert data.get("packages"), "Data must not be empty"
    assert "system" in data, "Data must not be empty"
    if torch is not None and getattr(torch.version, "cuda", None):
        assert "cuda_version" in data, "Data must not be empty"


def test_functional_training_logs_env(tmp_path):
    checkpoint_dir = tmp_path / "ckpt"
    run_functional_training(
        ["hi"],
        [{"prompt": "p", "completion": "c"}],
        [("p", "c", "x", 1)],
        checkpoint_dir=str(checkpoint_dir),
    )
    assert (checkpoint_dir / "env.json").exists(), "Condition must be true"
    provenance_dir = checkpoint_dir / "provenance"
    assert (provenance_dir / "environment.json").exists(), "Condition must be true"
    ndjson_path = provenance_dir / "environment.ndjson"
    assert ndjson_path.exists(), "Condition must be true"
    lines = [
        line.strip()
        for line in ndjson_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert lines, "environment.ndjson should contain at least one record"


def test_functional_training_art_dir_and_dataset_manifest(tmp_path):
    checkpoint_dir = tmp_path / "checkpoints"
    art_dir = tmp_path / "artifacts"
    dataset_file = tmp_path / "corpus.txt"
    dataset_file.write_text("hello\nworld\n", encoding="utf-8")

    run_functional_training(
        ["hi"],
        [{"prompt": "p", "completion": "c"}],
        [("p", "c", "x", 1)],
        checkpoint_dir=str(checkpoint_dir),
        art_dir=art_dir,
        dataset_sources=[dataset_file],
    )

    checksums_path = art_dir / "dataset_checksums.json"
    assert checksums_path.exists(), "Condition must be true"
    checksums = json.loads(checksums_path.read_text(encoding="utf-8"))
    assert dataset_file.name in checksums, "Data must not be empty"
    assert len(checksums[dataset_file.name]) == 64, "Collection must not be empty"
    provenance_dir = art_dir / "provenance"
    assert (provenance_dir / "environment.json").exists(), "Condition must be true"
