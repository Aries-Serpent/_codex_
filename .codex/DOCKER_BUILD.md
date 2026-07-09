# Docker Build Guide — Aries-Serpent v0.1.0-final

Production-grade Docker images for Aries-Serpent with optimized sizes, security hardening, and SBOM generation.

## Image Specifications

### 1. API Server Image (`aries-serpent:0.1.0-final-api`)

**Target:** <500 MB  
**Dockerfile:** `docker/Dockerfile.api-prod`  
**Base:** `python:3.12-slim`

**Features:**
- Multi-stage build for minimal size
- Non-root user (UID 1001)
- Read-only root filesystem support
- Health check: `GET /health` (30s interval)
- SBOM generated at build time
- Uvicorn with 4 workers (configurable)

**Exposed Ports:**
- `8000/TCP` — HTTP (FastAPI)

**Environment Variables:**
- `PYTHONUNBUFFERED=1` — Real-time logging
- `PYTHONDONTWRITEBYTECODE=1` — Skip .pyc files
- `LOG_LEVEL=INFO` — Logging level
- `API_TIMEOUT=30` — Request timeout (seconds)
- `CACHE_SIZE=1024` — Cache size (MB)
- `CORS_ORIGINS="*"` — CORS configuration
- `WORKERS=4` — Uvicorn workers

**Build Command:**
```bash
docker build -f docker/Dockerfile.api-prod -t aries-serpent:0.1.0-final-api .
```

**Run Command:**
```bash
docker run -p 8000:8000 \
  -e LOG_LEVEL=INFO \
  -e CORS_ORIGINS="http://localhost:3000" \
  aries-serpent:0.1.0-final-api
```

**Health Check:**
```bash
curl http://localhost:8000/health
```

---

### 2. Inference Service Image (`aries-serpent:0.1.0-final-inference`)

**Target:** <300 MB  
**Dockerfile:** `docker/Dockerfile.inference-prod`  
**Base:** `python:3.12-slim`

**Features:**
- Optimized for inference (minimal dependencies)
- Non-root user (UID 1001)
- gRPC service (port 8001)
- HTTP metrics endpoint (port 8002)
- Lazy model loading
- SBOM generated at build time

**Exposed Ports:**
- `8001/TCP` — gRPC (inference service)
- `8002/TCP` — HTTP metrics

**Environment Variables:**
- `INFERENCE_BATCH_SIZE=32` — Batch size for inference
- `INFERENCE_TIMEOUT=60` — Inference timeout (seconds)
- `METRICS_ENABLED=true` — Enable Prometheus metrics
- `MODEL_CACHE_DIR=/app/cache` — Model cache location

**Build Command:**
```bash
docker build -f docker/Dockerfile.inference-prod -t aries-serpent:0.1.0-final-inference .
```

**Run Command:**
```bash
docker run -p 8001:8001 -p 8002:8002 \
  -v inference-cache:/app/cache \
  -e INFERENCE_BATCH_SIZE=32 \
  aries-serpent:0.1.0-final-inference
```

**Health Check:**
```bash
curl http://localhost:8002/health
```

---

### 3. Development Image (`aries-serpent:0.1.0-final-dev`)

**Target:** <800 MB  
**Dockerfile:** `docker/Dockerfile.dev-prod`  
**Base:** `python:3.12`

**Features:**
- Full development toolchain
- pytest, mypy, ruff, black pre-installed
- Jupyter Lab + IPython
- All test and optional dependencies
- SBOM for dependency tracking
- Interactive bash shell

**Exposed Ports:**
- `8888/TCP` — Jupyter Lab
- `8000/TCP` — FastAPI test server
- `8002/TCP` — Metrics endpoint

**Environment Variables:**
- `DEVELOPMENT_MODE=true`
- `JUPYTER_ENABLE_LAB=yes`
- `LOG_LEVEL=DEBUG`

**Build Command:**
```bash
docker build -f docker/Dockerfile.dev-prod -t aries-serpent:0.1.0-final-dev .
```

**Run Command (Interactive):**
```bash
docker run -it --rm \
  -p 8888:8888 \
  -p 8000:8000 \
  -v $(pwd):/workspace/src \
  aries-serpent:0.1.0-final-dev
```

**Run Jupyter:**
```bash
docker run -it -p 8888:8888 \
  -e JUPYTER_ENABLE_LAB=yes \
  aries-serpent:0.1.0-final-dev \
  jupyter lab --ip=0.0.0.0 --no-browser
```

---

## Build Process

### Prerequisites
- Docker 20.10+
- Python 3.12 installed locally
- 2-4 GB disk space (for building all 3 images)

### Step-by-Step Build

```bash
# 1. Navigate to repository root
cd /path/to/_codex_

# 2. Build API image
docker build -f docker/Dockerfile.api-prod -t aries-serpent:0.1.0-final-api . \
  --label "version=0.1.0-final" \
  --label "builddate=$(date -u +'%Y-%m-%dT%H:%M:%SZ')"

# 3. Build inference image
docker build -f docker/Dockerfile.inference-prod -t aries-serpent:0.1.0-final-inference . \
  --label "version=0.1.0-final" \
  --label "builddate=$(date -u +'%Y-%m-%dT%H:%M:%SZ')"

# 4. Build development image
docker build -f docker/Dockerfile.dev-prod -t aries-serpent:0.1.0-final-dev . \
  --label "version=0.1.0-final" \
  --label "builddate=$(date -u +'%Y-%m-%dT%H:%M:%SZ')"

# 5. Verify images
docker images | grep aries-serpent

# 6. Extract SBOM files
docker run --rm aries-serpent:0.1.0-final-api cat /app/bom.json > .codex/sbom/api-bom.json
docker run --rm aries-serpent:0.1.0-final-inference cat /app/bom.json > .codex/sbom/inference-bom.json
docker run --rm aries-serpent:0.1.0-final-dev cat /workspace/bom.json > .codex/sbom/dev-bom.json
```

### Automated Build Script

```bash
#!/bin/bash
# build-images.sh - Build all Aries-Serpent Docker images

set -e

VERSION="0.1.0-final"
BUILDDATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')

echo "🐳 Building Aries-Serpent Docker Images v${VERSION}"
echo "Build Date: ${BUILDDATE}"

# API Image
echo "📦 Building API image..."
docker build -f docker/Dockerfile.api-prod \
  -t aries-serpent:${VERSION}-api \
  --label "version=${VERSION}" \
  --label "builddate=${BUILDDATE}" \
  . && echo "✅ API image built"

# Inference Image
echo "📦 Building Inference image..."
docker build -f docker/Dockerfile.inference-prod \
  -t aries-serpent:${VERSION}-inference \
  --label "version=${VERSION}" \
  --label "builddate=${BUILDDATE}" \
  . && echo "✅ Inference image built"

# Development Image
echo "📦 Building Development image..."
docker build -f docker/Dockerfile.dev-prod \
  -t aries-serpent:${VERSION}-dev \
  --label "version=${VERSION}" \
  --label "builddate=${BUILDDATE}" \
  . && echo "✅ Development image built"

# Extract SBOMs
echo "📋 Extracting SBOMs..."
mkdir -p .codex/sbom
docker run --rm aries-serpent:${VERSION}-api cat /app/bom.json > .codex/sbom/api-bom.json
docker run --rm aries-serpent:${VERSION}-inference cat /app/bom.json > .codex/sbom/inference-bom.json
docker run --rm aries-serpent:${VERSION}-dev cat /workspace/bom.json > .codex/sbom/dev-bom.json

# Image statistics
echo "📊 Image Statistics:"
docker images | grep aries-serpent | awk '{print $1":"$2" → " $7}'

echo "✅ All images built successfully!"
```

---

## Testing Containers

### API Server Tests

```bash
# 1. Start container
docker run -d --name aries-api -p 8000:8000 \
  aries-serpent:0.1.0-final-api

# 2. Wait for startup
sleep 5

# 3. Test health endpoint
curl http://localhost:8000/health

# 4. Test ready endpoint
curl http://localhost:8000/ready

# 5. Check logs
docker logs aries-api

# 6. Clean up
docker stop aries-api && docker rm aries-api
```

### Inference Service Tests

```bash
# 1. Start container
docker run -d --name aries-inference \
  -p 8001:8001 \
  -p 8002:8002 \
  aries-serpent:0.1.0-final-inference

# 2. Test health
curl http://localhost:8002/health

# 3. Check metrics
curl http://localhost:8002/metrics

# 4. Clean up
docker stop aries-inference && docker rm aries-inference
```

### Development Image Tests

```bash
# 1. Start interactive session
docker run -it --rm \
  -v $(pwd):/workspace/src \
  aries-serpent:0.1.0-final-dev /bin/bash

# 2. Inside container:
pytest tests/
mypy src/codex
ruff check src/
black --check src/
```

---

## Image Size Optimization

| Image | Target | Strategy |
|-------|--------|----------|
| **API** | <500 MB | Multi-stage, slim base, minimal dependencies |
| **Inference** | <300 MB | Inference-only deps, no test tools |
| **Dev** | <800 MB | Full toolchain needed, acceptable size |

### Size Reduction Techniques Applied

1. **Multi-stage builds** — Only runtime code in final image
2. **Slim base images** — `python:3.12-slim` instead of full `python:3.12`
3. **Wheel caching** — Build wheels in builder stage, copy to runtime
4. **apt cleanup** — Remove package manager cache after install
5. **No pip cache** — Use `--no-cache` flag during pip install
6. **Minimal system packages** — Only essential runtime libraries

---

## SBOM (Software Bill of Materials)

All images include SBOM in SPDX JSON format for security scanning.

### SBOM Locations

- **API SBOM:** `/app/bom.json` → `.codex/sbom/api-bom.json`
- **Inference SBOM:** `/app/bom.json` → `.codex/sbom/inference-bom.json`
- **Dev SBOM:** `/workspace/bom.json` → `.codex/sbom/dev-bom.json`

### Generate SBOMs

```bash
# Extract SBOM from built image
docker run --rm aries-serpent:0.1.0-final-api cat /app/bom.json

# Scan with grype
grype aries-serpent:0.1.0-final-api

# Generate vulnerability report
grype aries-serpent:0.1.0-final-api --output json > .codex/sbom/api-vuln-report.json
```

---

## Security Scanning

### Trivy Container Scan

```bash
# Scan for vulnerabilities
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image aries-serpent:0.1.0-final-api

# Generate JSON report
trivy image --format json --output sbom/api-trivy-report.json \
  aries-serpent:0.1.0-final-api
```

### Container Security Checklist

- ✅ Non-root user (UID 1001)
- ✅ Read-only root filesystem support
- ✅ No privileged capabilities
- ✅ Health checks configured
- ✅ SBOM included
- ✅ Security scanning passed
- ✅ CVE vulnerability scan completed

---

## Docker Compose for Local Testing

```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: docker/Dockerfile.api-prod
    image: aries-serpent:0.1.0-final-api
    container_name: aries-api
    ports:
      - "8000:8000"
    environment:
      LOG_LEVEL: INFO
      CORS_ORIGINS: "*"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - aries-network

  inference:
    build:
      context: .
      dockerfile: docker/Dockerfile.inference-prod
    image: aries-serpent:0.1.0-final-inference
    container_name: aries-inference
    ports:
      - "8001:8001"
      - "8002:8002"
    environment:
      INFERENCE_BATCH_SIZE: "32"
      METRICS_ENABLED: "true"
    volumes:
      - inference-cache:/app/cache
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8002/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - aries-network

networks:
  aries-network:
    driver: bridge

volumes:
  inference-cache:
```

---

## Publishing Images

### Docker Registry (Docker Hub)

```bash
# Login
docker login -u <username>

# Tag images
docker tag aries-serpent:0.1.0-final-api <username>/aries-serpent:0.1.0-final-api
docker tag aries-serpent:0.1.0-final-inference <username>/aries-serpent:0.1.0-final-inference
docker tag aries-serpent:0.1.0-final-dev <username>/aries-serpent:0.1.0-final-dev

# Push
docker push <username>/aries-serpent:0.1.0-final-api
docker push <username>/aries-serpent:0.1.0-final-inference
docker push <username>/aries-serpent:0.1.0-final-dev
```

### Container Image Signing (Cosign)

```bash
# Generate key pair
cosign generate-key-pair

# Sign images
cosign sign --key cosign.key aries-serpent:0.1.0-final-api
cosign sign --key cosign.key aries-serpent:0.1.0-final-inference
cosign sign --key cosign.key aries-serpent:0.1.0-final-dev

# Verify signature
cosign verify --key cosign.pub aries-serpent:0.1.0-final-api
```

---

## Troubleshooting

### Build Failures

| Issue | Solution |
|-------|----------|
| Out of disk space | Run `docker system prune` to clean up |
| Build context too large | Check `.dockerignore` file |
| Dependency resolution errors | Verify Python version (3.12+) in base image |
| Permission denied on socket | Run with `sudo` or add user to docker group |

### Runtime Issues

| Issue | Solution |
|-------|----------|
| Container won't start | Check logs: `docker logs <container>` |
| Health check failing | Verify endpoints are implemented in app |
| Port already in use | Change port mapping: `-p 9000:8000` |
| Out of memory | Increase memory limits in deployment |

---

## References

- Dockerfile best practices: https://docs.docker.com/develop/develop-images/dockerfile_best-practices/
- Python security: https://python-poetry.org/docs/basic-usage/
- SBOM format: https://cyclonedx.org/
- Container scanning: https://github.com/aquasecurity/trivy

---

**Last Updated:** 2026-07-09  
**Status:** ✅ Production Ready
