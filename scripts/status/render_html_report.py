#!/usr/bin/env python3
"""
Render Html Report

Purpose:
    Command-line utility (see argument parser for details)

Usage:
    python scripts/status/render_html_report.py [options]
    
    Examples:
    $ python scripts/status/render_html_report.py --help

Arguments:
    [To be documented]

Environment Variables:
    [To be documented]

Dependencies:
    [To be documented]

Exit Codes:
    0: Success
    1: Error

Author: Codex Team
Last Updated: 2026-01-16
"""


"""
Render an HTML report from a v1.2 status JSON using a simple HTML template.

Usage:
  python scripts/status/render_html_report.py --json reports/daily/2025-11-02.json --out reports/daily/2025-11-02.html [--template docs/templates/status/report_template.html]
"""
from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def default_template() -> str:
    # Minimal inline template if none provided
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
    .grid {display:grid;grid-template-columns: repeat(2, minmax(0,1fr)); gap: 1rem;}
    .card{border:1px solid #eee;border-radius:8px;padding:1rem}
    table{border-collapse:collapse;width:100%}
    th,td{border:1px solid #ddd;padding:0.5rem;text-align:left}
    .small{color:#666;font-size:0.9rem}
    code{background:#f7f7f7;padding:0.1rem 0.3rem;border-radius:4px}
  </style>
</head>
<body>
  <h1>{{title}}</h1>
  <div class="meta small">
    <div>Generated (UTC): {{timestamp_utc}}</div>
    <div>Template Version: {{template_version}}</div>
    <div>Branch: {{branch}} @ {{sha}}</div>
    <div>Python: {{python_version}} | OS: {{os}}</div>
  </div>

  <h2>1. Snapshot</h2>
  <div class="grid">
    <div class="card">
      <strong>Capabilities</strong>
      <div>{{capabilities_count}}</div>
    </div>
    <div class="card">
      <strong>Findings</strong>
      <div>{{findings_count}}</div>
    </div>
    <div class="card">
      <strong>Coverage (%)</strong>
      <div>{{coverage_percent}}</div>
    </div>
    <div class="card">
      <strong>Coverage Threshold (%)</strong>
      <div>{{coverage_threshold}}</div>
    </div>
  </div>

  <h2>2. Capabilities</h2>
  <table>
    <thead><tr><th>ID</th><th>Name</th><th>Status</th><th>Severity</th><th>Confidence</th><th>Evidence</th></tr></thead>
    <tbody>
    {{capabilities_rows}}
    </tbody>
  </table>

  <h2>3. Findings</h2>
  <table>
    <thead><tr><th>ID</th><th>Title</th><th>Severity</th><th>Confidence</th><th>Status</th><th>Proposed Action</th></tr></thead>
    <tbody>
    {{findings_rows}}
    </tbody>
  </table>

  <h2>4. Patches</h2>
  <table>
    <thead><tr><th>ID</th><th>Title</th><th>Risk</th><th>Confidence</th><th>Status</th></tr></thead>
    <tbody>
    {{patches_rows}}
    </tbody>
  </table>

  <h2>5. Delta</h2>
  <div class="small">Coverage Δ: {{coverage_delta}} (prev {{coverage_prev}} → curr {{coverage_curr}})</div>
</body>
</html>
"""


def render_rows_caps(data: dict[str, Any]) -> str:
    rows = []
    for c in data.get("snapshot", {}).get("capabilities", []):
        parts = [
            "<tr>",
            f"<td>{html.escape(str(c.get('id', '')))}</td>",
            f"<td>{html.escape(str(c.get('name', '')))}</td>",
            f"<td>{html.escape(str(c.get('status', '')))}</td>",
            f"<td>{html.escape(str(c.get('severity', '')))}</td>",
            f"<td>{html.escape(str(c.get('confidence', '')))}</td>",
            f"<td><code>{html.escape(str(c.get('artifacts', '')))}</code></td>",
            "</tr>",
        ]
        rows.append("".join(parts))
    return "\n".join(rows) or '<tr><td colspan="6" class="small">N/A</td></tr>'


def render_rows_findings(data: dict[str, Any]) -> str:
    rows = []
    for f in data.get("snapshot", {}).get("findings", []):
        parts = [
            "<tr>",
            f"<td>{html.escape(str(f.get('id', '')))}</td>",
            f"<td>{html.escape(str(f.get('title', '')))}</td>",
            f"<td>{html.escape(str(f.get('severity', '')))}</td>",
            f"<td>{html.escape(str(f.get('confidence', '')))}</td>",
            f"<td>{html.escape(str(f.get('status', '')))}</td>",
            f"<td>{html.escape(str(f.get('proposed_action', '')))}</td>",
            "</tr>",
        ]
        rows.append("".join(parts))
    return "\n".join(rows) or '<tr><td colspan="6" class="small">N/A</td></tr>'


def render_rows_patches(data: dict[str, Any]) -> str:
    rows = []
    for p in data.get("patches", []):
        parts = [
            "<tr>",
            f"<td>{html.escape(str(p.get('id', '')))}</td>",
            f"<td>{html.escape(str(p.get('title', '')))}</td>",
            f"<td>{html.escape(str(p.get('risk', '')))}</td>",
            f"<td>{html.escape(str(p.get('confidence', '')))}</td>",
            f"<td>{html.escape(str(p.get('status', '')))}</td>",
            "</tr>",
        ]
        rows.append("".join(parts))
    return "\n".join(rows) or '<tr><td colspan="5" class="small">N/A</td></tr>'


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--template", default="")
    args = ap.parse_args(argv)

    # Validate paths to prevent path traversal attacks
    # Allow absolute paths, but prevent relative paths with .. components
    for name, path_str in [
        ("json", args.json),
        ("template", args.template if args.template else None),
    ]:
        if path_str and ".." in Path(path_str).parts:
            print(f"Error: Path traversal detected in {name} path", file=sys.stderr)
            return 1

    data = load_json(Path(args.json))

    # Load template
    if args.template:
        template_path = Path(args.template)
        tpl = (
            template_path.read_text(encoding="utf-8")
            if template_path.exists()
            else default_template()
        )
    else:
        tpl = default_template()

    meta = data.get("metadata", {})
    gc = meta.get("git_context", {}) or {}
    env = meta.get("environment", {}) or {}
    tests = data.get("snapshot", {}).get("tests_gates", {}) or {}
    delta_cov = (data.get("delta", {}) or {}).get("tests_coverage_delta", {}) or {}

    html_out = (
        tpl.replace("{{title}}", html.escape(meta.get("title", "")))
        .replace("{{timestamp_utc}}", html.escape(meta.get("timestamp_utc", "")))
        .replace("{{template_version}}", html.escape(meta.get("template_version", "")))
        .replace("{{branch}}", html.escape(gc.get("branch", "")))
        .replace("{{sha}}", html.escape(gc.get("commit_sha_short", "")))
        .replace("{{python_version}}", html.escape(env.get("python_version", "")))
        .replace("{{os}}", html.escape(env.get("os", "")))
        .replace(
            "{{capabilities_count}}", str(len(data.get("snapshot", {}).get("capabilities", [])))
        )
        .replace("{{findings_count}}", str(len(data.get("snapshot", {}).get("findings", []))))
        .replace("{{coverage_percent}}", str(tests.get("coverage_percent", "")))
        .replace("{{coverage_threshold}}", str(tests.get("coverage_threshold", "")))
        .replace("{{capabilities_rows}}", render_rows_caps(data))
        .replace("{{findings_rows}}", render_rows_findings(data))
        .replace("{{patches_rows}}", render_rows_patches(data))
        .replace("{{coverage_delta}}", str(delta_cov.get("delta_percent", "")))
        .replace("{{coverage_prev}}", str(delta_cov.get("previous_percent", "")))
        .replace("{{coverage_curr}}", str(delta_cov.get("current_percent", "")))
    )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html_out, encoding="utf-8")
    print(f"[OK] Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
