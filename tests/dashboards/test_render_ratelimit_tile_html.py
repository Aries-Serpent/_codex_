"""
Test Render Ratelimit Tile Html

Test module for render ratelimit tile html.
"""

import json
import subprocess
import sys
from pathlib import Path


def test_render_tile_html(tmp_path):
    tile = {
        "generated_utc": "2025-11-02T00:00:00Z",
        "title": "GitHub Rate-Limit (7d)",
        "series": {
            "core": [["2025-11-01T00:00:00Z", 1], ["2025-11-02T00:00:00Z", 2]],
            "search": [["2025-11-01T00:00:00Z", 1], ["2025-11-02T00:00:00Z", 2]],
            "graphql": [["2025-11-01T00:00:00Z", 1], ["2025-11-02T00:00:00Z", 2]],
        },
        "summary": {
            "core": {"min": 1, "avg": 1.5, "max": 2},
            "search": {"min": 1, "avg": 1.5, "max": 2},
            "graphql": {"min": 1, "avg": 1.5, "max": 2},
        },
    }
    tile_p = tmp_path / "ratelimit_tile.json"
    out_p = tmp_path / "ratelimit_tile.html"
    repo_root = Path(__file__).resolve().parents[2]
    tile_p.write_text(json.dumps(tile), encoding="utf-8")
    renderer = repo_root / "scripts" / "dashboards" / "render_ratelimit_tile_html.py"
    code = subprocess.call(
        [sys.executable, str(renderer), "--tile", str(tile_p), "--out", str(out_p)]
    )
    assert code == 0, "code is not valid"
    assert out_p.exists(), "Condition must be true"
    html = out_p.read_text(encoding="utf-8")
    assert "<svg" in html and "GitHub Rate-Limit (7d)" in html, "Condition must be true"
