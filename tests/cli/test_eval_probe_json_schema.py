from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

SCHEMA_PATH = Path(__file__).parents[1] / "schemas" / "eval_probe.schema.json"
SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _validate(payload: dict[str, Any]) -> None:
    assert isinstance(payload.get("ok"), bool)
    assert payload.get("component") == "codex-eval"
    assert isinstance(payload.get("python"), str)
    assert isinstance(payload.get("platform"), str)
    details = payload.get("details")
    assert isinstance(details, dict)
    assert isinstance(details.get("env_override"), bool)


def test_eval_probe_json_output() -> None:
    proc = subprocess.run(
        [
            sys.executable,
            "-c",
            "import codex_ml.cli.entrypoints as E; import sys; sys.exit(E.eval_main())",
            "--probe-json",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    assert "Traceback" not in (proc.stderr or "")
    payload = json.loads(proc.stdout)
    _validate(payload)
    for required_key in SCHEMA["required"]:
        assert required_key in payload
