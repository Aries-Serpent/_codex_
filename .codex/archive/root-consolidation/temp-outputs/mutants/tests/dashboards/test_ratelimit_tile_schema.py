"""
Test Ratelimit Tile Schema

Test module for ratelimit tile schema.
"""

import json
import subprocess
import sys
from pathlib import Path


def test_ratelimit_tile_validates(tmp_path):
    tile = {
        "generated_utc": "2025-11-02T00:00:00Z",
        "title": "GitHub Rate-Limit (7d)",
        "series": {
            "core": [["2025-11-01T00:00:00Z", 4500], ["2025-11-02T00:00:00Z", 4400]],
            "search": [["2025-11-01T00:00:00Z", 180], ["2025-11-02T00:00:00Z", 175]],
            "graphql": [["2025-11-01T00:00:00Z", 5000], ["2025-11-02T00:00:00Z", 4990]],
        },
        "summary": {
            "core": {"min": 4400, "avg": 4450, "max": 4500},
            "search": {"min": 175, "avg": 177.5, "max": 180},
            "graphql": {"min": 4990, "avg": 4995, "max": 5000},
        },
    }
    data_p = tmp_path / "tile.json"
    schema_p = tmp_path / "schema.json"
    repo_root = Path(__file__).resolve().parents[2]
    data_p.write_text(json.dumps(tile), encoding="utf-8")
    schema_src = repo_root / "configs" / "schemas" / "ratelimit_tile.schema.json"
    schema_p.write_text(schema_src.read_text(encoding="utf-8"), encoding="utf-8")
    validator = repo_root / "tools" / "schema_validate.py"
    code = subprocess.call(
        [sys.executable, str(validator), "--data", str(data_p), "--schema", str(schema_p)]
    )
    assert code == 0, "code is not valid"
