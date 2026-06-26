"""
Test Static Code Analysis Step

Test module for static code analysis step.
"""

import json
from pathlib import Path

from analysis.audit_pipeline import step_static_code_analysis


def test_static_code_analysis_logs(tmp_path: Path) -> None:
    # Use a small synthetic directory to avoid compiling thousands of repo files.
    (tmp_path / "valid.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "another.py").write_text("def f():\n    return 42\n", encoding="utf-8")

    metrics = tmp_path / "m.jsonl"
    step_static_code_analysis(tmp_path, metrics)
    data = metrics.read_text().strip().splitlines()
    assert data, "Data must not be empty"
    record = json.loads(data[-1])
    assert record["name"] == "static.analysis.errors", "Error should be raised or set"
    assert isinstance(record["value"], int)
    assert record["value"] >= 0, "rec must be greater than zero"
