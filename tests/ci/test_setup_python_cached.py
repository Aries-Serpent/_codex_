"""Regression tests for the shared Python setup action's cache keys."""

from __future__ import annotations

import hashlib
import os
import subprocess
from pathlib import Path

import yaml

ACTION_PATH = (
    Path(__file__).resolve().parents[2]
    / ".github"
    / "actions"
    / "setup-python-cached"
    / "action.yml"
)


def _action_steps() -> list[dict[str, object]]:
    action = yaml.safe_load(ACTION_PATH.read_text(encoding="utf-8"))
    return action["runs"]["steps"]


def test_extras_fingerprint_is_deterministic_and_comma_free(tmp_path, monkeypatch):
    steps = _action_steps()
    fingerprint_step = next(step for step in steps if step.get("id") == "extras-key")
    output_hashes = []

    for index, extras in enumerate(
        (
            "runtime,test-ml-integrations",
            "runtime-test,ml-integrations",
            "runtime,test-ml-integrations,ml",
        )
    ):
        output_path = tmp_path / f"github-output-{index}"
        monkeypatch.setenv("CACHE_EXTRAS", extras)
        monkeypatch.setenv("GITHUB_OUTPUT", str(output_path))
        subprocess.run(
            ["bash", "-euo", "pipefail", "-c", fingerprint_step["run"]],
            check=True,
            capture_output=True,
            text=True,
            env=os.environ.copy(),
        )
        output_hash = output_path.read_text(encoding="utf-8").strip().removeprefix("sha256=")
        assert output_hash == hashlib.sha256(extras.encode("utf-8")).hexdigest()
        assert "," not in output_hash
        output_hashes.append(output_hash)

    assert len(set(output_hashes)) == len(output_hashes)


def test_venv_cache_and_restore_keys_use_fingerprint_without_changing_installs():
    action_text = ACTION_PATH.read_text(encoding="utf-8")
    steps = _action_steps()
    cache_step = next(step for step in steps if step.get("id") == "cache-venv")
    cache_config = cache_step["with"]
    key_text = "\n".join((cache_config["key"], cache_config["restore-keys"]))

    assert key_text.count("steps.extras-key.outputs.sha256") == 4
    assert "inputs.extras" not in key_text
    assert action_text.count('".[${{ inputs.extras }}]"') == 3
