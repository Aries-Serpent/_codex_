from __future__ import annotations

import csv
from pathlib import Path

import pytest


def _write_csv(path: Path, rows: list[dict[str, int]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["id", "value"])
        writer.writeheader()
        writer.writerows(rows)


def test_data_report_smoke(tmp_path: Path) -> None:
    try:
        from hhg_logistics.monitor.data_report import build_data_drift
    except Exception:  # pragma: no cover - optional dependency missing
        pytest.skip("evidently not installed")

    reference = tmp_path / "ref.csv"
    current = tmp_path / "cur.csv"
    _write_csv(reference, [{"id": i, "value": i % 3} for i in range(10)])
    _write_csv(current, [{"id": i, "value": (i + 1) % 3} for i in range(10)])

    html_path = tmp_path / "drift.html"
    json_path = tmp_path / "drift.json"
    summary = build_data_drift(reference, current, html_path, json_path, tracked_columns=["value"])

    assert html_path.exists() and json_path.exists()
    assert "drift_share" in summary
