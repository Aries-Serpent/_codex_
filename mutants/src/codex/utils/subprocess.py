"""Safe wrappers around :mod:`subprocess` calls."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Sequence
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


def x_run__mutmut_orig(
    cmd: Sequence[str],
    *,
    cwd: Path | None = None,
    capture_output: bool = False,
    text: bool = True,
    check: bool = True,
    timeout: float | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run *cmd* securely.

    Parameters mirror :func:`subprocess.run` but ``shell`` is always ``False`` and
    ``check`` defaults to ``True`` to ensure errors are surfaced.
    """
    return subprocess.run(  # nosec B603
        list(cmd),
        cwd=cwd,
        capture_output=capture_output,
        text=text,
        check=check,
        timeout=timeout,
        shell=False,
    )


def x_run__mutmut_1(
    cmd: Sequence[str],
    *,
    cwd: Path | None = None,
    capture_output: bool = True,
    text: bool = True,
    check: bool = True,
    timeout: float | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run *cmd* securely.

    Parameters mirror :func:`subprocess.run` but ``shell`` is always ``False`` and
    ``check`` defaults to ``True`` to ensure errors are surfaced.
    """
    return subprocess.run(  # nosec B603
        list(cmd),
        cwd=cwd,
        capture_output=capture_output,
        text=text,
        check=check,
        timeout=timeout,
        shell=False,
    )


def x_run__mutmut_2(
    cmd: Sequence[str],
    *,
    cwd: Path | None = None,
    capture_output: bool = False,
    text: bool = False,
    check: bool = True,
    timeout: float | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run *cmd* securely.

    Parameters mirror :func:`subprocess.run` but ``shell`` is always ``False`` and
    ``check`` defaults to ``True`` to ensure errors are surfaced.
    """
    return subprocess.run(  # nosec B603
        list(cmd),
        cwd=cwd,
        capture_output=capture_output,
        text=text,
        check=check,
        timeout=timeout,
        shell=False,
    )


def x_run__mutmut_3(
    cmd: Sequence[str],
    *,
    cwd: Path | None = None,
    capture_output: bool = False,
    text: bool = True,
    check: bool = False,
    timeout: float | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run *cmd* securely.

    Parameters mirror :func:`subprocess.run` but ``shell`` is always ``False`` and
    ``check`` defaults to ``True`` to ensure errors are surfaced.
    """
    return subprocess.run(  # nosec B603
        list(cmd),
        cwd=cwd,
        capture_output=capture_output,
        text=text,
        check=check,
        timeout=timeout,
        shell=False,
    )


def x_run__mutmut_4(
    cmd: Sequence[str],
    *,
    cwd: Path | None = None,
    capture_output: bool = False,
    text: bool = True,
    check: bool = True,
    timeout: float | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run *cmd* securely.

    Parameters mirror :func:`subprocess.run` but ``shell`` is always ``False`` and
    ``check`` defaults to ``True`` to ensure errors are surfaced.
    """
    return subprocess.run(  # nosec B603
        None,
        cwd=cwd,
        capture_output=capture_output,
        text=text,
        check=check,
        timeout=timeout,
        shell=False,
    )


def x_run__mutmut_5(
    cmd: Sequence[str],
    *,
    cwd: Path | None = None,
    capture_output: bool = False,
    text: bool = True,
    check: bool = True,
    timeout: float | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run *cmd* securely.

    Parameters mirror :func:`subprocess.run` but ``shell`` is always ``False`` and
    ``check`` defaults to ``True`` to ensure errors are surfaced.
    """
    return subprocess.run(  # nosec B603
        list(cmd),
        cwd=None,
        capture_output=capture_output,
        text=text,
        check=check,
        timeout=timeout,
        shell=False,
    )


def x_run__mutmut_6(
    cmd: Sequence[str],
    *,
    cwd: Path | None = None,
    capture_output: bool = False,
    text: bool = True,
    check: bool = True,
    timeout: float | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run *cmd* securely.

    Parameters mirror :func:`subprocess.run` but ``shell`` is always ``False`` and
    ``check`` defaults to ``True`` to ensure errors are surfaced.
    """
    return subprocess.run(  # nosec B603
        list(cmd),
        cwd=cwd,
        capture_output=None,
        text=text,
        check=check,
        timeout=timeout,
        shell=False,
    )


def x_run__mutmut_7(
    cmd: Sequence[str],
    *,
    cwd: Path | None = None,
    capture_output: bool = False,
    text: bool = True,
    check: bool = True,
    timeout: float | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run *cmd* securely.

    Parameters mirror :func:`subprocess.run` but ``shell`` is always ``False`` and
    ``check`` defaults to ``True`` to ensure errors are surfaced.
    """
    return subprocess.run(  # nosec B603
        list(cmd),
        cwd=cwd,
        capture_output=capture_output,
        text=None,
        check=check,
        timeout=timeout,
        shell=False,
    )


def x_run__mutmut_8(
    cmd: Sequence[str],
    *,
    cwd: Path | None = None,
    capture_output: bool = False,
    text: bool = True,
    check: bool = True,
    timeout: float | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run *cmd* securely.

    Parameters mirror :func:`subprocess.run` but ``shell`` is always ``False`` and
    ``check`` defaults to ``True`` to ensure errors are surfaced.
    """
    return subprocess.run(  # nosec B603
        list(cmd),
        cwd=cwd,
        capture_output=capture_output,
        text=text,
        check=None,
        timeout=timeout,
        shell=False,
    )


def x_run__mutmut_9(
    cmd: Sequence[str],
    *,
    cwd: Path | None = None,
    capture_output: bool = False,
    text: bool = True,
    check: bool = True,
    timeout: float | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run *cmd* securely.

    Parameters mirror :func:`subprocess.run` but ``shell`` is always ``False`` and
    ``check`` defaults to ``True`` to ensure errors are surfaced.
    """
    return subprocess.run(  # nosec B603
        list(cmd),
        cwd=cwd,
        capture_output=capture_output,
        text=text,
        check=check,
        timeout=None,
        shell=False,
    )


def x_run__mutmut_10(
    cmd: Sequence[str],
    *,
    cwd: Path | None = None,
    capture_output: bool = False,
    text: bool = True,
    check: bool = True,
    timeout: float | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run *cmd* securely.

    Parameters mirror :func:`subprocess.run` but ``shell`` is always ``False`` and
    ``check`` defaults to ``True`` to ensure errors are surfaced.
    """
    return subprocess.run(  # nosec B603
        list(cmd),
        cwd=cwd,
        capture_output=capture_output,
        text=text,
        check=check,
        timeout=timeout,
        shell=None,
    )


def x_run__mutmut_11(
    cmd: Sequence[str],
    *,
    cwd: Path | None = None,
    capture_output: bool = False,
    text: bool = True,
    check: bool = True,
    timeout: float | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run *cmd* securely.

    Parameters mirror :func:`subprocess.run` but ``shell`` is always ``False`` and
    ``check`` defaults to ``True`` to ensure errors are surfaced.
    """
    return subprocess.run(  # nosec B603
        cwd=cwd,
        capture_output=capture_output,
        text=text,
        check=check,
        timeout=timeout,
        shell=False,
    )


def x_run__mutmut_12(
    cmd: Sequence[str],
    *,
    cwd: Path | None = None,
    capture_output: bool = False,
    text: bool = True,
    check: bool = True,
    timeout: float | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run *cmd* securely.

    Parameters mirror :func:`subprocess.run` but ``shell`` is always ``False`` and
    ``check`` defaults to ``True`` to ensure errors are surfaced.
    """
    return subprocess.run(  # nosec B603
        list(cmd),
        capture_output=capture_output,
        text=text,
        check=check,
        timeout=timeout,
        shell=False,
    )


def x_run__mutmut_13(
    cmd: Sequence[str],
    *,
    cwd: Path | None = None,
    capture_output: bool = False,
    text: bool = True,
    check: bool = True,
    timeout: float | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run *cmd* securely.

    Parameters mirror :func:`subprocess.run` but ``shell`` is always ``False`` and
    ``check`` defaults to ``True`` to ensure errors are surfaced.
    """
    return subprocess.run(  # nosec B603
        list(cmd),
        cwd=cwd,
        text=text,
        check=check,
        timeout=timeout,
        shell=False,
    )


def x_run__mutmut_14(
    cmd: Sequence[str],
    *,
    cwd: Path | None = None,
    capture_output: bool = False,
    text: bool = True,
    check: bool = True,
    timeout: float | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run *cmd* securely.

    Parameters mirror :func:`subprocess.run` but ``shell`` is always ``False`` and
    ``check`` defaults to ``True`` to ensure errors are surfaced.
    """
    return subprocess.run(  # nosec B603
        list(cmd),
        cwd=cwd,
        capture_output=capture_output,
        check=check,
        timeout=timeout,
        shell=False,
    )


def x_run__mutmut_15(
    cmd: Sequence[str],
    *,
    cwd: Path | None = None,
    capture_output: bool = False,
    text: bool = True,
    check: bool = True,
    timeout: float | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run *cmd* securely.

    Parameters mirror :func:`subprocess.run` but ``shell`` is always ``False`` and
    ``check`` defaults to ``True`` to ensure errors are surfaced.
    """
    return subprocess.run(  # nosec B603
        list(cmd),
        cwd=cwd,
        capture_output=capture_output,
        text=text,
        timeout=timeout,
        shell=False,
    )


def x_run__mutmut_16(
    cmd: Sequence[str],
    *,
    cwd: Path | None = None,
    capture_output: bool = False,
    text: bool = True,
    check: bool = True,
    timeout: float | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run *cmd* securely.

    Parameters mirror :func:`subprocess.run` but ``shell`` is always ``False`` and
    ``check`` defaults to ``True`` to ensure errors are surfaced.
    """
    return subprocess.run(  # nosec B603
        list(cmd),
        cwd=cwd,
        capture_output=capture_output,
        text=text,
        check=check,
        shell=False,
    )


def x_run__mutmut_17(
    cmd: Sequence[str],
    *,
    cwd: Path | None = None,
    capture_output: bool = False,
    text: bool = True,
    check: bool = True,
    timeout: float | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run *cmd* securely.

    Parameters mirror :func:`subprocess.run` but ``shell`` is always ``False`` and
    ``check`` defaults to ``True`` to ensure errors are surfaced.
    """
    return subprocess.run(  # nosec B603
        list(cmd),
        cwd=cwd,
        capture_output=capture_output,
        text=text,
        check=check,
        timeout=timeout,
        )


def x_run__mutmut_18(
    cmd: Sequence[str],
    *,
    cwd: Path | None = None,
    capture_output: bool = False,
    text: bool = True,
    check: bool = True,
    timeout: float | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run *cmd* securely.

    Parameters mirror :func:`subprocess.run` but ``shell`` is always ``False`` and
    ``check`` defaults to ``True`` to ensure errors are surfaced.
    """
    return subprocess.run(  # nosec B603
        list(None),
        cwd=cwd,
        capture_output=capture_output,
        text=text,
        check=check,
        timeout=timeout,
        shell=False,
    )


def x_run__mutmut_19(
    cmd: Sequence[str],
    *,
    cwd: Path | None = None,
    capture_output: bool = False,
    text: bool = True,
    check: bool = True,
    timeout: float | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run *cmd* securely.

    Parameters mirror :func:`subprocess.run` but ``shell`` is always ``False`` and
    ``check`` defaults to ``True`` to ensure errors are surfaced.
    """
    return subprocess.run(  # nosec B603
        list(cmd),
        cwd=cwd,
        capture_output=capture_output,
        text=text,
        check=check,
        timeout=timeout,
        shell=True,
    )

x_run__mutmut_mutants : ClassVar[MutantDict] = {
'x_run__mutmut_1': x_run__mutmut_1, 
    'x_run__mutmut_2': x_run__mutmut_2, 
    'x_run__mutmut_3': x_run__mutmut_3, 
    'x_run__mutmut_4': x_run__mutmut_4, 
    'x_run__mutmut_5': x_run__mutmut_5, 
    'x_run__mutmut_6': x_run__mutmut_6, 
    'x_run__mutmut_7': x_run__mutmut_7, 
    'x_run__mutmut_8': x_run__mutmut_8, 
    'x_run__mutmut_9': x_run__mutmut_9, 
    'x_run__mutmut_10': x_run__mutmut_10, 
    'x_run__mutmut_11': x_run__mutmut_11, 
    'x_run__mutmut_12': x_run__mutmut_12, 
    'x_run__mutmut_13': x_run__mutmut_13, 
    'x_run__mutmut_14': x_run__mutmut_14, 
    'x_run__mutmut_15': x_run__mutmut_15, 
    'x_run__mutmut_16': x_run__mutmut_16, 
    'x_run__mutmut_17': x_run__mutmut_17, 
    'x_run__mutmut_18': x_run__mutmut_18, 
    'x_run__mutmut_19': x_run__mutmut_19
}

def run(*args, **kwargs):
    result = _mutmut_trampoline(x_run__mutmut_orig, x_run__mutmut_mutants, args, kwargs)
    return result 

run.__signature__ = _mutmut_signature(x_run__mutmut_orig)
x_run__mutmut_orig.__name__ = 'x_run'
