# `_codex_` Security & Safety Baseline (Scaffolding)

This document captures the *initial*, local-only security and safety
baseline for `_codex_`. It is not a full threat model, but it ties
together the tooling included in this repo.

## 1. Scope & Assumptions

- All workflows are assumed to run:
  - On local developer machines, or
  - In self-managed, offline containers.
- No cost-incurring external services are invoked by default.
- This baseline does **not** replace organization-wide security policies.

## 2. Key Tools

- `tools/codex_env_snapshot.py`
  - Captures Python + platform info and installed packages.
- `tools/codex_dependency_audit.py`
  - Records a static list of installed packages and versions.
- `tools/codex_secret_scan_stub.py`
  - Performs a trivial pattern-based scan for obvious secrets.
- `src/codex_ml/cli/env_check.py`
  - Runs the three tools above and is called from:
    - `codex_task_sequence.yaml` (Preparation phase).
    - `codex_ml.cli.codex_env` (health subcommand).

These tools are best-effort and meant to be extended.

## 3. Usage

From repo root:

```bash
python -m codex_ml.cli.env_check --repo-root .
```

Or via the unified env CLI (if present):

```bash
python -m codex_ml.cli.codex_env health
```

Artifacts produced:

* `codex_env_snapshot.json`
* `codex_dependency_report.json`
* `codex_secret_scan_report.json`

## 4. Next Steps (Future Work)

Future hardening Phase 5 include:

* Stronger secret scanning (regex-based, entropy-based).
* Dependency vulnerability checks (e.g. using offline advisories).
* Policy enforcement on minimum test coverage and linting.
* Signed reproducibility manifests.
