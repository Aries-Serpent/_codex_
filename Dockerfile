# syntax=docker/dockerfile:1.7
# Minimal, reproducible image for FastAPI/CLI runtime
# Set A: minimal image + CI (fast)
FROM python:3.11-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# System deps (keep minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates tini \
 && rm -rf /var/lib/apt/lists/*

# Non-root runtime user
RUN groupadd --gid 1000 appuser && useradd --uid 1000 --gid appuser -m appuser

WORKDIR /app

# Copy dependency manifests early for better layer caching
# Supports either requirements.txt or pyproject-based install
COPY requirements.txt /app/ 2>/dev/null || true
COPY pyproject.toml /app/ 2>/dev/null || true
COPY uv.lock /app/ 2>/dev/null || true
COPY requirements.lock /app/ 2>/dev/null || true

# Upgrade pip tooling
RUN pip install --upgrade pip setuptools wheel

# Prefer pinned requirements if available; fallback to editable install later
RUN if [ -f "requirements.txt" ]; then pip install -r requirements.txt; fi

# Copy application source
COPY src/ /app/src/
# Include configs if present (Hydra/YAML defaults)
COPY configs/ /app/configs/ 2>/dev/null || true

# Install project in editable mode if no requirements manifest was provided
RUN if [ ! -f "requirements.txt" ] && [ -f "pyproject.toml" ]; then \
      pip install .; \
    fi

# Expose default FastAPI port
EXPOSE 8000

# Switch to non-root
USER appuser

# Default command assumes a FastAPI app at src/codex/api/app.py exposing `app`
# Adjust as needed for your repo layout.
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["uvicorn", "src.codex.api.app:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]
