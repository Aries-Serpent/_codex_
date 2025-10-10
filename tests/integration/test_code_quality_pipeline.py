#!/usr/bin/env python
# Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5
# Purpose: Verify code quality tooling presence; skip gracefully if not installed.

from __future__ import annotations

import shutil
import subprocess

import pytest


def _has(cmd: str) -> bool:
    return shutil.which(cmd) is not None


@pytest.mark.smoke
def test_code_tools_versions_available():
    missing = []
    for tool in ("black", "ruff", "mypy"):
        if not _has(tool):
            missing.append(tool)
    if missing:
        pytest.skip(f"Missing tools: {', '.join(missing)}")
    # Light sanity: call --version for each tool
    for tool in ("black", "ruff", "mypy"):
        out = subprocess.run([tool, "--version"], capture_output=True, text=True)
        assert out.returncode == 0
        assert out.stdout or out.stderr
