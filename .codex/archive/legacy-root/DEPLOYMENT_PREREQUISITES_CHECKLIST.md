# Deployment Prerequisites Checklist

**Version:** 1.0  
**Last Updated:** 2026-07-09  
**Target Audience:** Deployment Engineers, SREs, CI/CD Operators  
**Status:** Production-Ready  

---

## Overview

This checklist provides 30 specific validation checkpoints across 6 critical sections to verify deployment readiness before initiating production deployments. All checks must pass with remediation procedures executed if any fail.

**Quick Reference:**
- Total validation points: 30
- Sections: 6 (Authorization, Code State, Version, Artifacts, Security, Compliance)
- Exit criteria: 30/30 checks PASS
- Escalation trigger: Any FAIL in Authorization or Security sections
- Estimated validation time: 15-25 minutes

---

## Section 1: Authorization & Approval (5 Checkpoints)

**Exit Criteria:** All 5 checks must PASS. Any FAIL blocks deployment.

### CHECK 1.1: Governance Gate Certification
**Requirement:** All 32 governance gates must be certified PASSED  
**Validation:** Verify `DEPLOYMENT_SIGN_OFF_*.md` file exists in `.codex/` with "32/32 gates PASSED"  
**Command:**
```bash
if grep -q "32/32" .codex/DEPLOYMENT_SIGN_OFF_*.md 2>/dev/null; then
  echo "✅ CHECK 1.1 PASS: 32/32 governance gates certified"
else
  echo "❌ CHECK 1.1 FAIL: Governance gate certification missing"
  exit 1
fi
```
**Remediation:** Run governance gate audit with `python scripts/ci/governance_gate_audit.py` and resolve all failures  
**Escalation:** If gates fail, escalate to @mbaetiong for override decision

### CHECK 1.2: Approval Authority Signature
**Requirement:** Primary maintainer (@mbaetiong) must have signed off on deployment  
**Validation:** Verify approval signature in DEPLOYMENT_SIGN_OFF file dated within 7 days  
**Command:**
```bash
SIGN_OFF_DATE=$(grep "Approved:" .codex/DEPLOYMENT_SIGN_OFF_*.md | sed 's/.*: //' | head -1)
CURRENT_DATE=$(date +%s)
SIGN_OFF_EPOCH=$(date -d "$SIGN_OFF_DATE" +%s 2>/dev/null || echo 0)
DIFF=$((($CURRENT_DATE - $SIGN_OFF_EPOCH) / 86400))
if [ $DIFF -le 7 ] && [ $DIFF -ge 0 ]; then
  echo "✅ CHECK 1.2 PASS: Approval signature valid (${DIFF} days old)"
else
  echo "❌ CHECK 1.2 FAIL: Approval signature missing or expired"
  exit 1
fi
```
**Remediation:** Request new sign-off from @mbaetiong; provide updated deployment metrics  
**Escalation:** Contact @mbaetiong directly for expedited re-approval

### CHECK 1.3: Change Advisory Board (CAB) Review
**Requirement:** CAB review completed and documented  
**Validation:** Verify CAB review document in `.codex/evidence/cab_review_*.md` or equivalent  
**Command:**
```bash
if [ -f .codex/evidence/cab_review_*.md ] || grep -q "CAB-APPROVED" .codex/DEPLOYMENT_SIGN_OFF_*.md; then
  echo "✅ CHECK 1.3 PASS: CAB review completed"
else
  echo "⚠️  CHECK 1.3 WARN: CAB review not found (non-blocking for emergency deployments)"
fi
```
**Remediation:** If blocking deployment, schedule CAB review session and document findings  
**Escalation:** For emergency deployments, CAB waiver requires override from @mbaetiong

### CHECK 1.4: Deployment Window Approved
**Requirement:** Deployment window matches approved maintenance window (if required)  
**Validation:** Current time is within approved deployment window OR emergency deployment flag set  
**Command:**
```bash
APPROVED_WINDOW=$(grep -i "deployment.*window" .codex/DEPLOYMENT_SIGN_OFF_*.md | head -1)
if [ -n "$APPROVED_WINDOW" ]; then
  echo "✅ CHECK 1.4 PASS: Deployment window approved"
else
  echo "⚠️  CHECK 1.4 WARN: Deployment window not specified (verify externally)"
fi
```
**Remediation:** Update DEPLOYMENT_SIGN_OFF file with approved maintenance window in ISO 8601 format  
**Escalation:** For off-window deployments, require explicit override and stakeholder notification

### CHECK 1.5: Rollback Authority Designated
**Requirement:** Designated rollback authority identified and notified  
**Validation:** Verify rollback authority contact in ROLLBACK_PROCEDURES.md or DEPLOYMENT_SIGN_OFF  
**Command:**
```bash
if grep -q "Rollback Authority:" .codex/DEPLOYMENT_SIGN_OFF_*.md .codex/ROLLBACK_PROCEDURES.md 2>/dev/null; then
  echo "✅ CHECK 1.5 PASS: Rollback authority designated"
else
  echo "❌ CHECK 1.5 FAIL: Rollback authority not designated"
  exit 1
fi
```
**Remediation:** Designate primary and secondary rollback authorities; add to deployment sign-off  
**Escalation:** If authority unavailable, escalate rollback decisions to @mbaetiong

---

## Section 2: Code State & Quality (5 Checkpoints)

**Exit Criteria:** All 5 checks must PASS. Any FAIL requires remediation.

### CHECK 2.1: Main Branch at Stable Commit
**Requirement:** Current commit on main branch is stable and passed all CI/CD gates  
**Validation:** Last commit on main has CODEQL/build/test checks all PASSING  
**Command:**
```bash
LAST_COMMIT=$(git rev-parse HEAD)
if gh run list --branch main --limit 1 --json conclusion -q | grep -q "success"; then
  echo "✅ CHECK 2.1 PASS: Main branch at stable commit ($LAST_COMMIT)"
else
  echo "❌ CHECK 2.1 FAIL: Main branch has failing CI/CD checks"
  echo "Last commit: $LAST_COMMIT"
  exit 1
fi
```
**Remediation:** Wait for CI/CD to complete; if failed, fix issues and merge to main  
**Escalation:** If CI/CD consistently fails, escalate to CI health team

### CHECK 2.2: No Uncommitted Changes
**Requirement:** Working directory clean; all changes committed and pushed  
**Validation:** `git status` shows no uncommitted changes  
**Command:**
```bash
if git diff-index --quiet HEAD --; then
  echo "✅ CHECK 2.2 PASS: No uncommitted changes"
else
  echo "❌ CHECK 2.2 FAIL: Uncommitted changes found"
  git status
  exit 1
fi
```
**Remediation:** Stage and commit all changes or stash uncommitted work  
**Escalation:** If changes are deployment-critical, create hotfix PR and merge before deployment

### CHECK 2.3: No Pre-existing Code Quality Issues
**Requirement:** Ruff (linting), Black (formatting), mypy (type checking) all pass  
**Validation:** Run linting and type checks; no errors allowed  
**Command:**
```bash
echo "Running Ruff linter..."
if ruff check . --select E,F,I 2>/dev/null | grep -q "error"; then
  echo "❌ CHECK 2.3 FAIL: Ruff linting errors found"
  ruff check . --select E,F,I
  exit 1
else
  echo "✅ CHECK 2.3 PASS: Ruff linting passed"
fi
```
**Remediation:** Run `ruff check --fix`, `black .`, and `mypy` to auto-fix issues  
**Escalation:** For complex linting issues, assign to code quality team

### CHECK 2.4: Test Suite Coverage ≥90%
**Requirement:** Overall test coverage must be ≥90%  
**Validation:** Coverage report shows overall coverage ≥90%  
**Command:**
```bash
if grep -q "coverage.*9[0-9]%" .codex/coverage_report.txt 2>/dev/null || \
   grep -q "TOTAL.*9[0-9]%" .coverage 2>/dev/null || \
   coverage report 2>/dev/null | grep "TOTAL" | awk '{print $NF}' | grep -qE "9[0-9]|100"; then
  echo "✅ CHECK 2.4 PASS: Test coverage ≥90%"
else
  echo "⚠️  CHECK 2.4 WARN: Test coverage may be <90% (verify with: coverage report)"
fi
```
**Remediation:** Run test suite with coverage; add tests until coverage reaches ≥90%  
**Escalation:** Coverage gap >5% requires code review and test enhancement plan

### CHECK 2.5: All Tests Pass Locally & in CI
**Requirement:** Full test suite passes with 0 failures  
**Validation:** `nox -s tests` completes with 0 failures  
**Command:**
```bash
echo "Running test suite..."
if nox -s tests 2>&1 | grep -qE "passed|PASSED" && ! grep -qE "FAILED|failed"; then
  echo "✅ CHECK 2.5 PASS: Test suite passed"
else
  echo "❌ CHECK 2.5 FAIL: Test suite failures detected"
  exit 1
fi
```
**Remediation:** Review failing tests; debug and fix root causes; run `nox -s tests` again  
**Escalation:** Flaky test failures escalate to test infrastructure team

---

## Section 3: Version & Release Artifacts (4 Checkpoints)

**Exit Criteria:** All 4 checks must PASS. Version mismatches block deployment.

### CHECK 3.1: Version Number Incremented Correctly
**Requirement:** Version in pyproject.toml matches release tag (e.g., v0.1.0)  
**Validation:** Version matches deployment target release  
**Command:**
```bash
PYPROJECT_VERSION=$(grep "version.*=" pyproject.toml | head -1 | sed 's/.*"\([^"]*\)".*/\1/')
RELEASE_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
if [[ "$PYPROJECT_VERSION" == "${RELEASE_TAG#v}" ]]; then
  echo "✅ CHECK 3.1 PASS: Version matches release tag (${PYPROJECT_VERSION})"
else
  echo "❌ CHECK 3.1 FAIL: Version mismatch (pyproject: ${PYPROJECT_VERSION}, tag: ${RELEASE_TAG})"
  exit 1
fi
```
**Remediation:** Update pyproject.toml version to match deployment target; create release tag  
**Escalation:** Version conflicts require manual resolution by release manager

### CHECK 3.2: Release Artifacts Generated
**Requirement:** Wheel (.whl) and source distributions (.tar.gz) exist  
**Validation:** Verify files in `dist/` directory  
**Command:**
```bash
if ls dist/*.whl dist/*.tar.gz 2>/dev/null | grep -q .; then
  echo "✅ CHECK 3.2 PASS: Release artifacts found"
  ls -lh dist/*.{whl,tar.gz}
else
  echo "❌ CHECK 3.2 FAIL: Release artifacts missing"
  echo "Run: python -m build"
  exit 1
fi
```
**Remediation:** Run `python -m build` to generate distributions  
**Escalation:** Build failures escalate to release engineering team

### CHECK 3.3: CHANGELOG.md Updated for Release
**Requirement:** CHANGELOG.md includes entry for current release version  
**Validation:** Current version appears in CHANGELOG.md with dated entry  
**Command:**
```bash
RELEASE_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
VERSION_CLEAN=${RELEASE_TAG#v}
if grep -q "## \[${VERSION_CLEAN}\]" CHANGELOG.md; then
  echo "✅ CHECK 3.3 PASS: CHANGELOG.md updated for ${VERSION_CLEAN}"
else
  echo "❌ CHECK 3.3 FAIL: CHANGELOG.md missing entry for ${VERSION_CLEAN}"
  exit 1
fi
```
**Remediation:** Add CHANGELOG entry with: version, date, bullet-point summary of changes  
**Escalation:** Incomplete changelogs require documentation team review

### CHECK 3.4: Git Tag Created & Signed
**Requirement:** Annotated git tag exists for release  
**Validation:** `git describe --tags` returns current tag; tag is signed  
**Command:**
```bash
RELEASE_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
if [ -n "$RELEASE_TAG" ]; then
  if git verify-tag "$RELEASE_TAG" 2>/dev/null | grep -q "gpg"; then
    echo "✅ CHECK 3.4 PASS: Git tag signed ($RELEASE_TAG)"
  else
    echo "⚠️  CHECK 3.4 WARN: Git tag exists but not signed ($RELEASE_TAG)"
  fi
else
  echo "❌ CHECK 3.4 FAIL: No git tag found"
  exit 1
fi
```
**Remediation:** Create annotated tag: `git tag -a v0.x.x -m "Release v0.x.x" && git push --tags`  
**Escalation:** Tag signing issues escalate to release manager

---

## Section 4: Artifacts & Infrastructure (4 Checkpoints)

**Exit Criteria:** All 4 checks must PASS. Missing artifacts block deployment.

### CHECK 4.1: Docker Images Built & Tagged
**Requirement:** Docker images built for all target platforms  
**Validation:** Images tagged with release version exist in registry  
**Command:**
```bash
RELEASE_TAG=$(git describe --tags --abbrev=0 2>/dev/null | sed 's/^v//')
IMAGE_TAG="codex:${RELEASE_TAG}"
if docker images | grep -q "$IMAGE_TAG"; then
  echo "✅ CHECK 4.1 PASS: Docker image tagged ($IMAGE_TAG)"
  docker images | grep "$IMAGE_TAG"
else
  echo "⚠️  CHECK 4.1 WARN: Docker image not found locally (may be in remote registry)"
fi
```
**Remediation:** Build images: `docker build -t codex:${RELEASE_TAG} .` and push to registry  
**Escalation:** Registry push failures escalate to infrastructure team

### CHECK 4.2: Kubernetes Manifests Validated
**Requirement:** All K8s manifests pass schema validation  
**Validation:** kubectl dry-run succeeds for all manifests  
**Command:**
```bash
echo "Validating Kubernetes manifests..."
if kubectl apply --dry-run=client -f .codex/k8s-manifests/ 2>&1 | grep -q "error"; then
  echo "❌ CHECK 4.2 FAIL: K8s manifest validation failed"
  kubectl apply --dry-run=client -f .codex/k8s-manifests/
  exit 1
else
  echo "✅ CHECK 4.2 PASS: K8s manifests validated"
fi
```
**Remediation:** Review K8s manifest errors; fix schema violations; validate again  
**Escalation:** K8s deployment issues escalate to platform team

### CHECK 4.3: Database Migration Scripts Ready
**Requirement:** All DB migration scripts exist and are tested  
**Validation:** Migration files present in `migrations/` directory  
**Command:**
```bash
if [ -d migrations ] && ls migrations/*.sql 2>/dev/null | grep -q .; then
  echo "✅ CHECK 4.3 PASS: Database migration scripts ready"
  ls -1 migrations/*.sql | wc -l | xargs echo "  Found"
else
  echo "⚠️  CHECK 4.3 WARN: No database migrations found (may not be required)"
fi
```
**Remediation:** Create migration scripts for schema changes; test on staging database  
**Escalation:** Migration failures require database team review

### CHECK 4.4: Infrastructure as Code (IaC) Validated
**Requirement:** Terraform/Helm configs validated and plan approved  
**Validation:** No drift between desired state and infrastructure  
**Command:**
```bash
if [ -d terraform ] || [ -f values.yaml ]; then
  echo "⚠️  CHECK 4.4 WARN: IaC validation requires manual review"
  echo "  Run: terraform validate && terraform plan"
  echo "  Or: helm lint && helm dry-run"
else
  echo "✅ CHECK 4.4 PASS: No IaC updates required"
fi
```
**Remediation:** Run terraform/helm validation and address any plan changes before deployment  
**Escalation:** Infrastructure drift issues escalate to platform engineering

---

## Section 5: Security & Compliance (4 Checkpoints)

**Exit Criteria:** All 4 checks must PASS. Security failures block deployment.

### CHECK 5.1: CodeQL Security Scan Passed
**Requirement:** No CRITICAL or HIGH severity findings  
**Validation:** Latest CodeQL scan has 0 unresolved security issues  
**Command:**
```bash
echo "Checking CodeQL findings..."
if gh code-scanning list --state open 2>/dev/null | grep -qE "CRITICAL|HIGH"; then
  echo "❌ CHECK 5.1 FAIL: CRITICAL or HIGH severity CodeQL findings exist"
  gh code-scanning list --state open
  exit 1
else
  echo "✅ CHECK 5.1 PASS: No CRITICAL/HIGH CodeQL findings"
fi
```
**Remediation:** Review and remediate security findings via CodeQL remediation agent  
**Escalation:** Unresolved CRITICAL findings require security team override

### CHECK 5.2: Dependency Vulnerabilities Resolved
**Requirement:** No unresolved vulnerabilities in pip/npm dependencies  
**Validation:** Dependabot alerts all resolved or waived  
**Command:**
```bash
echo "Checking dependency vulnerabilities..."
if gh api repos/{owner}/{repo}/dependabot/alerts --jq '.[] | select(.state=="open")' 2>/dev/null | grep -q .; then
  echo "⚠️  CHECK 5.2 WARN: Open Dependabot alerts exist (verify with: gh api repos/{owner}/{repo}/dependabot/alerts)"
else
  echo "✅ CHECK 5.2 PASS: No open dependency vulnerabilities"
fi
```
**Remediation:** Update vulnerable dependencies or document risk acceptance; link to risk acceptance record  
**Escalation:** Critical vulnerabilities (CVSS ≥9.0) require security review

### CHECK 5.3: Secrets Not Committed
**Requirement:** No secrets, API keys, or credentials in repository  
**Validation:** Secret scanning passed; no exposed secrets  
**Command:**
```bash
echo "Running secret scanning..."
if gh secret-scanning list 2>/dev/null | grep -q "open"; then
  echo "❌ CHECK 5.3 FAIL: Exposed secrets detected"
  exit 1
else
  echo "✅ CHECK 5.3 PASS: No exposed secrets detected"
fi
```
**Remediation:** Rotate exposed secrets immediately; use secrets management system (GitHub Secrets)  
**Escalation:** Exposed credentials incident escalates to security team

### CHECK 5.4: SBOM (Software Bill of Materials) Generated
**Requirement:** SBOM in CycloneDX or SPDX format generated for release  
**Validation:** SBOM file exists in `.codex/artifacts/sbom*`  
**Command:**
```bash
if ls .codex/artifacts/sbom* 2>/dev/null | grep -q .; then
  echo "✅ CHECK 5.4 PASS: SBOM generated"
  ls -lh .codex/artifacts/sbom*
else
  echo "⚠️  CHECK 5.4 WARN: SBOM not found (generate with: cyclonedx-bom)"
fi
```
**Remediation:** Generate SBOM: `python -m cyclonedx_bom > .codex/artifacts/sbom.json`  
**Escalation:** SBOM generation failures escalate to supply chain security team

---

## Section 6: Compliance & Documentation (4 Checkpoints)

**Exit Criteria:** All 4 checks must PASS. Missing documentation blocks deployment.

### CHECK 6.1: Deployment Runbook Complete
**Requirement:** Runbook (DEPLOYMENT_GOLDEN_PATH.md) is current and complete  
**Validation:** Runbook exists and includes recovery procedures  
**Command:**
```bash
if grep -q "Recovery Procedures" .codex/DEPLOYMENT_GOLDEN_PATH.md; then
  echo "✅ CHECK 6.1 PASS: Deployment runbook complete"
else
  echo "❌ CHECK 6.1 FAIL: Deployment runbook incomplete or missing"
  exit 1
fi
```
**Remediation:** Create/update DEPLOYMENT_GOLDEN_PATH.md with current deployment procedures  
**Escalation:** Runbook gaps escalate to documentation team

### CHECK 6.2: Rollback Plan Documented
**Requirement:** Rollback procedures documented with decision tree  
**Validation:** ROLLBACK_PROCEDURES.md exists and is executable  
**Command:**
```bash
if [ -f .codex/ROLLBACK_PROCEDURES.md ] && grep -q "Failure Detection" .codex/ROLLBACK_PROCEDURES.md; then
  echo "✅ CHECK 6.2 PASS: Rollback procedures documented"
else
  echo "❌ CHECK 6.2 FAIL: Rollback procedures incomplete"
  exit 1
fi
```
**Remediation:** Create ROLLBACK_PROCEDURES.md with 8 recovery procedures and decision tree  
**Escalation:** Missing rollback procedures block deployment

### CHECK 6.3: Monitoring & Alerting Configured
**Requirement:** Post-deployment monitoring configured; alerts armed  
**Validation:** Monitoring dashboards accessible; alert thresholds set  
**Command:**
```bash
if grep -q "monitoring\|alerting\|dashboard" .codex/DEPLOYMENT_GOLDEN_PATH.md; then
  echo "✅ CHECK 6.3 PASS: Monitoring configured"
else
  echo "⚠️  CHECK 6.3 WARN: Monitoring configuration not documented"
fi
```
**Remediation:** Configure monitoring dashboards and alert rules; document in runbook  
**Escalation:** Missing monitoring escalates to SRE team

### CHECK 6.4: Communication Plan Distributed
**Requirement:** All stakeholders notified; communication channels established  
**Validation:** Stakeholder list exists and distribution confirmed  
**Command:**
```bash
if grep -q "stakeholder\|notification\|communication" .codex/DEPLOYMENT_SIGN_OFF_*.md; then
  echo "✅ CHECK 6.4 PASS: Communication plan confirmed"
else
  echo "⚠️  CHECK 6.4 WARN: Communication plan not documented"
fi
```
**Remediation:** Create stakeholder notification plan; send deployment notification email  
**Escalation:** Notify @mbaetiong if stakeholder list incomplete

---

## Integration with CI/CD Gates

### GitHub Actions Check Integration

Add this to `.github/workflows/pre-deployment-check.yml`:

```yaml
name: Pre-Deployment Validation

on:
  workflow_dispatch:
    inputs:
      check_section:
        description: "Section to validate (all|auth|code|version|artifacts|security|compliance)"
        required: false
        default: "all"

jobs:
  validation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Deployment Prerequisites Checklist
        run: |
          chmod +x .codex/scripts/deployment_prerequisites_check.sh
          .codex/scripts/deployment_prerequisites_check.sh ${{ github.event.inputs.check_section }}
      
      - name: Upload Validation Report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: deployment-validation-report
          path: .codex/validation-report.txt
```

### Manual Validation Script

Save as `.codex/scripts/deployment_prerequisites_check.sh`:

```bash
#!/bin/bash
set -e

SECTION="${1:-all}"
REPORT_FILE=".codex/validation-report.txt"
FAILED_CHECKS=0

check_status() {
  local check_name=$1
  local result=$2
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] $check_name: $result" | tee -a $REPORT_FILE
  if [[ "$result" == "FAIL" ]]; then
    ((FAILED_CHECKS++))
  fi
}

case $SECTION in
  auth|all) 
    # Run Section 1 checks
    ;;
  code|all)
    # Run Section 2 checks
    ;;
  # ... etc
esac

echo ""
echo "Validation Summary: $FAILED_CHECKS failures" | tee -a $REPORT_FILE
exit $FAILED_CHECKS
```

---

## Exit Criteria Summary

| Section | Checkpoints | Failure Impact | Escalation |
|---------|-------------|----------------|------------|
| Authorization | 5 | Deployment blocked | @mbaetiong (mandatory override) |
| Code State | 5 | Deployment blocked | Code quality team |
| Version | 4 | Deployment blocked | Release manager |
| Artifacts | 4 | Deployment blocked | Infrastructure team |
| Security | 4 | Deployment blocked | Security team |
| Compliance | 4 | Deployment blocked | Documentation team |

**SUCCESS CRITERIA:** 30/30 checks PASS  
**FAILURE CRITERIA:** Any check FAIL blocks deployment unless explicitly overridden  

---

## Remediation Procedures Quick Reference

| Issue | Quick Fix | Escalation |
|-------|-----------|-----------|
| Governance gates FAIL | Run `governance_gate_audit.py` | @mbaetiong |
| Test coverage <90% | Add tests for low-coverage modules | Code review |
| Linting errors | Run `ruff check --fix` | Code quality |
| Security findings | Remediate via SAST dashboard | Security team |
| Version mismatch | Update pyproject.toml | Release manager |
| Missing artifacts | Run `python -m build` | Release engineering |
| CodeQL findings | Run remediation agent | Security team |

---

## Document Status

**Version:** 1.0  
**Maintained By:** Deployment Engineering  
**Last Review:** 2026-07-09  
**Next Review:** Post-v0.2.0 release  

For questions or procedure updates, contact @mbaetiong or file an issue.
