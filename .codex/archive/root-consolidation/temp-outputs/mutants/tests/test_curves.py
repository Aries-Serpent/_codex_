"""Check metric curve helpers."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def test_append_and_summarize(tmp_path):
    from codex_ml.metrics.curves import append_curve, summarize

    path = tmp_path / "curves"
    path.mkdir()
    append_curve(path, "loss", 1, 0.5)
    append_curve(path, "loss", 2, 0.2)

    summary = summarize(path, "loss")
    assert summary["count"] == 2, "Count must be greater than zero"
    assert summary["mean"] > 0, "Value must be greater than zero"
