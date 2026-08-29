"""
Test Validate Configs

Test module for validate configs.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

pytest.importorskip("jsonschema")

from tools import validate_configs


def test_validate_pair_for_training_profile():
    config_path = REPO_ROOT / "configs" / "training" / "profiles" / "default.yaml"
    schema_path = REPO_ROOT / "configs" / "schemas" / "training_profile.schema.json"
    errors = validate_configs.validate_pair(config_path, schema_path)
    assert errors == [], "Error should be raised or set"


def test_validate_pair_reports_errors(tmp_path):
    config = tmp_path / "config.yaml"
    config.write_text("epochs: 0\n", encoding="utf-8")
    schema = tmp_path / "schema.json"
    schema.write_text(
        json.dumps(
            {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "type": "object",
                "properties": {"epochs": {"type": "integer", "minimum": 1}},
            }
        ),
        encoding="utf-8",
    )
    errors = validate_configs.validate_pair(config, schema)
    assert errors, "Error should be raised or set"
    assert any("minimum" in err for err in errors), "Error should be raised or set"
