import json
from pathlib import Path
import tempfile
import subprocess
import sys

SCHEMA_CONTENT = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "required": ["model", "data", "training"],
    "properties": {
        "model": {
            "type": "object",
            "required": ["name"],
            "properties": {"name": {"type": "string"}},
        },
        "data": {
            "type": "object",
            "required": ["dataset"],
            "properties": {"dataset": {"type": "string"}},
        },
        "training": {
            "type": "object",
            "required": ["epochs", "batch_size"],
            "properties": {"epochs": {"type": "integer"}, "batch_size": {"type": "integer"}},
        },
    },
}

VALID_CFG = {
    "model": {"name": "demo"},
    "data": {"dataset": "synthetic"},
    "training": {"epochs": 1, "batch_size": 2},
}

INVALID_CFG = {
    "model": {"name": "demo"},
    "data": {},  # missing dataset
    "training": {"epochs": 1, "batch_size": 2},
}


def test_validator_success():
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        schema = td / "schema.json"
        schema.write_text(json.dumps(SCHEMA_CONTENT))

        cfg = td / "exp.json"
        cfg.write_text(json.dumps(VALID_CFG))

        result = subprocess.run(
            [
                sys.executable,
                "tools/validate_experiments.py",
                "--schema",
                str(schema),
                "--paths",
                str(td),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr


def test_validator_failure():
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        schema = td / "schema.json"
        schema.write_text(json.dumps(SCHEMA_CONTENT))

        cfg = td / "exp.json"
        cfg.write_text(json.dumps(INVALID_CFG))

        result = subprocess.run(
            [
                sys.executable,
                "tools/validate_experiments.py",
                "--schema",
                str(schema),
                "--paths",
                str(td),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 3
        assert "dataset" in result.stderr
