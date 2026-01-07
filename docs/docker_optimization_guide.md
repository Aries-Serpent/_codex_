# Docker Optimization Guide (D1)

## Overview

This guide documents the optimized Docker setup for Codex ML with multi-stage builds, security hardening, and conditional feature flags. All Dockerfiles follow security best practices and are production-ready.

## Features

✅ **Multi-stage builds** - Separate builder and runtime stages for minimal image size  
✅ **Non-root user** - All containers run as `appuser` (UID 1000, GID 1000)  
✅ **ARG flags** - Conditional feature installation (GPU, MLflow, Ray, build environment)  
✅ **Security scanning** - Automated vulnerability scanning with Trivy and Hadolint  
✅ **Best practices** - Health checks, tini init, minimal base images, OCI labels  

## Dockerfiles

### Dockerfile.optimized (Recommended)

The main optimized Dockerfile with all D1 enhancements:

```bash
# Production CPU build
docker build -f Dockerfile.optimized -t codex:prod .

# Development with GPU and MLflow
docker build -f Dockerfile.optimized \
    --build-arg BUILD_ENV=dev \
    --build-arg ENABLE_GPU=1 \
    --build-arg ENABLE_MLFLOW=1 \
    -t codex:dev-gpu .

# Minimal build (no optional dependencies)
docker build -f Dockerfile.optimized \
    --build-arg BUILD_ENV=minimal \
    -t codex:minimal .
```

### Dockerfile.gpu

GPU-optimized build with CUDA support:

```bash
docker build -f Dockerfile.gpu -t codex:gpu .
```

## Build Arguments

### Environment Selection

| Argument | Values | Default | Description |
|----------|--------|---------|-------------|
| `BUILD_ENV` | `prod`, `dev`, `minimal` | `prod` | Build environment |
| `PYTHON_VERSION` | `3.10`, `3.11`, `3.12` | `3.11` | Python version |

### Feature Flags

| Argument | Values | Default | Description |
|----------|--------|---------|-------------|
| `ENABLE_GPU` | `0`, `1` | `0` | Enable GPU support (CUDA) |
| `ENABLE_MLFLOW` | `0`, `1` | `1` | Include MLflow tracking |
| `ENABLE_RAY` | `0`, `1` | `0` | Include Ray distributed training |

### Version Control

| Argument | Example | Default | Description |
|----------|---------|---------|-------------|
| `VERSION` | `1.0.0` | `0.0.0` | Application version |
| `VCS_REF` | `abc123` | `unknown` | Git commit SHA |
| `BUILD_DATE` | `2025-12-08T00:00:00Z` | `unknown` | Build timestamp |
| `TORCH_VERSION` | `2.4.0` | `2.4.0` | PyTorch version |

## Build Examples

### Production Builds

```bash
# Standard production build
docker build -f Dockerfile.optimized \
    --build-arg BUILD_ENV=prod \
    --build-arg VERSION=1.0.0 \
    --build-arg VCS_REF=$(git rev-parse HEAD) \
    --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
    -t codex:1.0.0 \
    -t codex:latest .

# Production with GPU
docker build -f Dockerfile.optimized \
    --build-arg BUILD_ENV=prod \
    --build-arg ENABLE_GPU=1 \
    --build-arg ENABLE_MLFLOW=1 \
    -t codex:1.0.0-gpu .

# Production with Ray (distributed training)
docker build -f Dockerfile.optimized \
    --build-arg BUILD_ENV=prod \
    --build-arg ENABLE_RAY=1 \
    -t codex:1.0.0-ray .
```

### Development Builds

```bash
# Development with all features
docker build -f Dockerfile.optimized \
    --build-arg BUILD_ENV=dev \
    --build-arg ENABLE_GPU=1 \
    --build-arg ENABLE_MLFLOW=1 \
    --build-arg ENABLE_RAY=1 \
    -t codex:dev .

# Development minimal
docker build -f Dockerfile.optimized \
    --build-arg BUILD_ENV=minimal \
    -t codex:dev-minimal .
```

### CI/CD Builds

```bash
# CI build with metadata
docker build -f Dockerfile.optimized \
    --build-arg BUILD_ENV=prod \
    --build-arg VERSION=${CI_COMMIT_TAG:-latest} \
    --build-arg VCS_REF=${CI_COMMIT_SHA} \
    --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
    --build-arg VCS_URL=${CI_PROJECT_URL} \
    -t ${CI_REGISTRY_IMAGE}:${CI_COMMIT_TAG} .
```

## Security Features

### Non-Root User

All containers run as `appuser` (UID 1000, GID 1000):

```dockerfile
# User is created in build stage
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid appuser --create-home appuser

# Switched at end of Dockerfile
USER appuser
```

Verify:
```bash
docker run --rm codex:latest id
# uid=1000(appuser) gid=1000(appuser) groups=1000(appuser)
```

### Minimal Base Images

- **CPU**: `python:3.11-slim` (smallest Python image)
- **GPU**: `nvidia/cuda:12.2.2-cudnn8-runtime-ubuntu22.04` (CUDA runtime only, no dev tools)

### No Secrets in Layers

Build arguments are not persisted in final image:

```bash
# Secrets passed at runtime via environment
docker run --env-file .env codex:latest

# Or mount secrets
docker run -v /path/to/secrets:/run/secrets codex:latest
```

### Vulnerability Scanning

Use the provided security scanning script:

```bash
# Scan an image
./scripts/docker_security_scan.sh codex:latest

# Scan with custom report directory
REPORT_DIR=./my-reports ./scripts/docker_security_scan.sh codex:prod
```

The script checks:
- ✅ Dockerfile linting (Hadolint)
- ✅ CVE vulnerabilities (Trivy)
- ✅ Docker Scout analysis
- ✅ Best practices compliance
- ✅ Non-root user verification
- ✅ Health check presence

## Running Containers

### Basic Run

```bash
docker run -d -p 8000:8000 codex:latest
```

### With Volume Mounts

```bash
docker run -d \
    -p 8000:8000 \
    -v $(pwd)/data:/app/data:ro \
    -v $(pwd)/logs:/app/logs \
    -v $(pwd)/artifacts:/app/artifacts \
    codex:latest
```

### With GPU

```bash
docker run -d \
    --gpus all \
    -p 8000:8000 \
    codex:gpu
```

### With Environment Variables

```bash
docker run -d \
    -p 8000:8000 \
    -e MLFLOW_TRACKING_URI=http://mlflow:5000 \
    -e LOG_LEVEL=debug \
    --env-file .env \
    codex:latest
```

## Image Size Comparison

| Build Configuration | Size (approx) |
|---------------------|---------------|
| Minimal CPU | ~800 MB |
| Production CPU | ~1.2 GB |
| Production CPU + MLflow | ~1.4 GB |
| Production GPU | ~4.5 GB |
| Production GPU + MLflow + Ray | ~5.2 GB |
| Development (all features) | ~5.5 GB |

## Multi-Stage Build Structure

```
┌─────────────────────────────────────┐
│ Stage 1: Builder                    │
│ - Compiles dependencies             │
│ - Creates wheels                    │
│ - Build tools installed             │
│ Size: ~2-3 GB (discarded)          │
└─────────────────────────────────────┘
              ↓ Copy wheels only
┌─────────────────────────────────────┐
│ Stage 2: Base Runtime (CPU)         │
│ - python:3.11-slim                  │
│ - Minimal runtime deps              │
│ - Non-root user                     │
└─────────────────────────────────────┘
              ↓ OR
┌─────────────────────────────────────┐
│ Stage 2: GPU Runtime                │
│ - nvidia/cuda:12.2.2-runtime        │
│ - Python + CUDA libraries           │
│ - Non-root user                     │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ Stage 3: Final Runtime              │
│ - Install wheels from builder       │
│ - Copy application code             │
│ - Configure healthcheck             │
│ - Switch to non-root user           │
│ Size: Optimized (~1-5 GB)          │
└─────────────────────────────────────┘
```

## Health Checks

All images include health checks:

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -fsS http://localhost:8000/health || exit 1
```

Check health status:

```bash
docker ps  # Shows health status
docker inspect codex | jq '.[0].State.Health'
```

## OCI Labels

Images include metadata labels:

```bash
docker inspect codex:latest | jq '.[0].Config.Labels'
```

Example labels:
```json
{
  "org.opencontainers.image.title": "codex",
  "org.opencontainers.image.version": "1.0.0",
  "org.opencontainers.image.revision": "abc123",
  "org.opencontainers.image.created": "2025-12-08T00:00:00Z",
  "org.label.build_env": "prod",
  "org.label.gpu_enabled": "0"
}
```

## Troubleshooting

### Issue: Build fails at wheel creation

**Solution**: Check that all dependencies are in requirements files:

```bash
# Test locally first
pip wheel --no-build-isolation --wheel-dir /tmp/wheels -r requirements/base.txt
```

### Issue: Image too large

**Solution**: Use minimal build or specific features:

```bash
docker build --build-arg BUILD_ENV=minimal -t codex:minimal .
```

### Issue: Permission denied errors

**Solution**: Ensure directories have correct permissions:

```dockerfile
RUN mkdir -p /app/logs && chown -R appuser:appuser /app/logs
```

### Issue: GPU not detected in container

**Solution**: Install nvidia-docker and use --gpus flag:

```bash
# Install nvidia-container-toolkit
# https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html

docker run --gpus all codex:gpu nvidia-smi
```

## Best Practices

### 1. Use Versioned Tags

```bash
# ❌ Don't use latest in production
docker pull codex:latest

# ✅ Use specific versions
docker pull codex:1.0.0
```

### 2. Scan Before Deploying

```bash
# Always scan before production deployment
./scripts/docker_security_scan.sh codex:1.0.0

# Check exit code
if [ $? -eq 0 ]; then
    docker push codex:1.0.0
fi
```

### 3. Use Build Cache

```bash
# Build with cache
docker build --cache-from codex:latest -t codex:new .

# Or use BuildKit
DOCKER_BUILDKIT=1 docker build -t codex:new .
```

### 4. Minimize Layers

```bash
# ❌ Multiple RUN commands
RUN apt-get update
RUN apt-get install -y curl
RUN rm -rf /var/lib/apt/lists/*

# ✅ Combined RUN command
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
```

## Deferred Item D1 Completion

### Implementation Date
2025-12-08

### Deliverables Completed
✅ Optimized Dockerfile with multi-stage builds (`Dockerfile.optimized`)  
✅ Non-root user implementation (appuser:1000:1000)  
✅ ARG flags for conditional features (BUILD_ENV, ENABLE_GPU, ENABLE_MLFLOW, ENABLE_RAY)  
✅ Security scanning script (`scripts/docker_security_scan.sh`)  
✅ Comprehensive documentation (this file)  
✅ OCI metadata labels  
✅ Health checks configured  
✅ Build examples for all scenarios  

### Security Features Implemented
✅ Multi-stage builds (builder + runtime)  
✅ Minimal base images (python-slim, cuda-runtime)  
✅ Non-root user (all containers)  
✅ No secrets in layers  
✅ Tini init system (zombie process reaping)  
✅ Vulnerability scanning script  
✅ Health checks  
✅ Proper file permissions  

### Next Steps
1. ✅ D4: Config Consolidation - COMPLETE
2. ✅ D3: Multi-node Training - COMPLETE
3. ✅ D1: Docker Optimization - COMPLETE
4. Continue with D2: Plugin Registry

## References

- [Docker Multi-Stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [Docker Security Best Practices](https://docs.docker.com/develop/security-best-practices/)
- [OCI Image Spec](https://github.com/opencontainers/image-spec)
- [Trivy Scanner](https://github.com/aquasecurity/trivy)
- [Hadolint](https://github.com/hadolint/hadolint)
