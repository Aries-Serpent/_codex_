#!/usr/bin/env python3
"""
Render Ratelimit Tile Html

Purpose:
    Command-line utility (see argument parser for details)

Usage:
    python scripts/dashboards/render_ratelimit_tile_html.py [options]

    Examples:
    $ python scripts/dashboards/render_ratelimit_tile_html.py --help

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

import argparse
import html
import json
from pathlib import Path


def load_tile(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def scale_points(
    series: list[tuple[str, int]], width: int, height: int, pad: int = 20
) -> list[tuple[float, float]]:
    if not series:
        return []
    xs = list(range(len(series)))
    ys = [value for _, value in series]
    min_y, max_y = (min(ys), max(ys)) if ys else (0, 1)
    if max_y == min_y:
        max_y = min_y + 1
    sx = (width - 2 * pad) / max(1, (len(xs) - 1))

    def norm_y(value: float) -> float:
        return pad + (height - 2 * pad) * (1 - (value - min_y) / (max_y - min_y))

    return [(pad + index * sx, norm_y(value)) for index, value in enumerate(ys)]


def to_polyline(points: list[tuple[float, float]], color: str) -> str:
    if not points:
        return ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline fill="none" stroke="{color}" stroke-width="2" points="{pts}"/>'


def to_circles(points: list[tuple[float, float]], color: str) -> str:
    return "\n".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2" fill="{color}"/>' for x, y in points)


def render_html(tile: dict, width: int = 800, height: int = 240) -> str:
    title = html.escape(str(tile.get("title", "Rate-Limit (7d)")))
    series = tile.get("series", {})
    core = series.get("core", [])
    search = series.get("search", [])
    graphql = series.get("graphql", [])

    core_pts = scale_points(core, width, height)
    search_pts = scale_points(search, width, height)
    graphql_pts = scale_points(graphql, width, height)

    svg_parts = [
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{title}">',
        '<rect x="0" y="0" width="100%" height="100%" fill="#ffffff" />',
        to_polyline(core_pts, "#2563eb"),
        to_circles(core_pts, "#2563eb"),
        to_polyline(search_pts, "#65a30d"),
        to_circles(search_pts, "#65a30d"),
        to_polyline(graphql_pts, "#dc2626"),
        to_circles(graphql_pts, "#dc2626"),
        "</svg>",
    ]
    svg = "\n".join(filter(None, svg_parts))

    summaries = tile.get("summary", {})

    def summary_row(name: str, key: str, color: str) -> str:
        summary = summaries.get(key, {"min": 0, "max": 0, "avg": 0})
        return (
            "<tr>"
            f"<td><span style='color:{color};font-weight:600'>{name}</span></td>"
            f"<td>{summary.get('min', 0)}</td>"
            f"<td>{summary.get('avg', 0)}</td>"
            f"<td>{summary.get('max', 0)}</td>"
            "</tr>"
        )

    table = "\n".join(
        [
            "<table>",
            "<thead><tr><th>Resource</th><th>Min</th><th>Avg</th><th>Max</th></tr></thead>",
            "<tbody>",
            summary_row("core", "core", "#2563eb"),
            summary_row("search", "search", "#65a30d"),
            summary_row("graphql", "graphql", "#dc2626"),
            "</tbody>",
            "</table>",
        ]
    )

    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <title>{title}</title>
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <style>
    body{{font-family:system-ui,-apple-system,'Segoe UI',Roboto,Ubuntu,Cantarell,'Noto Sans',sans-serif;margin:2rem;color:#111}}
    h1{{margin:0 0 1rem 0}}
    table{{border-collapse:collapse;margin-top:1rem}}
    th,td{{border:1px solid #ddd;padding:0.4rem 0.6rem;text-align:left}}
    th{{background:#f3f4f6}}
  </style>
</head>
<body>
  <h1>{title}</h1>
  {svg}
  {table}
</body>
</html>
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Render an HTML chart for a rate-limit tile JSON document"
    )
    parser.add_argument("--tile", default=".codex/reports/tiles/ratelimit_tile.json")
    parser.add_argument("--out", default=".codex/reports/tiles/ratelimit_tile.html")
    parser.add_argument("--width", type=int, default=800)
    parser.add_argument("--height", type=int, default=240)
    args = parser.parse_args(argv)

    tile = load_tile(Path(args.tile))
    html_doc = render_html(tile, args.width, args.height)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html_doc, encoding="utf-8")
    print(f"[OK] Wrote {out_path}")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
