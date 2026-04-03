# Cognitive Brain & Agentic System — Live Status

> **Purpose**: Single canonical source of truth for ongoing cognitive system development.
> Update this document after every PR that touches the agentic infrastructure.
>
> **Last Updated**: 2026-04-03 (PR #3854, S301 — PDA loop documented, discussion cleanup token investigation, manifest refresh 538 dupes)
> **Maintainer**: auto-updated by agent sessions per REQ-4

---

## 🟢 System Health Dashboard

```
Soft→GROUNDED Conversion:  ✅ 100% COMPLETE  (7 phases, 18/18 work units)
E→D Gate Score:             5/5 ✅            (C1 C2 C3 C4 C5 all satisfied)
AGENT_REGISTRY:             v1.9.0            (152 agents | GROUNDED:8 PARTIAL:144 SOFT:0)
CODEX_MANIFEST.json:        ✅ Valid           (generated 2026-03-02T23:58:27Z, <24h)
FAISS Corpus:               ⚠️ Keyword fallback (index meta committed; .faiss rebuilt nightly)
Operating Model:            E (advisory)      — D_CAPABLE: all gates pass, human activation pending
CI Pipeline Health:         ✅ Fast validation unblocked as of PR #3474
Pre-commit Baseline:        ✅ detect-secrets baseline covers codex_index_meta.json
```

---

## 🔵 Component Status

| Component | Status | Version | Notes |
|-----------|:------:|---------|-------|
| `AGENT_REGISTRY.yaml` | ✅ Active | v1.9.0 | 152 agents; all enforcement fields present |
| `CODEX_MANIFEST.json` | ✅ Active | — | SHA-256 integrity; regenerated on each push via CI |
| `.codex/schemas/AgentRegistrySchema.json` | ✅ Active | draft-07 | Validates all 152 agents |
| `.codex/schemas/AgentHandoffManifest_v1.1.json` | ✅ Active | v1.1 | Tier-1 validated by agent-handoff-gate |
| `.codex/schemas/CodexManifestSchema.json` | ✅ Active | — | Validates CODEX_MANIFEST.json |
| `.codex/embeddings/codex_index_meta.json` | ✅ Active | — | EOF newline fixed (PR #3474); baseline registered |
| `agent-registry-validation.yml` | ✅ Tier-1 | — | exit 1 on schema violations (C1) |
| `agent-handoff-gate.yml` | ✅ Tier-1 | — | exit 1 on handoff violations (C4) |
| `e-to-d-transition-gate.yml` | ✅ Tier-1 | — | core.setFailed; 5/5 conditions (C1–C5) |
| `embedding-index-rebuild.yml` | ✅ Tier-1 | — | exit 1 on unhealthy FAISS index; nightly 2AM UTC |
| `actionlint-audit.yml` | ✅ Tier-1 | — | exit 1 on workflow lint errors |
| `pr-size-analyzer.yml` | ✅ Fixed | — | Concurrency group includes `github.event_name` (PR #3477) |
| `build_embeddings.py` | ✅ Deployed | — | FAISS all-MiniLM-L6-v2, 512 chunks, 90-day retention |
| `query_corpus.py` | ✅ Deployed | — | Semantic search with keyword fallback |
| `orchestrator_routing.py` | ✅ Deployed | — | Routes tasks to top-20 agents via corpus |
| `generate_manifest.py` | ✅ Hardened | — | R-12: CONTEXT_WINDOW_BUDGET=32_000; budget guard in sanitize_for_injection |
| `enforcement_kpi_dashboard.py` | ✅ Deployed | — | KPI extraction; tracks tier counts over time |
| `auto_promote_tier.py` | ✅ Deployed | — | Dry-run stub for tier promotion (human review required) |
| `auto_append_accountability.py` | ✅ Deployed | — | Auto-appends W-NNN rows to accountability report |
| SQLiteMemory (STM/LTM) | ✅ Active | — | `cli_api_server.py` — stm_entries + ltm_entries tables |
| OODA Loop API | ✅ Active | — | `POST /api/ooda/process`, `GET /api/ooda/metrics` |
| xterm.js PTY Terminal | ✅ Active | — | `XtermTerminal.tsx` — real PTY via WebSocket |
| Semgrep policies | ✅ Active | — | `.codex/policies/semgrep/` — SOFT enforcement rules |

---

## 🔴 Known Gaps & Improvement Areas

### Documentation Gaps

| Area | Gap | Priority | Owner |
|------|-----|:--------:|-------|
| `docs/AGENTIC_REPO_SYSTEM_GUIDE.md` | Section 9 CI workflows table missing `embedding-index-rebuild.yml` as Tier-1 (promoted from Tier-2 in PR #3448) | Medium | next agent session |
| `docs/audits/WORKFLOW_COMPLIANCE_MATRIX.md` | Generated at Phase 0 against 91 workflows; updated to 96 at Phase 7 | Low | complete |
| `docs/arch/ADR-*.md` | 5 ADRs written but not linked from system guide Section 12 | Medium | next agent session |
| `docs/SOFT_TO_GROUNDED_RELEASE_NOTES.md` | Does not reference PR #3477/#3478 final polish items (handoff protocol fix, R-12 hardening) | Low | next agent session |
| `.github/copilot-prompts/active/` | PR-3474/3477/3478 followup prompts have placeholder validation commands | Low | resolved in PR #3474 (reviewer comment) |
| `CODEX_MANIFEST.json` | Must be regenerated before any PR that introduces >24h gap from last generation | High | pre-merge checklist |

### Process Transparency Gaps

| Area | Gap | Priority | Recommended Fix |
|------|-----|:--------:|-----------------|
| CI failure classification | `iterative-self-healing-ci.yml` classifies failure as "unknown" pattern for pre-commit validation failures | High | Add `pre-commit-failure` pattern to `.codex/patterns/ci_failure_patterns.yaml` |
| `actionlint-audit.yml` | `admin_setup_verification.yml` has persistent SC2086/SC2129 shellcheck findings (pre-existing, not from this PR) | Medium | Quote variables in shell steps of `admin_setup_verification.yml` lines 57/107 |
| FAISS index seeding | CI only commits `codex_index_meta.json`; `.faiss` binary not in CI path; first-run agents get keyword fallback | Medium | Trigger `embedding-index-rebuild.yml` manually after merge; document fallback behavior |
| `auto_promote_tier.py` | Not wired into chatops `/copilot tier-promote` command | Medium | Wire into `chatops_copilot_trigger.yml` |
| D activation checklist | No formal checklist documenting what a human admin must do to activate D model | High | Create `docs/admin/D_ACTIVATION_CHECKLIST.md` |

### Security Items

| Item | Status | PR |
|------|:------:|-----|
| R-12: `sanitize_for_injection` budget guard | ✅ Done | PR #3478 |
| CVE-2025-55319 manifest integrity | ✅ Done | Phase 1 |
| CVE-2025-61260 field allowlist | ✅ Done | Phase 1 |
| Bandit B310 HTTPS-only URL scheme validation | ✅ Done | PR (QA walkthrough) |
| `admin_setup_verification.yml` SC2086 shellcheck | ⚠️ Open | pre-existing |

---

## 🗺️ Next Milestones (Updated 2026-03-30 — S230)

| Priority | Task | Estimated Effort | Status |
|:--------:|------|:----------------:|:------:|
| 🔴 High | Create `docs/admin/D_ACTIVATION_CHECKLIST.md` — formal steps for human to activate D model | 1h | ⏳ Pending · **Plan: P5-A** |
| 🔴 High | Trigger `embedding-index-rebuild.yml` automatically post-merge to seed FAISS in CI | 5min | ⏳ Pending · **Plan: P5-B** |
| 🔴 High | Reduce TTL in `COPILOT_ACTIVE_SESSION` from 4h → 1h to shorten max queue-wait time | 30min | ⏳ Pending · **Plan: P5-C** |
| 🟡 Medium | Fix SC2086/SC2129 in `admin_setup_verification.yml` to clear actionlint-audit | 30min | ⏳ Pending · **Plan: P5-D** |
| 🟡 Medium | Add `pre-commit-failure` pattern to `.codex/patterns/ci_failure_patterns.yaml` | 20min | ⏳ Pending · **Plan: P5-E** |
| 🟡 Medium | Wire `auto_promote_tier.py` into chatops (`/copilot tier-promote`) | 2h | ⏳ Pending · **Plan: P5-F** |
| 🟡 Medium | Link 5 ADRs from `docs/AGENTIC_REPO_SYSTEM_GUIDE.md` Section 12 | 20min | ⏳ Pending · **Plan: P5-G** |
| 🟡 Medium | Complete Sprint 2: identify top-3 unknown CI patterns; add to `collect_telemetry.py` | 1h | ⏳ Pending · **Plan: P5-H** |
| 🟢 Low | Refresh `docs/audits/WORKFLOW_COMPLIANCE_MATRIX.md` against current workflow count | 30min | ⏳ Pending |
| 🟢 Low | Update `docs/SOFT_TO_GROUNDED_RELEASE_NOTES.md` with PR #3477/#3478 polish items | 30min | ⏳ Pending |

> **📋 Full implementation detail for all P5-A–H items:**  
> `.codex/plans/pr_lifecycle_improvements.md` §Priority 5 — complete specification with
> CB layer mapping, file locations, implementation guides, and verification commands.
> Start any future session by loading that document.

---

## 📊 KPI Snapshot (2026-03-30 — S230)

| KPI | Baseline (Phase 0) | S230 | S293 | Target |
|-----|:-----------------:|:----:|:----:|:------:|
| Total registered agents | 128 | 153 | 153 | 153 ✅ |
| GROUNDED agents | 0 | 8 | 8 | ≥8 ✅ |
| PARTIAL agents | 128 | 145 | 145 | — |
| SOFT agents | 128 | 0 | 0 | ≤2 ✅ |
| Structured handoff agents | 0 | 14+ | 14+ | top-20 |
| Tier-1 CI gates | 0 | 6 | 6 | ≥5 ✅ |
| E→D gate score | 0/5 | 5/5 | 5/5 | 5/5 ✅ |
| CI pre-commit pass rate | unknown | ✅ passing | ✅ passing | passing |
| FAISS corpus | not built | built (keyword fallback) | built (keyword fallback) | seeded in CI |
| Readiness audit score | 68/100 | 100/100 | 100/100 | 100/100 ✅ |
| Session-gate queue strandage | ❌ Infinite TTL wait | ✅ Fixed (S230) | ✅ Fixed | Zero stranded |
| Cross-PR ci-rescue contamination | ❌ prs[0] bug | ✅ Fixed (S230) | ✅ Fixed | Zero mis-routes |
| S221 guard rescue-marker coverage | ❌ `ci-rescue-sha` not matched | — | ✅ Fixed (S293) | 100% markers matched |
| test-rag rescue token identity | ❌ 403 PATCH on key rotation | — | ✅ Fixed (S293) | No 403 risk |
| actionlint-audit rescue identity | ❌ posted as github-actions[bot] | — | ✅ Fixed (S293) | Posted as @mbaetiong |
| Open improvement plan items | — | — | 21 📋 Planned | 0 Planned |

---

## 📋 Work Item Log (abbreviated — full log in `AGENT_ACCOUNTABILITY_REPORT.md`)

| W-ID | PR | Summary | Status |
|------|----|---------|:------:|
| W-071–W-075 | Phase 0 | Workflow compliance scan, agent frequency audit, E→D map | ✅ |
| W-076–W-078 | PR #3477 | CI failure triage, GROUNDED handoff fix, CHANGELOG REQ-5 | ✅ |
| W-079–W-082 | PR #3478 | E→D C3 fix, pre-commit fixes, docs sync, R-12 hardening | ✅ |
| W-083 | PR #3474 | EOF newline fix, detect-secrets baseline, docs staleness fixes | ✅ |
| W-084–W-086 | PR #3790 (S227–S228) | CI rescue attribution, race-condition hardening, comment-review gate (REQ-13), session concurrency gate, workflow execution checklist | ✅ |
| W-087–W-089 | PR #3790 (S230) | Cross-PR contamination fix (ci_rescue.py `find_pr_for_run`), session-gate stale-TTL queue release, latency metric + pending gauge in check_pr_comments.py | ✅ |
| W-090–W-094 | PR #3854 (S293) | S221 guard `ci-rescue-sha` regex fix (P1-A), test-rag SHA-scoped marker (P1-B), actionlint-audit github-token (P1-C), SC2269 removal (P1-D), PR lifecycle improvement plan created with CB cross-reference (25 items, P1–P5) | ✅ |
| W-095–W-099 | PR #3854 (S294) | Unified rescue-comment upsert system: `scripts/ci/post_rescue_comment.py` canonical script; `migrate_rescue_comments.py` batch migrator; all 66 PR-triggered + 5 push-triggered workflows standardised to single SHA-scoped marker `<!-- ci-rescue-sha:{pr}:{sha} -->`; RAG coverage boost (chunker + pipeline tests: 28→44 test methods each); accountability + CB status updated | ✅ |

*For W-001–W-070 see `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md`.*

---

*Auto-maintained by agent sessions per REQ-4. Update after each PR touching agentic infrastructure.*
