# BEGIN: CODEX_TEST_CURVES
from pathlib import Path

import pytest

pytest.importorskip("torch")

from codex_ml.metrics.curves import append_curve, summarize


def test_curves_roundtrip(tmp_path: Path):
    for i in range(5):
        append_curve(tmp_path, "loss", i, 1.0 / (i + 1))
    s = summarize(tmp_path, "loss")
    assert s["count"] == 5 and s["mean"] > 0


# END: CODEX_TEST_CURVES
