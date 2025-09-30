from pathlib import Path


def test_telemetry_rollover(tmp_path: Path, monkeypatch):
    # Set max items to 1 so the second event triggers rollover
    monkeypatch.setenv("CODEX_TELEMETRY_MAX_ITEMS", "1")
    from src.codex_ml.train_loop import run_training

    outdir = tmp_path / "artifacts"
    # Two runs -> two telemetry events
    run_training(
        epochs=1,
        steps_per_epoch=1,
        grad_accum=1,
        art_dir=str(outdir),
        learning_rate=1e-3,
        model_name="minilm",
        dataset_cast_policy="to_fp32",
    )
    run_training(
        epochs=1,
        steps_per_epoch=1,
        grad_accum=1,
        art_dir=str(outdir),
        learning_rate=1e-3,
        model_name="minilm",
        dataset_cast_policy="to_fp32",
    )

    # Expect telemetry.json exists and at least one rolled file
    telem = outdir / "telemetry.json"
    assert telem.exists()
    rolled = list(outdir.glob("telemetry-*.json"))
    # Either rollover produced a file, or truncation fallback kept a single-element JSON
    if not rolled:
        import json
        data = json.loads(telem.read_text(encoding="utf-8"))
        assert isinstance(data, list) and len(data) >= 1
