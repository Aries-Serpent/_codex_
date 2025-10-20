# Enable Docker Build & Push Workflow (SAFE checklist)
> Created: 2025-10-20 | Author: mbaetiong

This repository gates workflows to control costs and comply with policy (see `.github/README.md` and AGENTS.md).
Workflows are stored under `.github/_workflows_disabled/` and are not active.

To enable the Docker workflow safely:

1) Review the file:
   - `.github/_workflows_disabled/docker-build-push.yml`
   - Ensure each job uses `runs-on: [self-hosted, linux]` per policy (or update per org rules).
2) Configure secrets/permissions as needed:
   - GHCR pushes typically work with `${{ secrets.GITHUB_TOKEN }}`.
   - For DockerHub or other registries, provide `DOCKER_USERNAME`/`DOCKER_PASSWORD` or tokens.
3) Move the file to the active path:
   ```bash
   git mv .github/_workflows_disabled/docker-build-push.yml .github/workflows/docker-build-push.yml
   git commit -m "Enable docker-build-push workflow (owner-approved)"
   ```
4) Push and monitor one run on `main`:
   - Verify the build, smoke test, and push steps.
   - Revert by moving it back to `_workflows_disabled/` if needed.

Local alternatives (no CI):
- Build: `bash scripts/ci/build_image.sh` (tags `codex:local`)
- Smoke: `bash scripts/ci/container_smoke.sh codex:local 8000 18000`
- Push (opt-in): `bash scripts/ci/push_image.sh ghcr.io/OWNER/REPO:tag`

Notes:
- The health endpoint is `/health` on port 8000 by default.
- The container runs as non-root `appuser`.
- Entrypoint loads `/app/.env` if present (non-destructive), then execs uvicorn by default.
