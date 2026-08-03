"""Policy-gated shell execution helpers for Cognitive Brain."""

from __future__ import annotations

import shlex
from pathlib import Path
from typing import Any, Optional, cast

from src.aries_serpent_core.utils import subprocess as secure_subprocess

from .shell_policy import GateDecision, PolicyVerdict, ShellPolicy, get_default_policy


class ShellExecutionDenied(PermissionError):
    """Raised when :class:`ShellPolicy` blocks a shell command."""

    def __init__(self, decision: GateDecision) -> None:
        super().__init__(decision.reason)
        self.decision = decision


def execute_command(
    command: str,
    *,
    cwd: str | Path | None = None,
    policy: Optional[ShellPolicy] = None,
    capture_output: bool = True,
    text: bool = True,
    check: bool = True,
    env: Optional[dict[str, str]] = None,
    input: Optional[str] = None,
) -> Any:
    """Execute *command* only after it passes :class:`ShellPolicy`.

    Denied commands raise :class:`ShellExecutionDenied` before any subprocess
    invocation. Allowed commands are split into an argv list and executed
    through the secure subprocess wrapper with ``shell=False``.
    """

    resolved_policy = policy or get_default_policy()
    cwd_path = Path(cwd) if cwd is not None else None
    decision = resolved_policy.gate(command, cwd=str(cwd_path) if cwd_path else None)
    if decision.verdict == PolicyVerdict.DENY:
        raise ShellExecutionDenied(decision)

    argv = shlex.split(command, posix=True)
    if not argv:
        raise ValueError("Command must not be empty")

    return secure_subprocess.run(
        argv,
        cwd=cwd_path,
        capture_output=capture_output,
        text=cast(Any, text),
        check=check,
        timeout=decision.timeout_s,
        env=env,
        input=input,
        shell=False,
    )
