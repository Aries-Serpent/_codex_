# [Plan]: Resolve Outstanding Unresolveds — Next Atomic Diffs
> Generated: 2025-10-11 | Owner: Codex Ops

## Executive Summary
- Remove duplicated seeding logic; unify on centralized helpers.
- Align docs build path with validation (artifacts/docs).
- Restore security nox session (bandit/semgrep/detect-secrets; pip-audit gated).
- Fix Docker lint/scan sessions (no pip install of hadolint; add image scan).
- Correct docker-compose override to target existing `codex-cpu` service.

## Post-merge Quick Validation
- `nox -l` shows: `docs`, `sec`, `docker_lint`, `dockerlint`, `imagescan`.
- `nox -s docs` creates `artifacts/docs/index.html`.
- `nox -s sec` runs local checks; `CODEX_AUDIT=1` gates `pip-audit`.
- `nox -s docker_lint` uses hadolint if installed (skips otherwise).
- `CODEX_AUDIT=1 CODEX_IMAGE=codex:local nox -s imagescan` scans image.
