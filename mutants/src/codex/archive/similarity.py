"""
Similarity Module

This module provides functionality for similarity.

Usage:
    from archive.similarity import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations
import logging
logger = logging.getLogger(__name__)
"""Similarity utilities for consolidation heuristics."""


import ast
import hashlib
from dataclasses import dataclass
from pathlib import Path

_SPLIT = set(" \t\r\n,.;:()[]{}<>+-=*/\\|!@#$%^&~`'\"")
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


def x__tokens__mutmut_orig(text: str) -> list[str]:
    tokens: list[str] = []
    current: list[str] = []
    for ch in text:
        if ch in _SPLIT:
            if current:
                tokens.append("".join(current))
                current.clear()
        else:
            current.append(ch)
    if current:
        tokens.append("".join(current))
    return tokens


def x__tokens__mutmut_1(text: str) -> list[str]:
    tokens: list[str] = None
    current: list[str] = []
    for ch in text:
        if ch in _SPLIT:
            if current:
                tokens.append("".join(current))
                current.clear()
        else:
            current.append(ch)
    if current:
        tokens.append("".join(current))
    return tokens


def x__tokens__mutmut_2(text: str) -> list[str]:
    tokens: list[str] = []
    current: list[str] = None
    for ch in text:
        if ch in _SPLIT:
            if current:
                tokens.append("".join(current))
                current.clear()
        else:
            current.append(ch)
    if current:
        tokens.append("".join(current))
    return tokens


def x__tokens__mutmut_3(text: str) -> list[str]:
    tokens: list[str] = []
    current: list[str] = []
    for ch in text:
        if ch not in _SPLIT:
            if current:
                tokens.append("".join(current))
                current.clear()
        else:
            current.append(ch)
    if current:
        tokens.append("".join(current))
    return tokens


def x__tokens__mutmut_4(text: str) -> list[str]:
    tokens: list[str] = []
    current: list[str] = []
    for ch in text:
        if ch in _SPLIT:
            if current:
                tokens.append(None)
                current.clear()
        else:
            current.append(ch)
    if current:
        tokens.append("".join(current))
    return tokens


def x__tokens__mutmut_5(text: str) -> list[str]:
    tokens: list[str] = []
    current: list[str] = []
    for ch in text:
        if ch in _SPLIT:
            if current:
                tokens.append("".join(None))
                current.clear()
        else:
            current.append(ch)
    if current:
        tokens.append("".join(current))
    return tokens


def x__tokens__mutmut_6(text: str) -> list[str]:
    tokens: list[str] = []
    current: list[str] = []
    for ch in text:
        if ch in _SPLIT:
            if current:
                tokens.append("XXXX".join(current))
                current.clear()
        else:
            current.append(ch)
    if current:
        tokens.append("".join(current))
    return tokens


def x__tokens__mutmut_7(text: str) -> list[str]:
    tokens: list[str] = []
    current: list[str] = []
    for ch in text:
        if ch in _SPLIT:
            if current:
                tokens.append("".join(current))
                current.clear()
        else:
            current.append(None)
    if current:
        tokens.append("".join(current))
    return tokens


def x__tokens__mutmut_8(text: str) -> list[str]:
    tokens: list[str] = []
    current: list[str] = []
    for ch in text:
        if ch in _SPLIT:
            if current:
                tokens.append("".join(current))
                current.clear()
        else:
            current.append(ch)
    if current:
        tokens.append(None)
    return tokens


def x__tokens__mutmut_9(text: str) -> list[str]:
    tokens: list[str] = []
    current: list[str] = []
    for ch in text:
        if ch in _SPLIT:
            if current:
                tokens.append("".join(current))
                current.clear()
        else:
            current.append(ch)
    if current:
        tokens.append("".join(None))
    return tokens


def x__tokens__mutmut_10(text: str) -> list[str]:
    tokens: list[str] = []
    current: list[str] = []
    for ch in text:
        if ch in _SPLIT:
            if current:
                tokens.append("".join(current))
                current.clear()
        else:
            current.append(ch)
    if current:
        tokens.append("XXXX".join(current))
    return tokens

x__tokens__mutmut_mutants : ClassVar[MutantDict] = {
'x__tokens__mutmut_1': x__tokens__mutmut_1, 
    'x__tokens__mutmut_2': x__tokens__mutmut_2, 
    'x__tokens__mutmut_3': x__tokens__mutmut_3, 
    'x__tokens__mutmut_4': x__tokens__mutmut_4, 
    'x__tokens__mutmut_5': x__tokens__mutmut_5, 
    'x__tokens__mutmut_6': x__tokens__mutmut_6, 
    'x__tokens__mutmut_7': x__tokens__mutmut_7, 
    'x__tokens__mutmut_8': x__tokens__mutmut_8, 
    'x__tokens__mutmut_9': x__tokens__mutmut_9, 
    'x__tokens__mutmut_10': x__tokens__mutmut_10
}

def _tokens(*args, **kwargs):
    result = _mutmut_trampoline(x__tokens__mutmut_orig, x__tokens__mutmut_mutants, args, kwargs)
    return result 

_tokens.__signature__ = _mutmut_signature(x__tokens__mutmut_orig)
x__tokens__mutmut_orig.__name__ = 'x__tokens'


def x__shingles__mutmut_orig(tokens: list[str], k: int = 5) -> set[str]:
    if len(tokens) < k:
        return {" ".join(tokens)} if tokens else set()
    return {" ".join(tokens[i : i + k]) for i in range(len(tokens) - k + 1)}


def x__shingles__mutmut_1(tokens: list[str], k: int = 6) -> set[str]:
    if len(tokens) < k:
        return {" ".join(tokens)} if tokens else set()
    return {" ".join(tokens[i : i + k]) for i in range(len(tokens) - k + 1)}


def x__shingles__mutmut_2(tokens: list[str], k: int = 5) -> set[str]:
    if len(tokens) <= k:
        return {" ".join(tokens)} if tokens else set()
    return {" ".join(tokens[i : i + k]) for i in range(len(tokens) - k + 1)}


def x__shingles__mutmut_3(tokens: list[str], k: int = 5) -> set[str]:
    if len(tokens) < k:
        return {" ".join(None)} if tokens else set()
    return {" ".join(tokens[i : i + k]) for i in range(len(tokens) - k + 1)}


def x__shingles__mutmut_4(tokens: list[str], k: int = 5) -> set[str]:
    if len(tokens) < k:
        return {"XX XX".join(tokens)} if tokens else set()
    return {" ".join(tokens[i : i + k]) for i in range(len(tokens) - k + 1)}


def x__shingles__mutmut_5(tokens: list[str], k: int = 5) -> set[str]:
    if len(tokens) < k:
        return {" ".join(tokens)} if tokens else set()
    return {" ".join(None) for i in range(len(tokens) - k + 1)}


def x__shingles__mutmut_6(tokens: list[str], k: int = 5) -> set[str]:
    if len(tokens) < k:
        return {" ".join(tokens)} if tokens else set()
    return {"XX XX".join(tokens[i : i + k]) for i in range(len(tokens) - k + 1)}


def x__shingles__mutmut_7(tokens: list[str], k: int = 5) -> set[str]:
    if len(tokens) < k:
        return {" ".join(tokens)} if tokens else set()
    return {" ".join(tokens[i : i - k]) for i in range(len(tokens) - k + 1)}


def x__shingles__mutmut_8(tokens: list[str], k: int = 5) -> set[str]:
    if len(tokens) < k:
        return {" ".join(tokens)} if tokens else set()
    return {" ".join(tokens[i : i + k]) for i in range(None)}


def x__shingles__mutmut_9(tokens: list[str], k: int = 5) -> set[str]:
    if len(tokens) < k:
        return {" ".join(tokens)} if tokens else set()
    return {" ".join(tokens[i : i + k]) for i in range(len(tokens) - k - 1)}


def x__shingles__mutmut_10(tokens: list[str], k: int = 5) -> set[str]:
    if len(tokens) < k:
        return {" ".join(tokens)} if tokens else set()
    return {" ".join(tokens[i : i + k]) for i in range(len(tokens) + k + 1)}


def x__shingles__mutmut_11(tokens: list[str], k: int = 5) -> set[str]:
    if len(tokens) < k:
        return {" ".join(tokens)} if tokens else set()
    return {" ".join(tokens[i : i + k]) for i in range(len(tokens) - k + 2)}

x__shingles__mutmut_mutants : ClassVar[MutantDict] = {
'x__shingles__mutmut_1': x__shingles__mutmut_1, 
    'x__shingles__mutmut_2': x__shingles__mutmut_2, 
    'x__shingles__mutmut_3': x__shingles__mutmut_3, 
    'x__shingles__mutmut_4': x__shingles__mutmut_4, 
    'x__shingles__mutmut_5': x__shingles__mutmut_5, 
    'x__shingles__mutmut_6': x__shingles__mutmut_6, 
    'x__shingles__mutmut_7': x__shingles__mutmut_7, 
    'x__shingles__mutmut_8': x__shingles__mutmut_8, 
    'x__shingles__mutmut_9': x__shingles__mutmut_9, 
    'x__shingles__mutmut_10': x__shingles__mutmut_10, 
    'x__shingles__mutmut_11': x__shingles__mutmut_11
}

def _shingles(*args, **kwargs):
    result = _mutmut_trampoline(x__shingles__mutmut_orig, x__shingles__mutmut_mutants, args, kwargs)
    return result 

_shingles.__signature__ = _mutmut_signature(x__shingles__mutmut_orig)
x__shingles__mutmut_orig.__name__ = 'x__shingles'


def x_jaccard__mutmut_orig(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    intersection = len(a & b)
    union = len(a | b)
    return intersection / union if union else 0.0


def x_jaccard__mutmut_1(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 1.0
    if not a or not b:
        return 0.0
    intersection = len(a & b)
    union = len(a | b)
    return intersection / union if union else 0.0


def x_jaccard__mutmut_2(a: set[str], b: set[str]) -> float:
    if a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    intersection = len(a & b)
    union = len(a | b)
    return intersection / union if union else 0.0


def x_jaccard__mutmut_3(a: set[str], b: set[str]) -> float:
    if not a and b:
        return 1.0
    if not a or not b:
        return 0.0
    intersection = len(a & b)
    union = len(a | b)
    return intersection / union if union else 0.0


def x_jaccard__mutmut_4(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 2.0
    if not a or not b:
        return 0.0
    intersection = len(a & b)
    union = len(a | b)
    return intersection / union if union else 0.0


def x_jaccard__mutmut_5(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a and not b:
        return 0.0
    intersection = len(a & b)
    union = len(a | b)
    return intersection / union if union else 0.0


def x_jaccard__mutmut_6(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if a or not b:
        return 0.0
    intersection = len(a & b)
    union = len(a | b)
    return intersection / union if union else 0.0


def x_jaccard__mutmut_7(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or b:
        return 0.0
    intersection = len(a & b)
    union = len(a | b)
    return intersection / union if union else 0.0


def x_jaccard__mutmut_8(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 1.0
    intersection = len(a & b)
    union = len(a | b)
    return intersection / union if union else 0.0


def x_jaccard__mutmut_9(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    intersection = None
    union = len(a | b)
    return intersection / union if union else 0.0


def x_jaccard__mutmut_10(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    intersection = len(a & b)
    union = None
    return intersection / union if union else 0.0


def x_jaccard__mutmut_11(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    intersection = len(a & b)
    union = len(a | b)
    return intersection * union if union else 0.0


def x_jaccard__mutmut_12(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    intersection = len(a & b)
    union = len(a | b)
    return intersection / union if union else 1.0

x_jaccard__mutmut_mutants : ClassVar[MutantDict] = {
'x_jaccard__mutmut_1': x_jaccard__mutmut_1, 
    'x_jaccard__mutmut_2': x_jaccard__mutmut_2, 
    'x_jaccard__mutmut_3': x_jaccard__mutmut_3, 
    'x_jaccard__mutmut_4': x_jaccard__mutmut_4, 
    'x_jaccard__mutmut_5': x_jaccard__mutmut_5, 
    'x_jaccard__mutmut_6': x_jaccard__mutmut_6, 
    'x_jaccard__mutmut_7': x_jaccard__mutmut_7, 
    'x_jaccard__mutmut_8': x_jaccard__mutmut_8, 
    'x_jaccard__mutmut_9': x_jaccard__mutmut_9, 
    'x_jaccard__mutmut_10': x_jaccard__mutmut_10, 
    'x_jaccard__mutmut_11': x_jaccard__mutmut_11, 
    'x_jaccard__mutmut_12': x_jaccard__mutmut_12
}

def jaccard(*args, **kwargs):
    result = _mutmut_trampoline(x_jaccard__mutmut_orig, x_jaccard__mutmut_mutants, args, kwargs)
    return result 

jaccard.__signature__ = _mutmut_signature(x_jaccard__mutmut_orig)
x_jaccard__mutmut_orig.__name__ = 'x_jaccard'


def x_py_ast_hash__mutmut_orig(text: str) -> str:
    try:
        tree = ast.parse(text)
        dump = ast.dump(tree, annotate_fields=True, include_attributes=False)
        return hashlib.sha256(dump.encode("utf-8")).hexdigest()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return ""


def x_py_ast_hash__mutmut_1(text: str) -> str:
    try:
        tree = None
        dump = ast.dump(tree, annotate_fields=True, include_attributes=False)
        return hashlib.sha256(dump.encode("utf-8")).hexdigest()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return ""


def x_py_ast_hash__mutmut_2(text: str) -> str:
    try:
        tree = ast.parse(None)
        dump = ast.dump(tree, annotate_fields=True, include_attributes=False)
        return hashlib.sha256(dump.encode("utf-8")).hexdigest()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return ""


def x_py_ast_hash__mutmut_3(text: str) -> str:
    try:
        tree = ast.parse(text)
        dump = None
        return hashlib.sha256(dump.encode("utf-8")).hexdigest()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return ""


def x_py_ast_hash__mutmut_4(text: str) -> str:
    try:
        tree = ast.parse(text)
        dump = ast.dump(None, annotate_fields=True, include_attributes=False)
        return hashlib.sha256(dump.encode("utf-8")).hexdigest()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return ""


def x_py_ast_hash__mutmut_5(text: str) -> str:
    try:
        tree = ast.parse(text)
        dump = ast.dump(tree, annotate_fields=None, include_attributes=False)
        return hashlib.sha256(dump.encode("utf-8")).hexdigest()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return ""


def x_py_ast_hash__mutmut_6(text: str) -> str:
    try:
        tree = ast.parse(text)
        dump = ast.dump(tree, annotate_fields=True, include_attributes=None)
        return hashlib.sha256(dump.encode("utf-8")).hexdigest()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return ""


def x_py_ast_hash__mutmut_7(text: str) -> str:
    try:
        tree = ast.parse(text)
        dump = ast.dump(annotate_fields=True, include_attributes=False)
        return hashlib.sha256(dump.encode("utf-8")).hexdigest()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return ""


def x_py_ast_hash__mutmut_8(text: str) -> str:
    try:
        tree = ast.parse(text)
        dump = ast.dump(tree, include_attributes=False)
        return hashlib.sha256(dump.encode("utf-8")).hexdigest()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return ""


def x_py_ast_hash__mutmut_9(text: str) -> str:
    try:
        tree = ast.parse(text)
        dump = ast.dump(tree, annotate_fields=True, )
        return hashlib.sha256(dump.encode("utf-8")).hexdigest()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return ""


def x_py_ast_hash__mutmut_10(text: str) -> str:
    try:
        tree = ast.parse(text)
        dump = ast.dump(tree, annotate_fields=False, include_attributes=False)
        return hashlib.sha256(dump.encode("utf-8")).hexdigest()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return ""


def x_py_ast_hash__mutmut_11(text: str) -> str:
    try:
        tree = ast.parse(text)
        dump = ast.dump(tree, annotate_fields=True, include_attributes=True)
        return hashlib.sha256(dump.encode("utf-8")).hexdigest()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return ""


def x_py_ast_hash__mutmut_12(text: str) -> str:
    try:
        tree = ast.parse(text)
        dump = ast.dump(tree, annotate_fields=True, include_attributes=False)
        return hashlib.sha256(None).hexdigest()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return ""


def x_py_ast_hash__mutmut_13(text: str) -> str:
    try:
        tree = ast.parse(text)
        dump = ast.dump(tree, annotate_fields=True, include_attributes=False)
        return hashlib.sha256(dump.encode(None)).hexdigest()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return ""


def x_py_ast_hash__mutmut_14(text: str) -> str:
    try:
        tree = ast.parse(text)
        dump = ast.dump(tree, annotate_fields=True, include_attributes=False)
        return hashlib.sha256(dump.encode("XXutf-8XX")).hexdigest()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return ""


def x_py_ast_hash__mutmut_15(text: str) -> str:
    try:
        tree = ast.parse(text)
        dump = ast.dump(tree, annotate_fields=True, include_attributes=False)
        return hashlib.sha256(dump.encode("UTF-8")).hexdigest()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return ""


def x_py_ast_hash__mutmut_16(text: str) -> str:
    try:
        tree = ast.parse(text)
        dump = ast.dump(tree, annotate_fields=True, include_attributes=False)
        return hashlib.sha256(dump.encode("utf-8")).hexdigest()
    except Exception:
        logger.warning(None, exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return ""


def x_py_ast_hash__mutmut_17(text: str) -> str:
    try:
        tree = ast.parse(text)
        dump = ast.dump(tree, annotate_fields=True, include_attributes=False)
        return hashlib.sha256(dump.encode("utf-8")).hexdigest()
    except Exception:
        logger.warning("Exception occurred", exc_info=None)
        logger.warning("Exception occurred", exc_info=True)
        return ""


def x_py_ast_hash__mutmut_18(text: str) -> str:
    try:
        tree = ast.parse(text)
        dump = ast.dump(tree, annotate_fields=True, include_attributes=False)
        return hashlib.sha256(dump.encode("utf-8")).hexdigest()
    except Exception:
        logger.warning(exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return ""


def x_py_ast_hash__mutmut_19(text: str) -> str:
    try:
        tree = ast.parse(text)
        dump = ast.dump(tree, annotate_fields=True, include_attributes=False)
        return hashlib.sha256(dump.encode("utf-8")).hexdigest()
    except Exception:
        logger.warning("Exception occurred", )
        logger.warning("Exception occurred", exc_info=True)
        return ""


def x_py_ast_hash__mutmut_20(text: str) -> str:
    try:
        tree = ast.parse(text)
        dump = ast.dump(tree, annotate_fields=True, include_attributes=False)
        return hashlib.sha256(dump.encode("utf-8")).hexdigest()
    except Exception:
        logger.warning("XXException occurredXX", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return ""


def x_py_ast_hash__mutmut_21(text: str) -> str:
    try:
        tree = ast.parse(text)
        dump = ast.dump(tree, annotate_fields=True, include_attributes=False)
        return hashlib.sha256(dump.encode("utf-8")).hexdigest()
    except Exception:
        logger.warning("exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return ""


def x_py_ast_hash__mutmut_22(text: str) -> str:
    try:
        tree = ast.parse(text)
        dump = ast.dump(tree, annotate_fields=True, include_attributes=False)
        return hashlib.sha256(dump.encode("utf-8")).hexdigest()
    except Exception:
        logger.warning("EXCEPTION OCCURRED", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return ""


def x_py_ast_hash__mutmut_23(text: str) -> str:
    try:
        tree = ast.parse(text)
        dump = ast.dump(tree, annotate_fields=True, include_attributes=False)
        return hashlib.sha256(dump.encode("utf-8")).hexdigest()
    except Exception:
        logger.warning("Exception occurred", exc_info=False)
        logger.warning("Exception occurred", exc_info=True)
        return ""


def x_py_ast_hash__mutmut_24(text: str) -> str:
    try:
        tree = ast.parse(text)
        dump = ast.dump(tree, annotate_fields=True, include_attributes=False)
        return hashlib.sha256(dump.encode("utf-8")).hexdigest()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning(None, exc_info=True)
        return ""


def x_py_ast_hash__mutmut_25(text: str) -> str:
    try:
        tree = ast.parse(text)
        dump = ast.dump(tree, annotate_fields=True, include_attributes=False)
        return hashlib.sha256(dump.encode("utf-8")).hexdigest()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=None)
        return ""


def x_py_ast_hash__mutmut_26(text: str) -> str:
    try:
        tree = ast.parse(text)
        dump = ast.dump(tree, annotate_fields=True, include_attributes=False)
        return hashlib.sha256(dump.encode("utf-8")).hexdigest()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning(exc_info=True)
        return ""


def x_py_ast_hash__mutmut_27(text: str) -> str:
    try:
        tree = ast.parse(text)
        dump = ast.dump(tree, annotate_fields=True, include_attributes=False)
        return hashlib.sha256(dump.encode("utf-8")).hexdigest()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", )
        return ""


def x_py_ast_hash__mutmut_28(text: str) -> str:
    try:
        tree = ast.parse(text)
        dump = ast.dump(tree, annotate_fields=True, include_attributes=False)
        return hashlib.sha256(dump.encode("utf-8")).hexdigest()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("XXException occurredXX", exc_info=True)
        return ""


def x_py_ast_hash__mutmut_29(text: str) -> str:
    try:
        tree = ast.parse(text)
        dump = ast.dump(tree, annotate_fields=True, include_attributes=False)
        return hashlib.sha256(dump.encode("utf-8")).hexdigest()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("exception occurred", exc_info=True)
        return ""


def x_py_ast_hash__mutmut_30(text: str) -> str:
    try:
        tree = ast.parse(text)
        dump = ast.dump(tree, annotate_fields=True, include_attributes=False)
        return hashlib.sha256(dump.encode("utf-8")).hexdigest()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("EXCEPTION OCCURRED", exc_info=True)
        return ""


def x_py_ast_hash__mutmut_31(text: str) -> str:
    try:
        tree = ast.parse(text)
        dump = ast.dump(tree, annotate_fields=True, include_attributes=False)
        return hashlib.sha256(dump.encode("utf-8")).hexdigest()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=False)
        return ""


def x_py_ast_hash__mutmut_32(text: str) -> str:
    try:
        tree = ast.parse(text)
        dump = ast.dump(tree, annotate_fields=True, include_attributes=False)
        return hashlib.sha256(dump.encode("utf-8")).hexdigest()
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        return "XXXX"

x_py_ast_hash__mutmut_mutants : ClassVar[MutantDict] = {
'x_py_ast_hash__mutmut_1': x_py_ast_hash__mutmut_1, 
    'x_py_ast_hash__mutmut_2': x_py_ast_hash__mutmut_2, 
    'x_py_ast_hash__mutmut_3': x_py_ast_hash__mutmut_3, 
    'x_py_ast_hash__mutmut_4': x_py_ast_hash__mutmut_4, 
    'x_py_ast_hash__mutmut_5': x_py_ast_hash__mutmut_5, 
    'x_py_ast_hash__mutmut_6': x_py_ast_hash__mutmut_6, 
    'x_py_ast_hash__mutmut_7': x_py_ast_hash__mutmut_7, 
    'x_py_ast_hash__mutmut_8': x_py_ast_hash__mutmut_8, 
    'x_py_ast_hash__mutmut_9': x_py_ast_hash__mutmut_9, 
    'x_py_ast_hash__mutmut_10': x_py_ast_hash__mutmut_10, 
    'x_py_ast_hash__mutmut_11': x_py_ast_hash__mutmut_11, 
    'x_py_ast_hash__mutmut_12': x_py_ast_hash__mutmut_12, 
    'x_py_ast_hash__mutmut_13': x_py_ast_hash__mutmut_13, 
    'x_py_ast_hash__mutmut_14': x_py_ast_hash__mutmut_14, 
    'x_py_ast_hash__mutmut_15': x_py_ast_hash__mutmut_15, 
    'x_py_ast_hash__mutmut_16': x_py_ast_hash__mutmut_16, 
    'x_py_ast_hash__mutmut_17': x_py_ast_hash__mutmut_17, 
    'x_py_ast_hash__mutmut_18': x_py_ast_hash__mutmut_18, 
    'x_py_ast_hash__mutmut_19': x_py_ast_hash__mutmut_19, 
    'x_py_ast_hash__mutmut_20': x_py_ast_hash__mutmut_20, 
    'x_py_ast_hash__mutmut_21': x_py_ast_hash__mutmut_21, 
    'x_py_ast_hash__mutmut_22': x_py_ast_hash__mutmut_22, 
    'x_py_ast_hash__mutmut_23': x_py_ast_hash__mutmut_23, 
    'x_py_ast_hash__mutmut_24': x_py_ast_hash__mutmut_24, 
    'x_py_ast_hash__mutmut_25': x_py_ast_hash__mutmut_25, 
    'x_py_ast_hash__mutmut_26': x_py_ast_hash__mutmut_26, 
    'x_py_ast_hash__mutmut_27': x_py_ast_hash__mutmut_27, 
    'x_py_ast_hash__mutmut_28': x_py_ast_hash__mutmut_28, 
    'x_py_ast_hash__mutmut_29': x_py_ast_hash__mutmut_29, 
    'x_py_ast_hash__mutmut_30': x_py_ast_hash__mutmut_30, 
    'x_py_ast_hash__mutmut_31': x_py_ast_hash__mutmut_31, 
    'x_py_ast_hash__mutmut_32': x_py_ast_hash__mutmut_32
}

def py_ast_hash(*args, **kwargs):
    result = _mutmut_trampoline(x_py_ast_hash__mutmut_orig, x_py_ast_hash__mutmut_mutants, args, kwargs)
    return result 

py_ast_hash.__signature__ = _mutmut_signature(x_py_ast_hash__mutmut_orig)
x_py_ast_hash__mutmut_orig.__name__ = 'x_py_ast_hash'


def x_simhash64__mutmut_orig(tokens: list[str]) -> int:
    vector = [0] * 64
    for token in tokens:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        hashed = int.from_bytes(digest, "big")
        for bit in range(64):
            if (hashed >> bit) & 1:
                vector[bit] += 1
            else:
                vector[bit] -= 1
    value = 0
    for bit, weight in enumerate(vector):
        if weight >= 0:
            value |= 1 << bit
    return value


def x_simhash64__mutmut_1(tokens: list[str]) -> int:
    vector = None
    for token in tokens:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        hashed = int.from_bytes(digest, "big")
        for bit in range(64):
            if (hashed >> bit) & 1:
                vector[bit] += 1
            else:
                vector[bit] -= 1
    value = 0
    for bit, weight in enumerate(vector):
        if weight >= 0:
            value |= 1 << bit
    return value


def x_simhash64__mutmut_2(tokens: list[str]) -> int:
    vector = [0] / 64
    for token in tokens:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        hashed = int.from_bytes(digest, "big")
        for bit in range(64):
            if (hashed >> bit) & 1:
                vector[bit] += 1
            else:
                vector[bit] -= 1
    value = 0
    for bit, weight in enumerate(vector):
        if weight >= 0:
            value |= 1 << bit
    return value


def x_simhash64__mutmut_3(tokens: list[str]) -> int:
    vector = [1] * 64
    for token in tokens:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        hashed = int.from_bytes(digest, "big")
        for bit in range(64):
            if (hashed >> bit) & 1:
                vector[bit] += 1
            else:
                vector[bit] -= 1
    value = 0
    for bit, weight in enumerate(vector):
        if weight >= 0:
            value |= 1 << bit
    return value


def x_simhash64__mutmut_4(tokens: list[str]) -> int:
    vector = [0] * 65
    for token in tokens:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        hashed = int.from_bytes(digest, "big")
        for bit in range(64):
            if (hashed >> bit) & 1:
                vector[bit] += 1
            else:
                vector[bit] -= 1
    value = 0
    for bit, weight in enumerate(vector):
        if weight >= 0:
            value |= 1 << bit
    return value


def x_simhash64__mutmut_5(tokens: list[str]) -> int:
    vector = [0] * 64
    for token in tokens:
        digest = None
        hashed = int.from_bytes(digest, "big")
        for bit in range(64):
            if (hashed >> bit) & 1:
                vector[bit] += 1
            else:
                vector[bit] -= 1
    value = 0
    for bit, weight in enumerate(vector):
        if weight >= 0:
            value |= 1 << bit
    return value


def x_simhash64__mutmut_6(tokens: list[str]) -> int:
    vector = [0] * 64
    for token in tokens:
        digest = hashlib.blake2b(None, digest_size=8).digest()
        hashed = int.from_bytes(digest, "big")
        for bit in range(64):
            if (hashed >> bit) & 1:
                vector[bit] += 1
            else:
                vector[bit] -= 1
    value = 0
    for bit, weight in enumerate(vector):
        if weight >= 0:
            value |= 1 << bit
    return value


def x_simhash64__mutmut_7(tokens: list[str]) -> int:
    vector = [0] * 64
    for token in tokens:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=None).digest()
        hashed = int.from_bytes(digest, "big")
        for bit in range(64):
            if (hashed >> bit) & 1:
                vector[bit] += 1
            else:
                vector[bit] -= 1
    value = 0
    for bit, weight in enumerate(vector):
        if weight >= 0:
            value |= 1 << bit
    return value


def x_simhash64__mutmut_8(tokens: list[str]) -> int:
    vector = [0] * 64
    for token in tokens:
        digest = hashlib.blake2b(digest_size=8).digest()
        hashed = int.from_bytes(digest, "big")
        for bit in range(64):
            if (hashed >> bit) & 1:
                vector[bit] += 1
            else:
                vector[bit] -= 1
    value = 0
    for bit, weight in enumerate(vector):
        if weight >= 0:
            value |= 1 << bit
    return value


def x_simhash64__mutmut_9(tokens: list[str]) -> int:
    vector = [0] * 64
    for token in tokens:
        digest = hashlib.blake2b(token.encode("utf-8"), ).digest()
        hashed = int.from_bytes(digest, "big")
        for bit in range(64):
            if (hashed >> bit) & 1:
                vector[bit] += 1
            else:
                vector[bit] -= 1
    value = 0
    for bit, weight in enumerate(vector):
        if weight >= 0:
            value |= 1 << bit
    return value


def x_simhash64__mutmut_10(tokens: list[str]) -> int:
    vector = [0] * 64
    for token in tokens:
        digest = hashlib.blake2b(token.encode(None), digest_size=8).digest()
        hashed = int.from_bytes(digest, "big")
        for bit in range(64):
            if (hashed >> bit) & 1:
                vector[bit] += 1
            else:
                vector[bit] -= 1
    value = 0
    for bit, weight in enumerate(vector):
        if weight >= 0:
            value |= 1 << bit
    return value


def x_simhash64__mutmut_11(tokens: list[str]) -> int:
    vector = [0] * 64
    for token in tokens:
        digest = hashlib.blake2b(token.encode("XXutf-8XX"), digest_size=8).digest()
        hashed = int.from_bytes(digest, "big")
        for bit in range(64):
            if (hashed >> bit) & 1:
                vector[bit] += 1
            else:
                vector[bit] -= 1
    value = 0
    for bit, weight in enumerate(vector):
        if weight >= 0:
            value |= 1 << bit
    return value


def x_simhash64__mutmut_12(tokens: list[str]) -> int:
    vector = [0] * 64
    for token in tokens:
        digest = hashlib.blake2b(token.encode("UTF-8"), digest_size=8).digest()
        hashed = int.from_bytes(digest, "big")
        for bit in range(64):
            if (hashed >> bit) & 1:
                vector[bit] += 1
            else:
                vector[bit] -= 1
    value = 0
    for bit, weight in enumerate(vector):
        if weight >= 0:
            value |= 1 << bit
    return value


def x_simhash64__mutmut_13(tokens: list[str]) -> int:
    vector = [0] * 64
    for token in tokens:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=9).digest()
        hashed = int.from_bytes(digest, "big")
        for bit in range(64):
            if (hashed >> bit) & 1:
                vector[bit] += 1
            else:
                vector[bit] -= 1
    value = 0
    for bit, weight in enumerate(vector):
        if weight >= 0:
            value |= 1 << bit
    return value


def x_simhash64__mutmut_14(tokens: list[str]) -> int:
    vector = [0] * 64
    for token in tokens:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        hashed = None
        for bit in range(64):
            if (hashed >> bit) & 1:
                vector[bit] += 1
            else:
                vector[bit] -= 1
    value = 0
    for bit, weight in enumerate(vector):
        if weight >= 0:
            value |= 1 << bit
    return value


def x_simhash64__mutmut_15(tokens: list[str]) -> int:
    vector = [0] * 64
    for token in tokens:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        hashed = int.from_bytes(None, "big")
        for bit in range(64):
            if (hashed >> bit) & 1:
                vector[bit] += 1
            else:
                vector[bit] -= 1
    value = 0
    for bit, weight in enumerate(vector):
        if weight >= 0:
            value |= 1 << bit
    return value


def x_simhash64__mutmut_16(tokens: list[str]) -> int:
    vector = [0] * 64
    for token in tokens:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        hashed = int.from_bytes(digest, None)
        for bit in range(64):
            if (hashed >> bit) & 1:
                vector[bit] += 1
            else:
                vector[bit] -= 1
    value = 0
    for bit, weight in enumerate(vector):
        if weight >= 0:
            value |= 1 << bit
    return value


def x_simhash64__mutmut_17(tokens: list[str]) -> int:
    vector = [0] * 64
    for token in tokens:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        hashed = int.from_bytes("big")
        for bit in range(64):
            if (hashed >> bit) & 1:
                vector[bit] += 1
            else:
                vector[bit] -= 1
    value = 0
    for bit, weight in enumerate(vector):
        if weight >= 0:
            value |= 1 << bit
    return value


def x_simhash64__mutmut_18(tokens: list[str]) -> int:
    vector = [0] * 64
    for token in tokens:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        hashed = int.from_bytes(digest, )
        for bit in range(64):
            if (hashed >> bit) & 1:
                vector[bit] += 1
            else:
                vector[bit] -= 1
    value = 0
    for bit, weight in enumerate(vector):
        if weight >= 0:
            value |= 1 << bit
    return value


def x_simhash64__mutmut_19(tokens: list[str]) -> int:
    vector = [0] * 64
    for token in tokens:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        hashed = int.from_bytes(digest, "XXbigXX")
        for bit in range(64):
            if (hashed >> bit) & 1:
                vector[bit] += 1
            else:
                vector[bit] -= 1
    value = 0
    for bit, weight in enumerate(vector):
        if weight >= 0:
            value |= 1 << bit
    return value


def x_simhash64__mutmut_20(tokens: list[str]) -> int:
    vector = [0] * 64
    for token in tokens:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        hashed = int.from_bytes(digest, "BIG")
        for bit in range(64):
            if (hashed >> bit) & 1:
                vector[bit] += 1
            else:
                vector[bit] -= 1
    value = 0
    for bit, weight in enumerate(vector):
        if weight >= 0:
            value |= 1 << bit
    return value


def x_simhash64__mutmut_21(tokens: list[str]) -> int:
    vector = [0] * 64
    for token in tokens:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        hashed = int.from_bytes(digest, "big")
        for bit in range(None):
            if (hashed >> bit) & 1:
                vector[bit] += 1
            else:
                vector[bit] -= 1
    value = 0
    for bit, weight in enumerate(vector):
        if weight >= 0:
            value |= 1 << bit
    return value


def x_simhash64__mutmut_22(tokens: list[str]) -> int:
    vector = [0] * 64
    for token in tokens:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        hashed = int.from_bytes(digest, "big")
        for bit in range(65):
            if (hashed >> bit) & 1:
                vector[bit] += 1
            else:
                vector[bit] -= 1
    value = 0
    for bit, weight in enumerate(vector):
        if weight >= 0:
            value |= 1 << bit
    return value


def x_simhash64__mutmut_23(tokens: list[str]) -> int:
    vector = [0] * 64
    for token in tokens:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        hashed = int.from_bytes(digest, "big")
        for bit in range(64):
            if (hashed >> bit) | 1:
                vector[bit] += 1
            else:
                vector[bit] -= 1
    value = 0
    for bit, weight in enumerate(vector):
        if weight >= 0:
            value |= 1 << bit
    return value


def x_simhash64__mutmut_24(tokens: list[str]) -> int:
    vector = [0] * 64
    for token in tokens:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        hashed = int.from_bytes(digest, "big")
        for bit in range(64):
            if (hashed << bit) & 1:
                vector[bit] += 1
            else:
                vector[bit] -= 1
    value = 0
    for bit, weight in enumerate(vector):
        if weight >= 0:
            value |= 1 << bit
    return value


def x_simhash64__mutmut_25(tokens: list[str]) -> int:
    vector = [0] * 64
    for token in tokens:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        hashed = int.from_bytes(digest, "big")
        for bit in range(64):
            if (hashed >> bit) & 2:
                vector[bit] += 1
            else:
                vector[bit] -= 1
    value = 0
    for bit, weight in enumerate(vector):
        if weight >= 0:
            value |= 1 << bit
    return value


def x_simhash64__mutmut_26(tokens: list[str]) -> int:
    vector = [0] * 64
    for token in tokens:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        hashed = int.from_bytes(digest, "big")
        for bit in range(64):
            if (hashed >> bit) & 1:
                vector[bit] = 1
            else:
                vector[bit] -= 1
    value = 0
    for bit, weight in enumerate(vector):
        if weight >= 0:
            value |= 1 << bit
    return value


def x_simhash64__mutmut_27(tokens: list[str]) -> int:
    vector = [0] * 64
    for token in tokens:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        hashed = int.from_bytes(digest, "big")
        for bit in range(64):
            if (hashed >> bit) & 1:
                vector[bit] -= 1
            else:
                vector[bit] -= 1
    value = 0
    for bit, weight in enumerate(vector):
        if weight >= 0:
            value |= 1 << bit
    return value


def x_simhash64__mutmut_28(tokens: list[str]) -> int:
    vector = [0] * 64
    for token in tokens:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        hashed = int.from_bytes(digest, "big")
        for bit in range(64):
            if (hashed >> bit) & 1:
                vector[bit] += 2
            else:
                vector[bit] -= 1
    value = 0
    for bit, weight in enumerate(vector):
        if weight >= 0:
            value |= 1 << bit
    return value


def x_simhash64__mutmut_29(tokens: list[str]) -> int:
    vector = [0] * 64
    for token in tokens:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        hashed = int.from_bytes(digest, "big")
        for bit in range(64):
            if (hashed >> bit) & 1:
                vector[bit] += 1
            else:
                vector[bit] = 1
    value = 0
    for bit, weight in enumerate(vector):
        if weight >= 0:
            value |= 1 << bit
    return value


def x_simhash64__mutmut_30(tokens: list[str]) -> int:
    vector = [0] * 64
    for token in tokens:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        hashed = int.from_bytes(digest, "big")
        for bit in range(64):
            if (hashed >> bit) & 1:
                vector[bit] += 1
            else:
                vector[bit] += 1
    value = 0
    for bit, weight in enumerate(vector):
        if weight >= 0:
            value |= 1 << bit
    return value


def x_simhash64__mutmut_31(tokens: list[str]) -> int:
    vector = [0] * 64
    for token in tokens:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        hashed = int.from_bytes(digest, "big")
        for bit in range(64):
            if (hashed >> bit) & 1:
                vector[bit] += 1
            else:
                vector[bit] -= 2
    value = 0
    for bit, weight in enumerate(vector):
        if weight >= 0:
            value |= 1 << bit
    return value


def x_simhash64__mutmut_32(tokens: list[str]) -> int:
    vector = [0] * 64
    for token in tokens:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        hashed = int.from_bytes(digest, "big")
        for bit in range(64):
            if (hashed >> bit) & 1:
                vector[bit] += 1
            else:
                vector[bit] -= 1
    value = None
    for bit, weight in enumerate(vector):
        if weight >= 0:
            value |= 1 << bit
    return value


def x_simhash64__mutmut_33(tokens: list[str]) -> int:
    vector = [0] * 64
    for token in tokens:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        hashed = int.from_bytes(digest, "big")
        for bit in range(64):
            if (hashed >> bit) & 1:
                vector[bit] += 1
            else:
                vector[bit] -= 1
    value = 1
    for bit, weight in enumerate(vector):
        if weight >= 0:
            value |= 1 << bit
    return value


def x_simhash64__mutmut_34(tokens: list[str]) -> int:
    vector = [0] * 64
    for token in tokens:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        hashed = int.from_bytes(digest, "big")
        for bit in range(64):
            if (hashed >> bit) & 1:
                vector[bit] += 1
            else:
                vector[bit] -= 1
    value = 0
    for bit, weight in enumerate(None):
        if weight >= 0:
            value |= 1 << bit
    return value


def x_simhash64__mutmut_35(tokens: list[str]) -> int:
    vector = [0] * 64
    for token in tokens:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        hashed = int.from_bytes(digest, "big")
        for bit in range(64):
            if (hashed >> bit) & 1:
                vector[bit] += 1
            else:
                vector[bit] -= 1
    value = 0
    for bit, weight in enumerate(vector):
        if weight > 0:
            value |= 1 << bit
    return value


def x_simhash64__mutmut_36(tokens: list[str]) -> int:
    vector = [0] * 64
    for token in tokens:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        hashed = int.from_bytes(digest, "big")
        for bit in range(64):
            if (hashed >> bit) & 1:
                vector[bit] += 1
            else:
                vector[bit] -= 1
    value = 0
    for bit, weight in enumerate(vector):
        if weight >= 1:
            value |= 1 << bit
    return value


def x_simhash64__mutmut_37(tokens: list[str]) -> int:
    vector = [0] * 64
    for token in tokens:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        hashed = int.from_bytes(digest, "big")
        for bit in range(64):
            if (hashed >> bit) & 1:
                vector[bit] += 1
            else:
                vector[bit] -= 1
    value = 0
    for bit, weight in enumerate(vector):
        if weight >= 0:
            value = 1 << bit
    return value


def x_simhash64__mutmut_38(tokens: list[str]) -> int:
    vector = [0] * 64
    for token in tokens:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        hashed = int.from_bytes(digest, "big")
        for bit in range(64):
            if (hashed >> bit) & 1:
                vector[bit] += 1
            else:
                vector[bit] -= 1
    value = 0
    for bit, weight in enumerate(vector):
        if weight >= 0:
            value &= 1 << bit
    return value


def x_simhash64__mutmut_39(tokens: list[str]) -> int:
    vector = [0] * 64
    for token in tokens:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        hashed = int.from_bytes(digest, "big")
        for bit in range(64):
            if (hashed >> bit) & 1:
                vector[bit] += 1
            else:
                vector[bit] -= 1
    value = 0
    for bit, weight in enumerate(vector):
        if weight >= 0:
            value |= 1 >> bit
    return value


def x_simhash64__mutmut_40(tokens: list[str]) -> int:
    vector = [0] * 64
    for token in tokens:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        hashed = int.from_bytes(digest, "big")
        for bit in range(64):
            if (hashed >> bit) & 1:
                vector[bit] += 1
            else:
                vector[bit] -= 1
    value = 0
    for bit, weight in enumerate(vector):
        if weight >= 0:
            value |= 2 << bit
    return value

x_simhash64__mutmut_mutants : ClassVar[MutantDict] = {
'x_simhash64__mutmut_1': x_simhash64__mutmut_1, 
    'x_simhash64__mutmut_2': x_simhash64__mutmut_2, 
    'x_simhash64__mutmut_3': x_simhash64__mutmut_3, 
    'x_simhash64__mutmut_4': x_simhash64__mutmut_4, 
    'x_simhash64__mutmut_5': x_simhash64__mutmut_5, 
    'x_simhash64__mutmut_6': x_simhash64__mutmut_6, 
    'x_simhash64__mutmut_7': x_simhash64__mutmut_7, 
    'x_simhash64__mutmut_8': x_simhash64__mutmut_8, 
    'x_simhash64__mutmut_9': x_simhash64__mutmut_9, 
    'x_simhash64__mutmut_10': x_simhash64__mutmut_10, 
    'x_simhash64__mutmut_11': x_simhash64__mutmut_11, 
    'x_simhash64__mutmut_12': x_simhash64__mutmut_12, 
    'x_simhash64__mutmut_13': x_simhash64__mutmut_13, 
    'x_simhash64__mutmut_14': x_simhash64__mutmut_14, 
    'x_simhash64__mutmut_15': x_simhash64__mutmut_15, 
    'x_simhash64__mutmut_16': x_simhash64__mutmut_16, 
    'x_simhash64__mutmut_17': x_simhash64__mutmut_17, 
    'x_simhash64__mutmut_18': x_simhash64__mutmut_18, 
    'x_simhash64__mutmut_19': x_simhash64__mutmut_19, 
    'x_simhash64__mutmut_20': x_simhash64__mutmut_20, 
    'x_simhash64__mutmut_21': x_simhash64__mutmut_21, 
    'x_simhash64__mutmut_22': x_simhash64__mutmut_22, 
    'x_simhash64__mutmut_23': x_simhash64__mutmut_23, 
    'x_simhash64__mutmut_24': x_simhash64__mutmut_24, 
    'x_simhash64__mutmut_25': x_simhash64__mutmut_25, 
    'x_simhash64__mutmut_26': x_simhash64__mutmut_26, 
    'x_simhash64__mutmut_27': x_simhash64__mutmut_27, 
    'x_simhash64__mutmut_28': x_simhash64__mutmut_28, 
    'x_simhash64__mutmut_29': x_simhash64__mutmut_29, 
    'x_simhash64__mutmut_30': x_simhash64__mutmut_30, 
    'x_simhash64__mutmut_31': x_simhash64__mutmut_31, 
    'x_simhash64__mutmut_32': x_simhash64__mutmut_32, 
    'x_simhash64__mutmut_33': x_simhash64__mutmut_33, 
    'x_simhash64__mutmut_34': x_simhash64__mutmut_34, 
    'x_simhash64__mutmut_35': x_simhash64__mutmut_35, 
    'x_simhash64__mutmut_36': x_simhash64__mutmut_36, 
    'x_simhash64__mutmut_37': x_simhash64__mutmut_37, 
    'x_simhash64__mutmut_38': x_simhash64__mutmut_38, 
    'x_simhash64__mutmut_39': x_simhash64__mutmut_39, 
    'x_simhash64__mutmut_40': x_simhash64__mutmut_40
}

def simhash64(*args, **kwargs):
    result = _mutmut_trampoline(x_simhash64__mutmut_orig, x_simhash64__mutmut_mutants, args, kwargs)
    return result 

simhash64.__signature__ = _mutmut_signature(x_simhash64__mutmut_orig)
x_simhash64__mutmut_orig.__name__ = 'x_simhash64'


def x_hamming64__mutmut_orig(a: int, b: int) -> int:
    return (a ^ b).bit_count()


def x_hamming64__mutmut_1(a: int, b: int) -> int:
    return (a & b).bit_count()

x_hamming64__mutmut_mutants : ClassVar[MutantDict] = {
'x_hamming64__mutmut_1': x_hamming64__mutmut_1
}

def hamming64(*args, **kwargs):
    result = _mutmut_trampoline(x_hamming64__mutmut_orig, x_hamming64__mutmut_mutants, args, kwargs)
    return result 

hamming64.__signature__ = _mutmut_signature(x_hamming64__mutmut_orig)
x_hamming64__mutmut_orig.__name__ = 'x_hamming64'


@dataclass(slots=True)
class Similarity:
    jaccard: float
    py_ast_equal: bool
    doc_hd: int


def x_compute_similarity__mutmut_orig(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_1(path_a: Path, path_b: Path) -> Similarity:
    text_a = None
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_2(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding=None, errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_3(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors=None)
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_4(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_5(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", )
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_6(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="XXutf-8XX", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_7(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="UTF-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_8(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="XXignoreXX")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_9(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="IGNORE")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_10(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = None
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_11(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding=None, errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_12(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors=None)
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_13(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_14(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", )
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_15(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="XXutf-8XX", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_16(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="UTF-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_17(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="XXignoreXX")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_18(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="IGNORE")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_19(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = None
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_20(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(None, _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_21(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), None)
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_22(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_23(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), )
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_24(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(None), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_25(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(None)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_26(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(None))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_27(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(None)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_28(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = None
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_29(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = True
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_30(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" or path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_31(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix != ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_32(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == "XX.pyXX" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_33(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".PY" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_34(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix != ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_35(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == "XX.pyXX":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_36(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".PY":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_37(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = None
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_38(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(None)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_39(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = None
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_40(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(None)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_41(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = None
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_42(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) or hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_43(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(None) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_44(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a != hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_45(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = None
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_46(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 65
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_47(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} or path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_48(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix not in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_49(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {"XX.mdXX", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_50(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".MD", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_51(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", "XX.txtXX"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_52(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".TXT"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_53(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix not in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_54(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {"XX.mdXX", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_55(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".MD", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_56(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", "XX.txtXX"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_57(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".TXT"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_58(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = None
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_59(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(None, simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_60(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), None)
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_61(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_62(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), )
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_63(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(None), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_64(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(None)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_65(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(None))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_66(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(None)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_67(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=None, py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_68(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=None, doc_hd=doc_hd)


def x_compute_similarity__mutmut_69(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=None)


def x_compute_similarity__mutmut_70(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_71(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), doc_hd=doc_hd)


def x_compute_similarity__mutmut_72(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, )


def x_compute_similarity__mutmut_73(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(None, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_74(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, None), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_75(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(4), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_76(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, ), py_ast_equal=ast_equal, doc_hd=doc_hd)


def x_compute_similarity__mutmut_77(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 5), py_ast_equal=ast_equal, doc_hd=doc_hd)

x_compute_similarity__mutmut_mutants : ClassVar[MutantDict] = {
'x_compute_similarity__mutmut_1': x_compute_similarity__mutmut_1, 
    'x_compute_similarity__mutmut_2': x_compute_similarity__mutmut_2, 
    'x_compute_similarity__mutmut_3': x_compute_similarity__mutmut_3, 
    'x_compute_similarity__mutmut_4': x_compute_similarity__mutmut_4, 
    'x_compute_similarity__mutmut_5': x_compute_similarity__mutmut_5, 
    'x_compute_similarity__mutmut_6': x_compute_similarity__mutmut_6, 
    'x_compute_similarity__mutmut_7': x_compute_similarity__mutmut_7, 
    'x_compute_similarity__mutmut_8': x_compute_similarity__mutmut_8, 
    'x_compute_similarity__mutmut_9': x_compute_similarity__mutmut_9, 
    'x_compute_similarity__mutmut_10': x_compute_similarity__mutmut_10, 
    'x_compute_similarity__mutmut_11': x_compute_similarity__mutmut_11, 
    'x_compute_similarity__mutmut_12': x_compute_similarity__mutmut_12, 
    'x_compute_similarity__mutmut_13': x_compute_similarity__mutmut_13, 
    'x_compute_similarity__mutmut_14': x_compute_similarity__mutmut_14, 
    'x_compute_similarity__mutmut_15': x_compute_similarity__mutmut_15, 
    'x_compute_similarity__mutmut_16': x_compute_similarity__mutmut_16, 
    'x_compute_similarity__mutmut_17': x_compute_similarity__mutmut_17, 
    'x_compute_similarity__mutmut_18': x_compute_similarity__mutmut_18, 
    'x_compute_similarity__mutmut_19': x_compute_similarity__mutmut_19, 
    'x_compute_similarity__mutmut_20': x_compute_similarity__mutmut_20, 
    'x_compute_similarity__mutmut_21': x_compute_similarity__mutmut_21, 
    'x_compute_similarity__mutmut_22': x_compute_similarity__mutmut_22, 
    'x_compute_similarity__mutmut_23': x_compute_similarity__mutmut_23, 
    'x_compute_similarity__mutmut_24': x_compute_similarity__mutmut_24, 
    'x_compute_similarity__mutmut_25': x_compute_similarity__mutmut_25, 
    'x_compute_similarity__mutmut_26': x_compute_similarity__mutmut_26, 
    'x_compute_similarity__mutmut_27': x_compute_similarity__mutmut_27, 
    'x_compute_similarity__mutmut_28': x_compute_similarity__mutmut_28, 
    'x_compute_similarity__mutmut_29': x_compute_similarity__mutmut_29, 
    'x_compute_similarity__mutmut_30': x_compute_similarity__mutmut_30, 
    'x_compute_similarity__mutmut_31': x_compute_similarity__mutmut_31, 
    'x_compute_similarity__mutmut_32': x_compute_similarity__mutmut_32, 
    'x_compute_similarity__mutmut_33': x_compute_similarity__mutmut_33, 
    'x_compute_similarity__mutmut_34': x_compute_similarity__mutmut_34, 
    'x_compute_similarity__mutmut_35': x_compute_similarity__mutmut_35, 
    'x_compute_similarity__mutmut_36': x_compute_similarity__mutmut_36, 
    'x_compute_similarity__mutmut_37': x_compute_similarity__mutmut_37, 
    'x_compute_similarity__mutmut_38': x_compute_similarity__mutmut_38, 
    'x_compute_similarity__mutmut_39': x_compute_similarity__mutmut_39, 
    'x_compute_similarity__mutmut_40': x_compute_similarity__mutmut_40, 
    'x_compute_similarity__mutmut_41': x_compute_similarity__mutmut_41, 
    'x_compute_similarity__mutmut_42': x_compute_similarity__mutmut_42, 
    'x_compute_similarity__mutmut_43': x_compute_similarity__mutmut_43, 
    'x_compute_similarity__mutmut_44': x_compute_similarity__mutmut_44, 
    'x_compute_similarity__mutmut_45': x_compute_similarity__mutmut_45, 
    'x_compute_similarity__mutmut_46': x_compute_similarity__mutmut_46, 
    'x_compute_similarity__mutmut_47': x_compute_similarity__mutmut_47, 
    'x_compute_similarity__mutmut_48': x_compute_similarity__mutmut_48, 
    'x_compute_similarity__mutmut_49': x_compute_similarity__mutmut_49, 
    'x_compute_similarity__mutmut_50': x_compute_similarity__mutmut_50, 
    'x_compute_similarity__mutmut_51': x_compute_similarity__mutmut_51, 
    'x_compute_similarity__mutmut_52': x_compute_similarity__mutmut_52, 
    'x_compute_similarity__mutmut_53': x_compute_similarity__mutmut_53, 
    'x_compute_similarity__mutmut_54': x_compute_similarity__mutmut_54, 
    'x_compute_similarity__mutmut_55': x_compute_similarity__mutmut_55, 
    'x_compute_similarity__mutmut_56': x_compute_similarity__mutmut_56, 
    'x_compute_similarity__mutmut_57': x_compute_similarity__mutmut_57, 
    'x_compute_similarity__mutmut_58': x_compute_similarity__mutmut_58, 
    'x_compute_similarity__mutmut_59': x_compute_similarity__mutmut_59, 
    'x_compute_similarity__mutmut_60': x_compute_similarity__mutmut_60, 
    'x_compute_similarity__mutmut_61': x_compute_similarity__mutmut_61, 
    'x_compute_similarity__mutmut_62': x_compute_similarity__mutmut_62, 
    'x_compute_similarity__mutmut_63': x_compute_similarity__mutmut_63, 
    'x_compute_similarity__mutmut_64': x_compute_similarity__mutmut_64, 
    'x_compute_similarity__mutmut_65': x_compute_similarity__mutmut_65, 
    'x_compute_similarity__mutmut_66': x_compute_similarity__mutmut_66, 
    'x_compute_similarity__mutmut_67': x_compute_similarity__mutmut_67, 
    'x_compute_similarity__mutmut_68': x_compute_similarity__mutmut_68, 
    'x_compute_similarity__mutmut_69': x_compute_similarity__mutmut_69, 
    'x_compute_similarity__mutmut_70': x_compute_similarity__mutmut_70, 
    'x_compute_similarity__mutmut_71': x_compute_similarity__mutmut_71, 
    'x_compute_similarity__mutmut_72': x_compute_similarity__mutmut_72, 
    'x_compute_similarity__mutmut_73': x_compute_similarity__mutmut_73, 
    'x_compute_similarity__mutmut_74': x_compute_similarity__mutmut_74, 
    'x_compute_similarity__mutmut_75': x_compute_similarity__mutmut_75, 
    'x_compute_similarity__mutmut_76': x_compute_similarity__mutmut_76, 
    'x_compute_similarity__mutmut_77': x_compute_similarity__mutmut_77
}

def compute_similarity(*args, **kwargs):
    result = _mutmut_trampoline(x_compute_similarity__mutmut_orig, x_compute_similarity__mutmut_mutants, args, kwargs)
    return result 

compute_similarity.__signature__ = _mutmut_signature(x_compute_similarity__mutmut_orig)
x_compute_similarity__mutmut_orig.__name__ = 'x_compute_similarity'
