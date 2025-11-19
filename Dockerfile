# syntax=docker/dockerfile:1.7
# Multi-stage build for the Codex runtime (CPU variant)

# Build-time metadata (optional; pass via --build-arg)
ARG VERSION="0.0.0"
ARG VCS_REF="unknown"
ARG BUILD_DATE="unknown"
ARG VCS_URL="https://github.com/Aries-Serpent/_codex_"

# For immutable builds, prefer digest pinning. Example:
# FROM python:3.11-slim@sha256:<digest-here>
FROM python:3.11-slim AS builder

ARG VERSION
ARG VCS_REF
ARG BUILD_DATE
ARG VCS_URL

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Stage dependency manifests first to maximise layer reuse.
COPY pyproject.toml ./
COPY MANIFEST.in ./
COPY requirements/ ./requirements/
COPY uv.lock ./uv.lock

RUN --mount=type=cache,target=/root/.cache/pip pip install --upgrade pip setuptools wheel
RUN --mount=type=cache,target=/root/.cache/pip mkdir -p /tmp/wheels

# Build wheels for runtime dependencies so the final stage installs offline.
RUN --mount=type=cache,target=/root/.cache/pip if [ -f "requirements/docker.txt" ]; then \
      pip wheel --no-build-isolation --wheel-dir /tmp/wheels -r requirements/docker.txt; \
    elif [ -f "requirements/base.txt" ]; then \
      pip wheel --no-build-isolation --wheel-dir /tmp/wheels -r requirements/base.txt; \
    fi

# Copy the full source tree and build a project wheel.
COPY . .
RUN --mount=type=cache,target=/root/.cache/pip pip wheel --no-build-isolation --no-deps --wheel-dir /tmp/wheels .

# For immutable builds, prefer digest pinning. Example:
# FROM python:3.11-slim@sha256:<digest-here>
FROM python:3.11-slim AS runtime

ARG VERSION
ARG VCS_REF
ARG BUILD_DATE
ARG VCS_URL

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PATH="/opt/venv/bin:${PATH}"

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

# Materialise a dedicated virtualenv and install from the cached wheels.
COPY --from=builder /tmp/wheels /tmp/wheels
RUN python -m venv /opt/venv \
 && /opt/venv/bin/pip install --upgrade pip \
 && /opt/venv/bin/pip install /tmp/wheels/*.whl \
 && rm -rf /tmp/wheels

# Copy runtime assets (configs, Hydra defaults, source for debugging).
COPY --from=builder /app/configs /app/configs
COPY --from=builder /app/hydra /app/hydra
COPY --from=builder /app/src /app/src
COPY docker/entrypoint.sh /app/docker/entrypoint.sh
RUN chmod +x /app/docker/entrypoint.sh

# Default FastAPI port
EXPOSE 8000

# Container healthcheck for readiness (fallback to / if /health is not present)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -fsS http://localhost:8000/health || curl -fsS http://localhost:8000/ || exit 1

# Switch to non-root
USER appuser

# Default entrypoint + command:
ENV APP_MODULE="src.codex.api.app:app"
ENTRYPOINT ["/app/docker/entrypoint.sh"]
CMD ["uvicorn", "src.codex.api.app:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]
