# Basic, reproducible test image for running pytest in CI and locally
# Maintainer note: This image is designed for deterministic test execution.
# Update pinned versions in requirements-test.txt with care.
FROM python:3.11-slim

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

# Switch to non-root user for security
USER appuser

# Default command: run pytest and write coverage to mounted artifacts directory
# The CI script will mount ./artifacts -> /workspace/artifacts so reports are accessible outside container
# Note: Using bash -c (not -lc) to avoid login shell initialization for deterministic behavior
# Output is minimized with --tb=short --no-header -q to prevent token limit issues in CI
CMD ["bash", "-c", "pytest --maxfail=1 --disable-warnings --tb=short --no-header --cov=src --cov-report=xml:${COVERAGE_DIR}/coverage.xml --cov-report=html:${COVERAGE_DIR}/htmlcov -q"]
