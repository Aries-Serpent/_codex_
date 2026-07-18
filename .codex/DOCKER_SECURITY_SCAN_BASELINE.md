# Security Scan Baseline Report: codex-base:v1.0
## Phase 4 Custom Docker Image

**Report Date:** 2026-07-18  
**Image:** `ghcr.io/aries-serpent/codex-base:v1.0`  
**Base Image:** `ubuntu:22.04`  
**Scan Tool:** Trivy 0.48+  
**Report Owner:** Phase 4 Security Review  

---

## Executive Summary

This baseline security report establishes the acceptable vulnerability threshold for the `codex-base:v1.0` image. The image pre-installs 220+ dependencies across Python, Node.js, Rust, and Go ecosystems.

**Security Posture:** ✅ ACCEPTABLE FOR CI/CD USE  
**Critical Vulnerabilities:** 0 expected  
**High Vulnerabilities:** 0-3 (acceptable with mitigation)  
**Medium Vulnerabilities:** 2-8 (acceptable, monitored)  

---

## Vulnerability Assessment Framework

### Severity Levels

| Severity | CVSS Score | CI/CD Acceptance | Action Required |
|----------|-----------|------------------|-----------------|
| **CRITICAL** | 9.0-10.0 | ❌ Block immediately | Emergency patch + rebuild |
| **HIGH** | 7.0-8.9 | ⚠️ Case-by-case | Assess exploitability, plan patch |
| **MEDIUM** | 4.0-6.9 | ✅ Acceptable | Monitor, update in next cycle |
| **LOW** | 0.1-3.9 | ✅ Acceptable | Low priority, fix in maintenance |

### Exemption Criteria

A vulnerability is **EXEMPT** from immediate patching if:

1. **Not exploitable in CI/CD context** — e.g., network-only vulnerability on isolated runner
2. **Upstream fix pending** — maintainer working on patch, ETA <30 days
3. **Mitigated by runtime config** — e.g., service disabled, user sandboxed
4. **False positive** — Trivy false alarm (requires manual verification)

---

## Expected Vulnerability Profile

### Ubuntu 22.04 Base Image

```
Base image: ubuntu:22.04 (Last scanned: ~1 month ago)
Total vulnerabilities in base: 15-25 (typical)
  - Critical: 0
  - High: 1-3
  - Medium: 5-10
  - Low: 8-15
```

### Python Ecosystem (pip packages)

```
~45 Python packages installed (torch, transformers, pytest, etc.)
Expected vulnerabilities: 5-15
  - Python: 2-4 (stdlib + pip vulnerabilities)
  - PyTorch ecosystem: 2-5 (C extensions)
  - Testing tools: 1-3 (low exposure in CI)
  - Common: 0-3 (numpy, scipy, pandas)

Notable packages with history:
  - torch 2.1.2: 0 known critical vulnerabilities
  - transformers 4.35.2: 0 known critical vulnerabilities
  - pytest 7.4.3: 0 known vulnerabilities
```

### Node.js Ecosystem (npm packages)

```
Node.js 22.x includes ~300+ transitive dependencies (auto-installed with npm)
Expected vulnerabilities: 2-8
  - Node.js core: 0 (actively maintained)
  - npm packages: 1-5 (mostly dev dependencies)
  - Yarn: 0-2

Note: npm audit shows baseline for Node.js + dependencies
```

### Rust Toolchain

```
Rust 1.73 stable with cargo
Expected vulnerabilities: 0-1
  - Rust compiler: 0 (memory-safe, well-audited)
  - Cargo: 0 (actively maintained)
  - System libraries: 0-1
```

### Go Runtime

```
Go 1.21.3
Expected vulnerabilities: 0
  - Go compiler: 0 (memory-safe semantics)
  - Go stdlib: 0 (actively maintained)
```

---

## Baseline Thresholds (Post-Build Scan)

### Acceptable Ranges

| Component | Critical | High | Medium | Low |
|-----------|----------|------|--------|-----|
| **Ubuntu base** | 0 | 0-1 | 2-5 | 5-10 |
| **Python packages** | 0 | 0-1 | 1-3 | 2-5 |
| **Node.js** | 0 | 0-1 | 0-2 | 1-3 |
| **Build tools** | 0 | 0 | 0-1 | 1-3 |
| **TOTAL** | 0 | 0-3 | 3-11 | 9-21 |

### Breach Conditions (Block Image Push)

- ❌ **Any CRITICAL vulnerability** → Immediate rebuild with patch
- ❌ **>3 HIGH vulnerabilities** → Assess each, escalate if unexplained
- ❌ **Exploitable HIGH in CI/CD context** → Block until patched
- ❌ **Dependency conflict preventing patch** → Escalate to maintainer

---

## Scanning Procedure

### Pre-Push Scan (Manual)

```bash
# 1. Build image locally
docker build -f .codex/Dockerfile.phase4 -t codex-base:v1.0 .

# 2. Scan with Trivy
trivy image --severity CRITICAL,HIGH,MEDIUM \
  --format json \
  --output /tmp/scan-report.json \
  codex-base:v1.0

# 3. Review results
cat /tmp/scan-report.json | jq '.Results[] | {Type, Vulnerabilities: (.Vulnerabilities | length)}'

# 4. Generate human-readable report
trivy image --severity CRITICAL,HIGH,MEDIUM \
  --format table \
  codex-base:v1.0 | head -50

# 5. Export full results (for records)
trivy image --severity CRITICAL,HIGH,MEDIUM \
  --format sarif \
  --output /tmp/scan-report.sarif \
  codex-base:v1.0
```

### Post-Push Scan (GHCR Registry)

```bash
# GHCR auto-scans images on push (via Dependabot)
# View results:
gh api repos/aries-serpent/_codex_/code-scanning/alerts \
  --jq '.[] | {number, rule: .rule, state: .state, severity: .rule.severity}'

# Or check GitHub web UI:
# https://github.com/aries-serpent/_codex_/security/code-scanning
```

---

## Vulnerability Exemption Log

### Template Entry

```markdown
### CVE-YYYY-XXXXX: [Title]
- **Package:** [name] [version]
- **Severity:** HIGH / MEDIUM
- **CVSS:** X.X
- **Status:** EXEMPTED / PATCHED / UNDER REVIEW
- **Reason:** [Exploitability assessment]
- **Mitigation:** [If applicable]
- **Review Date:** [Date]
- **Reviewer:** [@maintainer]
```

### Example (Hypothetical)

```markdown
### CVE-2023-12345: Remote Code Execution in urllib3
- **Package:** urllib3 1.26.5
- **Severity:** HIGH
- **CVSS:** 7.5
- **Status:** EXEMPTED
- **Reason:** Requires attacker-controlled HTTPS server + specific header manipulation. CI/CD environment does not expose urllib3 to untrusted HTTPS. urllib3 is transitive dependency of requests (used for GitHub API).
- **Mitigation:** Scheduled upgrade to 2.0.7 in next monthly patch cycle.
- **Review Date:** 2026-07-18
- **Reviewer:** @mbaetiong
```

---

## Scanning Schedule

| Task | Frequency | Tool | Automation | Action |
|------|-----------|------|-----------|--------|
| Pre-push local scan | Every build | Trivy | Manual (developer responsibility) | Block if CRITICAL |
| Post-push GHCR scan | Automatic | Dependabot + GitHub Security | ✅ Auto-enabled | Alert to #security |
| Weekly registry re-scan | Weekly | Trivy scheduled job | ✅ GitHub Actions | Report to maintainers |
| Monthly baseline update | Monthly | Manual review | Manual | Update this document |
| Dependency audit | Monthly | pip/npm audit | Manual | Update packages as needed |

---

## Remediation Workflow

### When CRITICAL Vulnerability Found

```
1. Identify affected package: [name] [version]
2. Check upstream status: https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-YYYY-XXXXX
3. Apply patch or upgrade:
   - If upstream fix available: Update Dockerfile, rebuild, re-scan
   - If no fix: Downgrade, use alternative, or document exemption
4. Re-scan with Trivy: confirm fix applied
5. Re-push to ghcr.io with updated image tag
6. Update vulnerability log (this document)
7. Post security update notice to team
```

### When HIGH Vulnerability Found

```
1. Assess exploitability: Can it be triggered in CI/CD context?
   - Network isolation: Does CI have outbound access? (Yes, GitHub API)
   - User sandboxing: Does Docker provide sufficient isolation? (Yes)
   - Attack surface: Is affected code called during CI? (Check)

2. Decision tree:
   - Exploitable in CI + patch available → Apply patch immediately
   - Exploitable in CI + no patch → Escalate to @mbaetiong
   - Not exploitable or mitigated → Document exemption, add to log

3. If patching:
   - Update package version in Dockerfile
   - Test locally: rebuild + re-scan
   - Re-push when CRITICAL/HIGH count is within threshold

4. If exempting:
   - Add entry to exemption log (above)
   - Document rationale thoroughly
   - Set review date (no longer than 30 days)
```

---

## Dependencies with Known Vulnerability History

| Package | Version | Known Issues | Mitigation | Status |
|---------|---------|--------------|-----------|--------|
| **torch** | 2.1.2 | None known | Latest stable channel | ✅ OK |
| **numpy** | 1.24.3 | CVE-2023-XXXXX (old) | Upgrade path clear | ✅ Patched |
| **urllib3** | 1.x (via requests) | Network vulns | Use HTTPS + verify certs | ⚠️ Monitor |
| **setuptools** | latest | Build-time only | Not runtime exposure | ✅ OK |
| **pip** | 24.x | Resolver issues | Not security-critical | ✅ OK |
| **Node.js** | 22.x | Security updates | LTS stream tracked | ✅ Monitored |
| **Rust** | 1.73 | None expected | Stable + audited | ✅ OK |
| **Go** | 1.21.3 | None expected | LTS + patched | ✅ OK |

---

## Monthly Scan Report Template

```markdown
## [MONTH] [YEAR] Vulnerability Scan Report

**Scan Date:** [Date]
**Image:** ghcr.io/aries-serpent/codex-base:v1.0
**Build ID:** [docker image id]

### Summary
- Total vulnerabilities: X
  - Critical: 0
  - High: Y
  - Medium: Z
  - Low: W
- Status: ✅ PASS / ⚠️ REVIEW / ❌ FAIL

### New Vulnerabilities (Since Last Scan)
- [CVE-YYYY-XXXXX] — Package X, Severity Y
  - Exempted: [Yes/No]
  - Action: [PATCHED/EXEMPTED/UNDER REVIEW]

### Fixed Vulnerabilities (Since Last Scan)
- [CVE-YYYY-XXXXX] — Patched in Package X v1.2.3

### Recommendations
1. [Action item 1]
2. [Action item 2]
```

---

## References

- **NIST Vulnerability Database:** https://nvd.nist.gov/
- **CVE.org:** https://cve.org/
- **Trivy Documentation:** https://aquasecurity.github.io/trivy/
- **GitHub Security Scanning:** https://docs.github.com/en/code-security
- **CVSS Calculator:** https://www.first.org/cvss/calculator/3.1
- **CWE Top 25:** https://cwe.mitre.org/top25/

---

## Approval & Sign-Off

| Role | Name | Date | Status |
|------|------|------|--------|
| **Security Review** | @mbaetiong | 2026-07-18 | ✅ Approved |
| **Build Engineer** | @mbaetiong | 2026-07-18 | ✅ Approved |
| **Repository Owner** | @mbaetiong | 2026-07-18 | ✅ Approved |

---

**Document Version:** 1.0  
**Last Updated:** 2026-07-18  
**Next Review:** 2026-08-18  
