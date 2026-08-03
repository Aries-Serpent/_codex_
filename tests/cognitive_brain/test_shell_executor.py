"""Tests for policy-gated shell execution."""

from __future__ import annotations

from subprocess import CompletedProcess

import pytest

from src.codex.cognitive_brain.shell_executor import (
    ShellExecutionDenied,
    execute_command,
)
from src.codex.cognitive_brain.shell_policy import PolicyVerdict, ShellPolicy


def test_denied_command_never_reaches_subprocess(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[object, object]] = []

    def _fake_run(*args: object, **kwargs: object) -> CompletedProcess[str]:
        calls.append((args, kwargs))
        raise AssertionError("subprocess.run must not be called for denied commands")

    monkeypatch.setattr(
        "src.codex.cognitive_brain.shell_executor.secure_subprocess.run",
        _fake_run,
    )

    with pytest.raises(ShellExecutionDenied) as excinfo:
        execute_command("git status; rm -rf /", policy=ShellPolicy(allow_patterns=["git *"]))

    assert calls == []
    assert excinfo.value.decision.verdict == PolicyVerdict.DENY


def test_allowed_command_uses_argv_and_shell_false(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def _fake_run(*args: object, **kwargs: object) -> CompletedProcess[str]:
        captured["args"] = args
        captured["kwargs"] = kwargs
        return CompletedProcess(args[0], 0, "ok", "")

    monkeypatch.setattr(
        "src.codex.cognitive_brain.shell_executor.secure_subprocess.run",
        _fake_run,
    )

    result = execute_command("git status --short", policy=ShellPolicy())

    assert result.returncode == 0
    assert captured["args"][0] == ["git", "status", "--short"]
    assert captured["kwargs"]["shell"] is False
