# Codex Environment Kit (updated)

This folder contains versioned scripts and config used by ChatGPT Codex.

## Files
- `scripts/setup.sh` — Manual setup script; deterministic, cache-friendly, graceful on errors.
- `scripts/maintenance.sh` — Runs after container resume; lock-aware dependency sync, budgets, token check.
- `codex.env.json` — Declarative mirror of Codex UI settings and limits.
- `.gitignore` — Keeps transient cache/logs out of git.

## New in this update
- **Secrets normalization:** resolves GH token from any of `GH_PAT`, `GITHUB_TOKEN`, `GH_TOKEN`, `_CODEX_ACTION_RUNNER`, `_CODEX_BOT_RUNNER`, `CODEX_ENVIRONMENT_RUNNER`; sets both `GITHUB_TOKEN` and `GH_TOKEN` for tools.
- **Safe status file:** `.codex/cache/secrets.status.json` records presence/equality (no token values).
- **Live verification:** maintenance calls GitHub `/user` to print login + scopes.
- **pip/uv fallback:** ensures `pre-commit` can be installed even if `pip` isn’t seeded in the venv.
- **HF pre-warm fix:** avoids `importlib.util` shadowing.
- **Unified lock hashing:** setup and maintenance use the same set of inputs.

## How to enable in Codex
- **Container Caching:** On
- **Setup script:** Manual → `.codex/scripts/setup.sh`
- **Maintenance script:** `.codex/scripts/maintenance.sh`
- **Agent Internet:** On
- **Allowlist (suggested):**
  - api.github.com, github.com, objects.githubusercontent.com
  - registry.npmjs.org
  - pypi.org, files.pythonhosted.org
  - api.openai.com

## Environment variables & secrets (examples)
- Env: `OPENAI_RPM`, `OPENAI_TPM`, `CODEX_ENVIRONMENT_RUNNER`, `CODEX_RUNNER_SHA256`
- Secrets: `CODEX_RUNNER_TOKEN`, `_CODEX_BOT_RUNNER`, `_CODEX_ACTION_RUNNER`
- Optional alias: `GH_PAT` (if set, it will be normalized to `GITHUB_TOKEN`/`GH_TOKEN`).

## Strict/Graceful switches
- `CODEX_GRACEFUL=1` (default): warn and continue on non-critical errors.
- `CODEX_STRICT_HASH=1`: fail if runner hash mismatches.
- `CODEX_STRICT_SETUP=1`: fail-fast on any setup/maintenance error.
- `CODEX_SMOKE=1`: enable quick smoke checks in maintenance.

## Notes
- Python deps prefer `uv.lock`/`pyproject.toml`; falls back to `requirements*.txt`.
- Node deps install only when lockfiles change.
- A lock-sum is written to `.codex/cache` to keep cache snapshots sane.
- Warnings are recorded under `.codex/logs/` for visibility.
