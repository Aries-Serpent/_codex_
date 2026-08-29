# WEC Canonical Items — Active Workflow Baseline

**Version:** 1.2.0  
**Last Updated:** 2026-08-29  
**Source of Truth:** `scripts/ci/session_wrapup_autofix.py` and `scripts/ci/wec_enforcer.py`  
**Status:** Aligned to the live enabled workflow baseline for the current repo contract

This document reflects the repo's current active workflow surface. Historical or duplicate workflow names are intentionally not part of the live WEC contract. If a workflow is not present in `.github/workflows/` as an active file, it must not be required in the WEC block on the current PR SHA.

## Canonical active WEC items

### Required gates

| Workflow | Label | Required | Notes |
|----------|-------|----------|-------|
| `deferral-language-gate.yml` | Deferral language guard | ✅ Yes | Enforced by repo policy and merge gate. |
| `agent-auth-delegation.yml` | Agent token delegation | ✅ Yes | Required when the repo is using Copilot delegation. |
| `workflow-execution-gate.yml` | WEC gate | ✅ Yes | Must exist and be checked for merge readiness. |
| `cost-gate.yml` | Cost governance gate | ✅ Yes | Active reusable gate referenced by active pipelines. |
| `auto-approve-workflows` | Auto-approve pending workflows | ✅ Yes | Required to clear pending action_required runs on the current SHA. |

### Active-but-optional workflows

These remain in the live workflow baseline and can be selected as needed without creating stale WEC references:

- `auth-tests.yml`
- `audit-qa-suite.yml`
- `data-quality-suite.yml`
- `docker-build-push.yml`
- `nox_gates.yml`
- `security-scanning-suite.yml`
- `test-rag.yml`
- `scheduled-archival.yml`
- `scheduled-dependency-audit.yml`

## Required rules

- The WEC block must list only active baseline workflows.
- Legacy names such as `pre-merge-validation.yml`, `comment-review-gate.yml`, `unified-copilot-management.yml`, and `pages-pre-merge-validation.yml` are not valid live required entries unless those files are re-enabled in the active workflow directory.
- `auto-approve-workflows` is the live approval path used to resolve pending `action_required` workflow runs on the current SHA.
- The WEC contract is enforced by `scripts/ci/session_wrapup_autofix.py` and validated by `scripts/ci/wec_enforcer.py`.

## Canonical PR body block

```markdown
## 🔄 Workflow Execution Checklist

### ✅ Always Required — fire automatically on every push (cannot be skipped)
- [x] deferral-language-gate.yml — Deferral language guard (always required)
- [x] agent-auth-delegation.yml — Agent token delegation (always required)
- [x] workflow-execution-gate.yml — WEC gate — parse checklist & arm allowed workflows (always required)
- [x] cost-gate.yml — Cost governance gate (called by agent-auth-delegation)
- [x] auto-approve-workflows — Auto-Approve workflow to run (approves all pending runs on last commit SHA)

### 🔄 Active Workflows — currently enabled in the live repo baseline
- [ ] auth-tests.yml — Authentication Tests
- [ ] audit-qa-suite.yml — Audit & QA Suite (Unified)
- [ ] data-quality-suite.yml — Data Quality & Determinism Suite
- [ ] docker-build-push.yml — Build & push Docker image (GHCR)
- [ ] nox_gates.yml — Nox quality gates (ruff, mypy, coverage)
- [ ] security-scanning-suite.yml — Full security audit (bandit, pip-audit)
- [ ] test-rag.yml — RAG Module Tests (coverage ≥95%)
- [ ] scheduled-archival.yml — Scheduled archival
- [ ] scheduled-dependency-audit.yml — Dependency audit
```

This must remain aligned with the current expression-based CCA contract and the repo's active workflow set; it is not a historical or archived workflow index.

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
