"""Tests for DuckDB dependency guards in metrics CLI."""

from __future__ import annotations

import builtins
from pathlib import Path

import pytest

from codex_ml.cli.metrics_cli import _csv_to_duckdb


def test_duckdb_missing_dependency(monkeypatch, tmp_path: Path) -> None:
    """`_csv_to_duckdb` should raise SystemExit when duckdb is unavailable."""

    csv = tmp_path / "metrics.csv"
    csv.write_text("run_id,epoch,key,value\nrun-1,0,loss,0.1\n", encoding="utf-8")

    original_import = builtins.__import__

    def fake_import(name: str, *args: object, **kwargs: object):  # type: ignore[override]
        if name == "duckdb":
            raise ModuleNotFoundError("No module named 'duckdb'")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    with pytest.raises(SystemExit) as exc:
        _csv_to_duckdb(csv, tmp_path / "metrics.duckdb", "metrics")

    assert "duckdb dependency missing" in str(exc.value)
