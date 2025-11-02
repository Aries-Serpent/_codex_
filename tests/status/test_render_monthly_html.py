import json
from pathlib import Path
import subprocess
import sys


def write_bundle(p: Path):
    bundle = {
        "month": "2025-11",
        "summary": {"reports_count": 2, "avg_coverage": 42.5, "total_findings": 3},
        "reports": [
            {
                "metadata": {"timestamp_utc": "2025-11-01T00:00:00Z"},
                "snapshot": {"tests_gates": {"coverage_percent": 41.0}, "findings": [{"id": "FIND-001"}]},
            },
            {
                "metadata": {"timestamp_utc": "2025-11-02T00:00:00Z"},
                "snapshot": {"tests_gates": {"coverage_percent": 44.0}, "findings": [{"id": "FIND-002"}, {"id": "FIND-003"}]},
            },
        ],
    }
    p.write_text(json.dumps(bundle), encoding="utf-8")


def test_render_monthly_html(tmp_path):
    src = tmp_path / "bundle.json"
    out = tmp_path / "bundle.html"
    write_bundle(src)
    code = subprocess.call([sys.executable, "scripts/status/render_monthly_html.py", "--in", str(src), "--out", str(out)])
    assert code == 0
    html = out.read_text(encoding="utf-8")
    assert "Status Monthly — 2025-11" in html
    assert "Reports" in html and "Avg Coverage" in html and "Total Findings" in html
    assert "2025-11-01T00:00:00Z" in html and "2025-11-02T00:00:00Z" in html
