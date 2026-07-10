# Codebase-Wide Coverage Capture Plan
## Improving Copilot Agent Error-Location & Cognitive Brain Resolution Accuracy

> **Status:** Draft — S235 (2026-03-30)
> **Author:** Copilot Coding Agent (auto-generated plan)
> **Related Issues:** #3779, #3816
> **Implementation artefacts:**
>   - `scripts/ci/generate_coverage_map.py`
>   - `.codex/coverage/coverage_map.json` (generated)
>   - `.codex/coverage/COVERAGE_GAPS.md` (generated)

---

## 1. Problem Statement

Copilot Coding Agents operating in this repository frequently encounter pre-existing
bugs or untested code paths that are **invisible to the agent** at session start.
Without per-module, per-function coverage data injected into agent context, the agent
cannot distinguish between:

- Lines that are regression-tested (safe to refactor)
- Lines that have *never* been executed in tests (high-risk; may contain dormant bugs)
- Lines that were once covered but regressed (signals test rot)

Additionally, the cognitive brain cannot record "module X, function Y is never
tested" as an actionable pattern unless a structured, machine-readable coverage map
exists and is refreshed on every CI cycle.

---

## 2. Objectives

| ID  | Objective | Benefit |
|-----|-----------|---------|
| O-1 | Capture line-level coverage for **every Python module** under `src/` | Eliminates blind spots |
| O-2 | Produce a per-function uncovered-index queryable by agents | Enables pre-task risk assessment |
| O-3 | Publish a coverage delta on every PR (which lines the PR changed were uncovered?) | Prevents untested bug introduction |
| O-4 | Integrate coverage gaps into the cognitive brain pattern DB | Persistent institutional memory |
| O-5 | Provide a CLI query interface agents can call at session start | Zero-friction context injection |

---

## 3. Current State

| Suite | Workflow | Scope | Status |
|-------|----------|-------|--------|
| RAG Module Tests | `test-rag.yml` | `src/codex/rag` | ✅ Fixed (S235: `--cov-config=tests/rag/.coveragerc`) |
| General Tests | `validate.yml` | `src/` (broad) | ⚠️ Coverage not published as artifact |
| Coverage with Timeout | `coverage-with-timeout.yml` | `src/` (sharded) | ⚠️ No aggregation |
| Code Quality Suite | `code-quality-coverage-suite.yml` | `src/` | ⚠️ Threshold only, no map artifact |

**Gap:** No single aggregated, machine-readable coverage map exists. Coverage data from
multiple suites is siloed as CI artifacts and never merged into a queryable index.

---

## 4. Architecture — Coverage Intelligence System

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       COVERAGE INTELLIGENCE SYSTEM                          │
│                                                                             │
│  Layer 1: Per-Suite Coverage (CI)                                           │
│  ┌──────────────┐ ┌──────────────┐ ┌────────────────────┐                  │
│  │ test-rag.yml │ │ validate.yml │ │ coverage-with-     │  → coverage.xml  │
│  │ (RAG scope)  │ │ (broad src/) │ │ timeout.yml        │    per suite     │
│  └──────────────┘ └──────────────┘ └────────────────────┘                  │
│            │               │                    │                           │
│            └───────────────┴────────────────────┘                           │
│                                   ▼                                         │
│  Layer 2: Coverage Aggregator (scripts/ci/generate_coverage_map.py)         │
│  ┌─────────────────────────────────────────────────────────────┐            │
│  │  • Merges multiple coverage.xml reports                     │            │
│  │  • Resolves line numbers → function names via ast.parse()   │            │
│  │  • Emits .codex/coverage/coverage_map.json (per-function)   │            │
│  │  • Emits .codex/coverage/COVERAGE_GAPS.md (human-readable)  │            │
│  └─────────────────────────────────────────────────────────────┘            │
│                                   │                                         │
│               ┌───────────────────┴───────────────────┐                    │
│               ▼                                       ▼                    │
│  Layer 3a: Cognitive Brain Integration    Layer 3b: Agent Context Injection │
│  ┌────────────────────────────────┐       ┌─────────────────────────────┐   │
│  │  scripts/cognitive/            │       │  scripts/ci/query_coverage  │   │
│  │  inject_coverage_context.py    │       │  .py --module <name>        │   │
│  │  • Stores coverage gap as      │       │  → prints uncovered funcs   │   │
│  │    CI pattern P-XXX            │       │    for agent session start   │   │
│  │  • Tags with ImprovementArea   │       └─────────────────────────────┘   │
│  └────────────────────────────────┘                                         │
│                                   │                                         │
│               ▼                                                              │
│  Layer 4: CI Workflow (coverage-intelligence.yml)                            │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  Trigger: schedule (nightly 03:00 UTC) + push to main + workflow_      │ │
│  │  dispatch                                                              │ │
│  │  • Downloads coverage artifacts from latest completed runs            │ │
│  │  • Runs generate_coverage_map.py                                       │ │
│  │  • Commits .codex/coverage/ updates [skip ci]                         │ │
│  │  • Posts coverage badge / delta comment on open PRs                   │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Implementation Phases

### Phase 1 — Foundation (S235, this session) ✅

- [x] Fix RAG coverage scope: `tests/rag/.coveragerc` + `--cov-config` in `test-rag.yml`
- [x] Create `scripts/ci/generate_coverage_map.py` — parses coverage.xml, emits
      `coverage_map.json` with per-function uncovered index
- [x] Create `.codex/coverage/COVERAGE_GAPS.md` schema (generated file)
- [x] Create `.codex/coverage/coverage_map.json` schema (generated file)

### Phase 2 — Aggregation Workflow (next session)

- [ ] Create `.github/workflows/coverage-intelligence.yml`
  - Triggers: nightly 03:00 UTC, push to main, workflow_dispatch
  - Downloads coverage.xml artifacts from `validate.yml`, `test-rag.yml`,
    `coverage-with-timeout.yml` using `gh run download`
  - Runs `python scripts/ci/generate_coverage_map.py --merge <xmlfiles...>`
  - Commits `.codex/coverage/` with `[skip ci]`
  - Uploads `coverage_map.json` as named artifact `coverage-intelligence-map`

### Phase 3 — PR Coverage Delta (next session)

- [ ] Extend `generate_coverage_map.py` with `--pr-delta <base_map> <head_map>` mode
  - Computes which functions changed in the PR are uncovered in head map
  - Posts delta as PR comment: "⚠️ 3 changed functions have no test coverage"
  - Integrates into `comment-review-gate.yml` as informational (non-blocking)

### Phase 4 — Cognitive Brain Integration (next session)

- [ ] Extend `scripts/cognitive/inject_coverage_context.py` to:
  - At agent session start, query `coverage_map.json` for the modules being edited
  - Inject uncovered function list into `agent_context.json` session context
  - Store coverage gaps as patterns in `.codex/patterns/ci_failure_patterns.yaml`
    with `ImprovementArea: test_coverage`
  - Format: `P-COV-{module_hash}: {module} has {n} uncovered functions`

### Phase 5 — Agent Query Interface (future)

- [ ] Create `scripts/ci/query_coverage.py`:
  ```
  python scripts/ci/query_coverage.py --module codex.rag.embeddings
  → codex.rag.embeddings: 87.3% coverage
     ⚠ Uncovered functions (3):
       embed_batch_async  (lines 234–267) — no tests
       _retry_on_error    (lines 312–334) — no tests
       flush_cache        (lines 401–412) — 1 partial branch
  ```
- [ ] Add `query_coverage` call to `check_pr_comments.py` pre-scan step so the
  checklist includes a "🔍 Coverage impact" section

---

## 6. Coverage Map JSON Schema

`.codex/coverage/coverage_map.json`:
```json
{
  "_meta": {
    "generated_at": "2026-03-30T17:40:00Z",
    "git_sha": "d15c925abc",
    "source_suites": ["test-rag", "validate", "coverage-with-timeout"],
    "total_modules": 120,
    "overall_line_rate": 0.72
  },
  "modules": {
    "codex.rag.embeddings": {
      "file": "src/codex/rag/embeddings.py",
      "suite": "test-rag",
      "line_rate": 0.924,
      "branch_rate": 0.871,
      "uncovered_lines": [234, 235, 236, 312, 313, 401],
      "uncovered_functions": [
        {
          "name": "embed_batch_async",
          "start_line": 234,
          "end_line": 267,
          "category": "async_path",
          "risk": "medium"
        }
      ],
      "covered_functions": ["embed", "embed_batch", "flush_cache"]
    }
  },
  "gaps_summary": {
    "modules_below_50pct": ["codex.rag.benchmarks.runner", "codex.cli_legacy"],
    "modules_zero_coverage": ["codex.rag.analytics.dashboard"],
    "total_uncovered_functions": 47,
    "high_risk_functions": 12
  }
}
```

---

## 7. COVERAGE_GAPS.md Schema

`.codex/coverage/COVERAGE_GAPS.md` (auto-generated, committed with `[skip ci]`):

```markdown
# Coverage Gaps Index — codex repository
> Generated: 2026-03-30 | SHA: d15c925 | Overall: 72.4%

## 🔴 Zero-Coverage Modules (0 %)
| Module | Lines | Notes |
|--------|-------|-------|
| codex.rag.analytics.dashboard | 213 | Needs DB service |

## 🟠 Low-Coverage Modules (< 50 %)
| Module | Coverage | Uncovered Functions |
|--------|----------|---------------------|
| codex.rag.benchmarks.runner | 12 % | run_suite, profile_run |

## 🟡 Partially-Covered (50–80 %)
...

## Uncovered Function Index
### codex.rag.embeddings
- `embed_batch_async` (lines 234–267): async variant never called in tests
```

---

## 8. Cognitive Brain Pattern Format

New pattern class for coverage gaps stored in
`.codex/patterns/ci_failure_patterns.yaml`:

```yaml
- id: P-COV-001
  name: uncovered_function
  description: >
    A function in the source code has never been executed by any test suite.
    When a Copilot agent modifies this function, it cannot rely on test
    regression to catch mistakes.
  category: test_coverage
  improvement_area: test_coverage
  trigger_condition: "function has line_rate == 0.0 in coverage_map.json"
  agent_action: >
    Before modifying an uncovered function:
    1. Check .codex/coverage/coverage_map.json for the function's risk level
    2. Add at minimum one happy-path unit test before modifying
    3. Re-run coverage after the change to confirm coverage increased
  examples:
    - module: codex.rag.embeddings
      function: embed_batch_async
      risk: medium
```

---

## 9. Agent Session Context Injection Protocol

At the start of each Copilot session, `cognitive-brain-session-injector` should:

```python
# Pseudo-code for inject_coverage_context.py
def inject_for_session(changed_files: list[str], agent_context: dict) -> dict:
    coverage_map = load_json(".codex/coverage/coverage_map.json")
    relevant_gaps = []
    for f in changed_files:
        module = file_to_module(f)          # "src/codex/rag/embeddings.py" → "codex.rag.embeddings"
        if module in coverage_map["modules"]:
            entry = coverage_map["modules"][module]
            if entry["uncovered_functions"]:
                relevant_gaps.append({
                    "module": module,
                    "coverage": entry["line_rate"],
                    "uncovered": entry["uncovered_functions"]
                })
    agent_context["coverage_gaps"] = relevant_gaps
    agent_context["coverage_warning"] = (
        f"⚠ {len(relevant_gaps)} module(s) you are editing have uncovered functions. "
        "See .codex/coverage/COVERAGE_GAPS.md for details."
    )
    return agent_context
```

---

## 10. Risk Assessment for Pre-Existing Errors

The coverage map enables a **pre-existing error risk score** per module:

| Score | Condition | Agent Behaviour |
|-------|-----------|-----------------|
| 🟢 LOW | `line_rate ≥ 0.90` | Proceed normally; tests will catch regressions |
| 🟡 MEDIUM | `0.50 ≤ line_rate < 0.90` | Add test for the specific line being changed |
| 🟠 HIGH | `0.20 ≤ line_rate < 0.50` | Write test first (TDD), then modify |
| 🔴 CRITICAL | `line_rate < 0.20` | Escalate; do not modify without owner review |

This risk score should be injected into the `.codex/archive/reports/AGENT_ACCOUNTABILITY_REPORT.md`
session header alongside the standard PDA loop metrics.

---

## 11. Success Metrics

| Metric | Current | Target (Phase 2) | Target (Phase 5) |
|--------|---------|------------------|------------------|
| Overall codebase coverage | ~72 % | 75 % | 85 % |
| Modules with 0 % coverage | ~8 | ≤ 4 | 0 |
| Agent sessions with coverage context | 0 % | 100 % | 100 % |
| Pre-existing bugs caught pre-fix | Unknown | Tracked | ≥ 80 % |
| Coverage map freshness | N/A | < 24 h | < 1 h |

---

## 12. Related Documents

- `.codex/CODEBASE_AGENCY_POLICY.md` — §3a: fix ALL issues found
- `.codex/patterns/ci_failure_patterns.yaml` — pattern library
- `.codex/plans/cognitive_brain_phase_implementation.md` — cognitive brain roadmap
- `docs/accountability/.codex/archive/reports/AGENT_ACCOUNTABILITY_REPORT.md` — session accountability
- `scripts/ci/generate_coverage_map.py` — Phase 1 implementation (this session)
