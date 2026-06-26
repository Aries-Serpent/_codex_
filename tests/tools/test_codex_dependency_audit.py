"""
Test Codex Dependency Audit

Test module for codex dependency audit.
"""

import json
from pathlib import Path

import tools.codex_dependency_audit as da


def test_dependency_audit_parses_requirements(tmp_path: Path):
    req = tmp_path / "requirements.txt"
    req.write_text("numpy==1.26.0\npytest>=7.0\n", encoding="utf-8")

    rc = da.main(
        [
            "--repo-root",
            str(tmp_path),
            "--json-out",
            "deps.json",
            "--md-out",
            "deps.md",
        ]
    )
    assert rc == 0, "rc is not valid"
    json_out = tmp_path / "deps.json"
    md_out = tmp_path / "deps.md"
    assert json_out.exists(), "Condition must be true"
    assert md_out.exists(), "Condition must be true"

    data = json.loads(json_out.read_text(encoding="utf-8"))
    assert data["summary"]["total_dependencies"] == 2, "Data must not be empty"
    names = {d["name"] for d in data["dependencies"]}
    assert "numpy" in names, "Condition must be true"
    assert "pytest" in names, "Condition must be true"
