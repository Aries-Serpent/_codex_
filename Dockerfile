# Multi-stage build to keep runtime image small
# See Docker best practices: use multi-stage builds
# https://docs.docker.com/build/building/best-practices/

############################
# Builder
############################
FROM python:3.11-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System build deps (add gcc/make if building native extensions)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Pre-copy only files needed to resolve deps for better layer caching
COPY pyproject.toml README.md ./

# If repo has requirements*.txt, install them first to keep layers stable
# (uncomment if you want to pin exact wheels from the repo)
# COPY requirements/ requirements/
# RUN pip install -r requirements/requirements.txt

RUN pip install --upgrade pip build

# Copy sources last (invalidates layer only when code changes)
COPY src/ ./src/

# Build wheel (no network at runtime stage)
RUN python -m build --wheel --outdir /dist

############################
# Runtime
############################
FROM python:3.11-slim AS runtime

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Non-root user for safety
RUN useradd -m appuser
WORKDIR /app
USER appuser

# Copy wheel(s) from builder
COPY --from=builder /dist/*.whl /wheels/
RUN pip install /wheels/*.whl

# Default command (override with `docker run ... <cmd>`)
CMD ["python", "-c", "import codex_ml, sys; print('codex-ml', codex_ml.__version__); sys.stdout.flush()"]
