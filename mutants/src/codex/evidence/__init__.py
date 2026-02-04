"""Evidence helpers for Codex operations."""

from __future__ import annotations

import sys
from importlib import util
from pathlib import Path
from types import ModuleType

from .core import evidence_append
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


def x__load_legacy_module__mutmut_orig() -> ModuleType:
    module_name = "codex._legacy_evidence"
    if module_name in sys.modules:
        return sys.modules[module_name]
    legacy_path = Path(__file__).resolve().parent.parent / "evidence.py"
    spec = util.spec_from_file_location(module_name, legacy_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load legacy evidence module from {legacy_path!s}")
    module = util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def x__load_legacy_module__mutmut_1() -> ModuleType:
    module_name = None
    if module_name in sys.modules:
        return sys.modules[module_name]
    legacy_path = Path(__file__).resolve().parent.parent / "evidence.py"
    spec = util.spec_from_file_location(module_name, legacy_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load legacy evidence module from {legacy_path!s}")
    module = util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def x__load_legacy_module__mutmut_2() -> ModuleType:
    module_name = "XXcodex._legacy_evidenceXX"
    if module_name in sys.modules:
        return sys.modules[module_name]
    legacy_path = Path(__file__).resolve().parent.parent / "evidence.py"
    spec = util.spec_from_file_location(module_name, legacy_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load legacy evidence module from {legacy_path!s}")
    module = util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def x__load_legacy_module__mutmut_3() -> ModuleType:
    module_name = "CODEX._LEGACY_EVIDENCE"
    if module_name in sys.modules:
        return sys.modules[module_name]
    legacy_path = Path(__file__).resolve().parent.parent / "evidence.py"
    spec = util.spec_from_file_location(module_name, legacy_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load legacy evidence module from {legacy_path!s}")
    module = util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def x__load_legacy_module__mutmut_4() -> ModuleType:
    module_name = "codex._legacy_evidence"
    if module_name not in sys.modules:
        return sys.modules[module_name]
    legacy_path = Path(__file__).resolve().parent.parent / "evidence.py"
    spec = util.spec_from_file_location(module_name, legacy_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load legacy evidence module from {legacy_path!s}")
    module = util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def x__load_legacy_module__mutmut_5() -> ModuleType:
    module_name = "codex._legacy_evidence"
    if module_name in sys.modules:
        return sys.modules[module_name]
    legacy_path = None
    spec = util.spec_from_file_location(module_name, legacy_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load legacy evidence module from {legacy_path!s}")
    module = util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def x__load_legacy_module__mutmut_6() -> ModuleType:
    module_name = "codex._legacy_evidence"
    if module_name in sys.modules:
        return sys.modules[module_name]
    legacy_path = Path(__file__).resolve().parent.parent * "evidence.py"
    spec = util.spec_from_file_location(module_name, legacy_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load legacy evidence module from {legacy_path!s}")
    module = util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def x__load_legacy_module__mutmut_7() -> ModuleType:
    module_name = "codex._legacy_evidence"
    if module_name in sys.modules:
        return sys.modules[module_name]
    legacy_path = Path(None).resolve().parent.parent / "evidence.py"
    spec = util.spec_from_file_location(module_name, legacy_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load legacy evidence module from {legacy_path!s}")
    module = util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def x__load_legacy_module__mutmut_8() -> ModuleType:
    module_name = "codex._legacy_evidence"
    if module_name in sys.modules:
        return sys.modules[module_name]
    legacy_path = Path(__file__).resolve().parent.parent / "XXevidence.pyXX"
    spec = util.spec_from_file_location(module_name, legacy_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load legacy evidence module from {legacy_path!s}")
    module = util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def x__load_legacy_module__mutmut_9() -> ModuleType:
    module_name = "codex._legacy_evidence"
    if module_name in sys.modules:
        return sys.modules[module_name]
    legacy_path = Path(__file__).resolve().parent.parent / "EVIDENCE.PY"
    spec = util.spec_from_file_location(module_name, legacy_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load legacy evidence module from {legacy_path!s}")
    module = util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def x__load_legacy_module__mutmut_10() -> ModuleType:
    module_name = "codex._legacy_evidence"
    if module_name in sys.modules:
        return sys.modules[module_name]
    legacy_path = Path(__file__).resolve().parent.parent / "evidence.py"
    spec = None
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load legacy evidence module from {legacy_path!s}")
    module = util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def x__load_legacy_module__mutmut_11() -> ModuleType:
    module_name = "codex._legacy_evidence"
    if module_name in sys.modules:
        return sys.modules[module_name]
    legacy_path = Path(__file__).resolve().parent.parent / "evidence.py"
    spec = util.spec_from_file_location(None, legacy_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load legacy evidence module from {legacy_path!s}")
    module = util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def x__load_legacy_module__mutmut_12() -> ModuleType:
    module_name = "codex._legacy_evidence"
    if module_name in sys.modules:
        return sys.modules[module_name]
    legacy_path = Path(__file__).resolve().parent.parent / "evidence.py"
    spec = util.spec_from_file_location(module_name, None)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load legacy evidence module from {legacy_path!s}")
    module = util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def x__load_legacy_module__mutmut_13() -> ModuleType:
    module_name = "codex._legacy_evidence"
    if module_name in sys.modules:
        return sys.modules[module_name]
    legacy_path = Path(__file__).resolve().parent.parent / "evidence.py"
    spec = util.spec_from_file_location(legacy_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load legacy evidence module from {legacy_path!s}")
    module = util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def x__load_legacy_module__mutmut_14() -> ModuleType:
    module_name = "codex._legacy_evidence"
    if module_name in sys.modules:
        return sys.modules[module_name]
    legacy_path = Path(__file__).resolve().parent.parent / "evidence.py"
    spec = util.spec_from_file_location(module_name, )
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load legacy evidence module from {legacy_path!s}")
    module = util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def x__load_legacy_module__mutmut_15() -> ModuleType:
    module_name = "codex._legacy_evidence"
    if module_name in sys.modules:
        return sys.modules[module_name]
    legacy_path = Path(__file__).resolve().parent.parent / "evidence.py"
    spec = util.spec_from_file_location(module_name, legacy_path)
    if spec is None and spec.loader is None:
        raise ImportError(f"Unable to load legacy evidence module from {legacy_path!s}")
    module = util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def x__load_legacy_module__mutmut_16() -> ModuleType:
    module_name = "codex._legacy_evidence"
    if module_name in sys.modules:
        return sys.modules[module_name]
    legacy_path = Path(__file__).resolve().parent.parent / "evidence.py"
    spec = util.spec_from_file_location(module_name, legacy_path)
    if spec is not None or spec.loader is None:
        raise ImportError(f"Unable to load legacy evidence module from {legacy_path!s}")
    module = util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def x__load_legacy_module__mutmut_17() -> ModuleType:
    module_name = "codex._legacy_evidence"
    if module_name in sys.modules:
        return sys.modules[module_name]
    legacy_path = Path(__file__).resolve().parent.parent / "evidence.py"
    spec = util.spec_from_file_location(module_name, legacy_path)
    if spec is None or spec.loader is not None:
        raise ImportError(f"Unable to load legacy evidence module from {legacy_path!s}")
    module = util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def x__load_legacy_module__mutmut_18() -> ModuleType:
    module_name = "codex._legacy_evidence"
    if module_name in sys.modules:
        return sys.modules[module_name]
    legacy_path = Path(__file__).resolve().parent.parent / "evidence.py"
    spec = util.spec_from_file_location(module_name, legacy_path)
    if spec is None or spec.loader is None:
        raise ImportError(None)
    module = util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def x__load_legacy_module__mutmut_19() -> ModuleType:
    module_name = "codex._legacy_evidence"
    if module_name in sys.modules:
        return sys.modules[module_name]
    legacy_path = Path(__file__).resolve().parent.parent / "evidence.py"
    spec = util.spec_from_file_location(module_name, legacy_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load legacy evidence module from {legacy_path!s}")
    module = None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def x__load_legacy_module__mutmut_20() -> ModuleType:
    module_name = "codex._legacy_evidence"
    if module_name in sys.modules:
        return sys.modules[module_name]
    legacy_path = Path(__file__).resolve().parent.parent / "evidence.py"
    spec = util.spec_from_file_location(module_name, legacy_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load legacy evidence module from {legacy_path!s}")
    module = util.module_from_spec(None)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def x__load_legacy_module__mutmut_21() -> ModuleType:
    module_name = "codex._legacy_evidence"
    if module_name in sys.modules:
        return sys.modules[module_name]
    legacy_path = Path(__file__).resolve().parent.parent / "evidence.py"
    spec = util.spec_from_file_location(module_name, legacy_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load legacy evidence module from {legacy_path!s}")
    module = util.module_from_spec(spec)
    sys.modules[module_name] = None
    spec.loader.exec_module(module)
    return module


def x__load_legacy_module__mutmut_22() -> ModuleType:
    module_name = "codex._legacy_evidence"
    if module_name in sys.modules:
        return sys.modules[module_name]
    legacy_path = Path(__file__).resolve().parent.parent / "evidence.py"
    spec = util.spec_from_file_location(module_name, legacy_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load legacy evidence module from {legacy_path!s}")
    module = util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(None)
    return module

x__load_legacy_module__mutmut_mutants : ClassVar[MutantDict] = {
'x__load_legacy_module__mutmut_1': x__load_legacy_module__mutmut_1, 
    'x__load_legacy_module__mutmut_2': x__load_legacy_module__mutmut_2, 
    'x__load_legacy_module__mutmut_3': x__load_legacy_module__mutmut_3, 
    'x__load_legacy_module__mutmut_4': x__load_legacy_module__mutmut_4, 
    'x__load_legacy_module__mutmut_5': x__load_legacy_module__mutmut_5, 
    'x__load_legacy_module__mutmut_6': x__load_legacy_module__mutmut_6, 
    'x__load_legacy_module__mutmut_7': x__load_legacy_module__mutmut_7, 
    'x__load_legacy_module__mutmut_8': x__load_legacy_module__mutmut_8, 
    'x__load_legacy_module__mutmut_9': x__load_legacy_module__mutmut_9, 
    'x__load_legacy_module__mutmut_10': x__load_legacy_module__mutmut_10, 
    'x__load_legacy_module__mutmut_11': x__load_legacy_module__mutmut_11, 
    'x__load_legacy_module__mutmut_12': x__load_legacy_module__mutmut_12, 
    'x__load_legacy_module__mutmut_13': x__load_legacy_module__mutmut_13, 
    'x__load_legacy_module__mutmut_14': x__load_legacy_module__mutmut_14, 
    'x__load_legacy_module__mutmut_15': x__load_legacy_module__mutmut_15, 
    'x__load_legacy_module__mutmut_16': x__load_legacy_module__mutmut_16, 
    'x__load_legacy_module__mutmut_17': x__load_legacy_module__mutmut_17, 
    'x__load_legacy_module__mutmut_18': x__load_legacy_module__mutmut_18, 
    'x__load_legacy_module__mutmut_19': x__load_legacy_module__mutmut_19, 
    'x__load_legacy_module__mutmut_20': x__load_legacy_module__mutmut_20, 
    'x__load_legacy_module__mutmut_21': x__load_legacy_module__mutmut_21, 
    'x__load_legacy_module__mutmut_22': x__load_legacy_module__mutmut_22
}

def _load_legacy_module(*args, **kwargs):
    result = _mutmut_trampoline(x__load_legacy_module__mutmut_orig, x__load_legacy_module__mutmut_mutants, args, kwargs)
    return result 

_load_legacy_module.__signature__ = _mutmut_signature(x__load_legacy_module__mutmut_orig)
x__load_legacy_module__mutmut_orig.__name__ = 'x__load_legacy_module'


_legacy = _load_legacy_module()
append_evidence = _legacy.append_evidence
utc_now = _legacy.utc_now

__all__ = ["evidence_append", "append_evidence", "utc_now"]
