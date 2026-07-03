# 📋 PHASE 8.1 — DOCUMENTATION REMEDIATION PLAN (Workstream 8.1.2)

**Track:** 8.1 — Documentation Remediation  
**Track Lead:** unified-doc-agent  
**Authority:** @mbaetiong (D-tier autonomy, GO CONTINUE on all gates)  
**Branch:** `copilot/deploy-phase-8-agents`  
**Repository:** Aries-Serpent/_codex_  
**Generated:** 2026-07-03T02:15Z  
**Workstream:** 8.1.2 Remediation Planning (Week 1)  
**Feeds Into:** Workstream 8.1.3 (Link Fixes), 8.1.4 (Consolidation), 8.1.5 (Automation)  

---

## 1. EXECUTIVE SUMMARY

This plan operationalizes the findings from Workstream 8.1.1 (Audit Report) into a **phased, sequenced remediation strategy** targeting three critical documentation health dimensions:

| Dimension | Current State | Target State | Owner |
|-----------|---------------|-------------|-------|
| **Broken links** | ~9.4% of relative links | ≤ 0.5% (sample-based) | doc-refactor-test-agent + manual review |
| **Stale content** | ~47% (proxy) | ≤ 20% (excludes archived/reports) | terminology-consistency-agent + refresh cycle |
| **Sprawl/clutter** | 1,547 PHASE/WAVE/GATE + 120 root files | Consolidated archive + clean root | ci-health-alert-agent coordination |

The plan respects **three hard constraints:**
- P0: **No git provenance for freshness** → adopt front-matter `last_reviewed: YYYY-MM-DD` metadata
- Scope: **User-facing docs only** (docs/, .github/agents/, README.md) treated as SLA targets; reports/ and archive/ are immutable historical  
- Timeline: **8 weeks total** (Phase 8.1 = Weeks 1–2 planning; Weeks 3–8 execution + closing)

---

## 2. REMEDIATION PHASES & SEQUENCING

### Phase 8.1.2a — P0 Enablers (Weeks 1–1.5; Planning → Execution Gate)

**Goal:** Establish freshness signal + define audit scope boundary  
**Owner:** unified-doc-agent (this session)  
**Commit:** Initial config + manifest  

#### 2a.1 — Freshness Signal Adoption

**Action:** Define and seed a front-matter freshness mechanism.

| Option | Implementation | Recommendation |
|--------|----------------|-----------------|
| Front-matter metadata | Add YAML block to all `.md` files: `---`\n`last_reviewed: YYYY-MM-DD`\n`—` | ✅ **SELECT** — Portable, embeddable, detectable by grep/sed |
| External manifest | `.codex/doc-freshness-manifest.json` tracking file → `last_reviewed` date | Fallback if front-matter adoption stalls |
| Git-commit proxies | Extract per-file commit date from richer git export | Not viable (squashed history) |

**Scope boundary (critical):**
- **In-scope for freshness/link SLA:** `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `docs/`, `.github/agents/`
- **Excluded (immutable/historical):** `reports/`, `archive/`, `.codex/archive/`, `.codex/` root (report files)

**Execution substeps:**
1. Create `.codex/DOC_FRESHNESS_MANIFEST.json` with baseline `last_reviewed` dates for all in-scope docs (default: 2026-07-03)
2. Create `.codex/FRESHNESS_GATE_CONFIG.yaml` defining thresholds (90 days for general, 30 days for critical: README, docs/index.md, API reference)
3. Seed 10 representative in-scope `.md` files with front-matter `last_reviewed:` blocks (proof of concept)
4. Generate `.codex/FRESHNESS_GATE_CI_SNIPPET.yaml` for wiring into `.github/workflows/` (defer to 8.1.5)

**Definition of Done:**
- Manifest generated + committed
- Front-matter format documented in `.codex/DOC_STANDARDS.md`
- 10 PPC files tagged (proof)
- CI snippet ready for 8.1.5 integration

#### 2a.2 — Audit Scope Boundary Definition

**Action:** Explicitly mark immutable vs. mutable doc trees.

Create `.codex/DOC_AUDIT_SCOPE.md` with:
- User-facing tree = SLA targets (link, freshness, quality)
- Historical/archive tree = audited for inventory but no SLA enforcement
- Grey zone (workbench/, misc/) = best-effort

**Definition of Done:**
- `.codex/DOC_AUDIT_SCOPE.md` created and approved

---

### Phase 8.1.3 — Link Fixes (Weeks 2–3; Execution)

**Goal:** Repair ~9.4% broken relative links in user-facing docs  
**Owner:** doc-refactor-test-agent (sub-agent dispatch)  
**Output:** Link-validation report + patch PRs  

#### 2a.1 — Full Link Validator Pass

**Action:** Run comprehensive link validator across all docs (including `.github/` which was excluded from 8.1.1 sample).

```bash
# Pseudocode for 8.1.3
python scripts/doc_link_validator.py \
  --include-paths docs/ .github/agents/ . \
  --exclude-dirs .git node_modules archive reports \
  --report-format json \
  --code-fence-filter true \
  --output artifacts/doc-link-validation-PHASE8.1.3.json
```

**Expected output:** Full inventory of ~121 real broken links (post-FP filtering)

#### 2a.2 — Prioritized Link Repairs

**Priority tier (fixes in this order):**

| Tier | Target | Examples | Estimate | Owner |
|------|--------|----------|----------|-------|
| **P0** | API/code-reference links to moved `.py` files | `../src/codex/ci/cache_manager.py`, `../src/cache/redis_cache.py` | 15 links | doc-refactor-test-agent |
| **P0** | Create missing `TERMINOLOGY_GLOSSARY.md` (referenced by 3+ docs) | Create at `docs/TERMINOLOGY_GLOSSARY.md` with bootstrapped terms | 1 file | terminology-consistency-agent |
| **P1** | Template placeholders (literal links) | `PLAN_TITLE.md`, `{output_file}` pattern removes | 8–12 links | unified-doc-agent (sed) |
| **P1** | Internal doc cross-refs in user-facing set | `docs/plans/README.md` → `./plans/PLAN_TITLE.md` | 30–40 links | doc-refactor-test-agent |
| **P2** | Historical/archive refs (lower priority) | `htmlcov/index.html`, deleted coverage artifacts | 20 links | ci-failure-resolution-agent |

**Definition of Done:**
- Link-validation report published (no code-fence FPs)
- P0 + P1 links fixed (60+ fixed)
- Remaining P2 links documented in waiver list for 8.1.4

---

### Phase 8.1.4 — Report Sprawl Consolidation (Weeks 3–5; Execution)

**Goal:** Archive 1,547 PHASE/WAVE/GATE reports; de-clutter root; resolve README/INDEX duplication  
**Owner:** ci-health-alert-agent + unified-doc-agent  
**Output:** Consolidated `.codex/archive/` taxonomy + consolidated indices  

#### 2a.1 — Archival Taxonomy & Manifest

**Action:** Define a **shared archival taxonomy** for Report-sprawl (8.1.4) + `.codex/` structural archival (8.2), with a **single master index**.

**Archive structure (Phase 8.1 responsibility):**
```
.codex/archive/
├── phases/                       # Historical PHASE_* reports
│   ├── phase-1/
│   │   ├── INDEX.md             # One index per phase (consolidation)
│   │   ├── (all PHASE_1_*.md files)
│   │   └── reports.manifest.json # Manifest: { "original_path": "path", "last_reviewed": date, "relevance": "high|medium|low" }
│   ├── phase-2/
│   ├── ... phase-12/
│   └── PHASES_INDEX.md          # Master index for all phases
├── waves/                        # WAVE_* reports
│   └── WAVES_INDEX.md
├── gates/                        # GATE_* reports
│   └── GATES_INDEX.md
├── reports-by-type/             # Cross-cutting groups
│   ├── status-updates/          # SUMMARY, COMPLETION, FINAL pattern
│   ├── audits/                  # AUDIT, VALIDATION
│   ├── security/                # SECURITY_*
│   └── INDEX.md
└── ARCHIVE_MANIFEST.json        # Master registry: { "archive_id": { "original_location": "...", "consolidation_date": "2026-07-03", "access_pattern": "phase_history" } }
```

**Definition of Done:**
- Archive taxonomy YAML/JSON defined in `.codex/ARCHIVE_TAXONOMY.md`
- Manifest schema finalized (coordinates with 8.2)
- Move script/automation pseudocode written (defer execution to 8.1.4)

#### 2a.2 — Report Family Moves (Consolidation)

**Action:** Batch-move reports to archive by family.

| Family | Count | Target | Automation |
|--------|-------|--------|-----------|
| `PHASE_*` | ~791 | `.codex/archive/phases/{phase-N}/` | `git mv` script + manifest injection |
| `WAVE_*` | ~91 | `.codex/archive/waves/` | same |
| `GATE_*` | ~32 | `.codex/archive/gates/` | same |
| `*REPORT*` / `*SUMMARY*` / `*FINAL*` | ~1,545 cumulative | `.codex/archive/reports-by-type/{type}/` | categorization + mv |

**Execution substeps:**
1. Validate archive move scripts in test clone
2. Run moves in sequence (PHASE → WAVE → GATE → cross-cutting)
3. Update all internal cross-references (in `.codex/`, `docs/`)
4. Generate consolidation report (files moved, refs updated, broken links detected)

**Definition of Done:**
- Report files moved to archive (1,547 files)
- All internal references updated (grep-based search + sed replacement)
- Consolidation report generated

#### 2a.3 — Root-Directory De-clutter

**Action:** Move non-canonical root `.md` files to `.codex/archive/`.

**Canonical root entrypoints (keep):**
- `README.md`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `CHANGELOG.md`
- `CODE_OF_CONDUCT.md`
- `AGENTS.md`
- `LICENSE`

**To relocate (~80 files):**
- All `PHASE_*`, `SECURITY_*`, `SEMGREP_*`, `TERMINOLOGY_*`, `AUDIT_*`, `REMEDIATION_*` at root → `.codex/archive/reports-by-type/{type}/`
- Example: `TERMINOLOGY_CONSISTENCY_AUDIT_REPORT.md` → `.codex/archive/reports-by-type/audits/TERMINOLOGY_CONSISTENCY_AUDIT_REPORT.md`

**Definition of Done:**
- Root `.md` reduced to ~10–12 canonical files
- All moved files updated in commit message + crossref validation

#### 2a.4 — README/INDEX Rationalization

**Action:** Resolve 224 READMEs → define a **folder-indexing policy** (which folders warrant their own INDEX).

**Policy definition:**
- **Must have INDEX:** Top-level trees (docs/, .github/agents/, .codex/archive/{phases,waves,gates,reports-by-type})
- **May have INDEX:** 2nd-level subtrees (docs/guides/, docs/reference/, docs/admin/, docs/ops/)
- **No INDEX:** Leaf folders with <5 files or leaf code packages

**Execution:**
1. Enumerate all 224 READMEs + 126 INDEXes
2. Classify by necessity (keep/consolidate/delete)
3. Merge redundant ones into one per folder
4. Fix casing collisions (`ARCHITECTURE.md` vs `architecture.md` → one canonical name per folder)

**Definition of Done:**
- README/INDEX policy documented
- Duplicates consolidated to policy-compliant count (target: ~60 READMEs + 40 INDEXes)
- Casing standardized

---

### Phase 8.1.5 — Freshness Automation & CI Gate (Weeks 5–6; Execution → Closing)

**Goal:** Wire freshness + link checks into CI; establish enforcement gate  
**Owner:** unified-doc-agent + workflow-compliance-guardian  
**Output:** GitHub Actions workflow + enforcement rule  

#### 2a.1 — CI Freshness Gate

**Action:** Create `.github/workflows/doc-freshness-gate.yml` (on PR and nightly schedule).

Pseudocode:
```yaml
# doc-freshness-gate.yml
name: Documentation Freshness Gate
on:
  pull_request:
    paths: ['docs/**', '.github/agents/**', 'README.md', 'SECURITY.md', 'CONTRIBUTING.md']
  schedule:
    - cron: '0 2 * * 1'  # Weekly Monday 02:00 UTC

jobs:
  freshness-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Check freshness (front-matter last_reviewed)
        run: |
          python scripts/ci/freshness_gate.py \
            --config .codex/FRESHNESS_GATE_CONFIG.yaml \
            --report-format json \
            --fail-on-critical true
        env:
          CRITICAL_DOCS_MAX_AGE_DAYS: 30
          GENERAL_DOCS_MAX_AGE_DAYS: 90
      - name: Check link validity (cached)
        run: |
          python scripts/ci/link_validator_cached.py \
            --scope user-facing \
            --exclude-dirs .git archive reports \
            --report-format json
      - name: Report (PR comment or workflow annotation)
        if: always()
        run: |
          # Emit summary; gate failure if critical docs stale OR P0 links broken
```

**Gate behavior:**
- **Pass:** All critical docs ≤ 30 days, general docs ≤ 90 days, no broken P0 links
- **Fail (blocking):** Critical docs > 30d OR P0 broken links detected
- **Review:** Manual-review whitelist for FP link patterns

**Definition of Done:**
- Workflow YAML created in `.github/workflows/`
- Scripts `freshness_gate.py` and `link_validator_cached.py` created in `scripts/ci/`
- Tested against 5–10 sample docs
- Gate wired to `.codex/FRESHNESS_GATE_CONFIG.yaml`

#### 2a.2 — Enforcement & Escalation

**Action:** Define escalation path for gate failures.

- **Documentation leads:** Alerted on critical-doc staleness (cc: terminology-consistency-agent)
- **Broken link reports:** Posted to GitHub Discussions `Documentation-Health` category
- **Waiver process:** For FPs, documented in `.codex/LINK_VALIDATION_WHITELIST.json`

**Definition of Done:**
- Escalation rules written in `scripts/ci/` (environment variable checks)
- `.codex/LINK_VALIDATION_WHITELIST.json` created (empty initially)

---

## 3. CRITICAL DEPENDENCIES & COORDINATION

### Dependency Graph

```
8.1.2a (P0 Enablers, Weeks 1–1.5)
├── Freshness signal adoption
│   └──→ 8.1.3 (Link fixes depend on scope boundary)
│       └──→ 8.1.4 (Archive moves depend on fixed links in user-facing)
│           └──→ 8.1.5 (CI gate depends on archive structure finalized)
│
└── Scope boundary definition
    └──→ All subsequent phases
```

### Cross-Track Coordination

| Track | Overlap | Sync Point |
|-------|---------|-----------|
| **8.1 ↔ 8.2** | Archive taxonomy (report-sprawl + `.codex/` structural) | Shared `.codex/ARCHIVE_TAXONOMY.md` + unified manifest (Week 1 → finalized Week 2) |
| **8.1 ↔ 8.3** | Terminology glossary creation | Create `.codex/TERMINOLOGY_GLOSSARY.md` (8.1.3) before 8.3 terminology fixes |
| **8.1 ↔ Link Validator** | Full pass including `.github/` | Run 8.1.3 after unified-doc-agent confirms scope boundary |
| **8.1 ↔ CI Integration** | Gate wiring (8.1.5) | Workflow-compliance-guardian consulted during 8.1.5 design |

---

## 4. RESOURCE ALLOCATION & OWNERS

| Workstream | Owner(s) | Effort | Duration | Dependencies |
|-----------|----------|--------|----------|--------------|
| **8.1.2a (P0 Enablers)** | unified-doc-agent | 16 h | Weeks 1–1.5 | None (critical path) |
| **8.1.3 (Link Fixes)** | doc-refactor-test-agent | 24 h | Weeks 2–3 | 8.1.2a scope definition |
| **8.1.4 (Consolidation)** | ci-health-alert-agent (dispatch) + unified-doc-agent (execution) | 32 h | Weeks 3–5 | 8.1.3 link validation complete |
| **8.1.5 (CI Gate)** | unified-doc-agent + workflow-compliance-guardian | 20 h | Weeks 5–6 | 8.1.4 archive structure finalized |
| **Total** | **—** | **~92 h** | **6 weeks** | **Critical path: 2a → 3 → 4 → 5** |

---

## 5. DEFINITION OF "DONE" — PHASE 8.1 EXIT CRITERIA

| Criterion | Target | Status (at phase end) |
|-----------|--------|------------------|
| **Freshness signal adopted** | All in-scope docs have `last_reviewed:` or manifest entry | ✓ |
| **Broken links fixed** | P0 + P1 links (60+) fixed; P2 documented in waiver | ≤ 0.5% broken rate on validation pass | ✓ |
| **Reports consolidated** | 1,547 PHASE/WAVE/GATE files archived; <50 remain at root | ✓ |
| **Archive manifest created** | `.codex/ARCHIVE_MANIFEST.json` governs all historical refs | ✓ |
| **CI gate wired** | `.github/workflows/doc-freshness-gate.yml` deployed; blocking enforcement enabled | ✓ |
| **Ownership matrix published** | `.codex/PHASE_8_1_DOC_OWNERSHIP_MATRIX.md` defines doc owners | ✓ |
| **Update cadence published** | `.codex/PHASE_8_1_UPDATE_CADENCE.md` defines refresh frequency per doc category | ✓ |

---

## 6. RISK REGISTER

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| **Link validator FPs inflate true broken count** | High | Medium | Manual code-fence filtering; whitelist-based waiver in CI gate |
| **Scope creep in report consolidation** | Medium | High | Freeze report-move scope after Week 2; defer new categories to Phase 8.2 |
| **Front-matter adoption low (<50% coverage)** | Medium | Medium | Fallback to manifest-based tracking (external JSON); prioritize critical docs first |
| **Archive move breaks internal cross-refs** | Medium | High | Automated ref-update scripts validated in test clone before live move |
| **CI gate too aggressive (false failures)** | Low | Medium | Whitelist + manual-review escalation path; 7-day waiver for new docs |
| **Phase 8.2 (archival) timing conflict** | Low | Low | Coordinate Week 1; freeze `.codex/` structure decisions before Phase 8.2 starts |

---

## 7. SUCCESS METRICS (Weeks 6–8 + beyond)

### 6-Week Post-Closure Metrics

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| Broken link rate (user-facing) | 9.4% | ≤ 0.5% | Link validator pass (excluding waivered FPs) |
| Critical doc staleness | ~30% (proxy) | ≤ 10% | `last_reviewed:` age check (critical = docs/index.md, README.md, API ref) |
| General doc freshness | ~47% (proxy) | ≤ 25% | Front-matter age check across `docs/` + `README.md` |
| Root-level clutter | 120 files | ≤ 12 files | Filesystem count |
| Duplicate README count | 224 | ≤ 50 | Basename enumeration |
| Archive integrity | N/A | 100% (no dangling refs) | Audit against `.codex/ARCHIVE_MANIFEST.json` |
| CI gate pass rate | N/A | ≥ 90% | Workflow success rate (excludes waivered FPs) |

---

## 8. HANDOFF & ESCALATION

**Escalation points (to @mbaetiong):**
- Week 1.5: P0 enablers complete; gate @mbaetiong before proceeding to 8.1.3 (link fixes)
- Week 3 end: Link fixes complete; gate before report consolidation (scope freeze)
- Week 5 end: Archive structure finalized; gate before CI gate deployment

**Next workstream:** 8.1.6 — Post-Closure Audit (Week 8), validating all SLA targets met

---

## 9. APPENDIX: IMPLEMENTATION SCRIPTS & CONFIGS

### A. Front-Matter Template

```markdown
---
title: "Document Title"
description: "Brief description"
last_reviewed: 2026-07-03
review_frequency: 90  # days until next review due
critical: false       # critical=true triggers 30-day SLA instead of 90-day
---

# Document Title

...
```

### B. Archive Manifest Schema (JSON)

```json
{
  "archive_created_date": "2026-07-03T02:15Z",
  "consolidation_phase": "8.1.4",
  "taxonomy_version": "1.0",
  "entries": [
    {
      "archive_id": "phase-7-lane-4",
      "original_path": ".codex/PHASE_7_LANE_4_COMPLETION_SUMMARY.md",
      "archive_path": ".codex/archive/phases/phase-7/PHASE_7_LANE_4_COMPLETION_SUMMARY.md",
      "category": "phase_report",
      "consolidation_date": "2026-07-10",
      "relevance": "high",
      "last_accessed": "2026-07-03",
      "cross_references": 3
    }
  ]
}
```

### C. Freshness Gate Config (YAML)

```yaml
# .codex/FRESHNESS_GATE_CONFIG.yaml
freshness_thresholds:
  critical:
    max_age_days: 30
    docs:
      - "README.md"
      - "docs/index.md"
      - "docs/api-reference.md"
      - "CONTRIBUTING.md"
      - "SECURITY.md"
  general:
    max_age_days: 90
    docs:
      - "docs/**/*.md"
      - ".github/agents/**/*.md"

exclusions:
  immutable_trees:
    - "archive/"
    - "reports/"
    - ".codex/archive/"
  
enforcement:
  block_on_critical_stale: true
  block_on_p0_broken_links: true
  allow_waivers: true
  waiver_source: ".codex/LINK_VALIDATION_WHITELIST.json"
```

---

**Plan Status:** 🟢 COMPLETE — Workstream 8.1.2 planning deliverable  
**Generated:** 2026-07-03T02:15Z  
**Next Step:** Hand off to Workstream 8.1.3 (Link Fixes Execution)  
**Approver:** @mbaetiong (D-tier gate)
