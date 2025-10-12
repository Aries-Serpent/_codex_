from __future__ import annotations

import csv
from pathlib import Path

import pytest


def _write_csv(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["latency_ms", "prompt_len", "gen_len", "model", "source"],
        )
        writer.writeheader()
        for idx in range(10):
            writer.writerow(
                {
                    "latency_ms": 10 + idx,
                    "prompt_len": 5 + idx,
                    "gen_len": 7 + idx,
                    "model": "tiny",
                    "source": "pretrained",
                }
            )


def test_build_report(tmp_path: Path) -> None:
    try:
        import hhg_logistics.monitor.serve_report as serve_report
    except Exception:  # pragma: no cover - optional dependency guard
        pytest.skip("evidently not installed")

    reference = tmp_path / "ref.csv"
    current = tmp_path / "cur.csv"
    _write_csv(reference)
    _write_csv(current)

    output = tmp_path / "report.html"
    result = serve_report.build_report(reference, current, output)

    assert result.exists()
    assert result == output
