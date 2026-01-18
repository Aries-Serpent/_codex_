# Zendesk Support Administrator Newcomer Guide

Welcome to Zendesk administration with **_codex_**! This guide will help you understand how to manage Zendesk Support configurations as code, enabling reproducible, version-controlled administrative workflows.

## Table of Contents

1. [Overview](#overview)
2. [Core Concepts](#core-concepts)
3. [Getting Started](#getting-started)
4. [Zendesk Workflow](#zendesk-workflow)
5. [Configuration Examples](#configuration-examples)
6. [Common Tasks](#common-tasks)
7. [Monitoring and Metrics](#monitoring-and-metrics)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)
10. [Advanced Topics](#advanced-topics)

## Overview

### What is Zendesk Administration with _codex_?

_codex_ provides a **configuration-as-code** approach to managing Zendesk Support:

- **Snapshot**: Capture current Zendesk configuration as JSON
- **Diff**: Compare desired vs. current state
- **Plan**: Generate change plans from diffs
- **Apply**: Execute plans safely with rollback capability
- **Verify**: Monitor metrics and validate outcomes

### Benefits

✅ **Version Control**: Track all configuration changes in Git  
✅ **Reproducibility**: Consistent deployments across environments  
✅ **Safety**: Review changes before applying  
✅ **Auditing**: Complete history of who changed what and when  
✅ **Automation**: Scriptable workflows for common tasks  
✅ **Documentation**: Self-documenting configurations  

### Supported Zendesk Objects

| Object Type | Description | Common Use Cases |
|------------|-------------|------------------|
| **Triggers** | Automated actions on ticket events | Auto-assign, notifications, SLA tracking |
| **Views** | Saved ticket filters | Agent queues, reporting views |
| **Macros** | Predefined responses and actions | Common replies, status updates |
| **Ticket Fields** | Custom fields on tickets | Product, priority, customer type |
| **Ticket Forms** | Forms for ticket submission | Different request types |
| **Groups** | Agent teams | Routing, permissions |
| **Webhooks** | External integrations | Incident escalation, notifications |
| **Routing** | Skills-based routing | Agent expertise matching |
| **Talk IVR** | Phone menu system | Voice front door |

## Core Concepts

### Configuration as Code

Instead of making changes in the Zendesk Admin UI:

1. **Define** desired state in JSON files
2. **Version** configurations in Git
3. **Review** changes via pull requests
4. **Apply** changes programmatically
5. **Verify** outcomes with metrics

### The Snapshot-Diff-Plan-Apply Cycle

```text
Current State (Zendesk) ──┐
                          │
                          ├──► Diff ──► Plan ──► Apply ──► New State
                          │
Desired State (JSON) ─────┘
```text
### Environments

Manage multiple Zendesk environments:

- **dev**: Development/sandbox
- **staging**: Pre-production testing
- **prod**: Production environment

Each environment has its own snapshots and configurations.

### Evidence and Audit Trail

Every operation generates evidence:

- **Snapshots**: Full state at a point in time
- **Diffs**: What changed
- **Plans**: What will be applied
- **Metrics**: Success rates, timing, errors
- **Logs**: Detailed operation history

## Getting Started

### Prerequisites

1. **Zendesk Account**: Admin access to at least one Zendesk instance
2. **API Credentials**: Generate an API token in Zendesk Admin
3. **_codex_ Installation**: Complete the main installation (see [NEWCOMER_GUIDE.md](../NEWCOMER_GUIDE.md))

### Environment Setup

1. **Configure Zendesk credentials**:

   Create `.env` file (or use environment variables). The CLI expects
   environment-scoped variables, so set credentials for each environment you
   plan to manage:

   ```bash
   ZENDESK_DEV_SUBDOMAIN=your-dev-subdomain
   ZENDESK_DEV_EMAIL=admin@example.com
   ZENDESK_DEV_TOKEN=your-dev-token
   ZENDESK_STAGING_SUBDOMAIN=your-staging-subdomain
   ZENDESK_STAGING_EMAIL=admin@example.com
   ZENDESK_STAGING_TOKEN=your-staging-token
   ZENDESK_PROD_SUBDOMAIN=your-prod-subdomain
   ZENDESK_PROD_EMAIL=admin@example.com
   ZENDESK_PROD_TOKEN=your-prod-token
   ```

2. **Verify connectivity**:
   ```bash
   codex zendesk snapshot --env=dev --dry-run
   ```

3. **Create directory structure**:
   ```bash
   mkdir -p configs/desired/zendesk
   mkdir -p snapshot/dev
   mkdir -p snapshot/staging
   mkdir -p snapshot/prod
   mkdir -p diffs
   mkdir -p plans
   ```

### First Snapshot

Capture your current Zendesk configuration:

```bash
# Snapshot all supported objects
codex zendesk snapshot --env=dev

# Snapshot specific object types
codex zendesk snapshot --env=dev --objects triggers,views,macros

# Check snapshot location
ls -la snapshot/dev/latest/
```text

Snapshot files are stored in JSON format, ready for version control.

## Zendesk Workflow

### Complete Workflow Example

Here's a complete workflow for managing Zendesk triggers:

#### Step 1: Snapshot Current State

```bash
codex zendesk snapshot --env=dev
```text

This creates `snapshot/dev/<timestamp>/triggers.json` and a `latest` symlink.

#### Step 2: Define Desired State

Create `configs/desired/zendesk/triggers.json`:

```json
{
  "triggers": [
    {
      "title": "Auto-assign high priority tickets",
      "active": true,
      "position": 1,
      "conditions": {
        "all": [
          {
            "field": "status",
            "operator": "is",
            "value": "new"
          },
          {
            "field": "priority",
            "operator": "is",
            "value": "high"
          }
        ]
      },
      "actions": [
        {
          "field": "group_id",
          "value": "TIER_2_GROUP_ID"
        },
        {
          "field": "status",
          "value": "open"
        }
      ]
    }
  ]
}
```text

#### Step 3: Generate Diff

```bash
codex zendesk diff triggers \
  --desired-file configs/desired/zendesk/triggers.json \
  --current-file snapshot/dev/latest/triggers.json \
  --output diffs/triggers_diff.json
```text

Review `diffs/triggers_diff.json` to see what will change.

#### Step 4: Create Plan

```bash
codex zendesk plan triggers \
  --diff-file diffs/triggers_diff.json \
  --output plans/triggers_plan.json
```text

The plan is a validated, executable set of changes.

#### Step 5: Apply Changes

```bash
# Dry run first
codex zendesk apply triggers \
  plans/triggers_plan.json \
  --env=dev \
  --dry-run

# Apply for real
codex zendesk apply triggers \
  plans/triggers_plan.json \
  --env=dev
```text

#### Step 6: Verify and Monitor

```bash
# Check metrics
codex zendesk metrics

# Take new snapshot to verify
codex zendesk snapshot --env=dev

# Compare before/after
diff snapshot/dev/<before>/triggers.json snapshot/dev/latest/triggers.json
```text

### Workflow Automation

Use task sequences for repeatable workflows:

```yaml
# scripts/task_sequences/update_triggers.yaml
name: Update Triggers Workflow
tasks:
  - name: Snapshot current state
    command: codex zendesk snapshot --env=dev
  
  - name: Generate diff
    command: codex zendesk diff triggers
      --desired-file configs/desired/zendesk/triggers.json
      --current-file snapshot/dev/latest/triggers.json
      --output diffs/triggers_diff.json
  
  - name: Create plan
    command: codex zendesk plan triggers
      --diff-file diffs/triggers_diff.json
      --output plans/triggers_plan.json
  
  - name: Apply changes
    command: codex zendesk apply triggers
      plans/triggers_plan.json
      --env=dev
  
  - name: Verify
    command: codex zendesk snapshot --env=dev
```text

Execute with:
```bash
codex-task-sequence --sequence scripts/task_sequences/update_triggers.yaml
```text

## Configuration Examples

### Example 1: Triggers

**Auto-notify on critical tickets**:

```json
{
  "title": "Notify on-call for critical issues",
  "active": true,
  "conditions": {
    "all": [
      {
        "field": "priority",
        "operator": "is",
        "value": "urgent"
      },
      {
        "field": "type",
        "operator": "is",
        "value": "incident"
      }
    ]
  },
  "actions": [
    {
      "field": "notification_webhook",
      "value": ["oncall_webhook_id"]
    }
  ]
}
```text

### Example 2: Views

**Tier 1 agent queue**:

```json
{
  "title": "Tier 1 Queue - Unassigned",
  "active": true,
  "conditions": {
    "all": [
      {
        "field": "status",
        "operator": "less_than",
        "value": "solved"
      },
      {
        "field": "assignee_id",
        "operator": "is",
        "value": "null"
      },
      {
        "field": "group_id",
        "operator": "is",
        "value": "TIER_1_GROUP_ID"
      }
    ],
    "any": []
  },
  "execution": {
    "group_by": "priority",
    "sort_by": "created_at",
    "sort_order": "asc"
  }
}
```text

### Example 3: Macros

**Close with resolution**:

```json
{
  "title": "Resolved - Thank you",
  "active": true,
  "actions": [
    {
      "field": "status",
      "value": "solved"
    },
    {
      "field": "comment_value",
      "value": "Thank you for contacting support. This issue has been resolved. Please don't hesitate to reach out if you have any other questions."
    },
    {
      "field": "comment_mode_is_public",
      "value": true
    }
  ]
}
```text

### Example 4: Ticket Fields

**Custom product field**:

```json
{
  "type": "tagger",
  "title": "Product",
  "description": "Which product is this ticket about?",
  "custom_field_options": [
    {"name": "Product A", "value": "product_a"},
    {"name": "Product B", "value": "product_b"},
    {"name": "Product C", "value": "product_c"}
  ],
  "required_in_portal": false,
  "visible_in_portal": true,
  "editable_in_portal": true,
  "required": false,
  "tag": "product"
}
```text

### Example 5: Webhooks

**Incident escalation webhook**:

```json
{
  "name": "PagerDuty Incident Webhook",
  "endpoint": "https://events.pagerduty.com/v2/enqueue",
  "http_method": "POST",
  "request_format": "json",
  "status": "active",
  "custom_headers": {
    "Authorization": "ENV:PAGERDUTY_TOKEN",
    "Content-Type": "application/json"
  }
}
```text

**Note**: Use `ENV:` prefix for sensitive values stored in environment variables.

## Common Tasks

### Task 1: Add a New Trigger

1. **Get current triggers**:
   ```bash
   codex zendesk snapshot --env=dev --objects triggers
   ```

2. **Edit desired state**:
   ```bash
   # Add new trigger to configs/desired/zendesk/triggers.json
   ```

3. **Preview changes**:
   ```bash
   codex zendesk diff triggers \
     --desired-file configs/desired/zendesk/triggers.json \
     --current-file snapshot/dev/latest/triggers.json \
     --output diffs/triggers_diff.json
   
   # Review the diff
   cat diffs/triggers_diff.json | jq
   ```

4. **Apply**:
   ```bash
   codex zendesk plan triggers --diff-file diffs/triggers_diff.json --output plans/triggers_plan.json
   codex zendesk apply triggers plans/triggers_plan.json --env=dev
   ```

### Task 2: Update Multiple Macros

1. **Snapshot**:
   ```bash
   codex zendesk snapshot --env=dev --objects macros
   ```

2. **Bulk edit** `configs/desired/zendesk/macros.json`

3. **Validate syntax**:
   ```bash
   cat configs/desired/zendesk/macros.json | jq . > /dev/null
   ```

4. **Diff and apply**:
   ```bash
   codex zendesk diff macros \
     --desired-file configs/desired/zendesk/macros.json \
     --current-file snapshot/dev/latest/macros.json \
     --output diffs/macros_diff.json
   
   codex zendesk plan macros --diff-file diffs/macros_diff.json --output plans/macros_plan.json
   codex zendesk apply macros plans/macros_plan.json --env=dev
   ```

### Task 3: Promote Configuration from Dev to Prod

1. **Test in dev**:
   ```bash
   # Apply and verify in dev first
   codex zendesk apply triggers plans/triggers_plan.json --env=dev
   codex zendesk metrics
   ```

2. **Snapshot prod**:
   ```bash
   codex zendesk snapshot --env=prod
   ```

3. **Generate prod plan**:
   ```bash
   codex zendesk diff triggers \
     --desired-file configs/desired/zendesk/triggers.json \
     --current-file snapshot/prod/latest/triggers.json \
     --output diffs/triggers_prod_diff.json
   
   codex zendesk plan triggers \
     --diff-file diffs/triggers_prod_diff.json \
     --output plans/triggers_prod_plan.json
   ```

4. **Review and apply to prod**:
   ```bash
   # Careful review!
   cat plans/triggers_prod_plan.json | jq
   
   # Dry run
   codex zendesk apply triggers plans/triggers_prod_plan.json --env=prod --dry-run
   
   # Apply
   codex zendesk apply triggers plans/triggers_prod_plan.json --env=prod
   ```

### Task 4: Rollback Changes

1. **Use previous snapshot**:
   ```bash
   # List available snapshots
   ls -la snapshot/dev/
   
   # Use older snapshot as "desired" state
   codex zendesk diff triggers \
     --desired-file snapshot/dev/2024-01-15_10-30-00/triggers.json \
     --current-file snapshot/dev/latest/triggers.json \
     --output diffs/rollback_diff.json
   ```

2. **Generate rollback plan**:
   ```bash
   codex zendesk plan triggers \
     --diff-file diffs/rollback_diff.json \
     --output plans/rollback_plan.json
   ```

3. **Apply rollback**:
   ```bash
   codex zendesk apply triggers plans/rollback_plan.json --env=dev
   ```

### Task 5: Bulk Import Macros

1. **Prepare CSV or JSON** with macro definitions

2. **Convert to desired state format**:
   ```python
   import json
   import csv
   
   macros = []
   with open('macros.csv', 'r') as f:
       reader = csv.DictReader(f)
       for row in reader:
           macros.append({
               "title": row['title'],
               "active": True,
               "actions": [
                   {"field": "status", "value": row['status']},
                   {"field": "comment_value", "value": row['comment']}
               ]
           })
   
   with open('configs/desired/zendesk/macros.json', 'w') as f:
       json.dump({"macros": macros}, f, indent=2)
   ```

3. **Apply standard workflow**:
   ```bash
   codex zendesk snapshot --env=dev --objects macros
   codex zendesk diff macros \
     --desired-file configs/desired/zendesk/macros.json \
     --current-file snapshot/dev/latest/macros.json \
     --output diffs/macros_diff.json
   codex zendesk plan macros --diff-file diffs/macros_diff.json --output plans/macros_plan.json
   codex zendesk apply macros plans/macros_plan.json --env=dev
   ```

## Monitoring and Metrics

### Available Metrics

The `codex zendesk metrics` command provides:

- **Apply success rate**: Percentage of successful applies
- **Rate limit behavior**: Retry counts, backoff times
- **Diff sizes**: Number of changes per operation
- **Operation timing**: Duration of snapshots, diffs, applies
- **Error rates**: Failed operations by type

### Viewing Metrics

```bash
# All metrics
codex zendesk metrics

# Specific time range
codex zendesk metrics --since 2024-01-01 --until 2024-01-31

# Export to JSON
codex zendesk metrics --format json > metrics.json
```text

### Integration with Monitoring Systems

Export metrics to Prometheus/Grafana:

```python
# In your monitoring setup
from codex.zendesk.monitoring.zendesk_metrics import ZendeskMetrics

metrics = ZendeskMetrics()
prometheus_metrics = metrics.export_prometheus()
```text

### Key Metrics to Monitor

| Metric | Target | Action if Below Target |
|--------|--------|----------------------|
| Apply success rate | > 95% | Investigate failures, review plans |
| Rate limit retries | < 5% | Reduce request frequency |
| Diff validation | 100% | Fix JSON syntax errors |
| Snapshot freshness | < 24h | Automate daily snapshots |

## Troubleshooting

### Common Issues

#### Issue 1: API Rate Limiting

**Symptoms**: `429 Too Many Requests` errors

**Solution**:
```bash
# Configure rate limiting
export ZENDESK_RATE_LIMIT_DELAY=1.5  # seconds between requests
export ZENDESK_MAX_RETRIES=5

# Apply with rate limiting
codex zendesk apply triggers plans/triggers_plan.json --env=dev --rate-limit
```text

#### Issue 2: Invalid Desired State JSON

**Symptoms**: JSON parsing errors, validation failures

**Solution**:
```bash
# Validate JSON syntax
jq . configs/desired/zendesk/triggers.json

# Validate against schema (if available)
python tools/schema_validate.py \
  --data configs/desired/zendesk/triggers.json \
  --schema schemas/zendesk_triggers.schema.json
```text

#### Issue 3: Missing Group/Schedule IDs

**Symptoms**: References to `GROUP_ID` or `SCHEDULE_ID` not resolved

**Solution**:
```bash
# List available groups
codex zendesk list-groups --env=dev

# List available schedules
codex zendesk list-schedules --env=dev

# Replace placeholders with actual IDs
sed -i 's/TIER_1_GROUP_ID/123456789/g' configs/desired/zendesk/triggers.json
```text

#### Issue 4: Diff Shows Unexpected Changes

**Symptoms**: Diff includes changes you didn't make

**Solution**:
```bash
# Take fresh snapshot
codex zendesk snapshot --env=dev --force

# Compare snapshots
diff snapshot/dev/<old>/triggers.json snapshot/dev/latest/triggers.json

# Verify desired state matches intent
cat configs/desired/zendesk/triggers.json | jq
```text

#### Issue 5: Apply Fails Partway Through

**Symptoms**: Some objects updated, others failed

**Solution**:
```bash
# Check apply logs
cat .codex/logs/zendesk_apply_<timestamp>.log

# Take new snapshot to see current state
codex zendesk snapshot --env=dev

# Generate new diff from current state
codex zendesk diff triggers \
  --desired-file configs/desired/zendesk/triggers.json \
  --current-file snapshot/dev/latest/triggers.json \
  --output diffs/triggers_recovery_diff.json

# Apply remaining changes
codex zendesk plan triggers --diff-file diffs/triggers_recovery_diff.json --output plans/recovery_plan.json
codex zendesk apply triggers plans/recovery_plan.json --env=dev
```text

### Debug Mode

Enable verbose logging:

```bash
export CODEX_LOG_LEVEL=DEBUG
codex zendesk apply triggers plans/triggers_plan.json --env=dev --verbose
```text

### Getting Help

1. **Check logs**: `.codex/logs/zendesk_*.log`
2. **Review documentation**: [docs/runbooks/zendesk_admin_workflow.md](../runbooks/zendesk_admin_workflow.md)
3. **Zendesk API docs**: Consult [docs/zendesk_api_reference.md](../zendesk_api_reference.md)
4. **Community support**: Open an issue or discussion

## Best Practices

### 1. Environment Isolation

- **Always test in dev first**
- **Use separate credentials** for each environment
- **Never apply untested plans to prod**

### 2. Version Control

```bash
# Commit desired state changes
git add configs/desired/zendesk/
git commit -m "Add high-priority auto-assignment trigger"

# Tag releases
git tag -a zendesk-release-v1.2.0 -m "Add new support workflows"
```text

### 3. Code Review

- **Require PR reviews** for all desired state changes
- **Include diffs** in PR descriptions
- **Test in dev** before merging

### 4. Documentation

- **Document why** changes are made (in commit messages)
- **Keep examples** up to date
- **Maintain runbooks** for common workflows

### 5. Snapshot Retention

```bash
# Keep snapshots for 30 days minimum
# Archive important snapshots
mkdir -p archive/snapshots/prod
cp -r snapshot/prod/<timestamp>/ archive/snapshots/prod/release-v1.0/
```text

### 6. Secrets Management

- **Never commit API tokens** to Git
- **Use environment variables** or secret managers
- **Use ENV: prefix** in webhook configurations
- **Rotate tokens** regularly

### 7. Change Management

| Change Size | Approval Required | Testing |
|------------|------------------|---------|
| Single trigger/view | Peer review | Dev environment |
| Multiple objects | Team lead | Dev + staging |
| Bulk changes | Manager | Full UAT cycle |
| Production | Change board | All environments |

### 8. Monitoring

- **Set up alerts** for apply failures
- **Monitor metrics** per commit cycle
- **Review logs** after major changes
- **Track ticket impact** after trigger changes

## Advanced Topics

### Custom Workflows

Build complex workflows with task sequences:

```yaml
# scripts/task_sequences/monthly_config_update.yaml
name: Monthly Configuration Update
tasks:
  - name: Snapshot all environments
    parallel:
      - codex zendesk snapshot --env=dev
      - codex zendesk snapshot --env=staging
      - codex zendesk snapshot --env=prod
  
  - name: Update triggers
    sequence:
      - codex zendesk diff triggers --desired-file configs/desired/zendesk/triggers.json --current-file snapshot/dev/latest/triggers.json --output diffs/triggers_diff.json
      - codex zendesk plan triggers --diff-file diffs/triggers_diff.json --output plans/triggers_plan.json
      - codex zendesk apply triggers plans/triggers_plan.json --env=dev
  
  - name: Verify changes
    command: codex zendesk metrics --since today
```text

### Integration with CI/CD

While _codex_ is designed for local-first workflows, you can integrate with CI/CD:

```yaml
# .github/workflows/zendesk-deploy.yml (example only, not active)
name: Deploy Zendesk Config
on:
  push:
    branches: [main]
    paths:
      - 'configs/desired/zendesk/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install codex
        run: pip install -e .
      - name: Deploy to staging
        env:
          ZENDESK_API_TOKEN: ${{ secrets.ZENDESK_STAGING_TOKEN }}
        run: |
          codex zendesk snapshot --env=staging
          codex zendesk diff triggers --desired-file configs/desired/zendesk/triggers.json --current-file snapshot/staging/latest/triggers.json --output diffs/triggers_diff.json
          codex zendesk plan triggers --diff-file diffs/triggers_diff.json --output plans/triggers_plan.json
          codex zendesk apply triggers plans/triggers_plan.json --env=staging
```text

### ML-Assisted Configuration

Optionally use ML to suggest optimizations:

```bash
# Train macro suggestion model
codex-train \
  data.train_path=data/zendesk_tickets.jsonl \
  data.task=macro_suggestion \
  training.output_dir=artifacts/zendesk_macro_model

# Generate macro suggestions
codex-infer \
  --model artifacts/zendesk_macro_model \
  --input data/recent_tickets.jsonl \
  --output suggestions/macros.json
```text

See [docs/runbooks/zendesk_e2e_support_workflows_plan.md](../runbooks/zendesk_e2e_support_workflows_plan.md) for ML integration details.

### Webhook Testing

Test webhooks locally before deploying:

```bash
# Start local webhook receiver
python scripts/webhook_test_server.py --port 8080

# Configure ngrok or similar for public URL
ngrok http 8080

# Update webhook in desired state with ngrok URL
# Apply and test
codex zendesk apply webhooks plans/webhooks_plan.json --env=dev

# Trigger a test ticket to fire webhook
# Check webhook receiver logs
```text

### Bulk Operations

For large-scale changes, use batch processing:

```python
# scripts/bulk_update_triggers.py
import json
from pathlib import Path

def update_all_triggers(desired_file, update_fn):
    """Apply update function to all triggers."""
    with open(desired_file) as f:
        config = json.load(f)
    
    for trigger in config.get('triggers', []):
        update_fn(trigger)
    
    with open(desired_file, 'w') as f:
        json.dump(config, f, indent=2)

def add_tag_action(trigger):
    """Add tag action to all triggers."""
    if 'actions' not in trigger:
        trigger['actions'] = []
    trigger['actions'].append({
        'field': 'current_tags',
        'value': 'automated_trigger'
    })

update_all_triggers('configs/desired/zendesk/triggers.json', add_tag_action)
```text

## Next Steps

### Learning Path

1. **Pre-commit 1-2**: Complete first snapshot-diff-plan-apply cycle
2. **Pre-commit 3-4**: Manage triggers and views for a small team
3. **Pre-commit 5-6**: Set up multi-environment workflow
4. **Pre-commit 7-8**: Implement monitoring and alerting
5. **Month 2+**: Advanced topics (ML, automation, custom workflows)

### Resources

- [Zendesk Admin Workflow Runbook](../runbooks/zendesk_admin_workflow.md)
- [End-to-End Support Workflows Plan](../runbooks/zendesk_e2e_support_workflows_plan.md)
- [Zendesk First Cycle Verification Checklist](../checklists/zendesk_first_cycle_verification.md)
- [Zendesk API Reference](../zendesk_api_reference.md)
- [Zendesk API Catalog](../zendesk_api_catalog_generated.md)

### Community

- **Discussions**: Share workflows and ask questions
- **Issues**: Report bugs or request features
- **Examples**: Contribute your configurations to `examples/zendesk/`

---

**You're now ready to manage Zendesk Support as code!** Start with a simple trigger or view, and gradually expand to more complex workflows. Remember to test thoroughly in dev before promoting to production.

Happy automating! 🎫
