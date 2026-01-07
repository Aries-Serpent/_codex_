# Inference Serving Guide

## Overview

The Codex ML Inference Server provides a production-ready inference serving layer with built-in safeguards, rate limiting, and support for multiple model backends.

## Features

- **Multiple Model Backends**: Support for stub (testing), HuggingFace, and ONNX models
- **Configuration Management**: Environment variables or config file-based setup
- **Rate Limiting**: Built-in request rate limiting per client
- **Input Validation**: Automatic validation of batch size and input length
- **Health Checks**: Comprehensive health monitoring endpoints
- **Error Handling**: Graceful error handling with detailed error messages
- **Metrics Collection**: Request tracking and performance metrics

## Quick Start

### Basic Setup (Stub Model)

The simplest way to get started is with a stub model for testing:

```python
from src.codex_ml.serving.inference_server import ModelServer, ModelConfig

# Create server with default stub model
config = ModelConfig(model_type="stub", model_name="my-test-model")
server = ModelServer(config=config)

# Load the model
server.load_model()

# Make predictions
predictions = server.predict(["Hello world", "Test input"])
print(predictions)
```text

The bundled `SimpleInferenceModel` is deterministic and exercises both happy-path and error-path logic:

- `/predict` echoes inputs with uppercase `prediction` fields and returns HTTP 500 for the sentinel input `"raise-error"`.
- `/embed` returns lightweight one-hot embeddings (dimension 8) keyed by character sums and raises HTTP 500 for `"raise-error"`.

### FastAPI Server

To run a full FastAPI server:

```bash
# Set environment variables
export CODEX_MODEL_NAME=my-model
export CODEX_MODEL_TYPE=stub
export CODEX_MODEL_DEVICE=cpu

# Run the server
python -m src.codex_ml.serving.inference_server
```text

The server will be available at `http://localhost:8000` with the following endpoints:

- `GET /` - Server information
- `GET /health` - Health check
- `POST /predict` - Make predictions
- `GET /metrics` - Server metrics

## Configuration

### Environment Variables

Configure the server using environment variables:

| Variable | Description | Default | Options |
|----------|-------------|---------|---------|
| `CODEX_MODEL_NAME` | Name of the model | `default-model` | Any string |
| `CODEX_MODEL_TYPE` | Type of model backend | `stub` | `stub`, `huggingface`, `onnx` |
| `CODEX_MODEL_PATH` | Path to model files | `.codex/models/<model_name>` | Any valid path |
| `CODEX_MODEL_DEVICE` | Device to run model on | `cpu` | `cpu`, `cuda` |
| `CODEX_MODEL_CONFIG` | Path to config file | None | Any valid file path |
| `CODEX_MODEL_DIR` | Base directory for models | `.codex/models` | Any valid directory |

### Configuration File

Alternatively, use a configuration dictionary:

```python
config_dict = {
    "model_name": "my-classifier",
    "model_type": "huggingface",
    "model_path": "/path/to/model",
    "device": "cpu",
}

config = ModelConfig.from_dict(config_dict)
server = ModelServer(config=config)
```text

### ModelConfig Class

The `ModelConfig` class provides a type-safe way to configure the model server:

```python
from src.codex_ml.serving.inference_server import ModelConfig

# Create configuration
config = ModelConfig(
    model_name="my-model",
    model_type="huggingface",
    model_path="/path/to/model",
    device="cpu",
)

# Validate configuration
config.validate()

# Convert to dictionary
config_dict = config.to_dict()
```text

## Model Backends

### Stub Model (Testing)

Best for development and testing. Returns dummy predictions:

```python
config = ModelConfig(model_type="stub", model_name="test-model")
server = ModelServer(config=config)
server.load_model()
```text

**Output Format:**
```python
[
    {
        "text": "input text",
        "label": "POSITIVE",
        "score": 0.95,
        "model": "test-model"
    }
]
```text

### HuggingFace Models

Load and serve HuggingFace Transformers models:

```python
config = ModelConfig(
    model_type="huggingface",
    model_name="bert-classifier",
    model_path="/path/to/huggingface/model",
    device="cpu",
)
server = ModelServer(config=config)
server.load_model()
```text

**Requirements:**
- Model files must exist at the specified path
- `transformers` package must be installed: `pip install transformers`

**Output Format:**
```python
[
    {
        "text": "input text",
        "embedding": [0.1, 0.2, ...],  # First 10 dimensions
        "model": "bert-classifier"
    }
]
```text

### ONNX Models

Load and serve ONNX Runtime models:

```python
config = ModelConfig(
    model_type="onnx",
    model_name="onnx-classifier",
    model_path="/path/to/model.onnx",
    device="cpu",
)
server = ModelServer(config=config)
server.load_model()
```text

**Requirements:**
- Model file must exist at the specified path
- `onnxruntime` package must be installed: `pip install onnxruntime`

**Note:** ONNX inference currently returns stub predictions. Full implementation requires proper tokenization for your specific model.

## Making Predictions

### Basic Prediction

```python
# Load model
server.load_model()

# Single or batch prediction
inputs = ["First input", "Second input", "Third input"]
predictions = server.predict(inputs)

for pred in predictions:
    print(f"Text: {pred['text']}")
    print(f"Label: {pred['label']}")
    print(f"Score: {pred['score']}")
```text

### With Parameters

Pass optional parameters to customize inference:

```python
predictions = server.predict(
    inputs=["Hello world"],
    parameters={
        "max_length": 512,
        "temperature": 0.7,
    }
)
```text

### Input Constraints

- **Batch Size**: Maximum 100 inputs per request (configurable via `MAX_BATCH_SIZE`)
- **Input Length**: Maximum 10,000 characters per input (configurable via `MAX_INPUT_LENGTH`)

## Error Handling

### Model Loading Errors

```python
from src.codex_ml.serving.inference_server import ModelLoadError

try:
    server.load_model()
except ModelLoadError as e:
    print(f"Failed to load model: {e}")
    # Handle error (fallback, retry, etc.)
```text

Common errors:
- **Missing model files**: Model path does not exist
- **Invalid configuration**: Invalid model_type or device
- **Missing dependencies**: Required package not installed

### Prediction Errors

```python
try:
    predictions = server.predict(inputs)
except RuntimeError as e:
    print(f"Prediction failed: {e}")
```text

Common errors:
- **Model not loaded**: Call `load_model()` first
- **Invalid input**: Check batch size and input length constraints

## Health Checks

Check server health programmatically:

```python
health = server.health_check()

print(f"Status: {health['status']}")
print(f"Model Loaded: {health['model_loaded']}")
print(f"Uptime: {health['uptime_seconds']} seconds")
print(f"Total Requests: {health['total_requests']}")
print(f"Model Type: {health['model_type']}")
print(f"Device: {health['device']}")

# Check for load errors
if health['load_errors']:
    print(f"Load Errors: {health['load_errors']}")
```text

## Rate Limiting

The server includes built-in rate limiting:

- **Default Limit**: 1000 requests per minute per client IP
- **Window**: 60 seconds (rolling window)
- **Response**: HTTP 429 (Too Many Requests) when limit exceeded

Configure rate limiting:

```python
from src.codex_ml.serving.inference_server import RateLimiter

# Custom rate limiter
limiter = RateLimiter(max_requests=500, window_seconds=60)

# Check if request is allowed
if limiter.is_allowed(client_ip):
    # Process request
    pass
else:
    # Reject request
    pass
```text

## API Endpoints (FastAPI)

### GET /

Server information and available endpoints.

**Response:**
```json
{
    "message": "Codex ML Inference Server",
    "model": "my-model",
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
    "total_requests": 42,
    "model_name": "my-model",
    "model_type": "stub",
    "device": "cpu",
    "load_errors": []
}
```text

### POST /predict

Make predictions.

**Request:**
```json
{
    "inputs": ["text1", "text2"],
    "parameters": {
        "max_length": 512
    }
}
```text

**Response:**
```json
{
    "predictions": [
        {
            "text": "text1",
            "label": "POSITIVE",
            "score": 0.95,
            "model": "my-model"
        }
    ],
    "model_name": "my-model",
    "inference_time_ms": 12.34,
    "metadata": {
        "batch_size": 1,
        "total_requests": 43
    }
}
```text

### GET /metrics

Server metrics.

**Response:**
```json
{
    "total_requests": 42,
    "uptime_seconds": 123.45,
    "model_name": "my-model",
    "model_loaded": true
}
```text

## What's NOT Covered (Advanced Features)

The following features are intentionally **not included** in this initial implementation and are reserved for future enhancements:

- **Streaming Inference**: Real-time streaming of predictions
- **Batching Optimization**: Automatic request batching for efficiency
- **Multi-Model Serving**: Serving multiple models simultaneously
- **Model Routing**: Intelligent routing between model versions
- **Vector Store Integration**: Integration with vector databases
- **Caching**: Response caching for repeated queries
- **Advanced Metrics**: Detailed performance profiling and traces
- **GPU Optimization**: Multi-GPU support and optimization
- **Model Versioning**: A/B testing and gradual rollouts
- **Custom Preprocessing**: Configurable preprocessing pipelines

These features will be addressed in subsequent pull requests as the system matures.

## Examples

### Complete Example: Stub Model

```python
from src.codex_ml.serving.inference_server import ModelServer, ModelConfig

# Configure
config = ModelConfig(
    model_name="sentiment-classifier",
    model_type="stub",
    device="cpu",
)

# Create server
server = ModelServer(config=config)

# Load model
server.load_model()

# Check health
health = server.health_check()
print(f"Server status: {health['status']}")

# Make predictions
inputs = [
    "This product is amazing!",
    "Worst purchase ever.",
    "It's okay, nothing special.",
]

predictions = server.predict(inputs)

for inp, pred in zip(inputs, predictions):
    print(f"\nInput: {inp}")
    print(f"Label: {pred['label']}")
    print(f"Score: {pred['score']:.2f}")
```text

### Complete Example: Running FastAPI Server

```bash
# 1. Install dependencies
pip install fastapi uvicorn

# 2. Set environment variables
export CODEX_MODEL_NAME=my-classifier
export CODEX_MODEL_TYPE=stub
export CODEX_MODEL_DEVICE=cpu

# 3. Run server
python -m src.codex_ml.serving.inference_server

# 4. Test endpoints
curl http://localhost:8000/
curl http://localhost:8000/health

# 5. Make prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": ["This is a test"],
    "parameters": {}
  }'
```text

## Troubleshooting

### Model Won't Load

1. **Check model path**: Verify the path exists and contains model files
2. **Check dependencies**: Ensure required packages are installed
3. **Check configuration**: Validate model_type and device settings
4. **Check logs**: Look for detailed error messages in server logs

### Predictions Fail

1. **Check model is loaded**: Call `load_model()` before `predict()`
2. **Check input format**: Ensure inputs are a list of strings
3. **Check input size**: Verify batch size and input length limits
4. **Check health**: Use `health_check()` to verify server state

### Rate Limiting Issues

1. **Check client IP**: Different clients have independent limits
2. **Wait for window**: Rate limit window resets after 60 seconds
3. **Adjust limits**: Configure custom `RateLimiter` if needed

## Performance Considerations

- **Stub models**: Very fast, suitable for testing
- **HuggingFace models**: Depends on model size and complexity
- **ONNX models**: Generally faster than HuggingFace for inference
- **Batch size**: Larger batches Phase 5 improve throughput but increase latency
- **Device**: GPU (`cuda`) will be faster than CPU for large models

## Security Considerations

- **Rate Limiting**: Prevents abuse and DoS attacks
- **Input Validation**: Enforces size limits on inputs
- **Error Handling**: Prevents information leakage in error messages
- **CORS**: Configure appropriately for production
- **Authentication**: Not included; add via middleware if needed

## Next Steps

1. **Try the stub model** to understand the API
2. **Configure environment variables** for your use case
3. **Load a real model** (HuggingFace or ONNX)
4. **Run the FastAPI server** and test endpoints
5. **Integrate with your application** using the Python API or HTTP endpoints

For questions or issues, refer to the test suite in `tests/codex_ml/test_inference_server.py` for working examples.
