"""
Test Data Report

Test module for data report.
"""

from __future__ import annotations

import csv
import json
import tomllib
from pathlib import Path

import pytest
from packaging.requirements import Requirement


def _write_csv(path: Path, rows: list[dict[str, int]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["id", "value"])
        writer.writeheader()
        writer.writerows(rows)


def test_data_report_smoke(tmp_path: Path) -> None:
    build_data_drift = pytest.importorskip("hhg_logistics.monitor.data_report").build_data_drift

    reference = tmp_path / "ref.csv"
    current = tmp_path / "cur.csv"
    _write_csv(reference, [{"id": i, "value": i % 3} for i in range(10)])
    _write_csv(current, [{"id": i, "value": (i + 1) % 3} for i in range(10)])

    html_path = tmp_path / "drift.html"
    json_path = tmp_path / "drift.json"
    summary = build_data_drift(reference, current, html_path, json_path, tracked_columns=["value"])

    assert html_path.exists() and json_path.exists(), "Condition must be true"
    assert summary["columns"] == ["value"]
    assert 0.0 <= summary["drift_share"] <= 1.0
    assert 0.0 <= summary["p_value_mean"] <= 1.0
    assert "value" in summary["per_feature"]
    report = json.loads(json_path.read_text())
    results = {metric["metric"]: metric["result"] for metric in report["metrics"]}
    assert summary["drift_share"] == results["DatasetDriftMetric"]["share_of_drifted_columns"]


def test_evidently_profiles_constrain_supported_pandas():
    """All Evidently profiles retain the security floor without admitting pandas 3.1."""
    project = Path(__file__).resolve().parents[2] / "pyproject.toml"
    with project.open("rb") as handle:
        extras = tomllib.load(handle)["project"]["optional-dependencies"]

    profiles = 0
    for dependencies in extras.values():
        requirements = {req.name: req for req in map(Requirement, dependencies)}
        if "evidently" in requirements:
            profiles += 1
            pandas = requirements["pandas"].specifier
            assert "3.0.5" in pandas
            assert "3.0.4" not in pandas
            assert "3.1.0" not in pandas
    assert profiles > 0


@pytest.mark.parametrize("shifted", [False, True])
def test_large_numeric_report_uses_p_values(tmp_path, shifted):
    """Large samples must not silently turn gate p-values into distance scores."""
    from hhg_logistics.monitor.data_report import build_data_drift

    reference = tmp_path / "reference.csv"
    current = tmp_path / "current.csv"
    _write_csv(reference, [{"id": i, "value": i} for i in range(1500)])
    offset = 5000 if shifted else 0
    _write_csv(current, [{"id": i, "value": i + offset} for i in range(1500)])

    summary = build_data_drift(
        reference,
        current,
        tmp_path / "report.html",
        tmp_path / "report.json",
        tracked_columns=["value"],
    )

    assert summary["drift_share"] == (1.0 if shifted else 0.0)
    if shifted:
        assert summary["p_value_mean"] < 0.001
    else:
        assert summary["p_value_mean"] == pytest.approx(1.0)
