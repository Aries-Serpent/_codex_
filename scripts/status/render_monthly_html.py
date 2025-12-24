#!/usr/bin/env python3
"""
Render a monthly HTML report from a bundle JSON containing aggregated status reports.

Usage:
  python scripts/status/render_monthly_html.py --in bundle.json --out bundle.html
"""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def default_template() -> str:
    """Minimal inline template for monthly reports."""
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{{title}}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,Cantarell,Noto Sans,sans-serif;line-height:1.5;margin:2rem;color:#111}
    h1,h2{margin:0.5rem 0}
    .meta, .grid {margin: 0.5rem 0}
    .grid {display:grid;grid-template-columns: repeat(3, minmax(0,1fr)); gap: 1rem;}
    .card{border:1px solid #eee;border-radius:8px;padding:1rem}
    table{border-collapse:collapse;width:100%;margin:1rem 0}
    th,td{border:1px solid #ddd;padding:0.5rem;text-align:left}
    .small{color:#666;font-size:0.9rem}
    code{background:#f7f7f7;padding:0.1rem 0.3rem;border-radius:4px}
  </style>
</head>
<body>
  <h1>{{title}}</h1>
  <div class="meta small">
    <div>Month: {{month}}</div>
  </div>

  <h2>Summary</h2>
  <div class="grid">
    <div class="card">
      <strong>Reports</strong>
      <div>{{reports_count}}</div>
    </div>
    <div class="card">
      <strong>Avg Coverage</strong>
      <div>{{avg_coverage}}%</div>
    </div>
    <div class="card">
      <strong>Total Findings</strong>
      <div>{{total_findings}}</div>
    </div>
  </div>

  <h2>Reports</h2>
  <table>
    <thead><tr><th>Timestamp (UTC)</th><th>Coverage (%)</th><th>Findings</th></tr></thead>
    <tbody>
    {{reports_rows}}
    </tbody>
  </table>
</body>
</html>
"""


def render_reports_rows(data: dict[str, Any]) -> str:
    """Render table rows for each report in the bundle."""
    rows = []
    for report in data.get("reports", []):
        meta = report.get("metadata", {})
        snapshot = report.get("snapshot", {})
        tests_gates = snapshot.get("tests_gates", {})
        findings = snapshot.get("findings", [])

        timestamp = html.escape(str(meta.get("timestamp_utc", "")))
        coverage = html.escape(str(tests_gates.get("coverage_percent", "N/A")))
        findings_count = len(findings)

        parts = [
            "<tr>",
            f"<td>{timestamp}</td>",
            f"<td>{coverage}</td>",
            f"<td>{findings_count}</td>",
            "</tr>",
        ]
        rows.append("".join(parts))
    return "\n".join(rows) or '<tr><td colspan="3" class="small">No reports</td></tr>'


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="input", required=True, help="Input bundle JSON file")
    ap.add_argument("--out", required=True, help="Output HTML file")
    args = ap.parse_args(argv)

    data = load_json(Path(args.input))
    tpl = default_template()

    month = data.get("month", "")
    summary = data.get("summary", {})

    html_out = (
        tpl.replace("{{title}}", f"Status Monthly — {html.escape(month)}")
        .replace("{{month}}", html.escape(month))
        .replace("{{reports_count}}", str(summary.get("reports_count", 0)))
        .replace("{{avg_coverage}}", str(summary.get("avg_coverage", 0)))
        .replace("{{total_findings}}", str(summary.get("total_findings", 0)))
        .replace("{{reports_rows}}", render_reports_rows(data))
    )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html_out, encoding="utf-8")
    print(f"[OK] Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
