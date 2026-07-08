"""
Test Prune Rate Limit History

Test module for prune rate limit history.
"""

import subprocess
import sys
from datetime import datetime, timedelta, timezone


def create_hist(root, dt):
    path = root / f"ratelimit_{dt.strftime('%Y%m%dT%H%M%SZ')}.json"
    path.write_text("{}", encoding="utf-8")


def test_prune_removes_old(tmp_path):
    root = tmp_path / "connectors/history"
    root.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    create_hist(root, now - timedelta(days=120))
    create_hist(root, now - timedelta(days=10))

    code = subprocess.call(
        [
            sys.executable,
            "scripts/connectors/prune_rate_limit_history.py",
            "--root",
            str(root),
            "--days",
            "90",
        ]
    )
    assert code == 0, "code is not valid"

    files = list(root.glob("ratelimit_*.json"))
    assert len(files) == 1, "Files must not be empty"
