# [Checklist]: Post-Apply Validation — Next Atomic Diffs
> Generated: 2025-10-11 | Owner: Codex Ops

## Nox Sessions
| Session | Command | Expected |
|--------|---------|----------|
| docs | `nox -s docs` | `artifacts/docs/` with pdoc output |
| sec | `nox -s sec` | bandit/semgrep/detect-secrets ran; `pip-audit` only if `CODEX_AUDIT=1` |
| docker_lint | `nox -s docker_lint` | hadolint runs or logs skip if not present |
| dockerlint | `nox -s dockerlint` | Delegates to docker_lint |
| imagescan | `CODEX_AUDIT=1 CODEX_IMAGE=codex:local nox -s imagescan` | Trivy image scan |

## Seeding API
- `from codex_ml.utils.seed import set_seed` works; delegates to centralized helpers.
- Deterministic across Python/NumPy/Torch with fixed seed.

## Compose Override
- Base compose has `codex-cpu`; healthcheck configured with official keys.
- `docker compose up` → service transitions to `healthy`.

## Artifacts
- `artifacts/docs/` (pdoc)
- Security scans produce console output; enable `CODEX_AUDIT=1` for `pip-audit` / image scans.

*End of Checklist*
