import json
from pathlib import Path

import jsonschema

from scripts.space_traversal.audit_runner import build_json_companion_payload


SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "scripts"
    / "space_traversal"
    / "schemas"
    / "capability_matrix.schema.json"
)


def test_json_companion_matches_schema():
    context = {
        "timestamp": "2025-11-19 00:00:00 UTC",
        "weights": {"functionality": 0.25, "tests": 0.25, "consistency": 0.5},
        "thresholds": {"low": 0.7, "medium": 0.85},
        "missing_detectors": ["training-engine::train_loop"],
        "gaps": [],
        "capabilities": [
            {
                "id": "training-engine",
                "score": 0.72,
                "components": {
                    "functionality": 0.8,
                    "consistency": 0.6,
                    "tests": 0.7,
                    "safeguards": 0.4,
                    "documentation": 0.9,
                },
                "evidence_files": ["README.md"],
                "missing_patterns": ["loop"],
                "meta": {"override_aliases": ["train_loop"]},
            }
        ],
    }

    payload = build_json_companion_payload(context, "capability_matrix_test.md")
    schema = json.loads(SCHEMA_PATH.read_text())
    jsonschema.validate(payload, schema)
    assert payload["capabilities"][0]["level"] == "medium"
    assert payload["missing_detectors"] == ["training-engine::train_loop"]
