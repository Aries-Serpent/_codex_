"""
Test Perf Snapshot

Test module for perf snapshot.
"""

import json
import subprocess
import sys

from tools.perf_snapshot import parse_perf_log

LOG = """steps/s: 12.5
epoch_time_s: 44.2
latency_p50_ms: 9.8
"""


def test_perf_snapshot_parses_tmp(tmp_path):
    log = tmp_path / "perf.log"
    out = tmp_path / "perf.json"
    log.write_text(LOG, encoding="utf-8")
    code = subprocess.call(
        [
            sys.executable,
            "-m",
            "tools.perf_snapshot",
            "--log",
            str(log),
            "--out",
            str(out),
        ]
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
        [
            sys.executable,
            "-m",
            "tools.perf_snapshot",
            "--log",
            str(log),
            "--out",
            str(out),
        ]
    )
    assert code == 0, "code is not valid"
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data == {"raw": {}}, "Data must not be empty"


def test_perf_snapshot_parses_trainer_rows():
    snapshot = parse_perf_log(
        "epoch=1 loss=1.25 steps/s: 40.0 epoch_time_s: 0.2\n"
        "epoch=2 loss=1.0 steps/s: 50.0 epoch_time_s: 0.16\n"
    )

    assert snapshot["training"] == {
        "loss": 1.0,
        "throughput_steps_per_sec": 50.0,
        "epoch_time_seconds": 0.16,
    }
    assert snapshot["raw"]["epoch"] == 2.0


def test_perf_snapshot_parses_mixed_row_with_one_colon():
    snapshot = parse_perf_log("epoch=3 steps/s: 75\n")

    assert snapshot["training"] == {"throughput_steps_per_sec": 75.0}
    assert snapshot["raw"] == {"epoch": 3.0, "steps/s": 75.0}


def test_perf_snapshot_preserves_legacy_keys_and_ignores_invalid_fields():
    snapshot = parse_perf_log(
        "# steps/s: 999\n"
        "custom metric: 2.5\n"
        "noise without metrics\n"
        "loss=invalid steps/s: 1.25e2 epoch_time_s: -0.5\n"
    )

    assert snapshot["raw"] == {
        "custom metric": 2.5,
        "steps/s": 125.0,
        "epoch_time_s": -0.5,
    }
    assert snapshot["training"] == {
        "throughput_steps_per_sec": 125.0,
        "epoch_time_seconds": -0.5,
    }
