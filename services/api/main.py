from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

import torch
from codex_ml.peft.peft_adapter import apply_lora
from codex_ml.registry.models import get_model
from codex_ml.registry.tokenizers import get_tokenizer

try:
    from codex_ml.tokenization.adapter import WhitespaceTokenizer
except ImportError:  # pragma: no cover - optional import
    WhitespaceTokenizer = None

ARTIFACTS = Path(os.getenv("ARTIFACTS_DIR", "artifacts/api"))
ARTIFACTS.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Codex API", version="0.1.0")
logger = logging.getLogger("codex_ml.api")

SECRET_PATTERNS: Tuple[re.Pattern[str], ...] = (
    re.compile(r"(?i)(sk-[A-Za-z0-9]{10,})"),
    re.compile(r"(?i)(AKIA[0-9A-Z]{16})"),
    re.compile(r"(?i)(ASIA[0-9A-Z]{16})"),
    re.compile(r"(?i)(aws_secret_access_key\s*=\s*[A-Za-z0-9/+=]{40})"),
    re.compile(r"(?i)(AIza[0-9A-Za-z\-_]{35})"),
    re.compile(r"(?i)(ghp_[A-Za-z0-9]{36})"),
    re.compile(r"(?i)(xox[baprs]-[A-Za-z0-9\-]{10,})"),
)

QUEUE: "asyncio.Queue[dict]" = asyncio.Queue(maxsize=128)
JOBS: Dict[str, Dict[str, Any]] = {}
_rate_ts = time.time()
_rate_count = 0


def _mask_secrets(payload: str) -> str:
    if os.getenv("DISABLE_SECRET_FILTER", "0") == "1":
        return payload
    redacted = payload
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub("[SECRET]", redacted)
    return redacted


def _to_tensor(value: Any) -> torch.Tensor:
    if isinstance(value, torch.Tensor):
        return value
    try:
        tensor = torch.as_tensor(value)
    except (TypeError, ValueError) as exc:  # pragma: no cover - defensive branch
        raise TypeError("logits output is not convertible to tensor") from exc
    if tensor.ndim == 0:
        raise TypeError("logits tensor must be at least 1D")
    return tensor


def _extract_logits(output: Any) -> torch.Tensor:
    if isinstance(output, torch.Tensor):
        return output
    if hasattr(output, "logits"):
        return _to_tensor(output.logits)
    if isinstance(output, dict) and "logits" in output:
        return _to_tensor(output["logits"])
    if isinstance(output, (tuple, list)) and output:
        first = output[0]
        if isinstance(first, torch.Tensor):
            return first
        if hasattr(first, "logits"):
            return _to_tensor(first.logits)
    raise TypeError("model output does not contain logits tensor")


def _resolve_context_limit(tokenizer: Any, model: Any) -> Optional[int]:
    env_override = os.getenv("API_MAX_PROMPT_TOKENS")
    if env_override:
        try:
            parsed = int(env_override)
        except ValueError:
            logger.warning("Invalid API_MAX_PROMPT_TOKENS value", extra={"value": env_override})
        else:
            if parsed > 0:
                return parsed
            logger.warning("API_MAX_PROMPT_TOKENS must be positive", extra={"value": env_override})

    def _coerce_int(value: Any) -> Optional[int]:
        if isinstance(value, bool):  # bool is subclass of int
            return None
        if isinstance(value, int) and value > 0:
            return value
        if isinstance(value, float) and value > 0 and value.is_integer():
            return int(value)
        return None

    def _get_attr(obj: Any, *names: str) -> Optional[int]:
        current = obj
        for name in names:
            current = getattr(current, name, None)
            if current is None:
                return None
        return _coerce_int(current)

    candidate_attrs = (
        (model, ("cfg", "max_seq_len")),
        (model, ("config", "max_position_embeddings")),
        (model, ("config", "n_positions")),
        (model, ("config", "n_ctx")),
        (model, ("config", "seq_length")),
        (model, ("max_seq_len",)),
        (model, ("max_position_embeddings",)),
        (tokenizer, ("model_max_length",)),
        (tokenizer, ("max_length",)),
    )

    for obj, path in candidate_attrs:
        limit = _get_attr(obj, *path)
        if limit is None:
            continue
        # Hugging Face uses extremely large sentinels for "no limit"
        if limit >= 10**8:
            continue
        return limit

    return None


def _get_model_vocab_size(model: Any) -> Optional[int]:
    """Best-effort extraction of a model's vocabulary size."""

    def _valid_size(value: Any) -> Optional[int]:
        if isinstance(value, bool):  # pragma: no cover - defensive
            return None
        if isinstance(value, int) and value > 0:
            return value
        return None

    cfg = getattr(model, "cfg", None)
    if cfg is not None:
        size = _valid_size(getattr(cfg, "vocab_size", None))
        if size:
            return size

    config = getattr(model, "config", None)
    if config is not None:
        size = _valid_size(getattr(config, "vocab_size", None))
        if size:
            return size

    get_input_embeddings = getattr(model, "get_input_embeddings", None)
    if callable(get_input_embeddings):
        embeddings = get_input_embeddings()
        num_embeddings = _valid_size(getattr(embeddings, "num_embeddings", None))
        if num_embeddings:
            return num_embeddings
        weight = getattr(embeddings, "weight", None)
        if weight is not None and hasattr(weight, "shape") and weight.shape:
            size = _valid_size(weight.shape[0])
            if size:
                return size

    size = _valid_size(getattr(model, "vocab_size", None))
    if size:
        return size

    return None


def _project_tokens(tokens: list[int], tokenizer: Any, model: Any) -> list[int]:
    """Clamp tokenizer output to the model's vocabulary when possible."""

    if not tokens:
        return tokens

    if WhitespaceTokenizer is not None and isinstance(tokenizer, WhitespaceTokenizer):
        vocab_size = _get_model_vocab_size(model)
        if vocab_size is None:
            logger.warning(
                "Unable to determine vocabulary size for whitespace tokenizer output",
                extra={"model": type(model).__name__},
            )
            return tokens
        return [token % vocab_size for token in tokens]

    return tokens


def _load_components() -> Tuple[Any, Any]:
    if not hasattr(app.state, "tokenizer") or not hasattr(app.state, "model"):
        tokenizer_name = os.getenv("API_TOKENIZER", "whitespace")
        model_name = os.getenv("API_MODEL", "MiniLM")
        model_cfg: Dict[str, Any] = {"local_files_only": True, "device": "cpu"}
        tokenizer = get_tokenizer(tokenizer_name)
        model = get_model(model_name, model_cfg)
        model.eval()
        if os.getenv("API_USE_LORA", "0") == "1":
            model = apply_lora(model)
        app.state.tokenizer = tokenizer
        app.state.model = model
        logger.info("Loaded API model", extra={"model": model_name, "tokenizer": tokenizer_name})
    return app.state.tokenizer, app.state.model


class InferRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=16000)


class InferResponse(BaseModel):
    completion: str
    tokens: int


class TrainRequest(BaseModel):
    epochs: int = Field(1, ge=1, le=100)
    notes: Optional[str] = None


class EvalRequest(BaseModel):
    dataset: str
    limit: int = 100


@app.on_event("startup")
async def _startup() -> None:
    async def worker() -> None:
        while True:
            job = await QUEUE.get()
            jid = job["id"]
            JOBS[jid] = {"status": "running", "started": time.time()}
            try:
                run_dir = ARTIFACTS / f"run-{int(time.time())}"
                run_dir.mkdir(parents=True, exist_ok=True)
                for e in range(job["epochs"]):
                    await asyncio.sleep(0.2)
                    (run_dir / f"epoch-{e + 1}.txt").write_text(
                        f"epoch {e + 1} done", encoding="utf-8"
                    )
                (run_dir / "metadata.json").write_text(
                    json.dumps({"epochs": job["epochs"]}), encoding="utf-8"
                )
                JOBS[jid] = {
                    "status": "completed",
                    "artifacts": str(run_dir),
                    "finished": time.time(),
                }
            except Exception as exc:  # noqa: BLE001
                JOBS[jid] = {"status": "failed", "error": str(exc)}
            finally:
                QUEUE.task_done()

    app.state.worker_task = asyncio.create_task(worker())


@app.post("/infer", response_model=InferResponse)
async def infer(req: InferRequest) -> InferResponse:
    tokenizer, model = _load_components()
    prompt_to_encode = req.prompt.strip()
    masked_prompt = _mask_secrets(prompt_to_encode)
    tokens = tokenizer.encode(masked_prompt)
    tokens = _project_tokens(tokens, tokenizer, model)
    limit = _resolve_context_limit(tokenizer, model)
    if limit is not None and len(tokens) > limit:
        detail = {
            "detail": "prompt too long for model context",
            "tokens": len(tokens),
            "limit": limit,
        }
        logger.warning("prompt exceeds model context", extra=detail)
        raise HTTPException(status_code=400, detail=detail)
    if not tokens:
        return InferResponse(completion="", tokens=0)
    input_ids = torch.tensor([tokens], dtype=torch.long)
    with torch.no_grad():
        raw_output = model(input_ids)
        logits = _extract_logits(raw_output)
        next_token = int(logits[0, -1].argmax().item())
    generated = tokens + [next_token]
    decoded = tokenizer.decode(generated)
    masked = _mask_secrets(decoded)
    if WhitespaceTokenizer is not None and isinstance(tokenizer, WhitespaceTokenizer):
        pieces = [masked_prompt] if masked_prompt else []
        pieces.append(str(next_token))
        masked = " ".join(pieces).strip()
    logger.info(
        "infer request",
        extra={
            "tokens_in": len(tokens),
            "tokens_out": len(generated),
            "model": type(model).__name__,
        },
    )
    return InferResponse(completion=masked, tokens=len(generated))


@app.post("/train")
async def train(req: TrainRequest) -> Dict[str, Any]:
    jid = f"job-{int(time.time() * 1000)}"
    await QUEUE.put({"id": jid, "epochs": req.epochs})
    return {"ok": True, "job_id": jid, "queued": QUEUE.qsize()}


@app.post("/evaluate")
async def evaluate(req: EvalRequest) -> Dict[str, Any]:
    return {
        "ok": True,
        "dataset": req.dataset,
        "limit": req.limit,
        "metrics": {"accuracy": 0.0},
    }


@app.get("/status")
async def status() -> Dict[str, Any]:
    return {"ok": True, "queue": QUEUE.qsize(), "jobs": JOBS}


@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    global _rate_ts, _rate_count
    key = request.headers.get("x-api-key")
    expected = os.getenv("API_KEY")
    if expected and key != expected:
        raise HTTPException(status_code=401, detail="unauthorized")
    limit = int(os.getenv("API_RATE_LIMIT", "0"))
    if limit > 0:
        now = time.time()
        if now - _rate_ts >= 1:
            _rate_ts = now
            _rate_count = 0
        if _rate_count >= limit:
            return JSONResponse({"detail": "rate limit exceeded"}, status_code=429)
        _rate_count += 1
    else:
        _rate_count = 0
    try:
        return await call_next(request)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc))
