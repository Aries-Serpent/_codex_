# Deployment Guide

> Last Updated: 2024-12-24

This guide covers deploying the _codex_ system in various environments.

## Prerequisites

- Python 3.11+
- Docker (for containerized deployment)
- Access to OpenAI API or compatible endpoint
- Vector store (Pinecone, Weaviate, or local)

## Environment Variables

Required environment variables:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-...          # Or use GITHUB_CODEX
OPENAI_ORG_ID=org-...          # Optional

# Vector Store
PINECONE_API_KEY=...           # If using Pinecone
PINECONE_ENVIRONMENT=...

# Application
CODEX_ENV=production           # development|staging|production
LOG_LEVEL=INFO
```

## Local Development

```bash
# Clone repository
git clone https://github.com/Aries-Serpent/_codex_.git
cd _codex_

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e .[dev]

# Run tests
pytest tests/

# Start development server
python -m src.mcp.server.app
```

## Docker Deployment

```bash
# Build image
docker build -t codex:latest .

# Run container
docker run -d \
  --name codex \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -e PINECONE_API_KEY=$PINECONE_API_KEY \
  -p 8000:8000 \
  codex:latest
```

## Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: codex
spec:
  replicas: 3
  template:
    spec:
      containers:
        - name: codex
          image: ghcr.io/aries-serpent/codex:latest
          envFrom:
            - secretRef:
                name: codex-secrets
          resources:
            requests:
              memory: "512Mi"
              cpu: "500m"
            limits:
              memory: "2Gi"
              cpu: "2000m"
```

## CI/CD Integration

The repository includes GitHub Actions workflows:

- `build-container-cache.yml` - Builds and caches Docker images
- `cache-warmer.yml` - Pre-warms dependency caches
- `wiki-assemble.yml` - Generates documentation

## Health Checks

The MCP server exposes health endpoints:

```bash
# Liveness probe
curl http://localhost:8000/health

# Readiness probe
curl http://localhost:8000/ready
```

## Monitoring

Metrics are exposed at `/metrics` in Prometheus format:
- `codex_requests_total` - Total API requests
- `codex_latency_seconds` - Request latency histogram
- `codex_tokens_used` - Token usage counter

## Troubleshooting

### Common Issues

1. **API Key Not Found**
   - Ensure `OPENAI_API_KEY` or `GITHUB_CODEX` is set
   - Check for typos in environment variable names

2. **Vector Store Connection Failed**
   - Verify Pinecone API key and environment
   - Check network connectivity

3. **Out of Memory**
   - Increase container memory limits
   - Reduce batch sizes in `rag_config.yaml`

## See Also

- [Architecture](architecture.md)
- [Security & Risks](security_and_risks.md)
