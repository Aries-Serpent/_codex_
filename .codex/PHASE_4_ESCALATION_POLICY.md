# Phase 4 Lane 2: Severity Classification & Escalation Policy

**Version**: 1.0.0  
**Effective Date**: 2026-07-18T22:29Z  
**Authority**: @mbaetiong D-tier approved (2026-07-13T18:20Z)  
**Status**: ✅ ACTIVE

---

## Executive Summary

Phase 4 Lane 2 implements a **3-tier escalation model** for Sev-1 critical CI failures with a hard SLA of **<2 minutes** from alert to maintainer escalation. This policy ensures rapid incident response through automated self-healing (Tier 1), specialist rerouting (Tier 2), and human escalation (Tier 3).

| Tier | Agent | SLA | Purpose | Success Rate Target |
|------|-------|-----|---------|---------------------|
| **Tier 1** | ci-failure-resolution-agent | <60s | Auto-remediation using self-healing patterns | 70% |
| **Tier 2** | Specialist Agent Pool | <90s | Domain-specific remediation (Docker, timeout, import, etc.) | 20% (of failures) |
| **Tier 3** | @mbaetiong (Maintainer) | <120s | Manual intervention & escalation | 10% (critical) |

---

## 1. Severity Classification Framework

### 1.1 Sev-1: CRITICAL (Blocks Main Branch)

**Characteristics**:
- Affects `main` branch OR default PR merge target
- 100% failure rate across all CI jobs
- Blocks ALL PR merges
- Service-wide impact
- Immediate user/developer impact

**Examples**:
- Docker image build fails for all jobs
- Python environment cannot initialize (ImportError on main module)
- Linting blockers preventing commit validation
- Database migration failure on startup
- Master workflow syntax errors preventing execution

**Response SLA**: <2 minutes (alert to maintainer)  
**Escalation Path**: T1 (60s) → T2 (90s) → T3 (120s)  
**On-Call Pager**: ✅ ALWAYS  
**War Room**: ✅ REQUIRED  

**Detection**:
```bash
# CI job status check
- If ALL jobs in a workflow fail: Sev-1
- If main branch blocked: Sev-1
- If master workflow has YAML error: Sev-1
```

### 1.2 Sev-2: HIGH (Blocks PR Merge)

**Characteristics**:
- Affects PR branch CI jobs
- >70% failure rate (70-99%)
- Prevents PR merge
- Subset of jobs affected
- Developers blocked but main not impacted

**Examples**:
- Specific test suite fails (e.g., ML tests, Rust tests)
- Linting fails on specific file types
- Timeout on one job type (e.g., coverage suite)
- Import error in non-core module
- Intermittent auth test failures

**Response SLA**: <10 minutes  
**Escalation Path**: T1 (90s) → T2 (300s) → escalate if unresolved  
**On-Call Pager**: 🔔 CONDITIONAL (if CI health <80%)  
**War Room**: ❌ NOT REQUIRED (debug async)  

**Detection**:
```bash
# CI job status check
- If jobs_failed / jobs_total >= 0.70: Sev-2
- If main branch not affected: Sev-2
```

### 1.3 Sev-3: MEDIUM (Intermittent)

**Characteristics**:
- Intermittent failures (30-70% rate)
- Does NOT block main or PR consistently
- Flaky tests or transient errors
- Reproducibility low

**Examples**:
- Flaky test that passes on retry
- Timeout on slow CI runner
- Transient network errors in integration tests
- Intermittent module import issues
- Race condition in async code

**Response SLA**: <2 hours (working hours)  
**Escalation Path**: T1 (auto-retry) → document pattern for T2 analysis  
**On-Call Pager**: ❌ NO (log and monitor)  
**War Room**: ❌ NO  

**Detection**:
```bash
# Flakiness detection
- If (jobs_failed / jobs_total) between 0.30 and 0.70: Sev-3
- If same failure passes on retry: Sev-3
```

### 1.4 Sev-4: LOW (Noise)

**Characteristics**:
- <30% failure rate
- Documentation issues
- Minor style violations
- No functional impact
- Does not block workflow

**Examples**:
- Broken documentation links
- Style violations in comments
- Deprecated warning messages
- Minor code quality issues
- Type annotation hints

**Response SLA**: <24 hours (or next sprint)  
**Escalation Path**: Log for pattern analysis  
**On-Call Pager**: ❌ NO  
**War Room**: ❌ NO  

**Detection**:
```bash
# Noise detection
- If (jobs_failed / jobs_total) < 0.30: Sev-4
- If warning-only (no failures): Sev-4
```

---

## 2. Three-Tier Escalation Routing Model

### 2.1 Tier 1: Automated Self-Healing (ci-failure-resolution-agent)

**Activation**: Immediate upon Sev-1 alert  
**SLA**: <60 seconds  
**Success Target**: 70% of Sev-1 incidents  
**Agent**: `ci-failure-resolution-agent`

**Capabilities**:

| Pattern | Auto-Fix? | Example Issues |
|---------|-----------|-----------------|
| **Linting Errors (W293, E402)** | ✅ YES | Whitespace, import ordering |
| **Import Path Errors** | ✅ YES | Missing __init__.py, bad imports |
| **YAML Syntax (Standard)** | ✅ YES | Indentation, mapping errors |
| **Test Auto-Retry** | ✅ YES | Flaky test, transient failure |
| **Docker Build Cache** | ✅ YES | Clear cache, retry build |
| **Dependency Resolution** | 🟡 PARTIAL | Simple version bump, conflicting deps |
| **Python Version Compat** | ✅ YES | Py 3.12 deprecated modules |
| **Security Patches** | ❌ NO | Requires human review |

**Tier 1 Decision Logic**:

```python
def tier1_attempt_remediation(incident):
    """Attempt Tier 1 auto-remediation."""
    
    # Classify incident type
    incident_type = classify_incident(incident)
    
    # Check if auto-fixable
    if incident_type in AUTO_FIXABLE_PATTERNS:
        result = apply_auto_fix(incident)
        
        if result.success:
            # Log and monitor
            return {"status": "RESOLVED", "tier": 1, "time_s": result.duration}
        else:
            # Continue to Tier 2
            return {"status": "ESCALATE", "tier": 2, "reason": result.error}
    else:
        # Not auto-fixable, escalate immediately
        return {"status": "ESCALATE", "tier": 2, "reason": f"Not auto-fixable: {incident_type}"}
```

**Tier 1 Checklist**:
- [ ] Classify incident type from logs
- [ ] Fetch full CI job logs and error traces
- [ ] Determine if pattern matches known auto-fix
- [ ] Apply auto-fix to local branch
- [ ] Run local validation (linting, imports, quick tests)
- [ ] Commit & push to branch
- [ ] Monitor CI re-run (60s window)
- [ ] If resolved: SUCCESS (escalation stops)
- [ ] If unresolved: ESCALATE to Tier 2 with context

**Tier 1 Remediation Patterns** (P-050 and extended):

```
RP-001: Linting whitespace (ruff W293, E302, etc.)
RP-002: Import ordering & path errors (missing __init__.py)
RP-003: YAML syntax & indentation
RP-004: Docker multi-stage build cache invalidation
RP-005: Python 3.12 compatibility (deprecated modules)
RP-006: Test auto-retry on transient failures
RP-007: Dependency version conflicts (simple bump)
RP-008: GitHub Actions secret scope errors
```

**Tier 1 Resources**:
- `.codex/patterns/P-050_INCIDENT_RESPONSE_AUTOMATION.md`
- `scripts/ci/ci-failure-resolution-agent.py`
- `.github/workflows/self-healing-ci.yml`

---

### 2.2 Tier 2: Specialist Agent Reroute (<90s)

**Activation**: Tier 1 escalation OR if Sev-1 incident not in RP-001 through RP-008  
**SLA**: <90 seconds total from Tier 1 start  
**Success Target**: 20% of Tier 1 failures  
**Agent Pool**:

| Incident Type | Specialist Agent | SLA | Patterns |
|---------------|-----------------|-----|----------|
| **Docker Build Failure** | ci-docker-build-healer | <90s | RP-009, RP-010 |
| **Timeout Cascade** | ci-resilience-emergency-response-agent | <90s | RP-011, RP-012 |
| **Test Framework Error** | autonomous-test-healer-agent | <90s | RP-013, RP-014 |
| **Dependency Conflict** | dependency-conflict-agent | <90s | RP-015, RP-016 |
| **Workflow Syntax** | workflow-ci-fixer | <90s | RP-017, RP-018 |
| **Security Scanning** | codeql-alert-resolution-agent | <120s | RP-019 |

**Tier 2 Activation**:

```python
def tier2_route_to_specialist(incident, tier1_reason):
    """Route to specialist agent based on incident type."""
    
    specialist_map = {
        "docker_build_error": "ci-docker-build-healer",
        "timeout_cascade": "ci-resilience-emergency-response-agent",
        "test_framework_error": "autonomous-test-healer-agent",
        "dependency_conflict": "dependency-conflict-agent",
        "workflow_syntax_error": "workflow-ci-fixer",
        "security_scanning": "codeql-alert-resolution-agent",
    }
    
    incident_category = categorize_incident(incident)
    specialist = specialist_map.get(incident_category, None)
    
    if specialist:
        # Dispatch to specialist with full context
        return dispatch_agent(specialist, incident, tier1_reason)
    else:
        # Unknown pattern, escalate to Tier 3
        return {"status": "ESCALATE_T3", "reason": f"Unknown: {incident_category}"}
```

**Tier 2 Checklist**:
- [ ] Route incident to appropriate specialist agent
- [ ] Pass Tier 1 diagnostics & remediation attempts
- [ ] Specialist reviews logs in <15s
- [ ] Apply specialized remediation (30-45s)
- [ ] Run targeted validation (10-15s)
- [ ] Commit & push changes
- [ ] Monitor Tier 2 agent response time
- [ ] If resolved: SUCCESS
- [ ] If unresolved: ESCALATE to Tier 3 with full context & attempts

---

### 2.3 Tier 3: Maintainer Escalation (<120s)

**Activation**: Tier 1 + Tier 2 failed OR unknown incident pattern  
**SLA**: <120 seconds from alert (strict)  
**Escalation Target**: @mbaetiong  
**Notification Method**: 
- PagerDuty alert (immediate)
- Slack #incident-response (direct message)
- GitHub issue with incident context

**Tier 3 Incident Context Package**:

```json
{
  "incident_id": "INC-2026-07-18-001",
  "severity": "Sev-1",
  "alert_time": "2026-07-18T22:29:41.641Z",
  "time_to_tier3_s": 119,
  "affected_branch": "main",
  "failure_rate": "100%",
  "jobs_failed": 12,
  "jobs_total": 12,
  "root_cause_detected": false,
  "tier1_attempts": [
    {
      "pattern": "RP-001",
      "result": "FAILED",
      "reason": "Issue not linting-related",
      "duration_s": 45
    }
  ],
  "tier2_attempts": [
    {
      "specialist": "ci-docker-build-healer",
      "result": "FAILED",
      "reason": "Build error unrecognized",
      "duration_s": 42
    }
  ],
  "diagnostic_summary": {
    "error_log_excerpt": "[Full error context]",
    "affected_jobs": ["job-1", "job-2", ...],
    "recent_changes": "[Last 5 commits]"
  },
  "recommended_actions": [
    "Check recent deployments",
    "Review last 10 commits",
    "Examine CI runner logs"
  ]
}
```

**Tier 3 Manual Process**:
1. **T+120s-130s**: Maintainer reviews incident context
2. **T+130s-180s**: Decision point
   - **Option A**: Rollback recent changes
   - **Option B**: Deploy hotfix
   - **Option C**: Manual CI job retry
   - **Option D**: Escalate to platform team
3. **T+180s-300s**: Execute remediation
4. **T+300s**: Verify resolution & declare incident closed

**Tier 3 Authority**:
- @mbaetiong: Primary incident commander
- Secondary on-call (if @mbaetiong unavailable)
- Platform team (if infrastructure issue)

---

## 3. Alert-to-Action Flow

### 3.1 Complete Timeline

```
T+0s     │ Alert fired (CI job failed, all jobs failed, workflow YAML error)
         │ → Alert system detects & creates incident #ID
         │ → Timestamp recorded in incident log
         │
T+2s     │ Tier 1 activation
         │ → ci-failure-resolution-agent auto-spawned
         │ → Fetch CI logs, classify incident type
         │ → Begin pattern matching
         │
T+10s    │ Pattern classification complete
         │ → If RP-001 through RP-008: Begin auto-fix
         │ → Else: Prepare Tier 2 escalation
         │
T+30-45s │ Tier 1 remediation applied (if auto-fixable)
         │ → Code changes committed & pushed
         │ → CI re-run triggered
         │ → Monitor for success/failure
         │
T+60s    │ Tier 1 decision point
         │ ├─ Success: RESOLVED (escalation stops) ✓
         │ └─ Failure: ESCALATE to Tier 2
         │
T+62s    │ Tier 2 activation (if needed)
         │ → Route to specialist agent
         │ → Specialist reviews incident in <10s
         │ → Apply specialized remediation (30-45s)
         │
T+90s    │ Tier 2 decision point
         │ ├─ Success: RESOLVED ✓
         │ └─ Failure: ESCALATE to Tier 3
         │
T+92s    │ Tier 3 activation (if needed)
         │ → Create incident context package
         │ → Page @mbaetiong via PagerDuty
         │ → Post incident to Slack #incident-response
         │
T+120s   │ Tier 3 SLA deadline
         │ → @mbaetiong must acknowledge within 30s
         │ → Provide manual remediation decision
         │
T+180s   │ Execute Tier 3 remediation
         │ → Rollback, hotfix, or manual intervention
         │ → Monitor resolution
         │
T+300s   │ Incident resolved (or escalated further)
         │ → Close incident
         │ → Schedule post-mortem
         │ → Document lessons learned
```

### 3.2 Escalation Criteria

**Automatic escalation from Tier 1 → Tier 2**:
- Incident NOT in RP-001 through RP-008
- Auto-fix applied but CI still failing
- Tier 1 agent unable to classify incident
- Time elapsed: >60s

**Automatic escalation from Tier 2 → Tier 3**:
- Specialist agent unable to resolve
- Specialist agent timeout (>90s)
- Incident classified as out-of-scope for Tier 2
- Multiple Tier 2 attempts failed
- Time elapsed: >90s from Tier 1 start

**Manual escalation**:
- Maintainer judgment call on critical incident
- Organizational policy violation
- Security issue requiring immediate lockdown
- Unknown error pattern with high impact

---

## 4. SLA Enforcement & Monitoring

### 4.1 SLA Metrics

```yaml
Sev-1 Incidents:
  Alert Detection: <10s (automated)
  Tier 1 Response: <60s (from alert)
  Tier 2 Response: <90s (from alert)
  Tier 3 Response: <120s (from alert)
  TOTAL SLA: <2 minutes (alert to maintainer)

Sev-2 Incidents:
  Response Time: <10 minutes
  Target Success: >80% resolution without escalation

Sev-3 Incidents:
  Response Time: <2 hours (working hours)
  Pattern Analysis: Automated logging
  
Sev-4 Incidents:
  Batch Processing: <24 hours
  No Individual SLA
```

### 4.2 Monitoring Dashboard

Create daily/weekly metrics:
```
Sev-1 KPIs:
├─ Mean Time to Tier 1: [X.XXs]
├─ Mean Time to Tier 2: [X.XXs]
├─ Mean Time to Tier 3: [X.XXs]
├─ Tier 1 Success Rate: [XX%]
├─ Tier 2 Success Rate: [XX%]
├─ Total Sev-1 Count: [N]
├─ Incidents hitting Tier 3: [N/total]
├─ SLA Compliance (Sev-1): [XX% <2min]
└─ SLA Compliance (Sev-2): [XX% <10min]

Sev-2 KPIs:
├─ Mean Time to Resolution: [X.XXmin]
├─ Success Rate (no escalation): [XX%]
└─ Escalation Rate: [XX%]

Sev-3 KPIs:
├─ Flaky Test Detection: [N/week]
├─ Pattern Analysis Complete: [Y/N]
└─ Root Cause Identified: [Y/N]
```

### 4.3 SLA Violation Response

**If Sev-1 SLA breached** (<2 min):
1. Incident marked as "SLA BREACH"
2. Post-mortem scheduled within 24 hours
3. Root cause analysis on escalation delay
4. Automation gap identified and documented
5. Corrective action plan created

**If Tier 1 success <70%**:
- Analyze failed patterns
- Extend RP patterns or improve detection
- Retrain agent with new examples

**If Tier 2 success <20%**:
- Review specialist agent routing
- Improve incident categorization
- Extend Tier 2 SLA if needed for complex cases

---

## 5. Incident Reporting & Post-Mortems

### 5.1 Incident Documentation

Every Sev-1 and Sev-2 incident generates:
```
incident-[timestamp]-[incident-id].md
├─ Alert Time
├─ Root Cause
├─ Tier 1 Attempts
├─ Tier 2 Attempts (if any)
├─ Tier 3 Actions (if any)
├─ Resolution Time
├─ SLA Status (met/breached)
├─ Lessons Learned
└─ Corrective Actions
```

### 5.2 Post-Mortem Schedule

| Severity | When | Format |
|----------|------|--------|
| Sev-1 | Within 24 hours | Sync meeting + document |
| Sev-2 | Within 72 hours | Async document |
| Sev-3 | Weekly pattern review | Batch analysis |

### 5.3 Blameless Culture

All post-mortems follow blameless incident review principles:
- Focus on systems, not individuals
- Identify root causes and contributing factors
- Extract learning for improvement
- Update runbooks and automation

---

## 6. Exception Handling

### 6.1 Known Limitations

**Tier 1 cannot auto-fix**:
- Breaking API changes
- Data migration failures
- Deployment orchestration issues
- Multi-service coordination problems

**Tier 2 escalation criteria**:
- If incident type not in specialist agent pool
- If specialist agent fails twice consecutively
- If unknown error pattern detected

**Tier 3 decision authority**:
- @mbaetiong has final decision on remediation strategy
- Can override Tier 1/2 recommendations
- Can escalate to platform team or leadership

### 6.2 Fallback Procedures

**If Tier 1 agent unavailable**:
- Skip to Tier 2 (specialist reroute)
- Add fallback note to incident context

**If Tier 2 specialist unavailable**:
- Route to general ci-failure-resolution-agent fallback
- Escalate to Tier 3 if unresolved

**If Tier 3 unavailable** (critical):
- Page secondary on-call
- Alert platform team lead
- Escalate to engineering leadership

---

## 7. Integration Points

### 7.1 GitHub Actions Workflows

Master workflows integrate escalation triggers:
```yaml
on: workflow_run

jobs:
  detect_failure:
    runs-on: ubuntu-latest
    if: failure()
    steps:
      - name: Classify Severity
        run: |
          python scripts/ci/classify_incident.py \
            --run-id ${{ github.run_id }} \
            --output /tmp/incident.json
      
      - name: Trigger Tier 1 Remediation
        if: ${{ env.SEVERITY == 'Sev-1' }}
        uses: ./.github/actions/tier1-auto-remediation
        with:
          incident-file: /tmp/incident.json
```

### 7.2 Cognitive Brain Integration

Incidents logged to cognitive memory for pattern learning:
```python
from scripts.cognitive.incident_memory import log_incident

log_incident(
    severity=incident.severity,
    pattern=incident.pattern,
    tier_resolved=incident.tier_resolved,
    resolution_time_s=incident.duration,
    success=incident.resolved
)
```

### 7.3 Alerting Systems

- **PagerDuty**: Tier 3 escalation
- **Slack**: #incident-response channel + DMs
- **GitHub Issues**: Incident tracking & linking
- **Email**: Post-mortem notifications

---

## 8. Policy Version Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-07-18 | CI Response Team | Initial policy, 3-tier model, Sev-1-4 classifications |

**Next Review**: 2026-08-18 (30 days)  
**Last Updated**: 2026-07-18T22:29Z

---

## 9. Quick Reference Card

### Severity Classification

```
Sev-1: 100% failure, blocks main  → <2 min SLA, Tier 1→2→3
Sev-2: 70%+ failure, blocks PR     → <10 min, Tier 1→2
Sev-3: 30-70% intermittent         → <2 hours, Tier 1 only
Sev-4: <30% noise                  → <24 hours, log & monitor
```

### Escalation Timeline

```
T+0s   : Alert
T+2s   : Tier 1 auto-remediation
T+60s  : Decision (success? → stop : escalate)
T+62s  : Tier 2 specialist (if needed)
T+90s  : Decision (success? → stop : escalate)
T+92s  : Tier 3 maintainer page (if needed)
T+120s : SLA deadline
T+300s : Resolution or further escalation
```

### Contact Escalation

```
Tier 1: ci-failure-resolution-agent (auto)
Tier 2: Specialist agents (auto-routed)
Tier 3: @mbaetiong (PagerDuty + Slack DM)
```

---

**Document Status**: ✅ APPROVED & ACTIVE  
**Compliance**: REQ-4 (SLA), REQ-5 (Escalation), PDA (Decision tracking)  
**Authority**: @mbaetiong D-tier (2026-07-13T18:20Z)
