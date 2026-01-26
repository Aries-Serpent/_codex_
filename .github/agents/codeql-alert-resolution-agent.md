# CodeQL Alert Resolution Agent

**Agent Type:** Security & Vulnerability Management  
**Version:** 1.0.0  
**Created:** 2026-01-26  
**Status:** ✅ Production Ready

---

## 🎯 Purpose

Autonomous agent for systematic resolution of CodeQL code scanning alerts. Fetches, triages, remediates, and closes security vulnerabilities across the entire codebase with zero-human-intervention capability.

## 📋 Capabilities

### Core Functions
1. **Alert Discovery** - Fetch all CodeQL alerts from GitHub Security tab (handles pagination)
2. **Categorization** - Classify alerts by severity, CWE, pattern, and remediability
3. **Priority Triage** - Apply risk-based prioritization matrix
4. **Automated Remediation** - Apply security codemods for common vulnerability patterns
5. **Manual Coordination** - Route complex issues to human security team
6. **Validation** - Run security regression tests after fixes
7. **Closure Tracking** - Close alerts via API with detailed comments
8. **Reporting** - Generate dashboards and metrics

### Security Patterns Handled
- **Injection**: SQL injection, command injection, XSS
- **Path Traversal**: Unsafe file operations
- **Cryptography**: Weak algorithms, hardcoded secrets
- **Authentication**: Broken auth, privilege escalation
- **Information Disclosure**: Sensitive data exposure
- **Resource Management**: DoS vulnerabilities
- **Error Handling**: Unsafe exception handling

## 🚀 Activation

### Copilot Command
```
@workspace Use the CodeQL Alert Resolution Agent to resolve all open security alerts
```

### Alternative Phrases
- "Scan and fix all CodeQL alerts"
- "Resolve code scanning notifications"
- "Triage security vulnerabilities"
- "Close open security alerts"

## 📊 Workflow

```mermaid
graph TD
    A[Start: Agent Activation] --> B[Fetch All Alerts via API]
    B --> C[Categorize by Severity/Pattern]
    C --> D{Is Automated Fix Available?}
    D -->|Yes| E[Apply Security Codemod]
    D -->|No| F[Route to Human Review]
    E --> G[Run Regression Tests]
    G --> H{Tests Pass?}
    H -->|Yes| I[Close Alert via API]
    H -->|No| J[Revert & Flag for Manual]
    I --> K[Update Dashboard]
    F --> K
    J --> K
    K --> L{More Alerts?}
    L -->|Yes| D
    L -->|No| M[Generate Final Report]
    M --> N[End]
```

## 🛠️ Tools & Scripts

### Primary Scripts
1. **`scripts/security/fetch_codeql_alerts.py`**
   - Fetch all alerts with pagination (59+ pages)
   - Export to JSON, CSV, Markdown
   - Handle rate limits
   
2. **`scripts/security/close_codeql_alert.py`**
   - Close alerts via GitHub API
   - Batch operations support
   - Detailed closure comments
   
3. **`scripts/security/codemods/*.py`**
   - `fix_sql_injection.py` - Parameterized queries
   - `fix_subprocess.py` - Safe command execution
   - `fix_hardcoded_secrets.py` - Environment variables
   - `fix_path_traversal.py` - Path sanitization

### Supporting Tools
- **Security Agent**: `.github/copilot-security/security_agent.py`
- **SARIF Merger**: `scripts/merge_sarif.py`
- **Validation**: `scripts/security/validate_security.py`

## 📁 Data Locations

### Input
- GitHub Code Scanning API: `GET /repos/{owner}/{repo}/code-scanning/alerts`
- CodeQL Config: `.codeql/codeql-config.yml`
- Security Patterns: `.github/copilot-security/fix_patterns.yaml`

### Output
- Alert Inventory: `.codex/security/alert_inventory.json`
- Alert Summary: `.codex/security/alert_summary.md`
- Closure Log: `.codex/security/alert_closures.jsonl`
- Dashboard: `.codex/security/resolution_dashboard.md`

## 🎯 Priority Matrix

| Severity | Exploitability | Priority | SLA |
|----------|---------------|----------|-----|
| Critical | High | P0 | 24h |
| Critical | Medium | P1 | 3d |
| High | High | P1 | 3d |
| High | Medium | P2 | 1w |
| Medium | High | P2 | 1w |
| Medium | Medium | P3 | 2w |
| Low | Any | P4 | 1m |

## 🔧 Configuration

### Environment Variables
```bash
export GITHUB_TOKEN="ghp_..."  # Required: security_events read/write
export CODEX_SECURITY_MODE="autonomous"  # Options: autonomous, supervised
export CODEX_AUTO_CLOSE_ALERTS="true"  # Auto-close fixed alerts
export CODEX_MAX_ALERTS_PER_BATCH="50"  # Batch processing limit
```

### Agent Settings
```yaml
# .codex/agents/codeql-resolver.yml
agent:
  name: codeql-alert-resolution-agent
  version: 1.0.0
  
  capabilities:
    - alert_fetching
    - automated_remediation
    - validation
    - closure_tracking
  
  thresholds:
    auto_fix_confidence: 0.8  # Apply fixes with 80%+ confidence
    max_alerts_per_run: 100
    rate_limit_buffer: 10  # API calls to keep in reserve
  
  routing:
    automated: ["sql-injection", "xss", "path-traversal"]
    manual_review: ["auth-bypass", "business-logic"]
    false_positive_patterns: ["test/**", "examples/**"]
```

## 📖 Usage Examples

### Example 1: Full Scan and Remediation
```markdown
@workspace Use the CodeQL Alert Resolution Agent to:
1. Fetch all open code scanning alerts
2. Prioritize by severity (critical/high first)
3. Apply automated fixes where possible
4. Generate remediation report
5. Close all resolved alerts
```

### Example 2: Specific Severity
```markdown
@workspace CodeQL Agent: resolve all critical and high severity alerts only
```

### Example 3: Pattern-Based
```markdown
@workspace CodeQL Agent: fix all SQL injection vulnerabilities
```

### Example 4: Dry Run
```markdown
@workspace CodeQL Agent: analyze alerts and generate action plan (no changes)
```

## 🔍 Validation Protocol

### Pre-Fix Validation
1. ✅ Alert is not a false positive
2. ✅ Fix pattern is known and tested
3. ✅ Confidence score meets threshold (≥0.8)
4. ✅ No existing PR addresses this alert

### Post-Fix Validation
1. ✅ All existing tests pass
2. ✅ Security regression tests added
3. ✅ CodeQL re-scan shows alert resolved
4. ✅ No new vulnerabilities introduced
5. ✅ Code review approved (for P0/P1)

### Validation Commands
```bash
# Run security validation
python scripts/security/validate_security.py

# Run CodeQL locally
codeql database create --language=python codeql-db
codeql database analyze codeql-db --format=sarif-latest

# Run all tests
pytest tests/ -v --tb=short

# Check for regressions
bandit -r src/ -f json -o security-report.json
```

## 📊 Reporting & Metrics

### Real-Time Dashboard
**Location:** `.codex/security/resolution_dashboard.md`

**Metrics:**
- Total alerts: 1,500
- Resolved: 450 (30%)
- In progress: 300 (20%)
- False positives: 100 (7%)
- Remaining: 650 (43%)

### Weekly Report
**Auto-generated:** Every Monday 9 AM UTC

**Includes:**
- Resolution velocity (alerts/week)
- Pattern distribution
- Mean time to remediation (MTTR)
- Top 10 vulnerable files
- Compliance status

### Closure Log
**Location:** `.codex/security/alert_closures.jsonl`

**Format:**
```json
{
  "alert_number": 123,
  "closed_at": "2026-01-26T12:00:00Z",
  "reason": "fixed",
  "comment": "Applied parameterized queries",
  "pr_number": 456,
  "commit_sha": "abc123",
  "confidence": 0.95
}
```

## 🚨 Escalation Rules

### Auto-Escalate to Human When:
1. ❌ Confidence score < 0.8
2. ❌ Complex authentication logic
3. ❌ Business logic vulnerabilities
4. ❌ Multi-file architectural changes
5. ❌ Post-fix tests fail
6. ❌ Potential false positive (test code)

### Escalation Procedure
1. Create GitHub issue with `[SECURITY-REVIEW]` label
2. Assign to @security-team
3. Include:
   - Alert details
   - Attempted fix (if any)
   - Reason for escalation
   - Recommended action
4. Update alert state to "under review"
5. Set SLA reminder based on priority

## 🔄 Continuous Improvement

### Learning Loop
1. **Track Fix Effectiveness**
   - Monitor alert re-occurrence
   - Measure false positive rate
   - Track manual intervention needs

2. **Update Fix Patterns**
   - Add new codemod scripts
   - Refine confidence thresholds
   - Update pattern matching rules

3. **Optimize Workflow**
   - Reduce MTTR
   - Increase automation coverage
   - Improve validation accuracy

### Feedback Collection
```yaml
# .codex/security/agent_feedback.yml
fix_effectiveness:
  alert_123:
    fix_applied: "parameterized_query"
    reoccurred: false
    manual_tweaks_needed: false
    rating: 5/5
  
  alert_456:
    fix_applied: "path_sanitization"
    reoccurred: false
    manual_tweaks_needed: true
    improvement: "Add more edge cases"
    rating: 4/5
```

## 🛡️ Security Considerations

### Agent Permissions
- ✅ Read: code scanning alerts
- ✅ Write: dismiss/close alerts
- ✅ Read/Write: repository code (for fixes)
- ❌ **No** direct access to secrets
- ❌ **No** workflow execution rights (until Genesis Phase 2)

### Safety Guards
1. **Dry Run Mode**: Test all operations without committing
2. **Confidence Threshold**: Only apply high-confidence fixes
3. **Regression Prevention**: Comprehensive test suite
4. **Rollback Capability**: All fixes in separate commits
5. **Human Oversight**: P0/P1 alerts require review

### Audit Trail
- All operations logged to `.codex/security/agent_actions.log`
- Git commits include agent signature
- PR descriptions include full context
- Closure comments link to fixes

## 📚 Documentation

### Related Docs
- **Master Planset**: `.codex/plans/CODEQL_ALERT_RESOLUTION_PLANSET.md`
- **Security Utils**: `scripts/security/README.md`
- **AI Agency Policy**: `.codex/CODEBASE_AGENCY_POLICY.md`
- **GitHub API**: [Code Scanning Alerts API](https://docs.github.com/en/rest/code-scanning)

### Training Materials
- **OWASP Top 10**: Internal training deck
- **CWE Database**: Reference guide
- **Secure Coding**: Best practices document
- **CodeQL Queries**: Custom query library

## 🎓 Prerequisites

### Required Knowledge
- Python security best practices
- OWASP vulnerability categories
- CodeQL query language basics
- GitHub API authentication

### Required Tools
- Python 3.12+
- `requests` library
- Git command line
- GitHub CLI (optional)

### Required Access
- GitHub token with `security_events` scope
- Repository write access
- Security team contact info

## 🐛 Troubleshooting

### Common Issues

#### "403 Insufficient permissions"
**Solution:** Verify GitHub token has `security_events:read` and `security_events:write` permissions

#### "No alerts found"
**Solution:** Check code scanning is enabled in repository settings

#### "Rate limit exceeded"
**Solution:** Script includes automatic rate limit handling. For large repos, use `--max-pages` option

#### "Fix applied but alert still open"
**Solution:** GitHub may take 24-48 hours to re-scan. Manually trigger CodeQL workflow or wait for scheduled run

### Debug Mode
```bash
# Enable verbose logging
export CODEX_DEBUG=true
export CODEX_LOG_LEVEL=DEBUG

# Run with debug output
python scripts/security/fetch_codeql_alerts.py --verbose

# Check logs
tail -f .codex/security/agent_actions.log
```

## 🎉 Success Criteria

### Agent Performance Targets
- ✅ 95% of alerts triaged within 48 hours
- ✅ 60% automated fix success rate
- ✅ <2% false positive rate
- ✅ <5% regression rate
- ✅ 100% audit trail compliance

### Repository Security Targets
- ✅ Zero P0/P1 alerts older than 7 days
- ✅ <10 P2 alerts in backlog
- ✅ Weekly security scan passing
- ✅ All developers security-trained

## 📞 Support & Escalation

### Agent Support
- **Owner:** @mbaetiong
- **Security Team:** @security-team
- **Escalation Path:** Issue → Security Team → CISO

### Office Hours
- **Weekly Agent Review:** Wednesdays 2 PM UTC
- **Security Stand-up:** Daily 9 AM UTC
- **On-call:** 24/7 for P0 alerts

---

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-26 | Initial release - Full autonomous capabilities |
| 0.9.0 | 2026-01-26 | Beta - Testing with production data |
| 0.1.0 | 2026-01-26 | Alpha - Script development |

---

**Status:** ✅ Production Ready  
**Last Updated:** 2026-01-26T17:40:00Z  
**Next Review:** Weekly (Wednesdays 2 PM UTC)

**Questions?** File an issue with label `agent:codeql-resolver` or contact @mbaetiong
