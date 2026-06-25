# Merge Readiness Validation Checklist

**Purpose:** Quick reference for validating PR merge readiness against the 10-gate model  
**Audience:** PR reviewers, maintainers, quality gates  
**Status:** ✅ Production Ready  
**Last Updated:** 2026-06-25

---

## Pre-Merge Validation Checklist (All 10 Gates)

Use this checklist when reviewing a PR for merge readiness. All items must pass for 100% readiness.

### ✅ Gate 1: Code Quality (12 pts) — MUST PASS

**Responsibility:** CI/CD (`pre-merge-validation.yml`)  
**Local Validation:**

```bash
# Run locally before pushing
python -m ruff check src/ tests/ --fix
python -m mypy src/ --ignore-missing-imports
```

**Checklist:**
- [ ] No ruff violations (run: `ruff check src/ tests/`)
- [ ] All types covered (run: `mypy src/`)
- [ ] No E402 or F811 violations in src/ (per-file ignores OK in tests/)
- [ ] PR body documents: "✅ Code Quality (12/12): X ruff errors, Y mypy errors"

**Evidence:** GitHub Actions → pre-merge-validation.yml → Code Quality step

---

### ✅ Gate 2: Test Coverage (12 pts) — MUST PASS

**Responsibility:** CI/CD (`pre-merge-validation.yml`)  
**Threshold:** ≥95% code coverage

**Local Validation:**

```bash
# Generate coverage report
pytest --cov=src --cov=codex_ml --cov-report=json -q

# Parse: jq '.totals.percent_covered' coverage.json
```

**Checklist:**
- [ ] Coverage ≥ 95% (check: `pytest --cov` report)
- [ ] Coverage delta documented (e.g., "+1.2% from baseline" or "-0.5%")
- [ ] New test cases added for new code (verify in PR diff)
- [ ] PR body shows: "✅ Test Coverage (12/12): 96.5% (+1.7% delta)"

**Evidence:** GitHub Actions → pre-merge-validation.yml → Test Coverage step

---

### ✅ Gate 3: Security & Secrets (15 pts) — HIGHEST WEIGHT

**Responsibility:** CI/CD (`pre-merge-validation.yml`) + agents

**Local Validation:**

```bash
# Detect new secrets (against baseline)
detect-secrets-hook --baseline .secrets.baseline $(git diff --name-only HEAD~1 HEAD)
# Exit 0 = pass, ≠0 = fail

# Check CodeQL (via GitHub API or Actions artifact)
gh api /repos/Aries-Serpent/_codex_/code-scanning/alerts?state=open

# Check pip vulnerabilities
python -m pip_audit --skip-editable --desc
```

**Checklist:**
- [ ] No new secrets detected (`detect-secrets-hook` exit: 0)
- [ ] CodeQL open alert count: 0 new (document pre-existing if any)
- [ ] Pip audit: No new vulnerabilities
- [ ] PR body shows: "✅ Security & Secrets (15/15): 0 new secrets, 0 CodeQL errors, 0 pip vulns"

**If Failed:**
- [ ] CodeQL error fix committed (with commit SHA in PR body)
- [ ] Security findings documented with remediation status
- [ ] Partial credit (7.5/15) for addressing major findings

**Evidence:** GitHub Actions → Security steps + CodeQL report artifact

---

### ✅ Gate 4: WEC Integrity (14 pts) — CRITICAL ORCHESTRATION

**Responsibility:** Agent + `workflow-execution-gate.yml`  
**Must Be Present:** Workflow Execution Checklist section in PR body

**Checklist:**
- [ ] WEC section header exists: `## 🔄 Workflow Execution Checklist`
- [ ] All 9 items present (see list below)
- [ ] Always-required items are `[x]` (6 items):
  - [ ] `pre-merge-validation.yml` ← Must be `[x]`
  - [ ] `comment-review-gate.yml` ← Must be `[x]`
  - [ ] `deferral-language-gate.yml` ← Must be `[x]`
  - [ ] `agent-auth-delegation.yml` ← Must be `[x]`
  - [ ] `workflow-execution-gate.yml` ← Must be `[x]`
  - [ ] `cost-gate.yml` ← Must be `[x]`
- [ ] Optional items are documented (3 items):
  - [ ] `copilot-agent-checkin.yml` (checked/unchecked documented)
  - [ ] `copilot-agent-session-done.yml` (checked/unchecked documented)
  - [ ] `copilot-iterative-self-healing.yml` (checked/unchecked documented)

**Full WEC Block:**
```markdown
## 🔄 Workflow Execution Checklist

Workflows can be skipped/dispatched by updating these checkboxes:

- [x] pre-merge-validation.yml        ← Always-required
- [x] comment-review-gate.yml         ← Always-required
- [x] deferral-language-gate.yml      ← Always-required
- [x] agent-auth-delegation.yml       ← Always-required
- [x] workflow-execution-gate.yml     ← Always-required (orchestrator)
- [ ] copilot-agent-checkin.yml       ← Optional (checked if session active)
- [ ] copilot-agent-session-done.yml  ← Optional (checked if awaiting closure)
- [ ] copilot-iterative-self-healing.yml ← Optional (checked if fixing flaky tests)
- [x] cost-gate.yml                   ← Always-required
```

**If Failed:** PR cannot merge — agent must add canonical WEC block

---

### ✅ Gate 5: Deferral Language Policy (10 pts)

**Responsibility:** `deferral-language-gate.yml` + agent

**Scan Locations:** PR body, commits, comments  
**Prohibited Phrases:** 20+ patterns (see list in [MERGE_READINESS_10_GATES.md](../ci/MERGE_READINESS_10_GATES.md))

**Manual Checklist:**
- [ ] PR body uses affirmative language (no "will defer", "pre-existing", etc.)
- [ ] Commit messages use affirmative language
- [ ] PR comments address issues directly (no deferral phrases)
- [ ] Run: `deferral-language-gate.yml` passes in Actions

**Examples:**
- ❌ "These are pre-existing issues"
- ✅ "These issues are fixed in commit abc1234"
- ❌ "Will address in a future PR"
- ✅ "Addressed in this PR via refactor at line 123"

---

### ✅ Gate 6: Comment Review Policy (12 pts)

**Responsibility:** `comment-review-gate.yml` + agent  
**Scope:** Blocking comments from maintainers, security bots, code review bots

**Checklist:**
- [ ] All comments from @mbaetiong reviewed and addressed or resolved
- [ ] All github-actions[bot] comments resolved
- [ ] All copilot-pull-request-reviewer[bot] comments resolved
- [ ] All security/quality bot comments addressed (with fix commits or explanations)
- [ ] Resolved comments marked as "Resolved" in PR conversation
- [ ] Unresolved comments have agent reply with commit SHA (per user preference)

**If Unaddressed Comment:**
- [ ] Create reply comment: "@copilot Addressed in commit [SHA]" (with fix link)
- [ ] Or: "Documented as known gap: [reason]"

**Evidence:** PR conversation tab shows ✅ Resolved next to resolved comments

---

### ✅ Gate 7: Accountability Report & CHANGELOG (8 pts)

**Responsibility:** Agent + auto-fix (`session_wrapup_autofix.py`)

**Checklist:**
- [ ] `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` updated in latest commit
  ```bash
  git diff --name-only HEAD~1 HEAD | grep -q "AGENT_ACCOUNTABILITY_REPORT.md"
  ```
- [ ] `CHANGELOG.md` updated in latest commit
  ```bash
  git diff --name-only HEAD~1 HEAD | grep -q "CHANGELOG.md"
  ```
- [ ] Entry format validated:
  - [ ] Timestamp: ISO-8601 format (YYYY-MM-DDTHH:MM:SSZ)
  - [ ] Session ID recorded (e.g., "S_12345")
  - [ ] Changes summarized (2–5 bullet points)
  - [ ] Author/agent recorded

**If Missing:** Auto-fix runs and appends minimal entry (marked `[auto-generated]`)  
**If Auto-Fixed:** Still counts as pass (score: 8/8)

**Entry Example:**
```markdown
### Fixed (2026-06-25, S_SESSION)
- [auto-generated] Added PR merge readiness framework
- [auto-generated] Implemented WEC preservation utilities
- [auto-generated] Created pr_description_helper.py module
```

---

### ✅ Gate 8: Action Versions Enforcement (7 pts)

**Responsibility:** `pre-merge-validation.yml` + auto-fix (`enforce_actions_versions.py`)

**Approved Versions (as of 2026-06-22):**
- `actions/checkout@v5` ✅ (not v3, v4)
- `actions/setup-node@v5` ✅ (not v3, v4)
- `actions/github-script@v8` ✅ (not v7 or older)
- `actions/setup-python@v6` ✅ (not v4, v5)
- `actions/upload-artifact@v5` ✅ (not v3, v4)

**Checklist:**
- [ ] All GitHub Actions in `.github/workflows/` use approved versions
  ```bash
  grep -r "uses: actions/" .github/workflows/ | grep -v "@v5\|@v8\|@v6"
  ```
  Should return: No results (empty)

- [ ] If violations found, auto-fix applied:
  ```bash
  python scripts/ci/enforce_actions_versions.py --fix
  ```
- [ ] Commit includes updated actions with new versions

**Evidence:** GitHub Actions → pre-merge-validation.yml → Action Versions step

---

### ✅ Gate 9: YAML Workflow Syntax & Indentation (7 pts)

**Responsibility:** `pre-merge-validation.yml`

**Local Validation:**

```bash
# Check for actionlint errors
actionlint .github/workflows/*.yml 2>&1 | grep -c error
# Should output: 0

# Check for yamllint errors
yamllint .github/workflows/ --config-file .yamllint.yml
# Should output: No errors
```

**Checklist:**
- [ ] actionlint: 0 errors
  - No invalid GitHub Actions syntax
  - No missing required fields
  - No unsupported constructs
- [ ] yamllint: 0 errors
  - Indentation correct (2-space increments)
  - Keys properly quoted
  - No trailing whitespace
- [ ] If modified `.github/workflows/*.yml` files: Each passes both checks
- [ ] PR body shows: "✅ Workflow Syntax (7/7): 0 actionlint, 0 yamllint errors"

**Common Fixes:**
- Add spaces after list markers: `-` → `- ` (before `name:`)
- Fix indentation under `steps:` (must be N+2 from parent)
- Escape special characters or use quotes
- Use `run: |` (block scalar) for multi-line shell commands

---

### ✅ Gate 10: Merge Dependency Checks (3 pts)

**Responsibility:** `pre-merge-validation.yml` + maintainer

**Checklist:**
- [ ] No unresolved merge conflicts
  ```bash
  git diff --name-only --diff-filter=U
  # Should return: (empty)
  ```
- [ ] Branch is up-to-date with `main` (or documented reason for divergence)
  ```bash
  git merge-base --is-ancestor main HEAD
  # Exit 0 = ancestor (up-to-date or ahead)
  ```
- [ ] All required branch protection rules satisfied
  - [ ] All status checks passing (green checkmarks)
  - [ ] All required reviewers approved (if configured)
  - [ ] No blocking dismissals
- [ ] PR body confirms: "✅ Merge Dependencies (3/3): Branch clean, up-to-date, all protections OK"

**If Conflicts Detected:**
- [ ] Resolve conflicts locally and push: `git merge main` → fix conflicts → `git commit` → `git push`

---

## Merge Readiness Score Calculation

| Gate # | Gate Name | Weight | Required | Status | Score |
|--------|-----------|--------|----------|--------|-------|
| 1 | Code Quality | 12 | ✅ | [ ] | [ ]/12 |
| 2 | Test Coverage | 12 | ✅ | [ ] | [ ]/12 |
| 3 | Security & Secrets | 15 | ✅ | [ ] | [ ]/15 |
| 4 | WEC Integrity | 14 | ✅ | [ ] | [ ]/14 |
| 5 | Deferral Language | 10 | ✅ | [ ] | [ ]/10 |
| 6 | Comment Review | 12 | ✅ | [ ] | [ ]/12 |
| 7 | Accountability | 8 | ✅ | [ ] | [ ]/8 |
| 8 | Action Versions | 7 | ✅ | [ ] | [ ]/7 |
| 9 | Workflow Syntax | 7 | ✅ | [ ] | [ ]/7 |
| 10 | Merge Dependencies | 3 | ✅ | [ ] | [ ]/3 |
| **TOTAL** | — | **100** | **10/10** | **?** | **[ ]/100** |

---

## Final Merge Readiness Confirmation

Before clicking "Merge", confirm:

```markdown
## 🚀 Ready for Merge

- [ ] All 10 gates passing (score = 100/100)
- [ ] WEC section present with canonical format (9 items)
- [ ] All always-required items checked: [x]
- [ ] Merge Readiness Summary table shows 10/10 pass
- [ ] No outstanding review comments
- [ ] Branch protection rules satisfied
- [ ] AAIS V4.0 composite score ≥ 95/100
- [ ] AGENT_ACCOUNTABILITY_REPORT.md + CHANGELOG.md updated

**Merge Status:** ✅ APPROVED FOR MERGE
```

---

## Quick Reference Links

| Reference | Purpose |
|-----------|---------|
| [10 Pre-Merge Gates](../ci/MERGE_READINESS_10_GATES.md) | Detailed gate documentation |
| [PR Body Template](../templates/PR_BODY_TEMPLATE_MERGE_READINESS.md) | Template for PR sections |
| [Agent Integration Guide](../agent/AGENT_MERGE_READINESS_INTEGRATION.md) | Agent implementation patterns |
| [WEC Conflicts Guide](../../docs/workflows/WEC_PR_BODY_CONFLICTS.md) | WEC preservation details |
| [PR Helper Module](../../scripts/ci/pr_description_helper.py) | Utility functions source |

---

**Last Updated:** 2026-06-25T15:50:00Z  
**Maintained By:** Copilot Agents + Maintainer  
**Status:** ✅ Production Ready
