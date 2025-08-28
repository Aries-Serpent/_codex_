# Codex-Ready Sequential Execution Block

## Phase 1 — Preparation
1. `python -m venv .venv && source .venv/bin/activate`
2. `pip install -U pip pre-commit pytest pytest-cov`
3. `export PYTHONHASHSEED=0 NO_NETWORK=1`

## Phase 2 — Search & Mapping
1. `command -v chatgpt-codex` (fallback to `python tools/audit_builder.py`)
2. `pre-commit validate-config && pre-commit run --all-files --verbose`
3. `pytest --version | grep -i cov || pip install pytest-cov`

## Phase 3 — Best-Effort Construction
1. `python tools/audit_builder.py --prompt-file AUDIT_PROMPT.md`
2. `pre-commit run --all-files --verbose`
3. `pytest --cov=src/codex_ml --cov-report=term --cov-fail-under=70`

## Phase 4 — Controlled Pruning
1. Prune `chatgpt-codex` CLI if unavailable; rely on Python fallback.
2. Move slow hooks to pre-push or skip with `SKIP=<hook_id>`.
3. Temporarily drop coverage threshold if blocking progress.

## Phase 5 — Error Capture
Record failures in `.codex/errors.ndjson` using `codex_digest/error_capture.make_error_block`.

## Phase 6 — Finalization
Re-run `pre-commit run --all-files` and `pytest`.
Document changes in CHANGELOG and ensure no GitHub Actions are activated.
