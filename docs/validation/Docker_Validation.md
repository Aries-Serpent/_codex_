# Docker Validation — Build, Run, Smoke, Scan
> Generated: Previous Cycle-10-20 18:34:03 UTC | Author: mbaetiong

This runbook verifies the Docker workflow locally (CI remains gated). Use a machine with Docker installed.

## Summary
| Step | Command | Pass criteria |
|---|---|---|
| Build | bash scripts/ci/build_image.sh codex:local Dockerfile --load | Image builds; labels show VERSION/VCS_REF/BUILD_DATE |
| Run | docker run --rm -p 8000:8000 codex:local | App serves on 8000; curl /health or / returns 200 |
| Smoke | bash scripts/ci/container_smoke.sh codex:local 8000 18000 | Script exits 0 and logs saved |
| Enforce health | SMOKE_ENFORCE_HEALTH=1 bash scripts/ci/container_smoke.sh codex:local 8000 18000 | Docker reports healthy |
| Pytest | RUN_CONTAINER_SMOKE=1 pytest -q tests/test_container_smoke.py | Test passes; skipped if Docker missing |
| SBOM | bash scripts/ci/sbom_syft.sh codex:local | artifacts/security/sbom-*.spdx.json exists |
| Scan | bash scripts/ci/scan_trivy.sh codex:local | artifacts/security/trivy-*.{txt,sarif} exist |

## Detailed steps
1) Build (with build metadata injected)
```bash
bash scripts/ci/build_image.sh codex:local Dockerfile --load
```text
2) Run and probe
```bash
docker run --rm -p 8000:8000 codex:local &
sleep 2
curl -fsS http://127.0.0.1:8000/health || curl -fsS http://127.0.0.1:8000/
```text
3) Smoke test
```bash
bash scripts/ci/container_smoke.sh codex:local 8000 18000
SMOKE_ENFORCE_HEALTH=1 bash scripts/ci/container_smoke.sh codex:local 8000 18000
```text
4) Pytest (optional)
```bash
RUN_CONTAINER_SMOKE=1 pytest -q tests/test_container_smoke.py
```text
5) Security artifacts (optional)
```bash
bash scripts/ci/sbom_syft.sh codex:local
bash scripts/ci/scan_trivy.sh codex:local
```text

## Notes
- If Docker is unavailable, tests and scripts skip gracefully.
- The HEALTHCHECK probes /health first, then falls back to /.
- To disable auto build metadata injection: AUTO_BUILD_METADATA=0 bash scripts/ci/build_image.sh ...
