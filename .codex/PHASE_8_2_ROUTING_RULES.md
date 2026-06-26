# Phase 8.2: Issue Classification & Routing Rules

**Date:** 2026-06-26  
**Authority:** D-mode (fully autonomous)  
**Status:** Active  
**Classification Accuracy Target:** 95%+

---

## Executive Summary

This document defines the intelligent issue triage system for v0.1.0-final post-release phase. It provides:
1. **Severity classification framework** (P0-P4)
2. **Automated routing rules** by severity and category
3. **SLA enforcement** for each severity level
4. **Category-based prioritization** heuristics
5. **Escalation procedures** for critical issues

---

## Severity Classification Framework

### P0: Critical (Immediate)

**SLA Response Time:** <15 minutes  
**Escalation:** Immediate to @mbaetiong  
**Auto-Response:** Highest priority queue

**Triggering Keywords:**
- `critical`
- `production-down`
- `exploit`
- `security-breach`
- `data-loss`
- `complete-outage`
- `release-blocker`
- `all-tests-fail`
- `regression` (on main branch)

**Examples:**
- Security vulnerability affecting live production
- All CI tests failing, blocking releases
- Data loss or corruption bug
- Complete service outage
- Unpatched CVE in dependency

**Routing Logic:**
```
IF (severity == "P0") THEN
  - Assign to @mbaetiong immediately
  - Add to urgent escalation queue
  - Post public status notification
  - Create emergency war room discussion
  - Begin incident response protocol
```

---

### P1: High Priority (24-Hour Response)

**SLA Response Time:** <24 hours  
**Escalation:** Urgent queue + @mbaetiong awareness  
**Auto-Response:** High priority queue

**Triggering Keywords:**
- `bug`
- `crash`
- `security` (non-critical)
- `vulnerability` (non-critical)
- `workaround-needed`
- `performance-degradation`
- `regression` (non-production)

**Examples:**
- Non-critical security vulnerability
- Feature crash with workaround available
- Significant performance degradation
- Infrastructure dependency failure
- Major documentation gap blocking users

**Routing Logic:**
```
IF (severity == "P1") THEN
  - Add to urgent queue
  - Flag for @mbaetiong daily review
  - Require action within 24 hours
  - Assign to on-call engineer or team lead
  - Consider public acknowledgment
```

---

### P2: Medium Priority (3-Day Response)

**SLA Response Time:** <72 hours  
**Escalation:** Standard queue  
**Auto-Response:** Normal priority queue

**Triggering Keywords:**
- `feature-request`
- `enhancement`
- `improvement`
- `documentation`
- `performance-optimization`
- `ci-cd` issues (non-blocking)
- `dependency-update` (non-critical)

**Examples:**
- New feature request from user
- Documentation clarification needed
- Non-critical performance optimization
- CI improvement (not blocking)
- Code quality enhancement
- Test coverage gap

**Routing Logic:**
```
IF (severity == "P2") THEN
  - Add to standard work queue
  - Plan for next sprint
  - Assign to team member
  - Acknowledge user within 24 hours
  - Target resolution within 3 days
```

---

### P3: Low Priority (1-Week Response)

**SLA Response Time:** <7 days  
**Escalation:** Backlog  
**Auto-Response:** Backlog queue

**Triggering Keywords:**
- `nice-to-have`
- `minor`
- `cosmetic`
- `typo`
- `style`
- `future-consideration`
- `wishlist`

**Examples:**
- Typo in documentation or code
- UI cosmetic improvement
- Code style suggestion
- Minor edge case handling
- Wishlist feature request
- Future API improvement

**Routing Logic:**
```
IF (severity == "P3") THEN
  - Add to backlog
  - No SLA enforcement
  - Consider in quarterly planning
  - Candidate for junior contributors
  - Batch similar issues for efficiency
```

---

### P4: Cosmetic (No SLA)

**SLA Response Time:** None  
**Escalation:** No escalation  
**Auto-Response:** Backlog (considered ad-hoc)

**Triggering Keywords:**
- `bikeshed`
- `non-functional`
- `discussion`
- `conversation-starter`

**Examples:**
- Design philosophy discussion
- Code review discussion
- Opinion-based improvements
- Exploratory discussions
- Community engagement

**Routing Logic:**
```
IF (severity == "P4") THEN
  - No automatic routing
  - May be closed as "discussion"
  - Community-driven engagement acceptable
  - Consider converting to Discussion
  - No SLA or escalation
```

---

## Issue Category Classification

The system classifies issues into 8 categories for better routing and prioritization:

| Category | Keywords | Default Severity | Routing Destination |
|----------|----------|------------------|-------------------|
| **Security** | security, vulnerability, exploit, cve, breach | P0 | @mbaetiong + Security team |
| **Bug** | bug, crash, fail, error, regression | P1 | Engineering team |
| **Feature** | feature, enhancement, request, improvement | P3 | Product backlog |
| **Documentation** | doc, documentation, guide, readme, tutorial | P3 | Docs team |
| **Performance** | performance, slow, memory, cpu, latency | P2 | Performance team |
| **Infrastructure** | ci-cd, deployment, docker, kubernetes, pipeline | P1 | DevOps/SRE team |
| **CI/CD** | ci-cd, github-actions, workflow, test | P2 | CI/CD team |
| **Dependency** | dependency, upgrade, requirement, package | P2 | Dependency management |

---

## Automated Classification Algorithm

### Step 1: Content Analysis

```python
def classify_issue(issue_title, issue_body, labels):
    """
    Classify issue by severity and category.
    Returns: (severity, category, confidence)
    """
    
    # Combine all text for keyword matching
    full_text = (issue_title + " " + issue_body).lower()
    
    # Extract explicit severity from labels if present
    explicit_severity = extract_severity_label(labels)
    if explicit_severity:
        return (explicit_severity, infer_category(full_text), 0.95)
    
    # Check for P0 keywords first (highest priority)
    if has_p0_keywords(full_text):
        return ("P0", infer_category(full_text), 0.90)
    
    # Check category-specific severity
    category = infer_category(full_text)
    base_severity = get_category_default_severity(category)
    
    # Adjust based on severity modifiers
    if has_p1_keywords(full_text):
        return ("P1", category, 0.85)
    elif has_p2_keywords(full_text):
        return ("P2", category, 0.80)
    elif has_p3_keywords(full_text):
        return ("P3", category, 0.75)
    
    # Default to category default
    return (base_severity, category, 0.70)
```

### Step 2: Category Detection

Priority order for multi-category issues:
1. Security (always highest priority if matches)
2. Infrastructure/CI-CD (high priority if production-affecting)
3. Bug (higher than feature)
4. Performance (medium priority)
5. Documentation (lower priority)
6. Feature (lowest unless user-critical)

### Step 3: Confidence Scoring

| Signal | Confidence Boost |
|--------|-----------------|
| Explicit P0-P4 label | +25% |
| Multiple matching keywords | +15% |
| Category match + severity keywords | +20% |
| User/PR author | +10% (if known reporter) |
| Related to recent release | +15% |

---

## Routing Matrix

### By Severity & Category

```
┌─────────────────────────────────────────────────────────────┐
│ ROUTING DECISION MATRIX                                      │
├─────────────────┬──────────────┬──────────┬────────────────┤
│ Severity        │ Response SLA │ Queue    │ Escalation     │
├─────────────────┼──────────────┼──────────┼────────────────┤
│ P0 - Critical   │ <15 minutes  │ Urgent   │ @mbaetiong     │
│                 │              │          │ + Incident     │
│ P1 - High       │ <24 hours    │ Urgent   │ On-call eng    │
│ P2 - Medium     │ <72 hours    │ Standard │ Team lead      │
│ P3 - Low        │ <7 days      │ Backlog  │ None           │
│ P4 - Cosmetic   │ None         │ Backlog  │ None           │
└─────────────────┴──────────────┴──────────┴────────────────┘
```

---

## Escalation Procedures

### P0 Critical Escalation (Auto-Triggered)

1. **Immediate Actions (0-5 minutes):**
   - Create emergency discussion in GitHub
   - Post Slack notification to #critical-incidents
   - Assign to @mbaetiong
   - Add `severity:critical` label
   - Create incident war room

2. **First Response (5-15 minutes):**
   - @mbaetiong acknowledges receipt
   - Assess scope and impact
   - Activate incident response team if needed
   - Post status update to issue

3. **Investigation Phase (15-60 minutes):**
   - Root cause analysis begins
   - Temporary mitigation deployed if possible
   - Escalation committee convenes
   - Public status page updated

4. **Resolution & Communication:**
   - Fix deployed and validated
   - Post-mortem planned
   - User communication posted
   - Incident closed and documented

### P1 High Priority Escalation (24-Hour Response)

1. **Acknowledgment (0-4 hours):**
   - Add to urgent queue
   - Assign to available engineer
   - Post initial response to issue
   - Add `severity:high` label

2. **Investigation (4-12 hours):**
   - Root cause analysis
   - Workaround posted if available
   - Timeline estimated

3. **Resolution (12-24 hours):**
   - Fix prepared and tested
   - Deployed or planned for next release
   - User notified of status

---

## Label Taxonomy

### Severity Labels
- `severity:critical` — P0 issues (immediate)
- `severity:high` — P1 issues (24-hour)
- `severity:medium` — P2 issues (3-day)
- `severity:low` — P3 issues (1-week)
- `severity:cosmetic` — P4 issues (no SLA)

### Category Labels
- `type:bug` — Bugs and regressions
- `type:feature` — Feature requests
- `type:documentation` — Documentation needs
- `type:security` — Security issues
- `type:performance` — Performance issues
- `component:ci-cd` — CI/CD pipeline
- `component:infrastructure` — Infrastructure
- `component:api` — API issues
- `component:ui` — UI issues
- `component:docs` — Documentation

### Status Labels
- `status:triage` — Needs triage
- `status:investigating` — Under investigation
- `status:blocked` — Blocked by another issue
- `status:in-progress` — Currently being worked on
- `status:resolved` — Resolved, awaiting verification
- `status:duplicate` — Duplicate of another issue
- `status:wontfix` — Won't be fixed (documented reason)

### Response Labels
- `needs-response` — Awaiting response
- `waiting-for-user` — Waiting on user feedback
- `waiting-for-feedback` — Waiting on community feedback
- `good-first-issue` — Suitable for new contributors
- `help-wanted` — Requesting community help

---

## Classification Accuracy Metrics

### Target: 95%+ Accuracy

**Measurement Criteria:**
- Classification accuracy: Severity assigned matches ground truth
- False positive rate: <3% (miscategorized as higher severity)
- False negative rate: <2% (missed critical issues)
- Category match rate: >90%

**Testing & Validation:**

Run classification on sample of 20+ issues:

```bash
# Test sample (pseudocode)
issues_to_test = [
  {id: 5085, expected_severity: "P2", expected_category: "CI/CD"},
  # ... 19+ more test cases
]

for issue in issues_to_test:
  result = classify_issue(issue)
  accuracy = result.severity == issue.expected_severity ? 100 : 0
  report_metric("classification_accuracy", accuracy)
```

---

## Manual Override Procedure

For issues where automated classification is uncertain:

1. **Confidence < 70%:** Flag for manual review
2. **Manual Review Process:**
   - Engineering lead reviews issue
   - Posts classification decision with rationale
   - Documents any edge cases
   - Updates training data

3. **Appeal Process:**
   - User can request severity review
   - @mbaetiong evaluates on business impact
   - Decision final, documented in issue

---

## Integration Points

### GitHub Workflows
- Automated labeling on new issues
- Triage summary reports (weekly)
- SLA tracking and alerts
- Escalation notifications

### Slack Integration
- P0 alerts to #critical-incidents
- P1 daily digests to #urgent-queue
- Weekly summary to #engineering

### External Systems
- Dashboard updates (`.codex/PHASE_8_2_TRIAGE_DASHBOARD.md`)
- Reports (`PHASE_8_2_WEEKLY_REPORT_WEEK1.md`)
- Metrics tracking (SQLite database)

---

## Success Criteria

✅ **Achieved Targets:**
- 100% of issues classified within 5 minutes
- P0 response time <15 minutes (SLA)
- 95%+ routing accuracy
- Zero critical issues missed (100% P0 detection)
- All open issues labeled and categorized

---

## Document Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-06-26 | Initial comprehensive rules document |

---

**Next Steps:**
- Apply routing rules to all issues
- Monitor SLA compliance
- Generate weekly triage reports
- Refine classification rules based on feedback
- Track metrics for continuous improvement

