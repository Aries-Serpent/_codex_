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


def test_data_gate_non_abort(tmp_path: Path) -> None:
    try:
        from hhg_logistics.monitor.data_gate import run_data_drift_gate
    except Exception:  # pragma: no cover - optional dependency missing
        pytest.skip("evidently not installed")

    reference = tmp_path / "ref.csv"
    current = tmp_path / "cur.csv"
    _write_csv(reference, [{"id": i, "value": i % 3} for i in range(10)])
    _write_csv(current, [{"id": i, "value": (i + 1) % 3} for i in range(10)])

    html_path = tmp_path / "drift.html"
    json_path = tmp_path / "drift.json"
    thresholds = {"drift_share_critical": 0.99, "p_value_critical": 0.0001}
    summary = run_data_drift_gate(
        reference,
        current,
        html_path,
        json_path,
        thresholds,
        abort_on_critical=False,
        tracked_columns=["value"],
    )
    assert "gate" in summary and isinstance(summary["gate"].get("fail"), bool)


def test_data_gate_abort(tmp_path: Path) -> None:
    try:
        from hhg_logistics.monitor.data_gate import run_data_drift_gate
    except Exception:  # pragma: no cover
        pytest.skip("evidently not installed")

    reference = tmp_path / "ref.csv"
    current = tmp_path / "cur.csv"
    _write_csv(reference, [{"id": i, "value": 0} for i in range(20)])
    _write_csv(current, [{"id": i, "value": 2} for i in range(20)])

    html_path = tmp_path / "drift.html"
    json_path = tmp_path / "drift.json"

    with pytest.raises(RuntimeError):
        run_data_drift_gate(
            reference,
            current,
            html_path,
            json_path,
            {"drift_share_critical": 0.2, "p_value_critical": 0.5},
            abort_on_critical=True,
            tracked_columns=["value"],
        )
