# Zendesk Examples

This directory contains example configurations, scripts, and templates for Zendesk administration with _codex_.

## Quick Start

Run the interactive setup script:

```bash
./quickstart.sh
```text

This will:
1. Check prerequisites (_codex_ installation, credentials)
2. Create directory structure
3. Test API connectivity
4. Take initial snapshot
5. Create sample configuration files
6. Show next steps

## Example Files

### Sample Configurations

Located in `../../configs/desired/zendesk/` after running quickstart:

- **triggers.sample.json** - Example auto-assignment trigger
- **macros.sample.json** - Example resolution macro
- **views.sample.json** - Example agent queue view
- **webhooks.sample.json** - Example PagerDuty integration

### Role Examples

See `zendesk_roles.example.json` for Zendesk role configurations.

## Scripts

### quickstart.sh

Interactive setup script for first-time Zendesk configuration management.

**Usage**:
```bash
./quickstart.sh
```text

**Features**:
- Guided credential setup
- Environment selection (dev/staging/prod)
- Directory structure creation
- API connectivity test
- Initial snapshot
- Sample configuration generation

### Task Sequences

Located in `../../scripts/task_sequences/`:

- **zendesk_first_cycle.yaml** - Complete first workflow cycle
- Custom sequences can be created following this template

## Configuration Templates

### Trigger Template

```json
{
  "title": "Trigger Name",
  "active": true,
  "position": 1,
  "conditions": {
    "all": [
      {
        "field": "status",
        "operator": "is",
        "value": "new"
      }
    ]
  },
  "actions": [
    {
      "field": "status",
      "value": "open"
    }
  ],
  "description": "Description of what this trigger does"
}
```text

### Macro Template

```json
{
  "title": "Macro Name",
  "active": true,
  "actions": [
    {
      "field": "status",
      "value": "solved"
    },
    {
      "field": "comment_value",
      "value": "Response text"
    },
    {
      "field": "comment_mode_is_public",
      "value": true
    }
  ],
  "description": "Description of macro purpose"
}
```text

### View Template

```json
{
  "title": "View Name",
  "active": true,
  "conditions": {
    "all": [
      {
        "field": "status",
        "operator": "less_than",
        "value": "solved"
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

### Webhook Template

```json
{
  "name": "Webhook Name",
  "endpoint": "https://api.service.com/webhook",
  "http_method": "POST",
  "request_format": "json",
  "status": "active",
  "custom_headers": {
    "Authorization": "ENV:WEBHOOK_TOKEN",
    "Content-Type": "application/json"
  }
}
```text

## Common Use Cases

### 1. Auto-Assignment by Priority

**Trigger**:
```json
{
  "title": "Auto-assign high priority to Tier 2",
  "conditions": {
    "all": [
      {"field": "status", "operator": "is", "value": "new"},
      {"field": "priority", "operator": "is", "value": "high"}
    ]
  },
  "actions": [
    {"field": "group_id", "value": "TIER_2_GROUP_ID"},
    {"field": "status", "value": "open"}
  ]
}
```text

### 2. Incident Escalation

**Webhook + Trigger**:
```json
{
  "webhook": {
    "name": "PagerDuty Escalation",
    "endpoint": "https://events.pagerduty.com/v2/enqueue",
    "custom_headers": {
      "Authorization": "ENV:PAGERDUTY_TOKEN"
    }
  },
  "trigger": {
    "title": "Escalate urgent incidents",
    "conditions": {
      "all": [
        {"field": "priority", "operator": "is", "value": "urgent"},
        {"field": "type", "operator": "is", "value": "incident"}
      ]
    },
    "actions": [
      {"field": "notification_webhook", "value": ["pagerduty_webhook_id"]}
    ]
  }
}
```text

### 3. Agent Queue View

**View**:
```json
{
  "title": "My Open Tickets",
  "conditions": {
    "all": [
      {"field": "status", "operator": "less_than", "value": "solved"},
      {"field": "assignee_id", "operator": "is", "value": "current_user"}
    ]
  },
  "execution": {
    "group_by": "priority",
    "sort_by": "updated_at",
    "sort_order": "desc"
  }
}
```text

### 4. Standard Resolution Macros

**Macros**:
```json
{
  "macros": [
    {
      "title": "[Support] Issue Resolved",
      "actions": [
        {"field": "status", "value": "solved"},
        {"field": "comment_value", "value": "Your issue has been resolved. Thank you!"},
        {"field": "comment_mode_is_public", "value": true}
      ]
    },
    {
      "title": "[Support] Need More Info",
      "actions": [
        {"field": "status", "value": "pending"},
        {"field": "comment_value", "value": "We need additional information to proceed."},
        {"field": "comment_mode_is_public", "value": true}
      ]
    }
  ]
}
```text

## Testing Your Configurations

### 1. Validate JSON Syntax

```bash
jq . configs/desired/zendesk/triggers.json
```text

### 2. Generate Diff

```bash
codex zendesk diff triggers \
  --desired-file configs/desired/zendesk/triggers.json \
  --current-file snapshot/dev/latest/triggers.json \
  --output diffs/triggers_diff.json
```text

### 3. Review Diff

```bash
cat diffs/triggers_diff.json | jq
```text

### 4. Dry Run

```bash
codex zendesk apply triggers plans/triggers_plan.json \
  --env=dev --dry-run
```text

## Best Practices

1. **Start Small**: Begin with 1-2 triggers or macros
2. **Test in Dev**: Always test in development environment first
3. **Version Control**: Commit desired state changes to Git
4. **Document Why**: Include descriptions explaining purpose
5. **Use ENV: Prefix**: For sensitive values in webhooks
6. **Follow Naming**: Use consistent naming conventions

## Naming Conventions

### Triggers
- Format: `[Category] Action`
- Examples:
  - `[Auto-assign] High Priority to Tier 2`
  - `[Notify] Escalate Urgent Incidents`
  - `[Tag] Mark Product Tickets`

### Macros
- Format: `[Department] Action`
- Examples:
  - `[Support] Issue Resolved`
  - `[Billing] Refund Processed`
  - `[Technical] Escalate to Engineering`

### Views
- Format: `Team/Agent - Description`
- Examples:
  - `Tier 1 - Unassigned Queue`
  - `My - Open Tickets`
  - `Manager - Team Overview`

## Resources

- **[../docs/zendesk/ZENDESK_NEWCOMER_GUIDE.md](../../docs/zendesk/ZENDESK_NEWCOMER_GUIDE.md)** - Complete guide
- **[../docs/zendesk/WORKFLOW_DIAGRAMS.md](../../docs/zendesk/WORKFLOW_DIAGRAMS.md)** - Visual workflows
- **[../docs/zendesk/AI_AGENT_APP_BUILDER.md](../../docs/zendesk/AI_AGENT_APP_BUILDER.md)** - AI App Builder guide
- **[../docs/runbooks/zendesk_admin_workflow.md](../../docs/runbooks/zendesk_admin_workflow.md)** - Admin runbook

## Contributing

To contribute new examples:

1. Test configuration in dev environment
2. Sanitize sensitive data (use placeholders)
3. Add clear descriptions and comments
4. Include use case explanation
5. Submit PR with example

---

**Ready to get started? Run `./quickstart.sh` now!** 🚀
