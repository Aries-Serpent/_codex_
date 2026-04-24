# Multi-stage Dockerfile for Codex ML
# Provides separate cpu-runtime and gpu-runtime targets for deployment

# ===== Stage 1: Base Image =====
FROM python:3.12-slim AS base

# Metadata
LABEL org.opencontainers.image.source="https://github.com/Aries-Serpent/_codex_"
LABEL org.opencontainers.image.description="Codex ML base environment"
LABEL org.opencontainers.image.version="1.0.0"

# Environment configuration
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Install OS dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    git \
    curl \
  && rm -rf /var/lib/apt/lists/*

# Copy dependency manifests for layer caching
COPY --chown=appuser:appuser requirements.txt requirements.txt
COPY --chown=appuser:appuser pyproject.toml pyproject.toml
COPY --chown=appuser:appuser README.md README.md

# Install core dependencies
RUN python -m pip install --upgrade pip setuptools wheel

# Copy source code
COPY --chown=appuser:appuser src/ ./src/

# Install the package with core dependencies
RUN pip install --no-cache-dir -e ".[core]"

# ===== Stage 2: CPU Runtime =====
FROM base AS cpu-runtime

LABEL org.opencontainers.image.description="Codex ML CPU runtime"

# Install CPU-optimized PyTorch
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

USER appuser

ENTRYPOINT ["python", "-m", "codex_ml"]
CMD ["--help"]

# ===== Stage 3: GPU Runtime =====
FROM nvidia/cuda:13.2.1-runtime-ubuntu22.04 AS gpu-runtime

LABEL org.opencontainers.image.description="Codex ML GPU runtime"

# Install Python 3.12
RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common \
  && add-apt-repository ppa:deadsnakes/ppa \
  && apt-get update \
  && apt-get install -y --no-install-recommends \
    python3.12 \
    python3.12-venv \
    python3.12-dev \
    python3-pip \
    build-essential \
    gcc \
    git \
    curl \
  && rm -rf /var/lib/apt/lists/*

# Set Python 3.12 as default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1

WORKDIR /app

# Copy project files
COPY --chown=root:root requirements.txt requirements.txt
COPY --chown=root:root pyproject.toml pyproject.toml
COPY --chown=root:root README.md README.md
COPY --chown=root:root src/ ./src/

# Install dependencies (rebuild instead of copy for compatibility)
RUN python3 -m pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -e ".[core]"

# Install GPU-enabled PyTorch
RUN pip install --no-cache-dir torch torchvision torchaudio

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser && \
    chown -R appuser:appuser /app

ENV CUDA_VISIBLE_DEVICES=0

USER appuser

ENTRYPOINT ["python3", "-m", "codex_ml"]
CMD ["--help"]

# ===== Stage 4: Test Environment (default) =====
FROM python:3.12-slim AS test

# Metadata
LABEL org.opencontainers.image.source="https://github.com/Aries-Serpent/_codex_"
LABEL org.opencontainers.image.description="Codex ML test environment"
LABEL org.opencontainers.image.version="1.0.0"

# Environment configuration
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV COVERAGE_DIR=/workspace/artifacts
ENV COVERAGE_THRESHOLD=90

# Create non-root user for security (production best practice)
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /workspace

# Install OS dependencies for builds & tests
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    git \
    curl \
  && rm -rf /var/lib/apt/lists/*

# Copy only dependency manifests first for Docker layer caching
# This allows faster rebuilds when only source code changes
COPY --chown=appuser:appuser requirements-test.txt requirements-test.txt
COPY --chown=appuser:appuser requirements.txt requirements.txt
COPY --chown=appuser:appuser pyproject.toml pyproject.toml

# Install pip, wheel, then test dependencies
RUN python -m pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements-test.txt

# Copy the rest of the source code
COPY --chown=appuser:appuser . /workspace

# Install the package into the image using the exact pip invocation that CI will be documented to use.
# This ensures pip install path parity between Docker and CI environments.
# CI Documentation: Use `pip install --no-cache-dir .` for consistent behavior.
RUN pip install --no-cache-dir .

# Ensure artifacts directory exists and is owned by non-root user
RUN mkdir -p ${COVERAGE_DIR} && chown -R appuser:appuser ${COVERAGE_DIR}

# Make test runner script executable
RUN chmod +x /workspace/scripts/ci/docker_pytest.sh

# Switch to non-root user for security
USER appuser

# Default command: run pytest via the shell script
# The CI script will mount ./artifacts -> /workspace/artifacts so reports are accessible outside container
# Note: Using the dedicated shell script for maintainability and consistency
CMD ["/workspace/scripts/ci/docker_pytest.sh"]
