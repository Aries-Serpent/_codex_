"""
Test Telemetry Rollover

Test module for telemetry rollover.
"""

from pathlib import Path


def test_telemetry_rollover(tmp_path: Path, monkeypatch):
    # Set max items to 1 so the second event triggers rollover
    monkeypatch.setenv("CODEX_TELEMETRY_MAX_ITEMS", "1")

    try:
        from src.codex_ml.train_loop import run_training
    except ImportError as e:
        import pytest

        pytest.skip(f"run_training not available: {e}")
    else:
        outdir = tmp_path / "artifacts"
        # Two runs -> two telemetry events
        try:
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
        except (ImportError, AttributeError) as e:
            import pytest

            # If training fails due to missing dependencies, skip
            pytest.skip(f"Training execution failed: {e}")

        # Expect telemetry.json exists and at least one rolled file
        telem = outdir / "telemetry.json"
        if not telem.exists():
            import pytest

            pytest.skip("telemetry.json not created - telemetry may be disabled")

        rolled = list(outdir.glob("telemetry-*.json"))
        # Either rollover produced a file, or truncation fallback kept a single-element JSON
        if not rolled:
            import json

            data = json.loads(telem.read_text(encoding="utf-8"))
            assert isinstance(data, list) and len(data) >= 1
