"""
pytest.importorskip("mlflow")
Test Sample Rate Gate

Test module for sample rate gate.
"""

import sys
from pathlib import Path

import pytest

pytest.importorskip("torch", reason="torch is required for telemetry emission tests")
from src.codex_ml import train_loop as train_loop_module

if train_loop_module.instantiate_model is None:  # pragma: no cover - optional dependency missing
    pytest.skip("model registry unavailable", allow_module_level=True)

# PyTorch 2.x has an isinstance bug with Python 3.12 union types
_TORCH_312_BUG = False
try:
    import torch

    _TORCH_312_BUG = sys.version_info >= (3, 12) and torch.__version__.startswith("2.")
except (ImportError, AttributeError):
    _TORCH_312_BUG = False  # torch not installed; PyTorch/Python 3.12 bug cannot apply


@pytest.mark.skipif(
    _TORCH_312_BUG, reason="PyTorch 2.x isinstance bug with Python 3.12 union types"
)
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
    assert not (outdir / "telemetry.json").exists(), "Condition must be true"
    assert not (outdir / "telemetry.ndjson").exists(), "Condition must be true"
