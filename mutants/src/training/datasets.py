"""
Datasets Module

This module provides functionality for datasets.

Usage:
    from training.datasets import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations
import logging
logger = logging.getLogger(__name__)
"""Dataset utilities for training."""


import hashlib
import json
from pathlib import Path
from typing import Iterable, Iterator, Sequence

import numpy as np

import torch

try:  # optional dependency
    from datasets import Dataset  # type: ignore
except ImportError:  # pragma: no cover - optional dep missing
    Dataset = None  # type: ignore[assignment]
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


def x__encode_text__mutmut_orig(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_1(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = None
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_2(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        None,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_3(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=None,
        padding="max_length",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_4(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding=None,
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_5(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=None,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_6(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors=None,
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_7(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_8(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        padding="max_length",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_9(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_10(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_11(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_12(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="XXmax_lengthXX",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_13(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="MAX_LENGTH",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_14(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=False,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_15(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="XXnpXX",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_16(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="NP",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_17(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="np",
    )
    input_ids = None
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_18(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype(None)
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_19(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["XXinput_idsXX"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_20(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["INPUT_IDS"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_21(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("XXint64XX")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_22(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("INT64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_23(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = None
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_24(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype(None)
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_25(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["XXattention_maskXX"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_26(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["ATTENTION_MASK"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_27(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("XXint64XX")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_28(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("INT64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_29(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = None
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_30(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(None)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_31(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = None
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_32(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :+1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_33(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-2] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_34(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 2:]
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_35(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = None
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_36(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(None, "eos_token_id", -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_37(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, None, -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_38(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", None)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_39(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr("eos_token_id", -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_40(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_41(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", )
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_42(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "XXeos_token_idXX", -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_43(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "EOS_TOKEN_ID", -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_44(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", +100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_45(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", -101)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_46(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, -1] = None
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_47(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, +1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_48(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, -2] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_49(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, -1] = int(None)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_50(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, -1] = int(eos)
    return {
        "XXinput_idsXX": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_51(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, -1] = int(eos)
    return {
        "INPUT_IDS": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_52(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[1],
        "attention_mask": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_53(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "XXattention_maskXX": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_54(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "ATTENTION_MASK": attn[0],
        "labels": labels[0],
    }


def x__encode_text__mutmut_55(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[1],
        "labels": labels[0],
    }


def x__encode_text__mutmut_56(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "XXlabelsXX": labels[0],
    }


def x__encode_text__mutmut_57(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "LABELS": labels[0],
    }


def x__encode_text__mutmut_58(tokenizer, text: str, max_length: int) -> dict[str, np.ndarray]:
    enc = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="np",
    )
    input_ids = enc["input_ids"].astype("int64")
    attn = enc["attention_mask"].astype("int64")
    labels = np.copy(input_ids)
    labels[:, :-1] = input_ids[:, 1:]
    eos = getattr(tokenizer, "eos_token_id", -100)
    labels[:, -1] = int(eos)
    return {
        "input_ids": input_ids[0],
        "attention_mask": attn[0],
        "labels": labels[1],
    }

x__encode_text__mutmut_mutants : ClassVar[MutantDict] = {
'x__encode_text__mutmut_1': x__encode_text__mutmut_1, 
    'x__encode_text__mutmut_2': x__encode_text__mutmut_2, 
    'x__encode_text__mutmut_3': x__encode_text__mutmut_3, 
    'x__encode_text__mutmut_4': x__encode_text__mutmut_4, 
    'x__encode_text__mutmut_5': x__encode_text__mutmut_5, 
    'x__encode_text__mutmut_6': x__encode_text__mutmut_6, 
    'x__encode_text__mutmut_7': x__encode_text__mutmut_7, 
    'x__encode_text__mutmut_8': x__encode_text__mutmut_8, 
    'x__encode_text__mutmut_9': x__encode_text__mutmut_9, 
    'x__encode_text__mutmut_10': x__encode_text__mutmut_10, 
    'x__encode_text__mutmut_11': x__encode_text__mutmut_11, 
    'x__encode_text__mutmut_12': x__encode_text__mutmut_12, 
    'x__encode_text__mutmut_13': x__encode_text__mutmut_13, 
    'x__encode_text__mutmut_14': x__encode_text__mutmut_14, 
    'x__encode_text__mutmut_15': x__encode_text__mutmut_15, 
    'x__encode_text__mutmut_16': x__encode_text__mutmut_16, 
    'x__encode_text__mutmut_17': x__encode_text__mutmut_17, 
    'x__encode_text__mutmut_18': x__encode_text__mutmut_18, 
    'x__encode_text__mutmut_19': x__encode_text__mutmut_19, 
    'x__encode_text__mutmut_20': x__encode_text__mutmut_20, 
    'x__encode_text__mutmut_21': x__encode_text__mutmut_21, 
    'x__encode_text__mutmut_22': x__encode_text__mutmut_22, 
    'x__encode_text__mutmut_23': x__encode_text__mutmut_23, 
    'x__encode_text__mutmut_24': x__encode_text__mutmut_24, 
    'x__encode_text__mutmut_25': x__encode_text__mutmut_25, 
    'x__encode_text__mutmut_26': x__encode_text__mutmut_26, 
    'x__encode_text__mutmut_27': x__encode_text__mutmut_27, 
    'x__encode_text__mutmut_28': x__encode_text__mutmut_28, 
    'x__encode_text__mutmut_29': x__encode_text__mutmut_29, 
    'x__encode_text__mutmut_30': x__encode_text__mutmut_30, 
    'x__encode_text__mutmut_31': x__encode_text__mutmut_31, 
    'x__encode_text__mutmut_32': x__encode_text__mutmut_32, 
    'x__encode_text__mutmut_33': x__encode_text__mutmut_33, 
    'x__encode_text__mutmut_34': x__encode_text__mutmut_34, 
    'x__encode_text__mutmut_35': x__encode_text__mutmut_35, 
    'x__encode_text__mutmut_36': x__encode_text__mutmut_36, 
    'x__encode_text__mutmut_37': x__encode_text__mutmut_37, 
    'x__encode_text__mutmut_38': x__encode_text__mutmut_38, 
    'x__encode_text__mutmut_39': x__encode_text__mutmut_39, 
    'x__encode_text__mutmut_40': x__encode_text__mutmut_40, 
    'x__encode_text__mutmut_41': x__encode_text__mutmut_41, 
    'x__encode_text__mutmut_42': x__encode_text__mutmut_42, 
    'x__encode_text__mutmut_43': x__encode_text__mutmut_43, 
    'x__encode_text__mutmut_44': x__encode_text__mutmut_44, 
    'x__encode_text__mutmut_45': x__encode_text__mutmut_45, 
    'x__encode_text__mutmut_46': x__encode_text__mutmut_46, 
    'x__encode_text__mutmut_47': x__encode_text__mutmut_47, 
    'x__encode_text__mutmut_48': x__encode_text__mutmut_48, 
    'x__encode_text__mutmut_49': x__encode_text__mutmut_49, 
    'x__encode_text__mutmut_50': x__encode_text__mutmut_50, 
    'x__encode_text__mutmut_51': x__encode_text__mutmut_51, 
    'x__encode_text__mutmut_52': x__encode_text__mutmut_52, 
    'x__encode_text__mutmut_53': x__encode_text__mutmut_53, 
    'x__encode_text__mutmut_54': x__encode_text__mutmut_54, 
    'x__encode_text__mutmut_55': x__encode_text__mutmut_55, 
    'x__encode_text__mutmut_56': x__encode_text__mutmut_56, 
    'x__encode_text__mutmut_57': x__encode_text__mutmut_57, 
    'x__encode_text__mutmut_58': x__encode_text__mutmut_58
}

def _encode_text(*args, **kwargs):
    result = _mutmut_trampoline(x__encode_text__mutmut_orig, x__encode_text__mutmut_mutants, args, kwargs)
    return result 

_encode_text.__signature__ = _mutmut_signature(x__encode_text__mutmut_orig)
x__encode_text__mutmut_orig.__name__ = 'x__encode_text'


class TextDataset(torch.utils.data.Dataset):
    """Materialized dataset of tokenized texts."""

    def xǁTextDatasetǁ__init____mutmut_orig(
        self,
        items: Sequence[str],
        tokenizer,
        max_length: int,
        *,
        seed_data: int | None = None,
    ) -> None:
        ordered = list(items)
        if seed_data is not None and len(ordered) > 1:
            rng = np.random.default_rng(seed_data)
            rng.shuffle(ordered)
        self.data = [_encode_text(tokenizer, t, max_length) for t in ordered]

    def xǁTextDatasetǁ__init____mutmut_1(
        self,
        items: Sequence[str],
        tokenizer,
        max_length: int,
        *,
        seed_data: int | None = None,
    ) -> None:
        ordered = None
        if seed_data is not None and len(ordered) > 1:
            rng = np.random.default_rng(seed_data)
            rng.shuffle(ordered)
        self.data = [_encode_text(tokenizer, t, max_length) for t in ordered]

    def xǁTextDatasetǁ__init____mutmut_2(
        self,
        items: Sequence[str],
        tokenizer,
        max_length: int,
        *,
        seed_data: int | None = None,
    ) -> None:
        ordered = list(None)
        if seed_data is not None and len(ordered) > 1:
            rng = np.random.default_rng(seed_data)
            rng.shuffle(ordered)
        self.data = [_encode_text(tokenizer, t, max_length) for t in ordered]

    def xǁTextDatasetǁ__init____mutmut_3(
        self,
        items: Sequence[str],
        tokenizer,
        max_length: int,
        *,
        seed_data: int | None = None,
    ) -> None:
        ordered = list(items)
        if seed_data is not None or len(ordered) > 1:
            rng = np.random.default_rng(seed_data)
            rng.shuffle(ordered)
        self.data = [_encode_text(tokenizer, t, max_length) for t in ordered]

    def xǁTextDatasetǁ__init____mutmut_4(
        self,
        items: Sequence[str],
        tokenizer,
        max_length: int,
        *,
        seed_data: int | None = None,
    ) -> None:
        ordered = list(items)
        if seed_data is None and len(ordered) > 1:
            rng = np.random.default_rng(seed_data)
            rng.shuffle(ordered)
        self.data = [_encode_text(tokenizer, t, max_length) for t in ordered]

    def xǁTextDatasetǁ__init____mutmut_5(
        self,
        items: Sequence[str],
        tokenizer,
        max_length: int,
        *,
        seed_data: int | None = None,
    ) -> None:
        ordered = list(items)
        if seed_data is not None and len(ordered) >= 1:
            rng = np.random.default_rng(seed_data)
            rng.shuffle(ordered)
        self.data = [_encode_text(tokenizer, t, max_length) for t in ordered]

    def xǁTextDatasetǁ__init____mutmut_6(
        self,
        items: Sequence[str],
        tokenizer,
        max_length: int,
        *,
        seed_data: int | None = None,
    ) -> None:
        ordered = list(items)
        if seed_data is not None and len(ordered) > 2:
            rng = np.random.default_rng(seed_data)
            rng.shuffle(ordered)
        self.data = [_encode_text(tokenizer, t, max_length) for t in ordered]

    def xǁTextDatasetǁ__init____mutmut_7(
        self,
        items: Sequence[str],
        tokenizer,
        max_length: int,
        *,
        seed_data: int | None = None,
    ) -> None:
        ordered = list(items)
        if seed_data is not None and len(ordered) > 1:
            rng = None
            rng.shuffle(ordered)
        self.data = [_encode_text(tokenizer, t, max_length) for t in ordered]

    def xǁTextDatasetǁ__init____mutmut_8(
        self,
        items: Sequence[str],
        tokenizer,
        max_length: int,
        *,
        seed_data: int | None = None,
    ) -> None:
        ordered = list(items)
        if seed_data is not None and len(ordered) > 1:
            rng = np.random.default_rng(None)
            rng.shuffle(ordered)
        self.data = [_encode_text(tokenizer, t, max_length) for t in ordered]

    def xǁTextDatasetǁ__init____mutmut_9(
        self,
        items: Sequence[str],
        tokenizer,
        max_length: int,
        *,
        seed_data: int | None = None,
    ) -> None:
        ordered = list(items)
        if seed_data is not None and len(ordered) > 1:
            rng = np.random.default_rng(seed_data)
            rng.shuffle(None)
        self.data = [_encode_text(tokenizer, t, max_length) for t in ordered]

    def xǁTextDatasetǁ__init____mutmut_10(
        self,
        items: Sequence[str],
        tokenizer,
        max_length: int,
        *,
        seed_data: int | None = None,
    ) -> None:
        ordered = list(items)
        if seed_data is not None and len(ordered) > 1:
            rng = np.random.default_rng(seed_data)
            rng.shuffle(ordered)
        self.data = None

    def xǁTextDatasetǁ__init____mutmut_11(
        self,
        items: Sequence[str],
        tokenizer,
        max_length: int,
        *,
        seed_data: int | None = None,
    ) -> None:
        ordered = list(items)
        if seed_data is not None and len(ordered) > 1:
            rng = np.random.default_rng(seed_data)
            rng.shuffle(ordered)
        self.data = [_encode_text(None, t, max_length) for t in ordered]

    def xǁTextDatasetǁ__init____mutmut_12(
        self,
        items: Sequence[str],
        tokenizer,
        max_length: int,
        *,
        seed_data: int | None = None,
    ) -> None:
        ordered = list(items)
        if seed_data is not None and len(ordered) > 1:
            rng = np.random.default_rng(seed_data)
            rng.shuffle(ordered)
        self.data = [_encode_text(tokenizer, None, max_length) for t in ordered]

    def xǁTextDatasetǁ__init____mutmut_13(
        self,
        items: Sequence[str],
        tokenizer,
        max_length: int,
        *,
        seed_data: int | None = None,
    ) -> None:
        ordered = list(items)
        if seed_data is not None and len(ordered) > 1:
            rng = np.random.default_rng(seed_data)
            rng.shuffle(ordered)
        self.data = [_encode_text(tokenizer, t, None) for t in ordered]

    def xǁTextDatasetǁ__init____mutmut_14(
        self,
        items: Sequence[str],
        tokenizer,
        max_length: int,
        *,
        seed_data: int | None = None,
    ) -> None:
        ordered = list(items)
        if seed_data is not None and len(ordered) > 1:
            rng = np.random.default_rng(seed_data)
            rng.shuffle(ordered)
        self.data = [_encode_text(t, max_length) for t in ordered]

    def xǁTextDatasetǁ__init____mutmut_15(
        self,
        items: Sequence[str],
        tokenizer,
        max_length: int,
        *,
        seed_data: int | None = None,
    ) -> None:
        ordered = list(items)
        if seed_data is not None and len(ordered) > 1:
            rng = np.random.default_rng(seed_data)
            rng.shuffle(ordered)
        self.data = [_encode_text(tokenizer, max_length) for t in ordered]

    def xǁTextDatasetǁ__init____mutmut_16(
        self,
        items: Sequence[str],
        tokenizer,
        max_length: int,
        *,
        seed_data: int | None = None,
    ) -> None:
        ordered = list(items)
        if seed_data is not None and len(ordered) > 1:
            rng = np.random.default_rng(seed_data)
            rng.shuffle(ordered)
        self.data = [_encode_text(tokenizer, t, ) for t in ordered]
    
    xǁTextDatasetǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTextDatasetǁ__init____mutmut_1': xǁTextDatasetǁ__init____mutmut_1, 
        'xǁTextDatasetǁ__init____mutmut_2': xǁTextDatasetǁ__init____mutmut_2, 
        'xǁTextDatasetǁ__init____mutmut_3': xǁTextDatasetǁ__init____mutmut_3, 
        'xǁTextDatasetǁ__init____mutmut_4': xǁTextDatasetǁ__init____mutmut_4, 
        'xǁTextDatasetǁ__init____mutmut_5': xǁTextDatasetǁ__init____mutmut_5, 
        'xǁTextDatasetǁ__init____mutmut_6': xǁTextDatasetǁ__init____mutmut_6, 
        'xǁTextDatasetǁ__init____mutmut_7': xǁTextDatasetǁ__init____mutmut_7, 
        'xǁTextDatasetǁ__init____mutmut_8': xǁTextDatasetǁ__init____mutmut_8, 
        'xǁTextDatasetǁ__init____mutmut_9': xǁTextDatasetǁ__init____mutmut_9, 
        'xǁTextDatasetǁ__init____mutmut_10': xǁTextDatasetǁ__init____mutmut_10, 
        'xǁTextDatasetǁ__init____mutmut_11': xǁTextDatasetǁ__init____mutmut_11, 
        'xǁTextDatasetǁ__init____mutmut_12': xǁTextDatasetǁ__init____mutmut_12, 
        'xǁTextDatasetǁ__init____mutmut_13': xǁTextDatasetǁ__init____mutmut_13, 
        'xǁTextDatasetǁ__init____mutmut_14': xǁTextDatasetǁ__init____mutmut_14, 
        'xǁTextDatasetǁ__init____mutmut_15': xǁTextDatasetǁ__init____mutmut_15, 
        'xǁTextDatasetǁ__init____mutmut_16': xǁTextDatasetǁ__init____mutmut_16
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTextDatasetǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁTextDatasetǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁTextDatasetǁ__init____mutmut_orig)
    xǁTextDatasetǁ__init____mutmut_orig.__name__ = 'xǁTextDatasetǁ__init__'

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self.data)

    def __getitem__(self, idx: int) -> dict[str, np.ndarray]:  # pragma: no cover - trivial
        return self.data[idx]


class IterableTextDataset(torch.utils.data.IterableDataset):
    """Tokenize a stream of texts on the fly."""

    def xǁIterableTextDatasetǁ__init____mutmut_orig(
        self,
        stream: Iterable[str],
        tokenizer,
        max_length: int,
        prefetch_k: int = 0,
    ) -> None:
        super().__init__()
        self.stream = stream
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.prefetch_k = int(prefetch_k)

    def xǁIterableTextDatasetǁ__init____mutmut_1(
        self,
        stream: Iterable[str],
        tokenizer,
        max_length: int,
        prefetch_k: int = 1,
    ) -> None:
        super().__init__()
        self.stream = stream
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.prefetch_k = int(prefetch_k)

    def xǁIterableTextDatasetǁ__init____mutmut_2(
        self,
        stream: Iterable[str],
        tokenizer,
        max_length: int,
        prefetch_k: int = 0,
    ) -> None:
        super().__init__()
        self.stream = None
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.prefetch_k = int(prefetch_k)

    def xǁIterableTextDatasetǁ__init____mutmut_3(
        self,
        stream: Iterable[str],
        tokenizer,
        max_length: int,
        prefetch_k: int = 0,
    ) -> None:
        super().__init__()
        self.stream = stream
        self.tokenizer = None
        self.max_length = max_length
        self.prefetch_k = int(prefetch_k)

    def xǁIterableTextDatasetǁ__init____mutmut_4(
        self,
        stream: Iterable[str],
        tokenizer,
        max_length: int,
        prefetch_k: int = 0,
    ) -> None:
        super().__init__()
        self.stream = stream
        self.tokenizer = tokenizer
        self.max_length = None
        self.prefetch_k = int(prefetch_k)

    def xǁIterableTextDatasetǁ__init____mutmut_5(
        self,
        stream: Iterable[str],
        tokenizer,
        max_length: int,
        prefetch_k: int = 0,
    ) -> None:
        super().__init__()
        self.stream = stream
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.prefetch_k = None

    def xǁIterableTextDatasetǁ__init____mutmut_6(
        self,
        stream: Iterable[str],
        tokenizer,
        max_length: int,
        prefetch_k: int = 0,
    ) -> None:
        super().__init__()
        self.stream = stream
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.prefetch_k = int(None)
    
    xǁIterableTextDatasetǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁIterableTextDatasetǁ__init____mutmut_1': xǁIterableTextDatasetǁ__init____mutmut_1, 
        'xǁIterableTextDatasetǁ__init____mutmut_2': xǁIterableTextDatasetǁ__init____mutmut_2, 
        'xǁIterableTextDatasetǁ__init____mutmut_3': xǁIterableTextDatasetǁ__init____mutmut_3, 
        'xǁIterableTextDatasetǁ__init____mutmut_4': xǁIterableTextDatasetǁ__init____mutmut_4, 
        'xǁIterableTextDatasetǁ__init____mutmut_5': xǁIterableTextDatasetǁ__init____mutmut_5, 
        'xǁIterableTextDatasetǁ__init____mutmut_6': xǁIterableTextDatasetǁ__init____mutmut_6
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁIterableTextDatasetǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁIterableTextDatasetǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁIterableTextDatasetǁ__init____mutmut_orig)
    xǁIterableTextDatasetǁ__init____mutmut_orig.__name__ = 'xǁIterableTextDatasetǁ__init__'

    def xǁIterableTextDatasetǁ__iter____mutmut_orig(self) -> Iterator[dict[str, np.ndarray]]:
        if self.prefetch_k <= 0:
            for text in self.stream:
                yield _encode_text(self.tokenizer, text, self.max_length)
        else:
            buf: list[dict[str, np.ndarray]] = []
            for text in self.stream:
                buf.append(_encode_text(self.tokenizer, text, self.max_length))
                if len(buf) >= self.prefetch_k:
                    for item in buf:
                        yield item
                    buf.clear()
            for item in buf:
                yield item

    def xǁIterableTextDatasetǁ__iter____mutmut_1(self) -> Iterator[dict[str, np.ndarray]]:
        if self.prefetch_k < 0:
            for text in self.stream:
                yield _encode_text(self.tokenizer, text, self.max_length)
        else:
            buf: list[dict[str, np.ndarray]] = []
            for text in self.stream:
                buf.append(_encode_text(self.tokenizer, text, self.max_length))
                if len(buf) >= self.prefetch_k:
                    for item in buf:
                        yield item
                    buf.clear()
            for item in buf:
                yield item

    def xǁIterableTextDatasetǁ__iter____mutmut_2(self) -> Iterator[dict[str, np.ndarray]]:
        if self.prefetch_k <= 1:
            for text in self.stream:
                yield _encode_text(self.tokenizer, text, self.max_length)
        else:
            buf: list[dict[str, np.ndarray]] = []
            for text in self.stream:
                buf.append(_encode_text(self.tokenizer, text, self.max_length))
                if len(buf) >= self.prefetch_k:
                    for item in buf:
                        yield item
                    buf.clear()
            for item in buf:
                yield item

    def xǁIterableTextDatasetǁ__iter____mutmut_3(self) -> Iterator[dict[str, np.ndarray]]:
        if self.prefetch_k <= 0:
            for text in self.stream:
                yield _encode_text(None, text, self.max_length)
        else:
            buf: list[dict[str, np.ndarray]] = []
            for text in self.stream:
                buf.append(_encode_text(self.tokenizer, text, self.max_length))
                if len(buf) >= self.prefetch_k:
                    for item in buf:
                        yield item
                    buf.clear()
            for item in buf:
                yield item

    def xǁIterableTextDatasetǁ__iter____mutmut_4(self) -> Iterator[dict[str, np.ndarray]]:
        if self.prefetch_k <= 0:
            for text in self.stream:
                yield _encode_text(self.tokenizer, None, self.max_length)
        else:
            buf: list[dict[str, np.ndarray]] = []
            for text in self.stream:
                buf.append(_encode_text(self.tokenizer, text, self.max_length))
                if len(buf) >= self.prefetch_k:
                    for item in buf:
                        yield item
                    buf.clear()
            for item in buf:
                yield item

    def xǁIterableTextDatasetǁ__iter____mutmut_5(self) -> Iterator[dict[str, np.ndarray]]:
        if self.prefetch_k <= 0:
            for text in self.stream:
                yield _encode_text(self.tokenizer, text, None)
        else:
            buf: list[dict[str, np.ndarray]] = []
            for text in self.stream:
                buf.append(_encode_text(self.tokenizer, text, self.max_length))
                if len(buf) >= self.prefetch_k:
                    for item in buf:
                        yield item
                    buf.clear()
            for item in buf:
                yield item

    def xǁIterableTextDatasetǁ__iter____mutmut_6(self) -> Iterator[dict[str, np.ndarray]]:
        if self.prefetch_k <= 0:
            for text in self.stream:
                yield _encode_text(text, self.max_length)
        else:
            buf: list[dict[str, np.ndarray]] = []
            for text in self.stream:
                buf.append(_encode_text(self.tokenizer, text, self.max_length))
                if len(buf) >= self.prefetch_k:
                    for item in buf:
                        yield item
                    buf.clear()
            for item in buf:
                yield item

    def xǁIterableTextDatasetǁ__iter____mutmut_7(self) -> Iterator[dict[str, np.ndarray]]:
        if self.prefetch_k <= 0:
            for text in self.stream:
                yield _encode_text(self.tokenizer, self.max_length)
        else:
            buf: list[dict[str, np.ndarray]] = []
            for text in self.stream:
                buf.append(_encode_text(self.tokenizer, text, self.max_length))
                if len(buf) >= self.prefetch_k:
                    for item in buf:
                        yield item
                    buf.clear()
            for item in buf:
                yield item

    def xǁIterableTextDatasetǁ__iter____mutmut_8(self) -> Iterator[dict[str, np.ndarray]]:
        if self.prefetch_k <= 0:
            for text in self.stream:
                yield _encode_text(self.tokenizer, text, )
        else:
            buf: list[dict[str, np.ndarray]] = []
            for text in self.stream:
                buf.append(_encode_text(self.tokenizer, text, self.max_length))
                if len(buf) >= self.prefetch_k:
                    for item in buf:
                        yield item
                    buf.clear()
            for item in buf:
                yield item

    def xǁIterableTextDatasetǁ__iter____mutmut_9(self) -> Iterator[dict[str, np.ndarray]]:
        if self.prefetch_k <= 0:
            for text in self.stream:
                yield _encode_text(self.tokenizer, text, self.max_length)
        else:
            buf: list[dict[str, np.ndarray]] = None
            for text in self.stream:
                buf.append(_encode_text(self.tokenizer, text, self.max_length))
                if len(buf) >= self.prefetch_k:
                    for item in buf:
                        yield item
                    buf.clear()
            for item in buf:
                yield item

    def xǁIterableTextDatasetǁ__iter____mutmut_10(self) -> Iterator[dict[str, np.ndarray]]:
        if self.prefetch_k <= 0:
            for text in self.stream:
                yield _encode_text(self.tokenizer, text, self.max_length)
        else:
            buf: list[dict[str, np.ndarray]] = []
            for text in self.stream:
                buf.append(None)
                if len(buf) >= self.prefetch_k:
                    for item in buf:
                        yield item
                    buf.clear()
            for item in buf:
                yield item

    def xǁIterableTextDatasetǁ__iter____mutmut_11(self) -> Iterator[dict[str, np.ndarray]]:
        if self.prefetch_k <= 0:
            for text in self.stream:
                yield _encode_text(self.tokenizer, text, self.max_length)
        else:
            buf: list[dict[str, np.ndarray]] = []
            for text in self.stream:
                buf.append(_encode_text(None, text, self.max_length))
                if len(buf) >= self.prefetch_k:
                    for item in buf:
                        yield item
                    buf.clear()
            for item in buf:
                yield item

    def xǁIterableTextDatasetǁ__iter____mutmut_12(self) -> Iterator[dict[str, np.ndarray]]:
        if self.prefetch_k <= 0:
            for text in self.stream:
                yield _encode_text(self.tokenizer, text, self.max_length)
        else:
            buf: list[dict[str, np.ndarray]] = []
            for text in self.stream:
                buf.append(_encode_text(self.tokenizer, None, self.max_length))
                if len(buf) >= self.prefetch_k:
                    for item in buf:
                        yield item
                    buf.clear()
            for item in buf:
                yield item

    def xǁIterableTextDatasetǁ__iter____mutmut_13(self) -> Iterator[dict[str, np.ndarray]]:
        if self.prefetch_k <= 0:
            for text in self.stream:
                yield _encode_text(self.tokenizer, text, self.max_length)
        else:
            buf: list[dict[str, np.ndarray]] = []
            for text in self.stream:
                buf.append(_encode_text(self.tokenizer, text, None))
                if len(buf) >= self.prefetch_k:
                    for item in buf:
                        yield item
                    buf.clear()
            for item in buf:
                yield item

    def xǁIterableTextDatasetǁ__iter____mutmut_14(self) -> Iterator[dict[str, np.ndarray]]:
        if self.prefetch_k <= 0:
            for text in self.stream:
                yield _encode_text(self.tokenizer, text, self.max_length)
        else:
            buf: list[dict[str, np.ndarray]] = []
            for text in self.stream:
                buf.append(_encode_text(text, self.max_length))
                if len(buf) >= self.prefetch_k:
                    for item in buf:
                        yield item
                    buf.clear()
            for item in buf:
                yield item

    def xǁIterableTextDatasetǁ__iter____mutmut_15(self) -> Iterator[dict[str, np.ndarray]]:
        if self.prefetch_k <= 0:
            for text in self.stream:
                yield _encode_text(self.tokenizer, text, self.max_length)
        else:
            buf: list[dict[str, np.ndarray]] = []
            for text in self.stream:
                buf.append(_encode_text(self.tokenizer, self.max_length))
                if len(buf) >= self.prefetch_k:
                    for item in buf:
                        yield item
                    buf.clear()
            for item in buf:
                yield item

    def xǁIterableTextDatasetǁ__iter____mutmut_16(self) -> Iterator[dict[str, np.ndarray]]:
        if self.prefetch_k <= 0:
            for text in self.stream:
                yield _encode_text(self.tokenizer, text, self.max_length)
        else:
            buf: list[dict[str, np.ndarray]] = []
            for text in self.stream:
                buf.append(_encode_text(self.tokenizer, text, ))
                if len(buf) >= self.prefetch_k:
                    for item in buf:
                        yield item
                    buf.clear()
            for item in buf:
                yield item

    def xǁIterableTextDatasetǁ__iter____mutmut_17(self) -> Iterator[dict[str, np.ndarray]]:
        if self.prefetch_k <= 0:
            for text in self.stream:
                yield _encode_text(self.tokenizer, text, self.max_length)
        else:
            buf: list[dict[str, np.ndarray]] = []
            for text in self.stream:
                buf.append(_encode_text(self.tokenizer, text, self.max_length))
                if len(buf) > self.prefetch_k:
                    for item in buf:
                        yield item
                    buf.clear()
            for item in buf:
                yield item
    
    xǁIterableTextDatasetǁ__iter____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁIterableTextDatasetǁ__iter____mutmut_1': xǁIterableTextDatasetǁ__iter____mutmut_1, 
        'xǁIterableTextDatasetǁ__iter____mutmut_2': xǁIterableTextDatasetǁ__iter____mutmut_2, 
        'xǁIterableTextDatasetǁ__iter____mutmut_3': xǁIterableTextDatasetǁ__iter____mutmut_3, 
        'xǁIterableTextDatasetǁ__iter____mutmut_4': xǁIterableTextDatasetǁ__iter____mutmut_4, 
        'xǁIterableTextDatasetǁ__iter____mutmut_5': xǁIterableTextDatasetǁ__iter____mutmut_5, 
        'xǁIterableTextDatasetǁ__iter____mutmut_6': xǁIterableTextDatasetǁ__iter____mutmut_6, 
        'xǁIterableTextDatasetǁ__iter____mutmut_7': xǁIterableTextDatasetǁ__iter____mutmut_7, 
        'xǁIterableTextDatasetǁ__iter____mutmut_8': xǁIterableTextDatasetǁ__iter____mutmut_8, 
        'xǁIterableTextDatasetǁ__iter____mutmut_9': xǁIterableTextDatasetǁ__iter____mutmut_9, 
        'xǁIterableTextDatasetǁ__iter____mutmut_10': xǁIterableTextDatasetǁ__iter____mutmut_10, 
        'xǁIterableTextDatasetǁ__iter____mutmut_11': xǁIterableTextDatasetǁ__iter____mutmut_11, 
        'xǁIterableTextDatasetǁ__iter____mutmut_12': xǁIterableTextDatasetǁ__iter____mutmut_12, 
        'xǁIterableTextDatasetǁ__iter____mutmut_13': xǁIterableTextDatasetǁ__iter____mutmut_13, 
        'xǁIterableTextDatasetǁ__iter____mutmut_14': xǁIterableTextDatasetǁ__iter____mutmut_14, 
        'xǁIterableTextDatasetǁ__iter____mutmut_15': xǁIterableTextDatasetǁ__iter____mutmut_15, 
        'xǁIterableTextDatasetǁ__iter____mutmut_16': xǁIterableTextDatasetǁ__iter____mutmut_16, 
        'xǁIterableTextDatasetǁ__iter____mutmut_17': xǁIterableTextDatasetǁ__iter____mutmut_17
    }
    
    def __iter__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁIterableTextDatasetǁ__iter____mutmut_orig"), object.__getattribute__(self, "xǁIterableTextDatasetǁ__iter____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __iter__.__signature__ = _mutmut_signature(xǁIterableTextDatasetǁ__iter____mutmut_orig)
    xǁIterableTextDatasetǁ__iter____mutmut_orig.__name__ = 'xǁIterableTextDatasetǁ__iter__'


def x_to_hf_dataset__mutmut_orig(items: Sequence[str], tokenizer, max_length: int) -> Dataset:
    """Return a HuggingFace ``Dataset`` of tokenized texts."""
    if Dataset is None:  # pragma: no cover - dependency guard
        raise ImportError("datasets is required for to_hf_dataset")
    data = [_encode_text(tokenizer, t, max_length) for t in items]
    return Dataset.from_list(data)


def x_to_hf_dataset__mutmut_1(items: Sequence[str], tokenizer, max_length: int) -> Dataset:
    """Return a HuggingFace ``Dataset`` of tokenized texts."""
    if Dataset is not None:  # pragma: no cover - dependency guard
        raise ImportError("datasets is required for to_hf_dataset")
    data = [_encode_text(tokenizer, t, max_length) for t in items]
    return Dataset.from_list(data)


def x_to_hf_dataset__mutmut_2(items: Sequence[str], tokenizer, max_length: int) -> Dataset:
    """Return a HuggingFace ``Dataset`` of tokenized texts."""
    if Dataset is None:  # pragma: no cover - dependency guard
        raise ImportError(None)
    data = [_encode_text(tokenizer, t, max_length) for t in items]
    return Dataset.from_list(data)


def x_to_hf_dataset__mutmut_3(items: Sequence[str], tokenizer, max_length: int) -> Dataset:
    """Return a HuggingFace ``Dataset`` of tokenized texts."""
    if Dataset is None:  # pragma: no cover - dependency guard
        raise ImportError("XXdatasets is required for to_hf_datasetXX")
    data = [_encode_text(tokenizer, t, max_length) for t in items]
    return Dataset.from_list(data)


def x_to_hf_dataset__mutmut_4(items: Sequence[str], tokenizer, max_length: int) -> Dataset:
    """Return a HuggingFace ``Dataset`` of tokenized texts."""
    if Dataset is None:  # pragma: no cover - dependency guard
        raise ImportError("DATASETS IS REQUIRED FOR TO_HF_DATASET")
    data = [_encode_text(tokenizer, t, max_length) for t in items]
    return Dataset.from_list(data)


def x_to_hf_dataset__mutmut_5(items: Sequence[str], tokenizer, max_length: int) -> Dataset:
    """Return a HuggingFace ``Dataset`` of tokenized texts."""
    if Dataset is None:  # pragma: no cover - dependency guard
        raise ImportError("datasets is required for to_hf_dataset")
    data = None
    return Dataset.from_list(data)


def x_to_hf_dataset__mutmut_6(items: Sequence[str], tokenizer, max_length: int) -> Dataset:
    """Return a HuggingFace ``Dataset`` of tokenized texts."""
    if Dataset is None:  # pragma: no cover - dependency guard
        raise ImportError("datasets is required for to_hf_dataset")
    data = [_encode_text(None, t, max_length) for t in items]
    return Dataset.from_list(data)


def x_to_hf_dataset__mutmut_7(items: Sequence[str], tokenizer, max_length: int) -> Dataset:
    """Return a HuggingFace ``Dataset`` of tokenized texts."""
    if Dataset is None:  # pragma: no cover - dependency guard
        raise ImportError("datasets is required for to_hf_dataset")
    data = [_encode_text(tokenizer, None, max_length) for t in items]
    return Dataset.from_list(data)


def x_to_hf_dataset__mutmut_8(items: Sequence[str], tokenizer, max_length: int) -> Dataset:
    """Return a HuggingFace ``Dataset`` of tokenized texts."""
    if Dataset is None:  # pragma: no cover - dependency guard
        raise ImportError("datasets is required for to_hf_dataset")
    data = [_encode_text(tokenizer, t, None) for t in items]
    return Dataset.from_list(data)


def x_to_hf_dataset__mutmut_9(items: Sequence[str], tokenizer, max_length: int) -> Dataset:
    """Return a HuggingFace ``Dataset`` of tokenized texts."""
    if Dataset is None:  # pragma: no cover - dependency guard
        raise ImportError("datasets is required for to_hf_dataset")
    data = [_encode_text(t, max_length) for t in items]
    return Dataset.from_list(data)


def x_to_hf_dataset__mutmut_10(items: Sequence[str], tokenizer, max_length: int) -> Dataset:
    """Return a HuggingFace ``Dataset`` of tokenized texts."""
    if Dataset is None:  # pragma: no cover - dependency guard
        raise ImportError("datasets is required for to_hf_dataset")
    data = [_encode_text(tokenizer, max_length) for t in items]
    return Dataset.from_list(data)


def x_to_hf_dataset__mutmut_11(items: Sequence[str], tokenizer, max_length: int) -> Dataset:
    """Return a HuggingFace ``Dataset`` of tokenized texts."""
    if Dataset is None:  # pragma: no cover - dependency guard
        raise ImportError("datasets is required for to_hf_dataset")
    data = [_encode_text(tokenizer, t, ) for t in items]
    return Dataset.from_list(data)


def x_to_hf_dataset__mutmut_12(items: Sequence[str], tokenizer, max_length: int) -> Dataset:
    """Return a HuggingFace ``Dataset`` of tokenized texts."""
    if Dataset is None:  # pragma: no cover - dependency guard
        raise ImportError("datasets is required for to_hf_dataset")
    data = [_encode_text(tokenizer, t, max_length) for t in items]
    return Dataset.from_list(None)

x_to_hf_dataset__mutmut_mutants : ClassVar[MutantDict] = {
'x_to_hf_dataset__mutmut_1': x_to_hf_dataset__mutmut_1, 
    'x_to_hf_dataset__mutmut_2': x_to_hf_dataset__mutmut_2, 
    'x_to_hf_dataset__mutmut_3': x_to_hf_dataset__mutmut_3, 
    'x_to_hf_dataset__mutmut_4': x_to_hf_dataset__mutmut_4, 
    'x_to_hf_dataset__mutmut_5': x_to_hf_dataset__mutmut_5, 
    'x_to_hf_dataset__mutmut_6': x_to_hf_dataset__mutmut_6, 
    'x_to_hf_dataset__mutmut_7': x_to_hf_dataset__mutmut_7, 
    'x_to_hf_dataset__mutmut_8': x_to_hf_dataset__mutmut_8, 
    'x_to_hf_dataset__mutmut_9': x_to_hf_dataset__mutmut_9, 
    'x_to_hf_dataset__mutmut_10': x_to_hf_dataset__mutmut_10, 
    'x_to_hf_dataset__mutmut_11': x_to_hf_dataset__mutmut_11, 
    'x_to_hf_dataset__mutmut_12': x_to_hf_dataset__mutmut_12
}

def to_hf_dataset(*args, **kwargs):
    result = _mutmut_trampoline(x_to_hf_dataset__mutmut_orig, x_to_hf_dataset__mutmut_mutants, args, kwargs)
    return result 

to_hf_dataset.__signature__ = _mutmut_signature(x_to_hf_dataset__mutmut_orig)
x_to_hf_dataset__mutmut_orig.__name__ = 'x_to_hf_dataset'


def x_compute_dataset_hash__mutmut_orig(items: Iterable[str]) -> str:
    """Compute a stable SHA256 hash for a collection of text samples."""

    digest = hashlib.sha256()
    for text in items:
        digest.update(text.encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()


def x_compute_dataset_hash__mutmut_1(items: Iterable[str]) -> str:
    """Compute a stable SHA256 hash for a collection of text samples."""

    digest = None
    for text in items:
        digest.update(text.encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()


def x_compute_dataset_hash__mutmut_2(items: Iterable[str]) -> str:
    """Compute a stable SHA256 hash for a collection of text samples."""

    digest = hashlib.sha256()
    for text in items:
        digest.update(None)
        digest.update(b"\n")
    return digest.hexdigest()


def x_compute_dataset_hash__mutmut_3(items: Iterable[str]) -> str:
    """Compute a stable SHA256 hash for a collection of text samples."""

    digest = hashlib.sha256()
    for text in items:
        digest.update(text.encode(None))
        digest.update(b"\n")
    return digest.hexdigest()


def x_compute_dataset_hash__mutmut_4(items: Iterable[str]) -> str:
    """Compute a stable SHA256 hash for a collection of text samples."""

    digest = hashlib.sha256()
    for text in items:
        digest.update(text.encode("XXutf-8XX"))
        digest.update(b"\n")
    return digest.hexdigest()


def x_compute_dataset_hash__mutmut_5(items: Iterable[str]) -> str:
    """Compute a stable SHA256 hash for a collection of text samples."""

    digest = hashlib.sha256()
    for text in items:
        digest.update(text.encode("UTF-8"))
        digest.update(b"\n")
    return digest.hexdigest()


def x_compute_dataset_hash__mutmut_6(items: Iterable[str]) -> str:
    """Compute a stable SHA256 hash for a collection of text samples."""

    digest = hashlib.sha256()
    for text in items:
        digest.update(text.encode("utf-8"))
        digest.update(None)
    return digest.hexdigest()


def x_compute_dataset_hash__mutmut_7(items: Iterable[str]) -> str:
    """Compute a stable SHA256 hash for a collection of text samples."""

    digest = hashlib.sha256()
    for text in items:
        digest.update(text.encode("utf-8"))
        digest.update(b"XX\nXX")
    return digest.hexdigest()

x_compute_dataset_hash__mutmut_mutants : ClassVar[MutantDict] = {
'x_compute_dataset_hash__mutmut_1': x_compute_dataset_hash__mutmut_1, 
    'x_compute_dataset_hash__mutmut_2': x_compute_dataset_hash__mutmut_2, 
    'x_compute_dataset_hash__mutmut_3': x_compute_dataset_hash__mutmut_3, 
    'x_compute_dataset_hash__mutmut_4': x_compute_dataset_hash__mutmut_4, 
    'x_compute_dataset_hash__mutmut_5': x_compute_dataset_hash__mutmut_5, 
    'x_compute_dataset_hash__mutmut_6': x_compute_dataset_hash__mutmut_6, 
    'x_compute_dataset_hash__mutmut_7': x_compute_dataset_hash__mutmut_7
}

def compute_dataset_hash(*args, **kwargs):
    result = _mutmut_trampoline(x_compute_dataset_hash__mutmut_orig, x_compute_dataset_hash__mutmut_mutants, args, kwargs)
    return result 

compute_dataset_hash.__signature__ = _mutmut_signature(x_compute_dataset_hash__mutmut_orig)
x_compute_dataset_hash__mutmut_orig.__name__ = 'x_compute_dataset_hash'


def x_cache_texts__mutmut_orig(
    items: Sequence[str],
    cache_dir: str | Path,
    *,
    name: str = "dataset",
    include_hash: bool = True,
) -> Path:
    """Persist raw texts to a cache directory with a hash-derived filename."""

    cache_root = Path(cache_dir)
    cache_root.mkdir(parents=True, exist_ok=True)
    ds_hash = compute_dataset_hash(items) if include_hash else "nohash"
    target = cache_root / f"{name}-{ds_hash}.jsonl"
    with target.open("w", encoding="utf-8") as fh:
        for text in items:
            fh.write(json.dumps({"text": text}) + "\n")
    return target


def x_cache_texts__mutmut_1(
    items: Sequence[str],
    cache_dir: str | Path,
    *,
    name: str = "XXdatasetXX",
    include_hash: bool = True,
) -> Path:
    """Persist raw texts to a cache directory with a hash-derived filename."""

    cache_root = Path(cache_dir)
    cache_root.mkdir(parents=True, exist_ok=True)
    ds_hash = compute_dataset_hash(items) if include_hash else "nohash"
    target = cache_root / f"{name}-{ds_hash}.jsonl"
    with target.open("w", encoding="utf-8") as fh:
        for text in items:
            fh.write(json.dumps({"text": text}) + "\n")
    return target


def x_cache_texts__mutmut_2(
    items: Sequence[str],
    cache_dir: str | Path,
    *,
    name: str = "DATASET",
    include_hash: bool = True,
) -> Path:
    """Persist raw texts to a cache directory with a hash-derived filename."""

    cache_root = Path(cache_dir)
    cache_root.mkdir(parents=True, exist_ok=True)
    ds_hash = compute_dataset_hash(items) if include_hash else "nohash"
    target = cache_root / f"{name}-{ds_hash}.jsonl"
    with target.open("w", encoding="utf-8") as fh:
        for text in items:
            fh.write(json.dumps({"text": text}) + "\n")
    return target


def x_cache_texts__mutmut_3(
    items: Sequence[str],
    cache_dir: str | Path,
    *,
    name: str = "dataset",
    include_hash: bool = False,
) -> Path:
    """Persist raw texts to a cache directory with a hash-derived filename."""

    cache_root = Path(cache_dir)
    cache_root.mkdir(parents=True, exist_ok=True)
    ds_hash = compute_dataset_hash(items) if include_hash else "nohash"
    target = cache_root / f"{name}-{ds_hash}.jsonl"
    with target.open("w", encoding="utf-8") as fh:
        for text in items:
            fh.write(json.dumps({"text": text}) + "\n")
    return target


def x_cache_texts__mutmut_4(
    items: Sequence[str],
    cache_dir: str | Path,
    *,
    name: str = "dataset",
    include_hash: bool = True,
) -> Path:
    """Persist raw texts to a cache directory with a hash-derived filename."""

    cache_root = None
    cache_root.mkdir(parents=True, exist_ok=True)
    ds_hash = compute_dataset_hash(items) if include_hash else "nohash"
    target = cache_root / f"{name}-{ds_hash}.jsonl"
    with target.open("w", encoding="utf-8") as fh:
        for text in items:
            fh.write(json.dumps({"text": text}) + "\n")
    return target


def x_cache_texts__mutmut_5(
    items: Sequence[str],
    cache_dir: str | Path,
    *,
    name: str = "dataset",
    include_hash: bool = True,
) -> Path:
    """Persist raw texts to a cache directory with a hash-derived filename."""

    cache_root = Path(None)
    cache_root.mkdir(parents=True, exist_ok=True)
    ds_hash = compute_dataset_hash(items) if include_hash else "nohash"
    target = cache_root / f"{name}-{ds_hash}.jsonl"
    with target.open("w", encoding="utf-8") as fh:
        for text in items:
            fh.write(json.dumps({"text": text}) + "\n")
    return target


def x_cache_texts__mutmut_6(
    items: Sequence[str],
    cache_dir: str | Path,
    *,
    name: str = "dataset",
    include_hash: bool = True,
) -> Path:
    """Persist raw texts to a cache directory with a hash-derived filename."""

    cache_root = Path(cache_dir)
    cache_root.mkdir(parents=None, exist_ok=True)
    ds_hash = compute_dataset_hash(items) if include_hash else "nohash"
    target = cache_root / f"{name}-{ds_hash}.jsonl"
    with target.open("w", encoding="utf-8") as fh:
        for text in items:
            fh.write(json.dumps({"text": text}) + "\n")
    return target


def x_cache_texts__mutmut_7(
    items: Sequence[str],
    cache_dir: str | Path,
    *,
    name: str = "dataset",
    include_hash: bool = True,
) -> Path:
    """Persist raw texts to a cache directory with a hash-derived filename."""

    cache_root = Path(cache_dir)
    cache_root.mkdir(parents=True, exist_ok=None)
    ds_hash = compute_dataset_hash(items) if include_hash else "nohash"
    target = cache_root / f"{name}-{ds_hash}.jsonl"
    with target.open("w", encoding="utf-8") as fh:
        for text in items:
            fh.write(json.dumps({"text": text}) + "\n")
    return target


def x_cache_texts__mutmut_8(
    items: Sequence[str],
    cache_dir: str | Path,
    *,
    name: str = "dataset",
    include_hash: bool = True,
) -> Path:
    """Persist raw texts to a cache directory with a hash-derived filename."""

    cache_root = Path(cache_dir)
    cache_root.mkdir(exist_ok=True)
    ds_hash = compute_dataset_hash(items) if include_hash else "nohash"
    target = cache_root / f"{name}-{ds_hash}.jsonl"
    with target.open("w", encoding="utf-8") as fh:
        for text in items:
            fh.write(json.dumps({"text": text}) + "\n")
    return target


def x_cache_texts__mutmut_9(
    items: Sequence[str],
    cache_dir: str | Path,
    *,
    name: str = "dataset",
    include_hash: bool = True,
) -> Path:
    """Persist raw texts to a cache directory with a hash-derived filename."""

    cache_root = Path(cache_dir)
    cache_root.mkdir(parents=True, )
    ds_hash = compute_dataset_hash(items) if include_hash else "nohash"
    target = cache_root / f"{name}-{ds_hash}.jsonl"
    with target.open("w", encoding="utf-8") as fh:
        for text in items:
            fh.write(json.dumps({"text": text}) + "\n")
    return target


def x_cache_texts__mutmut_10(
    items: Sequence[str],
    cache_dir: str | Path,
    *,
    name: str = "dataset",
    include_hash: bool = True,
) -> Path:
    """Persist raw texts to a cache directory with a hash-derived filename."""

    cache_root = Path(cache_dir)
    cache_root.mkdir(parents=False, exist_ok=True)
    ds_hash = compute_dataset_hash(items) if include_hash else "nohash"
    target = cache_root / f"{name}-{ds_hash}.jsonl"
    with target.open("w", encoding="utf-8") as fh:
        for text in items:
            fh.write(json.dumps({"text": text}) + "\n")
    return target


def x_cache_texts__mutmut_11(
    items: Sequence[str],
    cache_dir: str | Path,
    *,
    name: str = "dataset",
    include_hash: bool = True,
) -> Path:
    """Persist raw texts to a cache directory with a hash-derived filename."""

    cache_root = Path(cache_dir)
    cache_root.mkdir(parents=True, exist_ok=False)
    ds_hash = compute_dataset_hash(items) if include_hash else "nohash"
    target = cache_root / f"{name}-{ds_hash}.jsonl"
    with target.open("w", encoding="utf-8") as fh:
        for text in items:
            fh.write(json.dumps({"text": text}) + "\n")
    return target


def x_cache_texts__mutmut_12(
    items: Sequence[str],
    cache_dir: str | Path,
    *,
    name: str = "dataset",
    include_hash: bool = True,
) -> Path:
    """Persist raw texts to a cache directory with a hash-derived filename."""

    cache_root = Path(cache_dir)
    cache_root.mkdir(parents=True, exist_ok=True)
    ds_hash = None
    target = cache_root / f"{name}-{ds_hash}.jsonl"
    with target.open("w", encoding="utf-8") as fh:
        for text in items:
            fh.write(json.dumps({"text": text}) + "\n")
    return target


def x_cache_texts__mutmut_13(
    items: Sequence[str],
    cache_dir: str | Path,
    *,
    name: str = "dataset",
    include_hash: bool = True,
) -> Path:
    """Persist raw texts to a cache directory with a hash-derived filename."""

    cache_root = Path(cache_dir)
    cache_root.mkdir(parents=True, exist_ok=True)
    ds_hash = compute_dataset_hash(None) if include_hash else "nohash"
    target = cache_root / f"{name}-{ds_hash}.jsonl"
    with target.open("w", encoding="utf-8") as fh:
        for text in items:
            fh.write(json.dumps({"text": text}) + "\n")
    return target


def x_cache_texts__mutmut_14(
    items: Sequence[str],
    cache_dir: str | Path,
    *,
    name: str = "dataset",
    include_hash: bool = True,
) -> Path:
    """Persist raw texts to a cache directory with a hash-derived filename."""

    cache_root = Path(cache_dir)
    cache_root.mkdir(parents=True, exist_ok=True)
    ds_hash = compute_dataset_hash(items) if include_hash else "XXnohashXX"
    target = cache_root / f"{name}-{ds_hash}.jsonl"
    with target.open("w", encoding="utf-8") as fh:
        for text in items:
            fh.write(json.dumps({"text": text}) + "\n")
    return target


def x_cache_texts__mutmut_15(
    items: Sequence[str],
    cache_dir: str | Path,
    *,
    name: str = "dataset",
    include_hash: bool = True,
) -> Path:
    """Persist raw texts to a cache directory with a hash-derived filename."""

    cache_root = Path(cache_dir)
    cache_root.mkdir(parents=True, exist_ok=True)
    ds_hash = compute_dataset_hash(items) if include_hash else "NOHASH"
    target = cache_root / f"{name}-{ds_hash}.jsonl"
    with target.open("w", encoding="utf-8") as fh:
        for text in items:
            fh.write(json.dumps({"text": text}) + "\n")
    return target


def x_cache_texts__mutmut_16(
    items: Sequence[str],
    cache_dir: str | Path,
    *,
    name: str = "dataset",
    include_hash: bool = True,
) -> Path:
    """Persist raw texts to a cache directory with a hash-derived filename."""

    cache_root = Path(cache_dir)
    cache_root.mkdir(parents=True, exist_ok=True)
    ds_hash = compute_dataset_hash(items) if include_hash else "nohash"
    target = None
    with target.open("w", encoding="utf-8") as fh:
        for text in items:
            fh.write(json.dumps({"text": text}) + "\n")
    return target


def x_cache_texts__mutmut_17(
    items: Sequence[str],
    cache_dir: str | Path,
    *,
    name: str = "dataset",
    include_hash: bool = True,
) -> Path:
    """Persist raw texts to a cache directory with a hash-derived filename."""

    cache_root = Path(cache_dir)
    cache_root.mkdir(parents=True, exist_ok=True)
    ds_hash = compute_dataset_hash(items) if include_hash else "nohash"
    target = cache_root * f"{name}-{ds_hash}.jsonl"
    with target.open("w", encoding="utf-8") as fh:
        for text in items:
            fh.write(json.dumps({"text": text}) + "\n")
    return target


def x_cache_texts__mutmut_18(
    items: Sequence[str],
    cache_dir: str | Path,
    *,
    name: str = "dataset",
    include_hash: bool = True,
) -> Path:
    """Persist raw texts to a cache directory with a hash-derived filename."""

    cache_root = Path(cache_dir)
    cache_root.mkdir(parents=True, exist_ok=True)
    ds_hash = compute_dataset_hash(items) if include_hash else "nohash"
    target = cache_root / f"{name}-{ds_hash}.jsonl"
    with target.open(None, encoding="utf-8") as fh:
        for text in items:
            fh.write(json.dumps({"text": text}) + "\n")
    return target


def x_cache_texts__mutmut_19(
    items: Sequence[str],
    cache_dir: str | Path,
    *,
    name: str = "dataset",
    include_hash: bool = True,
) -> Path:
    """Persist raw texts to a cache directory with a hash-derived filename."""

    cache_root = Path(cache_dir)
    cache_root.mkdir(parents=True, exist_ok=True)
    ds_hash = compute_dataset_hash(items) if include_hash else "nohash"
    target = cache_root / f"{name}-{ds_hash}.jsonl"
    with target.open("w", encoding=None) as fh:
        for text in items:
            fh.write(json.dumps({"text": text}) + "\n")
    return target


def x_cache_texts__mutmut_20(
    items: Sequence[str],
    cache_dir: str | Path,
    *,
    name: str = "dataset",
    include_hash: bool = True,
) -> Path:
    """Persist raw texts to a cache directory with a hash-derived filename."""

    cache_root = Path(cache_dir)
    cache_root.mkdir(parents=True, exist_ok=True)
    ds_hash = compute_dataset_hash(items) if include_hash else "nohash"
    target = cache_root / f"{name}-{ds_hash}.jsonl"
    with target.open(encoding="utf-8") as fh:
        for text in items:
            fh.write(json.dumps({"text": text}) + "\n")
    return target


def x_cache_texts__mutmut_21(
    items: Sequence[str],
    cache_dir: str | Path,
    *,
    name: str = "dataset",
    include_hash: bool = True,
) -> Path:
    """Persist raw texts to a cache directory with a hash-derived filename."""

    cache_root = Path(cache_dir)
    cache_root.mkdir(parents=True, exist_ok=True)
    ds_hash = compute_dataset_hash(items) if include_hash else "nohash"
    target = cache_root / f"{name}-{ds_hash}.jsonl"
    with target.open("w", ) as fh:
        for text in items:
            fh.write(json.dumps({"text": text}) + "\n")
    return target


def x_cache_texts__mutmut_22(
    items: Sequence[str],
    cache_dir: str | Path,
    *,
    name: str = "dataset",
    include_hash: bool = True,
) -> Path:
    """Persist raw texts to a cache directory with a hash-derived filename."""

    cache_root = Path(cache_dir)
    cache_root.mkdir(parents=True, exist_ok=True)
    ds_hash = compute_dataset_hash(items) if include_hash else "nohash"
    target = cache_root / f"{name}-{ds_hash}.jsonl"
    with target.open("XXwXX", encoding="utf-8") as fh:
        for text in items:
            fh.write(json.dumps({"text": text}) + "\n")
    return target


def x_cache_texts__mutmut_23(
    items: Sequence[str],
    cache_dir: str | Path,
    *,
    name: str = "dataset",
    include_hash: bool = True,
) -> Path:
    """Persist raw texts to a cache directory with a hash-derived filename."""

    cache_root = Path(cache_dir)
    cache_root.mkdir(parents=True, exist_ok=True)
    ds_hash = compute_dataset_hash(items) if include_hash else "nohash"
    target = cache_root / f"{name}-{ds_hash}.jsonl"
    with target.open("W", encoding="utf-8") as fh:
        for text in items:
            fh.write(json.dumps({"text": text}) + "\n")
    return target


def x_cache_texts__mutmut_24(
    items: Sequence[str],
    cache_dir: str | Path,
    *,
    name: str = "dataset",
    include_hash: bool = True,
) -> Path:
    """Persist raw texts to a cache directory with a hash-derived filename."""

    cache_root = Path(cache_dir)
    cache_root.mkdir(parents=True, exist_ok=True)
    ds_hash = compute_dataset_hash(items) if include_hash else "nohash"
    target = cache_root / f"{name}-{ds_hash}.jsonl"
    with target.open("w", encoding="XXutf-8XX") as fh:
        for text in items:
            fh.write(json.dumps({"text": text}) + "\n")
    return target


def x_cache_texts__mutmut_25(
    items: Sequence[str],
    cache_dir: str | Path,
    *,
    name: str = "dataset",
    include_hash: bool = True,
) -> Path:
    """Persist raw texts to a cache directory with a hash-derived filename."""

    cache_root = Path(cache_dir)
    cache_root.mkdir(parents=True, exist_ok=True)
    ds_hash = compute_dataset_hash(items) if include_hash else "nohash"
    target = cache_root / f"{name}-{ds_hash}.jsonl"
    with target.open("w", encoding="UTF-8") as fh:
        for text in items:
            fh.write(json.dumps({"text": text}) + "\n")
    return target


def x_cache_texts__mutmut_26(
    items: Sequence[str],
    cache_dir: str | Path,
    *,
    name: str = "dataset",
    include_hash: bool = True,
) -> Path:
    """Persist raw texts to a cache directory with a hash-derived filename."""

    cache_root = Path(cache_dir)
    cache_root.mkdir(parents=True, exist_ok=True)
    ds_hash = compute_dataset_hash(items) if include_hash else "nohash"
    target = cache_root / f"{name}-{ds_hash}.jsonl"
    with target.open("w", encoding="utf-8") as fh:
        for text in items:
            fh.write(None)
    return target


def x_cache_texts__mutmut_27(
    items: Sequence[str],
    cache_dir: str | Path,
    *,
    name: str = "dataset",
    include_hash: bool = True,
) -> Path:
    """Persist raw texts to a cache directory with a hash-derived filename."""

    cache_root = Path(cache_dir)
    cache_root.mkdir(parents=True, exist_ok=True)
    ds_hash = compute_dataset_hash(items) if include_hash else "nohash"
    target = cache_root / f"{name}-{ds_hash}.jsonl"
    with target.open("w", encoding="utf-8") as fh:
        for text in items:
            fh.write(json.dumps({"text": text}) - "\n")
    return target


def x_cache_texts__mutmut_28(
    items: Sequence[str],
    cache_dir: str | Path,
    *,
    name: str = "dataset",
    include_hash: bool = True,
) -> Path:
    """Persist raw texts to a cache directory with a hash-derived filename."""

    cache_root = Path(cache_dir)
    cache_root.mkdir(parents=True, exist_ok=True)
    ds_hash = compute_dataset_hash(items) if include_hash else "nohash"
    target = cache_root / f"{name}-{ds_hash}.jsonl"
    with target.open("w", encoding="utf-8") as fh:
        for text in items:
            fh.write(json.dumps(None) + "\n")
    return target


def x_cache_texts__mutmut_29(
    items: Sequence[str],
    cache_dir: str | Path,
    *,
    name: str = "dataset",
    include_hash: bool = True,
) -> Path:
    """Persist raw texts to a cache directory with a hash-derived filename."""

    cache_root = Path(cache_dir)
    cache_root.mkdir(parents=True, exist_ok=True)
    ds_hash = compute_dataset_hash(items) if include_hash else "nohash"
    target = cache_root / f"{name}-{ds_hash}.jsonl"
    with target.open("w", encoding="utf-8") as fh:
        for text in items:
            fh.write(json.dumps({"XXtextXX": text}) + "\n")
    return target


def x_cache_texts__mutmut_30(
    items: Sequence[str],
    cache_dir: str | Path,
    *,
    name: str = "dataset",
    include_hash: bool = True,
) -> Path:
    """Persist raw texts to a cache directory with a hash-derived filename."""

    cache_root = Path(cache_dir)
    cache_root.mkdir(parents=True, exist_ok=True)
    ds_hash = compute_dataset_hash(items) if include_hash else "nohash"
    target = cache_root / f"{name}-{ds_hash}.jsonl"
    with target.open("w", encoding="utf-8") as fh:
        for text in items:
            fh.write(json.dumps({"TEXT": text}) + "\n")
    return target


def x_cache_texts__mutmut_31(
    items: Sequence[str],
    cache_dir: str | Path,
    *,
    name: str = "dataset",
    include_hash: bool = True,
) -> Path:
    """Persist raw texts to a cache directory with a hash-derived filename."""

    cache_root = Path(cache_dir)
    cache_root.mkdir(parents=True, exist_ok=True)
    ds_hash = compute_dataset_hash(items) if include_hash else "nohash"
    target = cache_root / f"{name}-{ds_hash}.jsonl"
    with target.open("w", encoding="utf-8") as fh:
        for text in items:
            fh.write(json.dumps({"text": text}) + "XX\nXX")
    return target

x_cache_texts__mutmut_mutants : ClassVar[MutantDict] = {
'x_cache_texts__mutmut_1': x_cache_texts__mutmut_1, 
    'x_cache_texts__mutmut_2': x_cache_texts__mutmut_2, 
    'x_cache_texts__mutmut_3': x_cache_texts__mutmut_3, 
    'x_cache_texts__mutmut_4': x_cache_texts__mutmut_4, 
    'x_cache_texts__mutmut_5': x_cache_texts__mutmut_5, 
    'x_cache_texts__mutmut_6': x_cache_texts__mutmut_6, 
    'x_cache_texts__mutmut_7': x_cache_texts__mutmut_7, 
    'x_cache_texts__mutmut_8': x_cache_texts__mutmut_8, 
    'x_cache_texts__mutmut_9': x_cache_texts__mutmut_9, 
    'x_cache_texts__mutmut_10': x_cache_texts__mutmut_10, 
    'x_cache_texts__mutmut_11': x_cache_texts__mutmut_11, 
    'x_cache_texts__mutmut_12': x_cache_texts__mutmut_12, 
    'x_cache_texts__mutmut_13': x_cache_texts__mutmut_13, 
    'x_cache_texts__mutmut_14': x_cache_texts__mutmut_14, 
    'x_cache_texts__mutmut_15': x_cache_texts__mutmut_15, 
    'x_cache_texts__mutmut_16': x_cache_texts__mutmut_16, 
    'x_cache_texts__mutmut_17': x_cache_texts__mutmut_17, 
    'x_cache_texts__mutmut_18': x_cache_texts__mutmut_18, 
    'x_cache_texts__mutmut_19': x_cache_texts__mutmut_19, 
    'x_cache_texts__mutmut_20': x_cache_texts__mutmut_20, 
    'x_cache_texts__mutmut_21': x_cache_texts__mutmut_21, 
    'x_cache_texts__mutmut_22': x_cache_texts__mutmut_22, 
    'x_cache_texts__mutmut_23': x_cache_texts__mutmut_23, 
    'x_cache_texts__mutmut_24': x_cache_texts__mutmut_24, 
    'x_cache_texts__mutmut_25': x_cache_texts__mutmut_25, 
    'x_cache_texts__mutmut_26': x_cache_texts__mutmut_26, 
    'x_cache_texts__mutmut_27': x_cache_texts__mutmut_27, 
    'x_cache_texts__mutmut_28': x_cache_texts__mutmut_28, 
    'x_cache_texts__mutmut_29': x_cache_texts__mutmut_29, 
    'x_cache_texts__mutmut_30': x_cache_texts__mutmut_30, 
    'x_cache_texts__mutmut_31': x_cache_texts__mutmut_31
}

def cache_texts(*args, **kwargs):
    result = _mutmut_trampoline(x_cache_texts__mutmut_orig, x_cache_texts__mutmut_mutants, args, kwargs)
    return result 

cache_texts.__signature__ = _mutmut_signature(x_cache_texts__mutmut_orig)
x_cache_texts__mutmut_orig.__name__ = 'x_cache_texts'


__all__ = [
    "Dataset",
    "IterableTextDataset",
    "TextDataset",
    "cache_texts",
    "compute_dataset_hash",
    "to_hf_dataset",
]
