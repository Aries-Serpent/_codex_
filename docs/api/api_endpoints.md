# API Endpoints Reference

## HTTP API (FastAPI)

The Codex HTTP API provides REST endpoints for:

- Model training
- Inference
- Evaluation
- Status monitoring

## Endpoints

### Training

#### POST /train

Enqueue a background training job.

**Request Body:**
```json
{
  "model_config": {
    "architecture": "transformer",
    "hidden_size": 768
  },
  "training_config": {
    "epochs": 10,
    "batch_size": 32
  }
}
```

**Response:**
```json
{
  "job_id": "train_20260210_123456",
  "status": "queued",
  "artifacts_path": "/artifacts/train_20260210_123456"
}
```

### Inference

#### POST /infer

Run inference on input data.

**Request Body:**
```json
{
  "input": "Sample text for inference",
  "model_id": "best_model_v1"
}
```

**Response:**
```json
{
  "predictions": [...],
  "confidence": 0.95,
  "latency_ms": 42
}
```

### Evaluation

#### POST /evaluate

Run model evaluation.

**Request Body:**
```json
{
  "model_id": "best_model_v1",
  "dataset": "validation_set",
  "metrics": ["accuracy", "f1"]
}
```

**Response:**
```json
{
  "metrics": {
    "accuracy": 0.92,
    "f1": 0.89
  },
  "timestamp": "2026-02-10T21:30:00Z"
}
```

### Status

#### GET /status

Get system and job status.

**Response:**
```json
{
  "queue_depth": 2,
  "active_jobs": 1,
  "completed_jobs": 15,
  "system_health": "healthy"
}
```

## OpenAPI Documentation

Interactive API documentation is available at `/docs` when running the FastAPI server:

```bash
# Start the server
uvicorn codex.api:app --reload

# Access documentation
# Navigate to http://localhost:8000/docs
```

## Related Documentation

- [API Index](index.md) - Main API documentation
- [Getting Started](../guides/getting-started.md) - Setup guide
- [Configuration](../guides/configuration.md) - Configuration reference
