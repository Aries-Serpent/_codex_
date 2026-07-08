"""
Test Perf Snapshot

Test module for perf snapshot.
"""

import json
import subprocess
import sys

LOG = """steps/s: 12.5
epoch_time_s: 44.2
latency_p50_ms: 9.8
"""


def test_perf_snapshot_parses_tmp(tmp_path):
    log = tmp_path / "perf.log"
    out = tmp_path / "perf.json"
    log.write_text(LOG, encoding="utf-8")
    code = subprocess.call(
        [sys.executable, "tools/perf_snapshot.py", "--log", str(log), "--out", str(out)]
    )
    assert code == 0, "code is not valid"
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["training"]["throughput_steps_per_sec"] == 12.5, "Data must not be empty"
    assert data["training"]["epoch_time_seconds"] == 44.2, "Data must not be empty"
    assert data["inference"]["latency_p50_ms"] == 9.8, "Data must not be empty"


def test_perf_snapshot_handles_missing_log(tmp_path):
    log = tmp_path / "missing.log"
    out = tmp_path / "perf.json"
    code = subprocess.call(
        [sys.executable, "tools/perf_snapshot.py", "--log", str(log), "--out", str(out)]
    )
    assert code == 0, "code is not valid"
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data == {"raw": {}}, "Data must not be empty"
