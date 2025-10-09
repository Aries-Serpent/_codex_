from __future__ import annotations

import json
from pathlib import Path

import pytest

try:
    import jsonschema  # type: ignore
except Exception:  # pragma: no cover
    jsonschema = None  # type: ignore


SCHEMA_PATH = Path("schemas/metrics-ndjson-v0.3.json")


@pytest.mark.skipif(jsonschema is None, reason="jsonschema not installed")
def test_metrics_schema_valid_and_invalid(tmp_path: Path):
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)  # type: ignore

    valid = [
        {"epoch": 1, "loss": 0.1},
        {"epoch": "2", "accuracy": 0.9},
        {"epoch": "0007", "nested": {"p": 1}},
    ]
    invalid = [
        {"loss": 0.1},  # missing epoch
        {"epoch": "abc"},  # non-numeric epoch string
    ]

    for rec in valid:
        errs = sorted(validator.iter_errors(rec), key=lambda e: e.path)  # type: ignore
        assert not errs

    for rec in invalid:
        errs = sorted(validator.iter_errors(rec), key=lambda e: e.path)  # type: ignore
        assert errs