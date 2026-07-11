# Comprehensive API Reference Guide
**Last Updated:** 2026-07-11
**Version:** v0.2.1

**Version:** 1.0.0  
**Last Updated: 2026-07-08
**Author:** Codex Team

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Authentication](#authentication)
4. [Main API Endpoints](#main-api-endpoints)
5. [Authentication Endpoints](#authentication-endpoints)
6. [RAG API Endpoints](#rag-api-endpoints)
7. [Data Types & Schemas](#data-types--schemas)
8. [Error Handling](#error-handling)
9. [Rate Limiting](#rate-limiting)
10. [Integration Examples](#integration-examples)

---

## Overview

The Codex platform provides a comprehensive REST API with the following capabilities:

### Core Services

| Service | Port | Purpose |
|---------|------|---------|
| **Main API** | 8000 | Text generation, health checks, authentication |
| **RAG API** | 8001 | Retrieval-augmented generation, indexing, search |

### Key Features

- **Text Generation**: Powered by transformer language models with safety checks
- **RAG System**: TF-IDF based retrieval with offline support
- **Authentication**: JWT-based user authentication and authorization
- **Content Safety**: Denylist enforcement and moderation checks
- **Rate Limiting**: Per-endpoint rate limits for resource protection
- **Interactive Docs**: Swagger UI and ReDoc documentation

### API Base URLs

```
Development:
- Main API: http://localhost:8000
- RAG API: http://localhost:8001

Production:
- Main API: https://api.codex.example.com
- RAG API: https://rag-api.codex.example.com
```

---

## Quick Start

### 1. Health Check

```bash
curl -X GET http://localhost:8000/health
```

**Response:**
```json
{
  "status": "ok",
  "cognitive_brain": {
    "available": true
  },
  "pattern_compressor": {
    "available": true
  }
}
```

### 2. Text Generation (Without Auth)

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is machine learning?"
  }'
```

**Response:**
```json
{
  "output": "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed..."
}
```

### 3. User Authentication

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "name": "John Doe"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

### 4. RAG Index Operations

```bash
# Build index
curl -X POST http://localhost:8001/rag/build \
  -H "Content-Type: application/json" \
  -d '{
    "index_name": "my_documents",
    "documents": [
      {
        "id": "doc_1",
        "content": "Document content here..."
      }
    ]
  }'

# Query index
curl -X POST http://localhost:8001/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "index_name": "my_documents",
    "query": "relevant search term",
    "top_k": 5
  }'
```

---

## Authentication

### JWT ******

All authenticated endpoints require a JWT bearer token obtained from the `/api/auth/login` endpoint.

#### Including Token in Requests

```bash
# In Authorization header
curl -X GET http://localhost:8000/api/protected \
  -H "Authorization: ******"

# Or as query parameter (less secure)
curl -X GET "http://localhost:8000/api/protected?token=YOUR_JWT_TOKEN"
```

#### Token Structure

```
Header: ******
Payload: eyJzdWIiOiJ1c3JfMTIzYWJjIiwiaWF0IjoxNjI0NTI0MTQwLCJleHAiOjE2MjQ1Mjc3NDB9
Signature: [signature]
```

#### Token Claims

- `sub`: User ID
- `iat`: Issued at (Unix timestamp)
- `exp`: Expiration (Unix timestamp, typically 1 hour)
- `email`: User email
- `name`: User name

#### Token Expiration & Refresh

- **Access Token Duration**: 1 hour (3600 seconds)
- **Refresh**: Use `/api/auth/refresh` endpoint
- **Logout**: Use `/api/auth/logout` to invalidate token

---

## Main API Endpoints

### Health & Info

#### GET /health

Check API health and subsystem status.

**Request:**
```bash
curl -X GET http://localhost:8000/health
```

**Response:**
```json
{
  "status": "ok",
  "cognitive_brain": {
    "available": true
  },
  "pattern_compressor": {
    "available": true,
    "n_components": 128
  }
}
```

**Status Codes:**
- `200`: Healthy
- `500`: Unhealthy (check logs)

---

#### GET /

Get API information.

**Request:**
```bash
curl -X GET http://localhost:8000/
```

**Response:**
```json
{
  "name": "codex",
  "status": "ok"
}
```

---

### Text Generation

#### POST /predict

Generate text predictions using the language model.

**Rate Limit:** 60 requests/minute

**Features:**
- Denylist enforcement
- Input/output moderation
- Configurable generation parameters
- Safety checks

**Request:**
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain quantum computing"
  }'
```

**Request Schema:**
```json
{
  "prompt": "string (1-2048 chars, required)"
}
```

**Response:**
```json
{
  "output": "Quantum computing is a revolutionary computing paradigm..."
}
```

**Response Schema:**
```json
{
  "output": "string (generated text)"
}
```

**Status Codes:**
- `200`: Success
- `400`: Invalid prompt or content policy rejection
- `422`: Validation error
- `429`: Rate limit exceeded

**Examples:**

Simple question:
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is AI?"}'
```

Complex prompt:
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Provide a detailed explanation of machine learning algorithms with examples"
  }'
```

---

## Authentication Endpoints

### POST /api/auth/register

Create a new user account.

**Rate Limit:** 5 requests/minute

**Request:**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "name": "John Doe"
  }'
```

**Request Schema:**
```json
{
  "email": "string (valid email, required, unique)",
  "password": "string (minimum 12 chars, required)",
  "name": "string (1-255 chars, required)"
}
```

**Response:**
```json
{
  "user_id": "usr_123abc",
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2026-07-08T05:53:48Z"
}
```

**Status Codes:**
- `201`: User created successfully
- `400`: Invalid input or user already exists
- `422`: Validation error

**Requirements:**
- Email must be valid format
- Email must be unique
- Password must be ≥12 characters
- Name must not be empty

---

### POST /api/auth/login

Authenticate user and obtain JWT token.

**Rate Limit:** 10 requests/minute

**Request:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

**Request Schema:**
```json
{
  "email": "string (required)",
  "password": "string (required)"
}
```

**Response:**
```json
{
  "access_token": "******",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "usr_123abc",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

**Status Codes:**
- `200`: Login successful
- `401`: Invalid credentials
- `422`: Validation error

---

### POST /api/auth/logout

Invalidate current user session.

**Rate Limit:** 30 requests/minute

**Request:**
```bash
curl -X POST http://localhost:8000/api/auth/logout \
  -H "Authorization: ******"
```

**Response:**
```json
{
  "message": "Logged out successfully"
}
```

**Status Codes:**
- `200`: Logout successful
- `401`: Unauthorized

---

### POST /api/auth/refresh

Obtain new access token using existing token.

**Rate Limit:** 20 requests/minute

**Request:**
```bash
curl -X POST http://localhost:8000/api/auth/refresh \
  -H "Authorization: ******"
```

**Response:**
```json
{
  "access_token": "******",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Status Codes:**
- `200`: Token refreshed
- `401`: Invalid or expired token

---

## RAG API Endpoints

### Health & Monitoring

#### GET /rag/health

Check RAG API health status.

**Request:**
```bash
curl -X GET http://localhost:8001/rag/health
```

**Response:**
```json
{
  "status": "ok"
}
```

---

#### GET /rag/metrics

Get system-wide RAG metrics.

**Rate Limit:** 30 requests/minute

**Request:**
```bash
curl -X GET http://localhost:8001/rag/metrics
```

**Response:**
```json
{
  "total_indices": 10,
  "total_documents": 2500,
  "total_queries": 5000,
  "average_query_time_ms": 145.3,
  "uptime_seconds": 86400
}
```

---

### Index Management

#### POST /rag/build

Build a new RAG index from documents.

**Rate Limit:** 10 requests/minute  
**Response Time:** 2-30 seconds (depends on document count)

**Request:**
```bash
curl -X POST http://localhost:8001/rag/build \
  -H "Content-Type: application/json" \
  -d '{
    "index_name": "my_documents",
    "documents": [
      {
        "id": "doc_001",
        "content": "Document content here...",
        "metadata": {
          "source": "file.txt",
          "category": "technical"
        }
      },
      {
        "id": "doc_002",
        "content": "Another document..."
      }
    ]
  }'
```

**Request Schema:**
```json
{
  "index_name": "string (1-128 alphanumeric/dash/underscore, required)",
  "documents": [
    {
      "id": "string (required)",
      "content": "string (required)",
      "metadata": {
        "string": "string (optional)"
      }
    }
  ]
}
```

**Response:**
```json
{
  "index_name": "my_documents",
  "document_count": 150,
  "size_bytes": 524288,
  "created_at": "2026-07-08T05:53:48Z"
}
```

**Status Codes:**
- `200`: Index created successfully
- `400`: Invalid request or index already exists
- `422`: Validation error

---

#### GET /rag/indices

List all available RAG indices.

**Rate Limit:** 30 requests/minute

**Request:**
```bash
curl -X GET http://localhost:8001/rag/indices
```

**Response:**
```json
{
  "indices": [
    {
      "name": "my_documents",
      "document_count": 150,
      "size_bytes": 524288,
      "created_at": "2026-07-08T05:53:48Z",
      "updated_at": "2026-07-08T06:00:00Z"
    },
    {
      "name": "technical_docs",
      "document_count": 350,
      "size_bytes": 1048576,
      "created_at": "2026-07-07T10:00:00Z",
      "updated_at": "2026-07-08T02:30:00Z"
    }
  ],
  "total_count": 2
}
```

---

#### DELETE /rag/indices/{index_name}

Delete a RAG index and all its documents.

**Rate Limit:** 10 requests/minute  
**WARNING:** This action is permanent and cannot be undone.

**Request:**
```bash
curl -X DELETE http://localhost:8001/rag/indices/my_documents
```

**Response:**
```json
{
  "index_name": "my_documents",
  "deleted_at": "2026-07-08T06:30:00Z",
  "document_count_deleted": 150
}
```

**Status Codes:**
- `200`: Index deleted successfully
- `404`: Index not found
- `400`: Invalid index name

---

#### POST /rag/merge

Merge multiple RAG indices into a single combined index.

**Rate Limit:** 5 requests/minute  
**Response Time:** 5-60 seconds

**Request:**
```bash
curl -X POST http://localhost:8001/rag/merge \
  -H "Content-Type: application/json" \
  -d '{
    "source_indices": ["index1", "index2", "index3"],
    "target_index": "combined_index"
  }'
```

**Request Schema:**
```json
{
  "source_indices": ["string (minimum 2, required)"],
  "target_index": "string (required)"
}
```

**Response:**
```json
{
  "target_index": "combined_index",
  "source_indices_merged": ["index1", "index2", "index3"],
  "total_documents": 450,
  "merged_at": "2026-07-08T07:00:00Z"
}
```

**Status Codes:**
- `200`: Merge successful
- `400`: Invalid indices or merge failed

---

### Retrieval

#### POST /rag/query

Query a RAG index and retrieve relevant documents.

**Rate Limit:** 60 requests/minute  
**Response Time:** 50-500ms

**Request:**
```bash
curl -X POST http://localhost:8001/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "index_name": "my_documents",
    "query": "machine learning algorithms",
    "top_k": 10,
    "threshold": 0.5
  }'
```

**Request Schema:**
```json
{
  "index_name": "string (required)",
  "query": "string (1-1024 chars, required)",
  "top_k": "integer (1-100, default: 5)",
  "threshold": "number (0-1, default: 0.0)"
}
```

**Response:**
```json
{
  "query": "machine learning algorithms",
  "results": [
    {
      "document_id": "doc_001",
      "content": "Machine learning is a subset of artificial intelligence...",
      "score": 0.92,
      "metadata": {
        "source": "file.txt",
        "category": "technical"
      }
    },
    {
      "document_id": "doc_002",
      "content": "Supervised learning algorithms include...",
      "score": 0.87,
      "metadata": {
        "source": "document.md"
      }
    }
  ],
  "total_results": 2,
  "query_time_ms": 125.5
}
```

**Status Codes:**
- `200`: Query successful
- `400`: Index not found or invalid query
- `422`: Validation error
- `429`: Rate limit exceeded

---

### Statistics

#### GET /rag/stats/{index_name}

Get detailed statistics for a RAG index.

**Rate Limit:** 30 requests/minute

**Request:**
```bash
curl -X GET http://localhost:8001/rag/stats/my_documents
```

**Response:**
```json
{
  "index_name": "my_documents",
  "document_count": 150,
  "average_doc_length": 350,
  "vocabulary_size": 12500,
  "size_bytes": 524288,
  "created_at": "2026-07-08T05:53:48Z"
}
```

**Status Codes:**
- `200`: Statistics retrieved
- `404`: Index not found

---

## Data Types & Schemas

### User Object

```json
{
  "id": "usr_123abc",
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2026-07-08T05:53:48Z",
  "updated_at": "2026-07-08T06:00:00Z"
}
```

### Document Object

```json
{
  "id": "doc_001",
  "content": "Document text content...",
  "metadata": {
    "source": "filename.txt",
    "category": "technical",
    "author": "Jane Doe"
  }
}
```

### Query Result Object

```json
{
  "document_id": "doc_001",
  "content": "Relevant text...",
  "score": 0.92,
  "metadata": {
    "source": "file.txt"
  }
}
```

### Index Info Object

```json
{
  "name": "my_documents",
  "document_count": 150,
  "size_bytes": 524288,
  "created_at": "2026-07-08T05:53:48Z",
  "updated_at": "2026-07-08T06:00:00Z"
}
```

---

## Error Handling

### Error Response Format

All errors follow a consistent JSON format:

```json
{
  "detail": "Error message describing what went wrong",
  "status_code": 400,
  "timestamp": "2026-07-08T05:53:48Z"
}
```

### Common Error Codes

| Code | Status | Meaning |
|------|--------|---------|
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | User lacks permissions |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation error in request |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily down |

### Error Recovery

**Retry Strategy:**
- Implement exponential backoff for `429` and `503`
- Do not retry `400`, `401`, `403`, `404`, `422`
- Safe to retry other 5xx errors after delays

**Example Retry Logic:**
```python
import time
import random

def retry_api_call(func, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            return func()
        except RateLimitError:
            delay = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(delay)
        except Exception as e:
            raise
```

---

## Rate Limiting

### Overview

Each endpoint has a rate limit to protect the API from abuse.

### Rate Limit Headers

All responses include rate limit information:

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1625180000
```

### Endpoint Limits

| Endpoint | Limit | Window |
|----------|-------|--------|
| `/health` | 100 | 1 minute |
| `/predict` | 60 | 1 minute |
| `/api/auth/register` | 5 | 1 minute |
| `/api/auth/login` | 10 | 1 minute |
| `/api/auth/logout` | 30 | 1 minute |
| `/api/auth/refresh` | 20 | 1 minute |
| `/rag/build` | 10 | 1 minute |
| `/rag/query` | 60 | 1 minute |
| `/rag/indices` | 30 | 1 minute |
| `/rag/merge` | 5 | 1 minute |
| `/rag/stats/{name}` | 30 | 1 minute |
| `/rag/metrics` | 30 | 1 minute |

### Handling Rate Limits

```bash
# Check rate limit before exceeding
REMAINING=$(curl -s -I http://localhost:8000/predict | grep X-RateLimit-Remaining | awk '{print $2}')
if [ "$REMAINING" -lt 5 ]; then
  echo "Approaching rate limit, waiting..."
  sleep 5
fi

# Handle 429 response
curl -X POST http://localhost:8000/predict ... 2>/dev/null || {
  RETRY_AFTER=$(curl -s -I http://localhost:8000/predict | grep Retry-After | awk '{print $2}')
  sleep $RETRY_AFTER
  curl -X POST http://localhost:8000/predict ...
}
```

---

## Integration Examples

### cURL Examples

See the [cURL Examples](CURL_EXAMPLES.md) for comprehensive command-line examples.

### Python Examples

See the [Python Integration Guide](PYTHON_docs/api/reference/INTEGRATION.md) for complete Python examples using the `requests` library.

### JavaScript/TypeScript Examples

See the [JavaScript Integration Guide](JAVASCRIPT_docs/api/reference/INTEGRATION.md) for complete JavaScript examples using `fetch` or `axios`.

### Postman Collection

See [POSTMAN_COLLECTION.json](POSTMAN_COLLECTION.json) for a complete Postman collection with all endpoints.

### Insomnia Collection

See [INSOMNIA_COLLECTION.json](INSOMNIA_COLLECTION.json) for an Insomnia collection with all endpoints.

---

## API Documentation Resources

- **Interactive Docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc
- **OpenAPI Spec**: http://localhost:8000/openapi.json

---

## Support

For issues or questions:
1. Check the [troubleshooting guide](TROUBLESHOOTING.md)
2. Review error codes in [Error Handling](#error-handling)
3. Contact: support@codex.example.com
4. GitHub Issues: https://github.com/Aries-Serpent/_codex_/issues

---

**Last Updated: 2026-07-08
**Version:** 1.0.0
