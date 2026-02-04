"""
Validate Module

This module provides functionality for validate.

Usage:
    from common.validate import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import csv
import logging
import shutil
import site
import sys
from importlib import import_module
from pathlib import Path

# Ensure the installed Great Expectations package takes precedence over
# the repository-local configuration directory of the same name.
for _site_path in site.getsitepackages():
    if _site_path in sys.path:
        sys.path.remove(_site_path)
    sys.path.insert(0, _site_path)

gx = import_module("great_expectations")

logger = logging.getLogger(__name__)
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


def x__ensure_docs_out__mutmut_orig() -> Path:
    out = Path(".codex") / "ge_docs"
    out.mkdir(parents=True, exist_ok=True)
    return out


def x__ensure_docs_out__mutmut_1() -> Path:
    out = None
    out.mkdir(parents=True, exist_ok=True)
    return out


def x__ensure_docs_out__mutmut_2() -> Path:
    out = Path(".codex") * "ge_docs"
    out.mkdir(parents=True, exist_ok=True)
    return out


def x__ensure_docs_out__mutmut_3() -> Path:
    out = Path(None) / "ge_docs"
    out.mkdir(parents=True, exist_ok=True)
    return out


def x__ensure_docs_out__mutmut_4() -> Path:
    out = Path("XX.codexXX") / "ge_docs"
    out.mkdir(parents=True, exist_ok=True)
    return out


def x__ensure_docs_out__mutmut_5() -> Path:
    out = Path(".CODEX") / "ge_docs"
    out.mkdir(parents=True, exist_ok=True)
    return out


def x__ensure_docs_out__mutmut_6() -> Path:
    out = Path(".codex") / "XXge_docsXX"
    out.mkdir(parents=True, exist_ok=True)
    return out


def x__ensure_docs_out__mutmut_7() -> Path:
    out = Path(".codex") / "GE_DOCS"
    out.mkdir(parents=True, exist_ok=True)
    return out


def x__ensure_docs_out__mutmut_8() -> Path:
    out = Path(".codex") / "ge_docs"
    out.mkdir(parents=None, exist_ok=True)
    return out


def x__ensure_docs_out__mutmut_9() -> Path:
    out = Path(".codex") / "ge_docs"
    out.mkdir(parents=True, exist_ok=None)
    return out


def x__ensure_docs_out__mutmut_10() -> Path:
    out = Path(".codex") / "ge_docs"
    out.mkdir(exist_ok=True)
    return out


def x__ensure_docs_out__mutmut_11() -> Path:
    out = Path(".codex") / "ge_docs"
    out.mkdir(parents=True, )
    return out


def x__ensure_docs_out__mutmut_12() -> Path:
    out = Path(".codex") / "ge_docs"
    out.mkdir(parents=False, exist_ok=True)
    return out


def x__ensure_docs_out__mutmut_13() -> Path:
    out = Path(".codex") / "ge_docs"
    out.mkdir(parents=True, exist_ok=False)
    return out

x__ensure_docs_out__mutmut_mutants : ClassVar[MutantDict] = {
'x__ensure_docs_out__mutmut_1': x__ensure_docs_out__mutmut_1, 
    'x__ensure_docs_out__mutmut_2': x__ensure_docs_out__mutmut_2, 
    'x__ensure_docs_out__mutmut_3': x__ensure_docs_out__mutmut_3, 
    'x__ensure_docs_out__mutmut_4': x__ensure_docs_out__mutmut_4, 
    'x__ensure_docs_out__mutmut_5': x__ensure_docs_out__mutmut_5, 
    'x__ensure_docs_out__mutmut_6': x__ensure_docs_out__mutmut_6, 
    'x__ensure_docs_out__mutmut_7': x__ensure_docs_out__mutmut_7, 
    'x__ensure_docs_out__mutmut_8': x__ensure_docs_out__mutmut_8, 
    'x__ensure_docs_out__mutmut_9': x__ensure_docs_out__mutmut_9, 
    'x__ensure_docs_out__mutmut_10': x__ensure_docs_out__mutmut_10, 
    'x__ensure_docs_out__mutmut_11': x__ensure_docs_out__mutmut_11, 
    'x__ensure_docs_out__mutmut_12': x__ensure_docs_out__mutmut_12, 
    'x__ensure_docs_out__mutmut_13': x__ensure_docs_out__mutmut_13
}

def _ensure_docs_out(*args, **kwargs):
    result = _mutmut_trampoline(x__ensure_docs_out__mutmut_orig, x__ensure_docs_out__mutmut_mutants, args, kwargs)
    return result 

_ensure_docs_out.__signature__ = _mutmut_signature(x__ensure_docs_out__mutmut_orig)
x__ensure_docs_out__mutmut_orig.__name__ = 'x__ensure_docs_out'


def x__fallback_validate__mutmut_orig(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = set()
    with clean_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get("id") or not row.get("value"):
                raise RuntimeError("GE validation failed for cleaned dataset.")
            if row["id"] in seen_ids:
                raise RuntimeError("GE validation failed for cleaned dataset.")
            seen_ids.add(row["id"])
            try:
                value = int(row["value"])
            except ValueError as exc:
                logger.debug(f"ValueError: {exc}")
                raise RuntimeError("GE validation failed for cleaned dataset.") from exc
            if not 0 <= value <= 2:
                raise RuntimeError("GE validation failed for cleaned dataset.")
    return True, docs_out


def x__fallback_validate__mutmut_1(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = None
    seen_ids = set()
    with clean_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get("id") or not row.get("value"):
                raise RuntimeError("GE validation failed for cleaned dataset.")
            if row["id"] in seen_ids:
                raise RuntimeError("GE validation failed for cleaned dataset.")
            seen_ids.add(row["id"])
            try:
                value = int(row["value"])
            except ValueError as exc:
                logger.debug(f"ValueError: {exc}")
                raise RuntimeError("GE validation failed for cleaned dataset.") from exc
            if not 0 <= value <= 2:
                raise RuntimeError("GE validation failed for cleaned dataset.")
    return True, docs_out


def x__fallback_validate__mutmut_2(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = None
    with clean_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get("id") or not row.get("value"):
                raise RuntimeError("GE validation failed for cleaned dataset.")
            if row["id"] in seen_ids:
                raise RuntimeError("GE validation failed for cleaned dataset.")
            seen_ids.add(row["id"])
            try:
                value = int(row["value"])
            except ValueError as exc:
                logger.debug(f"ValueError: {exc}")
                raise RuntimeError("GE validation failed for cleaned dataset.") from exc
            if not 0 <= value <= 2:
                raise RuntimeError("GE validation failed for cleaned dataset.")
    return True, docs_out


def x__fallback_validate__mutmut_3(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = set()
    with clean_csv.open(newline=None) as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get("id") or not row.get("value"):
                raise RuntimeError("GE validation failed for cleaned dataset.")
            if row["id"] in seen_ids:
                raise RuntimeError("GE validation failed for cleaned dataset.")
            seen_ids.add(row["id"])
            try:
                value = int(row["value"])
            except ValueError as exc:
                logger.debug(f"ValueError: {exc}")
                raise RuntimeError("GE validation failed for cleaned dataset.") from exc
            if not 0 <= value <= 2:
                raise RuntimeError("GE validation failed for cleaned dataset.")
    return True, docs_out


def x__fallback_validate__mutmut_4(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = set()
    with clean_csv.open(newline="XXXX") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get("id") or not row.get("value"):
                raise RuntimeError("GE validation failed for cleaned dataset.")
            if row["id"] in seen_ids:
                raise RuntimeError("GE validation failed for cleaned dataset.")
            seen_ids.add(row["id"])
            try:
                value = int(row["value"])
            except ValueError as exc:
                logger.debug(f"ValueError: {exc}")
                raise RuntimeError("GE validation failed for cleaned dataset.") from exc
            if not 0 <= value <= 2:
                raise RuntimeError("GE validation failed for cleaned dataset.")
    return True, docs_out


def x__fallback_validate__mutmut_5(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = set()
    with clean_csv.open(newline="") as handle:
        reader = None
        for row in reader:
            if not row.get("id") or not row.get("value"):
                raise RuntimeError("GE validation failed for cleaned dataset.")
            if row["id"] in seen_ids:
                raise RuntimeError("GE validation failed for cleaned dataset.")
            seen_ids.add(row["id"])
            try:
                value = int(row["value"])
            except ValueError as exc:
                logger.debug(f"ValueError: {exc}")
                raise RuntimeError("GE validation failed for cleaned dataset.") from exc
            if not 0 <= value <= 2:
                raise RuntimeError("GE validation failed for cleaned dataset.")
    return True, docs_out


def x__fallback_validate__mutmut_6(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = set()
    with clean_csv.open(newline="") as handle:
        reader = csv.DictReader(None)
        for row in reader:
            if not row.get("id") or not row.get("value"):
                raise RuntimeError("GE validation failed for cleaned dataset.")
            if row["id"] in seen_ids:
                raise RuntimeError("GE validation failed for cleaned dataset.")
            seen_ids.add(row["id"])
            try:
                value = int(row["value"])
            except ValueError as exc:
                logger.debug(f"ValueError: {exc}")
                raise RuntimeError("GE validation failed for cleaned dataset.") from exc
            if not 0 <= value <= 2:
                raise RuntimeError("GE validation failed for cleaned dataset.")
    return True, docs_out


def x__fallback_validate__mutmut_7(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = set()
    with clean_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get("id") and not row.get("value"):
                raise RuntimeError("GE validation failed for cleaned dataset.")
            if row["id"] in seen_ids:
                raise RuntimeError("GE validation failed for cleaned dataset.")
            seen_ids.add(row["id"])
            try:
                value = int(row["value"])
            except ValueError as exc:
                logger.debug(f"ValueError: {exc}")
                raise RuntimeError("GE validation failed for cleaned dataset.") from exc
            if not 0 <= value <= 2:
                raise RuntimeError("GE validation failed for cleaned dataset.")
    return True, docs_out


def x__fallback_validate__mutmut_8(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = set()
    with clean_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if row.get("id") or not row.get("value"):
                raise RuntimeError("GE validation failed for cleaned dataset.")
            if row["id"] in seen_ids:
                raise RuntimeError("GE validation failed for cleaned dataset.")
            seen_ids.add(row["id"])
            try:
                value = int(row["value"])
            except ValueError as exc:
                logger.debug(f"ValueError: {exc}")
                raise RuntimeError("GE validation failed for cleaned dataset.") from exc
            if not 0 <= value <= 2:
                raise RuntimeError("GE validation failed for cleaned dataset.")
    return True, docs_out


def x__fallback_validate__mutmut_9(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = set()
    with clean_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get(None) or not row.get("value"):
                raise RuntimeError("GE validation failed for cleaned dataset.")
            if row["id"] in seen_ids:
                raise RuntimeError("GE validation failed for cleaned dataset.")
            seen_ids.add(row["id"])
            try:
                value = int(row["value"])
            except ValueError as exc:
                logger.debug(f"ValueError: {exc}")
                raise RuntimeError("GE validation failed for cleaned dataset.") from exc
            if not 0 <= value <= 2:
                raise RuntimeError("GE validation failed for cleaned dataset.")
    return True, docs_out


def x__fallback_validate__mutmut_10(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = set()
    with clean_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get("XXidXX") or not row.get("value"):
                raise RuntimeError("GE validation failed for cleaned dataset.")
            if row["id"] in seen_ids:
                raise RuntimeError("GE validation failed for cleaned dataset.")
            seen_ids.add(row["id"])
            try:
                value = int(row["value"])
            except ValueError as exc:
                logger.debug(f"ValueError: {exc}")
                raise RuntimeError("GE validation failed for cleaned dataset.") from exc
            if not 0 <= value <= 2:
                raise RuntimeError("GE validation failed for cleaned dataset.")
    return True, docs_out


def x__fallback_validate__mutmut_11(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = set()
    with clean_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get("ID") or not row.get("value"):
                raise RuntimeError("GE validation failed for cleaned dataset.")
            if row["id"] in seen_ids:
                raise RuntimeError("GE validation failed for cleaned dataset.")
            seen_ids.add(row["id"])
            try:
                value = int(row["value"])
            except ValueError as exc:
                logger.debug(f"ValueError: {exc}")
                raise RuntimeError("GE validation failed for cleaned dataset.") from exc
            if not 0 <= value <= 2:
                raise RuntimeError("GE validation failed for cleaned dataset.")
    return True, docs_out


def x__fallback_validate__mutmut_12(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = set()
    with clean_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get("id") or row.get("value"):
                raise RuntimeError("GE validation failed for cleaned dataset.")
            if row["id"] in seen_ids:
                raise RuntimeError("GE validation failed for cleaned dataset.")
            seen_ids.add(row["id"])
            try:
                value = int(row["value"])
            except ValueError as exc:
                logger.debug(f"ValueError: {exc}")
                raise RuntimeError("GE validation failed for cleaned dataset.") from exc
            if not 0 <= value <= 2:
                raise RuntimeError("GE validation failed for cleaned dataset.")
    return True, docs_out


def x__fallback_validate__mutmut_13(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = set()
    with clean_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get("id") or not row.get(None):
                raise RuntimeError("GE validation failed for cleaned dataset.")
            if row["id"] in seen_ids:
                raise RuntimeError("GE validation failed for cleaned dataset.")
            seen_ids.add(row["id"])
            try:
                value = int(row["value"])
            except ValueError as exc:
                logger.debug(f"ValueError: {exc}")
                raise RuntimeError("GE validation failed for cleaned dataset.") from exc
            if not 0 <= value <= 2:
                raise RuntimeError("GE validation failed for cleaned dataset.")
    return True, docs_out


def x__fallback_validate__mutmut_14(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = set()
    with clean_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get("id") or not row.get("XXvalueXX"):
                raise RuntimeError("GE validation failed for cleaned dataset.")
            if row["id"] in seen_ids:
                raise RuntimeError("GE validation failed for cleaned dataset.")
            seen_ids.add(row["id"])
            try:
                value = int(row["value"])
            except ValueError as exc:
                logger.debug(f"ValueError: {exc}")
                raise RuntimeError("GE validation failed for cleaned dataset.") from exc
            if not 0 <= value <= 2:
                raise RuntimeError("GE validation failed for cleaned dataset.")
    return True, docs_out


def x__fallback_validate__mutmut_15(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = set()
    with clean_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get("id") or not row.get("VALUE"):
                raise RuntimeError("GE validation failed for cleaned dataset.")
            if row["id"] in seen_ids:
                raise RuntimeError("GE validation failed for cleaned dataset.")
            seen_ids.add(row["id"])
            try:
                value = int(row["value"])
            except ValueError as exc:
                logger.debug(f"ValueError: {exc}")
                raise RuntimeError("GE validation failed for cleaned dataset.") from exc
            if not 0 <= value <= 2:
                raise RuntimeError("GE validation failed for cleaned dataset.")
    return True, docs_out


def x__fallback_validate__mutmut_16(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = set()
    with clean_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get("id") or not row.get("value"):
                raise RuntimeError(None)
            if row["id"] in seen_ids:
                raise RuntimeError("GE validation failed for cleaned dataset.")
            seen_ids.add(row["id"])
            try:
                value = int(row["value"])
            except ValueError as exc:
                logger.debug(f"ValueError: {exc}")
                raise RuntimeError("GE validation failed for cleaned dataset.") from exc
            if not 0 <= value <= 2:
                raise RuntimeError("GE validation failed for cleaned dataset.")
    return True, docs_out


def x__fallback_validate__mutmut_17(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = set()
    with clean_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get("id") or not row.get("value"):
                raise RuntimeError("XXGE validation failed for cleaned dataset.XX")
            if row["id"] in seen_ids:
                raise RuntimeError("GE validation failed for cleaned dataset.")
            seen_ids.add(row["id"])
            try:
                value = int(row["value"])
            except ValueError as exc:
                logger.debug(f"ValueError: {exc}")
                raise RuntimeError("GE validation failed for cleaned dataset.") from exc
            if not 0 <= value <= 2:
                raise RuntimeError("GE validation failed for cleaned dataset.")
    return True, docs_out


def x__fallback_validate__mutmut_18(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = set()
    with clean_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get("id") or not row.get("value"):
                raise RuntimeError("ge validation failed for cleaned dataset.")
            if row["id"] in seen_ids:
                raise RuntimeError("GE validation failed for cleaned dataset.")
            seen_ids.add(row["id"])
            try:
                value = int(row["value"])
            except ValueError as exc:
                logger.debug(f"ValueError: {exc}")
                raise RuntimeError("GE validation failed for cleaned dataset.") from exc
            if not 0 <= value <= 2:
                raise RuntimeError("GE validation failed for cleaned dataset.")
    return True, docs_out


def x__fallback_validate__mutmut_19(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = set()
    with clean_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get("id") or not row.get("value"):
                raise RuntimeError("GE VALIDATION FAILED FOR CLEANED DATASET.")
            if row["id"] in seen_ids:
                raise RuntimeError("GE validation failed for cleaned dataset.")
            seen_ids.add(row["id"])
            try:
                value = int(row["value"])
            except ValueError as exc:
                logger.debug(f"ValueError: {exc}")
                raise RuntimeError("GE validation failed for cleaned dataset.") from exc
            if not 0 <= value <= 2:
                raise RuntimeError("GE validation failed for cleaned dataset.")
    return True, docs_out


def x__fallback_validate__mutmut_20(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = set()
    with clean_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get("id") or not row.get("value"):
                raise RuntimeError("GE validation failed for cleaned dataset.")
            if row["XXidXX"] in seen_ids:
                raise RuntimeError("GE validation failed for cleaned dataset.")
            seen_ids.add(row["id"])
            try:
                value = int(row["value"])
            except ValueError as exc:
                logger.debug(f"ValueError: {exc}")
                raise RuntimeError("GE validation failed for cleaned dataset.") from exc
            if not 0 <= value <= 2:
                raise RuntimeError("GE validation failed for cleaned dataset.")
    return True, docs_out


def x__fallback_validate__mutmut_21(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = set()
    with clean_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get("id") or not row.get("value"):
                raise RuntimeError("GE validation failed for cleaned dataset.")
            if row["ID"] in seen_ids:
                raise RuntimeError("GE validation failed for cleaned dataset.")
            seen_ids.add(row["id"])
            try:
                value = int(row["value"])
            except ValueError as exc:
                logger.debug(f"ValueError: {exc}")
                raise RuntimeError("GE validation failed for cleaned dataset.") from exc
            if not 0 <= value <= 2:
                raise RuntimeError("GE validation failed for cleaned dataset.")
    return True, docs_out


def x__fallback_validate__mutmut_22(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = set()
    with clean_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get("id") or not row.get("value"):
                raise RuntimeError("GE validation failed for cleaned dataset.")
            if row["id"] not in seen_ids:
                raise RuntimeError("GE validation failed for cleaned dataset.")
            seen_ids.add(row["id"])
            try:
                value = int(row["value"])
            except ValueError as exc:
                logger.debug(f"ValueError: {exc}")
                raise RuntimeError("GE validation failed for cleaned dataset.") from exc
            if not 0 <= value <= 2:
                raise RuntimeError("GE validation failed for cleaned dataset.")
    return True, docs_out


def x__fallback_validate__mutmut_23(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = set()
    with clean_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get("id") or not row.get("value"):
                raise RuntimeError("GE validation failed for cleaned dataset.")
            if row["id"] in seen_ids:
                raise RuntimeError(None)
            seen_ids.add(row["id"])
            try:
                value = int(row["value"])
            except ValueError as exc:
                logger.debug(f"ValueError: {exc}")
                raise RuntimeError("GE validation failed for cleaned dataset.") from exc
            if not 0 <= value <= 2:
                raise RuntimeError("GE validation failed for cleaned dataset.")
    return True, docs_out


def x__fallback_validate__mutmut_24(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = set()
    with clean_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get("id") or not row.get("value"):
                raise RuntimeError("GE validation failed for cleaned dataset.")
            if row["id"] in seen_ids:
                raise RuntimeError("XXGE validation failed for cleaned dataset.XX")
            seen_ids.add(row["id"])
            try:
                value = int(row["value"])
            except ValueError as exc:
                logger.debug(f"ValueError: {exc}")
                raise RuntimeError("GE validation failed for cleaned dataset.") from exc
            if not 0 <= value <= 2:
                raise RuntimeError("GE validation failed for cleaned dataset.")
    return True, docs_out


def x__fallback_validate__mutmut_25(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = set()
    with clean_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get("id") or not row.get("value"):
                raise RuntimeError("GE validation failed for cleaned dataset.")
            if row["id"] in seen_ids:
                raise RuntimeError("ge validation failed for cleaned dataset.")
            seen_ids.add(row["id"])
            try:
                value = int(row["value"])
            except ValueError as exc:
                logger.debug(f"ValueError: {exc}")
                raise RuntimeError("GE validation failed for cleaned dataset.") from exc
            if not 0 <= value <= 2:
                raise RuntimeError("GE validation failed for cleaned dataset.")
    return True, docs_out


def x__fallback_validate__mutmut_26(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = set()
    with clean_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get("id") or not row.get("value"):
                raise RuntimeError("GE validation failed for cleaned dataset.")
            if row["id"] in seen_ids:
                raise RuntimeError("GE VALIDATION FAILED FOR CLEANED DATASET.")
            seen_ids.add(row["id"])
            try:
                value = int(row["value"])
            except ValueError as exc:
                logger.debug(f"ValueError: {exc}")
                raise RuntimeError("GE validation failed for cleaned dataset.") from exc
            if not 0 <= value <= 2:
                raise RuntimeError("GE validation failed for cleaned dataset.")
    return True, docs_out


def x__fallback_validate__mutmut_27(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = set()
    with clean_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get("id") or not row.get("value"):
                raise RuntimeError("GE validation failed for cleaned dataset.")
            if row["id"] in seen_ids:
                raise RuntimeError("GE validation failed for cleaned dataset.")
            seen_ids.add(None)
            try:
                value = int(row["value"])
            except ValueError as exc:
                logger.debug(f"ValueError: {exc}")
                raise RuntimeError("GE validation failed for cleaned dataset.") from exc
            if not 0 <= value <= 2:
                raise RuntimeError("GE validation failed for cleaned dataset.")
    return True, docs_out


def x__fallback_validate__mutmut_28(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = set()
    with clean_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get("id") or not row.get("value"):
                raise RuntimeError("GE validation failed for cleaned dataset.")
            if row["id"] in seen_ids:
                raise RuntimeError("GE validation failed for cleaned dataset.")
            seen_ids.add(row["XXidXX"])
            try:
                value = int(row["value"])
            except ValueError as exc:
                logger.debug(f"ValueError: {exc}")
                raise RuntimeError("GE validation failed for cleaned dataset.") from exc
            if not 0 <= value <= 2:
                raise RuntimeError("GE validation failed for cleaned dataset.")
    return True, docs_out


def x__fallback_validate__mutmut_29(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = set()
    with clean_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get("id") or not row.get("value"):
                raise RuntimeError("GE validation failed for cleaned dataset.")
            if row["id"] in seen_ids:
                raise RuntimeError("GE validation failed for cleaned dataset.")
            seen_ids.add(row["ID"])
            try:
                value = int(row["value"])
            except ValueError as exc:
                logger.debug(f"ValueError: {exc}")
                raise RuntimeError("GE validation failed for cleaned dataset.") from exc
            if not 0 <= value <= 2:
                raise RuntimeError("GE validation failed for cleaned dataset.")
    return True, docs_out


def x__fallback_validate__mutmut_30(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = set()
    with clean_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get("id") or not row.get("value"):
                raise RuntimeError("GE validation failed for cleaned dataset.")
            if row["id"] in seen_ids:
                raise RuntimeError("GE validation failed for cleaned dataset.")
            seen_ids.add(row["id"])
            try:
                value = None
            except ValueError as exc:
                logger.debug(f"ValueError: {exc}")
                raise RuntimeError("GE validation failed for cleaned dataset.") from exc
            if not 0 <= value <= 2:
                raise RuntimeError("GE validation failed for cleaned dataset.")
    return True, docs_out


def x__fallback_validate__mutmut_31(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = set()
    with clean_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get("id") or not row.get("value"):
                raise RuntimeError("GE validation failed for cleaned dataset.")
            if row["id"] in seen_ids:
                raise RuntimeError("GE validation failed for cleaned dataset.")
            seen_ids.add(row["id"])
            try:
                value = int(None)
            except ValueError as exc:
                logger.debug(f"ValueError: {exc}")
                raise RuntimeError("GE validation failed for cleaned dataset.") from exc
            if not 0 <= value <= 2:
                raise RuntimeError("GE validation failed for cleaned dataset.")
    return True, docs_out


def x__fallback_validate__mutmut_32(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = set()
    with clean_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get("id") or not row.get("value"):
                raise RuntimeError("GE validation failed for cleaned dataset.")
            if row["id"] in seen_ids:
                raise RuntimeError("GE validation failed for cleaned dataset.")
            seen_ids.add(row["id"])
            try:
                value = int(row["XXvalueXX"])
            except ValueError as exc:
                logger.debug(f"ValueError: {exc}")
                raise RuntimeError("GE validation failed for cleaned dataset.") from exc
            if not 0 <= value <= 2:
                raise RuntimeError("GE validation failed for cleaned dataset.")
    return True, docs_out


def x__fallback_validate__mutmut_33(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = set()
    with clean_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get("id") or not row.get("value"):
                raise RuntimeError("GE validation failed for cleaned dataset.")
            if row["id"] in seen_ids:
                raise RuntimeError("GE validation failed for cleaned dataset.")
            seen_ids.add(row["id"])
            try:
                value = int(row["VALUE"])
            except ValueError as exc:
                logger.debug(f"ValueError: {exc}")
                raise RuntimeError("GE validation failed for cleaned dataset.") from exc
            if not 0 <= value <= 2:
                raise RuntimeError("GE validation failed for cleaned dataset.")
    return True, docs_out


def x__fallback_validate__mutmut_34(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = set()
    with clean_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get("id") or not row.get("value"):
                raise RuntimeError("GE validation failed for cleaned dataset.")
            if row["id"] in seen_ids:
                raise RuntimeError("GE validation failed for cleaned dataset.")
            seen_ids.add(row["id"])
            try:
                value = int(row["value"])
            except ValueError as exc:
                logger.debug(None)
                raise RuntimeError("GE validation failed for cleaned dataset.") from exc
            if not 0 <= value <= 2:
                raise RuntimeError("GE validation failed for cleaned dataset.")
    return True, docs_out


def x__fallback_validate__mutmut_35(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = set()
    with clean_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get("id") or not row.get("value"):
                raise RuntimeError("GE validation failed for cleaned dataset.")
            if row["id"] in seen_ids:
                raise RuntimeError("GE validation failed for cleaned dataset.")
            seen_ids.add(row["id"])
            try:
                value = int(row["value"])
            except ValueError as exc:
                logger.debug(f"ValueError: {exc}")
                raise RuntimeError(None) from exc
            if not 0 <= value <= 2:
                raise RuntimeError("GE validation failed for cleaned dataset.")
    return True, docs_out


def x__fallback_validate__mutmut_36(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = set()
    with clean_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get("id") or not row.get("value"):
                raise RuntimeError("GE validation failed for cleaned dataset.")
            if row["id"] in seen_ids:
                raise RuntimeError("GE validation failed for cleaned dataset.")
            seen_ids.add(row["id"])
            try:
                value = int(row["value"])
            except ValueError as exc:
                logger.debug(f"ValueError: {exc}")
                raise RuntimeError("XXGE validation failed for cleaned dataset.XX") from exc
            if not 0 <= value <= 2:
                raise RuntimeError("GE validation failed for cleaned dataset.")
    return True, docs_out


def x__fallback_validate__mutmut_37(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = set()
    with clean_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get("id") or not row.get("value"):
                raise RuntimeError("GE validation failed for cleaned dataset.")
            if row["id"] in seen_ids:
                raise RuntimeError("GE validation failed for cleaned dataset.")
            seen_ids.add(row["id"])
            try:
                value = int(row["value"])
            except ValueError as exc:
                logger.debug(f"ValueError: {exc}")
                raise RuntimeError("ge validation failed for cleaned dataset.") from exc
            if not 0 <= value <= 2:
                raise RuntimeError("GE validation failed for cleaned dataset.")
    return True, docs_out


def x__fallback_validate__mutmut_38(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = set()
    with clean_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get("id") or not row.get("value"):
                raise RuntimeError("GE validation failed for cleaned dataset.")
            if row["id"] in seen_ids:
                raise RuntimeError("GE validation failed for cleaned dataset.")
            seen_ids.add(row["id"])
            try:
                value = int(row["value"])
            except ValueError as exc:
                logger.debug(f"ValueError: {exc}")
                raise RuntimeError("GE VALIDATION FAILED FOR CLEANED DATASET.") from exc
            if not 0 <= value <= 2:
                raise RuntimeError("GE validation failed for cleaned dataset.")
    return True, docs_out


def x__fallback_validate__mutmut_39(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = set()
    with clean_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get("id") or not row.get("value"):
                raise RuntimeError("GE validation failed for cleaned dataset.")
            if row["id"] in seen_ids:
                raise RuntimeError("GE validation failed for cleaned dataset.")
            seen_ids.add(row["id"])
            try:
                value = int(row["value"])
            except ValueError as exc:
                logger.debug(f"ValueError: {exc}")
                raise RuntimeError("GE validation failed for cleaned dataset.") from exc
            if 0 <= value <= 2:
                raise RuntimeError("GE validation failed for cleaned dataset.")
    return True, docs_out


def x__fallback_validate__mutmut_40(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = set()
    with clean_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get("id") or not row.get("value"):
                raise RuntimeError("GE validation failed for cleaned dataset.")
            if row["id"] in seen_ids:
                raise RuntimeError("GE validation failed for cleaned dataset.")
            seen_ids.add(row["id"])
            try:
                value = int(row["value"])
            except ValueError as exc:
                logger.debug(f"ValueError: {exc}")
                raise RuntimeError("GE validation failed for cleaned dataset.") from exc
            if not 1 <= value <= 2:
                raise RuntimeError("GE validation failed for cleaned dataset.")
    return True, docs_out


def x__fallback_validate__mutmut_41(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = set()
    with clean_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get("id") or not row.get("value"):
                raise RuntimeError("GE validation failed for cleaned dataset.")
            if row["id"] in seen_ids:
                raise RuntimeError("GE validation failed for cleaned dataset.")
            seen_ids.add(row["id"])
            try:
                value = int(row["value"])
            except ValueError as exc:
                logger.debug(f"ValueError: {exc}")
                raise RuntimeError("GE validation failed for cleaned dataset.") from exc
            if not 0 < value <= 2:
                raise RuntimeError("GE validation failed for cleaned dataset.")
    return True, docs_out


def x__fallback_validate__mutmut_42(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = set()
    with clean_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get("id") or not row.get("value"):
                raise RuntimeError("GE validation failed for cleaned dataset.")
            if row["id"] in seen_ids:
                raise RuntimeError("GE validation failed for cleaned dataset.")
            seen_ids.add(row["id"])
            try:
                value = int(row["value"])
            except ValueError as exc:
                logger.debug(f"ValueError: {exc}")
                raise RuntimeError("GE validation failed for cleaned dataset.") from exc
            if not 0 <= value < 2:
                raise RuntimeError("GE validation failed for cleaned dataset.")
    return True, docs_out


def x__fallback_validate__mutmut_43(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = set()
    with clean_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get("id") or not row.get("value"):
                raise RuntimeError("GE validation failed for cleaned dataset.")
            if row["id"] in seen_ids:
                raise RuntimeError("GE validation failed for cleaned dataset.")
            seen_ids.add(row["id"])
            try:
                value = int(row["value"])
            except ValueError as exc:
                logger.debug(f"ValueError: {exc}")
                raise RuntimeError("GE validation failed for cleaned dataset.") from exc
            if not 0 <= value <= 3:
                raise RuntimeError("GE validation failed for cleaned dataset.")
    return True, docs_out


def x__fallback_validate__mutmut_44(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = set()
    with clean_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get("id") or not row.get("value"):
                raise RuntimeError("GE validation failed for cleaned dataset.")
            if row["id"] in seen_ids:
                raise RuntimeError("GE validation failed for cleaned dataset.")
            seen_ids.add(row["id"])
            try:
                value = int(row["value"])
            except ValueError as exc:
                logger.debug(f"ValueError: {exc}")
                raise RuntimeError("GE validation failed for cleaned dataset.") from exc
            if not 0 <= value <= 2:
                raise RuntimeError(None)
    return True, docs_out


def x__fallback_validate__mutmut_45(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = set()
    with clean_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get("id") or not row.get("value"):
                raise RuntimeError("GE validation failed for cleaned dataset.")
            if row["id"] in seen_ids:
                raise RuntimeError("GE validation failed for cleaned dataset.")
            seen_ids.add(row["id"])
            try:
                value = int(row["value"])
            except ValueError as exc:
                logger.debug(f"ValueError: {exc}")
                raise RuntimeError("GE validation failed for cleaned dataset.") from exc
            if not 0 <= value <= 2:
                raise RuntimeError("XXGE validation failed for cleaned dataset.XX")
    return True, docs_out


def x__fallback_validate__mutmut_46(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = set()
    with clean_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get("id") or not row.get("value"):
                raise RuntimeError("GE validation failed for cleaned dataset.")
            if row["id"] in seen_ids:
                raise RuntimeError("GE validation failed for cleaned dataset.")
            seen_ids.add(row["id"])
            try:
                value = int(row["value"])
            except ValueError as exc:
                logger.debug(f"ValueError: {exc}")
                raise RuntimeError("GE validation failed for cleaned dataset.") from exc
            if not 0 <= value <= 2:
                raise RuntimeError("ge validation failed for cleaned dataset.")
    return True, docs_out


def x__fallback_validate__mutmut_47(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = set()
    with clean_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get("id") or not row.get("value"):
                raise RuntimeError("GE validation failed for cleaned dataset.")
            if row["id"] in seen_ids:
                raise RuntimeError("GE validation failed for cleaned dataset.")
            seen_ids.add(row["id"])
            try:
                value = int(row["value"])
            except ValueError as exc:
                logger.debug(f"ValueError: {exc}")
                raise RuntimeError("GE validation failed for cleaned dataset.") from exc
            if not 0 <= value <= 2:
                raise RuntimeError("GE VALIDATION FAILED FOR CLEANED DATASET.")
    return True, docs_out


def x__fallback_validate__mutmut_48(clean_csv: Path) -> tuple[bool, Path]:
    docs_out = _ensure_docs_out()
    seen_ids = set()
    with clean_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get("id") or not row.get("value"):
                raise RuntimeError("GE validation failed for cleaned dataset.")
            if row["id"] in seen_ids:
                raise RuntimeError("GE validation failed for cleaned dataset.")
            seen_ids.add(row["id"])
            try:
                value = int(row["value"])
            except ValueError as exc:
                logger.debug(f"ValueError: {exc}")
                raise RuntimeError("GE validation failed for cleaned dataset.") from exc
            if not 0 <= value <= 2:
                raise RuntimeError("GE validation failed for cleaned dataset.")
    return False, docs_out

x__fallback_validate__mutmut_mutants : ClassVar[MutantDict] = {
'x__fallback_validate__mutmut_1': x__fallback_validate__mutmut_1, 
    'x__fallback_validate__mutmut_2': x__fallback_validate__mutmut_2, 
    'x__fallback_validate__mutmut_3': x__fallback_validate__mutmut_3, 
    'x__fallback_validate__mutmut_4': x__fallback_validate__mutmut_4, 
    'x__fallback_validate__mutmut_5': x__fallback_validate__mutmut_5, 
    'x__fallback_validate__mutmut_6': x__fallback_validate__mutmut_6, 
    'x__fallback_validate__mutmut_7': x__fallback_validate__mutmut_7, 
    'x__fallback_validate__mutmut_8': x__fallback_validate__mutmut_8, 
    'x__fallback_validate__mutmut_9': x__fallback_validate__mutmut_9, 
    'x__fallback_validate__mutmut_10': x__fallback_validate__mutmut_10, 
    'x__fallback_validate__mutmut_11': x__fallback_validate__mutmut_11, 
    'x__fallback_validate__mutmut_12': x__fallback_validate__mutmut_12, 
    'x__fallback_validate__mutmut_13': x__fallback_validate__mutmut_13, 
    'x__fallback_validate__mutmut_14': x__fallback_validate__mutmut_14, 
    'x__fallback_validate__mutmut_15': x__fallback_validate__mutmut_15, 
    'x__fallback_validate__mutmut_16': x__fallback_validate__mutmut_16, 
    'x__fallback_validate__mutmut_17': x__fallback_validate__mutmut_17, 
    'x__fallback_validate__mutmut_18': x__fallback_validate__mutmut_18, 
    'x__fallback_validate__mutmut_19': x__fallback_validate__mutmut_19, 
    'x__fallback_validate__mutmut_20': x__fallback_validate__mutmut_20, 
    'x__fallback_validate__mutmut_21': x__fallback_validate__mutmut_21, 
    'x__fallback_validate__mutmut_22': x__fallback_validate__mutmut_22, 
    'x__fallback_validate__mutmut_23': x__fallback_validate__mutmut_23, 
    'x__fallback_validate__mutmut_24': x__fallback_validate__mutmut_24, 
    'x__fallback_validate__mutmut_25': x__fallback_validate__mutmut_25, 
    'x__fallback_validate__mutmut_26': x__fallback_validate__mutmut_26, 
    'x__fallback_validate__mutmut_27': x__fallback_validate__mutmut_27, 
    'x__fallback_validate__mutmut_28': x__fallback_validate__mutmut_28, 
    'x__fallback_validate__mutmut_29': x__fallback_validate__mutmut_29, 
    'x__fallback_validate__mutmut_30': x__fallback_validate__mutmut_30, 
    'x__fallback_validate__mutmut_31': x__fallback_validate__mutmut_31, 
    'x__fallback_validate__mutmut_32': x__fallback_validate__mutmut_32, 
    'x__fallback_validate__mutmut_33': x__fallback_validate__mutmut_33, 
    'x__fallback_validate__mutmut_34': x__fallback_validate__mutmut_34, 
    'x__fallback_validate__mutmut_35': x__fallback_validate__mutmut_35, 
    'x__fallback_validate__mutmut_36': x__fallback_validate__mutmut_36, 
    'x__fallback_validate__mutmut_37': x__fallback_validate__mutmut_37, 
    'x__fallback_validate__mutmut_38': x__fallback_validate__mutmut_38, 
    'x__fallback_validate__mutmut_39': x__fallback_validate__mutmut_39, 
    'x__fallback_validate__mutmut_40': x__fallback_validate__mutmut_40, 
    'x__fallback_validate__mutmut_41': x__fallback_validate__mutmut_41, 
    'x__fallback_validate__mutmut_42': x__fallback_validate__mutmut_42, 
    'x__fallback_validate__mutmut_43': x__fallback_validate__mutmut_43, 
    'x__fallback_validate__mutmut_44': x__fallback_validate__mutmut_44, 
    'x__fallback_validate__mutmut_45': x__fallback_validate__mutmut_45, 
    'x__fallback_validate__mutmut_46': x__fallback_validate__mutmut_46, 
    'x__fallback_validate__mutmut_47': x__fallback_validate__mutmut_47, 
    'x__fallback_validate__mutmut_48': x__fallback_validate__mutmut_48
}

def _fallback_validate(*args, **kwargs):
    result = _mutmut_trampoline(x__fallback_validate__mutmut_orig, x__fallback_validate__mutmut_mutants, args, kwargs)
    return result 

_fallback_validate.__signature__ = _mutmut_signature(x__fallback_validate__mutmut_orig)
x__fallback_validate__mutmut_orig.__name__ = 'x__fallback_validate'


def x_run_clean_checkpoint__mutmut_orig(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_1(
    clean_csv: Path, suite_name: str = "XXclean_data_suiteXX"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_2(
    clean_csv: Path, suite_name: str = "CLEAN_DATA_SUITE"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_3(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = None
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_4(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(None)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_5(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_6(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(None)

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_7(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_8(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(None, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_9(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, None):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_10(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr("get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_11(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, ):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_12(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "XXget_contextXX"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_13(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "GET_CONTEXT"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_14(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(None)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_15(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = None
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_16(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = None
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_17(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(None)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_18(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning(None, exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_19(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=None)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_20(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning(exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_21(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", )
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_22(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("XXException occurredXX", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_23(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_24(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("EXCEPTION OCCURRED", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_25(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=False)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_26(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning(None, exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_27(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=None)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_28(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning(exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_29(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", )
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_30(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("XXException occurredXX", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_31(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_32(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("EXCEPTION OCCURRED", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_33(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=False)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_34(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = None

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_35(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(None)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_36(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = None
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_37(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(None)
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_38(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(None))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_39(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = None

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_40(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) != 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_41(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 1:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_42(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null(None)
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_43(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("XXidXX")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_44(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("ID")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_45(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null(None)
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_46(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("XXvalueXX")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_47(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("VALUE")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_48(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique(None)
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_49(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("XXidXX")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_50(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("ID")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_51(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between(None, min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_52(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=None, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_53(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=None)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_54(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between(min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_55(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_56(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, )
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_57(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("XXvalueXX", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_58(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("VALUE", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_59(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=1, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_60(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=3)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_61(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=None)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_62(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=True)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_63(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = None
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_64(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name=None,
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_65(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=None,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_66(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_67(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_68(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="XXclean_checkpointXX",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_69(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="CLEAN_CHECKPOINT",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_70(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = None

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_71(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = None
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_72(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" * "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_73(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") * "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_74(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path(None) / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_75(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("XXgreat_expectationsXX") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_76(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("GREAT_EXPECTATIONS") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_77(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "XXuncommittedXX" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_78(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "UNCOMMITTED" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_79(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "XXdata_docsXX"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_80(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "DATA_DOCS"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_81(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = None
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_82(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(None)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_83(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(None, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_84(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, None)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_85(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_86(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, )

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_87(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = None
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_88(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(None)
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_89(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(None, exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_90(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=None)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_91(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_92(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", )
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_93(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=False)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_94(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = None  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_95(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["XXsuccessXX"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_96(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["SUCCESS"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_97(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                None
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_98(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "XXGreat Expectations checkpoint did not expose a success flag.XX"
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_99(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "great expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_100(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "GREAT EXPECTATIONS CHECKPOINT DID NOT EXPOSE A SUCCESS FLAG."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_101(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = None
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_102(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(None)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_103(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_104(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error(None, clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_105(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", None)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_106(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error(clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_107(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", )
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_108(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("XXGreat Expectations validation FAILED for %sXX", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_109(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("great expectations validation failed for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_110(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("GREAT EXPECTATIONS VALIDATION FAILED FOR %S", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_111(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError(None)
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_112(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("XXGE validation failed for cleaned dataset.XX")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_113(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("ge validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_114(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE VALIDATION FAILED FOR CLEANED DATASET.")
    logger.info("Great Expectations validation SUCCEEDED for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_115(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info(None, clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_116(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", None)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_117(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info(clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_118(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("Great Expectations validation SUCCEEDED for %s", )
    return success, docs_out


def x_run_clean_checkpoint__mutmut_119(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("XXGreat Expectations validation SUCCEEDED for %sXX", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_120(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("great expectations validation succeeded for %s", clean_csv)
    return success, docs_out


def x_run_clean_checkpoint__mutmut_121(
    clean_csv: Path, suite_name: str = "clean_data_suite"
) -> tuple[bool, Path]:
    """
    Execute GE validation for the cleaned dataset CSV. Returns (success, docs_dir).
    Raises RuntimeError on failure.
    """
    clean_csv = Path(clean_csv)
    if not clean_csv.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    if not hasattr(gx, "get_context"):
        return _fallback_validate(clean_csv)

    context = gx.get_context()
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        suite = context.add_or_update_expectation_suite(suite_name)

    validator = context.sources.pandas_default.read_csv(str(clean_csv))
    validator.expectation_suite = suite

    if len(validator.get_expectation_suite(discard_failed_expectations=False).expectations) == 0:
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_not_be_null("value")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_between("value", min_value=0, max_value=2)
        validator.save_expectation_suite(discard_failed_expectations=False)

    checkpoint = context.add_or_update_checkpoint(
        name="clean_checkpoint",
        validator=validator,
    )
    results = checkpoint.run()

    context.build_data_docs()
    uncommitted_docs = Path("great_expectations") / "uncommitted" / "data_docs"
    docs_out = _ensure_docs_out()
    if uncommitted_docs.exists():
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(uncommitted_docs, docs_out)

    try:
        success_flag = results.success
    except AttributeError as e:
        logger.debug(f"AttributeError: {e}")
        logger.warning(f"AttributeError: {e}", exc_info=True)
        try:
            success_flag = results["success"]  # type: ignore[index]
        except (TypeError, KeyError) as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Great Expectations checkpoint did not expose a success flag."
            ) from exc

    success = bool(success_flag)
    if not success:
        logger.error("Great Expectations validation FAILED for %s", clean_csv)
        raise RuntimeError("GE validation failed for cleaned dataset.")
    logger.info("GREAT EXPECTATIONS VALIDATION SUCCEEDED FOR %S", clean_csv)
    return success, docs_out

x_run_clean_checkpoint__mutmut_mutants : ClassVar[MutantDict] = {
'x_run_clean_checkpoint__mutmut_1': x_run_clean_checkpoint__mutmut_1, 
    'x_run_clean_checkpoint__mutmut_2': x_run_clean_checkpoint__mutmut_2, 
    'x_run_clean_checkpoint__mutmut_3': x_run_clean_checkpoint__mutmut_3, 
    'x_run_clean_checkpoint__mutmut_4': x_run_clean_checkpoint__mutmut_4, 
    'x_run_clean_checkpoint__mutmut_5': x_run_clean_checkpoint__mutmut_5, 
    'x_run_clean_checkpoint__mutmut_6': x_run_clean_checkpoint__mutmut_6, 
    'x_run_clean_checkpoint__mutmut_7': x_run_clean_checkpoint__mutmut_7, 
    'x_run_clean_checkpoint__mutmut_8': x_run_clean_checkpoint__mutmut_8, 
    'x_run_clean_checkpoint__mutmut_9': x_run_clean_checkpoint__mutmut_9, 
    'x_run_clean_checkpoint__mutmut_10': x_run_clean_checkpoint__mutmut_10, 
    'x_run_clean_checkpoint__mutmut_11': x_run_clean_checkpoint__mutmut_11, 
    'x_run_clean_checkpoint__mutmut_12': x_run_clean_checkpoint__mutmut_12, 
    'x_run_clean_checkpoint__mutmut_13': x_run_clean_checkpoint__mutmut_13, 
    'x_run_clean_checkpoint__mutmut_14': x_run_clean_checkpoint__mutmut_14, 
    'x_run_clean_checkpoint__mutmut_15': x_run_clean_checkpoint__mutmut_15, 
    'x_run_clean_checkpoint__mutmut_16': x_run_clean_checkpoint__mutmut_16, 
    'x_run_clean_checkpoint__mutmut_17': x_run_clean_checkpoint__mutmut_17, 
    'x_run_clean_checkpoint__mutmut_18': x_run_clean_checkpoint__mutmut_18, 
    'x_run_clean_checkpoint__mutmut_19': x_run_clean_checkpoint__mutmut_19, 
    'x_run_clean_checkpoint__mutmut_20': x_run_clean_checkpoint__mutmut_20, 
    'x_run_clean_checkpoint__mutmut_21': x_run_clean_checkpoint__mutmut_21, 
    'x_run_clean_checkpoint__mutmut_22': x_run_clean_checkpoint__mutmut_22, 
    'x_run_clean_checkpoint__mutmut_23': x_run_clean_checkpoint__mutmut_23, 
    'x_run_clean_checkpoint__mutmut_24': x_run_clean_checkpoint__mutmut_24, 
    'x_run_clean_checkpoint__mutmut_25': x_run_clean_checkpoint__mutmut_25, 
    'x_run_clean_checkpoint__mutmut_26': x_run_clean_checkpoint__mutmut_26, 
    'x_run_clean_checkpoint__mutmut_27': x_run_clean_checkpoint__mutmut_27, 
    'x_run_clean_checkpoint__mutmut_28': x_run_clean_checkpoint__mutmut_28, 
    'x_run_clean_checkpoint__mutmut_29': x_run_clean_checkpoint__mutmut_29, 
    'x_run_clean_checkpoint__mutmut_30': x_run_clean_checkpoint__mutmut_30, 
    'x_run_clean_checkpoint__mutmut_31': x_run_clean_checkpoint__mutmut_31, 
    'x_run_clean_checkpoint__mutmut_32': x_run_clean_checkpoint__mutmut_32, 
    'x_run_clean_checkpoint__mutmut_33': x_run_clean_checkpoint__mutmut_33, 
    'x_run_clean_checkpoint__mutmut_34': x_run_clean_checkpoint__mutmut_34, 
    'x_run_clean_checkpoint__mutmut_35': x_run_clean_checkpoint__mutmut_35, 
    'x_run_clean_checkpoint__mutmut_36': x_run_clean_checkpoint__mutmut_36, 
    'x_run_clean_checkpoint__mutmut_37': x_run_clean_checkpoint__mutmut_37, 
    'x_run_clean_checkpoint__mutmut_38': x_run_clean_checkpoint__mutmut_38, 
    'x_run_clean_checkpoint__mutmut_39': x_run_clean_checkpoint__mutmut_39, 
    'x_run_clean_checkpoint__mutmut_40': x_run_clean_checkpoint__mutmut_40, 
    'x_run_clean_checkpoint__mutmut_41': x_run_clean_checkpoint__mutmut_41, 
    'x_run_clean_checkpoint__mutmut_42': x_run_clean_checkpoint__mutmut_42, 
    'x_run_clean_checkpoint__mutmut_43': x_run_clean_checkpoint__mutmut_43, 
    'x_run_clean_checkpoint__mutmut_44': x_run_clean_checkpoint__mutmut_44, 
    'x_run_clean_checkpoint__mutmut_45': x_run_clean_checkpoint__mutmut_45, 
    'x_run_clean_checkpoint__mutmut_46': x_run_clean_checkpoint__mutmut_46, 
    'x_run_clean_checkpoint__mutmut_47': x_run_clean_checkpoint__mutmut_47, 
    'x_run_clean_checkpoint__mutmut_48': x_run_clean_checkpoint__mutmut_48, 
    'x_run_clean_checkpoint__mutmut_49': x_run_clean_checkpoint__mutmut_49, 
    'x_run_clean_checkpoint__mutmut_50': x_run_clean_checkpoint__mutmut_50, 
    'x_run_clean_checkpoint__mutmut_51': x_run_clean_checkpoint__mutmut_51, 
    'x_run_clean_checkpoint__mutmut_52': x_run_clean_checkpoint__mutmut_52, 
    'x_run_clean_checkpoint__mutmut_53': x_run_clean_checkpoint__mutmut_53, 
    'x_run_clean_checkpoint__mutmut_54': x_run_clean_checkpoint__mutmut_54, 
    'x_run_clean_checkpoint__mutmut_55': x_run_clean_checkpoint__mutmut_55, 
    'x_run_clean_checkpoint__mutmut_56': x_run_clean_checkpoint__mutmut_56, 
    'x_run_clean_checkpoint__mutmut_57': x_run_clean_checkpoint__mutmut_57, 
    'x_run_clean_checkpoint__mutmut_58': x_run_clean_checkpoint__mutmut_58, 
    'x_run_clean_checkpoint__mutmut_59': x_run_clean_checkpoint__mutmut_59, 
    'x_run_clean_checkpoint__mutmut_60': x_run_clean_checkpoint__mutmut_60, 
    'x_run_clean_checkpoint__mutmut_61': x_run_clean_checkpoint__mutmut_61, 
    'x_run_clean_checkpoint__mutmut_62': x_run_clean_checkpoint__mutmut_62, 
    'x_run_clean_checkpoint__mutmut_63': x_run_clean_checkpoint__mutmut_63, 
    'x_run_clean_checkpoint__mutmut_64': x_run_clean_checkpoint__mutmut_64, 
    'x_run_clean_checkpoint__mutmut_65': x_run_clean_checkpoint__mutmut_65, 
    'x_run_clean_checkpoint__mutmut_66': x_run_clean_checkpoint__mutmut_66, 
    'x_run_clean_checkpoint__mutmut_67': x_run_clean_checkpoint__mutmut_67, 
    'x_run_clean_checkpoint__mutmut_68': x_run_clean_checkpoint__mutmut_68, 
    'x_run_clean_checkpoint__mutmut_69': x_run_clean_checkpoint__mutmut_69, 
    'x_run_clean_checkpoint__mutmut_70': x_run_clean_checkpoint__mutmut_70, 
    'x_run_clean_checkpoint__mutmut_71': x_run_clean_checkpoint__mutmut_71, 
    'x_run_clean_checkpoint__mutmut_72': x_run_clean_checkpoint__mutmut_72, 
    'x_run_clean_checkpoint__mutmut_73': x_run_clean_checkpoint__mutmut_73, 
    'x_run_clean_checkpoint__mutmut_74': x_run_clean_checkpoint__mutmut_74, 
    'x_run_clean_checkpoint__mutmut_75': x_run_clean_checkpoint__mutmut_75, 
    'x_run_clean_checkpoint__mutmut_76': x_run_clean_checkpoint__mutmut_76, 
    'x_run_clean_checkpoint__mutmut_77': x_run_clean_checkpoint__mutmut_77, 
    'x_run_clean_checkpoint__mutmut_78': x_run_clean_checkpoint__mutmut_78, 
    'x_run_clean_checkpoint__mutmut_79': x_run_clean_checkpoint__mutmut_79, 
    'x_run_clean_checkpoint__mutmut_80': x_run_clean_checkpoint__mutmut_80, 
    'x_run_clean_checkpoint__mutmut_81': x_run_clean_checkpoint__mutmut_81, 
    'x_run_clean_checkpoint__mutmut_82': x_run_clean_checkpoint__mutmut_82, 
    'x_run_clean_checkpoint__mutmut_83': x_run_clean_checkpoint__mutmut_83, 
    'x_run_clean_checkpoint__mutmut_84': x_run_clean_checkpoint__mutmut_84, 
    'x_run_clean_checkpoint__mutmut_85': x_run_clean_checkpoint__mutmut_85, 
    'x_run_clean_checkpoint__mutmut_86': x_run_clean_checkpoint__mutmut_86, 
    'x_run_clean_checkpoint__mutmut_87': x_run_clean_checkpoint__mutmut_87, 
    'x_run_clean_checkpoint__mutmut_88': x_run_clean_checkpoint__mutmut_88, 
    'x_run_clean_checkpoint__mutmut_89': x_run_clean_checkpoint__mutmut_89, 
    'x_run_clean_checkpoint__mutmut_90': x_run_clean_checkpoint__mutmut_90, 
    'x_run_clean_checkpoint__mutmut_91': x_run_clean_checkpoint__mutmut_91, 
    'x_run_clean_checkpoint__mutmut_92': x_run_clean_checkpoint__mutmut_92, 
    'x_run_clean_checkpoint__mutmut_93': x_run_clean_checkpoint__mutmut_93, 
    'x_run_clean_checkpoint__mutmut_94': x_run_clean_checkpoint__mutmut_94, 
    'x_run_clean_checkpoint__mutmut_95': x_run_clean_checkpoint__mutmut_95, 
    'x_run_clean_checkpoint__mutmut_96': x_run_clean_checkpoint__mutmut_96, 
    'x_run_clean_checkpoint__mutmut_97': x_run_clean_checkpoint__mutmut_97, 
    'x_run_clean_checkpoint__mutmut_98': x_run_clean_checkpoint__mutmut_98, 
    'x_run_clean_checkpoint__mutmut_99': x_run_clean_checkpoint__mutmut_99, 
    'x_run_clean_checkpoint__mutmut_100': x_run_clean_checkpoint__mutmut_100, 
    'x_run_clean_checkpoint__mutmut_101': x_run_clean_checkpoint__mutmut_101, 
    'x_run_clean_checkpoint__mutmut_102': x_run_clean_checkpoint__mutmut_102, 
    'x_run_clean_checkpoint__mutmut_103': x_run_clean_checkpoint__mutmut_103, 
    'x_run_clean_checkpoint__mutmut_104': x_run_clean_checkpoint__mutmut_104, 
    'x_run_clean_checkpoint__mutmut_105': x_run_clean_checkpoint__mutmut_105, 
    'x_run_clean_checkpoint__mutmut_106': x_run_clean_checkpoint__mutmut_106, 
    'x_run_clean_checkpoint__mutmut_107': x_run_clean_checkpoint__mutmut_107, 
    'x_run_clean_checkpoint__mutmut_108': x_run_clean_checkpoint__mutmut_108, 
    'x_run_clean_checkpoint__mutmut_109': x_run_clean_checkpoint__mutmut_109, 
    'x_run_clean_checkpoint__mutmut_110': x_run_clean_checkpoint__mutmut_110, 
    'x_run_clean_checkpoint__mutmut_111': x_run_clean_checkpoint__mutmut_111, 
    'x_run_clean_checkpoint__mutmut_112': x_run_clean_checkpoint__mutmut_112, 
    'x_run_clean_checkpoint__mutmut_113': x_run_clean_checkpoint__mutmut_113, 
    'x_run_clean_checkpoint__mutmut_114': x_run_clean_checkpoint__mutmut_114, 
    'x_run_clean_checkpoint__mutmut_115': x_run_clean_checkpoint__mutmut_115, 
    'x_run_clean_checkpoint__mutmut_116': x_run_clean_checkpoint__mutmut_116, 
    'x_run_clean_checkpoint__mutmut_117': x_run_clean_checkpoint__mutmut_117, 
    'x_run_clean_checkpoint__mutmut_118': x_run_clean_checkpoint__mutmut_118, 
    'x_run_clean_checkpoint__mutmut_119': x_run_clean_checkpoint__mutmut_119, 
    'x_run_clean_checkpoint__mutmut_120': x_run_clean_checkpoint__mutmut_120, 
    'x_run_clean_checkpoint__mutmut_121': x_run_clean_checkpoint__mutmut_121
}

def run_clean_checkpoint(*args, **kwargs):
    result = _mutmut_trampoline(x_run_clean_checkpoint__mutmut_orig, x_run_clean_checkpoint__mutmut_mutants, args, kwargs)
    return result 

run_clean_checkpoint.__signature__ = _mutmut_signature(x_run_clean_checkpoint__mutmut_orig)
x_run_clean_checkpoint__mutmut_orig.__name__ = 'x_run_clean_checkpoint'
