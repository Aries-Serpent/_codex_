"""
Test Telemetry Event Schema

Test module for telemetry event schema.
"""

# ruff: noqa: E402
import json
import sys
from pathlib import Path

import pytest

pytest.importorskip("torch", reason="torch is required for telemetry emission tests")
pytest.importorskip("jsonschema", reason="jsonschema not installed")

from jsonschema import Draft7Validator  # type: ignore  # noqa: E402

from src.codex_ml import train_loop as train_loop_module  # noqa: E402

if train_loop_module.instantiate_model is None:  # pragma: no cover - optional dependency missing
    pytest.skip("model registry unavailable", allow_module_level=True)

# PyTorch 2.x has an isinstance bug with Python 3.12 union types
_TORCH_312_BUG = False
try:
    import torch
    _TORCH_312_BUG = sys.version_info >= (3, 12) and torch.__version__.startswith("2.")
except (ImportError, AttributeError):
    pass

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


@pytest.mark.skipif(_TORCH_312_BUG, reason="PyTorch 2.x isinstance bug with Python 3.12 union types")
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
    assert telem_json.exists()
    data = json.loads(telem_json.read_text(encoding="utf-8"))
    assert isinstance(data, list) and data
    Draft7Validator(SCHEMA).validate(data[-1])

    # NDJSON lines
    telem_nd = outdir / "telemetry.ndjson"
    assert telem_nd.exists()
    lines = [line for line in telem_nd.read_text(encoding="utf-8").splitlines() if line]
    Draft7Validator(SCHEMA).validate(json.loads(lines[-1]))
