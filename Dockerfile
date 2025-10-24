# syntax=docker/dockerfile:1.7
# Minimal, reproducible image for FastAPI/CLI runtime
# Set A: minimal image + CI (fast)

# Build-time metadata (optional; pass via --build-arg)
ARG VERSION="0.0.0"
ARG VCS_REF="unknown"
ARG BUILD_DATE="unknown"
ARG VCS_URL="https://github.com/Aries-Serpent/_codex_"

FROM python:3.11-slim AS base

# Re-declare build metadata args for this stage
ARG VERSION
ARG VCS_REF
ARG BUILD_DATE
ARG VCS_URL

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# System deps (keep minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates tini \
 && rm -rf /var/lib/apt/lists/*

# OCI labels for provenance/metadata
LABEL org.opencontainers.image.title="codex" \
      org.opencontainers.image.description="Aries-Serpent _codex_ runtime image" \
      org.opencontainers.image.url="${VCS_URL}" \
      org.opencontainers.image.source="${VCS_URL}" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.revision="${VCS_REF}" \
      org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.licenses="Apache-2.0" \
      org.opencontainers.image.vendor="Aries-Serpent" \
      org.opencontainers.image.base.name="python:3.11-slim"

# Non-root runtime user
RUN groupadd --gid 1000 appuser && useradd --uid 1000 --gid appuser -m appuser

WORKDIR /app

# Copy dependency manifests early for better layer caching.
# BuildKit bind mount lets us conditionally copy only files that exist.
RUN --mount=type=bind,source=.,target=/tmp/context,ro \
    mkdir -p /app/requirements && \
    for file in requirements/base.txt requirements/docker.txt pyproject.toml uv.lock requirements/lock.txt; do \
        if [ -f "/tmp/context/${file}" ]; then \
            cp "/tmp/context/${file}" "/app/${file}"; \
        fi; \
    done

# Upgrade pip tooling
RUN pip install --upgrade pip setuptools wheel

# Prefer container-specific pins; fallback to requirements/base.txt if present
RUN if [ -f "requirements/docker.txt" ]; then \
      pip install -r requirements/docker.txt; \
    elif [ -f "requirements/base.txt" ]; then \
      pip install -r requirements/base.txt; \
    fi

# Copy application source
COPY src/ /app/src/
# Include configs if present (Hydra/YAML defaults)
RUN --mount=type=bind,source=.,target=/tmp/context,ro \
    if [ -d "/tmp/context/configs" ]; then \
        mkdir -p /app/configs && cp -r /tmp/context/configs/. /app/configs/; \
    fi

# Install project if no requirements manifests were provided
RUN if [ ! -f "requirements/docker.txt" ] && [ ! -f "requirements/base.txt" ] && [ -f "pyproject.toml" ]; then \
      pip install .; \
    fi

# Copy container entrypoint script
COPY docker/entrypoint.sh /app/docker/entrypoint.sh
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
ENV APP_MODULE="src.codex.api.app:app"
ENTRYPOINT ["/app/docker/entrypoint.sh"]
CMD ["uvicorn", "src.codex.api.app:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]
