#!/usr/bin/env python
# Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5
# Purpose: Validate metrics logging patterns (NDJSON/CSV) without external deps.

from __future__ import annotations

import io
import json
from pathlib import Path
from typing import Dict

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def _write_ndjson(records: list[Dict], fp: io.TextIOBase) -> None:
    for rec in records:
        fp.write(json.dumps(rec, sort_keys=True) + "\n")


@pytest.mark.smoke
def test_evaluation_ndjson_roundtrip(tmp_path: Path):
    out = tmp_path / "metrics.ndjson"
    records = [
        {"step": 1, "metric": "loss", "value": 1.234, "split": "train"},
        {"step": 1, "metric": "accuracy", "value": 0.56, "split": "eval"},
    ]
    with out.open("w", encoding="utf-8") as fh:
        _write_ndjson(records, fh)

    # Read back and validate schema
    got = [
        json.loads(line) for line in out.read_text(encoding="utf-8").splitlines() if line.strip()
    ]
    assert all({"step", "metric", "value"} <= set(r) for r in got)
    # Deterministic order preserved
    assert got[0]["metric"] == "loss"
    assert got[1]["metric"] == "accuracy"


@pytest.mark.smoke
def test_evaluation_csv_optional(tmp_path: Path):
    # Optional CSV pattern (no external libs): comma-separated header + rows
    out = tmp_path / "metrics.csv"
    header = "step,metric,value,split\n"
    rows = ["1,loss,1.234,train\n", "1,accuracy,0.56,eval\n"]
    out.write_text(header + "".join(rows), encoding="utf-8")
    lines = out.read_text(encoding="utf-8").splitlines()
    assert lines[0].strip() == "step,metric,value,split"
    assert len(lines) == 3
