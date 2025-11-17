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
- Runtime overrides:
  - `APP_MODULE` (default `src.codex.api.app:app`) selects the ASGI app.
  - `PORT` / `LOG_LEVEL` adjust uvicorn defaults when using the entrypoint auto-cmd.
  - `PRESTART_CMD` runs before the server (e.g., migrations).
  - `DISABLE_TINI=1` bypasses signal reaping (not recommended).

## Local smoke and health enforcement

Run local build and smoke without CI:
- Build: `bash scripts/ci/build_image.sh codex:local Dockerfile --load`
- Smoke (basic): `bash scripts/ci/container_smoke.sh codex:local 8000 18000`
- Smoke (enforce HEALTHCHECK): `SMOKE_ENFORCE_HEALTH=1 bash scripts/ci/container_smoke.sh codex:local 8000 18000`
- Pytest (opt-in): `RUN_CONTAINER_SMOKE=1 pytest -q tests/test_container_smoke.py`

Note: In environments without Docker you may see “Tests not run (Docker unavailable in environment).”
This is expected; use a machine with Docker installed or a self-hosted runner to validate containers.

## Owner-approval window (timeboxed switch)

You can approve cost-incurring workflows for a time window via either method:

A) Repository variables (no commit required):
- Set one of:
  - `OWNER_APPROVED_UNTIL="2025-10-21T04:00:00Z"`
  - `OWNER_APPROVED_DURATION="2h"` (supports s/m/h/d/w)
- Applicable to TOOL_KEY=docker-build-push in the workflow.

B) File-based approval (via commit):
- Edit `.github/OWNER_APPROVAL.yml`:
  - `enabled: true`
  - mode: `"duration"` with `duration: "4h"` and a valid `created_at` (ISO), OR
  - mode: `"until"` with `until: "2025-10-21T04:00:00Z"`
  - Include the workflow key in `cost_workflows:` (or `"all"`)

Guarding script:
- The workflow calls `scripts/ci/owner_approval_guard.sh` and fails fast if the window is not active.

Examples:
```yaml
# repo var example (no commit)
OWNER_APPROVED_DURATION=8h

# file example (commit change)
enabled: true
mode: "until"
until: "2025-10-21T04:00:00Z"
cost_workflows: ["all"]
created_at: "2025-10-20T16:00:00Z"
```text

Count-based approvals (next N runs):
- Optional keys can be added to `.github/OWNER_APPROVAL.yml` (e.g., `runs_max: 5`), but automatic decrement is not performed to avoid CI self-writes. Owners may manually adjust as needed.
