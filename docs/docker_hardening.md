# Docker Build System Hardening Checklist

Phase 4 audits the CPU and GPU Dockerfiles plus `docker-compose.yml` to ensure
they support offline builds, multi-stage caching, and GPU runtime hooks.

## Multi-stage build analysis

- [x] Builder stage installs Python dependencies with caching enabled.
- [x] Runtime stage copies only required artefacts and runs as a non-root user.
- [x] Optional development stage omitted from production images to keep them slim.

## Security & best practices

- [x] Base images pinned (`python:3.11-slim`, `nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04`) with commented digest examples in the Dockerfiles to encourage immutable builds.
- [x] `pip install --upgrade pip setuptools wheel` performed in builder stage.
- [x] Healthcheck present for API readiness.
- [x] `.dockerignore` relied upon to exclude build artefacts.

## Offline support

- [x] Dependency manifests copied before source to maximise caching.
- [x] Support for mounting `/app/models` and `/app/data` volumes documented.
- [x] `CODEX_OFFLINE=1` environment variable toggles offline behaviour.
- [x] Optional model staging layer documented in `docs/docker_guide.md`.

## GPU runtime integration

- [x] `Dockerfile.gpu` pins CUDA base image and mirrors CPU build steps.
- [x] `docker-compose.yml` documents `runtime: nvidia` and `--gpus all` usage.
- [x] Environment variables `NVIDIA_VISIBLE_DEVICES` + `CODEX_OFFLINE` surfaced.

## Testing

- [x] `docker build -t codex:phase4 .` succeeds (CPU variant).
- [x] `docker run --rm codex:phase4 python -c "import src.codex_ml"` validates runtime.
- [x] `docker-compose config` validates compose syntax after updates.

Refer to `docs/docker_guide.md` for detailed build and run recipes.
