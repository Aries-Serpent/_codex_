# Agent Ecosystem → Cognitive Brain Integration Planset
> Source: Comment #3938173408 (PR #3340) — Custom Agent Ecosystem Master Synthesis
> Compiled: 2026-02-21 | Session: 56 | Author: mbaetiong + Copilot
> Status: 🟢 Active | Energy: ⚡⚡⚡⚡⚡

---

## 🎯 Synthesis Ingestion Summary

The Master Synthesis (35,897 chars) documents **53+ custom agents** across three layers:

| Layer | Location | Count | Runtime |
|-------|----------|-------|---------|
| GitHub Ecosystem Agents | `.github/agents/` | 35+ | GitHub App / workflow |
| Python Runtime Agents | `agents/` package | 20+ | Process-level (v2.0.0) |
| Cognitive Brain Framework | `src/cognitive_brain/` | Core ABCs | Embedded in runtime agents |

**Key Gaps Identified:**
1. Only 7/53 agents standardized to `Planner` ABC (13%) — target: 53 (100%)
2. GitHub API integration in `codex-quantum-reviewer` is stub — blocks full cognitive loop
3. In-memory-only `SimpleDictMemory` — no cross-session persistence
4. `k₁ = 0.36` (3% above target 0.35) — Phase 8.0 weight refinement needed
5. 5 groups of overlapping agents consuming redundant compute — merge candidates identified

---

## 🔄 Session 57 PLANSET — OODA Formalization + Memory Persistence

### Priority 1 (S57-P1): E-01 — Formalize OODA in SelfHealingEngine + WorkflowNavigator

**Files:** `agents/self_healing.py`, `agents/workflow_navigator.py`
**Physics:** Path 🛤️ (clear forward momentum via tokenized execution)

```
Pre-condition: `pytest agents/ -q --timeout=60` passes on current HEAD
```

**Implementation Steps:**
1. Add `Planner` ABC inheritance to `SelfHealingEngine`:
   - `observe(input_data)` → wraps existing `detect_issues()` output
   - `orient(observation)` → wraps existing issue classification
   - `decide(orientation)` → wraps `_plan_remediation()`
   - `act(decision)` → wraps existing `remediate()` method
   - Keep all existing public API — additive only
2. Add `Planner` ABC inheritance to `WorkflowNavigator`:
   - `observe()` → captures trigger event + context
   - `orient()` → maps to workflow token selection
   - `decide()` → chooses next workflow step
   - `act()` → executes tokenized workflow step
   - Keep `execute_workflow()` as the high-level entry point (calls OODA internally)
3. Update `agents/__init__.py` exports
4. Add 4 tests each for new OODA methods in `tests/agents/`

**D1–D4 Validation Gate:**
- [ ] D1: ruff check passes
- [ ] D2: all existing `SelfHealingEngine` + `WorkflowNavigator` tests pass unchanged
- [ ] D3: 4 new OODA method tests pass
- [ ] D4: `from agents import SelfHealingEngine, WorkflowNavigator; assert issubclass(SelfHealingEngine, Planner)` succeeds

---

### Priority 2 (S57-P2): E-02 — SQLiteMemory Production MemoryInterface

**Files:** `agents/sqlite_memory.py` (new), `agents/__init__.py`
**Physics:** Redundancy 🔀 (fallback path + parallel persistence)

**Implementation Steps:**
1. Create `agents/sqlite_memory.py`:
   ```python
   class SQLiteMemory(MemoryInterface):
       """SQLite-backed persistent memory for cross-session agent state."""
       def __init__(self, db_path: str | Path = ".codex/agent_memory.db"): ...
       def store(self, key: str, value: Any, **kw) -> bool: ...
       def retrieve(self, key: str) -> Any: ...
       def search(self, query: str, limit: int = 10) -> list[dict]: ...
       def summarize_history(self, last_n: int = 5) -> str: ...
   ```
2. Use `contextlib.closing` + `sqlite3` (stdlib) — zero new dependencies
3. Schema: `(key TEXT PRIMARY KEY, value_json TEXT, created_at TEXT, updated_at TEXT)`
4. Export from `agents/__init__.py`
5. Wire into `LegacyAgentAdapter` as optional default: `memory=None` → falls back to `SimpleDictMemory`
6. Add `tests/agents/test_sqlite_memory.py` — 6 tests (CRUD + search + history)

**D1–D4 Validation Gate:**
- [ ] D1: ruff + mypy passes
- [ ] D2: `SimpleDictMemory` still works (no regression)
- [ ] D3: 6 SQLiteMemory tests pass; DB file created + cleaned in tmpdir
- [ ] D4: `LegacyAgentAdapter(memory=SQLiteMemory(":memory:"))` round-trips store/retrieve

---

### Priority 3 (S57-P3): E-06 — Wire ReflectionLoop → AdaptiveScoringOptimizer

**Files:** `agents/physics_orchestrator.py`, `src/cognitive_brain/quantum/adaptive_scoring.py`
**Physics:** Patterns 👁️ (observation → recurring structure recognition)

**Implementation Steps:**
1. Add `update(lesson: dict) → None` method to `AdaptiveScoringOptimizer`
   - Accepts lesson dict with keys: `scenario`, `outcome`, `complexity`, `weights_used`
   - Appends to internal lesson buffer (max 50 entries, FIFO)
   - Triggers weight micro-adjustment when buffer >= 10 entries
2. In `ReflectionLoop.reflect()`, call `scoring_optimizer.update(lesson)` if optimizer is injected
3. Wire via `PhysicsInspiredOrchestrator.__init__()` injection (optional kwarg `scoring_optimizer=None`)
4. Add 3 tests in `tests/cognitive_brain/quantum/test_adaptive_scoring_reflection.py`

---

## 🔀 Session 58 PLANSET — Agent Merges + GitHub API + k₁ Refinement

### Priority 1 (S58-P1): E-03 — k₁ Weight Refinement (Phase 8.0)

**Files:** `src/cognitive_brain/quantum/adaptive_scoring.py`
**Physics:** Balance ⚖️

**Changes:**
- `compliance_weight`: `0.40 → 0.38`
- `risk_weight`: `0.30 → 0.32`
- Expand EXP-1B scenario dataset: 50 → 100 scenarios
- Update expected K1 constants in `tests/cognitive_brain/quantum/test_adaptive_scoring_optimized.py`

**Constraint:** Run full 100-scenario validation before merging. Target: ≥95% accuracy.

---

### Priority 2 (S58-P2): M-01 — Unified Security Scanner Agent

**Files:** `.github/agents/unified-security-scanner.md` (new)
**Physics:** Balance ⚖️ (equilibrium between risk, cost, compliance, impact)

**Merge candidates:** `vulnerability-scanner-agent` + `alert-verification-agent` + `secret-detection-agent` + `gitleaks-agent` + `semgrep-agent`

**OODA Architecture:**
```
observe():  Run ALL 5 scanners in parallel (subprocess + API)
orient():   De-duplicate alerts; CVSS severity triage; false-positive filter
decide():   AND-gate: any CRITICAL → block PR; HIGH → require acknowledgment
act():      Post consolidated report (single PR comment, not 5 separate ones)
```

**Implementation Steps:**
1. Create `.github/agents/unified-security-scanner.md` agent spec
2. Add `AGENT_REGISTRY.yaml` entry (replaces 5 existing entries)
3. Update `AGENT_REGISTRY.md` — mark 5 source agents as `DEPRECATED → unified-security-scanner`
4. Create `.github/workflows/unified-security-scan.yml` — triggers on PR, calls all 5 tools
5. E-09 included: add entropy-based + variant patterns for secret detection (API keys, GitHub tokens)

---

### Priority 3 (S58-P3): M-02 — Unified Doc Agent

**Files:** `.github/agents/unified-doc-agent.md` (new)
**Physics:** Patterns 👁️

**Merge candidates:** `doc-quality-agent` + `doc-freshness-checker` + `link-validator-agent` + `documentation-consolidator`

**OODA Architecture:**
```
observe():  Single pass over changed docs (git diff --name-only | grep .md)
orient():   Parallel: quality check + freshness check + link validation + consolidation check
decide():   Score → FAIL if quality < 0.6 OR broken links > 5 OR freshness < 30 days
act():      Single unified PR comment with all findings; suggest consolidation candidates
```

---

### Priority 4 (S58-P4): M-03 — CI Triage Pipeline Agent

**Files:** `.github/agents/ci-triage-pipeline-agent.md` (new)
**Physics:** Path 🛤️

**Merge candidates:** `ci-diagnostician` + `batch-triage-agent` + `log-retrieval-agent`

**WorkflowNavigator Token:**
```python
WORKFLOW_TOKEN = "LOG_RETRIEVE → DIAGNOSE → BATCH_TRIAGE → FIX"
```
This replaces 3 sequential agent invocations with 1 tokenized pipeline execution.

---

### Priority 5 (S58-P5): E-04 — Quantum Reviewer GitHub API

**Files:** `.github/agents/github-guru-agent/github_client.py`
**Physics:** Fields 🔄

**Current gap:** `_github_api_post_review()` posts a stub comment `"Would post review..."`.

**Implementation:**
1. Complete `_github_api_post_review()` using existing `github_client.py` REST client
2. Add rate-limit handling: exponential backoff (max 3 retries, 2^n × 1s)
3. Add `review_body` truncation at 65,536 chars (GitHub limit)
4. Tests: mock REST client + assert review posted with correct `event` type
5. **SAFE_MODE guard:** If `SAFE_MODE=True`, log intent but do not POST (offline safety maintained)

---

## 🤖 Autonomous Iteration Methodology Improvements

> Addresses @mbaetiong's request: "These iteration sessions MUST BE automated"

### A1 — Enhanced Error Detection + Capturing

**Problem:** The auto-fix script detects F401/F841 locally with ruff but CI detects different issues
(version skew between local ruff and CI ruff).

**Solution:**
1. Pin ruff version in `requirements/dev.txt` AND in all CI workflows to same version
2. Add `.pre-commit-config.yaml` hook: `ruff check --select F401,F841,E741` — runs on every commit
3. Add pre-commit CodeQL-equivalent check using `semgrep` (already installed in CI)

**S56 Commit:** `9528c3c` already fixes the specific F401. Ruff pinning is S57-P4.

### A2 — MCP + Playwright CI Monitoring Loop

**Problem:** CI monitoring requires manual observation; session cannot wait for CI completion.

**Proposed Pattern:**
```python
# .codex/ci_monitor.py — NEW
class CIMonitor:
    """Uses GitHub MCP tools to monitor CI run completion with retry."""

    def wait_for_run(self, run_id: int, timeout: int = 600) -> str:
        """Poll run every 30s until completed or timeout."""
        # Uses github-mcp-server-actions_get → get_workflow_run
        # Returns: "success" | "failure" | "timeout"

    def summarize_failures(self, run_id: int) -> list[str]:
        """Extract FAILED test IDs from job logs."""
        # Uses github-mcp-server-get_job_logs with failed_only=True
```

This becomes the core loop for `AGENTIC_SESSION_METHODOLOGY.md` §MSP-2:
```
WHILE CI not green:
    run_result = ci_monitor.wait_for_run(latest_run_id)
    failures = ci_monitor.summarize_failures(latest_run_id)
    FOR each failure: apply_D1_D4_guardian_gate(); fix(); report_progress()
    re-trigger CI (implicit on push)
```

### A3 — GitHub Guru Agent Session Reviews

**Problem:** 55 sessions of context locked in PR comments — hard to retrieve patterns.

**Proposed:** Activate `github-guru-agent` capability `C-08` (Session Metrics) to:
1. On each session start: query last 5 session comments via GitHub MCP
2. Extract: recurring failure patterns, fixed/unfixed items, k₁ drift
3. Inject into current session PLANSET as "Lessons from previous sessions"
4. Store pattern fingerprints in `SQLiteMemory` (when E-02 is complete)

**Implementation file:** `.github/agents/github-guru-agent/session_reviewer.py` (S58)

### A4 — Automated PLANSET Generation

**Problem:** PLANSETs are manually written each session.

**Proposed:**
1. Extract recurring error patterns from `TECH_DEBT_REGISTRY.md` P1 items
2. Auto-generate next session PLANSET using `cognitive_brain.PhysicsOfThought.reason()`
3. Output to `.codex/plans/AUTO_PLANSET_S{N}.md` with D1–D4 gate pre-filled
4. Human review gate: @mbaetiong approves before execution

---

## 📊 Agent Ecosystem Success Metrics (Updated)

| Metric | Baseline | S57 Target | S58 Target | S59 Target |
|--------|----------|------------|------------|------------|
| k₁ score | 0.36 | 0.36 | 0.35 ✅ | 0.35 stable |
| Agents with Planner ABC | 7 | 9 (+SelfHealingEngine, WorkflowNavigator) | 12 (+3 more) | 53 (all) |
| Test coverage (GitHub agents) | ~65% | 70% | 75% | 80% |
| GitHub API integration (reviewer) | Stub | Stub | Full ✅ | Full + rate-limit |
| Merge candidates executed | 0 | 0 | 3 (M-01, M-02, M-03) | 5 (all) |
| SQLiteMemory available | No | Yes ✅ | Yes | Yes + WAL mode |
| Quantum advantage | 2.86× | 2.86× | 2.90× | 3.0× |
| Sessions automated | 0% | 0% | 30% (A1+A2) | 70% (A1–A4) |

---

## 🔗 Cross-References

| Document | Relevance |
|----------|-----------|
| `.codex/TECH_DEBT_REGISTRY.md` | TD-001..TD-048 — E-01..E-12 map to new P1/P2 items |
| `.codex/plans/AGENTIC_SESSION_METHODOLOGY.md` | MSP protocol — A2/A3 automation targets §MSP-2 |
| `.codex/plans/AI_AGENT_TEAM_DEVELOPMENT_PROCESS.md` | PDCA-MARL loop — agent merges follow ASSIGN→EXECUTE pattern |
| `.codex/plans/TOP3_AGENT_ENHANCEMENT_PLANSETS.md` | ci-testing-agent v4 (already implemented S53) |
| `.github/agents/AGENT_REGISTRY.yaml` | Source registry — update with merge deprecations in S58 |
| `.github/agents/github-guru-agent/` | E-04 GitHub API + A3 Session Reviewer target |
| `src/cognitive_brain/base.py` | Planner/MemoryInterface ABCs — E-01/E-02 foundation |
| `agents/cognitive_adapter.py` | LegacyAgentAdapter — already bridges to Planner ABC |

---

## ⚡ Deep Investigation Questions (DR-011..DR-016)

> From @mbaetiong's request to "look ahead of the errors to better understand what more there is to resolve"

| # | Question | Why It Matters |
|---|----------|----------------|
| DR-011 | Why do 46/53 GitHub agents NOT inherit `Planner` ABC? Is there a structural reason (stateless prompt files vs stateful Python)? | Determines whether OODA formalization is feasible for all 53 or only for Python-backed agents |
| DR-012 | What is the actual quantum advantage calculation? Is 2.86× measured or theoretical? | If theoretical, need empirical benchmark to validate E-03 weight changes don't regress it |
| DR-013 | Why does `_TORCH_312_BUG` affect `isinstance()` union types specifically? Will PyTorch 2.7 actually fix it? | Drives PyTorch upgrade urgency and xfail removal timeline |
| DR-014 | Is `SimpleDictMemory` causing cross-test contamination via shared global state? | Explains intermittent flaky tests in circuit-breaker / statistics suites |
| DR-015 | Does the CI "no tests ran" (exit code 5) for test-rag recur after our importorskip fix? | Validates whether `codex.rag` collection failure was the root cause |
| DR-016 | Can GitHub Guru Agent's SAFE_MODE be toggled per-session via environment variable without a code change? | Critical path for post-Genesis autonomous operation (Phase 2 readiness) |

---

**Status**: 🟢 Ready for S57 execution
**Next Action**: Apply E-01 (SelfHealingEngine OODA formalization) as first S57 task
**Guard Gate**: D1–D4 mandatory before every `report_progress` commit
**Compiled from**: Comment #3938173408 (35,897 chars) — 5 prior synthesis iterations
