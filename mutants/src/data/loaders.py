"""Data loading helpers with integrated input validation."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from pathlib import Path

from src.security import validate_input
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


def x_safe_line_loader__mutmut_orig(path: str | Path) -> Iterator[str]:
    """Yield sanitized lines from the given file."""

    resolved = Path(validate_input(str(path), input_type="path"))
    if not resolved.exists():
        raise FileNotFoundError(resolved)
    with resolved.open("r", encoding="utf-8") as handle:
        for line in handle:
            sanitized = validate_input(line, input_type="text")
            yield sanitized


def x_safe_line_loader__mutmut_1(path: str | Path) -> Iterator[str]:
    """Yield sanitized lines from the given file."""

    resolved = None
    if not resolved.exists():
        raise FileNotFoundError(resolved)
    with resolved.open("r", encoding="utf-8") as handle:
        for line in handle:
            sanitized = validate_input(line, input_type="text")
            yield sanitized


def x_safe_line_loader__mutmut_2(path: str | Path) -> Iterator[str]:
    """Yield sanitized lines from the given file."""

    resolved = Path(None)
    if not resolved.exists():
        raise FileNotFoundError(resolved)
    with resolved.open("r", encoding="utf-8") as handle:
        for line in handle:
            sanitized = validate_input(line, input_type="text")
            yield sanitized


def x_safe_line_loader__mutmut_3(path: str | Path) -> Iterator[str]:
    """Yield sanitized lines from the given file."""

    resolved = Path(validate_input(None, input_type="path"))
    if not resolved.exists():
        raise FileNotFoundError(resolved)
    with resolved.open("r", encoding="utf-8") as handle:
        for line in handle:
            sanitized = validate_input(line, input_type="text")
            yield sanitized


def x_safe_line_loader__mutmut_4(path: str | Path) -> Iterator[str]:
    """Yield sanitized lines from the given file."""

    resolved = Path(validate_input(str(path), input_type=None))
    if not resolved.exists():
        raise FileNotFoundError(resolved)
    with resolved.open("r", encoding="utf-8") as handle:
        for line in handle:
            sanitized = validate_input(line, input_type="text")
            yield sanitized


def x_safe_line_loader__mutmut_5(path: str | Path) -> Iterator[str]:
    """Yield sanitized lines from the given file."""

    resolved = Path(validate_input(input_type="path"))
    if not resolved.exists():
        raise FileNotFoundError(resolved)
    with resolved.open("r", encoding="utf-8") as handle:
        for line in handle:
            sanitized = validate_input(line, input_type="text")
            yield sanitized


def x_safe_line_loader__mutmut_6(path: str | Path) -> Iterator[str]:
    """Yield sanitized lines from the given file."""

    resolved = Path(validate_input(str(path), ))
    if not resolved.exists():
        raise FileNotFoundError(resolved)
    with resolved.open("r", encoding="utf-8") as handle:
        for line in handle:
            sanitized = validate_input(line, input_type="text")
            yield sanitized


def x_safe_line_loader__mutmut_7(path: str | Path) -> Iterator[str]:
    """Yield sanitized lines from the given file."""

    resolved = Path(validate_input(str(None), input_type="path"))
    if not resolved.exists():
        raise FileNotFoundError(resolved)
    with resolved.open("r", encoding="utf-8") as handle:
        for line in handle:
            sanitized = validate_input(line, input_type="text")
            yield sanitized


def x_safe_line_loader__mutmut_8(path: str | Path) -> Iterator[str]:
    """Yield sanitized lines from the given file."""

    resolved = Path(validate_input(str(path), input_type="XXpathXX"))
    if not resolved.exists():
        raise FileNotFoundError(resolved)
    with resolved.open("r", encoding="utf-8") as handle:
        for line in handle:
            sanitized = validate_input(line, input_type="text")
            yield sanitized


def x_safe_line_loader__mutmut_9(path: str | Path) -> Iterator[str]:
    """Yield sanitized lines from the given file."""

    resolved = Path(validate_input(str(path), input_type="PATH"))
    if not resolved.exists():
        raise FileNotFoundError(resolved)
    with resolved.open("r", encoding="utf-8") as handle:
        for line in handle:
            sanitized = validate_input(line, input_type="text")
            yield sanitized


def x_safe_line_loader__mutmut_10(path: str | Path) -> Iterator[str]:
    """Yield sanitized lines from the given file."""

    resolved = Path(validate_input(str(path), input_type="path"))
    if resolved.exists():
        raise FileNotFoundError(resolved)
    with resolved.open("r", encoding="utf-8") as handle:
        for line in handle:
            sanitized = validate_input(line, input_type="text")
            yield sanitized


def x_safe_line_loader__mutmut_11(path: str | Path) -> Iterator[str]:
    """Yield sanitized lines from the given file."""

    resolved = Path(validate_input(str(path), input_type="path"))
    if not resolved.exists():
        raise FileNotFoundError(None)
    with resolved.open("r", encoding="utf-8") as handle:
        for line in handle:
            sanitized = validate_input(line, input_type="text")
            yield sanitized


def x_safe_line_loader__mutmut_12(path: str | Path) -> Iterator[str]:
    """Yield sanitized lines from the given file."""

    resolved = Path(validate_input(str(path), input_type="path"))
    if not resolved.exists():
        raise FileNotFoundError(resolved)
    with resolved.open(None, encoding="utf-8") as handle:
        for line in handle:
            sanitized = validate_input(line, input_type="text")
            yield sanitized


def x_safe_line_loader__mutmut_13(path: str | Path) -> Iterator[str]:
    """Yield sanitized lines from the given file."""

    resolved = Path(validate_input(str(path), input_type="path"))
    if not resolved.exists():
        raise FileNotFoundError(resolved)
    with resolved.open("r", encoding=None) as handle:
        for line in handle:
            sanitized = validate_input(line, input_type="text")
            yield sanitized


def x_safe_line_loader__mutmut_14(path: str | Path) -> Iterator[str]:
    """Yield sanitized lines from the given file."""

    resolved = Path(validate_input(str(path), input_type="path"))
    if not resolved.exists():
        raise FileNotFoundError(resolved)
    with resolved.open(encoding="utf-8") as handle:
        for line in handle:
            sanitized = validate_input(line, input_type="text")
            yield sanitized


def x_safe_line_loader__mutmut_15(path: str | Path) -> Iterator[str]:
    """Yield sanitized lines from the given file."""

    resolved = Path(validate_input(str(path), input_type="path"))
    if not resolved.exists():
        raise FileNotFoundError(resolved)
    with resolved.open("r", ) as handle:
        for line in handle:
            sanitized = validate_input(line, input_type="text")
            yield sanitized


def x_safe_line_loader__mutmut_16(path: str | Path) -> Iterator[str]:
    """Yield sanitized lines from the given file."""

    resolved = Path(validate_input(str(path), input_type="path"))
    if not resolved.exists():
        raise FileNotFoundError(resolved)
    with resolved.open("XXrXX", encoding="utf-8") as handle:
        for line in handle:
            sanitized = validate_input(line, input_type="text")
            yield sanitized


def x_safe_line_loader__mutmut_17(path: str | Path) -> Iterator[str]:
    """Yield sanitized lines from the given file."""

    resolved = Path(validate_input(str(path), input_type="path"))
    if not resolved.exists():
        raise FileNotFoundError(resolved)
    with resolved.open("R", encoding="utf-8") as handle:
        for line in handle:
            sanitized = validate_input(line, input_type="text")
            yield sanitized


def x_safe_line_loader__mutmut_18(path: str | Path) -> Iterator[str]:
    """Yield sanitized lines from the given file."""

    resolved = Path(validate_input(str(path), input_type="path"))
    if not resolved.exists():
        raise FileNotFoundError(resolved)
    with resolved.open("r", encoding="XXutf-8XX") as handle:
        for line in handle:
            sanitized = validate_input(line, input_type="text")
            yield sanitized


def x_safe_line_loader__mutmut_19(path: str | Path) -> Iterator[str]:
    """Yield sanitized lines from the given file."""

    resolved = Path(validate_input(str(path), input_type="path"))
    if not resolved.exists():
        raise FileNotFoundError(resolved)
    with resolved.open("r", encoding="UTF-8") as handle:
        for line in handle:
            sanitized = validate_input(line, input_type="text")
            yield sanitized


def x_safe_line_loader__mutmut_20(path: str | Path) -> Iterator[str]:
    """Yield sanitized lines from the given file."""

    resolved = Path(validate_input(str(path), input_type="path"))
    if not resolved.exists():
        raise FileNotFoundError(resolved)
    with resolved.open("r", encoding="utf-8") as handle:
        for line in handle:
            sanitized = None
            yield sanitized


def x_safe_line_loader__mutmut_21(path: str | Path) -> Iterator[str]:
    """Yield sanitized lines from the given file."""

    resolved = Path(validate_input(str(path), input_type="path"))
    if not resolved.exists():
        raise FileNotFoundError(resolved)
    with resolved.open("r", encoding="utf-8") as handle:
        for line in handle:
            sanitized = validate_input(None, input_type="text")
            yield sanitized


def x_safe_line_loader__mutmut_22(path: str | Path) -> Iterator[str]:
    """Yield sanitized lines from the given file."""

    resolved = Path(validate_input(str(path), input_type="path"))
    if not resolved.exists():
        raise FileNotFoundError(resolved)
    with resolved.open("r", encoding="utf-8") as handle:
        for line in handle:
            sanitized = validate_input(line, input_type=None)
            yield sanitized


def x_safe_line_loader__mutmut_23(path: str | Path) -> Iterator[str]:
    """Yield sanitized lines from the given file."""

    resolved = Path(validate_input(str(path), input_type="path"))
    if not resolved.exists():
        raise FileNotFoundError(resolved)
    with resolved.open("r", encoding="utf-8") as handle:
        for line in handle:
            sanitized = validate_input(input_type="text")
            yield sanitized


def x_safe_line_loader__mutmut_24(path: str | Path) -> Iterator[str]:
    """Yield sanitized lines from the given file."""

    resolved = Path(validate_input(str(path), input_type="path"))
    if not resolved.exists():
        raise FileNotFoundError(resolved)
    with resolved.open("r", encoding="utf-8") as handle:
        for line in handle:
            sanitized = validate_input(line, )
            yield sanitized


def x_safe_line_loader__mutmut_25(path: str | Path) -> Iterator[str]:
    """Yield sanitized lines from the given file."""

    resolved = Path(validate_input(str(path), input_type="path"))
    if not resolved.exists():
        raise FileNotFoundError(resolved)
    with resolved.open("r", encoding="utf-8") as handle:
        for line in handle:
            sanitized = validate_input(line, input_type="XXtextXX")
            yield sanitized


def x_safe_line_loader__mutmut_26(path: str | Path) -> Iterator[str]:
    """Yield sanitized lines from the given file."""

    resolved = Path(validate_input(str(path), input_type="path"))
    if not resolved.exists():
        raise FileNotFoundError(resolved)
    with resolved.open("r", encoding="utf-8") as handle:
        for line in handle:
            sanitized = validate_input(line, input_type="TEXT")
            yield sanitized

x_safe_line_loader__mutmut_mutants : ClassVar[MutantDict] = {
'x_safe_line_loader__mutmut_1': x_safe_line_loader__mutmut_1, 
    'x_safe_line_loader__mutmut_2': x_safe_line_loader__mutmut_2, 
    'x_safe_line_loader__mutmut_3': x_safe_line_loader__mutmut_3, 
    'x_safe_line_loader__mutmut_4': x_safe_line_loader__mutmut_4, 
    'x_safe_line_loader__mutmut_5': x_safe_line_loader__mutmut_5, 
    'x_safe_line_loader__mutmut_6': x_safe_line_loader__mutmut_6, 
    'x_safe_line_loader__mutmut_7': x_safe_line_loader__mutmut_7, 
    'x_safe_line_loader__mutmut_8': x_safe_line_loader__mutmut_8, 
    'x_safe_line_loader__mutmut_9': x_safe_line_loader__mutmut_9, 
    'x_safe_line_loader__mutmut_10': x_safe_line_loader__mutmut_10, 
    'x_safe_line_loader__mutmut_11': x_safe_line_loader__mutmut_11, 
    'x_safe_line_loader__mutmut_12': x_safe_line_loader__mutmut_12, 
    'x_safe_line_loader__mutmut_13': x_safe_line_loader__mutmut_13, 
    'x_safe_line_loader__mutmut_14': x_safe_line_loader__mutmut_14, 
    'x_safe_line_loader__mutmut_15': x_safe_line_loader__mutmut_15, 
    'x_safe_line_loader__mutmut_16': x_safe_line_loader__mutmut_16, 
    'x_safe_line_loader__mutmut_17': x_safe_line_loader__mutmut_17, 
    'x_safe_line_loader__mutmut_18': x_safe_line_loader__mutmut_18, 
    'x_safe_line_loader__mutmut_19': x_safe_line_loader__mutmut_19, 
    'x_safe_line_loader__mutmut_20': x_safe_line_loader__mutmut_20, 
    'x_safe_line_loader__mutmut_21': x_safe_line_loader__mutmut_21, 
    'x_safe_line_loader__mutmut_22': x_safe_line_loader__mutmut_22, 
    'x_safe_line_loader__mutmut_23': x_safe_line_loader__mutmut_23, 
    'x_safe_line_loader__mutmut_24': x_safe_line_loader__mutmut_24, 
    'x_safe_line_loader__mutmut_25': x_safe_line_loader__mutmut_25, 
    'x_safe_line_loader__mutmut_26': x_safe_line_loader__mutmut_26
}

def safe_line_loader(*args, **kwargs):
    result = _mutmut_trampoline(x_safe_line_loader__mutmut_orig, x_safe_line_loader__mutmut_mutants, args, kwargs)
    return result 

safe_line_loader.__signature__ = _mutmut_signature(x_safe_line_loader__mutmut_orig)
x_safe_line_loader__mutmut_orig.__name__ = 'x_safe_line_loader'


def x_validate_records__mutmut_orig(records: Iterable[dict]) -> list[dict]:
    """Validate a collection of JSON-like dictionaries."""

    validated: list[dict] = []
    for record in records:
        cleaned = {}
        for key, value in record.items():
            cleaned[validate_input(key, input_type="text")] = validate_input(
                value, input_type="json"
            )
        validated.append(cleaned)
    return validated


def x_validate_records__mutmut_1(records: Iterable[dict]) -> list[dict]:
    """Validate a collection of JSON-like dictionaries."""

    validated: list[dict] = None
    for record in records:
        cleaned = {}
        for key, value in record.items():
            cleaned[validate_input(key, input_type="text")] = validate_input(
                value, input_type="json"
            )
        validated.append(cleaned)
    return validated


def x_validate_records__mutmut_2(records: Iterable[dict]) -> list[dict]:
    """Validate a collection of JSON-like dictionaries."""

    validated: list[dict] = []
    for record in records:
        cleaned = None
        for key, value in record.items():
            cleaned[validate_input(key, input_type="text")] = validate_input(
                value, input_type="json"
            )
        validated.append(cleaned)
    return validated


def x_validate_records__mutmut_3(records: Iterable[dict]) -> list[dict]:
    """Validate a collection of JSON-like dictionaries."""

    validated: list[dict] = []
    for record in records:
        cleaned = {}
        for key, value in record.items():
            cleaned[validate_input(key, input_type="text")] = None
        validated.append(cleaned)
    return validated


def x_validate_records__mutmut_4(records: Iterable[dict]) -> list[dict]:
    """Validate a collection of JSON-like dictionaries."""

    validated: list[dict] = []
    for record in records:
        cleaned = {}
        for key, value in record.items():
            cleaned[validate_input(None, input_type="text")] = validate_input(
                value, input_type="json"
            )
        validated.append(cleaned)
    return validated


def x_validate_records__mutmut_5(records: Iterable[dict]) -> list[dict]:
    """Validate a collection of JSON-like dictionaries."""

    validated: list[dict] = []
    for record in records:
        cleaned = {}
        for key, value in record.items():
            cleaned[validate_input(key, input_type=None)] = validate_input(
                value, input_type="json"
            )
        validated.append(cleaned)
    return validated


def x_validate_records__mutmut_6(records: Iterable[dict]) -> list[dict]:
    """Validate a collection of JSON-like dictionaries."""

    validated: list[dict] = []
    for record in records:
        cleaned = {}
        for key, value in record.items():
            cleaned[validate_input(input_type="text")] = validate_input(
                value, input_type="json"
            )
        validated.append(cleaned)
    return validated


def x_validate_records__mutmut_7(records: Iterable[dict]) -> list[dict]:
    """Validate a collection of JSON-like dictionaries."""

    validated: list[dict] = []
    for record in records:
        cleaned = {}
        for key, value in record.items():
            cleaned[validate_input(key, )] = validate_input(
                value, input_type="json"
            )
        validated.append(cleaned)
    return validated


def x_validate_records__mutmut_8(records: Iterable[dict]) -> list[dict]:
    """Validate a collection of JSON-like dictionaries."""

    validated: list[dict] = []
    for record in records:
        cleaned = {}
        for key, value in record.items():
            cleaned[validate_input(key, input_type="XXtextXX")] = validate_input(
                value, input_type="json"
            )
        validated.append(cleaned)
    return validated


def x_validate_records__mutmut_9(records: Iterable[dict]) -> list[dict]:
    """Validate a collection of JSON-like dictionaries."""

    validated: list[dict] = []
    for record in records:
        cleaned = {}
        for key, value in record.items():
            cleaned[validate_input(key, input_type="TEXT")] = validate_input(
                value, input_type="json"
            )
        validated.append(cleaned)
    return validated


def x_validate_records__mutmut_10(records: Iterable[dict]) -> list[dict]:
    """Validate a collection of JSON-like dictionaries."""

    validated: list[dict] = []
    for record in records:
        cleaned = {}
        for key, value in record.items():
            cleaned[validate_input(key, input_type="text")] = validate_input(
                None, input_type="json"
            )
        validated.append(cleaned)
    return validated


def x_validate_records__mutmut_11(records: Iterable[dict]) -> list[dict]:
    """Validate a collection of JSON-like dictionaries."""

    validated: list[dict] = []
    for record in records:
        cleaned = {}
        for key, value in record.items():
            cleaned[validate_input(key, input_type="text")] = validate_input(
                value, input_type=None
            )
        validated.append(cleaned)
    return validated


def x_validate_records__mutmut_12(records: Iterable[dict]) -> list[dict]:
    """Validate a collection of JSON-like dictionaries."""

    validated: list[dict] = []
    for record in records:
        cleaned = {}
        for key, value in record.items():
            cleaned[validate_input(key, input_type="text")] = validate_input(
                input_type="json"
            )
        validated.append(cleaned)
    return validated


def x_validate_records__mutmut_13(records: Iterable[dict]) -> list[dict]:
    """Validate a collection of JSON-like dictionaries."""

    validated: list[dict] = []
    for record in records:
        cleaned = {}
        for key, value in record.items():
            cleaned[validate_input(key, input_type="text")] = validate_input(
                value, )
        validated.append(cleaned)
    return validated


def x_validate_records__mutmut_14(records: Iterable[dict]) -> list[dict]:
    """Validate a collection of JSON-like dictionaries."""

    validated: list[dict] = []
    for record in records:
        cleaned = {}
        for key, value in record.items():
            cleaned[validate_input(key, input_type="text")] = validate_input(
                value, input_type="XXjsonXX"
            )
        validated.append(cleaned)
    return validated


def x_validate_records__mutmut_15(records: Iterable[dict]) -> list[dict]:
    """Validate a collection of JSON-like dictionaries."""

    validated: list[dict] = []
    for record in records:
        cleaned = {}
        for key, value in record.items():
            cleaned[validate_input(key, input_type="text")] = validate_input(
                value, input_type="JSON"
            )
        validated.append(cleaned)
    return validated


def x_validate_records__mutmut_16(records: Iterable[dict]) -> list[dict]:
    """Validate a collection of JSON-like dictionaries."""

    validated: list[dict] = []
    for record in records:
        cleaned = {}
        for key, value in record.items():
            cleaned[validate_input(key, input_type="text")] = validate_input(
                value, input_type="json"
            )
        validated.append(None)
    return validated

x_validate_records__mutmut_mutants : ClassVar[MutantDict] = {
'x_validate_records__mutmut_1': x_validate_records__mutmut_1, 
    'x_validate_records__mutmut_2': x_validate_records__mutmut_2, 
    'x_validate_records__mutmut_3': x_validate_records__mutmut_3, 
    'x_validate_records__mutmut_4': x_validate_records__mutmut_4, 
    'x_validate_records__mutmut_5': x_validate_records__mutmut_5, 
    'x_validate_records__mutmut_6': x_validate_records__mutmut_6, 
    'x_validate_records__mutmut_7': x_validate_records__mutmut_7, 
    'x_validate_records__mutmut_8': x_validate_records__mutmut_8, 
    'x_validate_records__mutmut_9': x_validate_records__mutmut_9, 
    'x_validate_records__mutmut_10': x_validate_records__mutmut_10, 
    'x_validate_records__mutmut_11': x_validate_records__mutmut_11, 
    'x_validate_records__mutmut_12': x_validate_records__mutmut_12, 
    'x_validate_records__mutmut_13': x_validate_records__mutmut_13, 
    'x_validate_records__mutmut_14': x_validate_records__mutmut_14, 
    'x_validate_records__mutmut_15': x_validate_records__mutmut_15, 
    'x_validate_records__mutmut_16': x_validate_records__mutmut_16
}

def validate_records(*args, **kwargs):
    result = _mutmut_trampoline(x_validate_records__mutmut_orig, x_validate_records__mutmut_mutants, args, kwargs)
    return result 

validate_records.__signature__ = _mutmut_signature(x_validate_records__mutmut_orig)
x_validate_records__mutmut_orig.__name__ = 'x_validate_records'
