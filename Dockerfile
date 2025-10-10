# Stage 1: dependency builder
FROM python:3.10-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends build-essential git && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --upgrade pip && \
    pip install --user -e .

# Stage 2: GPU runtime image
FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04 AS gpu-runtime
ENV PATH=/root/.local/bin:$PATH \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
COPY --from=builder /root/.local /root/.local
COPY --from=builder /build/src /app/src
COPY --from=builder /build/pyproject.toml /app/
COPY --from=builder /build/README.md /app/

RUN useradd -ms /bin/bash appuser
USER appuser
ENTRYPOINT ["python", "-m", "codex_ml.cli.main"]

# Stage 3: CPU runtime image
FROM python:3.10-slim AS cpu-runtime
ENV PATH=/root/.local/bin:$PATH \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
COPY --from=builder /root/.local /root/.local
COPY --from=builder /build/src /app/src
COPY --from=builder /build/pyproject.toml /app/
COPY --from=builder /build/README.md /app/

RUN useradd -ms /bin/bash appuser
USER appuser

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["python", "-m", "codex_ml.cli.main"]
