FROM python:3.10.14-slim AS base

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN useradd -ms /bin/bash appuser
WORKDIR /app

FROM base AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --upgrade pip && \
    pip wheel --wheel-dir /tmp/wheels .

FROM base AS runtime

COPY --from=builder /tmp/wheels /tmp/wheels

RUN pip install --upgrade pip && \
    pip install --no-index --find-links /tmp/wheels codex-ml

USER appuser

ENTRYPOINT ["codex-train"]
CMD []

# Notes:
#  - For GPU builds, prefer Dockerfile.gpu pinned to a CUDA tag.
#  - Keep this base CPU image small and reproducible.
