"""Exercise chunked SQLite ingest behavior."""

from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
from pathlib import Path


def run_cli(args: list[str]) -> tuple[int, str, str]:
    proc = subprocess.Popen(  # noqa: S603,S607 - CLI invocation
        [sys.executable, "-m", "codex_ml.cli", "metrics", *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    out, err = proc.communicate()
    return proc.returncode, out, err


def test_sqlite_chunked_and_index(tmp_path: Path) -> None:
    nd = tmp_path / "m.ndjson"
    with nd.open("w", encoding="utf-8") as fh:
        for i in range(10000):
            fh.write(f'{{"epoch":{i % 5},"loss":{10.0 - (i % 10) / 10.0}}}\n')

    rc, out, err = run_cli(
        [
            "ingest",
            "--input",
            str(nd),
            "--out-csv",
            str(tmp_path / "m.csv"),
            "--to-sqlite",
            str(tmp_path / "m.db"),
            "--table",
            "metrics",
            "--chunk-size",
            "2000",
            "--create-index",
        ]
    )
    assert err == ""
    assert rc == 0
    payload = json.loads(out)
    assert payload["ok"] is True


def test_sqlite_accepts_fractional_epoch(tmp_path: Path) -> None:
    nd = tmp_path / "fractional.ndjson"
    with nd.open("w", encoding="utf-8") as fh:
        fh.write('{"epoch": 0.5, "loss": 1.0}\n')
        fh.write('{"epoch": "1.25", "loss": 0.9}\n')

    db_path = tmp_path / "fractional.db"
    rc, out, err = run_cli(
        [
            "ingest",
            "--input",
            str(nd),
            "--out-csv",
            str(tmp_path / "fractional.csv"),
            "--to-sqlite",
            str(db_path),
            "--table",
            "metrics",
        ]
    )

    assert err == ""
    assert rc == 0
    payload = json.loads(out)
    assert payload["ok"] is True

    con = sqlite3.connect(db_path)
    try:
        rows = con.execute("SELECT epoch FROM metrics ORDER BY rowid").fetchall()
    finally:
        con.close()

    assert rows == [(0.5,), (1.25,)]
