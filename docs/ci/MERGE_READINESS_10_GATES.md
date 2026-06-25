# Pre-Merge Validation Gates — Complete Reference

**Status:** ✅ Authoritative Gate Definitions  
**Last Updated:** 2026-06-25  
**Audience:** PR reviewers, CI/CD engineers, Copilot agents

---

## Overview

The **Pre-Merge Readiness System** uses 10 weighted validation gates to determine whether a PR is ready for merge. Each gate is associated with a specific workflow, validation script, or manual check. Together, they form the **10-Gate Model** with a combined score of 0–100 points.

**Target:** All 10 gates must pass for 100% merge readiness.

---

## 10 Pre-Merge Validation Gates

### Gate 1: Code Quality (12 pts)

**Workflow:** `pre-merge-validation.yml` (always-checked)

**Purpose:** Ensure code follows style, type, and complexity standards.

**Validation Steps:**
1. Run Ruff linter: `python -m ruff check src/ tests/ --fix`
   - Must pass with 0 violations
   - Checks only E (error), F (Pyflakes), I (isort) rules
   - Per-file ignores: E402, F811 (test-only exceptions)

2. Run MyPy type checker: `python -m mypy src/ --ignore-missing-imports`
   - Must pass with all types covered
   - Reports errors if any function has untyped parameters or returns

**Failure Criterion:** Any ruff error or mypy error blocks merge

**PR Body Impact:**
- Record: "✅ Code Quality (12/12): 0 ruff errors, all types typed"
- Or: "❌ Code Quality (0/12): 15 ruff errors in src/, 3 mypy errors. Fix required."

**Weight:** 12 points

---

### Gate 2: Test Coverage (12 pts)

**Workflow:** `pre-merge-validation.yml`

**Purpose:** Maintain minimum test coverage (≥95%).

**Validation Steps:**
1. Run pytest with coverage: `pytest --cov=src --cov=codex_ml --cov-report=json -q`
2. Parse coverage report: Extract total_coverage percentage
3. Compare to baseline (95%)
4. Calculate delta: current - baseline

**Failure Criterion:** Coverage < 95% blocks merge

**PR Body Impact:**
- Record coverage delta: "✅ Test Coverage (12/12): 96.5% (+1.7% from baseline)"
- Or: "❌ Test Coverage (0/12): 94.2% coverage (below 95% threshold, -0.8% delta)"

**Weight:** 12 points

---

### Gate 3: Security & Secrets (15 pts)

**Workflow:** `pre-merge-validation.yml` + `unified-security-scanner` agents

**Purpose:** Prevent accidental credential commits and catch code vulnerabilities.

**Validation Steps:**
1. Detect-secrets check:
   ```bash
   detect-secrets-hook --baseline .secrets.baseline $(git diff --name-only HEAD~1 HEAD)
   ```
   - Exit code 0 = pass (no new secrets)
   - Exit code ≠ 0 = fail (new secrets detected)

2. CodeQL alert count:
   ```bash
   gh api /repos/Aries-Serpent/_codex_/code-scanning/alerts?state=open --jq '.[] | select(.rule.severity=="error" or .rule.severity=="warning") | .number'
   ```
   - Count open alerts
   - Threshold: 0 new alerts introduced in this PR

3. Pip audit (CVE check):
   ```bash
   python -m pip_audit --skip-editable --desc
   ```
   - Exit code 0 = pass (no vulnerabilities)

**Failure Criterion:** Any new secrets detected OR new CodeQL errors > threshold OR pip audit failures

**PR Body Impact:**
- Record: "✅ Security & Secrets (15/15): 0 new secrets, 0 CodeQL errors, 0 pip vulnerabilities"
- Or: "❌ Security & Secrets (5/15): 1 CodeQL error (py/wrong-named-arg), 2 pip audit warnings. Partial credit for addressing py/ alert."

**Weight:** 15 points (highest weight — security critical)

---

### Gate 4: WEC Integrity (14 pts)

**Workflow:** `workflow-execution-gate.yml` (always-checked + orchestrator)

**Purpose:** Ensure Workflow Execution Checklist (WEC) is present and valid.

**Validation Steps:**
1. Check WEC section exists: `grep "## 🔄 Workflow Execution Checklist" pr_body`
2. Validate all 9 items present:
   - pre-merge-validation.yml
   - comment-review-gate.yml
   - deferral-language-gate.yml
   - agent-auth-delegation.yml
   - workflow-execution-gate.yml
   - copilot-agent-checkin.yml
   - copilot-agent-session-done.yml
   - copilot-iterative-self-healing.yml
   - cost-gate.yml

3. Validate always-required items are `[x]`:
   - pre-merge-validation.yml: MUST be `[x]`
   - comment-review-gate.yml: MUST be `[x]`
   - deferral-language-gate.yml: MUST be `[x]`
   - agent-auth-delegation.yml: MUST be `[x]`
   - workflow-execution-gate.yml: MUST be `[x]`
   - cost-gate.yml: MUST be `[x]`

**Failure Criterion:** Missing WEC section OR incomplete items OR always-required items unchecked → blocks merge

**PR Body Impact:**
- Record: "✅ WEC Integrity (14/14): All 9 items present, all always-required checked"
- Or: "❌ WEC Integrity (0/14): WEC section missing or incomplete. Add canonical WEC block."

**Weight:** 14 points (critical for workflow orchestration)

---

### Gate 5: Deferral Language Policy (10 pts)

**Workflow:** `deferral-language-gate.yml` (always-checked)

**Purpose:** Enforce affirmative language; prevent procrastination phrases.

**Prohibited Phrases (20+ patterns):**
- "This is not related to my PR"
- "These are pre-existing issues"
- "My PR only adds files to X"
- "Not my responsibility"
- "Will address in a future PR"
- "Can be deferred"
- "Pre-existing and safe"
- And 13+ more variants

**Validation Steps:**
1. Scan PR body, commits, comments for prohibited phrases
2. Use regex + optional ML classifier (TF-IDF)
3. Report any matches

**Failure Criterion:** Any prohibited phrase detected → blocks merge

**PR Body Impact:**
- Record: "✅ Deferral Language (10/10): No prohibited phrases detected"
- Or: "❌ Deferral Language (0/10): Phrase detected: 'These are pre-existing issues' in commit message. Reword to use affirmative language."

**Weight:** 10 points

---

### Gate 6: Comment Review Policy (12 pts)

**Workflow:** `comment-review-gate.yml` (always-checked)

**Purpose:** Ensure all blocking PR comments are addressed.

**Scanned Comment Authors (blocking):**
- `@mbaetiong` (maintainer)
- `github-actions[bot]` (CI/CD)
- `copilot-pull-request-reviewer[bot]` (code review)
- `github-advanced-security[bot]` (security alerts)
- `github-code-quality[bot]` (quality findings)

**Scanned Comment Authors (warning only):**
- `dependabot[bot]` (dependency updates)
- `codecov[bot]` (coverage tracking)

**Validation Steps:**
1. Fetch all PR comments via GitHub API
2. Filter by author (blocking list)
3. Check for resolution:
   - Comment marked as "Resolved" in conversation
   - OR agent replied with commit SHA pointing to fix
   - OR maintainer explicitly approved

**Failure Criterion:** Unresolved blocking comment from maintainer or security bot → blocks merge

**PR Body Impact:**
- Record: "✅ Comment Review (12/12): All 2 blocking comments resolved"
- Or: "❌ Comment Review (0/12): 1 unresolved comment from @mbaetiong: 'Fix the type error in line 123.' [Link to comment]"

**Weight:** 12 points

---

### Gate 7: Accountability Report & CHANGELOG (8 pts)

**Workflow:** Part of `pre-merge-validation.yml`

**Purpose:** Maintain audit trail of changes and session responsibility.

**Validation Steps:**
1. Check `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` updated in last commit
   ```bash
   git diff --name-only HEAD~1 HEAD | grep -q "AGENT_ACCOUNTABILITY_REPORT.md"
   ```

2. Check `CHANGELOG.md` updated in last commit
   ```bash
   git diff --name-only HEAD~1 HEAD | grep -q "CHANGELOG.md"
   ```

3. Validate entry format:
   - Timestamp included
   - Session ID recorded
   - Changes summarized
   - Author/agent recorded

**Auto-Fix Mechanism:**
- If either file missing from last commit, `session_wrapup_autofix.py --fix` runs automatically
- Appends minimal entry if needed (marks as "[auto-generated]")

**Failure Criterion:** Either file missing after auto-fix attempt → manual update required OR auto-fix succeeds (no blocking failure)

**PR Body Impact:**
- Record: "✅ Accountability (8/8): AGENT_ACCOUNTABILITY_REPORT.md + CHANGELOG.md updated in commit abc1234"
- Or: "⚠️ Accountability (8/8): Auto-fixed — entries generated in commit xyz5678"

**Weight:** 8 points

---

### Gate 8: Action Versions Enforcement (7 pts)

**Workflow:** Part of `pre-merge-validation.yml`

**Purpose:** Ensure all GitHub Actions use approved versions (security + stability).

**Approved Versions (as of 2026-06-22):**
- `actions/checkout@v5` (not v3, v4)
- `actions/setup-node@v5` (not v3, v4)
- `actions/github-script@v8` (not v7, older)
- `actions/setup-python@v6` (not v4, v5)
- `actions/upload-artifact@v5` (not v3, v4)

**Validation Steps:**
1. Scan all `.github/workflows/*.yml` files in PR
2. Extract GitHub Actions (format: `owner/action@version`)
3. Compare version against approved list
4. Auto-fix via: `python scripts/ci/enforce_actions_versions.py --fix`

**Failure Criterion:** Unapproved action version detected after auto-fix → blocks merge

**PR Body Impact:**
- Record: "✅ Action Versions (7/7): All actions use approved versions"
- Or: "✅ Action Versions (7/7): Auto-fixed 2 action versions (actions/checkout v4→v5, actions/setup-python v5→v6)"

**Weight:** 7 points

---

### Gate 9: YAML Workflow Syntax & Indentation (7 pts)

**Workflow:** Part of `pre-merge-validation.yml`

**Purpose:** Catch YAML parse errors and indentation issues before merge.

**Validation Steps:**
1. Run actionlint on all workflow files:
   ```bash
   actionlint .github/workflows/*.yml 2>&1 | grep -c error
   ```
   - Exit code 0 = pass (0 errors)
   - Exit code ≠ 0 = fail (errors found)

2. Run yamllint:
   ```bash
   yamllint .github/workflows/ --config-file .yamllint.yml
   ```
   - Checks indentation, key ordering, line length

**Common Issues Fixed:**
- Missing spaces after list markers (e.g., `- name:` vs `-name:`)
- Incorrect indentation under `steps:`, `branches:`, `paths:`
- Unquoted long strings with special characters
- Shell braces in flow scalars (must use `run: |`)

**Failure Criterion:** Any actionlint error OR yamllint error → blocks merge

**PR Body Impact:**
- Record: "✅ Workflow Syntax (7/7): 0 actionlint errors, 0 yamllint errors"
- Or: "❌ Workflow Syntax (0/7): 2 actionlint errors in test.yml, 1 yamllint error in build.yml. Run actionlint and yamllint locally to fix."

**Weight:** 7 points

---

### Gate 10: Merge Dependency Checks (3 pts)

**Workflow:** Part of `pre-merge-validation.yml`

**Purpose:** Verify branch is clean and ready for merge.

**Validation Steps:**
1. Check for unresolved merge conflicts:
   ```bash
   git diff --name-only --diff-filter=U
   ```
   - Must return empty (no unmerged files)

2. Verify branch up-to-date:
   - Compare PR base (usually `main`) to current branch
   - If diverged, confirm documented reason in PR body

3. Check branch protection rules:
   - All required status checks pass
   - All required reviews completed
   - No blocking dismissals

**Failure Criterion:** Unresolved conflicts OR outdated branch (without documented reason) → blocks merge

**PR Body Impact:**
- Record: "✅ Merge Dependencies (3/3): Branch clean, up-to-date with main, all protections satisfied"
- Or: "❌ Merge Dependencies (0/3): 2 unresolved merge conflicts in src/module.py. Resolve conflicts before merge."

**Weight:** 3 points (lowest weight — usually resolved by auto-merge)

---

## Merge Readiness Score Calculation

### Formula

```
merge_readiness_score = Σ(gate_weight × gate_pass_rate)

where:
  gate_pass_rate = 1.0 if gate passes
                 = 0.5 if gate partially passes (with documented gap)
                 = 0.0 if gate fails
```

### Example Score Calculation

| Gate | Weight | Status | Rate | Contribution |
|------|--------|--------|------|--------------|
| Code Quality | 12 | ✅ Pass | 1.0 | 12 |
| Test Coverage | 12 | ✅ Pass | 1.0 | 12 |
| Security | 15 | ⚠️ Partial | 0.5 | 7.5 |
| WEC Integrity | 14 | ✅ Pass | 1.0 | 14 |
| Deferral Language | 10 | ✅ Pass | 1.0 | 10 |
| Comment Review | 12 | ❌ Fail | 0.0 | 0 |
| Accountability | 8 | ✅ Pass | 1.0 | 8 |
| Action Versions | 7 | ✅ Pass | 1.0 | 7 |
| Workflow Syntax | 7 | ✅ Pass | 1.0 | 7 |
| Merge Dependencies | 3 | ✅ Pass | 1.0 | 3 |
| **TOTAL** | **100** | **8/10 pass, 1 partial** | — | **80.5/100** |

### Interpretation

- **0–29/100:** 🔴 Critical issues — cannot merge
- **30–69/100:** 🟡 Major issues — significant remediation needed
- **70–89/100:** 🟠 Moderate issues — address before merge
- **90–94/100:** 🟢 Minor issues — close to ready
- **95–99/100:** ✅ Merge-ready (A+ grade)
- **100/100:** ✅✅ Perfect — all gates pass

---

## PR Body Documentation Format

Use this format in every PR body to document gate status:

```markdown
## 📊 Merge Readiness Summary

| Gate | Weight | Status | Score |
|------|--------|--------|-------|
| Code Quality | 12 | ✅ | 12/12 |
| Test Coverage | 12 | ✅ | 12/12 |
| Security & Secrets | 15 | ⚠️ Partial | 7.5/15 |
| WEC Integrity | 14 | ✅ | 14/14 |
| Deferral Language | 10 | ✅ | 10/10 |
| Comment Review | 12 | ❌ | 0/12 |
| Accountability Report | 8 | ✅ | 8/8 |
| Action Versions | 7 | ✅ | 7/7 |
| Workflow Syntax | 7 | ✅ | 7/7 |
| Merge Dependencies | 3 | ✅ | 3/3 |
| **TOTAL** | **100** | **8/10** | **80.5/100** |

### Failing Gates (Remediation Required)

**Gate 6: Comment Review (12 pts)**
- 1 unresolved comment from @mbaetiong
- [Link to comment]: "Fix the type error in line 123"
- Remediation: Commit fix for type error, reply to comment with commit SHA

**Gate 3: Security & Secrets (15 pts) — Partial Pass**
- 1 CodeQL alert: py/wrong-named-arg in test_module.py:145
- Remediation: Fix keyword argument name from `timeout=` to `time_limit=`
- Partial credit: 7.5/15 (other security checks pass)

### Next Steps
1. Address Comment Review gate: Fix type error + reply to comment
2. Address Security gate: Fix CodeQL py/wrong-named-arg alert
3. Re-run pre-merge validation to recalculate score
4. Target: 100/100 for merge approval
```

---

## Validation Checklist (For Reviewers)

Use this checklist when reviewing PRs against the 10-gate model:

- [ ] **Gate 1:** Run `ruff check` + `mypy` locally on changed files?
- [ ] **Gate 2:** Coverage ≥ 95%? (Check Actions → test report)
- [ ] **Gate 3:** No new CodeQL alerts? (Check Actions → CodeQL report)
- [ ] **Gate 4:** WEC section present with 9 items, all always-required `[x]`?
- [ ] **Gate 5:** No deferral language detected? (Check Comments)
- [ ] **Gate 6:** All blocking comments resolved or replied to with commit SHA?
- [ ] **Gate 7:** AGENT_ACCOUNTABILITY_REPORT.md + CHANGELOG.md in last commit?
- [ ] **Gate 8:** All GitHub Actions use approved versions? (Check workflow files)
- [ ] **Gate 9:** No actionlint/yamllint errors? (Run locally)
- [ ] **Gate 10:** Branch clean, up-to-date, no conflicts?

---

## References

- **WEC System:** [docs/workflows/WEC_PR_BODY_CONFLICTS.md](../../docs/workflows/WEC_PR_BODY_CONFLICTS.md)
- **GitHub API Reference:** [docs/ci/GITHUB_API_COPILOT_AGENT_REFERENCE.md](../../docs/ci/GITHUB_API_COPILOT_AGENT_REFERENCE.md)
- **PR Description Helper:** [scripts/ci/pr_description_helper.py](../../scripts/ci/pr_description_helper.py)
- **Session Wrapup Autofix:** [scripts/ci/session_wrapup_autofix.py](../../scripts/ci/session_wrapup_autofix.py)

---

**Status:** ✅ Ready for Production Use  
**Last Validated:** 2026-06-25T15:50:00Z
