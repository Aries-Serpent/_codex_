from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

SCHEMA_PATH = Path(__file__).parents[1] / "schemas" / "train_probe.schema.json"
SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _validate(payload: dict[str, Any]) -> None:
    assert isinstance(payload.get("ok"), bool)
    assert payload.get("component") == "codex-train"
    assert isinstance(payload.get("python"), str)
    assert isinstance(payload.get("platform"), str)


def test_train_probe_json_output() -> None:
    command = (
        "import codex_ml.cli.hydra_main as H; "
        "import sys; "
        "res = H.main(); "
        "sys.exit(res if isinstance(res, int) else 0)"
    )
    proc = subprocess.run(
        [sys.executable, "-c", command, "--probe-json"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    _validate(payload)
    for required_key in SCHEMA["required"]:
        assert required_key in payload
    assert "Traceback" not in (proc.stderr or "")
