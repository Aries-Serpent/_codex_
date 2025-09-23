import json

import pytest

from codex.training import run_functional_training
from codex_utils.repro import log_env_info

pytest.importorskip("omegaconf")
pytest.importorskip("transformers")
torch = pytest.importorskip("torch")


def test_log_env_info(tmp_path):
    path = tmp_path / "env.json"
    log_env_info(path)
    data = json.loads(path.read_text())
    assert data.get("git_commit")
    assert "packages" in data and data["packages"]
    assert "system" in data
    if torch is not None and getattr(torch.version, "cuda", None):
        assert "cuda_version" in data


def test_functional_training_logs_env(tmp_path):
    checkpoint_dir = tmp_path / "ckpt"
    run_functional_training(
        ["hi"],
        [{"prompt": "p", "completion": "c"}],
        [("p", "c", "x", 1)],
        checkpoint_dir=str(checkpoint_dir),
    )
    assert (checkpoint_dir / "env.json").exists()
    provenance_dir = checkpoint_dir / "provenance"
    assert (provenance_dir / "environment.json").exists()
    ndjson_path = provenance_dir / "environment.ndjson"
    assert ndjson_path.exists()
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
    assert checksums_path.exists()
    checksums = json.loads(checksums_path.read_text(encoding="utf-8"))
    assert dataset_file.name in checksums
    assert len(checksums[dataset_file.name]) == 64
    provenance_dir = art_dir / "provenance"
    assert (provenance_dir / "environment.json").exists()
