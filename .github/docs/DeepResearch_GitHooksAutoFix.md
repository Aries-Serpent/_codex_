# Deep Research — Git Hooks + Auto-Fix Rollout

This document captures the research spikes that informed the Codex hook
standardisation effort. It summarises the landscape review, trade-offs, and
adoption blockers observed across comparable organisations.

## Objectives

- Establish a **fast, predictable** baseline for formatting, linting, and
  notebook hygiene.
- Enforce **Conventional Commits** to unlock automated changelog and release
  tooling.
- Provide a guarded path for **LLM-assisted remediation** that keeps the human
  developer in control.

## Findings

1. Teams that succeed with auto-fix features make them **opt-in** and surface
   clear escape hatches. A toggle such as `CODEX_AUTO_FIX_ENABLED=1` keeps the
   feature discoverable without surprising contributors.
2. Pairing `ruff check --fix` with `ruff format` produced the most stable diffs
   in repositories that previously mixed Black and Ruff. Running Ruff in two
   phases mirrors the upstream guidance.
3. A minimal set of standard hooks (`check-merge-conflict`, `trailing-whitespace`,
   `end-of-file-fixer`, etc.) eliminates most paper cuts without noticeable
   latency. These hooks are already compiled for performance and require no
   bespoke maintenance.
4. Pre-push gates succeed when they run a **fast subset** (e.g. `pytest -q` or
   a lean `nox -s tests`) and allow an escape hatch via an environment variable.
5. Notebook churn remains a top frustration. Shipping `nbstripout` in the hook
   stack prevents large binary blobs from entering history while keeping local
   interactivity intact.

## Guardrails

- Never touch `.github/workflows/*` via the auto-fix flow; validation rejects
  such patches before `git apply` runs.
- Cap auto-generated diffs at **10 files** or **500 total line changes** to
  avoid runaway edits.
- Require `git apply --check` and a best-effort Python AST parse before applying
  any suggestion. Both steps run against a temporary index to avoid mutating the
  developer's worktree during validation.

## Adoption Checklist

1. `pre-commit install --install-hooks --hook-type commit-msg --hook-type pre-push`
2. Export variables from `.env` or `direnv`: `CODEX_AUTO_FIX_ENABLED=1`,
   `CODEX_LLM_ENDPOINT=…`, `CODEX_LLM_API_KEY=…`.
3. Trigger the flow by staging a file with a lint error and running
   `pre-commit run --all-files`. When the first pass fails, invoke the manual
   stage with `pre-commit run llm-auto-fix --hook-stage manual`.
4. Inspect patches captured under `.codex/patches/` and verify the ledger entry
   via `python -m tools.ledger verify`.

## Rollout Phases

- **M0**: Baseline hooks (Ruff, Black, notebook stripping) + Conventional
  Commits lint.
- **M1**: LLM orchestrator behind the opt-in toggle; ledger integration.
- **M2**: Hardening (expanded metrics, documentation polish, prepare-commit
  scaffolding refinements).

This research backlog should be revisited quarterly to validate assumptions and
incorporate developer feedback.
