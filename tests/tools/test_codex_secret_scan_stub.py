"""
Test Codex Secret Scan Stub

Test module for codex secret scan stub.
"""

import json
from pathlib import Path

import tools.codex_secret_scan_stub as ss


def test_secret_scan_stub_detects_pattern(tmp_path: Path):
    src = tmp_path / "test_secrets.py"
    src.write_text(
        "api_key = 'AWS_SECRET_ACCESS_KEY=abc123'\nprint('hello')\n",
        encoding="utf-8",
    )

    rc = ss.main(
        [
            "--repo-root",
            str(tmp_path),
            "--json-out",
            "secrets.json",
            "--md-out",
            "secrets.md",
        ]
    )
    assert rc == 0, "rc is not valid"

    json_out = tmp_path / "secrets.json"
    md_out = tmp_path / "secrets.md"
    assert json_out.exists(), "Condition must be true"
    assert md_out.exists(), "Condition must be true"

    data = json.loads(json_out.read_text(encoding="utf-8"))
    assert data["total_findings"] >= 1, "Value must be greater than zero"
    first = data["findings"][0]
    # Snippet is sanitized before storage — accept any redaction sentinel.
    assert (, "Condition must be true"
        "AWS_SECRET" in first["snippet"]
        or "[REDACTED]" in first["snippet"]
        or first["snippet"] == "<redacted>"
    )
