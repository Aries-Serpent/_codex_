# Security Enforcement Gates — _codex_ Repository

**Version**: 1.0  
**Date**: 2026-06-27  
**Status**: Phase 4, Lane 2 — ACTIVE  
**Owner**: Security Automation Team

---

## Overview

This document specifies the security enforcement gates that block or warn on code changes based on SAST findings. Each gate is implemented as a GitHub Actions workflow step that parses security tool output and fails the job if severity thresholds are exceeded.

---

## Gate Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   Code Change (Push / PR)                       │
└────────────────────────────────┬────────────────────────────────┘
                                 │
         ┌───────────────────────┼────────────────────────────┐
         │                       │                            │
         ▼                       ▼                            ▼
    ┌─────────┐            ┌──────────┐             ┌─────────────┐
    │ Semgrep │            │ pip-audit│             │  Bandit     │
    │  SAST   │            │  Vulns   │             │ Security    │
    └────┬────┘            └────┬─────┘             └─────┬───────┘
         │                      │                        │
         │ [HIGH/CRITICAL]      │ [CRITICAL]             │ [CRITICAL]
         │                      │                        │
         └──────────────┬───────┴────────────────────────┘
                        │
                        ▼
              ┌──────────────────────┐
              │ Parse Severity Level │
              └──────┬───────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
     [BLOCK]              [WARN/ADVISORY]
         │                       │
         ▼                       ▼
    Fail Job              Continue with warning
    Exit code 1           (advisory only)
```

---

## Gate 1: Semgrep SAST

### Configuration

**Workflow**: `.github/workflows/semgrep_sarif.yml`  
**Trigger**: Push (main, develop, copilot/*), PR (main, develop), scheduled (daily 3 AM), manual dispatch  
**Runtime**: ~10 minutes  
**Permissions**: `contents:read`, `security-events:write`

### Enforcement Rules

| Severity | Count | Behavior | Action |
|----------|-------|----------|--------|
| CRITICAL | > 0 | Block | Fail job, block PR |
| HIGH | > 0 | Block | Fail job, block PR |
| MEDIUM | — | Warning | Log warning, continue |
| LOW | — | Advisory | Log info, continue |

### SARIF Output

Semgrep generates SARIF (Static Analysis Results Interchange Format) for direct ingestion into GitHub Security:

```bash
returntocorp/semgrep-action@v1 --generateSarif true
github/codeql-action/upload-sarif@v4 --sarif-file semgrep.sarif
```

### Bypass Policy

**Breaks Semgrep gates** require:
- Issue approval from security team lead
- Documented suppression in `.codex/security/SUPPRESSIONS_LOG.md`
- Mitigation controls documented in PR description

### Configuration Profiles

```yaml
config: >-
  p/security-audit      # Top security rules
  p/python              # Python-specific checks
  p/owasp-top-ten       # OWASP Top 10
```

See: [Semgrep Registry](https://semgrep.dev/r)

---

## Gate 2: pip-audit (Dependency Vulnerabilities)

### Configuration

**Workflow**: `.github/workflows/scheduled-dependency-audit.yml` (dependency-audit job)  
**Trigger**: PR (changes to `requirements*.txt`, `pyproject.toml`), scheduled (weekly Monday)  
**Runtime**: ~5 minutes  
**Permissions**: `contents:read`, `security-events:write`

### Enforcement Rules

| Severity | Count | Behavior | Action |
|----------|-------|----------|--------|
| CRITICAL | > 0 | Block | Fail job, block PR merge |
| HIGH | > 0 | Warning | Log warning, allow merge |
| MEDIUM | — | Advisory | Log info, continue |
| LOW | — | Advisory | Log info, continue |

### Detection Logic

```bash
pip-audit -r requirements.txt -r requirements-dev.txt \
  --format json -o ci_pip_audit.json

# Parse CRITICAL severity from JSON output
if grep -i 'CRITICAL' pip_audit_output.txt; then
  echo "::error::CRITICAL CVE detected"
  exit 1  # Block PR
fi
```

### Output Formats

1. **JSON** → `.codex/reports/ci_pip_audit.json` (machine-readable)
2. **CycloneDX** → `.codex/reports/ci_pip_audit_cyclonedx.json` (SBOM-compatible)
3. **Text** → Logged to workflow summary for human review

### Remediation Workflow

1. **Detect**: pip-audit identifies CVE
2. **Analyze**: Check if fix available (`pip-audit --desc`)
3. **Upgrade**: Bump package version in `requirements.txt`
4. **Test**: Verify build and tests pass
5. **Review**: Security team approves version change
6. **Commit**: Merge dependency update PR

### Known Exemptions

None at this time. All CRITICAL CVEs block PRs.

---

## Gate 3: Bandit (Python Security)

### Configuration

**Workflow**: `.github/workflows/code-quality-coverage-suite.yml` (bandit step)  
**Trigger**: PR (changes to src/ or scripts/), push (main), dispatch  
**Runtime**: ~2 minutes  
**Permissions**: `contents:read`

### Enforcement Rules

| Severity | Count | Behavior | Action |
|----------|-------|----------|--------|
| CRITICAL (HIGH + HIGH confidence) | > 0 | Block | Fail job, block PR |
| HIGH | > 0 | Warning | Log warning, allow merge |
| MEDIUM | — | Advisory | Log info, continue |
| LOW | — | Advisory | Log info, continue |

### Detection Logic

```bash
bandit -r src/ --configfile .bandit \
  -f json -o bandit-report.json \
  -f txt -o bandit-output.txt

# Count CRITICAL and HIGH
CRITICAL_COUNT=$(jq '[.results[] | select(.severity == "HIGH" and .confidence == "HIGH")] | length' bandit-report.json)
HIGH_COUNT=$(jq '[.results[] | select(.severity == "HIGH")] | length' bandit-report.json)

if [ $CRITICAL_COUNT -gt 0 ]; then
  echo "::error::Bandit found ${CRITICAL_COUNT} CRITICAL issues"
  exit 1  # Block PR
fi
```

### Configuration File

**Location**: `.bandit` (YAML format)

Key skips (security-justified):
- B101: assert_used (test pattern)
- B110/B112: try/except/pass (optional imports with graceful fallback)
- B311: random (non-cryptographic use only)
- B403: pickle (trusted internal files only)
- B404/B603/B607: subprocess (no shell=True, safe execution)
- B310: urlopen (hardcoded HTTPS GitHub API only)

### Remediation Strategy

1. **Auto-fix**: Use Bandit's suggestion (e.g., use `secrets` module instead of `random`)
2. **Suppress**: Add `# nosec BXXX` comment with documented rationale
3. **Redesign**: Refactor code to eliminate dangerous pattern

---

## Gate 4: CodeQL Analysis

### Configuration

**Workflow**: `.github/workflows/security-scanning-suite.yml` (codeql-scan job)  
**Trigger**: Push (main, develop, copilot/*), PR (main, develop), scheduled (daily 2 AM + Sunday 3 AM)  
**Runtime**: ~40-50 minutes  
**Permissions**: `actions:read`, `contents:read`, `security-events:write`

### Enforcement Model

**Advisory Mode** (current):
- HIGH/MEDIUM findings reported to GitHub Security tab
- Does NOT block PR merge
- Findings tracked in `.codex/security/codeql_alert_inventory.json`

**Blocking Mode** (after Phase 4):
- CRITICAL findings (0 expected) block PR
- HIGH findings require documented suppression
- MEDIUM findings advisory

### Languages

| Language | Status | Continue-on-Error |
|----------|--------|-------------------|
| Python | ✅ Required | false (must pass) |
| JavaScript | ⚠️ Optional | true (may fail) |

### Queries

```yaml
languages: [python, javascript]
queries: +security-extended,security-and-quality
```

Scope:
- `security-extended`: Deep security rules
- `security-and-quality`: Security + code quality

### Current Alert Summary

| Severity | Count | Status |
|----------|-------|--------|
| HIGH | 36 | IN_REMEDIATION (code-fix) |
| MEDIUM | 30 | IN_REMEDIATION (code-fix + suppress) |
| LOW | 0 | — |
| **Total** | 66 | Target: 0 HIGH/MEDIUM |

**Remediation**: Delegated to `codeql-alert-resolution-agent`

---

## Gate Integration

### PR Check Status

When a PR is opened, all gates run in parallel:

```
GitHub PR
  ├─ Semgrep SAST (10 min)
  │   └─ [BLOCK] if HIGH/CRITICAL found
  ├─ pip-audit (5 min)
  │   └─ [BLOCK] if CRITICAL CVE found
  ├─ Bandit (2 min)
  │   └─ [BLOCK] if CRITICAL issue found
  └─ CodeQL (45 min)
      └─ [WARN] if HIGH/MEDIUM found

Result: PR can merge only if all gates pass
```

### Branch Protection Rules

**Main Branch** (`main`):
- Require semgrep ✅
- Require pip-audit ✅
- Require bandit ✅
- Require CodeQL (advisory → blocking after Phase 4)
- Require status checks to pass
- Dismiss stale PR approvals on new commits

**Develop Branch** (`develop`):
- Same gates as main
- Require codeql-alert-resolution-agent approval for CodeQL findings

---

## Severity Definitions

### SAST Severities

| Level | Definition | Example | Action |
|-------|-----------|---------|--------|
| **CRITICAL** | Exploitable vulnerability with high impact | SQL injection, RCE, auth bypass | Immediate fix required |
| **HIGH** | Significant security risk | Weak crypto, hardcoded secrets, dangerous function use | Fix required before merge |
| **MEDIUM** | Potential security issue | Log injection, unvalidated input | Review and suppress with reason |
| **LOW** | Information or code quality issue | Unused variable, code smell | Advisory only |

### CVE Severity (CVSS)

| Level | CVSS Score | Action |
|-------|-----------|--------|
| **CRITICAL** | 9.0 - 10.0 | Block PR, open emergency issue |
| **HIGH** | 7.0 - 8.9 | Block PR, open P2 issue |
| **MEDIUM** | 4.0 - 6.9 | Warn, create tracking issue |
| **LOW** | 0.0 - 3.9 | Advisory, log only |

---

## Workflow Artifacts

### Output Files

Each gate produces artifacts stored in GitHub Actions:

| Gate | Output File | Format | Retention |
|------|-------------|--------|-----------|
| Semgrep | `semgrep.sarif` | SARIF/JSON | 30 days |
| pip-audit | `ci_pip_audit.json` | JSON | 30 days |
| pip-audit | `ci_pip_audit_cyclonedx.json` | CycloneDX | 30 days |
| Bandit | `bandit-report.json` | JSON | 30 days |
| CodeQL | `codeql-sarif/*.sarif` | SARIF | 30 days |

### Artifact Access

Via GitHub Actions UI:
1. Click **Artifacts** at bottom of workflow run
2. Download desired security report
3. View in SARIF viewer or parse locally

---

## Troubleshooting & Overrides

### Override Procedures

**If a gate blocks a legitimate PR:**

1. **Assessment**: Verify the finding is a false positive
2. **Documentation**: Comment in PR with:
   - Finding ID and severity
   - Why it's not a real vulnerability
   - Mitigation or code change
3. **Approval**: Request security team review (`@security-team`)
4. **Tracking**: Create suppression entry in `.codex/security/SUPPRESSIONS_LOG.md`
5. **Bypass**: Security lead approves, finding suppressed

### Common False Positives

| Tool | Pattern | Root Cause | Fix |
|------|---------|-----------|-----|
| Bandit | B101 (assert) | Tests using assertions | Suppress B101 in config |
| Bandit | B310 (urlopen) | GitHub API only | Suppress for hardcoded HTTPS |
| CodeQL | Log injection | Parameterized logging | Use logging formatter |
| Semgrep | SQL injection | Parameterized queries | Verify parameterization |

---

## Monitoring & Metrics

### Dashboard Metrics

Track over time:
- **Open findings by severity** (target: 0 HIGH/CRITICAL)
- **Finding resolution time** (SLA: CRITICAL < 1 day, HIGH < 1 week)
- **False positive rate** (target: < 5%)
- **Gate pass rate** (target: > 95% of runs)

### Reporting

Monthly security report:
- Gate pass/fail stats
- Top finding categories
- Remediation backlog
- Suppression justifications

---

## Gate Maintenance

### Update Schedule

| Activity | Frequency | Owner |
|----------|-----------|-------|
| Semgrep rule updates | Monthly | Security team |
| pip-audit CVE refresh | Daily (automated) | GitHub |
| Bandit config review | Quarterly | Security team |
| CodeQL rule updates | Per CodeQL release | GitHub |

### Escalation

**If gate is down/broken:**
1. Post issue in `#security` channel
2. Disable gate temporarily with documentation
3. File bug with reproduction steps
4. Restore gate when fixed

---

## Related Documentation

- **Semgrep Docs**: https://semgrep.dev/docs
- **pip-audit Docs**: https://github.com/pypa/pip-audit
- **Bandit Docs**: https://bandit.readthedocs.io
- **CodeQL Docs**: https://codeql.github.com/docs
- **SARIF Spec**: https://sarifweb.azurewebsites.net/
- **Security Posture**: `.codex/SECURITY_POSTURE.md`

---

**Last Updated**: 2026-06-27  
**Next Review**: 2026-09-27 (quarterly)  
**Contact**: @security-team

