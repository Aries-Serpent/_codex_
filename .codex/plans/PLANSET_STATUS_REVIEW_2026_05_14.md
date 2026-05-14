# 📋 Planset & Promptset Status Review
**Generated:** 2026-05-14T00:45Z (S1003-ctep)  
**Scope:** All plansets in `.codex/plans/` (128 files) and promptsets in `.github/copilot-prompts/active/` (235 files)  
**Review method:** Full directory scan + content-based status classification

---

## 🟢 TIER 1 — COMPLETED / CLOSED (no action needed)

| ID / File | Title | Completed | Evidence |
|-----------|-------|-----------|----------|
| PS-01 | Configuration Consolidation | 2026-01-09 | `.codex/cognitive_brain/ps01_status.md` |
| PS-02 | IPC Bridge Hardening | 2026-01-09 | `ps02_status.md` |
| PS-03 | Split Brain Elimination | 2026-01-09 | `ps03_status.md` |
| PS-04 | Privacy-First Memory | 2026-01-09 | `ps04_status.md` |
| PS-05 | Token Security Neutralization | 2026-01-09 | `ps05_status.md` |
| PS-06 | Knowledge Crawler Service | 2026-01-09 | `ps06_status.md` |
| PS-06e | Knowledge Crawler Enhancement | 2026-01-09 | `ps06_enhancement_status.md` |
| PS-07 | Business Logic Elevation | 2026-01-09 | `ps07_status.md` |
| PS-08 | Microservice Root Cleanup | 2026-01-09 | `ps08_status.md` |
| PS-09 | Training Entry Point Unification | 2026-01-09 | `ps09_status.md` |
| PS-10 | Owner Guard CI/CD Enforcement | 2026-01-09 | `ps10_status.md` |
| PS-11 | MCP Size Estimation | 2026-02-12 | `ADVANCED_FEATURES_PLANSET.md` Feature 1 |
| PS-12 | MCP Exclude Patterns | 2026-02-12 | `ADVANCED_FEATURES_PLANSET.md` Feature 2 |
| PS-13 | Agent Task Router | 2026-02-12 | `scripts/monitoring/agent_orchestrator.py` |
| PS-14 | Cognitive Dashboard MSV | 2026-02-12 | `MSVRadarChart.tsx` |
| PS-15 | Advanced Infrastructure | 2026-02-12 | CacheManager Ph3, Trend v2, Healing v2 |
| PS-16 | Production Readiness | 2026-02-12 | Context optimizer, AAIS 97.0 |
| PS-17 | Operational Excellence | 2026-02-12 | Pages deploy, CacheManager Ph4 |
| PS-18 | Continuous Improvement | 2026-02-12 | AAIS pipeline, Benchmarking |
| CB-ST-2026-02-05 | Cognitive Brain Short-term (5 sessions) | 2026-02-05 | `cognitive_brain_short_term_planset.md` — 133 tests passing |
| IP-005 | Dependency Security Audit | 2026-01-16 | All 26 CVEs addressed, pip-audit clean |
| IP-002 | Legacy Config Consolidation | ~2026-02-xx | `IP-002_LEGACY_CONFIG_AUDIT.md` |
| IP-004 | Production Authentication | ~2026-02-xx | `IP-004_PRODUCTION_AUTHENTICATION.md` |
| Security Batches 1–4 | Bandit/CVE remediation (Batches 1-4) | 2026-05-13 | `security-remediation-planset.md` Master Tracking |
| `PR-4427-codeql-remediation.md` S967–S968 | CodeQL 127→117 (2 sessions) | 2026-05-12 | PR #4427 S968 complete |
| S1003 full sweep (PR #4450) | CodeQL 127→~54 (-73 alerts) | 2026-05-13 | S1003–S1003-ctep commits |
| Pattern 30 REQ-PDA hardening | `pda_today` pda_manual → pda_auto | 2026-05-14 | commit `30bd4b3` (S1003-ctep) |
| Mermaid docs refresh | `architecture.mmd`, `ci_self_healing_flow.mmd`, README index | 2026-05-14 | commit `4848978` (S1003-ctep) |

---

## 🟡 TIER 2 — IN PROGRESS (active / partially complete)

### 🔴 P1 — Critical, blocking PR #4450 merge

| File | Title | Status | Next Action |
|------|-------|--------|-------------|
| `CODEQL_ALERT_INVENTORY.md` + `CODEQL_REMEDIATION_MASTER_PLAN.md` | CodeQL 127 → 0 alerts | **~54 remaining** — merge gate is < 25 | Fix residual `py/unused-local-variable`, `py/ineffectual-statement`, additional `actions/unpinned-tag` → recount via API once rate limit resets |
| `PR-4427-codeql-remediation.md` sessions S969–S975 | Unpinned tags (part 1/2) + workflow permissions + untrusted checkout + code quality | S969 onwards not executed (superseded by S1003 bulk sweep — ~54 alerts remain) | Use `list_code_scanning_alerts` to get current list; fix remaining `actions/unpinned-tag` and `py/unused-local-variable` |
| `security-remediation-planset.md` Batch 5 | Transitive CVE monitoring (diskcache, sqlitedict) | 🔲 Monitor only — no fix versions exist | Re-run `security-scanning-suite.yml` monthly or on major dep bump |
| `security-remediation-planset.md` Batch 6 | Full post-merge rescan | 🔲 **After PR #4450 merges to main** | Dispatch `security-scanning-suite.yml` on `main`, update planset Master Tracking |

### 🟡 P2 — Active, not blocking merge

| File | Title | Status | Next Action |
|------|-------|--------|-------------|
| `CB-LT-2026-02-05` / `cognitive_brain_long_term_planset.md` | Cognitive Brain long-term (15 sessions): 100% agent integration, ML pattern recognition, cross-session learning | Plan 1 complete, Plan 2 Phase 2.3 complete — **ongoing** | Continue Plan 2 Phase 2.4+ in next dedicated CB session |
| `COVERAGE_THRESHOLD_ROADMAP.md` | Coverage 0% → 70% → 100% | Threshold at 70% (Pattern 4 auto-fix). Actual ~90% per AGENTS.md | Raise `fail_under` progressively; `unified-coverage-agent` owns |
| `CODEQL_CHUNKING_PLAN.md` | Systematic alert chunking/batching | Sessions S969–S975 partially planned | Superseded by S1003 bulk approach; review remaining ~54 alerts and re-chunk |
| `PS-19` | Next Evolution Phase (AAIS V4.0, Multi-repo, ML tracking, Auto-docs) | ⏳ Planned | Start after merge gate cleared |
| `BRANCH_DIVERGENCE_PLAN_SET.md` | Branch divergence `0D_base_` ↔ `main` prevention | RC-1 through RC-4 fixed in S237 (PR #3770) — monitor for recurrence | Run `branch-divergence-monitor.yml` weekly; `branch-divergence-resolution-agent` handles any new recurrence |

### 🟢 P3 — Ongoing / maintenance cadence

| File | Title | Cadence | Owner |
|------|-------|---------|-------|
| `COVERAGE_PATH_70_TO_100_PERCENT.md` | Test coverage 70% → 100% | Per-sprint | `unified-coverage-agent` |
| `MASTER_100_PERCENT_COVERAGE_PROMPTSET.md` | 100% coverage promptset | Per sprint | `unified-coverage-agent` |
| `AI_AGENT_RAG_EXECUTION_PLANSET.md` | RAG index freshness + embedding updates | Weekly sweep | `rag-freshness-loop-agent` |
| `AGENT_CHAINING_INTEGRATION_PLANSET.md` | Agent chaining + orchestration | Ongoing | `orchestrator-agent` |
| `BATCH_TRIAGE_COGNITIVE_BRAIN_INTEGRATION_PLANSET.md` | CI batch triage + CB integration | Per-session | `ci-triage-pipeline-agent` |
| `AGENTIC_SESSION_METHODOLOGY.md` | Session methodology enforcement | Always-on | All agents |
| `ML_PATTERN_FEEDING_PLANSET.md` | ML pattern ingestion into cognitive brain | Monthly | `rag-index-manager` |

---

## 🔴 TIER 3 — STALE / NEEDS ARCHIVING

These plansets reference outdated PR numbers, old session IDs, or work that was superseded:

| File | Reason | Recommendation |
|------|--------|----------------|
| `PR-2639-*` (5 files) | PR #2639 merged long ago | Archive to `.github/copilot-prompts/archive/` |
| `PR-2665-followup.md` through `PR-2688-followup.md` | PRs 2665–2688 all merged/closed | Archive |
| `PR-3133-followup.md` through `PR-3145-followup.md` | PRs 3133–3145 all merged/closed | Archive |
| `PHASE1-COMPLETE-NEXT-STEPS.md`, `PHASE2-COMPLETE-PHASE3-READY.md` | Genesis phases 1-2 complete | Archive |
| `PHASE3A_IMMEDIATE_IMPLEMENTATION.md`, `PHASE3C_LITE_IMPLEMENTATION.md` | Phase 3A/3C done | Archive |
| `PHASE5-COMPLETE-SUMMARY.md`, `PHASE6-CONTINUATION-PROMPT.md` | Phases 5-6 done | Archive |
| `HOTFIX-deferral-ml-userstore-db.md`, `HOTFIX-post-PR3375-infra-failures.md` | One-time hotfixes, resolved | Archive |
| `MASTER_PLANSET_PRODUCTION_READINESS.md` | Partial completion from 2026-02-06, stale timing | Review and archive PS-1/PS-2 items; retain active ones |
| `COGNITIVE_BRAIN_STATUS_POST_PR2956.md`, `COGNITIVE_BRAIN_STATUS_PR3478.md`, `COGNITIVE_BRAIN_STATUS_V2.md` | Superseded by latest CB status | Archive |
| `ENHANCEMENT_RESEARCH_PLANSETS.md` | Catch-all research doc, superseded | Archive or consolidate into PS-19 |

---

## 📊 Promptset Status Summary

| Category | Total | ✅ Done / archive-ready | 🔄 Active | ⏳ Pending |
|----------|:-----:|:-----------------------:|:---------:|:---------:|
| PR followups (old PRs < #4400) | ~80 | ~75 | 5 | 0 |
| PR followups (current PRs ≥ #4427) | 6 | 0 | 6 | 0 |
| Phase / Genesis prompts | ~12 | ~10 | 2 | 0 |
| CodeQL remediation sessions | 7 | 2 (S967–S968) | 1 (active) | 4 (S969–S975) |
| Session continuation prompts | ~20 | ~15 | 5 | 0 |
| Security / IP plans | 5 | 4 | 1 (IP-005 monitor) | 0 |
| Coverage / quality roadmaps | 4 | 0 | 4 | 0 |
| Cognitive brain plansets | 6 | 2 (short-term) | 3 (long-term) | 1 (PS-19) |
| Agent plansets (custom) | 4 | 0 | 4 | 0 |

---

## 🎯 Priority Actions for Next Sessions

### Immediate (this PR — #4450, pre-merge)
1. **CodeQL alert count < 25** — API rate-limited; recheck after reset. Fix remaining `actions/unpinned-tag` + `py/unused-local-variable` alerts to reach < 25.
2. **Batch 5** (CVE monitor) — No action needed; re-check monthly.

### Next PR (post-merge `0D_base_` → `main`)
3. **Batch 6** — Run `security-scanning-suite.yml` on `main`, confirm 0 actionable CVEs, update planset Master Tracking.
4. **CodeQL → 0** — New PR from `0D_base_` targeting 0 residual alerts; use `codeql-alert-resolution-agent`.
5. **PS-19 launch** — AAIS V4.0, multi-repo expansion, ML tracking, auto-docs.
6. **Archive stale prompts** — Move 75+ stale PR followups to `.github/copilot-prompts/archive/`.

### Ongoing (maintenance cadence)
7. **Cognitive Brain long-term** — Plan 2 Phase 2.4+ (autonomous objective adjustment).
8. **Coverage 70% → 100%** — `unified-coverage-agent` incremental raises.
9. **RAG freshness** — Weekly `rag-freshness-loop-agent` sweeps.

---

## 📌 Key Artifacts for Next Session

```
Artifacts from run 25833450038 (2026-05-14):
  dependency-scan-results  sha256:843798e5…  → 0 actionable CVEs
  sbom-reports             sha256:028fc402…  → 326 components, 0 vulns

CodeQL target: ~54 open → <25 (merge gate) → 0 (post-merge)
Security planset: security-remediation-planset.md (Batch 5/6 remaining)
Living docs: docs/roadmap/PR4448_whats_next.md (score 100/100 CI dims)
```

---

_Last updated: 2026-05-14T00:45Z by S1003-ctep (`4848978`)_
