"""
Load Module

This module provides functionality for load.

Usage:
    from mapping.load import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations
import logging
logger = logging.getLogger(__name__)
"""CSV mapping loaders with typed validation and evidence logging."""


import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Generic, TypeVar

from pydantic import BaseModel, ValidationError

from codex.evidence import append_evidence, utc_now

from .models import RoutingPattern, SlaParity

__all__ = [
    "MappingLoadResult",
    "load_all_mappings",
    "load_routing",
    "load_sla",
]

T = TypeVar("T", bound=BaseModel)
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


@dataclass(slots=True)
class MappingLoadResult(Generic[T]):
    records: list[T]
    deferred: int = 0


def x__log_deferred__mutmut_orig(source: Path, row_number: int, row: dict[str, str], error: object) -> None:
    append_evidence(
        "deferred.jsonl",
        {
            "ts": utc_now(),
            "source": source.as_posix(),
            "row_number": row_number,
            "error": error,
            "row": row,
            "phase": "mapping-validation",
        },
    )


def x__log_deferred__mutmut_1(source: Path, row_number: int, row: dict[str, str], error: object) -> None:
    append_evidence(
        None,
        {
            "ts": utc_now(),
            "source": source.as_posix(),
            "row_number": row_number,
            "error": error,
            "row": row,
            "phase": "mapping-validation",
        },
    )


def x__log_deferred__mutmut_2(source: Path, row_number: int, row: dict[str, str], error: object) -> None:
    append_evidence(
        "deferred.jsonl",
        None,
    )


def x__log_deferred__mutmut_3(source: Path, row_number: int, row: dict[str, str], error: object) -> None:
    append_evidence(
        {
            "ts": utc_now(),
            "source": source.as_posix(),
            "row_number": row_number,
            "error": error,
            "row": row,
            "phase": "mapping-validation",
        },
    )


def x__log_deferred__mutmut_4(source: Path, row_number: int, row: dict[str, str], error: object) -> None:
    append_evidence(
        "deferred.jsonl",
        )


def x__log_deferred__mutmut_5(source: Path, row_number: int, row: dict[str, str], error: object) -> None:
    append_evidence(
        "XXdeferred.jsonlXX",
        {
            "ts": utc_now(),
            "source": source.as_posix(),
            "row_number": row_number,
            "error": error,
            "row": row,
            "phase": "mapping-validation",
        },
    )


def x__log_deferred__mutmut_6(source: Path, row_number: int, row: dict[str, str], error: object) -> None:
    append_evidence(
        "DEFERRED.JSONL",
        {
            "ts": utc_now(),
            "source": source.as_posix(),
            "row_number": row_number,
            "error": error,
            "row": row,
            "phase": "mapping-validation",
        },
    )


def x__log_deferred__mutmut_7(source: Path, row_number: int, row: dict[str, str], error: object) -> None:
    append_evidence(
        "deferred.jsonl",
        {
            "XXtsXX": utc_now(),
            "source": source.as_posix(),
            "row_number": row_number,
            "error": error,
            "row": row,
            "phase": "mapping-validation",
        },
    )


def x__log_deferred__mutmut_8(source: Path, row_number: int, row: dict[str, str], error: object) -> None:
    append_evidence(
        "deferred.jsonl",
        {
            "TS": utc_now(),
            "source": source.as_posix(),
            "row_number": row_number,
            "error": error,
            "row": row,
            "phase": "mapping-validation",
        },
    )


def x__log_deferred__mutmut_9(source: Path, row_number: int, row: dict[str, str], error: object) -> None:
    append_evidence(
        "deferred.jsonl",
        {
            "ts": utc_now(),
            "XXsourceXX": source.as_posix(),
            "row_number": row_number,
            "error": error,
            "row": row,
            "phase": "mapping-validation",
        },
    )


def x__log_deferred__mutmut_10(source: Path, row_number: int, row: dict[str, str], error: object) -> None:
    append_evidence(
        "deferred.jsonl",
        {
            "ts": utc_now(),
            "SOURCE": source.as_posix(),
            "row_number": row_number,
            "error": error,
            "row": row,
            "phase": "mapping-validation",
        },
    )


def x__log_deferred__mutmut_11(source: Path, row_number: int, row: dict[str, str], error: object) -> None:
    append_evidence(
        "deferred.jsonl",
        {
            "ts": utc_now(),
            "source": source.as_posix(),
            "XXrow_numberXX": row_number,
            "error": error,
            "row": row,
            "phase": "mapping-validation",
        },
    )


def x__log_deferred__mutmut_12(source: Path, row_number: int, row: dict[str, str], error: object) -> None:
    append_evidence(
        "deferred.jsonl",
        {
            "ts": utc_now(),
            "source": source.as_posix(),
            "ROW_NUMBER": row_number,
            "error": error,
            "row": row,
            "phase": "mapping-validation",
        },
    )


def x__log_deferred__mutmut_13(source: Path, row_number: int, row: dict[str, str], error: object) -> None:
    append_evidence(
        "deferred.jsonl",
        {
            "ts": utc_now(),
            "source": source.as_posix(),
            "row_number": row_number,
            "XXerrorXX": error,
            "row": row,
            "phase": "mapping-validation",
        },
    )


def x__log_deferred__mutmut_14(source: Path, row_number: int, row: dict[str, str], error: object) -> None:
    append_evidence(
        "deferred.jsonl",
        {
            "ts": utc_now(),
            "source": source.as_posix(),
            "row_number": row_number,
            "ERROR": error,
            "row": row,
            "phase": "mapping-validation",
        },
    )


def x__log_deferred__mutmut_15(source: Path, row_number: int, row: dict[str, str], error: object) -> None:
    append_evidence(
        "deferred.jsonl",
        {
            "ts": utc_now(),
            "source": source.as_posix(),
            "row_number": row_number,
            "error": error,
            "XXrowXX": row,
            "phase": "mapping-validation",
        },
    )


def x__log_deferred__mutmut_16(source: Path, row_number: int, row: dict[str, str], error: object) -> None:
    append_evidence(
        "deferred.jsonl",
        {
            "ts": utc_now(),
            "source": source.as_posix(),
            "row_number": row_number,
            "error": error,
            "ROW": row,
            "phase": "mapping-validation",
        },
    )


def x__log_deferred__mutmut_17(source: Path, row_number: int, row: dict[str, str], error: object) -> None:
    append_evidence(
        "deferred.jsonl",
        {
            "ts": utc_now(),
            "source": source.as_posix(),
            "row_number": row_number,
            "error": error,
            "row": row,
            "XXphaseXX": "mapping-validation",
        },
    )


def x__log_deferred__mutmut_18(source: Path, row_number: int, row: dict[str, str], error: object) -> None:
    append_evidence(
        "deferred.jsonl",
        {
            "ts": utc_now(),
            "source": source.as_posix(),
            "row_number": row_number,
            "error": error,
            "row": row,
            "PHASE": "mapping-validation",
        },
    )


def x__log_deferred__mutmut_19(source: Path, row_number: int, row: dict[str, str], error: object) -> None:
    append_evidence(
        "deferred.jsonl",
        {
            "ts": utc_now(),
            "source": source.as_posix(),
            "row_number": row_number,
            "error": error,
            "row": row,
            "phase": "XXmapping-validationXX",
        },
    )


def x__log_deferred__mutmut_20(source: Path, row_number: int, row: dict[str, str], error: object) -> None:
    append_evidence(
        "deferred.jsonl",
        {
            "ts": utc_now(),
            "source": source.as_posix(),
            "row_number": row_number,
            "error": error,
            "row": row,
            "phase": "MAPPING-VALIDATION",
        },
    )

x__log_deferred__mutmut_mutants : ClassVar[MutantDict] = {
'x__log_deferred__mutmut_1': x__log_deferred__mutmut_1, 
    'x__log_deferred__mutmut_2': x__log_deferred__mutmut_2, 
    'x__log_deferred__mutmut_3': x__log_deferred__mutmut_3, 
    'x__log_deferred__mutmut_4': x__log_deferred__mutmut_4, 
    'x__log_deferred__mutmut_5': x__log_deferred__mutmut_5, 
    'x__log_deferred__mutmut_6': x__log_deferred__mutmut_6, 
    'x__log_deferred__mutmut_7': x__log_deferred__mutmut_7, 
    'x__log_deferred__mutmut_8': x__log_deferred__mutmut_8, 
    'x__log_deferred__mutmut_9': x__log_deferred__mutmut_9, 
    'x__log_deferred__mutmut_10': x__log_deferred__mutmut_10, 
    'x__log_deferred__mutmut_11': x__log_deferred__mutmut_11, 
    'x__log_deferred__mutmut_12': x__log_deferred__mutmut_12, 
    'x__log_deferred__mutmut_13': x__log_deferred__mutmut_13, 
    'x__log_deferred__mutmut_14': x__log_deferred__mutmut_14, 
    'x__log_deferred__mutmut_15': x__log_deferred__mutmut_15, 
    'x__log_deferred__mutmut_16': x__log_deferred__mutmut_16, 
    'x__log_deferred__mutmut_17': x__log_deferred__mutmut_17, 
    'x__log_deferred__mutmut_18': x__log_deferred__mutmut_18, 
    'x__log_deferred__mutmut_19': x__log_deferred__mutmut_19, 
    'x__log_deferred__mutmut_20': x__log_deferred__mutmut_20
}

def _log_deferred(*args, **kwargs):
    result = _mutmut_trampoline(x__log_deferred__mutmut_orig, x__log_deferred__mutmut_mutants, args, kwargs)
    return result 

_log_deferred.__signature__ = _mutmut_signature(x__log_deferred__mutmut_orig)
x__log_deferred__mutmut_orig.__name__ = 'x__log_deferred'


def x__resolve_path__mutmut_orig(path: Path) -> Path:
    if path.exists():
        return path
    if path.is_absolute():
        return path
    repo_root = Path(__file__).resolve().parents[3]
    candidate = repo_root / path
    return candidate


def x__resolve_path__mutmut_1(path: Path) -> Path:
    if path.exists():
        return path
    if path.is_absolute():
        return path
    repo_root = None
    candidate = repo_root / path
    return candidate


def x__resolve_path__mutmut_2(path: Path) -> Path:
    if path.exists():
        return path
    if path.is_absolute():
        return path
    repo_root = Path(None).resolve().parents[3]
    candidate = repo_root / path
    return candidate


def x__resolve_path__mutmut_3(path: Path) -> Path:
    if path.exists():
        return path
    if path.is_absolute():
        return path
    repo_root = Path(__file__).resolve().parents[4]
    candidate = repo_root / path
    return candidate


def x__resolve_path__mutmut_4(path: Path) -> Path:
    if path.exists():
        return path
    if path.is_absolute():
        return path
    repo_root = Path(__file__).resolve().parents[3]
    candidate = None
    return candidate


def x__resolve_path__mutmut_5(path: Path) -> Path:
    if path.exists():
        return path
    if path.is_absolute():
        return path
    repo_root = Path(__file__).resolve().parents[3]
    candidate = repo_root * path
    return candidate

x__resolve_path__mutmut_mutants : ClassVar[MutantDict] = {
'x__resolve_path__mutmut_1': x__resolve_path__mutmut_1, 
    'x__resolve_path__mutmut_2': x__resolve_path__mutmut_2, 
    'x__resolve_path__mutmut_3': x__resolve_path__mutmut_3, 
    'x__resolve_path__mutmut_4': x__resolve_path__mutmut_4, 
    'x__resolve_path__mutmut_5': x__resolve_path__mutmut_5
}

def _resolve_path(*args, **kwargs):
    result = _mutmut_trampoline(x__resolve_path__mutmut_orig, x__resolve_path__mutmut_mutants, args, kwargs)
    return result 

_resolve_path.__signature__ = _mutmut_signature(x__resolve_path__mutmut_orig)
x__resolve_path__mutmut_orig.__name__ = 'x__resolve_path'


def x__load_csv__mutmut_orig(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, idx, row, exc.errors(include_url=False))
                deferred += 1
    return MappingLoadResult(records=records, deferred=deferred)


def x__load_csv__mutmut_1(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = None
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, idx, row, exc.errors(include_url=False))
                deferred += 1
    return MappingLoadResult(records=records, deferred=deferred)


def x__load_csv__mutmut_2(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(None)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, idx, row, exc.errors(include_url=False))
                deferred += 1
    return MappingLoadResult(records=records, deferred=deferred)


def x__load_csv__mutmut_3(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, idx, row, exc.errors(include_url=False))
                deferred += 1
    return MappingLoadResult(records=records, deferred=deferred)


def x__load_csv__mutmut_4(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(None)

    records: list[T] = []
    deferred = 0
    with candidate.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, idx, row, exc.errors(include_url=False))
                deferred += 1
    return MappingLoadResult(records=records, deferred=deferred)


def x__load_csv__mutmut_5(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = None
    deferred = 0
    with candidate.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, idx, row, exc.errors(include_url=False))
                deferred += 1
    return MappingLoadResult(records=records, deferred=deferred)


def x__load_csv__mutmut_6(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = None
    with candidate.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, idx, row, exc.errors(include_url=False))
                deferred += 1
    return MappingLoadResult(records=records, deferred=deferred)


def x__load_csv__mutmut_7(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 1
    with candidate.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, idx, row, exc.errors(include_url=False))
                deferred += 1
    return MappingLoadResult(records=records, deferred=deferred)


def x__load_csv__mutmut_8(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open(None, encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, idx, row, exc.errors(include_url=False))
                deferred += 1
    return MappingLoadResult(records=records, deferred=deferred)


def x__load_csv__mutmut_9(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open("r", encoding=None, newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, idx, row, exc.errors(include_url=False))
                deferred += 1
    return MappingLoadResult(records=records, deferred=deferred)


def x__load_csv__mutmut_10(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open("r", encoding="utf-8", newline=None) as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, idx, row, exc.errors(include_url=False))
                deferred += 1
    return MappingLoadResult(records=records, deferred=deferred)


def x__load_csv__mutmut_11(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, idx, row, exc.errors(include_url=False))
                deferred += 1
    return MappingLoadResult(records=records, deferred=deferred)


def x__load_csv__mutmut_12(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open("r", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, idx, row, exc.errors(include_url=False))
                deferred += 1
    return MappingLoadResult(records=records, deferred=deferred)


def x__load_csv__mutmut_13(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open("r", encoding="utf-8", ) as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, idx, row, exc.errors(include_url=False))
                deferred += 1
    return MappingLoadResult(records=records, deferred=deferred)


def x__load_csv__mutmut_14(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open("XXrXX", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, idx, row, exc.errors(include_url=False))
                deferred += 1
    return MappingLoadResult(records=records, deferred=deferred)


def x__load_csv__mutmut_15(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open("R", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, idx, row, exc.errors(include_url=False))
                deferred += 1
    return MappingLoadResult(records=records, deferred=deferred)


def x__load_csv__mutmut_16(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open("r", encoding="XXutf-8XX", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, idx, row, exc.errors(include_url=False))
                deferred += 1
    return MappingLoadResult(records=records, deferred=deferred)


def x__load_csv__mutmut_17(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open("r", encoding="UTF-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, idx, row, exc.errors(include_url=False))
                deferred += 1
    return MappingLoadResult(records=records, deferred=deferred)


def x__load_csv__mutmut_18(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open("r", encoding="utf-8", newline="XXXX") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, idx, row, exc.errors(include_url=False))
                deferred += 1
    return MappingLoadResult(records=records, deferred=deferred)


def x__load_csv__mutmut_19(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open("r", encoding="utf-8", newline="") as handle:
        reader = None
        for idx, raw_row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, idx, row, exc.errors(include_url=False))
                deferred += 1
    return MappingLoadResult(records=records, deferred=deferred)


def x__load_csv__mutmut_20(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(None)
        for idx, raw_row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, idx, row, exc.errors(include_url=False))
                deferred += 1
    return MappingLoadResult(records=records, deferred=deferred)


def x__load_csv__mutmut_21(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(None, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, idx, row, exc.errors(include_url=False))
                deferred += 1
    return MappingLoadResult(records=records, deferred=deferred)


def x__load_csv__mutmut_22(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, start=None):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, idx, row, exc.errors(include_url=False))
                deferred += 1
    return MappingLoadResult(records=records, deferred=deferred)


def x__load_csv__mutmut_23(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, idx, row, exc.errors(include_url=False))
                deferred += 1
    return MappingLoadResult(records=records, deferred=deferred)


def x__load_csv__mutmut_24(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, ):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, idx, row, exc.errors(include_url=False))
                deferred += 1
    return MappingLoadResult(records=records, deferred=deferred)


def x__load_csv__mutmut_25(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, start=3):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, idx, row, exc.errors(include_url=False))
                deferred += 1
    return MappingLoadResult(records=records, deferred=deferred)


def x__load_csv__mutmut_26(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, start=2):
            row = None
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, idx, row, exc.errors(include_url=False))
                deferred += 1
    return MappingLoadResult(records=records, deferred=deferred)


def x__load_csv__mutmut_27(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, start=2):
            row = {key: (value and "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, idx, row, exc.errors(include_url=False))
                deferred += 1
    return MappingLoadResult(records=records, deferred=deferred)


def x__load_csv__mutmut_28(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, start=2):
            row = {key: (value or "XXXX").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, idx, row, exc.errors(include_url=False))
                deferred += 1
    return MappingLoadResult(records=records, deferred=deferred)


def x__load_csv__mutmut_29(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, idx, row, exc.errors(include_url=False))
                deferred += 1
    return MappingLoadResult(records=records, deferred=deferred)


def x__load_csv__mutmut_30(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(None):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, idx, row, exc.errors(include_url=False))
                deferred += 1
    return MappingLoadResult(records=records, deferred=deferred)


def x__load_csv__mutmut_31(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                break
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, idx, row, exc.errors(include_url=False))
                deferred += 1
    return MappingLoadResult(records=records, deferred=deferred)


def x__load_csv__mutmut_32(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(None)
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, idx, row, exc.errors(include_url=False))
                deferred += 1
    return MappingLoadResult(records=records, deferred=deferred)


def x__load_csv__mutmut_33(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(None))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, idx, row, exc.errors(include_url=False))
                deferred += 1
    return MappingLoadResult(records=records, deferred=deferred)


def x__load_csv__mutmut_34(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(None)
                _log_deferred(candidate, idx, row, exc.errors(include_url=False))
                deferred += 1
    return MappingLoadResult(records=records, deferred=deferred)


def x__load_csv__mutmut_35(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(None, idx, row, exc.errors(include_url=False))
                deferred += 1
    return MappingLoadResult(records=records, deferred=deferred)


def x__load_csv__mutmut_36(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, None, row, exc.errors(include_url=False))
                deferred += 1
    return MappingLoadResult(records=records, deferred=deferred)


def x__load_csv__mutmut_37(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, idx, None, exc.errors(include_url=False))
                deferred += 1
    return MappingLoadResult(records=records, deferred=deferred)


def x__load_csv__mutmut_38(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, idx, row, None)
                deferred += 1
    return MappingLoadResult(records=records, deferred=deferred)


def x__load_csv__mutmut_39(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(idx, row, exc.errors(include_url=False))
                deferred += 1
    return MappingLoadResult(records=records, deferred=deferred)


def x__load_csv__mutmut_40(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, row, exc.errors(include_url=False))
                deferred += 1
    return MappingLoadResult(records=records, deferred=deferred)


def x__load_csv__mutmut_41(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, idx, exc.errors(include_url=False))
                deferred += 1
    return MappingLoadResult(records=records, deferred=deferred)


def x__load_csv__mutmut_42(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, idx, row, )
                deferred += 1
    return MappingLoadResult(records=records, deferred=deferred)


def x__load_csv__mutmut_43(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, idx, row, exc.errors(include_url=None))
                deferred += 1
    return MappingLoadResult(records=records, deferred=deferred)


def x__load_csv__mutmut_44(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, idx, row, exc.errors(include_url=True))
                deferred += 1
    return MappingLoadResult(records=records, deferred=deferred)


def x__load_csv__mutmut_45(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, idx, row, exc.errors(include_url=False))
                deferred = 1
    return MappingLoadResult(records=records, deferred=deferred)


def x__load_csv__mutmut_46(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, idx, row, exc.errors(include_url=False))
                deferred -= 1
    return MappingLoadResult(records=records, deferred=deferred)


def x__load_csv__mutmut_47(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, idx, row, exc.errors(include_url=False))
                deferred += 2
    return MappingLoadResult(records=records, deferred=deferred)


def x__load_csv__mutmut_48(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, idx, row, exc.errors(include_url=False))
                deferred += 1
    return MappingLoadResult(records=None, deferred=deferred)


def x__load_csv__mutmut_49(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, idx, row, exc.errors(include_url=False))
                deferred += 1
    return MappingLoadResult(records=records, deferred=None)


def x__load_csv__mutmut_50(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, idx, row, exc.errors(include_url=False))
                deferred += 1
    return MappingLoadResult(deferred=deferred)


def x__load_csv__mutmut_51(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                logger.debug(f"ValidationError: {exc}")
                _log_deferred(candidate, idx, row, exc.errors(include_url=False))
                deferred += 1
    return MappingLoadResult(records=records, )

x__load_csv__mutmut_mutants : ClassVar[MutantDict] = {
'x__load_csv__mutmut_1': x__load_csv__mutmut_1, 
    'x__load_csv__mutmut_2': x__load_csv__mutmut_2, 
    'x__load_csv__mutmut_3': x__load_csv__mutmut_3, 
    'x__load_csv__mutmut_4': x__load_csv__mutmut_4, 
    'x__load_csv__mutmut_5': x__load_csv__mutmut_5, 
    'x__load_csv__mutmut_6': x__load_csv__mutmut_6, 
    'x__load_csv__mutmut_7': x__load_csv__mutmut_7, 
    'x__load_csv__mutmut_8': x__load_csv__mutmut_8, 
    'x__load_csv__mutmut_9': x__load_csv__mutmut_9, 
    'x__load_csv__mutmut_10': x__load_csv__mutmut_10, 
    'x__load_csv__mutmut_11': x__load_csv__mutmut_11, 
    'x__load_csv__mutmut_12': x__load_csv__mutmut_12, 
    'x__load_csv__mutmut_13': x__load_csv__mutmut_13, 
    'x__load_csv__mutmut_14': x__load_csv__mutmut_14, 
    'x__load_csv__mutmut_15': x__load_csv__mutmut_15, 
    'x__load_csv__mutmut_16': x__load_csv__mutmut_16, 
    'x__load_csv__mutmut_17': x__load_csv__mutmut_17, 
    'x__load_csv__mutmut_18': x__load_csv__mutmut_18, 
    'x__load_csv__mutmut_19': x__load_csv__mutmut_19, 
    'x__load_csv__mutmut_20': x__load_csv__mutmut_20, 
    'x__load_csv__mutmut_21': x__load_csv__mutmut_21, 
    'x__load_csv__mutmut_22': x__load_csv__mutmut_22, 
    'x__load_csv__mutmut_23': x__load_csv__mutmut_23, 
    'x__load_csv__mutmut_24': x__load_csv__mutmut_24, 
    'x__load_csv__mutmut_25': x__load_csv__mutmut_25, 
    'x__load_csv__mutmut_26': x__load_csv__mutmut_26, 
    'x__load_csv__mutmut_27': x__load_csv__mutmut_27, 
    'x__load_csv__mutmut_28': x__load_csv__mutmut_28, 
    'x__load_csv__mutmut_29': x__load_csv__mutmut_29, 
    'x__load_csv__mutmut_30': x__load_csv__mutmut_30, 
    'x__load_csv__mutmut_31': x__load_csv__mutmut_31, 
    'x__load_csv__mutmut_32': x__load_csv__mutmut_32, 
    'x__load_csv__mutmut_33': x__load_csv__mutmut_33, 
    'x__load_csv__mutmut_34': x__load_csv__mutmut_34, 
    'x__load_csv__mutmut_35': x__load_csv__mutmut_35, 
    'x__load_csv__mutmut_36': x__load_csv__mutmut_36, 
    'x__load_csv__mutmut_37': x__load_csv__mutmut_37, 
    'x__load_csv__mutmut_38': x__load_csv__mutmut_38, 
    'x__load_csv__mutmut_39': x__load_csv__mutmut_39, 
    'x__load_csv__mutmut_40': x__load_csv__mutmut_40, 
    'x__load_csv__mutmut_41': x__load_csv__mutmut_41, 
    'x__load_csv__mutmut_42': x__load_csv__mutmut_42, 
    'x__load_csv__mutmut_43': x__load_csv__mutmut_43, 
    'x__load_csv__mutmut_44': x__load_csv__mutmut_44, 
    'x__load_csv__mutmut_45': x__load_csv__mutmut_45, 
    'x__load_csv__mutmut_46': x__load_csv__mutmut_46, 
    'x__load_csv__mutmut_47': x__load_csv__mutmut_47, 
    'x__load_csv__mutmut_48': x__load_csv__mutmut_48, 
    'x__load_csv__mutmut_49': x__load_csv__mutmut_49, 
    'x__load_csv__mutmut_50': x__load_csv__mutmut_50, 
    'x__load_csv__mutmut_51': x__load_csv__mutmut_51
}

def _load_csv(*args, **kwargs):
    result = _mutmut_trampoline(x__load_csv__mutmut_orig, x__load_csv__mutmut_mutants, args, kwargs)
    return result 

_load_csv.__signature__ = _mutmut_signature(x__load_csv__mutmut_orig)
x__load_csv__mutmut_orig.__name__ = 'x__load_csv'


def x_load_routing__mutmut_orig(path: Path) -> MappingLoadResult[RoutingPattern]:
    return _load_csv(path, RoutingPattern)


def x_load_routing__mutmut_1(path: Path) -> MappingLoadResult[RoutingPattern]:
    return _load_csv(None, RoutingPattern)


def x_load_routing__mutmut_2(path: Path) -> MappingLoadResult[RoutingPattern]:
    return _load_csv(path, None)


def x_load_routing__mutmut_3(path: Path) -> MappingLoadResult[RoutingPattern]:
    return _load_csv(RoutingPattern)


def x_load_routing__mutmut_4(path: Path) -> MappingLoadResult[RoutingPattern]:
    return _load_csv(path, )

x_load_routing__mutmut_mutants : ClassVar[MutantDict] = {
'x_load_routing__mutmut_1': x_load_routing__mutmut_1, 
    'x_load_routing__mutmut_2': x_load_routing__mutmut_2, 
    'x_load_routing__mutmut_3': x_load_routing__mutmut_3, 
    'x_load_routing__mutmut_4': x_load_routing__mutmut_4
}

def load_routing(*args, **kwargs):
    result = _mutmut_trampoline(x_load_routing__mutmut_orig, x_load_routing__mutmut_mutants, args, kwargs)
    return result 

load_routing.__signature__ = _mutmut_signature(x_load_routing__mutmut_orig)
x_load_routing__mutmut_orig.__name__ = 'x_load_routing'


def x_load_sla__mutmut_orig(path: Path) -> MappingLoadResult[SlaParity]:
    return _load_csv(path, SlaParity)


def x_load_sla__mutmut_1(path: Path) -> MappingLoadResult[SlaParity]:
    return _load_csv(None, SlaParity)


def x_load_sla__mutmut_2(path: Path) -> MappingLoadResult[SlaParity]:
    return _load_csv(path, None)


def x_load_sla__mutmut_3(path: Path) -> MappingLoadResult[SlaParity]:
    return _load_csv(SlaParity)


def x_load_sla__mutmut_4(path: Path) -> MappingLoadResult[SlaParity]:
    return _load_csv(path, )

x_load_sla__mutmut_mutants : ClassVar[MutantDict] = {
'x_load_sla__mutmut_1': x_load_sla__mutmut_1, 
    'x_load_sla__mutmut_2': x_load_sla__mutmut_2, 
    'x_load_sla__mutmut_3': x_load_sla__mutmut_3, 
    'x_load_sla__mutmut_4': x_load_sla__mutmut_4
}

def load_sla(*args, **kwargs):
    result = _mutmut_trampoline(x_load_sla__mutmut_orig, x_load_sla__mutmut_mutants, args, kwargs)
    return result 

load_sla.__signature__ = _mutmut_signature(x_load_sla__mutmut_orig)
x_load_sla__mutmut_orig.__name__ = 'x_load_sla'


def x_load_all_mappings__mutmut_orig(mappings_dir: Path) -> dict[str, dict[str, object]]:
    routing = load_routing(mappings_dir / "routing_patterns.csv")
    slas = load_sla(mappings_dir / "sla_parity.csv")
    return {
        "routing": {
            "source": _resolve_path(mappings_dir / "routing_patterns.csv").as_posix(),
            "count": len(routing.records),
            "deferred": routing.deferred,
            "rows": [record.model_dump() for record in routing.records],
        },
        "sla": {
            "source": _resolve_path(mappings_dir / "sla_parity.csv").as_posix(),
            "count": len(slas.records),
            "deferred": slas.deferred,
            "rows": [record.model_dump() for record in slas.records],
        },
    }


def x_load_all_mappings__mutmut_1(mappings_dir: Path) -> dict[str, dict[str, object]]:
    routing = None
    slas = load_sla(mappings_dir / "sla_parity.csv")
    return {
        "routing": {
            "source": _resolve_path(mappings_dir / "routing_patterns.csv").as_posix(),
            "count": len(routing.records),
            "deferred": routing.deferred,
            "rows": [record.model_dump() for record in routing.records],
        },
        "sla": {
            "source": _resolve_path(mappings_dir / "sla_parity.csv").as_posix(),
            "count": len(slas.records),
            "deferred": slas.deferred,
            "rows": [record.model_dump() for record in slas.records],
        },
    }


def x_load_all_mappings__mutmut_2(mappings_dir: Path) -> dict[str, dict[str, object]]:
    routing = load_routing(None)
    slas = load_sla(mappings_dir / "sla_parity.csv")
    return {
        "routing": {
            "source": _resolve_path(mappings_dir / "routing_patterns.csv").as_posix(),
            "count": len(routing.records),
            "deferred": routing.deferred,
            "rows": [record.model_dump() for record in routing.records],
        },
        "sla": {
            "source": _resolve_path(mappings_dir / "sla_parity.csv").as_posix(),
            "count": len(slas.records),
            "deferred": slas.deferred,
            "rows": [record.model_dump() for record in slas.records],
        },
    }


def x_load_all_mappings__mutmut_3(mappings_dir: Path) -> dict[str, dict[str, object]]:
    routing = load_routing(mappings_dir * "routing_patterns.csv")
    slas = load_sla(mappings_dir / "sla_parity.csv")
    return {
        "routing": {
            "source": _resolve_path(mappings_dir / "routing_patterns.csv").as_posix(),
            "count": len(routing.records),
            "deferred": routing.deferred,
            "rows": [record.model_dump() for record in routing.records],
        },
        "sla": {
            "source": _resolve_path(mappings_dir / "sla_parity.csv").as_posix(),
            "count": len(slas.records),
            "deferred": slas.deferred,
            "rows": [record.model_dump() for record in slas.records],
        },
    }


def x_load_all_mappings__mutmut_4(mappings_dir: Path) -> dict[str, dict[str, object]]:
    routing = load_routing(mappings_dir / "XXrouting_patterns.csvXX")
    slas = load_sla(mappings_dir / "sla_parity.csv")
    return {
        "routing": {
            "source": _resolve_path(mappings_dir / "routing_patterns.csv").as_posix(),
            "count": len(routing.records),
            "deferred": routing.deferred,
            "rows": [record.model_dump() for record in routing.records],
        },
        "sla": {
            "source": _resolve_path(mappings_dir / "sla_parity.csv").as_posix(),
            "count": len(slas.records),
            "deferred": slas.deferred,
            "rows": [record.model_dump() for record in slas.records],
        },
    }


def x_load_all_mappings__mutmut_5(mappings_dir: Path) -> dict[str, dict[str, object]]:
    routing = load_routing(mappings_dir / "ROUTING_PATTERNS.CSV")
    slas = load_sla(mappings_dir / "sla_parity.csv")
    return {
        "routing": {
            "source": _resolve_path(mappings_dir / "routing_patterns.csv").as_posix(),
            "count": len(routing.records),
            "deferred": routing.deferred,
            "rows": [record.model_dump() for record in routing.records],
        },
        "sla": {
            "source": _resolve_path(mappings_dir / "sla_parity.csv").as_posix(),
            "count": len(slas.records),
            "deferred": slas.deferred,
            "rows": [record.model_dump() for record in slas.records],
        },
    }


def x_load_all_mappings__mutmut_6(mappings_dir: Path) -> dict[str, dict[str, object]]:
    routing = load_routing(mappings_dir / "routing_patterns.csv")
    slas = None
    return {
        "routing": {
            "source": _resolve_path(mappings_dir / "routing_patterns.csv").as_posix(),
            "count": len(routing.records),
            "deferred": routing.deferred,
            "rows": [record.model_dump() for record in routing.records],
        },
        "sla": {
            "source": _resolve_path(mappings_dir / "sla_parity.csv").as_posix(),
            "count": len(slas.records),
            "deferred": slas.deferred,
            "rows": [record.model_dump() for record in slas.records],
        },
    }


def x_load_all_mappings__mutmut_7(mappings_dir: Path) -> dict[str, dict[str, object]]:
    routing = load_routing(mappings_dir / "routing_patterns.csv")
    slas = load_sla(None)
    return {
        "routing": {
            "source": _resolve_path(mappings_dir / "routing_patterns.csv").as_posix(),
            "count": len(routing.records),
            "deferred": routing.deferred,
            "rows": [record.model_dump() for record in routing.records],
        },
        "sla": {
            "source": _resolve_path(mappings_dir / "sla_parity.csv").as_posix(),
            "count": len(slas.records),
            "deferred": slas.deferred,
            "rows": [record.model_dump() for record in slas.records],
        },
    }


def x_load_all_mappings__mutmut_8(mappings_dir: Path) -> dict[str, dict[str, object]]:
    routing = load_routing(mappings_dir / "routing_patterns.csv")
    slas = load_sla(mappings_dir * "sla_parity.csv")
    return {
        "routing": {
            "source": _resolve_path(mappings_dir / "routing_patterns.csv").as_posix(),
            "count": len(routing.records),
            "deferred": routing.deferred,
            "rows": [record.model_dump() for record in routing.records],
        },
        "sla": {
            "source": _resolve_path(mappings_dir / "sla_parity.csv").as_posix(),
            "count": len(slas.records),
            "deferred": slas.deferred,
            "rows": [record.model_dump() for record in slas.records],
        },
    }


def x_load_all_mappings__mutmut_9(mappings_dir: Path) -> dict[str, dict[str, object]]:
    routing = load_routing(mappings_dir / "routing_patterns.csv")
    slas = load_sla(mappings_dir / "XXsla_parity.csvXX")
    return {
        "routing": {
            "source": _resolve_path(mappings_dir / "routing_patterns.csv").as_posix(),
            "count": len(routing.records),
            "deferred": routing.deferred,
            "rows": [record.model_dump() for record in routing.records],
        },
        "sla": {
            "source": _resolve_path(mappings_dir / "sla_parity.csv").as_posix(),
            "count": len(slas.records),
            "deferred": slas.deferred,
            "rows": [record.model_dump() for record in slas.records],
        },
    }


def x_load_all_mappings__mutmut_10(mappings_dir: Path) -> dict[str, dict[str, object]]:
    routing = load_routing(mappings_dir / "routing_patterns.csv")
    slas = load_sla(mappings_dir / "SLA_PARITY.CSV")
    return {
        "routing": {
            "source": _resolve_path(mappings_dir / "routing_patterns.csv").as_posix(),
            "count": len(routing.records),
            "deferred": routing.deferred,
            "rows": [record.model_dump() for record in routing.records],
        },
        "sla": {
            "source": _resolve_path(mappings_dir / "sla_parity.csv").as_posix(),
            "count": len(slas.records),
            "deferred": slas.deferred,
            "rows": [record.model_dump() for record in slas.records],
        },
    }


def x_load_all_mappings__mutmut_11(mappings_dir: Path) -> dict[str, dict[str, object]]:
    routing = load_routing(mappings_dir / "routing_patterns.csv")
    slas = load_sla(mappings_dir / "sla_parity.csv")
    return {
        "XXroutingXX": {
            "source": _resolve_path(mappings_dir / "routing_patterns.csv").as_posix(),
            "count": len(routing.records),
            "deferred": routing.deferred,
            "rows": [record.model_dump() for record in routing.records],
        },
        "sla": {
            "source": _resolve_path(mappings_dir / "sla_parity.csv").as_posix(),
            "count": len(slas.records),
            "deferred": slas.deferred,
            "rows": [record.model_dump() for record in slas.records],
        },
    }


def x_load_all_mappings__mutmut_12(mappings_dir: Path) -> dict[str, dict[str, object]]:
    routing = load_routing(mappings_dir / "routing_patterns.csv")
    slas = load_sla(mappings_dir / "sla_parity.csv")
    return {
        "ROUTING": {
            "source": _resolve_path(mappings_dir / "routing_patterns.csv").as_posix(),
            "count": len(routing.records),
            "deferred": routing.deferred,
            "rows": [record.model_dump() for record in routing.records],
        },
        "sla": {
            "source": _resolve_path(mappings_dir / "sla_parity.csv").as_posix(),
            "count": len(slas.records),
            "deferred": slas.deferred,
            "rows": [record.model_dump() for record in slas.records],
        },
    }


def x_load_all_mappings__mutmut_13(mappings_dir: Path) -> dict[str, dict[str, object]]:
    routing = load_routing(mappings_dir / "routing_patterns.csv")
    slas = load_sla(mappings_dir / "sla_parity.csv")
    return {
        "routing": {
            "XXsourceXX": _resolve_path(mappings_dir / "routing_patterns.csv").as_posix(),
            "count": len(routing.records),
            "deferred": routing.deferred,
            "rows": [record.model_dump() for record in routing.records],
        },
        "sla": {
            "source": _resolve_path(mappings_dir / "sla_parity.csv").as_posix(),
            "count": len(slas.records),
            "deferred": slas.deferred,
            "rows": [record.model_dump() for record in slas.records],
        },
    }


def x_load_all_mappings__mutmut_14(mappings_dir: Path) -> dict[str, dict[str, object]]:
    routing = load_routing(mappings_dir / "routing_patterns.csv")
    slas = load_sla(mappings_dir / "sla_parity.csv")
    return {
        "routing": {
            "SOURCE": _resolve_path(mappings_dir / "routing_patterns.csv").as_posix(),
            "count": len(routing.records),
            "deferred": routing.deferred,
            "rows": [record.model_dump() for record in routing.records],
        },
        "sla": {
            "source": _resolve_path(mappings_dir / "sla_parity.csv").as_posix(),
            "count": len(slas.records),
            "deferred": slas.deferred,
            "rows": [record.model_dump() for record in slas.records],
        },
    }


def x_load_all_mappings__mutmut_15(mappings_dir: Path) -> dict[str, dict[str, object]]:
    routing = load_routing(mappings_dir / "routing_patterns.csv")
    slas = load_sla(mappings_dir / "sla_parity.csv")
    return {
        "routing": {
            "source": _resolve_path(None).as_posix(),
            "count": len(routing.records),
            "deferred": routing.deferred,
            "rows": [record.model_dump() for record in routing.records],
        },
        "sla": {
            "source": _resolve_path(mappings_dir / "sla_parity.csv").as_posix(),
            "count": len(slas.records),
            "deferred": slas.deferred,
            "rows": [record.model_dump() for record in slas.records],
        },
    }


def x_load_all_mappings__mutmut_16(mappings_dir: Path) -> dict[str, dict[str, object]]:
    routing = load_routing(mappings_dir / "routing_patterns.csv")
    slas = load_sla(mappings_dir / "sla_parity.csv")
    return {
        "routing": {
            "source": _resolve_path(mappings_dir * "routing_patterns.csv").as_posix(),
            "count": len(routing.records),
            "deferred": routing.deferred,
            "rows": [record.model_dump() for record in routing.records],
        },
        "sla": {
            "source": _resolve_path(mappings_dir / "sla_parity.csv").as_posix(),
            "count": len(slas.records),
            "deferred": slas.deferred,
            "rows": [record.model_dump() for record in slas.records],
        },
    }


def x_load_all_mappings__mutmut_17(mappings_dir: Path) -> dict[str, dict[str, object]]:
    routing = load_routing(mappings_dir / "routing_patterns.csv")
    slas = load_sla(mappings_dir / "sla_parity.csv")
    return {
        "routing": {
            "source": _resolve_path(mappings_dir / "XXrouting_patterns.csvXX").as_posix(),
            "count": len(routing.records),
            "deferred": routing.deferred,
            "rows": [record.model_dump() for record in routing.records],
        },
        "sla": {
            "source": _resolve_path(mappings_dir / "sla_parity.csv").as_posix(),
            "count": len(slas.records),
            "deferred": slas.deferred,
            "rows": [record.model_dump() for record in slas.records],
        },
    }


def x_load_all_mappings__mutmut_18(mappings_dir: Path) -> dict[str, dict[str, object]]:
    routing = load_routing(mappings_dir / "routing_patterns.csv")
    slas = load_sla(mappings_dir / "sla_parity.csv")
    return {
        "routing": {
            "source": _resolve_path(mappings_dir / "ROUTING_PATTERNS.CSV").as_posix(),
            "count": len(routing.records),
            "deferred": routing.deferred,
            "rows": [record.model_dump() for record in routing.records],
        },
        "sla": {
            "source": _resolve_path(mappings_dir / "sla_parity.csv").as_posix(),
            "count": len(slas.records),
            "deferred": slas.deferred,
            "rows": [record.model_dump() for record in slas.records],
        },
    }


def x_load_all_mappings__mutmut_19(mappings_dir: Path) -> dict[str, dict[str, object]]:
    routing = load_routing(mappings_dir / "routing_patterns.csv")
    slas = load_sla(mappings_dir / "sla_parity.csv")
    return {
        "routing": {
            "source": _resolve_path(mappings_dir / "routing_patterns.csv").as_posix(),
            "XXcountXX": len(routing.records),
            "deferred": routing.deferred,
            "rows": [record.model_dump() for record in routing.records],
        },
        "sla": {
            "source": _resolve_path(mappings_dir / "sla_parity.csv").as_posix(),
            "count": len(slas.records),
            "deferred": slas.deferred,
            "rows": [record.model_dump() for record in slas.records],
        },
    }


def x_load_all_mappings__mutmut_20(mappings_dir: Path) -> dict[str, dict[str, object]]:
    routing = load_routing(mappings_dir / "routing_patterns.csv")
    slas = load_sla(mappings_dir / "sla_parity.csv")
    return {
        "routing": {
            "source": _resolve_path(mappings_dir / "routing_patterns.csv").as_posix(),
            "COUNT": len(routing.records),
            "deferred": routing.deferred,
            "rows": [record.model_dump() for record in routing.records],
        },
        "sla": {
            "source": _resolve_path(mappings_dir / "sla_parity.csv").as_posix(),
            "count": len(slas.records),
            "deferred": slas.deferred,
            "rows": [record.model_dump() for record in slas.records],
        },
    }


def x_load_all_mappings__mutmut_21(mappings_dir: Path) -> dict[str, dict[str, object]]:
    routing = load_routing(mappings_dir / "routing_patterns.csv")
    slas = load_sla(mappings_dir / "sla_parity.csv")
    return {
        "routing": {
            "source": _resolve_path(mappings_dir / "routing_patterns.csv").as_posix(),
            "count": len(routing.records),
            "XXdeferredXX": routing.deferred,
            "rows": [record.model_dump() for record in routing.records],
        },
        "sla": {
            "source": _resolve_path(mappings_dir / "sla_parity.csv").as_posix(),
            "count": len(slas.records),
            "deferred": slas.deferred,
            "rows": [record.model_dump() for record in slas.records],
        },
    }


def x_load_all_mappings__mutmut_22(mappings_dir: Path) -> dict[str, dict[str, object]]:
    routing = load_routing(mappings_dir / "routing_patterns.csv")
    slas = load_sla(mappings_dir / "sla_parity.csv")
    return {
        "routing": {
            "source": _resolve_path(mappings_dir / "routing_patterns.csv").as_posix(),
            "count": len(routing.records),
            "DEFERRED": routing.deferred,
            "rows": [record.model_dump() for record in routing.records],
        },
        "sla": {
            "source": _resolve_path(mappings_dir / "sla_parity.csv").as_posix(),
            "count": len(slas.records),
            "deferred": slas.deferred,
            "rows": [record.model_dump() for record in slas.records],
        },
    }


def x_load_all_mappings__mutmut_23(mappings_dir: Path) -> dict[str, dict[str, object]]:
    routing = load_routing(mappings_dir / "routing_patterns.csv")
    slas = load_sla(mappings_dir / "sla_parity.csv")
    return {
        "routing": {
            "source": _resolve_path(mappings_dir / "routing_patterns.csv").as_posix(),
            "count": len(routing.records),
            "deferred": routing.deferred,
            "XXrowsXX": [record.model_dump() for record in routing.records],
        },
        "sla": {
            "source": _resolve_path(mappings_dir / "sla_parity.csv").as_posix(),
            "count": len(slas.records),
            "deferred": slas.deferred,
            "rows": [record.model_dump() for record in slas.records],
        },
    }


def x_load_all_mappings__mutmut_24(mappings_dir: Path) -> dict[str, dict[str, object]]:
    routing = load_routing(mappings_dir / "routing_patterns.csv")
    slas = load_sla(mappings_dir / "sla_parity.csv")
    return {
        "routing": {
            "source": _resolve_path(mappings_dir / "routing_patterns.csv").as_posix(),
            "count": len(routing.records),
            "deferred": routing.deferred,
            "ROWS": [record.model_dump() for record in routing.records],
        },
        "sla": {
            "source": _resolve_path(mappings_dir / "sla_parity.csv").as_posix(),
            "count": len(slas.records),
            "deferred": slas.deferred,
            "rows": [record.model_dump() for record in slas.records],
        },
    }


def x_load_all_mappings__mutmut_25(mappings_dir: Path) -> dict[str, dict[str, object]]:
    routing = load_routing(mappings_dir / "routing_patterns.csv")
    slas = load_sla(mappings_dir / "sla_parity.csv")
    return {
        "routing": {
            "source": _resolve_path(mappings_dir / "routing_patterns.csv").as_posix(),
            "count": len(routing.records),
            "deferred": routing.deferred,
            "rows": [record.model_dump() for record in routing.records],
        },
        "XXslaXX": {
            "source": _resolve_path(mappings_dir / "sla_parity.csv").as_posix(),
            "count": len(slas.records),
            "deferred": slas.deferred,
            "rows": [record.model_dump() for record in slas.records],
        },
    }


def x_load_all_mappings__mutmut_26(mappings_dir: Path) -> dict[str, dict[str, object]]:
    routing = load_routing(mappings_dir / "routing_patterns.csv")
    slas = load_sla(mappings_dir / "sla_parity.csv")
    return {
        "routing": {
            "source": _resolve_path(mappings_dir / "routing_patterns.csv").as_posix(),
            "count": len(routing.records),
            "deferred": routing.deferred,
            "rows": [record.model_dump() for record in routing.records],
        },
        "SLA": {
            "source": _resolve_path(mappings_dir / "sla_parity.csv").as_posix(),
            "count": len(slas.records),
            "deferred": slas.deferred,
            "rows": [record.model_dump() for record in slas.records],
        },
    }


def x_load_all_mappings__mutmut_27(mappings_dir: Path) -> dict[str, dict[str, object]]:
    routing = load_routing(mappings_dir / "routing_patterns.csv")
    slas = load_sla(mappings_dir / "sla_parity.csv")
    return {
        "routing": {
            "source": _resolve_path(mappings_dir / "routing_patterns.csv").as_posix(),
            "count": len(routing.records),
            "deferred": routing.deferred,
            "rows": [record.model_dump() for record in routing.records],
        },
        "sla": {
            "XXsourceXX": _resolve_path(mappings_dir / "sla_parity.csv").as_posix(),
            "count": len(slas.records),
            "deferred": slas.deferred,
            "rows": [record.model_dump() for record in slas.records],
        },
    }


def x_load_all_mappings__mutmut_28(mappings_dir: Path) -> dict[str, dict[str, object]]:
    routing = load_routing(mappings_dir / "routing_patterns.csv")
    slas = load_sla(mappings_dir / "sla_parity.csv")
    return {
        "routing": {
            "source": _resolve_path(mappings_dir / "routing_patterns.csv").as_posix(),
            "count": len(routing.records),
            "deferred": routing.deferred,
            "rows": [record.model_dump() for record in routing.records],
        },
        "sla": {
            "SOURCE": _resolve_path(mappings_dir / "sla_parity.csv").as_posix(),
            "count": len(slas.records),
            "deferred": slas.deferred,
            "rows": [record.model_dump() for record in slas.records],
        },
    }


def x_load_all_mappings__mutmut_29(mappings_dir: Path) -> dict[str, dict[str, object]]:
    routing = load_routing(mappings_dir / "routing_patterns.csv")
    slas = load_sla(mappings_dir / "sla_parity.csv")
    return {
        "routing": {
            "source": _resolve_path(mappings_dir / "routing_patterns.csv").as_posix(),
            "count": len(routing.records),
            "deferred": routing.deferred,
            "rows": [record.model_dump() for record in routing.records],
        },
        "sla": {
            "source": _resolve_path(None).as_posix(),
            "count": len(slas.records),
            "deferred": slas.deferred,
            "rows": [record.model_dump() for record in slas.records],
        },
    }


def x_load_all_mappings__mutmut_30(mappings_dir: Path) -> dict[str, dict[str, object]]:
    routing = load_routing(mappings_dir / "routing_patterns.csv")
    slas = load_sla(mappings_dir / "sla_parity.csv")
    return {
        "routing": {
            "source": _resolve_path(mappings_dir / "routing_patterns.csv").as_posix(),
            "count": len(routing.records),
            "deferred": routing.deferred,
            "rows": [record.model_dump() for record in routing.records],
        },
        "sla": {
            "source": _resolve_path(mappings_dir * "sla_parity.csv").as_posix(),
            "count": len(slas.records),
            "deferred": slas.deferred,
            "rows": [record.model_dump() for record in slas.records],
        },
    }


def x_load_all_mappings__mutmut_31(mappings_dir: Path) -> dict[str, dict[str, object]]:
    routing = load_routing(mappings_dir / "routing_patterns.csv")
    slas = load_sla(mappings_dir / "sla_parity.csv")
    return {
        "routing": {
            "source": _resolve_path(mappings_dir / "routing_patterns.csv").as_posix(),
            "count": len(routing.records),
            "deferred": routing.deferred,
            "rows": [record.model_dump() for record in routing.records],
        },
        "sla": {
            "source": _resolve_path(mappings_dir / "XXsla_parity.csvXX").as_posix(),
            "count": len(slas.records),
            "deferred": slas.deferred,
            "rows": [record.model_dump() for record in slas.records],
        },
    }


def x_load_all_mappings__mutmut_32(mappings_dir: Path) -> dict[str, dict[str, object]]:
    routing = load_routing(mappings_dir / "routing_patterns.csv")
    slas = load_sla(mappings_dir / "sla_parity.csv")
    return {
        "routing": {
            "source": _resolve_path(mappings_dir / "routing_patterns.csv").as_posix(),
            "count": len(routing.records),
            "deferred": routing.deferred,
            "rows": [record.model_dump() for record in routing.records],
        },
        "sla": {
            "source": _resolve_path(mappings_dir / "SLA_PARITY.CSV").as_posix(),
            "count": len(slas.records),
            "deferred": slas.deferred,
            "rows": [record.model_dump() for record in slas.records],
        },
    }


def x_load_all_mappings__mutmut_33(mappings_dir: Path) -> dict[str, dict[str, object]]:
    routing = load_routing(mappings_dir / "routing_patterns.csv")
    slas = load_sla(mappings_dir / "sla_parity.csv")
    return {
        "routing": {
            "source": _resolve_path(mappings_dir / "routing_patterns.csv").as_posix(),
            "count": len(routing.records),
            "deferred": routing.deferred,
            "rows": [record.model_dump() for record in routing.records],
        },
        "sla": {
            "source": _resolve_path(mappings_dir / "sla_parity.csv").as_posix(),
            "XXcountXX": len(slas.records),
            "deferred": slas.deferred,
            "rows": [record.model_dump() for record in slas.records],
        },
    }


def x_load_all_mappings__mutmut_34(mappings_dir: Path) -> dict[str, dict[str, object]]:
    routing = load_routing(mappings_dir / "routing_patterns.csv")
    slas = load_sla(mappings_dir / "sla_parity.csv")
    return {
        "routing": {
            "source": _resolve_path(mappings_dir / "routing_patterns.csv").as_posix(),
            "count": len(routing.records),
            "deferred": routing.deferred,
            "rows": [record.model_dump() for record in routing.records],
        },
        "sla": {
            "source": _resolve_path(mappings_dir / "sla_parity.csv").as_posix(),
            "COUNT": len(slas.records),
            "deferred": slas.deferred,
            "rows": [record.model_dump() for record in slas.records],
        },
    }


def x_load_all_mappings__mutmut_35(mappings_dir: Path) -> dict[str, dict[str, object]]:
    routing = load_routing(mappings_dir / "routing_patterns.csv")
    slas = load_sla(mappings_dir / "sla_parity.csv")
    return {
        "routing": {
            "source": _resolve_path(mappings_dir / "routing_patterns.csv").as_posix(),
            "count": len(routing.records),
            "deferred": routing.deferred,
            "rows": [record.model_dump() for record in routing.records],
        },
        "sla": {
            "source": _resolve_path(mappings_dir / "sla_parity.csv").as_posix(),
            "count": len(slas.records),
            "XXdeferredXX": slas.deferred,
            "rows": [record.model_dump() for record in slas.records],
        },
    }


def x_load_all_mappings__mutmut_36(mappings_dir: Path) -> dict[str, dict[str, object]]:
    routing = load_routing(mappings_dir / "routing_patterns.csv")
    slas = load_sla(mappings_dir / "sla_parity.csv")
    return {
        "routing": {
            "source": _resolve_path(mappings_dir / "routing_patterns.csv").as_posix(),
            "count": len(routing.records),
            "deferred": routing.deferred,
            "rows": [record.model_dump() for record in routing.records],
        },
        "sla": {
            "source": _resolve_path(mappings_dir / "sla_parity.csv").as_posix(),
            "count": len(slas.records),
            "DEFERRED": slas.deferred,
            "rows": [record.model_dump() for record in slas.records],
        },
    }


def x_load_all_mappings__mutmut_37(mappings_dir: Path) -> dict[str, dict[str, object]]:
    routing = load_routing(mappings_dir / "routing_patterns.csv")
    slas = load_sla(mappings_dir / "sla_parity.csv")
    return {
        "routing": {
            "source": _resolve_path(mappings_dir / "routing_patterns.csv").as_posix(),
            "count": len(routing.records),
            "deferred": routing.deferred,
            "rows": [record.model_dump() for record in routing.records],
        },
        "sla": {
            "source": _resolve_path(mappings_dir / "sla_parity.csv").as_posix(),
            "count": len(slas.records),
            "deferred": slas.deferred,
            "XXrowsXX": [record.model_dump() for record in slas.records],
        },
    }


def x_load_all_mappings__mutmut_38(mappings_dir: Path) -> dict[str, dict[str, object]]:
    routing = load_routing(mappings_dir / "routing_patterns.csv")
    slas = load_sla(mappings_dir / "sla_parity.csv")
    return {
        "routing": {
            "source": _resolve_path(mappings_dir / "routing_patterns.csv").as_posix(),
            "count": len(routing.records),
            "deferred": routing.deferred,
            "rows": [record.model_dump() for record in routing.records],
        },
        "sla": {
            "source": _resolve_path(mappings_dir / "sla_parity.csv").as_posix(),
            "count": len(slas.records),
            "deferred": slas.deferred,
            "ROWS": [record.model_dump() for record in slas.records],
        },
    }

x_load_all_mappings__mutmut_mutants : ClassVar[MutantDict] = {
'x_load_all_mappings__mutmut_1': x_load_all_mappings__mutmut_1, 
    'x_load_all_mappings__mutmut_2': x_load_all_mappings__mutmut_2, 
    'x_load_all_mappings__mutmut_3': x_load_all_mappings__mutmut_3, 
    'x_load_all_mappings__mutmut_4': x_load_all_mappings__mutmut_4, 
    'x_load_all_mappings__mutmut_5': x_load_all_mappings__mutmut_5, 
    'x_load_all_mappings__mutmut_6': x_load_all_mappings__mutmut_6, 
    'x_load_all_mappings__mutmut_7': x_load_all_mappings__mutmut_7, 
    'x_load_all_mappings__mutmut_8': x_load_all_mappings__mutmut_8, 
    'x_load_all_mappings__mutmut_9': x_load_all_mappings__mutmut_9, 
    'x_load_all_mappings__mutmut_10': x_load_all_mappings__mutmut_10, 
    'x_load_all_mappings__mutmut_11': x_load_all_mappings__mutmut_11, 
    'x_load_all_mappings__mutmut_12': x_load_all_mappings__mutmut_12, 
    'x_load_all_mappings__mutmut_13': x_load_all_mappings__mutmut_13, 
    'x_load_all_mappings__mutmut_14': x_load_all_mappings__mutmut_14, 
    'x_load_all_mappings__mutmut_15': x_load_all_mappings__mutmut_15, 
    'x_load_all_mappings__mutmut_16': x_load_all_mappings__mutmut_16, 
    'x_load_all_mappings__mutmut_17': x_load_all_mappings__mutmut_17, 
    'x_load_all_mappings__mutmut_18': x_load_all_mappings__mutmut_18, 
    'x_load_all_mappings__mutmut_19': x_load_all_mappings__mutmut_19, 
    'x_load_all_mappings__mutmut_20': x_load_all_mappings__mutmut_20, 
    'x_load_all_mappings__mutmut_21': x_load_all_mappings__mutmut_21, 
    'x_load_all_mappings__mutmut_22': x_load_all_mappings__mutmut_22, 
    'x_load_all_mappings__mutmut_23': x_load_all_mappings__mutmut_23, 
    'x_load_all_mappings__mutmut_24': x_load_all_mappings__mutmut_24, 
    'x_load_all_mappings__mutmut_25': x_load_all_mappings__mutmut_25, 
    'x_load_all_mappings__mutmut_26': x_load_all_mappings__mutmut_26, 
    'x_load_all_mappings__mutmut_27': x_load_all_mappings__mutmut_27, 
    'x_load_all_mappings__mutmut_28': x_load_all_mappings__mutmut_28, 
    'x_load_all_mappings__mutmut_29': x_load_all_mappings__mutmut_29, 
    'x_load_all_mappings__mutmut_30': x_load_all_mappings__mutmut_30, 
    'x_load_all_mappings__mutmut_31': x_load_all_mappings__mutmut_31, 
    'x_load_all_mappings__mutmut_32': x_load_all_mappings__mutmut_32, 
    'x_load_all_mappings__mutmut_33': x_load_all_mappings__mutmut_33, 
    'x_load_all_mappings__mutmut_34': x_load_all_mappings__mutmut_34, 
    'x_load_all_mappings__mutmut_35': x_load_all_mappings__mutmut_35, 
    'x_load_all_mappings__mutmut_36': x_load_all_mappings__mutmut_36, 
    'x_load_all_mappings__mutmut_37': x_load_all_mappings__mutmut_37, 
    'x_load_all_mappings__mutmut_38': x_load_all_mappings__mutmut_38
}

def load_all_mappings(*args, **kwargs):
    result = _mutmut_trampoline(x_load_all_mappings__mutmut_orig, x_load_all_mappings__mutmut_mutants, args, kwargs)
    return result 

load_all_mappings.__signature__ = _mutmut_signature(x_load_all_mappings__mutmut_orig)
x_load_all_mappings__mutmut_orig.__name__ = 'x_load_all_mappings'
