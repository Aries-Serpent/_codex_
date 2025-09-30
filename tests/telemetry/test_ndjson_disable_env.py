from pathlib import Path
import os


def test_telemetry_ndjson_disable_env(tmp_path: Path, monkeypatch):
    from src.codex_ml.train_loop import run_training

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
