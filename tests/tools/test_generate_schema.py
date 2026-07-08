"""
Test Generate Schema

Test module for generate schema.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tools.generate_schema import build_schema, infer_schema

ROOT = Path(__file__).resolve().parents[2]


def test_infer_schema_handles_nested_objects_and_arrays():
    sample = {
        "name": "demo",
        "enabled": True,
        "retries": 2,
        "thresholds": {"p95": 0.5, "p99": 0.8},
        "labels": ["blue", "green"],
    }
    schema = infer_schema(sample)
    assert schema["type"] == "object", "Object must be initialized"
    assert schema["properties"]["name"]["type"] == "string", "Condition must be true"
    assert schema["properties"]["enabled"]["type"] == "boolean", "Condition must be true"
    assert schema["properties"]["retries"]["type"] == "integer", "Condition must be true"
    assert schema["properties"]["thresholds"]["type"] == "object", "Object must be initialized"
    assert schema["properties"]["labels"]["type"] == "array", "Condition must be true"


def test_build_schema_wraps_non_object_values():
    schema = build_schema([1, 2, 3], title="ArrayConfig")
    assert schema["title"] == "ArrayConfig", "Condition must be true"
    assert schema["properties"]["value"]["type"] == "array", "Value must be initialized"
    assert "required" in schema, "Condition must be true"


def test_generate_schema_cli(tmp_path: Path):
    cfg = tmp_path / "sample.yaml"
    cfg.write_text(
        """
name: widget
retries: 3
features:
  - a
  - b
metadata:
  region: us-west
  owner: ops
""",
        encoding="utf-8",
    )
    output = tmp_path / "schema.json"
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools/generate_schema.py"),
            str(cfg),
            "--output",
            str(output),
            "--title",
            "WidgetSchema",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    schema = json.loads(output.read_text(encoding="utf-8"))
    assert schema["title"] == "WidgetSchema", "Condition must be true"
    assert schema["properties"]["name"]["type"] == "string", "Condition must be true"
    assert schema["properties"]["retries"]["type"] == "integer", "Condition must be true"
    assert schema["properties"]["metadata"]["type"] == "object", "Data must not be empty"
    assert schema["properties"]["features"]["type"] == "array", "Condition must be true"
