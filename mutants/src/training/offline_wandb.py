"""Utilities to ensure WandB stays offline in audit environments."""

from __future__ import annotations

import os
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


def x_force_offline__mutmut_orig() -> None:
    """Default WandB to offline mode without clobbering existing settings."""

    os.environ.setdefault("WANDB_MODE", "offline")


def x_force_offline__mutmut_1() -> None:
    """Default WandB to offline mode without clobbering existing settings."""

    os.environ.setdefault(None, "offline")


def x_force_offline__mutmut_2() -> None:
    """Default WandB to offline mode without clobbering existing settings."""

    os.environ.setdefault("WANDB_MODE", None)


def x_force_offline__mutmut_3() -> None:
    """Default WandB to offline mode without clobbering existing settings."""

    os.environ.setdefault("offline")


def x_force_offline__mutmut_4() -> None:
    """Default WandB to offline mode without clobbering existing settings."""

    os.environ.setdefault("WANDB_MODE", )


def x_force_offline__mutmut_5() -> None:
    """Default WandB to offline mode without clobbering existing settings."""

    os.environ.setdefault("XXWANDB_MODEXX", "offline")


def x_force_offline__mutmut_6() -> None:
    """Default WandB to offline mode without clobbering existing settings."""

    os.environ.setdefault("wandb_mode", "offline")


def x_force_offline__mutmut_7() -> None:
    """Default WandB to offline mode without clobbering existing settings."""

    os.environ.setdefault("WANDB_MODE", "XXofflineXX")


def x_force_offline__mutmut_8() -> None:
    """Default WandB to offline mode without clobbering existing settings."""

    os.environ.setdefault("WANDB_MODE", "OFFLINE")

x_force_offline__mutmut_mutants : ClassVar[MutantDict] = {
'x_force_offline__mutmut_1': x_force_offline__mutmut_1, 
    'x_force_offline__mutmut_2': x_force_offline__mutmut_2, 
    'x_force_offline__mutmut_3': x_force_offline__mutmut_3, 
    'x_force_offline__mutmut_4': x_force_offline__mutmut_4, 
    'x_force_offline__mutmut_5': x_force_offline__mutmut_5, 
    'x_force_offline__mutmut_6': x_force_offline__mutmut_6, 
    'x_force_offline__mutmut_7': x_force_offline__mutmut_7, 
    'x_force_offline__mutmut_8': x_force_offline__mutmut_8
}

def force_offline(*args, **kwargs):
    result = _mutmut_trampoline(x_force_offline__mutmut_orig, x_force_offline__mutmut_mutants, args, kwargs)
    return result 

force_offline.__signature__ = _mutmut_signature(x_force_offline__mutmut_orig)
x_force_offline__mutmut_orig.__name__ = 'x_force_offline'


__all__ = ["force_offline"]
