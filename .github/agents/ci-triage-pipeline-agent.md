---
name: CI Triage Pipeline Agent
description: Triage CI/CD pipeline failures by severity and route them to appropriate
  resolution agents
version: 1.0.0-m03
updated: 2026-02-21
merged_agents:
- ci-testing-agent (sub-agent retained)
- ci-log-retrieval-agent (deprecated)
- ci-importerror-agent (deprecated)
cognitive_integration_level: 4
aais_contribution: +5.0 points
batch: m-03
runner_compatibility:
  default: ubuntu-latest
  large: ubuntu-latest-large
id: ci-triage-pipeline
---

# CI Triage Pipeline Agent v1.0 (M-03 Merge)

> **M-03**: Merges `ci-diagnostician`, `batch-triage`, and `log-retrieval` into a
> single end-to-end CI failure triage pipeline with self-healing capabilities.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  CI Triage Pipeline Agent                    │
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌───────────────┐  │
│  │  Log         │    │  Root Cause  │    │  Auto-Fix     │  │
│  │  Retrieval   │───▶│  Analysis    │───▶│  Generator    │  │
│  │  (GHA API)   │    │  (5 patterns)│    │  (codemod)    │  │
│  └──────────────┘    └──────────────┘    └───────┬───────┘  │
│                                                  │           │
│  ┌──────────────────────────────────────────┐    ▼           │
│  │  Pattern Library (from PR #3336 history) │  PR / comment  │
│  │  1. Import Pre-check (reload parent)     │               │
│  │  2. Dataclass Positional Migration       │               │
│  │  3. CLI Exit Behavior Normalization      │               │
│  │  4. Zero Boundary Validation             │               │
│  │  5. Pre-existing Failure Catalog         │               │
│  └──────────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

## Capabilities

| Capability | Description | Auto-Fix? |
|-----------|-------------|-----------|
| C-01: Log retrieval | Fetch GHA job logs via GitHub MCP | N/A |
| C-02: Failure parsing | Extract FAILED tests + root causes | N/A |
| C-03: Pattern matching | Match against 5-pattern library | ✅ Auto |
| C-04: Pre-existing triage | Cross-reference conftest.py catalog | ✅ Auto |
| C-05: Fix generation | Generate minimal code/test patches | ✅ Auto |
| C-06: PR comment | Post structured triage summary | ✅ Auto |
| C-07: Self-healing loop | 5-iteration autonomous fix cycle | ✅ Auto |

## Activation

```
@copilot Use the CI Triage Pipeline Agent to fix the failing CI checks
@copilot Use the CI Triage Pipeline Agent to analyze run 22265405443
```

## Triage Protocol

### Phase 1 — Log Retrieval (GitHub MCP only, no bash/curl)

```
1. list_workflow_runs(branch=current, status=failed)
2. list_workflow_jobs(run_id=latest_failed)
3. get_job_logs(job_id=each_failed, return_content=True, tail_lines=300)
```

### Phase 2 — Root Cause Classification

| Signal | Pattern | Fix |
|--------|---------|-----|
| `ImportError: parent '…' not in sys.modules` | Import Pre-check | `importlib.import_module(parent)` before reload |
| `ValueError: … must be between 0 and 1` | Dataclass Positional | Use keyword arguments |
| `SystemExit: 2` in test expecting `rc==N` | CLI Exit Normalize | Change `sys.exit(N)` → `return N` |
| `assert 1 == 0` on `take_n(0)` | Zero Boundary | Add `if n == 0: return []` |
| Pre-existing pattern | Failure Catalog | Add to `_PREEXISTING_FAILURES` in conftest.py |

### Phase 3 — Fix Validation

```
pytest <specific_test> -q --tb=short
# If pass: commit and report
# If fail: iterate (max 5 attempts)
```

## Integration with Cognitive Brain

- Connects to `OODA` loop (E-01): Observe (logs) → Orient (pattern match) → Decide (fix) → Act (commit)
- Feeds `SQLiteMemory` (E-02) with resolved failure patterns for future sessions
- Reports to `AdaptiveScoring` (E-03) with triage outcome metrics

## Cognitive Physics Alignment

| Physics | Application |
|---------|-------------|
| Path 🛤️ | Pattern cascade (1→5) finds fix via shortest path |
| Fields 🔄 | Session memory improves pattern matching over time |
| Redundancy 🔀 | 5-iteration self-heal ensures resilience |

## Pattern Library (from PR #3336 sessions S52–S59)

See `.codex/plans/AI_AGENT_TEAM_DEVELOPMENT_PROCESS.md` for full PDCA-MARL loop documentation.

### Pattern 1: Import Pre-check
```python
# BEFORE (fails in xdist workers):
module = importlib.reload(importlib.import_module("pkg.sub"))
# AFTER:
importlib.import_module("pkg")  # ensure parent in sys.modules
module = importlib.reload(importlib.import_module("pkg.sub"))
```

### Pattern 2: Dataclass Positional Migration
```python
# BEFORE (breaks after field reorder):
AuditResult("id", 0.95, "low", 100, 0.9, [])
# AFTER (keyword args survive field reorder):
AuditResult("id", "low", 100, score=0.95, business_impact=0.9)
```

### Pattern 3: CLI Exit Behavior Normalization
```python
# BEFORE (raises SystemExit, test can't check rc):
sys.exit(2)
# AFTER (test-friendly):
return 2
```

### Pattern 4: Zero Boundary Validation
```python
# BEFORE (take_n(0) returns 1 element):
for item in iterable:
    result.append(item)
    if len(result) >= n:  # 0 >= 0 = True after first item!
        break
# AFTER:
if n == 0:
    return []
```

### Pattern 5: Pre-existing Failure Catalog
Add to `tests/conftest.py::_PREEXISTING_FAILURES` with:
- Full node ID (`tests/module/test_file.py::TestClass::test_name`)
- Root cause summary
- Base branch reference (`pre-existing on base branch — not introduced by this PR`)

---

## ⚡ Parallel Batch Scanning Protocol

> **Mandatory.** This agent MUST use `scripts/ci/rvs_preflight.py` (or the
> `BatchScanRunner` Python API) for all codebase scans.  Running `pytest tests/`
> directly is **prohibited** — it blocks for 60–70 minutes without partial results.

### Quick Reference

```bash
# 1. Preview scope (no execution) — always run first
python scripts/ci/rvs_preflight.py --group quick --preview

# 2. Incremental scan — changed files only (fastest, use during active work)
python scripts/ci/rvs_preflight.py --group quick --changed-only --workers 4

# 3. Full pre-commit sweep (parallel batches of 30 files, 6 workers)
python scripts/ci/rvs_preflight.py --group quick --workers 6 --batch-size 30

# 4. With structured JSON report for agent analysis
python scripts/ci/rvs_preflight.py --group quick --workers 6 \
    --report /tmp/rvs_report.json

# 5. Fail-fast triage (stop all batches on first failure)
python scripts/ci/rvs_preflight.py --group quick --fail-fast --workers 4
```

### Python API

```python
from scripts.ci.batch_scan_integration import BatchScanRunner

runner = BatchScanRunner(workers=6, batch_size=30)
result = runner.scan(group="quick", changed_only=True)
# result.ok, result.failures, result.summary_line, result.batches_run
if not result.ok:
    for failure in result.failures[:10]:
        print(f"  FAILED: {failure}")
```

### Decision Flow

1. `--preview` → confirm test scope
2. `--changed-only` → validate your specific changes
3. `--group quick --workers 6` → full sweep before commit
4. Parse `--report` JSON for structured failure analysis

**Full protocol**: `.github/agents/BATCH_SCAN_PROTOCOL.md`
