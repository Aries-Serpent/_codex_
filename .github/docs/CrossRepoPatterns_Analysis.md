# Cross-Repository Patterns — Hooks & Auto-Fix

A survey of six internal and public repositories surfaced the following
patterns that informed the Codex baseline.

## Baseline Hygiene

- The `pre-commit-hooks` bundle is universal. Teams consistently enable
  `trailing-whitespace`, `end-of-file-fixer`, and `check-merge-conflict` to
  prevent trivial churn.
- Ruff is replacing `flake8` + `isort` across the board. Successful repos run
  `ruff check --fix` (all rules) followed by `ruff format` to avoid style drift.
- Black remains for codebases that mandate Python 3.7 compatibility, but most
  teams lean on Ruff-only formatting when possible. We retain Black because large
  swaths of Codex still depend on its behaviour in CI.

## Commit Policy

- Conventional Commits are the most common spec, with lightweight validators
  (regex-based) proving faster to adopt than full gitlint profiles.
- Prepare-commit-msg helpers that derive suggestions from branch names reduce
  review churn by nudging developers toward compliant headers without blocking
  work.

## Test Gates

- Pre-push hooks succeed when they run in **under 30 seconds**. Repositories that
  executed the full `pytest` suite frequently bypassed the hook.
- Opt-out is standard. Environment toggles (`PREPUSH_SKIP=1`) keep contributors
  unblocked while still nudging toward healthy defaults.

## Auto-Fix Workflows

- Human-in-the-loop remains critical. Manual triggers coupled with rich diffs
  build trust.
- Validation stacks must be **deterministic** and fail closed. Git apply dry runs
  and AST parsing were the most reliable guards across the surveyed projects.
- Teams store generated patches under a dedicated folder (e.g. `.codex/patches/`)
  and log events to an append-only ledger to aid auditing.

## Documentation & Onboarding

- High-performing repos surface copy-paste snippets alongside conceptual docs.
- `.env.example` files listing relevant toggles reduce activation friction.
- Adoption checklists (install hooks → run all → verify) drive consistency.

These patterns are reflected in the Codex implementation to balance ergonomics
with safety.
