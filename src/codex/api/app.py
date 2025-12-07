"""FastAPI application exposing health and text generation endpoints."""

from __future__ import annotations

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


class PredictRequest(BaseModel):
    """Request schema for the `/predict` endpoint."""

    prompt: str


class PredictResponse(BaseModel):
    """Response schema for the `/predict` endpoint."""

    output: str


@lru_cache
def _denylist_cached() -> DenylistEnforcer:
    return DenylistEnforcer.from_yaml(Path("policies/denylist.yaml"))


def _fallback_tokenizer() -> PreTrainedTokenizerFast:
    tokenizer_obj = Tokenizer(WordLevel({"[PAD]": 0, "[UNK]": 1, "hello": 2, "world": 3}))
    tokenizer_obj.pre_tokenizer = Whitespace()
    tokenizer = PreTrainedTokenizerFast(
        tokenizer_object=tokenizer_obj, pad_token="[PAD]", unk_token="[UNK]"
    )
    tokenizer.pad_token = "[PAD]"
    tokenizer.eos_token = tokenizer.eos_token or tokenizer.pad_token
    return tokenizer


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
        model = AutoModelForCausalLM.from_pretrained(
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


def _denylist() -> DenylistEnforcer:
    return _RUNTIME_DENYLIST or _denylist_cached()


def _tokenizer() -> PreTrainedTokenizerBase:
    return _RUNTIME_TOKENIZER or _tokenizer_cached()


def _model() -> AutoModelForCausalLM:
    return _RUNTIME_MODEL or _model_cached()


def configure_runtime(
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
