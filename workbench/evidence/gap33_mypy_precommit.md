# Gap 33 — mypy pre-commit hook

**Status:** ✅ Implemented  
**Date:** 2026-05-22  
**Branch:** `copilot/explore-codebase-and-create-plan`

---

## Summary

Added a `mypy-src` hook to `.pre-commit-config.yaml` that runs `mypy` against
`src/` at every commit.  The hook is **informational / non-blocking** (always
exits 0) so it never refuses a commit because of pre-existing type debt.  The
strict anti-regression enforcement is already handled by the separate
`mypy-isolated-venv-gate` hook at the `pre-push` stage, which enforces the
`.mypy_baseline` ratchet file.

---

## Hook configuration added

```yaml
# ── Gap 33: mypy type-check (src/ only, informational) ────────────────
- id: mypy-src
  name: "🔬 mypy type check (src/ only – informational)"
  entry: >
    bash -c '
      if ! python -m mypy --version >/dev/null 2>&1; then
        echo "⚠️  mypy not installed — skipping (pip install mypy)";
        exit 0;
      fi;
      python -m mypy src/
        --config-file=mypy.ini
        --no-error-summary
        --no-pretty
      ; EXIT=$?;
      if [ "$EXIT" -ne 0 ]; then
        echo "ℹ️  mypy found type errors in src/ (non-blocking).";
        echo "ℹ️  Run: python scripts/ci/mypy_baseline.py --update  to refresh baseline.";
      fi;
      exit 0'
  language: system
  stages: [pre-commit]
  pass_filenames: false
  # To run manually:   pre-commit run mypy-src --all-files
  # Strict pre-push gate: mypy-isolated-venv-gate (blocks on regression)
```

---

## Design decisions

| Decision | Rationale |
|----------|-----------|
| `repo: local` / `language: system` | Reuses the project's already-installed `mypy`; avoids a second isolated venv at commit time (the pre-push gate already creates one). |
| `--config-file=mypy.ini` | Honours the project's existing mypy configuration (`python_version = 3.12`, `ignore_missing_imports = True`, etc.). |
| `pass_filenames: false` with hard-coded `src/` | mypy must type-check full packages, not individual files, to resolve cross-module references correctly. |
| `--no-error-summary` | Suppresses the "Found N errors" footer so output is cleaner for incremental dev use. |
| `--no-pretty` | Removes ANSI colours; cleaner in terminal log output. |
| Exit 0 always (non-blocking) | Baseline is 131 errors (as of 2026-03-14). Blocking commits would break every developer until the full debt is paid. The `mypy-isolated-venv-gate` pre-push hook already enforces `--require-baseline` and blocks pushes that **increase** the error count. |
| `stages: [pre-commit]` | Runs at `git commit` time, giving immediate feedback without the ~15 s venv setup cost of the pre-push gate. |

---

## Existing mypy infrastructure

| Artifact | Purpose |
|----------|---------|
| `.mypy_baseline` | Ratchet file — current value: `131` (updated from initial 1152 after fixes) |
| `.github/workflows/mypy-baseline.yml` | CI workflow — fails if mypy count exceeds `.mypy_baseline` |
| `scripts/ci/mypy_baseline.py` | Script that reads baseline, runs mypy, exits 1 on regression |
| `mypy.ini` | Project mypy configuration (`python_version = 3.12`, `ignore_missing_imports = True`) |
| `.pre-commit-config.yaml` `mypy-isolated-venv-gate` | Pre-push blocking gate using isolated venv + `--require-baseline` |

---

## Validation results

```
$ python -c "import yaml; yaml.safe_load(open('.pre-commit-config.yaml')); print('YAML valid')"
✅ YAML valid
```

---

## How to use

```bash
# Run the hook manually across all Python files in src/
pre-commit run mypy-src --all-files

# Run the strict pre-push gate manually
pre-commit run mypy-isolated-venv-gate

# Update the baseline after fixing type errors
python scripts/ci/mypy_baseline.py --update
```
