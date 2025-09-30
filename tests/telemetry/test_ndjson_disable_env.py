# ruff: noqa: E402
from pathlib import Path

import pytest

pytest.importorskip("torch", reason="torch is required for telemetry emission tests")
from src.codex_ml import train_loop as train_loop_module

if train_loop_module.instantiate_model is None:  # pragma: no cover - optional dependency missing
    pytest.skip("model registry unavailable", allow_module_level=True)


def test_telemetry_ndjson_disable_env(tmp_path: Path, monkeypatch):
    run_training = train_loop_module.run_training

    monkeypatch.setenv("CODEX_TELEMETRY_NDJSON_DISABLE", "1")
    outdir = tmp_path / "artifacts"
    run_training(
        epochs=1,
        steps_per_epoch=1,
        grad_accum=1,
        art_dir=str(outdir),
        learning_rate=1e-3,
        model_name="minilm",
        dataset_cast_policy="to_fp32",
    )

    assert not (outdir / "telemetry.ndjson").exists()
    # JSON should still be present by default (due to dataset_cast events)
    assert (outdir / "telemetry.json").exists()
