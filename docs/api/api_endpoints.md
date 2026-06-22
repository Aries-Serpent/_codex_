# API Endpoints Reference

**Version:** 1.0.0 | **Release Date:** 2026-06-22

## HTTP API (FastAPI)

The Codex HTTP API provides REST endpoints for text generation and RAG operations.

**Note**: This repository includes two FastAPI applications:
- `src/codex/api/app.py` - Main text generation API
- `src/codex/api/rag_api.py` - RAG (Retrieval Augmented Generation) API

## Main API Endpoints (app.py)

### Health Check

#### GET /health

Check API health status.

**Response:**
```json
{
  "status": "healthy"
}
```

### Root

#### GET /

API information.

**Response:**
```json
{
  "message": "Codex API v0.2.0",
  "docs": "/docs"
}
```

### Text Generation

#### POST /predict

Generate text predictions using the loaded model.

**Request Body:**
```json
{
  "text": "Sample input text",
  "max_length": 100,
  "temperature": 0.8
}
```

**Response:**
```json
{
  "generated_text": "Generated output text...",
  "model_name": "codex-model",
  "tokens_generated": 50
}
```

## RAG API Endpoints (rag_api.py)

The RAG API provides retrieval-augmented generation with offline TF-IDF support.

### Index Operations

#### POST /rag/build

Build a new RAG index from documents.

#### POST /rag/query

Query the RAG index with a question.

#### GET /rag/indices

List all available RAG indices.

#### GET /rag/stats

Get RAG system statistics.

For complete RAG API documentation, see [RAG Pipelines](rag_pipelines.md).

## OpenAPI Documentation

Interactive API documentation is available at `/docs` when running the FastAPI server:

```bash
# Start the main API server
uvicorn src.codex.api.app:app --reload --port 8000

# Start the RAG API server
uvicorn src.codex.api.rag_api:app --reload --port 8001

# Access documentation
```

## Related Documentation

- [API Index](index.md) - Main API documentation
- [CLI Documentation](cli.md) - Command-line interface
- [RAG Pipeline](rag.md) - RAG API reference
