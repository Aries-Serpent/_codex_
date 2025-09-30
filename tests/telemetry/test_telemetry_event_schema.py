from pathlib import Path
import json
import pytest


jsonschema = pytest.importorskip("jsonschema", reason="jsonschema not installed")
from jsonschema import Draft7Validator  # type: ignore


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


def test_telemetry_events_json_and_ndjson(tmp_path: Path):
    from src.codex_ml.train_loop import run_training

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
    last_line = [l for l in telem_nd.read_text(encoding="utf-8").splitlines() if l][-1]
    Draft7Validator(SCHEMA).validate(json.loads(last_line))

