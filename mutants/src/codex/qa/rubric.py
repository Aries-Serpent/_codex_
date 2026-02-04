"""
Rubric Module

This module provides functionality for rubric.

Usage:
    from qa.rubric import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations
import logging
logger = logging.getLogger(__name__)
"""Offline QA rubric handling and score generation utilities."""


import csv
import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field
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


class RubricCriterion(BaseModel):
    """A single evaluation criterion in a QA rubric."""

    id: str
    description: str
    max_score: float


class QARubric(BaseModel):
    """A QA rubric composed of multiple criteria."""

    name: str
    criteria: list[RubricCriterion] = Field(default_factory=list)


def x_load_rubric__mutmut_orig(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == ".csv":
        criteria: list[RubricCriterion] = []
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    RubricCriterion(
                        id=(row.get("id") or "").strip(),
                        description=(row.get("description") or "").strip(),
                        max_score=float(row.get("max_score") or 0),
                    )
                )
        return QARubric(name=path.stem, criteria=criteria)

    data = json.loads(path.read_text(encoding="utf-8"))
    return QARubric(**data)


def x_load_rubric__mutmut_1(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.upper() == ".csv":
        criteria: list[RubricCriterion] = []
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    RubricCriterion(
                        id=(row.get("id") or "").strip(),
                        description=(row.get("description") or "").strip(),
                        max_score=float(row.get("max_score") or 0),
                    )
                )
        return QARubric(name=path.stem, criteria=criteria)

    data = json.loads(path.read_text(encoding="utf-8"))
    return QARubric(**data)


def x_load_rubric__mutmut_2(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() != ".csv":
        criteria: list[RubricCriterion] = []
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    RubricCriterion(
                        id=(row.get("id") or "").strip(),
                        description=(row.get("description") or "").strip(),
                        max_score=float(row.get("max_score") or 0),
                    )
                )
        return QARubric(name=path.stem, criteria=criteria)

    data = json.loads(path.read_text(encoding="utf-8"))
    return QARubric(**data)


def x_load_rubric__mutmut_3(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == "XX.csvXX":
        criteria: list[RubricCriterion] = []
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    RubricCriterion(
                        id=(row.get("id") or "").strip(),
                        description=(row.get("description") or "").strip(),
                        max_score=float(row.get("max_score") or 0),
                    )
                )
        return QARubric(name=path.stem, criteria=criteria)

    data = json.loads(path.read_text(encoding="utf-8"))
    return QARubric(**data)


def x_load_rubric__mutmut_4(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == ".CSV":
        criteria: list[RubricCriterion] = []
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    RubricCriterion(
                        id=(row.get("id") or "").strip(),
                        description=(row.get("description") or "").strip(),
                        max_score=float(row.get("max_score") or 0),
                    )
                )
        return QARubric(name=path.stem, criteria=criteria)

    data = json.loads(path.read_text(encoding="utf-8"))
    return QARubric(**data)


def x_load_rubric__mutmut_5(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == ".csv":
        criteria: list[RubricCriterion] = None
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    RubricCriterion(
                        id=(row.get("id") or "").strip(),
                        description=(row.get("description") or "").strip(),
                        max_score=float(row.get("max_score") or 0),
                    )
                )
        return QARubric(name=path.stem, criteria=criteria)

    data = json.loads(path.read_text(encoding="utf-8"))
    return QARubric(**data)


def x_load_rubric__mutmut_6(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == ".csv":
        criteria: list[RubricCriterion] = []
        with path.open(None, encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    RubricCriterion(
                        id=(row.get("id") or "").strip(),
                        description=(row.get("description") or "").strip(),
                        max_score=float(row.get("max_score") or 0),
                    )
                )
        return QARubric(name=path.stem, criteria=criteria)

    data = json.loads(path.read_text(encoding="utf-8"))
    return QARubric(**data)


def x_load_rubric__mutmut_7(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == ".csv":
        criteria: list[RubricCriterion] = []
        with path.open("r", encoding=None) as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    RubricCriterion(
                        id=(row.get("id") or "").strip(),
                        description=(row.get("description") or "").strip(),
                        max_score=float(row.get("max_score") or 0),
                    )
                )
        return QARubric(name=path.stem, criteria=criteria)

    data = json.loads(path.read_text(encoding="utf-8"))
    return QARubric(**data)


def x_load_rubric__mutmut_8(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == ".csv":
        criteria: list[RubricCriterion] = []
        with path.open(encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    RubricCriterion(
                        id=(row.get("id") or "").strip(),
                        description=(row.get("description") or "").strip(),
                        max_score=float(row.get("max_score") or 0),
                    )
                )
        return QARubric(name=path.stem, criteria=criteria)

    data = json.loads(path.read_text(encoding="utf-8"))
    return QARubric(**data)


def x_load_rubric__mutmut_9(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == ".csv":
        criteria: list[RubricCriterion] = []
        with path.open("r", ) as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    RubricCriterion(
                        id=(row.get("id") or "").strip(),
                        description=(row.get("description") or "").strip(),
                        max_score=float(row.get("max_score") or 0),
                    )
                )
        return QARubric(name=path.stem, criteria=criteria)

    data = json.loads(path.read_text(encoding="utf-8"))
    return QARubric(**data)


def x_load_rubric__mutmut_10(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == ".csv":
        criteria: list[RubricCriterion] = []
        with path.open("XXrXX", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    RubricCriterion(
                        id=(row.get("id") or "").strip(),
                        description=(row.get("description") or "").strip(),
                        max_score=float(row.get("max_score") or 0),
                    )
                )
        return QARubric(name=path.stem, criteria=criteria)

    data = json.loads(path.read_text(encoding="utf-8"))
    return QARubric(**data)


def x_load_rubric__mutmut_11(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == ".csv":
        criteria: list[RubricCriterion] = []
        with path.open("R", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    RubricCriterion(
                        id=(row.get("id") or "").strip(),
                        description=(row.get("description") or "").strip(),
                        max_score=float(row.get("max_score") or 0),
                    )
                )
        return QARubric(name=path.stem, criteria=criteria)

    data = json.loads(path.read_text(encoding="utf-8"))
    return QARubric(**data)


def x_load_rubric__mutmut_12(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == ".csv":
        criteria: list[RubricCriterion] = []
        with path.open("r", encoding="XXutf-8XX") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    RubricCriterion(
                        id=(row.get("id") or "").strip(),
                        description=(row.get("description") or "").strip(),
                        max_score=float(row.get("max_score") or 0),
                    )
                )
        return QARubric(name=path.stem, criteria=criteria)

    data = json.loads(path.read_text(encoding="utf-8"))
    return QARubric(**data)


def x_load_rubric__mutmut_13(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == ".csv":
        criteria: list[RubricCriterion] = []
        with path.open("r", encoding="UTF-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    RubricCriterion(
                        id=(row.get("id") or "").strip(),
                        description=(row.get("description") or "").strip(),
                        max_score=float(row.get("max_score") or 0),
                    )
                )
        return QARubric(name=path.stem, criteria=criteria)

    data = json.loads(path.read_text(encoding="utf-8"))
    return QARubric(**data)


def x_load_rubric__mutmut_14(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == ".csv":
        criteria: list[RubricCriterion] = []
        with path.open("r", encoding="utf-8") as handle:
            reader = None
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    RubricCriterion(
                        id=(row.get("id") or "").strip(),
                        description=(row.get("description") or "").strip(),
                        max_score=float(row.get("max_score") or 0),
                    )
                )
        return QARubric(name=path.stem, criteria=criteria)

    data = json.loads(path.read_text(encoding="utf-8"))
    return QARubric(**data)


def x_load_rubric__mutmut_15(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == ".csv":
        criteria: list[RubricCriterion] = []
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(None)
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    RubricCriterion(
                        id=(row.get("id") or "").strip(),
                        description=(row.get("description") or "").strip(),
                        max_score=float(row.get("max_score") or 0),
                    )
                )
        return QARubric(name=path.stem, criteria=criteria)

    data = json.loads(path.read_text(encoding="utf-8"))
    return QARubric(**data)


def x_load_rubric__mutmut_16(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == ".csv":
        criteria: list[RubricCriterion] = []
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if row:
                    continue
                criteria.append(
                    RubricCriterion(
                        id=(row.get("id") or "").strip(),
                        description=(row.get("description") or "").strip(),
                        max_score=float(row.get("max_score") or 0),
                    )
                )
        return QARubric(name=path.stem, criteria=criteria)

    data = json.loads(path.read_text(encoding="utf-8"))
    return QARubric(**data)


def x_load_rubric__mutmut_17(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == ".csv":
        criteria: list[RubricCriterion] = []
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    break
                criteria.append(
                    RubricCriterion(
                        id=(row.get("id") or "").strip(),
                        description=(row.get("description") or "").strip(),
                        max_score=float(row.get("max_score") or 0),
                    )
                )
        return QARubric(name=path.stem, criteria=criteria)

    data = json.loads(path.read_text(encoding="utf-8"))
    return QARubric(**data)


def x_load_rubric__mutmut_18(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == ".csv":
        criteria: list[RubricCriterion] = []
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    None
                )
        return QARubric(name=path.stem, criteria=criteria)

    data = json.loads(path.read_text(encoding="utf-8"))
    return QARubric(**data)


def x_load_rubric__mutmut_19(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == ".csv":
        criteria: list[RubricCriterion] = []
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    RubricCriterion(
                        id=None,
                        description=(row.get("description") or "").strip(),
                        max_score=float(row.get("max_score") or 0),
                    )
                )
        return QARubric(name=path.stem, criteria=criteria)

    data = json.loads(path.read_text(encoding="utf-8"))
    return QARubric(**data)


def x_load_rubric__mutmut_20(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == ".csv":
        criteria: list[RubricCriterion] = []
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    RubricCriterion(
                        id=(row.get("id") or "").strip(),
                        description=None,
                        max_score=float(row.get("max_score") or 0),
                    )
                )
        return QARubric(name=path.stem, criteria=criteria)

    data = json.loads(path.read_text(encoding="utf-8"))
    return QARubric(**data)


def x_load_rubric__mutmut_21(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == ".csv":
        criteria: list[RubricCriterion] = []
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    RubricCriterion(
                        id=(row.get("id") or "").strip(),
                        description=(row.get("description") or "").strip(),
                        max_score=None,
                    )
                )
        return QARubric(name=path.stem, criteria=criteria)

    data = json.loads(path.read_text(encoding="utf-8"))
    return QARubric(**data)


def x_load_rubric__mutmut_22(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == ".csv":
        criteria: list[RubricCriterion] = []
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    RubricCriterion(
                        description=(row.get("description") or "").strip(),
                        max_score=float(row.get("max_score") or 0),
                    )
                )
        return QARubric(name=path.stem, criteria=criteria)

    data = json.loads(path.read_text(encoding="utf-8"))
    return QARubric(**data)


def x_load_rubric__mutmut_23(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == ".csv":
        criteria: list[RubricCriterion] = []
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    RubricCriterion(
                        id=(row.get("id") or "").strip(),
                        max_score=float(row.get("max_score") or 0),
                    )
                )
        return QARubric(name=path.stem, criteria=criteria)

    data = json.loads(path.read_text(encoding="utf-8"))
    return QARubric(**data)


def x_load_rubric__mutmut_24(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == ".csv":
        criteria: list[RubricCriterion] = []
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    RubricCriterion(
                        id=(row.get("id") or "").strip(),
                        description=(row.get("description") or "").strip(),
                        )
                )
        return QARubric(name=path.stem, criteria=criteria)

    data = json.loads(path.read_text(encoding="utf-8"))
    return QARubric(**data)


def x_load_rubric__mutmut_25(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == ".csv":
        criteria: list[RubricCriterion] = []
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    RubricCriterion(
                        id=(row.get("id") and "").strip(),
                        description=(row.get("description") or "").strip(),
                        max_score=float(row.get("max_score") or 0),
                    )
                )
        return QARubric(name=path.stem, criteria=criteria)

    data = json.loads(path.read_text(encoding="utf-8"))
    return QARubric(**data)


def x_load_rubric__mutmut_26(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == ".csv":
        criteria: list[RubricCriterion] = []
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    RubricCriterion(
                        id=(row.get(None) or "").strip(),
                        description=(row.get("description") or "").strip(),
                        max_score=float(row.get("max_score") or 0),
                    )
                )
        return QARubric(name=path.stem, criteria=criteria)

    data = json.loads(path.read_text(encoding="utf-8"))
    return QARubric(**data)


def x_load_rubric__mutmut_27(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == ".csv":
        criteria: list[RubricCriterion] = []
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    RubricCriterion(
                        id=(row.get("XXidXX") or "").strip(),
                        description=(row.get("description") or "").strip(),
                        max_score=float(row.get("max_score") or 0),
                    )
                )
        return QARubric(name=path.stem, criteria=criteria)

    data = json.loads(path.read_text(encoding="utf-8"))
    return QARubric(**data)


def x_load_rubric__mutmut_28(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == ".csv":
        criteria: list[RubricCriterion] = []
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    RubricCriterion(
                        id=(row.get("ID") or "").strip(),
                        description=(row.get("description") or "").strip(),
                        max_score=float(row.get("max_score") or 0),
                    )
                )
        return QARubric(name=path.stem, criteria=criteria)

    data = json.loads(path.read_text(encoding="utf-8"))
    return QARubric(**data)


def x_load_rubric__mutmut_29(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == ".csv":
        criteria: list[RubricCriterion] = []
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    RubricCriterion(
                        id=(row.get("id") or "XXXX").strip(),
                        description=(row.get("description") or "").strip(),
                        max_score=float(row.get("max_score") or 0),
                    )
                )
        return QARubric(name=path.stem, criteria=criteria)

    data = json.loads(path.read_text(encoding="utf-8"))
    return QARubric(**data)


def x_load_rubric__mutmut_30(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == ".csv":
        criteria: list[RubricCriterion] = []
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    RubricCriterion(
                        id=(row.get("id") or "").strip(),
                        description=(row.get("description") and "").strip(),
                        max_score=float(row.get("max_score") or 0),
                    )
                )
        return QARubric(name=path.stem, criteria=criteria)

    data = json.loads(path.read_text(encoding="utf-8"))
    return QARubric(**data)


def x_load_rubric__mutmut_31(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == ".csv":
        criteria: list[RubricCriterion] = []
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    RubricCriterion(
                        id=(row.get("id") or "").strip(),
                        description=(row.get(None) or "").strip(),
                        max_score=float(row.get("max_score") or 0),
                    )
                )
        return QARubric(name=path.stem, criteria=criteria)

    data = json.loads(path.read_text(encoding="utf-8"))
    return QARubric(**data)


def x_load_rubric__mutmut_32(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == ".csv":
        criteria: list[RubricCriterion] = []
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    RubricCriterion(
                        id=(row.get("id") or "").strip(),
                        description=(row.get("XXdescriptionXX") or "").strip(),
                        max_score=float(row.get("max_score") or 0),
                    )
                )
        return QARubric(name=path.stem, criteria=criteria)

    data = json.loads(path.read_text(encoding="utf-8"))
    return QARubric(**data)


def x_load_rubric__mutmut_33(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == ".csv":
        criteria: list[RubricCriterion] = []
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    RubricCriterion(
                        id=(row.get("id") or "").strip(),
                        description=(row.get("DESCRIPTION") or "").strip(),
                        max_score=float(row.get("max_score") or 0),
                    )
                )
        return QARubric(name=path.stem, criteria=criteria)

    data = json.loads(path.read_text(encoding="utf-8"))
    return QARubric(**data)


def x_load_rubric__mutmut_34(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == ".csv":
        criteria: list[RubricCriterion] = []
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    RubricCriterion(
                        id=(row.get("id") or "").strip(),
                        description=(row.get("description") or "XXXX").strip(),
                        max_score=float(row.get("max_score") or 0),
                    )
                )
        return QARubric(name=path.stem, criteria=criteria)

    data = json.loads(path.read_text(encoding="utf-8"))
    return QARubric(**data)


def x_load_rubric__mutmut_35(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == ".csv":
        criteria: list[RubricCriterion] = []
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    RubricCriterion(
                        id=(row.get("id") or "").strip(),
                        description=(row.get("description") or "").strip(),
                        max_score=float(None),
                    )
                )
        return QARubric(name=path.stem, criteria=criteria)

    data = json.loads(path.read_text(encoding="utf-8"))
    return QARubric(**data)


def x_load_rubric__mutmut_36(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == ".csv":
        criteria: list[RubricCriterion] = []
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    RubricCriterion(
                        id=(row.get("id") or "").strip(),
                        description=(row.get("description") or "").strip(),
                        max_score=float(row.get("max_score") and 0),
                    )
                )
        return QARubric(name=path.stem, criteria=criteria)

    data = json.loads(path.read_text(encoding="utf-8"))
    return QARubric(**data)


def x_load_rubric__mutmut_37(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == ".csv":
        criteria: list[RubricCriterion] = []
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    RubricCriterion(
                        id=(row.get("id") or "").strip(),
                        description=(row.get("description") or "").strip(),
                        max_score=float(row.get(None) or 0),
                    )
                )
        return QARubric(name=path.stem, criteria=criteria)

    data = json.loads(path.read_text(encoding="utf-8"))
    return QARubric(**data)


def x_load_rubric__mutmut_38(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == ".csv":
        criteria: list[RubricCriterion] = []
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    RubricCriterion(
                        id=(row.get("id") or "").strip(),
                        description=(row.get("description") or "").strip(),
                        max_score=float(row.get("XXmax_scoreXX") or 0),
                    )
                )
        return QARubric(name=path.stem, criteria=criteria)

    data = json.loads(path.read_text(encoding="utf-8"))
    return QARubric(**data)


def x_load_rubric__mutmut_39(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == ".csv":
        criteria: list[RubricCriterion] = []
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    RubricCriterion(
                        id=(row.get("id") or "").strip(),
                        description=(row.get("description") or "").strip(),
                        max_score=float(row.get("MAX_SCORE") or 0),
                    )
                )
        return QARubric(name=path.stem, criteria=criteria)

    data = json.loads(path.read_text(encoding="utf-8"))
    return QARubric(**data)


def x_load_rubric__mutmut_40(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == ".csv":
        criteria: list[RubricCriterion] = []
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    RubricCriterion(
                        id=(row.get("id") or "").strip(),
                        description=(row.get("description") or "").strip(),
                        max_score=float(row.get("max_score") or 1),
                    )
                )
        return QARubric(name=path.stem, criteria=criteria)

    data = json.loads(path.read_text(encoding="utf-8"))
    return QARubric(**data)


def x_load_rubric__mutmut_41(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == ".csv":
        criteria: list[RubricCriterion] = []
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    RubricCriterion(
                        id=(row.get("id") or "").strip(),
                        description=(row.get("description") or "").strip(),
                        max_score=float(row.get("max_score") or 0),
                    )
                )
        return QARubric(name=None, criteria=criteria)

    data = json.loads(path.read_text(encoding="utf-8"))
    return QARubric(**data)


def x_load_rubric__mutmut_42(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == ".csv":
        criteria: list[RubricCriterion] = []
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    RubricCriterion(
                        id=(row.get("id") or "").strip(),
                        description=(row.get("description") or "").strip(),
                        max_score=float(row.get("max_score") or 0),
                    )
                )
        return QARubric(name=path.stem, criteria=None)

    data = json.loads(path.read_text(encoding="utf-8"))
    return QARubric(**data)


def x_load_rubric__mutmut_43(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == ".csv":
        criteria: list[RubricCriterion] = []
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    RubricCriterion(
                        id=(row.get("id") or "").strip(),
                        description=(row.get("description") or "").strip(),
                        max_score=float(row.get("max_score") or 0),
                    )
                )
        return QARubric(criteria=criteria)

    data = json.loads(path.read_text(encoding="utf-8"))
    return QARubric(**data)


def x_load_rubric__mutmut_44(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == ".csv":
        criteria: list[RubricCriterion] = []
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    RubricCriterion(
                        id=(row.get("id") or "").strip(),
                        description=(row.get("description") or "").strip(),
                        max_score=float(row.get("max_score") or 0),
                    )
                )
        return QARubric(name=path.stem, )

    data = json.loads(path.read_text(encoding="utf-8"))
    return QARubric(**data)


def x_load_rubric__mutmut_45(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == ".csv":
        criteria: list[RubricCriterion] = []
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    RubricCriterion(
                        id=(row.get("id") or "").strip(),
                        description=(row.get("description") or "").strip(),
                        max_score=float(row.get("max_score") or 0),
                    )
                )
        return QARubric(name=path.stem, criteria=criteria)

    data = None
    return QARubric(**data)


def x_load_rubric__mutmut_46(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == ".csv":
        criteria: list[RubricCriterion] = []
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    RubricCriterion(
                        id=(row.get("id") or "").strip(),
                        description=(row.get("description") or "").strip(),
                        max_score=float(row.get("max_score") or 0),
                    )
                )
        return QARubric(name=path.stem, criteria=criteria)

    data = json.loads(None)
    return QARubric(**data)


def x_load_rubric__mutmut_47(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == ".csv":
        criteria: list[RubricCriterion] = []
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    RubricCriterion(
                        id=(row.get("id") or "").strip(),
                        description=(row.get("description") or "").strip(),
                        max_score=float(row.get("max_score") or 0),
                    )
                )
        return QARubric(name=path.stem, criteria=criteria)

    data = json.loads(path.read_text(encoding=None))
    return QARubric(**data)


def x_load_rubric__mutmut_48(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == ".csv":
        criteria: list[RubricCriterion] = []
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    RubricCriterion(
                        id=(row.get("id") or "").strip(),
                        description=(row.get("description") or "").strip(),
                        max_score=float(row.get("max_score") or 0),
                    )
                )
        return QARubric(name=path.stem, criteria=criteria)

    data = json.loads(path.read_text(encoding="XXutf-8XX"))
    return QARubric(**data)


def x_load_rubric__mutmut_49(path: Path) -> QARubric:
    """
    Load a QA rubric definition from a file.
    Supports CSV (with headers: id, description, max_score) or JSON format.
    """

    if path.suffix.lower() == ".csv":
        criteria: list[RubricCriterion] = []
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    continue
                criteria.append(
                    RubricCriterion(
                        id=(row.get("id") or "").strip(),
                        description=(row.get("description") or "").strip(),
                        max_score=float(row.get("max_score") or 0),
                    )
                )
        return QARubric(name=path.stem, criteria=criteria)

    data = json.loads(path.read_text(encoding="UTF-8"))
    return QARubric(**data)

x_load_rubric__mutmut_mutants : ClassVar[MutantDict] = {
'x_load_rubric__mutmut_1': x_load_rubric__mutmut_1, 
    'x_load_rubric__mutmut_2': x_load_rubric__mutmut_2, 
    'x_load_rubric__mutmut_3': x_load_rubric__mutmut_3, 
    'x_load_rubric__mutmut_4': x_load_rubric__mutmut_4, 
    'x_load_rubric__mutmut_5': x_load_rubric__mutmut_5, 
    'x_load_rubric__mutmut_6': x_load_rubric__mutmut_6, 
    'x_load_rubric__mutmut_7': x_load_rubric__mutmut_7, 
    'x_load_rubric__mutmut_8': x_load_rubric__mutmut_8, 
    'x_load_rubric__mutmut_9': x_load_rubric__mutmut_9, 
    'x_load_rubric__mutmut_10': x_load_rubric__mutmut_10, 
    'x_load_rubric__mutmut_11': x_load_rubric__mutmut_11, 
    'x_load_rubric__mutmut_12': x_load_rubric__mutmut_12, 
    'x_load_rubric__mutmut_13': x_load_rubric__mutmut_13, 
    'x_load_rubric__mutmut_14': x_load_rubric__mutmut_14, 
    'x_load_rubric__mutmut_15': x_load_rubric__mutmut_15, 
    'x_load_rubric__mutmut_16': x_load_rubric__mutmut_16, 
    'x_load_rubric__mutmut_17': x_load_rubric__mutmut_17, 
    'x_load_rubric__mutmut_18': x_load_rubric__mutmut_18, 
    'x_load_rubric__mutmut_19': x_load_rubric__mutmut_19, 
    'x_load_rubric__mutmut_20': x_load_rubric__mutmut_20, 
    'x_load_rubric__mutmut_21': x_load_rubric__mutmut_21, 
    'x_load_rubric__mutmut_22': x_load_rubric__mutmut_22, 
    'x_load_rubric__mutmut_23': x_load_rubric__mutmut_23, 
    'x_load_rubric__mutmut_24': x_load_rubric__mutmut_24, 
    'x_load_rubric__mutmut_25': x_load_rubric__mutmut_25, 
    'x_load_rubric__mutmut_26': x_load_rubric__mutmut_26, 
    'x_load_rubric__mutmut_27': x_load_rubric__mutmut_27, 
    'x_load_rubric__mutmut_28': x_load_rubric__mutmut_28, 
    'x_load_rubric__mutmut_29': x_load_rubric__mutmut_29, 
    'x_load_rubric__mutmut_30': x_load_rubric__mutmut_30, 
    'x_load_rubric__mutmut_31': x_load_rubric__mutmut_31, 
    'x_load_rubric__mutmut_32': x_load_rubric__mutmut_32, 
    'x_load_rubric__mutmut_33': x_load_rubric__mutmut_33, 
    'x_load_rubric__mutmut_34': x_load_rubric__mutmut_34, 
    'x_load_rubric__mutmut_35': x_load_rubric__mutmut_35, 
    'x_load_rubric__mutmut_36': x_load_rubric__mutmut_36, 
    'x_load_rubric__mutmut_37': x_load_rubric__mutmut_37, 
    'x_load_rubric__mutmut_38': x_load_rubric__mutmut_38, 
    'x_load_rubric__mutmut_39': x_load_rubric__mutmut_39, 
    'x_load_rubric__mutmut_40': x_load_rubric__mutmut_40, 
    'x_load_rubric__mutmut_41': x_load_rubric__mutmut_41, 
    'x_load_rubric__mutmut_42': x_load_rubric__mutmut_42, 
    'x_load_rubric__mutmut_43': x_load_rubric__mutmut_43, 
    'x_load_rubric__mutmut_44': x_load_rubric__mutmut_44, 
    'x_load_rubric__mutmut_45': x_load_rubric__mutmut_45, 
    'x_load_rubric__mutmut_46': x_load_rubric__mutmut_46, 
    'x_load_rubric__mutmut_47': x_load_rubric__mutmut_47, 
    'x_load_rubric__mutmut_48': x_load_rubric__mutmut_48, 
    'x_load_rubric__mutmut_49': x_load_rubric__mutmut_49
}

def load_rubric(*args, **kwargs):
    result = _mutmut_trampoline(x_load_rubric__mutmut_orig, x_load_rubric__mutmut_mutants, args, kwargs)
    return result 

load_rubric.__signature__ = _mutmut_signature(x_load_rubric__mutmut_orig)
x_load_rubric__mutmut_orig.__name__ = 'x_load_rubric'


def x_generate_scores__mutmut_orig(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_1(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open(None, encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_2(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding=None) as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_3(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open(encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_4(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", ) as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_5(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("XXrXX", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_6(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("R", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_7(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="XXutf-8XX") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_8(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="UTF-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_9(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open(None, encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_10(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding=None) as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_11(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open(encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_12(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", ) as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_13(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("XXwXX", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_14(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("W", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_15(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="XXutf-8XX") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_16(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="UTF-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_17(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = None
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_18(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(None)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_19(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_20(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                break
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_21(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = None
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_22(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") and ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_23(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") and row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_24(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get(None) or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_25(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("XXidXX") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_26(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("ID") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_27(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get(None) or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_28(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("XXrecord_idXX") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_29(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("RECORD_ID") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_30(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or "XXXX"
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_31(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = None
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_32(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = None
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_33(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 1.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_34(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = None
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_35(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(None)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_36(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_37(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(None) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_38(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_39(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "XXXX") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_40(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(None)
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_41(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(None, exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_42(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=None)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_43(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_44(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", )
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_45(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=False)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_46(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = ""
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_47(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = None
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_48(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_49(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score = value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_50(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score -= value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_51(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = None
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_52(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"XXidXX": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_53(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"ID": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_54(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "XXscoresXX": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_55(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "SCORES": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_56(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "XXtotal_scoreXX": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_57(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "TOTAL_SCORE": total_score}
            fout.write(json.dumps(payload) + "\n")


def x_generate_scores__mutmut_58(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(None)


def x_generate_scores__mutmut_59(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) - "\n")


def x_generate_scores__mutmut_60(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(None) + "\n")


def x_generate_scores__mutmut_61(input_path: Path, rubric: QARubric, output_path: Path) -> None:
    """
    Generate a JSONL file with scores per record based on the provided rubric.
    Expects input CSV with an 'id' column and one column per rubric criterion
    (using the criterion identifier as the header).
    """

    with (
        input_path.open("r", encoding="utf-8") as fin,
        output_path.open("w", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        for row in reader:
            if not row:
                continue
            record_id = row.get("id") or row.get("record_id") or ""
            scores: dict[str, Any] = {}
            total_score = 0.0
            for criterion in rubric.criteria:
                raw_value = row.get(criterion.id)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else None
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
                    value = None
                scores[criterion.id] = value
                if value is not None:
                    total_score += value
            payload = {"id": record_id, "scores": scores, "total_score": total_score}
            fout.write(json.dumps(payload) + "XX\nXX")

x_generate_scores__mutmut_mutants : ClassVar[MutantDict] = {
'x_generate_scores__mutmut_1': x_generate_scores__mutmut_1, 
    'x_generate_scores__mutmut_2': x_generate_scores__mutmut_2, 
    'x_generate_scores__mutmut_3': x_generate_scores__mutmut_3, 
    'x_generate_scores__mutmut_4': x_generate_scores__mutmut_4, 
    'x_generate_scores__mutmut_5': x_generate_scores__mutmut_5, 
    'x_generate_scores__mutmut_6': x_generate_scores__mutmut_6, 
    'x_generate_scores__mutmut_7': x_generate_scores__mutmut_7, 
    'x_generate_scores__mutmut_8': x_generate_scores__mutmut_8, 
    'x_generate_scores__mutmut_9': x_generate_scores__mutmut_9, 
    'x_generate_scores__mutmut_10': x_generate_scores__mutmut_10, 
    'x_generate_scores__mutmut_11': x_generate_scores__mutmut_11, 
    'x_generate_scores__mutmut_12': x_generate_scores__mutmut_12, 
    'x_generate_scores__mutmut_13': x_generate_scores__mutmut_13, 
    'x_generate_scores__mutmut_14': x_generate_scores__mutmut_14, 
    'x_generate_scores__mutmut_15': x_generate_scores__mutmut_15, 
    'x_generate_scores__mutmut_16': x_generate_scores__mutmut_16, 
    'x_generate_scores__mutmut_17': x_generate_scores__mutmut_17, 
    'x_generate_scores__mutmut_18': x_generate_scores__mutmut_18, 
    'x_generate_scores__mutmut_19': x_generate_scores__mutmut_19, 
    'x_generate_scores__mutmut_20': x_generate_scores__mutmut_20, 
    'x_generate_scores__mutmut_21': x_generate_scores__mutmut_21, 
    'x_generate_scores__mutmut_22': x_generate_scores__mutmut_22, 
    'x_generate_scores__mutmut_23': x_generate_scores__mutmut_23, 
    'x_generate_scores__mutmut_24': x_generate_scores__mutmut_24, 
    'x_generate_scores__mutmut_25': x_generate_scores__mutmut_25, 
    'x_generate_scores__mutmut_26': x_generate_scores__mutmut_26, 
    'x_generate_scores__mutmut_27': x_generate_scores__mutmut_27, 
    'x_generate_scores__mutmut_28': x_generate_scores__mutmut_28, 
    'x_generate_scores__mutmut_29': x_generate_scores__mutmut_29, 
    'x_generate_scores__mutmut_30': x_generate_scores__mutmut_30, 
    'x_generate_scores__mutmut_31': x_generate_scores__mutmut_31, 
    'x_generate_scores__mutmut_32': x_generate_scores__mutmut_32, 
    'x_generate_scores__mutmut_33': x_generate_scores__mutmut_33, 
    'x_generate_scores__mutmut_34': x_generate_scores__mutmut_34, 
    'x_generate_scores__mutmut_35': x_generate_scores__mutmut_35, 
    'x_generate_scores__mutmut_36': x_generate_scores__mutmut_36, 
    'x_generate_scores__mutmut_37': x_generate_scores__mutmut_37, 
    'x_generate_scores__mutmut_38': x_generate_scores__mutmut_38, 
    'x_generate_scores__mutmut_39': x_generate_scores__mutmut_39, 
    'x_generate_scores__mutmut_40': x_generate_scores__mutmut_40, 
    'x_generate_scores__mutmut_41': x_generate_scores__mutmut_41, 
    'x_generate_scores__mutmut_42': x_generate_scores__mutmut_42, 
    'x_generate_scores__mutmut_43': x_generate_scores__mutmut_43, 
    'x_generate_scores__mutmut_44': x_generate_scores__mutmut_44, 
    'x_generate_scores__mutmut_45': x_generate_scores__mutmut_45, 
    'x_generate_scores__mutmut_46': x_generate_scores__mutmut_46, 
    'x_generate_scores__mutmut_47': x_generate_scores__mutmut_47, 
    'x_generate_scores__mutmut_48': x_generate_scores__mutmut_48, 
    'x_generate_scores__mutmut_49': x_generate_scores__mutmut_49, 
    'x_generate_scores__mutmut_50': x_generate_scores__mutmut_50, 
    'x_generate_scores__mutmut_51': x_generate_scores__mutmut_51, 
    'x_generate_scores__mutmut_52': x_generate_scores__mutmut_52, 
    'x_generate_scores__mutmut_53': x_generate_scores__mutmut_53, 
    'x_generate_scores__mutmut_54': x_generate_scores__mutmut_54, 
    'x_generate_scores__mutmut_55': x_generate_scores__mutmut_55, 
    'x_generate_scores__mutmut_56': x_generate_scores__mutmut_56, 
    'x_generate_scores__mutmut_57': x_generate_scores__mutmut_57, 
    'x_generate_scores__mutmut_58': x_generate_scores__mutmut_58, 
    'x_generate_scores__mutmut_59': x_generate_scores__mutmut_59, 
    'x_generate_scores__mutmut_60': x_generate_scores__mutmut_60, 
    'x_generate_scores__mutmut_61': x_generate_scores__mutmut_61
}

def generate_scores(*args, **kwargs):
    result = _mutmut_trampoline(x_generate_scores__mutmut_orig, x_generate_scores__mutmut_mutants, args, kwargs)
    return result 

generate_scores.__signature__ = _mutmut_signature(x_generate_scores__mutmut_orig)
x_generate_scores__mutmut_orig.__name__ = 'x_generate_scores'
