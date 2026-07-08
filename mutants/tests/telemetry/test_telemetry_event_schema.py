"""
pytest.importorskip("mlflow")
Test Telemetry Event Schema

Test module for telemetry event schema.
"""

import json
import sys
from pathlib import Path

import pytest

pytest.importorskip("torch", reason="torch is required for telemetry emission tests")
pytest.importorskip("jsonschema", reason="jsonschema not installed")

from jsonschema import Draft7Validator  # type: ignore

from src.codex_ml import train_loop as train_loop_module

if train_loop_module.instantiate_model is None:  # pragma: no cover - optional dependency missing
    pytest.skip("model registry unavailable", allow_module_level=True)

# PyTorch 2.x (<2.2.0) has an isinstance bug with Python 3.12 union types
# DR-003: guard tightened to torch < 2.2.0; CI uses torch >= 2.2.0 so tests run.
_TORCH_312_BUG = False
try:
    import torch as _torch_mod

    _torch_ver = tuple(int(x) for x in _torch_mod.__version__.split(".")[:2])
    _TORCH_312_BUG = sys.version_info >= (3, 12) and _torch_ver < (2, 2)
except (ImportError, AttributeError, ValueError):
    _TORCH_312_BUG = False  # torch not installed; PyTorch/Python 3.12 bug cannot apply

SCHEMA = {
    "type": "object",
    "properties": {
        "type": {"type": "string"},
        "event": {"type": "string"},
        "timestamp": {"type": "string"},
    },
    "required": ["type", "event", "timestamp"],
    "additionalProperties": True,
}


@pytest.mark.skipif(
    _TORCH_312_BUG, reason="PyTorch 2.x isinstance bug with Python 3.12 union types"
)
def test_telemetry_events_json_and_ndjson(tmp_path: Path):
    run_training = train_loop_module.run_training

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

    # JSON array
    telem_json = outdir / "telemetry.json"
    assert telem_json.exists(), "Condition must be true"
    data = json.loads(telem_json.read_text(encoding="utf-8"))
    assert isinstance(data, list) and data
    Draft7Validator(SCHEMA).validate(data[-1])

    # NDJSON lines
    telem_nd = outdir / "telemetry.ndjson"
    assert telem_nd.exists(), "Condition must be true"
    lines = [line for line in telem_nd.read_text(encoding="utf-8").splitlines() if line]
    Draft7Validator(SCHEMA).validate(json.loads(lines[-1]))
