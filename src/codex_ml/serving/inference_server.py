"""Lightweight inference server scaffolding used by integration tests."""

from __future__ import annotations

import logging
import os
import secrets
import time
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from fastapi import FastAPI, HTTPException, Request, Security
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.security import APIKeyHeader
    from pydantic import BaseModel, Field

    FASTAPI_AVAILABLE = True
except ImportError:  # pragma: no cover
    FASTAPI_AVAILABLE = False
    FastAPI = None
    HTTPException = Exception
    BaseModel = object
    APIKeyHeader = None
    Security = None

    def Field(*a, **k):
        return None

    Request = object

logger = logging.getLogger(__name__)

MAX_BATCH_SIZE = 100
MAX_INPUT_LENGTH = 10000
_MAX_EMBEDDING_SEED = 2**32
REQUEST_RATE_LIMIT = 1000

# API Key Security
API_KEY_NAME = "X-API-Key"
API_KEY_HEADER = APIKeyHeader(name=API_KEY_NAME, auto_error=False) if FASTAPI_AVAILABLE else None


class ModelLoadError(Exception):
    """Raised when a model cannot be loaded."""


class AuthenticationError(Exception):
    """Raised when authentication fails."""


class AuthManager:
    """API key authentication manager with JWT support

    Attributes:
        api_keys: Set of valid API keys
        jwt_secret: Secret key for JWT validation (optional)
        jwt_algorithm: Algorithm for JWT validation
    """

    def __init__(
        self,
        api_keys: Optional[List[str]] = None,
        jwt_secret: Optional[str] = None,
        jwt_algorithm: str = "HS256",
    ):
        """Initialize authentication manager

        Args:
            api_keys: List of valid API keys (None = allow all)
            jwt_secret: Secret for JWT validation (None = JWT disabled)
            jwt_algorithm: JWT algorithm (default: HS256)
        """
        self.api_keys = set(api_keys) if api_keys else None
        self.jwt_secret = jwt_secret
        self.jwt_algorithm = jwt_algorithm
        self.auth_enabled = api_keys is not None or jwt_secret is not None

        logger.info(
            f"AuthManager initialized: api_keys={len(api_keys) if api_keys else 0}, "
            f"jwt_enabled={jwt_secret is not None}"
        )

    def verify_api_key(self, api_key: Optional[str]) -> bool:
        """Verify API key

        Args:
            api_key: API key to verify

        Returns:
            True if valid or auth disabled, False otherwise
        """
        if not self.auth_enabled or self.api_keys is None:
            return True

        if not api_key:
            return False

        return api_key in self.api_keys

    def verify_jwt(self, token: str) -> Dict[str, Any]:
        """Verify JWT token

        Args:
            token: JWT token string

        Returns:
            Decoded token payload

        Raises:
            AuthenticationError: If token is invalid
        """
        if not self.jwt_secret:
            raise AuthenticationError("JWT authentication not configured")

        try:
            from jose import JWTError, jwt

            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return payload
        except ImportError as e:
           logger.debug(f"ImportError: {e}")
            logger.warning(f"ImportError: {e}", exc_info=True)
            raise AuthenticationError("python-jose not installed for JWT support")
        except JWTError as e:
            logger.debug(f"JWTError: {e}")
            raise AuthenticationError(f"Invalid JWT token: {e}")

    @staticmethod
    def generate_api_key() -> str:
        """Generate a new API key

        Returns:
            Random API key string
        """
        return secrets.token_urlsafe(32)


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

        # Initialize circuit breaker
        try:
            from codex_ml.serving.resilience import CircuitBreaker, CircuitBreakerConfig

            self.circuit_breaker = CircuitBreaker(CircuitBreakerConfig(failure_threshold=5))
            logger.info("Circuit breaker enabled")
        except ImportError as e:
           logger.debug(f"ImportError: {e}")
            logger.warning(f"ImportError: {e}", exc_info=True)
            self.circuit_breaker = None
            logger.warning("Circuit breaker not available (resilience module not found)")

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
            logger.debug(f"Exception: {exc}")
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

    def predict_with_circuit_breaker(self, inputs: List[str]) -> List[Dict[str, Any]]:
        """Predict with circuit breaker protection

        Args:
            inputs: Input texts

        Returns:
            Predictions

        Raises:
            Exception: If circuit breaker is open or prediction fails
        """
        if self.circuit_breaker:
            return self.circuit_breaker.call(self.predict, inputs)
        else:
            return self.predict(inputs)

    def embed(self, texts: List[str]):
        if self.model is None:
            raise RuntimeError("Model not loaded")
        import numpy as np

        if not texts:
            return np.zeros((0, self._embedding_dim), dtype=np.float32)

        embeddings = []
        for text in texts:
            seed = abs(hash(text)) % _MAX_EMBEDDING_SEED
            rng = np.random.default_rng(seed)
            vec = rng.random(self._embedding_dim, dtype=np.float32)
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            embeddings.append(vec)
        return np.vstack(embeddings)

    def health_check(self) -> Dict[str, Any]:
        loaded = self.model is not None
        health = {
            "status": "healthy" if loaded else "unhealthy",
            "model_loaded": loaded,
            "model_type": self.config.model_type,
            "device": self.config.device,
            "total_requests": self.total_requests,
            "uptime_seconds": time.time() - self.start_time,
            "load_errors": list(self.load_errors),
        }

        # Add circuit breaker status if available
        if self.circuit_breaker:
            cb_state = self.circuit_breaker.get_state()
            health["circuit_breaker"] = cb_state
            # Mark unhealthy if circuit is open
            if cb_state["state"] == "open":
                health["status"] = "degraded"

        return health


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

    def create_app(config: Optional[ModelConfig] = None) -> FastAPI:
        app = FastAPI(title="Codex Inference Server", version="0.2.0")
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        server = ModelServer(config=config)
        limiter = server.rate_limiter
        start_time = time.time()

        # Initialize authentication
        api_keys_env = os.getenv("CODEX_API_KEYS")
        api_keys = api_keys_env.split(",") if api_keys_env else None
        jwt_secret = os.getenv("CODEX_JWT_SECRET")
        auth_manager = AuthManager(api_keys=api_keys, jwt_secret=jwt_secret)

        # Load the model early so integration tests hit a ready server.
        try:
            server.load_model()
        except Exception as exc:  # pragma: no cover - surfaced via API if needed
            logger.warning("Model preload failed: %s", exc)

        # Setup dependencies based on auth config
        auth_dependencies = []
        if auth_manager.auth_enabled and API_KEY_HEADER:

            async def verify_auth(api_key: Optional[str] = Security(API_KEY_HEADER)) -> None:
                """Verify API key authentication"""
                if not auth_manager.verify_api_key(api_key):
                    raise HTTPException(status_code=401, detail="Invalid or missing API key")

            auth_dependencies = [Security(verify_auth)]

        @app.get("/")
        def root():
            return {
                "service": "codex-inference",
                "version": "0.2.0",
                "auth_enabled": auth_manager.auth_enabled,
            }

        @app.get("/health")
        def health():
            """Health check with circuit breaker status"""
            return server.health_check()

        @app.get("/ready")
        def readiness():
            """Readiness check"""
            health = server.health_check()
            return {
                "ready": health["status"] == "healthy",
                "model_loaded": health["model_loaded"],
                "uptime": health["uptime_seconds"],
            }

        @app.get("/live")
        def liveness():
            """Liveness check - always returns 200 if server is running"""
            return {"status": "alive", "uptime": time.time() - start_time}

        @app.get("/metrics")
        def metrics():
            """Metrics endpoint"""
            metrics_data = {
                "request_count": server.total_requests,
                "prediction_count": server.prediction_count,
            }
            # Add circuit breaker metrics if available
            if server.circuit_breaker:
                metrics_data["circuit_breaker"] = server.circuit_breaker.get_state()
            return metrics_data

        @app.post("/predict", response_model=PredictionResponse, dependencies=auth_dependencies)
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

            # Use circuit breaker if available
            try:
                preds = server.predict_with_circuit_breaker(request.inputs)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                if "Circuit breaker" in str(e):
                    raise HTTPException(status_code=503, detail=str(e))
                raise

            return PredictionResponse(
                predictions=preds,
                model_name=request.model_name or server.model_name,
                inference_time_ms=(time.time() - t0) * 1000,
                metadata={"model_type": server.config.model_type},
            )

        @app.post("/batch_infer", response_model=PredictionResponse, dependencies=auth_dependencies)
        def batch_infer(request: PredictionRequest, http_request: Request):
            """Batch inference endpoint (alias for /predict with same logic)"""
            return predict(request, http_request)

        return app

else:

    def create_app() -> None:  # pragma: no cover
        raise RuntimeError("FastAPI not installed. Install with: pip install fastapi uvicorn")
