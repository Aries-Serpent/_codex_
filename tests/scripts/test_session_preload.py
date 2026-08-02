"""Tests for the Copilot session preload script."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_session_preload_output_is_bounded() -> None:
    """The preload output should remain stable and truncated."""
    repo_root = Path(__file__).parent.parent.parent
    script_path = repo_root / ".github" / "scripts" / "session_preload.py"

    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True,
        cwd=repo_root,
        timeout=120,
        check=False,
    )

    assert result.returncode == 0
    assert "::group::✅ AGENTIC REPO STATE" in result.stdout
    assert "::endgroup::" in result.stdout
    assert len(result.stdout) < 30_000
