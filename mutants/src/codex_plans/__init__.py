"""Codex planning package.

This module provides a namespace for repository planning artifacts used in
continuous improvement tasks. It intentionally remains lightweight to allow
packaging tools to include the plan documents alongside source code.
"""

from __future__ import annotations

from pathlib import Path

__all__ = ["list_plan_documents"]
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


def x_list_plan_documents__mutmut_orig(base_dir: Path | None = None) -> list[Path]:
    """Return available plan documents within the ``codex_plans`` package.

    Parameters
    ----------
    base_dir:
        Optional override for the root search directory. Defaults to the
        directory containing this module.

    Returns
    -------
    list[pathlib.Path]
        Sorted list of Markdown files representing execution plans.
    """

    root = base_dir or Path(__file__).resolve().parent
    return sorted(root.glob("*.md"))


def x_list_plan_documents__mutmut_1(base_dir: Path | None = None) -> list[Path]:
    """Return available plan documents within the ``codex_plans`` package.

    Parameters
    ----------
    base_dir:
        Optional override for the root search directory. Defaults to the
        directory containing this module.

    Returns
    -------
    list[pathlib.Path]
        Sorted list of Markdown files representing execution plans.
    """

    root = None
    return sorted(root.glob("*.md"))


def x_list_plan_documents__mutmut_2(base_dir: Path | None = None) -> list[Path]:
    """Return available plan documents within the ``codex_plans`` package.

    Parameters
    ----------
    base_dir:
        Optional override for the root search directory. Defaults to the
        directory containing this module.

    Returns
    -------
    list[pathlib.Path]
        Sorted list of Markdown files representing execution plans.
    """

    root = base_dir and Path(__file__).resolve().parent
    return sorted(root.glob("*.md"))


def x_list_plan_documents__mutmut_3(base_dir: Path | None = None) -> list[Path]:
    """Return available plan documents within the ``codex_plans`` package.

    Parameters
    ----------
    base_dir:
        Optional override for the root search directory. Defaults to the
        directory containing this module.

    Returns
    -------
    list[pathlib.Path]
        Sorted list of Markdown files representing execution plans.
    """

    root = base_dir or Path(None).resolve().parent
    return sorted(root.glob("*.md"))


def x_list_plan_documents__mutmut_4(base_dir: Path | None = None) -> list[Path]:
    """Return available plan documents within the ``codex_plans`` package.

    Parameters
    ----------
    base_dir:
        Optional override for the root search directory. Defaults to the
        directory containing this module.

    Returns
    -------
    list[pathlib.Path]
        Sorted list of Markdown files representing execution plans.
    """

    root = base_dir or Path(__file__).resolve().parent
    return sorted(None)


def x_list_plan_documents__mutmut_5(base_dir: Path | None = None) -> list[Path]:
    """Return available plan documents within the ``codex_plans`` package.

    Parameters
    ----------
    base_dir:
        Optional override for the root search directory. Defaults to the
        directory containing this module.

    Returns
    -------
    list[pathlib.Path]
        Sorted list of Markdown files representing execution plans.
    """

    root = base_dir or Path(__file__).resolve().parent
    return sorted(root.glob(None))


def x_list_plan_documents__mutmut_6(base_dir: Path | None = None) -> list[Path]:
    """Return available plan documents within the ``codex_plans`` package.

    Parameters
    ----------
    base_dir:
        Optional override for the root search directory. Defaults to the
        directory containing this module.

    Returns
    -------
    list[pathlib.Path]
        Sorted list of Markdown files representing execution plans.
    """

    root = base_dir or Path(__file__).resolve().parent
    return sorted(root.glob("XX*.mdXX"))


def x_list_plan_documents__mutmut_7(base_dir: Path | None = None) -> list[Path]:
    """Return available plan documents within the ``codex_plans`` package.

    Parameters
    ----------
    base_dir:
        Optional override for the root search directory. Defaults to the
        directory containing this module.

    Returns
    -------
    list[pathlib.Path]
        Sorted list of Markdown files representing execution plans.
    """

    root = base_dir or Path(__file__).resolve().parent
    return sorted(root.glob("*.MD"))

x_list_plan_documents__mutmut_mutants : ClassVar[MutantDict] = {
'x_list_plan_documents__mutmut_1': x_list_plan_documents__mutmut_1, 
    'x_list_plan_documents__mutmut_2': x_list_plan_documents__mutmut_2, 
    'x_list_plan_documents__mutmut_3': x_list_plan_documents__mutmut_3, 
    'x_list_plan_documents__mutmut_4': x_list_plan_documents__mutmut_4, 
    'x_list_plan_documents__mutmut_5': x_list_plan_documents__mutmut_5, 
    'x_list_plan_documents__mutmut_6': x_list_plan_documents__mutmut_6, 
    'x_list_plan_documents__mutmut_7': x_list_plan_documents__mutmut_7
}

def list_plan_documents(*args, **kwargs):
    result = _mutmut_trampoline(x_list_plan_documents__mutmut_orig, x_list_plan_documents__mutmut_mutants, args, kwargs)
    return result 

list_plan_documents.__signature__ = _mutmut_signature(x_list_plan_documents__mutmut_orig)
x_list_plan_documents__mutmut_orig.__name__ = 'x_list_plan_documents'
