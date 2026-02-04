"""
Config Module

This module provides functionality for config.

Usage:
    from archive.config import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations
import logging
logger = logging.getLogger(__name__)
"""Configuration helpers for the archive command surface."""


import os
import typing as _t
from dataclasses import asdict, dataclass, field
from pathlib import Path

if _t.TYPE_CHECKING:  # pragma: no cover - typing helpers
    from .backend import ArchiveConfig as _ArchiveConfig
    from .retry import RetryConfig as _RetryConfig
else:  # pragma: no cover - runtime fallback for type hints
    _ArchiveConfig = _t.Any  # type: ignore[assignment]
    _RetryConfig = _t.Any  # type: ignore[assignment]

try:  # pragma: no cover - Python 3.11+
    import tomllib as _toml
except ModuleNotFoundError:  # pragma: no cover - fallback for <3.11
    import tomli as _toml  # type: ignore


_T = _t.TypeVar("_T")
_ENV_BOOL_TRUE = {"1", "true", "yes", "on", "enabled"}
_ENV_BOOL_FALSE = {"0", "false", "no", "off", "disabled"}
_SUPPORTED_BACKENDS = {"sqlite", "postgres", "mariadb"}
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


def x__coerce_bool__mutmut_orig(value: object, *, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    if isinstance(value, int | float):
        return bool(value)
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in _ENV_BOOL_TRUE:
            return True
        if lowered in _ENV_BOOL_FALSE:
            return False
    return default


def x__coerce_bool__mutmut_1(value: object, *, default: bool = True) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    if isinstance(value, int | float):
        return bool(value)
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in _ENV_BOOL_TRUE:
            return True
        if lowered in _ENV_BOOL_FALSE:
            return False
    return default


def x__coerce_bool__mutmut_2(value: object, *, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is not None:
        return default
    if isinstance(value, int | float):
        return bool(value)
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in _ENV_BOOL_TRUE:
            return True
        if lowered in _ENV_BOOL_FALSE:
            return False
    return default


def x__coerce_bool__mutmut_3(value: object, *, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    if isinstance(value, int | float):
        return bool(None)
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in _ENV_BOOL_TRUE:
            return True
        if lowered in _ENV_BOOL_FALSE:
            return False
    return default


def x__coerce_bool__mutmut_4(value: object, *, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    if isinstance(value, int | float):
        return bool(value)
    if isinstance(value, str):
        lowered = None
        if lowered in _ENV_BOOL_TRUE:
            return True
        if lowered in _ENV_BOOL_FALSE:
            return False
    return default


def x__coerce_bool__mutmut_5(value: object, *, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    if isinstance(value, int | float):
        return bool(value)
    if isinstance(value, str):
        lowered = value.strip().upper()
        if lowered in _ENV_BOOL_TRUE:
            return True
        if lowered in _ENV_BOOL_FALSE:
            return False
    return default


def x__coerce_bool__mutmut_6(value: object, *, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    if isinstance(value, int | float):
        return bool(value)
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered not in _ENV_BOOL_TRUE:
            return True
        if lowered in _ENV_BOOL_FALSE:
            return False
    return default


def x__coerce_bool__mutmut_7(value: object, *, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    if isinstance(value, int | float):
        return bool(value)
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in _ENV_BOOL_TRUE:
            return False
        if lowered in _ENV_BOOL_FALSE:
            return False
    return default


def x__coerce_bool__mutmut_8(value: object, *, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    if isinstance(value, int | float):
        return bool(value)
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in _ENV_BOOL_TRUE:
            return True
        if lowered not in _ENV_BOOL_FALSE:
            return False
    return default


def x__coerce_bool__mutmut_9(value: object, *, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    if isinstance(value, int | float):
        return bool(value)
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in _ENV_BOOL_TRUE:
            return True
        if lowered in _ENV_BOOL_FALSE:
            return True
    return default

x__coerce_bool__mutmut_mutants : ClassVar[MutantDict] = {
'x__coerce_bool__mutmut_1': x__coerce_bool__mutmut_1, 
    'x__coerce_bool__mutmut_2': x__coerce_bool__mutmut_2, 
    'x__coerce_bool__mutmut_3': x__coerce_bool__mutmut_3, 
    'x__coerce_bool__mutmut_4': x__coerce_bool__mutmut_4, 
    'x__coerce_bool__mutmut_5': x__coerce_bool__mutmut_5, 
    'x__coerce_bool__mutmut_6': x__coerce_bool__mutmut_6, 
    'x__coerce_bool__mutmut_7': x__coerce_bool__mutmut_7, 
    'x__coerce_bool__mutmut_8': x__coerce_bool__mutmut_8, 
    'x__coerce_bool__mutmut_9': x__coerce_bool__mutmut_9
}

def _coerce_bool(*args, **kwargs):
    result = _mutmut_trampoline(x__coerce_bool__mutmut_orig, x__coerce_bool__mutmut_mutants, args, kwargs)
    return result 

_coerce_bool.__signature__ = _mutmut_signature(x__coerce_bool__mutmut_orig)
x__coerce_bool__mutmut_orig.__name__ = 'x__coerce_bool'


def x__coerce_int__mutmut_orig(value: object, *, default: int) -> int:
    if isinstance(value, bool):  # pragma: no branch - bool is int subclass
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError as e:
            logger.debug(f"ValueError: {e}")
            logger.warning(f"ValueError: {e}", exc_info=True)
            return default
    return default


def x__coerce_int__mutmut_1(value: object, *, default: int) -> int:
    if isinstance(value, bool):  # pragma: no branch - bool is int subclass
        return int(None)
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError as e:
            logger.debug(f"ValueError: {e}")
            logger.warning(f"ValueError: {e}", exc_info=True)
            return default
    return default


def x__coerce_int__mutmut_2(value: object, *, default: int) -> int:
    if isinstance(value, bool):  # pragma: no branch - bool is int subclass
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(None)
        except ValueError as e:
            logger.debug(f"ValueError: {e}")
            logger.warning(f"ValueError: {e}", exc_info=True)
            return default
    return default


def x__coerce_int__mutmut_3(value: object, *, default: int) -> int:
    if isinstance(value, bool):  # pragma: no branch - bool is int subclass
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError as e:
            logger.debug(None)
            logger.warning(f"ValueError: {e}", exc_info=True)
            return default
    return default


def x__coerce_int__mutmut_4(value: object, *, default: int) -> int:
    if isinstance(value, bool):  # pragma: no branch - bool is int subclass
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError as e:
            logger.debug(f"ValueError: {e}")
            logger.warning(None, exc_info=True)
            return default
    return default


def x__coerce_int__mutmut_5(value: object, *, default: int) -> int:
    if isinstance(value, bool):  # pragma: no branch - bool is int subclass
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError as e:
            logger.debug(f"ValueError: {e}")
            logger.warning(f"ValueError: {e}", exc_info=None)
            return default
    return default


def x__coerce_int__mutmut_6(value: object, *, default: int) -> int:
    if isinstance(value, bool):  # pragma: no branch - bool is int subclass
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError as e:
            logger.debug(f"ValueError: {e}")
            logger.warning(exc_info=True)
            return default
    return default


def x__coerce_int__mutmut_7(value: object, *, default: int) -> int:
    if isinstance(value, bool):  # pragma: no branch - bool is int subclass
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError as e:
            logger.debug(f"ValueError: {e}")
            logger.warning(f"ValueError: {e}", )
            return default
    return default


def x__coerce_int__mutmut_8(value: object, *, default: int) -> int:
    if isinstance(value, bool):  # pragma: no branch - bool is int subclass
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError as e:
            logger.debug(f"ValueError: {e}")
            logger.warning(f"ValueError: {e}", exc_info=False)
            return default
    return default

x__coerce_int__mutmut_mutants : ClassVar[MutantDict] = {
'x__coerce_int__mutmut_1': x__coerce_int__mutmut_1, 
    'x__coerce_int__mutmut_2': x__coerce_int__mutmut_2, 
    'x__coerce_int__mutmut_3': x__coerce_int__mutmut_3, 
    'x__coerce_int__mutmut_4': x__coerce_int__mutmut_4, 
    'x__coerce_int__mutmut_5': x__coerce_int__mutmut_5, 
    'x__coerce_int__mutmut_6': x__coerce_int__mutmut_6, 
    'x__coerce_int__mutmut_7': x__coerce_int__mutmut_7, 
    'x__coerce_int__mutmut_8': x__coerce_int__mutmut_8
}

def _coerce_int(*args, **kwargs):
    result = _mutmut_trampoline(x__coerce_int__mutmut_orig, x__coerce_int__mutmut_mutants, args, kwargs)
    return result 

_coerce_int.__signature__ = _mutmut_signature(x__coerce_int__mutmut_orig)
x__coerce_int__mutmut_orig.__name__ = 'x__coerce_int'


def x__coerce_float__mutmut_orig(value: object, *, default: float) -> float:
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError as e:
            logger.debug(f"ValueError: {e}")
            logger.warning(f"ValueError: {e}", exc_info=True)
            return default
    return default


def x__coerce_float__mutmut_1(value: object, *, default: float) -> float:
    if isinstance(value, int | float):
        return float(None)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError as e:
            logger.debug(f"ValueError: {e}")
            logger.warning(f"ValueError: {e}", exc_info=True)
            return default
    return default


def x__coerce_float__mutmut_2(value: object, *, default: float) -> float:
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        try:
            return float(None)
        except ValueError as e:
            logger.debug(f"ValueError: {e}")
            logger.warning(f"ValueError: {e}", exc_info=True)
            return default
    return default


def x__coerce_float__mutmut_3(value: object, *, default: float) -> float:
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError as e:
            logger.debug(None)
            logger.warning(f"ValueError: {e}", exc_info=True)
            return default
    return default


def x__coerce_float__mutmut_4(value: object, *, default: float) -> float:
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError as e:
            logger.debug(f"ValueError: {e}")
            logger.warning(None, exc_info=True)
            return default
    return default


def x__coerce_float__mutmut_5(value: object, *, default: float) -> float:
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError as e:
            logger.debug(f"ValueError: {e}")
            logger.warning(f"ValueError: {e}", exc_info=None)
            return default
    return default


def x__coerce_float__mutmut_6(value: object, *, default: float) -> float:
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError as e:
            logger.debug(f"ValueError: {e}")
            logger.warning(exc_info=True)
            return default
    return default


def x__coerce_float__mutmut_7(value: object, *, default: float) -> float:
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError as e:
            logger.debug(f"ValueError: {e}")
            logger.warning(f"ValueError: {e}", )
            return default
    return default


def x__coerce_float__mutmut_8(value: object, *, default: float) -> float:
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError as e:
            logger.debug(f"ValueError: {e}")
            logger.warning(f"ValueError: {e}", exc_info=False)
            return default
    return default

x__coerce_float__mutmut_mutants : ClassVar[MutantDict] = {
'x__coerce_float__mutmut_1': x__coerce_float__mutmut_1, 
    'x__coerce_float__mutmut_2': x__coerce_float__mutmut_2, 
    'x__coerce_float__mutmut_3': x__coerce_float__mutmut_3, 
    'x__coerce_float__mutmut_4': x__coerce_float__mutmut_4, 
    'x__coerce_float__mutmut_5': x__coerce_float__mutmut_5, 
    'x__coerce_float__mutmut_6': x__coerce_float__mutmut_6, 
    'x__coerce_float__mutmut_7': x__coerce_float__mutmut_7, 
    'x__coerce_float__mutmut_8': x__coerce_float__mutmut_8
}

def _coerce_float(*args, **kwargs):
    result = _mutmut_trampoline(x__coerce_float__mutmut_orig, x__coerce_float__mutmut_mutants, args, kwargs)
    return result 

_coerce_float.__signature__ = _mutmut_signature(x__coerce_float__mutmut_orig)
x__coerce_float__mutmut_orig.__name__ = 'x__coerce_float'


def x__load_toml__mutmut_orig(path: Path) -> dict[str, _t.Any]:
    if not path.exists():
        raise FileNotFoundError(f"Configuration file does not exist: {path}")
    with path.open("rb") as handle:
        data = _toml.load(handle)
    if not isinstance(data, dict):  # pragma: no cover - defensive
        raise ValueError("TOML configuration must yield a table at the root level")
    return data


def x__load_toml__mutmut_1(path: Path) -> dict[str, _t.Any]:
    if path.exists():
        raise FileNotFoundError(f"Configuration file does not exist: {path}")
    with path.open("rb") as handle:
        data = _toml.load(handle)
    if not isinstance(data, dict):  # pragma: no cover - defensive
        raise ValueError("TOML configuration must yield a table at the root level")
    return data


def x__load_toml__mutmut_2(path: Path) -> dict[str, _t.Any]:
    if not path.exists():
        raise FileNotFoundError(None)
    with path.open("rb") as handle:
        data = _toml.load(handle)
    if not isinstance(data, dict):  # pragma: no cover - defensive
        raise ValueError("TOML configuration must yield a table at the root level")
    return data


def x__load_toml__mutmut_3(path: Path) -> dict[str, _t.Any]:
    if not path.exists():
        raise FileNotFoundError(f"Configuration file does not exist: {path}")
    with path.open(None) as handle:
        data = _toml.load(handle)
    if not isinstance(data, dict):  # pragma: no cover - defensive
        raise ValueError("TOML configuration must yield a table at the root level")
    return data


def x__load_toml__mutmut_4(path: Path) -> dict[str, _t.Any]:
    if not path.exists():
        raise FileNotFoundError(f"Configuration file does not exist: {path}")
    with path.open("XXrbXX") as handle:
        data = _toml.load(handle)
    if not isinstance(data, dict):  # pragma: no cover - defensive
        raise ValueError("TOML configuration must yield a table at the root level")
    return data


def x__load_toml__mutmut_5(path: Path) -> dict[str, _t.Any]:
    if not path.exists():
        raise FileNotFoundError(f"Configuration file does not exist: {path}")
    with path.open("RB") as handle:
        data = _toml.load(handle)
    if not isinstance(data, dict):  # pragma: no cover - defensive
        raise ValueError("TOML configuration must yield a table at the root level")
    return data


def x__load_toml__mutmut_6(path: Path) -> dict[str, _t.Any]:
    if not path.exists():
        raise FileNotFoundError(f"Configuration file does not exist: {path}")
    with path.open("rb") as handle:
        data = None
    if not isinstance(data, dict):  # pragma: no cover - defensive
        raise ValueError("TOML configuration must yield a table at the root level")
    return data


def x__load_toml__mutmut_7(path: Path) -> dict[str, _t.Any]:
    if not path.exists():
        raise FileNotFoundError(f"Configuration file does not exist: {path}")
    with path.open("rb") as handle:
        data = _toml.load(None)
    if not isinstance(data, dict):  # pragma: no cover - defensive
        raise ValueError("TOML configuration must yield a table at the root level")
    return data


def x__load_toml__mutmut_8(path: Path) -> dict[str, _t.Any]:
    if not path.exists():
        raise FileNotFoundError(f"Configuration file does not exist: {path}")
    with path.open("rb") as handle:
        data = _toml.load(handle)
    if isinstance(data, dict):  # pragma: no cover - defensive
        raise ValueError("TOML configuration must yield a table at the root level")
    return data


def x__load_toml__mutmut_9(path: Path) -> dict[str, _t.Any]:
    if not path.exists():
        raise FileNotFoundError(f"Configuration file does not exist: {path}")
    with path.open("rb") as handle:
        data = _toml.load(handle)
    if not isinstance(data, dict):  # pragma: no cover - defensive
        raise ValueError(None)
    return data


def x__load_toml__mutmut_10(path: Path) -> dict[str, _t.Any]:
    if not path.exists():
        raise FileNotFoundError(f"Configuration file does not exist: {path}")
    with path.open("rb") as handle:
        data = _toml.load(handle)
    if not isinstance(data, dict):  # pragma: no cover - defensive
        raise ValueError("XXTOML configuration must yield a table at the root levelXX")
    return data


def x__load_toml__mutmut_11(path: Path) -> dict[str, _t.Any]:
    if not path.exists():
        raise FileNotFoundError(f"Configuration file does not exist: {path}")
    with path.open("rb") as handle:
        data = _toml.load(handle)
    if not isinstance(data, dict):  # pragma: no cover - defensive
        raise ValueError("toml configuration must yield a table at the root level")
    return data


def x__load_toml__mutmut_12(path: Path) -> dict[str, _t.Any]:
    if not path.exists():
        raise FileNotFoundError(f"Configuration file does not exist: {path}")
    with path.open("rb") as handle:
        data = _toml.load(handle)
    if not isinstance(data, dict):  # pragma: no cover - defensive
        raise ValueError("TOML CONFIGURATION MUST YIELD A TABLE AT THE ROOT LEVEL")
    return data

x__load_toml__mutmut_mutants : ClassVar[MutantDict] = {
'x__load_toml__mutmut_1': x__load_toml__mutmut_1, 
    'x__load_toml__mutmut_2': x__load_toml__mutmut_2, 
    'x__load_toml__mutmut_3': x__load_toml__mutmut_3, 
    'x__load_toml__mutmut_4': x__load_toml__mutmut_4, 
    'x__load_toml__mutmut_5': x__load_toml__mutmut_5, 
    'x__load_toml__mutmut_6': x__load_toml__mutmut_6, 
    'x__load_toml__mutmut_7': x__load_toml__mutmut_7, 
    'x__load_toml__mutmut_8': x__load_toml__mutmut_8, 
    'x__load_toml__mutmut_9': x__load_toml__mutmut_9, 
    'x__load_toml__mutmut_10': x__load_toml__mutmut_10, 
    'x__load_toml__mutmut_11': x__load_toml__mutmut_11, 
    'x__load_toml__mutmut_12': x__load_toml__mutmut_12
}

def _load_toml(*args, **kwargs):
    result = _mutmut_trampoline(x__load_toml__mutmut_orig, x__load_toml__mutmut_mutants, args, kwargs)
    return result 

_load_toml.__signature__ = _mutmut_signature(x__load_toml__mutmut_orig)
x__load_toml__mutmut_orig.__name__ = 'x__load_toml'


def x__mark_explicit_fields__mutmut_orig(instance: _T, keys: _t.Iterable[str]) -> _T:
    """Attach explicit field markers to frozen dataclass instances."""

    object.__setattr__(instance, "_codex_explicit_fields", frozenset(keys))
    return instance


def x__mark_explicit_fields__mutmut_1(instance: _T, keys: _t.Iterable[str]) -> _T:
    """Attach explicit field markers to frozen dataclass instances."""

    object.__setattr__(None, "_codex_explicit_fields", frozenset(keys))
    return instance


def x__mark_explicit_fields__mutmut_2(instance: _T, keys: _t.Iterable[str]) -> _T:
    """Attach explicit field markers to frozen dataclass instances."""

    object.__setattr__(instance, None, frozenset(keys))
    return instance


def x__mark_explicit_fields__mutmut_3(instance: _T, keys: _t.Iterable[str]) -> _T:
    """Attach explicit field markers to frozen dataclass instances."""

    object.__setattr__(instance, "_codex_explicit_fields", None)
    return instance


def x__mark_explicit_fields__mutmut_4(instance: _T, keys: _t.Iterable[str]) -> _T:
    """Attach explicit field markers to frozen dataclass instances."""

    object.__setattr__("_codex_explicit_fields", frozenset(keys))
    return instance


def x__mark_explicit_fields__mutmut_5(instance: _T, keys: _t.Iterable[str]) -> _T:
    """Attach explicit field markers to frozen dataclass instances."""

    object.__setattr__(instance, frozenset(keys))
    return instance


def x__mark_explicit_fields__mutmut_6(instance: _T, keys: _t.Iterable[str]) -> _T:
    """Attach explicit field markers to frozen dataclass instances."""

    object.__setattr__(instance, "_codex_explicit_fields", )
    return instance


def x__mark_explicit_fields__mutmut_7(instance: _T, keys: _t.Iterable[str]) -> _T:
    """Attach explicit field markers to frozen dataclass instances."""

    object.__setattr__(instance, "XX_codex_explicit_fieldsXX", frozenset(keys))
    return instance


def x__mark_explicit_fields__mutmut_8(instance: _T, keys: _t.Iterable[str]) -> _T:
    """Attach explicit field markers to frozen dataclass instances."""

    object.__setattr__(instance, "_CODEX_EXPLICIT_FIELDS", frozenset(keys))
    return instance


def x__mark_explicit_fields__mutmut_9(instance: _T, keys: _t.Iterable[str]) -> _T:
    """Attach explicit field markers to frozen dataclass instances."""

    object.__setattr__(instance, "_codex_explicit_fields", frozenset(None))
    return instance

x__mark_explicit_fields__mutmut_mutants : ClassVar[MutantDict] = {
'x__mark_explicit_fields__mutmut_1': x__mark_explicit_fields__mutmut_1, 
    'x__mark_explicit_fields__mutmut_2': x__mark_explicit_fields__mutmut_2, 
    'x__mark_explicit_fields__mutmut_3': x__mark_explicit_fields__mutmut_3, 
    'x__mark_explicit_fields__mutmut_4': x__mark_explicit_fields__mutmut_4, 
    'x__mark_explicit_fields__mutmut_5': x__mark_explicit_fields__mutmut_5, 
    'x__mark_explicit_fields__mutmut_6': x__mark_explicit_fields__mutmut_6, 
    'x__mark_explicit_fields__mutmut_7': x__mark_explicit_fields__mutmut_7, 
    'x__mark_explicit_fields__mutmut_8': x__mark_explicit_fields__mutmut_8, 
    'x__mark_explicit_fields__mutmut_9': x__mark_explicit_fields__mutmut_9
}

def _mark_explicit_fields(*args, **kwargs):
    result = _mutmut_trampoline(x__mark_explicit_fields__mutmut_orig, x__mark_explicit_fields__mutmut_mutants, args, kwargs)
    return result 

_mark_explicit_fields.__signature__ = _mutmut_signature(x__mark_explicit_fields__mutmut_orig)
x__mark_explicit_fields__mutmut_orig.__name__ = 'x__mark_explicit_fields'


@dataclass(frozen=True)
class BackendConfig:
    """Backend connection information."""

    backend: str = "sqlite"
    url: str = "sqlite:///./.codex/archive.sqlite"

    def __post_init__(self) -> None:  # pragma: no cover - exercised indirectly
        object.__setattr__(self, "backend", self.backend.lower())
        if self.backend not in _SUPPORTED_BACKENDS:
            raise ValueError(f"Unsupported archive backend: {self.backend}")
        if not self.url:
            raise ValueError("Archive URL must be provided")

    @classmethod
    def from_dict(cls, payload: dict[str, _t.Any]) -> BackendConfig:
        backend = payload.get("backend", cls.backend)
        url = payload.get("url", cls.url)
        return cls(backend=backend, url=url)

    @classmethod
    def from_env(cls, env: dict[str, str]) -> BackendConfig:
        backend = env.get("CODEX_ARCHIVE_BACKEND")
        url = env.get("CODEX_ARCHIVE_URL")
        payload = {}
        if backend:
            payload["backend"] = backend
        if url:
            payload["url"] = url
            if not backend:
                from .backend import infer_backend

                payload["backend"] = infer_backend(url)
        return _mark_explicit_fields(cls.from_dict(payload), payload.keys())

    def to_archive_config(self) -> _ArchiveConfig:
        from .backend import ArchiveConfig

        return ArchiveConfig(url=self.url, backend=self.backend)


@dataclass(frozen=True)
class LoggingConfig:
    """Logging configuration for archive commands."""

    level: str = "info"
    format: str = "text"
    evidence_file: Path | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "level", self.level.lower())
        object.__setattr__(self, "format", self.format.lower())
        if self.format not in {"text", "json"}:
            raise ValueError("Logging format must be either 'text' or 'json'")

    @classmethod
    def from_dict(cls, payload: dict[str, _t.Any]) -> LoggingConfig:
        return cls(
            level=payload.get("level", cls.level),
            format=payload.get("format", cls.format),
            evidence_file=Path(payload["evidence_file"]) if payload.get("evidence_file") else None,
        )

    @classmethod
    def from_env(cls, env: dict[str, str]) -> LoggingConfig:
        payload: dict[str, _t.Any] = {}
        if env.get("CODEX_ARCHIVE_LOG_LEVEL"):
            payload["level"] = env["CODEX_ARCHIVE_LOG_LEVEL"]
        if env.get("CODEX_ARCHIVE_LOG_FORMAT"):
            payload["format"] = env["CODEX_ARCHIVE_LOG_FORMAT"]
        if env.get("CODEX_ARCHIVE_LOG_EVIDENCE"):
            payload["evidence_file"] = env["CODEX_ARCHIVE_LOG_EVIDENCE"]
        return _mark_explicit_fields(cls.from_dict(payload), payload.keys())


@dataclass(frozen=True)
class RetrySettings:
    """Retry parameters for batch operations."""

    enabled: bool = True
    max_attempts: int = 5
    initial_delay: float = 1.0
    max_delay: float = 32.0
    multiplier: float = 2.0
    jitter: float = 0.1
    seed: int | None = None

    @classmethod
    def from_dict(cls, payload: dict[str, _t.Any]) -> RetrySettings:
        return cls(
            enabled=_coerce_bool(payload.get("enabled"), default=cls.enabled),
            max_attempts=_coerce_int(payload.get("max_attempts"), default=cls.max_attempts),
            initial_delay=_coerce_float(payload.get("initial_delay"), default=cls.initial_delay),
            max_delay=_coerce_float(payload.get("max_delay"), default=cls.max_delay),
            multiplier=_coerce_float(payload.get("multiplier"), default=cls.multiplier),
            jitter=_coerce_float(payload.get("jitter"), default=cls.jitter),
            seed=(
                _coerce_int(payload.get("seed"), default=0)
                if payload.get("seed") is not None
                else None
            ),
        )

    @classmethod
    def from_env(cls, env: dict[str, str]) -> RetrySettings:
        payload: dict[str, _t.Any] = {}
        if env.get("CODEX_ARCHIVE_RETRY_ENABLED"):
            payload["enabled"] = env["CODEX_ARCHIVE_RETRY_ENABLED"]
        if env.get("CODEX_ARCHIVE_RETRY_ATTEMPTS"):
            payload["max_attempts"] = env["CODEX_ARCHIVE_RETRY_ATTEMPTS"]
        if env.get("CODEX_ARCHIVE_RETRY_INITIAL"):
            payload["initial_delay"] = env["CODEX_ARCHIVE_RETRY_INITIAL"]
        if env.get("CODEX_ARCHIVE_RETRY_MAX"):
            payload["max_delay"] = env["CODEX_ARCHIVE_RETRY_MAX"]
        if env.get("CODEX_ARCHIVE_RETRY_MULTIPLIER"):
            payload["multiplier"] = env["CODEX_ARCHIVE_RETRY_MULTIPLIER"]
        if env.get("CODEX_ARCHIVE_RETRY_JITTER"):
            payload["jitter"] = env["CODEX_ARCHIVE_RETRY_JITTER"]
        if env.get("CODEX_ARCHIVE_RETRY_SEED"):
            payload["seed"] = env["CODEX_ARCHIVE_RETRY_SEED"]
        return _mark_explicit_fields(cls.from_dict(payload), payload.keys())

    def to_retry_config(self) -> _RetryConfig:
        from .retry import RetryConfig

        return RetryConfig(
            enabled=self.enabled,
            max_attempts=self.max_attempts,
            initial_delay=self.initial_delay,
            max_delay=self.max_delay,
            multiplier=self.multiplier,
            jitter=self.jitter,
            seed=self.seed,
        )


@dataclass(frozen=True)
class BatchConfig:
    """Batch execution parameters."""

    concurrent: int = 4
    progress_interval: int = 10
    results_path: Path | None = None

    @classmethod
    def from_dict(cls, payload: dict[str, _t.Any]) -> BatchConfig:
        return cls(
            concurrent=max(1, _coerce_int(payload.get("concurrent"), default=cls.concurrent)),
            progress_interval=max(
                1, _coerce_int(payload.get("progress_interval"), default=cls.progress_interval)
            ),
            results_path=Path(payload["results_path"]) if payload.get("results_path") else None,
        )

    @classmethod
    def from_env(cls, env: dict[str, str]) -> BatchConfig:
        payload: dict[str, _t.Any] = {}
        if env.get("CODEX_ARCHIVE_BATCH_CONCURRENT"):
            payload["concurrent"] = env["CODEX_ARCHIVE_BATCH_CONCURRENT"]
        if env.get("CODEX_ARCHIVE_BATCH_PROGRESS"):
            payload["progress_interval"] = env["CODEX_ARCHIVE_BATCH_PROGRESS"]
        if env.get("CODEX_ARCHIVE_BATCH_RESULTS"):
            payload["results_path"] = env["CODEX_ARCHIVE_BATCH_RESULTS"]
        return _mark_explicit_fields(cls.from_dict(payload), payload.keys())


@dataclass(frozen=True)
class PerformanceConfig:
    """Performance instrumentation toggles."""

    enabled: bool = True
    emit_to_evidence: bool = True

    @classmethod
    def from_dict(cls, payload: dict[str, _t.Any]) -> PerformanceConfig:
        return cls(
            enabled=_coerce_bool(payload.get("enabled"), default=cls.enabled),
            emit_to_evidence=_coerce_bool(
                payload.get("emit_to_evidence"), default=cls.emit_to_evidence
            ),
        )

    @classmethod
    def from_env(cls, env: dict[str, str]) -> PerformanceConfig:
        payload: dict[str, _t.Any] = {}
        if env.get("CODEX_ARCHIVE_PERF_ENABLED"):
            payload["enabled"] = env["CODEX_ARCHIVE_PERF_ENABLED"]
        if env.get("CODEX_ARCHIVE_PERF_EVIDENCE"):
            payload["emit_to_evidence"] = env["CODEX_ARCHIVE_PERF_EVIDENCE"]
        return _mark_explicit_fields(cls.from_dict(payload), payload.keys())


@dataclass(frozen=True)
class ArchiveAppConfig:
    """Top level configuration loaded for CLI commands."""

    backend: BackendConfig = field(default_factory=BackendConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    retry: RetrySettings = field(default_factory=RetrySettings)
    batch: BatchConfig = field(default_factory=BatchConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)

    @classmethod
    def from_dict(cls, payload: dict[str, _t.Any]) -> ArchiveAppConfig:
        return cls(
            backend=BackendConfig.from_dict(payload.get("backend", {})),
            logging=LoggingConfig.from_dict(payload.get("logging", {})),
            retry=RetrySettings.from_dict(payload.get("retry", {})),
            batch=BatchConfig.from_dict(payload.get("batch", {})),
            performance=PerformanceConfig.from_dict(payload.get("performance", {})),
        )

    @classmethod
    def from_env(cls, env: dict[str, str]) -> ArchiveAppConfig:
        return cls(
            backend=BackendConfig.from_env(env),
            logging=LoggingConfig.from_env(env),
            retry=RetrySettings.from_env(env),
            batch=BatchConfig.from_env(env),
            performance=PerformanceConfig.from_env(env),
        )

    @classmethod
    def from_file(cls, path: Path) -> ArchiveAppConfig:
        data = _load_toml(path)
        return cls.from_dict(data)

    @classmethod
    def load(
        cls,
        *,
        config_file: Path | str | None = None,
        env: _t.Mapping[str, str] | None = None,
    ) -> ArchiveAppConfig:
        runtime_env = dict(os.environ)
        if env is not None:
            runtime_env.update(env)

        file_override = config_file or runtime_env.get("CODEX_ARCHIVE_CONFIG")
        base_config = cls()
        if file_override:
            base_config = cls.from_file(Path(file_override))

        env_config = cls.from_env(runtime_env)

        return cls(
            backend=_merge(base_config.backend, env_config.backend),
            logging=_merge(base_config.logging, env_config.logging),
            retry=_merge(base_config.retry, env_config.retry),
            batch=_merge(base_config.batch, env_config.batch),
            performance=_merge(base_config.performance, env_config.performance),
        )

    def to_backend_config(self) -> _ArchiveConfig:
        return self.backend.to_archive_config()

    def to_dict(self) -> dict[str, _t.Any]:
        return {
            "backend": asdict(self.backend),
            "logging": _serialize_logging(self.logging),
            "retry": asdict(self.retry),
            "batch": _serialize_batch(self.batch),
            "performance": asdict(self.performance),
        }


def x__merge__mutmut_orig(current: _T, override: _T) -> _T:
    if current == override:
        return current
    cls = type(current)
    defaults = asdict(cls())
    payload = asdict(current)
    explicit_fields = getattr(override, "_codex_explicit_fields", None)
    for key, value in asdict(override).items():
        if explicit_fields is not None and key not in explicit_fields:
            continue
        default_value = defaults.get(key)
        if value == default_value and payload.get(key) == value:
            continue
        payload[key] = value
    return cls(**payload)


def x__merge__mutmut_1(current: _T, override: _T) -> _T:
    if current != override:
        return current
    cls = type(current)
    defaults = asdict(cls())
    payload = asdict(current)
    explicit_fields = getattr(override, "_codex_explicit_fields", None)
    for key, value in asdict(override).items():
        if explicit_fields is not None and key not in explicit_fields:
            continue
        default_value = defaults.get(key)
        if value == default_value and payload.get(key) == value:
            continue
        payload[key] = value
    return cls(**payload)


def x__merge__mutmut_2(current: _T, override: _T) -> _T:
    if current == override:
        return current
    cls = None
    defaults = asdict(cls())
    payload = asdict(current)
    explicit_fields = getattr(override, "_codex_explicit_fields", None)
    for key, value in asdict(override).items():
        if explicit_fields is not None and key not in explicit_fields:
            continue
        default_value = defaults.get(key)
        if value == default_value and payload.get(key) == value:
            continue
        payload[key] = value
    return cls(**payload)


def x__merge__mutmut_3(current: _T, override: _T) -> _T:
    if current == override:
        return current
    cls = type(None)
    defaults = asdict(cls())
    payload = asdict(current)
    explicit_fields = getattr(override, "_codex_explicit_fields", None)
    for key, value in asdict(override).items():
        if explicit_fields is not None and key not in explicit_fields:
            continue
        default_value = defaults.get(key)
        if value == default_value and payload.get(key) == value:
            continue
        payload[key] = value
    return cls(**payload)


def x__merge__mutmut_4(current: _T, override: _T) -> _T:
    if current == override:
        return current
    cls = type(current)
    defaults = None
    payload = asdict(current)
    explicit_fields = getattr(override, "_codex_explicit_fields", None)
    for key, value in asdict(override).items():
        if explicit_fields is not None and key not in explicit_fields:
            continue
        default_value = defaults.get(key)
        if value == default_value and payload.get(key) == value:
            continue
        payload[key] = value
    return cls(**payload)


def x__merge__mutmut_5(current: _T, override: _T) -> _T:
    if current == override:
        return current
    cls = type(current)
    defaults = asdict(None)
    payload = asdict(current)
    explicit_fields = getattr(override, "_codex_explicit_fields", None)
    for key, value in asdict(override).items():
        if explicit_fields is not None and key not in explicit_fields:
            continue
        default_value = defaults.get(key)
        if value == default_value and payload.get(key) == value:
            continue
        payload[key] = value
    return cls(**payload)


def x__merge__mutmut_6(current: _T, override: _T) -> _T:
    if current == override:
        return current
    cls = type(current)
    defaults = asdict(cls())
    payload = None
    explicit_fields = getattr(override, "_codex_explicit_fields", None)
    for key, value in asdict(override).items():
        if explicit_fields is not None and key not in explicit_fields:
            continue
        default_value = defaults.get(key)
        if value == default_value and payload.get(key) == value:
            continue
        payload[key] = value
    return cls(**payload)


def x__merge__mutmut_7(current: _T, override: _T) -> _T:
    if current == override:
        return current
    cls = type(current)
    defaults = asdict(cls())
    payload = asdict(None)
    explicit_fields = getattr(override, "_codex_explicit_fields", None)
    for key, value in asdict(override).items():
        if explicit_fields is not None and key not in explicit_fields:
            continue
        default_value = defaults.get(key)
        if value == default_value and payload.get(key) == value:
            continue
        payload[key] = value
    return cls(**payload)


def x__merge__mutmut_8(current: _T, override: _T) -> _T:
    if current == override:
        return current
    cls = type(current)
    defaults = asdict(cls())
    payload = asdict(current)
    explicit_fields = None
    for key, value in asdict(override).items():
        if explicit_fields is not None and key not in explicit_fields:
            continue
        default_value = defaults.get(key)
        if value == default_value and payload.get(key) == value:
            continue
        payload[key] = value
    return cls(**payload)


def x__merge__mutmut_9(current: _T, override: _T) -> _T:
    if current == override:
        return current
    cls = type(current)
    defaults = asdict(cls())
    payload = asdict(current)
    explicit_fields = getattr(None, "_codex_explicit_fields", None)
    for key, value in asdict(override).items():
        if explicit_fields is not None and key not in explicit_fields:
            continue
        default_value = defaults.get(key)
        if value == default_value and payload.get(key) == value:
            continue
        payload[key] = value
    return cls(**payload)


def x__merge__mutmut_10(current: _T, override: _T) -> _T:
    if current == override:
        return current
    cls = type(current)
    defaults = asdict(cls())
    payload = asdict(current)
    explicit_fields = getattr(override, None, None)
    for key, value in asdict(override).items():
        if explicit_fields is not None and key not in explicit_fields:
            continue
        default_value = defaults.get(key)
        if value == default_value and payload.get(key) == value:
            continue
        payload[key] = value
    return cls(**payload)


def x__merge__mutmut_11(current: _T, override: _T) -> _T:
    if current == override:
        return current
    cls = type(current)
    defaults = asdict(cls())
    payload = asdict(current)
    explicit_fields = getattr("_codex_explicit_fields", None)
    for key, value in asdict(override).items():
        if explicit_fields is not None and key not in explicit_fields:
            continue
        default_value = defaults.get(key)
        if value == default_value and payload.get(key) == value:
            continue
        payload[key] = value
    return cls(**payload)


def x__merge__mutmut_12(current: _T, override: _T) -> _T:
    if current == override:
        return current
    cls = type(current)
    defaults = asdict(cls())
    payload = asdict(current)
    explicit_fields = getattr(override, None)
    for key, value in asdict(override).items():
        if explicit_fields is not None and key not in explicit_fields:
            continue
        default_value = defaults.get(key)
        if value == default_value and payload.get(key) == value:
            continue
        payload[key] = value
    return cls(**payload)


def x__merge__mutmut_13(current: _T, override: _T) -> _T:
    if current == override:
        return current
    cls = type(current)
    defaults = asdict(cls())
    payload = asdict(current)
    explicit_fields = getattr(override, "_codex_explicit_fields", )
    for key, value in asdict(override).items():
        if explicit_fields is not None and key not in explicit_fields:
            continue
        default_value = defaults.get(key)
        if value == default_value and payload.get(key) == value:
            continue
        payload[key] = value
    return cls(**payload)


def x__merge__mutmut_14(current: _T, override: _T) -> _T:
    if current == override:
        return current
    cls = type(current)
    defaults = asdict(cls())
    payload = asdict(current)
    explicit_fields = getattr(override, "XX_codex_explicit_fieldsXX", None)
    for key, value in asdict(override).items():
        if explicit_fields is not None and key not in explicit_fields:
            continue
        default_value = defaults.get(key)
        if value == default_value and payload.get(key) == value:
            continue
        payload[key] = value
    return cls(**payload)


def x__merge__mutmut_15(current: _T, override: _T) -> _T:
    if current == override:
        return current
    cls = type(current)
    defaults = asdict(cls())
    payload = asdict(current)
    explicit_fields = getattr(override, "_CODEX_EXPLICIT_FIELDS", None)
    for key, value in asdict(override).items():
        if explicit_fields is not None and key not in explicit_fields:
            continue
        default_value = defaults.get(key)
        if value == default_value and payload.get(key) == value:
            continue
        payload[key] = value
    return cls(**payload)


def x__merge__mutmut_16(current: _T, override: _T) -> _T:
    if current == override:
        return current
    cls = type(current)
    defaults = asdict(cls())
    payload = asdict(current)
    explicit_fields = getattr(override, "_codex_explicit_fields", None)
    for key, value in asdict(None).items():
        if explicit_fields is not None and key not in explicit_fields:
            continue
        default_value = defaults.get(key)
        if value == default_value and payload.get(key) == value:
            continue
        payload[key] = value
    return cls(**payload)


def x__merge__mutmut_17(current: _T, override: _T) -> _T:
    if current == override:
        return current
    cls = type(current)
    defaults = asdict(cls())
    payload = asdict(current)
    explicit_fields = getattr(override, "_codex_explicit_fields", None)
    for key, value in asdict(override).items():
        if explicit_fields is not None or key not in explicit_fields:
            continue
        default_value = defaults.get(key)
        if value == default_value and payload.get(key) == value:
            continue
        payload[key] = value
    return cls(**payload)


def x__merge__mutmut_18(current: _T, override: _T) -> _T:
    if current == override:
        return current
    cls = type(current)
    defaults = asdict(cls())
    payload = asdict(current)
    explicit_fields = getattr(override, "_codex_explicit_fields", None)
    for key, value in asdict(override).items():
        if explicit_fields is None and key not in explicit_fields:
            continue
        default_value = defaults.get(key)
        if value == default_value and payload.get(key) == value:
            continue
        payload[key] = value
    return cls(**payload)


def x__merge__mutmut_19(current: _T, override: _T) -> _T:
    if current == override:
        return current
    cls = type(current)
    defaults = asdict(cls())
    payload = asdict(current)
    explicit_fields = getattr(override, "_codex_explicit_fields", None)
    for key, value in asdict(override).items():
        if explicit_fields is not None and key in explicit_fields:
            continue
        default_value = defaults.get(key)
        if value == default_value and payload.get(key) == value:
            continue
        payload[key] = value
    return cls(**payload)


def x__merge__mutmut_20(current: _T, override: _T) -> _T:
    if current == override:
        return current
    cls = type(current)
    defaults = asdict(cls())
    payload = asdict(current)
    explicit_fields = getattr(override, "_codex_explicit_fields", None)
    for key, value in asdict(override).items():
        if explicit_fields is not None and key not in explicit_fields:
            break
        default_value = defaults.get(key)
        if value == default_value and payload.get(key) == value:
            continue
        payload[key] = value
    return cls(**payload)


def x__merge__mutmut_21(current: _T, override: _T) -> _T:
    if current == override:
        return current
    cls = type(current)
    defaults = asdict(cls())
    payload = asdict(current)
    explicit_fields = getattr(override, "_codex_explicit_fields", None)
    for key, value in asdict(override).items():
        if explicit_fields is not None and key not in explicit_fields:
            continue
        default_value = None
        if value == default_value and payload.get(key) == value:
            continue
        payload[key] = value
    return cls(**payload)


def x__merge__mutmut_22(current: _T, override: _T) -> _T:
    if current == override:
        return current
    cls = type(current)
    defaults = asdict(cls())
    payload = asdict(current)
    explicit_fields = getattr(override, "_codex_explicit_fields", None)
    for key, value in asdict(override).items():
        if explicit_fields is not None and key not in explicit_fields:
            continue
        default_value = defaults.get(None)
        if value == default_value and payload.get(key) == value:
            continue
        payload[key] = value
    return cls(**payload)


def x__merge__mutmut_23(current: _T, override: _T) -> _T:
    if current == override:
        return current
    cls = type(current)
    defaults = asdict(cls())
    payload = asdict(current)
    explicit_fields = getattr(override, "_codex_explicit_fields", None)
    for key, value in asdict(override).items():
        if explicit_fields is not None and key not in explicit_fields:
            continue
        default_value = defaults.get(key)
        if value == default_value or payload.get(key) == value:
            continue
        payload[key] = value
    return cls(**payload)


def x__merge__mutmut_24(current: _T, override: _T) -> _T:
    if current == override:
        return current
    cls = type(current)
    defaults = asdict(cls())
    payload = asdict(current)
    explicit_fields = getattr(override, "_codex_explicit_fields", None)
    for key, value in asdict(override).items():
        if explicit_fields is not None and key not in explicit_fields:
            continue
        default_value = defaults.get(key)
        if value != default_value and payload.get(key) == value:
            continue
        payload[key] = value
    return cls(**payload)


def x__merge__mutmut_25(current: _T, override: _T) -> _T:
    if current == override:
        return current
    cls = type(current)
    defaults = asdict(cls())
    payload = asdict(current)
    explicit_fields = getattr(override, "_codex_explicit_fields", None)
    for key, value in asdict(override).items():
        if explicit_fields is not None and key not in explicit_fields:
            continue
        default_value = defaults.get(key)
        if value == default_value and payload.get(None) == value:
            continue
        payload[key] = value
    return cls(**payload)


def x__merge__mutmut_26(current: _T, override: _T) -> _T:
    if current == override:
        return current
    cls = type(current)
    defaults = asdict(cls())
    payload = asdict(current)
    explicit_fields = getattr(override, "_codex_explicit_fields", None)
    for key, value in asdict(override).items():
        if explicit_fields is not None and key not in explicit_fields:
            continue
        default_value = defaults.get(key)
        if value == default_value and payload.get(key) != value:
            continue
        payload[key] = value
    return cls(**payload)


def x__merge__mutmut_27(current: _T, override: _T) -> _T:
    if current == override:
        return current
    cls = type(current)
    defaults = asdict(cls())
    payload = asdict(current)
    explicit_fields = getattr(override, "_codex_explicit_fields", None)
    for key, value in asdict(override).items():
        if explicit_fields is not None and key not in explicit_fields:
            continue
        default_value = defaults.get(key)
        if value == default_value and payload.get(key) == value:
            break
        payload[key] = value
    return cls(**payload)


def x__merge__mutmut_28(current: _T, override: _T) -> _T:
    if current == override:
        return current
    cls = type(current)
    defaults = asdict(cls())
    payload = asdict(current)
    explicit_fields = getattr(override, "_codex_explicit_fields", None)
    for key, value in asdict(override).items():
        if explicit_fields is not None and key not in explicit_fields:
            continue
        default_value = defaults.get(key)
        if value == default_value and payload.get(key) == value:
            continue
        payload[key] = None
    return cls(**payload)

x__merge__mutmut_mutants : ClassVar[MutantDict] = {
'x__merge__mutmut_1': x__merge__mutmut_1, 
    'x__merge__mutmut_2': x__merge__mutmut_2, 
    'x__merge__mutmut_3': x__merge__mutmut_3, 
    'x__merge__mutmut_4': x__merge__mutmut_4, 
    'x__merge__mutmut_5': x__merge__mutmut_5, 
    'x__merge__mutmut_6': x__merge__mutmut_6, 
    'x__merge__mutmut_7': x__merge__mutmut_7, 
    'x__merge__mutmut_8': x__merge__mutmut_8, 
    'x__merge__mutmut_9': x__merge__mutmut_9, 
    'x__merge__mutmut_10': x__merge__mutmut_10, 
    'x__merge__mutmut_11': x__merge__mutmut_11, 
    'x__merge__mutmut_12': x__merge__mutmut_12, 
    'x__merge__mutmut_13': x__merge__mutmut_13, 
    'x__merge__mutmut_14': x__merge__mutmut_14, 
    'x__merge__mutmut_15': x__merge__mutmut_15, 
    'x__merge__mutmut_16': x__merge__mutmut_16, 
    'x__merge__mutmut_17': x__merge__mutmut_17, 
    'x__merge__mutmut_18': x__merge__mutmut_18, 
    'x__merge__mutmut_19': x__merge__mutmut_19, 
    'x__merge__mutmut_20': x__merge__mutmut_20, 
    'x__merge__mutmut_21': x__merge__mutmut_21, 
    'x__merge__mutmut_22': x__merge__mutmut_22, 
    'x__merge__mutmut_23': x__merge__mutmut_23, 
    'x__merge__mutmut_24': x__merge__mutmut_24, 
    'x__merge__mutmut_25': x__merge__mutmut_25, 
    'x__merge__mutmut_26': x__merge__mutmut_26, 
    'x__merge__mutmut_27': x__merge__mutmut_27, 
    'x__merge__mutmut_28': x__merge__mutmut_28
}

def _merge(*args, **kwargs):
    result = _mutmut_trampoline(x__merge__mutmut_orig, x__merge__mutmut_mutants, args, kwargs)
    return result 

_merge.__signature__ = _mutmut_signature(x__merge__mutmut_orig)
x__merge__mutmut_orig.__name__ = 'x__merge'


def x__serialize_logging__mutmut_orig(config: LoggingConfig) -> dict[str, _t.Any]:
    payload = asdict(config)
    if config.evidence_file is not None:
        payload["evidence_file"] = str(config.evidence_file)
    return payload


def x__serialize_logging__mutmut_1(config: LoggingConfig) -> dict[str, _t.Any]:
    payload = None
    if config.evidence_file is not None:
        payload["evidence_file"] = str(config.evidence_file)
    return payload


def x__serialize_logging__mutmut_2(config: LoggingConfig) -> dict[str, _t.Any]:
    payload = asdict(None)
    if config.evidence_file is not None:
        payload["evidence_file"] = str(config.evidence_file)
    return payload


def x__serialize_logging__mutmut_3(config: LoggingConfig) -> dict[str, _t.Any]:
    payload = asdict(config)
    if config.evidence_file is None:
        payload["evidence_file"] = str(config.evidence_file)
    return payload


def x__serialize_logging__mutmut_4(config: LoggingConfig) -> dict[str, _t.Any]:
    payload = asdict(config)
    if config.evidence_file is not None:
        payload["evidence_file"] = None
    return payload


def x__serialize_logging__mutmut_5(config: LoggingConfig) -> dict[str, _t.Any]:
    payload = asdict(config)
    if config.evidence_file is not None:
        payload["XXevidence_fileXX"] = str(config.evidence_file)
    return payload


def x__serialize_logging__mutmut_6(config: LoggingConfig) -> dict[str, _t.Any]:
    payload = asdict(config)
    if config.evidence_file is not None:
        payload["EVIDENCE_FILE"] = str(config.evidence_file)
    return payload


def x__serialize_logging__mutmut_7(config: LoggingConfig) -> dict[str, _t.Any]:
    payload = asdict(config)
    if config.evidence_file is not None:
        payload["evidence_file"] = str(None)
    return payload

x__serialize_logging__mutmut_mutants : ClassVar[MutantDict] = {
'x__serialize_logging__mutmut_1': x__serialize_logging__mutmut_1, 
    'x__serialize_logging__mutmut_2': x__serialize_logging__mutmut_2, 
    'x__serialize_logging__mutmut_3': x__serialize_logging__mutmut_3, 
    'x__serialize_logging__mutmut_4': x__serialize_logging__mutmut_4, 
    'x__serialize_logging__mutmut_5': x__serialize_logging__mutmut_5, 
    'x__serialize_logging__mutmut_6': x__serialize_logging__mutmut_6, 
    'x__serialize_logging__mutmut_7': x__serialize_logging__mutmut_7
}

def _serialize_logging(*args, **kwargs):
    result = _mutmut_trampoline(x__serialize_logging__mutmut_orig, x__serialize_logging__mutmut_mutants, args, kwargs)
    return result 

_serialize_logging.__signature__ = _mutmut_signature(x__serialize_logging__mutmut_orig)
x__serialize_logging__mutmut_orig.__name__ = 'x__serialize_logging'


def x__serialize_batch__mutmut_orig(config: BatchConfig) -> dict[str, _t.Any]:
    payload = asdict(config)
    if config.results_path is not None:
        payload["results_path"] = str(config.results_path)
    return payload


def x__serialize_batch__mutmut_1(config: BatchConfig) -> dict[str, _t.Any]:
    payload = None
    if config.results_path is not None:
        payload["results_path"] = str(config.results_path)
    return payload


def x__serialize_batch__mutmut_2(config: BatchConfig) -> dict[str, _t.Any]:
    payload = asdict(None)
    if config.results_path is not None:
        payload["results_path"] = str(config.results_path)
    return payload


def x__serialize_batch__mutmut_3(config: BatchConfig) -> dict[str, _t.Any]:
    payload = asdict(config)
    if config.results_path is None:
        payload["results_path"] = str(config.results_path)
    return payload


def x__serialize_batch__mutmut_4(config: BatchConfig) -> dict[str, _t.Any]:
    payload = asdict(config)
    if config.results_path is not None:
        payload["results_path"] = None
    return payload


def x__serialize_batch__mutmut_5(config: BatchConfig) -> dict[str, _t.Any]:
    payload = asdict(config)
    if config.results_path is not None:
        payload["XXresults_pathXX"] = str(config.results_path)
    return payload


def x__serialize_batch__mutmut_6(config: BatchConfig) -> dict[str, _t.Any]:
    payload = asdict(config)
    if config.results_path is not None:
        payload["RESULTS_PATH"] = str(config.results_path)
    return payload


def x__serialize_batch__mutmut_7(config: BatchConfig) -> dict[str, _t.Any]:
    payload = asdict(config)
    if config.results_path is not None:
        payload["results_path"] = str(None)
    return payload

x__serialize_batch__mutmut_mutants : ClassVar[MutantDict] = {
'x__serialize_batch__mutmut_1': x__serialize_batch__mutmut_1, 
    'x__serialize_batch__mutmut_2': x__serialize_batch__mutmut_2, 
    'x__serialize_batch__mutmut_3': x__serialize_batch__mutmut_3, 
    'x__serialize_batch__mutmut_4': x__serialize_batch__mutmut_4, 
    'x__serialize_batch__mutmut_5': x__serialize_batch__mutmut_5, 
    'x__serialize_batch__mutmut_6': x__serialize_batch__mutmut_6, 
    'x__serialize_batch__mutmut_7': x__serialize_batch__mutmut_7
}

def _serialize_batch(*args, **kwargs):
    result = _mutmut_trampoline(x__serialize_batch__mutmut_orig, x__serialize_batch__mutmut_mutants, args, kwargs)
    return result 

_serialize_batch.__signature__ = _mutmut_signature(x__serialize_batch__mutmut_orig)
x__serialize_batch__mutmut_orig.__name__ = 'x__serialize_batch'
