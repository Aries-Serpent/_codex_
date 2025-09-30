from pathlib import Path


def test_dataset_cast_policy_emits_event(tmp_path: Path):
    # Run one synthetic epoch and ensure dataset_cast telemetry is written
    from src.codex_ml.train_loop import run_training

    outdir = tmp_path / "artifacts"
    res = run_training(
        epochs=1,
        steps_per_epoch=1,
        grad_accum=1,
        art_dir=str(outdir),
        learning_rate=1e-3,
        model_name="minilm",
        dataset_cast_policy="to_fp32",
    )
    assert isinstance(res, dict)
    ndjson = outdir / "metrics.ndjson"
    assert ndjson.exists(), "metrics.ndjson not created"
    content = ndjson.read_text(encoding="utf-8")
    assert '"event": "dataset_cast"' in content

    telem = outdir / "telemetry.json"
    assert telem.exists(), "telemetry.json not created"
    tcontent = telem.read_text(encoding="utf-8")
    assert '"event": "dataset_cast"' in tcontent
    # NDJSON alternative should also exist
    tnd = outdir / "telemetry.ndjson"
    assert tnd.exists()
    assert '"event": "dataset_cast"' in tnd.read_text(encoding="utf-8")
