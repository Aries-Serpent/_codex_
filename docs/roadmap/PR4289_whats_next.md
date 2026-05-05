# _codex_ — What's Next: Roadmap After PR #4289

> **Status as of 2026-05-05** · Merge Readiness: 100/100 · CI Issues: 0 · CodeQL Alerts: 0

---

## Roadmap Overview

```mermaid
gantt
    title _codex_ Roadmap — Post PR #4289
    dateFormat  YYYY-MM-DD
    section Security
        Verify all CodeQL alerts closed in GH Security tab     :crit, sec1, 2026-05-06, 1d
        Run Semgrep SAST full scan + review new findings       :sec2, after sec1, 2d
        Bandit audit — address any medium/high severity        :sec3, after sec2, 2d
        Upgrade PBKDF2 iterations 100k → 600k (OWASP 2024)    :sec4, after sec3, 3d
    section CI Health
        Confirm Issue Resolution Gate passes                   :crit, ci1, 2026-05-06, 1d
        Confirm Agent Token Delegation passes                  :crit, ci2, 2026-05-06, 1d
        Monitor Pattern 17 drift suppression in live CI        :ci3, after ci1, 2d
        Add Pattern 33 — BLE001 ruff lint gate for src/        :ci4, after ci3, 3d
    section Code Quality
        Apply except-narrowing to src/ non-test code           :q1, 2026-05-07, 3d
        Resolve 113 remaining mypy errors (baseline 328 → 215) :q2, after q1, 5d
        Eliminate all Src Absolute Imports (Pattern 19)        :q3, after q2, 5d
        Fix YAML Multiline Strings in workflows (Pattern 20)   :q4, after q3, 2d
    section Coverage
        RAG module coverage >= 95% (test-rag.yml gate)         :cov1, 2026-05-08, 5d
        Add missing unit tests for rag_api._ensure_subpath     :cov2, 2026-05-08, 2d
        Increase overall coverage from ~70% → 80%              :cov3, after cov1, 7d
    section Genesis / Autonomy
        E-to-D transition gate (e-to-d-transition-gate.yml)    :gen1, 2026-05-12, 3d
        D-CAPABLE promotion gate                               :gen2, after gen1, 3d
        MCP Health gate (mcp-health.yml)                       :gen3, after gen2, 2d
```

---

## Priority 1 — Immediate (Next Session)

```mermaid
flowchart TD
    P1([Priority 1 — Next Session])

    P1 --> CI_GATE[Confirm CI gates\nIssue Resolution Gate\nAgent Token Delegation\nFast Validation\nPre-Merge Validation]

    P1 --> CODEQL_CHECK[Verify GitHub Security tab\nall alerts 13330–13361\nshown as Closed / Fixed]

    P1 --> RUFF_CHECK[ruff check src/ tests/\nconfirm 0 violations\non merged HEAD]

    P1 --> SYNC_CHECK[sync_tracked_files.py --check\nconfirm all hashes consistent\nafter merge commit]

    CI_GATE --> MERGE_READY[PR #4289 merges cleanly]
    CODEQL_CHECK --> MERGE_READY
    RUFF_CHECK --> MERGE_READY
    SYNC_CHECK --> MERGE_READY
```

---

## Priority 2 — Near-Term Quality

```mermaid
mindmap
  root((Quality Backlog))
    Security
      PBKDF2 iterations 100k to 600k per OWASP 2024
      Semgrep SAST full scan review
      Bandit medium/high findings
    Code Health
      except Exception in src/ non-test files
      BLE001 ruff rule enable for src/
      Src Absolute Imports Pattern 19
      YAML Multiline Strings Pattern 20
    Type Safety
      mypy baseline 328 to 215 errors
      New stub packages for missing types
      Strict mode gradual rollout
    Test Coverage
      rag_api._ensure_subpath unit tests
      RAG module coverage gate 95 pct
      Overall coverage 70 to 80 pct
```

---

## Priority 3 — Auto-Fix Pipeline Expansion

```mermaid
flowchart LR
    CURRENT["Current Auto-Fix Patterns\n18 patterns\nP1 P4 P6 P7 P8 P9 P10\nP11 P12 P13 P14 P16 P18\nP23 P25 P26 P27 P29 P30"]

    CURRENT --> ADD1["Pattern 33 — BLE001 src/\nEnable ruff BLE001 for src/\nnarrow broad handlers in prod code"]
    CURRENT --> ADD2["Pattern 34 — mypy strict\nAuto-add type annotations\nwhere mypy reports missing"]
    CURRENT --> ADD3["Pattern 35 — YAML Multiline\nAuto-convert multiline bash\nto printf pipeline pattern"]
    CURRENT --> ADD4["Pattern 36 — Src Imports\nAuto-rewrite from src.X\nto from codex.X"]

    ADD1 --> FUTURE_P["Future auto-fix suite\n22 patterns\nzero manual-review patterns\nfor mechanical fixes"]
    ADD2 --> FUTURE_P
    ADD3 --> FUTURE_P
    ADD4 --> FUTURE_P
```

---

## Priority 4 — Genesis Protocol

```mermaid
stateDiagram-v2
    [*] --> PreGenesis : Current state
    PreGenesis : Pre-Genesis\nSAFE_MODE=true\nAdvisory only

    PreGenesis --> EToD : e-to-d-transition-gate.yml passes\nAll CI green + coverage + security

    EToD : E Model\nAdvisory + PR creation\nNo direct commits

    EToD --> DCapable : d-capable-promotion-gate.yml\nAll autonomy metrics green

    DCapable : D_CAPABLE\nFull autonomous operations\nwithin guardrails

    DCapable --> Genesis2 : Human admin\nactivates Phase 2

    Genesis2 : Genesis Phase 2\nSecret injection\nWorkflow enablement

    Genesis2 --> Genesis3 : Validation complete
    Genesis3 : Genesis Phase 3\nFull autonomous production ops
```

---

## Dependency Map

```mermaid
flowchart TD
    A[PR #4289 merged] --> B[CodeQL baseline clean]
    A --> C[0 auto-fix issues baseline]

    B --> D[Enable CodeQL for all branches\nnot just PRs]
    C --> E[Add Patterns 33-36\nexpand auto-fix coverage]

    D --> F[Semgrep SART + CodeQL\ndual SAST gate]
    E --> G[mypy strict mode\ngradual rollout]

    F --> H[Security posture: HIGH]
    G --> I[Type safety: HIGH]

    H --> J[E-to-D transition gate\neligibility]
    I --> J

    J --> K[D_CAPABLE promotion]
    K --> L[Genesis Phase 2]
```

---

## Key Metrics to Track

| Metric | Current | Target | Owner Pattern |
|--------|---------|--------|---------------|
| `auto_fix_common_issues --check-only` exit code | **0** ✅ | 0 forever | Patterns 1–32 |
| CodeQL open alerts | **0** ✅ | 0 forever | SAST workflow |
| Merge Readiness Score | **100/100** ✅ | ≥ 95/100 | Pattern 30 |
| mypy error count | ~282 (full env) | ≤ 215 | Pattern 15 |
| Test coverage (overall) | ~70% | ≥ 80% | coverage-with-timeout |
| RAG module coverage | unknown | ≥ 95% | test-rag.yml |
| `except Exception:` in `src/` | unknown | 0 | Pattern 33 (new) |
| `from src.X` imports | unknown | 0 | Pattern 19 |
