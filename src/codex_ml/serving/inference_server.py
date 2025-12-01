"""Lightweight inference server scaffolding used by integration tests."""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from typing import Any, Dict, List, Optional

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, Field, validator

    FASTAPI_AVAILABLE = True
except ImportError:  # pragma: no cover
    FASTAPI_AVAILABLE = False
    FastAPI = None  # type: ignore
    HTTPException = Exception  # type: ignore
    BaseModel = object  # type: ignore
    Field = lambda *a, **k: None  # type: ignore
    validator = lambda *a, **k: (lambda f: f)  # type: ignore

logger = logging.getLogger(__name__)

MAX_BATCH_SIZE = 100
MAX_INPUT_LENGTH = 10000
REQUEST_RATE_LIMIT = 1000


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


class SimpleModel:
    def predict(self, inputs: List[str]) -> List[str]:
        return [text.upper() for text in inputs]


class ModelServer:
    def __init__(self) -> None:
        self.model = None

    def load_model(self) -> SimpleModel:
        if self.model is None:
            self.model = SimpleModel()
        return self.model

    def predict(self, inputs: List[str]) -> List[str]:
        model = self.load_model()
        return model.predict(inputs)


if FASTAPI_AVAILABLE:

    class PredictionRequest(BaseModel):
        inputs: List[str] = Field(...)

        @validator("inputs")
        def validate_inputs(cls, v: List[str]) -> List[str]:
            if not v:
                raise ValueError("Inputs cannot be empty")
            if len(v) > MAX_BATCH_SIZE:
                raise ValueError("Batch size cannot exceed MAX_BATCH_SIZE")
            for text in v:
                if len(text) > MAX_INPUT_LENGTH:
                    raise ValueError("Input length exceeds limit")
            return v

    class PredictionResponse(BaseModel):
        predictions: List[Any]
        model_name: str
        inference_time_ms: float
        metadata: Optional[Dict[str, Any]] = None


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
        limiter = RateLimiter()
        start_time = time.time()

        @app.get("/")
        def root():
            return {"service": "codex-inference", "version": "0.1"}

        @app.get("/health")
        def health():
            return {"status": "healthy", "uptime": time.time() - start_time}

        @app.get("/metrics")
        def metrics():
            return {"request_count": len(limiter.state)}

        @app.post("/predict", response_model=PredictionResponse)
        def predict(request: PredictionRequest):
            if not limiter.is_allowed("global"):
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            t0 = time.time()
            preds = server.predict(request.inputs)
            return PredictionResponse(
                predictions=preds,
                model_name="default",
                inference_time_ms=(time.time() - t0) * 1000,
                metadata={},
            )

        return app

else:

    def create_app():  # pragma: no cover
        raise ImportError("FastAPI not installed")

