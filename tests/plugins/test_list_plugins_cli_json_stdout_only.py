from __future__ import annotations

import json
import subprocess
import sys


def test_list_plugins_json_stdout_only():
    """
    Ensure JSON output is emitted on stdout only and stderr is empty.
    """
    # Construct invocation using module path to avoid import path surprises
    cmd = [sys.executable, "-m", "codex_ml.cli.list_plugins", "--format", "json"]
    proc = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, text=True
    )
    # Contract: exit code 0, empty stderr in JSON mode
    assert (
        proc.returncode == 0
    ), f"list_plugins returned non-zero exit: {proc.returncode}, stderr={proc.stderr}"
    assert proc.stderr.strip() == "", f"stderr must be empty in JSON mode, got: {proc.stderr!r}"
    # Parseable JSON
    payload = json.loads(proc.stdout)
    # Payload can be a list or dict; minimally ensure it's JSON and not empty in normal repos
    assert isinstance(payload, (list, dict)), f"unexpected JSON type: {type(payload)}"
    # Optional: basic shape checks if dict-based
    if isinstance(payload, dict):
        expected_keys = {"plugins", "entries", "names", "programmatic", "legacy"}
        assert expected_keys.intersection(
            payload.keys()
        ), f"unexpected JSON keys: {list(payload.keys())}"
