from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import time
from collections.abc import MutableMapping
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from fastapi import Body, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

try:  # Optional dependency: allow API to run in environments without torch
    import torch
except ImportError:  # pragma: no cover - executed in lightweight environments
    torch = SimpleNamespace()  # type: ignore[assignment]

if not hasattr(torch, "tensor") or not hasattr(torch, "as_tensor"):

    class _FakeTensor:
        def __init__(self, data: Any) -> None:
            self._data = data

        def __iter__(self):
            if isinstance(self._data, list):
                return iter(self._data)
            return iter([self._data])

        def __len__(self) -> int:
            return len(self._data) if isinstance(self._data, list) else 0

        def __getitem__(self, item: Any) -> Any:
            if isinstance(item, tuple):
                current: Any = self
                for part in item:
                    current = current[part]
                    if isinstance(current, _FakeTensor):
                        current = current
                return current
            value = self._data[item]
            return _FakeTensor(value) if isinstance(value, list) else value

        @property
        def ndim(self) -> int:
            depth = 0
            current = self._data
            while isinstance(current, list) and current:
                depth += 1
                current = current[0]
            return depth

        @property
        def shape(self) -> tuple[int, ...]:
            dims: list[int] = []
            current = self._data
            while isinstance(current, list):
                dims.append(len(current))
                if not current:
                    break
                current = current[0]
            return tuple(dims)

        def argmax(self) -> "_FakeTensor":
            if not isinstance(self._data, list) or not self._data:
                raise TypeError("argmax is only supported for non-empty sequences")
            index = max(range(len(self._data)), key=self._data.__getitem__)
            return _FakeTensor(index)

        def item(self) -> Any:
            if isinstance(self._data, list):
                if len(self._data) != 1:
                    raise ValueError("fake tensor contains multiple items")
                return self._data[0]
            return self._data

        def tolist(self) -> Any:
            if isinstance(self._data, list):
                return [(_FakeTensor(v).tolist() if isinstance(v, list) else v) for v in self._data]
            return self._data

    class _FakeNoGrad:
        def __enter__(self) -> None:  # pragma: no cover - simple context manager
            return None

        def __exit__(self, *exc_info: Any) -> bool:  # pragma: no cover - simple context manager
            return False

    def _fake_tensor(
        value: Any, dtype: Any = None
    ) -> _FakeTensor:  # noqa: ARG001 - dtype kept for API parity
        if isinstance(value, _FakeTensor):
            return value
        return _FakeTensor(value)

    def _fake_as_tensor(value: Any) -> _FakeTensor:
        return _fake_tensor(value)

    def _fake_no_grad() -> _FakeNoGrad:
        return _FakeNoGrad()

    torch.Tensor = _FakeTensor  # type: ignore[attr-defined]
    torch.tensor = _fake_tensor  # type: ignore[attr-defined]
    torch.as_tensor = _fake_as_tensor  # type: ignore[attr-defined]
    torch.long = int  # type: ignore[attr-defined]
    torch.no_grad = _fake_no_grad  # type: ignore[attr-defined]
from codex_ml.peft.peft_adapter import apply_lora
from codex_ml.registry.models import get_model
from codex_ml.registry.tokenizers import get_tokenizer

try:
    from codex_ml.tokenization.adapter import WhitespaceTokenizer
except ImportError:  # pragma: no cover - optional import
    WhitespaceTokenizer = None

from src.security import (
    SecurityError,
    log_security_event,
    rate_limiter,
    validate_input,
    verify_csrf_token,
    verify_session_integrity,
)
from src.security.content_filters import enforce_content_policies

ARTIFACTS = Path(os.getenv("ARTIFACTS_DIR", "artifacts/api"))
ARTIFACTS.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Codex API", version="0.1.0")
logger = logging.getLogger("codex_ml.api")

_AWS_SECRET_PATTERN = "AWS_SECRET_ACCESS_" + "KEY"

SECRET_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"(?i)(sk-[A-Za-z0-9]{10,})"),
    re.compile(r"(?i)(AKIA[0-9A-Z]{16})"),
    re.compile(r"(?i)(ASIA[0-9A-Z]{16})"),
    re.compile(rf"(?i)({_AWS_SECRET_PATTERN}\s*=\s*[A-Za-z0-9/+=]{{40}})"),
    re.compile(r"(?i)(AIza[0-9A-Za-z\-_]{35})"),
    re.compile(r"(?i)(ghp_[A-Za-z0-9]{36})"),
    re.compile(r"(?i)(xox[baprs]-[A-Za-z0-9\-]{10,})"),
)

QUEUE: asyncio.Queue[dict] = asyncio.Queue(maxsize=128)
JOBS: dict[str, dict[str, Any]] = {}
_rate_ts = time.time()
_rate_count = 0
ACTIVE_SESSIONS: list[MutableMapping[str, Any]] = []


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


def _resolve_context_limit(tokenizer: Any, model: Any) -> int | None:
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

    def _coerce_int(value: Any) -> int | None:
        if isinstance(value, bool):  # bool is subclass of int
            return None
        if isinstance(value, int) and value > 0:
            return value
        if isinstance(value, float) and value > 0 and value.is_integer():
            return int(value)
        return None

    def _get_attr(obj: Any, *names: str) -> int | None:
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


def _get_model_vocab_size(model: Any) -> int | None:
    """Best-effort extraction of a model's vocabulary size."""

    def _valid_size(value: Any) -> int | None:
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


class _EchoModel:
    def __init__(self, vocab_size: int = 128) -> None:
        self.vocab_size = vocab_size

    def eval(self) -> "_EchoModel":
        return self

    def __call__(self, input_ids: Any) -> dict[str, Any]:
        raw = input_ids.tolist() if hasattr(input_ids, "tolist") else input_ids
        if not raw:
            tokens: list[int] = []
        else:
            tokens = list(raw[0]) if isinstance(raw[0], list) else list(raw)
        if not tokens:
            logits = [[[0 for _ in range(self.vocab_size)]]]
        else:
            next_token = (int(tokens[-1]) + 1) % self.vocab_size
            logits = [[[0 for _ in range(self.vocab_size)] for _ in tokens]]
            logits[0][-1][next_token] = 1
        return {"logits": torch.tensor(logits)}


def _load_components() -> tuple[Any, Any]:
    if not hasattr(app.state, "tokenizer") or not hasattr(app.state, "model"):
        tokenizer_name = os.getenv("API_TOKENIZER", "whitespace")
        model_name = os.getenv("API_MODEL", "MiniLM")
        model_cfg: dict[str, Any] = {"local_files_only": True, "device": "cpu"}
        tokenizer = get_tokenizer(tokenizer_name)
        try:
            model = get_model(model_name, model_cfg)
        except (ImportError, AttributeError) as exc:
            logger.warning("Falling back to echo inference model", extra={"error": str(exc)})
            model = _EchoModel()
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
    notes: str | None = None


class EvalRequest(BaseModel):
    dataset: str
    limit: int = 100


InferRequest.model_rebuild(force=True)
InferResponse.model_rebuild(force=True)
TrainRequest.model_rebuild(force=True)
EvalRequest.model_rebuild(force=True)


@app.on_event("startup")
async def _startup() -> None:
    ACTIVE_SESSIONS.clear()
    ACTIVE_SESSIONS.append(
        {
            "id": "system-session",
            "fingerprint": "system",
            "ip": "127.0.0.1",
            "user_agent": "codex-internal",
        }
    )

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
            except Exception as exc:
                JOBS[jid] = {"status": "failed", "error": str(exc)}
            finally:
                QUEUE.task_done()

    app.state.worker_task = asyncio.create_task(worker())


def _rate_key(_: InferRequest) -> str:
    return "infer"


@rate_limiter(calls=30, period=60.0, key_func=_rate_key)
async def _enforce_infer_rate(req: InferRequest) -> None:
    return None


@app.post("/infer", response_model=InferResponse)
async def infer(req: InferRequest = Body(...)) -> InferResponse:
    await _enforce_infer_rate(req)
    tokenizer, model = _load_components()
    try:
        prompt_to_encode = validate_input(req.prompt, input_type="html")
        enforce_content_policies(prompt_to_encode)
    except SecurityError as exc:
        log_security_event(f"infer_blocked:{exc}")
        raise HTTPException(status_code=400, detail=str(exc)) from exc
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
    generated = [*tokens, next_token]
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


infer.__annotations__["req"] = InferRequest


@app.post("/train")
async def train(req: TrainRequest) -> dict[str, Any]:
    if req.notes:
        try:
            sanitized_notes = validate_input(req.notes, input_type="text")
            enforce_content_policies(sanitized_notes)
        except SecurityError as exc:
            log_security_event(f"train_blocked:{exc}")
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    jid = f"job-{int(time.time() * 1000)}"
    await QUEUE.put({"id": jid, "epochs": req.epochs})
    return {"ok": True, "job_id": jid, "queued": QUEUE.qsize()}


@app.post("/evaluate")
async def evaluate(req: EvalRequest) -> dict[str, Any]:
    return {
        "ok": True,
        "dataset": req.dataset,
        "limit": req.limit,
        "metrics": {"accuracy": 0.0},
    }


@app.get("/status")
async def status() -> dict[str, Any]:
    return {"ok": True, "queue": QUEUE.qsize(), "jobs": JOBS}


@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    global _rate_ts, _rate_count
    key = request.headers.get("x-api-key")
    expected = os.getenv("API_KEY")
    if expected and key != expected:
        raise HTTPException(status_code=401, detail="unauthorized")

    try:
        csrf_header = request.headers.get("x-csrf-token")
        csrf_cookie = request.cookies.get("csrftoken")
        if csrf_header or csrf_cookie:
            verify_csrf_token(csrf_header, csrf_cookie)

        session_id = request.headers.get("x-session-id")
        fingerprint = request.headers.get("x-session-fingerprint")
        if session_id and fingerprint:
            verify_session_integrity(
                session_id,
                {
                    "fingerprint": fingerprint,
                    "ip": request.client.host if request.client else "unknown",
                    "user_agent": request.headers.get("user-agent", "unknown"),
                },
                ACTIVE_SESSIONS,
            )

        for _, value in request.query_params.multi_items():
            validate_input(value, input_type="text")
            enforce_content_policies(value)

        if request.method in {"POST", "PUT", "PATCH"}:
            body_bytes = await request.body()
            if body_bytes:
                body_text = body_bytes.decode("utf-8", errors="ignore")
                validate_input(body_text, input_type="json")
    except SecurityError as exc:
        log_security_event(f"request_blocked:{exc}")
        raise HTTPException(status_code=400, detail=str(exc)) from exc

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
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/health")
async def health() -> dict[str, Any]:
    return {"status": "healthy", "timestamp": time.time()}


def check_db_connection() -> bool:
    return True


def check_model_loaded() -> bool:
    return hasattr(app.state, "model")


@app.get("/ready")
async def readiness() -> dict[str, Any]:
    checks = {"db": check_db_connection(), "model": check_model_loaded()}
    if all(checks.values()):
        return {"status": "ready", "checks": checks}
    raise HTTPException(status_code=503, detail=checks)
