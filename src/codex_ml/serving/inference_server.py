"""
FastAPI Inference Serving Layer

Provides ML model serving capabilities with safeguards:
- Rate limiting
- Input validation
- Health checks
- Metrics collection
- Error handling
"""
import logging
import os
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from fastapi import FastAPI, HTTPException, Request, status
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel, Field, validator
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    # Provide stub classes for when FastAPI is not installed
    class BaseModel:
        pass
    class FastAPI:
        pass

logger = logging.getLogger(__name__)

# Configuration
MAX_BATCH_SIZE = 100
MAX_INPUT_LENGTH = 10000
REQUEST_RATE_LIMIT = 1000  # requests per minute per IP

# Model configuration defaults
DEFAULT_MODEL_DIR = os.environ.get("CODEX_MODEL_DIR", ".codex/models")
DEFAULT_MODEL_NAME = os.environ.get("CODEX_MODEL_NAME", "default-model")
DEFAULT_MODEL_TYPE = os.environ.get("CODEX_MODEL_TYPE", "stub")  # stub, huggingface, onnx


class ModelLoadError(Exception):
    """Raised when model loading fails"""
    pass


class ModelConfig:
    """Configuration for model loading
    
    Attributes:
        model_name: Name of the model
        model_type: Type of model (stub, huggingface, onnx)
        model_path: Path to model files
        device: Device to load model on (cpu, cuda)
        config_file: Optional config file path
    """
    
    def __init__(
        self,
        model_name: str = DEFAULT_MODEL_NAME,
        model_type: str = DEFAULT_MODEL_TYPE,
        model_path: Optional[str] = None,
        device: str = "cpu",
        config_file: Optional[str] = None,
    ):
        self.model_name = model_name
        self.model_type = model_type
        self.model_path = model_path or os.path.join(DEFAULT_MODEL_DIR, model_name)
        self.device = device
        self.config_file = config_file
        
    @classmethod
    def from_env(cls) -> "ModelConfig":
        """Create config from environment variables"""
        return cls(
            model_name=os.environ.get("CODEX_MODEL_NAME", DEFAULT_MODEL_NAME),
            model_type=os.environ.get("CODEX_MODEL_TYPE", DEFAULT_MODEL_TYPE),
            model_path=os.environ.get("CODEX_MODEL_PATH"),
            device=os.environ.get("CODEX_MODEL_DEVICE", "cpu"),
            config_file=os.environ.get("CODEX_MODEL_CONFIG"),
        )
    
    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> "ModelConfig":
        """Create config from dictionary"""
        return cls(
            model_name=config.get("model_name", DEFAULT_MODEL_NAME),
            model_type=config.get("model_type", DEFAULT_MODEL_TYPE),
            model_path=config.get("model_path"),
            device=config.get("device", "cpu"),
            config_file=config.get("config_file"),
        )
    
    def validate(self) -> None:
        """Validate configuration
        
        Raises:
            ValueError: If configuration is invalid
        """
        if not self.model_name:
            raise ValueError("model_name cannot be empty")
        
        if self.model_type not in ["stub", "huggingface", "onnx"]:
            raise ValueError(f"Unsupported model_type: {self.model_type}")
        
        if self.device not in ["cpu", "cuda"]:
            raise ValueError(f"Unsupported device: {self.device}")
        
        # For non-stub models, path should exist or be valid
        if self.model_type != "stub" and self.model_path:
            path = Path(self.model_path)
            if not path.exists() and not path.parent.exists():
                logger.warning(f"Model path does not exist: {self.model_path}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "model_name": self.model_name,
            "model_type": self.model_type,
            "model_path": self.model_path,
            "device": self.device,
            "config_file": self.config_file,
        }


if FASTAPI_AVAILABLE:
    class PredictionRequest(BaseModel):
        """Request model for predictions"""
        inputs: List[str] = Field(..., description="List of input texts")
        parameters: Optional[Dict[str, Any]] = Field(default=None, description="Model parameters")
        
        @validator('inputs')
        def validate_inputs(cls, v):
            """Validate inputs"""
            if not v:
                raise ValueError("Inputs cannot be empty")
            if len(v) > MAX_BATCH_SIZE:
                raise ValueError(f"Batch size cannot exceed {MAX_BATCH_SIZE}")
            for inp in v:
                if len(inp) > MAX_INPUT_LENGTH:
                    raise ValueError(f"Input length cannot exceed {MAX_INPUT_LENGTH}")
            return v


    class PredictionResponse(BaseModel):
        """Response model for predictions"""
        predictions: List[Any]
        model_name: str
        inference_time_ms: float
        metadata: Optional[Dict[str, Any]] = None


    class HealthResponse(BaseModel):
        """Health check response"""
        status: str
        model_loaded: bool
        uptime_seconds: float
        total_requests: int


class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self, max_requests: int = REQUEST_RATE_LIMIT, window_seconds: int = 60):
        """
        Initialize rate limiter
        
        Args:
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> bool:
        """
        Check if request is allowed
        
        Args:
            client_id: Client identifier (e.g., IP address)
            
        Returns:
            True if request is allowed, False otherwise
        """
        now = time.time()
        cutoff = now - self.window_seconds
        
        # Remove old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > cutoff
        ]
        
        # Check limit
        if len(self.requests[client_id]) >= self.max_requests:
            return False
        
        # Add current request
        self.requests[client_id].append(now)
        return True


class ModelServer:
    """Base model server with safeguards and real model loading"""
    
    def __init__(self, config: Optional[ModelConfig] = None):
        """
        Initialize model server
        
        Args:
            config: Model configuration (defaults to environment-based config)
        """
        self.config = config or ModelConfig.from_env()
        self.config.validate()
        
        self.model_name = self.config.model_name
        self.model = None
        self.start_time = time.time()
        self.total_requests = 0
        self.rate_limiter = RateLimiter()
        self.load_errors: List[str] = []
        
        logger.info(f"Initialized ModelServer for: {self.model_name}")
        logger.info(f"Model config: {self.config.to_dict()}")
    
    def _load_stub_model(self) -> Dict[str, Any]:
        """Load a stub model for testing"""
        logger.info("Loading stub model")
        return {
            "type": "stub",
            "name": self.config.model_name,
            "device": self.config.device,
        }
    
    def _load_huggingface_model(self) -> Any:
        """Load a HuggingFace model
        
        Returns:
            Loaded model object
            
        Raises:
            ModelLoadError: If loading fails
        """
        try:
            from transformers import AutoModel, AutoTokenizer
        except ImportError:
            raise ModelLoadError(
                "transformers not installed. Install with: pip install transformers"
            )
        
        try:
            logger.info(f"Loading HuggingFace model from: {self.config.model_path}")
            
            # Check if path exists
            model_path = Path(self.config.model_path)
            if not model_path.exists():
                raise ModelLoadError(f"Model path does not exist: {self.config.model_path}")
            
            # Load tokenizer and model
            tokenizer = AutoTokenizer.from_pretrained(str(model_path))
            model = AutoModel.from_pretrained(str(model_path))
            
            logger.info(f"Successfully loaded HuggingFace model: {self.config.model_name}")
            
            return {
                "type": "huggingface",
                "name": self.config.model_name,
                "model": model,
                "tokenizer": tokenizer,
                "device": self.config.device,
            }
        except Exception as e:
            error_msg = f"Failed to load HuggingFace model: {str(e)}"
            logger.error(error_msg)
            raise ModelLoadError(error_msg) from e
    
    def _load_onnx_model(self) -> Any:
        """Load an ONNX model
        
        Returns:
            Loaded model object
            
        Raises:
            ModelLoadError: If loading fails
        """
        try:
            import onnxruntime as ort
        except ImportError:
            raise ModelLoadError(
                "onnxruntime not installed. Install with: pip install onnxruntime"
            )
        
        try:
            logger.info(f"Loading ONNX model from: {self.config.model_path}")
            
            # Check if path exists
            model_path = Path(self.config.model_path)
            if not model_path.exists():
                raise ModelLoadError(f"Model path does not exist: {self.config.model_path}")
            
            # Create inference session
            session = ort.InferenceSession(str(model_path))
            
            logger.info(f"Successfully loaded ONNX model: {self.config.model_name}")
            
            return {
                "type": "onnx",
                "name": self.config.model_name,
                "session": session,
                "device": self.config.device,
            }
        except Exception as e:
            error_msg = f"Failed to load ONNX model: {str(e)}"
            logger.error(error_msg)
            raise ModelLoadError(error_msg) from e
    
    def load_model(self) -> Any:
        """Load the model based on configuration
        
        Returns:
            Loaded model object
            
        Raises:
            ModelLoadError: If loading fails
        """
        try:
            if self.config.model_type == "stub":
                self.model = self._load_stub_model()
            elif self.config.model_type == "huggingface":
                self.model = self._load_huggingface_model()
            elif self.config.model_type == "onnx":
                self.model = self._load_onnx_model()
            else:
                raise ModelLoadError(f"Unsupported model type: {self.config.model_type}")
            
            logger.info("Model loaded successfully")
            return self.model
            
        except ModelLoadError:
            raise
        except Exception as e:
            error_msg = f"Unexpected error loading model: {str(e)}"
            logger.error(error_msg)
            self.load_errors.append(error_msg)
            raise ModelLoadError(error_msg) from e
    
    def predict(self, inputs: List[str], parameters: Optional[Dict[str, Any]] = None) -> List[Any]:
        """
        Make predictions
        
        Args:
            inputs: List of input texts
            parameters: Optional model parameters
            
        Returns:
            List of predictions with standardized structure
            
        Raises:
            RuntimeError: If model not loaded
        """
        if not self.model:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        model_type = self.model.get("type", "unknown")
        
        if model_type == "stub":
            # Stub implementation: return dummy predictions
            predictions = [
                {
                    "text": inp,
                    "label": "POSITIVE",
                    "score": 0.95 + (i * 0.01) % 0.05,
                    "model": self.model_name,
                }
                for i, inp in enumerate(inputs)
            ]
        elif model_type == "huggingface":
            # HuggingFace model inference
            predictions = self._predict_huggingface(inputs, parameters)
        elif model_type == "onnx":
            # ONNX model inference
            predictions = self._predict_onnx(inputs, parameters)
        else:
            raise RuntimeError(f"Unknown model type: {model_type}")
        
        return predictions
    
    def _predict_huggingface(
        self, inputs: List[str], parameters: Optional[Dict[str, Any]] = None
    ) -> List[Any]:
        """Run inference with HuggingFace model
        
        Args:
            inputs: List of input texts
            parameters: Optional inference parameters
            
        Returns:
            List of predictions
        """
        # Basic implementation - can be extended for specific model types
        tokenizer = self.model["tokenizer"]
        model = self.model["model"]
        
        # Tokenize inputs
        encoded = tokenizer(
            inputs,
            padding=True,
            truncation=True,
            return_tensors="pt",
            max_length=MAX_INPUT_LENGTH,
        )
        
        # Run inference
        import torch
        with torch.no_grad():
            outputs = model(**encoded)
        
        # Format predictions (basic structure)
        predictions = [
            {
                "text": inp,
                "embedding": outputs.last_hidden_state[i, 0, :].tolist()[:10],  # First 10 dims
                "model": self.model_name,
            }
            for i, inp in enumerate(inputs)
        ]
        
        return predictions
    
    def _predict_onnx(
        self, inputs: List[str], parameters: Optional[Dict[str, Any]] = None
    ) -> List[Any]:
        """Run inference with ONNX model
        
        Args:
            inputs: List of input texts
            parameters: Optional inference parameters
            
        Returns:
            List of predictions
        """
        # Basic ONNX inference - needs tokenization
        session = self.model["session"]
        
        # For now, return stub predictions
        # Real implementation would need proper tokenization
        logger.warning("ONNX inference not fully implemented - returning stub predictions")
        predictions = [
            {
                "text": inp,
                "label": "POSITIVE",
                "score": 0.90,
                "model": self.model_name,
            }
            for inp in inputs
        ]
        
        return predictions
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        return {
            "status": "healthy" if self.model else "unhealthy",
            "model_loaded": self.model is not None,
            "uptime_seconds": time.time() - self.start_time,
            "total_requests": self.total_requests,
            "model_name": self.model_name,
            "model_type": self.config.model_type,
            "device": self.config.device,
            "load_errors": self.load_errors,
        }


def create_app(config: Optional[ModelConfig] = None):
    """
    Create FastAPI application with safeguards
    
    Args:
        config: Model configuration (defaults to environment-based config)
        
    Returns:
        Configured FastAPI application or None if FastAPI not available
    """
    if not FASTAPI_AVAILABLE:
        raise ImportError(
            "FastAPI is not installed. Install with: pip install fastapi uvicorn"
        )
    
    app = FastAPI(
        title="Codex ML Inference Server",
        description="ML model serving with safeguards and rate limiting",
        version="1.0.0",
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize model server
    server = ModelServer(config=config)
    
    # Try to load model on startup
    try:
        server.load_model()
    except ModelLoadError as e:
        logger.warning(f"Failed to load model on startup: {e}")
        logger.warning("Server will start but predictions will fail until model is loaded")
    
    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        """Rate limiting middleware"""
        client_ip = request.client.host if request.client else "unknown"
        
        if not server.rate_limiter.is_allowed(client_ip):
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Rate limit exceeded. Try again later."},
            )
        
        response = await call_next(request)
        return response
    
    @app.get("/health", response_model=HealthResponse)
    async def health():
        """Health check endpoint"""
        health_status = server.health_check()
        return HealthResponse(**health_status)
    
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "message": "Codex ML Inference Server",
            "model": server.model_name,
            "endpoints": {
                "health": "/health",
                "predict": "/predict (POST)",
                "metrics": "/metrics",
            }
        }
    
    @app.post("/predict", response_model=PredictionResponse)
    async def predict(request: PredictionRequest):
        """
        Prediction endpoint
        
        Args:
            request: Prediction request with inputs and parameters
            
        Returns:
            Predictions with metadata
        """
        try:
            # Track request
            server.total_requests += 1
            
            # Perform inference
            start_time = time.time()
            predictions = server.predict(request.inputs, request.parameters)
            inference_time = (time.time() - start_time) * 1000  # Convert to ms
            
            return PredictionResponse(
                predictions=predictions,
                model_name=server.model_name,
                inference_time_ms=inference_time,
                metadata={
                    "batch_size": len(request.inputs),
                    "total_requests": server.total_requests,
                }
            )
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Prediction failed: {str(e)}"
            )
    
    @app.get("/metrics")
    async def metrics():
        """Metrics endpoint"""
        return {
            "total_requests": server.total_requests,
            "uptime_seconds": time.time() - server.start_time,
            "model_name": server.model_name,
            "model_loaded": server.model is not None,
        }
    
    return app


def main():
    """Run the server"""
    if not FASTAPI_AVAILABLE:
        print("Error: FastAPI is not installed. Install with: pip install fastapi uvicorn")
        return 1
    
    import uvicorn
    
    # Create config from environment
    config = ModelConfig.from_env()
    logger.info(f"Starting server with config: {config.to_dict()}")
    
    app = create_app(config=config)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
