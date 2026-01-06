# Docker: Build, Run, Smoke, Scan

This repo ships a local-first Docker workflow that remains CI-gated by policy. Use these commands to build, run, smoke-test, and (optionally) generate security artifacts locally.

## Prereqs
- Docker engine with Buildx (recommended)
- Optional: `syft` for SBOM, `trivy` for vulnerability scanning

## Build
```bash
bash scripts/ci/build_image.sh codex:local Dockerfile --load
```text

You can pass build metadata (displayed in image labels):
```bash
docker build \
  --build-arg VERSION="$(git describe --tags --always --dirty=+)" \
  --build-arg VCS_REF="$(git rev-parse --short=12 HEAD)" \
  --build-arg BUILD_DATE="$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  -t codex:local -f Dockerfile .
```text

## Run
```bash
docker run --rm -p 8000:8000 codex:local
```text

Health path override and timeouts (smoke script environment):
- `HEALTH_PATH` (default `/health`, falls back to `/`)
- `FALLBACK_PATH` (default `/`)
- `TIMEOUT_STARTUP_SEC` (default `60`)
- `TIMEOUT_HEALTH_SEC` (default `3`)
- `SMOKE_ENFORCE_HEALTH=1` also checks Docker `HEALTHCHECK`

Environment variables recognized by the entrypoint:
- `APP_MODULE` (default: `src.codex.api.app:app`)
- `PORT` (default: `8000`)
- `LOG_LEVEL` (default: `info`)
- `PRESTART_CMD` (optional; e.g., migrations)
- `DISABLE_TINI=1` (not recommended; disables signal reaping)

Examples:
```bash
docker run --rm -e APP_MODULE="src.codex.api.app:app" -e LOG_LEVEL=debug -p 8000:8000 codex:local
docker run --rm --env-file .env -p 8000:8000 codex:local
```text

## Smoke test
Script waits for HTTP 200 on `/health` (or falls back to `/`) and can enforce Docker HEALTHCHECK status:
```bash
bash scripts/ci/container_smoke.sh codex:local 8000 18000
SMOKE_ENFORCE_HEALTH=1 bash scripts/ci/container_smoke.sh codex:local 8000 18000
# Override the health path and extend startup timeout
HEALTH_PATH=/ TIMEOUT_STARTUP_SEC=120 bash scripts/ci/container_smoke.sh codex:local 8000 18000
```text

Pytest (opt-in; requires Docker):
```bash
RUN_CONTAINER_SMOKE=1 pytest -q tests/test_container_smoke.py
```text

## SBOM and vulnerability scan (local)
Generate an SPDX JSON SBOM with syft:
```bash
bash scripts/ci/sbom_syft.sh codex:local
```text

Scan with trivy and export SARIF:
```bash
bash scripts/ci/scan_trivy.sh codex:local
```text
Outputs are saved under `artifacts/security/`.

## Push (GHCR, opt-in)
```bash
bash scripts/ci/push_image.sh ghcr.io/OWNER/REPO:tag --dry-run
# After 'docker login ghcr.io' or set GITHUB_TOKEN/GITHUB_ACTOR in CI:
bash scripts/ci/push_image.sh ghcr.io/OWNER/REPO:tag
```text
- GHCR requires lowercase repository/image references. The helper script normalizes `ghcr.io/...` refs before pushing and logs the rewrite.
Owner approval gate:
- Push is gated by scripts/ci/owner_approval_guard.sh with TOOL_KEY=docker-build-push.
- Approval options:
  - File mode: .github/OWNER_APPROVAL.yml with enabled: true, mode: duration, duration: "24h" and a fresh created_at.
  - Env mode: export OWNER_APPROVED_DURATION=24h (or OWNER_APPROVED_UNTIL=...Z).
- To bypass locally: SKIP_OWNER_APPROVAL=1 bash scripts/ci/push_image.sh ghcr.io/OWNER/REPO:tag
- Every decision is written to .codex/evidence/owner_approval.jsonl (JSONL).
Convenience targets:
- make owner-approve-24h | make owner-approve-status | make owner-approve-extend-24h | make owner-approve-clear

## GPU image (optional)
The GPU image (`Dockerfile.gpu`) is based on `nvidia/cuda:12.2.2-cudnn8-runtime-ubuntu22.04` and includes CUDA-enabled PyTorch.

**Important**: The GPU image explicitly installs PyTorch with CUDA 12.1 support (compatible with CUDA 12.2 runtime) before processing requirements files. This ensures GPU training capabilities are available.

- Build locally:
```bash
make docker-gpu-build
# Or manually:
docker build -t codex:gpu -f Dockerfile.gpu .
```text

- Verify GPU support:
```bash
docker run --rm --gpus all codex:gpu python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```text

- Run (requires NVIDIA Container Toolkit):
```bash
make docker-gpu-run HOST_PORT=8000
# Or manually:
docker run --rm --gpus all -p 8000:8000 codex:gpu
```text

**Prerequisites for GPU containers**:
- NVIDIA GPU with CUDA support
- NVIDIA Container Toolkit installed on the host
- Docker configured to use the NVIDIA runtime

**Known limitations**:
- PyTorch version is pinned to ensure CUDA compatibility
- Base requirements Phase 5 list CPU-only torch; the Dockerfile explicitly overrides this
- Image size is significantly larger due to CUDA libraries

## Multi-arch builds
- For local buildx (no `--load`), specify platforms:
```bash
PLATFORMS=linux/amd64,linux/arm64 BUILDX_FLAGS="--output=type=registry" \
  bash scripts/ci/build_image.sh ghcr.io/OWNER/REPO:tag Dockerfile
```text
- The GitHub Actions workflow (`.github/workflows/docker-build-push.yml`) respects `PUSH_PLATFORMS` to enable
  multi-architecture pushes when an OWNER opts in.

## CI build cache (self-hosted)
- The Docker workflow restores a persistent local Buildx cache at `/tmp/.buildx-cache` using `actions/cache@v4` when running on self-hosted runners.
- Cache keys include the Dockerfile and requirements lockfiles to ensure rebuilds occur when inputs change, while restore-keys allow reuse across related revisions.

## Compose
For a quick local run after `cp .env.docker.example .env` (or merge with your .env):
```bash
docker compose up
```text
For a self-contained local image build + run, use the optional override:
```bash
docker compose -f docker-compose.yml -f docker-compose.override.local.yml up --build
```text

## Healthcheck
The image includes a HEALTHCHECK which probes `/health`, then `/` if missing. Prefer implementing a `/health` route in your API for explicit readiness.

## CI enablement (gated)
See `.github/ENABLE_WORKFLOW.md` for the safe checklist. The Docker workflow lives under `.github/_workflows_disabled/` and must be moved by an OWNER to enable.
