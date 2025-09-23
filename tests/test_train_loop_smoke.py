"""Smoke tests for the codex_ml.train_loop module."""

from __future__ import annotations

import hashlib
import importlib
import json


def test_run_training_smoke(tmp_path, monkeypatch):
    """Basic sanity check that ``run_training`` executes and writes metrics."""
    module = importlib.import_module("codex_ml.train_loop")
    module = importlib.reload(module)

    captured: list[int] = []

    def fake_set_reproducible(seed: int) -> None:
        captured.append(seed)

    monkeypatch.setattr(module, "set_reproducible", fake_set_reproducible)

    first_art_dir = tmp_path / "first" / "metrics"
    assert not first_art_dir.exists()

    dataset_file = tmp_path / "data" / "sample.txt"
    dataset_file.parent.mkdir(parents=True, exist_ok=True)
    dataset_file.write_text("codex", encoding="utf-8")

    module.run_training(
        epochs=1,
        grad_accum=2,
        seed=42,
        art_dir=first_art_dir,
        dataset_sources=[dataset_file],
    )

    assert captured[0] == 42
    assert first_art_dir.exists()
    metrics_json = first_art_dir / "metrics.json"
    assert metrics_json.exists()
    data = json.loads(metrics_json.read_text(encoding="utf-8"))
    phases = {entry.get("phase") for entry in data}
    assert {"epoch_end", "best_checkpoint"}.issubset(phases)
    env_json = first_art_dir / "environment.json"
    assert env_json.exists()
    env_data = json.loads(env_json.read_text(encoding="utf-8"))
    assert "python" in env_data
    checksums_path = first_art_dir / "dataset_checksums.json"
    assert checksums_path.exists()
    checksums = json.loads(checksums_path.read_text(encoding="utf-8"))
    expected_hash = hashlib.sha256(dataset_file.read_bytes()).hexdigest()
    assert checksums[dataset_file.name] == expected_hash

    second_art_dir = tmp_path / "second" / "metrics"
    module.run_training(epochs=0, grad_accum=1, seed=0, art_dir=second_art_dir)

    assert second_art_dir.exists()
    assert len(captured) == 2
    assert isinstance(captured[1], int)
    assert captured[1] != 0
    second_json = second_art_dir / "metrics.json"
    assert second_json.exists()
    second_data = json.loads(second_json.read_text(encoding="utf-8"))
    assert second_data[-1]["phase"] == "best_checkpoint"
