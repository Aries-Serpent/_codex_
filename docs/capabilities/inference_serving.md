# Inference Serving

## Overview

The inference serving capability provides production-ready model serving infrastructure including FastAPI/Flask endpoints, batch inference, model versioning, and high-performance prediction APIs for deploying ML models.

**Keywords**: inference, serving, api, predict, fastapi, flask, model-serving, endpoint, batch, streaming, grpc

## Purpose

Provides inference serving through:
- **REST APIs**: FastAPI/Flask prediction endpoints
- **Batch Inference**: High-throughput batch predictions
- **Model Versioning**: A/B testing and model switching
- **Streaming**: Real-time prediction streaming
- **Load Balancing**: Distribute requests across instances
- **Caching**: Cache predictions for repeated inputs

## Architecture

### Serving Layers

```
┌─────────────────────────────────────┐
│   Load Balancer                     │
│   (nginx, HAProxy, cloud LB)        │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│   API Gateway                       │
│   (Rate limiting, auth, routing)    │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│   Inference Server                  │
│   (FastAPI, Flask, gRPC)            │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│   Model Runtime                     │
│   (PyTorch, TensorFlow, ONNX)       │
└─────────────────────────────────────┘
```

## Configuration

### FastAPI Server Configuration

```python
# config/serving.py
from pydantic import BaseSettings

class ServingConfig(BaseSettings):
    """
    Inference serving configuration.
    
    Safeguard: Validates all settings.
    """
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8080
    workers: int = 4
    
    # Model settings
    model_path: str = "models/production"
    model_version: str = "latest"
    
    # Performance
    max_batch_size: int = 32
    timeout_seconds: float = 30.0
    
    # Safeguards
    max_request_size_mb: int = 10
    rate_limit_per_minute: int = 1000
    
    class Config:
        env_prefix = "INFERENCE_"
```

### YAML Configuration

```yaml
# config/inference.yaml
server:
  host: 0.0.0.0
  port: 8080
  workers: 4

model:
  path: models/production
  version: v1.2.0
  device: cuda
  precision: fp16

performance:
  max_batch_size: 64
  batch_timeout_ms: 50
  inference_timeout_s: 30

safeguards:
  max_request_size_mb: 10
  rate_limit:
    enabled: true
    requests_per_minute: 1000
  input_validation:
    enabled: true
    max_sequence_length: 512
```

## Implementation

### FastAPI Inference Server

```python
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, validator
from typing import List, Optional
import torch

app = FastAPI(title="Codex ML Inference API")

class PredictionRequest(BaseModel):
    """
    Request model for predictions.
    
    Safeguard: Validates input data.
    """
    inputs: List[float]
    model_version: Optional[str] = None
    
    @validator("inputs")
    def validate_inputs(cls, v):
        """Validate input bounds."""
        if len(v) == 0:
            raise ValueError("inputs cannot be empty")
        if len(v) > 10000:
            raise ValueError("inputs exceeds maximum length")
        return v

class PredictionResponse(BaseModel):
    """Response model for predictions."""
    predictions: List[float]
    model_version: str
    latency_ms: float

class ModelManager:
    """
    Manage model loading and inference.
    
    Safeguard: Thread-safe model access.
    """
    
    def __init__(self):
        self._model = None
        self._version = None
        self._lock = threading.Lock()
    
    def load_model(self, path: str, version: str) -> None:
        """
        Load model from path.
        
        Safeguard: Validates model path exists.
        Timeout: Model loading timeout.
        """
        if not Path(path).exists():
            raise ValueError(f"Model path not found: {path}")
        
        with self._lock:
            self._model = torch.jit.load(path)
            self._model.eval()
            self._version = version
    
    def predict(self, inputs: torch.Tensor) -> torch.Tensor:
        """
        Run inference.
        
        Safeguard: Validates model is loaded.
        """
        if self._model is None:
            raise RuntimeError("Model not loaded")
        
        with torch.no_grad():
            return self._model(inputs)
    
    @property
    def version(self) -> str:
        return self._version or "unknown"

model_manager = ModelManager()

@app.on_event("startup")
async def startup():
    """Load model on startup."""
    model_manager.load_model("models/production/model.pt", "v1.0.0")

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest) -> PredictionResponse:
    """
    Make predictions.
    
    Safeguard: Validates input and handles errors.
    Rate-limit: Applied via middleware.
    """
    import time
    start = time.time()
    
    try:
        # Convert to tensor
        inputs = torch.tensor(request.inputs).unsqueeze(0)
        
        # Run inference
        predictions = model_manager.predict(inputs)
        
        latency = (time.time() - start) * 1000
        
        return PredictionResponse(
            predictions=predictions.squeeze().tolist(),
            model_version=model_manager.version,
            latency_ms=latency,
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/healthz")
async def health():
    """
    Health check endpoint.
    
    Safeguard: Validates model is ready.
    """
    if model_manager._model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "healthy", "model_version": model_manager.version}
```

### Batch Inference

```python
from typing import List
import asyncio
from collections import defaultdict

class BatchInferenceServer:
    """
    Batch inference server with request coalescing.
    
    Safeguard: Limits batch size.
    Timeout: Batch timeout for latency control.
    """
    
    def __init__(
        self,
        model: torch.nn.Module,
        max_batch_size: int = 32,
        batch_timeout_ms: float = 50.0,
    ):
        self.model = model
        self.max_batch_size = max_batch_size
        self.batch_timeout = batch_timeout_ms / 1000
        self.pending_requests = []
        self._lock = asyncio.Lock()
    
    async def predict(self, inputs: List[float]) -> List[float]:
        """
        Add request to batch and wait for result.
        
        Safeguard: Validates input length.
        """
        if len(inputs) > 10000:
            raise ValueError("Input too large")
        
        future = asyncio.Future()
        
        async with self._lock:
            self.pending_requests.append((inputs, future))
            
            # Process batch if full
            if len(self.pending_requests) >= self.max_batch_size:
                await self._process_batch()
        
        # Wait for result with timeout
        try:
            result = await asyncio.wait_for(future, timeout=30.0)
            return result
        except asyncio.TimeoutError:
            raise RuntimeError("Inference timeout")
    
    async def _process_batch(self):
        """Process pending batch."""
        if not self.pending_requests:
            return
        
        requests = self.pending_requests[:self.max_batch_size]
        self.pending_requests = self.pending_requests[self.max_batch_size:]
        
        # Build batch tensor
        inputs = [r[0] for r in requests]
        futures = [r[1] for r in requests]
        
        batch = torch.tensor(inputs)
        
        # Run inference
        with torch.no_grad():
            outputs = self.model(batch)
        
        # Send results
        for i, future in enumerate(futures):
            future.set_result(outputs[i].tolist())
```

## Usage Examples

### Example 1: Run Inference Server

```bash
# Start server with uvicorn
uvicorn app:app --host 0.0.0.0 --port 8080 --workers 4

# Or with gunicorn for production
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8080
```

### Example 2: Make Predictions

```python
import requests

# Single prediction
response = requests.post(
    "http://localhost:8080/predict",
    json={"inputs": [1.0, 2.0, 3.0, 4.0]}
)
print(response.json())
# {"predictions": [0.5, 0.3], "model_version": "v1.0.0", "latency_ms": 5.2}

# Batch predictions
batch_response = requests.post(
    "http://localhost:8080/predict/batch",
    json={"batch": [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]}
)
print(batch_response.json())
```

### Example 3: gRPC Inference

```python
# inference.proto
"""
syntax = "proto3";

service InferenceService {
    rpc Predict (PredictRequest) returns (PredictResponse);
    rpc PredictStream (stream PredictRequest) returns (stream PredictResponse);
}

message PredictRequest {
    repeated float inputs = 1;
    string model_version = 2;
}

message PredictResponse {
    repeated float predictions = 1;
    string model_version = 2;
    float latency_ms = 3;
}
"""

# grpc_server.py
import grpc
from concurrent import futures
import inference_pb2
import inference_pb2_grpc

class InferenceServicer(inference_pb2_grpc.InferenceServiceServicer):
    """
    gRPC inference servicer.
    
    Safeguard: Validates requests.
    """
    
    def Predict(self, request, context):
        """Handle single prediction."""
        inputs = torch.tensor(list(request.inputs))
        
        with torch.no_grad():
            outputs = model(inputs)
        
        return inference_pb2.PredictResponse(
            predictions=outputs.tolist(),
            model_version="v1.0.0",
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    inference_pb2_grpc.add_InferenceServiceServicer_to_server(
        InferenceServicer(), server
    )
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()
```

### Example 4: Streaming Inference

```python
from fastapi import WebSocket
from fastapi.responses import StreamingResponse

@app.websocket("/predict/stream")
async def predict_stream(websocket: WebSocket):
    """
    WebSocket endpoint for streaming predictions.
    
    Safeguard: Connection timeout.
    Rate-limit: Max messages per second.
    """
    await websocket.accept()
    
    try:
        while True:
            # Receive input
            data = await asyncio.wait_for(
                websocket.receive_json(),
                timeout=60.0  # Timeout safeguard
            )
            
            # Validate input
            if "inputs" not in data:
                await websocket.send_json({"error": "Missing inputs"})
                continue
            
            # Run inference
            inputs = torch.tensor(data["inputs"])
            with torch.no_grad():
                outputs = model(inputs)
            
            await websocket.send_json({
                "predictions": outputs.tolist()
            })
    
    except asyncio.TimeoutError:
        await websocket.close(code=1000, reason="Timeout")
    except Exception as e:
        await websocket.close(code=1011, reason=str(e))
```

### Example 5: Model A/B Testing

```python
from typing import Dict
import random

class ABTestingServer:
    """
    A/B testing for model versions.
    
    Safeguard: Validates model versions exist.
    """
    
    def __init__(self):
        self.models: Dict[str, torch.nn.Module] = {}
        self.traffic_split: Dict[str, float] = {}
    
    def register_model(self, version: str, model: torch.nn.Module, traffic: float):
        """Register model with traffic split."""
        if traffic < 0 or traffic > 1:
            raise ValueError("Traffic must be between 0 and 1")
        
        self.models[version] = model
        self.traffic_split[version] = traffic
    
    def predict(self, inputs: torch.Tensor) -> tuple:
        """
        Route prediction to model based on traffic split.
        
        Returns tuple of (predictions, model_version).
        """
        # Select model based on traffic split
        rand = random.random()
        cumulative = 0.0
        
        for version, traffic in self.traffic_split.items():
            cumulative += traffic
            if rand <= cumulative:
                model = self.models[version]
                with torch.no_grad():
                    outputs = model(inputs)
                return outputs, version
        
        # Fallback to first model
        version = list(self.models.keys())[0]
        model = self.models[version]
        with torch.no_grad():
            outputs = model(inputs)
        return outputs, version
```

## Safeguards

### Input Validation

```python
def validate_inference_input(inputs: List[float], max_length: int = 10000) -> None:
    """
    Validate inference input.
    
    Safeguard: Prevents malformed or oversized inputs.
    Bounds: Limits input size.
    """
    if not inputs:
        raise ValueError("Input cannot be empty")
    
    if len(inputs) > max_length:
        raise ValueError(f"Input exceeds max length {max_length}")
    
    for val in inputs:
        if not isinstance(val, (int, float)):
            raise TypeError("Input must contain only numbers")
        if math.isnan(val) or math.isinf(val):
            raise ValueError("Input contains NaN or Inf")
```

### Rate Limiting

```python
from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/predict")
@limiter.limit("100/minute")  # Rate limit safeguard
async def predict(request: Request, body: PredictionRequest):
    pass
```

### Timeout Handling

```python
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("Inference timeout")

def predict_with_timeout(model, inputs, timeout_seconds: float = 30.0):
    """
    Run inference with timeout.
    
    Safeguard: Prevents hanging requests.
    Timeout: Raises after timeout_seconds.
    """
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(int(timeout_seconds))
    
    try:
        with torch.no_grad():
            return model(inputs)
    finally:
        signal.alarm(0)
```

## Best Practices

1. **Input Validation**: Always validate input data types and bounds
2. **Batch Requests**: Use batching for high-throughput scenarios
3. **Model Versioning**: Tag and version all production models
4. **Health Checks**: Implement `/healthz` and `/ready` endpoints
5. **Rate Limiting**: Protect against abuse with rate limits
6. **Timeouts**: Set inference timeouts to prevent hangs
7. **Monitoring**: Track latency, throughput, and error rates
8. **Graceful Shutdown**: Handle shutdown signals properly

## Troubleshooting

### High Latency

```python
# Profile inference
import torch.profiler

with torch.profiler.profile() as prof:
    outputs = model(inputs)
print(prof.key_averages().table())

# Check for CPU/GPU sync issues
torch.cuda.synchronize()
```

### Out of Memory

```python
# Clear CUDA cache
torch.cuda.empty_cache()

# Use smaller batch size
MAX_BATCH_SIZE = 16

# Enable gradient checkpointing for large models
model.gradient_checkpointing_enable()
```

## Related Capabilities

- [Deployment Infrastructure](deployment_infrastructure.md) - Container deployment
- [MCP Protocol Surface](mcp_protocol_surface.md) - API design patterns
- [Status Reporting](status_reporting.md) - Monitoring metrics

## References

- FastAPI Documentation: https://fastapi.tiangolo.com/
- PyTorch Serving: https://pytorch.org/serve/
- gRPC Python: https://grpc.io/docs/languages/python/
