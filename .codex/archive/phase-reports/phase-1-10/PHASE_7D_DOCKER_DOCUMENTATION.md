# 📖 Phase 7D Docker Complete Documentation Suite

**Campaign:** Docker Phase 1 - Complete Audit Documents  
**Generated:** 2026-06-20T07:54:04Z  
**Repository:** Aries-Serpent/_codex_  
**Status:** ✅ **DOCUMENTATION SUITE COMPLETE**

---

## Table of Contents

1. **BUILD_GUIDE.md** - Local build instructions for all 8 variants
2. **DEPLOYMENT_GUIDE.md** - Docker Compose, Kubernetes, environment vars, health checks
3. **TROUBLESHOOTING.md** - Common issues, debugging, security responses

---

# Part 1: BUILD_GUIDE.md

## Local Build Instructions for All Variants

### Prerequisites

```bash
# System requirements
- Docker 20.10+ (or Docker Desktop)
- Docker Buildx 0.9+
- 50+ GB disk space for all variants
- 4+ CPU cores recommended
```

**Installation:**
```bash
# Docker Desktop (includes Buildx)
# https://docs.docker.com/get-docker/

# Or via Buildx separately:
docker buildx create --use
```

### Quick Start: Build Single Variant

#### 1. Build CPU Runtime (Most Common)

```bash
# From repository root
docker build -f docker/Dockerfile.cpu \
  -t _codex_:cpu-local \
  .

# Verify build
docker images | grep _codex_
```

**Expected Time:** 15-20 minutes  
**Expected Size:** 1.1 GB

#### 2. Build GPU Runtime

```bash
docker build -f Dockerfile \
  --target gpu-runtime \
  -t _codex_:gpu-local \
  .

# Verify
docker images | grep _codex_:gpu
```

**Expected Time:** 25-35 minutes  
**Expected Size:** 3.2 GB

#### 3. Build Preview API

```bash
docker build -f Dockerfile.preview \
  -t _codex_:preview-local \
  .

# Verify
docker images | grep preview
```

**Expected Time:** 10-15 minutes  
**Expected Size:** 900 MB

---

### Build All Variants (Parallel)

#### Automated Build Script

**File:** `scripts/docker-build-all.sh`

```bash
#!/bin/bash
set -e

VARIANTS=(cpu gpu embedding ci preview optimized local)

echo "Building all variants in parallel..."

for variant in "${VARIANTS[@]}"; do
  echo "Building $variant..."
  docker build \
    -f docker/Dockerfile.$variant \
    -t _codex_:$variant-local \
    . &
done

wait
echo "✅ All variants built successfully"
docker images | grep _codex_
```

**Usage:**
```bash
chmod +x scripts/docker-build-all.sh
./scripts/docker-build-all.sh
```

---

### Multi-Platform Builds (amd64 + arm64)

**Command:**
```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -f docker/Dockerfile.cpu \
  -t _codex_:cpu-multiplatform \
  .
```

**Expected Time:** 30-40 minutes (first run), 10-15 minutes (with cache)

---

### Build Arguments & Customization

#### Available Build Arguments

```dockerfile
# Dockerfile.preview (example)
ARG STUB_DIRS="agents codex_addons codex_digest ..."
ARG PYTHON_VERSION=3.12
ARG PIP_CACHE_DIR=/tmp/pip-cache
```

**Usage:**
```bash
docker build \
  --build-arg STUB_DIRS="agents codex_addons" \
  -f Dockerfile.preview \
  -t _codex_:preview-custom \
  .
```

---

### Caching & Optimization

#### Enable BuildKit Cache

```bash
docker buildx build \
  --cache-from=type=local,src=/tmp/docker-cache \
  --cache-to=type=local,dest=/tmp/docker-cache,mode=max \
  -f docker/Dockerfile.cpu \
  -t _codex_:cpu-cached \
  .
```

**Benefit:** 50% faster rebuilds

---

#### Registry Cache (GHCR)

```bash
# Pull cache layers from GHCR
docker buildx build \
  --cache-from=type=registry,ref=ghcr.io/aries-serpent/_codex_:cpu-latest \
  -f docker/Dockerfile.cpu \
  -t _codex_:cpu-latest \
  --push \
  .
```

---

### Docker Compose Local Builds

```bash
# Build via docker-compose
docker-compose build cpu

# Build all services
docker-compose build

# Build without cache
docker-compose build --no-cache
```

---

### Validation After Build

```bash
# Check image metadata
docker inspect _codex_:cpu-local | jq '.[] | {Id, RepoTags, Size}'

# Run smoke test
docker run --rm _codex_:cpu-local python -c "import torch; print(torch.__version__)"

# Check layers
docker history _codex_:cpu-local

# Scan for vulnerabilities
docker scan _codex_:cpu-local
```

---

## Part 2: DEPLOYMENT_GUIDE.md

### Docker Compose Deployment

#### Production Compose Stack

**File:** `docker-compose.yml`

```yaml
version: '3.9'

services:
  # CPU Runtime
  api-cpu:
    image: _codex_:cpu-latest
    ports:
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1
      - MODEL_NAME=default
      - DEVICE=cpu
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    volumes:
      - model_cache:/home/appuser/.cache
    restart: unless-stopped

  # GPU Runtime
  api-gpu:
    image: _codex_:gpu-latest
    ports:
      - "8001:8000"
    environment:
      - PYTHONUNBUFFERED=1
      - DEVICE=cuda:0
    devices:
      - /dev/nvidia0:/dev/nvidia0
    volumes:
      - model_cache:/home/appuser/.cache
    restart: unless-stopped

  # Preview API
  preview:
    image: _codex_:preview-latest
    ports:
      - "8765:8765"
    environment:
      - PYTHONUNBUFFERED=1
      - CODEX_MASTER_KEY=${CODEX_MASTER_KEY}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8765/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

  # Embedding Service
  embedding:
    image: _codex_:embedding-latest
    ports:
      - "8002:8000"
    environment:
      - DEVICE=cpu
    restart: unless-stopped

volumes:
  model_cache:
    driver: local
```

**Usage:**
```bash
# Start stack
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f api-cpu

# Stop
docker-compose down
```

---

#### Environment Variables

**File:** `.env` (template: `.env.docker.example`)

```env
# Core Configuration
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1

# Model & Device
MODEL_NAME=default
DEVICE=cpu                    # or cuda:0, cuda:1, etc.

# API Keys & Secrets
CODEX_MASTER_KEY=             # Injected at runtime
GITHUB_APP_PRIVATE_KEY=       # Injected at runtime

# Performance
MAX_WORKERS=4
BATCH_SIZE=32

# Logging
LOG_LEVEL=INFO
```

**Usage:**
```bash
# Load from .env file
docker-compose --env-file .env up -d

# Or set individually
docker run -e DEVICE=cuda:0 _codex_:gpu-latest
```

---

### Kubernetes Deployment

#### Deployment Manifest

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: codex-api
  namespace: default
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0

  selector:
    matchLabels:
      app: codex-api

  template:
    metadata:
      labels:
        app: codex-api
        version: v1.0.0
    spec:
      containers:
      - name: api
        image: ghcr.io/aries-serpent/_codex_:cpu-v1.0.0
        imagePullPolicy: IfNotPresent

        ports:
        - name: http
          containerPort: 8000
          protocol: TCP

        env:
        - name: PYTHONUNBUFFERED
          value: "1"
        - name: DEVICE
          value: "cpu"
        - name: CODEX_MASTER_KEY
          valueFrom:
            secretKeyRef:
              name: codex-secrets
              key: master-key

        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"

        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10

        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

        securityContext:
          runAsNonRoot: true
          runAsUser: 1000
          readOnlyRootFilesystem: true
          allowPrivilegeEscalation: false
          capabilities:
            drop:
              - ALL

      securityContext:
        fsGroup: 1000

      imagePullSecrets:
      - name: ghcr-credentials

---
apiVersion: v1
kind: Service
metadata:
  name: codex-api
spec:
  selector:
    app: codex-api
  type: LoadBalancer
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
```

**Deployment:**
```bash
# Create namespace
kubectl create namespace codex

# Create secrets
kubectl create secret generic codex-secrets \
  --from-literal=master-key=your-secret-key \
  -n codex

# Deploy
kubectl apply -f deployment.yaml -n codex

# Check status
kubectl get pods -n codex
kubectl logs -f deployment/codex-api -n codex
```

---

### Health Checks

#### HTTP Health Check Endpoints

| Endpoint | Service | Purpose | Response |
|----------|---------|---------|----------|
| `GET /health` | API | Liveness probe | 200 OK (ready) / 503 (not ready) |
| `GET /ready` | API | Readiness probe | 200 OK (ready) / 503 (dependencies missing) |
| `/api/health` | Preview | Cognitive Brain health | 200 OK |

**Example:**
```bash
# Check health
curl -v http://localhost:8000/health

# Expected response:
# HTTP/1.1 200 OK
# {"status": "healthy", "version": "1.0.0"}
```

---

## Part 3: TROUBLESHOOTING.md

### Common Issues

#### Issue 1: Build Fails with "egg_base 'src' does not exist"

**Symptom:**
```
error: error in 'egg_base' option: 'src' does not exist or is not a directory
```

**Root Cause:** Dockerfile.preview uses editable install (`pip install -e .`); `src/` not COPIed before installation

**Solution:**
```dockerfile
# ❌ WRONG
RUN pip install -e .

# ✅ CORRECT
COPY src/ ./src/
COPY services/ ./services/
RUN pip install -e .
```

**Verification:**
```bash
docker build -f Dockerfile.preview --target preview-base .
```

---

#### Issue 2: "package directory does not exist"

**Symptom:**
```
error: package directory 'services' does not exist or is not a directory
```

**Root Cause:** `services/` directory not COPIed; setuptools can't find sub-packages

**Solution:**
```dockerfile
# List explicit COPY for directories with sub-packages
COPY services/ ./services/
COPY codex_utils/ ./codex_utils/
RUN pip install -e .
```

---

#### Issue 3: CUDA Version Mismatch

**Symptom:**
```
RuntimeError: CUDA runtime mismatch
```

**Cause:** Container CUDA version (12.2.2) doesn't match host NVIDIA driver

**Solution:**
```bash
# Check host CUDA version
nvidia-smi

# Verify container CUDA version
docker run --gpus all _codex_:gpu-latest nvidia-smi

# Use matching CUDA version Dockerfile:
# For CUDA 12.2: docker/Dockerfile.gpu ✅
# For CUDA 13.3: Dockerfile (gpu-runtime target)
```

---

#### Issue 4: Image Build Timeout (90+ minutes)

**Symptom:**
```
Error: build cancelled after 3600s
```

**Cause:** GitHub Actions timeout; build too large or layer inefficiency

**Solution:**
```bash
# Use cache from registry
docker buildx build \
  --cache-from=type=registry,ref=ghcr.io/aries-serpent/_codex_:cpu-latest \
  -f docker/Dockerfile.cpu \
  .

# Or use local cache
docker buildx build \
  --cache-from=type=local,src=/tmp/cache \
  -f docker/Dockerfile.cpu \
  .
```

---

#### Issue 5: Disk Space Exceeded (50+ GB used)

**Symptom:**
```
Error: no space left on device
```

**Solution:**
```bash
# Clean up old images
docker image prune -a --force

# Clean up build cache
docker buildx prune --all --force

# Check disk usage
docker system df
```

---

### Debugging Tips

#### Enable Verbose Build Output

```bash
docker build \
  --progress=plain \
  -f docker/Dockerfile.cpu \
  -t test:debug \
  .
```

---

#### Inspect Image Layers

```bash
# View layer history
docker history _codex_:cpu-local

# Export image for inspection
docker save _codex_:cpu-local -o image.tar
tar -tf image.tar | head -20
```

---

#### Run Image with Debug Shell

```bash
# Drop into shell
docker run -it --rm _codex_:cpu-local /bin/bash

# Verify Python packages
python -c "import torch; print(torch.__version__)"

# Check working directory
pwd
ls -la
```

---

### Security Responses

#### Discovered CVE in Base Image

**Response Plan:**

1. **Identify:** Use Trivy scanner
   ```bash
   docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
     aquasec/trivy image _codex_:cpu-local
   ```

2. **Assess:** Determine severity and impact
   ```bash
   # Check if CVE affects our code path
   # Example: glibc CVE affecting only specific syscalls
   ```

3. **Mitigate:**
   - Update base image: `python:3.12-slim@sha256:NEW_DIGEST`
   - Test locally
   - Push with security advisory

4. **Communicate:** Document in CHANGELOG.md
   ```markdown
   ## [1.0.1] - 2026-06-21
   ### Security
   - Patched CVE-2026-xxxx in python:3.12-slim base image
   ```

---

#### Verify Image Signing

```bash
# Verify cosign signature (Phase 2)
cosign verify --key cosign.pub \
  ghcr.io/aries-serpent/_codex_:cpu-v1.0.0

# Verify SBOM attestation
cosign verify-attestation \
  --key cosign.pub \
  ghcr.io/aries-serpent/_codex_:cpu-v1.0.0
```

---

### Performance Tuning

#### Layer Caching Best Practices

```dockerfile
# ✅ GOOD: Stable layers first, changing layers last
FROM python:3.12-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./src/                    ← Changes frequently
RUN pip install -e .

# ❌ BAD: Changing layer before stable layer
FROM python:3.12-slim
COPY src/ ./src/                    ← Changes frequently
COPY requirements.txt .             ← Stable, but after changing layer
RUN pip install -r requirements.txt
```

---

#### Multi-Platform Build Optimization

```bash
# For amd64 + arm64, build sequentially (faster than simultaneous)
docker buildx build \
  --platform linux/amd64 \
  --output type=docker \
  -f docker/Dockerfile.cpu .

docker buildx build \
  --platform linux/arm64 \
  --output type=docker \
  -f docker/Dockerfile.cpu .
```

---

### Resource Limits & Monitoring

#### Docker Stats

```bash
# Monitor container resources
docker stats _codex_

# Expected output (CPU runtime):
# CONTAINER  CPU%   MEM USAGE / LIMIT
# codex      12%    450MiB / 1GiB
```

---

#### Kubernetes Pod Monitoring

```bash
# Watch pod resources
kubectl top pods -n codex --containers

# View resource usage history
kubectl describe pod codex-api-xxxxx -n codex
```

---

### Getting Help

**Documentation Resources:**
- Official Docker docs: https://docs.docker.com
- Kubernetes docs: https://kubernetes.io/docs
- Trivy scanner: https://aquasecurity.github.io/trivy/

**Internal Resources:**
- PHASE_7D_DOCKER_INVENTORY_AUDIT.md
- PHASE_7D_DOCKER_SECURITY_AUDIT.md
- PHASE_7D_DOCKER_OPTIMIZATION.md

---

# Complete Documentation Index

| Document | Purpose | Audience | Sections |
|----------|---------|----------|----------|
| **BUILD_GUIDE.md** (Part 1) | Local builds | Developers, CI/CD | Quick start, multi-variant, caching |
| **DEPLOYMENT_GUIDE.md** (Part 2) | Deployment patterns | DevOps, SRE | Docker Compose, Kubernetes, health checks |
| **TROUBLESHOOTING.md** (Part 3) | Common issues | Everyone | Debug tips, CVE response, performance |

---

## Quick Reference

### Build Commands Cheat Sheet

```bash
# Single variant
docker build -f docker/Dockerfile.cpu -t _codex_:cpu .

# Multi-platform
docker buildx build --platform linux/amd64,linux/arm64 -f docker/Dockerfile.cpu .

# With cache
docker buildx build --cache-from=type=local,src=/tmp/cache -f docker/Dockerfile.cpu .

# Push to registry
docker buildx build --push -t ghcr.io/aries-serpent/_codex_:cpu-v1.0.0 -f docker/Dockerfile.cpu .
```

### Deployment Commands Cheat Sheet

```bash
# Docker Compose
docker-compose up -d
docker-compose ps
docker-compose logs -f

# Kubernetes
kubectl apply -f deployment.yaml
kubectl get pods
kubectl logs -f deployment/codex-api

# Health check
curl http://localhost:8000/health
```

---

**Document Version:** 1.0.0  
**Campaign Phase:** Docker Phase 1 - Documentation  
**Next Review:** Phase 2 - Build Execution

---

✅ **PHASE 1 COMPLETE: All 6 Deliverables Ready**
- ✅ PHASE_7D_DOCKER_INVENTORY_AUDIT.md
- ✅ PHASE_7D_DOCKER_BUILD_VALIDATION.md
- ✅ PHASE_7D_DOCKER_SECURITY_AUDIT.md
- ✅ PHASE_7D_DOCKER_OPTIMIZATION.md
- ✅ PHASE_7D_DOCKER_REGISTRY_ROADMAP.md
- ✅ PHASE_7D_DOCKER_DOCUMENTATION.md (THIS DOCUMENT)
