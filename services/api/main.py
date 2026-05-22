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
from typing import Any, Optional

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
                        pass  # already a _FakeTensor
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
from codex_ml.registry.base import RegistryError
from codex_ml.registry.models import get_model
from codex_ml.registry.tokenizers import get_tokenizer

try:
    from codex_ml.tokenization.adapter import WhitespaceTokenizer
except ImportError:  # pragma: no cover - optional import
    WhitespaceTokenizer = None

from security import (
    SecurityError,
    log_security_event,
    rate_limiter,
    validate_input,
    verify_csrf_token,
    verify_session_integrity,
)
from security.content_filters import enforce_content_policies

ARTIFACTS = Path(os.getenv("ARTIFACTS_DIR", "artifacts/api"))
ARTIFACTS.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Codex API", version="0.1.0")
logger = logging.getLogger("codex_ml.api")

# --- Authentication middleware + routes ------------------------------------
try:
    from codex.api.auth_routes import create_auth_router as _create_auth_router
    from codex.auth.middleware import AuthConfig, AuthMiddleware
    from codex.auth.token_manager import TokenManager as _AuthTokenManager

    _auth_secret = os.getenv("CODEX_AUTH_SECRET", "")
    if not _auth_secret:
        _env = os.getenv("CODEX_ENV", "development")
        if _env == "production":
            raise RuntimeError(
                "CODEX_AUTH_SECRET must be explicitly set in production. "
                "Set the CODEX_AUTH_SECRET environment variable to a strong secret."
            )
        logger.warning(
            "CODEX_AUTH_SECRET not set — using insecure default. "
            "Set CODEX_AUTH_SECRET for production deployments."
        )
        _auth_secret = "codex-auth-change-me-in-production"  # nosec B105 — dev only  # pragma: allowlist secret
    _auth_tm = _AuthTokenManager(secret_key=_auth_secret)

    # Auth routes must be exempt from the middleware since they are public.
    # Use startswith-based prefix matching so all current and future /auth/*
    # endpoints (including /auth/csrf-token) are automatically exempt.
    _exempt = {
        "/health", "/ready", "/metrics", "/docs", "/openapi.json",
    }
    _auth_prefix = "/auth/"
    _auth_cfg = AuthConfig(
        enabled=os.getenv("CODEX_AUTH_MIDDLEWARE_ENABLED", "1") == "1",
        exempt_paths=_exempt,
        exempt_prefixes=[_auth_prefix],
        rate_limit_requests=int(os.getenv("CODEX_AUTH_RATE_LIMIT", "100")),
        rate_limit_window=60,
    )
    app.add_middleware(AuthMiddleware, token_manager=_auth_tm, config=_auth_cfg)
    app.include_router(_create_auth_router(secret_key=_auth_secret))
except Exception:  # pragma: no cover - auth module may be absent in some deploys
    logger.debug("Auth routes/middleware not available; skipping registration")

_AWS_SECRET_PATTERN = "AWS_SECRET_ACCESS_" + "KEY"  # pragma: allowlist secret

SECRET_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"(?i)(sk-[A-Za-z0-9]{10,})"),
    re.compile(r"(?i)(AKIA[0-9A-Z]{16})"),
    re.compile(r"(?i)(ASIA[0-9A-Z]{16})"),
    re.compile(rf"(?i)({_AWS_SECRET_PATTERN}\s*=\s*[A-Za-z0-9/+=]{{40}})"),
    re.compile(r"(?i)(AIza[0-9A-Za-z\-_]{20,})"),  # Google API keys: min 24 chars total (AIza + 20 suffix)
    re.compile(r"(?i)(ghp_[A-Za-z0-9]{35,})"),  # GitHub PATs: min 39 chars total (ghp_ + 35 suffix)
    re.compile(r"(?i)(xox[baprs]-[A-Za-z0-9\-]{10,})"),
)

QUEUE: asyncio.Queue[dict] = asyncio.Queue(maxsize=128)
JOBS: dict[str, dict[str, Any]] = {}
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


# ---------------------------------------------------------------------------
# Helpers for context-limit and vocab-size resolution (extracted from inner
# functions to keep cyclomatic complexity below the C901 threshold of 10).
# ---------------------------------------------------------------------------

def _coerce_positive_int(value: Any) -> Optional[int]:
    """Return *value* as a positive int, or ``None`` if not coercible."""
    if isinstance(value, bool):  # bool subclasses int — reject it
        return None
    if isinstance(value, int) and value > 0:
        return value
    if isinstance(value, float) and value > 0 and value.is_integer():
        return int(value)
    return None


def _get_nested_attr(obj: Any, *names: str) -> Optional[int]:
    """Walk a dotted attribute path and coerce the leaf to a positive int."""
    current: Any = obj
    for name in names:
        current = getattr(current, name, None)
        if current is None:
            return None
    return _coerce_positive_int(current)


def _parse_env_context_limit() -> Optional[int]:
    """Parse ``API_MAX_PROMPT_TOKENS`` env-var; return ``None`` if absent/invalid."""
    raw = os.getenv("API_MAX_PROMPT_TOKENS")
    if not raw:
        return None
    try:
        parsed = int(raw)
    except ValueError:
        logger.warning("Invalid API_MAX_PROMPT_TOKENS value", extra={"value": raw})
        return None
    if parsed > 0:
        return parsed
    logger.warning("API_MAX_PROMPT_TOKENS must be positive", extra={"value": raw})
    return None


_CONTEXT_LIMIT_ATTR_PATHS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("model", ("cfg", "max_seq_len")),
    ("model", ("config", "max_position_embeddings")),
    ("model", ("config", "n_positions")),
    ("model", ("config", "n_ctx")),
    ("model", ("config", "seq_length")),
    ("model", ("max_seq_len",)),
    ("model", ("max_position_embeddings",)),
    ("tokenizer", ("model_max_length",)),
    ("tokenizer", ("max_length",)),
)

_HF_SENTINEL = 10**8  # Hugging Face uses huge values to mean "no limit"


def _valid_vocab_size(value: Any) -> Optional[int]:
    """Return *value* as a positive int vocab size, or ``None``."""
    if isinstance(value, bool):  # pragma: no cover - defensive
        return None
    if isinstance(value, int) and value > 0:
        return value
    return None


def _resolve_context_limit(tokenizer: Any, model: Any) -> Optional[int]:
    env_limit = _parse_env_context_limit()
    if env_limit is not None:
        return env_limit

    objs = {"model": model, "tokenizer": tokenizer}
    for obj_key, path in _CONTEXT_LIMIT_ATTR_PATHS:
        limit = _get_nested_attr(objs[obj_key], *path)
        if limit is None or limit >= _HF_SENTINEL:
            continue
        return limit

    return None


def _get_model_vocab_size(model: Any) -> Optional[int]:
    """Best-effort extraction of a model's vocabulary size."""
    for attr in ("cfg", "config"):
        container = getattr(model, attr, None)
        if container is not None:
            size = _valid_vocab_size(getattr(container, "vocab_size", None))
            if size:
                return size

    size = _valid_vocab_size(getattr(model, "vocab_size", None))
    if size:
        return size

    return _get_vocab_size_from_embeddings(model)


def _get_vocab_size_from_embeddings(model: Any) -> Optional[int]:
    """Probe ``get_input_embeddings()`` for the model's vocabulary size."""
    get_input_embeddings = getattr(model, "get_input_embeddings", None)
    if not callable(get_input_embeddings):
        return None
    embeddings = get_input_embeddings()
    size = _valid_vocab_size(getattr(embeddings, "num_embeddings", None))
    if size:
        return size
    weight = getattr(embeddings, "weight", None)
    if weight is not None and hasattr(weight, "shape") and weight.shape:
        return _valid_vocab_size(weight.shape[0])
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
        except (ImportError, AttributeError, RegistryError, ValueError) as exc:
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
    notes: Optional[str] = None


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
            except asyncio.CancelledError:
                # Re-raise so the task loop exits cleanly on cancellation.
                # Without this, CancelledError would be caught by the broad
                # `except Exception` below and swallowed, causing task.cancel()
                # in _shutdown() to hang waiting for the task to finish.
                raise
            except Exception as exc:
                JOBS[jid] = {"status": "failed", "error": str(exc)}
            finally:
                QUEUE.task_done()

    app.state.worker_task = asyncio.create_task(worker())


@app.on_event("shutdown")
async def _shutdown() -> None:
    worker_task = getattr(app.state, "worker_task", None)
    if worker_task is not None and not worker_task.done():
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            # Intentionally suppressed: CancelledError is the expected outcome of
            # task.cancel() and signals successful teardown.  In a shutdown handler
            # there is no outer coroutine to propagate to, so swallowing is correct.
            logger.info("Background worker task cancelled during shutdown")


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
    key = request.headers.get("x-api-key")
    expected = os.getenv("API_KEY")
    if expected and key != expected:
        return JSONResponse({"detail": "unauthorized"}, status_code=401)

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
        if not hasattr(app.state, "rate_ts"):
            app.state.rate_ts = 0.0
        if not hasattr(app.state, "rate_count"):
            app.state.rate_count = 0
        now = time.time()
        if now - app.state.rate_ts >= 1:
            app.state.rate_ts = now
            app.state.rate_count = 0
        if app.state.rate_count >= limit:
            return JSONResponse({"detail": "rate limit exceeded"}, status_code=429)
        app.state.rate_count += 1
    else:
        app.state.rate_count = 0
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
