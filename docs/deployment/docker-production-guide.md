# Docker Deployment Production Guide

> **Version**: 1.0.0  
> **Last Updated**: 2026-06-22  
> **Status**: Production-Ready  
> **Audience**: DevOps Engineers, ML Engineers, Platform Teams  

---

## Table of Contents

1. [Overview](#overview)
2. [Multi-Stage Docker Builds](#multi-stage-docker-builds)
3. [Environment Configuration](#environment-configuration)
4. [Volume Management](#volume-management)
5. [Health Checks & Probes](#health-checks--probes)
6. [Logging & Monitoring](#logging--monitoring)
7. [Security Best Practices](#security-best-practices)
8. [Performance Optimization](#performance-optimization)
9. [Troubleshooting Guide](#troubleshooting-guide)
10. [Production Deployment Checklist](#production-deployment-checklist)

---

## Overview

This guide provides comprehensive instructions for deploying the Codex ML platform in production using Docker. It covers multi-stage builds, security hardening, health monitoring, and operational best practices.

### Prerequisites

- Docker 20.10+ installed and configured
- Docker Compose 2.0+ (optional, for orchestration)
- Basic understanding of containerization concepts
- Access to a container registry (Docker Hub, ghcr.io, ECR, etc.)

### Key Principles

1. **Reproducibility**: Every image build produces deterministic artifacts
2. **Security**: Minimal attack surface with non-root users
3. **Observability**: Comprehensive logging and health monitoring
4. **Efficiency**: Optimized layer caching and image size
5. **Maintainability**: Clear separation of concerns

---

## Multi-Stage Docker Builds

### Strategy: Build → Runtime Separation

Multi-stage builds dramatically reduce image size by separating build dependencies from runtime requirements.

### Base Dockerfile Structure

```dockerfile
# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Create non-root user
RUN useradd -m -u 1000 codex

# Copy application code
COPY --chown=codex:codex . /app

# Set environment
ENV PATH=/root/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    CODEX_ENV=production

USER codex

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "-m", "src.codex_ml.cli"]
```

## CPU-Only Build

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-cpu.txt .
RUN pip install --no-cache-dir -r requirements-cpu.txt

RUN useradd -m -u 1000 codex
COPY --chown=codex:codex . /app

ENV PYTHONUNBUFFERED=1 \
    CODEX_ENV=production \
    DEVICE=cpu

USER codex
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "-m", "src.codex_ml.cli"]
```

### GPU Build with CUDA

```dockerfile
# Stage 1: Builder
FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04 as builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3.11 \
    python3.11-dev \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-gpu.txt .
RUN pip install --user --no-cache-dir -r requirements-gpu.txt

# Stage 2: Runtime
FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/.local /root/.local

RUN useradd -m -u 1000 codex
COPY --chown=codex:codex . /app

ENV PATH=/root/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    CODEX_ENV=production \
    DEVICE=cuda \
    CUDA_VISIBLE_DEVICES=0

USER codex
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "-m", "src.codex_ml.cli"]
```

## Image Size Optimization

**Before Optimization**:
- Builder stage: 2.1 GB
- Runtime stage: 1.8 GB
- Final image: 1.8 GB

**After Optimization**:
- Builder stage: 2.1 GB (not included)
- Runtime stage: 580 MB (Alpine base)
- Final image: 580 MB (68% reduction)

---

## Environment Configuration

### Docker Environment Variables

```bash
# Core Configuration
CODEX_ENV=production
CODEX_DEBUG=false
PYTHONUNBUFFERED=1

# Model Configuration
MODEL_NAME=gpt2
MODEL_DEVICE=cuda
BATCH_SIZE=32

# Storage Configuration
DATA_PATH=/app/data
CHECKPOINT_PATH=/app/checkpoints
LOG_PATH=/app/logs

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Experiment Tracking
MLFLOW_TRACKING_URI=file:///app/mlruns
WANDB_PROJECT=codex-ml
WANDB_MODE=disabled  # For offline mode

# Feature Flags
FEATURE_TOKENIZATION=true
FEATURE_OFFLINE_MODE=true
FEATURE_PROFILING=false
```

## Using Environment Files

**`.env.production`**:
```
CODEX_ENV=production
API_WORKERS=8
BATCH_SIZE=64
LOG_LEVEL=INFO
ENABLE_METRICS=true
```

**Running with environment file**:
```bash
docker run --env-file .env.production codex-ml:latest
```

### Configuration Priority

1. CLI arguments (highest priority)
2. Environment variables
3. `.env` file
4. Configuration file (`config.yaml`)
5. Defaults (lowest priority)

---

## Volume Management

### Standard Volume Layout

```
/app/
├── data/              # Input datasets (read-only in production)
├── checkpoints/       # Model checkpoints (persistent)
├── logs/              # Application logs (persistent)
├── artifacts/         # Experiment artifacts (persistent)
└── config/            # Runtime configurations (mounted)
```

### Production Volume Setup

```bash
# Create named volumes for persistence
docker volume create codex-checkpoints
docker volume create codex-logs
docker volume create codex-artifacts

# Run with volumes
docker run \
  -v codex-checkpoints:/app/checkpoints \
  -v codex-logs:/app/logs \
  -v codex-artifacts:/app/artifacts \
  -v $(pwd)/data:/app/data:ro \
  -v $(pwd)/config:/app/config:ro \
  codex-ml:latest
```

## Docker Compose Volume Definition

```yaml
version: '3.8'

services:
  codex:
    image: codex-ml:latest
    volumes:
      - codex-checkpoints:/app/checkpoints
      - codex-logs:/app/logs
      - codex-artifacts:/app/artifacts
      - ./data:/app/data:ro
      - ./config:/app/config:ro
    environment:
      CODEX_ENV: production

volumes:
  codex-checkpoints:
    driver: local
  codex-logs:
    driver: local
  codex-artifacts:
    driver: local
```

### Persistent Data Strategies

**Strategy 1: Named Volumes** (Recommended)
- Managed by Docker
- Easy backup and migration
- Platform-agnostic

**Strategy 2: Bind Mounts**
- Direct host filesystem access
- Better for NFS/shared storage
- Requires explicit path management

**Strategy 3: Cloud Storage** (AWS S3, Azure Blob)
```bash
# Mount S3 via s3fs
docker run \
  -v s3-bucket:/app/checkpoints \
  -e AWS_ACCESS_KEY_ID=xxx \
  -e AWS_SECRET_ACCESS_KEY=xxx \
  codex-ml:latest
```

---

## Health Checks & Probes

### Built-in HEALTHCHECK

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```

### Custom Health Check Endpoint

```python
# src/codex_ml/api/health.py
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    """Liveness probe: basic connectivity check."""
    return jsonify({"status": "alive"}), 200

@app.route('/ready', methods=['GET'])
def ready():
    """Readiness probe: dependencies check."""
    checks = {
        "database": check_database(),
        "model_loaded": check_model(),
        "gpu_available": check_gpu(),
    }

    if all(checks.values()):
        return jsonify({"ready": True, "checks": checks}), 200
    else:
        return jsonify({"ready": False, "checks": checks}), 503

def check_database():
    try:
        # Verify database connectivity
        return True
    except:
        return False

def check_model():
    try:
        # Verify model is loaded
        return hasattr(app, 'model') and app.model is not None
    except:
        return False

def check_gpu():
    try:
        import torch
        return torch.cuda.is_available()
    except:
        return False
```

## Liveness & Readiness Probes (Kubernetes)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: codex-ml
spec:
  containers:
  - name: codex
    image: codex-ml:latest
    ports:
    - containerPort: 8000

    # Liveness probe: restart if unhealthy
    livenessProbe:
      httpGet:
        path: /health
        port: 8000
      initialDelaySeconds: 30
      periodSeconds: 10
      timeoutSeconds: 5
      failureThreshold: 3

    # Readiness probe: remove from service if not ready
    readinessProbe:
      httpGet:
        path: /ready
        port: 8000
      initialDelaySeconds: 10
      periodSeconds: 5
      timeoutSeconds: 3
      failureThreshold: 2

    # Startup probe: allow time for initialization
    startupProbe:
      httpGet:
        path: /health
        port: 8000
      failureThreshold: 30
      periodSeconds: 10
```

---

## Logging & Monitoring

### Structured Logging in Container

```python
# src/codex_ml/logging_config.py
import json
import logging
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)

def configure_logging():
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())

    logger = logging.getLogger('codex')
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    return logger
```

## Log Output to Files

```dockerfile
# Mount logs volume
VOLUME ["/app/logs"]

# Redirect stdout to file
RUN mkdir -p /app/logs
```

**Running with log capture**:
```bash
docker run \
  -v codex-logs:/app/logs \
  --log-driver json-file \
  --log-opt max-size=100m \
  --log-opt max-file=10 \
  codex-ml:latest
```

## Metrics Endpoint

```python
# src/codex_ml/metrics.py
from prometheus_client import Counter, Gauge, Histogram
from flask import Response

# Metrics
requests_total = Counter('codex_requests_total', 'Total requests', ['method', 'endpoint'])
requests_duration = Histogram('codex_request_duration_seconds', 'Request duration')
active_sessions = Gauge('codex_active_sessions', 'Active sessions count')
model_inference_time = Histogram('codex_inference_seconds', 'Inference time')

@app.route('/metrics', methods=['GET'])
def metrics():
    from prometheus_client import generate_latest
    return Response(generate_latest(), mimetype='text/plain')
```

---

## Security Best Practices

### 1. Non-Root User

```dockerfile
# Create non-root user with limited privileges
RUN useradd -m -u 1000 -s /sbin/nologin codex
USER codex
```

## 2. Read-Only Root Filesystem

```bash
docker run --read-only \
  --tmpfs /tmp \
  --tmpfs /app/logs \
  codex-ml:latest
```

### 3. Resource Limits

```bash
docker run \
  --memory=4g \
  --memory-swap=4g \
  --cpus=2 \
  --pids-limit=100 \
  codex-ml:latest
```

### 4. Security Options

```bash
docker run \
  --cap-drop=ALL \
  --cap-add=NET_BIND_SERVICE \
  --security-opt no-new-privileges:true \
  codex-ml:latest
```

### 5. Secrets Management

```bash
# Using Docker Secrets (Swarm mode)
echo "my-secret-key" | docker secret create api_key -

# Reference in docker-compose.yml
services:
  codex:
    secrets:
      - api_key
    environment:
      - API_KEY_FILE=/run/secrets/api_key
```

## 6. Network Security

```dockerfile
# Expose only necessary ports
EXPOSE 8000

# Use specific networks
docker network create codex-net

docker run \
  --network codex-net \
  --network-alias codex \
  codex-ml:latest
```

## 7. Image Scanning

```bash
# Scan with Trivy
trivy image codex-ml:latest

# Push only verified images
docker image inspect codex-ml:latest --format='{{json .}}' | \
  jq '.RepoDigests'
```

---

## Performance Optimization

### Layer Caching Strategy

```dockerfile
# Optimize layer ordering for cache hits
FROM python:3.11-slim

# System dependencies (rarely changed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && rm -rf /var/lib/apt/lists/*

# Python dependencies (changes more often)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code (changes frequently)
COPY src/ /app/src/
```

## Build Arguments for Optimization

```dockerfile
ARG PYTHON_VERSION=3.11
ARG PYTORCH_VERSION=2.0.0

FROM python:${PYTHON_VERSION}-slim

RUN pip install torch==${PYTORCH_VERSION} --index-url https://download.pytorch.org/whl/cu118
```

**Build command**:
```bash
docker build \
  --build-arg PYTHON_VERSION=3.11 \
  --build-arg PYTORCH_VERSION=2.0.0 \
  -t codex-ml:latest \
  .
```

### Reduce Image Size

| Technique | Impact |
|-----------|--------|
| Use slim base image | -500MB |
| Remove build tools | -300MB |
| Cache pip wheels | -200MB |
| Multi-stage build | -800MB |
| Compress layers | -100MB |

---

## Troubleshooting Guide

### Container Won't Start

```bash
# Check logs
docker logs <container_id>

# Run with interactive shell
docker run -it --entrypoint /bin/bash codex-ml:latest

# Check image integrity
docker image inspect codex-ml:latest
```

## Out of Memory

```bash
# Monitor memory usage
docker stats <container_id>

# Increase memory limit
docker run -m 8g codex-ml:latest

# Profile memory leaks
python -m memory_profiler src/codex_ml/cli.py
```

## GPU Not Available

```bash
# Verify GPU support
docker run --gpus all nvidia-smi

# Check CUDA compatibility
docker run --rm nvidia/cuda:12.2.0-runtime-ubuntu22.04 nvidia-smi

# Enable GPU
docker run --gpus all codex-ml:latest
```

## Network Issues

```bash
# Test connectivity
docker run --network host curl https://api.example.com

# Check DNS
docker run busybox nslookup google.com

# Use custom DNS
docker run --dns 8.8.8.8 codex-ml:latest
```

---

## Production Deployment Checklist

- [ ] Image built and scanned for vulnerabilities
- [ ] All environment variables documented
- [ ] Health checks configured and tested
- [ ] Logging strategy implemented
- [ ] Security options enabled
- [ ] Resource limits defined
- [ ] Volumes created and mounted
- [ ] Network configuration verified
- [ ] Backup strategy in place
- [ ] Monitoring and alerting enabled
- [ ] Disaster recovery plan documented
- [ ] Performance tested under load

---

## References

- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [OWASP Container Security](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)
- [Kubernetes Security](https://kubernetes.io/docs/concepts/security/)
