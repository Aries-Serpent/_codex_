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


import os  # noqa: E402
from functools import lru_cache  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Any  # noqa: E402

import torch  # noqa: E402
from fastapi import FastAPI, HTTPException  # noqa: E402
from pydantic import BaseModel  # noqa: E402

from codex_ml.safety.moderation import (  # noqa: E402
    ModerationAdapter,
    ModerationRejection,
    ModerationSettings,
)
from codex_ml.security import DenylistEnforcer, DenylistViolation  # noqa: E402
from transformers import (  # noqa: E402
    AutoModelForCausalLM,
    GPT2Config,
    PreTrainedTokenizerBase,
    PreTrainedTokenizerFast,
)

app = FastAPI(title="codex", version="0.2.0")

try:
    from aries_serpent_core.api.auth_routes import create_auth_router

    # Pass prefix="" to override the router's own default "/auth" prefix —
    # the include_router prefix="/api/auth" supplies the full mount point.
    app.include_router(create_auth_router(prefix=""), prefix="/api/auth", tags=["auth"])
except ImportError:  # pragma: no cover – auth module not installed
    logger.debug("Suppressed exception in handler", exc_info=True)
except AttributeError as _auth_exc:  # pragma: no cover – unexpected init error
    import logging as _logging

    _logging.getLogger(__name__).warning(
        "Auth router not mounted — unexpected error during import: %s", _auth_exc
    )

# Include legacy endpoints with RFC 8594 deprecation headers
try:
    from aries_serpent_core.api.legacy_endpoints import router as legacy_router

    app.include_router(legacy_router, tags=["legacy"])
except (IOError, OSError, ModuleNotFoundError, ImportError) as _legacy_exc:  # pragma: no cover – unexpected init error
    logger.warning("Legacy router not mounted — unexpected error during import: %s", _legacy_exc)

_DEFAULT_CACHE_DIR = os.environ.get("CODEX_TOKENIZER_CACHE", "artifacts/tokenizer_cache")
_DEFAULT_MODEL_NAME = os.environ.get("CODEX_MODEL_NAME")
_DEFAULT_TOKENIZER_FILE = os.environ.get("CODEX_TOKENIZER_FILE")
_ALLOW_REMOTE = os.environ.get("CODEX_ALLOW_REMOTE", "0").lower() in {
    "1",
    "true",
    "on",
    "yes",
}
_MAX_NEW_TOKENS = int(os.environ.get("CODEX_MAX_NEW_TOKENS", "32"))
_RUNTIME_MODEL: AutoModelForCausalLM | None = None
_RUNTIME_TOKENIZER: PreTrainedTokenizerBase | None = None
_RUNTIME_DENYLIST: DenylistEnforcer | None = None
PAD_TOKEN = "[PAD]"  # nosec B105 - conventional tokenizer pad token
UNK_TOKEN = "[UNK]"  # nosec B105 B106 - conventional unknown token marker


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
    from tokenizers import Tokenizer
    from tokenizers.models import WordLevel
    from tokenizers.pre_tokenizers import Whitespace

    tokenizer_obj = Tokenizer(WordLevel({PAD_TOKEN: 0, UNK_TOKEN: 1, "hello": 2, "world": 3}))
    tokenizer_obj.pre_tokenizer = Whitespace()
    tokenizer = PreTrainedTokenizerFast(
        tokenizer_object=tokenizer_obj, pad_token=PAD_TOKEN, unk_token=UNK_TOKEN
    )
    tokenizer.pad_token = PAD_TOKEN
    tokenizer.eos_token = tokenizer.eos_token or tokenizer.pad_token
    return tokenizer


@lru_cache
def _tokenizer_cached() -> PreTrainedTokenizerBase:
    from tokenization.loader import load_tokenizer

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
        model = AutoModelForCausalLM.from_pretrained(  # nosec B615  # type: ignore[assignment]
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
    model.eval()  # type: ignore[attr-defined]
    return model  # type: ignore[return-value]


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
def health() -> dict[str, Any]:
    """Health endpoint with sub-system status.

    Returns a 200 response with the overall status plus optional
    ``cognitive_brain`` and ``pattern_compressor`` diagnostics when
    the cognitive subsystem packages are importable.
    """
    result: dict[str, Any] = {"status": "ok"}

    # -- BrainClient health (CB-004) ----------------------------------------
    try:
        from aries_serpent_core.agents.brain_client import BrainClient

        client = BrainClient()
        result["cognitive_brain"] = {
            "available": client.is_available(),
        }
    except (ImportError, AttributeError):
        result["cognitive_brain"] = {"available": False, "note": "import failed"}

    # -- PatternCompressor metrics (CB-003) ---------------------------------
    try:
        from cognitive_brain.quantum.compression import PatternCompressor

        pc = PatternCompressor()
        result["pattern_compressor"] = {
            "available": True,
            "n_components": getattr(pc, "n_components", None),
        }
    except (ImportError, AttributeError):
        result["pattern_compressor"] = {"available": False}

    return result


@app.get("/")
def root() -> dict[str, Any]:
    """Root endpoint mirroring the health payload."""

    return {"name": "codex", "status": "ok"}


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest) -> PredictResponse:
    """Tokenize input, enforce denylist and moderation, then generate a response."""

    try:
        _denylist().ensure_allowed(req.prompt)
    except DenylistViolation as exc:  # pragma: no cover - defensive branch
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    # Gap 27: mandatory pre-prompt moderation (fail-closed)
    _mod = ModerationAdapter(ModerationSettings(enabled=True, fail_open=False))
    try:
        _mod.enforce(req.prompt, stage="input")
    except ModerationRejection:
        logger.warning("Moderation rejected /predict input")
        raise HTTPException(status_code=400, detail="Request rejected by content policy.")

    tokenizer = _tokenizer()
    model = _model()
    encoded = tokenizer(  # type: ignore[func-returns-value]
        req.prompt,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=tokenizer.model_max_length,
    )
    pad_token_id = tokenizer.pad_token_id or tokenizer.eos_token_id
    with torch.no_grad():
        generated = model.generate(  # type: ignore[arg-type,func-returns-value]
            **encoded,
            max_new_tokens=_MAX_NEW_TOKENS,
            pad_token_id=pad_token_id,
            do_sample=False,
        )
    output = tokenizer.batch_decode(generated, skip_special_tokens=True)[0]  # type: ignore[func-returns-value,index]

    # Gap 27: post-output moderation check (fail-closed)
    try:
        _mod.enforce(output, stage="output")
    except ModerationRejection:
        logger.warning("Moderation rejected /predict output")
        raise HTTPException(status_code=400, detail="Response rejected by content policy.")

    return PredictResponse(output=output)
