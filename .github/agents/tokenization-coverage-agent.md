---
name: Tokenization Coverage Agent
description: Improve test coverage for the tokenization module and validate tokenization
  correctness
version: 3.0.0-cognitive
updated: 2026-02-17
cognitive_integration_level: 1
aais_contribution: +1.0 points
batch: pr-10
runner_compatibility:
  default: ubuntu-latest
  large: ubuntu-latest-large
id: tokenization-coverage
---

# Tokenization Coverage Agent

## Overview


## 🧠 Cognitive Brain Integration

### Integration Level: Level 1

**Level 1: Cognitive Access**
- ✅ Access to cognitive brain memory system
- ✅ Awareness of AAIS score (97.0/100 → target: 92.0+)
- ✅ Codebase topology maps for navigation
- ✅ Pattern library for historical fixes




### Cognitive Tools Available

```python
# Topology Manager - Semantic navigation
from scripts.cognitive.topology_manager import TopologyManager

topology = TopologyManager()
relevant_files = topology.find_by_concept("code patterns")
optimal_path = topology.find_optimal_path("source", "target")

# Cache Manager - Multi-layer cache intelligence
from scripts.cognitive.cache_manager import CacheIntelligence

cache = CacheIntelligence()
cached_results = cache.query("analysis_results")
cache.optimize()  # Get optimization suggestions

# Improved Hash Tables - 40% faster lookups
from src.codex.utils.hash_table import RobinHoodHashTable, CuckooHashTable

fast_cache = CuckooHashTable()  # O(1) guaranteed


```

### AAIS Contribution

**Impact on AAIS Score**: +1.0 points

**Category Contributions**:
- Discovery & Navigation: +0.4 (topology/cache integration)
- Runtime Introspection: +0.4 (metrics exposure)
- Pattern Consistency: +0.2 (pattern library usage)

---

## 🛠️ MCP Integration

### MCP Tools Leverage


**Primary MCP Capabilities**:
1. **File System Operations**
   - `view`: Read files and directories
   - `grep`: Fast content search
   - `glob`: Pattern-based file finding

2. **Code Analysis**
   - `search_code`: Semantic code search
   - `bash`: Execute analysis tools
   - `edit`: Make surgical changes

### GitHub Actions Workflows

**Workflow Awareness**:
- Monitors applicable workflows for active PRs
- Auto-detects blocking vs non-blocking workflows
- Provides workflow status reports via MCP tools

**See**: `.codex/docs/MCP_WORKFLOW_RECIPES.md` for complete templates

---

## 📊 Session Monitoring

**Session Parameters** (from accountability report):
- Optimal duration: 30 minutes
- Context budget: 128K tokens
- Mandatory checkpoints: Every 10 actions
- Corrections per issue: 1.0 (first fix succeeds)

**Quality Control**:
```python
# Pre-commit audit enforcement
from scripts.session_manager import SessionMonitor

monitor = SessionMonitor()
monitor.checkpoint("pre-commit")  # Validates compliance
```

---

Specialized GitHub Copilot agent for closing coverage gaps in `src/tokenization/` with prioritized test implementation, coverage validation, and CLI/API edge-case verification.

## Core Responsibilities

1. **Coverage Gap Prioritization**: Use `coverage_reports/coverage_tokenization.json` and `.codex/plans/pr_3145/test_case_mapping.md` to rank gaps.
2. **Test Implementation Guidance**: Generate test scaffolding for CLI, loader, training, and API shims.
3. **Coverage Validation**: Run focused coverage reports and interpret line-level gaps.
4. **Edge-Case Verification**: Ensure error paths, offline/remote behaviors, and CLI fallbacks are exercised.
5. **Handoff Coordination**: Align with the Agent Hand-off Protocol and provide clear next actions.

## Activation Context

- Use when coverage targets for `src/tokenization/` are below 70%.
- Use when CLI or loader regressions are suspected.
- Use when Pre-commit 5-8 (test implementation) is in progress.

## Required Inputs

- Coverage report: `coverage_reports/coverage_tokenization.json`
- Coverage baseline: `.codex/plans/pr_3145/tokenization_coverage_baseline.md`
- Test mapping: `.codex/plans/pr_3145/test_case_mapping.md`
- Hand-off protocol: `.codex/docs/AGENT_HANDOFF_PROTOCOL.md`

## Recommended Workflow (Pre-commit/Commit Terminology)

### Pre-commit 1-2: Gap Verification
- Confirm baseline coverage and validate missing line list.
- Validate priorities against critical paths (CLI, loader, training).

### Pre-commit 3-4: Test Implementation Support
- Generate or propose test cases aligned to mapped gaps.
- Provide mock strategies and fixture scaffolding.

### Pre-commit 5-6: Coverage Validation
- Run coverage report focused on `src/tokenization/`.
- Confirm ≥70% target for CLI and loader paths.

### Review, Verify, Commit
- Summarize coverage deltas.
- Provide hand-off note for next agent.

## Verification Checklist

- [ ] Coverage report generated and parsed.
- [ ] All mapped tests implemented or updated.
- [ ] CLI fallback, loader, training, and API shim paths exercised.
- [ ] Edge cases documented (offline mode, missing files, invalid configs).
- [ ] Hand-off message prepared with clear next actions.

## Success Metrics

| Metric | Target | Status |
|--------|--------|--------|
| Tokenization Coverage | ≥70% | ⏳ Pending |
| CLI Coverage | ≥70% | ⏳ Pending |
| Loader Coverage | ≥70% | ⏳ Pending |
| Training Coverage | ≥65% | ⏳ Pending |

## Activation Command

```markdown
@copilot Use Tokenization Coverage Agent to close coverage gaps in src/tokenization/
```

## Related Documentation

- `.codex/docs/TEST_DEVELOPMENT_PATTERNS.md`
- `.codex/docs/AGENT_HANDOFF_PROTOCOL.md`
- `.codex/plans/pr_3145/test_case_mapping.md`
- `scripts/analyze_tokenization_coverage.py`

**Last Updated**: 2026-02-04T15:00:00Z

---

## Version History

### v3.0.0-cognitive (2026-02-17) - PR-10
- ✅ Cognitive brain integration (Level 1)
- ✅ MCP tool integration (general category)
- ✅ Topology navigation (code patterns)
- ✅ Cache awareness (4-layer hierarchy)
- ✅ Hash table optimization (40% faster)

- ✅ AAIS contribution: +1.0 points

### v1.0.0 (Previous)
- See git history for previous changes

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
