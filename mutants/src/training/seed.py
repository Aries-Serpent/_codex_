"""Utilities for establishing deterministic seeds in lightweight training loops."""

from __future__ import annotations

from typing import Optional

from codex_ml.utils.repro import set_seed as _set_seed

_DEFAULT_SEED = 42
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


def x_ensure_global_seed__mutmut_orig(seed: Optional[int] = None, *, deterministic: bool = True) -> int:
    """Resolve ``seed`` to an integer and propagate it via :func:`set_seed`.

    Parameters
    ----------
    seed:
        Optional user-provided seed. When ``None`` a sensible default is used so
        call sites can simply invoke :func:`ensure_global_seed()` to obtain a
        reproducible configuration.
    deterministic:
        Forwarded to :func:`codex_ml.utils.repro.set_seed` to toggle deterministic
        backend behaviour.

    Returns
    -------
    int
        The resolved seed value. Returning the seed makes it trivial for callers
        to persist the decision alongside checkpoints or logs.
    """

    resolved = int(seed) if seed is not None else _DEFAULT_SEED
    _set_seed(resolved, deterministic=deterministic)
    return resolved


def x_ensure_global_seed__mutmut_1(seed: Optional[int] = None, *, deterministic: bool = False) -> int:
    """Resolve ``seed`` to an integer and propagate it via :func:`set_seed`.

    Parameters
    ----------
    seed:
        Optional user-provided seed. When ``None`` a sensible default is used so
        call sites can simply invoke :func:`ensure_global_seed()` to obtain a
        reproducible configuration.
    deterministic:
        Forwarded to :func:`codex_ml.utils.repro.set_seed` to toggle deterministic
        backend behaviour.

    Returns
    -------
    int
        The resolved seed value. Returning the seed makes it trivial for callers
        to persist the decision alongside checkpoints or logs.
    """

    resolved = int(seed) if seed is not None else _DEFAULT_SEED
    _set_seed(resolved, deterministic=deterministic)
    return resolved


def x_ensure_global_seed__mutmut_2(seed: Optional[int] = None, *, deterministic: bool = True) -> int:
    """Resolve ``seed`` to an integer and propagate it via :func:`set_seed`.

    Parameters
    ----------
    seed:
        Optional user-provided seed. When ``None`` a sensible default is used so
        call sites can simply invoke :func:`ensure_global_seed()` to obtain a
        reproducible configuration.
    deterministic:
        Forwarded to :func:`codex_ml.utils.repro.set_seed` to toggle deterministic
        backend behaviour.

    Returns
    -------
    int
        The resolved seed value. Returning the seed makes it trivial for callers
        to persist the decision alongside checkpoints or logs.
    """

    resolved = None
    _set_seed(resolved, deterministic=deterministic)
    return resolved


def x_ensure_global_seed__mutmut_3(seed: Optional[int] = None, *, deterministic: bool = True) -> int:
    """Resolve ``seed`` to an integer and propagate it via :func:`set_seed`.

    Parameters
    ----------
    seed:
        Optional user-provided seed. When ``None`` a sensible default is used so
        call sites can simply invoke :func:`ensure_global_seed()` to obtain a
        reproducible configuration.
    deterministic:
        Forwarded to :func:`codex_ml.utils.repro.set_seed` to toggle deterministic
        backend behaviour.

    Returns
    -------
    int
        The resolved seed value. Returning the seed makes it trivial for callers
        to persist the decision alongside checkpoints or logs.
    """

    resolved = int(None) if seed is not None else _DEFAULT_SEED
    _set_seed(resolved, deterministic=deterministic)
    return resolved


def x_ensure_global_seed__mutmut_4(seed: Optional[int] = None, *, deterministic: bool = True) -> int:
    """Resolve ``seed`` to an integer and propagate it via :func:`set_seed`.

    Parameters
    ----------
    seed:
        Optional user-provided seed. When ``None`` a sensible default is used so
        call sites can simply invoke :func:`ensure_global_seed()` to obtain a
        reproducible configuration.
    deterministic:
        Forwarded to :func:`codex_ml.utils.repro.set_seed` to toggle deterministic
        backend behaviour.

    Returns
    -------
    int
        The resolved seed value. Returning the seed makes it trivial for callers
        to persist the decision alongside checkpoints or logs.
    """

    resolved = int(seed) if seed is None else _DEFAULT_SEED
    _set_seed(resolved, deterministic=deterministic)
    return resolved


def x_ensure_global_seed__mutmut_5(seed: Optional[int] = None, *, deterministic: bool = True) -> int:
    """Resolve ``seed`` to an integer and propagate it via :func:`set_seed`.

    Parameters
    ----------
    seed:
        Optional user-provided seed. When ``None`` a sensible default is used so
        call sites can simply invoke :func:`ensure_global_seed()` to obtain a
        reproducible configuration.
    deterministic:
        Forwarded to :func:`codex_ml.utils.repro.set_seed` to toggle deterministic
        backend behaviour.

    Returns
    -------
    int
        The resolved seed value. Returning the seed makes it trivial for callers
        to persist the decision alongside checkpoints or logs.
    """

    resolved = int(seed) if seed is not None else _DEFAULT_SEED
    _set_seed(None, deterministic=deterministic)
    return resolved


def x_ensure_global_seed__mutmut_6(seed: Optional[int] = None, *, deterministic: bool = True) -> int:
    """Resolve ``seed`` to an integer and propagate it via :func:`set_seed`.

    Parameters
    ----------
    seed:
        Optional user-provided seed. When ``None`` a sensible default is used so
        call sites can simply invoke :func:`ensure_global_seed()` to obtain a
        reproducible configuration.
    deterministic:
        Forwarded to :func:`codex_ml.utils.repro.set_seed` to toggle deterministic
        backend behaviour.

    Returns
    -------
    int
        The resolved seed value. Returning the seed makes it trivial for callers
        to persist the decision alongside checkpoints or logs.
    """

    resolved = int(seed) if seed is not None else _DEFAULT_SEED
    _set_seed(resolved, deterministic=None)
    return resolved


def x_ensure_global_seed__mutmut_7(seed: Optional[int] = None, *, deterministic: bool = True) -> int:
    """Resolve ``seed`` to an integer and propagate it via :func:`set_seed`.

    Parameters
    ----------
    seed:
        Optional user-provided seed. When ``None`` a sensible default is used so
        call sites can simply invoke :func:`ensure_global_seed()` to obtain a
        reproducible configuration.
    deterministic:
        Forwarded to :func:`codex_ml.utils.repro.set_seed` to toggle deterministic
        backend behaviour.

    Returns
    -------
    int
        The resolved seed value. Returning the seed makes it trivial for callers
        to persist the decision alongside checkpoints or logs.
    """

    resolved = int(seed) if seed is not None else _DEFAULT_SEED
    _set_seed(deterministic=deterministic)
    return resolved


def x_ensure_global_seed__mutmut_8(seed: Optional[int] = None, *, deterministic: bool = True) -> int:
    """Resolve ``seed`` to an integer and propagate it via :func:`set_seed`.

    Parameters
    ----------
    seed:
        Optional user-provided seed. When ``None`` a sensible default is used so
        call sites can simply invoke :func:`ensure_global_seed()` to obtain a
        reproducible configuration.
    deterministic:
        Forwarded to :func:`codex_ml.utils.repro.set_seed` to toggle deterministic
        backend behaviour.

    Returns
    -------
    int
        The resolved seed value. Returning the seed makes it trivial for callers
        to persist the decision alongside checkpoints or logs.
    """

    resolved = int(seed) if seed is not None else _DEFAULT_SEED
    _set_seed(resolved, )
    return resolved

x_ensure_global_seed__mutmut_mutants : ClassVar[MutantDict] = {
'x_ensure_global_seed__mutmut_1': x_ensure_global_seed__mutmut_1, 
    'x_ensure_global_seed__mutmut_2': x_ensure_global_seed__mutmut_2, 
    'x_ensure_global_seed__mutmut_3': x_ensure_global_seed__mutmut_3, 
    'x_ensure_global_seed__mutmut_4': x_ensure_global_seed__mutmut_4, 
    'x_ensure_global_seed__mutmut_5': x_ensure_global_seed__mutmut_5, 
    'x_ensure_global_seed__mutmut_6': x_ensure_global_seed__mutmut_6, 
    'x_ensure_global_seed__mutmut_7': x_ensure_global_seed__mutmut_7, 
    'x_ensure_global_seed__mutmut_8': x_ensure_global_seed__mutmut_8
}

def ensure_global_seed(*args, **kwargs):
    result = _mutmut_trampoline(x_ensure_global_seed__mutmut_orig, x_ensure_global_seed__mutmut_mutants, args, kwargs)
    return result 

ensure_global_seed.__signature__ = _mutmut_signature(x_ensure_global_seed__mutmut_orig)
x_ensure_global_seed__mutmut_orig.__name__ = 'x_ensure_global_seed'


__all__ = ["ensure_global_seed"]
