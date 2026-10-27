"""Regression coverage for canonical authentication errors across legacy imports."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize("legacy_first", [True, False])
def test_auth_exception_module_identity_in_both_import_orders(legacy_first):
    """Both namespaces must expose the same classes used by route exception handlers."""
    root = Path(__file__).resolve().parents[2]
    modules = ["codex.auth.exceptions", "aries_serpent_core.auth.exceptions"]
    if not legacy_first:
        modules.reverse()
    script = """
import importlib
import pathlib
import sys

first = importlib.import_module(sys.argv[1])
second = importlib.import_module(sys.argv[2])
assert first is second
assert first.__name__ == "aries_serpent_core.auth.exceptions"
assert pathlib.Path(first.__file__).resolve().is_relative_to(pathlib.Path.cwd() / "src")
for name, value in vars(first).items():
    if isinstance(value, type) and issubclass(value, first.AuthError):
        assert getattr(second, name) is value
"""
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join([str(root / "src"), env.get("PYTHONPATH", "")])
    result = subprocess.run(
        [sys.executable, "-c", script, *modules],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    assert result.returncode == 0, result.stderr
