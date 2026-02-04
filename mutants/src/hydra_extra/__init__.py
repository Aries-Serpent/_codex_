"""Codex-provided stub for Hydra's ``hydra.extra`` setuptools plugin.

The real plugin ships with some Hydra distributions, but offline or minimal
installations used in CI often omit it which breaks implicit imports triggered
by Hydra's auto-discovery.  This stub keeps the import resolvable while clearly
signalling that the implementation is a lightweight placeholder.
"""

from __future__ import annotations

import sys
import types
from dataclasses import dataclass
from typing import Optional

__all__ = ["HydraExtraStatus", "ensure", "ensure_registered", "status", "__version__"]

__version__ = "0.1.0.dev0"
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


@dataclass(frozen=True)
class HydraExtraStatus:
    """Expose the state of the shim so callers can introspect behaviour."""

    available: bool
    reason: Optional[str] = None


def x__build_stub_module__mutmut_orig() -> types.ModuleType:
    module = types.ModuleType("hydra.extra")
    module.__doc__ = (
        "Codex stub for the hydra.extra plugin. The full plugin is unavailable, "
        "so the shim exports minimal markers only."
    )
    module.AVAILABLE = False  # type: ignore[attr-defined]
    module.STUB = True  # type: ignore[attr-defined]
    return module


def x__build_stub_module__mutmut_1() -> types.ModuleType:
    module = None
    module.__doc__ = (
        "Codex stub for the hydra.extra plugin. The full plugin is unavailable, "
        "so the shim exports minimal markers only."
    )
    module.AVAILABLE = False  # type: ignore[attr-defined]
    module.STUB = True  # type: ignore[attr-defined]
    return module


def x__build_stub_module__mutmut_2() -> types.ModuleType:
    module = types.ModuleType(None)
    module.__doc__ = (
        "Codex stub for the hydra.extra plugin. The full plugin is unavailable, "
        "so the shim exports minimal markers only."
    )
    module.AVAILABLE = False  # type: ignore[attr-defined]
    module.STUB = True  # type: ignore[attr-defined]
    return module


def x__build_stub_module__mutmut_3() -> types.ModuleType:
    module = types.ModuleType("XXhydra.extraXX")
    module.__doc__ = (
        "Codex stub for the hydra.extra plugin. The full plugin is unavailable, "
        "so the shim exports minimal markers only."
    )
    module.AVAILABLE = False  # type: ignore[attr-defined]
    module.STUB = True  # type: ignore[attr-defined]
    return module


def x__build_stub_module__mutmut_4() -> types.ModuleType:
    module = types.ModuleType("HYDRA.EXTRA")
    module.__doc__ = (
        "Codex stub for the hydra.extra plugin. The full plugin is unavailable, "
        "so the shim exports minimal markers only."
    )
    module.AVAILABLE = False  # type: ignore[attr-defined]
    module.STUB = True  # type: ignore[attr-defined]
    return module


def x__build_stub_module__mutmut_5() -> types.ModuleType:
    module = types.ModuleType("hydra.extra")
    module.__doc__ = None
    module.AVAILABLE = False  # type: ignore[attr-defined]
    module.STUB = True  # type: ignore[attr-defined]
    return module


def x__build_stub_module__mutmut_6() -> types.ModuleType:
    module = types.ModuleType("hydra.extra")
    module.__doc__ = (
        "XXCodex stub for the hydra.extra plugin. The full plugin is unavailable, XX"
        "so the shim exports minimal markers only."
    )
    module.AVAILABLE = False  # type: ignore[attr-defined]
    module.STUB = True  # type: ignore[attr-defined]
    return module


def x__build_stub_module__mutmut_7() -> types.ModuleType:
    module = types.ModuleType("hydra.extra")
    module.__doc__ = (
        "codex stub for the hydra.extra plugin. the full plugin is unavailable, "
        "so the shim exports minimal markers only."
    )
    module.AVAILABLE = False  # type: ignore[attr-defined]
    module.STUB = True  # type: ignore[attr-defined]
    return module


def x__build_stub_module__mutmut_8() -> types.ModuleType:
    module = types.ModuleType("hydra.extra")
    module.__doc__ = (
        "CODEX STUB FOR THE HYDRA.EXTRA PLUGIN. THE FULL PLUGIN IS UNAVAILABLE, "
        "so the shim exports minimal markers only."
    )
    module.AVAILABLE = False  # type: ignore[attr-defined]
    module.STUB = True  # type: ignore[attr-defined]
    return module


def x__build_stub_module__mutmut_9() -> types.ModuleType:
    module = types.ModuleType("hydra.extra")
    module.__doc__ = (
        "Codex stub for the hydra.extra plugin. The full plugin is unavailable, "
        "XXso the shim exports minimal markers only.XX"
    )
    module.AVAILABLE = False  # type: ignore[attr-defined]
    module.STUB = True  # type: ignore[attr-defined]
    return module


def x__build_stub_module__mutmut_10() -> types.ModuleType:
    module = types.ModuleType("hydra.extra")
    module.__doc__ = (
        "Codex stub for the hydra.extra plugin. The full plugin is unavailable, "
        "SO THE SHIM EXPORTS MINIMAL MARKERS ONLY."
    )
    module.AVAILABLE = False  # type: ignore[attr-defined]
    module.STUB = True  # type: ignore[attr-defined]
    return module


def x__build_stub_module__mutmut_11() -> types.ModuleType:
    module = types.ModuleType("hydra.extra")
    module.__doc__ = (
        "Codex stub for the hydra.extra plugin. The full plugin is unavailable, "
        "so the shim exports minimal markers only."
    )
    module.AVAILABLE = None  # type: ignore[attr-defined]
    module.STUB = True  # type: ignore[attr-defined]
    return module


def x__build_stub_module__mutmut_12() -> types.ModuleType:
    module = types.ModuleType("hydra.extra")
    module.__doc__ = (
        "Codex stub for the hydra.extra plugin. The full plugin is unavailable, "
        "so the shim exports minimal markers only."
    )
    module.AVAILABLE = True  # type: ignore[attr-defined]
    module.STUB = True  # type: ignore[attr-defined]
    return module


def x__build_stub_module__mutmut_13() -> types.ModuleType:
    module = types.ModuleType("hydra.extra")
    module.__doc__ = (
        "Codex stub for the hydra.extra plugin. The full plugin is unavailable, "
        "so the shim exports minimal markers only."
    )
    module.AVAILABLE = False  # type: ignore[attr-defined]
    module.STUB = None  # type: ignore[attr-defined]
    return module


def x__build_stub_module__mutmut_14() -> types.ModuleType:
    module = types.ModuleType("hydra.extra")
    module.__doc__ = (
        "Codex stub for the hydra.extra plugin. The full plugin is unavailable, "
        "so the shim exports minimal markers only."
    )
    module.AVAILABLE = False  # type: ignore[attr-defined]
    module.STUB = False  # type: ignore[attr-defined]
    return module

x__build_stub_module__mutmut_mutants : ClassVar[MutantDict] = {
'x__build_stub_module__mutmut_1': x__build_stub_module__mutmut_1, 
    'x__build_stub_module__mutmut_2': x__build_stub_module__mutmut_2, 
    'x__build_stub_module__mutmut_3': x__build_stub_module__mutmut_3, 
    'x__build_stub_module__mutmut_4': x__build_stub_module__mutmut_4, 
    'x__build_stub_module__mutmut_5': x__build_stub_module__mutmut_5, 
    'x__build_stub_module__mutmut_6': x__build_stub_module__mutmut_6, 
    'x__build_stub_module__mutmut_7': x__build_stub_module__mutmut_7, 
    'x__build_stub_module__mutmut_8': x__build_stub_module__mutmut_8, 
    'x__build_stub_module__mutmut_9': x__build_stub_module__mutmut_9, 
    'x__build_stub_module__mutmut_10': x__build_stub_module__mutmut_10, 
    'x__build_stub_module__mutmut_11': x__build_stub_module__mutmut_11, 
    'x__build_stub_module__mutmut_12': x__build_stub_module__mutmut_12, 
    'x__build_stub_module__mutmut_13': x__build_stub_module__mutmut_13, 
    'x__build_stub_module__mutmut_14': x__build_stub_module__mutmut_14
}

def _build_stub_module(*args, **kwargs):
    result = _mutmut_trampoline(x__build_stub_module__mutmut_orig, x__build_stub_module__mutmut_mutants, args, kwargs)
    return result 

_build_stub_module.__signature__ = _mutmut_signature(x__build_stub_module__mutmut_orig)
x__build_stub_module__mutmut_orig.__name__ = 'x__build_stub_module'


def x_ensure_registered__mutmut_orig() -> types.ModuleType:
    """Guarantee that ``hydra.extra`` can be imported."""

    existing = sys.modules.get("hydra.extra")
    if isinstance(existing, types.ModuleType):
        return existing
    module = _build_stub_module()
    sys.modules["hydra.extra"] = module
    return module


def x_ensure_registered__mutmut_1() -> types.ModuleType:
    """Guarantee that ``hydra.extra`` can be imported."""

    existing = None
    if isinstance(existing, types.ModuleType):
        return existing
    module = _build_stub_module()
    sys.modules["hydra.extra"] = module
    return module


def x_ensure_registered__mutmut_2() -> types.ModuleType:
    """Guarantee that ``hydra.extra`` can be imported."""

    existing = sys.modules.get(None)
    if isinstance(existing, types.ModuleType):
        return existing
    module = _build_stub_module()
    sys.modules["hydra.extra"] = module
    return module


def x_ensure_registered__mutmut_3() -> types.ModuleType:
    """Guarantee that ``hydra.extra`` can be imported."""

    existing = sys.modules.get("XXhydra.extraXX")
    if isinstance(existing, types.ModuleType):
        return existing
    module = _build_stub_module()
    sys.modules["hydra.extra"] = module
    return module


def x_ensure_registered__mutmut_4() -> types.ModuleType:
    """Guarantee that ``hydra.extra`` can be imported."""

    existing = sys.modules.get("HYDRA.EXTRA")
    if isinstance(existing, types.ModuleType):
        return existing
    module = _build_stub_module()
    sys.modules["hydra.extra"] = module
    return module


def x_ensure_registered__mutmut_5() -> types.ModuleType:
    """Guarantee that ``hydra.extra`` can be imported."""

    existing = sys.modules.get("hydra.extra")
    if isinstance(existing, types.ModuleType):
        return existing
    module = None
    sys.modules["hydra.extra"] = module
    return module


def x_ensure_registered__mutmut_6() -> types.ModuleType:
    """Guarantee that ``hydra.extra`` can be imported."""

    existing = sys.modules.get("hydra.extra")
    if isinstance(existing, types.ModuleType):
        return existing
    module = _build_stub_module()
    sys.modules["hydra.extra"] = None
    return module


def x_ensure_registered__mutmut_7() -> types.ModuleType:
    """Guarantee that ``hydra.extra`` can be imported."""

    existing = sys.modules.get("hydra.extra")
    if isinstance(existing, types.ModuleType):
        return existing
    module = _build_stub_module()
    sys.modules["XXhydra.extraXX"] = module
    return module


def x_ensure_registered__mutmut_8() -> types.ModuleType:
    """Guarantee that ``hydra.extra`` can be imported."""

    existing = sys.modules.get("hydra.extra")
    if isinstance(existing, types.ModuleType):
        return existing
    module = _build_stub_module()
    sys.modules["HYDRA.EXTRA"] = module
    return module

x_ensure_registered__mutmut_mutants : ClassVar[MutantDict] = {
'x_ensure_registered__mutmut_1': x_ensure_registered__mutmut_1, 
    'x_ensure_registered__mutmut_2': x_ensure_registered__mutmut_2, 
    'x_ensure_registered__mutmut_3': x_ensure_registered__mutmut_3, 
    'x_ensure_registered__mutmut_4': x_ensure_registered__mutmut_4, 
    'x_ensure_registered__mutmut_5': x_ensure_registered__mutmut_5, 
    'x_ensure_registered__mutmut_6': x_ensure_registered__mutmut_6, 
    'x_ensure_registered__mutmut_7': x_ensure_registered__mutmut_7, 
    'x_ensure_registered__mutmut_8': x_ensure_registered__mutmut_8
}

def ensure_registered(*args, **kwargs):
    result = _mutmut_trampoline(x_ensure_registered__mutmut_orig, x_ensure_registered__mutmut_mutants, args, kwargs)
    return result 

ensure_registered.__signature__ = _mutmut_signature(x_ensure_registered__mutmut_orig)
x_ensure_registered__mutmut_orig.__name__ = 'x_ensure_registered'


def ensure() -> types.ModuleType:
    """Alias for :func:`ensure_registered` to mirror the real plugin."""

    return ensure_registered()


def x_status__mutmut_orig() -> HydraExtraStatus:
    module = sys.modules.get("hydra.extra")
    if isinstance(module, types.ModuleType) and getattr(module, "STUB", False):
        return HydraExtraStatus(available=False, reason="codex-stub")
    return HydraExtraStatus(available=True)


def x_status__mutmut_1() -> HydraExtraStatus:
    module = None
    if isinstance(module, types.ModuleType) and getattr(module, "STUB", False):
        return HydraExtraStatus(available=False, reason="codex-stub")
    return HydraExtraStatus(available=True)


def x_status__mutmut_2() -> HydraExtraStatus:
    module = sys.modules.get(None)
    if isinstance(module, types.ModuleType) and getattr(module, "STUB", False):
        return HydraExtraStatus(available=False, reason="codex-stub")
    return HydraExtraStatus(available=True)


def x_status__mutmut_3() -> HydraExtraStatus:
    module = sys.modules.get("XXhydra.extraXX")
    if isinstance(module, types.ModuleType) and getattr(module, "STUB", False):
        return HydraExtraStatus(available=False, reason="codex-stub")
    return HydraExtraStatus(available=True)


def x_status__mutmut_4() -> HydraExtraStatus:
    module = sys.modules.get("HYDRA.EXTRA")
    if isinstance(module, types.ModuleType) and getattr(module, "STUB", False):
        return HydraExtraStatus(available=False, reason="codex-stub")
    return HydraExtraStatus(available=True)


def x_status__mutmut_5() -> HydraExtraStatus:
    module = sys.modules.get("hydra.extra")
    if isinstance(module, types.ModuleType) or getattr(module, "STUB", False):
        return HydraExtraStatus(available=False, reason="codex-stub")
    return HydraExtraStatus(available=True)


def x_status__mutmut_6() -> HydraExtraStatus:
    module = sys.modules.get("hydra.extra")
    if isinstance(module, types.ModuleType) and getattr(None, "STUB", False):
        return HydraExtraStatus(available=False, reason="codex-stub")
    return HydraExtraStatus(available=True)


def x_status__mutmut_7() -> HydraExtraStatus:
    module = sys.modules.get("hydra.extra")
    if isinstance(module, types.ModuleType) and getattr(module, None, False):
        return HydraExtraStatus(available=False, reason="codex-stub")
    return HydraExtraStatus(available=True)


def x_status__mutmut_8() -> HydraExtraStatus:
    module = sys.modules.get("hydra.extra")
    if isinstance(module, types.ModuleType) and getattr(module, "STUB", None):
        return HydraExtraStatus(available=False, reason="codex-stub")
    return HydraExtraStatus(available=True)


def x_status__mutmut_9() -> HydraExtraStatus:
    module = sys.modules.get("hydra.extra")
    if isinstance(module, types.ModuleType) and getattr("STUB", False):
        return HydraExtraStatus(available=False, reason="codex-stub")
    return HydraExtraStatus(available=True)


def x_status__mutmut_10() -> HydraExtraStatus:
    module = sys.modules.get("hydra.extra")
    if isinstance(module, types.ModuleType) and getattr(module, False):
        return HydraExtraStatus(available=False, reason="codex-stub")
    return HydraExtraStatus(available=True)


def x_status__mutmut_11() -> HydraExtraStatus:
    module = sys.modules.get("hydra.extra")
    if isinstance(module, types.ModuleType) and getattr(module, "STUB", ):
        return HydraExtraStatus(available=False, reason="codex-stub")
    return HydraExtraStatus(available=True)


def x_status__mutmut_12() -> HydraExtraStatus:
    module = sys.modules.get("hydra.extra")
    if isinstance(module, types.ModuleType) and getattr(module, "XXSTUBXX", False):
        return HydraExtraStatus(available=False, reason="codex-stub")
    return HydraExtraStatus(available=True)


def x_status__mutmut_13() -> HydraExtraStatus:
    module = sys.modules.get("hydra.extra")
    if isinstance(module, types.ModuleType) and getattr(module, "stub", False):
        return HydraExtraStatus(available=False, reason="codex-stub")
    return HydraExtraStatus(available=True)


def x_status__mutmut_14() -> HydraExtraStatus:
    module = sys.modules.get("hydra.extra")
    if isinstance(module, types.ModuleType) and getattr(module, "STUB", True):
        return HydraExtraStatus(available=False, reason="codex-stub")
    return HydraExtraStatus(available=True)


def x_status__mutmut_15() -> HydraExtraStatus:
    module = sys.modules.get("hydra.extra")
    if isinstance(module, types.ModuleType) and getattr(module, "STUB", False):
        return HydraExtraStatus(available=None, reason="codex-stub")
    return HydraExtraStatus(available=True)


def x_status__mutmut_16() -> HydraExtraStatus:
    module = sys.modules.get("hydra.extra")
    if isinstance(module, types.ModuleType) and getattr(module, "STUB", False):
        return HydraExtraStatus(available=False, reason=None)
    return HydraExtraStatus(available=True)


def x_status__mutmut_17() -> HydraExtraStatus:
    module = sys.modules.get("hydra.extra")
    if isinstance(module, types.ModuleType) and getattr(module, "STUB", False):
        return HydraExtraStatus(reason="codex-stub")
    return HydraExtraStatus(available=True)


def x_status__mutmut_18() -> HydraExtraStatus:
    module = sys.modules.get("hydra.extra")
    if isinstance(module, types.ModuleType) and getattr(module, "STUB", False):
        return HydraExtraStatus(available=False, )
    return HydraExtraStatus(available=True)


def x_status__mutmut_19() -> HydraExtraStatus:
    module = sys.modules.get("hydra.extra")
    if isinstance(module, types.ModuleType) and getattr(module, "STUB", False):
        return HydraExtraStatus(available=True, reason="codex-stub")
    return HydraExtraStatus(available=True)


def x_status__mutmut_20() -> HydraExtraStatus:
    module = sys.modules.get("hydra.extra")
    if isinstance(module, types.ModuleType) and getattr(module, "STUB", False):
        return HydraExtraStatus(available=False, reason="XXcodex-stubXX")
    return HydraExtraStatus(available=True)


def x_status__mutmut_21() -> HydraExtraStatus:
    module = sys.modules.get("hydra.extra")
    if isinstance(module, types.ModuleType) and getattr(module, "STUB", False):
        return HydraExtraStatus(available=False, reason="CODEX-STUB")
    return HydraExtraStatus(available=True)


def x_status__mutmut_22() -> HydraExtraStatus:
    module = sys.modules.get("hydra.extra")
    if isinstance(module, types.ModuleType) and getattr(module, "STUB", False):
        return HydraExtraStatus(available=False, reason="codex-stub")
    return HydraExtraStatus(available=None)


def x_status__mutmut_23() -> HydraExtraStatus:
    module = sys.modules.get("hydra.extra")
    if isinstance(module, types.ModuleType) and getattr(module, "STUB", False):
        return HydraExtraStatus(available=False, reason="codex-stub")
    return HydraExtraStatus(available=False)

x_status__mutmut_mutants : ClassVar[MutantDict] = {
'x_status__mutmut_1': x_status__mutmut_1, 
    'x_status__mutmut_2': x_status__mutmut_2, 
    'x_status__mutmut_3': x_status__mutmut_3, 
    'x_status__mutmut_4': x_status__mutmut_4, 
    'x_status__mutmut_5': x_status__mutmut_5, 
    'x_status__mutmut_6': x_status__mutmut_6, 
    'x_status__mutmut_7': x_status__mutmut_7, 
    'x_status__mutmut_8': x_status__mutmut_8, 
    'x_status__mutmut_9': x_status__mutmut_9, 
    'x_status__mutmut_10': x_status__mutmut_10, 
    'x_status__mutmut_11': x_status__mutmut_11, 
    'x_status__mutmut_12': x_status__mutmut_12, 
    'x_status__mutmut_13': x_status__mutmut_13, 
    'x_status__mutmut_14': x_status__mutmut_14, 
    'x_status__mutmut_15': x_status__mutmut_15, 
    'x_status__mutmut_16': x_status__mutmut_16, 
    'x_status__mutmut_17': x_status__mutmut_17, 
    'x_status__mutmut_18': x_status__mutmut_18, 
    'x_status__mutmut_19': x_status__mutmut_19, 
    'x_status__mutmut_20': x_status__mutmut_20, 
    'x_status__mutmut_21': x_status__mutmut_21, 
    'x_status__mutmut_22': x_status__mutmut_22, 
    'x_status__mutmut_23': x_status__mutmut_23
}

def status(*args, **kwargs):
    result = _mutmut_trampoline(x_status__mutmut_orig, x_status__mutmut_mutants, args, kwargs)
    return result 

status.__signature__ = _mutmut_signature(x_status__mutmut_orig)
x_status__mutmut_orig.__name__ = 'x_status'


ensure_registered()
