from __future__ import annotations

import json
import subprocess
import sys


def _run_json(args: list[str]) -> dict[str, object]:
    proc = subprocess.run(
        [sys.executable, "-m", "codex_ml.cli.list_plugins", "--format", "json", *args],
        capture_output=True,
        text=True,
        check=True,
    )
    assert proc.stderr.strip() == ""
    return json.loads(proc.stdout)


def test_json_shape_no_discover() -> None:
    payload = _run_json(["--no-discover"])
    assert "programmatic" in payload and "legacy" in payload and "options" in payload
    prog = payload["programmatic"]
    assert isinstance(prog, dict)
    assert isinstance(prog.get("discovered"), int)
    assert isinstance(prog.get("names"), list)
    legacy = payload["legacy"]
    assert isinstance(legacy, dict)
    assert "tokenizers" in legacy
    assert "datasets" in legacy
    opts = payload["options"]
    assert opts["format"] == "json"
    assert opts["discover"] is False
