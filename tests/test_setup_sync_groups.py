"""Validate CODEX_SYNC_GROUPS parsing in setup.sh."""

from __future__ import annotations

import subprocess
import textwrap
from pathlib import Path

import pytest


def _extract_uv_sync_selective() -> str:
    script = Path(__file__).resolve().parents[1] / ".codex/scripts/setup.sh"
    lines = script.read_text().splitlines()
    func_lines: list[str] = []
    capturing = False
    depth = 0
    for line in lines:
        if not capturing and line.startswith("_uv_sync_selective()"):
            capturing = True
        if capturing:
            func_lines.append(line)
            depth += line.count("{") - line.count("}")
            if depth == 0:
                break
    return "\n".join(func_lines)


def test_setup_group_parsing() -> None:
    func_def = _extract_uv_sync_selective()
    if not func_def.strip():
        pytest.skip("_uv_sync_selective helper not defined in setup script")
    script = textwrap.dedent(
        f"""
        run() {{ echo "$@"; }}
        warn() {{ :; }}
        uv() {{ :; }}
        CODEX_SYNC_GROUPS=base,dev,cpu,test
        {func_def}
        _uv_sync_selective
        """
    )
    result = subprocess.run(
        ["bash", "-c", script],
        capture_output=True,
        text=True,
        cwd=Path(__file__).resolve().parents[1],
    )
    assert "--group dev --group cpu --group test" in result.stdout
