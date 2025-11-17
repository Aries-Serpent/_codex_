# FastAPI Inference Server - User Guide

## Overview

The FastAPI Inference Server provides ML model serving with comprehensive safeguards including rate limiting, input validation, health checks, and metrics collection.

## Features

- **Rate Limiting**: Per-IP request throttling (1000 req/min)
- **Input Validation**: Batch size and length limits with Pydantic
- **Health Checks**: Monitor server and model status
- **Metrics**: Request counts, uptime, performance tracking
- **Error Handling**: Graceful degradation and informative errors
- **Auto Documentation**: OpenAPI/Swagger UI included

## Installation

```bash
pip install fastapi uvicorn pydantic
```text

## Quick Start

### Basic Server

```python
from src.codex_ml.serving.inference_server import create_app

# Create app
app = create_app(model_name="my-model-v1")

# Run server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```text

### Start Server

```bash
# Method 1: Direct
python src/codex_ml/serving/inference_server.py

# Method 2: Uvicorn
uvicorn src.codex_ml.serving.inference_server:create_app --factory --reload

# Method 3: Custom
python -c "from src.codex_ml.serving.inference_server import create_app; import uvicorn; uvicorn.run(create_app('my-model'), port=8000)"
```text

### Make Requests

```python
import requests

# Health check
response = requests.get("http://localhost:8000/health")
print(response.json())
# {"status": "healthy", "model_loaded": true, "uptime_seconds": 42.5, ...}

# Prediction
data = {
    "inputs": ["Hello world", "Another input"],
    "parameters": {"temperature": 0.7}
}
response = requests.post("http://localhost:8000/predict", json=data)
results = response.json()
print(results["predictions"])
```text

## Configuration

### Safety Limits

```python
from src.codex_ml.serving.inference_server import (
    MAX_BATCH_SIZE,      # 100
    MAX_INPUT_LENGTH,    # 10,000
    REQUEST_RATE_LIMIT,  # 1,000 per minute
)

# These are module-level constants
# Modify before import if needed
```text

### Custom Rate Limiting

```python
from src.codex_ml.serving.inference_server import ModelServer, RateLimiter

# Custom rate limiter
server = ModelServer(model_name="my-model")
server.rate_limiter = RateLimiter(
    max_requests=500,    # Lower limit
    window_seconds=60
)
```text

### Model Loading

```python
from src.codex_ml.serving.inference_server import ModelServer

class CustomModelServer(ModelServer):
    def load_model(self):
        """Custom model loading logic"""
        import torch
        self.model = torch.load("model.pt")
        logger.info(f"Loaded custom model: {self.model_name}")
    
    def predict(self, inputs, parameters=None):
        """Custom inference logic"""
        # Your inference code here
        with torch.no_grad():
            predictions = self.model(inputs)
        return predictions.tolist()
```text

## API Endpoints

### GET /

Service information and available endpoints.

**Response:**
```json
{
  "message": "Codex ML Inference Server",
  "model": "model-name",
  "endpoints": {
    "health": "/health",
    "predict": "/predict (POST)",
    "metrics": "/metrics"
  }
}
```text

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "uptime_seconds": 123.45,
  "total_requests": 42
}
```text

### POST /predict

Inference endpoint.

**Request:**
```json
{
  "inputs": ["text1", "text2"],
  "parameters": {
    "temperature": 0.7,
    "max_length": 100
  }
}
```text

**Validation:**
- `inputs`: Required, non-empty list
- Max batch size: 100 inputs
- Max input length: 10,000 characters per input
- `parameters`: Optional dict

**Response:**
```json
{
  "predictions": [
    {"label": "POSITIVE", "score": 0.95},
    {"label": "NEGATIVE", "score": 0.87}
  ],
  "model_name": "my-model",
  "inference_time_ms": 42.5,
  "metadata": {
    "batch_size": 2,
    "total_requests": 43
  }
}
```text

**Errors:**
- `400`: Invalid input (batch size, length)
- `429`: Rate limit exceeded
- `500`: Inference error

### GET /metrics

Metrics endpoint.

**Response:**
```json
{
  "total_requests": 142,
  "uptime_seconds": 3600.5,
  "model_name": "my-model",
  "model_loaded": true
}
```text

## Rate Limiting

### How It Works

```python
from src.codex_ml.serving.inference_server import RateLimiter

limiter = RateLimiter(max_requests=10, window_seconds=60)

# Check if request allowed
if limiter.is_allowed("client_ip_address"):
    # Process request
    pass
else:
    # Return 429 Too Many Requests
    pass
```text

### Sliding Window

- Tracks requests per client (by IP)
- Removes expired requests automatically
- Independent limits per client
- Default: 1000 requests per 60 seconds

### Bypassing (for testing)

```python
# Disable rate limiting for tests
app = create_app()
app.middleware_stack = [
    m for m in app.middleware_stack
    if "rate_limit" not in str(m)
]
```text

## Input Validation

### Pydantic Models

```python
from pydantic import BaseModel, Field, validator

class PredictionRequest(BaseModel):
    inputs: List[str] = Field(..., description="Input texts")
    parameters: Optional[Dict] = None
    
    @validator('inputs')
    def validate_inputs(cls, v):
        if not v:
            raise ValueError("Inputs cannot be empty")
        if len(v) > MAX_BATCH_SIZE:
            raise ValueError(f"Batch size exceeds {MAX_BATCH_SIZE}")
        return v
```text

### Custom Validation

```python
class CustomRequest(PredictionRequest):
    @validator('inputs')
    def validate_language(cls, v):
        # Add custom validation
        for text in v:
            if not text.isascii():
                raise ValueError("Only ASCII input allowed")
        return v
```text

## Error Handling

### Common Errors

**Rate Limit Exceeded (429):**
```python
try:
    response = requests.post(url, json=data)
    response.raise_for_status()
except requests.HTTPError as e:
    if e.response.status_code == 429:
        print("Rate limited. Wait before retrying.")
        time.sleep(60)  # Wait 1 minute
```text

**Invalid Input (400):**
```python
try:
    response = requests.post(url, json=data)
    response.raise_for_status()
except requests.HTTPError as e:
    if e.response.status_code == 400:
        print(f"Invalid input: {e.response.json()['detail']}")
        # Fix input and retry
```text

**Server Error (500):**
```python
try:
    response = requests.post(url, json=data)
    response.raise_for_status()
except requests.HTTPError as e:
    if e.response.status_code == 500:
        print("Server error. Check server logs.")
        # Implement retry with backoff
```text

## Production Deployment

### With Gunicorn

```bash
# Install
pip install gunicorn

# Run with multiple workers
gunicorn -w 4 -k uvicorn.workers.UvicornWorker \
  src.codex_ml.serving.inference_server:create_app \
  --bind 0.0.0.0:8000
```text

### With Docker

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
EXPOSE 8000

CMD ["uvicorn", "src.codex_ml.serving.inference_server:create_app", \
     "--factory", "--host", "0.0.0.0", "--port", "8000"]
```text

### Environment Variables

```bash
# Set model name
export MODEL_NAME="production-model-v2"

# Run
python src/codex_ml/serving/inference_server.py
```text

## Monitoring

### Prometheus Metrics (Future)

```python
from prometheus_client import Counter, Histogram

request_counter = Counter('requests_total', 'Total requests')
latency_histogram = Histogram('request_latency', 'Request latency')

@app.post("/predict")
async def predict(request: PredictionRequest):
    request_counter.inc()
    with latency_histogram.time():
        # ... inference ...
        pass
```text

### Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Logs appear in server output
# INFO - Initialized ModelServer for: my-model
# INFO - Model loaded successfully
```text

## Testing

### Unit Tests

```python
from src.codex_ml.serving.inference_server import ModelServer, RateLimiter

def test_model_server():
    server = ModelServer("test-model")
    server.load_model()
    
    predictions = server.predict(["input1", "input2"])
    assert len(predictions) == 2

def test_rate_limiter():
    limiter = RateLimiter(max_requests=2, window_seconds=60)
    
    assert limiter.is_allowed("client1") is True
    assert limiter.is_allowed("client1") is True
    assert limiter.is_allowed("client1") is False  # Exceeded
```text

### Integration Tests

```python
from fastapi.testclient import TestClient
from src.codex_ml.serving.inference_server import create_app

client = TestClient(create_app())

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_predict():
    data = {"inputs": ["test input"]}
    response = client.post("/predict", json=data)
    assert response.status_code == 200
    assert "predictions" in response.json()
```text

## Best Practices

1. **Always validate inputs**
   ```python
   # Server handles this automatically with Pydantic
   ```

2. **Monitor rate limits**
   ```python
   # Check metrics regularly
   response = requests.get("http://localhost:8000/metrics")
   print(f"Total requests: {response.json()['total_requests']}")
   ```

3. **Handle errors gracefully**
   ```python
   try:
       result = requests.post(url, json=data).json()
   except Exception as e:
       logger.error(f"Request failed: {e}")
       result = {"error": str(e)}
   ```

4. **Use health checks**
   ```python
   # Before making requests
   health = requests.get(f"{base_url}/health").json()
   if health["status"] != "healthy":
       raise RuntimeError("Server unhealthy")
   ```

5. **Batch requests when possible**
   ```python
   # Instead of 100 single requests
   inputs_batch = ["input1", "input2", ..., "input100"]
   result = requests.post(url, json={"inputs": inputs_batch})
   ```

## Examples

See `tests/codex_ml/test_inference_server.py` for comprehensive examples.

## OpenAPI Documentation

Access auto-generated docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## Support

For issues or questions:
- Check test suite: `tests/codex_ml/test_inference_server.py`
- Review source: `src/codex_ml/serving/inference_server.py`
- Check server logs for errors
