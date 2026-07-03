# 🎯 PHASE 8 — WORKSTREAM 2 (PLANNING) STAGING BRIEF

**Staged:** 2026-07-03T01:41Z
**Prerequisite:** Week-1 Audit Gate ✅ SATISFIED (all 4 audit reports delivered)
**Authority:** @mbaetiong (D-tier autonomy, GO CONTINUE all gates)
**Purpose:** Stage the next-session execution steps for all 4 tracks' Workstream 2
(Planning) phase, grounded in the completed Workstream 1 audit findings.

---

## 📌 GATE CONFIRMATION

| Track | WS1 Deliverable | Size | State |
|-------|-----------------|------|-------|
| 8.1 | `.codex/PHASE_8_1_DOC_AUDIT_REPORT.md` | 19 KB | ✅ |
| 8.2 | `.codex/PHASE_8_2_STRUCTURE_AUDIT.md` | 19 KB | ✅ |
| 8.3 | `.codex/PHASE_8_3_PLATFORM_AUDIT_REPORT.md` | 18 KB | ✅ |
| 8.4 | `.codex/PHASE_8_4_DEPENDENCY_AUDIT.md` | 18 KB | ✅ |

**Week-1 Audit Gate: SATISFIED.** All tracks cleared to advance to Workstream 2.

---

## 🚀 NEXT-SESSION ACTIVATION PLAN (Workstream 2 — Planning)

Deploy all 4 lead agents in parallel (background mode) for their planning workstream.
Each brief below is grounded in the specific findings from its track's audit report.

### ▶ Track 8.1 — WS 8.1.2 Remediation Planning
**Agent:** unified-doc-agent · **Supporting:** link-validator-agent, doc-freshness-checker, documentation-consolidator

**Inputs from audit (P0/P1 to resolve in planning):**
- **P0 provenance gap:** git history is single-day → freshness gating cannot rely on git mtime.
  Planning must define an alternative freshness signal (content-embedded date front-matter
  or a manifest-tracked `last_reviewed` field).
- **~47% content-stale** and **1,547 report-sprawl files** → planning must set consolidation
  scope and an archival policy for PHASE/WAVE/GATE reports.
- **~9.4% broken links** → planning must prioritize the missing `TERMINOLOGY_GLOSSARY.md`,
  moved `.py` targets, and template placeholders.

**Deliverables:** `.codex/PHASE_8_1_REMEDIATION_PLAN.md`, `.codex/PHASE_8_1_DOC_OWNERSHIP_MATRIX.md`, `.codex/PHASE_8_1_UPDATE_CADENCE.md`

---

### ▶ Track 8.2 — WS 8.2.2 Cleanup Strategy & Planning
**Agent:** repository-organization-agent · **Supporting:** repository-hygiene-agent, root-organizer-agent, reference-updater-agent

**Inputs from audit (highest-impact quick wins to plan):**
- **Committed venvs** (`venv_test/` 511, `.venv_ci/` 202 incl. binaries) → plan safe untrack +
  `.gitignore` hardening (largest single reduction; ~715 files).
- **`.codex/` = 25% of repo / 866 top-level PHASE reports** → plan an archival taxonomy
  (`.codex/archive/phase-reports/`) with an index, coordinated with Track 8.1 consolidation.
- **205 loose root files** → plan root-declutter batches with reference updates.
- **7 config-directory roots** → plan consolidation strategy + rollback procedures.

**Deliverables:** `.codex/PHASE_8_2_CLEANUP_STRATEGY.md`, `.codex/PHASE_8_2_DIRECTORY_STANDARDS.md`, `.codex/PHASE_8_2_CLEANUP_PHASES.md`

---

### ▶ Track 8.3 — WS 8.3.2 Windows Compatibility Matrix
**Agent:** cross-platform-filename-validator · **Supporting:** workflow-ci-fixer, ci-testing-agent

**Inputs from audit (matrix must rank these):**
- **🔴 BLOCKING: 13 case-collision groups (28 files)** → matrix must sequence de-collision
  with reference updates (top priority; coordinate with Track 8.1/8.2 doc moves).
- **🟠 HIGH: inactive `.gitattributes`** → matrix must plan a root `.gitattributes` (fastest
  high-impact fix; protects 216 bash scripts from CRLF corruption).
- **44 repo-root hardcodes / 93 `/tmp` hardcodes / 15 symlinks** → rank by blast radius.
- Read-only workflow-config compatibility pass (deferred from WS1 per no-workflow-edit rule).

**Deliverables:** `.codex/PHASE_8_3_COMPATIBILITY_MATRIX.md`, `.codex/PHASE_8_3_REMEDIATION_PRIORITY.md`

---

### ▶ Track 8.4 — WS 8.4.2 Standardization & Lock Files
**Agent:** packaging-validation-agent · **Supporting:** dependency-conflict-agent, unified-security-scanner, dependency-security-review-agent

**Inputs from audit (resolve the 3 hard conflicts first):**
1. **pytest-cov** `==7.0.0` vs `<6.0.0` cap → choose a single satisfiable version.
2. **pytest floor** vs CVE-2025-71176 (`>=9.0.3`) → reconcile dev/agent floors.
3. **pydantic/fastapi v1-vs-v2** split in `docker.txt` → align to the v2 stack.
- **18 unpinned deps** (14 in dev.txt) → define pinning strategy.
- **Lock-file gaps** → plan compiled locks for uncovered surfaces; reconcile overlapping
  `uv.lock` / `requirements/lock.txt` strategies.
- Run **live GH Advisory DB** vulnerability scan on flagged candidates.

**Deliverables:** Lock files, `.codex/PHASE_8_4_DEPENDENCY_STRATEGY.md`

---

## 🔗 CROSS-TRACK COORDINATION NOTES

- **8.1 ↔ 8.2:** Report-sprawl consolidation (8.1) and `.codex/` archival (8.2) overlap —
  plan a shared archival taxonomy and single index to avoid double-moves.
- **8.2 ↔ 8.3:** Directory restructuring (8.2) and case-collision de-duplication (8.3) both
  move/rename docs — sequence 8.3 de-collision **before** 8.2 bulk moves to avoid churn.
- **8.3 root `.gitattributes`:** touches repo-wide line endings — coordinate timing with any
  large 8.2 file moves to keep diffs reviewable.

---

## 🗓️ TIMELINE ALIGNMENT

| Milestone | Date | Gate |
|-----------|------|------|
| Week-1 Audit | 2026-07-10 | ✅ Met early (2026-07-03) |
| Week 2-3 Planning | 2026-07-17 | 4 planning deliverables ready |
| Week-5 Critical Fixes | 2026-07-31 | All tracks 50%+ |
| Campaign Completion | 2026-08-30 | 100% + automation |

**Status:** Campaign is **ahead of schedule** — Week-1 audit gate satisfied on Day 1.

---

**Next Action:** In the next session, deploy the 4 planning-phase agents in parallel per the
briefs above. All decision gates remain pre-approved (GO CONTINUE).

**Author:** Phase 8 Campaign Coordinator (Copilot Agent)
**Last Updated:** 2026-07-03T01:41Z
