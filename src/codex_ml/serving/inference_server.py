"""Lightweight inference server scaffolding used by integration tests."""

from __future__ import annotations

import logging
import os
import time
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, Field

    FASTAPI_AVAILABLE = True
except ImportError:  # pragma: no cover
    FASTAPI_AVAILABLE = False
    FastAPI = None  # type: ignore
    HTTPException = Exception  # type: ignore
    BaseModel = object  # type: ignore
    Field = lambda *a, **k: None  # type: ignore
    Request = object  # type: ignore

logger = logging.getLogger(__name__)

MAX_BATCH_SIZE = 100
MAX_INPUT_LENGTH = 10000
REQUEST_RATE_LIMIT = 1000


class ModelLoadError(Exception):
    """Raised when a model cannot be loaded."""


@dataclass
class ModelConfig:
    model_name: Optional[str] = "codex-default"
    model_type: str = "stub"
    model_path: Optional[str] = None
    device: str = "cpu"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelConfig":
        return cls(
            model_name=data.get("model_name"),
            model_type=data.get("model_type", "stub"),
            model_path=data.get("model_path"),
            device=data.get("device", "cpu"),
        )

    @classmethod
    def from_env(cls) -> "ModelConfig":
        return cls(
            model_name=os.getenv("CODEX_MODEL_NAME", "codex-default"),
            model_type=os.getenv("CODEX_MODEL_TYPE", "stub"),
            model_path=os.getenv("CODEX_MODEL_PATH"),
            device=os.getenv("CODEX_MODEL_DEVICE", "cpu"),
        )

    def validate(self) -> None:
        if not self.model_name:
            raise ValueError("model_name cannot be empty")
        if self.model_type not in {"stub", "huggingface", "onnx"}:
            raise ValueError("Unsupported model_type")
        if self.device not in {"cpu", "cuda"}:
            raise ValueError("Unsupported device")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "model_type": self.model_type,
            "model_path": self.model_path,
            "device": self.device,
        }


class RateLimiter:
    def __init__(self, max_requests: int = REQUEST_RATE_LIMIT, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.state: Dict[str, List[float]] = defaultdict(list)

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        window_start = now - self.window_seconds
        self.state[key] = [t for t in self.state[key] if t >= window_start]
        if len(self.state[key]) >= self.max_requests:
            return False
        self.state[key].append(now)
        return True


class ModelServer:
    def __init__(self, config: Optional[ModelConfig] = None) -> None:
        self.config = config or ModelConfig(model_name="codex-default", model_type="stub")
        if not self.config.model_name:
            self.config.model_name = "codex-default"
        self.model_name = self.config.model_name
        self.model: Optional[Dict[str, Any]] = None
        self.total_requests = 0
        self.prediction_count = 0
        self.rate_limiter: RateLimiter = RateLimiter()
        self.load_errors: list[str] = []
        self.start_time = time.time()
        self._embedding_dim = 16

    def load_model(self) -> Dict[str, Any]:
        try:
            if self.config.model_type not in {"stub", "huggingface", "onnx"}:
                raise ModelLoadError("Unsupported model type")

            if self.config.model_type in {"huggingface", "onnx"}:
                if not self.config.model_path or not Path(self.config.model_path).exists():
                    raise ModelLoadError("Model path does not exist")

            if self.model is None:
                self.model = {
                    "type": self.config.model_type,
                    "name": self.model_name,
                    "path": self.config.model_path,
                }
            return self.model
        except Exception as exc:
            self.load_errors.append(str(exc))
            raise

    def predict(self, inputs: List[str]) -> List[Dict[str, Any]]:
        if self.model is None:
            raise RuntimeError("Model not loaded")
        self.total_requests += 1
        self.prediction_count += len(inputs)
        # Minimal stub prediction payload
        return [
            {"label": f"label-{idx}", "score": 1.0, "text": text, "model": self.model_name}
            for idx, text in enumerate(inputs)
        ]

    def embed(self, texts: List[str]):
        if self.model is None:
            raise RuntimeError("Model not loaded")
        import numpy as np  # type: ignore

        if not texts:
            return np.zeros((0, self._embedding_dim), dtype=np.float32)

        _MAX_SEED_VALUE = 2**32
        embeddings = []
        for text in texts:
            seed = abs(hash(text)) % _MAX_SEED_VALUE
            rng = np.random.default_rng(seed)
            vec = rng.random(self._embedding_dim, dtype=np.float32)
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            embeddings.append(vec)
        return np.vstack(embeddings)

    def health_check(self) -> Dict[str, Any]:
        loaded = self.model is not None
        return {
            "status": "healthy" if loaded else "unhealthy",
            "model_loaded": loaded,
            "model_type": self.config.model_type,
            "device": self.config.device,
            "total_requests": self.total_requests,
            "uptime_seconds": time.time() - self.start_time,
            "load_errors": list(self.load_errors),
        }


if FASTAPI_AVAILABLE:

    class PredictionRequest(BaseModel):
        inputs: List[str] = Field(...)
        model_name: Optional[str] = Field(default=None)

    class PredictionResponse(BaseModel):
        predictions: List[Any]
        model_name: str
        inference_time_ms: float
        metadata: Optional[Dict[str, Any]] = None

    def _validate_payload(inputs: List[str]) -> None:
        if not inputs:
            raise HTTPException(status_code=400, detail="Inputs cannot be empty")
        if len(inputs) > MAX_BATCH_SIZE:
            raise HTTPException(status_code=400, detail="Batch size exceeds limit")
        if any(len(text) > MAX_INPUT_LENGTH for text in inputs):
            raise HTTPException(status_code=400, detail="Input length exceeds limit")

    def create_app() -> FastAPI:
        app = FastAPI()
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        server = ModelServer()
        limiter = server.rate_limiter
        start_time = time.time()

        # Load the model early so integration tests hit a ready server.
        try:
            server.load_model()
        except Exception as exc:  # pragma: no cover - surfaced via API if needed
            logger.warning("Model preload failed: %s", exc)

        @app.get("/")
        def root():
            return {"service": "codex-inference", "version": "0.1"}

        @app.get("/health")
        def health():
            return {"status": "healthy", "uptime": time.time() - start_time}

        @app.get("/metrics")
        def metrics():
            return {
                "request_count": server.total_requests,
                "prediction_count": server.prediction_count,
            }

        @app.post("/predict", response_model=PredictionResponse)
        def predict(request: PredictionRequest, http_request: Request):
            client_key = (
                http_request.client.host if getattr(http_request, "client", None) else "global"
            )
            if not limiter.is_allowed(client_key):
                raise HTTPException(status_code=429, detail="Rate limit exceeded")

            _validate_payload(request.inputs)

            t0 = time.time()
            if server.model is None:
                server.load_model()
            preds = server.predict(request.inputs)
            return PredictionResponse(
                predictions=preds,
                model_name=request.model_name or server.model_name,
                inference_time_ms=(time.time() - t0) * 1000,
                metadata={"model_type": server.config.model_type},
            )

        return app

else:

    def create_app():  # pragma: no cover
        raise ImportError("FastAPI not installed")
