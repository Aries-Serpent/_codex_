"""
Test List Plugins Cli Json

Test module for list plugins cli json.
"""

from __future__ import annotations

import json
import subprocess
import sys

_ALLOWED_STDERR_FRAGMENTS = (
    "psutil import failed; falling back to minimal sampler",
    "env_file not supported when pydantic_settings unavailable",
)


def _run_json(args: list[str]) -> dict[str, object]:
    proc = subprocess.run(
        [sys.executable, "-m", "codex_ml.cli.list_plugins", "--format", "json", *args],
        capture_output=True,
        text=True,
        check=True,
    )
    stderr = proc.stderr.strip()
    assert stderr == "" or any(fragment in stderr for fragment in _ALLOWED_STDERR_FRAGMENTS)
    return json.loads(proc.stdout)


def test_json_shape_no_discover() -> None:
    payload = _run_json(["--no-discover"])
    assert "programmatic" in payload and "legacy" in payload and "options" in payload
    prog = payload["programmatic"]
    assert isinstance(prog, dict)
    assert isinstance(prog.get("discovered"), list)  # discovered is a list, not int
    assert isinstance(prog.get("names"), list)
    legacy = payload["legacy"]
    assert isinstance(legacy, dict)
    assert "tokenizers" in legacy, "Condition must be true"
    assert "datasets" in legacy, "Data must not be empty"
    opts = payload["options"]
    assert opts["format"] == "json", "Condition must be true"
    assert opts["discover"] is False, "Condition must be true"
