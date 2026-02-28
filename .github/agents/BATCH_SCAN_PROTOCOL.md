# Batch Scan Protocol — Parallel Codebase Scanning for All Agents
<!-- version: 1.0.0 | updated: 2026-02-28 | canonical reference for all scanning agents -->

> **Mandatory for ALL applicable agents.**  
> Every agent that performs test execution, codebase scanning, coverage analysis,
> security auditing, or CI validation MUST follow this protocol instead of running
> `pytest tests/` as a single sequential command.

---

## Why Batched Parallel Scanning?

The full test suite (`pytest tests/`) runs sequentially for **60–70 minutes** in CI and
produces a single pass/fail at the end.  With batched parallel scanning:

| Metric | Sequential (old) | Batched Parallel (new) |
|--------|-----------------|------------------------|
| Time to first failure | up to 70 min | **< 5 min** |
| Workers | 1 | configurable (default: cpu/2) |
| Scope control | all tests | `--changed-only`, `--group` |
| Output | terminal dump | structured JSON report |
| Pre-commit | ❌ | ✅ (`--preview` + `--changed-only`) |

---

## Core Tool: `scripts/ci/rvs_preflight.py`

Mirrors **`resilient_validation.yml`** exactly — same markers, timeouts, and maxfail
values — but splits test files into batches and runs them via `ProcessPoolExecutor`.

### Groups (exact mirrors of CI matrix)

| Group | Marker | Timeout | maxfail |
|-------|--------|---------|---------|
| `quick` | `not slow and not integration` | 60 s | 20 |
| `slow` | `slow` | 600 s | 5 |
| `integration` | `integration and not slow` | 300 s | 10 |
| `docs` | n/a (markdown + validate_docs.py) | — | — |
| `all` | all four groups | — | — |

---

## Standard Agent Invocations

```bash
# ── Step 1: ALWAYS preview scope before running ──────────────────────────
python scripts/ci/rvs_preflight.py --group quick --preview

# ── Step 2: Changed-only (fastest — run on every file save / pre-commit) ──
python scripts/ci/rvs_preflight.py --group quick --changed-only --workers 4

# ── Step 3: Full quick sweep before pushing ───────────────────────────────
python scripts/ci/rvs_preflight.py --group quick --workers 6 --batch-size 30

# ── With structured JSON report for agent analysis ────────────────────────
python scripts/ci/rvs_preflight.py --group quick --workers 6 \
    --report /tmp/rvs_report.json

# ── Fail-fast triage (stop all batches on first failure) ──────────────────
python scripts/ci/rvs_preflight.py --group quick --fail-fast --workers 4

# ── Full suite (all 4 groups, sequential groups, parallel batches within) ─
python scripts/ci/rvs_preflight.py --group all --workers 8

# ── Slow / integration groups ─────────────────────────────────────────────
python scripts/ci/rvs_preflight.py --group slow        --workers 4
python scripts/ci/rvs_preflight.py --group integration --workers 6
```

---

## Python API (for agent code)

```python
from scripts.ci.batch_scan_integration import BatchScanRunner

runner = BatchScanRunner(workers=6, batch_size=30)

# ── Preview scope ────────────────────────────────────────────────────────
print(runner.preview(group="quick"))

# ── Incremental scan (changed files only) ────────────────────────────────
result = runner.scan(group="quick", changed_only=True)
print(result.summary_line)   # "✅ QUICK  P:312  F:0  S:18  4.2s  batches:11"

# ── Full scan with JSON report ────────────────────────────────────────────
from pathlib import Path
result = runner.scan(
    group="quick",
    report_path=Path("/tmp/rvs_report.json"),
)
if not result.ok:
    for failure in result.failures:
        print(f"  FAILED: {failure}")

# ── BatchScanResult fields ────────────────────────────────────────────────
# result.ok          → bool
# result.passed      → int
# result.failed      → int
# result.failures    → List[str]  — test node-ids that failed
# result.batches_run → int
# result.duration_s  → float
# result.raw         → dict       — full JSON report
```

---

## Agent Decision Tree

```
Agent triggered
     │
     ▼
1. runner.preview(group)     ← always confirm scope first
     │
     ▼
2. runner.scan(changed_only=True)  ← fastest, runs only YOUR changes
     │
     ├── result.ok? ──Yes──► commit / push safe ✅
     │
     └── No ──► inspect result.failures
                     │
                     ▼
               Fix failing tests
                     │
                     ▼
3. runner.scan(group="quick")    ← full sweep before committing
                     │
                     ├── result.ok? ──Yes──► commit ✅
                     │
                     └── No ──► escalate / create issue / self-heal loop
```

---

## Integration Points

| File | Role |
|------|------|
| `scripts/ci/rvs_preflight.py` | CLI runner (ProcessPoolExecutor, JUnit aggregation) |
| `scripts/ci/batch_scan_integration.py` | Python API for agent code |
| `scripts/ci_local.sh preflight` | Shell alias for the runner |
| `nox -s rvs_preflight` | Nox session (installs deps + runs) |
| `.github/hooks/pre-push` | Git hook template (auto-runs `--changed-only`) |

---

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | All batches passed |
| `1` | One or more test failures |
| `2` | Configuration / invocation error |

---

## Configuration

| Flag | Default | Description |
|------|---------|-------------|
| `--workers` | cpu_count/2 | Parallel batch processes |
| `--batch-size` | 30 | Test files per batch |
| `--changed-only` | false | Limit to git-changed files |
| `--fail-fast` | false | Stop all batches on first failure |
| `--preview` | false | Dry-run: show scope only |
| `--report PATH` | none | Write JSON report |

Tune `--batch-size` based on test weight:
- **Unit tests** (fast): batch-size 40–60
- **Integration tests** (slow): batch-size 10–15
- **Mixed**: default 30

---

## Prohibited Patterns

The following patterns are **banned** for applicable agents:

```bash
# ❌ NEVER — runs sequentially, blocks for 70+ minutes
pytest tests/

# ❌ NEVER — single directory, still sequential
pytest tests/codex_ml/

# ✅ ALWAYS — batched parallel
python scripts/ci/rvs_preflight.py --group quick --workers 6
```

---

*This document is the canonical reference.  When adding new scanning agents, include
the standard `⚡ Parallel Batch Scanning Protocol` section and point to this file.*
