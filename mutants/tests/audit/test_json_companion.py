"""
Test that S6 render writes a JSON companion file with expected schema keys
"""

import json

from scripts.space_traversal import audit_runner as runner


def make_cfg(tmp_path):
    return {
        "output": {
            "artifacts_dir": str(tmp_path / "audit_artifacts"),
            "reports_dir": str(tmp_path / "reports"),
        },
        "weights": {
            "functionality": 0.25,
            "consistency": 0.2,
            "tests": 0.25,
            "safeguards": 0.15,
            "documentation": 0.15,
        },
        "scoring": {"thresholds": {"low": 0.7, "medium": 0.85}},
        "matrix_template": "templates/audit/capability_matrix.md.j2",
        "metrics_schema_version": "2.0.0",
    }


def test_json_companion_written(tmp_path):
    cfg = make_cfg(tmp_path)
    scored = [
        {
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
        }
    ]
    _md, js = runner.render_template(
        cfg,
        {
            "timestamp": "x",
            "capabilities": scored,
            "gaps": [],
            "weights": cfg["weights"],
            "scoring": cfg["scoring"],
        },
    )
    assert js.exists(), "Condition must be true"
    data = json.loads(js.read_text())
    assert "capabilities" in data, "Data must not be empty"
    assert data["metrics_schema_version"] == "2.0.0", "Data must not be empty"
