# Multi-stage build to keep runtime image small
# See Docker best practices: use multi-stage builds
# https://docs.docker.com/build/building/best-practices/

############################
# Builder / base stage installs package once; runtime copies installed files only.
FROM python:3.11-slim AS base

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY src/ ./src/

RUN pip install --upgrade pip && \
    pip install --no-cache-dir .

############################
# Runtime
############################
FROM python:3.11-slim AS runtime

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN useradd -m appuser
WORKDIR /app
USER appuser

COPY --from=base /usr/local /usr/local

ENTRYPOINT ["python", "-c", "print('Codex ML container ready')"]
