"""
Test Toy Trainer Perf Snapshot

Test module for toy trainer perf snapshot.
"""

import json
import subprocess
import sys

import pytest


@pytest.mark.timeout(30)
def test_toy_trainer_generates_perf_and_parse(tmp_path, monkeypatch):
    # Run toy trainer to produce a log
    log = tmp_path / "train.log"
    code = subprocess.call(
        [
            sys.executable,
            "-m",
            "src.codex_ml.training.toy_trainer",
            "--epochs",
            "1",
            "--batch-size",
            "8",
            "--log",
            str(log),
        ]
    )
    assert code == 0, "code is not valid"
    assert log.exists(), "Condition must be true"

    # Parse perf snapshot
    out = tmp_path / "perf.json"
    code = subprocess.call(
        [sys.executable, "tools/perf_snapshot.py", "--log", str(log), "--out", str(out)]
    )
    assert code == 0, "code is not valid"
    data = json.loads(out.read_text(encoding="utf-8"))
    assert isinstance(data.get("training", {}).get("throughput_steps_per_sec", 0), (int, float))
