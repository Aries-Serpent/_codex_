from pathlib import Path


def test_sample_rate_zero_disables_telemetry(tmp_path: Path, monkeypatch):
    from src.codex_ml.train_loop import run_training

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

