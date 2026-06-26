# WEC Canonical Items — Authoritative Workflow Checklist

**Version:** 1.0.0  
**Last Updated:** 2026-06-26  
**Source of Truth:** `scripts/ci/session_wrapup_autofix.py` (line numbers to be verified in Phase 3.1 implementation)  
**Status:** APPROVED for all PRs merging to main or 0D_base_

---

## Purpose

This document defines the **canonical list of all Workflow Execution Checklist (WEC) items** that appear in PR bodies. It serves as the single source of truth for:

1. Which workflows are included in WEC
2. Which workflows are REQUIRED vs OPTIONAL for each merge target
3. Merge-blocking rules per workflow
4. Auto-approval prerequisites

---

## Canonical WEC Items (9 Total)

### Item 1: pre-merge-validation.yml

| Attribute | Value |
|-----------|-------|
| **Filename** | pre-merge-validation.yml |
| **Display Label** | Pre-merge checks |
| **Required for main** | ✅ YES — ALWAYS CHECK |
| **Required for 0D_base_** | ✅ YES — ALWAYS CHECK |
| **Auto-Approve Prerequisite** | Must be auto-approved BEFORE merge approval |
| **Purpose** | Final validation before merge (code quality, tests, security) |
| **Failure Mode** | Blocks merge if any check fails |
| **Owner Agent** | workflow-health-monitor |

---

### Item 2: comment-review-gate.yml

| Attribute | Value |
|-----------|-------|
| **Filename** | comment-review-gate.yml |
| **Display Label** | Comment review gate |
| **Required for main** | ✅ YES — ALWAYS CHECK |
| **Required for 0D_base_** | ✅ YES — ALWAYS CHECK |
| **Auto-Approve Prerequisite** | Must validate all bot/maintainer comments addressed |
| **Purpose** | Enforce addressing of critical bot comments & maintainer feedback |
| **Failure Mode** | Blocks merge if unresolved comments detected |
| **Owner Agent** | unified-governance-gate |
| **Related Policy** | CODEBASE_AGENCY_POLICY.md §0 — Mandatory pre-session review |

---

### Item 3: deferral-language-gate.yml

| Attribute | Value |
|-----------|-------|
| **Filename** | deferral-language-gate.yml |
| **Display Label** | Deferral language guard |
| **Required for main** | ✅ YES — ALWAYS CHECK |
| **Required for 0D_base_** | ✅ YES — ALWAYS CHECK |
| **Auto-Approve Prerequisite** | Commit messages & PR body must not contain deferral phrases |
| **Purpose** | Enforce "fix all issues now" mandate per Codebase Agency Policy |
| **Failure Mode** | Blocks merge if deferral phrases detected |
| **Owner Agent** | policy-coach-agent |
| **Deferral Triggers** | "will address later", "pre-existing issue", "out of scope", etc. |

---

### Item 4: agent-auth-delegation.yml

| Attribute | Value |
|-----------|-------|
| **Filename** | agent-auth-delegation.yml |
| **Display Label** | Agent token delegation |
| **Required for main** | ✅ YES (if agent-delegated PR) |
| **Required for 0D_base_** | ✅ YES (if agent-delegated PR) |
| **Auto-Approve Prerequisite** | Token delegation must complete BEFORE auto-approve |
| **Purpose** | Validate agent auth tokens & inject delegated permissions |
| **Failure Mode** | Blocks merge if delegation validation fails |
| **Owner Agent** | cognitive-brain-cli-agent |
| **Trigger Condition** | Only required for PRs with `copilot/` or `feature/` prefix |

---

### Item 5: workflow-execution-gate.yml

| Attribute | Value |
|-----------|-------|
| **Filename** | workflow-execution-gate.yml |
| **Display Label** | WEC gate |
| **Required for main** | ✅ YES — ALWAYS CHECK |
| **Required for 0D_base_** | ✅ YES — ALWAYS CHECK |
| **Auto-Approve Prerequisite** | WEC state must be valid before approval |
| **Purpose** | Enforce WEC checklist integrity & detect workflow intent changes |
| **Failure Mode** | Blocks merge if WEC is malformed or required items unchecked |
| **Owner Agent** | unified-governance-gate |
| **Actions** | Cancel runs for unchecked workflows; dispatch for newly-checked workflows |

---

### Item 6: copilot-agent-checkin.yml

| Attribute | Value |
|-----------|-------|
| **Filename** | copilot-agent-checkin.yml |
| **Display Label** | Agent check-in |
| **Required for main** | ❌ NO — OPTIONAL |
| **Required for 0D_base_** | ❌ NO — OPTIONAL |
| **Auto-Approve Prerequisite** | None |
| **Purpose** | Agent status reporting & session diagnostics |
| **Failure Mode** | Non-blocking; informational only |
| **Owner Agent** | session-analysis-agent |
| **Recommendation** | Check if agent diagnostics/status reporting needed |

---

### Item 7: copilot-agent-session-done.yml

| Attribute | Value |
|-----------|-------|
| **Filename** | copilot-agent-session-done.yml |
| **Display Label** | Auto-post review |
| **Required for main** | ❌ NO — OPTIONAL |
| **Required for 0D_base_** | ❌ NO — OPTIONAL |
| **Auto-Approve Prerequisite** | None |
| **Purpose** | Automatic post-session review comment |
| **Failure Mode** | Non-blocking |
| **Owner Agent** | session-analysis-agent |
| **Recommendation** | Uncheck if session review already posted manually |

---

### Item 8: copilot-iterative-self-healing.yml

| Attribute | Value |
|-----------|-------|
| **Filename** | copilot-iterative-self-healing.yml |
| **Display Label** | Iterative self-healing |
| **Required for main** | ❌ NO — OPTIONAL |
| **Required for 0D_base_** | ❌ NO — OPTIONAL |
| **Auto-Approve Prerequisite** | None |
| **Purpose** | Automated CI failure diagnosis and fixing loops |
| **Failure Mode** | Non-blocking |
| **Owner Agent** | self-healing-orchestrator-agent |
| **Recommendation** | Check if CI failures expected; self-healing will attempt fixes |

---

### Item 9: cost-gate.yml

| Attribute | Value |
|-----------|-------|
| **Filename** | cost-gate.yml |
| **Display Label** | Cost governance gate |
| **Required for main** | ❌ NO — OPTIONAL |
| **Required for 0D_base_** | ❌ NO — OPTIONAL |
| **Auto-Approve Prerequisite** | If checked: cost impact must be within budget |
| **Purpose** | Cost governance & budget enforcement |
| **Failure Mode** | Blocks merge if cost exceeds budget threshold |
| **Owner Agent** | cache-management-agent |
| **Recommendation** | Check if deployment/resource changes expected to impact costs |

---

## WEC Format & Syntax

### Standard PR Body Section

```markdown
## 🔄 Workflow Execution Checklist

Select workflows to execute for this PR. **REQUIRED items must be checked to merge.**

### REQUIRED for All Merges
- [x] pre-merge-validation.yml — Pre-merge checks
- [x] comment-review-gate.yml — Comment review gate
- [x] deferral-language-gate.yml — Deferral language guard
- [x] agent-auth-delegation.yml — Agent token delegation
- [x] workflow-execution-gate.yml — WEC gate

### OPTIONAL - Select as Needed
- [x] copilot-agent-checkin.yml — Agent check-in
- [ ] copilot-agent-session-done.yml — Auto-post review
- [x] copilot-iterative-self-healing.yml — Iterative self-healing
- [ ] cost-gate.yml — Cost governance gate
```

### Validation Rules

| Rule | Requirement |
|------|-------------|
| **Checkbox Format** | Must be `[x]` (checked) or `[ ]` (unchecked); no other formats |
| **Section Header** | Must be `## 🔄 Workflow Execution Checklist` (exact text) |
| **Item Format** | `- [x/·] FILENAME — Label` (one item per line) |
| **Required Items** | Items 1-5 MUST all be present and correctly formatted for any PR |
| **Optional Items** | Items 6-9 MAY be missing if not applicable to session |
| **Appendable** | WEC may be appended to in future sessions if new workflows added |

---

## Merge Target Rules

### Merge to `main` Branch

| Item | Check? | Blocking? | Notes |
|------|--------|-----------|-------|
| pre-merge-validation.yml | ✅ MUST | ✅ YES | All main merges require pre-merge validation |
| comment-review-gate.yml | ✅ MUST | ✅ YES | All maintainer comments must be addressed |
| deferral-language-gate.yml | ✅ MUST | ✅ YES | Policy enforcement required |
| agent-auth-delegation.yml | ✅ MUST (if agent PR) | ✅ YES | Required for copilot/* or feature/* branches |
| workflow-execution-gate.yml | ✅ MUST | ✅ YES | WEC gate always required |
| copilot-agent-checkin.yml | ❌ OPTIONAL | ❌ NO | Agent diagnostics optional |
| copilot-agent-session-done.yml | ❌ OPTIONAL | ❌ NO | Auto-review optional |
| copilot-iterative-self-healing.yml | ❌ OPTIONAL | ❌ NO | Self-healing optional |
| cost-gate.yml | ❌ OPTIONAL | ❌ NO | Cost gate optional |

**Merge Blocked If:**
- Any REQUIRED item is unchecked
- Any REQUIRED item has invalid format
- WEC section is missing

---

### Merge to `0D_base_` (Integration Branch)

| Item | Check? | Blocking? | Notes |
|------|--------|-----------|-------|
| pre-merge-validation.yml | ✅ MUST | ✅ YES | Staging branch also requires validation |
| comment-review-gate.yml | ✅ MUST | ✅ YES | Comment gate required |
| deferral-language-gate.yml | ✅ MUST | ✅ YES | Policy enforcement |
| agent-auth-delegation.yml | ✅ MUST (if agent PR) | ✅ YES | Token delegation if agent-delegated |
| workflow-execution-gate.yml | ✅ MUST | ✅ YES | WEC gate required |
| Others | ❌ OPTIONAL | ❌ NO | Staging policy more lenient |

---

## Auto-Approval Prerequisites

### When Workflow Can Be Auto-Approved

A workflow can be auto-approved (via `auto-approve-workflows.yml`) if:

1. **Workflow is CHECKED in WEC** ✅
2. **Workflow is in `action_required` state** (awaiting approval)
3. **Token has `actions:write` scope** (CODEX_MASTER_KEY or CODEX_BACKUP_KEY)
4. **No override rules apply** (see exceptions below)

### Auto-Approval Exceptions

| Workflow | Auto-Approvable? | Exception |
|----------|------------------|-----------|
| pre-merge-validation.yml | ❌ NO | Passes/fails autonomously; no manual approval needed |
| comment-review-gate.yml | ❌ NO | Non-blocking informational gate; auto-passes |
| deferral-language-gate.yml | ❌ NO | Non-blocking; auto-passes |
| agent-auth-delegation.yml | ✅ YES | Can be auto-approved if checked in WEC |
| workflow-execution-gate.yml | ❌ NO | Dispatcher workflow; doesn't require approval |
| copilot-agent-checkin.yml | ❌ NO | Informational; auto-passes |
| copilot-agent-session-done.yml | ✅ YES | Can be auto-approved if checked |
| copilot-iterative-self-healing.yml | ✅ YES | Can be auto-approved if checked |
| cost-gate.yml | ⚠️ MAYBE | Depends on cost impact; may need human review |

---

## WEC Item Ownership

| Item | Responsible Agent(s) | Repository Contact |
|------|---------------------|-------------------|
| pre-merge-validation.yml | unified-governance-gate | @mbaetiong |
| comment-review-gate.yml | unified-governance-gate, policy-coach-agent | @mbaetiong |
| deferral-language-gate.yml | policy-coach-agent | @mbaetiong |
| agent-auth-delegation.yml | cognitive-brain-cli-agent | @mbaetiong |
| workflow-execution-gate.yml | unified-governance-gate | @mbaetiong |
| copilot-agent-checkin.yml | session-analysis-agent | @mbaetiong |
| copilot-agent-session-done.yml | session-analysis-agent | @mbaetiong |
| copilot-iterative-self-healing.yml | self-healing-orchestrator-agent | @mbaetiong |
| cost-gate.yml | cache-management-agent | @mbaetiong |

---

## Testing & Validation

### Syntax Validation

```bash
# Check WEC format in PR body
python scripts/ci/wec_enforcer.py --validate-body --pr N
```

### Consistency Check

```bash
# Verify all items in this document are in session_wrapup_autofix.py
python scripts/ci/wec_enforcer.py --list-items --json | \
  jq '.items | length' # Should equal 9
```

### Required Items Check

```bash
# Verify required items are checked for main branch merges
gh pr view N --json body | jq -r '.body' | \
  grep -E "pre-merge-validation|comment-review-gate|workflow-execution-gate" | \
  grep "\[x\]" | wc -l  # Should be >= 3
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-06-26 | Initial canonical list; 9 items defined; merge rules established |

---

## Related Documentation

- **WEC Session Invariant:** `.codex/WEC_SESSION_INVARIANT.md`
- **WEC PR Body Conflicts:** `docs/workflows/WEC_PR_BODY_CONFLICTS.md`
- **Workflow Execution Gate:** `.github/workflows/workflow-execution-gate.yml`
- **Session Wrapup Tool:** `scripts/ci/session_wrapup_autofix.py`
- **Governance Policy:** `.codex/CODEBASE_AGENCY_POLICY.md`
