"""Focused regressions for persistent SSH signing bootstrap."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from scripts.ci import setup_git_signing as signing


def test_configure_git_uses_private_key_path(monkeypatch: Any, tmp_path: Path) -> None:
    commands: list[list[str]] = []

    def run(command: list[str], **_kwargs: Any) -> subprocess.CompletedProcess[str]:
        commands.append(command)
        return subprocess.CompletedProcess(command, 0, stdout="")

    monkeypatch.setattr(signing.subprocess, "run", run)
    private_key = tmp_path / "codex_signing_ed25519"

    signing.configure_git(private_key, "ssh-ed25519 AAAA test@example.com\n")

    assert [
        "git",
        "config",
        "--global",
        "user.signingkey",
        str(private_key),
    ] in commands
    assert not any(command[-1].endswith(".pub") for command in commands)


def test_direct_script_invocation_resolves_repository_imports(tmp_path: Path) -> None:
    script = Path(signing.__file__).resolve()
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)

    result = subprocess.run(
        [sys.executable, str(script), "--help"],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "Configure persistent SSH commit signing" in result.stdout
