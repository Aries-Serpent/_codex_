"""Tests for :mod:`codex_ml.tracking.offline`."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def test_decide_offline_prefers_file_uri(monkeypatch, tmp_path):
    from codex_ml.tracking.offline import decide_offline, export_env_lines

    monkeypatch.setenv("MLFLOW_TRACKING_URI", "")
    decision = decide_offline(prefer_offline=True, allow_remote=False, mlruns_dir=tmp_path)

    assert decision.offline is True, "offline is not valid"
    assert decision.mlflow_tracking_uri.startswith("file:"), "Condition must be true"
    exports = export_env_lines(decision)
    assert "MLFLOW_TRACKING_URI" in exports, "Condition must be true"


def test_ndjson_logger_writes_and_rotates(tmp_path):
    from codex_ml.tracking.offline import NDJSONLogger

    log_path = tmp_path / "metrics.ndjson"
    logger = NDJSONLogger(log_path, max_bytes=30, backup_count=1, enable_rotation=True)
    for idx in range(3):
        logger.write({"step": idx})

    assert log_path.exists(), "Condition must be true"
    rotated = log_path.with_name(log_path.name + ".1")
    assert rotated.exists(), "Condition must be true"
    assert "step" in log_path.read_text(), "Condition must be true"
