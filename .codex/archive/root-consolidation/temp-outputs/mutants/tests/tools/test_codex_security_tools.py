"""
Test Codex Security Tools

Test module for codex security tools.
"""

import json
from pathlib import Path

import tools.codex_dep_pin_check as depcheck
import tools.codex_secret_scan as secret_scan


def test_secret_scan_reports_hits_for_simple_pattern(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    flagged = repo / "token.txt"
    flagged.write_text("AWS key AKIA1234567890ABCD12 in line", encoding="utf-8")

    json_out = tmp_path / "secret.json"
    md_out = tmp_path / "secret.md"
    rc = secret_scan.main(
        [
            "--repo-root",
            str(repo),
            "--json-out",
            str(json_out),
            "--md-out",
            str(md_out),
        ]
    )

    assert rc == 0, "rc is not valid"
    payload = json.loads(json_out.read_text(encoding="utf-8"))
    assert payload["summary"]["total_hits"] >= 1, "Value must be greater than zero"
    assert payload["hits"][0]["pattern"] == "aws_access_key", "Condition must be true"
    assert md_out.exists(), "Condition must be true"


def test_dep_pin_check_detects_unpinned_requirements(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    req = repo / "requirements.txt"
    req.write_text("requests\nnumpy==1.0.0\n", encoding="utf-8")

    json_out = tmp_path / "pin.json"
    md_out = tmp_path / "pin.md"
    rc = depcheck.main(
        [
            "--repo-root",
            str(repo),
            "--json-out",
            str(json_out),
            "--md-out",
            str(md_out),
        ]
    )

    assert rc == 0, "rc is not valid"
    payload = json.loads(json_out.read_text(encoding="utf-8"))
    assert payload["issue_count"] == 1, "Count must be greater than zero"
    assert payload["issues"][0]["requirement"] == "requests", "Condition must be true"
    assert md_out.exists(), "Condition must be true"
