"""
Ndjson Tools Module

This module provides functionality for ndjson tools.

Usage:
    from common.ndjson_tools import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import csv
import datetime as dt
import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any
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


def x__flatten__mutmut_orig(data: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    flattened: dict[str, Any] = {}
    for key, value in data.items():
        column = f"{prefix}{key}" if not prefix else f"{prefix}.{key}"
        if isinstance(value, dict):
            flattened.update(_flatten(value, column))
        else:
            flattened[column] = value
    return flattened


def x__flatten__mutmut_1(data: dict[str, Any], prefix: str = "XXXX") -> dict[str, Any]:
    flattened: dict[str, Any] = {}
    for key, value in data.items():
        column = f"{prefix}{key}" if not prefix else f"{prefix}.{key}"
        if isinstance(value, dict):
            flattened.update(_flatten(value, column))
        else:
            flattened[column] = value
    return flattened


def x__flatten__mutmut_2(data: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    flattened: dict[str, Any] = None
    for key, value in data.items():
        column = f"{prefix}{key}" if not prefix else f"{prefix}.{key}"
        if isinstance(value, dict):
            flattened.update(_flatten(value, column))
        else:
            flattened[column] = value
    return flattened


def x__flatten__mutmut_3(data: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    flattened: dict[str, Any] = {}
    for key, value in data.items():
        column = None
        if isinstance(value, dict):
            flattened.update(_flatten(value, column))
        else:
            flattened[column] = value
    return flattened


def x__flatten__mutmut_4(data: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    flattened: dict[str, Any] = {}
    for key, value in data.items():
        column = f"{prefix}{key}" if prefix else f"{prefix}.{key}"
        if isinstance(value, dict):
            flattened.update(_flatten(value, column))
        else:
            flattened[column] = value
    return flattened


def x__flatten__mutmut_5(data: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    flattened: dict[str, Any] = {}
    for key, value in data.items():
        column = f"{prefix}{key}" if not prefix else f"{prefix}.{key}"
        if isinstance(value, dict):
            flattened.update(None)
        else:
            flattened[column] = value
    return flattened


def x__flatten__mutmut_6(data: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    flattened: dict[str, Any] = {}
    for key, value in data.items():
        column = f"{prefix}{key}" if not prefix else f"{prefix}.{key}"
        if isinstance(value, dict):
            flattened.update(_flatten(None, column))
        else:
            flattened[column] = value
    return flattened


def x__flatten__mutmut_7(data: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    flattened: dict[str, Any] = {}
    for key, value in data.items():
        column = f"{prefix}{key}" if not prefix else f"{prefix}.{key}"
        if isinstance(value, dict):
            flattened.update(_flatten(value, None))
        else:
            flattened[column] = value
    return flattened


def x__flatten__mutmut_8(data: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    flattened: dict[str, Any] = {}
    for key, value in data.items():
        column = f"{prefix}{key}" if not prefix else f"{prefix}.{key}"
        if isinstance(value, dict):
            flattened.update(_flatten(column))
        else:
            flattened[column] = value
    return flattened


def x__flatten__mutmut_9(data: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    flattened: dict[str, Any] = {}
    for key, value in data.items():
        column = f"{prefix}{key}" if not prefix else f"{prefix}.{key}"
        if isinstance(value, dict):
            flattened.update(_flatten(value, ))
        else:
            flattened[column] = value
    return flattened


def x__flatten__mutmut_10(data: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    flattened: dict[str, Any] = {}
    for key, value in data.items():
        column = f"{prefix}{key}" if not prefix else f"{prefix}.{key}"
        if isinstance(value, dict):
            flattened.update(_flatten(value, column))
        else:
            flattened[column] = None
    return flattened

x__flatten__mutmut_mutants : ClassVar[MutantDict] = {
'x__flatten__mutmut_1': x__flatten__mutmut_1, 
    'x__flatten__mutmut_2': x__flatten__mutmut_2, 
    'x__flatten__mutmut_3': x__flatten__mutmut_3, 
    'x__flatten__mutmut_4': x__flatten__mutmut_4, 
    'x__flatten__mutmut_5': x__flatten__mutmut_5, 
    'x__flatten__mutmut_6': x__flatten__mutmut_6, 
    'x__flatten__mutmut_7': x__flatten__mutmut_7, 
    'x__flatten__mutmut_8': x__flatten__mutmut_8, 
    'x__flatten__mutmut_9': x__flatten__mutmut_9, 
    'x__flatten__mutmut_10': x__flatten__mutmut_10
}

def _flatten(*args, **kwargs):
    result = _mutmut_trampoline(x__flatten__mutmut_orig, x__flatten__mutmut_mutants, args, kwargs)
    return result 

_flatten.__signature__ = _mutmut_signature(x__flatten__mutmut_orig)
x__flatten__mutmut_orig.__name__ = 'x__flatten'


def x_append_event_ndjson__mutmut_orig(out_file: Path, event: dict[str, Any]) -> None:
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with out_file.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def x_append_event_ndjson__mutmut_1(out_file: Path, event: dict[str, Any]) -> None:
    out_file.parent.mkdir(parents=None, exist_ok=True)
    with out_file.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def x_append_event_ndjson__mutmut_2(out_file: Path, event: dict[str, Any]) -> None:
    out_file.parent.mkdir(parents=True, exist_ok=None)
    with out_file.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def x_append_event_ndjson__mutmut_3(out_file: Path, event: dict[str, Any]) -> None:
    out_file.parent.mkdir(exist_ok=True)
    with out_file.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def x_append_event_ndjson__mutmut_4(out_file: Path, event: dict[str, Any]) -> None:
    out_file.parent.mkdir(parents=True, )
    with out_file.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def x_append_event_ndjson__mutmut_5(out_file: Path, event: dict[str, Any]) -> None:
    out_file.parent.mkdir(parents=False, exist_ok=True)
    with out_file.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def x_append_event_ndjson__mutmut_6(out_file: Path, event: dict[str, Any]) -> None:
    out_file.parent.mkdir(parents=True, exist_ok=False)
    with out_file.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def x_append_event_ndjson__mutmut_7(out_file: Path, event: dict[str, Any]) -> None:
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with out_file.open(None, encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def x_append_event_ndjson__mutmut_8(out_file: Path, event: dict[str, Any]) -> None:
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with out_file.open("a", encoding=None) as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def x_append_event_ndjson__mutmut_9(out_file: Path, event: dict[str, Any]) -> None:
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with out_file.open(encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def x_append_event_ndjson__mutmut_10(out_file: Path, event: dict[str, Any]) -> None:
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with out_file.open("a", ) as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def x_append_event_ndjson__mutmut_11(out_file: Path, event: dict[str, Any]) -> None:
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with out_file.open("XXaXX", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def x_append_event_ndjson__mutmut_12(out_file: Path, event: dict[str, Any]) -> None:
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with out_file.open("A", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def x_append_event_ndjson__mutmut_13(out_file: Path, event: dict[str, Any]) -> None:
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with out_file.open("a", encoding="XXutf-8XX") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def x_append_event_ndjson__mutmut_14(out_file: Path, event: dict[str, Any]) -> None:
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with out_file.open("a", encoding="UTF-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def x_append_event_ndjson__mutmut_15(out_file: Path, event: dict[str, Any]) -> None:
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with out_file.open("a", encoding="utf-8") as handle:
        handle.write(None)


def x_append_event_ndjson__mutmut_16(out_file: Path, event: dict[str, Any]) -> None:
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with out_file.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) - "\n")


def x_append_event_ndjson__mutmut_17(out_file: Path, event: dict[str, Any]) -> None:
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with out_file.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(None, ensure_ascii=False) + "\n")


def x_append_event_ndjson__mutmut_18(out_file: Path, event: dict[str, Any]) -> None:
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with out_file.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=None) + "\n")


def x_append_event_ndjson__mutmut_19(out_file: Path, event: dict[str, Any]) -> None:
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with out_file.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(ensure_ascii=False) + "\n")


def x_append_event_ndjson__mutmut_20(out_file: Path, event: dict[str, Any]) -> None:
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with out_file.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ) + "\n")


def x_append_event_ndjson__mutmut_21(out_file: Path, event: dict[str, Any]) -> None:
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with out_file.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=True) + "\n")


def x_append_event_ndjson__mutmut_22(out_file: Path, event: dict[str, Any]) -> None:
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with out_file.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "XX\nXX")

x_append_event_ndjson__mutmut_mutants : ClassVar[MutantDict] = {
'x_append_event_ndjson__mutmut_1': x_append_event_ndjson__mutmut_1, 
    'x_append_event_ndjson__mutmut_2': x_append_event_ndjson__mutmut_2, 
    'x_append_event_ndjson__mutmut_3': x_append_event_ndjson__mutmut_3, 
    'x_append_event_ndjson__mutmut_4': x_append_event_ndjson__mutmut_4, 
    'x_append_event_ndjson__mutmut_5': x_append_event_ndjson__mutmut_5, 
    'x_append_event_ndjson__mutmut_6': x_append_event_ndjson__mutmut_6, 
    'x_append_event_ndjson__mutmut_7': x_append_event_ndjson__mutmut_7, 
    'x_append_event_ndjson__mutmut_8': x_append_event_ndjson__mutmut_8, 
    'x_append_event_ndjson__mutmut_9': x_append_event_ndjson__mutmut_9, 
    'x_append_event_ndjson__mutmut_10': x_append_event_ndjson__mutmut_10, 
    'x_append_event_ndjson__mutmut_11': x_append_event_ndjson__mutmut_11, 
    'x_append_event_ndjson__mutmut_12': x_append_event_ndjson__mutmut_12, 
    'x_append_event_ndjson__mutmut_13': x_append_event_ndjson__mutmut_13, 
    'x_append_event_ndjson__mutmut_14': x_append_event_ndjson__mutmut_14, 
    'x_append_event_ndjson__mutmut_15': x_append_event_ndjson__mutmut_15, 
    'x_append_event_ndjson__mutmut_16': x_append_event_ndjson__mutmut_16, 
    'x_append_event_ndjson__mutmut_17': x_append_event_ndjson__mutmut_17, 
    'x_append_event_ndjson__mutmut_18': x_append_event_ndjson__mutmut_18, 
    'x_append_event_ndjson__mutmut_19': x_append_event_ndjson__mutmut_19, 
    'x_append_event_ndjson__mutmut_20': x_append_event_ndjson__mutmut_20, 
    'x_append_event_ndjson__mutmut_21': x_append_event_ndjson__mutmut_21, 
    'x_append_event_ndjson__mutmut_22': x_append_event_ndjson__mutmut_22
}

def append_event_ndjson(*args, **kwargs):
    result = _mutmut_trampoline(x_append_event_ndjson__mutmut_orig, x_append_event_ndjson__mutmut_mutants, args, kwargs)
    return result 

append_event_ndjson.__signature__ = _mutmut_signature(x_append_event_ndjson__mutmut_orig)
x_append_event_ndjson__mutmut_orig.__name__ = 'x_append_event_ndjson'


def x__iter_ndjson_files__mutmut_orig(in_path: Path) -> Iterable[Path]:
    if in_path.is_file():
        yield in_path
    elif in_path.is_dir():
        for path in sorted(in_path.rglob("*.ndjson")):
            if path.is_file():
                yield path


def x__iter_ndjson_files__mutmut_1(in_path: Path) -> Iterable[Path]:
    if in_path.is_file():
        yield in_path
    elif in_path.is_dir():
        for path in sorted(None):
            if path.is_file():
                yield path


def x__iter_ndjson_files__mutmut_2(in_path: Path) -> Iterable[Path]:
    if in_path.is_file():
        yield in_path
    elif in_path.is_dir():
        for path in sorted(in_path.rglob(None)):
            if path.is_file():
                yield path


def x__iter_ndjson_files__mutmut_3(in_path: Path) -> Iterable[Path]:
    if in_path.is_file():
        yield in_path
    elif in_path.is_dir():
        for path in sorted(in_path.rglob("XX*.ndjsonXX")):
            if path.is_file():
                yield path


def x__iter_ndjson_files__mutmut_4(in_path: Path) -> Iterable[Path]:
    if in_path.is_file():
        yield in_path
    elif in_path.is_dir():
        for path in sorted(in_path.rglob("*.NDJSON")):
            if path.is_file():
                yield path

x__iter_ndjson_files__mutmut_mutants : ClassVar[MutantDict] = {
'x__iter_ndjson_files__mutmut_1': x__iter_ndjson_files__mutmut_1, 
    'x__iter_ndjson_files__mutmut_2': x__iter_ndjson_files__mutmut_2, 
    'x__iter_ndjson_files__mutmut_3': x__iter_ndjson_files__mutmut_3, 
    'x__iter_ndjson_files__mutmut_4': x__iter_ndjson_files__mutmut_4
}

def _iter_ndjson_files(*args, **kwargs):
    result = _mutmut_trampoline(x__iter_ndjson_files__mutmut_orig, x__iter_ndjson_files__mutmut_mutants, args, kwargs)
    return result 

_iter_ndjson_files.__signature__ = _mutmut_signature(x__iter_ndjson_files__mutmut_orig)
x__iter_ndjson_files__mutmut_orig.__name__ = 'x__iter_ndjson_files'


def x_ndjson_to_csv__mutmut_orig(in_path: Path, out_csv: Path) -> None:
    """Convert NDJSON records (from a file or directory tree) into a single CSV."""
    rows: list[dict[str, Any]] = []
    headers: list[str] = []
    header_set = set()

    for file_path in _iter_ndjson_files(in_path):
        for line in file_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            flat = _flatten(record)
            rows.append(flat)
            for column in flat:
                if column not in header_set:
                    header_set.add(column)
                    headers.append(column)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def x_ndjson_to_csv__mutmut_1(in_path: Path, out_csv: Path) -> None:
    """Convert NDJSON records (from a file or directory tree) into a single CSV."""
    rows: list[dict[str, Any]] = None
    headers: list[str] = []
    header_set = set()

    for file_path in _iter_ndjson_files(in_path):
        for line in file_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            flat = _flatten(record)
            rows.append(flat)
            for column in flat:
                if column not in header_set:
                    header_set.add(column)
                    headers.append(column)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def x_ndjson_to_csv__mutmut_2(in_path: Path, out_csv: Path) -> None:
    """Convert NDJSON records (from a file or directory tree) into a single CSV."""
    rows: list[dict[str, Any]] = []
    headers: list[str] = None
    header_set = set()

    for file_path in _iter_ndjson_files(in_path):
        for line in file_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            flat = _flatten(record)
            rows.append(flat)
            for column in flat:
                if column not in header_set:
                    header_set.add(column)
                    headers.append(column)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def x_ndjson_to_csv__mutmut_3(in_path: Path, out_csv: Path) -> None:
    """Convert NDJSON records (from a file or directory tree) into a single CSV."""
    rows: list[dict[str, Any]] = []
    headers: list[str] = []
    header_set = None

    for file_path in _iter_ndjson_files(in_path):
        for line in file_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            flat = _flatten(record)
            rows.append(flat)
            for column in flat:
                if column not in header_set:
                    header_set.add(column)
                    headers.append(column)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def x_ndjson_to_csv__mutmut_4(in_path: Path, out_csv: Path) -> None:
    """Convert NDJSON records (from a file or directory tree) into a single CSV."""
    rows: list[dict[str, Any]] = []
    headers: list[str] = []
    header_set = set()

    for file_path in _iter_ndjson_files(None):
        for line in file_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            flat = _flatten(record)
            rows.append(flat)
            for column in flat:
                if column not in header_set:
                    header_set.add(column)
                    headers.append(column)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def x_ndjson_to_csv__mutmut_5(in_path: Path, out_csv: Path) -> None:
    """Convert NDJSON records (from a file or directory tree) into a single CSV."""
    rows: list[dict[str, Any]] = []
    headers: list[str] = []
    header_set = set()

    for file_path in _iter_ndjson_files(in_path):
        for line in file_path.read_text(encoding=None).splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            flat = _flatten(record)
            rows.append(flat)
            for column in flat:
                if column not in header_set:
                    header_set.add(column)
                    headers.append(column)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def x_ndjson_to_csv__mutmut_6(in_path: Path, out_csv: Path) -> None:
    """Convert NDJSON records (from a file or directory tree) into a single CSV."""
    rows: list[dict[str, Any]] = []
    headers: list[str] = []
    header_set = set()

    for file_path in _iter_ndjson_files(in_path):
        for line in file_path.read_text(encoding="XXutf-8XX").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            flat = _flatten(record)
            rows.append(flat)
            for column in flat:
                if column not in header_set:
                    header_set.add(column)
                    headers.append(column)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def x_ndjson_to_csv__mutmut_7(in_path: Path, out_csv: Path) -> None:
    """Convert NDJSON records (from a file or directory tree) into a single CSV."""
    rows: list[dict[str, Any]] = []
    headers: list[str] = []
    header_set = set()

    for file_path in _iter_ndjson_files(in_path):
        for line in file_path.read_text(encoding="UTF-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            flat = _flatten(record)
            rows.append(flat)
            for column in flat:
                if column not in header_set:
                    header_set.add(column)
                    headers.append(column)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def x_ndjson_to_csv__mutmut_8(in_path: Path, out_csv: Path) -> None:
    """Convert NDJSON records (from a file or directory tree) into a single CSV."""
    rows: list[dict[str, Any]] = []
    headers: list[str] = []
    header_set = set()

    for file_path in _iter_ndjson_files(in_path):
        for line in file_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                continue
            record = json.loads(line)
            flat = _flatten(record)
            rows.append(flat)
            for column in flat:
                if column not in header_set:
                    header_set.add(column)
                    headers.append(column)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def x_ndjson_to_csv__mutmut_9(in_path: Path, out_csv: Path) -> None:
    """Convert NDJSON records (from a file or directory tree) into a single CSV."""
    rows: list[dict[str, Any]] = []
    headers: list[str] = []
    header_set = set()

    for file_path in _iter_ndjson_files(in_path):
        for line in file_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                break
            record = json.loads(line)
            flat = _flatten(record)
            rows.append(flat)
            for column in flat:
                if column not in header_set:
                    header_set.add(column)
                    headers.append(column)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def x_ndjson_to_csv__mutmut_10(in_path: Path, out_csv: Path) -> None:
    """Convert NDJSON records (from a file or directory tree) into a single CSV."""
    rows: list[dict[str, Any]] = []
    headers: list[str] = []
    header_set = set()

    for file_path in _iter_ndjson_files(in_path):
        for line in file_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = None
            flat = _flatten(record)
            rows.append(flat)
            for column in flat:
                if column not in header_set:
                    header_set.add(column)
                    headers.append(column)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def x_ndjson_to_csv__mutmut_11(in_path: Path, out_csv: Path) -> None:
    """Convert NDJSON records (from a file or directory tree) into a single CSV."""
    rows: list[dict[str, Any]] = []
    headers: list[str] = []
    header_set = set()

    for file_path in _iter_ndjson_files(in_path):
        for line in file_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(None)
            flat = _flatten(record)
            rows.append(flat)
            for column in flat:
                if column not in header_set:
                    header_set.add(column)
                    headers.append(column)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def x_ndjson_to_csv__mutmut_12(in_path: Path, out_csv: Path) -> None:
    """Convert NDJSON records (from a file or directory tree) into a single CSV."""
    rows: list[dict[str, Any]] = []
    headers: list[str] = []
    header_set = set()

    for file_path in _iter_ndjson_files(in_path):
        for line in file_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            flat = None
            rows.append(flat)
            for column in flat:
                if column not in header_set:
                    header_set.add(column)
                    headers.append(column)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def x_ndjson_to_csv__mutmut_13(in_path: Path, out_csv: Path) -> None:
    """Convert NDJSON records (from a file or directory tree) into a single CSV."""
    rows: list[dict[str, Any]] = []
    headers: list[str] = []
    header_set = set()

    for file_path in _iter_ndjson_files(in_path):
        for line in file_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            flat = _flatten(None)
            rows.append(flat)
            for column in flat:
                if column not in header_set:
                    header_set.add(column)
                    headers.append(column)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def x_ndjson_to_csv__mutmut_14(in_path: Path, out_csv: Path) -> None:
    """Convert NDJSON records (from a file or directory tree) into a single CSV."""
    rows: list[dict[str, Any]] = []
    headers: list[str] = []
    header_set = set()

    for file_path in _iter_ndjson_files(in_path):
        for line in file_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            flat = _flatten(record)
            rows.append(None)
            for column in flat:
                if column not in header_set:
                    header_set.add(column)
                    headers.append(column)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def x_ndjson_to_csv__mutmut_15(in_path: Path, out_csv: Path) -> None:
    """Convert NDJSON records (from a file or directory tree) into a single CSV."""
    rows: list[dict[str, Any]] = []
    headers: list[str] = []
    header_set = set()

    for file_path in _iter_ndjson_files(in_path):
        for line in file_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            flat = _flatten(record)
            rows.append(flat)
            for column in flat:
                if column in header_set:
                    header_set.add(column)
                    headers.append(column)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def x_ndjson_to_csv__mutmut_16(in_path: Path, out_csv: Path) -> None:
    """Convert NDJSON records (from a file or directory tree) into a single CSV."""
    rows: list[dict[str, Any]] = []
    headers: list[str] = []
    header_set = set()

    for file_path in _iter_ndjson_files(in_path):
        for line in file_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            flat = _flatten(record)
            rows.append(flat)
            for column in flat:
                if column not in header_set:
                    header_set.add(None)
                    headers.append(column)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def x_ndjson_to_csv__mutmut_17(in_path: Path, out_csv: Path) -> None:
    """Convert NDJSON records (from a file or directory tree) into a single CSV."""
    rows: list[dict[str, Any]] = []
    headers: list[str] = []
    header_set = set()

    for file_path in _iter_ndjson_files(in_path):
        for line in file_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            flat = _flatten(record)
            rows.append(flat)
            for column in flat:
                if column not in header_set:
                    header_set.add(column)
                    headers.append(None)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def x_ndjson_to_csv__mutmut_18(in_path: Path, out_csv: Path) -> None:
    """Convert NDJSON records (from a file or directory tree) into a single CSV."""
    rows: list[dict[str, Any]] = []
    headers: list[str] = []
    header_set = set()

    for file_path in _iter_ndjson_files(in_path):
        for line in file_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            flat = _flatten(record)
            rows.append(flat)
            for column in flat:
                if column not in header_set:
                    header_set.add(column)
                    headers.append(column)

    out_csv.parent.mkdir(parents=None, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def x_ndjson_to_csv__mutmut_19(in_path: Path, out_csv: Path) -> None:
    """Convert NDJSON records (from a file or directory tree) into a single CSV."""
    rows: list[dict[str, Any]] = []
    headers: list[str] = []
    header_set = set()

    for file_path in _iter_ndjson_files(in_path):
        for line in file_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            flat = _flatten(record)
            rows.append(flat)
            for column in flat:
                if column not in header_set:
                    header_set.add(column)
                    headers.append(column)

    out_csv.parent.mkdir(parents=True, exist_ok=None)
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def x_ndjson_to_csv__mutmut_20(in_path: Path, out_csv: Path) -> None:
    """Convert NDJSON records (from a file or directory tree) into a single CSV."""
    rows: list[dict[str, Any]] = []
    headers: list[str] = []
    header_set = set()

    for file_path in _iter_ndjson_files(in_path):
        for line in file_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            flat = _flatten(record)
            rows.append(flat)
            for column in flat:
                if column not in header_set:
                    header_set.add(column)
                    headers.append(column)

    out_csv.parent.mkdir(exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def x_ndjson_to_csv__mutmut_21(in_path: Path, out_csv: Path) -> None:
    """Convert NDJSON records (from a file or directory tree) into a single CSV."""
    rows: list[dict[str, Any]] = []
    headers: list[str] = []
    header_set = set()

    for file_path in _iter_ndjson_files(in_path):
        for line in file_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            flat = _flatten(record)
            rows.append(flat)
            for column in flat:
                if column not in header_set:
                    header_set.add(column)
                    headers.append(column)

    out_csv.parent.mkdir(parents=True, )
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def x_ndjson_to_csv__mutmut_22(in_path: Path, out_csv: Path) -> None:
    """Convert NDJSON records (from a file or directory tree) into a single CSV."""
    rows: list[dict[str, Any]] = []
    headers: list[str] = []
    header_set = set()

    for file_path in _iter_ndjson_files(in_path):
        for line in file_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            flat = _flatten(record)
            rows.append(flat)
            for column in flat:
                if column not in header_set:
                    header_set.add(column)
                    headers.append(column)

    out_csv.parent.mkdir(parents=False, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def x_ndjson_to_csv__mutmut_23(in_path: Path, out_csv: Path) -> None:
    """Convert NDJSON records (from a file or directory tree) into a single CSV."""
    rows: list[dict[str, Any]] = []
    headers: list[str] = []
    header_set = set()

    for file_path in _iter_ndjson_files(in_path):
        for line in file_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            flat = _flatten(record)
            rows.append(flat)
            for column in flat:
                if column not in header_set:
                    header_set.add(column)
                    headers.append(column)

    out_csv.parent.mkdir(parents=True, exist_ok=False)
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def x_ndjson_to_csv__mutmut_24(in_path: Path, out_csv: Path) -> None:
    """Convert NDJSON records (from a file or directory tree) into a single CSV."""
    rows: list[dict[str, Any]] = []
    headers: list[str] = []
    header_set = set()

    for file_path in _iter_ndjson_files(in_path):
        for line in file_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            flat = _flatten(record)
            rows.append(flat)
            for column in flat:
                if column not in header_set:
                    header_set.add(column)
                    headers.append(column)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open(None, newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def x_ndjson_to_csv__mutmut_25(in_path: Path, out_csv: Path) -> None:
    """Convert NDJSON records (from a file or directory tree) into a single CSV."""
    rows: list[dict[str, Any]] = []
    headers: list[str] = []
    header_set = set()

    for file_path in _iter_ndjson_files(in_path):
        for line in file_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            flat = _flatten(record)
            rows.append(flat)
            for column in flat:
                if column not in header_set:
                    header_set.add(column)
                    headers.append(column)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline=None, encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def x_ndjson_to_csv__mutmut_26(in_path: Path, out_csv: Path) -> None:
    """Convert NDJSON records (from a file or directory tree) into a single CSV."""
    rows: list[dict[str, Any]] = []
    headers: list[str] = []
    header_set = set()

    for file_path in _iter_ndjson_files(in_path):
        for line in file_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            flat = _flatten(record)
            rows.append(flat)
            for column in flat:
                if column not in header_set:
                    header_set.add(column)
                    headers.append(column)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding=None) as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def x_ndjson_to_csv__mutmut_27(in_path: Path, out_csv: Path) -> None:
    """Convert NDJSON records (from a file or directory tree) into a single CSV."""
    rows: list[dict[str, Any]] = []
    headers: list[str] = []
    header_set = set()

    for file_path in _iter_ndjson_files(in_path):
        for line in file_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            flat = _flatten(record)
            rows.append(flat)
            for column in flat:
                if column not in header_set:
                    header_set.add(column)
                    headers.append(column)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open(newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def x_ndjson_to_csv__mutmut_28(in_path: Path, out_csv: Path) -> None:
    """Convert NDJSON records (from a file or directory tree) into a single CSV."""
    rows: list[dict[str, Any]] = []
    headers: list[str] = []
    header_set = set()

    for file_path in _iter_ndjson_files(in_path):
        for line in file_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            flat = _flatten(record)
            rows.append(flat)
            for column in flat:
                if column not in header_set:
                    header_set.add(column)
                    headers.append(column)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def x_ndjson_to_csv__mutmut_29(in_path: Path, out_csv: Path) -> None:
    """Convert NDJSON records (from a file or directory tree) into a single CSV."""
    rows: list[dict[str, Any]] = []
    headers: list[str] = []
    header_set = set()

    for file_path in _iter_ndjson_files(in_path):
        for line in file_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            flat = _flatten(record)
            rows.append(flat)
            for column in flat:
                if column not in header_set:
                    header_set.add(column)
                    headers.append(column)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", ) as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def x_ndjson_to_csv__mutmut_30(in_path: Path, out_csv: Path) -> None:
    """Convert NDJSON records (from a file or directory tree) into a single CSV."""
    rows: list[dict[str, Any]] = []
    headers: list[str] = []
    header_set = set()

    for file_path in _iter_ndjson_files(in_path):
        for line in file_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            flat = _flatten(record)
            rows.append(flat)
            for column in flat:
                if column not in header_set:
                    header_set.add(column)
                    headers.append(column)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("XXwXX", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def x_ndjson_to_csv__mutmut_31(in_path: Path, out_csv: Path) -> None:
    """Convert NDJSON records (from a file or directory tree) into a single CSV."""
    rows: list[dict[str, Any]] = []
    headers: list[str] = []
    header_set = set()

    for file_path in _iter_ndjson_files(in_path):
        for line in file_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            flat = _flatten(record)
            rows.append(flat)
            for column in flat:
                if column not in header_set:
                    header_set.add(column)
                    headers.append(column)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("W", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def x_ndjson_to_csv__mutmut_32(in_path: Path, out_csv: Path) -> None:
    """Convert NDJSON records (from a file or directory tree) into a single CSV."""
    rows: list[dict[str, Any]] = []
    headers: list[str] = []
    header_set = set()

    for file_path in _iter_ndjson_files(in_path):
        for line in file_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            flat = _flatten(record)
            rows.append(flat)
            for column in flat:
                if column not in header_set:
                    header_set.add(column)
                    headers.append(column)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="XXXX", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def x_ndjson_to_csv__mutmut_33(in_path: Path, out_csv: Path) -> None:
    """Convert NDJSON records (from a file or directory tree) into a single CSV."""
    rows: list[dict[str, Any]] = []
    headers: list[str] = []
    header_set = set()

    for file_path in _iter_ndjson_files(in_path):
        for line in file_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            flat = _flatten(record)
            rows.append(flat)
            for column in flat:
                if column not in header_set:
                    header_set.add(column)
                    headers.append(column)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="XXutf-8XX") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def x_ndjson_to_csv__mutmut_34(in_path: Path, out_csv: Path) -> None:
    """Convert NDJSON records (from a file or directory tree) into a single CSV."""
    rows: list[dict[str, Any]] = []
    headers: list[str] = []
    header_set = set()

    for file_path in _iter_ndjson_files(in_path):
        for line in file_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            flat = _flatten(record)
            rows.append(flat)
            for column in flat:
                if column not in header_set:
                    header_set.add(column)
                    headers.append(column)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="UTF-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def x_ndjson_to_csv__mutmut_35(in_path: Path, out_csv: Path) -> None:
    """Convert NDJSON records (from a file or directory tree) into a single CSV."""
    rows: list[dict[str, Any]] = []
    headers: list[str] = []
    header_set = set()

    for file_path in _iter_ndjson_files(in_path):
        for line in file_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            flat = _flatten(record)
            rows.append(flat)
            for column in flat:
                if column not in header_set:
                    header_set.add(column)
                    headers.append(column)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = None
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def x_ndjson_to_csv__mutmut_36(in_path: Path, out_csv: Path) -> None:
    """Convert NDJSON records (from a file or directory tree) into a single CSV."""
    rows: list[dict[str, Any]] = []
    headers: list[str] = []
    header_set = set()

    for file_path in _iter_ndjson_files(in_path):
        for line in file_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            flat = _flatten(record)
            rows.append(flat)
            for column in flat:
                if column not in header_set:
                    header_set.add(column)
                    headers.append(column)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(None, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def x_ndjson_to_csv__mutmut_37(in_path: Path, out_csv: Path) -> None:
    """Convert NDJSON records (from a file or directory tree) into a single CSV."""
    rows: list[dict[str, Any]] = []
    headers: list[str] = []
    header_set = set()

    for file_path in _iter_ndjson_files(in_path):
        for line in file_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            flat = _flatten(record)
            rows.append(flat)
            for column in flat:
                if column not in header_set:
                    header_set.add(column)
                    headers.append(column)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=None)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def x_ndjson_to_csv__mutmut_38(in_path: Path, out_csv: Path) -> None:
    """Convert NDJSON records (from a file or directory tree) into a single CSV."""
    rows: list[dict[str, Any]] = []
    headers: list[str] = []
    header_set = set()

    for file_path in _iter_ndjson_files(in_path):
        for line in file_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            flat = _flatten(record)
            rows.append(flat)
            for column in flat:
                if column not in header_set:
                    header_set.add(column)
                    headers.append(column)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def x_ndjson_to_csv__mutmut_39(in_path: Path, out_csv: Path) -> None:
    """Convert NDJSON records (from a file or directory tree) into a single CSV."""
    rows: list[dict[str, Any]] = []
    headers: list[str] = []
    header_set = set()

    for file_path in _iter_ndjson_files(in_path):
        for line in file_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            flat = _flatten(record)
            rows.append(flat)
            for column in flat:
                if column not in header_set:
                    header_set.add(column)
                    headers.append(column)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def x_ndjson_to_csv__mutmut_40(in_path: Path, out_csv: Path) -> None:
    """Convert NDJSON records (from a file or directory tree) into a single CSV."""
    rows: list[dict[str, Any]] = []
    headers: list[str] = []
    header_set = set()

    for file_path in _iter_ndjson_files(in_path):
        for line in file_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            flat = _flatten(record)
            rows.append(flat)
            for column in flat:
                if column not in header_set:
                    header_set.add(column)
                    headers.append(column)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(None)

x_ndjson_to_csv__mutmut_mutants : ClassVar[MutantDict] = {
'x_ndjson_to_csv__mutmut_1': x_ndjson_to_csv__mutmut_1, 
    'x_ndjson_to_csv__mutmut_2': x_ndjson_to_csv__mutmut_2, 
    'x_ndjson_to_csv__mutmut_3': x_ndjson_to_csv__mutmut_3, 
    'x_ndjson_to_csv__mutmut_4': x_ndjson_to_csv__mutmut_4, 
    'x_ndjson_to_csv__mutmut_5': x_ndjson_to_csv__mutmut_5, 
    'x_ndjson_to_csv__mutmut_6': x_ndjson_to_csv__mutmut_6, 
    'x_ndjson_to_csv__mutmut_7': x_ndjson_to_csv__mutmut_7, 
    'x_ndjson_to_csv__mutmut_8': x_ndjson_to_csv__mutmut_8, 
    'x_ndjson_to_csv__mutmut_9': x_ndjson_to_csv__mutmut_9, 
    'x_ndjson_to_csv__mutmut_10': x_ndjson_to_csv__mutmut_10, 
    'x_ndjson_to_csv__mutmut_11': x_ndjson_to_csv__mutmut_11, 
    'x_ndjson_to_csv__mutmut_12': x_ndjson_to_csv__mutmut_12, 
    'x_ndjson_to_csv__mutmut_13': x_ndjson_to_csv__mutmut_13, 
    'x_ndjson_to_csv__mutmut_14': x_ndjson_to_csv__mutmut_14, 
    'x_ndjson_to_csv__mutmut_15': x_ndjson_to_csv__mutmut_15, 
    'x_ndjson_to_csv__mutmut_16': x_ndjson_to_csv__mutmut_16, 
    'x_ndjson_to_csv__mutmut_17': x_ndjson_to_csv__mutmut_17, 
    'x_ndjson_to_csv__mutmut_18': x_ndjson_to_csv__mutmut_18, 
    'x_ndjson_to_csv__mutmut_19': x_ndjson_to_csv__mutmut_19, 
    'x_ndjson_to_csv__mutmut_20': x_ndjson_to_csv__mutmut_20, 
    'x_ndjson_to_csv__mutmut_21': x_ndjson_to_csv__mutmut_21, 
    'x_ndjson_to_csv__mutmut_22': x_ndjson_to_csv__mutmut_22, 
    'x_ndjson_to_csv__mutmut_23': x_ndjson_to_csv__mutmut_23, 
    'x_ndjson_to_csv__mutmut_24': x_ndjson_to_csv__mutmut_24, 
    'x_ndjson_to_csv__mutmut_25': x_ndjson_to_csv__mutmut_25, 
    'x_ndjson_to_csv__mutmut_26': x_ndjson_to_csv__mutmut_26, 
    'x_ndjson_to_csv__mutmut_27': x_ndjson_to_csv__mutmut_27, 
    'x_ndjson_to_csv__mutmut_28': x_ndjson_to_csv__mutmut_28, 
    'x_ndjson_to_csv__mutmut_29': x_ndjson_to_csv__mutmut_29, 
    'x_ndjson_to_csv__mutmut_30': x_ndjson_to_csv__mutmut_30, 
    'x_ndjson_to_csv__mutmut_31': x_ndjson_to_csv__mutmut_31, 
    'x_ndjson_to_csv__mutmut_32': x_ndjson_to_csv__mutmut_32, 
    'x_ndjson_to_csv__mutmut_33': x_ndjson_to_csv__mutmut_33, 
    'x_ndjson_to_csv__mutmut_34': x_ndjson_to_csv__mutmut_34, 
    'x_ndjson_to_csv__mutmut_35': x_ndjson_to_csv__mutmut_35, 
    'x_ndjson_to_csv__mutmut_36': x_ndjson_to_csv__mutmut_36, 
    'x_ndjson_to_csv__mutmut_37': x_ndjson_to_csv__mutmut_37, 
    'x_ndjson_to_csv__mutmut_38': x_ndjson_to_csv__mutmut_38, 
    'x_ndjson_to_csv__mutmut_39': x_ndjson_to_csv__mutmut_39, 
    'x_ndjson_to_csv__mutmut_40': x_ndjson_to_csv__mutmut_40
}

def ndjson_to_csv(*args, **kwargs):
    result = _mutmut_trampoline(x_ndjson_to_csv__mutmut_orig, x_ndjson_to_csv__mutmut_mutants, args, kwargs)
    return result 

ndjson_to_csv.__signature__ = _mutmut_signature(x_ndjson_to_csv__mutmut_orig)
x_ndjson_to_csv__mutmut_orig.__name__ = 'x_ndjson_to_csv'


def x_cli_ndjson_to_csv__mutmut_orig() -> None:
    import sys

    if len(sys.argv) < 3:
        print("Usage: ndjson-to-csv <IN_FILE_OR_DIR> <OUT_CSV>", file=sys.stderr)
        sys.exit(2)

    in_path = Path(sys.argv[1])
    out_csv = Path(sys.argv[2])
    ndjson_to_csv(in_path, out_csv)
    print(f"Wrote CSV: {out_csv}")


def x_cli_ndjson_to_csv__mutmut_1() -> None:
    import sys

    if len(sys.argv) <= 3:
        print("Usage: ndjson-to-csv <IN_FILE_OR_DIR> <OUT_CSV>", file=sys.stderr)
        sys.exit(2)

    in_path = Path(sys.argv[1])
    out_csv = Path(sys.argv[2])
    ndjson_to_csv(in_path, out_csv)
    print(f"Wrote CSV: {out_csv}")


def x_cli_ndjson_to_csv__mutmut_2() -> None:
    import sys

    if len(sys.argv) < 4:
        print("Usage: ndjson-to-csv <IN_FILE_OR_DIR> <OUT_CSV>", file=sys.stderr)
        sys.exit(2)

    in_path = Path(sys.argv[1])
    out_csv = Path(sys.argv[2])
    ndjson_to_csv(in_path, out_csv)
    print(f"Wrote CSV: {out_csv}")


def x_cli_ndjson_to_csv__mutmut_3() -> None:
    import sys

    if len(sys.argv) < 3:
        print(None, file=sys.stderr)
        sys.exit(2)

    in_path = Path(sys.argv[1])
    out_csv = Path(sys.argv[2])
    ndjson_to_csv(in_path, out_csv)
    print(f"Wrote CSV: {out_csv}")


def x_cli_ndjson_to_csv__mutmut_4() -> None:
    import sys

    if len(sys.argv) < 3:
        print("Usage: ndjson-to-csv <IN_FILE_OR_DIR> <OUT_CSV>", file=None)
        sys.exit(2)

    in_path = Path(sys.argv[1])
    out_csv = Path(sys.argv[2])
    ndjson_to_csv(in_path, out_csv)
    print(f"Wrote CSV: {out_csv}")


def x_cli_ndjson_to_csv__mutmut_5() -> None:
    import sys

    if len(sys.argv) < 3:
        print(file=sys.stderr)
        sys.exit(2)

    in_path = Path(sys.argv[1])
    out_csv = Path(sys.argv[2])
    ndjson_to_csv(in_path, out_csv)
    print(f"Wrote CSV: {out_csv}")


def x_cli_ndjson_to_csv__mutmut_6() -> None:
    import sys

    if len(sys.argv) < 3:
        print("Usage: ndjson-to-csv <IN_FILE_OR_DIR> <OUT_CSV>", )
        sys.exit(2)

    in_path = Path(sys.argv[1])
    out_csv = Path(sys.argv[2])
    ndjson_to_csv(in_path, out_csv)
    print(f"Wrote CSV: {out_csv}")


def x_cli_ndjson_to_csv__mutmut_7() -> None:
    import sys

    if len(sys.argv) < 3:
        print("XXUsage: ndjson-to-csv <IN_FILE_OR_DIR> <OUT_CSV>XX", file=sys.stderr)
        sys.exit(2)

    in_path = Path(sys.argv[1])
    out_csv = Path(sys.argv[2])
    ndjson_to_csv(in_path, out_csv)
    print(f"Wrote CSV: {out_csv}")


def x_cli_ndjson_to_csv__mutmut_8() -> None:
    import sys

    if len(sys.argv) < 3:
        print("usage: ndjson-to-csv <in_file_or_dir> <out_csv>", file=sys.stderr)
        sys.exit(2)

    in_path = Path(sys.argv[1])
    out_csv = Path(sys.argv[2])
    ndjson_to_csv(in_path, out_csv)
    print(f"Wrote CSV: {out_csv}")


def x_cli_ndjson_to_csv__mutmut_9() -> None:
    import sys

    if len(sys.argv) < 3:
        print("USAGE: NDJSON-TO-CSV <IN_FILE_OR_DIR> <OUT_CSV>", file=sys.stderr)
        sys.exit(2)

    in_path = Path(sys.argv[1])
    out_csv = Path(sys.argv[2])
    ndjson_to_csv(in_path, out_csv)
    print(f"Wrote CSV: {out_csv}")


def x_cli_ndjson_to_csv__mutmut_10() -> None:
    import sys

    if len(sys.argv) < 3:
        print("Usage: ndjson-to-csv <IN_FILE_OR_DIR> <OUT_CSV>", file=sys.stderr)
        sys.exit(None)

    in_path = Path(sys.argv[1])
    out_csv = Path(sys.argv[2])
    ndjson_to_csv(in_path, out_csv)
    print(f"Wrote CSV: {out_csv}")


def x_cli_ndjson_to_csv__mutmut_11() -> None:
    import sys

    if len(sys.argv) < 3:
        print("Usage: ndjson-to-csv <IN_FILE_OR_DIR> <OUT_CSV>", file=sys.stderr)
        sys.exit(3)

    in_path = Path(sys.argv[1])
    out_csv = Path(sys.argv[2])
    ndjson_to_csv(in_path, out_csv)
    print(f"Wrote CSV: {out_csv}")


def x_cli_ndjson_to_csv__mutmut_12() -> None:
    import sys

    if len(sys.argv) < 3:
        print("Usage: ndjson-to-csv <IN_FILE_OR_DIR> <OUT_CSV>", file=sys.stderr)
        sys.exit(2)

    in_path = None
    out_csv = Path(sys.argv[2])
    ndjson_to_csv(in_path, out_csv)
    print(f"Wrote CSV: {out_csv}")


def x_cli_ndjson_to_csv__mutmut_13() -> None:
    import sys

    if len(sys.argv) < 3:
        print("Usage: ndjson-to-csv <IN_FILE_OR_DIR> <OUT_CSV>", file=sys.stderr)
        sys.exit(2)

    in_path = Path(None)
    out_csv = Path(sys.argv[2])
    ndjson_to_csv(in_path, out_csv)
    print(f"Wrote CSV: {out_csv}")


def x_cli_ndjson_to_csv__mutmut_14() -> None:
    import sys

    if len(sys.argv) < 3:
        print("Usage: ndjson-to-csv <IN_FILE_OR_DIR> <OUT_CSV>", file=sys.stderr)
        sys.exit(2)

    in_path = Path(sys.argv[2])
    out_csv = Path(sys.argv[2])
    ndjson_to_csv(in_path, out_csv)
    print(f"Wrote CSV: {out_csv}")


def x_cli_ndjson_to_csv__mutmut_15() -> None:
    import sys

    if len(sys.argv) < 3:
        print("Usage: ndjson-to-csv <IN_FILE_OR_DIR> <OUT_CSV>", file=sys.stderr)
        sys.exit(2)

    in_path = Path(sys.argv[1])
    out_csv = None
    ndjson_to_csv(in_path, out_csv)
    print(f"Wrote CSV: {out_csv}")


def x_cli_ndjson_to_csv__mutmut_16() -> None:
    import sys

    if len(sys.argv) < 3:
        print("Usage: ndjson-to-csv <IN_FILE_OR_DIR> <OUT_CSV>", file=sys.stderr)
        sys.exit(2)

    in_path = Path(sys.argv[1])
    out_csv = Path(None)
    ndjson_to_csv(in_path, out_csv)
    print(f"Wrote CSV: {out_csv}")


def x_cli_ndjson_to_csv__mutmut_17() -> None:
    import sys

    if len(sys.argv) < 3:
        print("Usage: ndjson-to-csv <IN_FILE_OR_DIR> <OUT_CSV>", file=sys.stderr)
        sys.exit(2)

    in_path = Path(sys.argv[1])
    out_csv = Path(sys.argv[3])
    ndjson_to_csv(in_path, out_csv)
    print(f"Wrote CSV: {out_csv}")


def x_cli_ndjson_to_csv__mutmut_18() -> None:
    import sys

    if len(sys.argv) < 3:
        print("Usage: ndjson-to-csv <IN_FILE_OR_DIR> <OUT_CSV>", file=sys.stderr)
        sys.exit(2)

    in_path = Path(sys.argv[1])
    out_csv = Path(sys.argv[2])
    ndjson_to_csv(None, out_csv)
    print(f"Wrote CSV: {out_csv}")


def x_cli_ndjson_to_csv__mutmut_19() -> None:
    import sys

    if len(sys.argv) < 3:
        print("Usage: ndjson-to-csv <IN_FILE_OR_DIR> <OUT_CSV>", file=sys.stderr)
        sys.exit(2)

    in_path = Path(sys.argv[1])
    out_csv = Path(sys.argv[2])
    ndjson_to_csv(in_path, None)
    print(f"Wrote CSV: {out_csv}")


def x_cli_ndjson_to_csv__mutmut_20() -> None:
    import sys

    if len(sys.argv) < 3:
        print("Usage: ndjson-to-csv <IN_FILE_OR_DIR> <OUT_CSV>", file=sys.stderr)
        sys.exit(2)

    in_path = Path(sys.argv[1])
    out_csv = Path(sys.argv[2])
    ndjson_to_csv(out_csv)
    print(f"Wrote CSV: {out_csv}")


def x_cli_ndjson_to_csv__mutmut_21() -> None:
    import sys

    if len(sys.argv) < 3:
        print("Usage: ndjson-to-csv <IN_FILE_OR_DIR> <OUT_CSV>", file=sys.stderr)
        sys.exit(2)

    in_path = Path(sys.argv[1])
    out_csv = Path(sys.argv[2])
    ndjson_to_csv(in_path, )
    print(f"Wrote CSV: {out_csv}")


def x_cli_ndjson_to_csv__mutmut_22() -> None:
    import sys

    if len(sys.argv) < 3:
        print("Usage: ndjson-to-csv <IN_FILE_OR_DIR> <OUT_CSV>", file=sys.stderr)
        sys.exit(2)

    in_path = Path(sys.argv[1])
    out_csv = Path(sys.argv[2])
    ndjson_to_csv(in_path, out_csv)
    print(None)

x_cli_ndjson_to_csv__mutmut_mutants : ClassVar[MutantDict] = {
'x_cli_ndjson_to_csv__mutmut_1': x_cli_ndjson_to_csv__mutmut_1, 
    'x_cli_ndjson_to_csv__mutmut_2': x_cli_ndjson_to_csv__mutmut_2, 
    'x_cli_ndjson_to_csv__mutmut_3': x_cli_ndjson_to_csv__mutmut_3, 
    'x_cli_ndjson_to_csv__mutmut_4': x_cli_ndjson_to_csv__mutmut_4, 
    'x_cli_ndjson_to_csv__mutmut_5': x_cli_ndjson_to_csv__mutmut_5, 
    'x_cli_ndjson_to_csv__mutmut_6': x_cli_ndjson_to_csv__mutmut_6, 
    'x_cli_ndjson_to_csv__mutmut_7': x_cli_ndjson_to_csv__mutmut_7, 
    'x_cli_ndjson_to_csv__mutmut_8': x_cli_ndjson_to_csv__mutmut_8, 
    'x_cli_ndjson_to_csv__mutmut_9': x_cli_ndjson_to_csv__mutmut_9, 
    'x_cli_ndjson_to_csv__mutmut_10': x_cli_ndjson_to_csv__mutmut_10, 
    'x_cli_ndjson_to_csv__mutmut_11': x_cli_ndjson_to_csv__mutmut_11, 
    'x_cli_ndjson_to_csv__mutmut_12': x_cli_ndjson_to_csv__mutmut_12, 
    'x_cli_ndjson_to_csv__mutmut_13': x_cli_ndjson_to_csv__mutmut_13, 
    'x_cli_ndjson_to_csv__mutmut_14': x_cli_ndjson_to_csv__mutmut_14, 
    'x_cli_ndjson_to_csv__mutmut_15': x_cli_ndjson_to_csv__mutmut_15, 
    'x_cli_ndjson_to_csv__mutmut_16': x_cli_ndjson_to_csv__mutmut_16, 
    'x_cli_ndjson_to_csv__mutmut_17': x_cli_ndjson_to_csv__mutmut_17, 
    'x_cli_ndjson_to_csv__mutmut_18': x_cli_ndjson_to_csv__mutmut_18, 
    'x_cli_ndjson_to_csv__mutmut_19': x_cli_ndjson_to_csv__mutmut_19, 
    'x_cli_ndjson_to_csv__mutmut_20': x_cli_ndjson_to_csv__mutmut_20, 
    'x_cli_ndjson_to_csv__mutmut_21': x_cli_ndjson_to_csv__mutmut_21, 
    'x_cli_ndjson_to_csv__mutmut_22': x_cli_ndjson_to_csv__mutmut_22
}

def cli_ndjson_to_csv(*args, **kwargs):
    result = _mutmut_trampoline(x_cli_ndjson_to_csv__mutmut_orig, x_cli_ndjson_to_csv__mutmut_mutants, args, kwargs)
    return result 

cli_ndjson_to_csv.__signature__ = _mutmut_signature(x_cli_ndjson_to_csv__mutmut_orig)
x_cli_ndjson_to_csv__mutmut_orig.__name__ = 'x_cli_ndjson_to_csv'


def x_make_run_metrics_path__mutmut_orig(base_dir: Path = Path(".codex/metrics")) -> Path:
    timestamp = dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")
    return base_dir / f"run-{timestamp}.ndjson"


def x_make_run_metrics_path__mutmut_1(base_dir: Path = Path(".codex/metrics")) -> Path:
    timestamp = None
    return base_dir / f"run-{timestamp}.ndjson"


def x_make_run_metrics_path__mutmut_2(base_dir: Path = Path(".codex/metrics")) -> Path:
    timestamp = dt.datetime.now(dt.UTC).strftime(None)
    return base_dir / f"run-{timestamp}.ndjson"


def x_make_run_metrics_path__mutmut_3(base_dir: Path = Path(".codex/metrics")) -> Path:
    timestamp = dt.datetime.now(None).strftime("%Y%m%dT%H%M%SZ")
    return base_dir / f"run-{timestamp}.ndjson"


def x_make_run_metrics_path__mutmut_4(base_dir: Path = Path(".codex/metrics")) -> Path:
    timestamp = dt.datetime.now(dt.UTC).strftime("XX%Y%m%dT%H%M%SZXX")
    return base_dir / f"run-{timestamp}.ndjson"


def x_make_run_metrics_path__mutmut_5(base_dir: Path = Path(".codex/metrics")) -> Path:
    timestamp = dt.datetime.now(dt.UTC).strftime("%y%m%dt%h%m%sz")
    return base_dir / f"run-{timestamp}.ndjson"


def x_make_run_metrics_path__mutmut_6(base_dir: Path = Path(".codex/metrics")) -> Path:
    timestamp = dt.datetime.now(dt.UTC).strftime("%Y%M%DT%H%M%SZ")
    return base_dir / f"run-{timestamp}.ndjson"


def x_make_run_metrics_path__mutmut_7(base_dir: Path = Path(".codex/metrics")) -> Path:
    timestamp = dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")
    return base_dir * f"run-{timestamp}.ndjson"

x_make_run_metrics_path__mutmut_mutants : ClassVar[MutantDict] = {
'x_make_run_metrics_path__mutmut_1': x_make_run_metrics_path__mutmut_1, 
    'x_make_run_metrics_path__mutmut_2': x_make_run_metrics_path__mutmut_2, 
    'x_make_run_metrics_path__mutmut_3': x_make_run_metrics_path__mutmut_3, 
    'x_make_run_metrics_path__mutmut_4': x_make_run_metrics_path__mutmut_4, 
    'x_make_run_metrics_path__mutmut_5': x_make_run_metrics_path__mutmut_5, 
    'x_make_run_metrics_path__mutmut_6': x_make_run_metrics_path__mutmut_6, 
    'x_make_run_metrics_path__mutmut_7': x_make_run_metrics_path__mutmut_7
}

def make_run_metrics_path(*args, **kwargs):
    result = _mutmut_trampoline(x_make_run_metrics_path__mutmut_orig, x_make_run_metrics_path__mutmut_mutants, args, kwargs)
    return result 

make_run_metrics_path.__signature__ = _mutmut_signature(x_make_run_metrics_path__mutmut_orig)
x_make_run_metrics_path__mutmut_orig.__name__ = 'x_make_run_metrics_path'
