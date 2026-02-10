# CodeQL Alert Resolution Planset

> **Status:** 🚧 Active Development  
> **Created:** 2026-01-26  
> **Author:** AI Agent via mbaetiong  
> **Objective:** Systematically resolve, comment, and close all CodeQL code scanning alerts across 59 pages

---

## 📋 Executive Summary

This planset provides a comprehensive framework for addressing all code scanning alerts detected by CodeQL in the Aries-Serpent/_codex_ repository. With alerts spanning 59 pages (~1,500+ potential alerts), this document outlines a phased, systematic approach to vulnerability remediation, validation, and closure.

### Key Objectives
1. ✅ **Discover & Categorize**: Fetch and classify all code scanning alerts
2. 🎯 **Prioritize**: Rank alerts by severity, exploitability, and impact
3. 🔧 **Remediate**: Fix vulnerabilities using automated and manual approaches
4. ✔️ **Validate**: Verify fixes don't introduce regressions
5. 📝 **Document**: Comment and close alerts with proper justification
6. 🛡️ **Prevent**: Implement safeguards to prevent future issues

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    CodeQL Alert Resolution                  │
│                        Workflow                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 1: Alert Discovery & Categorization                  │
│  - Fetch all alerts via GitHub API (59 pages)              │
│  - Categorize by CWE, severity, file path                  │
│  - Generate alert inventory JSON/CSV                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 2: Priority-based Resolution Strategy                │
│  - Critical/High: Immediate attention                       │
│  - Medium: Scheduled remediation                            │
│  - Low: Batch processing                                    │
│  - Create resolution roadmap                                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 3: Automated Fix Generation                          │
│  - Use security agent for common patterns                   │
│  - Apply security codemods                                  │
│  - Generate fix PRs with test cases                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 4: Manual Review & Remediation                       │
│  - Complex vulnerabilities requiring human judgment         │
│  - False positive identification and documentation          │
│  - Custom fixes for unique scenarios                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 5: Verification & Closure                            │
│  - Run security regression tests                            │
│  - Verify fixes with CodeQL re-scan                         │
│  - Comment on alerts with fix details                       │
│  - Close resolved alerts via API                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 6: Documentation & Prevention                        │
│  - Update security documentation                            │
│  - Add security guidelines to CONTRIBUTING.md               │
│  - Implement pre-commit security hooks                      │
│  - Schedule recurring CodeQL scans                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Phase 1: Alert Discovery & Categorization

### Objectives
- Fetch all code scanning alerts from GitHub API (59 pages, ~30 alerts/page)
- Categorize alerts by type, severity, CWE, and affected module
- Generate comprehensive alert inventory

### Tasks

#### 1.1 Create Alert Fetcher Script
**Location:** `scripts/security/fetch_codeql_alerts.py`

**Features:**
- Paginated API calls to fetch all 59 pages
- Rate limit handling (5000 requests/hour for authenticated)
- Export to JSON, CSV, and Markdown formats
- Deduplication logic for repeat alerts

**API Endpoint:**
```
GET /repos/Aries-Serpent/_codex_/code-scanning/alerts
  ?state=open
  &page={1..59}
  &per_page=100
```

**Output Schema:**
```json
{
  "alert_number": 123,
  "rule_id": "py/sql-injection",
  "severity": "high",
  "state": "open",
  "cwe_id": "CWE-89",
  "file_path": "src/codex/database.py",
  "line_start": 145,
  "line_end": 148,
  "description": "SQL query built from user input",
  "created_at": "2026-01-15T10:30:00Z",
  "html_url": "https://github.com/..."
}
```

#### 1.2 Categorization Logic
**Categories:**
- **Injection Vulnerabilities**: SQL injection, command injection, XSS
- **Path Traversal**: Unsafe file operations
- **Cryptographic Issues**: Weak algorithms, hardcoded secrets
- **Authentication/Authorization**: Privilege escalation, broken auth
- **Information Disclosure**: Sensitive data exposure
- **Resource Management**: Memory leaks, DoS vulnerabilities
- **Error Handling**: Unsafe error messages, exception handling

#### 1.3 Generate Alert Inventory
**Outputs:**
- `.codex/security/alert_inventory.json` - Full alert data
- `.codex/security/alert_summary.md` - Human-readable summary
- `.codex/security/alert_roadmap.csv` - Prioritized resolution plan

---

## 🎯 Phase 2: Priority-based Resolution Strategy

### Objectives
- Rank alerts by severity, exploitability, and business impact
- Create resolution roadmap with time estimates
- Assign alerts to automated vs. manual workflows

### Priority Matrix

| Severity | Exploitability | Resolution Priority | Target SLA |
|----------|----------------|---------------------|------------|
| Critical | High | P0 | 24 Commits |
| Critical | Medium | P1 | 3 iterations |
| High | High | P1 | 3 iterations |
| High | Medium | P2 | 1 phase |
| Medium | High | P2 | 1 phase |
| Medium | Medium | P3 | 2 phases |
| Low | Any | P4 | 1 month |

### Alert Routing Rules

**Automated Resolution (60% of alerts):**
- SQL injection with clear parameterization fix
- Hardcoded secrets → Environment variables
- Unsafe subprocess calls → Parameterized commands
- Path traversal → Path validation utilities

**Manual Review Required (30% of alerts):**
- Complex authentication logic
- Business logic vulnerabilities
- Multi-file architectural issues
- Requires design pattern changes

**False Positives (10% of alerts):**
- Test code intentionally demonstrating vulnerabilities
- Validated edge cases with proper sanitization
- Third-party library code outside our control

---

## 🎯 Phase 3: Automated Fix Generation

### Objectives
- Apply automated fixes for common vulnerability patterns
- Generate test cases to validate fixes
- Create PRs for batch review

### Tools & Frameworks

#### 3.1 Security Agent Integration
**Script:** `.github/copilot-security/security_agent.py`

**Capabilities:**
- Pattern-based fix generation
- AST-aware code transformations
- Test case synthesis
- Validation before/after fix

**Usage:**
```python
from security_agent import CopilotSecurityAgent

agent = CopilotSecurityAgent(repo_path=".", github_token="...")
vulns = await agent.scan_for_vulnerabilities()
for vuln in vulns:
    fix = await agent.generate_fix(vuln)
    if fix and fix.confidence > 0.8:
        apply_fix(fix)
```

#### 3.2 Security Codemods
**Location:** `scripts/security/codemods/`

**Available Codemods:**
- `fix_sql_injection.py` - Converts string concatenation to parameterized queries
- `fix_subprocess.py` - Adds shell=False and argument validation
- `fix_hardcoded_secrets.py` - Migrates to environment variables
- `fix_path_traversal.py` - Adds path sanitization

#### 3.3 Automated PR Generation
**Workflow:**
1. Group alerts by module/file
2. Generate fixes for all alerts in group
3. Run tests to validate fixes
4. Create PR with:
   - Alert numbers resolved
   - Fix descriptions
   - Test results
   - Validation checklist

**PR Template:**
```markdown
## Security Fix: [Module Name]

### Alerts Resolved
- #123: SQL injection in database.py:145
- #456: Command injection in cli.py:89

### Changes Made
- Converted string concatenation to parameterized queries
- Added input validation for CLI commands

### Validation
- [x] All existing tests pass
- [x] New test cases added
- [x] CodeQL re-scan clean
- [x] Security team review (for P0/P1)

### Related Alerts
Closes: https://github.com/Aries-Serpent/_codex_/security/code-scanning/123
Closes: https://github.com/Aries-Serpent/_codex_/security/code-scanning/456
```

---

## 🎯 Phase 4: Manual Review & Remediation

### Objectives
- Address complex vulnerabilities requiring architectural changes
- Document false positives with justification
- Implement custom fixes for unique scenarios

### Manual Review Workflow

#### 4.1 Complex Vulnerabilities
**Examples:**
- Authentication logic requiring redesign
- Race conditions in concurrent code
- Business logic vulnerabilities
- Cryptographic protocol issues

**Process:**
1. **Analysis:** Document root cause and impact
2. **Design:** Propose secure solution with alternatives
3. **Review:** Security team and stakeholder approval
4. **Implementation:** Implement with comprehensive tests
5. **Validation:** Penetration testing for critical issues

#### 4.2 False Positive Management
**Documentation Standard:**
```markdown
## False Positive: Alert #789

**Rule:** py/path-traversal
**File:** tests/security/test_path_validation.py:45
**Justification:** 
This is a test case intentionally demonstrating path traversal 
detection. The test validates that our sanitization logic correctly 
blocks malicious paths.

**Evidence:**
- Test file in `tests/` directory
- Proper input validation applied in production code
- Mock filesystem used, no real file access

**CodeQL Suppression:**
```python
# codeql[py/path-traversal]
test_path = "../../../etc/passwd"  # Intentional test case
```

**Approval:** @security-team
**Date:** 2026-01-26
```

#### 4.3 Custom Fix Development
**Guidelines:**
- Follow existing security patterns in codebase
- Use security utilities from `src/codex/security_utils.py`
- Add comprehensive test coverage (unit + integration)
- Document security considerations in code comments

---

## 🎯 Phase 5: Verification & Closure

### Objectives
- Validate all fixes don't introduce regressions
- Re-run CodeQL to confirm alert closure
- Update alert status via GitHub API
- Track resolution metrics

### Verification Checklist

#### 5.1 Pre-Closure Validation
```yaml
- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] CodeQL re-scan shows alert resolved
- [ ] Security regression tests added
- [ ] Peer review completed
- [ ] Documentation updated
```

#### 5.2 Alert Closure Script
**Location:** `scripts/security/close_codeql_alert.py`

**Features:**
- Close alert via GitHub API
- Add closure comment with fix details
- Link to fix PR/commit
- Update alert inventory

**API Call:**
```http
PATCH /repos/Aries-Serpent/_codex_/code-scanning/alerts/{alert_number}
{
  "state": "dismissed",
  "dismissed_reason": "fixed",
  "dismissed_comment": "Fixed in PR #1234: Added parameterized queries to prevent SQL injection"
}
```

#### 5.3 Resolution Tracking
**Dashboard:** `.codex/security/resolution_dashboard.md`

**Metrics:**
- Total alerts: 1,500
- Resolved: 450 (30%)
- In progress: 300 (20%)
- Pending review: 150 (10%)
- False positives: 100 (7%)
- Remaining: 500 (33%)

**Visualizations:**
- Resolution velocity chart
- Severity distribution
- Module-level heatmap
- CWE frequency analysis

---

## 🎯 Phase 6: Documentation & Prevention

### Objectives
- Document security best practices
- Implement preventive measures
- Establish ongoing security monitoring

### Documentation Updates

#### 6.1 Security Guidelines
**Location:** `docs/security/SECURITY_GUIDELINES.md`

**Topics:**
- Secure coding patterns
- Input validation best practices
- Authentication/authorization patterns
- Cryptographic recommendations
- Dependency security

#### 6.2 Contribution Guidelines
**Update:** `CONTRIBUTING.md`

**Additions:**
- Security review requirements for PRs
- Required security tools (Bandit, CodeQL)
- How to run security scans locally
- Reporting security issues

#### 6.3 Pre-commit Hooks
**Configuration:** `.pre-commit-config.yaml`

**Security Checks:**
```yaml
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: ['-c', '.bandit.yaml']
  
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
```

### Prevention Measures

#### 6.4 Recurring Security Scans
**Workflow:** `.github/workflows/codeql-analysis.yml`

**Schedule:**
- Weekly full CodeQL scan (Sunday 3 AM UTC)
- per-iteration incremental scan for changed files
- Pre-merge security gate for PRs

#### 6.5 Security Training
**Resources:**
- OWASP Top 10 training materials
- CWE database references
- Internal secure coding workshops
- Quarterly security reviews

---

## 📊 Implementation Timeline

### Week 1: Setup & Discovery
- **Days 1-2:** Create alert fetcher script
- **Days 3-4:** Run full alert discovery (59 pages)
- **Days 5-7:** Categorization and prioritization

### Weeks 2-4: P0/P1 Alerts (Critical/High)
- **Week 2:** Automated fixes for injection vulnerabilities
- **Week 3:** Manual fixes for authentication issues
- **Week 4:** Validation and closure (P0/P1)

### Weeks 5-8: P2/P3 Alerts (Medium/Low)
- **Weeks 5-6:** Batch processing medium severity alerts
- **Weeks 7-8:** Low priority and false positive documentation

### Week 9: Final Validation
- **Days 1-3:** Full CodeQL re-scan
- **Days 4-5:** Documentation updates
- **Days 6-7:** Team training and handoff

### Week 10: Prevention & Monitoring
- **Days 1-3:** Implement pre-commit hooks
- **Days 4-5:** Configure recurring scans
- **Days 6-7:** Security review process documentation

---

## 🛠️ Required Tools & Scripts

### Core Scripts

#### 1. Alert Fetcher
**File:** `scripts/security/fetch_codeql_alerts.py`
**Purpose:** Fetch all alerts from GitHub API
**Dependencies:** `requests`, `json`, `csv`

#### 2. Alert Categorizer
**File:** `scripts/security/categorize_alerts.py`
**Purpose:** Group and prioritize alerts
**Dependencies:** `pandas`, `yaml`

#### 3. Alert Closer
**File:** `scripts/security/close_codeql_alert.py`
**Purpose:** Close alerts via API with comments
**Dependencies:** `requests`, `argparse`

#### 4. Security Dashboard Generator
**File:** `scripts/security/generate_dashboard.py`
**Purpose:** Create HTML/Markdown dashboard
**Dependencies:** `jinja2`, `matplotlib`

#### 5. Fix Validator
**File:** `scripts/security/validate_fixes.py`
**Purpose:** Run security regression tests
**Dependencies:** `pytest`, `bandit`

### Utility Functions

**File:** `scripts/security/utils.py`

```python
def fetch_all_alerts(owner: str, repo: str, token: str) -> List[Dict]:
    """Fetch all code scanning alerts with pagination."""
    pass

def categorize_by_cwe(alerts: List[Dict]) -> Dict[str, List[Dict]]:
    """Group alerts by CWE identifier."""
    pass

def generate_fix_pr(alerts: List[Dict], fixes: List[Dict]) -> str:
    """Create PR with automated fixes."""
    pass

def close_alert(alert_number: int, reason: str, comment: str) -> bool:
    """Close alert via GitHub API."""
    pass

def validate_fix(file_path: str, alert_id: str) -> bool:
    """Run security checks on fixed file."""
    pass
```

---

## 📈 Success Metrics

### Quantitative Metrics
- **Alert Resolution Rate:** 95% within 10 phases
- **Mean Time to Remediation (MTTR):**
  - P0: < 24 hours
  - P1: < 3 iterations
  - P2: < 1 phase
  - P3: < 2 phases
- **False Positive Rate:** < 10%
- **Regression Rate:** < 2%
- **Test Coverage:** 100% for security fixes

### Qualitative Metrics
- Clear documentation for all alerts
- Stakeholder confidence in security posture
- Developer understanding of secure coding
- Sustainable security practices established

---

## 🔄 Continuous Improvement

### Post-Resolution Activities

#### 1. Retrospective Analysis
- What types of vulnerabilities were most common?
- Which automated fixes were most effective?
- Where did manual intervention add most value?
- What patterns emerged from false positives?

#### 2. Process Optimization
- Refine automated fix patterns
- Update security agent training data
- Improve alert categorization rules
- Streamline manual review workflow

#### 3. Knowledge Sharing
- Document lessons learned
- Share case studies with team
- Update security training materials
- Contribute to open-source security tools

---

## 📚 References

### GitHub API Documentation
- [Code Scanning Alerts API](https://docs.github.com/en/rest/code-scanning)
- [SARIF Format Specification](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html)

### Security Standards
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Database](https://cwe.mitre.org/)
- [SANS Top 25](https://www.sans.org/top25-software-errors/)

### CodeQL Resources
- [CodeQL Documentation](https://codeql.github.com/docs/)
- [Python Query Library](https://codeql.github.com/codeql-standard-libraries/python/)
- [Security Queries](https://github.com/github/codeql/tree/main/python/ql/src/Security)

### Internal Resources
- `.codex/SECURITY_FALSE_POSITIVE_STANDARD.md`
- `.github/copilot-security/security_agent.py`
- `scripts/security/` directory
- `.codeql/codeql-config.yml`

---

## ✅ Completion Checklist

### Phase 1: Discovery
- [ ] Alert fetcher script created
- [ ] All 59 pages processed
- [ ] Alert inventory generated
- [ ] Categorization complete

### Phase 2: Prioritization
- [ ] Priority matrix applied
- [ ] Resolution roadmap created
- [ ] Alerts routed to workflows

### Phase 3: Automation
- [ ] Security agent configured
- [ ] Codemods tested
- [ ] Automated PRs generated

### Phase 4: Manual Review
- [ ] Complex vulnerabilities addressed
- [ ] False positives documented
- [ ] Custom fixes implemented

### Phase 5: Verification
- [ ] All fixes validated
- [ ] CodeQL re-scan clean
- [ ] Alerts closed with comments

### Phase 6: Prevention
- [ ] Documentation updated
- [ ] Pre-commit hooks enabled
- [ ] Recurring scans configured
- [ ] Team training completed

---

## 🎉 Success Criteria

**This planset is considered complete when:**
1. ✅ All code scanning alerts are triaged (resolved, documented as FP, or scheduled)
2. ✅ 95%+ of actionable alerts are resolved with validated fixes
3. ✅ All resolved alerts are closed via API with proper documentation
4. ✅ Preventive measures are in place to minimize future alerts
5. ✅ Team is trained on secure coding practices
6. ✅ Security monitoring is ongoing and sustainable

---

**Version:** 1.0.0  
**Last Updated:** 2026-01-26  
**Next Review:** After Week 5 (mid-implementation checkpoint)  
**Owner:** @mbaetiong  
**Stakeholders:** Security Team, Engineering Team, Platform Team
