# Zendesk Workflow Visual Guide

This document provides visual representations of the Zendesk administration workflows in _codex_.

## Core Workflow: Snapshot-Diff-Plan-Apply

```text
┌─────────────────────────────────────────────────────────────────────┐
│                    Zendesk Configuration Lifecycle                   │
└─────────────────────────────────────────────────────────────────────┘

┌────────────────┐
│  SNAPSHOT      │  1. Capture current state from Zendesk
│  Current State │     Command: codex zendesk snapshot --env=dev
└───────┬────────┘     Output: snapshot/dev/latest/*.json
        │
        ▼
┌────────────────┐
│  DEFINE        │  2. Create or update desired state
│  Desired State │     Edit: configs/desired/zendesk/*.json
└───────┬────────┘     Version control changes
        │
        ▼
┌────────────────┐
│  DIFF          │  3. Compare desired vs. current
│  Compare       │     Command: codex zendesk diff <type>
└───────┬────────┘     Output: diffs/<type>_diff.json
        │
        ▼
┌────────────────┐
│  REVIEW        │  4. Human review of changes
│  Changes       │     Review: cat diffs/*.json | jq
└───────┬────────┘     Verify intent matches diff
        │
        ▼
┌────────────────┐
│  PLAN          │  5. Generate validated execution plan
│  Create Plan   │     Command: codex zendesk plan <type>
└───────┬────────┘     Output: plans/<type>_plan.json
        │
        ▼
┌────────────────┐
│  DRY RUN       │  6. Test plan without making changes
│  Validate      │     Command: codex zendesk apply --dry-run
└───────┬────────┘     Verify plan is executable
        │
        ▼
┌────────────────┐
│  APPLY         │  7. Execute plan in Zendesk
│  Execute       │     Command: codex zendesk apply <type>
└───────┬────────┘     Updates Zendesk configuration
        │
        ▼
┌────────────────┐
│  VERIFY        │  8. Confirm changes applied correctly
│  Validate      │     Command: codex zendesk snapshot --env=dev
└───────┬────────┘     Compare before/after snapshots
        │
        ▼
┌────────────────┐
│  MONITOR       │  9. Track metrics and outcomes
│  Metrics       │     Command: codex zendesk metrics
└────────────────┘     Monitor success rates, errors
```text
## Multi-Environment Promotion Flow

```text
┌─────────────────────────────────────────────────────────────────────┐
│              Development → Staging → Production Flow                 │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│  DEV ENVIRONMENT │  Test changes in safe environment
└────────┬─────────┘
         │
         │ 1. Test & Validate
         │    - Apply configuration
         │    - Create test tickets
         │    - Verify triggers/macros work
         │
         ▼
┌──────────────────┐
│  PEER REVIEW     │  Code review & approval
└────────┬─────────┘
         │
         │ 2. Git workflow
         │    - Commit desired state
         │    - Open pull request
         │    - Get approvals
         │
         ▼
┌──────────────────┐
│ STAGING ENV      │  Pre-production validation
└────────┬─────────┘
         │
         │ 3. UAT & Integration
         │    - Apply to staging
         │    - User acceptance testing
         │    - Integration testing
         │
         ▼
┌──────────────────┐
│ CHANGE APPROVAL  │  Production change control
└────────┬─────────┘
         │
         │ 4. Change Management
         │    - CAB approval (if required)
         │    - Schedule maintenance window
         │    - Prepare rollback plan
         │
         ▼
┌──────────────────┐
│ PROD ENVIRONMENT │  Production deployment
└────────┬─────────┘
         │
         │ 5. Deploy & Monitor
         │    - Apply to production
         │    - Monitor metrics
         │    - Verify ticket flow
         │
         ▼
┌──────────────────┐
│ POST-DEPLOYMENT  │  Validation & documentation
└──────────────────┘
         │
         • Archive snapshots
         • Update documentation
         • Track metrics
```text
## Object Type Workflows

### Triggers Workflow

```text
┌─────────────────────────────────────────────────────────────────────┐
│                    Trigger Management Workflow                       │
└─────────────────────────────────────────────────────────────────────┘

Trigger Types:
┌──────────────┬──────────────┬──────────────┬──────────────┐
│ AUTO-ASSIGN  │ NOTIFICATION │  ESCALATION  │   TAGGING    │
└──────────────┴──────────────┴──────────────┴──────────────┘

Workflow:
1. Define trigger conditions
   └─> Status, priority, custom fields, etc.

2. Define trigger actions
   └─> Assign, notify, tag, update field

3. Set trigger priority/position
   └─> Order matters! Lower number = higher priority

4. Test with sample tickets
   └─> Create test ticket in dev, verify trigger fires

5. Monitor trigger performance
   └─> Track execution metrics

Example Flow:
New Ticket (Priority: High)
    │
    ├─> Trigger: "Auto-assign high priority"
    │   └─> Action: Assign to Tier 2 group
    │
    ├─> Trigger: "Notify on high priority"
    │   └─> Action: Send webhook to PagerDuty
    │
    └─> Trigger: "Tag high priority tickets"
        └─> Action: Add tag "priority_escalation"
```text
### Views Workflow

```text
┌─────────────────────────────────────────────────────────────────────┐
│                     View Management Workflow                         │
└─────────────────────────────────────────────────────────────────────┘

View Categories:
┌──────────────┬──────────────┬──────────────┬──────────────┐
│ AGENT QUEUES │  REPORTING   │   MANAGER    │   CUSTOM     │
└──────────────┴──────────────┴──────────────┴──────────────┘

Common View Patterns:

1. Personal Queue
   Conditions:
   • Status: not solved
   • Assignee: current user
   Sort: created_at (oldest first)

2. Team Queue
   Conditions:
   • Status: new or open
   • Group: specific team
   • Assignee: none
   Sort: priority, then created_at

3. Escalated Tickets
   Conditions:
   • Priority: high or urgent
   • Status: not solved
   • Age: > 24 hours
   Sort: priority, then age

4. Pending Tickets
   Conditions:
   • Status: pending
   • Updated: > 48 hours ago
   Sort: updated_at (oldest first)
```text
### Macros Workflow

```text
┌─────────────────────────────────────────────────────────────────────┐
│                    Macro Management Workflow                         │
└─────────────────────────────────────────────────────────────────────┘

Macro Design Process:

1. Identify Common Patterns
   │
   ├─> Analyze ticket resolution patterns
   ├─> Survey agents for frequently used responses
   └─> Review ticket metrics for common resolutions

2. Design Macro Actions
   │
   ├─> Set ticket status
   ├─> Add public/private comment
   ├─> Update custom fields
   └─> Add tags for tracking

3. Organize Macros
   │
   ├─> Use consistent naming: [Category] Action
   │   Example: [Billing] Refund Processed
   ├─> Group by department/product
   └─> Maintain top 20-30 most used

4. Test & Refine
   │
   ├─> Pilot with small team
   ├─> Gather feedback
   ├─> Track usage metrics
   └─> Iterate based on data

5. Monitor Usage
   │
   └─> Track macro application rates
       └─> Archive unused macros
```text
## Error Handling & Recovery

```text
┌─────────────────────────────────────────────────────────────────────┐
│                    Error Handling Flow Chart                         │
└─────────────────────────────────────────────────────────────────────┘

Apply Command Executed
        │
        ▼
┌───────────────┐
│ Rate Limited? │──Yes──> Wait & Retry (exponential backoff)
└───────┬───────┘             │
        │No                   │
        ▼                     ▼
┌───────────────┐      ┌──────────────┐
│ Auth Failed?  │──Yes─>│ Check Creds  │──> Fix & Retry
└───────┬───────┘      └──────────────┘
        │No
        ▼
┌───────────────┐
│ Invalid JSON? │──Yes──> Validate JSON ──> Fix & Retry
└───────┬───────┘
        │No
        ▼
┌───────────────┐
│ Partial Fail? │──Yes──> Snapshot Current ──> Diff ──> Apply Remaining
└───────┬───────┘
        │No
        ▼
┌───────────────┐
│ Success!      │──> Verify ──> Monitor Metrics
└───────────────┘

Rollback Decision Tree:
        │
        ▼
┌─────────────────┐
│ Need Rollback?  │
└───────┬─────────┘
        │
        ├─> Minor Issue ──> Fix Forward
        │   └─> Create new plan with correction
        │
        ├─> Major Issue ──> Rollback
        │   └─> Use previous snapshot as desired state
        │
        └─> Critical ──> Emergency Rollback
            └─> Manual intervention + snapshot restore
```text
## Automation & Task Sequences

```text
┌─────────────────────────────────────────────────────────────────────┐
│                    Task Sequence Automation                          │
└─────────────────────────────────────────────────────────────────────┘

Task Sequence Types:

1. Daily Operations
   ┌──────────────────┐
   │ Morning Snapshot │ ──> Capture overnight changes
   └──────────────────┘

2. Configuration Updates
   ┌──────────────────┐
   │ Snapshot All     │
   └────────┬─────────┘
            │
   ┌────────▼─────────┐
   │ Update Configs   │ ──> Triggers, Views, Macros
   └────────┬─────────┘
            │
   ┌────────▼─────────┐
   │ Generate Plans   │
   └────────┬─────────┘
            │
   ┌────────▼─────────┐
   │ Apply Changes    │
   └────────┬─────────┘
            │
   ┌────────▼─────────┐
   │ Verify & Report  │
   └──────────────────┘

3. Multi-Environment Promotion
   ┌──────────────────┐
   │ Test in Dev      │
   └────────┬─────────┘
            │
   ┌────────▼─────────┐
   │ Promote Staging  │
   └────────┬─────────┘
            │
   ┌────────▼─────────┐
   │ Validate Staging │
   └────────┬─────────┘
            │
   ┌────────▼─────────┐
   │ Deploy Prod      │
   └────────┬─────────┘
            │
   ┌────────▼─────────┐
   │ Monitor Metrics  │
   └──────────────────┘

4. Scheduled Maintenance
   ┌──────────────────┐
   │ Weekly Review    │ ──> Audit configurations
   └────────┬─────────┘
            │
   ┌────────▼─────────┐
   │ Archive Snapshots│ ──> Retention policy
   └────────┬─────────┘
            │
   ┌────────▼─────────┐
   │ Generate Reports │ ──> Metrics & trends
   └──────────────────┘
```text
## Monitoring & Metrics Flow

```text
┌─────────────────────────────────────────────────────────────────────┐
│                    Metrics & Monitoring Flow                         │
└─────────────────────────────────────────────────────────────────────┘

Data Collection:
┌──────────────────┐
│ Operation Logs   │ ──> .codex/logs/zendesk_*.log
└────────┬─────────┘
         │
         ├──> Apply Success Rate
         ├──> Rate Limit Retries
         ├──> Operation Duration
         └──> Error Types

Metrics Processing:
┌──────────────────┐
│ codex zendesk    │
│ metrics          │ ──> Aggregate data
└────────┬─────────┘     Generate reports
         │
         ├──> JSON export ──> Prometheus
         ├──> Text report ──> Review
         └──> Time series ──> Grafana

Alerting:
┌──────────────────┐
│ Threshold Check  │
└────────┬─────────┘
         │
         ├──> Success Rate < 95% ──> Alert
         ├──> Rate Limits > 5%    ──> Alert
         └──> Apply Failures      ──> Notify On-Call

Dashboard Metrics:
┌─────────────────────────┐
│ Key Performance         │
│ Indicators (KPIs)       │
└─────────────────────────┘
│
├─> Apply Success Rate
│   Target: > 95%
│
├─> Average Apply Duration
│   Target: < 30 seconds
│
├─> Rate Limit Hit Rate
│   Target: < 5%
│
├─> Snapshot Freshness
│   Target: < 24 hours
│
└─> Configuration Drift
    Target: Monitor trends
```text
## Integration Points

```text
┌─────────────────────────────────────────────────────────────────────┐
│                    System Integration Map                            │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────┐
│   Git/VCS    │ ◄──┐
└──────────────┘    │
                    │ Desired State
┌──────────────┐    │ Version Control
│   _codex_    │ ───┤
│   CLI        │    │ Plans & Diffs
└──────┬───────┘    │
       │            │
       │ API        │
       ▼            │
┌──────────────┐    │
│   Zendesk    │ ───┘
│   Support    │    Snapshots
└──────┬───────┘    Current State
       │
       │ Webhooks
       ▼
┌──────────────┐
│  External    │
│  Systems     │
└──────────────┘
       │
       ├──> PagerDuty
       ├──> Slack
       ├──> Custom Apps
       └──> Monitoring

Data Flow:
Git → _codex_ → Zendesk → Webhooks → External Systems
 ↑                ↓
 └────────────────┘
   Snapshots & Evidence
```text
## Quick Reference Commands

```bash
# Complete workflow in one sequence
codex-task-sequence --sequence scripts/task_sequences/zendesk_first_cycle.yaml

# Individual steps
codex zendesk snapshot --env=dev                                    # 1. Snapshot
codex zendesk diff triggers --desired-file ... --current-file ...   # 2. Diff
codex zendesk plan triggers --diff-file ... --output ...            # 3. Plan
codex zendesk apply triggers plans/plan.json --env=dev --dry-run   # 4. Dry run
codex zendesk apply triggers plans/plan.json --env=dev             # 5. Apply
codex zendesk snapshot --env=dev                                    # 6. Verify
codex zendesk metrics                                               # 7. Monitor
```text

## Troubleshooting Decision Tree

```text
Issue Encountered
        │
        ▼
┌──────────────────┐
│ What went wrong? │
└────────┬─────────┘
         │
         ├─> API Error ──────────────> Check credentials
         │                             Check rate limits
         │                             Verify network
         │
         ├─> JSON Error ─────────────> Validate with jq
         │                             Check syntax
         │                             Review schema
         │
         ├─> Apply Failed ───────────> Check logs
         │                             Review plan
         │                             Dry run again
         │
         ├─> Unexpected Changes ─────> Compare snapshots
         │                             Review diff
         │                             Check desired state
         │
         └─> Performance Issue ──────> Check rate limiting
                                       Monitor metrics
                                       Optimize batch size
```text
## Best Practices Checklist

```text
Before Making Changes:
□ Snapshot current state
□ Review existing configuration
□ Define desired state clearly
□ Validate JSON syntax

During Changes:
□ Generate and review diff
□ Create validated plan
□ Run dry-run first
□ Test in dev environment
□ Get peer review

After Changes:
□ Verify with new snapshot
□ Monitor metrics
□ Document changes
□ Update runbooks if needed
□ Archive evidence

Regular Maintenance:
□ Daily: Monitor metrics
□ Weekly: Review logs
□ Monthly: Audit configurations
□ Quarterly: Clean up unused objects
```text
## Additional Resources

- [ZENDESK_NEWCOMER_GUIDE.md](ZENDESK_NEWCOMER_GUIDE.md) - Complete guide
- [../runbooks/zendesk_admin_workflow.md](../runbooks/zendesk_admin_workflow.md) - Detailed workflow
- [README.md](README.md) - Zendesk docs navigation

---

**These visual guides complement the written documentation. Use them as quick references when working with Zendesk configurations.**
