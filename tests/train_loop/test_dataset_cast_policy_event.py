"""
Test Dataset Cast Policy Event

Test module for dataset cast policy event.
"""

import sys
from pathlib import Path

import pytest

pytest.importorskip("torch")

try:
    import torch as _torch

    _TORCH_312_BUG = sys.version_info >= (3, 12) and _torch.__version__.startswith("2.")
except ImportError:
    _TORCH_312_BUG = False


@pytest.mark.skipif(
    _TORCH_312_BUG, reason="PyTorch 2.x isinstance() bug on Python 3.12 (fixed in 2.2.0 — DR-003)"
)
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
    assert '"event": "dataset_cast"' in content, "Data must not be empty"

    telem = outdir / "telemetry.json"
    assert telem.exists(), "telemetry.json not created"
    tcontent = telem.read_text(encoding="utf-8")
    assert '"event": "dataset_cast"' in tcontent, "Data must not be empty"
    # NDJSON alternative should also exist
    tnd = outdir / "telemetry.ndjson"
    assert tnd.exists(), "Condition must be true"
    assert '"event": "dataset_cast"' in tnd.read_text(encoding="utf-8"), "Data must not be empty"
