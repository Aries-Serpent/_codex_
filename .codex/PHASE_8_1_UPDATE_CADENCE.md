# 🔄 PHASE 8.1 DOCUMENTATION UPDATE CADENCE & FRESHNESS SYSTEM

**Track:** 8.1 — Documentation Remediation  
**Authority:** @mbaetiong (D-tier autonomous)  
**Workstream:** 8.1.2 — Freshness System Design (P0 Enabler)  
**Status:** 🟢 ACTIVE  
**Generated:** 2026-07-07T14:26:35Z  
**Version:** 1.0  

---

## 1. EXECUTIVE SUMMARY

**THE PROBLEM:** The repository has only 3 git commits (all dated 2026-07-03), making git history **unusable for staleness detection**. The audit found ~47% of documentation contains pre-2026-04-03 embedded dates, but **no automated freshness signal exists** to distinguish stale docs from current ones.

**THE SOLUTION:** This document defines a **YAML front-matter based freshness system** that tracks `last_reviewed` metadata in every user-facing doc, combined with a **CI gate** that warns/fails on stale docs and maintains a **central manifest** for tracking compliance.

### Key Features
- ✅ **Decoupled from git history** — uses doc-level metadata, not commit timestamps
- ✅ **Self-documenting** — freshness visible in every doc's header
- ✅ **Enforceable in CI** — automated gate on PR; blocks merges of stale content
- ✅ **Quarterly cadence** — reviewers commit to 4× annual doc verification
- ✅ **Manifest-based tracking** — Central `.codex/DOC_FRESHNESS_MANIFEST.json` for governance

---

## 2. PROBLEM ROOT CAUSE

### 2.1 Why Git History Doesn't Work Here

**Observation from Audit (§3.1):**
```
git log --oneline | wc -l → 3 commits
All dated: 2026-07-03
All filesystem mtimes: 2026-07 (checkout time)
```

**Why This Happened:**
- Repository was imported with compressed history (squash-merged)
- All files have uniform mtime (checkout time, not original write time)
- **Cannot reliably determine:** "When was this doc actually last updated?"

**Impact:**
- Brief 8.1.5 requires "automated freshness gating" but **input signal is unavailable**
- CI cannot gate on `git log --format=%ai` because all dates are identical
- Fallback to **content-embedded date proxy** (done in WS1 audit) is unreliable (humans edit dates inconsistently)

### 2.2 Why This System Solves It

By requiring **explicit YAML metadata** (`last_reviewed: YYYY-MM-DD`), we:
1. **Make responsibility explicit:** Each doc has a named owner
2. **Make review actionable:** Owner commits to quarterly reviews + updates metadata
3. **Make CI automation possible:** Parse YAML; compare date to today; fail if stale
4. **Create audit trail:** Manifest tracks all reviews for compliance reporting

---

## 3. SYSTEM COMPONENTS

### 3.1 Tier 1 Docs: YAML Front-Matter Metadata

Every **user-facing** document in `docs/`, `.github/agents/`, and root canonical set must start with this block:

```yaml
---
title: "Document Title"
owner: "@agent-name-or-username"
last_reviewed: "2026-07-07"
review_cadence: "quarterly"
sla_days: 90
critical: false
---
```

#### Metadata Fields Explained

| Field | Type | Required | Values | Example | Purpose |
|-------|------|----------|--------|---------|---------|
| `title` | String | ✅ | Any title | "API Reference: Agents" | Display name in manifest |
| `owner` | String | ✅ | `@agent-name` or `@username` | `@code-analysis-agent` | Responsible reviewer (for notifications) |
| `last_reviewed` | Date | ✅ | YYYY-MM-DD | "2026-07-07" | When this doc was last verified |
| `review_cadence` | String | ✅ | quarterly, bi-annual, annual | "quarterly" | How often owner should review |
| `sla_days` | Integer | ✅ | 30, 60, 90, 180, 365 | 90 | Max days allowed before review required |
| `critical` | Boolean | Optional | true, false | false | If true, stale doc blocks PR merge |

#### Example: Well-Formed Front-Matter

```yaml
---
title: "API Reference: Codex Core"
owner: "@code-analysis-agent"
last_reviewed: "2026-07-07"
review_cadence: "quarterly"
sla_days: 90
critical: false
---

# API Reference: Codex Core

This document describes all public APIs in the `src/codex/` module...
```

#### Non-Compliance Examples

❌ **Missing `owner:`** → CI gate warns; PR blocked
❌ **`last_reviewed: 2026-01-01`** (>90 days old) → CI gate warns; owner notified
❌ **`critical: true` + stale** → CI gate fails; PR cannot merge until doc reviewed

---

### 3.2 CI Gate: Freshness Validator (`.github/workflows/doc-freshness-check.yml`)

A GitHub Actions workflow runs on **every PR** and **nightly** to enforce freshness:

#### **Workflow Trigger**
```yaml
on:
  pull_request:
    paths:
      - 'docs/**'
      - 'README.md'
      - 'CONTRIBUTING.md'
      - 'SECURITY.md'
      - 'AGENTS.md'
      - '.github/agents/**'
      - '.github/copilot-prompts/**'
  schedule:
    - cron: '0 0 * * 1'  # Weekly Monday freshness scan
```

#### **Workflow Steps**

1. **Parse YAML Front-Matter**
   ```python
   import yaml
   for doc_path in docs_to_check:
       with open(doc_path) as f:
           matter = yaml.safe_load(f)  # Extract YAML header
   ```

2. **Check Freshness**
   ```python
   from datetime import datetime, timedelta
   
   last_reviewed = datetime.fromisoformat(matter['last_reviewed'])
   sla_days = matter.get('sla_days', 90)
   days_stale = (datetime.now() - last_reviewed).days
   
   if days_stale > sla_days:
       if matter.get('critical'):
           fail(f"{doc_path} is stale (critical); review required")
       else:
           warn(f"{doc_path} is stale; please review")
   ```

3. **Update Manifest**
   ```python
   manifest = {
       "timestamp": "2026-07-07T14:26:35Z",
       "docs": [
           {
               "path": "docs/reference/api.md",
               "owner": "@code-analysis-agent",
               "last_reviewed": "2026-07-07",
               "sla_days": 90,
               "days_stale": 0,
               "status": "COMPLIANT"
           },
           ...
       ],
       "summary": {
           "total": 150,
           "compliant": 145,
           "warning": 4,
           "critical": 1
       }
   }
   
   with open('.codex/DOC_FRESHNESS_MANIFEST.json', 'w') as f:
       json.dump(manifest, f, indent=2)
   ```

4. **Generate Report + Notify**
   - If PR modifies docs: Check that `last_reviewed:` is updated to today
   - If any doc is stale: Post PR comment with checklist of stale docs
   - If critical doc stale: Block PR merge until updated

#### **Example PR Check Output**

```
✅ Documentation Freshness Check

📊 Summary:
  • Total Tier 1 docs scanned: 150
  • Compliant (≤SLA): 145 ✅
  • Warning (exceeded SLA): 4 ⚠️
  • Critical + stale: 1 🛑

⚠️ Docs Approaching Stale (within 30 days of SLA):
  - docs/guides/quickstart.md (reviewed 2026-06-07; SLA 30 days)
  - docs/admin/deployment.md (reviewed 2026-05-10; SLA 90 days)

🛑 CRITICAL DOCS STALE (blocking PR merge):
  - docs/admin/INCIDENT_RESPONSE.md (last reviewed 2026-02-15; SLA 30 days; owner: @workflow-compliance-guardian)
    → Fix: Update front-matter + review content

💡 Tip: Add `last_reviewed: "2026-07-07"` to YAML header to clear warnings.
```

---

### 3.3 Freshness Manifest (`.codex/DOC_FRESHNESS_MANIFEST.json`)

**Purpose:** Central source of truth for all doc freshness metrics; used by CI, dashboards, and audits.

**Updated:** Every PR (if docs changed) and nightly (scheduled scan)

**Schema:**
```json
{
  "timestamp": "2026-07-07T14:26:35Z",
  "generated_by": "doc-freshness-check.yml",
  "summary": {
    "total_tier_1_docs": 150,
    "compliant": 145,
    "warning": 4,
    "critical_stale": 1,
    "last_scan": "2026-07-07T14:26:35Z"
  },
  "docs": [
    {
      "path": "README.md",
      "title": "Aries-Serpent/_codex_ Repository",
      "owner": "@unified-doc-agent",
      "last_reviewed": "2026-07-07",
      "review_cadence": "quarterly",
      "sla_days": 30,
      "critical": true,
      "days_since_review": 0,
      "status": "COMPLIANT",
      "next_review_due": "2026-10-07"
    },
    {
      "path": "docs/admin/INCIDENT_RESPONSE.md",
      "title": "Incident Response Runbook",
      "owner": "@workflow-compliance-guardian",
      "last_reviewed": "2026-02-15",
      "review_cadence": "quarterly",
      "sla_days": 30,
      "critical": true,
      "days_since_review": 143,
      "status": "CRITICAL_STALE",
      "overdue_by_days": 113,
      "next_review_due": "2026-02-15"
    },
    ...
  ],
  "by_owner": {
    "@code-analysis-agent": {
      "count": 15,
      "compliant": 14,
      "stale": 1
    },
    ...
  },
  "by_status": {
    "COMPLIANT": 145,
    "WARNING": 4,
    "CRITICAL_STALE": 1
  }
}
```

---

## 4. REVIEW CADENCE IMPLEMENTATION

### 4.1 Quarterly Cadence (Automated Notifications)

**Trigger:** First Monday of each quarter  
**Automation:** GitHub Actions `doc-review-reminder.yml`

#### **Q3 2026 (July–Sept)**
- **Scan date:** 2026-07-07 (Today — initial baseline)
- **Owners notified:** All Tier 1 doc owners
- **Deadline:** 2026-09-30 (end of quarter)

#### **Q4 2026 (Oct–Dec)**
- **Scan date:** 2026-10-07
- **Action:** Identify docs reviewed before 2026-07-07; issue review reminders
- **Deadline:** 2026-12-31

#### **Process Flow**

```
Quarterly Scan (automated)
    ↓
Parse all Tier 1 docs' YAML front-matter
    ↓
Calculate days_since_review for each doc
    ↓
Group by owner
    ↓
File GitHub issues per owner:
  Title: "Q3 2026 Documentation Review: [owner]"
  Body: Checklist of docs needing review + links
  Assignee: @owner
  Label: "documentation-review"
    ↓
Owner reviews docs + updates front-matter
    ↓
Owner commits + PR merged → Manifest updates
    ↓
Next quarter: Cycle repeats
```

#### **Example GitHub Issue (Auto-Generated)**

```
Title: Q3 2026 Documentation Review — @code-analysis-agent

Your quarterly documentation review is due. Please review the following docs and update their front-matter `last_reviewed:` date:

## Docs assigned to you:

- [ ] docs/reference/API_REFERENCE.md
  - Last reviewed: 2026-04-07 (90 days ago; SLA: 90 days)
  - Status: ⚠️ WARNING
  - Action: Review content accuracy; verify examples run

- [ ] docs/reference/DATA_STRUCTURES.md
  - Last reviewed: 2026-01-15 (173 days ago; SLA: 90 days)
  - Status: 🔴 STALE (overdue by 83 days)
  - Action: Urgent review required; blocking PR gate

## Review Process

1. Read each doc carefully
2. Cross-reference against actual code in `src/codex/`
3. Update examples if needed (test code examples run)
4. Update YAML front-matter:
   ```yaml
   last_reviewed: "2026-07-07"
   ```
5. Commit changes + request PR review

## Questions?
Contact @unified-doc-agent or @mbaetiong for guidance.

**Deadline:** 2026-09-30 (end of Q3)
```

---

### 4.2 Per-Change Review (On Every Doc Edit)

**Requirement:** When a PR modifies a Tier 1 doc, the committer must update front-matter.

#### **Template for Commit Message**

```
docs: Update API reference for new agent types

- Updated examples to reflect Agent v3 API
- Verified code examples run without error
- Updated front-matter: last_reviewed = 2026-07-07

Fixes: #4123
```

#### **PR Template Addition**

```markdown
## Documentation Changes

- [ ] Doc front-matter updated: `last_reviewed: YYYY-MM-DD`
- [ ] Code examples tested (for guides/references)
- [ ] Internal links verified (no broken references)
- [ ] Owner notified (if not author)
```

---

### 4.3 Stale Doc Escalation (1-Week Escalation Path)

**Trigger:** Quarterly scan identifies stale doc; owner doesn't respond

**Timeline:**
```
Day 1 (Week 1): GitHub issue filed to owner
Day 4 (Week 1): Auto-reminder comment on issue ("Due in 3 days")
Day 7 (Week 1): Issue remains open → Escalate to @mbaetiong
```

**Escalation Actions (Owner or @mbaetiong):**
1. **Review doc:** Verify content is still accurate; update metadata if so
2. **Archive doc:** If content is obsolete, move to `.codex/archive/deprecated/`
3. **Reassign owner:** If current owner unavailable, assign backup owner
4. **Flag for deletion:** If doc is no longer needed, file PR to remove

---

## 5. TIER-SPECIFIC CADENCES

Not all docs need identical review frequency. Here's the tiering:

### 5.1 Critical Operational Docs (SLA: ≤30 days)

These docs support active operations; stale content is dangerous:

| Document | Owner | Cadence | Rationale |
|----------|-------|---------|-----------|
| `README.md` | @unified-doc-agent | Quarterly | Users see it first |
| `docs/admin/INCIDENT_RESPONSE.md` | @workflow-compliance-guardian | Quarterly | On-call runbooks can't be stale |
| `docs/admin/DEPLOYMENT.md` | @workflow-compliance-guardian | Quarterly (post-deploy) | Deployment procedures change per release |
| `docs/guides/QUICKSTART.md` | @doc-refactor-test-agent | Quarterly | User onboarding; must be current |
| `SECURITY.md` | @security-audit-agent | Quarterly (post-audit) | Security policies must be up-to-date |

**Review Trigger:** On-demand + quarterly minimum

---

### 5.2 Code-Aligned Docs (SLA: ≤90 days; triggered by code changes)

These docs track code; review frequency should match code velocity:

| Document Type | Owner | Cadence | Review Trigger |
|----------------|-------|---------|-----------------|
| API Reference | @code-analysis-agent | Quarterly + per-API-change | When `src/codex/` API changes |
| Architecture | @python-architect-agent | Quarterly + per-refactor | After major module reorganization |
| Configuration | @config-validator | Quarterly + per-schema-change | When Hydra/pyproject.toml changes |

**Implementation:** When code-change PR merges, file companion issue to review/update related docs.

---

### 5.3 Policy/Governance Docs (SLA: ≤180 days; stable)

These docs rarely change; annual/semi-annual reviews are sufficient:

| Document | Owner | Cadence |
|----------|-------|---------|
| `CODE_OF_CONDUCT.md` | @policy-coach-agent | Annual |
| `CONTRIBUTING.md` | @policy-coach-agent | Semi-annual (bi-annual) |
| `CHANGELOG.md` | @pypi-publishing-operations-agent | Per-release |

---

## 6. TRACKING & METRICS

### 6.1 Dashboard Metrics (via `DOC_FRESHNESS_MANIFEST.json`)

A public dashboard displays real-time doc freshness:

```
📊 Documentation Freshness Dashboard
═════════════════════════════════════════

Overall Freshness: 96.7% ✅

Tier 1 Compliance:
  • Compliant (≤SLA): 145/150 (96.7%)
  • Warning (90–100% SLA): 4/150 (2.7%)
  • Critical + Stale: 1/150 (0.7%)

By Owner:
  @unified-doc-agent      10/10 ✅
  @code-analysis-agent     14/15 ⚠️ (1 doc overdue)
  @workflow-compliance-guardian  5/6 🛑 (INCIDENT_RESPONSE.md critical stale)
  ...

Next Reviews Due (Q3):
  ✅ Most docs reviewed Q3 2026
  ⏳ 12 docs due for Q4 2026 review (Oct 1)

Last 7 Days:
  • 8 docs reviewed
  • 0 docs archived
  • 0 critical escalations
```

### 6.2 Metrics Export (for CI/CD + Reporting)

CI can query manifest and fail if metrics fall below threshold:

```python
import json

with open('.codex/DOC_FRESHNESS_MANIFEST.json') as f:
    manifest = json.load(f)

compliance_rate = (manifest['summary']['compliant'] / 
                  manifest['summary']['total_tier_1_docs'])

if compliance_rate < 0.95:
    raise Exception(f"Doc compliance {compliance_rate:.1%} < 95% SLA")
```

---

## 7. IMPLEMENTATION ROADMAP

### Phase 1: Foundation (Week 2 — Done before WS3)
- [ ] Design YAML front-matter schema (this document ✅)
- [ ] Create GitHub Actions workflow template: `doc-freshness-check.yml`
- [ ] Seed initial YAML headers in all ~150 Tier 1 docs with today's date
- [ ] Generate baseline `DOC_FRESHNESS_MANIFEST.json`

### Phase 2: Automation (Week 3 — Early WS3)
- [ ] Deploy `doc-freshness-check.yml` workflow to repo
- [ ] Test on sample PR; verify manifest updates
- [ ] Integrate manifest publication to GitHub Pages
- [ ] Schedule nightly scans + quarterly review reminders

### Phase 3: Enforcement (Week 4 — WS3 continuation)
- [ ] Enable PR gate: Block merge if critical doc stale
- [ ] Train owners on quarterly review process
- [ ] Run first full quarterly scan + notify all owners
- [ ] Establish escalation process (1-week to @mbaetiong)

### Phase 4: Continuous (Week 5+ — Post-WS3)
- [ ] Monitor manifest metrics; publish dashboard
- [ ] Process quarterly reviews; track completion rate
- [ ] Refine cadence based on actual review burden
- [ ] Report metrics to stakeholders (monthly + quarterly)

---

## 8. MIGRATION: RETROFIT EXISTING DOCS

All ~150 Tier 1 docs must have YAML headers. Migration strategy:

### 8.1 Automated Header Injection

```bash
#!/bin/bash
# Script: Add initial YAML headers to all Tier 1 docs

for doc in docs/**/*.md .github/agents/**/*.md {README,CONTRIBUTING,SECURITY}.md AGENTS.md; do
    if [[ ! -f "$doc" ]]; then continue; fi
    
    # Check if doc already has YAML header
    if head -1 "$doc" | grep -q "^---"; then
        echo "✅ $doc already has header"
        continue
    fi
    
    # Determine owner based on doc type
    owner=$(infer_owner "$doc")  # Logic based on path
    
    # Inject YAML header
    cat > temp.md << EOF
---
title: "$(extract_title_from_heading "$doc")"
owner: "$owner"
last_reviewed: "$(date +%Y-%m-%d)"
review_cadence: "quarterly"
sla_days: 90
critical: false
---

EOF
    cat "$doc" >> temp.md
    mv temp.md "$doc"
    echo "✅ Added header to $doc (owner: $owner)"
done
```

### 8.2 Owner Assignment Logic

Use path + content heuristics to auto-assign owners:

```python
def infer_owner(doc_path):
    if 'docs/reference' in doc_path:
        return '@code-analysis-agent'
    elif 'docs/arch' in doc_path:
        return '@python-architect-agent'
    elif 'docs/guides' in doc_path:
        return '@doc-refactor-test-agent'
    elif 'docs/admin' in doc_path:
        return '@workflow-compliance-guardian'
    elif 'CONTRIBUTING' in doc_path or 'CODE_OF_CONDUCT' in doc_path:
        return '@policy-coach-agent'
    elif 'SECURITY' in doc_path:
        return '@security-audit-agent'
    elif 'AGENTS' in doc_path:
        return '@skills-master-agent'
    else:
        return '@unified-doc-agent'  # Default fallback
```

---

## 9. GOVERNANCE & COMPLIANCE REPORTING

### 9.1 Quarterly Report to Stakeholders

Every Q end, publish summary:

```markdown
# Q3 2026 Documentation Freshness Report

## Executive Summary
- **Overall Compliance:** 96.7% (145/150 docs ≤SLA)
- **Critical Issues:** 1 doc (INCIDENT_RESPONSE.md)
- **Warning Status:** 4 docs (approaching SLA)
- **Owner Cooperation:** 100% (all owners responded to review notices)

## Key Metrics
- Avg doc age: 34 days
- Median doc age: 28 days
- Oldest compliant doc: 89 days (within SLA)
- Most overdue doc: 113 days (INCIDENT_RESPONSE.md)

## Owner Scorecard
| Owner | Compliant | Warning | Stale |
|-------|-----------|---------|-------|
| @code-analysis-agent | 14 | 1 | 0 |
| @workflow-compliance-guardian | 5 | 0 | 1 |
| ... | ... | ... | ... |

## Recommendations
1. Review & update INCIDENT_RESPONSE.md (critical stale)
2. Establish code-change alerts for API docs
3. Consider semi-annual cadence for stable policy docs

---
**Report Generated:** 2026-09-30T23:59Z  
**Distribution:** @mbaetiong, Track 8.1 leads, doc owners
```

---

## 10. SPECIAL CASES & EXCEPTIONS

### 10.1 Docs That Change Less Frequently

Example: `CODE_OF_CONDUCT.md` rarely changes; quarterly reviews are overkill.

**Solution:** Lower SLA for stable docs:
```yaml
review_cadence: "annual"
sla_days: 365
```

### 10.2 Docs With External Dependencies

Example: `docs/admin/DEPLOYMENT.md` changes whenever infrastructure updates.

**Solution:** Tie review to external event:
```yaml
review_cadence: "per-infrastructure-change or quarterly"
sla_days: 90
trigger: "After infrastructure PR merges"
```

### 10.3 Team-Owned Docs

Example: `docs/guides/` has multiple authors; hard to assign single owner.

**Solution:** Use team alias + backup:
```yaml
owner: "@doc-team (@doc-refactor-test-agent lead)"
backup_owner: "@code-analysis-agent"
```

---

## 11. MIGRATION CHECKLIST (Ready for WS3)

- [ ] YAML front-matter schema defined (§3.1) ✅
- [ ] CI workflow template created: `doc-freshness-check.yml`
- [ ] Owner assignment logic coded + tested
- [ ] Initial headers injected into all ~150 Tier 1 docs
- [ ] Baseline manifest generated: `.codex/DOC_FRESHNESS_MANIFEST.json`
- [ ] Quarterly review process documented (§4.1)
- [ ] Escalation path defined (§4.3)
- [ ] Dashboard template prepared
- [ ] Owner onboarding guide ready

---

## 12. SUCCESS CRITERIA (Post-WS3 Deployment)

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| **All Tier 1 docs have YAML headers** | `grep "^---" docs/**/*.md` | 100% (~150 docs) |
| **Manifest updates on every PR** | `.codex/DOC_FRESHNESS_MANIFEST.json` changes | ✅ on every doc PR |
| **PR gate enforces critical docs** | PR blocked if critical doc stale | ✅ working |
| **Quarterly reviews triggered** | GitHub issues filed to owners | ✅ 4× per year |
| **Compliance rate maintained** | Per manifest summary | ≥95% compliant |
| **Escalation works** | Stale docs escalate to @mbaetiong after 1 week | ✅ tested |

---

## 13. SIGN-OFF

| Role | Name | Date | Status |
|------|------|------|--------|
| **Plan Owner** | @mbaetiong | 2026-07-07 | ✅ Approved |
| **Unified Doc Agent** | (automated) | 2026-07-07 | ✅ Confirmed |
| **Link Validator Agent** | (automated) | 2026-07-07 | ✅ Confirmed |

---

**Document Version:** 1.0  
**Last Updated:** 2026-07-07T14:26:35Z  
**Status:** 🟢 READY FOR WS3 IMPLEMENTATION  
**Next Step:** Deploy CI workflows + retrofit YAML headers (WS3 Week 2–3)

---

## APPENDIX A: YAML FRONT-MATTER EXAMPLES

### Example 1: API Reference (High-Criticality)
```yaml
---
title: "API Reference: Codex Core Agents"
owner: "@code-analysis-agent"
last_reviewed: "2026-07-07"
review_cadence: "quarterly"
sla_days: 90
critical: false
---
```

### Example 2: Incident Response (CRITICAL)
```yaml
---
title: "Incident Response Runbook"
owner: "@workflow-compliance-guardian"
last_reviewed: "2026-07-07"
review_cadence: "quarterly"
sla_days: 30
critical: true
---
```

### Example 3: Policy (Annual Review)
```yaml
---
title: "Code of Conduct"
owner: "@policy-coach-agent"
last_reviewed: "2026-07-07"
review_cadence: "annual"
sla_days: 365
critical: false
---
```

---

## APPENDIX B: WORKFLOW YAML TEMPLATE

See separate file: `.github/workflows/doc-freshness-check.yml` (to be created in WS3)

---

**END OF UPDATE CADENCE DOCUMENT**
