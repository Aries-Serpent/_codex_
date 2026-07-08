"""
Test Json Disable Env

Test module for json disable env.
"""
import sys
from pathlib import Path
    import torch as _torch_json
    from src.codex_ml.train_loop import run_training



try:

    _TORCH_312_BUG = sys.version_info >= (3, 12) and _torch_json.__version__.startswith("2.")
except (ImportError, AttributeError):
    _TORCH_312_BUG = False


@pytest.mark.skipif(
    _TORCH_312_BUG, reason="PyTorch 2.x isinstance bug with Python 3.12 union types"
)
def test_telemetry_json_disable_env(tmp_path: Path, monkeypatch):

    monkeypatch.setenv("CODEX_TELEMETRY_JSON_DISABLE", "1")
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

    assert not (outdir / "telemetry.json").exists(), "Condition must be true"
    # NDJSON still present by default
    assert (outdir / "telemetry.ndjson").exists(), "Condition must be true"
