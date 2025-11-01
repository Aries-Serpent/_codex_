# MSP Gateway Dockerfile (Local-first, Offline-capable)
# 
# Purpose:
# - Provide a reproducible container environment for the MSP Gateway
# - Support local development and testing
# - Optional in Local Mode (primary use case is venv-based)
#
# Build:
#   docker build -f docker/msp-gateway.Dockerfile -t msp-gateway:local .
#
# Run:
#   docker run -p 8080:8080 -v $(pwd)/.codex:/app/.codex msp-gateway:local

FROM python:3.11-slim

# Metadata
LABEL maintainer="MSP Gateway Team"
LABEL description="Tenant-aware inference API with local RAG and vector search"
LABEL version="0.1.0"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt* pyproject.toml* setup.py* ./
COPY src/ ./src/
COPY services/ ./services/
COPY policies/ ./policies/
COPY configs/ ./configs/

# Install Python package and dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e . && \
    pip install --no-cache-dir \
        fastapi \
        uvicorn[standard] \
        httpx \
        sentence-transformers \
        faiss-cpu \
        pydantic \
        pydantic-settings \
        pyyaml

# Create required directories
RUN mkdir -p /app/.codex/logs \
             /app/.codex/tenants \
             /app/artifacts/emb

# Environment variables (defaults)
ENV MSP_OFFLINE=1 \
    MSP_HOST=0.0.0.0 \
    MSP_PORT=8080 \
    MSP_LOG_LEVEL=INFO \
    MSP_MODEL_BACKEND=mock \
    MSP_VECTOR_BACKEND=faiss \
    PYTHONUNBUFFERED=1

# Expose gateway port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run gateway
CMD ["uvicorn", "services.msp_gateway.main:app", "--host", "0.0.0.0", "--port", "8080"]
