#!/usr/bin/env python3
"""Schema round-trip tests for the evaluation runner (NDJSON/CSV)."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

pytest.importorskip("datasets")

from codex_ml.eval.eval_runner import evaluate_datasets  # noqa: E402


def test_schema_round_trip(tmp_path: Path):
    out = tmp_path
    evaluate_datasets(["toy_copy_task"], ["exact_match"], out)
    ndjson_path = out / "metrics.ndjson"
    csv_path = out / "metrics.csv"

    # NDJSON first record
    record = json.loads(ndjson_path.read_text().strip().splitlines()[0])
    required = {
        "$schema",
        "schema_version",
        "run_id",
        "dataset",
        "split",
        "step",
        "metric",
        "value",
        "n",
        "timestamp",
        "tags",
    }
    # Allow additional fields (e.g., notes, ci_low, ci_high), only require a subset
    assert required.issubset(record.keys())
    assert record["dataset"] == "toy_copy_task"
    assert record["metric"] == "exact_match"
    assert float(record["value"]) == 1.0
    assert record["tags"]["phase"] == "eval"

    # CSV schema and value agreement
    with csv_path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
    assert rows, "CSV must contain at least one row"
    # Must contain required columns; allow extra columns
    assert {key for key in required if key not in {"$schema", "schema_version", "tags"}}.issubset(
        rows[0].keys()
    )
    assert float(rows[0]["value"]) == float(record["value"])
    assert rows[0]["metric"] == record["metric"]
    assert rows[0]["phase"] == "eval"
