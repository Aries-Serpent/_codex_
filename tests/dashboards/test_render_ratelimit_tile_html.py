import json
import subprocess
import sys

import pytest

from scripts.dashboards.render_ratelimit_tile_html import scale_points


@pytest.mark.parametrize(
    "values",
    [
        [("a", 5)],
        [("a", 3), ("b", 3), ("c", 3)],
    ],
)
def test_scale_points_handles_constant_series(values):
    width, height = 120, 100
    points = scale_points(values, width, height)

    assert len(points) == len(values)

    xs = [p[0] for p in points]
    assert xs == sorted(xs)
    assert xs[0] >= 20
    assert xs[-1] <= width - 20

    ys = [p[1] for p in points]
    assert max(ys) - min(ys) < 1e-6


def test_render_main_writes_html(tmp_path):
    reports_dir = tmp_path / "reports/tiles"
    reports_dir.mkdir(parents=True)
    tile_data = {
        "title": "My Tile",
        "series": {
            "core": [["2024-01-01", 4500], ["2024-01-02", 4490]],
            "search": [["2024-01-01", 180], ["2024-01-02", 175]],
            "graphql": [["2024-01-01", 5000], ["2024-01-02", 4995]],
        },
        "summary": {
            "core": {"min": 4400, "avg": 4450, "max": 4500},
            "search": {"min": 170, "avg": 175, "max": 180},
            "graphql": {"min": 4900, "avg": 4950, "max": 5000},
        },
    }
    tile_path = reports_dir / "ratelimit_tile.json"
    tile_path.write_text(json.dumps(tile_data), encoding="utf-8")

    code = subprocess.call(
        [
            sys.executable,
            "-c",
            "import scripts.dashboards.render_ratelimit_tile_html as m; m.main()",
        ],
        cwd=tmp_path,
    )
    assert code == 0

    html_path = reports_dir / "ratelimit_tile.html"
    html = html_path.read_text(encoding="utf-8")

    assert "<svg" in html
    assert "polyline" in html
    assert "<table" in html
    assert html.count("My Tile") >= 2
