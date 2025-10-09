from __future__ import annotations

import json
import math
import tempfile
from pathlib import Path

from hypothesis import given, strategies as st

from codex_ml.cli.ndjson_summary import NdjsonSummarizer


@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=50))
def test_summarizer_tracks_loss_bounds(values: list[float]) -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        run_dir = Path(tmp_dir)
        path = run_dir / "metrics.ndjson"
        with path.open("w", encoding="utf-8") as fh:
            for value in values:
                record = {"metric": "loss", "value": value}
                fh.write(json.dumps(record, allow_nan=False) + "\n")

        summarizer = NdjsonSummarizer(run_dir)
        rows = summarizer.collect()
        summary = summarizer.summarise()

        assert len(rows) == len(values)
        loss_row = next((row for row in summary if row["metric"] == "loss"), None)
        assert loss_row is not None
        assert loss_row["count"] == len(values)
        assert math.isclose(loss_row["min_value"], min(values))
        assert math.isclose(loss_row["max_value"], max(values))
