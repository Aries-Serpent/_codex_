from pathlib import Path
import json

import tools.codex_secret_scan_stub as ss


def test_secret_scan_stub_detects_pattern(tmp_path: Path):
    src = tmp_path / "test_secrets.py"
    src.write_text(
        "api_key = 'AWS_SECRET_ACCESS_KEY=abc123'\n" "print('hello')\n",
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
    assert rc == 0

    json_out = tmp_path / "secrets.json"
    md_out = tmp_path / "secrets.md"
    assert json_out.exists()
    assert md_out.exists()

    data = json.loads(json_out.read_text(encoding="utf-8"))
    assert data["total_findings"] >= 1
    first = data["findings"][0]
    assert "AWS_SECRET_ACCESS_KEY" in first["snippet"]
