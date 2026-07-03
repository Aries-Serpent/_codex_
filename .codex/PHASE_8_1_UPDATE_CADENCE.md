# 📅 PHASE 8.1 — DOCUMENTATION UPDATE CADENCE & FRESHNESS AUTOMATION (Workstream 8.1.2)

**Track:** 8.1 — Documentation Remediation  
**Track Lead:** unified-doc-agent  
**Authority:** @mbaetiong (D-tier autonomy, GO CONTINUE on all gates)  
**Generated:** 2026-07-03T02:25Z  
**Workstream:** 8.1.2 Update Cadence & Freshness Automation Blueprint  
**Scope:** Refresh schedules, automation triggers, and SLA enforcement across all user-facing docs  

---

## 1. EXECUTIVE SUMMARY

This document establishes **content refresh schedules** (cadence) and **automation rules** that will keep documentation synchronized with code, architecture, and operational reality. It operationalizes the P0 enabler from the Remediation Plan (freshness signal adoption) by defining:

1. **Refresh frequency per doc category** (critical 30d, general 90d, archive immutable)
2. **Automated triggers** that alert owners when docs approach stale threshold
3. **Freshness metadata** (front-matter `last_reviewed:` + external manifest)
4. **CI gate rules** (blocking vs. waivered) for enforcement
5. **Post-Phase-8.1 automation roadmap** (Weeks 7–52 and beyond)

**Key principle:** *Documentation freshness is a **continuous property**, not a one-time fix.*

---

## 2. REFRESH CADENCE TIERS

### 2.1 Critical Cadence (30-day max stale; zero broken links allowed)

**Docs in this tier see frequent updates and must stay current.**

| Category | Documents | Reason | Refresh Trigger | Owner Check Interval |
|----------|-----------|--------|-----------------|-----|
| **Core entrypoints** | README.md, CONTRIBUTING.md, SECURITY.md, CHANGELOG.md, AGENTS.md | High visibility; user trust | Before release, or 30d calendar | Weekly |
| **API reference** | docs/reference/api*.md (15 files) | Code API surface drifts frequently | On every public API change | Weekly |
| **CLI reference** | docs/reference/cli*.md (8 files) | CLI options/subcommands change | On CLI flag/subcommand addition | Weekly |
| **Terminology glossary** | docs/TERMINOLOGY_GLOSSARY.md (NEW) | Used by all consistency checks | On terminology-agent audit | Weekly |
| **Cognitive brain docs** | docs/cognitive_brain/*.md (53 files) | Active system development | On feature/OODA loop change | Bi-weekly |
| **Agent registry + index** | AGENTS.md, docs/agent/index.md, .github/agents/AGENT_REGISTRY.yaml | Agent ecosystem churn | On agent deploy/retire | Weekly |

**SLA enforcement:**
- ✅ PASS: Last reviewed ≤ 30 days ago
- 🟡 WARNING: 30–35 days ago (yellow flag, email alert)
- 🔴 FAILING: > 35 days old (CI gate blocks new PRs to user-facing docs)
- 🟠 ESCALATION: > 45 days old (escalate to fallback owner + @mbaetiong)

---

### 2.2 General Cadence (90-day max stale; broken links should not exceed 0.5% rate)

**Mainstream docs; updated quarterly or on significant changes.**

| Category | Documents | Reason | Refresh Trigger | Owner Check Interval |
|----------|-----------|--------|-----------------|-----|
| **Guides** | docs/guides/*.md (48 files) | How-to content; lasts longer but needs seasonal refresh | Quarterly + on API change | Monthly |
| **Administration** | docs/admin/*.md (30 files) | Governance, access control; less frequent change | Quarterly governance review | Monthly |
| **Operations** | docs/ops/*.md (73 files) | Runbooks, monitoring; change with infra updates | On infra change or quarterly | Monthly |
| **Architecture** | docs/arch/*.md (29 files) | System design; changes on major refactor | Major refactor or 6-month cycle | Monthly |
| **Testing** | docs/testing/*.md (32 files) | Test patterns; stable but evolve with practices | Quarterly + on test framework upgrade | Monthly |
| **Validation** | docs/validation/*.md (69 files) | QA procedures; update on process change | Quarterly + on automation addition | Monthly |
| **Capabilities** | docs/capabilities/*.md (31 files) | Feature inventory; update on release | Per-release + feature deprecation | Monthly |
| **Security** | docs/security/*.md (49 files) | Threat models, vulnerability response | Threat review + alert response | Bi-weekly (more volatile) |

**SLA enforcement:**
- ✅ PASS: Last reviewed ≤ 90 days ago
- 🟡 WARNING: 90–110 days ago (email alert)
- 🔴 FAILING: > 110 days old (CI gate blocks new PRs to same domain)
- 🟠 ESCALATION: > 180 days old (escalate + consider archival)

---

### 2.3 Low-Priority Cadence (180-day; best-effort)

**Stable, less-frequently-updated content.**

| Category | Documents | Reason | Refresh Trigger | Owner Check Interval |
|----------|-----------|--------|-----------------|-----|
| **Templates** | docs/templates/*.md (61 files) | Boilerplate; stable reference | On template spec change or semi-annual review | Quarterly |
| **Legacy guides** | docs/archive/*.md + docs/legacy/*.md | Superseded; kept for reference | None (immutable) | On-demand only |

**SLA enforcement:**
- ✅ PASS: < 180 days old (soft requirement)
- 🟡 WARNING: 180–270 days old
- 🟠 ESCALATION: > 270 days old (consider archival)

---

### 2.4 Immutable Cadence (Archive/Reports; no SLA)

**Historical snapshots; frozen for audit trail.**

| Category | Documents | SLA | Policy |
|----------|-----------|-----|--------|
| **Phase/Wave/Gate reports** | `.codex/archive/phases/*`, `.codex/archive/waves/*`, `.codex/archive/gates/*` | None | **Never update.** Consolidate to archive during 8.1.4; reference via `.codex/ARCHIVE_MANIFEST.json` only. |
| **Status snapshots** | `.codex/archive/reports-by-type/*` (SUMMARY, FINAL, COMPLETION) | None | Immutable historical records. |
| **Old docs** | `docs/archive/*` | None | Frozen; remove from `mkdocs.yml` nav. |
| **Legacy `.txt` reports** | `reports/*.txt`, legacy `.txt` artifacts | None | Convert to `.md` or deprecate during 8.1.4 archival. |

---

## 3. CONTENT CHANGE TRIGGERS & CADENCE RESET

**The `last_reviewed` date resets when:**

1. **Code change impacts docs** (e.g., API signature change, new feature, security fix)
   - Owner notified immediately (by diff analyzer or CI hook)
   - 14-day grace period to review + update docs
   - Auto-flag if no update by grace period expiration

2. **Owner-initiated refresh** (monthly, quarterly, etc. scheduled review)
   - Owner manually updates `last_reviewed: YYYY-MM-DD` front-matter
   - CI confirms freshness gate compliance

3. **Dependency/tool upgrade** (Python, Rust, MkDocs, docs framework)
   - Flag docs that reference version numbers, install steps
   - 7-day review window

4. **Terminology audit** (terminology-consistency-agent scan)
   - If glossary changes, touch all docs using those terms
   - 3-day review window for consistency sweep

5. **Security alert** (code-scanning, secret-detection, vulnerability)
   - If docs reference vulnerable library, attack surface, or mitigation, review immediately
   - Emergency lane: 24-hour SLA

---

## 4. AUTOMATED FRESHNESS SIGNALS & ALERTS

### 4.1 — Front-Matter Metadata (Primary Signal)

**Embedded in every `.md` file (user-facing tree only):**

```yaml
---
title: "API Reference"
description: "Public API documentation for _codex_ CLI and Python SDK"
last_reviewed: 2026-07-03
review_frequency: 30  # days; critical=30, general=90, low=180
critical: true        # Use critical SLA (30d) instead of general (90d)
owner: "@codebase-health-guardian"
related_code:
  - "src/codex/cli/main.py"
  - "src/codex/api/client.py"
tags:
  - "api"
  - "reference"
  - "requires-validation"
---
```

**Automation: CI script extracts front-matter YAML, compares `last_reviewed` to today.**

### 4.2 — External Freshness Manifest (Fallback Signal)

**For docs that cannot accept front-matter (auto-generated, legacy):**

`.codex/DOC_FRESHNESS_MANIFEST.json`:

```json
{
  "manifest_version": "1.0",
  "generated_at": "2026-07-03T02:25Z",
  "entries": [
    {
      "doc_path": "README.md",
      "doc_title": "Main repository introduction",
      "last_reviewed": "2026-07-03",
      "review_frequency_days": 30,
      "critical": true,
      "owner": "@unified-doc-agent",
      "stale_status": "green",
      "days_since_review": 0,
      "days_until_stale": 30,
      "related_code": [],
      "notes": "Core entrypoint; reviewed weekly"
    },
    {
      "doc_path": "docs/guides/quickstart.md",
      "doc_title": "Getting Started",
      "last_reviewed": "2026-05-15",
      "review_frequency_days": 90,
      "critical": false,
      "owner": "@post-merge-doc-alignment-agent",
      "stale_status": "yellow",
      "days_since_review": 49,
      "days_until_stale": 41,
      "related_code": ["src/codex/cli/main.py"],
      "notes": "Needs refresh; API example may be outdated"
    }
  ]
}
```

**Automation: CI script generates this nightly by scanning all user-facing `.md` files.**

### 4.3 — CI Gate Automation (Enforcement)

**GitHub Actions workflow: `.github/workflows/doc-freshness-gate.yml` (deployed in 8.1.5)**

```yaml
name: Documentation Freshness Gate
on:
  pull_request:
    paths:
      - 'docs/**'
      - '.github/agents/**'
      - 'README.md'
      - 'SECURITY.md'
      - 'CONTRIBUTING.md'
      - 'CHANGELOG.md'
      - 'AGENTS.md'
  schedule:
    - cron: '0 2 * * 0'  # Weekly Sunday 02:00 UTC

jobs:
  freshness-gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Extract freshness metadata
        id: freshness
        run: |
          python scripts/ci/extract_freshness_metadata.py \
            --output freshness-report.json \
            --critical-threshold-days 30 \
            --general-threshold-days 90

      - name: Generate freshness dashboard
        run: |
          python scripts/ci/generate_freshness_dashboard.py \
            --input freshness-report.json \
            --output doc-health-dashboard.md

      - name: Gate logic (blocking)
        id: gate
        run: |
          python scripts/ci/doc_freshness_gate.py \
            --config .codex/FRESHNESS_GATE_CONFIG.yaml \
            --input freshness-report.json \
            --fail-on-critical-stale \
            --fail-on-p0-broken-links

      - name: Comment on PR (if PR context)
        if: github.event_name == 'pull_request' && always()
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const report = JSON.parse(fs.readFileSync('freshness-report.json', 'utf8'));
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## Documentation Freshness Check\n\n${report.pr_summary}`
            });

      - name: Upload dashboard
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: doc-health-dashboard
          path: doc-health-dashboard.md
          retention-days: 30

      - name: Publish to GitHub Discussions
        if: github.event_name == 'schedule'
        run: |
          python scripts/ci/publish_doc_health_to_discussions.py \
            --board "Documentation-Health" \
            --input doc-health-dashboard.md
```

**Gate behavior:**

```
IF (doc in CRITICAL set) AND (days_since_review > 30):
  THEN fail_gate()  # Blocks PR merge to user-facing docs
ELSE IF (doc in GENERAL set) AND (days_since_review > 110):
  THEN fail_gate()  # Blocks PR to that domain
ELSE IF (broken_p0_links > 0):
  THEN fail_gate()  # Blocks any PR to docs
ELSE:
  pass_gate()  # Comment on PR with status
```

---

## 5. AUTOMATION ROADMAP (Weeks 7 & Beyond)

### 5.1 — Weeks 7–8 (Phase 8.1 Close-Out)

| Week | Automation | Task | Owner |
|------|-----------|------|-------|
| **Week 6.5** | CI gate deployment | Deploy `.github/workflows/doc-freshness-gate.yml` to production | unified-doc-agent + workflow-compliance-guardian |
| **Week 7** | Retrospective + tuning | Collect FP feedback from first 100 CI runs; refine whitelist | unified-doc-agent |
| **Week 7** | Scorecard baseline | Generate first official freshness scorecard + dashboard | unified-doc-agent |
| **Week 8** | Handoff to automation | Owner assignments finalized; all owners briefed on cadence | unified-doc-agent + @mbaetiong |

### 5.2 — Weeks 9–26 (Continuous Enforcement)

| Phase | Automation | Frequency | Owner |
|-------|-----------|-----------|-------|
| **Link health** | Weekly link-validation report (cached) | Every Monday morning | unified-doc-agent (gate automation) |
| **Freshness scorecard** | Weekly status report (critical) + monthly digest (general) | Every Sunday + 1st of month | unified-doc-agent (gate automation) |
| **Staleness alerts** | Slack/email to owner when doc > threshold − 7 days | Dynamic (triggered by gates) | unified-doc-agent (gate automation) |
| **Code-example validation** | Per-release (before tag) + on-demand (PR) | Release cadence + manual | doc-refactor-test-agent |
| **Terminology consistency scan** | Monthly + on glossary change | 1st of month + event-driven | terminology-consistency-agent |
| **Post-merge drift detection** | On-release check for API/CLI/config docs vs. codebase | Per-release | post-merge-doc-alignment-agent |

### 5.3 — Weeks 27+ (Optimization & Learning)

| Milestone | Action | Target | Owner |
|-----------|--------|--------|-------|
| **Month 4 (Sept 2026)** | Quarterly freshness audit | Identify patterns in ownership gaps; recommend process changes | unified-doc-agent + leadership |
| **Month 6 (Nov 2026)** | Cadence tuning | Adjust thresholds based on 6 months of gate data | unified-doc-agent (with stakeholder input) |
| **Month 12 (May 2027)** | Full-year retrospective | Assess cost-benefit of automation; evaluate against Unified Doc Agent v1.0 SLAs | unified-doc-agent + leadership |

---

## 6. EDGE CASES & EXEMPTIONS

### 6.1 — Emergency Exemption: Security Vulnerability

**If a security vulnerability is disclosed:**
- **SLA override:** All doc-change deadlines are suspended for security-focused docs (SECURITY.md, relevant API docs)
- **Fast lane:** 24-hour update SLA; CI gate bypassed for approved security PRs
- **Notification:** @security-audit-agent + @mbaetiong + doc owners notified immediately

### 6.2 — Exemption: Newly Created Docs

**New docs get a 14-day grace period before freshness gate applies:**
- `last_reviewed:` is set to creation date
- First refresh due date = creation + review_frequency
- Owner has 14 days to validate completeness before gate enforces

### 6.3 — Exemption: Docs Under Active Refactor

**Docs flagged as "in-progress" (front-matter `status: refactoring`) are:**
- Excluded from freshness SLA (temporarily)
- Still subject to broken-link checks (P0 links must not break mid-refactor)
- Expected to transition to `status: stable` within 14 days
- If not, escalate to fallback owner

### 6.4 — Exemption: Archive & Historical Docs

**Docs in `.codex/archive/` and `docs/archive/` are:**
- Never subject to freshness gate
- Included in periodic integrity scans (broken links, but waived if internal-only)
- Eligible for purge if > 2 years old and zero references from live docs

---

## 7. MEASUREMENT & DASHBOARDING

### 7.1 — Primary Metrics

| Metric | Definition | Target | Measurement Method |
|--------|-----------|--------|-----|
| **Critical freshness** | % of critical docs ≤ 30 days old | ≥ 95% | Extract `last_reviewed:` front-matter; count days |
| **General freshness** | % of general docs ≤ 90 days old | ≥ 90% | same |
| **Broken link rate** | % of broken relative links in user-facing docs | ≤ 0.5% | Weekly link-validator pass; exclude waivered FPs |
| **Code-example validation** | % of API docs passing code-example tests | ≥ 95% | CI test harness (pre-merge) |
| **Ownership coverage** | % of docs with assigned owner in OWNERSHIP_MATRIX | 100% | Grep for unmapped paths in matrix |
| **Gate compliance** | % of merged PRs passing freshness + link gates | ≥ 98% | CI gate success rate |

### 7.2 — Sample Weekly Scorecard (Auto-Generated)

```markdown
# 📊 Documentation Health Scorecard — Week of 2026-07-10

## Critical Freshness (SLA: 30 days max)
✅ **PASS** — 95% compliant (19/20 docs ≤ 30 days old)

**Compliant:**
- README.md (3 days old)
- CONTRIBUTING.md (42 days old) ⚠️ → 🔴 FAILING [ACTION: @policy-coach-agent review]
- SECURITY.md (2 days old)
- CHANGELOG.md (35 days old) ⚠️ → 🔴 FAILING [ACTION: @pypi-publishing-operations-agent update]
- docs/index.md (5 days old)
- AGENTS.md (21 days old)
- docs/TERMINOLOGY_GLOSSARY.md (0 days old, just created)
- docs/reference/api*.md (7/8 compliant; 1 @ 65d) → 🟡 WARNING
- docs/cognitive_brain/*.md (52/53 compliant)
...

**Failures (> 30 days):**
1. CONTRIBUTING.md — 42 days — Owner: @policy-coach-agent — Escalate: @mbaetiong
2. CHANGELOG.md — 35 days — Owner: @pypi-publishing-operations-agent — Escalate: @mbaetiong
3. docs/reference/api-events.md — 65 days — Owner: @codebase-health-guardian — Escalate: @codebase-health-guardian

**Actions Required:** 2 owner notifications + 1 escalation to @mbaetiong

---

## General Freshness (SLA: 90 days max)
✅ **PASS** — 89% compliant (182/205 docs ≤ 90 days old)

**Warnings (70–90 days):**
- docs/guides/advanced-patterns.md (88 days) — Review within 2 days
- docs/ops/monitoring.md (84 days) — Review within 6 days

**Failures (> 90 days):**
- docs/admin/access-control.md (124 days) — Owner: @owner-approval-guard — Escalate
- docs/arch/cache-layers.md (156 days) — Owner: @codebase-health-guardian — Escalate

**Actions Required:** 2 escalations

---

## Broken Links (SLA: ≤ 0.5%)
✅ **PASS** — 0 broken P0 links; 3 P1 links (waivered FPs)

**P0 Critical Links:** 0 broken ✅
- Code references (src/**/*.py): 0 broken
- API cross-refs: 0 broken

**P1 Important Links:** 3 broken (all waivered)
- docs/guides/deprecated.md → ./old-api.md (FP, whitelisted)
- docs/ops/runbook.md → ../archive/script.sh (valid archive ref)
- .codex/README_DISCUSSION.md → SESSION_ANALYSIS_SUMMARY_20260619.md (archived report ref)

**Broken Rate:** 0 / 12,000 = 0% ✅

---

## Code-Example Validation
✅ **PASS** — 94% (48/51 API docs validated)

**Failures (examples do not run):**
- docs/reference/api-webhooks.md: Example authentication token format outdated (needs SDK v2.3+)

---

## Overall Scorecard
| Metric | Score | Target | Status |
|--------|-------|--------|--------|
| Critical freshness | 95% | ≥ 95% | ✅ At target |
| General freshness | 89% | ≥ 90% | 🟡 Close; monitor |
| Broken links | 0% | ≤ 0.5% | ✅ At target |
| Code examples | 94% | ≥ 95% | 🟡 Close; monitor |
| **Overall** | **93%** | **≥ 93%** | **✅ PASS** |

---

## Upcoming Deadline Alerts

**Next 7 days (by 2026-07-17):**
- ⚠️ docs/guides/advanced-patterns.md due for review (2 days remaining)
- 🔴 CONTRIBUTING.md now 42 days overdue (critical)
- 🔴 CHANGELOG.md now 35 days overdue (critical)

**Next 14 days (by 2026-07-24):**
- ⚠️ docs/ops/monitoring.md due for review (9 days remaining)

---

**Generated:** 2026-07-10T02:05Z | Next update: 2026-07-17T02:00Z
**Dashboard:** [View full metrics on GitHub Discussions](https://github.com/Aries-Serpent/_codex_/discussions/2850)
```

---

## 8. MANUAL OVERRIDE & WAIVER PROCESS

**If a doc cannot meet SLA due to external factors:**

1. **Owner files waiver request** → Creates GitHub issue with label `docs-waiver-request` + rationale
2. **Unified-doc-agent reviews** → Determines if valid (e.g., code not ready yet, API unstable)
3. **Approval** → If approved, adds entry to `.codex/FRESHNESS_EXEMPTIONS.json`:

```json
{
  "exemptions": [
    {
      "doc_path": "docs/reference/api-experimental.md",
      "reason": "Experimental API; SDK v3.0 still in beta (target merge 2026-07-30)",
      "exemption_type": "temporary",
      "expires_at": "2026-07-30",
      "approved_by": "@unified-doc-agent",
      "jira_ref": "CODEX-1234"
    }
  ]
}
```

4. **CI gate updated** → Doc excluded from gate until expiration date
5. **Auto-removal** → On expiration, gate resumes normal enforcement; owner notified

**Abuse prevention:**
- Max 3 exemptions per owner per quarter
- Exemptions > 14 days require @mbaetiong approval
- Quarterly review of waiver patterns (if >20% of domain waivered, reassign owner)

---

## 9. GLOSSARY: FRESHNESS TERMINOLOGY

| Term | Definition |
|------|-----------|
| **last_reviewed** | ISO date (YYYY-MM-DD) when a doc was last read and verified accurate by owner |
| **days_since_review** | `today - last_reviewed` |
| **review_frequency** | How often owner must review doc (30/90/180 days depending on category) |
| **stale threshold** | SLA boundary (`review_frequency + 5-day grace`); doc alerts when approaching |
| **critical doc** | High-visibility, API/security-sensitive doc; SLA 30 days |
| **general doc** | Mainstream user-facing doc; SLA 90 days |
| **archive doc** | Historical/immutable; no SLA |
| **FP (false positive)** | Automated link that appears broken but is valid (e.g., code fence pattern); waivered |
| **broken link** | Relative link target that does not exist in repo and is not an FP |
| **P0 link** | Critical broken link (code ref, API, security); blocks gate |
| **P1 link** | Important but non-blocking broken link; escalated but merge allowed |
| **P2 link** | Low-priority broken link (archive/historical); waivered by default |
| **Exemption** | Time-limited waiver for docs that cannot meet SLA due to external factors |

---

## 10. SUCCESS CRITERIA FOR PHASE 8.1

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| **Freshness signal adopted** | 100% of user-facing docs have `last_reviewed:` or manifest entry | Grep check for presence in all user-facing `.md` |
| **Cadence tiers defined** | Clear SLA for critical/general/low-priority | This document, sections 2.1–2.3 |
| **CI gate deployed** | Freshness gate enforces critical SLA ≥ critical doc, general SLA ≥ general docs | `.github/workflows/doc-freshness-gate.yml` runs on PR + schedule |
| **Automation baseline** | Weekly scorecards published; no manual stat-collection needed | CI artifacts + GitHub Discussions posts |
| **Owner buy-in** | 100% of owners briefed on cadence + SLAs | Briefing documented, sign-offs collected |

---

**Update Cadence Plan Status:** 🟢 COMPLETE — Workstream 8.1.2 planning deliverable  
**Generated:** 2026-07-03T02:25Z  
**Effective Date:** 2026-07-10 (after Phase 8.1.2a completion)  
**Implementation Begins:** Week 3 (8.1.3) with link fixes; CI gate deployment Week 5.5 (8.1.5)  
**Approver:** @mbaetiong (D-tier gate)
