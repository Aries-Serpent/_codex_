"""
Test that S6 render writes a JSON companion file with expected schema keys
"""
import json
from pathlib import Path
from scripts.space_traversal import audit_runner as runner

def make_cfg(tmp_path):
    """Builds test config ensuring matrix_template is nested under 'output' as expected by render_template."""
    return {
        "output": {
            "artifacts_dir": str(tmp_path / "audit_artifacts"),
            "reports_dir": str(tmp_path / "reports"),
            "matrix_template": "templates/audit/capability_matrix.md.j2"  # Nest under output
        },
        "weights": {
            "functionality": 0.25,
            "consistency": 0.2,
            "tests": 0.25,
            "safeguards": 0.15,
            "documentation": 0.15,
        },
        "scoring": {
            "thresholds": {"low": 0.7, "medium": 0.85}
        },
        "metrics_schema_version": "2.0.0"
    }

def test_json_companion_written(tmp_path):
    """
    Validates companion JSON file creation and schema from rendered audit.
    Ensures capabilities and schema version are present.
    """
    cfg = make_cfg(tmp_path)
    scored = [{
        "id": "a",
        "components": {
            "functionality": 1.0,
            "consistency": 1.0,
            "tests": 0.0,
            "safeguards": 0.0,
            "documentation": 0.0
        },
        "score": 0.6,
        "evidence_files": [],
        "found_patterns": []
    }]
    # Render template and companion JSON file.
    md_path, json_path = runner.render_template(
        cfg,
        {
            "timestamp": "2025-11-19 00:00:00 UTC",
            "capabilities": scored,
            "gaps": [],
            "weights": cfg["weights"],
            "scoring": cfg["scoring"]
        }
    )
    assert json_path.exists(), f"Companion JSON not written to {json_path}"
    data = json.loads(json_path.read_text())
    assert "capabilities" in data, "'capabilities' missing in companion JSON"
    assert data["metrics_schema_version"] == "2.0.0", "Wrong metrics_schema_version in JSON"
