"""DuckDB ingest mode tests for metrics CLI."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


duckdb = pytest.importorskip("duckdb")  # noqa: F841  # skip if dependency missing


def run_cli(args: list[str]) -> tuple[int, str, str]:
    proc = subprocess.Popen(  # noqa: S603,S607 - CLI invocation
        [sys.executable, "-m", "codex_ml.cli", "metrics", *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    out, err = proc.communicate()
    return proc.returncode, out, err


def test_duckdb_replace_append_fail(tmp_path: Path) -> None:
    nd = tmp_path / "m.ndjson"
    nd.write_text('{"epoch":0,"loss":1.0}\n{"epoch":1,"loss":0.9}\n', encoding="utf-8")
    csv = tmp_path / "m.csv"
    db = tmp_path / "m.duckdb"

    rc, out, err = run_cli(
        [
            "ingest",
            "--input",
            str(nd),
            "--out-csv",
            str(csv),
            "--to-duckdb",
            str(db),
            "--table",
            "metrics",
            "--mode",
            "replace",
        ]
    )
    assert err == ""
    assert rc == 0 and json.loads(out)["ok"]

    rc, out, err = run_cli(
        [
            "ingest",
            "--input",
            str(nd),
            "--out-csv",
            str(csv),
            "--to-duckdb",
            str(db),
            "--table",
            "metrics",
            "--mode",
            "append",
        ]
    )
    assert err == ""
    assert rc == 0 and json.loads(out)["ok"]

    rc, _out, err = run_cli(
        [
            "ingest",
            "--input",
            str(nd),
            "--out-csv",
            str(csv),
            "--to-duckdb",
            str(db),
            "--table",
            "metrics",
            "--mode",
            "fail",
        ]
    )
    assert rc != 0
    assert "Error" in err or "error" in err
