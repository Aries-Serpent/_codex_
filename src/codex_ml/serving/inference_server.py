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
import time
from collections import defaultdict
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
    """Base model server with safeguards"""
    
    def __init__(self, model_name: str = "default-model"):
        """
        Initialize model server
        
        Args:
            model_name: Name of the model to serve
        """
        self.model_name = model_name
        self.model = None
        self.start_time = time.time()
        self.total_requests = 0
        self.rate_limiter = RateLimiter()
        logger.info(f"Initialized ModelServer for: {model_name}")
    
    def load_model(self, model_name: Optional[str] = None):
        """Load the model (stub implementation)
        
        Args:
            model_name: Optional model name to load (defaults to self.model_name)
        """
        model_to_load = model_name if model_name else self.model_name
        logger.info(f"Loading model: {model_to_load}")
        # Stub: In real implementation, load actual model here
        self.model = {"type": "stub", "name": model_to_load}
        logger.info("Model loaded successfully")
        return self.model
    
    def predict(self, inputs: List[str], parameters: Optional[Dict[str, Any]] = None) -> List[Any]:
        """
        Make predictions
        
        Args:
            inputs: List of input texts
            parameters: Optional model parameters
            
        Returns:
            List of predictions
        """
        if not self.model:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        # Stub implementation: return dummy predictions
        # In real implementation, call actual model inference
        predictions = [
            {"label": "POSITIVE", "score": 0.95 + i * 0.01}
            for i in range(len(inputs))
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
        }


def create_app(model_name: str = "default-model"):
    """
    Create FastAPI application with safeguards
    
    Args:
        model_name: Name of the model to serve
        
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
    server = ModelServer(model_name=model_name)
    server.load_model()
    
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
    
    app = create_app(model_name="codex-model-v1")
    
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
