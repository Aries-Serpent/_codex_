# Copilot Verification Prompt: PR #2207 Pre-Merge Analysis
**Timestamp:** Previous Cycle-11-14 16:45:20 UTC  
**User:** mbaetiong  
**Target:** Aries-Serpent/_codex_ PR #2207 → main  
---
## COMPREHENSIVE PROMPT FOR COPILOT
You are tasked with comprehensive pre-merge verification for **PR #2207 ("0D to main")** in the `Aries-Serpent/_codex_` repository. This PR introduces critical CI/CD, security, and dependency management configurations that directly impact the stability of the `main` branch.
#### Gate 1: Workflow Validation
```bash
Command: yamllint .github/workflows/
Expected: "All files are valid YAML"
Failure Impact: BLOCK MERGE
```text
#### Gate 2: Security Scan
```bash
Command: bandit -r src/ --severity-level=MEDIUM
Expected: "No HIGH/CRITICAL issues"
Failure Impact: BLOCK MERGE
```text
#### Gate 3: Coverage Check
```bash
Command: pytest --cov=src --cov-report=term-missing
Expected: "Coverage >= 96%"
Failure Impact: BLOCK MERGE (or adjust threshold with approval)
```text
#### Gate 4: Lock File Consistency
```bash
Command: grep -E "(torch|cuda|tensorflow)" uv.lock
Expected: "0 matches"
Failure Impact: BLOCK MERGE
```text
#### Gate 5: Merge Conflicts
```bash
Command: gh pr view 2207 --json mergeable
Expected: "mergeable: true"
Failure Impact: BLOCK MERGE
```text
#### Gate 6: CODEOWNERS Coverage
```bash
Command: Verify all 126 changed files have owner assignment
Expected: "100% coverage"
Failure Impact: BLOCK MERGE
```text
### 🔐 SECURITY CHECKLIST
- ☐ **Secrets Detection:** No new API keys, tokens, or credentials exposed
  - Command: `detect-secrets scan --baseline .secrets.baseline`
  - Expected: "No secrets found"
- ☐ **Bandit Configuration:** Proper exclusions (tests, docs, .venv, artifacts, .git)
  - Command: Validate `.bandit.yaml` structure
  - Expected: Targets only `src/` directory
- ☐ **Dependency Vulnerabilities:** No known CVEs in dependencies
  - Command: `pip-audit` or `safety check`
  - Expected: "No vulnerabilities"
- ☐ **GPU Package Removal:** Confirmed CPU-only environment
  - Command: Audit log review (`.codex/evidence/dependency_ops.jsonl`)
  - Expected: GPU removals documented with justification
### 📊 TEST & COVERAGE VERIFICATION
- ☐ **Coverage Threshold:** Current coverage meets or exceeds 96%
  - File: `.github/coverage_threshold.txt`
  - Command: `pytest --cov=src --cov-report=term-missing`
  - Action: If < 96%, determine if gap should be addressed or threshold adjusted
- ☐ **Code Quality:** No new linting or type-checking errors
  - Command: `nox -s lint && nox -s type_check`
  - Expected: All checks pass
- ☐ **Test Execution:** All tests pass on 0D_base_ branch
  - Command: `pytest tests/ -v`
  - Expected: 0 failures, 0 skipped (or document justified skips)
### 📦 DEPENDENCY MANAGEMENT
- ☐ **Lock File Integrity:** `uv.lock` resolves without conflicts
  - Command: `uv sync --check`
  - Expected: Success (no resolution errors)
- ☐ **Environment Reproducibility:** Fresh environment can be built
  - Command: Test in isolated venv
  - Expected: All dependencies install cleanly
- ☐ **GPU Cleanup:** All GPU/CUDA packages removed
  - Files: `uv.lock`, `requirements.txt`, `requirements-ml-cpu.txt`
  - Audit: `.codex/evidence/dependency_ops.jsonl` entries present
### 📝 DOCUMENTATION REVIEW
- ☐ **Copilot.md Enhancements:** CI/CD guidelines clear and actionable
  - New Sections: artifact handling, uv.lock regeneration, DoD checklist
  - Verification: Links valid, code examples executable
- ☐ **PR #2224 Review Response:** Detailed implementation plan provided
  - File: `.github/docs/AGENTS_PR2224_Review_Comments_Response_Copilot.md`
  - Coverage: imports, assertions, style, unused imports, thread safety
- ☐ **CODEOWNERS Assignment:** All modified files have responsible owner
  - File: `.github/CODEOWNERS`
  - Coverage: 100% of 126 modified files
### 🚀 CI/CD PIPELINE VERIFICATION
**Active Workflows (Verify Not Broken):**
1. ☐ `tests.yml` — Pytest with coverage
2. ☐ `security_gates.yml` — Bandit + Semgrep
3. ☐ `nox_gates.yml` — Linting & type checking
4. ☐ `coverage_report.yml` — Coverage threshold enforcement
5. ☐ `post-merge-validation-optimized.yml` — Post-merge chain
6. ☐ `docker-build-push.yml` — Container builds (if applicable)
**Verification:**
- All workflow files syntactically valid YAML ✅
- No circular job dependencies ✅
- Trigger conditions properly configured ✅
- Environment variables documented ✅
### 🔄 POST-MERGE VALIDATION PLAN
**Immediate Post-Merge (Automated):**
1. ☐ Workflow: `post-merge-validation-optimized.yml` triggers automatically
2. ☐ Full test suite runs with coverage report
3. ☐ Docker images built (CPU-only verified)
4. ☐ Artifacts archived with retention policy
5. ☐ Notifications sent (Slack, email)
6. ☐ Status dashboard updated
**Monitoring Duration:** 30-45 minutes post-merge
**Rollback Trigger Conditions:**
- Post-merge workflow fails
- Coverage drops below 96%
- Critical security issue discovered
- Production impact reported
### 📞 APPROVAL STAKEHOLDERS
Obtain explicit approval from:
| Role | Approval Item | Status |
|------|---------------|--------|
| Code Owner (mbaetiong) | Overall PR readiness | ☐ PENDING |
| Security Lead | Security scans & config | ☐ PENDING |
| QA Lead | Coverage threshold & tests | ☐ PENDING |
| DevOps Lead | CI/CD pipeline & post-merge | ☐ PENDING |
### 🎬 EXECUTION STEPS
#### Step 1: Automated Checks (5 minutes)
```bash
yamllint .github/workflows/ .github/*.yml
gh pr view 2207 --json mergeable,mergeStateStatus
gh pr checks 2207
```text
#### Step 2: Security Validation (15 minutes)
```bash
bandit -r src/ -f json -o bandit-report.json
detect-secrets scan --baseline .secrets.baseline
pip-audit
grep -E "(torch|cuda)" uv.lock
```text
#### Step 3: Test Coverage (20 minutes)
```bash
pytest --cov=src --cov-report=term-missing
cat .github/coverage_threshold.txt
nox -s lint && nox -s type_check
```text
#### Step 4: Dependency Validation (10 minutes)
```bash
uv sync --check
pip install --dry-run -r requirements.txt
test -f .codex/evidence/dependency_ops.jsonl
```text
#### Step 5: Documentation Review (5 minutes)
```bash
grep -E "^(#|##)" .github/Copilot.md
test -f .github/docs/AGENTS_PR2224_Review_Comments_Response_Copilot.md
```text
#### Step 6: CODEOWNERS Verification (3 minutes)
```bash
git diff HEAD~102..HEAD --name-only | \
  while read file; do \
    grep -q "^$file" .github/CODEOWNERS || echo "ORPHANED: $file"; \
  done
```text
### ✅ MERGE AUTHORIZATION DECISION
**Merge if ALL gates pass:**
- ✅ Workflow validation: PASS
- ✅ Security scan: PASS (0 HIGH/CRITICAL)
- ✅ Coverage: >= 96%
- ✅ Dependency lock: Consistent
- ✅ No merge conflicts
- ✅ CODEOWNERS: 100% coverage
- ✅ All approvals obtained
**Conditional Merge (with documented exceptions):**
- Coverage < 96% BUT threshold adjustment approved
- Known, documented security finding with mitigation plan
**Block Merge (resolve before proceeding):**
- Workflow syntax errors
- Critical security vulnerabilities
- Merge conflicts
- Missing CODEOWNERS assignments
- Failed status checks
### 📊 FINAL SIGN-OFF
```markdown
PR #2207 Verification Complete
├── Files Changed: 126 ✅
├── Additions: 20,518 ✅
├── Deletions: 3,502 ✅
├── Security Scan: PASS ✅
├── Coverage: __%  (Target: 96%)
├── Merge Conflicts: NONE ✅
├── CODEOWNERS: 100% Coverage ✅
└── Status: READY FOR MERGE 🚀
Approved By:
- Code Owner: _________________
- Security: _________________
- QA: _________________
- DevOps: _________________
Merge Time: Previous Cycle-11-14 HH:MM:SS UTC
Merge Commit: ___________________________
```text
---
**Copilot, proceed with comprehensive verification using the checklist and execution steps above. Generate detailed reports for any findings and provide clear PASS/FAIL status for each gate.**
