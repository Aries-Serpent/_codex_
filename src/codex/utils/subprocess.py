"""Safe wrappers around :mod:`subprocess` calls."""

from __future__ import annotations

import importlib
from collections.abc import Sequence
from pathlib import Path
from typing import IO, TYPE_CHECKING, Any, Literal, overload

if TYPE_CHECKING:
    # At type-check time, import the real stdlib subprocess so that mypy can
    # resolve `_stdlib_subprocess.CompletedProcess` correctly.
    import subprocess as _stdlib_subprocess
else:
    # At runtime, resolve via importlib to avoid local-module name shadowing
    # (`src.codex.utils.subprocess`) reported by code scanning in direct imports.
    _stdlib_subprocess: Any = importlib.import_module("subprocess")


@overload
def run(
    cmd: Sequence[str],
    *,
    cwd: Path | None = None,
    capture_output: bool = False,
    text: Literal[True] = True,
    check: bool = True,
    timeout: float | None = None,
    env: dict[str, str] | None = None,
    input: str | None = None,
    stdin: int | IO[Any] | None = None,
    stdout: int | IO[Any] | None = None,
    stderr: int | IO[Any] | None = None,
    encoding: str | None = None,
    errors: str | None = None,
    shell: bool = False,
) -> _stdlib_subprocess.CompletedProcess[str]:
    pass


@overload
def run(
    cmd: Sequence[str],
    *,
    cwd: Path | None = None,
    capture_output: bool = False,
    text: Literal[False],
    check: bool = True,
    timeout: float | None = None,
    env: dict[str, str] | None = None,
    input: bytes | None = None,
    stdin: int | IO[Any] | None = None,
    stdout: int | IO[Any] | None = None,
    stderr: int | IO[Any] | None = None,
    encoding: str | None = None,
    errors: str | None = None,
    shell: bool = False,
) -> _stdlib_subprocess.CompletedProcess[bytes]:
    pass


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
    shell: bool = False,  # accepted for API compatibility; rejected at runtime
) -> _stdlib_subprocess.CompletedProcess[Any]:
    """Run *cmd* securely.

    Parameters mirror :func:`subprocess.run`.

    Parameters
    ----------
    shell:
        Must be ``False``. This argument is accepted only for API compatibility.
        Passing ``True`` is rejected and raises :class:`ValueError` to prevent
        shell-injection risks.

    ``check`` defaults to ``True`` to ensure errors are surfaced immediately.
    ``text`` defaults to ``True``, so output streams are decoded and returned
    as ``str`` unless ``text=False`` is explicitly provided (which returns
    ``bytes`` output).
    """
    if shell:
        raise ValueError("shell=True is not supported by this secure wrapper")  # nosec

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
