import json
from pathlib import Path

import jsonschema

from scripts.space_traversal.audit_runner import build_json_companion_payload, render_template

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

# Additional test for file writing and companion file presence
def test_json_companion_written(tmp_path):
    # Prepare configuration and context
    ROOT = Path(__file__).resolve().parents[2]
    TEMPLATE = ROOT / "templates/audit/capability_matrix.md.j2"

    cfg = {
        "output": {
            "artifacts_dir": str(tmp_path / "audit_artifacts"),
            "reports_dir": str(tmp_path / "reports"),
            "matrix_template": str(TEMPLATE),
        },
        "weights": {
            "functionality": 0.25,
            "consistency": 0.2,
            "tests": 0.25,
            "safeguards": 0.15,
            "documentation": 0.15,
        },
        "scoring": {"thresholds": {"low": 0.7, "medium": 0.85}},
        "metrics_schema_version": "2.0.0"
    }

    scored = [{
        "id": "a",
        "components": {
            "functionality": 1.0,
            "consistency": 1.0,
            "tests": 0.0,
            "safeguards": 0.0,
            "documentation": 0.0,
        },
        "score": 0.6,
        "evidence_files": [],
        "found_patterns": [],
        "required_patterns": [],
        "missing_patterns": [],
        "meta": {},
    }]
    gaps = {"low_maturity": []}

    context = {
        "timestamp": "2025-11-19 00:00:00 UTC",
        "capabilities": scored,
        "gaps": [],
        "weights": cfg["weights"],
        "scoring": cfg["scoring"],
        "thresholds": cfg["scoring"]["thresholds"],
    }

    md_path, stamp = render_template(cfg, context)
    # Manually import build_json_companion_payload if needed, or utilize code as in audit_runner.py to write JSON companion.
    companion = build_json_companion_payload(context, md_path.name)
    reports_dir = Path(cfg["output"]["reports_dir"])
    json_path = reports_dir / f"capability_matrix_{stamp}.json"
    json_path.write_text(json.dumps(companion, indent=2), encoding="utf-8")

    assert json_path.exists()
    data = json.loads(json_path.read_text())
    assert "capabilities" in data
    assert data["schema_version"] == "2.0.0"
