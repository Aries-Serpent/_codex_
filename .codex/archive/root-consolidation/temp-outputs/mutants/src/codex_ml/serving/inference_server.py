"""Lightweight inference server scaffolding used by integration tests."""

from __future__ import annotations

import logging
import os
import secrets
import time
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

try:
    from fastapi import FastAPI, Header, HTTPException, Request, Security
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.security import APIKeyHeader
    from pydantic import BaseModel, Field
    from starlette.middleware.trustedhost import TrustedHostMiddleware

    FASTAPI_AVAILABLE = True
except ImportError:  # pragma: no cover
    FASTAPI_AVAILABLE = False
    FastAPI = None  # type: ignore[misc,assignment]
    HTTPException = Exception  # type: ignore[misc,assignment]
    BaseModel = object  # type: ignore[misc,assignment]
    APIKeyHeader = None  # type: ignore[misc,assignment]
    Security = None  # type: ignore[assignment]
    TrustedHostMiddleware = None  # type: ignore[misc,assignment]

    def Field(*a: Any, **k: Any) -> None:  # type: ignore[no-redef]
        return None

    Request = object  # type: ignore[misc,assignment]

logger = logging.getLogger(__name__)

MAX_BATCH_SIZE = 100
MAX_INPUT_LENGTH = 10000
_MAX_EMBEDDING_SEED = 2**32
REQUEST_RATE_LIMIT = 1000
DEFAULT_ALLOWED_ORIGINS = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8000",
    "https://localhost",
    "https://localhost:3000",
    "https://localhost:5173",
    "https://localhost:8000",
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8000",
    "https://127.0.0.1",
    "https://127.0.0.1:3000",
    "https://127.0.0.1:5173",
    "https://127.0.0.1:8000",
    "http://testserver",
]
DEFAULT_TRUSTED_HOSTS = [
    h.strip()
    for h in os.environ.get("CODEX_TRUSTED_HOSTS", "localhost,127.0.0.1,testserver").split(",")
    if h.strip()
]

# API Key Security
API_KEY_NAME = "X-API-Key"  # pragma: allowlist secret
API_KEY_HEADER = APIKeyHeader(name=API_KEY_NAME, auto_error=False) if FASTAPI_AVAILABLE else None


class ModelLoadError(Exception):
    """Raised when a model cannot be loaded."""


class AuthenticationError(Exception):
    """Raised when authentication fails."""


class AuthManager:
    """API key authentication manager with JWT support

    Attributes:
        api_keys: set of valid API keys
        jwt_secret: Secret key for JWT validation (optional)
        jwt_algorithm: Algorithm for JWT validation
    """

    def __init__(
        self,
        api_keys: Optional[list[str]] = None,
        jwt_secret: Optional[str] = None,
        jwt_algorithm: str = "HS256",
    ):
        """Initialize authentication manager

        Args:
            api_keys: list of valid API keys (None = allow all)
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

        for stored_key in self.api_keys:
            if secrets.compare_digest(stored_key, api_key):
                return True
        return False

    def verify_jwt(self, token: str) -> dict[str, Any]:
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

            return jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
        except ImportError as e:
            type(e).__name__
            logger.debug("ImportError: <ERROR_TYPE>")
            logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
            raise AuthenticationError("python-jose not installed for JWT support") from e
        except JWTError as e:
            type(e).__name__
            logger.debug("JWTError: <ERROR_TYPE>")
            raise AuthenticationError(f"Invalid JWT token: {e}") from e

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
    def from_dict(cls, data: dict[str, Any]) -> ModelConfig:
        return cls(
            model_name=data.get("model_name"),
            model_type=data.get("model_type", "stub"),
            model_path=data.get("model_path"),
            device=data.get("device", "cpu"),
        )

    @classmethod
    def from_env(cls) -> ModelConfig:
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

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_name": self.model_name,
            "model_type": self.model_type,
            "model_path": self.model_path,
            "device": self.device,
        }


@dataclass
class ServerConfig:
    """Configuration for inference server host and port."""

    host: str = field(
        default_factory=lambda: os.environ.get("CODEX_INFERENCE_SERVICE_HOST", "127.0.0.1")
    )
    port: int = field(
        default_factory=lambda: int(os.environ.get("CODEX_INFERENCE_SERVICE_PORT", "8000"))
    )

    @classmethod
    def from_env(cls) -> ServerConfig:
        """Create server config from environment variables."""
        return cls(
            host=os.environ.get("CODEX_INFERENCE_SERVICE_HOST", "127.0.0.1"),
            port=int(os.environ.get("CODEX_INFERENCE_SERVICE_PORT", "8000")),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "host": self.host,
            "port": self.port,
        }


class RateLimiter:
    def __init__(self, max_requests: int = REQUEST_RATE_LIMIT, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.state: dict[str, list[float]] = defaultdict(list)

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
        self.model: Optional[dict[str, Any]] = None
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
            type(e).__name__
            logger.debug("ImportError: <ERROR_TYPE>")
            logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
            self.circuit_breaker = None
            logger.warning("Circuit breaker not available (resilience module not found)")

    def load_model(self) -> dict[str, Any]:
        try:
            if self.config.model_type not in {"stub", "huggingface", "onnx", "local"}:
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
        except (IOError, OSError) as exc:
            type(exc).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            self.load_errors.append(str(exc))
            raise

    def predict(self, inputs: list[str]) -> list[dict[str, Any]]:
        if self.model is None:
            raise RuntimeError("Model not loaded")
        self.total_requests += 1
        self.prediction_count += len(inputs)
        results = []
        for idx, text in enumerate(inputs):
            if text == "raise-error":
                raise RuntimeError("Prediction failed")
            results.append(
                {
                    "prediction": text.upper(),
                    "label": f"label-{idx}",
                    "score": 1.0,
                    "text": text,
                    "model": self.model_name,
                }
            )
        return results

    def predict_with_circuit_breaker(self, inputs: list[str]) -> list[dict[str, Any]]:
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
        return self.predict(inputs)

    def embed(self, texts: list[str]):
        if self.model is None:
            raise RuntimeError("Model not loaded")
        try:
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
        except ImportError:
            import math
            import random

            embeddings: list[list[float]] = []  # type: ignore[no-redef]
            for text in texts:
                seed = abs(hash(text)) % _MAX_EMBEDDING_SEED
                rng = random.Random(seed)  # nosec B311 — non-cryptographic ML sampling/shuffling
                vec = [rng.random() for _ in range(self._embedding_dim)]
                norm = math.sqrt(sum(v * v for v in vec))
                if norm > 0:
                    vec = [v / norm for v in vec]
                embeddings.append(vec)
            return embeddings

    def health_check(self) -> dict[str, Any]:
        loaded = self.model is not None
        uptime = time.time() - self.start_time
        health = {
            "status": "healthy" if loaded else "unhealthy",
            "model_loaded": loaded,
            "model_type": self.config.model_type,
            "device": self.config.device,
            "total_requests": self.total_requests,
            "uptime_seconds": uptime,
            "uptime": uptime,  # Alias for backward compatibility
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
        inputs: list[str] = Field(...)
        model_name: Optional[str] = Field(default=None)

    class PredictionResponse(BaseModel):
        predictions: list[Any]
        model_name: str
        inference_time_ms: float
        metadata: Optional[dict[str, Any]] = None

    class EmbedRequest(BaseModel):
        texts: list[str] = Field(...)

    class EmbedResponse(BaseModel):
        embeddings: list[list[float]]
        num_texts: int
        model_name: str

    def _validate_payload(inputs: list[str]) -> None:
        if not inputs:
            raise HTTPException(status_code=400, detail="Inputs cannot be empty")
        if len(inputs) > MAX_BATCH_SIZE:
            raise HTTPException(status_code=400, detail="Batch size exceeds limit")
        if any(len(text) > MAX_INPUT_LENGTH for text in inputs):
            raise HTTPException(status_code=400, detail="Input length exceeds limit")

    def _validate_model_name(model_name: Optional[str]) -> None:
        """Reject model names containing path-traversal or injection sequences."""
        if model_name is None:
            return
        # Block path traversal and SQL/shell injection; allow '/' for namespaced models (e.g. org/model)  # noqa: E501
        for bad in ("..", "\\", ";", "'", '"', "<", ">"):
            if bad in model_name:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid model_name: disallowed character sequence",
                )

    def create_app(config: Optional[ModelConfig] = None) -> FastAPI:
        app = FastAPI(title="Codex Inference Server", version="0.2.0")
        allowed_origins_env = os.getenv("CODEX_ALLOWED_ORIGINS")
        allowed_origins = (
            [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]
            if allowed_origins_env
            else list(DEFAULT_ALLOWED_ORIGINS)
        )
        app.add_middleware(
            CORSMiddleware,
            allow_origins=allowed_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=DEFAULT_TRUSTED_HOSTS)

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
        except (IOError, OSError) as exc:  # pragma: no cover - surfaced via API if needed
            logger.warning("Model preload failed: %s", exc)

        # Setup dependencies based on auth config
        auth_dependencies = []
        if auth_manager.auth_enabled and API_KEY_HEADER:

            async def verify_auth(
                api_key: Optional[str] = Security(API_KEY_HEADER),
                authorization: Optional[str] = Header(default=None),
            ) -> None:
                """Verify API key or JWT authentication."""
                # JWT path: Authorization: Bearer <token>
                if auth_manager.jwt_secret and authorization:
                    scheme, _, token = authorization.partition(" ")
                    if scheme.lower() == "bearer" and token:
                        try:
                            auth_manager.verify_jwt(token)
                            return  # JWT valid
                        except AuthenticationError as exc:
                            logger.warning("Authentication failed for inference API request.")
                            raise HTTPException(status_code=401, detail="Authentication failed.") from exc
                # API key path
                if auth_manager.api_keys is not None:
                    if not auth_manager.verify_api_key(api_key):
                        raise HTTPException(status_code=401, detail="Invalid or missing API key")
                    return
                # JWT configured but no bearer token provided
                if auth_manager.jwt_secret:
                    raise HTTPException(status_code=401, detail="Authorization header required")

            auth_dependencies = [Security(verify_auth)]

        @app.get("/")
        def root() -> dict[str, Any]:
            return {
                "service": "codex-inference",
                "version": "0.2.0",
                "auth_enabled": auth_manager.auth_enabled,
            }

        @app.get("/health")
        def health() -> dict[str, Any]:
            """Health check with circuit breaker status"""
            return server.health_check()

        @app.get("/ready")
        def readiness() -> dict[str, Any]:
            """Readiness check"""
            health = server.health_check()
            return {
                "ready": health["status"] == "healthy",
                "model_loaded": health["model_loaded"],
                "uptime": health["uptime_seconds"],
            }

        @app.get("/live")
        def liveness() -> dict[str, Any]:
            """Liveness check - always returns 200 if server is running"""
            return {"status": "alive", "uptime": time.time() - start_time}

        @app.get("/metrics")
        def metrics() -> dict[str, Any]:
            """Metrics endpoint"""
            metrics_data = {
                "request_count": server.total_requests,
                "prediction_count": server.prediction_count,
            }
            # Add circuit breaker metrics if available
            if server.circuit_breaker:
                metrics_data["circuit_breaker"] = server.circuit_breaker.get_state()
            return metrics_data

        @app.post(
            "/predict",
            response_model=PredictionResponse,
            dependencies=auth_dependencies,
        )
        def predict(request: PredictionRequest, http_request: Request):
            client_key = (
                http_request.client.host if getattr(http_request, "client", None) else "global"  # type: ignore[union-attr]
            )
            if not limiter.is_allowed(client_key):
                raise HTTPException(status_code=429, detail="Rate limit exceeded")

            _validate_payload(request.inputs)
            _validate_model_name(request.model_name)

            t0 = time.time()
            if server.model is None:
                server.load_model()

            # Use circuit breaker if available
            try:
                preds = server.predict_with_circuit_breaker(request.inputs)
            except RuntimeError as e:
                logger.exception("Inference prediction failed.")
                raise HTTPException(status_code=500, detail="Prediction request failed.") from e
            except (ConnectionError, TimeoutError) as e:
                type(e).__name__
                logger.debug("Exception: <ERROR_TYPE>")
                if "Circuit breaker" in str(e):
                    raise HTTPException(status_code=503, detail="Inference service is unavailable.") from e
                raise

            return PredictionResponse(
                predictions=preds,
                model_name=request.model_name or server.model_name,
                inference_time_ms=(time.time() - t0) * 1000,
                metadata={"model_type": server.config.model_type},
            )

        @app.post(
            "/batch_infer",
            response_model=PredictionResponse,
            dependencies=auth_dependencies,
        )
        def batch_infer(request: PredictionRequest, http_request: Request):
            """Batch inference endpoint (alias for /predict with same logic)"""
            return predict(request, http_request)

        @app.post("/infer", response_model=PredictionResponse, dependencies=auth_dependencies)
        def infer(request: PredictionRequest, http_request: Request):
            """Inference endpoint (alias for /predict with same logic)"""
            return predict(request, http_request)

        @app.post(
            "/embed",
            response_model=EmbedResponse,
            dependencies=auth_dependencies,
        )
        def embed(request: EmbedRequest, http_request: Request):
            """Text embedding endpoint."""
            if server.model is None:
                server.load_model()
            try:
                vecs = server.embed(request.texts)
                embeddings = vecs.tolist() if hasattr(vecs, "tolist") else [list(v) for v in vecs]
            except (ConnectionError, TimeoutError) as e:
                logger.exception("Embedding generation failed.")
                raise HTTPException(status_code=500, detail="Embedding request failed.") from e
            return EmbedResponse(
                embeddings=embeddings,
                num_texts=len(request.texts),
                model_name=server.model_name,
            )

        return app

else:

    def create_app(config: Optional[ModelConfig] = None) -> None:  # type: ignore[misc]  # pragma: no cover
        raise RuntimeError("FastAPI not installed. Install with: pip install fastapi uvicorn")
