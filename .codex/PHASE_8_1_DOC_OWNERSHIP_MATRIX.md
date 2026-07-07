# 👥 PHASE 8.1 DOCUMENTATION OWNERSHIP MATRIX

**Track:** 8.1 — Documentation Remediation  
**Authority:** @mbaetiong (D-tier autonomous)  
**Workstream:** 8.1.2 — Ownership & Responsibility Mapping  
**Status:** 🟢 ACTIVE  
**Generated:** 2026-07-07T14:26:35Z  
**Version:** 1.0  

---

## 1. EXECUTIVE SUMMARY

This matrix defines **clear ownership, responsibility, and review cadence** for all user-facing documentation in the Aries-Serpent/_codex_ codebase. It addresses the finding that 47% of documentation is stale and lacks a freshness signal, by assigning reviewers and establishing review schedules.

### Key Principles
1. **Single Owner per Major Doc:** Each critical doc has a named owner (agent or person) responsible for accuracy
2. **Quarterly Review Cadence:** All Tier 1 docs reviewed ≥ 4× per year
3. **YAML Front-Matter Metadata:** All docs track `owner`, `last_reviewed`, `review_cadence` in header
4. **Escalation Path:** Stale docs trigger owner notifications; escalate to @mbaetiong if unaddressed

---

## 2. TIER 1: USER-FACING DOCUMENTATION (SLA: 0 broken links, ≤90 days stale)

### 2.1 Root-Level Canonical Documentation

| Document | Owner | Review Cadence | Last Reviewed | SLA | Notes |
|-----------|-------|-----------------|----------------|-----|-------|
| `README.md` | @unified-doc-agent | Quarterly | 2026-07-07 | ≤90 days | Primary entry point; link-validation gate |
| `CONTRIBUTING.md` | @policy-coach-agent | Quarterly | 2026-07-07 | ≤90 days | Contributor onboarding; code-style alignment |
| `SECURITY.md` | @security-audit-agent | Quarterly | 2026-07-07 | ≤90 days | Security policy; must stay current |
| `CHANGELOG.md` | @pypi-publishing-operations-agent | Quarterly (post-release) | 2026-07-07 | ≤90 days | Version history; updated per release |
| `AGENTS.md` | @skills-master-agent | Quarterly | 2026-07-07 | ≤90 days | Agent registry; sync w/ `.github/agents/` |
| `CODE_OF_CONDUCT.md` | @policy-coach-agent | Annually | 2026-07-07 | ≤180 days | Code of conduct; low-change doc |

### 2.2 Documentation Root: `docs/` Directory (1,800 files)

#### 2.2.1 Core Navigation & Discovery

| Document | Owner | Review Cadence | SLA |
|-----------|-------|-----------------|-----|
| `docs/index.md` | @unified-doc-agent | Quarterly | ≤90 days |
| `docs/README.md` | @documentation-quality-agent | Quarterly | ≤90 days |
| `docs/GETTING_STARTED.md` (if exists) | @unified-doc-agent | Quarterly | ≤90 days |

#### 2.2.2 API & Reference Documentation (`docs/reference/`)

**Owner:** @code-analysis-agent  
**Review Cadence:** Quarterly + post-code-change audits  
**SLA:** ≤90 days stale; 0 broken code-target links  

| Category | Document Count | Coverage SLA | Notes |
|----------|-----------------|--------------|-------|
| API Reference | ~50 files | ≥80% public APIs documented | Code examples must run w/o error |
| Data Structures | ~30 files | ≥100% type definitions | Update when dataclass/TypedDict changes |
| Configuration | ~20 files | ≥95% config options | Tied to `pyproject.toml` / Hydra schema |

**Review Process:**
- `code-analysis-agent` scans public APIs in `src/codex/`, `src/services/`, etc.
- Compares against API reference docs in `docs/reference/`
- Files PR with "API Doc Sync" for any drift
- Quarterly audit: Run `doc-refactor-test-agent` to verify code examples compile

---

#### 2.2.3 Architecture & Design (`docs/arch/`)

**Owner:** @python-architect-agent  
**Review Cadence:** Quarterly + post-major-refactor  
**SLA:** ≤90 days stale; diagrams updated when architecture changes  

| Document | Responsibility | Update Trigger |
|-----------|-----------------|-----------------|
| `docs/arch/ARCHITECTURE.md` | Overview of modules + data flow | Major code reorganization |
| `docs/arch/COGNITIVE_BRAIN_ARCHITECTURE.md` | Cognitive brain system design | Skill/surface changes |
| `docs/arch/SYSTEM_DESIGN.md` | End-to-end system flows | API changes, new services |
| Mermaid diagrams (`.md` with embedded diagrams) | Architectural diagrams | Design reviews |

**Review Process:**
- `python-architect-agent` conducts quarterly design review
- Cross-reference `docs/arch/` against actual `src/codex/` module structure
- Ensure all major modules documented; update ERD/flow diagrams if needed
- File PR if discrepancies found

---

#### 2.2.4 Guides & How-To (`docs/guides/`)

**Owner:** @doc-refactor-test-agent  
**Review Cadence:** Quarterly + per-feature release  
**SLA:** ≤90 days stale; 100% of examples must execute successfully  

| Document Type | Count | Owner | SLA |
|----------------|-------|-------|-----|
| Quickstart guides | ~15 | @unified-doc-agent | ≤30 days (high visibility) |
| Integration guides | ~20 | @integration-test-runner | ≤90 days |
| Admin/ops guides | ~25 | @workflow-health-monitor | ≤90 days |
| Security hardening | ~10 | @security-audit-agent | ≤60 days |

**Review Process:**
- `doc-refactor-test-agent` runs code examples in each guide to verify correctness
- Flags guides with outdated API calls or broken imports
- Files PR with "Guide Update: [topic]" before release
- Maintains test harness for guide validation (`.codex/scripts/validate_guides.py`)

---

#### 2.2.5 Admin & Operations (`docs/admin/`)

**Owner:** @workflow-compliance-guardian  
**Review Cadence:** Quarterly + per-infrastructure-change  
**SLA:** ≤90 days stale; all procedural steps verified to work  

| Document | Responsibility |
|-----------|-----------------|
| `docs/admin/DEPLOYMENT.md` | Deployment procedures; CI/CD steps |
| `docs/admin/INCIDENT_RESPONSE.md` | On-call runbooks; escalation paths |
| `docs/admin/INFRASTRUCTURE.md` | K8s, storage, networking config |
| `docs/admin/RBAC_POLICIES.md` | Authorization model; role definitions |

**Review Process:**
- `workflow-compliance-guardian` validates procedures in staging environment
- Test each admin procedure quarterly (deployment, incident response, RBAC changes)
- File PR with "Admin Procedure Validation" if steps change

---

#### 2.2.6 Troubleshooting & Diagnostics (`docs/troubleshooting/` if exists)

**Owner:** @ci-health-alert-agent  
**Review Cadence:** Reactive (as issues arise) + quarterly sync  
**SLA:** ≤90 days for resolved issues (stale diagnostic docs are dangerous)  

| Category | Example | Owner |
|----------|---------|-------|
| CI/CD Failures | "Pipeline stuck in queued state" | @ci-health-alert-agent |
| Deployment Errors | "PullImageError in K8s" | @artifact-monitor-agent |
| Performance | "Slow test runs; cache degradation" | @cache-management-agent |

**Review Process:**
- When CI issue filed: Diagnostic doc updated immediately
- `ci-health-alert-agent` reviews monthly for stale diagnostics
- Archive resolved issues to `.codex/archive/diagnostics/`

---

#### 2.2.7 Terminology & Glossary (`docs/TERMINOLOGY_GLOSSARY.md`)

**Owner:** @terminology-consistency-agent  
**Review Cadence:** Quarterly + per-terminology-change  
**SLA:** ≤90 days stale; all glossary terms used in codebase + docs  

**Sections to Maintain:**
1. **Agent Terminology** — agent types, autonomy tiers, execution modes
2. **Governance** — D-tier, D-CAPABLE, gating, Brief, Workstream
3. **Infrastructure** — CI/CD, K8s, caching, networking
4. **Testing** — flakiness, P19, shadow imports, mutation testing
5. **Performance** — benchmarks, regression, throughput
6. **Compliance** — GDPR, CCPA, audit, PII

**Review Process:**
- `terminology-consistency-agent` audits all docs for undefined jargon
- Quarterly: Review against code comments + commit messages for new terms
- Update glossary; file PR with "Terminology Sync"

---

### 2.3 Agent & Configuration Specs (`.github/agents/` & `.github/copilot-prompts/`)

**Owner:** @skills-master-agent  
**Review Cadence:** Per-agent-update or quarterly (whichever is sooner)  
**SLA:** ≤30 days stale (agents are active code); 100% linked to AGENTS.md  

| Document Type | Count | SLA | Notes |
|----------------|-------|-----|-------|
| Agent specs (`*_AGENT*.md`) | ~250 | ≤30 days | Tied to agent source code |
| Prompt library (`.copilot-prompts/`) | ~400 | ≤30 days | Updated per prompt iteration |

**Review Process:**
- `skills-master-agent` maintains agent registry in real time
- Per PR that modifies agent: Update spec doc + metadata
- Quarterly: Audit all agent specs for stale descriptions vs. actual capability
- Maintain `AGENTS.md` as single source of truth; `.github/agents/` as detailed specs

---

## 3. TIER 2: HISTORICAL DOCUMENTATION (No SLA; archived)

### 3.1 Report Archive (`.codex/archive/`)

| Category | Owner | Retention | Notes |
|----------|-------|-----------|-------|
| Phase reports (PHASE_1_* through PHASE_12_*) | @ci-pattern-guardian | ≤5 years | Point-in-time snapshots; consolidate under phase-level index |
| Wave reports (WAVE_*) | @ci-pattern-guardian | ≤5 years | Consolidated similarly |
| Gate/validation reports | @ci-pattern-guardian | ≤5 years | Historical snapshots |
| Agent accountability | @orchestrator-agent | ≤2 years | Archive old sessions; keep recent for audit trail |

**No SLA applied.** These docs are historical and expected to be stale.

---

### 3.2 Legacy `.txt` Reports

| Category | Disposition |
|----------|------------|
| Old telemetry/metrics | Convert to `.md` + archive, or delete if obsolete |
| Build/test artifacts | Delete (transient; archived in CI artifacts) |
| Audit snapshots | Convert to `.md` + `.codex/archive/audits/` |

---

## 4. METADATA STANDARD: YAML FRONT-MATTER

All **Tier 1 documents** must include this YAML front-matter block at the start:

```yaml
---
title: "Document Title"
owner: "@agent-name-or-username"
last_reviewed: "2026-07-07"
review_cadence: "quarterly|bi-annual|annual"
sla_days: 90
critical: false
---
```

### Field Definitions

| Field | Values | Requirement | Example |
|-------|--------|-------------|---------|
| `title` | String | Required | "API Reference" |
| `owner` | `@agent-name` or `@username` | Required | `@code-analysis-agent` |
| `last_reviewed` | ISO date (YYYY-MM-DD) | Required | "2026-07-07" |
| `review_cadence` | quarterly\|bi-annual\|annual | Required | "quarterly" |
| `sla_days` | Integer | Required | 90 |
| `critical` | true\|false | Optional | false (true if blocking other work) |

### CI Gate Implementation

A GitHub Actions workflow (`link-validation + freshness-check.yml`) will:
1. Extract `last_reviewed` from all `.md` front-matter in `docs/` and `root`
2. Calculate days since review: `(today - last_reviewed).days`
3. **Warn** if `days > sla_days`
4. **Fail PR** if any critical doc is stale (only for `critical: true` docs)
5. Maintain manifest: `.codex/DOC_FRESHNESS_MANIFEST.json` tracking all docs + status

---

## 5. REVIEW PROCESS & ESCALATION

### 5.1 Quarterly Review Cadence (Automation)

**Trigger:** First Monday of every quarter (Q3 2026: Oct 7, Q4 2026: Jan 6, etc.)

**Process:**
1. **Automated scan:** Run `ci/freshness-check.py` against all Tier 1 docs
2. **Identify stale:** Docs where `today - last_reviewed > 90 days`
3. **Issue notifications:** GitHub issue per owner with checklist
   - Title: "Documentation Review Due: [doc name]"
   - Checklist: [ ] Verify content accuracy; [ ] Update examples; [ ] Commit front-matter `last_reviewed: YYYY-MM-DD`
4. **Owner response:** 1 week to close or update; escalate to @mbaetiong if unaddressed

### 5.2 Manual Review Process (Per-Doc Change)

**Trigger:** PR that modifies a Tier 1 doc

**Process:**
1. **Author** commits front-matter update: `last_reviewed: [today]`
2. **Reviewer** ensures:
   - Content is accurate vs. current code
   - Links are not broken (link-validator gate)
   - Examples have been tested (for guides/references)
   - YAML front-matter updated
3. **Merge:** Commit includes updated `last_reviewed` metadata

### 5.3 Escalation Path

```
Owner → Stale Doc Notification (automated)
  ↓
Owner Reviews / Updates (1 week)
  ↓
Stale? → Escalate to @mbaetiong (D-tier authority)
  ↓
@mbaetiong → Reassign owner OR archive doc
```

---

## 6. OWNERSHIP ASSIGNMENTS BY AGENT SPECIALIZATION

### 6.1 Primary Owners (by domain)

| Domain | Primary Agent | Backup | Scope |
|--------|---------------|--------|-------|
| **Link Validation** | @link-validator-agent | @unified-doc-agent | All broken links in Tier 1 |
| **Code Examples** | @doc-refactor-test-agent | @code-analysis-agent | Guides, API docs, quickstarts |
| **API Reference** | @code-analysis-agent | @python-architect-agent | `docs/reference/` |
| **Architecture** | @python-architect-agent | @codebase-health-guardian | `docs/arch/` |
| **Operations & Admin** | @workflow-compliance-guardian | @ci-health-alert-agent | `docs/admin/`, `docs/ops/` |
| **Terminology** | @terminology-consistency-agent | @unified-doc-agent | `docs/TERMINOLOGY_GLOSSARY.md` |
| **Agent Specs** | @skills-master-agent | @agent-iq-scoring-gate | `.github/agents/` |
| **Guides & How-To** | @doc-refactor-test-agent | @integration-test-runner | `docs/guides/` |
| **Root Canonical** | @unified-doc-agent | @policy-coach-agent | `README.md`, `AGENTS.md`, etc. |

### 6.2 Escalation (if primary owner unavailable)

Each agent has a **backup owner** listed in `ownership_matrix` column 3. If primary owner cannot respond within 1 week:
- **Reassign to backup owner** (automated GitHub issue reassignment)
- **Escalate to @mbaetiong** if both primary + backup unresponsive

---

## 7. REVIEW SCHEDULE CALENDAR

### Quarterly Review Dates (2026-2027)

| Quarter | Start Date | Review Window | Lead |
|---------|-----------|----------------|------|
| **Q3 2026** | 2026-07-01 | 2026-07-01 to 2026-09-30 | unified-doc-agent |
| **Q4 2026** | 2026-10-01 | 2026-10-01 to 2026-12-31 | unified-doc-agent |
| **Q1 2027** | 2027-01-01 | 2027-01-01 to 2027-03-31 | unified-doc-agent |
| **Q2 2027** | 2027-04-01 | 2027-04-01 to 2027-06-30 | unified-doc-agent |

**Key dates within each quarter:**
- **Week 1:** Automated freshness scan; identify stale docs
- **Week 2–3:** Owner responses; reviews conducted
- **Week 4:** Escalations to @mbaetiong (if needed)

---

## 8. SPECIAL CASES & EXCEPTIONS

### 8.1 High-Criticality Docs (Review More Frequently)

These docs have **shorter SLA** (≤30 days) due to operational criticality:

| Document | Owner | SLA | Reason |
|----------|-------|-----|--------|
| `README.md` | @unified-doc-agent | ≤30 days | First impression; users rely on it |
| `SECURITY.md` | @security-audit-agent | ≤60 days | Security policies must be current |
| `docs/admin/INCIDENT_RESPONSE.md` | @workflow-compliance-guardian | ≤30 days | On-call runbooks can't be stale |
| `docs/guides/QUICKSTART.md` | @doc-refactor-test-agent | ≤30 days | First-time user experience |

---

### 8.2 Low-Change Docs (Review Less Frequently)

These docs are **stable** and reviewed **annually**:

| Document | Owner | SLA | Reason |
|----------|-------|-----|--------|
| `CODE_OF_CONDUCT.md` | @policy-coach-agent | ≤180 days | Rarely changes; once yearly sufficient |
| `LICENSE` | @legal-team (if applicable) | ≤365 days | License rarely changes |

---

### 8.3 Track 8.3 Coordination: Code-Moved Docs

**Situation:** When Track 8.3 moves/renames source files, docs may reference old paths.

**Owner Action:**
1. Track 8.3 provides file-move mapping to Track 8.1
2. `@link-validator-agent` re-runs validator; identifies P1b broken links (code-moved targets)
3. Owner (e.g., `@code-analysis-agent` for API docs) updates links to new paths
4. Update front-matter `last_reviewed: [today]`

**SLA:** Link fixes merged within 1 week of Track 8.3 completion.

---

## 9. OWNERSHIP MATRIX MAINTENANCE

This matrix is **living documentation** and should be updated when:

1. **Agent is added to codebase** → Add row to relevant table with owner assignment
2. **Owner becomes unavailable** → Reassign to backup; file issue in `.codex/` tracking changes
3. **New doc category created** → Add to appropriate section; assign owner
4. **Review cadence changes** → Update this matrix + YAML front-matter in affected docs

**Matrix Review:** Quarterly (aligned with doc review cycle)  
**Maintainer:** @unified-doc-agent + @skills-master-agent (co-maintainers)

---

## 10. QUICK-REFERENCE: OWNER LOOKUP TABLE

For any Tier 1 doc in the repo, find its owner here:

```
Document Path                          → Owner                          → SLA
─────────────────────────────────────────────────────────────────────────────
README.md                              → @unified-doc-agent            → ≤30 days
CONTRIBUTING.md                        → @policy-coach-agent           → ≤90 days
SECURITY.md                            → @security-audit-agent         → ≤60 days
AGENTS.md                              → @skills-master-agent          → ≤90 days
docs/index.md                          → @unified-doc-agent            → ≤90 days
docs/reference/*                       → @code-analysis-agent          → ≤90 days
docs/arch/*                            → @python-architect-agent       → ≤90 days
docs/guides/*                          → @doc-refactor-test-agent      → ≤90 days
docs/admin/*                           → @workflow-compliance-guardian → ≤90 days
docs/TERMINOLOGY_GLOSSARY.md           → @terminology-consistency-agent→ ≤90 days
.github/agents/*                       → @skills-master-agent          → ≤30 days
.github/copilot-prompts/*              → @skills-master-agent          → ≤30 days
```

---

## 11. SIGN-OFF & ACKNOWLEDGMENT

| Role | Name | Date | Status |
|------|------|------|--------|
| **Plan Owner** | @mbaetiong | 2026-07-07 | ✅ Approved |
| **Unified Doc Agent** | (automated) | 2026-07-07 | ✅ Confirmed |
| **Skills Master Agent** | (automated) | 2026-07-07 | ✅ Confirmed |

---

**Matrix Version:** 1.0  
**Last Updated:** 2026-07-07T14:26:35Z  
**Status:** 🟢 READY FOR WS3 IMPLEMENTATION  
**Next Review:** Q3 2026 (quarterly cadence begins)

---

## APPENDIX A: ONBOARDING NEW OWNERS

When assigning a new owner to a doc:

1. **Add entry to this matrix** (appropriate section + lookup table §10)
2. **Notify the owner** via GitHub issue: "New documentation ownership: [doc name]"
3. **Set initial `last_reviewed:`** to today (fresh ownership start)
4. **Establish review cadence:** Default quarterly; adjust if needed
5. **Add to CI gate:** Ensure doc is scanned in `.codex/DOC_FRESHNESS_MANIFEST.json`

---

## APPENDIX B: AGENT CAPABILITY TAGS

Map of agents → their documentation responsibilities (for routing):

```yaml
capabilities:
  code_analysis:
    agent: code-analysis-agent
    docs:
      - docs/reference/API_REFERENCE.md
      - docs/reference/DATA_STRUCTURES.md
    cadence: quarterly_post_audit
  
  architecture:
    agent: python-architect-agent
    docs:
      - docs/arch/ARCHITECTURE.md
      - docs/arch/SYSTEM_DESIGN.md
    cadence: quarterly_post_refactor
  
  operations:
    agent: workflow-compliance-guardian
    docs:
      - docs/admin/DEPLOYMENT.md
      - docs/admin/INCIDENT_RESPONSE.md
    cadence: quarterly_post_infrastructure_change
  
  links:
    agent: link-validator-agent
    docs:
      - all_tier_1_docs
    cadence: per_commit
  
  glossary:
    agent: terminology-consistency-agent
    docs:
      - docs/TERMINOLOGY_GLOSSARY.md
    cadence: quarterly_or_per_term_change
```

---

**END OF OWNERSHIP MATRIX**
