# Docker Guide — Offline & GPU Ready

This guide captures the Phase 4 hardening work for the Docker build system.

## Build images

### CPU (default)
```bash
docker build -t codex:cpu -f Dockerfile .
```text

### GPU (requires NVIDIA Container Toolkit)
```bash
docker build -t codex:gpu -f Dockerfile.gpu .
```text

Use `--build-arg VERSION=$(git rev-parse --short HEAD)` to embed metadata.

## Run containers

### CPU runtime
```bash
docker run --rm \
  -e CODEX_OFFLINE=1 \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/data:/app/data \
  codex:cpu python -m codex_ml.cli.train --help
```text

### GPU runtime
```bash
docker run --rm \
  --gpus all \
  -e CODEX_OFFLINE=1 \
  -e NVIDIA_VISIBLE_DEVICES=all \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/data:/app/data \
  codex:gpu python -c "import torch; print(torch.cuda.is_available())"
```text

## docker-compose

The compose file now includes CPU + GPU services. Enable the GPU profile when
NVIDIA hardware is available:

```bash
docker compose --profile gpu up --build
```text

## Offline artefact staging

* Mount `/app/models` for cached checkpoints.
* Mount `/app/data` for local datasets.
* Set `CODEX_OFFLINE=1` to ensure runtime code avoids HTTP downloads.

Refer to the [Docker Hardening Checklist](docker_hardening.md) for the
audit log and validation commands.
