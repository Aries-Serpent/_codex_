# Implementation Notes — LLM Auto-Fix Hook

This guide explains how the Codex LLM auto-fix orchestrator is wired into the
pre-commit workflow.

## Overview

```text
pre-commit (pre-commit stage)
  └── failure? → developer runs manual stage
        └── tools/llm_auto_fix.py
              ├── capture staged diff + hook output
              ├── request patch via tools/llm_bridge.py
              ├── validate with tools/validate_patch.py
              ├── apply + restage (git apply --index)
              └── rerun checks → ledger events
```

The orchestrator is intentionally **manual**: developers opt in via
`pre-commit run llm-auto-fix --hook-stage manual` (or a wrapper script) after a
failed hook run.

## Environment Flags

| Variable | Purpose |
| --- | --- |
| `CODEX_AUTO_FIX_ENABLED` | Enable/disable the orchestrator (default `0`). |
| `CODEX_LLM_ENDPOINT` | HTTPS endpoint for the Codex LLM bridge. |
| `CODEX_LLM_API_KEY` | Bearer token injected into the HTTP request headers. |
| `CODEX_LLM_MODEL` | Optional model identifier forwarded to the endpoint. |
| `CODEX_LLM_TIMEOUT` | Request timeout in seconds (default `60`). |
| `CODEX_AUTO_FIX_CHECK_CMD` | Override for the validation command. Use `{files}` placeholder to interpolate staged paths. |
| `CODEX_LLM_MAX_FILES` | Maximum number of files that a generated patch may touch (default `10`). |
| `CODEX_LLM_MAX_LINE_CHANGES` | Total added+removed line cap (default `500`). |

Additional quality-of-life toggles live in `.env.example`.

## Validation Pipeline

1. **Size & path limits** — `tools/validate_patch.py` rejects diffs that exceed
   file or line caps, contain binary hunks, or target `.github/workflows/*`.
2. **`git apply --check`** — ensures the diff applies cleanly without touching
   the working tree.
3. **Python AST parsing** — for any `.py` file touched by the patch, a temporary
   index is created, the patch is applied, and the file is parsed with `ast.parse`.
4. **Ledger logging** — both generation and application outcomes are recorded in
   `.codex/ledger.jsonl` with hash chaining.

If any validation step fails, the orchestrator aborts before mutating the
developer's checkout.

## Ledger Events

| Event | Status | Meaning |
| --- | --- | --- |
| `llm_patch_generated` | `ok` | Patch accepted by validation. |
| `llm_patch_generated` | `skipped` | No endpoint configured or request failure. |
| `llm_patch_apply` | `rejected` | Patch failed validation. |
| `llm_patch_apply` | `failed` | Application or post-check run failed; patch rolled back. |
| `llm_patch_apply` | `applied` | Patch applied and checks passed. |

Use `python -m tools.ledger verify` to inspect integrity.

## Usage Flow

1. Ensure environment variables are set (`CODEX_AUTO_FIX_ENABLED=1` and LLM
   credentials).
2. Stage your changes and run `pre-commit run --files …`. If a hook fails, run
   `pre-commit run llm-auto-fix --hook-stage manual`.
3. Review the resulting patch under `.codex/patches/` and rerun `git status` to
   confirm the intended changes.
4. If the auto-fix is unsuitable, revert with `git apply --reverse` on the saved
   patch or simply `git checkout -- <file>` to discard.

## Failure Modes

- **Endpoint offline** — the bridge logs a `skipped` event and leaves your tree
  untouched.
- **Validation failure** — errors are printed and the patch file is preserved
  for inspection.
- **Post-check failure** — the orchestrator automatically rolls back the patch
  and records context in the ledger.

## Extending the Flow

- Add more validators (e.g. AST for other languages) by extending
  `tools/validate_patch.py`.
- Wrap the manual stage in a convenience script to re-run pre-commit followed by
  the auto-fix (e.g. `tools/run_precommit_with_llm.sh`).
- Feed additional telemetry into the ledger via the `data` payload.

For support or iteration proposals, open a discussion in the Engineering
Enablement channel.
