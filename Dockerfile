# BEGIN: CODEX_DOCKERFILE
# syntax=docker/dockerfile:1
FROM ubuntu:22.04 AS base
ENV DEBIAN_FRONTEND=noninteractive PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends     python3 python3-pip python3-venv ca-certificates curl &&     rm -rf /var/lib/apt/lists/*

FROM base AS builder
WORKDIR /app
COPY services/api/requirements.txt .
RUN python3 -m pip install --upgrade pip && pip install --prefix=/install -r requirements.txt

FROM base AS runtime
RUN useradd -m -u 10001 appuser && mkdir -p /app /artifacts && chown -R appuser:appuser /app /artifacts
USER appuser
WORKDIR /app
ENV PATH=/home/appuser/.local/bin:$PATH
COPY --from=builder /install /usr/local
COPY --chown=appuser:appuser services/api /app/services/api
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s CMD curl -fsS http://localhost:8000/status || exit 1
CMD ["python", "-m", "codex.cli"]
