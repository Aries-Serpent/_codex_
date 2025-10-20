# [How-To]: Docker Build, Run, and Push (Set A: Minimal Image + CI)
> Generated: 2025-10-20 14:30:59 | Author: mbaetiong

This guide shows how to:
- Build a minimal runtime image
- Run a local container and verify health
- Push images to GHCR via GitHub Actions

## Prerequisites
- Docker 24+ with Buildx enabled
- Python project installable via `requirements.txt` or `pyproject.toml`
- Optional: FastAPI app at `src/codex/api/app.py` exporting `app`

## Local build
```bash
docker build -t codex:local .
```

## Run locally (FastAPI on 8000)
```bash
docker run --rm -p 8000:8000 codex:local
# In another terminal:
curl -sS http://localhost:8000/health || curl -sS http://localhost:8000/
```

## Image contents and defaults
- Base: `python:3.11-slim`
- Non-root `appuser`
- CMD: `uvicorn src.codex.api.app:app --host 0.0.0.0 --port 8000`
- Exposed port: 8000
- Copies `src/` and optional `configs/`

## GitHub Actions workflow
- Builds and loads image for a smoke test on every push/PR
- On `main`, pushes to GHCR:
  - `ghcr.io/<owner>/<repo>:latest` (main)
  - `ghcr.io/<owner>/<repo>:sha-<shortsha>`
  - `ghcr.io/<owner>/<repo>:<branch>` (non-main)
- Repo policy keeps CI YAML in `.github/_workflows_disabled/`. Move
  `docker-build-push.yml` into `.github/workflows/` to enable it.

## Smoke test in CI
- Uses `scripts/ci/container_smoke.sh IMAGE SRC_PORT HOST_PORT`
- Starts the container, waits for 200 OK on `/health` (or `/` fallback), and prints logs.

## Environment variables
- Configure your app using env vars; do not bake secrets in the image.
- Use GitHub Actions `secrets.*` for registry auth (`${{ secrets.GITHUB_TOKEN }}` for GHCR).

## Troubleshooting
- If the app import path differs, edit the Dockerfile CMD.
- If the health path differs, update `container_smoke.sh`.
- If dependencies are unpinned, add `requirements.txt` / lock to improve reproducibility.

## Next steps (optional hardening)
- Add multi-stage build with wheel caching
- Add vulnerability scanning (Trivy) and SBOM generation
- Reduce image size with `--no-cache-dir` and slim runtimes
