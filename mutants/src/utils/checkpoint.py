"""
Legacy checkpoint helpers (compat shim).

This module remains for backward-compatibility only. Prefer:
  - codex_ml.utils.checkpoint_core
  - codex_ml.utils.checkpointing (CheckpointManager)
"""

from __future__ import annotations

import inspect
import logging
logger = logging.getLogger(__name__)
import os
import random as _random
import tempfile
import warnings as _warnings
from collections.abc import Mapping
from contextlib import suppress
from pathlib import Path
from typing import Any, Callable

try:  # pragma: no cover - optional dependency
    import torch as _torch  # type: ignore[import-not-found]
except Exception:  # pragma: no cover - torch unavailable
    _torch = None  # type: ignore[assignment]

try:  # pragma: no cover - optional dependency
    import numpy as _np  # type: ignore[import-not-found]
except Exception:  # pragma: no cover - numpy unavailable
    _np = None  # type: ignore[assignment]

_warnings.warn(
    "src.utils.checkpoint is legacy; use codex_ml.utils.checkpointing or "
    "codex_ml.utils.checkpoint_core for new code.",
    DeprecationWarning,
    stacklevel=2,
)

LOGGER = logging.getLogger(__name__)

_canonical_load_checkpoint: Callable[..., Any] | None = None
_canonical_save_checkpoint: Callable[..., Any] | None = None
_capture_rng_state: Callable[[], dict[str, Any]] | None = None
_restore_rng_state: Callable[[Mapping[str, Any]], None] | None = None

try:  # pragma: no cover - optional dependency
    import torch as _torch  # type: ignore
except Exception:  # pragma: no cover - tolerate missing torch
    _torch = None  # type: ignore[assignment]

try:  # pragma: no cover - optional dependency
    import numpy as _np  # type: ignore
except Exception:  # pragma: no cover - tolerate missing numpy
    _np = None  # type: ignore[assignment]

# If a local legacy implementation exists in the repository, import it.
# Otherwise provide minimal stubs or re-export from canonical APIs.
try:  # pragma: no cover - legacy path
    from src.training.checkpoint_manager import (
        CheckpointManager,  # type: ignore # noqa: F401
    )
except Exception:  # pragma: no cover - fallback to canonical
    from codex_ml.utils.checkpointing import (
        CheckpointManager,  # type: ignore # noqa: F401
    )

try:  # pragma: no cover - prefer canonical helpers
    from codex_ml.utils.checkpoint_core import (
        capture_rng_state as _capture_rng_state,  # type: ignore
    )
    from codex_ml.utils.checkpoint_core import (
        load_checkpoint as _canonical_load_checkpoint,  # type: ignore
    )
    from codex_ml.utils.checkpoint_core import (
        restore_rng_state as _restore_rng_state,  # type: ignore
    )
    from codex_ml.utils.checkpoint_core import (
        save_checkpoint as _canonical_save_checkpoint,
    )
except Exception as exc:  # pragma: no cover - canonical helpers unavailable
    LOGGER.debug("Canonical checkpoint helpers unavailable: %s", exc)
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


def x__ensure_torch_available__mutmut_orig() -> None:
    if _torch is None:  # pragma: no cover - defensive
        raise RuntimeError("torch is required to use src.utils.checkpoint")


def x__ensure_torch_available__mutmut_1() -> None:
    if _torch is not None:  # pragma: no cover - defensive
        raise RuntimeError("torch is required to use src.utils.checkpoint")


def x__ensure_torch_available__mutmut_2() -> None:
    if _torch is None:  # pragma: no cover - defensive
        raise RuntimeError(None)


def x__ensure_torch_available__mutmut_3() -> None:
    if _torch is None:  # pragma: no cover - defensive
        raise RuntimeError("XXtorch is required to use src.utils.checkpointXX")


def x__ensure_torch_available__mutmut_4() -> None:
    if _torch is None:  # pragma: no cover - defensive
        raise RuntimeError("TORCH IS REQUIRED TO USE SRC.UTILS.CHECKPOINT")

x__ensure_torch_available__mutmut_mutants : ClassVar[MutantDict] = {
'x__ensure_torch_available__mutmut_1': x__ensure_torch_available__mutmut_1, 
    'x__ensure_torch_available__mutmut_2': x__ensure_torch_available__mutmut_2, 
    'x__ensure_torch_available__mutmut_3': x__ensure_torch_available__mutmut_3, 
    'x__ensure_torch_available__mutmut_4': x__ensure_torch_available__mutmut_4
}

def _ensure_torch_available(*args, **kwargs):
    result = _mutmut_trampoline(x__ensure_torch_available__mutmut_orig, x__ensure_torch_available__mutmut_mutants, args, kwargs)
    return result 

_ensure_torch_available.__signature__ = _mutmut_signature(x__ensure_torch_available__mutmut_orig)
x__ensure_torch_available__mutmut_orig.__name__ = 'x__ensure_torch_available'


def x__torch_supports_weights_only__mutmut_orig() -> bool:
    if _torch is None:
        return False
    try:
        load_fn = getattr(_torch, "load", None)
        if load_fn is None:
            return False
        signature = inspect.signature(load_fn)
    except (TypeError, ValueError):  # pragma: no cover - torch may bypass inspect
        return False
    return "weights_only" in signature.parameters


def x__torch_supports_weights_only__mutmut_1() -> bool:
    if _torch is not None:
        return False
    try:
        load_fn = getattr(_torch, "load", None)
        if load_fn is None:
            return False
        signature = inspect.signature(load_fn)
    except (TypeError, ValueError):  # pragma: no cover - torch may bypass inspect
        return False
    return "weights_only" in signature.parameters


def x__torch_supports_weights_only__mutmut_2() -> bool:
    if _torch is None:
        return True
    try:
        load_fn = getattr(_torch, "load", None)
        if load_fn is None:
            return False
        signature = inspect.signature(load_fn)
    except (TypeError, ValueError):  # pragma: no cover - torch may bypass inspect
        return False
    return "weights_only" in signature.parameters


def x__torch_supports_weights_only__mutmut_3() -> bool:
    if _torch is None:
        return False
    try:
        load_fn = None
        if load_fn is None:
            return False
        signature = inspect.signature(load_fn)
    except (TypeError, ValueError):  # pragma: no cover - torch may bypass inspect
        return False
    return "weights_only" in signature.parameters


def x__torch_supports_weights_only__mutmut_4() -> bool:
    if _torch is None:
        return False
    try:
        load_fn = getattr(None, "load", None)
        if load_fn is None:
            return False
        signature = inspect.signature(load_fn)
    except (TypeError, ValueError):  # pragma: no cover - torch may bypass inspect
        return False
    return "weights_only" in signature.parameters


def x__torch_supports_weights_only__mutmut_5() -> bool:
    if _torch is None:
        return False
    try:
        load_fn = getattr(_torch, None, None)
        if load_fn is None:
            return False
        signature = inspect.signature(load_fn)
    except (TypeError, ValueError):  # pragma: no cover - torch may bypass inspect
        return False
    return "weights_only" in signature.parameters


def x__torch_supports_weights_only__mutmut_6() -> bool:
    if _torch is None:
        return False
    try:
        load_fn = getattr("load", None)
        if load_fn is None:
            return False
        signature = inspect.signature(load_fn)
    except (TypeError, ValueError):  # pragma: no cover - torch may bypass inspect
        return False
    return "weights_only" in signature.parameters


def x__torch_supports_weights_only__mutmut_7() -> bool:
    if _torch is None:
        return False
    try:
        load_fn = getattr(_torch, None)
        if load_fn is None:
            return False
        signature = inspect.signature(load_fn)
    except (TypeError, ValueError):  # pragma: no cover - torch may bypass inspect
        return False
    return "weights_only" in signature.parameters


def x__torch_supports_weights_only__mutmut_8() -> bool:
    if _torch is None:
        return False
    try:
        load_fn = getattr(_torch, "load", )
        if load_fn is None:
            return False
        signature = inspect.signature(load_fn)
    except (TypeError, ValueError):  # pragma: no cover - torch may bypass inspect
        return False
    return "weights_only" in signature.parameters


def x__torch_supports_weights_only__mutmut_9() -> bool:
    if _torch is None:
        return False
    try:
        load_fn = getattr(_torch, "XXloadXX", None)
        if load_fn is None:
            return False
        signature = inspect.signature(load_fn)
    except (TypeError, ValueError):  # pragma: no cover - torch may bypass inspect
        return False
    return "weights_only" in signature.parameters


def x__torch_supports_weights_only__mutmut_10() -> bool:
    if _torch is None:
        return False
    try:
        load_fn = getattr(_torch, "LOAD", None)
        if load_fn is None:
            return False
        signature = inspect.signature(load_fn)
    except (TypeError, ValueError):  # pragma: no cover - torch may bypass inspect
        return False
    return "weights_only" in signature.parameters


def x__torch_supports_weights_only__mutmut_11() -> bool:
    if _torch is None:
        return False
    try:
        load_fn = getattr(_torch, "load", None)
        if load_fn is not None:
            return False
        signature = inspect.signature(load_fn)
    except (TypeError, ValueError):  # pragma: no cover - torch may bypass inspect
        return False
    return "weights_only" in signature.parameters


def x__torch_supports_weights_only__mutmut_12() -> bool:
    if _torch is None:
        return False
    try:
        load_fn = getattr(_torch, "load", None)
        if load_fn is None:
            return True
        signature = inspect.signature(load_fn)
    except (TypeError, ValueError):  # pragma: no cover - torch may bypass inspect
        return False
    return "weights_only" in signature.parameters


def x__torch_supports_weights_only__mutmut_13() -> bool:
    if _torch is None:
        return False
    try:
        load_fn = getattr(_torch, "load", None)
        if load_fn is None:
            return False
        signature = None
    except (TypeError, ValueError):  # pragma: no cover - torch may bypass inspect
        return False
    return "weights_only" in signature.parameters


def x__torch_supports_weights_only__mutmut_14() -> bool:
    if _torch is None:
        return False
    try:
        load_fn = getattr(_torch, "load", None)
        if load_fn is None:
            return False
        signature = inspect.signature(None)
    except (TypeError, ValueError):  # pragma: no cover - torch may bypass inspect
        return False
    return "weights_only" in signature.parameters


def x__torch_supports_weights_only__mutmut_15() -> bool:
    if _torch is None:
        return False
    try:
        load_fn = getattr(_torch, "load", None)
        if load_fn is None:
            return False
        signature = inspect.signature(load_fn)
    except (TypeError, ValueError):  # pragma: no cover - torch may bypass inspect
        return True
    return "weights_only" in signature.parameters


def x__torch_supports_weights_only__mutmut_16() -> bool:
    if _torch is None:
        return False
    try:
        load_fn = getattr(_torch, "load", None)
        if load_fn is None:
            return False
        signature = inspect.signature(load_fn)
    except (TypeError, ValueError):  # pragma: no cover - torch may bypass inspect
        return False
    return "XXweights_onlyXX" in signature.parameters


def x__torch_supports_weights_only__mutmut_17() -> bool:
    if _torch is None:
        return False
    try:
        load_fn = getattr(_torch, "load", None)
        if load_fn is None:
            return False
        signature = inspect.signature(load_fn)
    except (TypeError, ValueError):  # pragma: no cover - torch may bypass inspect
        return False
    return "WEIGHTS_ONLY" in signature.parameters


def x__torch_supports_weights_only__mutmut_18() -> bool:
    if _torch is None:
        return False
    try:
        load_fn = getattr(_torch, "load", None)
        if load_fn is None:
            return False
        signature = inspect.signature(load_fn)
    except (TypeError, ValueError):  # pragma: no cover - torch may bypass inspect
        return False
    return "weights_only" not in signature.parameters

x__torch_supports_weights_only__mutmut_mutants : ClassVar[MutantDict] = {
'x__torch_supports_weights_only__mutmut_1': x__torch_supports_weights_only__mutmut_1, 
    'x__torch_supports_weights_only__mutmut_2': x__torch_supports_weights_only__mutmut_2, 
    'x__torch_supports_weights_only__mutmut_3': x__torch_supports_weights_only__mutmut_3, 
    'x__torch_supports_weights_only__mutmut_4': x__torch_supports_weights_only__mutmut_4, 
    'x__torch_supports_weights_only__mutmut_5': x__torch_supports_weights_only__mutmut_5, 
    'x__torch_supports_weights_only__mutmut_6': x__torch_supports_weights_only__mutmut_6, 
    'x__torch_supports_weights_only__mutmut_7': x__torch_supports_weights_only__mutmut_7, 
    'x__torch_supports_weights_only__mutmut_8': x__torch_supports_weights_only__mutmut_8, 
    'x__torch_supports_weights_only__mutmut_9': x__torch_supports_weights_only__mutmut_9, 
    'x__torch_supports_weights_only__mutmut_10': x__torch_supports_weights_only__mutmut_10, 
    'x__torch_supports_weights_only__mutmut_11': x__torch_supports_weights_only__mutmut_11, 
    'x__torch_supports_weights_only__mutmut_12': x__torch_supports_weights_only__mutmut_12, 
    'x__torch_supports_weights_only__mutmut_13': x__torch_supports_weights_only__mutmut_13, 
    'x__torch_supports_weights_only__mutmut_14': x__torch_supports_weights_only__mutmut_14, 
    'x__torch_supports_weights_only__mutmut_15': x__torch_supports_weights_only__mutmut_15, 
    'x__torch_supports_weights_only__mutmut_16': x__torch_supports_weights_only__mutmut_16, 
    'x__torch_supports_weights_only__mutmut_17': x__torch_supports_weights_only__mutmut_17, 
    'x__torch_supports_weights_only__mutmut_18': x__torch_supports_weights_only__mutmut_18
}

def _torch_supports_weights_only(*args, **kwargs):
    result = _mutmut_trampoline(x__torch_supports_weights_only__mutmut_orig, x__torch_supports_weights_only__mutmut_mutants, args, kwargs)
    return result 

_torch_supports_weights_only.__signature__ = _mutmut_signature(x__torch_supports_weights_only__mutmut_orig)
x__torch_supports_weights_only__mutmut_orig.__name__ = 'x__torch_supports_weights_only'


_TORCH_SUPPORTS_WEIGHTS_ONLY = _torch_supports_weights_only()


def x__torch_rng_get_state__mutmut_orig() -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(_torch, "random", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(_torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_1() -> Any:
    if _torch is not None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(_torch, "random", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(_torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_2() -> Any:
    if _torch is None:
        raise RuntimeError(None)
    random_mod = getattr(_torch, "random", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(_torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_3() -> Any:
    if _torch is None:
        raise RuntimeError("XXtorch is required to capture RNG stateXX")
    random_mod = getattr(_torch, "random", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(_torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_4() -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to capture rng state")
    random_mod = getattr(_torch, "random", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(_torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_5() -> Any:
    if _torch is None:
        raise RuntimeError("TORCH IS REQUIRED TO CAPTURE RNG STATE")
    random_mod = getattr(_torch, "random", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(_torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_6() -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = None
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(_torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_7() -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(None, "random", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(_torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_8() -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(_torch, None, None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(_torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_9() -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr("random", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(_torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_10() -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(_torch, None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(_torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_11() -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(_torch, "random", )
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(_torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_12() -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(_torch, "XXrandomXX", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(_torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_13() -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(_torch, "RANDOM", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(_torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_14() -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(_torch, "random", None)
    getter = None
    if callable(getter):
        return getter()
    legacy_getter = getattr(_torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_15() -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(_torch, "random", None)
    getter = getattr(None, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(_torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_16() -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(_torch, "random", None)
    getter = getattr(random_mod, None, None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(_torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_17() -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(_torch, "random", None)
    getter = getattr("get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(_torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_18() -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(_torch, "random", None)
    getter = getattr(random_mod, None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(_torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_19() -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(_torch, "random", None)
    getter = getattr(random_mod, "get_rng_state", ) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(_torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_20() -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(_torch, "random", None)
    getter = getattr(random_mod, "XXget_rng_stateXX", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(_torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_21() -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(_torch, "random", None)
    getter = getattr(random_mod, "GET_RNG_STATE", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(_torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_22() -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(_torch, "random", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(_torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_23() -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(_torch, "random", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(None):
        return getter()
    legacy_getter = getattr(_torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_24() -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(_torch, "random", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = None
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_25() -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(_torch, "random", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(None, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_26() -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(_torch, "random", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(_torch, None, None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_27() -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(_torch, "random", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr("get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_28() -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(_torch, "random", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(_torch, None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_29() -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(_torch, "random", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(_torch, "get_rng_state", )
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_30() -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(_torch, "random", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(_torch, "XXget_rng_stateXX", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_31() -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(_torch, "random", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(_torch, "GET_RNG_STATE", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_32() -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(_torch, "random", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(_torch, "get_rng_state", None)
    if callable(None):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_get_state__mutmut_33() -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(_torch, "random", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(_torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError(None)


def x__torch_rng_get_state__mutmut_34() -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(_torch, "random", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(_torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("XXCurrent torch build lacks RNG state APIsXX")


def x__torch_rng_get_state__mutmut_35() -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(_torch, "random", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(_torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("current torch build lacks rng state apis")


def x__torch_rng_get_state__mutmut_36() -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(_torch, "random", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(_torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("CURRENT TORCH BUILD LACKS RNG STATE APIS")

x__torch_rng_get_state__mutmut_mutants : ClassVar[MutantDict] = {
'x__torch_rng_get_state__mutmut_1': x__torch_rng_get_state__mutmut_1, 
    'x__torch_rng_get_state__mutmut_2': x__torch_rng_get_state__mutmut_2, 
    'x__torch_rng_get_state__mutmut_3': x__torch_rng_get_state__mutmut_3, 
    'x__torch_rng_get_state__mutmut_4': x__torch_rng_get_state__mutmut_4, 
    'x__torch_rng_get_state__mutmut_5': x__torch_rng_get_state__mutmut_5, 
    'x__torch_rng_get_state__mutmut_6': x__torch_rng_get_state__mutmut_6, 
    'x__torch_rng_get_state__mutmut_7': x__torch_rng_get_state__mutmut_7, 
    'x__torch_rng_get_state__mutmut_8': x__torch_rng_get_state__mutmut_8, 
    'x__torch_rng_get_state__mutmut_9': x__torch_rng_get_state__mutmut_9, 
    'x__torch_rng_get_state__mutmut_10': x__torch_rng_get_state__mutmut_10, 
    'x__torch_rng_get_state__mutmut_11': x__torch_rng_get_state__mutmut_11, 
    'x__torch_rng_get_state__mutmut_12': x__torch_rng_get_state__mutmut_12, 
    'x__torch_rng_get_state__mutmut_13': x__torch_rng_get_state__mutmut_13, 
    'x__torch_rng_get_state__mutmut_14': x__torch_rng_get_state__mutmut_14, 
    'x__torch_rng_get_state__mutmut_15': x__torch_rng_get_state__mutmut_15, 
    'x__torch_rng_get_state__mutmut_16': x__torch_rng_get_state__mutmut_16, 
    'x__torch_rng_get_state__mutmut_17': x__torch_rng_get_state__mutmut_17, 
    'x__torch_rng_get_state__mutmut_18': x__torch_rng_get_state__mutmut_18, 
    'x__torch_rng_get_state__mutmut_19': x__torch_rng_get_state__mutmut_19, 
    'x__torch_rng_get_state__mutmut_20': x__torch_rng_get_state__mutmut_20, 
    'x__torch_rng_get_state__mutmut_21': x__torch_rng_get_state__mutmut_21, 
    'x__torch_rng_get_state__mutmut_22': x__torch_rng_get_state__mutmut_22, 
    'x__torch_rng_get_state__mutmut_23': x__torch_rng_get_state__mutmut_23, 
    'x__torch_rng_get_state__mutmut_24': x__torch_rng_get_state__mutmut_24, 
    'x__torch_rng_get_state__mutmut_25': x__torch_rng_get_state__mutmut_25, 
    'x__torch_rng_get_state__mutmut_26': x__torch_rng_get_state__mutmut_26, 
    'x__torch_rng_get_state__mutmut_27': x__torch_rng_get_state__mutmut_27, 
    'x__torch_rng_get_state__mutmut_28': x__torch_rng_get_state__mutmut_28, 
    'x__torch_rng_get_state__mutmut_29': x__torch_rng_get_state__mutmut_29, 
    'x__torch_rng_get_state__mutmut_30': x__torch_rng_get_state__mutmut_30, 
    'x__torch_rng_get_state__mutmut_31': x__torch_rng_get_state__mutmut_31, 
    'x__torch_rng_get_state__mutmut_32': x__torch_rng_get_state__mutmut_32, 
    'x__torch_rng_get_state__mutmut_33': x__torch_rng_get_state__mutmut_33, 
    'x__torch_rng_get_state__mutmut_34': x__torch_rng_get_state__mutmut_34, 
    'x__torch_rng_get_state__mutmut_35': x__torch_rng_get_state__mutmut_35, 
    'x__torch_rng_get_state__mutmut_36': x__torch_rng_get_state__mutmut_36
}

def _torch_rng_get_state(*args, **kwargs):
    result = _mutmut_trampoline(x__torch_rng_get_state__mutmut_orig, x__torch_rng_get_state__mutmut_mutants, args, kwargs)
    return result 

_torch_rng_get_state.__signature__ = _mutmut_signature(x__torch_rng_get_state__mutmut_orig)
x__torch_rng_get_state__mutmut_orig.__name__ = 'x__torch_rng_get_state'


def x__torch_rng_set_state__mutmut_orig(state: Any) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(_torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(_torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_1(state: Any) -> None:
    if _torch is not None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(_torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(_torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_2(state: Any) -> None:
    if _torch is None:
        raise RuntimeError(None)
    random_mod = getattr(_torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(_torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_3(state: Any) -> None:
    if _torch is None:
        raise RuntimeError("XXtorch is required to restore RNG stateXX")
    random_mod = getattr(_torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(_torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_4(state: Any) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore rng state")
    random_mod = getattr(_torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(_torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_5(state: Any) -> None:
    if _torch is None:
        raise RuntimeError("TORCH IS REQUIRED TO RESTORE RNG STATE")
    random_mod = getattr(_torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(_torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_6(state: Any) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = None
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(_torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_7(state: Any) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(None, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(_torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_8(state: Any) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(_torch, None, None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(_torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_9(state: Any) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr("random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(_torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_10(state: Any) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(_torch, None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(_torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_11(state: Any) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(_torch, "random", )
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(_torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_12(state: Any) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(_torch, "XXrandomXX", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(_torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_13(state: Any) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(_torch, "RANDOM", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(_torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_14(state: Any) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(_torch, "random", None)
    setter = None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(_torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_15(state: Any) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(_torch, "random", None)
    setter = getattr(None, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(_torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_16(state: Any) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(_torch, "random", None)
    setter = getattr(random_mod, None, None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(_torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_17(state: Any) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(_torch, "random", None)
    setter = getattr("set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(_torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_18(state: Any) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(_torch, "random", None)
    setter = getattr(random_mod, None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(_torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_19(state: Any) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(_torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", ) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(_torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_20(state: Any) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(_torch, "random", None)
    setter = getattr(random_mod, "XXset_rng_stateXX", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(_torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_21(state: Any) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(_torch, "random", None)
    setter = getattr(random_mod, "SET_RNG_STATE", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(_torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_22(state: Any) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(_torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(_torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_23(state: Any) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(_torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(None):
        setter(state)
        return
    legacy_setter = getattr(_torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_24(state: Any) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(_torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(None)
        return
    legacy_setter = getattr(_torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_25(state: Any) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(_torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = None
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_26(state: Any) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(_torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(None, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_27(state: Any) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(_torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(_torch, None, None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_28(state: Any) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(_torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr("set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_29(state: Any) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(_torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(_torch, None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_30(state: Any) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(_torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(_torch, "set_rng_state", )
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_31(state: Any) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(_torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(_torch, "XXset_rng_stateXX", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_32(state: Any) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(_torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(_torch, "SET_RNG_STATE", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_33(state: Any) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(_torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(_torch, "set_rng_state", None)
    if callable(None):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_34(state: Any) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(_torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(_torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(None)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def x__torch_rng_set_state__mutmut_35(state: Any) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(_torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(_torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError(None)


def x__torch_rng_set_state__mutmut_36(state: Any) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(_torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(_torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("XXCurrent torch build lacks RNG state APIsXX")


def x__torch_rng_set_state__mutmut_37(state: Any) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(_torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(_torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("current torch build lacks rng state apis")


def x__torch_rng_set_state__mutmut_38(state: Any) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(_torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(_torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("CURRENT TORCH BUILD LACKS RNG STATE APIS")

x__torch_rng_set_state__mutmut_mutants : ClassVar[MutantDict] = {
'x__torch_rng_set_state__mutmut_1': x__torch_rng_set_state__mutmut_1, 
    'x__torch_rng_set_state__mutmut_2': x__torch_rng_set_state__mutmut_2, 
    'x__torch_rng_set_state__mutmut_3': x__torch_rng_set_state__mutmut_3, 
    'x__torch_rng_set_state__mutmut_4': x__torch_rng_set_state__mutmut_4, 
    'x__torch_rng_set_state__mutmut_5': x__torch_rng_set_state__mutmut_5, 
    'x__torch_rng_set_state__mutmut_6': x__torch_rng_set_state__mutmut_6, 
    'x__torch_rng_set_state__mutmut_7': x__torch_rng_set_state__mutmut_7, 
    'x__torch_rng_set_state__mutmut_8': x__torch_rng_set_state__mutmut_8, 
    'x__torch_rng_set_state__mutmut_9': x__torch_rng_set_state__mutmut_9, 
    'x__torch_rng_set_state__mutmut_10': x__torch_rng_set_state__mutmut_10, 
    'x__torch_rng_set_state__mutmut_11': x__torch_rng_set_state__mutmut_11, 
    'x__torch_rng_set_state__mutmut_12': x__torch_rng_set_state__mutmut_12, 
    'x__torch_rng_set_state__mutmut_13': x__torch_rng_set_state__mutmut_13, 
    'x__torch_rng_set_state__mutmut_14': x__torch_rng_set_state__mutmut_14, 
    'x__torch_rng_set_state__mutmut_15': x__torch_rng_set_state__mutmut_15, 
    'x__torch_rng_set_state__mutmut_16': x__torch_rng_set_state__mutmut_16, 
    'x__torch_rng_set_state__mutmut_17': x__torch_rng_set_state__mutmut_17, 
    'x__torch_rng_set_state__mutmut_18': x__torch_rng_set_state__mutmut_18, 
    'x__torch_rng_set_state__mutmut_19': x__torch_rng_set_state__mutmut_19, 
    'x__torch_rng_set_state__mutmut_20': x__torch_rng_set_state__mutmut_20, 
    'x__torch_rng_set_state__mutmut_21': x__torch_rng_set_state__mutmut_21, 
    'x__torch_rng_set_state__mutmut_22': x__torch_rng_set_state__mutmut_22, 
    'x__torch_rng_set_state__mutmut_23': x__torch_rng_set_state__mutmut_23, 
    'x__torch_rng_set_state__mutmut_24': x__torch_rng_set_state__mutmut_24, 
    'x__torch_rng_set_state__mutmut_25': x__torch_rng_set_state__mutmut_25, 
    'x__torch_rng_set_state__mutmut_26': x__torch_rng_set_state__mutmut_26, 
    'x__torch_rng_set_state__mutmut_27': x__torch_rng_set_state__mutmut_27, 
    'x__torch_rng_set_state__mutmut_28': x__torch_rng_set_state__mutmut_28, 
    'x__torch_rng_set_state__mutmut_29': x__torch_rng_set_state__mutmut_29, 
    'x__torch_rng_set_state__mutmut_30': x__torch_rng_set_state__mutmut_30, 
    'x__torch_rng_set_state__mutmut_31': x__torch_rng_set_state__mutmut_31, 
    'x__torch_rng_set_state__mutmut_32': x__torch_rng_set_state__mutmut_32, 
    'x__torch_rng_set_state__mutmut_33': x__torch_rng_set_state__mutmut_33, 
    'x__torch_rng_set_state__mutmut_34': x__torch_rng_set_state__mutmut_34, 
    'x__torch_rng_set_state__mutmut_35': x__torch_rng_set_state__mutmut_35, 
    'x__torch_rng_set_state__mutmut_36': x__torch_rng_set_state__mutmut_36, 
    'x__torch_rng_set_state__mutmut_37': x__torch_rng_set_state__mutmut_37, 
    'x__torch_rng_set_state__mutmut_38': x__torch_rng_set_state__mutmut_38
}

def _torch_rng_set_state(*args, **kwargs):
    result = _mutmut_trampoline(x__torch_rng_set_state__mutmut_orig, x__torch_rng_set_state__mutmut_mutants, args, kwargs)
    return result 

_torch_rng_set_state.__signature__ = _mutmut_signature(x__torch_rng_set_state__mutmut_orig)
x__torch_rng_set_state__mutmut_orig.__name__ = 'x__torch_rng_set_state'


def x__legacy_capture_rng_state__mutmut_orig() -> dict[str, Any]:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    if _np is None:
        raise RuntimeError("numpy is required to capture RNG state")

    state: dict[str, Any] = {
        "torch": _torch_rng_get_state().tolist(),
        "python": _random.getstate(),
        "numpy": _np.random.get_state(),
    }
    cuda_mod = getattr(_torch, "cuda", None)
    if cuda_mod is not None and hasattr(cuda_mod, "is_available") and cuda_mod.is_available():
        state["cuda"] = [tensor.tolist() for tensor in cuda_mod.get_rng_state_all()]
    else:
        state["cuda"] = None
    return state


def x__legacy_capture_rng_state__mutmut_1() -> dict[str, Any]:
    if _torch is not None:
        raise RuntimeError("torch is required to capture RNG state")
    if _np is None:
        raise RuntimeError("numpy is required to capture RNG state")

    state: dict[str, Any] = {
        "torch": _torch_rng_get_state().tolist(),
        "python": _random.getstate(),
        "numpy": _np.random.get_state(),
    }
    cuda_mod = getattr(_torch, "cuda", None)
    if cuda_mod is not None and hasattr(cuda_mod, "is_available") and cuda_mod.is_available():
        state["cuda"] = [tensor.tolist() for tensor in cuda_mod.get_rng_state_all()]
    else:
        state["cuda"] = None
    return state


def x__legacy_capture_rng_state__mutmut_2() -> dict[str, Any]:
    if _torch is None:
        raise RuntimeError(None)
    if _np is None:
        raise RuntimeError("numpy is required to capture RNG state")

    state: dict[str, Any] = {
        "torch": _torch_rng_get_state().tolist(),
        "python": _random.getstate(),
        "numpy": _np.random.get_state(),
    }
    cuda_mod = getattr(_torch, "cuda", None)
    if cuda_mod is not None and hasattr(cuda_mod, "is_available") and cuda_mod.is_available():
        state["cuda"] = [tensor.tolist() for tensor in cuda_mod.get_rng_state_all()]
    else:
        state["cuda"] = None
    return state


def x__legacy_capture_rng_state__mutmut_3() -> dict[str, Any]:
    if _torch is None:
        raise RuntimeError("XXtorch is required to capture RNG stateXX")
    if _np is None:
        raise RuntimeError("numpy is required to capture RNG state")

    state: dict[str, Any] = {
        "torch": _torch_rng_get_state().tolist(),
        "python": _random.getstate(),
        "numpy": _np.random.get_state(),
    }
    cuda_mod = getattr(_torch, "cuda", None)
    if cuda_mod is not None and hasattr(cuda_mod, "is_available") and cuda_mod.is_available():
        state["cuda"] = [tensor.tolist() for tensor in cuda_mod.get_rng_state_all()]
    else:
        state["cuda"] = None
    return state


def x__legacy_capture_rng_state__mutmut_4() -> dict[str, Any]:
    if _torch is None:
        raise RuntimeError("torch is required to capture rng state")
    if _np is None:
        raise RuntimeError("numpy is required to capture RNG state")

    state: dict[str, Any] = {
        "torch": _torch_rng_get_state().tolist(),
        "python": _random.getstate(),
        "numpy": _np.random.get_state(),
    }
    cuda_mod = getattr(_torch, "cuda", None)
    if cuda_mod is not None and hasattr(cuda_mod, "is_available") and cuda_mod.is_available():
        state["cuda"] = [tensor.tolist() for tensor in cuda_mod.get_rng_state_all()]
    else:
        state["cuda"] = None
    return state


def x__legacy_capture_rng_state__mutmut_5() -> dict[str, Any]:
    if _torch is None:
        raise RuntimeError("TORCH IS REQUIRED TO CAPTURE RNG STATE")
    if _np is None:
        raise RuntimeError("numpy is required to capture RNG state")

    state: dict[str, Any] = {
        "torch": _torch_rng_get_state().tolist(),
        "python": _random.getstate(),
        "numpy": _np.random.get_state(),
    }
    cuda_mod = getattr(_torch, "cuda", None)
    if cuda_mod is not None and hasattr(cuda_mod, "is_available") and cuda_mod.is_available():
        state["cuda"] = [tensor.tolist() for tensor in cuda_mod.get_rng_state_all()]
    else:
        state["cuda"] = None
    return state


def x__legacy_capture_rng_state__mutmut_6() -> dict[str, Any]:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    if _np is not None:
        raise RuntimeError("numpy is required to capture RNG state")

    state: dict[str, Any] = {
        "torch": _torch_rng_get_state().tolist(),
        "python": _random.getstate(),
        "numpy": _np.random.get_state(),
    }
    cuda_mod = getattr(_torch, "cuda", None)
    if cuda_mod is not None and hasattr(cuda_mod, "is_available") and cuda_mod.is_available():
        state["cuda"] = [tensor.tolist() for tensor in cuda_mod.get_rng_state_all()]
    else:
        state["cuda"] = None
    return state


def x__legacy_capture_rng_state__mutmut_7() -> dict[str, Any]:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    if _np is None:
        raise RuntimeError(None)

    state: dict[str, Any] = {
        "torch": _torch_rng_get_state().tolist(),
        "python": _random.getstate(),
        "numpy": _np.random.get_state(),
    }
    cuda_mod = getattr(_torch, "cuda", None)
    if cuda_mod is not None and hasattr(cuda_mod, "is_available") and cuda_mod.is_available():
        state["cuda"] = [tensor.tolist() for tensor in cuda_mod.get_rng_state_all()]
    else:
        state["cuda"] = None
    return state


def x__legacy_capture_rng_state__mutmut_8() -> dict[str, Any]:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    if _np is None:
        raise RuntimeError("XXnumpy is required to capture RNG stateXX")

    state: dict[str, Any] = {
        "torch": _torch_rng_get_state().tolist(),
        "python": _random.getstate(),
        "numpy": _np.random.get_state(),
    }
    cuda_mod = getattr(_torch, "cuda", None)
    if cuda_mod is not None and hasattr(cuda_mod, "is_available") and cuda_mod.is_available():
        state["cuda"] = [tensor.tolist() for tensor in cuda_mod.get_rng_state_all()]
    else:
        state["cuda"] = None
    return state


def x__legacy_capture_rng_state__mutmut_9() -> dict[str, Any]:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    if _np is None:
        raise RuntimeError("numpy is required to capture rng state")

    state: dict[str, Any] = {
        "torch": _torch_rng_get_state().tolist(),
        "python": _random.getstate(),
        "numpy": _np.random.get_state(),
    }
    cuda_mod = getattr(_torch, "cuda", None)
    if cuda_mod is not None and hasattr(cuda_mod, "is_available") and cuda_mod.is_available():
        state["cuda"] = [tensor.tolist() for tensor in cuda_mod.get_rng_state_all()]
    else:
        state["cuda"] = None
    return state


def x__legacy_capture_rng_state__mutmut_10() -> dict[str, Any]:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    if _np is None:
        raise RuntimeError("NUMPY IS REQUIRED TO CAPTURE RNG STATE")

    state: dict[str, Any] = {
        "torch": _torch_rng_get_state().tolist(),
        "python": _random.getstate(),
        "numpy": _np.random.get_state(),
    }
    cuda_mod = getattr(_torch, "cuda", None)
    if cuda_mod is not None and hasattr(cuda_mod, "is_available") and cuda_mod.is_available():
        state["cuda"] = [tensor.tolist() for tensor in cuda_mod.get_rng_state_all()]
    else:
        state["cuda"] = None
    return state


def x__legacy_capture_rng_state__mutmut_11() -> dict[str, Any]:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    if _np is None:
        raise RuntimeError("numpy is required to capture RNG state")

    state: dict[str, Any] = None
    cuda_mod = getattr(_torch, "cuda", None)
    if cuda_mod is not None and hasattr(cuda_mod, "is_available") and cuda_mod.is_available():
        state["cuda"] = [tensor.tolist() for tensor in cuda_mod.get_rng_state_all()]
    else:
        state["cuda"] = None
    return state


def x__legacy_capture_rng_state__mutmut_12() -> dict[str, Any]:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    if _np is None:
        raise RuntimeError("numpy is required to capture RNG state")

    state: dict[str, Any] = {
        "XXtorchXX": _torch_rng_get_state().tolist(),
        "python": _random.getstate(),
        "numpy": _np.random.get_state(),
    }
    cuda_mod = getattr(_torch, "cuda", None)
    if cuda_mod is not None and hasattr(cuda_mod, "is_available") and cuda_mod.is_available():
        state["cuda"] = [tensor.tolist() for tensor in cuda_mod.get_rng_state_all()]
    else:
        state["cuda"] = None
    return state


def x__legacy_capture_rng_state__mutmut_13() -> dict[str, Any]:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    if _np is None:
        raise RuntimeError("numpy is required to capture RNG state")

    state: dict[str, Any] = {
        "TORCH": _torch_rng_get_state().tolist(),
        "python": _random.getstate(),
        "numpy": _np.random.get_state(),
    }
    cuda_mod = getattr(_torch, "cuda", None)
    if cuda_mod is not None and hasattr(cuda_mod, "is_available") and cuda_mod.is_available():
        state["cuda"] = [tensor.tolist() for tensor in cuda_mod.get_rng_state_all()]
    else:
        state["cuda"] = None
    return state


def x__legacy_capture_rng_state__mutmut_14() -> dict[str, Any]:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    if _np is None:
        raise RuntimeError("numpy is required to capture RNG state")

    state: dict[str, Any] = {
        "torch": _torch_rng_get_state().tolist(),
        "XXpythonXX": _random.getstate(),
        "numpy": _np.random.get_state(),
    }
    cuda_mod = getattr(_torch, "cuda", None)
    if cuda_mod is not None and hasattr(cuda_mod, "is_available") and cuda_mod.is_available():
        state["cuda"] = [tensor.tolist() for tensor in cuda_mod.get_rng_state_all()]
    else:
        state["cuda"] = None
    return state


def x__legacy_capture_rng_state__mutmut_15() -> dict[str, Any]:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    if _np is None:
        raise RuntimeError("numpy is required to capture RNG state")

    state: dict[str, Any] = {
        "torch": _torch_rng_get_state().tolist(),
        "PYTHON": _random.getstate(),
        "numpy": _np.random.get_state(),
    }
    cuda_mod = getattr(_torch, "cuda", None)
    if cuda_mod is not None and hasattr(cuda_mod, "is_available") and cuda_mod.is_available():
        state["cuda"] = [tensor.tolist() for tensor in cuda_mod.get_rng_state_all()]
    else:
        state["cuda"] = None
    return state


def x__legacy_capture_rng_state__mutmut_16() -> dict[str, Any]:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    if _np is None:
        raise RuntimeError("numpy is required to capture RNG state")

    state: dict[str, Any] = {
        "torch": _torch_rng_get_state().tolist(),
        "python": _random.getstate(),
        "XXnumpyXX": _np.random.get_state(),
    }
    cuda_mod = getattr(_torch, "cuda", None)
    if cuda_mod is not None and hasattr(cuda_mod, "is_available") and cuda_mod.is_available():
        state["cuda"] = [tensor.tolist() for tensor in cuda_mod.get_rng_state_all()]
    else:
        state["cuda"] = None
    return state


def x__legacy_capture_rng_state__mutmut_17() -> dict[str, Any]:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    if _np is None:
        raise RuntimeError("numpy is required to capture RNG state")

    state: dict[str, Any] = {
        "torch": _torch_rng_get_state().tolist(),
        "python": _random.getstate(),
        "NUMPY": _np.random.get_state(),
    }
    cuda_mod = getattr(_torch, "cuda", None)
    if cuda_mod is not None and hasattr(cuda_mod, "is_available") and cuda_mod.is_available():
        state["cuda"] = [tensor.tolist() for tensor in cuda_mod.get_rng_state_all()]
    else:
        state["cuda"] = None
    return state


def x__legacy_capture_rng_state__mutmut_18() -> dict[str, Any]:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    if _np is None:
        raise RuntimeError("numpy is required to capture RNG state")

    state: dict[str, Any] = {
        "torch": _torch_rng_get_state().tolist(),
        "python": _random.getstate(),
        "numpy": _np.random.get_state(),
    }
    cuda_mod = None
    if cuda_mod is not None and hasattr(cuda_mod, "is_available") and cuda_mod.is_available():
        state["cuda"] = [tensor.tolist() for tensor in cuda_mod.get_rng_state_all()]
    else:
        state["cuda"] = None
    return state


def x__legacy_capture_rng_state__mutmut_19() -> dict[str, Any]:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    if _np is None:
        raise RuntimeError("numpy is required to capture RNG state")

    state: dict[str, Any] = {
        "torch": _torch_rng_get_state().tolist(),
        "python": _random.getstate(),
        "numpy": _np.random.get_state(),
    }
    cuda_mod = getattr(None, "cuda", None)
    if cuda_mod is not None and hasattr(cuda_mod, "is_available") and cuda_mod.is_available():
        state["cuda"] = [tensor.tolist() for tensor in cuda_mod.get_rng_state_all()]
    else:
        state["cuda"] = None
    return state


def x__legacy_capture_rng_state__mutmut_20() -> dict[str, Any]:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    if _np is None:
        raise RuntimeError("numpy is required to capture RNG state")

    state: dict[str, Any] = {
        "torch": _torch_rng_get_state().tolist(),
        "python": _random.getstate(),
        "numpy": _np.random.get_state(),
    }
    cuda_mod = getattr(_torch, None, None)
    if cuda_mod is not None and hasattr(cuda_mod, "is_available") and cuda_mod.is_available():
        state["cuda"] = [tensor.tolist() for tensor in cuda_mod.get_rng_state_all()]
    else:
        state["cuda"] = None
    return state


def x__legacy_capture_rng_state__mutmut_21() -> dict[str, Any]:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    if _np is None:
        raise RuntimeError("numpy is required to capture RNG state")

    state: dict[str, Any] = {
        "torch": _torch_rng_get_state().tolist(),
        "python": _random.getstate(),
        "numpy": _np.random.get_state(),
    }
    cuda_mod = getattr("cuda", None)
    if cuda_mod is not None and hasattr(cuda_mod, "is_available") and cuda_mod.is_available():
        state["cuda"] = [tensor.tolist() for tensor in cuda_mod.get_rng_state_all()]
    else:
        state["cuda"] = None
    return state


def x__legacy_capture_rng_state__mutmut_22() -> dict[str, Any]:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    if _np is None:
        raise RuntimeError("numpy is required to capture RNG state")

    state: dict[str, Any] = {
        "torch": _torch_rng_get_state().tolist(),
        "python": _random.getstate(),
        "numpy": _np.random.get_state(),
    }
    cuda_mod = getattr(_torch, None)
    if cuda_mod is not None and hasattr(cuda_mod, "is_available") and cuda_mod.is_available():
        state["cuda"] = [tensor.tolist() for tensor in cuda_mod.get_rng_state_all()]
    else:
        state["cuda"] = None
    return state


def x__legacy_capture_rng_state__mutmut_23() -> dict[str, Any]:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    if _np is None:
        raise RuntimeError("numpy is required to capture RNG state")

    state: dict[str, Any] = {
        "torch": _torch_rng_get_state().tolist(),
        "python": _random.getstate(),
        "numpy": _np.random.get_state(),
    }
    cuda_mod = getattr(_torch, "cuda", )
    if cuda_mod is not None and hasattr(cuda_mod, "is_available") and cuda_mod.is_available():
        state["cuda"] = [tensor.tolist() for tensor in cuda_mod.get_rng_state_all()]
    else:
        state["cuda"] = None
    return state


def x__legacy_capture_rng_state__mutmut_24() -> dict[str, Any]:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    if _np is None:
        raise RuntimeError("numpy is required to capture RNG state")

    state: dict[str, Any] = {
        "torch": _torch_rng_get_state().tolist(),
        "python": _random.getstate(),
        "numpy": _np.random.get_state(),
    }
    cuda_mod = getattr(_torch, "XXcudaXX", None)
    if cuda_mod is not None and hasattr(cuda_mod, "is_available") and cuda_mod.is_available():
        state["cuda"] = [tensor.tolist() for tensor in cuda_mod.get_rng_state_all()]
    else:
        state["cuda"] = None
    return state


def x__legacy_capture_rng_state__mutmut_25() -> dict[str, Any]:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    if _np is None:
        raise RuntimeError("numpy is required to capture RNG state")

    state: dict[str, Any] = {
        "torch": _torch_rng_get_state().tolist(),
        "python": _random.getstate(),
        "numpy": _np.random.get_state(),
    }
    cuda_mod = getattr(_torch, "CUDA", None)
    if cuda_mod is not None and hasattr(cuda_mod, "is_available") and cuda_mod.is_available():
        state["cuda"] = [tensor.tolist() for tensor in cuda_mod.get_rng_state_all()]
    else:
        state["cuda"] = None
    return state


def x__legacy_capture_rng_state__mutmut_26() -> dict[str, Any]:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    if _np is None:
        raise RuntimeError("numpy is required to capture RNG state")

    state: dict[str, Any] = {
        "torch": _torch_rng_get_state().tolist(),
        "python": _random.getstate(),
        "numpy": _np.random.get_state(),
    }
    cuda_mod = getattr(_torch, "cuda", None)
    if cuda_mod is not None and hasattr(cuda_mod, "is_available") or cuda_mod.is_available():
        state["cuda"] = [tensor.tolist() for tensor in cuda_mod.get_rng_state_all()]
    else:
        state["cuda"] = None
    return state


def x__legacy_capture_rng_state__mutmut_27() -> dict[str, Any]:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    if _np is None:
        raise RuntimeError("numpy is required to capture RNG state")

    state: dict[str, Any] = {
        "torch": _torch_rng_get_state().tolist(),
        "python": _random.getstate(),
        "numpy": _np.random.get_state(),
    }
    cuda_mod = getattr(_torch, "cuda", None)
    if cuda_mod is not None or hasattr(cuda_mod, "is_available") and cuda_mod.is_available():
        state["cuda"] = [tensor.tolist() for tensor in cuda_mod.get_rng_state_all()]
    else:
        state["cuda"] = None
    return state


def x__legacy_capture_rng_state__mutmut_28() -> dict[str, Any]:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    if _np is None:
        raise RuntimeError("numpy is required to capture RNG state")

    state: dict[str, Any] = {
        "torch": _torch_rng_get_state().tolist(),
        "python": _random.getstate(),
        "numpy": _np.random.get_state(),
    }
    cuda_mod = getattr(_torch, "cuda", None)
    if cuda_mod is None and hasattr(cuda_mod, "is_available") and cuda_mod.is_available():
        state["cuda"] = [tensor.tolist() for tensor in cuda_mod.get_rng_state_all()]
    else:
        state["cuda"] = None
    return state


def x__legacy_capture_rng_state__mutmut_29() -> dict[str, Any]:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    if _np is None:
        raise RuntimeError("numpy is required to capture RNG state")

    state: dict[str, Any] = {
        "torch": _torch_rng_get_state().tolist(),
        "python": _random.getstate(),
        "numpy": _np.random.get_state(),
    }
    cuda_mod = getattr(_torch, "cuda", None)
    if cuda_mod is not None and hasattr(None, "is_available") and cuda_mod.is_available():
        state["cuda"] = [tensor.tolist() for tensor in cuda_mod.get_rng_state_all()]
    else:
        state["cuda"] = None
    return state


def x__legacy_capture_rng_state__mutmut_30() -> dict[str, Any]:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    if _np is None:
        raise RuntimeError("numpy is required to capture RNG state")

    state: dict[str, Any] = {
        "torch": _torch_rng_get_state().tolist(),
        "python": _random.getstate(),
        "numpy": _np.random.get_state(),
    }
    cuda_mod = getattr(_torch, "cuda", None)
    if cuda_mod is not None and hasattr(cuda_mod, None) and cuda_mod.is_available():
        state["cuda"] = [tensor.tolist() for tensor in cuda_mod.get_rng_state_all()]
    else:
        state["cuda"] = None
    return state


def x__legacy_capture_rng_state__mutmut_31() -> dict[str, Any]:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    if _np is None:
        raise RuntimeError("numpy is required to capture RNG state")

    state: dict[str, Any] = {
        "torch": _torch_rng_get_state().tolist(),
        "python": _random.getstate(),
        "numpy": _np.random.get_state(),
    }
    cuda_mod = getattr(_torch, "cuda", None)
    if cuda_mod is not None and hasattr("is_available") and cuda_mod.is_available():
        state["cuda"] = [tensor.tolist() for tensor in cuda_mod.get_rng_state_all()]
    else:
        state["cuda"] = None
    return state


def x__legacy_capture_rng_state__mutmut_32() -> dict[str, Any]:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    if _np is None:
        raise RuntimeError("numpy is required to capture RNG state")

    state: dict[str, Any] = {
        "torch": _torch_rng_get_state().tolist(),
        "python": _random.getstate(),
        "numpy": _np.random.get_state(),
    }
    cuda_mod = getattr(_torch, "cuda", None)
    if cuda_mod is not None and hasattr(cuda_mod, ) and cuda_mod.is_available():
        state["cuda"] = [tensor.tolist() for tensor in cuda_mod.get_rng_state_all()]
    else:
        state["cuda"] = None
    return state


def x__legacy_capture_rng_state__mutmut_33() -> dict[str, Any]:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    if _np is None:
        raise RuntimeError("numpy is required to capture RNG state")

    state: dict[str, Any] = {
        "torch": _torch_rng_get_state().tolist(),
        "python": _random.getstate(),
        "numpy": _np.random.get_state(),
    }
    cuda_mod = getattr(_torch, "cuda", None)
    if cuda_mod is not None and hasattr(cuda_mod, "XXis_availableXX") and cuda_mod.is_available():
        state["cuda"] = [tensor.tolist() for tensor in cuda_mod.get_rng_state_all()]
    else:
        state["cuda"] = None
    return state


def x__legacy_capture_rng_state__mutmut_34() -> dict[str, Any]:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    if _np is None:
        raise RuntimeError("numpy is required to capture RNG state")

    state: dict[str, Any] = {
        "torch": _torch_rng_get_state().tolist(),
        "python": _random.getstate(),
        "numpy": _np.random.get_state(),
    }
    cuda_mod = getattr(_torch, "cuda", None)
    if cuda_mod is not None and hasattr(cuda_mod, "IS_AVAILABLE") and cuda_mod.is_available():
        state["cuda"] = [tensor.tolist() for tensor in cuda_mod.get_rng_state_all()]
    else:
        state["cuda"] = None
    return state


def x__legacy_capture_rng_state__mutmut_35() -> dict[str, Any]:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    if _np is None:
        raise RuntimeError("numpy is required to capture RNG state")

    state: dict[str, Any] = {
        "torch": _torch_rng_get_state().tolist(),
        "python": _random.getstate(),
        "numpy": _np.random.get_state(),
    }
    cuda_mod = getattr(_torch, "cuda", None)
    if cuda_mod is not None and hasattr(cuda_mod, "is_available") and cuda_mod.is_available():
        state["cuda"] = None
    else:
        state["cuda"] = None
    return state


def x__legacy_capture_rng_state__mutmut_36() -> dict[str, Any]:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    if _np is None:
        raise RuntimeError("numpy is required to capture RNG state")

    state: dict[str, Any] = {
        "torch": _torch_rng_get_state().tolist(),
        "python": _random.getstate(),
        "numpy": _np.random.get_state(),
    }
    cuda_mod = getattr(_torch, "cuda", None)
    if cuda_mod is not None and hasattr(cuda_mod, "is_available") and cuda_mod.is_available():
        state["XXcudaXX"] = [tensor.tolist() for tensor in cuda_mod.get_rng_state_all()]
    else:
        state["cuda"] = None
    return state


def x__legacy_capture_rng_state__mutmut_37() -> dict[str, Any]:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    if _np is None:
        raise RuntimeError("numpy is required to capture RNG state")

    state: dict[str, Any] = {
        "torch": _torch_rng_get_state().tolist(),
        "python": _random.getstate(),
        "numpy": _np.random.get_state(),
    }
    cuda_mod = getattr(_torch, "cuda", None)
    if cuda_mod is not None and hasattr(cuda_mod, "is_available") and cuda_mod.is_available():
        state["CUDA"] = [tensor.tolist() for tensor in cuda_mod.get_rng_state_all()]
    else:
        state["cuda"] = None
    return state


def x__legacy_capture_rng_state__mutmut_38() -> dict[str, Any]:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    if _np is None:
        raise RuntimeError("numpy is required to capture RNG state")

    state: dict[str, Any] = {
        "torch": _torch_rng_get_state().tolist(),
        "python": _random.getstate(),
        "numpy": _np.random.get_state(),
    }
    cuda_mod = getattr(_torch, "cuda", None)
    if cuda_mod is not None and hasattr(cuda_mod, "is_available") and cuda_mod.is_available():
        state["cuda"] = [tensor.tolist() for tensor in cuda_mod.get_rng_state_all()]
    else:
        state["cuda"] = ""
    return state


def x__legacy_capture_rng_state__mutmut_39() -> dict[str, Any]:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    if _np is None:
        raise RuntimeError("numpy is required to capture RNG state")

    state: dict[str, Any] = {
        "torch": _torch_rng_get_state().tolist(),
        "python": _random.getstate(),
        "numpy": _np.random.get_state(),
    }
    cuda_mod = getattr(_torch, "cuda", None)
    if cuda_mod is not None and hasattr(cuda_mod, "is_available") and cuda_mod.is_available():
        state["cuda"] = [tensor.tolist() for tensor in cuda_mod.get_rng_state_all()]
    else:
        state["XXcudaXX"] = None
    return state


def x__legacy_capture_rng_state__mutmut_40() -> dict[str, Any]:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    if _np is None:
        raise RuntimeError("numpy is required to capture RNG state")

    state: dict[str, Any] = {
        "torch": _torch_rng_get_state().tolist(),
        "python": _random.getstate(),
        "numpy": _np.random.get_state(),
    }
    cuda_mod = getattr(_torch, "cuda", None)
    if cuda_mod is not None and hasattr(cuda_mod, "is_available") and cuda_mod.is_available():
        state["cuda"] = [tensor.tolist() for tensor in cuda_mod.get_rng_state_all()]
    else:
        state["CUDA"] = None
    return state

x__legacy_capture_rng_state__mutmut_mutants : ClassVar[MutantDict] = {
'x__legacy_capture_rng_state__mutmut_1': x__legacy_capture_rng_state__mutmut_1, 
    'x__legacy_capture_rng_state__mutmut_2': x__legacy_capture_rng_state__mutmut_2, 
    'x__legacy_capture_rng_state__mutmut_3': x__legacy_capture_rng_state__mutmut_3, 
    'x__legacy_capture_rng_state__mutmut_4': x__legacy_capture_rng_state__mutmut_4, 
    'x__legacy_capture_rng_state__mutmut_5': x__legacy_capture_rng_state__mutmut_5, 
    'x__legacy_capture_rng_state__mutmut_6': x__legacy_capture_rng_state__mutmut_6, 
    'x__legacy_capture_rng_state__mutmut_7': x__legacy_capture_rng_state__mutmut_7, 
    'x__legacy_capture_rng_state__mutmut_8': x__legacy_capture_rng_state__mutmut_8, 
    'x__legacy_capture_rng_state__mutmut_9': x__legacy_capture_rng_state__mutmut_9, 
    'x__legacy_capture_rng_state__mutmut_10': x__legacy_capture_rng_state__mutmut_10, 
    'x__legacy_capture_rng_state__mutmut_11': x__legacy_capture_rng_state__mutmut_11, 
    'x__legacy_capture_rng_state__mutmut_12': x__legacy_capture_rng_state__mutmut_12, 
    'x__legacy_capture_rng_state__mutmut_13': x__legacy_capture_rng_state__mutmut_13, 
    'x__legacy_capture_rng_state__mutmut_14': x__legacy_capture_rng_state__mutmut_14, 
    'x__legacy_capture_rng_state__mutmut_15': x__legacy_capture_rng_state__mutmut_15, 
    'x__legacy_capture_rng_state__mutmut_16': x__legacy_capture_rng_state__mutmut_16, 
    'x__legacy_capture_rng_state__mutmut_17': x__legacy_capture_rng_state__mutmut_17, 
    'x__legacy_capture_rng_state__mutmut_18': x__legacy_capture_rng_state__mutmut_18, 
    'x__legacy_capture_rng_state__mutmut_19': x__legacy_capture_rng_state__mutmut_19, 
    'x__legacy_capture_rng_state__mutmut_20': x__legacy_capture_rng_state__mutmut_20, 
    'x__legacy_capture_rng_state__mutmut_21': x__legacy_capture_rng_state__mutmut_21, 
    'x__legacy_capture_rng_state__mutmut_22': x__legacy_capture_rng_state__mutmut_22, 
    'x__legacy_capture_rng_state__mutmut_23': x__legacy_capture_rng_state__mutmut_23, 
    'x__legacy_capture_rng_state__mutmut_24': x__legacy_capture_rng_state__mutmut_24, 
    'x__legacy_capture_rng_state__mutmut_25': x__legacy_capture_rng_state__mutmut_25, 
    'x__legacy_capture_rng_state__mutmut_26': x__legacy_capture_rng_state__mutmut_26, 
    'x__legacy_capture_rng_state__mutmut_27': x__legacy_capture_rng_state__mutmut_27, 
    'x__legacy_capture_rng_state__mutmut_28': x__legacy_capture_rng_state__mutmut_28, 
    'x__legacy_capture_rng_state__mutmut_29': x__legacy_capture_rng_state__mutmut_29, 
    'x__legacy_capture_rng_state__mutmut_30': x__legacy_capture_rng_state__mutmut_30, 
    'x__legacy_capture_rng_state__mutmut_31': x__legacy_capture_rng_state__mutmut_31, 
    'x__legacy_capture_rng_state__mutmut_32': x__legacy_capture_rng_state__mutmut_32, 
    'x__legacy_capture_rng_state__mutmut_33': x__legacy_capture_rng_state__mutmut_33, 
    'x__legacy_capture_rng_state__mutmut_34': x__legacy_capture_rng_state__mutmut_34, 
    'x__legacy_capture_rng_state__mutmut_35': x__legacy_capture_rng_state__mutmut_35, 
    'x__legacy_capture_rng_state__mutmut_36': x__legacy_capture_rng_state__mutmut_36, 
    'x__legacy_capture_rng_state__mutmut_37': x__legacy_capture_rng_state__mutmut_37, 
    'x__legacy_capture_rng_state__mutmut_38': x__legacy_capture_rng_state__mutmut_38, 
    'x__legacy_capture_rng_state__mutmut_39': x__legacy_capture_rng_state__mutmut_39, 
    'x__legacy_capture_rng_state__mutmut_40': x__legacy_capture_rng_state__mutmut_40
}

def _legacy_capture_rng_state(*args, **kwargs):
    result = _mutmut_trampoline(x__legacy_capture_rng_state__mutmut_orig, x__legacy_capture_rng_state__mutmut_mutants, args, kwargs)
    return result 

_legacy_capture_rng_state.__signature__ = _mutmut_signature(x__legacy_capture_rng_state__mutmut_orig)
x__legacy_capture_rng_state__mutmut_orig.__name__ = 'x__legacy_capture_rng_state'


def x__legacy_restore_rng_state__mutmut_orig(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_1(state: Mapping[str, Any]) -> None:
    if _torch is not None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_2(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError(None)

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_3(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("XXtorch is required to restore RNG stateXX")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_4(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore rng state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_5(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("TORCH IS REQUIRED TO RESTORE RNG STATE")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_6(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = None
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_7(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get(None)
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_8(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("XXtorchXX")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_9(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("TORCH")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_10(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is not None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_11(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = None
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_12(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get(None)
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_13(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("XXtorch_cpuXX")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_14(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("TORCH_CPU")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_15(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_16(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(None):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_17(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = None
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_18(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=None)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_19(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = None
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_20(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(None, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_21(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=None)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_22(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_23(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, )
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_24(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(None)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_25(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None or "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_26(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_27(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "XXnumpyXX" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_28(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "NUMPY" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_29(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" not in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_30(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(None):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_31(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(None)  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_32(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["XXnumpyXX"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_33(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["NUMPY"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_34(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "XXpythonXX" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_35(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "PYTHON" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_36(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" not in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_37(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(None):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_38(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(None)  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_39(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["XXpythonXX"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_40(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["PYTHON"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_41(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = None
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_42(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(None, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_43(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, None, None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_44(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr("cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_45(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_46(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", )
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_47(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "XXcudaXX", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_48(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "CUDA", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_49(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = None
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_50(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get(None)
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_51(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("XXcudaXX")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_52(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("CUDA")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_53(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is not None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_54(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = None
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_55(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get(None)
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_56(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("XXtorch_cudaXX")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_57(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("TORCH_CUDA")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_58(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available") or cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_59(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None or hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_60(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state or cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_61(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_62(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(None, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_63(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, None)
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_64(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr("is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_65(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, )
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_66(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "XXis_availableXX")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_67(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "IS_AVAILABLE")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_68(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = None
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_69(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(None, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_70(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, None, None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_71(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr("set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_72(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_73(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", )
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_74(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "XXset_rng_state_allXX", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_75(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "SET_RNG_STATE_ALL", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_76(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(None):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_77(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(None):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_78(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(None)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_79(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = None
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_80(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = None
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_81(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(None)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_82(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(None)
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_83(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(None, exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_84(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=None)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_85(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_86(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", )
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_87(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=False)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_88(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = None
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_89(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(None):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_90(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(None):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_91(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = None
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_92(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=None)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_93(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = None
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_94(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(None, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_95(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=None)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_96(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_97(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, )
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_98(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    None,
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_99(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    device=None,
                )


def x__legacy_restore_rng_state__mutmut_100(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    device=idx,
                )


def x__legacy_restore_rng_state__mutmut_101(state: Mapping[str, Any]) -> None:
    if _torch is None:
        raise RuntimeError("torch is required to restore RNG state")

    torch_state = state.get("torch")
    if torch_state is None:
        torch_state = state.get("torch_cpu")
    if torch_state is not None:
        with suppress(Exception):
            if isinstance(torch_state, _torch.Tensor):
                tensor_state = torch_state.to(dtype=_torch.uint8)
            else:
                tensor_state = _torch.tensor(torch_state, dtype=_torch.uint8)
            _torch_rng_set_state(tensor_state)
    if _np is not None and "numpy" in state:
        with suppress(Exception):
            _np.random.set_state(state["numpy"])  # type: ignore[arg-type]
    if "python" in state:
        with suppress(Exception):
            _random.setstate(state["python"])  # type: ignore[arg-type]
    cuda_mod = getattr(_torch, "cuda", None)
    cuda_state = state.get("cuda")
    if cuda_state is None:
        cuda_state = state.get("torch_cuda")
    if (
        cuda_state
        and cuda_mod is not None
        and hasattr(cuda_mod, "is_available")
        and cuda_mod.is_available()
    ):
        set_all = getattr(cuda_mod, "set_rng_state_all", None)
        if callable(set_all):
            with suppress(Exception):
                set_all(cuda_state)  # type: ignore[arg-type]
                return
        if isinstance(cuda_state, _torch.Tensor):
            iterable_states = [cuda_state]
        else:
            try:
                iterable_states = list(cuda_state)
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                iterable_states = [cuda_state]
        for idx, tensor_state in enumerate(iterable_states):
            with suppress(Exception):
                if isinstance(tensor_state, _torch.Tensor):
                    normalized = tensor_state.to(dtype=_torch.uint8)
                else:
                    normalized = _torch.tensor(tensor_state, dtype=_torch.uint8)
                cuda_mod.set_rng_state(  # type: ignore[call-arg]
                    normalized,
                    )

x__legacy_restore_rng_state__mutmut_mutants : ClassVar[MutantDict] = {
'x__legacy_restore_rng_state__mutmut_1': x__legacy_restore_rng_state__mutmut_1, 
    'x__legacy_restore_rng_state__mutmut_2': x__legacy_restore_rng_state__mutmut_2, 
    'x__legacy_restore_rng_state__mutmut_3': x__legacy_restore_rng_state__mutmut_3, 
    'x__legacy_restore_rng_state__mutmut_4': x__legacy_restore_rng_state__mutmut_4, 
    'x__legacy_restore_rng_state__mutmut_5': x__legacy_restore_rng_state__mutmut_5, 
    'x__legacy_restore_rng_state__mutmut_6': x__legacy_restore_rng_state__mutmut_6, 
    'x__legacy_restore_rng_state__mutmut_7': x__legacy_restore_rng_state__mutmut_7, 
    'x__legacy_restore_rng_state__mutmut_8': x__legacy_restore_rng_state__mutmut_8, 
    'x__legacy_restore_rng_state__mutmut_9': x__legacy_restore_rng_state__mutmut_9, 
    'x__legacy_restore_rng_state__mutmut_10': x__legacy_restore_rng_state__mutmut_10, 
    'x__legacy_restore_rng_state__mutmut_11': x__legacy_restore_rng_state__mutmut_11, 
    'x__legacy_restore_rng_state__mutmut_12': x__legacy_restore_rng_state__mutmut_12, 
    'x__legacy_restore_rng_state__mutmut_13': x__legacy_restore_rng_state__mutmut_13, 
    'x__legacy_restore_rng_state__mutmut_14': x__legacy_restore_rng_state__mutmut_14, 
    'x__legacy_restore_rng_state__mutmut_15': x__legacy_restore_rng_state__mutmut_15, 
    'x__legacy_restore_rng_state__mutmut_16': x__legacy_restore_rng_state__mutmut_16, 
    'x__legacy_restore_rng_state__mutmut_17': x__legacy_restore_rng_state__mutmut_17, 
    'x__legacy_restore_rng_state__mutmut_18': x__legacy_restore_rng_state__mutmut_18, 
    'x__legacy_restore_rng_state__mutmut_19': x__legacy_restore_rng_state__mutmut_19, 
    'x__legacy_restore_rng_state__mutmut_20': x__legacy_restore_rng_state__mutmut_20, 
    'x__legacy_restore_rng_state__mutmut_21': x__legacy_restore_rng_state__mutmut_21, 
    'x__legacy_restore_rng_state__mutmut_22': x__legacy_restore_rng_state__mutmut_22, 
    'x__legacy_restore_rng_state__mutmut_23': x__legacy_restore_rng_state__mutmut_23, 
    'x__legacy_restore_rng_state__mutmut_24': x__legacy_restore_rng_state__mutmut_24, 
    'x__legacy_restore_rng_state__mutmut_25': x__legacy_restore_rng_state__mutmut_25, 
    'x__legacy_restore_rng_state__mutmut_26': x__legacy_restore_rng_state__mutmut_26, 
    'x__legacy_restore_rng_state__mutmut_27': x__legacy_restore_rng_state__mutmut_27, 
    'x__legacy_restore_rng_state__mutmut_28': x__legacy_restore_rng_state__mutmut_28, 
    'x__legacy_restore_rng_state__mutmut_29': x__legacy_restore_rng_state__mutmut_29, 
    'x__legacy_restore_rng_state__mutmut_30': x__legacy_restore_rng_state__mutmut_30, 
    'x__legacy_restore_rng_state__mutmut_31': x__legacy_restore_rng_state__mutmut_31, 
    'x__legacy_restore_rng_state__mutmut_32': x__legacy_restore_rng_state__mutmut_32, 
    'x__legacy_restore_rng_state__mutmut_33': x__legacy_restore_rng_state__mutmut_33, 
    'x__legacy_restore_rng_state__mutmut_34': x__legacy_restore_rng_state__mutmut_34, 
    'x__legacy_restore_rng_state__mutmut_35': x__legacy_restore_rng_state__mutmut_35, 
    'x__legacy_restore_rng_state__mutmut_36': x__legacy_restore_rng_state__mutmut_36, 
    'x__legacy_restore_rng_state__mutmut_37': x__legacy_restore_rng_state__mutmut_37, 
    'x__legacy_restore_rng_state__mutmut_38': x__legacy_restore_rng_state__mutmut_38, 
    'x__legacy_restore_rng_state__mutmut_39': x__legacy_restore_rng_state__mutmut_39, 
    'x__legacy_restore_rng_state__mutmut_40': x__legacy_restore_rng_state__mutmut_40, 
    'x__legacy_restore_rng_state__mutmut_41': x__legacy_restore_rng_state__mutmut_41, 
    'x__legacy_restore_rng_state__mutmut_42': x__legacy_restore_rng_state__mutmut_42, 
    'x__legacy_restore_rng_state__mutmut_43': x__legacy_restore_rng_state__mutmut_43, 
    'x__legacy_restore_rng_state__mutmut_44': x__legacy_restore_rng_state__mutmut_44, 
    'x__legacy_restore_rng_state__mutmut_45': x__legacy_restore_rng_state__mutmut_45, 
    'x__legacy_restore_rng_state__mutmut_46': x__legacy_restore_rng_state__mutmut_46, 
    'x__legacy_restore_rng_state__mutmut_47': x__legacy_restore_rng_state__mutmut_47, 
    'x__legacy_restore_rng_state__mutmut_48': x__legacy_restore_rng_state__mutmut_48, 
    'x__legacy_restore_rng_state__mutmut_49': x__legacy_restore_rng_state__mutmut_49, 
    'x__legacy_restore_rng_state__mutmut_50': x__legacy_restore_rng_state__mutmut_50, 
    'x__legacy_restore_rng_state__mutmut_51': x__legacy_restore_rng_state__mutmut_51, 
    'x__legacy_restore_rng_state__mutmut_52': x__legacy_restore_rng_state__mutmut_52, 
    'x__legacy_restore_rng_state__mutmut_53': x__legacy_restore_rng_state__mutmut_53, 
    'x__legacy_restore_rng_state__mutmut_54': x__legacy_restore_rng_state__mutmut_54, 
    'x__legacy_restore_rng_state__mutmut_55': x__legacy_restore_rng_state__mutmut_55, 
    'x__legacy_restore_rng_state__mutmut_56': x__legacy_restore_rng_state__mutmut_56, 
    'x__legacy_restore_rng_state__mutmut_57': x__legacy_restore_rng_state__mutmut_57, 
    'x__legacy_restore_rng_state__mutmut_58': x__legacy_restore_rng_state__mutmut_58, 
    'x__legacy_restore_rng_state__mutmut_59': x__legacy_restore_rng_state__mutmut_59, 
    'x__legacy_restore_rng_state__mutmut_60': x__legacy_restore_rng_state__mutmut_60, 
    'x__legacy_restore_rng_state__mutmut_61': x__legacy_restore_rng_state__mutmut_61, 
    'x__legacy_restore_rng_state__mutmut_62': x__legacy_restore_rng_state__mutmut_62, 
    'x__legacy_restore_rng_state__mutmut_63': x__legacy_restore_rng_state__mutmut_63, 
    'x__legacy_restore_rng_state__mutmut_64': x__legacy_restore_rng_state__mutmut_64, 
    'x__legacy_restore_rng_state__mutmut_65': x__legacy_restore_rng_state__mutmut_65, 
    'x__legacy_restore_rng_state__mutmut_66': x__legacy_restore_rng_state__mutmut_66, 
    'x__legacy_restore_rng_state__mutmut_67': x__legacy_restore_rng_state__mutmut_67, 
    'x__legacy_restore_rng_state__mutmut_68': x__legacy_restore_rng_state__mutmut_68, 
    'x__legacy_restore_rng_state__mutmut_69': x__legacy_restore_rng_state__mutmut_69, 
    'x__legacy_restore_rng_state__mutmut_70': x__legacy_restore_rng_state__mutmut_70, 
    'x__legacy_restore_rng_state__mutmut_71': x__legacy_restore_rng_state__mutmut_71, 
    'x__legacy_restore_rng_state__mutmut_72': x__legacy_restore_rng_state__mutmut_72, 
    'x__legacy_restore_rng_state__mutmut_73': x__legacy_restore_rng_state__mutmut_73, 
    'x__legacy_restore_rng_state__mutmut_74': x__legacy_restore_rng_state__mutmut_74, 
    'x__legacy_restore_rng_state__mutmut_75': x__legacy_restore_rng_state__mutmut_75, 
    'x__legacy_restore_rng_state__mutmut_76': x__legacy_restore_rng_state__mutmut_76, 
    'x__legacy_restore_rng_state__mutmut_77': x__legacy_restore_rng_state__mutmut_77, 
    'x__legacy_restore_rng_state__mutmut_78': x__legacy_restore_rng_state__mutmut_78, 
    'x__legacy_restore_rng_state__mutmut_79': x__legacy_restore_rng_state__mutmut_79, 
    'x__legacy_restore_rng_state__mutmut_80': x__legacy_restore_rng_state__mutmut_80, 
    'x__legacy_restore_rng_state__mutmut_81': x__legacy_restore_rng_state__mutmut_81, 
    'x__legacy_restore_rng_state__mutmut_82': x__legacy_restore_rng_state__mutmut_82, 
    'x__legacy_restore_rng_state__mutmut_83': x__legacy_restore_rng_state__mutmut_83, 
    'x__legacy_restore_rng_state__mutmut_84': x__legacy_restore_rng_state__mutmut_84, 
    'x__legacy_restore_rng_state__mutmut_85': x__legacy_restore_rng_state__mutmut_85, 
    'x__legacy_restore_rng_state__mutmut_86': x__legacy_restore_rng_state__mutmut_86, 
    'x__legacy_restore_rng_state__mutmut_87': x__legacy_restore_rng_state__mutmut_87, 
    'x__legacy_restore_rng_state__mutmut_88': x__legacy_restore_rng_state__mutmut_88, 
    'x__legacy_restore_rng_state__mutmut_89': x__legacy_restore_rng_state__mutmut_89, 
    'x__legacy_restore_rng_state__mutmut_90': x__legacy_restore_rng_state__mutmut_90, 
    'x__legacy_restore_rng_state__mutmut_91': x__legacy_restore_rng_state__mutmut_91, 
    'x__legacy_restore_rng_state__mutmut_92': x__legacy_restore_rng_state__mutmut_92, 
    'x__legacy_restore_rng_state__mutmut_93': x__legacy_restore_rng_state__mutmut_93, 
    'x__legacy_restore_rng_state__mutmut_94': x__legacy_restore_rng_state__mutmut_94, 
    'x__legacy_restore_rng_state__mutmut_95': x__legacy_restore_rng_state__mutmut_95, 
    'x__legacy_restore_rng_state__mutmut_96': x__legacy_restore_rng_state__mutmut_96, 
    'x__legacy_restore_rng_state__mutmut_97': x__legacy_restore_rng_state__mutmut_97, 
    'x__legacy_restore_rng_state__mutmut_98': x__legacy_restore_rng_state__mutmut_98, 
    'x__legacy_restore_rng_state__mutmut_99': x__legacy_restore_rng_state__mutmut_99, 
    'x__legacy_restore_rng_state__mutmut_100': x__legacy_restore_rng_state__mutmut_100, 
    'x__legacy_restore_rng_state__mutmut_101': x__legacy_restore_rng_state__mutmut_101
}

def _legacy_restore_rng_state(*args, **kwargs):
    result = _mutmut_trampoline(x__legacy_restore_rng_state__mutmut_orig, x__legacy_restore_rng_state__mutmut_mutants, args, kwargs)
    return result 

_legacy_restore_rng_state.__signature__ = _mutmut_signature(x__legacy_restore_rng_state__mutmut_orig)
x__legacy_restore_rng_state__mutmut_orig.__name__ = 'x__legacy_restore_rng_state'


def x__capture_rng__mutmut_orig() -> dict[str, Any]:
    if _capture_rng_state is not None:
        return _capture_rng_state()
    return _legacy_capture_rng_state()


def x__capture_rng__mutmut_1() -> dict[str, Any]:
    if _capture_rng_state is None:
        return _capture_rng_state()
    return _legacy_capture_rng_state()

x__capture_rng__mutmut_mutants : ClassVar[MutantDict] = {
'x__capture_rng__mutmut_1': x__capture_rng__mutmut_1
}

def _capture_rng(*args, **kwargs):
    result = _mutmut_trampoline(x__capture_rng__mutmut_orig, x__capture_rng__mutmut_mutants, args, kwargs)
    return result 

_capture_rng.__signature__ = _mutmut_signature(x__capture_rng__mutmut_orig)
x__capture_rng__mutmut_orig.__name__ = 'x__capture_rng'


def x__restore_rng__mutmut_orig(state: Mapping[str, Any]) -> None:
    if not state:
        return
    if _restore_rng_state is not None:
        try:
            _restore_rng_state(state)
            return
        except Exception as exc:  # pragma: no cover - fall back to legacy behaviour
            LOGGER.debug("Canonical RNG restore failed; falling back to legacy: %s", exc)
    _legacy_restore_rng_state(state)


def x__restore_rng__mutmut_1(state: Mapping[str, Any]) -> None:
    if state:
        return
    if _restore_rng_state is not None:
        try:
            _restore_rng_state(state)
            return
        except Exception as exc:  # pragma: no cover - fall back to legacy behaviour
            LOGGER.debug("Canonical RNG restore failed; falling back to legacy: %s", exc)
    _legacy_restore_rng_state(state)


def x__restore_rng__mutmut_2(state: Mapping[str, Any]) -> None:
    if not state:
        return
    if _restore_rng_state is None:
        try:
            _restore_rng_state(state)
            return
        except Exception as exc:  # pragma: no cover - fall back to legacy behaviour
            LOGGER.debug("Canonical RNG restore failed; falling back to legacy: %s", exc)
    _legacy_restore_rng_state(state)


def x__restore_rng__mutmut_3(state: Mapping[str, Any]) -> None:
    if not state:
        return
    if _restore_rng_state is not None:
        try:
            _restore_rng_state(None)
            return
        except Exception as exc:  # pragma: no cover - fall back to legacy behaviour
            LOGGER.debug("Canonical RNG restore failed; falling back to legacy: %s", exc)
    _legacy_restore_rng_state(state)


def x__restore_rng__mutmut_4(state: Mapping[str, Any]) -> None:
    if not state:
        return
    if _restore_rng_state is not None:
        try:
            _restore_rng_state(state)
            return
        except Exception as exc:  # pragma: no cover - fall back to legacy behaviour
            LOGGER.debug(None, exc)
    _legacy_restore_rng_state(state)


def x__restore_rng__mutmut_5(state: Mapping[str, Any]) -> None:
    if not state:
        return
    if _restore_rng_state is not None:
        try:
            _restore_rng_state(state)
            return
        except Exception as exc:  # pragma: no cover - fall back to legacy behaviour
            LOGGER.debug("Canonical RNG restore failed; falling back to legacy: %s", None)
    _legacy_restore_rng_state(state)


def x__restore_rng__mutmut_6(state: Mapping[str, Any]) -> None:
    if not state:
        return
    if _restore_rng_state is not None:
        try:
            _restore_rng_state(state)
            return
        except Exception as exc:  # pragma: no cover - fall back to legacy behaviour
            LOGGER.debug(exc)
    _legacy_restore_rng_state(state)


def x__restore_rng__mutmut_7(state: Mapping[str, Any]) -> None:
    if not state:
        return
    if _restore_rng_state is not None:
        try:
            _restore_rng_state(state)
            return
        except Exception as exc:  # pragma: no cover - fall back to legacy behaviour
            LOGGER.debug("Canonical RNG restore failed; falling back to legacy: %s", )
    _legacy_restore_rng_state(state)


def x__restore_rng__mutmut_8(state: Mapping[str, Any]) -> None:
    if not state:
        return
    if _restore_rng_state is not None:
        try:
            _restore_rng_state(state)
            return
        except Exception as exc:  # pragma: no cover - fall back to legacy behaviour
            LOGGER.debug("XXCanonical RNG restore failed; falling back to legacy: %sXX", exc)
    _legacy_restore_rng_state(state)


def x__restore_rng__mutmut_9(state: Mapping[str, Any]) -> None:
    if not state:
        return
    if _restore_rng_state is not None:
        try:
            _restore_rng_state(state)
            return
        except Exception as exc:  # pragma: no cover - fall back to legacy behaviour
            LOGGER.debug("canonical rng restore failed; falling back to legacy: %s", exc)
    _legacy_restore_rng_state(state)


def x__restore_rng__mutmut_10(state: Mapping[str, Any]) -> None:
    if not state:
        return
    if _restore_rng_state is not None:
        try:
            _restore_rng_state(state)
            return
        except Exception as exc:  # pragma: no cover - fall back to legacy behaviour
            LOGGER.debug("CANONICAL RNG RESTORE FAILED; FALLING BACK TO LEGACY: %S", exc)
    _legacy_restore_rng_state(state)


def x__restore_rng__mutmut_11(state: Mapping[str, Any]) -> None:
    if not state:
        return
    if _restore_rng_state is not None:
        try:
            _restore_rng_state(state)
            return
        except Exception as exc:  # pragma: no cover - fall back to legacy behaviour
            LOGGER.debug("Canonical RNG restore failed; falling back to legacy: %s", exc)
    _legacy_restore_rng_state(None)

x__restore_rng__mutmut_mutants : ClassVar[MutantDict] = {
'x__restore_rng__mutmut_1': x__restore_rng__mutmut_1, 
    'x__restore_rng__mutmut_2': x__restore_rng__mutmut_2, 
    'x__restore_rng__mutmut_3': x__restore_rng__mutmut_3, 
    'x__restore_rng__mutmut_4': x__restore_rng__mutmut_4, 
    'x__restore_rng__mutmut_5': x__restore_rng__mutmut_5, 
    'x__restore_rng__mutmut_6': x__restore_rng__mutmut_6, 
    'x__restore_rng__mutmut_7': x__restore_rng__mutmut_7, 
    'x__restore_rng__mutmut_8': x__restore_rng__mutmut_8, 
    'x__restore_rng__mutmut_9': x__restore_rng__mutmut_9, 
    'x__restore_rng__mutmut_10': x__restore_rng__mutmut_10, 
    'x__restore_rng__mutmut_11': x__restore_rng__mutmut_11
}

def _restore_rng(*args, **kwargs):
    result = _mutmut_trampoline(x__restore_rng__mutmut_orig, x__restore_rng__mutmut_mutants, args, kwargs)
    return result 

_restore_rng.__signature__ = _mutmut_signature(x__restore_rng__mutmut_orig)
x__restore_rng__mutmut_orig.__name__ = 'x__restore_rng'


def x__torch_load__mutmut_orig(path: str, *, map_location: str | None = None) -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(_torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug(f"TypeError: {exc}")
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_1(path: str, *, map_location: str | None = None) -> Any:
    if _torch is not None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(_torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug(f"TypeError: {exc}")
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_2(path: str, *, map_location: str | None = None) -> Any:
    if _torch is None:
        raise RuntimeError(None)
    load_fn = getattr(_torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug(f"TypeError: {exc}")
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_3(path: str, *, map_location: str | None = None) -> Any:
    if _torch is None:
        raise RuntimeError("XXtorch is required to load checkpointsXX")
    load_fn = getattr(_torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug(f"TypeError: {exc}")
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_4(path: str, *, map_location: str | None = None) -> Any:
    if _torch is None:
        raise RuntimeError("TORCH IS REQUIRED TO LOAD CHECKPOINTS")
    load_fn = getattr(_torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug(f"TypeError: {exc}")
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_5(path: str, *, map_location: str | None = None) -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = None
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug(f"TypeError: {exc}")
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_6(path: str, *, map_location: str | None = None) -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(None, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug(f"TypeError: {exc}")
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_7(path: str, *, map_location: str | None = None) -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(_torch, None, None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug(f"TypeError: {exc}")
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_8(path: str, *, map_location: str | None = None) -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr("load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug(f"TypeError: {exc}")
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_9(path: str, *, map_location: str | None = None) -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(_torch, None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug(f"TypeError: {exc}")
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_10(path: str, *, map_location: str | None = None) -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(_torch, "load", )
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug(f"TypeError: {exc}")
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_11(path: str, *, map_location: str | None = None) -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(_torch, "XXloadXX", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug(f"TypeError: {exc}")
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_12(path: str, *, map_location: str | None = None) -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(_torch, "LOAD", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug(f"TypeError: {exc}")
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_13(path: str, *, map_location: str | None = None) -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(_torch, "load", None)
    if load_fn is not None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug(f"TypeError: {exc}")
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_14(path: str, *, map_location: str | None = None) -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(_torch, "load", None)
    if load_fn is None:
        raise RuntimeError(None)
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug(f"TypeError: {exc}")
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_15(path: str, *, map_location: str | None = None) -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(_torch, "load", None)
    if load_fn is None:
        raise RuntimeError("XXCurrent torch build does not expose torch.loadXX")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug(f"TypeError: {exc}")
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_16(path: str, *, map_location: str | None = None) -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(_torch, "load", None)
    if load_fn is None:
        raise RuntimeError("current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug(f"TypeError: {exc}")
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_17(path: str, *, map_location: str | None = None) -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(_torch, "load", None)
    if load_fn is None:
        raise RuntimeError("CURRENT TORCH BUILD DOES NOT EXPOSE TORCH.LOAD")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug(f"TypeError: {exc}")
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_18(path: str, *, map_location: str | None = None) -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(_torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = None
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug(f"TypeError: {exc}")
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_19(path: str, *, map_location: str | None = None) -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(_torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug(f"TypeError: {exc}")
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_20(path: str, *, map_location: str | None = None) -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(_torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = None
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug(f"TypeError: {exc}")
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_21(path: str, *, map_location: str | None = None) -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(_torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["XXmap_locationXX"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug(f"TypeError: {exc}")
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_22(path: str, *, map_location: str | None = None) -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(_torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["MAP_LOCATION"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug(f"TypeError: {exc}")
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_23(path: str, *, map_location: str | None = None) -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(_torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = None
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug(f"TypeError: {exc}")
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_24(path: str, *, map_location: str | None = None) -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(_torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["XXweights_onlyXX"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug(f"TypeError: {exc}")
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_25(path: str, *, map_location: str | None = None) -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(_torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["WEIGHTS_ONLY"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug(f"TypeError: {exc}")
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_26(path: str, *, map_location: str | None = None) -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(_torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = False
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug(f"TypeError: {exc}")
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_27(path: str, *, map_location: str | None = None) -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(_torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(None, **kwargs)
    except TypeError as exc:
        logger.debug(f"TypeError: {exc}")
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_28(path: str, *, map_location: str | None = None) -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(_torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(**kwargs)
    except TypeError as exc:
        logger.debug(f"TypeError: {exc}")
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_29(path: str, *, map_location: str | None = None) -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(_torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, )
    except TypeError as exc:
        logger.debug(f"TypeError: {exc}")
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_30(path: str, *, map_location: str | None = None) -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(_torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug(None)
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_31(path: str, *, map_location: str | None = None) -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(_torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug(f"TypeError: {exc}")
        if _TORCH_SUPPORTS_WEIGHTS_ONLY or "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_32(path: str, *, map_location: str | None = None) -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(_torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug(f"TypeError: {exc}")
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "XXweights_onlyXX" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_33(path: str, *, map_location: str | None = None) -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(_torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug(f"TypeError: {exc}")
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "WEIGHTS_ONLY" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_34(path: str, *, map_location: str | None = None) -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(_torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug(f"TypeError: {exc}")
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" not in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_35(path: str, *, map_location: str | None = None) -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(_torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug(f"TypeError: {exc}")
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(None):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_36(path: str, *, map_location: str | None = None) -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(_torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug(f"TypeError: {exc}")
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop(None, None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_37(path: str, *, map_location: str | None = None) -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(_torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug(f"TypeError: {exc}")
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop(None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_38(path: str, *, map_location: str | None = None) -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(_torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug(f"TypeError: {exc}")
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", )
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_39(path: str, *, map_location: str | None = None) -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(_torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug(f"TypeError: {exc}")
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("XXweights_onlyXX", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_40(path: str, *, map_location: str | None = None) -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(_torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug(f"TypeError: {exc}")
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("WEIGHTS_ONLY", None)
            return load_fn(path, **kwargs)
        raise


def x__torch_load__mutmut_41(path: str, *, map_location: str | None = None) -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(_torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug(f"TypeError: {exc}")
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(None, **kwargs)
        raise


def x__torch_load__mutmut_42(path: str, *, map_location: str | None = None) -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(_torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug(f"TypeError: {exc}")
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(**kwargs)
        raise


def x__torch_load__mutmut_43(path: str, *, map_location: str | None = None) -> Any:
    if _torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(_torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        # Security: Use weights_only=True to prevent arbitrary code execution
        # This is the secure default for PyTorch >=2.2.2 (CVE-2024-XXXXX)
        kwargs["weights_only"] = True
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        logger.debug(f"TypeError: {exc}")
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, )
        raise

x__torch_load__mutmut_mutants : ClassVar[MutantDict] = {
'x__torch_load__mutmut_1': x__torch_load__mutmut_1, 
    'x__torch_load__mutmut_2': x__torch_load__mutmut_2, 
    'x__torch_load__mutmut_3': x__torch_load__mutmut_3, 
    'x__torch_load__mutmut_4': x__torch_load__mutmut_4, 
    'x__torch_load__mutmut_5': x__torch_load__mutmut_5, 
    'x__torch_load__mutmut_6': x__torch_load__mutmut_6, 
    'x__torch_load__mutmut_7': x__torch_load__mutmut_7, 
    'x__torch_load__mutmut_8': x__torch_load__mutmut_8, 
    'x__torch_load__mutmut_9': x__torch_load__mutmut_9, 
    'x__torch_load__mutmut_10': x__torch_load__mutmut_10, 
    'x__torch_load__mutmut_11': x__torch_load__mutmut_11, 
    'x__torch_load__mutmut_12': x__torch_load__mutmut_12, 
    'x__torch_load__mutmut_13': x__torch_load__mutmut_13, 
    'x__torch_load__mutmut_14': x__torch_load__mutmut_14, 
    'x__torch_load__mutmut_15': x__torch_load__mutmut_15, 
    'x__torch_load__mutmut_16': x__torch_load__mutmut_16, 
    'x__torch_load__mutmut_17': x__torch_load__mutmut_17, 
    'x__torch_load__mutmut_18': x__torch_load__mutmut_18, 
    'x__torch_load__mutmut_19': x__torch_load__mutmut_19, 
    'x__torch_load__mutmut_20': x__torch_load__mutmut_20, 
    'x__torch_load__mutmut_21': x__torch_load__mutmut_21, 
    'x__torch_load__mutmut_22': x__torch_load__mutmut_22, 
    'x__torch_load__mutmut_23': x__torch_load__mutmut_23, 
    'x__torch_load__mutmut_24': x__torch_load__mutmut_24, 
    'x__torch_load__mutmut_25': x__torch_load__mutmut_25, 
    'x__torch_load__mutmut_26': x__torch_load__mutmut_26, 
    'x__torch_load__mutmut_27': x__torch_load__mutmut_27, 
    'x__torch_load__mutmut_28': x__torch_load__mutmut_28, 
    'x__torch_load__mutmut_29': x__torch_load__mutmut_29, 
    'x__torch_load__mutmut_30': x__torch_load__mutmut_30, 
    'x__torch_load__mutmut_31': x__torch_load__mutmut_31, 
    'x__torch_load__mutmut_32': x__torch_load__mutmut_32, 
    'x__torch_load__mutmut_33': x__torch_load__mutmut_33, 
    'x__torch_load__mutmut_34': x__torch_load__mutmut_34, 
    'x__torch_load__mutmut_35': x__torch_load__mutmut_35, 
    'x__torch_load__mutmut_36': x__torch_load__mutmut_36, 
    'x__torch_load__mutmut_37': x__torch_load__mutmut_37, 
    'x__torch_load__mutmut_38': x__torch_load__mutmut_38, 
    'x__torch_load__mutmut_39': x__torch_load__mutmut_39, 
    'x__torch_load__mutmut_40': x__torch_load__mutmut_40, 
    'x__torch_load__mutmut_41': x__torch_load__mutmut_41, 
    'x__torch_load__mutmut_42': x__torch_load__mutmut_42, 
    'x__torch_load__mutmut_43': x__torch_load__mutmut_43
}

def _torch_load(*args, **kwargs):
    result = _mutmut_trampoline(x__torch_load__mutmut_orig, x__torch_load__mutmut_mutants, args, kwargs)
    return result 

_torch_load.__signature__ = _mutmut_signature(x__torch_load__mutmut_orig)
x__torch_load__mutmut_orig.__name__ = 'x__torch_load'


def x_save_checkpoint__mutmut_orig(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_1(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = False,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_2(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        None,
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_3(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        None,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_4(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=None,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_5(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_6(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_7(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_8(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "XXsrc.utils.checkpoint.save_checkpoint is deprecated; use XX"
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_9(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "SRC.UTILS.CHECKPOINT.SAVE_CHECKPOINT IS DEPRECATED; USE "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_10(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "XXcodex_ml.utils.checkpoint_core.save_checkpoint instead.XX",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_11(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "CODEX_ML.UTILS.CHECKPOINT_CORE.SAVE_CHECKPOINT INSTEAD.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_12(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=3,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_13(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is not None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_14(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError(None)

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_15(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("XXsave_checkpoint is unavailable; install codex-ml checkpoint extrasXX")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_16(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("SAVE_CHECKPOINT IS UNAVAILABLE; INSTALL CODEX-ML CHECKPOINT EXTRAS")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_17(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = None
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_18(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(None)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_19(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() or target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_20(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(None, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_21(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, None, **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_22(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_23(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_24(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), )
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_25(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(None), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_26(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = None
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_27(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(None) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_28(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(None)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_29(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path("XX.XX")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_30(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=None, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_31(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=None)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_32(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_33(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, )
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_34(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=False, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_35(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=False)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_36(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = None

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_37(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(None, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_38(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, None, **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_39(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_40(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_41(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), )

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_42(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(None), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_43(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = None
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_44(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(None) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_45(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(None)
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_46(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path("XX.XX")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_47(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=None, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_48(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=None)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_49(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_50(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, )
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_51(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=False, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_52(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=False)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_53(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = None
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_54(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = ""
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_55(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=None, delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_56(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=None) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_57(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_58(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), ) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_59(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(None), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_60(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=True) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_61(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(None)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_62(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = None
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_63(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(None)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_64(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(None, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_65(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, None)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_66(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_67(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, )
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_68(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = ""
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_69(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_70(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(None)
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_71(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning(None, tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_72(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", None, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_73(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, None)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_74(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning(tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_75(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_76(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, )

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_77(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("XXTemporary checkpoint cleanup failed for %s: %sXX", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_78(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_79(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("TEMPORARY CHECKPOINT CLEANUP FAILED FOR %S: %S", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_80(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest or target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_81(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(None)
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_82(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug(None, target, exc)
    return None


def x_save_checkpoint__mutmut_83(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", None, exc)
    return None


def x_save_checkpoint__mutmut_84(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, None)
    return None


def x_save_checkpoint__mutmut_85(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug(target, exc)
    return None


def x_save_checkpoint__mutmut_86(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", exc)
    return None


def x_save_checkpoint__mutmut_87(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("Failed to clean up symlink %s during archive: %s", target, )
    return None


def x_save_checkpoint__mutmut_88(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("XXFailed to clean up symlink %s during archive: %sXX", target, exc)
    return None


def x_save_checkpoint__mutmut_89(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("failed to clean up symlink %s during archive: %s", target, exc)
    return None


def x_save_checkpoint__mutmut_90(
    state: Mapping[str, Any],
    path: str | os.PathLike[str],
    archive_latest: bool = True,
    **kwargs: Any,
) -> None:
    """Legacy wrapper preserving the historic :mod:`src.utils.checkpoint` contract.

    The canonical implementation expects the checkpoint directory as the first
    argument and returns ``(path, meta)``.  Historical callers passed a file path
    and ignored the return value.  This shim adapts arguments to the canonical
    helper while keeping the observable behaviour intact.
    """

    _warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.save_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_save_checkpoint is None:
        raise ImportError("save_checkpoint is unavailable; install codex-ml checkpoint extras")

    target = Path(path)
    # When the caller already points at a directory, defer completely to the
    # canonical implementation.
    if target.exists() and target.is_dir():
        _canonical_save_checkpoint(target, dict(state), **kwargs)
        return None

    checkpoint_dir = target.parent if str(target.parent) else Path(".")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    written_path, _meta = _canonical_save_checkpoint(checkpoint_dir, dict(state), **kwargs)

    target_parent = target.parent if str(target.parent) else Path(".")
    target_parent.mkdir(parents=True, exist_ok=True)
    raw = written_path.read_bytes()
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(target_parent), delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except Exception as exc:
                logger.debug(f"Exception: {exc}")
                LOGGER.warning("Temporary checkpoint cleanup failed for %s: %s", tmp_path, exc)

    if archive_latest and target.is_symlink():
        try:
            target.unlink()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            LOGGER.debug("FAILED TO CLEAN UP SYMLINK %S DURING ARCHIVE: %S", target, exc)
    return None

x_save_checkpoint__mutmut_mutants : ClassVar[MutantDict] = {
'x_save_checkpoint__mutmut_1': x_save_checkpoint__mutmut_1, 
    'x_save_checkpoint__mutmut_2': x_save_checkpoint__mutmut_2, 
    'x_save_checkpoint__mutmut_3': x_save_checkpoint__mutmut_3, 
    'x_save_checkpoint__mutmut_4': x_save_checkpoint__mutmut_4, 
    'x_save_checkpoint__mutmut_5': x_save_checkpoint__mutmut_5, 
    'x_save_checkpoint__mutmut_6': x_save_checkpoint__mutmut_6, 
    'x_save_checkpoint__mutmut_7': x_save_checkpoint__mutmut_7, 
    'x_save_checkpoint__mutmut_8': x_save_checkpoint__mutmut_8, 
    'x_save_checkpoint__mutmut_9': x_save_checkpoint__mutmut_9, 
    'x_save_checkpoint__mutmut_10': x_save_checkpoint__mutmut_10, 
    'x_save_checkpoint__mutmut_11': x_save_checkpoint__mutmut_11, 
    'x_save_checkpoint__mutmut_12': x_save_checkpoint__mutmut_12, 
    'x_save_checkpoint__mutmut_13': x_save_checkpoint__mutmut_13, 
    'x_save_checkpoint__mutmut_14': x_save_checkpoint__mutmut_14, 
    'x_save_checkpoint__mutmut_15': x_save_checkpoint__mutmut_15, 
    'x_save_checkpoint__mutmut_16': x_save_checkpoint__mutmut_16, 
    'x_save_checkpoint__mutmut_17': x_save_checkpoint__mutmut_17, 
    'x_save_checkpoint__mutmut_18': x_save_checkpoint__mutmut_18, 
    'x_save_checkpoint__mutmut_19': x_save_checkpoint__mutmut_19, 
    'x_save_checkpoint__mutmut_20': x_save_checkpoint__mutmut_20, 
    'x_save_checkpoint__mutmut_21': x_save_checkpoint__mutmut_21, 
    'x_save_checkpoint__mutmut_22': x_save_checkpoint__mutmut_22, 
    'x_save_checkpoint__mutmut_23': x_save_checkpoint__mutmut_23, 
    'x_save_checkpoint__mutmut_24': x_save_checkpoint__mutmut_24, 
    'x_save_checkpoint__mutmut_25': x_save_checkpoint__mutmut_25, 
    'x_save_checkpoint__mutmut_26': x_save_checkpoint__mutmut_26, 
    'x_save_checkpoint__mutmut_27': x_save_checkpoint__mutmut_27, 
    'x_save_checkpoint__mutmut_28': x_save_checkpoint__mutmut_28, 
    'x_save_checkpoint__mutmut_29': x_save_checkpoint__mutmut_29, 
    'x_save_checkpoint__mutmut_30': x_save_checkpoint__mutmut_30, 
    'x_save_checkpoint__mutmut_31': x_save_checkpoint__mutmut_31, 
    'x_save_checkpoint__mutmut_32': x_save_checkpoint__mutmut_32, 
    'x_save_checkpoint__mutmut_33': x_save_checkpoint__mutmut_33, 
    'x_save_checkpoint__mutmut_34': x_save_checkpoint__mutmut_34, 
    'x_save_checkpoint__mutmut_35': x_save_checkpoint__mutmut_35, 
    'x_save_checkpoint__mutmut_36': x_save_checkpoint__mutmut_36, 
    'x_save_checkpoint__mutmut_37': x_save_checkpoint__mutmut_37, 
    'x_save_checkpoint__mutmut_38': x_save_checkpoint__mutmut_38, 
    'x_save_checkpoint__mutmut_39': x_save_checkpoint__mutmut_39, 
    'x_save_checkpoint__mutmut_40': x_save_checkpoint__mutmut_40, 
    'x_save_checkpoint__mutmut_41': x_save_checkpoint__mutmut_41, 
    'x_save_checkpoint__mutmut_42': x_save_checkpoint__mutmut_42, 
    'x_save_checkpoint__mutmut_43': x_save_checkpoint__mutmut_43, 
    'x_save_checkpoint__mutmut_44': x_save_checkpoint__mutmut_44, 
    'x_save_checkpoint__mutmut_45': x_save_checkpoint__mutmut_45, 
    'x_save_checkpoint__mutmut_46': x_save_checkpoint__mutmut_46, 
    'x_save_checkpoint__mutmut_47': x_save_checkpoint__mutmut_47, 
    'x_save_checkpoint__mutmut_48': x_save_checkpoint__mutmut_48, 
    'x_save_checkpoint__mutmut_49': x_save_checkpoint__mutmut_49, 
    'x_save_checkpoint__mutmut_50': x_save_checkpoint__mutmut_50, 
    'x_save_checkpoint__mutmut_51': x_save_checkpoint__mutmut_51, 
    'x_save_checkpoint__mutmut_52': x_save_checkpoint__mutmut_52, 
    'x_save_checkpoint__mutmut_53': x_save_checkpoint__mutmut_53, 
    'x_save_checkpoint__mutmut_54': x_save_checkpoint__mutmut_54, 
    'x_save_checkpoint__mutmut_55': x_save_checkpoint__mutmut_55, 
    'x_save_checkpoint__mutmut_56': x_save_checkpoint__mutmut_56, 
    'x_save_checkpoint__mutmut_57': x_save_checkpoint__mutmut_57, 
    'x_save_checkpoint__mutmut_58': x_save_checkpoint__mutmut_58, 
    'x_save_checkpoint__mutmut_59': x_save_checkpoint__mutmut_59, 
    'x_save_checkpoint__mutmut_60': x_save_checkpoint__mutmut_60, 
    'x_save_checkpoint__mutmut_61': x_save_checkpoint__mutmut_61, 
    'x_save_checkpoint__mutmut_62': x_save_checkpoint__mutmut_62, 
    'x_save_checkpoint__mutmut_63': x_save_checkpoint__mutmut_63, 
    'x_save_checkpoint__mutmut_64': x_save_checkpoint__mutmut_64, 
    'x_save_checkpoint__mutmut_65': x_save_checkpoint__mutmut_65, 
    'x_save_checkpoint__mutmut_66': x_save_checkpoint__mutmut_66, 
    'x_save_checkpoint__mutmut_67': x_save_checkpoint__mutmut_67, 
    'x_save_checkpoint__mutmut_68': x_save_checkpoint__mutmut_68, 
    'x_save_checkpoint__mutmut_69': x_save_checkpoint__mutmut_69, 
    'x_save_checkpoint__mutmut_70': x_save_checkpoint__mutmut_70, 
    'x_save_checkpoint__mutmut_71': x_save_checkpoint__mutmut_71, 
    'x_save_checkpoint__mutmut_72': x_save_checkpoint__mutmut_72, 
    'x_save_checkpoint__mutmut_73': x_save_checkpoint__mutmut_73, 
    'x_save_checkpoint__mutmut_74': x_save_checkpoint__mutmut_74, 
    'x_save_checkpoint__mutmut_75': x_save_checkpoint__mutmut_75, 
    'x_save_checkpoint__mutmut_76': x_save_checkpoint__mutmut_76, 
    'x_save_checkpoint__mutmut_77': x_save_checkpoint__mutmut_77, 
    'x_save_checkpoint__mutmut_78': x_save_checkpoint__mutmut_78, 
    'x_save_checkpoint__mutmut_79': x_save_checkpoint__mutmut_79, 
    'x_save_checkpoint__mutmut_80': x_save_checkpoint__mutmut_80, 
    'x_save_checkpoint__mutmut_81': x_save_checkpoint__mutmut_81, 
    'x_save_checkpoint__mutmut_82': x_save_checkpoint__mutmut_82, 
    'x_save_checkpoint__mutmut_83': x_save_checkpoint__mutmut_83, 
    'x_save_checkpoint__mutmut_84': x_save_checkpoint__mutmut_84, 
    'x_save_checkpoint__mutmut_85': x_save_checkpoint__mutmut_85, 
    'x_save_checkpoint__mutmut_86': x_save_checkpoint__mutmut_86, 
    'x_save_checkpoint__mutmut_87': x_save_checkpoint__mutmut_87, 
    'x_save_checkpoint__mutmut_88': x_save_checkpoint__mutmut_88, 
    'x_save_checkpoint__mutmut_89': x_save_checkpoint__mutmut_89, 
    'x_save_checkpoint__mutmut_90': x_save_checkpoint__mutmut_90
}

def save_checkpoint(*args, **kwargs):
    result = _mutmut_trampoline(x_save_checkpoint__mutmut_orig, x_save_checkpoint__mutmut_mutants, args, kwargs)
    return result 

save_checkpoint.__signature__ = _mutmut_signature(x_save_checkpoint__mutmut_orig)
x_save_checkpoint__mutmut_orig.__name__ = 'x_save_checkpoint'


def x_load_checkpoint__mutmut_orig(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_1(
    path: str | os.PathLike[str],
    device: str = "XXcpuXX",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_2(
    path: str | os.PathLike[str],
    device: str = "CPU",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_3(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        None,
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_4(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        None,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_5(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=None,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_6(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_7(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_8(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_9(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "XXsrc.utils.checkpoint.load_checkpoint is deprecated; use XX"
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_10(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "SRC.UTILS.CHECKPOINT.LOAD_CHECKPOINT IS DEPRECATED; USE "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_11(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "XXcodex_ml.utils.checkpoint_core.load_checkpoint instead.XX",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_12(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "CODEX_ML.UTILS.CHECKPOINT_CORE.LOAD_CHECKPOINT INSTEAD.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_13(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=3,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_14(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is not None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_15(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError(None)

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_16(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("XXload_checkpoint is unavailable; install codex-ml checkpoint extrasXX")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_17(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("LOAD_CHECKPOINT IS UNAVAILABLE; INSTALL CODEX-ML CHECKPOINT EXTRAS")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_18(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = None
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_19(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_20(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else False
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_21(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device or device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_22(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs or device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_23(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "XXmap_locationXX" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_24(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "MAP_LOCATION" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_25(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" not in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_26(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device == "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_27(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "XXcpuXX":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_28(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "CPU":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_29(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            None,
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_30(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            None,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_31(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=None,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_32(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_33(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_34(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_35(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "XXBoth device and map_location specified; preferring explicit map_location.XX",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_36(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_37(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "BOTH DEVICE AND MAP_LOCATION SPECIFIED; PREFERRING EXPLICIT MAP_LOCATION.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_38(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=3,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_39(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs or device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_40(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "XXmap_locationXX" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_41(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "MAP_LOCATION" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_42(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_43(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = None

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_44(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["XXmap_locationXX"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_45(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["MAP_LOCATION"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_46(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = None
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_47(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(None, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_48(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=None, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_49(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_50(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_51(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, )
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_52(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning(None, exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_53(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=None)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_54(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning(exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_55(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", )
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_56(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("XXException occurredXX", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_57(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_58(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("EXCEPTION OCCURRED", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_59(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=False)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_60(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning(None, exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_61(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=None)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_62(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning(exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_63(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", )
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_64(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("XXException occurredXX", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_65(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_66(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("EXCEPTION OCCURRED", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_67(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=False)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_68(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = None
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_69(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(None, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_70(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=None)
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_71(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_72(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, )
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_73(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get(None))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_74(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("XXmap_locationXX"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_75(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("MAP_LOCATION"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_76(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is not None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_77(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = None
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_78(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            None,
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_79(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            None,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_80(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=None,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_81(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_82(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_83(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_84(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "XXLoaded checkpoint without metadata; falling back to legacy deserializer.XX",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_85(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_86(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "LOADED CHECKPOINT WITHOUT METADATA; FALLING BACK TO LEGACY DESERIALIZER.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_87(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=3,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_88(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore or legacy_rng:
            with suppress(Exception):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_89(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(None):
                _restore_rng(legacy_rng)
        return legacy_state


def x_load_checkpoint__mutmut_90(
    path: str | os.PathLike[str],
    device: str = "cpu",
    *,
    restore_rng: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Legacy wrapper that adapts return values from the canonical loader."""

    _warnings.warn(
        "src.utils.checkpoint.load_checkpoint is deprecated; use "
        "codex_ml.utils.checkpoint_core.load_checkpoint instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if _canonical_load_checkpoint is None:
        raise ImportError("load_checkpoint is unavailable; install codex-ml checkpoint extras")

    restore = restore_rng if restore_rng is not None else True
    if "map_location" in kwargs and device and device != "cpu":
        _warnings.warn(
            "Both device and map_location specified; preferring explicit map_location.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif "map_location" not in kwargs and device:
        kwargs["map_location"] = device

    try:
        state, _meta = _canonical_load_checkpoint(path, restore_rng=restore, **kwargs)
        return state
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        fallback = _load_legacy_checkpoint_payload(path, map_location=kwargs.get("map_location"))
        if fallback is None:
            raise
        legacy_state, legacy_rng = fallback
        _warnings.warn(
            "Loaded checkpoint without metadata; falling back to legacy deserializer.",
            RuntimeWarning,
            stacklevel=2,
        )
        if restore and legacy_rng:
            with suppress(Exception):
                _restore_rng(None)
        return legacy_state

x_load_checkpoint__mutmut_mutants : ClassVar[MutantDict] = {
'x_load_checkpoint__mutmut_1': x_load_checkpoint__mutmut_1, 
    'x_load_checkpoint__mutmut_2': x_load_checkpoint__mutmut_2, 
    'x_load_checkpoint__mutmut_3': x_load_checkpoint__mutmut_3, 
    'x_load_checkpoint__mutmut_4': x_load_checkpoint__mutmut_4, 
    'x_load_checkpoint__mutmut_5': x_load_checkpoint__mutmut_5, 
    'x_load_checkpoint__mutmut_6': x_load_checkpoint__mutmut_6, 
    'x_load_checkpoint__mutmut_7': x_load_checkpoint__mutmut_7, 
    'x_load_checkpoint__mutmut_8': x_load_checkpoint__mutmut_8, 
    'x_load_checkpoint__mutmut_9': x_load_checkpoint__mutmut_9, 
    'x_load_checkpoint__mutmut_10': x_load_checkpoint__mutmut_10, 
    'x_load_checkpoint__mutmut_11': x_load_checkpoint__mutmut_11, 
    'x_load_checkpoint__mutmut_12': x_load_checkpoint__mutmut_12, 
    'x_load_checkpoint__mutmut_13': x_load_checkpoint__mutmut_13, 
    'x_load_checkpoint__mutmut_14': x_load_checkpoint__mutmut_14, 
    'x_load_checkpoint__mutmut_15': x_load_checkpoint__mutmut_15, 
    'x_load_checkpoint__mutmut_16': x_load_checkpoint__mutmut_16, 
    'x_load_checkpoint__mutmut_17': x_load_checkpoint__mutmut_17, 
    'x_load_checkpoint__mutmut_18': x_load_checkpoint__mutmut_18, 
    'x_load_checkpoint__mutmut_19': x_load_checkpoint__mutmut_19, 
    'x_load_checkpoint__mutmut_20': x_load_checkpoint__mutmut_20, 
    'x_load_checkpoint__mutmut_21': x_load_checkpoint__mutmut_21, 
    'x_load_checkpoint__mutmut_22': x_load_checkpoint__mutmut_22, 
    'x_load_checkpoint__mutmut_23': x_load_checkpoint__mutmut_23, 
    'x_load_checkpoint__mutmut_24': x_load_checkpoint__mutmut_24, 
    'x_load_checkpoint__mutmut_25': x_load_checkpoint__mutmut_25, 
    'x_load_checkpoint__mutmut_26': x_load_checkpoint__mutmut_26, 
    'x_load_checkpoint__mutmut_27': x_load_checkpoint__mutmut_27, 
    'x_load_checkpoint__mutmut_28': x_load_checkpoint__mutmut_28, 
    'x_load_checkpoint__mutmut_29': x_load_checkpoint__mutmut_29, 
    'x_load_checkpoint__mutmut_30': x_load_checkpoint__mutmut_30, 
    'x_load_checkpoint__mutmut_31': x_load_checkpoint__mutmut_31, 
    'x_load_checkpoint__mutmut_32': x_load_checkpoint__mutmut_32, 
    'x_load_checkpoint__mutmut_33': x_load_checkpoint__mutmut_33, 
    'x_load_checkpoint__mutmut_34': x_load_checkpoint__mutmut_34, 
    'x_load_checkpoint__mutmut_35': x_load_checkpoint__mutmut_35, 
    'x_load_checkpoint__mutmut_36': x_load_checkpoint__mutmut_36, 
    'x_load_checkpoint__mutmut_37': x_load_checkpoint__mutmut_37, 
    'x_load_checkpoint__mutmut_38': x_load_checkpoint__mutmut_38, 
    'x_load_checkpoint__mutmut_39': x_load_checkpoint__mutmut_39, 
    'x_load_checkpoint__mutmut_40': x_load_checkpoint__mutmut_40, 
    'x_load_checkpoint__mutmut_41': x_load_checkpoint__mutmut_41, 
    'x_load_checkpoint__mutmut_42': x_load_checkpoint__mutmut_42, 
    'x_load_checkpoint__mutmut_43': x_load_checkpoint__mutmut_43, 
    'x_load_checkpoint__mutmut_44': x_load_checkpoint__mutmut_44, 
    'x_load_checkpoint__mutmut_45': x_load_checkpoint__mutmut_45, 
    'x_load_checkpoint__mutmut_46': x_load_checkpoint__mutmut_46, 
    'x_load_checkpoint__mutmut_47': x_load_checkpoint__mutmut_47, 
    'x_load_checkpoint__mutmut_48': x_load_checkpoint__mutmut_48, 
    'x_load_checkpoint__mutmut_49': x_load_checkpoint__mutmut_49, 
    'x_load_checkpoint__mutmut_50': x_load_checkpoint__mutmut_50, 
    'x_load_checkpoint__mutmut_51': x_load_checkpoint__mutmut_51, 
    'x_load_checkpoint__mutmut_52': x_load_checkpoint__mutmut_52, 
    'x_load_checkpoint__mutmut_53': x_load_checkpoint__mutmut_53, 
    'x_load_checkpoint__mutmut_54': x_load_checkpoint__mutmut_54, 
    'x_load_checkpoint__mutmut_55': x_load_checkpoint__mutmut_55, 
    'x_load_checkpoint__mutmut_56': x_load_checkpoint__mutmut_56, 
    'x_load_checkpoint__mutmut_57': x_load_checkpoint__mutmut_57, 
    'x_load_checkpoint__mutmut_58': x_load_checkpoint__mutmut_58, 
    'x_load_checkpoint__mutmut_59': x_load_checkpoint__mutmut_59, 
    'x_load_checkpoint__mutmut_60': x_load_checkpoint__mutmut_60, 
    'x_load_checkpoint__mutmut_61': x_load_checkpoint__mutmut_61, 
    'x_load_checkpoint__mutmut_62': x_load_checkpoint__mutmut_62, 
    'x_load_checkpoint__mutmut_63': x_load_checkpoint__mutmut_63, 
    'x_load_checkpoint__mutmut_64': x_load_checkpoint__mutmut_64, 
    'x_load_checkpoint__mutmut_65': x_load_checkpoint__mutmut_65, 
    'x_load_checkpoint__mutmut_66': x_load_checkpoint__mutmut_66, 
    'x_load_checkpoint__mutmut_67': x_load_checkpoint__mutmut_67, 
    'x_load_checkpoint__mutmut_68': x_load_checkpoint__mutmut_68, 
    'x_load_checkpoint__mutmut_69': x_load_checkpoint__mutmut_69, 
    'x_load_checkpoint__mutmut_70': x_load_checkpoint__mutmut_70, 
    'x_load_checkpoint__mutmut_71': x_load_checkpoint__mutmut_71, 
    'x_load_checkpoint__mutmut_72': x_load_checkpoint__mutmut_72, 
    'x_load_checkpoint__mutmut_73': x_load_checkpoint__mutmut_73, 
    'x_load_checkpoint__mutmut_74': x_load_checkpoint__mutmut_74, 
    'x_load_checkpoint__mutmut_75': x_load_checkpoint__mutmut_75, 
    'x_load_checkpoint__mutmut_76': x_load_checkpoint__mutmut_76, 
    'x_load_checkpoint__mutmut_77': x_load_checkpoint__mutmut_77, 
    'x_load_checkpoint__mutmut_78': x_load_checkpoint__mutmut_78, 
    'x_load_checkpoint__mutmut_79': x_load_checkpoint__mutmut_79, 
    'x_load_checkpoint__mutmut_80': x_load_checkpoint__mutmut_80, 
    'x_load_checkpoint__mutmut_81': x_load_checkpoint__mutmut_81, 
    'x_load_checkpoint__mutmut_82': x_load_checkpoint__mutmut_82, 
    'x_load_checkpoint__mutmut_83': x_load_checkpoint__mutmut_83, 
    'x_load_checkpoint__mutmut_84': x_load_checkpoint__mutmut_84, 
    'x_load_checkpoint__mutmut_85': x_load_checkpoint__mutmut_85, 
    'x_load_checkpoint__mutmut_86': x_load_checkpoint__mutmut_86, 
    'x_load_checkpoint__mutmut_87': x_load_checkpoint__mutmut_87, 
    'x_load_checkpoint__mutmut_88': x_load_checkpoint__mutmut_88, 
    'x_load_checkpoint__mutmut_89': x_load_checkpoint__mutmut_89, 
    'x_load_checkpoint__mutmut_90': x_load_checkpoint__mutmut_90
}

def load_checkpoint(*args, **kwargs):
    result = _mutmut_trampoline(x_load_checkpoint__mutmut_orig, x_load_checkpoint__mutmut_mutants, args, kwargs)
    return result 

load_checkpoint.__signature__ = _mutmut_signature(x_load_checkpoint__mutmut_orig)
x_load_checkpoint__mutmut_orig.__name__ = 'x_load_checkpoint'


__all__ = ["CheckpointManager", "save_checkpoint", "load_checkpoint"]


def x__load_legacy_checkpoint_payload__mutmut_orig(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_1(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = ""
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_2(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_3(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = None
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_4(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(None, map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_5(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=None)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_6(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_7(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), )
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_8(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(None), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_9(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning(None, exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_10(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=None)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_11(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning(exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_12(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", )
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_13(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("XXException occurredXX", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_14(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_15(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("EXCEPTION OCCURRED", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_16(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=False)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_17(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning(None, exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_18(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=None)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_19(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning(exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_20(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", )
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_21(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("XXException occurredXX", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_22(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_23(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("EXCEPTION OCCURRED", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_24(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=False)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_25(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = ""
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_26(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = None
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_27(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is not None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_28(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = None
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_29(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(None, use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_30(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=None)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_31(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_32(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), )
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_33(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(None), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_34(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=False)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_35(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning(None, exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_36(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=None)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_37(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning(exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_38(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", )
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_39(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("XXException occurredXX", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_40(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_41(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("EXCEPTION OCCURRED", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_42(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=False)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_43(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning(None, exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_44(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=None)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_45(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning(exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_46(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", )
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_47(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("XXException occurredXX", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_48(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_49(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("EXCEPTION OCCURRED", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_50(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=False)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_51(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_52(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = None

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_53(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate or "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_54(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "XXstateXX" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_55(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "STATE" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_56(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" not in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_57(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "XXmetaXX" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_58(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "META" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_59(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" not in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_60(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = None
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_61(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(None)
    rng_state = state.pop("_rng", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_62(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = None
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_63(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop(None, None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_64(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop(None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_65(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_rng", )
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_66(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("XX_rngXX", None)
    return state, rng_state


def x__load_legacy_checkpoint_payload__mutmut_67(
    path: str | os.PathLike[str], *, map_location: Any | None
) -> tuple[dict[str, Any], Any] | None:
    """Best-effort loader for historical ``torch.save`` checkpoints."""

    candidate: Mapping[str, Any] | None = None
    if _torch is not None:
        try:
            loaded = _torch_load(str(path), map_location=map_location)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            loaded = None
        if isinstance(loaded, Mapping):
            candidate = loaded
    if candidate is None:
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from utils.safe_pickle import safe_pickle_load
            loaded = safe_pickle_load(str(path), use_restricted_unpickler=True)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return None
        if not isinstance(loaded, Mapping):
            return None
        candidate = loaded

    if "state" in candidate and "meta" in candidate:
        return None

    state = dict(candidate)
    rng_state = state.pop("_RNG", None)
    return state, rng_state

x__load_legacy_checkpoint_payload__mutmut_mutants : ClassVar[MutantDict] = {
'x__load_legacy_checkpoint_payload__mutmut_1': x__load_legacy_checkpoint_payload__mutmut_1, 
    'x__load_legacy_checkpoint_payload__mutmut_2': x__load_legacy_checkpoint_payload__mutmut_2, 
    'x__load_legacy_checkpoint_payload__mutmut_3': x__load_legacy_checkpoint_payload__mutmut_3, 
    'x__load_legacy_checkpoint_payload__mutmut_4': x__load_legacy_checkpoint_payload__mutmut_4, 
    'x__load_legacy_checkpoint_payload__mutmut_5': x__load_legacy_checkpoint_payload__mutmut_5, 
    'x__load_legacy_checkpoint_payload__mutmut_6': x__load_legacy_checkpoint_payload__mutmut_6, 
    'x__load_legacy_checkpoint_payload__mutmut_7': x__load_legacy_checkpoint_payload__mutmut_7, 
    'x__load_legacy_checkpoint_payload__mutmut_8': x__load_legacy_checkpoint_payload__mutmut_8, 
    'x__load_legacy_checkpoint_payload__mutmut_9': x__load_legacy_checkpoint_payload__mutmut_9, 
    'x__load_legacy_checkpoint_payload__mutmut_10': x__load_legacy_checkpoint_payload__mutmut_10, 
    'x__load_legacy_checkpoint_payload__mutmut_11': x__load_legacy_checkpoint_payload__mutmut_11, 
    'x__load_legacy_checkpoint_payload__mutmut_12': x__load_legacy_checkpoint_payload__mutmut_12, 
    'x__load_legacy_checkpoint_payload__mutmut_13': x__load_legacy_checkpoint_payload__mutmut_13, 
    'x__load_legacy_checkpoint_payload__mutmut_14': x__load_legacy_checkpoint_payload__mutmut_14, 
    'x__load_legacy_checkpoint_payload__mutmut_15': x__load_legacy_checkpoint_payload__mutmut_15, 
    'x__load_legacy_checkpoint_payload__mutmut_16': x__load_legacy_checkpoint_payload__mutmut_16, 
    'x__load_legacy_checkpoint_payload__mutmut_17': x__load_legacy_checkpoint_payload__mutmut_17, 
    'x__load_legacy_checkpoint_payload__mutmut_18': x__load_legacy_checkpoint_payload__mutmut_18, 
    'x__load_legacy_checkpoint_payload__mutmut_19': x__load_legacy_checkpoint_payload__mutmut_19, 
    'x__load_legacy_checkpoint_payload__mutmut_20': x__load_legacy_checkpoint_payload__mutmut_20, 
    'x__load_legacy_checkpoint_payload__mutmut_21': x__load_legacy_checkpoint_payload__mutmut_21, 
    'x__load_legacy_checkpoint_payload__mutmut_22': x__load_legacy_checkpoint_payload__mutmut_22, 
    'x__load_legacy_checkpoint_payload__mutmut_23': x__load_legacy_checkpoint_payload__mutmut_23, 
    'x__load_legacy_checkpoint_payload__mutmut_24': x__load_legacy_checkpoint_payload__mutmut_24, 
    'x__load_legacy_checkpoint_payload__mutmut_25': x__load_legacy_checkpoint_payload__mutmut_25, 
    'x__load_legacy_checkpoint_payload__mutmut_26': x__load_legacy_checkpoint_payload__mutmut_26, 
    'x__load_legacy_checkpoint_payload__mutmut_27': x__load_legacy_checkpoint_payload__mutmut_27, 
    'x__load_legacy_checkpoint_payload__mutmut_28': x__load_legacy_checkpoint_payload__mutmut_28, 
    'x__load_legacy_checkpoint_payload__mutmut_29': x__load_legacy_checkpoint_payload__mutmut_29, 
    'x__load_legacy_checkpoint_payload__mutmut_30': x__load_legacy_checkpoint_payload__mutmut_30, 
    'x__load_legacy_checkpoint_payload__mutmut_31': x__load_legacy_checkpoint_payload__mutmut_31, 
    'x__load_legacy_checkpoint_payload__mutmut_32': x__load_legacy_checkpoint_payload__mutmut_32, 
    'x__load_legacy_checkpoint_payload__mutmut_33': x__load_legacy_checkpoint_payload__mutmut_33, 
    'x__load_legacy_checkpoint_payload__mutmut_34': x__load_legacy_checkpoint_payload__mutmut_34, 
    'x__load_legacy_checkpoint_payload__mutmut_35': x__load_legacy_checkpoint_payload__mutmut_35, 
    'x__load_legacy_checkpoint_payload__mutmut_36': x__load_legacy_checkpoint_payload__mutmut_36, 
    'x__load_legacy_checkpoint_payload__mutmut_37': x__load_legacy_checkpoint_payload__mutmut_37, 
    'x__load_legacy_checkpoint_payload__mutmut_38': x__load_legacy_checkpoint_payload__mutmut_38, 
    'x__load_legacy_checkpoint_payload__mutmut_39': x__load_legacy_checkpoint_payload__mutmut_39, 
    'x__load_legacy_checkpoint_payload__mutmut_40': x__load_legacy_checkpoint_payload__mutmut_40, 
    'x__load_legacy_checkpoint_payload__mutmut_41': x__load_legacy_checkpoint_payload__mutmut_41, 
    'x__load_legacy_checkpoint_payload__mutmut_42': x__load_legacy_checkpoint_payload__mutmut_42, 
    'x__load_legacy_checkpoint_payload__mutmut_43': x__load_legacy_checkpoint_payload__mutmut_43, 
    'x__load_legacy_checkpoint_payload__mutmut_44': x__load_legacy_checkpoint_payload__mutmut_44, 
    'x__load_legacy_checkpoint_payload__mutmut_45': x__load_legacy_checkpoint_payload__mutmut_45, 
    'x__load_legacy_checkpoint_payload__mutmut_46': x__load_legacy_checkpoint_payload__mutmut_46, 
    'x__load_legacy_checkpoint_payload__mutmut_47': x__load_legacy_checkpoint_payload__mutmut_47, 
    'x__load_legacy_checkpoint_payload__mutmut_48': x__load_legacy_checkpoint_payload__mutmut_48, 
    'x__load_legacy_checkpoint_payload__mutmut_49': x__load_legacy_checkpoint_payload__mutmut_49, 
    'x__load_legacy_checkpoint_payload__mutmut_50': x__load_legacy_checkpoint_payload__mutmut_50, 
    'x__load_legacy_checkpoint_payload__mutmut_51': x__load_legacy_checkpoint_payload__mutmut_51, 
    'x__load_legacy_checkpoint_payload__mutmut_52': x__load_legacy_checkpoint_payload__mutmut_52, 
    'x__load_legacy_checkpoint_payload__mutmut_53': x__load_legacy_checkpoint_payload__mutmut_53, 
    'x__load_legacy_checkpoint_payload__mutmut_54': x__load_legacy_checkpoint_payload__mutmut_54, 
    'x__load_legacy_checkpoint_payload__mutmut_55': x__load_legacy_checkpoint_payload__mutmut_55, 
    'x__load_legacy_checkpoint_payload__mutmut_56': x__load_legacy_checkpoint_payload__mutmut_56, 
    'x__load_legacy_checkpoint_payload__mutmut_57': x__load_legacy_checkpoint_payload__mutmut_57, 
    'x__load_legacy_checkpoint_payload__mutmut_58': x__load_legacy_checkpoint_payload__mutmut_58, 
    'x__load_legacy_checkpoint_payload__mutmut_59': x__load_legacy_checkpoint_payload__mutmut_59, 
    'x__load_legacy_checkpoint_payload__mutmut_60': x__load_legacy_checkpoint_payload__mutmut_60, 
    'x__load_legacy_checkpoint_payload__mutmut_61': x__load_legacy_checkpoint_payload__mutmut_61, 
    'x__load_legacy_checkpoint_payload__mutmut_62': x__load_legacy_checkpoint_payload__mutmut_62, 
    'x__load_legacy_checkpoint_payload__mutmut_63': x__load_legacy_checkpoint_payload__mutmut_63, 
    'x__load_legacy_checkpoint_payload__mutmut_64': x__load_legacy_checkpoint_payload__mutmut_64, 
    'x__load_legacy_checkpoint_payload__mutmut_65': x__load_legacy_checkpoint_payload__mutmut_65, 
    'x__load_legacy_checkpoint_payload__mutmut_66': x__load_legacy_checkpoint_payload__mutmut_66, 
    'x__load_legacy_checkpoint_payload__mutmut_67': x__load_legacy_checkpoint_payload__mutmut_67
}

def _load_legacy_checkpoint_payload(*args, **kwargs):
    result = _mutmut_trampoline(x__load_legacy_checkpoint_payload__mutmut_orig, x__load_legacy_checkpoint_payload__mutmut_mutants, args, kwargs)
    return result 

_load_legacy_checkpoint_payload.__signature__ = _mutmut_signature(x__load_legacy_checkpoint_payload__mutmut_orig)
x__load_legacy_checkpoint_payload__mutmut_orig.__name__ = 'x__load_legacy_checkpoint_payload'
