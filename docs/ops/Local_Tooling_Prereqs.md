# [Guide]: Local Tooling Prerequisites — Docker & Security
> Generated: 2025-10-14 02:46:01 UTC | Author: mbaetiong
🧠 Roles: [Audit Orchestrator], [Capability Cartographer] ⚡ Energy: 5

## Purpose
Document external CLI dependencies used by local hygiene gates (opt-in) and how to enable/defer them safely.

## Tools
| Tool | Used by | Install | Verify |
|------|---------|---------|--------|
| hadolint | nox docker_lint / make docker-hadolint | [https://github.com/hadolint/hadolint](https://github.com/hadolint/hadolint) | `hadolint --version` |
| trivy | nox imagescan / make docker-trivy | [https://aquasecurity.github.io/trivy](https://aquasecurity.github.io/trivy) | `trivy --version` |

Notes:
- These sessions are optional. If the binaries are not found on PATH, sessions will log a skip message and exit cleanly.
- Image scan is gated by `CODEX_AUDIT=1` to prevent accidental network-heavy runs.

## Commands
- Lint Dockerfiles:
  - `make docker-hadolint`
  - `nox -s docker_lint`
- Scan container image (opt-in):
  - `CODEX_AUDIT=1 CODEX_IMAGE=codex:local nox -s imagescan`
  - `make docker-trivy`

## Security Baselines (Opt-in)
Set `CODEX_AUDIT=1` to persist security scan outputs under `audit_artifacts/security/`:
- `bandit.json`
- `semgrep.json` (if rules present)
- `detect-secrets.json`
- `pip-audit.json`

Run:
```bash
CODEX_AUDIT=1 nox -s sec
```

*End*
