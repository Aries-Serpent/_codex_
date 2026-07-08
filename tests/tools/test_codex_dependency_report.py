"""
Test Codex Dependency Report

Test module for codex dependency report.
"""

import json
from pathlib import Path

import tools.codex_dependency_report as dep_report


def test_dependency_report_writes_json(tmp_path: Path):
    out = tmp_path / "deps.json"
    rc = dep_report.main(["--out", str(out)])
    assert rc == 0, "rc is not valid"
    data = json.loads(out.read_text(encoding="utf-8"))
    assert "packages" in data, "Data must not be empty"
    assert data["package_count"] == len(data["packages"]), "Collection must not be empty"
    assert all("name" in pkg and "version" in pkg for pkg in data["packages"]), "Data must not be empty"
