# Phase 5 Quality Metrics Alert Policy

**Document Version**: 1.0.0  
**Created**: 2026-07-18  
**Phase**: 5 Lane 3  
**Status**: Active  
**Enforcement Mode**: Advisory (Phase 5) → Blocking (Phase 6)  

---

## 📋 Executive Summary

This document defines alert thresholds, severity levels, escalation procedures, and notification routing for quality metric violations in the Codex repository. The policy ensures that quality regressions are detected, surfaced, and remediated quickly.

**Key Principles**:
1. **Early Detection**: Alert immediately on threshold miss
2. **Clear Escalation**: Graduated response based on severity
3. **Actionable Alerts**: Every alert includes investigation path
4. **Team Coordination**: Notifications reach right people at right time
5. **Trend Awareness**: Track patterns, not just individual violations

---

## 🔴 Severity Levels & Definitions

### Critical (🔴) - Immediate Action Required
- **Enforcement**: Blocks PR merge or stops deployment
- **Response Time**: 0-4 hours
- **Escalation**: @mbaetiong, @codex-team/security (if security-related)
- **Examples**:
  - Security vulnerability (CVSS 7.0+)
  - Critical module coverage drops >10%
  - Build failure on main branch
  - Any test failure blocking merge

### High (🟠) - Urgent Attention Needed
- **Enforcement**: PR comment, team notification (advisory Phase 5, blocking Phase 6)
- **Response Time**: 4-24 hours
- **Escalation**: @codex-team/quality, pull request comment
- **Examples**:
  - Module coverage drops 5-10%
  - Test flakiness increases >5%
  - Mutation kill rate drops 5-10%
  - Build time increases >20%

### Medium (🟡) - Should Address Soon
- **Enforcement**: PR comment for awareness
- **Response Time**: 24-72 hours
- **Escalation**: PR comment with details
- **Examples**:
  - Coverage drops 1-5%
  - Documentation coverage drops 2-5%
  - Complexity increases 10-20%
  - Build time increases 10-20%

### Low (🔵) - Informational
- **Enforcement**: Logged only, no PR action
- **Response Time**: Best effort
- **Escalation**: None (logged for trend analysis)
- **Examples**:
  - Metrics index updated
  - Coverage holding steady
  - Minor documentation changes
  - Performance improvements

---

## 📊 Alert Thresholds by Metric

### Coverage Metrics

#### Overall Coverage
| Threshold | Severity | Action | Response Time |
|-----------|----------|--------|----------------|
| Drops >5% in PR | 🔴 Critical | Block merge | 0-4h |
| Drops 2-5% in PR | 🟠 High | PR comment | 4-24h |
| Drops 1-2% in PR | 🟡 Medium | PR comment | 24-72h |
| Drops >1% in 24h | 🟡 Medium | Notify team | 24-72h |
| Increases <1% | 🔵 Low | Log only | N/A |

**Collection**: Per PR and per merge to main  
**Source**: `pytest --cov=src --cov-report=json`  
**Storage**: `.reports/metrics/coverage_latest.json`  

#### Per-Module Coverage (SLO Miss)
| Module Category | Threshold | Severity | Action |
|-----------------|-----------|----------|--------|
| Critical (80% target) | Drops below 75% | 🔴 Critical | Block merge |
| Critical (80% target) | Drops 75-80% | 🟠 High | PR comment + escalate |
| Core (70% target) | Drops below 65% | 🟠 High | PR comment |
| Core (70% target) | Drops 65-70% | 🟡 Medium | PR comment |
| Utility (50% target) | Drops below 45% | 🟡 Medium | Notify team |
| Utility (50% target) | Drops 45-50% | 🔵 Low | Log only |

**Escalation Path for Critical Modules**:
1. Module drops below SLO → Automatic PR comment (severity high)
2. If not addressed in 24h → Escalate to module owner
3. If not addressed in 72h → Escalate to @mbaetiong

#### Coverage Trend
| Trend Pattern | Duration | Severity | Action |
|---------------|----------|----------|--------|
| Consistent decline | 7+ days | 🟠 High | Team meeting required |
| Decline with recovery | 3-7 days | 🟡 Medium | Monitor closely |
| Plateau | Any | 🔵 Low | Informational |
| Improvement | Any | 🔵 Low | Celebrate! |

**Trend Alert**: If 7-day rolling average drops >1% below previous week's average, alert team.

---

### Test Health Metrics

#### Test Flakiness Rate
| Threshold | Severity | Action | Response Time |
|-----------|----------|--------|----------------|
| Exceeds 5% | 🟠 High | PR comment with flaky list | 4-24h |
| Exceeds 3% | 🟡 Medium | PR comment | 24-72h |
| Exceeds 10% | 🔴 Critical | Block merge | 0-4h |
| <2% | ✅ Healthy | No action | N/A |

**Calculation**: `(tests_with_retries / total_tests) × 100` in last 50 runs  
**Investigation Path**:
1. Identify flaky test from PR comment
2. Run locally with `pytest --lf --verbose`
3. Add retry logic only if environmental (not code)
4. Fix root cause (timing, mocks, async patterns)

#### Test Execution Latency
| Percentile | Target | Alert (>10% miss) | Severity |
|-----------|--------|-------------------|----------|
| p50 | <2s | >2.2s | 🟡 Medium |
| p95 | <10s | >11s | 🟠 High |
| p99 | <30s | >33s | 🟠 High |

**Alert Action**: Comment on PR with slowest 5 tests, suggest optimization  
**Root Cause**: Often database setup, network calls, or test data generation  

#### Test Count & Distribution
| Change | Severity | Action |
|--------|----------|--------|
| Decreases >10% | 🔴 Critical | Block merge, require justification |
| Decreases 5-10% | 🟠 High | PR comment requesting explanation |
| Decreases <5% | 🟡 Medium | Log for trend analysis |
| Increases | 🔵 Low | Celebrate growth |

**Justification Reason**: May be valid (e.g., consolidating test cases), but requires explanation.

---

### Build & Pipeline Metrics

#### Build Time
| Change | Severity | Action | Response Time |
|--------|----------|--------|----------------|
| Increases >20% | 🟠 High | Notify team, investigate | 4-24h |
| Increases 10-20% | 🟡 Medium | Log trend | 24-72h |
| Increases <10% | 🔵 Low | Monitor | N/A |

**Investigation**: Check for new test additions, dependency updates, or system slowness  
**Optimization**: Parallel jobs, test selection, caching improvements  

#### CI Pass Rate
| Pass Rate | Severity | Action |
|-----------|----------|--------|
| <90% | 🔴 Critical | Investigate failure pattern |
| 90-95% | 🟠 High | Team review of failure causes |
| >95% | ✅ Healthy | No action |

**Calculation**: Last 100 workflow runs  
**Failure Pattern Analysis**: Group by error type (timeout, flaky, logic)  

---

### Code Quality Metrics

#### Mutation Kill Rate
| Kill Rate | Severity | Action | Response Time |
|-----------|----------|--------|----------------|
| Drops >5% | 🟠 High | Comment with low-coverage areas | 4-24h |
| Drops 2-5% | 🟡 Medium | Log for team review | 24-72h |
| <70% | 🔴 Critical | Escalate to team lead | 0-4h |
| >85% | ✅ Healthy | No action | N/A |

**Investigation**: Run `mutmut run --coverage` to identify uncaught mutations  
**Action**: Add assertions for untested code paths  

#### Code Complexity
| Metric | Threshold | Severity | Action |
|--------|-----------|----------|--------|
| Avg cyclomatic | >15 | 🟡 Medium | Comment with high-complexity functions |
| Avg cognitive | >20 | 🟡 Medium | Comment with refactor suggestions |
| Function cyclomatic | >20 | 🟠 High | Comment on PR, suggest refactoring |
| Function cognitive | >25 | 🟠 High | Comment on PR, suggest breaking up |

**Alert Action**: Provide specific line numbers and refactoring hints  

---

### Security & Dependency Metrics

#### Security Vulnerabilities
| Severity | Known CVE | Action | Response Time |
|----------|-----------|--------|----------------|
| Critical | Any | 🔴 Block merge immediately | 0-2h |
| High | Any | 🔴 Block merge | 0-4h |
| Medium | >5 accumulated | 🟠 High priority fix | 24-48h |
| Low | Any | 🟡 Plan in roadmap | Best effort |

**Escalation**: Auto-escalate critical to @codex-team/security  
**Remediation**: Update dependency or apply patch immediately  

#### Dependency Health Score
| Score | Severity | Action |
|-------|----------|--------|
| <70 | 🔴 Critical | Remediate dependency issues |
| 70-80 | 🟠 High | Plan dependency updates |
| 80-90 | 🟡 Medium | Monitor for new issues |
| 90+ | ✅ Healthy | Maintain current status |

**Score Calculation**:
```
score = 100 - (
  (outdated_pkg_count × 0.3) +
  (critical_cve_count × 5.0) +
  (high_cve_count × 3.0) +
  (license_violation_count × 2.0)
)
```

---

### Documentation Metrics

#### Docstring Coverage
| Threshold | Severity | Action |
|-----------|----------|--------|
| Drops >5% | 🟡 Medium | PR comment with undocumented items |
| Drops 2-5% | 🟡 Medium | Log for review |
| Drops <2% | 🔵 Low | Maintain awareness |

**Alert Action**: Provide list of undocumented functions for current PR  

#### Documentation Freshness
| File | Threshold (Days) | Severity | Action |
|------|------------------|----------|--------|
| README.md | 60+ days | 🟡 Medium | Notify docs team |
| Module README | 90+ days | 🔵 Low | Log for review |
| CHANGELOG | 30+ days (no entry) | 🟡 Medium | Prompt for updates |

---

## 🚨 Escalation Procedures

### Level 1: Detection (Immediate)
**Trigger**: Alert threshold crossed  
**Automatic Action**: 
- Metrics collected and analyzed
- Alert generated and classified by severity
- Data stored in `.reports/metrics/`

**Output**: 
- PR comment (if PR-based alert)
- GitHub issue (if trend alert)
- Slack notification (if configured)

### Level 2: Notification (0-4 hours for Critical)
**Critical (🔴)**: 
- Automatic PR comment with blocking indicator
- Slack notification to #ci-alerts
- Email to @mbaetiong, @codex-team/quality

**High (🟠)**: 
- PR comment with escalation info
- Slack notification to #ci-notifications
- Email to @codex-team/quality

**Medium (🟡)**: 
- PR comment only
- Logged for trend analysis

**Low (🔵)**: 
- Logged only

### Level 3: Investigation (4-24 hours for High)
**Responsible Party**: Issue author or module owner  
**Required Actions**:
1. Acknowledge receipt (👍 reaction on PR comment)
2. Investigate root cause
3. Comment with finding or fix plan
4. Schedule follow-up if needed

**Escalation**: If no response in 4 hours, escalate to module owner

### Level 4: Remediation (24-72 hours)
**Responsible Party**: Module owner or team lead  
**Actions**:
1. Implement fix or mitigation
2. Add tests to prevent recurrence
3. Document lessons learned
4. Close issue or mark as resolved

**Escalation**: If unresolved after 72 hours, escalate to @mbaetiong

### Level 5: Review & Prevention (Weekly)
**Weekly Review**: Every Monday  
**Attendees**: @mbaetiong, quality team  
**Agenda**:
- Review high/critical alerts from previous week
- Identify systemic issues
- Plan preventive improvements
- Update alert thresholds if needed

---

## 📱 Notification Routing

### Automatic Channels
| Severity | Channel | Recipient | Delay |
|----------|---------|-----------|-------|
| 🔴 Critical | PR Comment + Slack + Email | @mbaetiong, quality team | Immediate |
| 🟠 High | PR Comment + Slack | @codex-team/quality | Immediate |
| 🟡 Medium | PR Comment | Committer | Immediate |
| 🔵 Low | Dashboard + Logs | Dashboard users | Batch (hourly) |

### Configuration Files
```yaml
# File: .github/QUALITY_ALERTS_CONFIG.yml

critical:
  slack_channel: "#ci-alerts"
  email_recipients:
    - "mbaetiong@github.com"
    - "quality-team@codex.dev"
  block_merge: true
  
high:
  slack_channel: "#ci-notifications"
  email_recipients:
    - "quality-team@codex.dev"
  block_merge: false
  
medium:
  slack_channel: null  # PR comment only
  email_recipients: []
  block_merge: false
```

### Slack Notifications Format
```
🟠 [HIGH] Coverage Miss in auth module
PR: #1234 | Author: @john.doe
Current: 72% → Previous: 78% (↓ 6%)
Target: 80% | Category: Critical

Action: Add tests for uncovered paths
URL: https://github.com/...
```

---

## 🔍 Investigation & Remediation

### Root Cause Analysis Template
```markdown
## Alert: [Metric Name]
**Severity**: [Level]
**Threshold**: [X% miss]
**Detection Time**: [Timestamp]

### Root Cause
- [ ] Code change (specific PR)
- [ ] Test removal
- [ ] Environment issue
- [ ] Flaky test detection
- [ ] Tool issue
- [ ] Unknown

### Investigation Steps
1. Identify affected module/metric
2. Review recent changes in area
3. Check test execution logs
4. Run locally to verify
5. Document findings

### Remediation
- [ ] Code fix
- [ ] Test addition
- [ ] Configuration change
- [ ] Tool update
- [ ] Documentation

### Verification
- [ ] Alert clears on next run
- [ ] Trend improves
- [ ] No new related alerts
```

---

## 📈 Trend Analysis & Continuous Improvement

### Weekly Review Metrics
1. **Alert Volume**: Total alerts by severity (trend direction)
2. **Alert Resolution**: Avg time to resolve by severity
3. **False Positive Rate**: Alerts that don't require action
4. **Threshold Calibration**: Are thresholds too strict/loose?

### Monthly Review (1st of month)
1. **Alert Pattern Analysis**: Recurring issues?
2. **Team Capacity**: Can we handle alert volume?
3. **Process Improvement**: What's working/not working?
4. **Threshold Adjustment**: Any alerts need recalibration?

### Quarterly Review (Start of quarter)
1. **SLO Attainment**: Are modules meeting targets?
2. **Process Effectiveness**: Is alert system helping?
3. **Tooling**: Any new tools or integrations needed?
4. **Policy Update**: Any changes to enforcement levels?

---

## 🔧 Alert Configuration

### Environment Variables
```bash
# Enable/disable alerts
QUALITY_ALERTS_ENABLED=true
ALERT_SLACK_ENABLED=true
ALERT_EMAIL_ENABLED=true

# Thresholds
COVERAGE_CRITICAL_THRESHOLD=5   # % drop
COVERAGE_HIGH_THRESHOLD=2
FLAKINESS_THRESHOLD=5           # % flaky
BUILD_TIME_THRESHOLD=20         # % increase

# Escalation
ESCALATION_HOURS_CRITICAL=4
ESCALATION_HOURS_HIGH=24
ESCALATION_HOURS_MEDIUM=72
```

### Phase-Specific Overrides
```yaml
# Phase 5: Advisory mode
phase_5:
  enforcement: advisory
  block_merge: false
  pr_comment: true
  
# Phase 6: Blocking mode  
phase_6:
  enforcement: blocking
  block_merge: true
  pr_comment: true
  escalate_to_lead: true
```

---

## 📊 Alert Metrics & KPIs

### Success Metrics
| KPI | Target | Measurement |
|-----|--------|-------------|
| Alert Accuracy | >90% | % non-false-positive alerts |
| Resolution Time (Critical) | <4h | Avg time to fix |
| Resolution Time (High) | <24h | Avg time to fix |
| Alert Noise | <10% | % alerts that don't require action |
| Team Satisfaction | >4/5 | Survey score on alert system |

### Reporting
- **Daily**: Alert summary dashboard
- **Weekly**: Alert trend report (Mondays)
- **Monthly**: Alert metrics analysis
- **Quarterly**: Alert system effectiveness review

---

## 🎓 Policy Exceptions & Overrides

### Justified Exceptions
Exceptions may be granted for:
1. **Environmental Issues**: Known CI infrastructure issue (documented)
2. **Intended Changes**: Intentional test removal (with approval)
3. **Temporary Build Issues**: Dependency problems (with time limit)

**Approval Process**:
1. Comment on PR with `@quality-policy-exception`
2. Provide justification in comment
3. Requires approval from @mbaetiong
4. Auto-remove exception after time limit

### Disabling Alerts
Temporary alert disables:
```yaml
# In PR comment:
@quality-alerts disable coverage_critical until 2026-07-25
reason: "Known test flakiness, fixing in parallel PR"
```

Requires:
- Clear justification
- Time-limited (max 7 days)
- Follow-up issue created
- @mbaetiong approval

---

## 📋 Checklist for Alert System Health

- [ ] All thresholds reviewed and calibrated (monthly)
- [ ] Escalation procedures tested (quarterly)
- [ ] Notification routing verified (weekly)
- [ ] False positives investigated (weekly)
- [ ] Team trained on alert procedures (annual)
- [ ] Documentation kept up-to-date (per update)
- [ ] Process improvements documented (quarterly)

---

## 🔗 Related Documents

- `.codex/PHASE_5_QUALITY_METRICS_DEFINITION.md` - Metric definitions
- `.codex/PHASE_5_COVERAGE_SLOS.yaml` - SLO targets
- `docs/quality_dashboard/DASHBOARD_README.md` - Dashboard guide
- `.github/workflows/quality-metrics-collection.yml` - Metrics workflow

---

## 📞 Support

- **Alert Questions**: Open issue with `quality-alerts` label
- **Threshold Discussion**: Raise in #quality-metrics Slack
- **Exception Request**: Comment on PR with `@quality-policy-exception`
- **Process Issues**: Escalate to @mbaetiong

---

**Document Status**: Active  
**Last Updated**: 2026-07-18T22:51:00Z  
**Next Review**: 2026-07-25T00:00:00Z  
**Maintained By**: @mbaetiong (Phase 5 Lane 3 Lead)
