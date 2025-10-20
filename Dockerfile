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
COPY requirements.docker.txt /app/ 2>/dev/null || true
COPY pyproject.toml /app/ 2>/dev/null || true
COPY uv.lock /app/ 2>/dev/null || true
COPY requirements.lock /app/ 2>/dev/null || true

# Upgrade pip tooling
RUN pip install --upgrade pip setuptools wheel

# Prefer container-specific pins; fallback to requirements.txt if present
RUN if [ -f "requirements.docker.txt" ]; then \
      pip install -r requirements.docker.txt; \
    elif [ -f "requirements.txt" ]; then \
      pip install -r requirements.txt; \
    fi

# Copy application source
COPY src/ /app/src/
# Include configs if present (Hydra/YAML defaults)
COPY configs/ /app/configs/ 2>/dev/null || true

# Install project if no requirements manifests were provided
RUN if [ ! -f "requirements.docker.txt" ] && [ ! -f "requirements.txt" ] && [ -f "pyproject.toml" ]; then \
      pip install .; \
    fi

# Copy entrypoint scripts
COPY docker/ /app/docker/
RUN chmod +x /app/docker/entrypoint.sh

# Expose default FastAPI port
EXPOSE 8000

# Container healthcheck for readiness (fallback to / if /health is not present)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -fsS http://localhost:8000/health || curl -fsS http://localhost:8000/ || exit 1

# Switch to non-root
USER appuser

# Default entrypoint + command:
# - entrypoint sets up env and then execs the given command
# - cmd runs uvicorn against the FastAPI app by default
ENTRYPOINT ["/app/docker/entrypoint.sh"]
CMD ["uvicorn", "src.codex.api.app:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]
