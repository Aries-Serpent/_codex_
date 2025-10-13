from __future__ import annotations

import tempfile
from pathlib import Path
from subprocess import check_call


def _run_cli(*args: str) -> None:
    check_call(["python", "-m", "codex_crm.cli", *args])


def test_cli_smoke() -> None:
    with tempfile.TemporaryDirectory() as tempdir:
        zd_out = Path(tempdir) / "zd"
        d365_out = Path(tempdir) / "d365"

        _run_cli("apply-zd", "--out", str(zd_out))
        _run_cli("apply-d365", "--out", str(d365_out))

        assert (zd_out / "forms.json").exists()
        assert (d365_out / "tables.csv").exists()
