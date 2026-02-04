"""
App Module

This module provides functionality for app.

Usage:
    from api.app import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations
import logging
logger = logging.getLogger(__name__)
"""FastAPI application exposing health and text generation endpoints."""


import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from tokenizers import Tokenizer
from tokenizers.models import WordLevel
from tokenizers.pre_tokenizers import Whitespace

import torch
from codex_ml.security import DenylistEnforcer, DenylistViolation
from src.tokenization.loader import load_tokenizer
from transformers import (
    AutoModelForCausalLM,
    GPT2Config,
    PreTrainedTokenizerBase,
    PreTrainedTokenizerFast,
)

app = FastAPI(title="codex", version="0.2.0")

_DEFAULT_CACHE_DIR = os.environ.get("CODEX_TOKENIZER_CACHE", "artifacts/tokenizer_cache")
_DEFAULT_MODEL_NAME = os.environ.get("CODEX_MODEL_NAME")
_DEFAULT_TOKENIZER_FILE = os.environ.get("CODEX_TOKENIZER_FILE")
_ALLOW_REMOTE = os.environ.get("CODEX_ALLOW_REMOTE", "0").lower() in {"1", "true", "on", "yes"}
_MAX_NEW_TOKENS = int(os.environ.get("CODEX_MAX_NEW_TOKENS", "32"))
_RUNTIME_MODEL: AutoModelForCausalLM | None = None
_RUNTIME_TOKENIZER: PreTrainedTokenizerBase | None = None
_RUNTIME_DENYLIST: DenylistEnforcer | None = None
PAD_TOKEN = "[PAD]"  # nosec B105 - conventional tokenizer pad token
UNK_TOKEN = "[UNK]"  # nosec B105,B106 - conventional unknown token marker
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


class PredictRequest(BaseModel):
    """Request schema for the `/predict` endpoint."""

    prompt: str


class PredictResponse(BaseModel):
    """Response schema for the `/predict` endpoint."""

    output: str


@lru_cache
def _denylist_cached() -> DenylistEnforcer:
    return DenylistEnforcer.from_yaml(Path("policies/denylist.yaml"))


def x__fallback_tokenizer__mutmut_orig() -> PreTrainedTokenizerFast:
    tokenizer_obj = Tokenizer(WordLevel({PAD_TOKEN: 0, UNK_TOKEN: 1, "hello": 2, "world": 3}))
    tokenizer_obj.pre_tokenizer = Whitespace()
    tokenizer = PreTrainedTokenizerFast(
        tokenizer_object=tokenizer_obj, pad_token=PAD_TOKEN, unk_token=UNK_TOKEN
    )
    tokenizer.pad_token = PAD_TOKEN
    tokenizer.eos_token = tokenizer.eos_token or tokenizer.pad_token
    return tokenizer


def x__fallback_tokenizer__mutmut_1() -> PreTrainedTokenizerFast:
    tokenizer_obj = None
    tokenizer_obj.pre_tokenizer = Whitespace()
    tokenizer = PreTrainedTokenizerFast(
        tokenizer_object=tokenizer_obj, pad_token=PAD_TOKEN, unk_token=UNK_TOKEN
    )
    tokenizer.pad_token = PAD_TOKEN
    tokenizer.eos_token = tokenizer.eos_token or tokenizer.pad_token
    return tokenizer


def x__fallback_tokenizer__mutmut_2() -> PreTrainedTokenizerFast:
    tokenizer_obj = Tokenizer(None)
    tokenizer_obj.pre_tokenizer = Whitespace()
    tokenizer = PreTrainedTokenizerFast(
        tokenizer_object=tokenizer_obj, pad_token=PAD_TOKEN, unk_token=UNK_TOKEN
    )
    tokenizer.pad_token = PAD_TOKEN
    tokenizer.eos_token = tokenizer.eos_token or tokenizer.pad_token
    return tokenizer


def x__fallback_tokenizer__mutmut_3() -> PreTrainedTokenizerFast:
    tokenizer_obj = Tokenizer(WordLevel(None))
    tokenizer_obj.pre_tokenizer = Whitespace()
    tokenizer = PreTrainedTokenizerFast(
        tokenizer_object=tokenizer_obj, pad_token=PAD_TOKEN, unk_token=UNK_TOKEN
    )
    tokenizer.pad_token = PAD_TOKEN
    tokenizer.eos_token = tokenizer.eos_token or tokenizer.pad_token
    return tokenizer


def x__fallback_tokenizer__mutmut_4() -> PreTrainedTokenizerFast:
    tokenizer_obj = Tokenizer(WordLevel({PAD_TOKEN: 1, UNK_TOKEN: 1, "hello": 2, "world": 3}))
    tokenizer_obj.pre_tokenizer = Whitespace()
    tokenizer = PreTrainedTokenizerFast(
        tokenizer_object=tokenizer_obj, pad_token=PAD_TOKEN, unk_token=UNK_TOKEN
    )
    tokenizer.pad_token = PAD_TOKEN
    tokenizer.eos_token = tokenizer.eos_token or tokenizer.pad_token
    return tokenizer


def x__fallback_tokenizer__mutmut_5() -> PreTrainedTokenizerFast:
    tokenizer_obj = Tokenizer(WordLevel({PAD_TOKEN: 0, UNK_TOKEN: 2, "hello": 2, "world": 3}))
    tokenizer_obj.pre_tokenizer = Whitespace()
    tokenizer = PreTrainedTokenizerFast(
        tokenizer_object=tokenizer_obj, pad_token=PAD_TOKEN, unk_token=UNK_TOKEN
    )
    tokenizer.pad_token = PAD_TOKEN
    tokenizer.eos_token = tokenizer.eos_token or tokenizer.pad_token
    return tokenizer


def x__fallback_tokenizer__mutmut_6() -> PreTrainedTokenizerFast:
    tokenizer_obj = Tokenizer(WordLevel({PAD_TOKEN: 0, UNK_TOKEN: 1, "XXhelloXX": 2, "world": 3}))
    tokenizer_obj.pre_tokenizer = Whitespace()
    tokenizer = PreTrainedTokenizerFast(
        tokenizer_object=tokenizer_obj, pad_token=PAD_TOKEN, unk_token=UNK_TOKEN
    )
    tokenizer.pad_token = PAD_TOKEN
    tokenizer.eos_token = tokenizer.eos_token or tokenizer.pad_token
    return tokenizer


def x__fallback_tokenizer__mutmut_7() -> PreTrainedTokenizerFast:
    tokenizer_obj = Tokenizer(WordLevel({PAD_TOKEN: 0, UNK_TOKEN: 1, "HELLO": 2, "world": 3}))
    tokenizer_obj.pre_tokenizer = Whitespace()
    tokenizer = PreTrainedTokenizerFast(
        tokenizer_object=tokenizer_obj, pad_token=PAD_TOKEN, unk_token=UNK_TOKEN
    )
    tokenizer.pad_token = PAD_TOKEN
    tokenizer.eos_token = tokenizer.eos_token or tokenizer.pad_token
    return tokenizer


def x__fallback_tokenizer__mutmut_8() -> PreTrainedTokenizerFast:
    tokenizer_obj = Tokenizer(WordLevel({PAD_TOKEN: 0, UNK_TOKEN: 1, "hello": 3, "world": 3}))
    tokenizer_obj.pre_tokenizer = Whitespace()
    tokenizer = PreTrainedTokenizerFast(
        tokenizer_object=tokenizer_obj, pad_token=PAD_TOKEN, unk_token=UNK_TOKEN
    )
    tokenizer.pad_token = PAD_TOKEN
    tokenizer.eos_token = tokenizer.eos_token or tokenizer.pad_token
    return tokenizer


def x__fallback_tokenizer__mutmut_9() -> PreTrainedTokenizerFast:
    tokenizer_obj = Tokenizer(WordLevel({PAD_TOKEN: 0, UNK_TOKEN: 1, "hello": 2, "XXworldXX": 3}))
    tokenizer_obj.pre_tokenizer = Whitespace()
    tokenizer = PreTrainedTokenizerFast(
        tokenizer_object=tokenizer_obj, pad_token=PAD_TOKEN, unk_token=UNK_TOKEN
    )
    tokenizer.pad_token = PAD_TOKEN
    tokenizer.eos_token = tokenizer.eos_token or tokenizer.pad_token
    return tokenizer


def x__fallback_tokenizer__mutmut_10() -> PreTrainedTokenizerFast:
    tokenizer_obj = Tokenizer(WordLevel({PAD_TOKEN: 0, UNK_TOKEN: 1, "hello": 2, "WORLD": 3}))
    tokenizer_obj.pre_tokenizer = Whitespace()
    tokenizer = PreTrainedTokenizerFast(
        tokenizer_object=tokenizer_obj, pad_token=PAD_TOKEN, unk_token=UNK_TOKEN
    )
    tokenizer.pad_token = PAD_TOKEN
    tokenizer.eos_token = tokenizer.eos_token or tokenizer.pad_token
    return tokenizer


def x__fallback_tokenizer__mutmut_11() -> PreTrainedTokenizerFast:
    tokenizer_obj = Tokenizer(WordLevel({PAD_TOKEN: 0, UNK_TOKEN: 1, "hello": 2, "world": 4}))
    tokenizer_obj.pre_tokenizer = Whitespace()
    tokenizer = PreTrainedTokenizerFast(
        tokenizer_object=tokenizer_obj, pad_token=PAD_TOKEN, unk_token=UNK_TOKEN
    )
    tokenizer.pad_token = PAD_TOKEN
    tokenizer.eos_token = tokenizer.eos_token or tokenizer.pad_token
    return tokenizer


def x__fallback_tokenizer__mutmut_12() -> PreTrainedTokenizerFast:
    tokenizer_obj = Tokenizer(WordLevel({PAD_TOKEN: 0, UNK_TOKEN: 1, "hello": 2, "world": 3}))
    tokenizer_obj.pre_tokenizer = None
    tokenizer = PreTrainedTokenizerFast(
        tokenizer_object=tokenizer_obj, pad_token=PAD_TOKEN, unk_token=UNK_TOKEN
    )
    tokenizer.pad_token = PAD_TOKEN
    tokenizer.eos_token = tokenizer.eos_token or tokenizer.pad_token
    return tokenizer


def x__fallback_tokenizer__mutmut_13() -> PreTrainedTokenizerFast:
    tokenizer_obj = Tokenizer(WordLevel({PAD_TOKEN: 0, UNK_TOKEN: 1, "hello": 2, "world": 3}))
    tokenizer_obj.pre_tokenizer = Whitespace()
    tokenizer = None
    tokenizer.pad_token = PAD_TOKEN
    tokenizer.eos_token = tokenizer.eos_token or tokenizer.pad_token
    return tokenizer


def x__fallback_tokenizer__mutmut_14() -> PreTrainedTokenizerFast:
    tokenizer_obj = Tokenizer(WordLevel({PAD_TOKEN: 0, UNK_TOKEN: 1, "hello": 2, "world": 3}))
    tokenizer_obj.pre_tokenizer = Whitespace()
    tokenizer = PreTrainedTokenizerFast(
        tokenizer_object=None, pad_token=PAD_TOKEN, unk_token=UNK_TOKEN
    )
    tokenizer.pad_token = PAD_TOKEN
    tokenizer.eos_token = tokenizer.eos_token or tokenizer.pad_token
    return tokenizer


def x__fallback_tokenizer__mutmut_15() -> PreTrainedTokenizerFast:
    tokenizer_obj = Tokenizer(WordLevel({PAD_TOKEN: 0, UNK_TOKEN: 1, "hello": 2, "world": 3}))
    tokenizer_obj.pre_tokenizer = Whitespace()
    tokenizer = PreTrainedTokenizerFast(
        tokenizer_object=tokenizer_obj, pad_token=None, unk_token=UNK_TOKEN
    )
    tokenizer.pad_token = PAD_TOKEN
    tokenizer.eos_token = tokenizer.eos_token or tokenizer.pad_token
    return tokenizer


def x__fallback_tokenizer__mutmut_16() -> PreTrainedTokenizerFast:
    tokenizer_obj = Tokenizer(WordLevel({PAD_TOKEN: 0, UNK_TOKEN: 1, "hello": 2, "world": 3}))
    tokenizer_obj.pre_tokenizer = Whitespace()
    tokenizer = PreTrainedTokenizerFast(
        tokenizer_object=tokenizer_obj, pad_token=PAD_TOKEN, unk_token=None
    )
    tokenizer.pad_token = PAD_TOKEN
    tokenizer.eos_token = tokenizer.eos_token or tokenizer.pad_token
    return tokenizer


def x__fallback_tokenizer__mutmut_17() -> PreTrainedTokenizerFast:
    tokenizer_obj = Tokenizer(WordLevel({PAD_TOKEN: 0, UNK_TOKEN: 1, "hello": 2, "world": 3}))
    tokenizer_obj.pre_tokenizer = Whitespace()
    tokenizer = PreTrainedTokenizerFast(
        pad_token=PAD_TOKEN, unk_token=UNK_TOKEN
    )
    tokenizer.pad_token = PAD_TOKEN
    tokenizer.eos_token = tokenizer.eos_token or tokenizer.pad_token
    return tokenizer


def x__fallback_tokenizer__mutmut_18() -> PreTrainedTokenizerFast:
    tokenizer_obj = Tokenizer(WordLevel({PAD_TOKEN: 0, UNK_TOKEN: 1, "hello": 2, "world": 3}))
    tokenizer_obj.pre_tokenizer = Whitespace()
    tokenizer = PreTrainedTokenizerFast(
        tokenizer_object=tokenizer_obj, unk_token=UNK_TOKEN
    )
    tokenizer.pad_token = PAD_TOKEN
    tokenizer.eos_token = tokenizer.eos_token or tokenizer.pad_token
    return tokenizer


def x__fallback_tokenizer__mutmut_19() -> PreTrainedTokenizerFast:
    tokenizer_obj = Tokenizer(WordLevel({PAD_TOKEN: 0, UNK_TOKEN: 1, "hello": 2, "world": 3}))
    tokenizer_obj.pre_tokenizer = Whitespace()
    tokenizer = PreTrainedTokenizerFast(
        tokenizer_object=tokenizer_obj, pad_token=PAD_TOKEN, )
    tokenizer.pad_token = PAD_TOKEN
    tokenizer.eos_token = tokenizer.eos_token or tokenizer.pad_token
    return tokenizer


def x__fallback_tokenizer__mutmut_20() -> PreTrainedTokenizerFast:
    tokenizer_obj = Tokenizer(WordLevel({PAD_TOKEN: 0, UNK_TOKEN: 1, "hello": 2, "world": 3}))
    tokenizer_obj.pre_tokenizer = Whitespace()
    tokenizer = PreTrainedTokenizerFast(
        tokenizer_object=tokenizer_obj, pad_token=PAD_TOKEN, unk_token=UNK_TOKEN
    )
    tokenizer.pad_token = None
    tokenizer.eos_token = tokenizer.eos_token or tokenizer.pad_token
    return tokenizer


def x__fallback_tokenizer__mutmut_21() -> PreTrainedTokenizerFast:
    tokenizer_obj = Tokenizer(WordLevel({PAD_TOKEN: 0, UNK_TOKEN: 1, "hello": 2, "world": 3}))
    tokenizer_obj.pre_tokenizer = Whitespace()
    tokenizer = PreTrainedTokenizerFast(
        tokenizer_object=tokenizer_obj, pad_token=PAD_TOKEN, unk_token=UNK_TOKEN
    )
    tokenizer.pad_token = PAD_TOKEN
    tokenizer.eos_token = None
    return tokenizer


def x__fallback_tokenizer__mutmut_22() -> PreTrainedTokenizerFast:
    tokenizer_obj = Tokenizer(WordLevel({PAD_TOKEN: 0, UNK_TOKEN: 1, "hello": 2, "world": 3}))
    tokenizer_obj.pre_tokenizer = Whitespace()
    tokenizer = PreTrainedTokenizerFast(
        tokenizer_object=tokenizer_obj, pad_token=PAD_TOKEN, unk_token=UNK_TOKEN
    )
    tokenizer.pad_token = PAD_TOKEN
    tokenizer.eos_token = tokenizer.eos_token and tokenizer.pad_token
    return tokenizer

x__fallback_tokenizer__mutmut_mutants : ClassVar[MutantDict] = {
'x__fallback_tokenizer__mutmut_1': x__fallback_tokenizer__mutmut_1, 
    'x__fallback_tokenizer__mutmut_2': x__fallback_tokenizer__mutmut_2, 
    'x__fallback_tokenizer__mutmut_3': x__fallback_tokenizer__mutmut_3, 
    'x__fallback_tokenizer__mutmut_4': x__fallback_tokenizer__mutmut_4, 
    'x__fallback_tokenizer__mutmut_5': x__fallback_tokenizer__mutmut_5, 
    'x__fallback_tokenizer__mutmut_6': x__fallback_tokenizer__mutmut_6, 
    'x__fallback_tokenizer__mutmut_7': x__fallback_tokenizer__mutmut_7, 
    'x__fallback_tokenizer__mutmut_8': x__fallback_tokenizer__mutmut_8, 
    'x__fallback_tokenizer__mutmut_9': x__fallback_tokenizer__mutmut_9, 
    'x__fallback_tokenizer__mutmut_10': x__fallback_tokenizer__mutmut_10, 
    'x__fallback_tokenizer__mutmut_11': x__fallback_tokenizer__mutmut_11, 
    'x__fallback_tokenizer__mutmut_12': x__fallback_tokenizer__mutmut_12, 
    'x__fallback_tokenizer__mutmut_13': x__fallback_tokenizer__mutmut_13, 
    'x__fallback_tokenizer__mutmut_14': x__fallback_tokenizer__mutmut_14, 
    'x__fallback_tokenizer__mutmut_15': x__fallback_tokenizer__mutmut_15, 
    'x__fallback_tokenizer__mutmut_16': x__fallback_tokenizer__mutmut_16, 
    'x__fallback_tokenizer__mutmut_17': x__fallback_tokenizer__mutmut_17, 
    'x__fallback_tokenizer__mutmut_18': x__fallback_tokenizer__mutmut_18, 
    'x__fallback_tokenizer__mutmut_19': x__fallback_tokenizer__mutmut_19, 
    'x__fallback_tokenizer__mutmut_20': x__fallback_tokenizer__mutmut_20, 
    'x__fallback_tokenizer__mutmut_21': x__fallback_tokenizer__mutmut_21, 
    'x__fallback_tokenizer__mutmut_22': x__fallback_tokenizer__mutmut_22
}

def _fallback_tokenizer(*args, **kwargs):
    result = _mutmut_trampoline(x__fallback_tokenizer__mutmut_orig, x__fallback_tokenizer__mutmut_mutants, args, kwargs)
    return result 

_fallback_tokenizer.__signature__ = _mutmut_signature(x__fallback_tokenizer__mutmut_orig)
x__fallback_tokenizer__mutmut_orig.__name__ = 'x__fallback_tokenizer'


@lru_cache
def _tokenizer_cached() -> PreTrainedTokenizerBase:
    config: dict[str, Any] = {}
    if _DEFAULT_MODEL_NAME:
        config["model_name_or_path"] = _DEFAULT_MODEL_NAME
    if _DEFAULT_TOKENIZER_FILE:
        config["tokenizer_file"] = _DEFAULT_TOKENIZER_FILE
    if config:
        return load_tokenizer(config, cache_dir=_DEFAULT_CACHE_DIR, allow_remote=_ALLOW_REMOTE)
    return _fallback_tokenizer()


@lru_cache
def _model_cached() -> AutoModelForCausalLM:
    tokenizer = _tokenizer_cached()
    if _DEFAULT_MODEL_NAME:
        model = AutoModelForCausalLM.from_pretrained(  # nosec B615
            _DEFAULT_MODEL_NAME,
            cache_dir=_DEFAULT_CACHE_DIR,
            local_files_only=not _ALLOW_REMOTE,
        )
    else:
        config = GPT2Config(
            vocab_size=tokenizer.vocab_size,
            n_embd=64,
            n_layer=2,
            n_head=2,
        )
        model = AutoModelForCausalLM.from_config(config)
    model.eval()
    return model


def x__denylist__mutmut_orig() -> DenylistEnforcer:
    return _RUNTIME_DENYLIST or _denylist_cached()


def x__denylist__mutmut_1() -> DenylistEnforcer:
    return _RUNTIME_DENYLIST and _denylist_cached()

x__denylist__mutmut_mutants : ClassVar[MutantDict] = {
'x__denylist__mutmut_1': x__denylist__mutmut_1
}

def _denylist(*args, **kwargs):
    result = _mutmut_trampoline(x__denylist__mutmut_orig, x__denylist__mutmut_mutants, args, kwargs)
    return result 

_denylist.__signature__ = _mutmut_signature(x__denylist__mutmut_orig)
x__denylist__mutmut_orig.__name__ = 'x__denylist'


def x__tokenizer__mutmut_orig() -> PreTrainedTokenizerBase:
    return _RUNTIME_TOKENIZER or _tokenizer_cached()


def x__tokenizer__mutmut_1() -> PreTrainedTokenizerBase:
    return _RUNTIME_TOKENIZER and _tokenizer_cached()

x__tokenizer__mutmut_mutants : ClassVar[MutantDict] = {
'x__tokenizer__mutmut_1': x__tokenizer__mutmut_1
}

def _tokenizer(*args, **kwargs):
    result = _mutmut_trampoline(x__tokenizer__mutmut_orig, x__tokenizer__mutmut_mutants, args, kwargs)
    return result 

_tokenizer.__signature__ = _mutmut_signature(x__tokenizer__mutmut_orig)
x__tokenizer__mutmut_orig.__name__ = 'x__tokenizer'


def x__model__mutmut_orig() -> AutoModelForCausalLM:
    return _RUNTIME_MODEL or _model_cached()


def x__model__mutmut_1() -> AutoModelForCausalLM:
    return _RUNTIME_MODEL and _model_cached()

x__model__mutmut_mutants : ClassVar[MutantDict] = {
'x__model__mutmut_1': x__model__mutmut_1
}

def _model(*args, **kwargs):
    result = _mutmut_trampoline(x__model__mutmut_orig, x__model__mutmut_mutants, args, kwargs)
    return result 

_model.__signature__ = _mutmut_signature(x__model__mutmut_orig)
x__model__mutmut_orig.__name__ = 'x__model'


def x_configure_runtime__mutmut_orig(
    *,
    model: AutoModelForCausalLM | None = None,
    tokenizer: PreTrainedTokenizerBase | None = None,
    enforcer: DenylistEnforcer | None = None,
) -> None:
    """Override cached runtime components (primarily for tests)."""

    global _RUNTIME_MODEL, _RUNTIME_TOKENIZER, _RUNTIME_DENYLIST
    if model is not None:
        _RUNTIME_MODEL = model
    if tokenizer is not None:
        _RUNTIME_TOKENIZER = tokenizer
    if enforcer is not None:
        _RUNTIME_DENYLIST = enforcer


def x_configure_runtime__mutmut_1(
    *,
    model: AutoModelForCausalLM | None = None,
    tokenizer: PreTrainedTokenizerBase | None = None,
    enforcer: DenylistEnforcer | None = None,
) -> None:
    """Override cached runtime components (primarily for tests)."""

    global _RUNTIME_MODEL, _RUNTIME_TOKENIZER, _RUNTIME_DENYLIST
    if model is None:
        _RUNTIME_MODEL = model
    if tokenizer is not None:
        _RUNTIME_TOKENIZER = tokenizer
    if enforcer is not None:
        _RUNTIME_DENYLIST = enforcer


def x_configure_runtime__mutmut_2(
    *,
    model: AutoModelForCausalLM | None = None,
    tokenizer: PreTrainedTokenizerBase | None = None,
    enforcer: DenylistEnforcer | None = None,
) -> None:
    """Override cached runtime components (primarily for tests)."""

    global _RUNTIME_MODEL, _RUNTIME_TOKENIZER, _RUNTIME_DENYLIST
    if model is not None:
        _RUNTIME_MODEL = None
    if tokenizer is not None:
        _RUNTIME_TOKENIZER = tokenizer
    if enforcer is not None:
        _RUNTIME_DENYLIST = enforcer


def x_configure_runtime__mutmut_3(
    *,
    model: AutoModelForCausalLM | None = None,
    tokenizer: PreTrainedTokenizerBase | None = None,
    enforcer: DenylistEnforcer | None = None,
) -> None:
    """Override cached runtime components (primarily for tests)."""

    global _RUNTIME_MODEL, _RUNTIME_TOKENIZER, _RUNTIME_DENYLIST
    if model is not None:
        _RUNTIME_MODEL = model
    if tokenizer is None:
        _RUNTIME_TOKENIZER = tokenizer
    if enforcer is not None:
        _RUNTIME_DENYLIST = enforcer


def x_configure_runtime__mutmut_4(
    *,
    model: AutoModelForCausalLM | None = None,
    tokenizer: PreTrainedTokenizerBase | None = None,
    enforcer: DenylistEnforcer | None = None,
) -> None:
    """Override cached runtime components (primarily for tests)."""

    global _RUNTIME_MODEL, _RUNTIME_TOKENIZER, _RUNTIME_DENYLIST
    if model is not None:
        _RUNTIME_MODEL = model
    if tokenizer is not None:
        _RUNTIME_TOKENIZER = None
    if enforcer is not None:
        _RUNTIME_DENYLIST = enforcer


def x_configure_runtime__mutmut_5(
    *,
    model: AutoModelForCausalLM | None = None,
    tokenizer: PreTrainedTokenizerBase | None = None,
    enforcer: DenylistEnforcer | None = None,
) -> None:
    """Override cached runtime components (primarily for tests)."""

    global _RUNTIME_MODEL, _RUNTIME_TOKENIZER, _RUNTIME_DENYLIST
    if model is not None:
        _RUNTIME_MODEL = model
    if tokenizer is not None:
        _RUNTIME_TOKENIZER = tokenizer
    if enforcer is None:
        _RUNTIME_DENYLIST = enforcer


def x_configure_runtime__mutmut_6(
    *,
    model: AutoModelForCausalLM | None = None,
    tokenizer: PreTrainedTokenizerBase | None = None,
    enforcer: DenylistEnforcer | None = None,
) -> None:
    """Override cached runtime components (primarily for tests)."""

    global _RUNTIME_MODEL, _RUNTIME_TOKENIZER, _RUNTIME_DENYLIST
    if model is not None:
        _RUNTIME_MODEL = model
    if tokenizer is not None:
        _RUNTIME_TOKENIZER = tokenizer
    if enforcer is not None:
        _RUNTIME_DENYLIST = None

x_configure_runtime__mutmut_mutants : ClassVar[MutantDict] = {
'x_configure_runtime__mutmut_1': x_configure_runtime__mutmut_1, 
    'x_configure_runtime__mutmut_2': x_configure_runtime__mutmut_2, 
    'x_configure_runtime__mutmut_3': x_configure_runtime__mutmut_3, 
    'x_configure_runtime__mutmut_4': x_configure_runtime__mutmut_4, 
    'x_configure_runtime__mutmut_5': x_configure_runtime__mutmut_5, 
    'x_configure_runtime__mutmut_6': x_configure_runtime__mutmut_6
}

def configure_runtime(*args, **kwargs):
    result = _mutmut_trampoline(x_configure_runtime__mutmut_orig, x_configure_runtime__mutmut_mutants, args, kwargs)
    return result 

configure_runtime.__signature__ = _mutmut_signature(x_configure_runtime__mutmut_orig)
x_configure_runtime__mutmut_orig.__name__ = 'x_configure_runtime'


@app.get("/health")
def health() -> dict:
    """Simple health endpoint returning a 200 response."""

    return {"status": "ok"}


@app.get("/")
def root() -> dict:
    """Root endpoint mirroring the health payload."""

    return {"name": "codex", "status": "ok"}


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest) -> PredictResponse:
    """Tokenize input, enforce denylist, and generate a response."""

    try:
        _denylist().ensure_allowed(req.prompt)
    except DenylistViolation as exc:  # pragma: no cover - defensive branch
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    tokenizer = _tokenizer()
    model = _model()
    encoded = tokenizer(
        req.prompt,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=tokenizer.model_max_length,
    )
    pad_token_id = tokenizer.pad_token_id or tokenizer.eos_token_id
    with torch.no_grad():
        generated = model.generate(
            **encoded,
            max_new_tokens=_MAX_NEW_TOKENS,
            pad_token_id=pad_token_id,
            do_sample=False,
        )
    output = tokenizer.batch_decode(generated, skip_special_tokens=True)[0]
    return PredictResponse(output=output)
