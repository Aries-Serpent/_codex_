FROM python:3.10.14-slim

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN useradd -ms /bin/bash appuser
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    git build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --upgrade pip && \
    pip install -e .

USER appuser

ENTRYPOINT ["codex-train"]
CMD []

# Notes:
#  - For GPU builds, prefer Dockerfile.gpu pinned to a CUDA tag.
#  - Keep this base CPU image small and reproducible.
