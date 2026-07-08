"""
Conftest Module

This module provides functionality for conftest.

Usage:
    from cli.conftest import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

import importlib.util
import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if (repo_str := str(REPO_ROOT)) in sys.path:
    sys.path.remove(repo_str)
    sys.path.append(repo_str)


def _is_stub_spec(spec: importlib.machinery.ModuleSpec | None, name: str) -> bool:
    if spec is None:
        return False
    origin = getattr(spec, "origin", None)
    if not origin:
        return False
    try:
        return Path(origin).resolve().is_relative_to(REPO_ROOT / name)
    except OSError:
        return False


if os.environ.get("CODEX_CLI_LIGHTWEIGHT", "0") != "1":
    required = ("yaml", "omegaconf", "hydra")
    missing = [
        name
        for name in required
        if (spec := importlib.util.find_spec(name)) is None or _is_stub_spec(spec, name)
    ]
    if missing:
        pytest.skip(
            f"Skipping CLI tests: missing required dependencies {missing}",
            allow_module_level=True,
        )

    # Check if torch is actually importable (not just present)
    try:
        importlib.import_module("torch")
        spec = importlib.util.find_spec("torch")
        if spec is None or _is_stub_spec(spec, "torch"):
            raise ImportError("torch stubbed")
    except (ImportError, OSError) as e:
        # OSError can occur if torch libraries (libtorch_global_deps.so) are missing
        pytest.skip(
            f"Skipping CLI tests: torch unavailable or unloadable ({e})",
            allow_module_level=True,
        )
