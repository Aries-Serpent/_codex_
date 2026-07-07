# 📋 PHASE 8.1 WORKSTREAM 2 — DOCUMENTATION REMEDIATION PLAN

**Track:** 8.1 — Documentation Remediation  
**Authority:** @mbaetiong (D-tier autonomous)  
**Workstream:** 8.1.2 — Remediation Planning (Weeks 2-5)  
**Status:** 🟢 ACTIVE  
**Generated:** 2026-07-07T14:26:35Z  
**Version:** 1.0  

---

## 1. EXECUTIVE SUMMARY

This document translates the **PHASE_8_1_DOC_AUDIT_REPORT** findings into a phased, sequenced remediation approach for documentation quality, freshness, and link integrity. The plan spans **4 weeks** (WS2 planning + WS3 execution) and addresses three critical issues:

1. **P0 Provenance Gap** — No usable git history; requires alternative freshness signal
2. **P1 Broken Links** — ~9.4% broken relative links; prioritized by user-impact
3. **P2 Stale Content + Report Sprawl** — 47% of corpus stale; 1,547 PHASE/WAVE/GATE reports need consolidation

---

## 2. PROBLEM RESTATEMENT

### 2.1 Scope & Scale
- **7,411 Markdown files** across 9 major directories
- **~3,463 files (~47%)** contain pre-2026-04-03 embedded dates → stale content proxy
- **~1,547 PHASE_/WAVE_/GATE_ reports** + 656 REPORT docs → point-in-time sprawl
- **~9.4% broken relative links** (121/1,285 sampled; true rate likely lower after code-fence filtering)
- **224 README + 126 INDEX duplicates** → no single source of truth

### 2.2 Root Cause Analysis

| Issue | Root Cause | Impact |
|-------|-----------|--------|
| No freshness gating possible | Git history squashed to 3 commits (2026-07-03) → all mtimes uniform | Can't automate "last reviewed" checks; CI gate unmeasurable |
| Broken links proliferate | Code moves/deletions not tracked in docs; templates committed as live | Users hit 404s; loss of credibility |
| Report sprawl unchecked | Point-in-time reports archived inline, never consolidated | Discovery collapse; ~51% of corpus is `.codex/` machine output |
| Duplicate basenames | No architectural policy; each folder re-documents itself | Case-fs breakage; navigation chaos |

### 2.3 User-Facing Impact
- **Readability crisis:** Users land on stale guidance (47% of corpus); no way to know if content is current
- **Correctness gap:** Broken links force manual search; code-doc drift accumulates
- **Trust erosion:** 224 READMEs + 1,547 report files signal poor governance to new contributors

---

## 3. TARGETED REMEDIATION SCOPE (WS2–WS3)

### 3.1 "User-Facing" vs. "Historical" Sets (P0 Enabler)

To avoid overwhelming remediation with immutable historical reports, we partition the corpus:

#### **Tier 1: User-Facing (Remediation scope)**
- `README.md` (root only; 1 canonical)
- `docs/` subdirectory (all; esp. `guides/`, `reference/`, `admin/`, `index.md`)
- `.github/agents/` — agent specifications & copilot prompts
- `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`, `AGENTS.md` (root canonical set)

**SLA:**
- ✅ 0 broken links
- ✅ Freshness ≤ 90 days (via new signal: see §4.2)
- ✅ Quality score ≥ 0.75 (accuracy, completeness, structure)

#### **Tier 2: Historical (Excluded from SLA)**
- `.codex/archive/` — all archived reports
- `reports/`, `archive/` directories
- All `PHASE_*/WAVE_*/GATE_*` prefixed files
- All dated snapshots (`*REPORT*`, `*SUMMARY*`, `*FINAL*`, `*COMPLETION*` docs)

**Treatment:** Consolidate into dated hierarchies; no link validation; no freshness gate.

### 3.2 Audit-to-Remediation Mapping

| Audit Finding | Remediation | Owner | Priority | Week |
|----------------|-------------|-------|----------|------|
| P0: No git provenance | Design + implement freshness signal (§4.2) | unified-doc-agent | P0 | W2 |
| P1: ~9.4% broken links | Full validator pass + prioritized fixing | link-validator-agent | P1 | W2–W3 |
| P2: 1,547 PHASE_*/WAVE_*/* reports | Consolidate into `.codex/archive/` hierarchy | ci-pattern-guardian | P2 | W3–W4 |
| P2: 224 READMEs / 126 INDEXes | Rationalize; resolve casing collisions | repository-organization-agent | P2 | W4 |
| P2: 120 root-level clutter | Move to archive; leave ~6 canonical | documentation-consolidator | P2 | W4 |
| Missing `TERMINOLOGY_GLOSSARY.md` | Create stub + map glossary links | terminology-consistency-agent | P1 | W2 |
| Template placeholders (`PLAN_TITLE.md`) | Audit + remove/fix | documentation-consolidator | P2 | W3 |
| 41 stub docs; 194 `.txt` reports | Delete/archive | repository-hygiene-agent | P3 | W5 |

---

## 4. PHASED EXECUTION ROADMAP (Weeks 2–5)

### Week 2: Enablers & P1 Critical Fixes

**Goal:** Unlock automation; fix high-impact broken links; design freshness system.

#### **Task 2.1: P0 Freshness Signal Design** (unified-doc-agent)
**Deliverable:** `.codex/PHASE_8_1_UPDATE_CADENCE.md` (detailed in separate doc; summarized below)

- **Option A (Recommended):** Front-matter `last_reviewed:` metadata in every user-facing doc
  - Format: YAML front-matter block at doc start:
    ```yaml
    ---
    last_reviewed: 2026-07-07
    owner: @agent-name
    review_cadence: quarterly
    ---
    ```
  - CI gate: Compare `last_reviewed` date to current date; warn if > 90 days
  - Governance: Documentation owners commit to quarterly reviews (§4.2 detailed plan)

- **Option B:** Manifest-tracked review dates
  - Single `.codex/DOC_FRESHNESS_MANIFEST.json` tracking all user-facing docs + last review
  - Easier bulk management; harder to enforce per-doc responsibility

- **Recommendation:** Use Option A + manifest as index; front-matter is self-documenting

#### **Task 2.2: Terminology Glossary Creation** (terminology-consistency-agent)
**Deliverable:** `docs/TERMINOLOGY_GLOSSARY.md` (new; ~5–10 KB stub)

- Audit all doc links referencing glossary
- Extract terminology from codebase (`src/`, `docs/`) via semantic search
- Create glossary stub with sections:
  - Agent terminology (agent types, autonomy tiers, etc.)
  - Infrastructure (CI/CD, K8s, caching, etc.)
  - Testing (flaky, P19, shadow imports, etc.)
  - Compliance & governance (D-tier, D-CAPABLE, gating, etc.)
- Cross-reference links in existing docs (TERMINOLOGY_CONSISTENCY_*.md, etc.)

#### **Task 2.3: Full Link Validation Pass + Prioritization** (link-validator-agent)
**Deliverable:** `artifacts/PHASE_8_1_LINK_VALIDATION_FULL.json` (detailed report)

- Run full validator on all 7,411 docs (unlike WS1 sample)
- Include `.github/agents/` (excluded in audit sample — §4.2 caveat)
- Implement code-fence filtering to reduce false positives
- Output format:
  ```json
  {
    "summary": { "total_links": ..., "broken": ..., "rate": ... },
    "by_tier": {
      "tier_1_user_facing": { "broken": [...], "priority": "P1" },
      "tier_2_historical": { "broken": [...], "priority": "P2" }
    }
  }
  ```
- Categorize by remediation complexity:
  - **P1a (Tier 1, quick fixes):** Typo links, trivial path corrections
  - **P1b (Tier 1, code-drift):** Links to moved `.py` files; requires code search
  - **P1c (Tier 1, missing content):** Links to non-existent reference docs (e.g., `TERMINOLOGY_GLOSSARY.md` once created)
  - **P2 (Tier 2, defer):** Historical reports; no SLA
  - **FP (False positives):** Code-fence content; template syntax; requires manual review

#### **Task 2.4: P1 Link Remediation (Week 2 Quick Wins)** (link-validator-agent + doc-refactor-test-agent)
**Deliverable:** PRs for P1a + P1c fixes; remediation status report

- **P1a fixes:** Batch-fix typos, path corrections (~20–30 links, <2 hours)
  - Example: `../src/codex/ci/cache_manager.py` → correct actual path via grep
- **P1c fixes:** Redirect references to newly created `TERMINOLOGY_GLOSSARY.md`
  - Examples: `TERMINOLOGY_CONSISTENCY_AUDIT_REPORT.md` → now links to glossary (live target)
- **P1b deferred:** Document moving source files (Track 8.3) → revisit in Week 4
- Test all fixed links locally before commit

---

### Week 3: Consolidation Phase 1 + Secondary Link Fixes

**Goal:** Archive point-in-time reports; fix P1b code-drift links; consolidate first wave of READMEs.

#### **Task 3.1: Report Consolidation Strategy** (ci-pattern-guardian)
**Deliverable:** `.codex/PHASE_8_1_REPORT_CONSOLIDATION_MANIFEST.md`

- Define consolidation hierarchy for `.codex/archive/`:
  ```
  .codex/archive/
  ├── phase-reports/
  │   ├── phase-01-10/       (PHASE_1_* through PHASE_10_* reports)
  │   │   ├── index.md       (one living index per phase)
  │   │   └── snapshots/     (point-in-time reports, sorted by date)
  │   ├── phase-11-20/
  │   ├── waves/             (WAVE_* reports)
  │   └── gates/             (GATE_* reports)
  ├── agent-reports/         (AGENT_* docs)
  └── timestamp-index.json   (manifest of all archived with date, topic)
  ```
- Identify 1,547 files for consolidation; group by phase/wave/gate prefix
- Plan batch moves: `mv PHASE_7_*.md .codex/archive/phase-reports/phase-01-10/snapshots/`
- Create living indexes (`phase-reports/phase-01-10/index.md`) that replace 1,547 snapshots

#### **Task 3.2: Execute First Wave of Report Consolidation** (ci-pattern-guardian + repository-organization-agent)
**Deliverable:** Completed moves for Phase 7, 8, 9 (est. 500+ files)

- Consolidate all `PHASE_7_*` → `.codex/archive/phase-reports/phase-01-10/snapshots/`
- Consolidate all `PHASE_8_*` → `.codex/archive/phase-reports/phase-01-10/snapshots/`
- Consolidate all `PHASE_9_*` → `.codex/archive/phase-reports/phase-01-10/snapshots/`
- Create phase-level index MD files replacing the point-in-time sprawl
- Update any cross-references in Tier 1 docs to point to new archive paths
- Validate that no Tier 1 docs break (re-run link validator on `docs/`, `.github/agents/`)

#### **Task 3.3: P1b Link Fixes (Code Drift)** (link-validator-agent + Track 8.3 coordination)
**Deliverable:** PRs for code-moved fixes; coordination notes for Track 8.3

- Wait for Track 8.3 (doc renames) to provide mapping of old → new file paths
- For each P1b broken link (code-moved targets):
  - Search codebase (`src/codex/`, `scripts/`) to find current path
  - Update doc link
  - Add comment: "Code moved in Track 8.3; updated link"
- Flag links that require code renaming as dependencies for Track 8.3

---

### Week 4: Consolidation Phase 2 + Duplicate Resolution

**Goal:** Finalize README/INDEX consolidation; resolve casing collisions; de-clutter root.

#### **Task 4.1: README/INDEX Audit & Rationalization** (repository-organization-agent)
**Deliverable:** `.codex/PHASE_8_1_README_INDEX_RATIONALIZATION.md`

- Audit the **224 READMEs** and **126 INDEXes**
- Identify which folders legitimately need an index:
  - Tier 1 docs: Yes, consolidate to single `index.md` per directory
  - Major subdivisions (e.g., `docs/guides/`, `docs/reference/`): Yes, index
  - Deep nesting (e.g., `docs/admin/policies/settings/`): No, delete; link to parent
- Resolve casing collisions:
  - Identify `ARCHITECTURE.md` vs `architecture.md` pairs
  - Standardize to lowercase for consistency with MkDocs conventions
  - Create redirects/aliases or consolidate into single file
- Delete truly redundant READMEs (e.g., in single-file folders)

#### **Task 4.2: Execute README/INDEX Consolidation** (repository-organization-agent)
**Deliverable:** Consolidated file structure; casing normalized

- Batch consolidate 100–150 redundant READMEs/INDEXes
- Resolve 5+ casing collisions (ARCHITECTURE.md → architecture.md + aliases)
- Re-validate Tier 1 links (should be zero impact if consolidation is within Tier 2)
- Test MkDocs build: `mkdocs build` → should succeed

#### **Task 4.3: Root-Level De-Clutter** (documentation-consolidator)
**Deliverable:** Cleaned root directory; archive manifest

- Audit 120 root-level `.md`/`.txt` files
- **Keep only (6 canonical):**
  - `README.md`
  - `CONTRIBUTING.md`
  - `SECURITY.md`
  - `CHANGELOG.md`
  - `CODE_OF_CONDUCT.md`
  - `AGENTS.md`
- **Move remaining 114 files** to `.codex/archive/` or `reports/`:
  - `PHASE_*` → `.codex/archive/phase-reports/`
  - `SECURITY_*` → `.codex/archive/security-reports/` (or `docs/security/`)
  - `TERMINOLOGY_*`, `AUDIT_*` → `.codex/archive/audits/`
  - One-off reports → `.codex/archive/miscellaneous/`
- Create `.codex/ROOT_DIRECTORY_MANIFEST.md` listing what moved where

---

### Week 5: Validation, Hygiene, & Handoff to WS3

**Goal:** Verify all remediations; clean up stubs; finalize for WS3 execution.

#### **Task 5.1: Comprehensive Link Validation (Post-Consolidation)** (link-validator-agent)
**Deliverable:** `artifacts/PHASE_8_1_LINK_VALIDATION_FINAL.json`

- Re-run full link validator after all consolidations
- Target: **0 broken links in Tier 1** (`docs/`, `.github/agents/`, root canonical)
- Tier 2: Acceptable rate (historical reports); flag only critical dead links
- Generate summary: "Tier 1 links: X/X valid (100%); Tier 2: X/X (Y%)"

#### **Task 5.2: Freshness Check (Manual Sampling)** (unified-doc-agent)
**Deliverable:** Sample audit; refresh critical docs if needed

- Sample 20 Tier 1 docs across `docs/guides/`, `docs/reference/`, `docs/admin/`
- Verify content accuracy against current codebase state
- Update `last_reviewed:` frontmatter for any docs updated in Week 2–4
- Document any remaining stale sections requiring future refresh

#### **Task 5.3: Stub Cleanup & Legacy Archive** (repository-hygiene-agent)
**Deliverable:** Deletion/archive of 41 stubs + 194 `.txt` files

- Delete 41 stub docs (< 200 bytes; likely empty placeholders)
- Convert or archive 194 legacy `.txt` reports:
  - If content is valuable: convert to `.md` in `.codex/archive/legacy/`
  - If obsolete: delete
- Verify no Tier 1 docs link to deleted stubs

#### **Task 5.4: WS3 Execution Readiness Handoff** (unified-doc-agent)
**Deliverable:** `.codex/PHASE_8_1_WS3_HANDOFF_CHECKLIST.md`

- Compile all WS2 outputs: remediation PRs, consolidation manifest, freshness signal design
- Create checklist of WS3 execution tasks:
  - Merge WS2 PRs (link fixes, consolidations, cleanups)
  - Implement freshness signal system (deploy CI gate for `last_reviewed` checks)
  - Conduct final QA on all Tier 1 docs
  - Publish remediation report to stakeholders
- Flag any blockers or dependencies for WS3 leads

---

## 5. CRITICAL DEPENDENCIES & COORDINATION

### 5.1 Track 8.2 Coordination (Cleanup)
**Overlap:** Archive structure, manifest format

- Track 8.2 will also clean up `.codex/` root files; coordinate taxonomy
- **Sync point:** Week 3 consolidation manifest (§3.1) defines shared hierarchy
- **Handoff:** WS2 documents what was moved; Track 8.2 ensures CI/automation aligns

### 5.2 Track 8.3 Coordination (Doc Renames)
**Dependency:** Code-file moves → link remediation

- WS2 identifies P1b (code-drift) broken links but **defers remediation** until Track 8.3 provides file-move mapping
- **Handoff point:** Week 3 → WS3 Phase (Week 5) finalizes P1b fixes once code locations known
- **Constraint:** Do not rename/move files that Tier 1 docs link to without updating links first

### 5.3 Unified Documentation Agent Lifecycle
**Scope:** This plan integrates findings from `unified-doc-agent` (merged from doc-quality, doc-freshness, link-validator, documentation-consolidator)

- All tasks below should be **delegated to appropriate sub-agents** based on specialization
- Unified agent coordinates sequence and ensures dependencies are honored

---

## 6. SUCCESS CRITERIA & METRICS

### 6.1 WS2 Planning Deliverables (Current)
- ✅ `.codex/PHASE_8_1_REMEDIATION_PLAN.md` (this document)
- ✅ `.codex/PHASE_8_1_DOC_OWNERSHIP_MATRIX.md` (separate document)
- ✅ `.codex/PHASE_8_1_UPDATE_CADENCE.md` (separate document)

### 6.2 WS3 Execution Metrics (to be measured post-WS2)

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Link Integrity** | 0 broken links in Tier 1 | `link-validator-agent` final pass |
| **Freshness System** | 100% of Tier 1 docs have `last_reviewed:` | grep for YAML front-matter |
| **Freshness Compliance** | ≥95% of docs reviewed ≤90 days | `grep last_reviewed` + date arithmetic |
| **Report Consolidation** | 1,500+ PHASE_*/WAVE_* moved to archive | `find .codex/archive/ \| wc -l` |
| **Duplicate Reduction** | <50 READMEs, <25 INDEXes | `find -iname readme.md \| wc -l` |
| **Root De-Clutter** | ≤6 canonical + archive manifest | `ls /*.md \| wc -l` |
| **Quality Score** | ≥0.75 on sampled Tier 1 docs | doc-quality-agent sampling |
| **Build Success** | `mkdocs build` succeeds; zero warnings | CI gate output |

---

## 7. RISK MITIGATION & FALLBACK PLANS

### 7.1 Link Validator False Positives
**Risk:** Automated link checker flags code-fence content as broken links

**Mitigation:**
- Implement code-fence filtering in validator (WS1 identified issue; implement in WS2 Task 2.3)
- Maintain manual review whitelist for known FPs (regex patterns, blob: URLs, etc.)
- Threshold: Accept up to 10% FP rate; manual review before declaring "zero broken"

### 7.2 Consolidation Cascades (Breaking References)
**Risk:** Moving 1,547 PHASE_*/WAVE_* files breaks links within Tier 2 (historical)

**Mitigation:**
- Consolidation changes are **within Tier 2 only** (historical docs)
- **Prerequisite:** Pre-consolidation audit of all intra-Tier-2 links
- If links break: Create `.codex/archive/CONSOLIDATION_REDIRECT_MAP.json` mapping old → new paths
- Acceptance: Tier 2 docs are historical; broken intra-Tier-2 links are lower priority

### 7.3 Track 8.3 Dependency Slip
**Risk:** Code file moves (Track 8.3) delayed; P1b link fixes blocked

**Mitigation:**
- WS2 completes P1a (typos) + P1c (new content) in Week 2; P1b deferred
- By Week 5, P1b becomes a **WS3 Phase task** with dependency on Track 8.3 output
- Contingency: If Track 8.3 slips, P1b links can be marked as "awaiting code move mapping" in final report

### 7.4 Freshness Signal Adoption Friction
**Risk:** Contributors forget to update `last_reviewed:` metadata

**Mitigation:**
- Make YAML front-matter **mandatory** in PR template for docs; CI check warns if missing
- Quarterly review cadence with reminders (tracked in `DOC_FRESHNESS_MANIFEST.json`)
- Build trust early: Show that system works in WS3 (prove value before enforcement)

---

## 8. SUCCESS EXAMPLE (Post-WS2, ready for WS3)

After WS2 planning is complete, the codebase should meet these criteria:

```
✅ Freshness system designed and documented (.codex/PHASE_8_1_UPDATE_CADENCE.md)
✅ Broken links prioritized and categorized (artifacts/PHASE_8_1_LINK_VALIDATION_FULL.json)
✅ Consolidation manifest ready (phase-reports hierarchy defined)
✅ Ownership matrix assigned (each critical doc has owner + review cadence)
✅ WS3 tasks itemized and sequenced (phased execution roadmap ready)
✅ Coordination notes with Track 8.2, 8.3 documented
✅ No immediate blockers; dependencies identified
```

When WS3 execution begins, teams can:
- **Link Validator Agent:** Execute full validator pass + P1a/P1c fixes
- **CI Pattern Guardian:** Consolidate reports into hierarchy
- **Repository Organization Agent:** De-clutter + resolve duplicates
- **Unified Documentation Agent:** Coordinate, validate, and hand off to stakeholders

---

## 9. APPENDIX: QUICK-START CHECKLIST FOR WS3

### **Week 2 Sprint (Link Validation & P1 Fixes)**
- [ ] Task 2.1: Finalize freshness signal design (`.codex/PHASE_8_1_UPDATE_CADENCE.md`)
- [ ] Task 2.2: Create `docs/TERMINOLOGY_GLOSSARY.md` stub
- [ ] Task 2.3: Run full link validator; output `artifacts/PHASE_8_1_LINK_VALIDATION_FULL.json`
- [ ] Task 2.4: Fix P1a (typos) + P1c (glossary refs); submit PRs

### **Week 3 Sprint (Report Consolidation + Link Fixes)**
- [ ] Task 3.1: Create `.codex/PHASE_8_1_REPORT_CONSOLIDATION_MANIFEST.md`
- [ ] Task 3.2: Consolidate Phase 7–9 reports; create phase-level indexes
- [ ] Task 3.3: Coordinate with Track 8.3 for P1b code-drift fixes

### **Week 4 Sprint (README/INDEX Consolidation)**
- [ ] Task 4.1: Audit & rationalize READMEs/INDEXes
- [ ] Task 4.2: Execute consolidation; normalize casing; test MkDocs build
- [ ] Task 4.3: De-clutter root; move 114 files to archive; create manifest

### **Week 5 Sprint (Validation & Handoff)**
- [ ] Task 5.1: Run final link validation; confirm 0 broken in Tier 1
- [ ] Task 5.2: Sample-audit Tier 1 docs for freshness; update metadata
- [ ] Task 5.3: Clean up 41 stubs + 194 `.txt` files
- [ ] Task 5.4: Create WS3 handoff checklist; notify stakeholders

---

## 10. DOCUMENT STATUS & SIGN-OFF

| Item | Status | Owner | Date |
|------|--------|-------|------|
| Audit Report (WS1) | ✅ Complete | unified-doc-agent | 2026-07-03 |
| Remediation Plan (this doc) | 🟢 ACTIVE | @mbaetiong | 2026-07-07 |
| Ownership Matrix | ⏳ In progress | unified-doc-agent | 2026-07-07 |
| Update Cadence | ⏳ In progress | unified-doc-agent | 2026-07-07 |
| **Next Step** | **WS3 Execution** | Track 8.1 leads + sub-agents | 2026-07-10 |

---

**Report Version:** 1.0  
**Last Updated:** 2026-07-07T14:26:35Z  
**Status:** 🟢 READY FOR WS3 HANDOFF  
**Escalation:** @mbaetiong (D-tier; GO CONTINUE on all gates)
