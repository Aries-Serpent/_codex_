# ruff: noqa: E402
from pathlib import Path

import pytest

pytest.importorskip("torch", reason="torch is required for telemetry emission tests")
from src.codex_ml import train_loop as train_loop_module

if train_loop_module.instantiate_model is None:  # pragma: no cover - optional dependency missing
    pytest.skip("model registry unavailable", allow_module_level=True)


def test_sample_rate_zero_disables_telemetry(tmp_path: Path, monkeypatch):
    run_training = train_loop_module.run_training

    monkeypatch.setenv("CODEX_TELEMETRY_SAMPLE_RATE", "0")
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
    # No telemetry files should be created when sample_rate=0
    assert not (outdir / "telemetry.json").exists()
    assert not (outdir / "telemetry.ndjson").exists()
