# MSP Gateway - Managed Service Provider Capabilities

This directory contains the implementation of MSP (Managed Service Provider) capabilities for the Codex project, designed for **local-first, offline operation**.

## Overview

MSP Gateway is a tenant-aware inference API built with FastAPI that provides:

- **Tenant isolation** with API key authentication
- **Rate limiting** per tenant (in-memory token bucket)
- **Local model inference** (CPU-based, no external API calls)
- **Vector search** using FAISS for knowledge base retrieval
- **RAG (Retrieval-Augmented Generation)** with safety delimiters
- **Content redaction** and policy enforcement
- **Offline-first** architecture with zero external dependencies

## Architecture

```
services/msp_gateway/          # FastAPI gateway service
├── app.py                     # FastAPI app factory
├── main.py                    # Uvicorn entrypoint
├── config.py                  # Settings (env/Hydra)
├── security.py                # Auth, policies, redaction
├── middleware/                # Request processing
│   ├── tenant_context.py     # API key → tenant resolution
│   └── rate_limit.py         # Per-tenant rate limiting
├── providers/                 # Backend adapters
│   ├── model_adapter.py      # Model inference interface
│   └── retrieval_adapter.py  # Vector store interface
├── routers/                   # API endpoints
│   ├── infer.py              # POST /v1/infer
│   ├── kb.py                 # POST /v1/query_kb
│   └── admin.py              # Admin operations
└── schemas/                   # Pydantic models
    ├── requests.py
    └── responses.py

src/codex/                     # Core libraries
├── rag/                       # RAG pipeline
│   ├── prompt.py             # Prompt assembly with safety
│   └── postprocess.py        # Output scrubbing, citations
└── retrieval/                 # Vector search
    ├── embed.py              # Build embeddings
    ├── search.py             # Top-k retrieval API
    └── stores/               # Vector store implementations
        ├── faiss_store.py    # FAISS (local CPU)
        ├── pgvector_store.py # PostgreSQL (stub)
        └── weaviate_store.py # Weaviate (stub)

policies/                      # Security policies
├── safelist.yaml             # Allowed patterns
├── denylist.yaml             # Blocked/redacted patterns
└── tenant_policy.schema.json # Per-tenant policy schema

configs/msp/                   # Configuration
├── gateway.yaml              # Gateway settings
├── retrieval.yaml            # Vector search config
└── safety.yaml               # Security policies

scripts/local/                 # Local runner scripts
├── serve_local.sh            # Start gateway
├── build_faiss.sh            # Build FAISS index
└── run_tests.sh              # Run tests offline
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -e .
pip install fastapi uvicorn httpx
pip install sentence-transformers faiss-cpu
```

### 2. Build a Knowledge Base Index

```bash
# Create sample data or use your own NDJSON file
bash scripts/local/build_faiss.sh my-tenant data/kb.ndjson
```

### 3. Start the Gateway

```bash
bash scripts/local/serve_local.sh
```

The gateway will start on `http://127.0.0.1:8080`.

### 4. Create a Tenant

```bash
curl -X POST http://127.0.0.1:8080/admin/tenants \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "my-tenant",
    "name": "My Tenant",
    "api_key": "my-secret-key",
    "quota": {
      "requests_per_minute": 60,
      "tokens_per_minute": 10000
    }
  }'
```

### 5. Query the Knowledge Base

```bash
curl -X POST http://127.0.0.1:8080/v1/query_kb \
  -H "Authorization: Bearer my-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "my-tenant",
    "query": "What is machine learning?",
    "top_k": 3
  }'
```

### 6. Run Inference

```bash
curl -X POST http://127.0.0.1:8080/v1/infer \
  -H "Authorization: Bearer my-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "my-tenant",
    "prompt": "Explain machine learning",
    "max_tokens": 100,
    "options": {
      "use_rag": true,
      "rag_top_k": 3
    }
  }'
```

## Python Client

Use the MSP client for programmatic access:

```python
from agents.msp_client import MSPClient

# Create client
client = MSPClient(
    base_url="http://127.0.0.1:8080",
    api_key="my-secret-key"
)

# Query knowledge base
kb_results = client.query_kb(
    tenant_id="my-tenant",
    query="What is machine learning?",
    top_k=3
)

# Run inference
response = client.infer(
    tenant_id="my-tenant",
    prompt="Explain deep learning",
    max_tokens=100
)

print(response["generated_text"])
```

## Configuration

### Environment Variables

Set these in `.env` or export them:

```bash
MSP_OFFLINE=1                 # Enforce offline mode
MSP_HOST=127.0.0.1           # Bind address
MSP_PORT=8080                # Server port
MSP_LOG_LEVEL=INFO           # Log level
MSP_MODEL_BACKEND=mock       # Model backend: mock, transformers
MSP_VECTOR_BACKEND=faiss     # Vector store: faiss
MSP_RATE_LIMIT_ENABLED=true  # Enable rate limiting
```

### Model Backend

By default, the gateway uses a **mock model** for testing. To use a real model:

1. Install transformers: `pip install transformers torch`
2. Set environment:
   ```bash
   export MSP_MODEL_BACKEND=transformers
   export MSP_MODEL_PATH=gpt2  # or path to local weights
   export MSP_MODEL_DEVICE=cpu
   ```

## Testing

Run the test suite:

```bash
bash scripts/local/run_tests.sh
```

Or use pytest directly:

```bash
pytest tests/test_msp_*.py -v
```

## Security Features

### Content Redaction

Automatically redacts sensitive information:
- Email addresses → `[EMAIL]`
- Phone numbers → `[PHONE]`
- SSNs → `[SSN]`
- Credit cards → `[CARD]`
- Custom sensitive terms

### Prompt Validation

Blocks malicious patterns:
- Prompt injection attempts
- System instruction manipulation
- Cross-tenant data access

### Offline Enforcement

In offline mode (`MSP_OFFLINE=1`):
- No external network calls allowed
- Local models only
- File-based persistence (SQLite)
- In-memory rate limiting

## Tenant Isolation

Each tenant has:
- Unique API key
- Separate FAISS index
- Resource quotas
- Custom policies
- Isolated audit logs

## Development

### Adding a New Endpoint

1. Create router in `services/msp_gateway/routers/`
2. Add request/response schemas in `schemas/`
3. Include router in `app.py`
4. Add tests in `tests/`

### Adding a New Vector Store

1. Implement store in `src/codex/retrieval/stores/`
2. Follow `FAISSStore` interface
3. Update `RetrievalEngine` to support new backend
4. Add configuration in `configs/msp/retrieval.yaml`

## Troubleshooting

### Gateway won't start

- Check Python version (requires 3.10+)
- Install missing dependencies: `pip install -e .`
- Check port availability: `lsof -i :8080`

### Empty KB query results

- Build FAISS index first: `bash scripts/local/build_faiss.sh`
- Verify index exists: `ls -la .codex/tenants/<tenant>/faiss/`

### Inference errors

- For testing, use mock backend: `export MSP_MODEL_BACKEND=mock`
- For real inference, install transformers and set model path

## License

MIT - See LICENSE file in repository root
