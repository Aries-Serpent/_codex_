"""
Test Build Ratelimit Tile

Test module for build ratelimit tile.
"""

import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone


def write_entry(path, remaining_core, remaining_search, remaining_graphql, dt):
    data = {
        "captured_utc": dt.isoformat(),
        "data": {
            "resources": {
                "core": {"remaining": remaining_core},
                "search": {"remaining": remaining_search},
                "graphql": {"remaining": remaining_graphql},
            }
        },
    }
    path.write_text(json.dumps(data), encoding="utf-8")


def test_build_ratelimit_tile_from_history(tmp_path):
    history_dir = tmp_path / "connectors/history"
    history_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    for i in range(3):
        ts = now - timedelta(days=i)
        write_entry(
            history_dir / f"ratelimit_{ts.strftime('%Y%m%dT%H%M%SZ')}.json",
            4500 - i,
            180 - i,
            5000 - i,
            ts,
        )

    (tmp_path / "reports/tiles").mkdir(parents=True, exist_ok=True)

    code = subprocess.call(
        [
            sys.executable,
            "-c",
            "import scripts.dashboards.build_ratelimit_tile as m; m.main()",
        ],
        cwd=tmp_path,
    )
    assert code == 0, "code is not valid"

    tile = json.loads((tmp_path / "reports/tiles/ratelimit_tile.json").read_text(encoding="utf-8"))
    assert "series" in tile and "core" in tile["series"], "Condition must be true"
    assert len(tile["series"]["core"]) >= 1, "Collection must not be empty"
