#!/usr/bin/env python3
"""
Render a Markdown report from a v1.2 status JSON using simple templates.

Usage:
  python scripts/status/render_markdown_report.py --json reports/daily/2025-11-02.json --out reports/daily/2025-11-02.md
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    
    data = json.loads(Path(args.json).read_text(encoding="utf-8"))
    md = []
    md.append(f"# {data['metadata']['title']}")
    md.append("")
    md.append(f"- Generated (UTC): {data['metadata'].get('timestamp_utc','')}")
    md.append(f"- Template Version: {data['metadata'].get('template_version','')}")
    md.append("")
    md.append("## 1. Executive Summary")
    md.append("- Fill this section from JSON fields as needed.")
    
    md_text = "\n".join(md)
    Path(args.out).write_text(md_text, encoding="utf-8")
    print(f"[OK] Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
