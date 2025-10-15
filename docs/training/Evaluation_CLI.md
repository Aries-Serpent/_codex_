# [Guide]: Evaluation CLI — codex-eval
> Generated: 2025-10-15 · Maintainer: Codex ML Platform Team


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

## Troubleshooting
- The CLI attempts four dispatch strategies. If they all fail, the error message will
  echo the encountered issues (e.g., import failures or exceptions thrown by module `main`
  functions). Use that detail to decide whether to install optional dependencies or fix
  module-level errors.
- To prefer the programmatic registry for plugin discovery, ensure the relevant
  packages expose entry points; `codex-eval` will surface the discovery summary when
  available.

*End*
