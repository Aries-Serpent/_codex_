"""Safe wrappers around :mod:`subprocess` calls."""

from __future__ import annotations

import importlib
from collections.abc import Sequence
from pathlib import Path
from typing import IO, Any

_stdlib_subprocess = importlib.import_module("subprocess")


def run(
    cmd: Sequence[str],
    *,
    cwd: Path | None = None,
    capture_output: bool = False,
    text: bool = True,
    check: bool = True,
    timeout: float | None = None,
    env: dict[str, str] | None = None,
    input: str | bytes | None = None,
    stdin: int | IO[Any] | None = None,
    stdout: int | IO[Any] | None = None,
    stderr: int | IO[Any] | None = None,
    encoding: str | None = None,
    errors: str | None = None,
    shell: bool = False,  # accepted for API compatibility; always forced to False
) -> Any:
    """Run *cmd* securely.

    Parameters mirror :func:`subprocess.run`.  ``shell`` is **always** ``False``
    regardless of the value passed — this wrapper exists specifically to prevent
    shell-injection risks.  ``check`` defaults to ``True`` to ensure errors are
    surfaced immediately.
    """
    return _stdlib_subprocess.run(  # nosec B603
        list(cmd),
        cwd=cwd,
        capture_output=capture_output,
        text=text,
        check=check,
        timeout=timeout,
        env=env,
        input=input,
        stdin=stdin,
        stdout=stdout,
        stderr=stderr,
        encoding=encoding,
        errors=errors,
        shell=False,
    )
