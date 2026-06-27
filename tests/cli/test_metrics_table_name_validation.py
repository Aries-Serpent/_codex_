"""Tests for metrics CLI table-name validation flags."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def run_cli(args: list[str]) -> tuple[int, str, str]:
    proc = subprocess.Popen(
        [sys.executable, "-m", "codex_ml.cli", "metrics", *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    out, err = proc.communicate()
    return proc.returncode, out, err


def test_rejects_unsafe_table_name(tmp_path: Path) -> None:
    nd = tmp_path / "m.ndjson"
    nd.write_text('{"epoch":0,"loss":1.0}\n', encoding="utf-8")
    rc, _out, err = run_cli(
        [
            "ingest",
            "--input",
            str(nd),
            "--out-csv",
            str(tmp_path / "m.csv"),
            "--to-sqlite",
            str(tmp_path / "m.db"),
            "--table",
            "bad-name;drop",
        ]
    )
    assert rc != 0, "rc is not valid"
    assert "[metrics-cli] invalid table name" in err, "Condition must be true"


def test_allows_unsafe_with_override(tmp_path: Path) -> None:
    nd = tmp_path / "m.ndjson"
    nd.write_text('{"epoch":0,"loss":1.0}\n', encoding="utf-8")
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
            "ok$name",
            "--allow-unsafe-table-name",
        ]
    )
    # With the allow-unsafe-table-name flag, should succeed (exit code 0)
    assert (rc == 0, "rc is not valid"
    ), f"Expected success with --allow-unsafe-table-name flag. stderr: {err}, stdout: {out}"

    # Verify success message in output
    payload = json.loads(out)
    assert payload["ok"] is True, "Condition must be true"
