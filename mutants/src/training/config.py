"""Dataclass-driven configuration for ``training.engine_hf_trainer``.

This module provides a lightweight configuration object with validation and
helper constructors. It avoids depending on Hydra/YAML so that simple scripts
can configure ``run_hf_trainer`` using environment variables or small JSON
files.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, fields
from pathlib import Path
from types import UnionType
from typing import (
    Any,
    Mapping,
    MutableMapping,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

_VALID_PRECISIONS = {"fp32", "fp16", "bf16"}
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


def x__to_bool__mutmut_orig(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in {"1", "true", "yes", "on", "enable", "enabled"}:
        return True
    if lowered in {"0", "false", "no", "off", "disable", "disabled"}:
        return False
    raise ValueError(f"Cannot coerce boolean from '{value}'")


def x__to_bool__mutmut_1(value: str) -> bool:
    lowered = None
    if lowered in {"1", "true", "yes", "on", "enable", "enabled"}:
        return True
    if lowered in {"0", "false", "no", "off", "disable", "disabled"}:
        return False
    raise ValueError(f"Cannot coerce boolean from '{value}'")


def x__to_bool__mutmut_2(value: str) -> bool:
    lowered = value.strip().upper()
    if lowered in {"1", "true", "yes", "on", "enable", "enabled"}:
        return True
    if lowered in {"0", "false", "no", "off", "disable", "disabled"}:
        return False
    raise ValueError(f"Cannot coerce boolean from '{value}'")


def x__to_bool__mutmut_3(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered not in {"1", "true", "yes", "on", "enable", "enabled"}:
        return True
    if lowered in {"0", "false", "no", "off", "disable", "disabled"}:
        return False
    raise ValueError(f"Cannot coerce boolean from '{value}'")


def x__to_bool__mutmut_4(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in {"XX1XX", "true", "yes", "on", "enable", "enabled"}:
        return True
    if lowered in {"0", "false", "no", "off", "disable", "disabled"}:
        return False
    raise ValueError(f"Cannot coerce boolean from '{value}'")


def x__to_bool__mutmut_5(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in {"1", "XXtrueXX", "yes", "on", "enable", "enabled"}:
        return True
    if lowered in {"0", "false", "no", "off", "disable", "disabled"}:
        return False
    raise ValueError(f"Cannot coerce boolean from '{value}'")


def x__to_bool__mutmut_6(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in {"1", "TRUE", "yes", "on", "enable", "enabled"}:
        return True
    if lowered in {"0", "false", "no", "off", "disable", "disabled"}:
        return False
    raise ValueError(f"Cannot coerce boolean from '{value}'")


def x__to_bool__mutmut_7(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in {"1", "true", "XXyesXX", "on", "enable", "enabled"}:
        return True
    if lowered in {"0", "false", "no", "off", "disable", "disabled"}:
        return False
    raise ValueError(f"Cannot coerce boolean from '{value}'")


def x__to_bool__mutmut_8(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in {"1", "true", "YES", "on", "enable", "enabled"}:
        return True
    if lowered in {"0", "false", "no", "off", "disable", "disabled"}:
        return False
    raise ValueError(f"Cannot coerce boolean from '{value}'")


def x__to_bool__mutmut_9(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in {"1", "true", "yes", "XXonXX", "enable", "enabled"}:
        return True
    if lowered in {"0", "false", "no", "off", "disable", "disabled"}:
        return False
    raise ValueError(f"Cannot coerce boolean from '{value}'")


def x__to_bool__mutmut_10(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in {"1", "true", "yes", "ON", "enable", "enabled"}:
        return True
    if lowered in {"0", "false", "no", "off", "disable", "disabled"}:
        return False
    raise ValueError(f"Cannot coerce boolean from '{value}'")


def x__to_bool__mutmut_11(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in {"1", "true", "yes", "on", "XXenableXX", "enabled"}:
        return True
    if lowered in {"0", "false", "no", "off", "disable", "disabled"}:
        return False
    raise ValueError(f"Cannot coerce boolean from '{value}'")


def x__to_bool__mutmut_12(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in {"1", "true", "yes", "on", "ENABLE", "enabled"}:
        return True
    if lowered in {"0", "false", "no", "off", "disable", "disabled"}:
        return False
    raise ValueError(f"Cannot coerce boolean from '{value}'")


def x__to_bool__mutmut_13(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in {"1", "true", "yes", "on", "enable", "XXenabledXX"}:
        return True
    if lowered in {"0", "false", "no", "off", "disable", "disabled"}:
        return False
    raise ValueError(f"Cannot coerce boolean from '{value}'")


def x__to_bool__mutmut_14(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in {"1", "true", "yes", "on", "enable", "ENABLED"}:
        return True
    if lowered in {"0", "false", "no", "off", "disable", "disabled"}:
        return False
    raise ValueError(f"Cannot coerce boolean from '{value}'")


def x__to_bool__mutmut_15(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in {"1", "true", "yes", "on", "enable", "enabled"}:
        return False
    if lowered in {"0", "false", "no", "off", "disable", "disabled"}:
        return False
    raise ValueError(f"Cannot coerce boolean from '{value}'")


def x__to_bool__mutmut_16(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in {"1", "true", "yes", "on", "enable", "enabled"}:
        return True
    if lowered not in {"0", "false", "no", "off", "disable", "disabled"}:
        return False
    raise ValueError(f"Cannot coerce boolean from '{value}'")


def x__to_bool__mutmut_17(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in {"1", "true", "yes", "on", "enable", "enabled"}:
        return True
    if lowered in {"XX0XX", "false", "no", "off", "disable", "disabled"}:
        return False
    raise ValueError(f"Cannot coerce boolean from '{value}'")


def x__to_bool__mutmut_18(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in {"1", "true", "yes", "on", "enable", "enabled"}:
        return True
    if lowered in {"0", "XXfalseXX", "no", "off", "disable", "disabled"}:
        return False
    raise ValueError(f"Cannot coerce boolean from '{value}'")


def x__to_bool__mutmut_19(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in {"1", "true", "yes", "on", "enable", "enabled"}:
        return True
    if lowered in {"0", "FALSE", "no", "off", "disable", "disabled"}:
        return False
    raise ValueError(f"Cannot coerce boolean from '{value}'")


def x__to_bool__mutmut_20(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in {"1", "true", "yes", "on", "enable", "enabled"}:
        return True
    if lowered in {"0", "false", "XXnoXX", "off", "disable", "disabled"}:
        return False
    raise ValueError(f"Cannot coerce boolean from '{value}'")


def x__to_bool__mutmut_21(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in {"1", "true", "yes", "on", "enable", "enabled"}:
        return True
    if lowered in {"0", "false", "NO", "off", "disable", "disabled"}:
        return False
    raise ValueError(f"Cannot coerce boolean from '{value}'")


def x__to_bool__mutmut_22(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in {"1", "true", "yes", "on", "enable", "enabled"}:
        return True
    if lowered in {"0", "false", "no", "XXoffXX", "disable", "disabled"}:
        return False
    raise ValueError(f"Cannot coerce boolean from '{value}'")


def x__to_bool__mutmut_23(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in {"1", "true", "yes", "on", "enable", "enabled"}:
        return True
    if lowered in {"0", "false", "no", "OFF", "disable", "disabled"}:
        return False
    raise ValueError(f"Cannot coerce boolean from '{value}'")


def x__to_bool__mutmut_24(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in {"1", "true", "yes", "on", "enable", "enabled"}:
        return True
    if lowered in {"0", "false", "no", "off", "XXdisableXX", "disabled"}:
        return False
    raise ValueError(f"Cannot coerce boolean from '{value}'")


def x__to_bool__mutmut_25(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in {"1", "true", "yes", "on", "enable", "enabled"}:
        return True
    if lowered in {"0", "false", "no", "off", "DISABLE", "disabled"}:
        return False
    raise ValueError(f"Cannot coerce boolean from '{value}'")


def x__to_bool__mutmut_26(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in {"1", "true", "yes", "on", "enable", "enabled"}:
        return True
    if lowered in {"0", "false", "no", "off", "disable", "XXdisabledXX"}:
        return False
    raise ValueError(f"Cannot coerce boolean from '{value}'")


def x__to_bool__mutmut_27(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in {"1", "true", "yes", "on", "enable", "enabled"}:
        return True
    if lowered in {"0", "false", "no", "off", "disable", "DISABLED"}:
        return False
    raise ValueError(f"Cannot coerce boolean from '{value}'")


def x__to_bool__mutmut_28(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in {"1", "true", "yes", "on", "enable", "enabled"}:
        return True
    if lowered in {"0", "false", "no", "off", "disable", "disabled"}:
        return True
    raise ValueError(f"Cannot coerce boolean from '{value}'")


def x__to_bool__mutmut_29(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in {"1", "true", "yes", "on", "enable", "enabled"}:
        return True
    if lowered in {"0", "false", "no", "off", "disable", "disabled"}:
        return False
    raise ValueError(None)

x__to_bool__mutmut_mutants : ClassVar[MutantDict] = {
'x__to_bool__mutmut_1': x__to_bool__mutmut_1, 
    'x__to_bool__mutmut_2': x__to_bool__mutmut_2, 
    'x__to_bool__mutmut_3': x__to_bool__mutmut_3, 
    'x__to_bool__mutmut_4': x__to_bool__mutmut_4, 
    'x__to_bool__mutmut_5': x__to_bool__mutmut_5, 
    'x__to_bool__mutmut_6': x__to_bool__mutmut_6, 
    'x__to_bool__mutmut_7': x__to_bool__mutmut_7, 
    'x__to_bool__mutmut_8': x__to_bool__mutmut_8, 
    'x__to_bool__mutmut_9': x__to_bool__mutmut_9, 
    'x__to_bool__mutmut_10': x__to_bool__mutmut_10, 
    'x__to_bool__mutmut_11': x__to_bool__mutmut_11, 
    'x__to_bool__mutmut_12': x__to_bool__mutmut_12, 
    'x__to_bool__mutmut_13': x__to_bool__mutmut_13, 
    'x__to_bool__mutmut_14': x__to_bool__mutmut_14, 
    'x__to_bool__mutmut_15': x__to_bool__mutmut_15, 
    'x__to_bool__mutmut_16': x__to_bool__mutmut_16, 
    'x__to_bool__mutmut_17': x__to_bool__mutmut_17, 
    'x__to_bool__mutmut_18': x__to_bool__mutmut_18, 
    'x__to_bool__mutmut_19': x__to_bool__mutmut_19, 
    'x__to_bool__mutmut_20': x__to_bool__mutmut_20, 
    'x__to_bool__mutmut_21': x__to_bool__mutmut_21, 
    'x__to_bool__mutmut_22': x__to_bool__mutmut_22, 
    'x__to_bool__mutmut_23': x__to_bool__mutmut_23, 
    'x__to_bool__mutmut_24': x__to_bool__mutmut_24, 
    'x__to_bool__mutmut_25': x__to_bool__mutmut_25, 
    'x__to_bool__mutmut_26': x__to_bool__mutmut_26, 
    'x__to_bool__mutmut_27': x__to_bool__mutmut_27, 
    'x__to_bool__mutmut_28': x__to_bool__mutmut_28, 
    'x__to_bool__mutmut_29': x__to_bool__mutmut_29
}

def _to_bool(*args, **kwargs):
    result = _mutmut_trampoline(x__to_bool__mutmut_orig, x__to_bool__mutmut_mutants, args, kwargs)
    return result 

_to_bool.__signature__ = _mutmut_signature(x__to_bool__mutmut_orig)
x__to_bool__mutmut_orig.__name__ = 'x__to_bool'


def x__resolve_target_type__mutmut_orig(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_1(annotation: Any, current: Any) -> type[Any] | None:
    origin = None
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_2(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(None)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_3(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is not None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_4(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = None
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_5(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "XXintXX": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_6(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "INT": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_7(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "XXfloatXX": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_8(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "FLOAT": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_9(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "XXboolXX": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_10(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "BOOL": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_11(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "XXPathXX": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_12(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_13(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "PATH": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_14(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "XXOptional[int]XX": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_15(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_16(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "OPTIONAL[INT]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_17(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "XXOptional[float]XX": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_18(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_19(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "OPTIONAL[FLOAT]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_20(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "XXOptional[bool]XX": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_21(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_22(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "OPTIONAL[BOOL]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_23(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "XXOptional[Path]XX": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_24(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "optional[path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_25(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "OPTIONAL[PATH]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_26(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = None
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_27(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(None)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_28(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_29(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "XX|XX" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_30(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" not in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_31(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = None
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_32(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split(None)]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_33(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("XX|XX")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_34(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = None
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_35(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_36(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"XXNoneXX", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_37(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"none", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_38(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"NONE", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_39(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "XXNoneTypeXX"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_40(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "nonetype"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_41(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NONETYPE"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_42(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) != 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_43(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 2:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_44(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(None)
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_45(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[1])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_46(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is not Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_47(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(None) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_48(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_49(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is not None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_50(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin not in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_51(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin not in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_52(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = None
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_53(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(None) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_54(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_55(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_56(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(None, current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_57(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], None)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_58(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_59(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], )
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_60(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[1], current)
    return type(current) if current is not None else str


def x__resolve_target_type__mutmut_61(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(None) if current is not None else str


def x__resolve_target_type__mutmut_62(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation  # type: ignore[return-value]
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is None else str

x__resolve_target_type__mutmut_mutants : ClassVar[MutantDict] = {
'x__resolve_target_type__mutmut_1': x__resolve_target_type__mutmut_1, 
    'x__resolve_target_type__mutmut_2': x__resolve_target_type__mutmut_2, 
    'x__resolve_target_type__mutmut_3': x__resolve_target_type__mutmut_3, 
    'x__resolve_target_type__mutmut_4': x__resolve_target_type__mutmut_4, 
    'x__resolve_target_type__mutmut_5': x__resolve_target_type__mutmut_5, 
    'x__resolve_target_type__mutmut_6': x__resolve_target_type__mutmut_6, 
    'x__resolve_target_type__mutmut_7': x__resolve_target_type__mutmut_7, 
    'x__resolve_target_type__mutmut_8': x__resolve_target_type__mutmut_8, 
    'x__resolve_target_type__mutmut_9': x__resolve_target_type__mutmut_9, 
    'x__resolve_target_type__mutmut_10': x__resolve_target_type__mutmut_10, 
    'x__resolve_target_type__mutmut_11': x__resolve_target_type__mutmut_11, 
    'x__resolve_target_type__mutmut_12': x__resolve_target_type__mutmut_12, 
    'x__resolve_target_type__mutmut_13': x__resolve_target_type__mutmut_13, 
    'x__resolve_target_type__mutmut_14': x__resolve_target_type__mutmut_14, 
    'x__resolve_target_type__mutmut_15': x__resolve_target_type__mutmut_15, 
    'x__resolve_target_type__mutmut_16': x__resolve_target_type__mutmut_16, 
    'x__resolve_target_type__mutmut_17': x__resolve_target_type__mutmut_17, 
    'x__resolve_target_type__mutmut_18': x__resolve_target_type__mutmut_18, 
    'x__resolve_target_type__mutmut_19': x__resolve_target_type__mutmut_19, 
    'x__resolve_target_type__mutmut_20': x__resolve_target_type__mutmut_20, 
    'x__resolve_target_type__mutmut_21': x__resolve_target_type__mutmut_21, 
    'x__resolve_target_type__mutmut_22': x__resolve_target_type__mutmut_22, 
    'x__resolve_target_type__mutmut_23': x__resolve_target_type__mutmut_23, 
    'x__resolve_target_type__mutmut_24': x__resolve_target_type__mutmut_24, 
    'x__resolve_target_type__mutmut_25': x__resolve_target_type__mutmut_25, 
    'x__resolve_target_type__mutmut_26': x__resolve_target_type__mutmut_26, 
    'x__resolve_target_type__mutmut_27': x__resolve_target_type__mutmut_27, 
    'x__resolve_target_type__mutmut_28': x__resolve_target_type__mutmut_28, 
    'x__resolve_target_type__mutmut_29': x__resolve_target_type__mutmut_29, 
    'x__resolve_target_type__mutmut_30': x__resolve_target_type__mutmut_30, 
    'x__resolve_target_type__mutmut_31': x__resolve_target_type__mutmut_31, 
    'x__resolve_target_type__mutmut_32': x__resolve_target_type__mutmut_32, 
    'x__resolve_target_type__mutmut_33': x__resolve_target_type__mutmut_33, 
    'x__resolve_target_type__mutmut_34': x__resolve_target_type__mutmut_34, 
    'x__resolve_target_type__mutmut_35': x__resolve_target_type__mutmut_35, 
    'x__resolve_target_type__mutmut_36': x__resolve_target_type__mutmut_36, 
    'x__resolve_target_type__mutmut_37': x__resolve_target_type__mutmut_37, 
    'x__resolve_target_type__mutmut_38': x__resolve_target_type__mutmut_38, 
    'x__resolve_target_type__mutmut_39': x__resolve_target_type__mutmut_39, 
    'x__resolve_target_type__mutmut_40': x__resolve_target_type__mutmut_40, 
    'x__resolve_target_type__mutmut_41': x__resolve_target_type__mutmut_41, 
    'x__resolve_target_type__mutmut_42': x__resolve_target_type__mutmut_42, 
    'x__resolve_target_type__mutmut_43': x__resolve_target_type__mutmut_43, 
    'x__resolve_target_type__mutmut_44': x__resolve_target_type__mutmut_44, 
    'x__resolve_target_type__mutmut_45': x__resolve_target_type__mutmut_45, 
    'x__resolve_target_type__mutmut_46': x__resolve_target_type__mutmut_46, 
    'x__resolve_target_type__mutmut_47': x__resolve_target_type__mutmut_47, 
    'x__resolve_target_type__mutmut_48': x__resolve_target_type__mutmut_48, 
    'x__resolve_target_type__mutmut_49': x__resolve_target_type__mutmut_49, 
    'x__resolve_target_type__mutmut_50': x__resolve_target_type__mutmut_50, 
    'x__resolve_target_type__mutmut_51': x__resolve_target_type__mutmut_51, 
    'x__resolve_target_type__mutmut_52': x__resolve_target_type__mutmut_52, 
    'x__resolve_target_type__mutmut_53': x__resolve_target_type__mutmut_53, 
    'x__resolve_target_type__mutmut_54': x__resolve_target_type__mutmut_54, 
    'x__resolve_target_type__mutmut_55': x__resolve_target_type__mutmut_55, 
    'x__resolve_target_type__mutmut_56': x__resolve_target_type__mutmut_56, 
    'x__resolve_target_type__mutmut_57': x__resolve_target_type__mutmut_57, 
    'x__resolve_target_type__mutmut_58': x__resolve_target_type__mutmut_58, 
    'x__resolve_target_type__mutmut_59': x__resolve_target_type__mutmut_59, 
    'x__resolve_target_type__mutmut_60': x__resolve_target_type__mutmut_60, 
    'x__resolve_target_type__mutmut_61': x__resolve_target_type__mutmut_61, 
    'x__resolve_target_type__mutmut_62': x__resolve_target_type__mutmut_62
}

def _resolve_target_type(*args, **kwargs):
    result = _mutmut_trampoline(x__resolve_target_type__mutmut_orig, x__resolve_target_type__mutmut_mutants, args, kwargs)
    return result 

_resolve_target_type.__signature__ = _mutmut_signature(x__resolve_target_type__mutmut_orig)
x__resolve_target_type__mutmut_orig.__name__ = 'x__resolve_target_type'


def x__coerce_value__mutmut_orig(value: Any, annotation: Any, current: Any) -> Any:
    if isinstance(value, str):
        if isinstance(current, bool):
            return _to_bool(value)
        if isinstance(current, int):
            return int(value)
        if isinstance(current, float):
            return float(value)
        if isinstance(current, Path):
            return Path(value)
    if isinstance(value, (int, float)) and annotation in {int, float}:
        return annotation(value)
    if isinstance(value, bool) and annotation is bool:
        return value
    if isinstance(value, Path) and annotation in {Path, str | Path}:
        return value
    if isinstance(value, str):
        target = _resolve_target_type(annotation, current)
        if target in {str, None}:
            return value
        if target is Path:
            return Path(value)
        if target in {int, "int"}:
            return int(value)
        if target in {float, "float"}:
            return float(value)
        if target in {bool, "bool"}:
            return _to_bool(value)
    return value


def x__coerce_value__mutmut_1(value: Any, annotation: Any, current: Any) -> Any:
    if isinstance(value, str):
        if isinstance(current, bool):
            return _to_bool(None)
        if isinstance(current, int):
            return int(value)
        if isinstance(current, float):
            return float(value)
        if isinstance(current, Path):
            return Path(value)
    if isinstance(value, (int, float)) and annotation in {int, float}:
        return annotation(value)
    if isinstance(value, bool) and annotation is bool:
        return value
    if isinstance(value, Path) and annotation in {Path, str | Path}:
        return value
    if isinstance(value, str):
        target = _resolve_target_type(annotation, current)
        if target in {str, None}:
            return value
        if target is Path:
            return Path(value)
        if target in {int, "int"}:
            return int(value)
        if target in {float, "float"}:
            return float(value)
        if target in {bool, "bool"}:
            return _to_bool(value)
    return value


def x__coerce_value__mutmut_2(value: Any, annotation: Any, current: Any) -> Any:
    if isinstance(value, str):
        if isinstance(current, bool):
            return _to_bool(value)
        if isinstance(current, int):
            return int(None)
        if isinstance(current, float):
            return float(value)
        if isinstance(current, Path):
            return Path(value)
    if isinstance(value, (int, float)) and annotation in {int, float}:
        return annotation(value)
    if isinstance(value, bool) and annotation is bool:
        return value
    if isinstance(value, Path) and annotation in {Path, str | Path}:
        return value
    if isinstance(value, str):
        target = _resolve_target_type(annotation, current)
        if target in {str, None}:
            return value
        if target is Path:
            return Path(value)
        if target in {int, "int"}:
            return int(value)
        if target in {float, "float"}:
            return float(value)
        if target in {bool, "bool"}:
            return _to_bool(value)
    return value


def x__coerce_value__mutmut_3(value: Any, annotation: Any, current: Any) -> Any:
    if isinstance(value, str):
        if isinstance(current, bool):
            return _to_bool(value)
        if isinstance(current, int):
            return int(value)
        if isinstance(current, float):
            return float(None)
        if isinstance(current, Path):
            return Path(value)
    if isinstance(value, (int, float)) and annotation in {int, float}:
        return annotation(value)
    if isinstance(value, bool) and annotation is bool:
        return value
    if isinstance(value, Path) and annotation in {Path, str | Path}:
        return value
    if isinstance(value, str):
        target = _resolve_target_type(annotation, current)
        if target in {str, None}:
            return value
        if target is Path:
            return Path(value)
        if target in {int, "int"}:
            return int(value)
        if target in {float, "float"}:
            return float(value)
        if target in {bool, "bool"}:
            return _to_bool(value)
    return value


def x__coerce_value__mutmut_4(value: Any, annotation: Any, current: Any) -> Any:
    if isinstance(value, str):
        if isinstance(current, bool):
            return _to_bool(value)
        if isinstance(current, int):
            return int(value)
        if isinstance(current, float):
            return float(value)
        if isinstance(current, Path):
            return Path(None)
    if isinstance(value, (int, float)) and annotation in {int, float}:
        return annotation(value)
    if isinstance(value, bool) and annotation is bool:
        return value
    if isinstance(value, Path) and annotation in {Path, str | Path}:
        return value
    if isinstance(value, str):
        target = _resolve_target_type(annotation, current)
        if target in {str, None}:
            return value
        if target is Path:
            return Path(value)
        if target in {int, "int"}:
            return int(value)
        if target in {float, "float"}:
            return float(value)
        if target in {bool, "bool"}:
            return _to_bool(value)
    return value


def x__coerce_value__mutmut_5(value: Any, annotation: Any, current: Any) -> Any:
    if isinstance(value, str):
        if isinstance(current, bool):
            return _to_bool(value)
        if isinstance(current, int):
            return int(value)
        if isinstance(current, float):
            return float(value)
        if isinstance(current, Path):
            return Path(value)
    if isinstance(value, (int, float)) or annotation in {int, float}:
        return annotation(value)
    if isinstance(value, bool) and annotation is bool:
        return value
    if isinstance(value, Path) and annotation in {Path, str | Path}:
        return value
    if isinstance(value, str):
        target = _resolve_target_type(annotation, current)
        if target in {str, None}:
            return value
        if target is Path:
            return Path(value)
        if target in {int, "int"}:
            return int(value)
        if target in {float, "float"}:
            return float(value)
        if target in {bool, "bool"}:
            return _to_bool(value)
    return value


def x__coerce_value__mutmut_6(value: Any, annotation: Any, current: Any) -> Any:
    if isinstance(value, str):
        if isinstance(current, bool):
            return _to_bool(value)
        if isinstance(current, int):
            return int(value)
        if isinstance(current, float):
            return float(value)
        if isinstance(current, Path):
            return Path(value)
    if isinstance(value, (int, float)) and annotation not in {int, float}:
        return annotation(value)
    if isinstance(value, bool) and annotation is bool:
        return value
    if isinstance(value, Path) and annotation in {Path, str | Path}:
        return value
    if isinstance(value, str):
        target = _resolve_target_type(annotation, current)
        if target in {str, None}:
            return value
        if target is Path:
            return Path(value)
        if target in {int, "int"}:
            return int(value)
        if target in {float, "float"}:
            return float(value)
        if target in {bool, "bool"}:
            return _to_bool(value)
    return value


def x__coerce_value__mutmut_7(value: Any, annotation: Any, current: Any) -> Any:
    if isinstance(value, str):
        if isinstance(current, bool):
            return _to_bool(value)
        if isinstance(current, int):
            return int(value)
        if isinstance(current, float):
            return float(value)
        if isinstance(current, Path):
            return Path(value)
    if isinstance(value, (int, float)) and annotation in {int, float}:
        return annotation(None)
    if isinstance(value, bool) and annotation is bool:
        return value
    if isinstance(value, Path) and annotation in {Path, str | Path}:
        return value
    if isinstance(value, str):
        target = _resolve_target_type(annotation, current)
        if target in {str, None}:
            return value
        if target is Path:
            return Path(value)
        if target in {int, "int"}:
            return int(value)
        if target in {float, "float"}:
            return float(value)
        if target in {bool, "bool"}:
            return _to_bool(value)
    return value


def x__coerce_value__mutmut_8(value: Any, annotation: Any, current: Any) -> Any:
    if isinstance(value, str):
        if isinstance(current, bool):
            return _to_bool(value)
        if isinstance(current, int):
            return int(value)
        if isinstance(current, float):
            return float(value)
        if isinstance(current, Path):
            return Path(value)
    if isinstance(value, (int, float)) and annotation in {int, float}:
        return annotation(value)
    if isinstance(value, bool) or annotation is bool:
        return value
    if isinstance(value, Path) and annotation in {Path, str | Path}:
        return value
    if isinstance(value, str):
        target = _resolve_target_type(annotation, current)
        if target in {str, None}:
            return value
        if target is Path:
            return Path(value)
        if target in {int, "int"}:
            return int(value)
        if target in {float, "float"}:
            return float(value)
        if target in {bool, "bool"}:
            return _to_bool(value)
    return value


def x__coerce_value__mutmut_9(value: Any, annotation: Any, current: Any) -> Any:
    if isinstance(value, str):
        if isinstance(current, bool):
            return _to_bool(value)
        if isinstance(current, int):
            return int(value)
        if isinstance(current, float):
            return float(value)
        if isinstance(current, Path):
            return Path(value)
    if isinstance(value, (int, float)) and annotation in {int, float}:
        return annotation(value)
    if isinstance(value, bool) and annotation is not bool:
        return value
    if isinstance(value, Path) and annotation in {Path, str | Path}:
        return value
    if isinstance(value, str):
        target = _resolve_target_type(annotation, current)
        if target in {str, None}:
            return value
        if target is Path:
            return Path(value)
        if target in {int, "int"}:
            return int(value)
        if target in {float, "float"}:
            return float(value)
        if target in {bool, "bool"}:
            return _to_bool(value)
    return value


def x__coerce_value__mutmut_10(value: Any, annotation: Any, current: Any) -> Any:
    if isinstance(value, str):
        if isinstance(current, bool):
            return _to_bool(value)
        if isinstance(current, int):
            return int(value)
        if isinstance(current, float):
            return float(value)
        if isinstance(current, Path):
            return Path(value)
    if isinstance(value, (int, float)) and annotation in {int, float}:
        return annotation(value)
    if isinstance(value, bool) and annotation is bool:
        return value
    if isinstance(value, Path) or annotation in {Path, str | Path}:
        return value
    if isinstance(value, str):
        target = _resolve_target_type(annotation, current)
        if target in {str, None}:
            return value
        if target is Path:
            return Path(value)
        if target in {int, "int"}:
            return int(value)
        if target in {float, "float"}:
            return float(value)
        if target in {bool, "bool"}:
            return _to_bool(value)
    return value


def x__coerce_value__mutmut_11(value: Any, annotation: Any, current: Any) -> Any:
    if isinstance(value, str):
        if isinstance(current, bool):
            return _to_bool(value)
        if isinstance(current, int):
            return int(value)
        if isinstance(current, float):
            return float(value)
        if isinstance(current, Path):
            return Path(value)
    if isinstance(value, (int, float)) and annotation in {int, float}:
        return annotation(value)
    if isinstance(value, bool) and annotation is bool:
        return value
    if isinstance(value, Path) and annotation not in {Path, str | Path}:
        return value
    if isinstance(value, str):
        target = _resolve_target_type(annotation, current)
        if target in {str, None}:
            return value
        if target is Path:
            return Path(value)
        if target in {int, "int"}:
            return int(value)
        if target in {float, "float"}:
            return float(value)
        if target in {bool, "bool"}:
            return _to_bool(value)
    return value


def x__coerce_value__mutmut_12(value: Any, annotation: Any, current: Any) -> Any:
    if isinstance(value, str):
        if isinstance(current, bool):
            return _to_bool(value)
        if isinstance(current, int):
            return int(value)
        if isinstance(current, float):
            return float(value)
        if isinstance(current, Path):
            return Path(value)
    if isinstance(value, (int, float)) and annotation in {int, float}:
        return annotation(value)
    if isinstance(value, bool) and annotation is bool:
        return value
    if isinstance(value, Path) and annotation in {Path, str & Path}:
        return value
    if isinstance(value, str):
        target = _resolve_target_type(annotation, current)
        if target in {str, None}:
            return value
        if target is Path:
            return Path(value)
        if target in {int, "int"}:
            return int(value)
        if target in {float, "float"}:
            return float(value)
        if target in {bool, "bool"}:
            return _to_bool(value)
    return value


def x__coerce_value__mutmut_13(value: Any, annotation: Any, current: Any) -> Any:
    if isinstance(value, str):
        if isinstance(current, bool):
            return _to_bool(value)
        if isinstance(current, int):
            return int(value)
        if isinstance(current, float):
            return float(value)
        if isinstance(current, Path):
            return Path(value)
    if isinstance(value, (int, float)) and annotation in {int, float}:
        return annotation(value)
    if isinstance(value, bool) and annotation is bool:
        return value
    if isinstance(value, Path) and annotation in {Path, str | Path}:
        return value
    if isinstance(value, str):
        target = None
        if target in {str, None}:
            return value
        if target is Path:
            return Path(value)
        if target in {int, "int"}:
            return int(value)
        if target in {float, "float"}:
            return float(value)
        if target in {bool, "bool"}:
            return _to_bool(value)
    return value


def x__coerce_value__mutmut_14(value: Any, annotation: Any, current: Any) -> Any:
    if isinstance(value, str):
        if isinstance(current, bool):
            return _to_bool(value)
        if isinstance(current, int):
            return int(value)
        if isinstance(current, float):
            return float(value)
        if isinstance(current, Path):
            return Path(value)
    if isinstance(value, (int, float)) and annotation in {int, float}:
        return annotation(value)
    if isinstance(value, bool) and annotation is bool:
        return value
    if isinstance(value, Path) and annotation in {Path, str | Path}:
        return value
    if isinstance(value, str):
        target = _resolve_target_type(None, current)
        if target in {str, None}:
            return value
        if target is Path:
            return Path(value)
        if target in {int, "int"}:
            return int(value)
        if target in {float, "float"}:
            return float(value)
        if target in {bool, "bool"}:
            return _to_bool(value)
    return value


def x__coerce_value__mutmut_15(value: Any, annotation: Any, current: Any) -> Any:
    if isinstance(value, str):
        if isinstance(current, bool):
            return _to_bool(value)
        if isinstance(current, int):
            return int(value)
        if isinstance(current, float):
            return float(value)
        if isinstance(current, Path):
            return Path(value)
    if isinstance(value, (int, float)) and annotation in {int, float}:
        return annotation(value)
    if isinstance(value, bool) and annotation is bool:
        return value
    if isinstance(value, Path) and annotation in {Path, str | Path}:
        return value
    if isinstance(value, str):
        target = _resolve_target_type(annotation, None)
        if target in {str, None}:
            return value
        if target is Path:
            return Path(value)
        if target in {int, "int"}:
            return int(value)
        if target in {float, "float"}:
            return float(value)
        if target in {bool, "bool"}:
            return _to_bool(value)
    return value


def x__coerce_value__mutmut_16(value: Any, annotation: Any, current: Any) -> Any:
    if isinstance(value, str):
        if isinstance(current, bool):
            return _to_bool(value)
        if isinstance(current, int):
            return int(value)
        if isinstance(current, float):
            return float(value)
        if isinstance(current, Path):
            return Path(value)
    if isinstance(value, (int, float)) and annotation in {int, float}:
        return annotation(value)
    if isinstance(value, bool) and annotation is bool:
        return value
    if isinstance(value, Path) and annotation in {Path, str | Path}:
        return value
    if isinstance(value, str):
        target = _resolve_target_type(current)
        if target in {str, None}:
            return value
        if target is Path:
            return Path(value)
        if target in {int, "int"}:
            return int(value)
        if target in {float, "float"}:
            return float(value)
        if target in {bool, "bool"}:
            return _to_bool(value)
    return value


def x__coerce_value__mutmut_17(value: Any, annotation: Any, current: Any) -> Any:
    if isinstance(value, str):
        if isinstance(current, bool):
            return _to_bool(value)
        if isinstance(current, int):
            return int(value)
        if isinstance(current, float):
            return float(value)
        if isinstance(current, Path):
            return Path(value)
    if isinstance(value, (int, float)) and annotation in {int, float}:
        return annotation(value)
    if isinstance(value, bool) and annotation is bool:
        return value
    if isinstance(value, Path) and annotation in {Path, str | Path}:
        return value
    if isinstance(value, str):
        target = _resolve_target_type(annotation, )
        if target in {str, None}:
            return value
        if target is Path:
            return Path(value)
        if target in {int, "int"}:
            return int(value)
        if target in {float, "float"}:
            return float(value)
        if target in {bool, "bool"}:
            return _to_bool(value)
    return value


def x__coerce_value__mutmut_18(value: Any, annotation: Any, current: Any) -> Any:
    if isinstance(value, str):
        if isinstance(current, bool):
            return _to_bool(value)
        if isinstance(current, int):
            return int(value)
        if isinstance(current, float):
            return float(value)
        if isinstance(current, Path):
            return Path(value)
    if isinstance(value, (int, float)) and annotation in {int, float}:
        return annotation(value)
    if isinstance(value, bool) and annotation is bool:
        return value
    if isinstance(value, Path) and annotation in {Path, str | Path}:
        return value
    if isinstance(value, str):
        target = _resolve_target_type(annotation, current)
        if target not in {str, None}:
            return value
        if target is Path:
            return Path(value)
        if target in {int, "int"}:
            return int(value)
        if target in {float, "float"}:
            return float(value)
        if target in {bool, "bool"}:
            return _to_bool(value)
    return value


def x__coerce_value__mutmut_19(value: Any, annotation: Any, current: Any) -> Any:
    if isinstance(value, str):
        if isinstance(current, bool):
            return _to_bool(value)
        if isinstance(current, int):
            return int(value)
        if isinstance(current, float):
            return float(value)
        if isinstance(current, Path):
            return Path(value)
    if isinstance(value, (int, float)) and annotation in {int, float}:
        return annotation(value)
    if isinstance(value, bool) and annotation is bool:
        return value
    if isinstance(value, Path) and annotation in {Path, str | Path}:
        return value
    if isinstance(value, str):
        target = _resolve_target_type(annotation, current)
        if target in {str, None}:
            return value
        if target is not Path:
            return Path(value)
        if target in {int, "int"}:
            return int(value)
        if target in {float, "float"}:
            return float(value)
        if target in {bool, "bool"}:
            return _to_bool(value)
    return value


def x__coerce_value__mutmut_20(value: Any, annotation: Any, current: Any) -> Any:
    if isinstance(value, str):
        if isinstance(current, bool):
            return _to_bool(value)
        if isinstance(current, int):
            return int(value)
        if isinstance(current, float):
            return float(value)
        if isinstance(current, Path):
            return Path(value)
    if isinstance(value, (int, float)) and annotation in {int, float}:
        return annotation(value)
    if isinstance(value, bool) and annotation is bool:
        return value
    if isinstance(value, Path) and annotation in {Path, str | Path}:
        return value
    if isinstance(value, str):
        target = _resolve_target_type(annotation, current)
        if target in {str, None}:
            return value
        if target is Path:
            return Path(None)
        if target in {int, "int"}:
            return int(value)
        if target in {float, "float"}:
            return float(value)
        if target in {bool, "bool"}:
            return _to_bool(value)
    return value


def x__coerce_value__mutmut_21(value: Any, annotation: Any, current: Any) -> Any:
    if isinstance(value, str):
        if isinstance(current, bool):
            return _to_bool(value)
        if isinstance(current, int):
            return int(value)
        if isinstance(current, float):
            return float(value)
        if isinstance(current, Path):
            return Path(value)
    if isinstance(value, (int, float)) and annotation in {int, float}:
        return annotation(value)
    if isinstance(value, bool) and annotation is bool:
        return value
    if isinstance(value, Path) and annotation in {Path, str | Path}:
        return value
    if isinstance(value, str):
        target = _resolve_target_type(annotation, current)
        if target in {str, None}:
            return value
        if target is Path:
            return Path(value)
        if target not in {int, "int"}:
            return int(value)
        if target in {float, "float"}:
            return float(value)
        if target in {bool, "bool"}:
            return _to_bool(value)
    return value


def x__coerce_value__mutmut_22(value: Any, annotation: Any, current: Any) -> Any:
    if isinstance(value, str):
        if isinstance(current, bool):
            return _to_bool(value)
        if isinstance(current, int):
            return int(value)
        if isinstance(current, float):
            return float(value)
        if isinstance(current, Path):
            return Path(value)
    if isinstance(value, (int, float)) and annotation in {int, float}:
        return annotation(value)
    if isinstance(value, bool) and annotation is bool:
        return value
    if isinstance(value, Path) and annotation in {Path, str | Path}:
        return value
    if isinstance(value, str):
        target = _resolve_target_type(annotation, current)
        if target in {str, None}:
            return value
        if target is Path:
            return Path(value)
        if target in {int, "XXintXX"}:
            return int(value)
        if target in {float, "float"}:
            return float(value)
        if target in {bool, "bool"}:
            return _to_bool(value)
    return value


def x__coerce_value__mutmut_23(value: Any, annotation: Any, current: Any) -> Any:
    if isinstance(value, str):
        if isinstance(current, bool):
            return _to_bool(value)
        if isinstance(current, int):
            return int(value)
        if isinstance(current, float):
            return float(value)
        if isinstance(current, Path):
            return Path(value)
    if isinstance(value, (int, float)) and annotation in {int, float}:
        return annotation(value)
    if isinstance(value, bool) and annotation is bool:
        return value
    if isinstance(value, Path) and annotation in {Path, str | Path}:
        return value
    if isinstance(value, str):
        target = _resolve_target_type(annotation, current)
        if target in {str, None}:
            return value
        if target is Path:
            return Path(value)
        if target in {int, "INT"}:
            return int(value)
        if target in {float, "float"}:
            return float(value)
        if target in {bool, "bool"}:
            return _to_bool(value)
    return value


def x__coerce_value__mutmut_24(value: Any, annotation: Any, current: Any) -> Any:
    if isinstance(value, str):
        if isinstance(current, bool):
            return _to_bool(value)
        if isinstance(current, int):
            return int(value)
        if isinstance(current, float):
            return float(value)
        if isinstance(current, Path):
            return Path(value)
    if isinstance(value, (int, float)) and annotation in {int, float}:
        return annotation(value)
    if isinstance(value, bool) and annotation is bool:
        return value
    if isinstance(value, Path) and annotation in {Path, str | Path}:
        return value
    if isinstance(value, str):
        target = _resolve_target_type(annotation, current)
        if target in {str, None}:
            return value
        if target is Path:
            return Path(value)
        if target in {int, "int"}:
            return int(None)
        if target in {float, "float"}:
            return float(value)
        if target in {bool, "bool"}:
            return _to_bool(value)
    return value


def x__coerce_value__mutmut_25(value: Any, annotation: Any, current: Any) -> Any:
    if isinstance(value, str):
        if isinstance(current, bool):
            return _to_bool(value)
        if isinstance(current, int):
            return int(value)
        if isinstance(current, float):
            return float(value)
        if isinstance(current, Path):
            return Path(value)
    if isinstance(value, (int, float)) and annotation in {int, float}:
        return annotation(value)
    if isinstance(value, bool) and annotation is bool:
        return value
    if isinstance(value, Path) and annotation in {Path, str | Path}:
        return value
    if isinstance(value, str):
        target = _resolve_target_type(annotation, current)
        if target in {str, None}:
            return value
        if target is Path:
            return Path(value)
        if target in {int, "int"}:
            return int(value)
        if target not in {float, "float"}:
            return float(value)
        if target in {bool, "bool"}:
            return _to_bool(value)
    return value


def x__coerce_value__mutmut_26(value: Any, annotation: Any, current: Any) -> Any:
    if isinstance(value, str):
        if isinstance(current, bool):
            return _to_bool(value)
        if isinstance(current, int):
            return int(value)
        if isinstance(current, float):
            return float(value)
        if isinstance(current, Path):
            return Path(value)
    if isinstance(value, (int, float)) and annotation in {int, float}:
        return annotation(value)
    if isinstance(value, bool) and annotation is bool:
        return value
    if isinstance(value, Path) and annotation in {Path, str | Path}:
        return value
    if isinstance(value, str):
        target = _resolve_target_type(annotation, current)
        if target in {str, None}:
            return value
        if target is Path:
            return Path(value)
        if target in {int, "int"}:
            return int(value)
        if target in {float, "XXfloatXX"}:
            return float(value)
        if target in {bool, "bool"}:
            return _to_bool(value)
    return value


def x__coerce_value__mutmut_27(value: Any, annotation: Any, current: Any) -> Any:
    if isinstance(value, str):
        if isinstance(current, bool):
            return _to_bool(value)
        if isinstance(current, int):
            return int(value)
        if isinstance(current, float):
            return float(value)
        if isinstance(current, Path):
            return Path(value)
    if isinstance(value, (int, float)) and annotation in {int, float}:
        return annotation(value)
    if isinstance(value, bool) and annotation is bool:
        return value
    if isinstance(value, Path) and annotation in {Path, str | Path}:
        return value
    if isinstance(value, str):
        target = _resolve_target_type(annotation, current)
        if target in {str, None}:
            return value
        if target is Path:
            return Path(value)
        if target in {int, "int"}:
            return int(value)
        if target in {float, "FLOAT"}:
            return float(value)
        if target in {bool, "bool"}:
            return _to_bool(value)
    return value


def x__coerce_value__mutmut_28(value: Any, annotation: Any, current: Any) -> Any:
    if isinstance(value, str):
        if isinstance(current, bool):
            return _to_bool(value)
        if isinstance(current, int):
            return int(value)
        if isinstance(current, float):
            return float(value)
        if isinstance(current, Path):
            return Path(value)
    if isinstance(value, (int, float)) and annotation in {int, float}:
        return annotation(value)
    if isinstance(value, bool) and annotation is bool:
        return value
    if isinstance(value, Path) and annotation in {Path, str | Path}:
        return value
    if isinstance(value, str):
        target = _resolve_target_type(annotation, current)
        if target in {str, None}:
            return value
        if target is Path:
            return Path(value)
        if target in {int, "int"}:
            return int(value)
        if target in {float, "float"}:
            return float(None)
        if target in {bool, "bool"}:
            return _to_bool(value)
    return value


def x__coerce_value__mutmut_29(value: Any, annotation: Any, current: Any) -> Any:
    if isinstance(value, str):
        if isinstance(current, bool):
            return _to_bool(value)
        if isinstance(current, int):
            return int(value)
        if isinstance(current, float):
            return float(value)
        if isinstance(current, Path):
            return Path(value)
    if isinstance(value, (int, float)) and annotation in {int, float}:
        return annotation(value)
    if isinstance(value, bool) and annotation is bool:
        return value
    if isinstance(value, Path) and annotation in {Path, str | Path}:
        return value
    if isinstance(value, str):
        target = _resolve_target_type(annotation, current)
        if target in {str, None}:
            return value
        if target is Path:
            return Path(value)
        if target in {int, "int"}:
            return int(value)
        if target in {float, "float"}:
            return float(value)
        if target not in {bool, "bool"}:
            return _to_bool(value)
    return value


def x__coerce_value__mutmut_30(value: Any, annotation: Any, current: Any) -> Any:
    if isinstance(value, str):
        if isinstance(current, bool):
            return _to_bool(value)
        if isinstance(current, int):
            return int(value)
        if isinstance(current, float):
            return float(value)
        if isinstance(current, Path):
            return Path(value)
    if isinstance(value, (int, float)) and annotation in {int, float}:
        return annotation(value)
    if isinstance(value, bool) and annotation is bool:
        return value
    if isinstance(value, Path) and annotation in {Path, str | Path}:
        return value
    if isinstance(value, str):
        target = _resolve_target_type(annotation, current)
        if target in {str, None}:
            return value
        if target is Path:
            return Path(value)
        if target in {int, "int"}:
            return int(value)
        if target in {float, "float"}:
            return float(value)
        if target in {bool, "XXboolXX"}:
            return _to_bool(value)
    return value


def x__coerce_value__mutmut_31(value: Any, annotation: Any, current: Any) -> Any:
    if isinstance(value, str):
        if isinstance(current, bool):
            return _to_bool(value)
        if isinstance(current, int):
            return int(value)
        if isinstance(current, float):
            return float(value)
        if isinstance(current, Path):
            return Path(value)
    if isinstance(value, (int, float)) and annotation in {int, float}:
        return annotation(value)
    if isinstance(value, bool) and annotation is bool:
        return value
    if isinstance(value, Path) and annotation in {Path, str | Path}:
        return value
    if isinstance(value, str):
        target = _resolve_target_type(annotation, current)
        if target in {str, None}:
            return value
        if target is Path:
            return Path(value)
        if target in {int, "int"}:
            return int(value)
        if target in {float, "float"}:
            return float(value)
        if target in {bool, "BOOL"}:
            return _to_bool(value)
    return value


def x__coerce_value__mutmut_32(value: Any, annotation: Any, current: Any) -> Any:
    if isinstance(value, str):
        if isinstance(current, bool):
            return _to_bool(value)
        if isinstance(current, int):
            return int(value)
        if isinstance(current, float):
            return float(value)
        if isinstance(current, Path):
            return Path(value)
    if isinstance(value, (int, float)) and annotation in {int, float}:
        return annotation(value)
    if isinstance(value, bool) and annotation is bool:
        return value
    if isinstance(value, Path) and annotation in {Path, str | Path}:
        return value
    if isinstance(value, str):
        target = _resolve_target_type(annotation, current)
        if target in {str, None}:
            return value
        if target is Path:
            return Path(value)
        if target in {int, "int"}:
            return int(value)
        if target in {float, "float"}:
            return float(value)
        if target in {bool, "bool"}:
            return _to_bool(None)
    return value

x__coerce_value__mutmut_mutants : ClassVar[MutantDict] = {
'x__coerce_value__mutmut_1': x__coerce_value__mutmut_1, 
    'x__coerce_value__mutmut_2': x__coerce_value__mutmut_2, 
    'x__coerce_value__mutmut_3': x__coerce_value__mutmut_3, 
    'x__coerce_value__mutmut_4': x__coerce_value__mutmut_4, 
    'x__coerce_value__mutmut_5': x__coerce_value__mutmut_5, 
    'x__coerce_value__mutmut_6': x__coerce_value__mutmut_6, 
    'x__coerce_value__mutmut_7': x__coerce_value__mutmut_7, 
    'x__coerce_value__mutmut_8': x__coerce_value__mutmut_8, 
    'x__coerce_value__mutmut_9': x__coerce_value__mutmut_9, 
    'x__coerce_value__mutmut_10': x__coerce_value__mutmut_10, 
    'x__coerce_value__mutmut_11': x__coerce_value__mutmut_11, 
    'x__coerce_value__mutmut_12': x__coerce_value__mutmut_12, 
    'x__coerce_value__mutmut_13': x__coerce_value__mutmut_13, 
    'x__coerce_value__mutmut_14': x__coerce_value__mutmut_14, 
    'x__coerce_value__mutmut_15': x__coerce_value__mutmut_15, 
    'x__coerce_value__mutmut_16': x__coerce_value__mutmut_16, 
    'x__coerce_value__mutmut_17': x__coerce_value__mutmut_17, 
    'x__coerce_value__mutmut_18': x__coerce_value__mutmut_18, 
    'x__coerce_value__mutmut_19': x__coerce_value__mutmut_19, 
    'x__coerce_value__mutmut_20': x__coerce_value__mutmut_20, 
    'x__coerce_value__mutmut_21': x__coerce_value__mutmut_21, 
    'x__coerce_value__mutmut_22': x__coerce_value__mutmut_22, 
    'x__coerce_value__mutmut_23': x__coerce_value__mutmut_23, 
    'x__coerce_value__mutmut_24': x__coerce_value__mutmut_24, 
    'x__coerce_value__mutmut_25': x__coerce_value__mutmut_25, 
    'x__coerce_value__mutmut_26': x__coerce_value__mutmut_26, 
    'x__coerce_value__mutmut_27': x__coerce_value__mutmut_27, 
    'x__coerce_value__mutmut_28': x__coerce_value__mutmut_28, 
    'x__coerce_value__mutmut_29': x__coerce_value__mutmut_29, 
    'x__coerce_value__mutmut_30': x__coerce_value__mutmut_30, 
    'x__coerce_value__mutmut_31': x__coerce_value__mutmut_31, 
    'x__coerce_value__mutmut_32': x__coerce_value__mutmut_32
}

def _coerce_value(*args, **kwargs):
    result = _mutmut_trampoline(x__coerce_value__mutmut_orig, x__coerce_value__mutmut_mutants, args, kwargs)
    return result 

_coerce_value.__signature__ = _mutmut_signature(x__coerce_value__mutmut_orig)
x__coerce_value__mutmut_orig.__name__ = 'x__coerce_value'


@dataclass
class TrainingConfig:
    """Configuration for ``run_hf_trainer``.

    Fields intentionally mirror a subset of the HF trainer arguments along with
    Codex-specific toggles.
    """

    model_name: str = "sshleifer/tiny-gpt2"
    tokenizer_name: str | None = None
    dataset_path: Path = Path("data/train.jsonl")
    eval_dataset_path: Path | None = None
    output_dir: Path = Path("artifacts/hf_trainer")
    batch_size: int = 8
    eval_batch_size: int = 8
    learning_rate: float = 5e-5
    num_train_epochs: int = 3
    max_seq_length: int = 256
    gradient_accumulation_steps: int = 1
    precision: str = "fp32"
    seed: int = 42
    deterministic: bool = True
    val_split: float = 0.0
    mlflow_tracking_uri: str | None = None
    dataset_version: str | None = None
    dataset_hash: str | None = None
    use_lora: bool = False
    lora_r: int | None = None
    lora_alpha: float | None = None
    lora_dropout: float | None = None
    lora_task_type: str | None = None

    def validate(self) -> None:
        """Validate numeric and categorical constraints."""

        errors: list[str] = []
        if self.batch_size < 1:
            errors.append("batch_size must be >= 1")
        if self.eval_batch_size < 1:
            errors.append("eval_batch_size must be >= 1")
        if self.learning_rate <= 0:
            errors.append("learning_rate must be > 0")
        if self.num_train_epochs < 0:
            errors.append("num_train_epochs must be >= 0")
        if self.gradient_accumulation_steps < 1:
            errors.append("gradient_accumulation_steps must be >= 1")
        if self.precision not in _VALID_PRECISIONS:
            errors.append(f"precision must be one of {sorted(_VALID_PRECISIONS)}")
        if not (0 <= self.val_split < 1 or self.val_split == 0):
            errors.append("val_split must be in the range [0, 1)")
        if not (0 <= self.seed < 2**32):
            errors.append("seed must be in [0, 2**32)")
        if self.use_lora and self.lora_r is not None and self.lora_r <= 0:
            errors.append("lora_r must be positive when use_lora is enabled")
        if errors:
            raise ValueError("; ".join(errors))

    def as_dict(self) -> dict[str, Any]:
        """Return a ``dict`` copy of the configuration."""

        return {field.name: getattr(self, field.name) for field in fields(self)}

    def replace(self, **updates: Any) -> "TrainingConfig":
        """Return a new config with ``updates`` applied."""

        data = self.as_dict()
        data.update(updates)
        cfg = TrainingConfig(**data)
        cfg.validate()
        return cfg

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, Any]) -> "TrainingConfig":
        """Build a config from a mapping, coercing values when possible."""

        base = cls()
        type_hints = get_type_hints(cls)
        data: MutableMapping[str, Any] = {
            field.name: getattr(base, field.name) for field in fields(cls)
        }
        for field in fields(cls):
            if field.name not in mapping:
                continue
            raw = mapping[field.name]
            annotation = type_hints.get(field.name, field.type)
            data[field.name] = _coerce_value(raw, annotation, data[field.name])
        cfg = cls(**data)
        cfg.validate()
        return cfg

    @classmethod
    def from_env(cls, prefix: str = "TRAIN_") -> "TrainingConfig":
        """Construct a config from environment variables."""

        base = cls()
        type_hints = get_type_hints(cls)
        data: MutableMapping[str, Any] = base.as_dict()
        for field in fields(cls):
            env_name = f"{prefix}{field.name}".upper()
            if env_name not in os.environ:
                continue
            raw = os.environ[env_name]
            annotation = type_hints.get(field.name, field.type)
            data[field.name] = _coerce_value(raw, annotation, data[field.name])
        cfg = cls(**data)
        cfg.validate()
        return cfg


__all__ = ["TrainingConfig"]
