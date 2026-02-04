"""
Legacy checkpointing manager (compat shim).

Prefer codex_ml.utils.checkpointing.CheckpointManager for new code.
"""

from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

import random as _random
import warnings as _warnings
from typing import Any

_warnings.warn(
    "src.utils.checkpointing is legacy; use codex_ml.utils.checkpointing for new code.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export canonical manager where compatible, to reduce duplication.
try:  # pragma: no cover - mirror class
    from codex_ml.utils.checkpointing import CheckpointManager  # type: ignore
except Exception:  # pragma: no cover - defensive
    CheckpointManager = object  # type: ignore[misc,assignment]


try:  # pragma: no cover - prefer canonical RNG helpers
    from codex_ml.utils.checkpoint_core import (
        dump_rng_state as _canonical_dump_rng_state,  # type: ignore
    )
    from codex_ml.utils.checkpoint_core import (
        load_rng_state as _canonical_load_rng_state,
    )
    from codex_ml.utils.checkpoint_core import set_seed as _canonical_set_seed
except Exception:  # pragma: no cover - canonical RNG helpers unavailable
    _canonical_dump_rng_state = None  # type: ignore[assignment]
    _canonical_load_rng_state = None  # type: ignore[assignment]
    _canonical_set_seed = None  # type: ignore[assignment]

try:  # pragma: no cover - optional numpy
    import numpy as _np
except Exception:  # pragma: no cover - numpy optional
    _np = None  # type: ignore[assignment]

try:  # pragma: no cover - optional torch
    import torch as _torch
except Exception:  # pragma: no cover - torch optional
    _torch = None  # type: ignore[assignment]
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


# Optional helper aliases to ease migration of call-sites
def x_save_ckpt__mutmut_orig(*args, **kwargs):  # pragma: no cover - passthrough
    from codex_ml.utils.checkpoint_core import save_checkpoint as _save  # type: ignore

    return _save(*args, **kwargs)


# Optional helper aliases to ease migration of call-sites
def x_save_ckpt__mutmut_1(*args, **kwargs):  # pragma: no cover - passthrough
    from codex_ml.utils.checkpoint_core import save_checkpoint as _save  # type: ignore

    return _save(**kwargs)


# Optional helper aliases to ease migration of call-sites
def x_save_ckpt__mutmut_2(*args, **kwargs):  # pragma: no cover - passthrough
    from codex_ml.utils.checkpoint_core import save_checkpoint as _save  # type: ignore

    return _save(*args, )

x_save_ckpt__mutmut_mutants : ClassVar[MutantDict] = {
'x_save_ckpt__mutmut_1': x_save_ckpt__mutmut_1, 
    'x_save_ckpt__mutmut_2': x_save_ckpt__mutmut_2
}

def save_ckpt(*args, **kwargs):
    result = _mutmut_trampoline(x_save_ckpt__mutmut_orig, x_save_ckpt__mutmut_mutants, args, kwargs)
    return result 

save_ckpt.__signature__ = _mutmut_signature(x_save_ckpt__mutmut_orig)
x_save_ckpt__mutmut_orig.__name__ = 'x_save_ckpt'


def x_verify_ckpt_integrity__mutmut_orig(*args, **kwargs):  # pragma: no cover - passthrough
    from codex_ml.utils.checkpoint_core import (
        verify_checkpoint as _verify,  # type: ignore
    )

    return _verify(*args, **kwargs)


def x_verify_ckpt_integrity__mutmut_1(*args, **kwargs):  # pragma: no cover - passthrough
    from codex_ml.utils.checkpoint_core import (
        verify_checkpoint as _verify,  # type: ignore
    )

    return _verify(**kwargs)


def x_verify_ckpt_integrity__mutmut_2(*args, **kwargs):  # pragma: no cover - passthrough
    from codex_ml.utils.checkpoint_core import (
        verify_checkpoint as _verify,  # type: ignore
    )

    return _verify(*args, )

x_verify_ckpt_integrity__mutmut_mutants : ClassVar[MutantDict] = {
'x_verify_ckpt_integrity__mutmut_1': x_verify_ckpt_integrity__mutmut_1, 
    'x_verify_ckpt_integrity__mutmut_2': x_verify_ckpt_integrity__mutmut_2
}

def verify_ckpt_integrity(*args, **kwargs):
    result = _mutmut_trampoline(x_verify_ckpt_integrity__mutmut_orig, x_verify_ckpt_integrity__mutmut_mutants, args, kwargs)
    return result 

verify_ckpt_integrity.__signature__ = _mutmut_signature(x_verify_ckpt_integrity__mutmut_orig)
x_verify_ckpt_integrity__mutmut_orig.__name__ = 'x_verify_ckpt_integrity'


def x_dump_rng_state__mutmut_orig() -> dict[str, Any]:  # pragma: no cover - passthrough
    """Capture RNG state while preserving legacy structure."""

    if _canonical_dump_rng_state is not None:
        return _canonical_dump_rng_state()

    state: dict[str, Any] = {"python": _random.getstate()}
    if _np is not None:
        state["numpy"] = _np.random.get_state()
    if _torch is not None:
        torch_state = {"cpu": _torch.random.get_rng_state().tolist()}
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
        ):
            torch_state["cuda"] = [
                s.tolist() for s in cuda_mod.get_rng_state_all()
            ]  # pragma: no cover - cuda optional
        state["torch"] = torch_state
    return state


def x_dump_rng_state__mutmut_1() -> dict[str, Any]:  # pragma: no cover - passthrough
    """Capture RNG state while preserving legacy structure."""

    if _canonical_dump_rng_state is None:
        return _canonical_dump_rng_state()

    state: dict[str, Any] = {"python": _random.getstate()}
    if _np is not None:
        state["numpy"] = _np.random.get_state()
    if _torch is not None:
        torch_state = {"cpu": _torch.random.get_rng_state().tolist()}
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
        ):
            torch_state["cuda"] = [
                s.tolist() for s in cuda_mod.get_rng_state_all()
            ]  # pragma: no cover - cuda optional
        state["torch"] = torch_state
    return state


def x_dump_rng_state__mutmut_2() -> dict[str, Any]:  # pragma: no cover - passthrough
    """Capture RNG state while preserving legacy structure."""

    if _canonical_dump_rng_state is not None:
        return _canonical_dump_rng_state()

    state: dict[str, Any] = None
    if _np is not None:
        state["numpy"] = _np.random.get_state()
    if _torch is not None:
        torch_state = {"cpu": _torch.random.get_rng_state().tolist()}
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
        ):
            torch_state["cuda"] = [
                s.tolist() for s in cuda_mod.get_rng_state_all()
            ]  # pragma: no cover - cuda optional
        state["torch"] = torch_state
    return state


def x_dump_rng_state__mutmut_3() -> dict[str, Any]:  # pragma: no cover - passthrough
    """Capture RNG state while preserving legacy structure."""

    if _canonical_dump_rng_state is not None:
        return _canonical_dump_rng_state()

    state: dict[str, Any] = {"XXpythonXX": _random.getstate()}
    if _np is not None:
        state["numpy"] = _np.random.get_state()
    if _torch is not None:
        torch_state = {"cpu": _torch.random.get_rng_state().tolist()}
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
        ):
            torch_state["cuda"] = [
                s.tolist() for s in cuda_mod.get_rng_state_all()
            ]  # pragma: no cover - cuda optional
        state["torch"] = torch_state
    return state


def x_dump_rng_state__mutmut_4() -> dict[str, Any]:  # pragma: no cover - passthrough
    """Capture RNG state while preserving legacy structure."""

    if _canonical_dump_rng_state is not None:
        return _canonical_dump_rng_state()

    state: dict[str, Any] = {"PYTHON": _random.getstate()}
    if _np is not None:
        state["numpy"] = _np.random.get_state()
    if _torch is not None:
        torch_state = {"cpu": _torch.random.get_rng_state().tolist()}
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
        ):
            torch_state["cuda"] = [
                s.tolist() for s in cuda_mod.get_rng_state_all()
            ]  # pragma: no cover - cuda optional
        state["torch"] = torch_state
    return state


def x_dump_rng_state__mutmut_5() -> dict[str, Any]:  # pragma: no cover - passthrough
    """Capture RNG state while preserving legacy structure."""

    if _canonical_dump_rng_state is not None:
        return _canonical_dump_rng_state()

    state: dict[str, Any] = {"python": _random.getstate()}
    if _np is None:
        state["numpy"] = _np.random.get_state()
    if _torch is not None:
        torch_state = {"cpu": _torch.random.get_rng_state().tolist()}
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
        ):
            torch_state["cuda"] = [
                s.tolist() for s in cuda_mod.get_rng_state_all()
            ]  # pragma: no cover - cuda optional
        state["torch"] = torch_state
    return state


def x_dump_rng_state__mutmut_6() -> dict[str, Any]:  # pragma: no cover - passthrough
    """Capture RNG state while preserving legacy structure."""

    if _canonical_dump_rng_state is not None:
        return _canonical_dump_rng_state()

    state: dict[str, Any] = {"python": _random.getstate()}
    if _np is not None:
        state["numpy"] = None
    if _torch is not None:
        torch_state = {"cpu": _torch.random.get_rng_state().tolist()}
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
        ):
            torch_state["cuda"] = [
                s.tolist() for s in cuda_mod.get_rng_state_all()
            ]  # pragma: no cover - cuda optional
        state["torch"] = torch_state
    return state


def x_dump_rng_state__mutmut_7() -> dict[str, Any]:  # pragma: no cover - passthrough
    """Capture RNG state while preserving legacy structure."""

    if _canonical_dump_rng_state is not None:
        return _canonical_dump_rng_state()

    state: dict[str, Any] = {"python": _random.getstate()}
    if _np is not None:
        state["XXnumpyXX"] = _np.random.get_state()
    if _torch is not None:
        torch_state = {"cpu": _torch.random.get_rng_state().tolist()}
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
        ):
            torch_state["cuda"] = [
                s.tolist() for s in cuda_mod.get_rng_state_all()
            ]  # pragma: no cover - cuda optional
        state["torch"] = torch_state
    return state


def x_dump_rng_state__mutmut_8() -> dict[str, Any]:  # pragma: no cover - passthrough
    """Capture RNG state while preserving legacy structure."""

    if _canonical_dump_rng_state is not None:
        return _canonical_dump_rng_state()

    state: dict[str, Any] = {"python": _random.getstate()}
    if _np is not None:
        state["NUMPY"] = _np.random.get_state()
    if _torch is not None:
        torch_state = {"cpu": _torch.random.get_rng_state().tolist()}
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
        ):
            torch_state["cuda"] = [
                s.tolist() for s in cuda_mod.get_rng_state_all()
            ]  # pragma: no cover - cuda optional
        state["torch"] = torch_state
    return state


def x_dump_rng_state__mutmut_9() -> dict[str, Any]:  # pragma: no cover - passthrough
    """Capture RNG state while preserving legacy structure."""

    if _canonical_dump_rng_state is not None:
        return _canonical_dump_rng_state()

    state: dict[str, Any] = {"python": _random.getstate()}
    if _np is not None:
        state["numpy"] = _np.random.get_state()
    if _torch is None:
        torch_state = {"cpu": _torch.random.get_rng_state().tolist()}
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
        ):
            torch_state["cuda"] = [
                s.tolist() for s in cuda_mod.get_rng_state_all()
            ]  # pragma: no cover - cuda optional
        state["torch"] = torch_state
    return state


def x_dump_rng_state__mutmut_10() -> dict[str, Any]:  # pragma: no cover - passthrough
    """Capture RNG state while preserving legacy structure."""

    if _canonical_dump_rng_state is not None:
        return _canonical_dump_rng_state()

    state: dict[str, Any] = {"python": _random.getstate()}
    if _np is not None:
        state["numpy"] = _np.random.get_state()
    if _torch is not None:
        torch_state = None
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
        ):
            torch_state["cuda"] = [
                s.tolist() for s in cuda_mod.get_rng_state_all()
            ]  # pragma: no cover - cuda optional
        state["torch"] = torch_state
    return state


def x_dump_rng_state__mutmut_11() -> dict[str, Any]:  # pragma: no cover - passthrough
    """Capture RNG state while preserving legacy structure."""

    if _canonical_dump_rng_state is not None:
        return _canonical_dump_rng_state()

    state: dict[str, Any] = {"python": _random.getstate()}
    if _np is not None:
        state["numpy"] = _np.random.get_state()
    if _torch is not None:
        torch_state = {"XXcpuXX": _torch.random.get_rng_state().tolist()}
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
        ):
            torch_state["cuda"] = [
                s.tolist() for s in cuda_mod.get_rng_state_all()
            ]  # pragma: no cover - cuda optional
        state["torch"] = torch_state
    return state


def x_dump_rng_state__mutmut_12() -> dict[str, Any]:  # pragma: no cover - passthrough
    """Capture RNG state while preserving legacy structure."""

    if _canonical_dump_rng_state is not None:
        return _canonical_dump_rng_state()

    state: dict[str, Any] = {"python": _random.getstate()}
    if _np is not None:
        state["numpy"] = _np.random.get_state()
    if _torch is not None:
        torch_state = {"CPU": _torch.random.get_rng_state().tolist()}
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
        ):
            torch_state["cuda"] = [
                s.tolist() for s in cuda_mod.get_rng_state_all()
            ]  # pragma: no cover - cuda optional
        state["torch"] = torch_state
    return state


def x_dump_rng_state__mutmut_13() -> dict[str, Any]:  # pragma: no cover - passthrough
    """Capture RNG state while preserving legacy structure."""

    if _canonical_dump_rng_state is not None:
        return _canonical_dump_rng_state()

    state: dict[str, Any] = {"python": _random.getstate()}
    if _np is not None:
        state["numpy"] = _np.random.get_state()
    if _torch is not None:
        torch_state = {"cpu": _torch.random.get_rng_state().tolist()}
        cuda_mod = None
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
        ):
            torch_state["cuda"] = [
                s.tolist() for s in cuda_mod.get_rng_state_all()
            ]  # pragma: no cover - cuda optional
        state["torch"] = torch_state
    return state


def x_dump_rng_state__mutmut_14() -> dict[str, Any]:  # pragma: no cover - passthrough
    """Capture RNG state while preserving legacy structure."""

    if _canonical_dump_rng_state is not None:
        return _canonical_dump_rng_state()

    state: dict[str, Any] = {"python": _random.getstate()}
    if _np is not None:
        state["numpy"] = _np.random.get_state()
    if _torch is not None:
        torch_state = {"cpu": _torch.random.get_rng_state().tolist()}
        cuda_mod = getattr(None, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
        ):
            torch_state["cuda"] = [
                s.tolist() for s in cuda_mod.get_rng_state_all()
            ]  # pragma: no cover - cuda optional
        state["torch"] = torch_state
    return state


def x_dump_rng_state__mutmut_15() -> dict[str, Any]:  # pragma: no cover - passthrough
    """Capture RNG state while preserving legacy structure."""

    if _canonical_dump_rng_state is not None:
        return _canonical_dump_rng_state()

    state: dict[str, Any] = {"python": _random.getstate()}
    if _np is not None:
        state["numpy"] = _np.random.get_state()
    if _torch is not None:
        torch_state = {"cpu": _torch.random.get_rng_state().tolist()}
        cuda_mod = getattr(_torch, None, None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
        ):
            torch_state["cuda"] = [
                s.tolist() for s in cuda_mod.get_rng_state_all()
            ]  # pragma: no cover - cuda optional
        state["torch"] = torch_state
    return state


def x_dump_rng_state__mutmut_16() -> dict[str, Any]:  # pragma: no cover - passthrough
    """Capture RNG state while preserving legacy structure."""

    if _canonical_dump_rng_state is not None:
        return _canonical_dump_rng_state()

    state: dict[str, Any] = {"python": _random.getstate()}
    if _np is not None:
        state["numpy"] = _np.random.get_state()
    if _torch is not None:
        torch_state = {"cpu": _torch.random.get_rng_state().tolist()}
        cuda_mod = getattr("cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
        ):
            torch_state["cuda"] = [
                s.tolist() for s in cuda_mod.get_rng_state_all()
            ]  # pragma: no cover - cuda optional
        state["torch"] = torch_state
    return state


def x_dump_rng_state__mutmut_17() -> dict[str, Any]:  # pragma: no cover - passthrough
    """Capture RNG state while preserving legacy structure."""

    if _canonical_dump_rng_state is not None:
        return _canonical_dump_rng_state()

    state: dict[str, Any] = {"python": _random.getstate()}
    if _np is not None:
        state["numpy"] = _np.random.get_state()
    if _torch is not None:
        torch_state = {"cpu": _torch.random.get_rng_state().tolist()}
        cuda_mod = getattr(_torch, None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
        ):
            torch_state["cuda"] = [
                s.tolist() for s in cuda_mod.get_rng_state_all()
            ]  # pragma: no cover - cuda optional
        state["torch"] = torch_state
    return state


def x_dump_rng_state__mutmut_18() -> dict[str, Any]:  # pragma: no cover - passthrough
    """Capture RNG state while preserving legacy structure."""

    if _canonical_dump_rng_state is not None:
        return _canonical_dump_rng_state()

    state: dict[str, Any] = {"python": _random.getstate()}
    if _np is not None:
        state["numpy"] = _np.random.get_state()
    if _torch is not None:
        torch_state = {"cpu": _torch.random.get_rng_state().tolist()}
        cuda_mod = getattr(_torch, "cuda", )
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
        ):
            torch_state["cuda"] = [
                s.tolist() for s in cuda_mod.get_rng_state_all()
            ]  # pragma: no cover - cuda optional
        state["torch"] = torch_state
    return state


def x_dump_rng_state__mutmut_19() -> dict[str, Any]:  # pragma: no cover - passthrough
    """Capture RNG state while preserving legacy structure."""

    if _canonical_dump_rng_state is not None:
        return _canonical_dump_rng_state()

    state: dict[str, Any] = {"python": _random.getstate()}
    if _np is not None:
        state["numpy"] = _np.random.get_state()
    if _torch is not None:
        torch_state = {"cpu": _torch.random.get_rng_state().tolist()}
        cuda_mod = getattr(_torch, "XXcudaXX", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
        ):
            torch_state["cuda"] = [
                s.tolist() for s in cuda_mod.get_rng_state_all()
            ]  # pragma: no cover - cuda optional
        state["torch"] = torch_state
    return state


def x_dump_rng_state__mutmut_20() -> dict[str, Any]:  # pragma: no cover - passthrough
    """Capture RNG state while preserving legacy structure."""

    if _canonical_dump_rng_state is not None:
        return _canonical_dump_rng_state()

    state: dict[str, Any] = {"python": _random.getstate()}
    if _np is not None:
        state["numpy"] = _np.random.get_state()
    if _torch is not None:
        torch_state = {"cpu": _torch.random.get_rng_state().tolist()}
        cuda_mod = getattr(_torch, "CUDA", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
        ):
            torch_state["cuda"] = [
                s.tolist() for s in cuda_mod.get_rng_state_all()
            ]  # pragma: no cover - cuda optional
        state["torch"] = torch_state
    return state


def x_dump_rng_state__mutmut_21() -> dict[str, Any]:  # pragma: no cover - passthrough
    """Capture RNG state while preserving legacy structure."""

    if _canonical_dump_rng_state is not None:
        return _canonical_dump_rng_state()

    state: dict[str, Any] = {"python": _random.getstate()}
    if _np is not None:
        state["numpy"] = _np.random.get_state()
    if _torch is not None:
        torch_state = {"cpu": _torch.random.get_rng_state().tolist()}
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None)) or cuda_mod.is_available()
        ):
            torch_state["cuda"] = [
                s.tolist() for s in cuda_mod.get_rng_state_all()
            ]  # pragma: no cover - cuda optional
        state["torch"] = torch_state
    return state


def x_dump_rng_state__mutmut_22() -> dict[str, Any]:  # pragma: no cover - passthrough
    """Capture RNG state while preserving legacy structure."""

    if _canonical_dump_rng_state is not None:
        return _canonical_dump_rng_state()

    state: dict[str, Any] = {"python": _random.getstate()}
    if _np is not None:
        state["numpy"] = _np.random.get_state()
    if _torch is not None:
        torch_state = {"cpu": _torch.random.get_rng_state().tolist()}
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None or callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
        ):
            torch_state["cuda"] = [
                s.tolist() for s in cuda_mod.get_rng_state_all()
            ]  # pragma: no cover - cuda optional
        state["torch"] = torch_state
    return state


def x_dump_rng_state__mutmut_23() -> dict[str, Any]:  # pragma: no cover - passthrough
    """Capture RNG state while preserving legacy structure."""

    if _canonical_dump_rng_state is not None:
        return _canonical_dump_rng_state()

    state: dict[str, Any] = {"python": _random.getstate()}
    if _np is not None:
        state["numpy"] = _np.random.get_state()
    if _torch is not None:
        torch_state = {"cpu": _torch.random.get_rng_state().tolist()}
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
        ):
            torch_state["cuda"] = [
                s.tolist() for s in cuda_mod.get_rng_state_all()
            ]  # pragma: no cover - cuda optional
        state["torch"] = torch_state
    return state


def x_dump_rng_state__mutmut_24() -> dict[str, Any]:  # pragma: no cover - passthrough
    """Capture RNG state while preserving legacy structure."""

    if _canonical_dump_rng_state is not None:
        return _canonical_dump_rng_state()

    state: dict[str, Any] = {"python": _random.getstate()}
    if _np is not None:
        state["numpy"] = _np.random.get_state()
    if _torch is not None:
        torch_state = {"cpu": _torch.random.get_rng_state().tolist()}
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(None)
            and cuda_mod.is_available()
        ):
            torch_state["cuda"] = [
                s.tolist() for s in cuda_mod.get_rng_state_all()
            ]  # pragma: no cover - cuda optional
        state["torch"] = torch_state
    return state


def x_dump_rng_state__mutmut_25() -> dict[str, Any]:  # pragma: no cover - passthrough
    """Capture RNG state while preserving legacy structure."""

    if _canonical_dump_rng_state is not None:
        return _canonical_dump_rng_state()

    state: dict[str, Any] = {"python": _random.getstate()}
    if _np is not None:
        state["numpy"] = _np.random.get_state()
    if _torch is not None:
        torch_state = {"cpu": _torch.random.get_rng_state().tolist()}
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(None, "is_available", None))
            and cuda_mod.is_available()
        ):
            torch_state["cuda"] = [
                s.tolist() for s in cuda_mod.get_rng_state_all()
            ]  # pragma: no cover - cuda optional
        state["torch"] = torch_state
    return state


def x_dump_rng_state__mutmut_26() -> dict[str, Any]:  # pragma: no cover - passthrough
    """Capture RNG state while preserving legacy structure."""

    if _canonical_dump_rng_state is not None:
        return _canonical_dump_rng_state()

    state: dict[str, Any] = {"python": _random.getstate()}
    if _np is not None:
        state["numpy"] = _np.random.get_state()
    if _torch is not None:
        torch_state = {"cpu": _torch.random.get_rng_state().tolist()}
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, None, None))
            and cuda_mod.is_available()
        ):
            torch_state["cuda"] = [
                s.tolist() for s in cuda_mod.get_rng_state_all()
            ]  # pragma: no cover - cuda optional
        state["torch"] = torch_state
    return state


def x_dump_rng_state__mutmut_27() -> dict[str, Any]:  # pragma: no cover - passthrough
    """Capture RNG state while preserving legacy structure."""

    if _canonical_dump_rng_state is not None:
        return _canonical_dump_rng_state()

    state: dict[str, Any] = {"python": _random.getstate()}
    if _np is not None:
        state["numpy"] = _np.random.get_state()
    if _torch is not None:
        torch_state = {"cpu": _torch.random.get_rng_state().tolist()}
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr("is_available", None))
            and cuda_mod.is_available()
        ):
            torch_state["cuda"] = [
                s.tolist() for s in cuda_mod.get_rng_state_all()
            ]  # pragma: no cover - cuda optional
        state["torch"] = torch_state
    return state


def x_dump_rng_state__mutmut_28() -> dict[str, Any]:  # pragma: no cover - passthrough
    """Capture RNG state while preserving legacy structure."""

    if _canonical_dump_rng_state is not None:
        return _canonical_dump_rng_state()

    state: dict[str, Any] = {"python": _random.getstate()}
    if _np is not None:
        state["numpy"] = _np.random.get_state()
    if _torch is not None:
        torch_state = {"cpu": _torch.random.get_rng_state().tolist()}
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, None))
            and cuda_mod.is_available()
        ):
            torch_state["cuda"] = [
                s.tolist() for s in cuda_mod.get_rng_state_all()
            ]  # pragma: no cover - cuda optional
        state["torch"] = torch_state
    return state


def x_dump_rng_state__mutmut_29() -> dict[str, Any]:  # pragma: no cover - passthrough
    """Capture RNG state while preserving legacy structure."""

    if _canonical_dump_rng_state is not None:
        return _canonical_dump_rng_state()

    state: dict[str, Any] = {"python": _random.getstate()}
    if _np is not None:
        state["numpy"] = _np.random.get_state()
    if _torch is not None:
        torch_state = {"cpu": _torch.random.get_rng_state().tolist()}
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", ))
            and cuda_mod.is_available()
        ):
            torch_state["cuda"] = [
                s.tolist() for s in cuda_mod.get_rng_state_all()
            ]  # pragma: no cover - cuda optional
        state["torch"] = torch_state
    return state


def x_dump_rng_state__mutmut_30() -> dict[str, Any]:  # pragma: no cover - passthrough
    """Capture RNG state while preserving legacy structure."""

    if _canonical_dump_rng_state is not None:
        return _canonical_dump_rng_state()

    state: dict[str, Any] = {"python": _random.getstate()}
    if _np is not None:
        state["numpy"] = _np.random.get_state()
    if _torch is not None:
        torch_state = {"cpu": _torch.random.get_rng_state().tolist()}
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "XXis_availableXX", None))
            and cuda_mod.is_available()
        ):
            torch_state["cuda"] = [
                s.tolist() for s in cuda_mod.get_rng_state_all()
            ]  # pragma: no cover - cuda optional
        state["torch"] = torch_state
    return state


def x_dump_rng_state__mutmut_31() -> dict[str, Any]:  # pragma: no cover - passthrough
    """Capture RNG state while preserving legacy structure."""

    if _canonical_dump_rng_state is not None:
        return _canonical_dump_rng_state()

    state: dict[str, Any] = {"python": _random.getstate()}
    if _np is not None:
        state["numpy"] = _np.random.get_state()
    if _torch is not None:
        torch_state = {"cpu": _torch.random.get_rng_state().tolist()}
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "IS_AVAILABLE", None))
            and cuda_mod.is_available()
        ):
            torch_state["cuda"] = [
                s.tolist() for s in cuda_mod.get_rng_state_all()
            ]  # pragma: no cover - cuda optional
        state["torch"] = torch_state
    return state


def x_dump_rng_state__mutmut_32() -> dict[str, Any]:  # pragma: no cover - passthrough
    """Capture RNG state while preserving legacy structure."""

    if _canonical_dump_rng_state is not None:
        return _canonical_dump_rng_state()

    state: dict[str, Any] = {"python": _random.getstate()}
    if _np is not None:
        state["numpy"] = _np.random.get_state()
    if _torch is not None:
        torch_state = {"cpu": _torch.random.get_rng_state().tolist()}
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
        ):
            torch_state["cuda"] = None  # pragma: no cover - cuda optional
        state["torch"] = torch_state
    return state


def x_dump_rng_state__mutmut_33() -> dict[str, Any]:  # pragma: no cover - passthrough
    """Capture RNG state while preserving legacy structure."""

    if _canonical_dump_rng_state is not None:
        return _canonical_dump_rng_state()

    state: dict[str, Any] = {"python": _random.getstate()}
    if _np is not None:
        state["numpy"] = _np.random.get_state()
    if _torch is not None:
        torch_state = {"cpu": _torch.random.get_rng_state().tolist()}
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
        ):
            torch_state["XXcudaXX"] = [
                s.tolist() for s in cuda_mod.get_rng_state_all()
            ]  # pragma: no cover - cuda optional
        state["torch"] = torch_state
    return state


def x_dump_rng_state__mutmut_34() -> dict[str, Any]:  # pragma: no cover - passthrough
    """Capture RNG state while preserving legacy structure."""

    if _canonical_dump_rng_state is not None:
        return _canonical_dump_rng_state()

    state: dict[str, Any] = {"python": _random.getstate()}
    if _np is not None:
        state["numpy"] = _np.random.get_state()
    if _torch is not None:
        torch_state = {"cpu": _torch.random.get_rng_state().tolist()}
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
        ):
            torch_state["CUDA"] = [
                s.tolist() for s in cuda_mod.get_rng_state_all()
            ]  # pragma: no cover - cuda optional
        state["torch"] = torch_state
    return state


def x_dump_rng_state__mutmut_35() -> dict[str, Any]:  # pragma: no cover - passthrough
    """Capture RNG state while preserving legacy structure."""

    if _canonical_dump_rng_state is not None:
        return _canonical_dump_rng_state()

    state: dict[str, Any] = {"python": _random.getstate()}
    if _np is not None:
        state["numpy"] = _np.random.get_state()
    if _torch is not None:
        torch_state = {"cpu": _torch.random.get_rng_state().tolist()}
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
        ):
            torch_state["cuda"] = [
                s.tolist() for s in cuda_mod.get_rng_state_all()
            ]  # pragma: no cover - cuda optional
        state["torch"] = None
    return state


def x_dump_rng_state__mutmut_36() -> dict[str, Any]:  # pragma: no cover - passthrough
    """Capture RNG state while preserving legacy structure."""

    if _canonical_dump_rng_state is not None:
        return _canonical_dump_rng_state()

    state: dict[str, Any] = {"python": _random.getstate()}
    if _np is not None:
        state["numpy"] = _np.random.get_state()
    if _torch is not None:
        torch_state = {"cpu": _torch.random.get_rng_state().tolist()}
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
        ):
            torch_state["cuda"] = [
                s.tolist() for s in cuda_mod.get_rng_state_all()
            ]  # pragma: no cover - cuda optional
        state["XXtorchXX"] = torch_state
    return state


def x_dump_rng_state__mutmut_37() -> dict[str, Any]:  # pragma: no cover - passthrough
    """Capture RNG state while preserving legacy structure."""

    if _canonical_dump_rng_state is not None:
        return _canonical_dump_rng_state()

    state: dict[str, Any] = {"python": _random.getstate()}
    if _np is not None:
        state["numpy"] = _np.random.get_state()
    if _torch is not None:
        torch_state = {"cpu": _torch.random.get_rng_state().tolist()}
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
        ):
            torch_state["cuda"] = [
                s.tolist() for s in cuda_mod.get_rng_state_all()
            ]  # pragma: no cover - cuda optional
        state["TORCH"] = torch_state
    return state

x_dump_rng_state__mutmut_mutants : ClassVar[MutantDict] = {
'x_dump_rng_state__mutmut_1': x_dump_rng_state__mutmut_1, 
    'x_dump_rng_state__mutmut_2': x_dump_rng_state__mutmut_2, 
    'x_dump_rng_state__mutmut_3': x_dump_rng_state__mutmut_3, 
    'x_dump_rng_state__mutmut_4': x_dump_rng_state__mutmut_4, 
    'x_dump_rng_state__mutmut_5': x_dump_rng_state__mutmut_5, 
    'x_dump_rng_state__mutmut_6': x_dump_rng_state__mutmut_6, 
    'x_dump_rng_state__mutmut_7': x_dump_rng_state__mutmut_7, 
    'x_dump_rng_state__mutmut_8': x_dump_rng_state__mutmut_8, 
    'x_dump_rng_state__mutmut_9': x_dump_rng_state__mutmut_9, 
    'x_dump_rng_state__mutmut_10': x_dump_rng_state__mutmut_10, 
    'x_dump_rng_state__mutmut_11': x_dump_rng_state__mutmut_11, 
    'x_dump_rng_state__mutmut_12': x_dump_rng_state__mutmut_12, 
    'x_dump_rng_state__mutmut_13': x_dump_rng_state__mutmut_13, 
    'x_dump_rng_state__mutmut_14': x_dump_rng_state__mutmut_14, 
    'x_dump_rng_state__mutmut_15': x_dump_rng_state__mutmut_15, 
    'x_dump_rng_state__mutmut_16': x_dump_rng_state__mutmut_16, 
    'x_dump_rng_state__mutmut_17': x_dump_rng_state__mutmut_17, 
    'x_dump_rng_state__mutmut_18': x_dump_rng_state__mutmut_18, 
    'x_dump_rng_state__mutmut_19': x_dump_rng_state__mutmut_19, 
    'x_dump_rng_state__mutmut_20': x_dump_rng_state__mutmut_20, 
    'x_dump_rng_state__mutmut_21': x_dump_rng_state__mutmut_21, 
    'x_dump_rng_state__mutmut_22': x_dump_rng_state__mutmut_22, 
    'x_dump_rng_state__mutmut_23': x_dump_rng_state__mutmut_23, 
    'x_dump_rng_state__mutmut_24': x_dump_rng_state__mutmut_24, 
    'x_dump_rng_state__mutmut_25': x_dump_rng_state__mutmut_25, 
    'x_dump_rng_state__mutmut_26': x_dump_rng_state__mutmut_26, 
    'x_dump_rng_state__mutmut_27': x_dump_rng_state__mutmut_27, 
    'x_dump_rng_state__mutmut_28': x_dump_rng_state__mutmut_28, 
    'x_dump_rng_state__mutmut_29': x_dump_rng_state__mutmut_29, 
    'x_dump_rng_state__mutmut_30': x_dump_rng_state__mutmut_30, 
    'x_dump_rng_state__mutmut_31': x_dump_rng_state__mutmut_31, 
    'x_dump_rng_state__mutmut_32': x_dump_rng_state__mutmut_32, 
    'x_dump_rng_state__mutmut_33': x_dump_rng_state__mutmut_33, 
    'x_dump_rng_state__mutmut_34': x_dump_rng_state__mutmut_34, 
    'x_dump_rng_state__mutmut_35': x_dump_rng_state__mutmut_35, 
    'x_dump_rng_state__mutmut_36': x_dump_rng_state__mutmut_36, 
    'x_dump_rng_state__mutmut_37': x_dump_rng_state__mutmut_37
}

def dump_rng_state(*args, **kwargs):
    result = _mutmut_trampoline(x_dump_rng_state__mutmut_orig, x_dump_rng_state__mutmut_mutants, args, kwargs)
    return result 

dump_rng_state.__signature__ = _mutmut_signature(x_dump_rng_state__mutmut_orig)
x_dump_rng_state__mutmut_orig.__name__ = 'x_dump_rng_state'


def x_load_rng_state__mutmut_orig(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_1(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_2(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(None)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_3(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "XXpythonXX" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_4(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "PYTHON" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_5(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" not in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_6(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(None)
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_7(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["XXpythonXX"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_8(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["PYTHON"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_9(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None or "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_10(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_11(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "XXnumpyXX" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_12(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "NUMPY" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_13(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" not in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_14(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(None)
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_15(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["XXnumpyXX"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_16(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["NUMPY"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_17(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None or "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_18(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_19(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "XXtorchXX" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_20(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "TORCH" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_21(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" not in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_22(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = None
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_23(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["XXtorchXX"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_24(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["TORCH"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_25(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = None
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_26(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get(None)
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_27(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("XXcpuXX")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_28(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("CPU")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_29(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_30(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(None)
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_31(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(None, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_32(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=None))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_33(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_34(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, ))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_35(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = None
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_36(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(None, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_37(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, None, None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_38(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr("cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_39(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_40(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", )
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_41(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "XXcudaXX", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_42(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "CUDA", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_43(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available() or "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_44(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None)) or cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_45(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None or callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_46(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_47(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(None)
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_48(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(None, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_49(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, None, None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_50(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr("is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_51(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_52(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", ))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_53(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "XXis_availableXX", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_54(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "IS_AVAILABLE", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_55(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "XXcudaXX" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_56(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "CUDA" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_57(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" not in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_58(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = None
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_59(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(None, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_60(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=None) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_61(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_62(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, ) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_63(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get(None, [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_64(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", None)
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_65(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get([])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_66(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", )
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_67(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("XXcudaXX", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_68(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("CUDA", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def x_load_rng_state__mutmut_69(state: dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8) for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(None)

x_load_rng_state__mutmut_mutants : ClassVar[MutantDict] = {
'x_load_rng_state__mutmut_1': x_load_rng_state__mutmut_1, 
    'x_load_rng_state__mutmut_2': x_load_rng_state__mutmut_2, 
    'x_load_rng_state__mutmut_3': x_load_rng_state__mutmut_3, 
    'x_load_rng_state__mutmut_4': x_load_rng_state__mutmut_4, 
    'x_load_rng_state__mutmut_5': x_load_rng_state__mutmut_5, 
    'x_load_rng_state__mutmut_6': x_load_rng_state__mutmut_6, 
    'x_load_rng_state__mutmut_7': x_load_rng_state__mutmut_7, 
    'x_load_rng_state__mutmut_8': x_load_rng_state__mutmut_8, 
    'x_load_rng_state__mutmut_9': x_load_rng_state__mutmut_9, 
    'x_load_rng_state__mutmut_10': x_load_rng_state__mutmut_10, 
    'x_load_rng_state__mutmut_11': x_load_rng_state__mutmut_11, 
    'x_load_rng_state__mutmut_12': x_load_rng_state__mutmut_12, 
    'x_load_rng_state__mutmut_13': x_load_rng_state__mutmut_13, 
    'x_load_rng_state__mutmut_14': x_load_rng_state__mutmut_14, 
    'x_load_rng_state__mutmut_15': x_load_rng_state__mutmut_15, 
    'x_load_rng_state__mutmut_16': x_load_rng_state__mutmut_16, 
    'x_load_rng_state__mutmut_17': x_load_rng_state__mutmut_17, 
    'x_load_rng_state__mutmut_18': x_load_rng_state__mutmut_18, 
    'x_load_rng_state__mutmut_19': x_load_rng_state__mutmut_19, 
    'x_load_rng_state__mutmut_20': x_load_rng_state__mutmut_20, 
    'x_load_rng_state__mutmut_21': x_load_rng_state__mutmut_21, 
    'x_load_rng_state__mutmut_22': x_load_rng_state__mutmut_22, 
    'x_load_rng_state__mutmut_23': x_load_rng_state__mutmut_23, 
    'x_load_rng_state__mutmut_24': x_load_rng_state__mutmut_24, 
    'x_load_rng_state__mutmut_25': x_load_rng_state__mutmut_25, 
    'x_load_rng_state__mutmut_26': x_load_rng_state__mutmut_26, 
    'x_load_rng_state__mutmut_27': x_load_rng_state__mutmut_27, 
    'x_load_rng_state__mutmut_28': x_load_rng_state__mutmut_28, 
    'x_load_rng_state__mutmut_29': x_load_rng_state__mutmut_29, 
    'x_load_rng_state__mutmut_30': x_load_rng_state__mutmut_30, 
    'x_load_rng_state__mutmut_31': x_load_rng_state__mutmut_31, 
    'x_load_rng_state__mutmut_32': x_load_rng_state__mutmut_32, 
    'x_load_rng_state__mutmut_33': x_load_rng_state__mutmut_33, 
    'x_load_rng_state__mutmut_34': x_load_rng_state__mutmut_34, 
    'x_load_rng_state__mutmut_35': x_load_rng_state__mutmut_35, 
    'x_load_rng_state__mutmut_36': x_load_rng_state__mutmut_36, 
    'x_load_rng_state__mutmut_37': x_load_rng_state__mutmut_37, 
    'x_load_rng_state__mutmut_38': x_load_rng_state__mutmut_38, 
    'x_load_rng_state__mutmut_39': x_load_rng_state__mutmut_39, 
    'x_load_rng_state__mutmut_40': x_load_rng_state__mutmut_40, 
    'x_load_rng_state__mutmut_41': x_load_rng_state__mutmut_41, 
    'x_load_rng_state__mutmut_42': x_load_rng_state__mutmut_42, 
    'x_load_rng_state__mutmut_43': x_load_rng_state__mutmut_43, 
    'x_load_rng_state__mutmut_44': x_load_rng_state__mutmut_44, 
    'x_load_rng_state__mutmut_45': x_load_rng_state__mutmut_45, 
    'x_load_rng_state__mutmut_46': x_load_rng_state__mutmut_46, 
    'x_load_rng_state__mutmut_47': x_load_rng_state__mutmut_47, 
    'x_load_rng_state__mutmut_48': x_load_rng_state__mutmut_48, 
    'x_load_rng_state__mutmut_49': x_load_rng_state__mutmut_49, 
    'x_load_rng_state__mutmut_50': x_load_rng_state__mutmut_50, 
    'x_load_rng_state__mutmut_51': x_load_rng_state__mutmut_51, 
    'x_load_rng_state__mutmut_52': x_load_rng_state__mutmut_52, 
    'x_load_rng_state__mutmut_53': x_load_rng_state__mutmut_53, 
    'x_load_rng_state__mutmut_54': x_load_rng_state__mutmut_54, 
    'x_load_rng_state__mutmut_55': x_load_rng_state__mutmut_55, 
    'x_load_rng_state__mutmut_56': x_load_rng_state__mutmut_56, 
    'x_load_rng_state__mutmut_57': x_load_rng_state__mutmut_57, 
    'x_load_rng_state__mutmut_58': x_load_rng_state__mutmut_58, 
    'x_load_rng_state__mutmut_59': x_load_rng_state__mutmut_59, 
    'x_load_rng_state__mutmut_60': x_load_rng_state__mutmut_60, 
    'x_load_rng_state__mutmut_61': x_load_rng_state__mutmut_61, 
    'x_load_rng_state__mutmut_62': x_load_rng_state__mutmut_62, 
    'x_load_rng_state__mutmut_63': x_load_rng_state__mutmut_63, 
    'x_load_rng_state__mutmut_64': x_load_rng_state__mutmut_64, 
    'x_load_rng_state__mutmut_65': x_load_rng_state__mutmut_65, 
    'x_load_rng_state__mutmut_66': x_load_rng_state__mutmut_66, 
    'x_load_rng_state__mutmut_67': x_load_rng_state__mutmut_67, 
    'x_load_rng_state__mutmut_68': x_load_rng_state__mutmut_68, 
    'x_load_rng_state__mutmut_69': x_load_rng_state__mutmut_69
}

def load_rng_state(*args, **kwargs):
    result = _mutmut_trampoline(x_load_rng_state__mutmut_orig, x_load_rng_state__mutmut_mutants, args, kwargs)
    return result 

load_rng_state.__signature__ = _mutmut_signature(x_load_rng_state__mutmut_orig)
x_load_rng_state__mutmut_orig.__name__ = 'x_load_rng_state'


def x_set_seed__mutmut_orig(seed: int) -> None:  # pragma: no cover - passthrough
    """Seed available RNG backends with ``seed``."""

    if _canonical_set_seed is not None:
        _canonical_set_seed(seed)
        return

    _random.seed(seed)
    if _np is not None:
        _np.random.seed(seed)
    if _torch is not None:
        _torch.manual_seed(seed)
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
        ):
            cuda_mod.manual_seed_all(seed)


def x_set_seed__mutmut_1(seed: int) -> None:  # pragma: no cover - passthrough
    """Seed available RNG backends with ``seed``."""

    if _canonical_set_seed is None:
        _canonical_set_seed(seed)
        return

    _random.seed(seed)
    if _np is not None:
        _np.random.seed(seed)
    if _torch is not None:
        _torch.manual_seed(seed)
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
        ):
            cuda_mod.manual_seed_all(seed)


def x_set_seed__mutmut_2(seed: int) -> None:  # pragma: no cover - passthrough
    """Seed available RNG backends with ``seed``."""

    if _canonical_set_seed is not None:
        _canonical_set_seed(None)
        return

    _random.seed(seed)
    if _np is not None:
        _np.random.seed(seed)
    if _torch is not None:
        _torch.manual_seed(seed)
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
        ):
            cuda_mod.manual_seed_all(seed)


def x_set_seed__mutmut_3(seed: int) -> None:  # pragma: no cover - passthrough
    """Seed available RNG backends with ``seed``."""

    if _canonical_set_seed is not None:
        _canonical_set_seed(seed)
        return

    _random.seed(None)
    if _np is not None:
        _np.random.seed(seed)
    if _torch is not None:
        _torch.manual_seed(seed)
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
        ):
            cuda_mod.manual_seed_all(seed)


def x_set_seed__mutmut_4(seed: int) -> None:  # pragma: no cover - passthrough
    """Seed available RNG backends with ``seed``."""

    if _canonical_set_seed is not None:
        _canonical_set_seed(seed)
        return

    _random.seed(seed)
    if _np is None:
        _np.random.seed(seed)
    if _torch is not None:
        _torch.manual_seed(seed)
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
        ):
            cuda_mod.manual_seed_all(seed)


def x_set_seed__mutmut_5(seed: int) -> None:  # pragma: no cover - passthrough
    """Seed available RNG backends with ``seed``."""

    if _canonical_set_seed is not None:
        _canonical_set_seed(seed)
        return

    _random.seed(seed)
    if _np is not None:
        _np.random.seed(None)
    if _torch is not None:
        _torch.manual_seed(seed)
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
        ):
            cuda_mod.manual_seed_all(seed)


def x_set_seed__mutmut_6(seed: int) -> None:  # pragma: no cover - passthrough
    """Seed available RNG backends with ``seed``."""

    if _canonical_set_seed is not None:
        _canonical_set_seed(seed)
        return

    _random.seed(seed)
    if _np is not None:
        _np.random.seed(seed)
    if _torch is None:
        _torch.manual_seed(seed)
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
        ):
            cuda_mod.manual_seed_all(seed)


def x_set_seed__mutmut_7(seed: int) -> None:  # pragma: no cover - passthrough
    """Seed available RNG backends with ``seed``."""

    if _canonical_set_seed is not None:
        _canonical_set_seed(seed)
        return

    _random.seed(seed)
    if _np is not None:
        _np.random.seed(seed)
    if _torch is not None:
        _torch.manual_seed(None)
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
        ):
            cuda_mod.manual_seed_all(seed)


def x_set_seed__mutmut_8(seed: int) -> None:  # pragma: no cover - passthrough
    """Seed available RNG backends with ``seed``."""

    if _canonical_set_seed is not None:
        _canonical_set_seed(seed)
        return

    _random.seed(seed)
    if _np is not None:
        _np.random.seed(seed)
    if _torch is not None:
        _torch.manual_seed(seed)
        cuda_mod = None
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
        ):
            cuda_mod.manual_seed_all(seed)


def x_set_seed__mutmut_9(seed: int) -> None:  # pragma: no cover - passthrough
    """Seed available RNG backends with ``seed``."""

    if _canonical_set_seed is not None:
        _canonical_set_seed(seed)
        return

    _random.seed(seed)
    if _np is not None:
        _np.random.seed(seed)
    if _torch is not None:
        _torch.manual_seed(seed)
        cuda_mod = getattr(None, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
        ):
            cuda_mod.manual_seed_all(seed)


def x_set_seed__mutmut_10(seed: int) -> None:  # pragma: no cover - passthrough
    """Seed available RNG backends with ``seed``."""

    if _canonical_set_seed is not None:
        _canonical_set_seed(seed)
        return

    _random.seed(seed)
    if _np is not None:
        _np.random.seed(seed)
    if _torch is not None:
        _torch.manual_seed(seed)
        cuda_mod = getattr(_torch, None, None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
        ):
            cuda_mod.manual_seed_all(seed)


def x_set_seed__mutmut_11(seed: int) -> None:  # pragma: no cover - passthrough
    """Seed available RNG backends with ``seed``."""

    if _canonical_set_seed is not None:
        _canonical_set_seed(seed)
        return

    _random.seed(seed)
    if _np is not None:
        _np.random.seed(seed)
    if _torch is not None:
        _torch.manual_seed(seed)
        cuda_mod = getattr("cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
        ):
            cuda_mod.manual_seed_all(seed)


def x_set_seed__mutmut_12(seed: int) -> None:  # pragma: no cover - passthrough
    """Seed available RNG backends with ``seed``."""

    if _canonical_set_seed is not None:
        _canonical_set_seed(seed)
        return

    _random.seed(seed)
    if _np is not None:
        _np.random.seed(seed)
    if _torch is not None:
        _torch.manual_seed(seed)
        cuda_mod = getattr(_torch, None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
        ):
            cuda_mod.manual_seed_all(seed)


def x_set_seed__mutmut_13(seed: int) -> None:  # pragma: no cover - passthrough
    """Seed available RNG backends with ``seed``."""

    if _canonical_set_seed is not None:
        _canonical_set_seed(seed)
        return

    _random.seed(seed)
    if _np is not None:
        _np.random.seed(seed)
    if _torch is not None:
        _torch.manual_seed(seed)
        cuda_mod = getattr(_torch, "cuda", )
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
        ):
            cuda_mod.manual_seed_all(seed)


def x_set_seed__mutmut_14(seed: int) -> None:  # pragma: no cover - passthrough
    """Seed available RNG backends with ``seed``."""

    if _canonical_set_seed is not None:
        _canonical_set_seed(seed)
        return

    _random.seed(seed)
    if _np is not None:
        _np.random.seed(seed)
    if _torch is not None:
        _torch.manual_seed(seed)
        cuda_mod = getattr(_torch, "XXcudaXX", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
        ):
            cuda_mod.manual_seed_all(seed)


def x_set_seed__mutmut_15(seed: int) -> None:  # pragma: no cover - passthrough
    """Seed available RNG backends with ``seed``."""

    if _canonical_set_seed is not None:
        _canonical_set_seed(seed)
        return

    _random.seed(seed)
    if _np is not None:
        _np.random.seed(seed)
    if _torch is not None:
        _torch.manual_seed(seed)
        cuda_mod = getattr(_torch, "CUDA", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
        ):
            cuda_mod.manual_seed_all(seed)


def x_set_seed__mutmut_16(seed: int) -> None:  # pragma: no cover - passthrough
    """Seed available RNG backends with ``seed``."""

    if _canonical_set_seed is not None:
        _canonical_set_seed(seed)
        return

    _random.seed(seed)
    if _np is not None:
        _np.random.seed(seed)
    if _torch is not None:
        _torch.manual_seed(seed)
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None)) or cuda_mod.is_available()
        ):
            cuda_mod.manual_seed_all(seed)


def x_set_seed__mutmut_17(seed: int) -> None:  # pragma: no cover - passthrough
    """Seed available RNG backends with ``seed``."""

    if _canonical_set_seed is not None:
        _canonical_set_seed(seed)
        return

    _random.seed(seed)
    if _np is not None:
        _np.random.seed(seed)
    if _torch is not None:
        _torch.manual_seed(seed)
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None or callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
        ):
            cuda_mod.manual_seed_all(seed)


def x_set_seed__mutmut_18(seed: int) -> None:  # pragma: no cover - passthrough
    """Seed available RNG backends with ``seed``."""

    if _canonical_set_seed is not None:
        _canonical_set_seed(seed)
        return

    _random.seed(seed)
    if _np is not None:
        _np.random.seed(seed)
    if _torch is not None:
        _torch.manual_seed(seed)
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
        ):
            cuda_mod.manual_seed_all(seed)


def x_set_seed__mutmut_19(seed: int) -> None:  # pragma: no cover - passthrough
    """Seed available RNG backends with ``seed``."""

    if _canonical_set_seed is not None:
        _canonical_set_seed(seed)
        return

    _random.seed(seed)
    if _np is not None:
        _np.random.seed(seed)
    if _torch is not None:
        _torch.manual_seed(seed)
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(None)
            and cuda_mod.is_available()
        ):
            cuda_mod.manual_seed_all(seed)


def x_set_seed__mutmut_20(seed: int) -> None:  # pragma: no cover - passthrough
    """Seed available RNG backends with ``seed``."""

    if _canonical_set_seed is not None:
        _canonical_set_seed(seed)
        return

    _random.seed(seed)
    if _np is not None:
        _np.random.seed(seed)
    if _torch is not None:
        _torch.manual_seed(seed)
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(None, "is_available", None))
            and cuda_mod.is_available()
        ):
            cuda_mod.manual_seed_all(seed)


def x_set_seed__mutmut_21(seed: int) -> None:  # pragma: no cover - passthrough
    """Seed available RNG backends with ``seed``."""

    if _canonical_set_seed is not None:
        _canonical_set_seed(seed)
        return

    _random.seed(seed)
    if _np is not None:
        _np.random.seed(seed)
    if _torch is not None:
        _torch.manual_seed(seed)
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, None, None))
            and cuda_mod.is_available()
        ):
            cuda_mod.manual_seed_all(seed)


def x_set_seed__mutmut_22(seed: int) -> None:  # pragma: no cover - passthrough
    """Seed available RNG backends with ``seed``."""

    if _canonical_set_seed is not None:
        _canonical_set_seed(seed)
        return

    _random.seed(seed)
    if _np is not None:
        _np.random.seed(seed)
    if _torch is not None:
        _torch.manual_seed(seed)
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr("is_available", None))
            and cuda_mod.is_available()
        ):
            cuda_mod.manual_seed_all(seed)


def x_set_seed__mutmut_23(seed: int) -> None:  # pragma: no cover - passthrough
    """Seed available RNG backends with ``seed``."""

    if _canonical_set_seed is not None:
        _canonical_set_seed(seed)
        return

    _random.seed(seed)
    if _np is not None:
        _np.random.seed(seed)
    if _torch is not None:
        _torch.manual_seed(seed)
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, None))
            and cuda_mod.is_available()
        ):
            cuda_mod.manual_seed_all(seed)


def x_set_seed__mutmut_24(seed: int) -> None:  # pragma: no cover - passthrough
    """Seed available RNG backends with ``seed``."""

    if _canonical_set_seed is not None:
        _canonical_set_seed(seed)
        return

    _random.seed(seed)
    if _np is not None:
        _np.random.seed(seed)
    if _torch is not None:
        _torch.manual_seed(seed)
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", ))
            and cuda_mod.is_available()
        ):
            cuda_mod.manual_seed_all(seed)


def x_set_seed__mutmut_25(seed: int) -> None:  # pragma: no cover - passthrough
    """Seed available RNG backends with ``seed``."""

    if _canonical_set_seed is not None:
        _canonical_set_seed(seed)
        return

    _random.seed(seed)
    if _np is not None:
        _np.random.seed(seed)
    if _torch is not None:
        _torch.manual_seed(seed)
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "XXis_availableXX", None))
            and cuda_mod.is_available()
        ):
            cuda_mod.manual_seed_all(seed)


def x_set_seed__mutmut_26(seed: int) -> None:  # pragma: no cover - passthrough
    """Seed available RNG backends with ``seed``."""

    if _canonical_set_seed is not None:
        _canonical_set_seed(seed)
        return

    _random.seed(seed)
    if _np is not None:
        _np.random.seed(seed)
    if _torch is not None:
        _torch.manual_seed(seed)
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "IS_AVAILABLE", None))
            and cuda_mod.is_available()
        ):
            cuda_mod.manual_seed_all(seed)


def x_set_seed__mutmut_27(seed: int) -> None:  # pragma: no cover - passthrough
    """Seed available RNG backends with ``seed``."""

    if _canonical_set_seed is not None:
        _canonical_set_seed(seed)
        return

    _random.seed(seed)
    if _np is not None:
        _np.random.seed(seed)
    if _torch is not None:
        _torch.manual_seed(seed)
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
        ):
            cuda_mod.manual_seed_all(None)

x_set_seed__mutmut_mutants : ClassVar[MutantDict] = {
'x_set_seed__mutmut_1': x_set_seed__mutmut_1, 
    'x_set_seed__mutmut_2': x_set_seed__mutmut_2, 
    'x_set_seed__mutmut_3': x_set_seed__mutmut_3, 
    'x_set_seed__mutmut_4': x_set_seed__mutmut_4, 
    'x_set_seed__mutmut_5': x_set_seed__mutmut_5, 
    'x_set_seed__mutmut_6': x_set_seed__mutmut_6, 
    'x_set_seed__mutmut_7': x_set_seed__mutmut_7, 
    'x_set_seed__mutmut_8': x_set_seed__mutmut_8, 
    'x_set_seed__mutmut_9': x_set_seed__mutmut_9, 
    'x_set_seed__mutmut_10': x_set_seed__mutmut_10, 
    'x_set_seed__mutmut_11': x_set_seed__mutmut_11, 
    'x_set_seed__mutmut_12': x_set_seed__mutmut_12, 
    'x_set_seed__mutmut_13': x_set_seed__mutmut_13, 
    'x_set_seed__mutmut_14': x_set_seed__mutmut_14, 
    'x_set_seed__mutmut_15': x_set_seed__mutmut_15, 
    'x_set_seed__mutmut_16': x_set_seed__mutmut_16, 
    'x_set_seed__mutmut_17': x_set_seed__mutmut_17, 
    'x_set_seed__mutmut_18': x_set_seed__mutmut_18, 
    'x_set_seed__mutmut_19': x_set_seed__mutmut_19, 
    'x_set_seed__mutmut_20': x_set_seed__mutmut_20, 
    'x_set_seed__mutmut_21': x_set_seed__mutmut_21, 
    'x_set_seed__mutmut_22': x_set_seed__mutmut_22, 
    'x_set_seed__mutmut_23': x_set_seed__mutmut_23, 
    'x_set_seed__mutmut_24': x_set_seed__mutmut_24, 
    'x_set_seed__mutmut_25': x_set_seed__mutmut_25, 
    'x_set_seed__mutmut_26': x_set_seed__mutmut_26, 
    'x_set_seed__mutmut_27': x_set_seed__mutmut_27
}

def set_seed(*args, **kwargs):
    result = _mutmut_trampoline(x_set_seed__mutmut_orig, x_set_seed__mutmut_mutants, args, kwargs)
    return result 

set_seed.__signature__ = _mutmut_signature(x_set_seed__mutmut_orig)
x_set_seed__mutmut_orig.__name__ = 'x_set_seed'


__all__ = [
    "CheckpointManager",
    "save_ckpt",
    "verify_ckpt_integrity",
    "dump_rng_state",
    "load_rng_state",
    "set_seed",
]
