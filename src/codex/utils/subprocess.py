"""Safe wrappers around :mod:`subprocess` calls."""

from __future__ import annotations

import importlib
from collections.abc import Sequence
from pathlib import Path
from typing import IO, Any, Literal, cast, overload

# Resolve stdlib subprocess via importlib to avoid local-module name shadowing
# (`src.codex.utils.subprocess`) reported by code scanning in direct imports.
_stdlib_subprocess = cast(Any, importlib.import_module("subprocess"))


@overload
def run(
    cmd: Sequence[str],
    *,
    cwd: Path | None = None,
    capture_output: bool = False,
    check: bool = True,
    timeout: float | None = None,
    env: dict[str, str] | None = None,
    input: str | bytes | None = None,
    stdin: int | IO[Any] | None = None,
    stdout: int | IO[Any] | None = None,
    stderr: int | IO[Any] | None = None,
    encoding: str | None = None,
    errors: str | None = None,
    shell: bool = False,
) -> _stdlib_subprocess.CompletedProcess[str]: ...


@overload
def run(
    cmd: Sequence[str],
    *,
    cwd: Path | None = None,
    capture_output: bool = False,
    text: Literal[True],
    check: bool = True,
    timeout: float | None = None,
    env: dict[str, str] | None = None,
    input: str | bytes | None = None,
    stdin: int | IO[Any] | None = None,
    stdout: int | IO[Any] | None = None,
    stderr: int | IO[Any] | None = None,
    encoding: str | None = None,
    errors: str | None = None,
    shell: bool = False,
) -> _stdlib_subprocess.CompletedProcess[str]: ...


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
    input: str | bytes | None = None,
    stdin: int | IO[Any] | None = None,
    stdout: int | IO[Any] | None = None,
    stderr: int | IO[Any] | None = None,
    encoding: str | None = None,
    errors: str | None = None,
    shell: bool = False,
) -> _stdlib_subprocess.CompletedProcess[bytes]: ...


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
    shell: bool = False,  # accepted for API compatibility; shell=True is rejected
) -> _stdlib_subprocess.CompletedProcess[Any]:
    """Run *cmd* securely.

    Parameters mirror :func:`subprocess.run`. This wrapper forbids shell
    execution to prevent shell-injection risks; passing ``shell=True`` raises
    :class:`ValueError`. ``check`` defaults to ``True`` to ensure errors are
    surfaced immediately.
    """
    if shell:
        raise ValueError("shell=True is not supported by this secure wrapper")

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
