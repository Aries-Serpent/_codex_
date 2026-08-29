#!/usr/bin/env python3
"""
Build Tiles Index

Purpose:
    Builds tiles_index

Usage:
    python scripts/dashboards/build_tiles_index.py [options]

    Examples:
    $ python scripts/dashboards/build_tiles_index.py --help

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


from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path


def main(argv=None) -> int:
    tiles_dir = Path(".codex/reports/tiles")
    out_dir = Path("public/tiles")
    out_dir.mkdir(parents=True, exist_ok=True)

    # Copy HTML tiles and index them
    items = []
    for p in sorted(tiles_dir.glob("*.html")):
        dest = out_dir / p.name
        dest.write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
        items.append(p.name)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lis = "\n".join(f'<li><a href="{name}">{name}</a></li>' for name in reversed(items))
    index = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>_codex_ — Dashboard Tiles</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>body{{font-family:system-ui,Arial,sans-serif;margin:2rem}}h1{{margin:0 0 1rem}}</style>
</head>
<body>
  <h1>Dashboard Tiles</h1>
  <div>Updated: {ts}</div>
  <ul>
    {lis or '<li>N/A</li>'}
  </ul>
</body>
</html>
"""
    (out_dir / "index.html").write_text(index, encoding="utf-8")
    print(f"[OK] Built tiles index with {len(items)} item(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
