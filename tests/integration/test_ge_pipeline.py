from __future__ import annotations

import csv
from pathlib import Path

import pytest

from common.validate import run_clean_checkpoint


def _write_clean_csv(path: Path, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "value"])
        writer.writeheader()
        writer.writerows(rows)


def test_ge_validation_success(tmp_path: Path) -> None:
    good_rows = [{"id": i, "value": i % 3} for i in range(5)]
    clean_csv = tmp_path / "clean.csv"
    _write_clean_csv(clean_csv, good_rows)
    ok, docs_dir = run_clean_checkpoint(clean_csv)
    assert ok is True
    assert docs_dir.exists()


def test_ge_validation_failure(tmp_path: Path) -> None:
    bad_rows = [{"id": 0, "value": 9}]
    clean_csv = tmp_path / "clean.csv"
    _write_clean_csv(clean_csv, bad_rows)
    with pytest.raises(RuntimeError):
        run_clean_checkpoint(clean_csv)
