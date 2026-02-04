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

    def fake_set_reproducible(seed: int, **_: object) -> None:
        captured.append(seed)

    monkeypatch.setattr(module, "set_reproducible", fake_set_reproducible)

    class _StubModel:
        def to(self, *args, **kwargs):  # pragma: no cover - simple stub
            return self

        def train(self):  # pragma: no cover - simple stub
            return None

        def parameters(self):  # pragma: no cover - simple stub
            return []

    monkeypatch.setattr(module, "instantiate_model", lambda name, cfg: _StubModel())

    first_art_dir = tmp_path / "first" / "metrics"
    assert not first_art_dir.exists()

    dataset_file = tmp_path / "data" / "sample.txt"
    dataset_file.parent.mkdir(parents=True, exist_ok=True)
    dataset_file.write_text("codex", encoding="utf-8")

    result = module.run_training(
        epochs=1,
        grad_accum=2,
        seed=42,
        art_dir=first_art_dir,
        model_name="dummy",
        dataset_sources=[dataset_file],
    )

    assert result["callback_errors"] == []
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
    result_zero = module.run_training(
        epochs=0,
        grad_accum=1,
        seed=0,
        art_dir=second_art_dir,
        model_name="dummy",
    )

    assert second_art_dir.exists()
    assert len(captured) == 2
    assert isinstance(captured[1], int)
    assert captured[1] != 0
    second_json = second_art_dir / "metrics.json"
    assert second_json.exists()
    second_data = json.loads(second_json.read_text(encoding="utf-8"))
    assert second_data[-1]["phase"] == "best_checkpoint"
    assert result_zero["callback_errors"] == []


def test_run_training_records_callback_errors(tmp_path, monkeypatch):
    module = importlib.import_module("codex_ml.train_loop")
    module = importlib.reload(module)

    class BrokenCallback(module.Callback):
        def on_train_start(self, state):  # pragma: no cover - intentional failure
            raise RuntimeError("boom")

    class _StubModel:
        def to(self, *args, **kwargs):  # pragma: no cover - simple stub
            return self

        def train(self):  # pragma: no cover - simple stub
            return None

        def parameters(self):  # pragma: no cover - simple stub
            return []

    monkeypatch.setattr(module, "instantiate_model", lambda name, cfg: _StubModel())

    res = module.run_training(
        epochs=0,
        grad_accum=1,
        seed=123,
        art_dir=tmp_path / "errors",
        callbacks=[BrokenCallback()],
        model_name="dummy",
        return_state=True,
    )

    errors = res["callback_errors"]
    assert errors and errors[0]["stage"] == "on_train_start"
    assert "boom" in errors[0]["error"]
