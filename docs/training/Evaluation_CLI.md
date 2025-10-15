# [Guide]: Evaluation CLI — codex-eval


## Overview
`codex-eval` is a thin wrapper that dispatches to in-repo evaluation modules:
- Preferred: `codex_ml.training.eval:main()`
- Fallbacks: run modules `codex_ml.training.eval` or `codex_ml.eval.evaluator`

This keeps CLI stable while allowing module-internal evolution.

## Usage
```bash
codex-eval --help
codex-eval --dry-run   # smoke test without running evaluation
```

Downstream modules handle their own arguments (datasets, models, metrics).

## Notes
- Offline-first: no network calls are introduced by this wrapper.
- Determinism: relies on evaluation code seeding and dataset determinism.
- Exit codes are propagated from the underlying module(s).

*End*
