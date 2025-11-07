# Zendesk Support Administration Documentation

This directory contains all documentation related to managing Zendesk Support with _codex_.

## Start Here

**New to Zendesk workflows with _codex_?** Begin with:

👉 **[ZENDESK_NEWCOMER_GUIDE.md](ZENDESK_NEWCOMER_GUIDE.md)** - Complete guide for Zendesk Support administrators

## Documentation Overview

### Quick Reference

| Document | Description | Audience |
|----------|-------------|----------|
| **[ZENDESK_NEWCOMER_GUIDE.md](ZENDESK_NEWCOMER_GUIDE.md)** | Comprehensive onboarding guide | New Zendesk admins |
| **[AI_AGENT_APP_BUILDER.md](AI_AGENT_APP_BUILDER.md)** | Mathematical model + extensive visual capability maps for AI Agent App Builder | App developers |
| **[CANONICAL_CAPABILITY_MAP.md](CANONICAL_CAPABILITY_MAP.md)** | Visual-first symbolic capability map with AI transparency notes | App developers |
| **[WORKFLOW_DIAGRAMS.md](WORKFLOW_DIAGRAMS.md)** | Visual workflow diagrams and decision trees | All users |
| **[../runbooks/zendesk_admin_workflow.md](../runbooks/zendesk_admin_workflow.md)** | Core snapshot-diff-plan-apply workflow | All users |
| **[../runbooks/zendesk_e2e_support_workflows_plan.md](../runbooks/zendesk_e2e_support_workflows_plan.md)** | End-to-end workflow planning | Support ops leads |
| **[../checklists/zendesk_first_cycle_verification.md](../checklists/zendesk_first_cycle_verification.md)** | First cycle verification checklist | First-time users |
| **[../zendesk_api_reference.md](../zendesk_api_reference.md)** | Zendesk API reference | Developers |
| **[../zendesk_api_catalog_generated.md](../zendesk_api_catalog_generated.md)** | Generated API catalog | Developers |

### Additional Resources

- **[AI_AGENT_APP_BUILDER.md](AI_AGENT_APP_BUILDER.md)** - Mathematical model & optimization framework for AI Agent App Builder
- **[CANONICAL_CAPABILITY_MAP.md](CANONICAL_CAPABILITY_MAP.md)** - Visual symbolic capability map with AI transparency appendix
- **[WORKFLOW_DIAGRAMS.md](WORKFLOW_DIAGRAMS.md)** - Visual workflow diagrams and ASCII art decision trees
- **[../runbooks/zendesk_docs_pipeline.md](../runbooks/zendesk_docs_pipeline.md)** - Documentation pipeline
- **[../guides/zendesk_ai_app_builder_limitations.md](../guides/zendesk_ai_app_builder_limitations.md)** - AI app builder limitations (legacy reference)
- **[../validation/zendesk_ai_builder_readiness_validation.md](../validation/zendesk_ai_builder_readiness_validation.md)** - AI builder readiness
- **[../crm/admin-runbooks/zendesk.md](../crm/admin-runbooks/zendesk.md)** - CRM integration runbook

## Learning Paths

### Path 1: Quick Start (2-3 hours)
1. Read [ZENDESK_NEWCOMER_GUIDE.md](ZENDESK_NEWCOMER_GUIDE.md) - Overview and concepts
2. Follow [../runbooks/zendesk_admin_workflow.md](../runbooks/zendesk_admin_workflow.md) - First workflow
3. Complete one snapshot-diff-plan-apply cycle

### Path 2: Full Onboarding (1-2 days)
1. Complete Path 1
2. Study [../runbooks/zendesk_e2e_support_workflows_plan.md](../runbooks/zendesk_e2e_support_workflows_plan.md)
3. Review configuration examples in [ZENDESK_NEWCOMER_GUIDE.md](ZENDESK_NEWCOMER_GUIDE.md)
4. Set up multi-environment workflow (dev → staging → prod)
5. Complete [../checklists/zendesk_first_cycle_verification.md](../checklists/zendesk_first_cycle_verification.md)

### Path 3: Advanced Topics (1 week)
1. Complete Path 2
2. Implement task automation with task sequences
3. Set up monitoring and metrics
4. Explore ML-assisted configuration options
5. Build custom workflows for your organization

### Path 4: AI Agent App Builder (3-5 days)
1. Review [CANONICAL_CAPABILITY_MAP.md](CANONICAL_CAPABILITY_MAP.md) - Visual capability overview
2. Study [AI_AGENT_APP_BUILDER.md](AI_AGENT_APP_BUILDER.md) - Mathematical model
3. Understand location manifold and capacity fields
4. Calculate feasibility ($\Psi_i$) for your features
5. Apply optimization framework ($\mathcal{S}$)
6. Build within constraints (no backend, proxy-only APIs)

## Common Tasks

### Getting Started
```bash
# 1. Configure credentials (per environment)
export ZENDESK_DEV_SUBDOMAIN=your-subdomain
export ZENDESK_DEV_EMAIL=admin@example.com
export ZENDESK_DEV_TOKEN=your-token

# 2. Take first snapshot
codex zendesk snapshot --env=dev

# 3. Explore snapshot
ls -la snapshot/dev/latest/
```

### Daily Operations
```bash
# Snapshot current state
codex zendesk snapshot --env=dev

# Generate diff
codex zendesk diff triggers \
  --desired-file configs/desired/zendesk/triggers.json \
  --current-file snapshot/dev/latest/triggers.json \
  --output diffs/triggers_diff.json

# Plan changes
codex zendesk plan triggers \
  --diff-file diffs/triggers_diff.json \
  --output plans/triggers_plan.json

# Apply changes
codex zendesk apply triggers plans/triggers_plan.json --env=dev

# Monitor metrics
codex zendesk metrics
```

### Using Task Sequences
```bash
# Execute predefined workflow
codex-task-sequence --sequence scripts/task_sequences/zendesk_first_cycle.yaml

# Create custom sequence
cat > my_workflow.yaml <<EOF
name: My Zendesk Workflow
tasks:
  - name: Snapshot
    command: codex zendesk snapshot --env=dev
  - name: Apply triggers
    command: codex zendesk apply triggers plans/triggers_plan.json --env=dev
EOF

codex-task-sequence --sequence my_workflow.yaml
```

## Configuration Examples

### Directory Structure
```text
configs/desired/zendesk/
├── triggers.json          # Automated actions
├── views.json             # Agent queues
├── macros.json            # Common responses
├── ticket_fields.json     # Custom fields
├── ticket_forms.json      # Submission forms
└── webhooks.json          # External integrations
```
### Example Files
See detailed examples in [ZENDESK_NEWCOMER_GUIDE.md](ZENDESK_NEWCOMER_GUIDE.md):

- **Triggers**: Auto-assignment, notifications, escalations
- **Views**: Agent queues, reporting views
- **Macros**: Common responses, status updates
- **Ticket Fields**: Product selectors, custom data
- **Webhooks**: PagerDuty, Slack, custom integrations

## Troubleshooting

### Quick Diagnostics
```bash
# Test API connectivity
codex zendesk snapshot --env=dev --dry-run

# Enable debug logging
export CODEX_LOG_LEVEL=DEBUG
codex zendesk snapshot --env=dev --verbose

# Check logs
cat .codex/logs/zendesk_*.log
```

### Common Issues

| Issue | Quick Fix |
|-------|-----------|
| Rate limiting | Add `--rate-limit` flag, increase delay |
| Invalid JSON | Validate with `jq .` |
| Missing IDs | Use `codex zendesk list-groups` etc. |
| Auth errors | Verify credentials in `.env` |

See [ZENDESK_NEWCOMER_GUIDE.md#troubleshooting](ZENDESK_NEWCOMER_GUIDE.md#troubleshooting) for complete guide.

## Best Practices

✅ **Always test in dev first**  
✅ **Version control all configurations**  
✅ **Review diffs before applying**  
✅ **Monitor metrics regularly**  
✅ **Keep snapshots for rollback**  
✅ **Document changes in commit messages**  
✅ **Use task sequences for repeatability**  
✅ **Never commit API tokens**  

## Supported Zendesk Objects

| Object | CRUD | Notes |
|--------|------|-------|
| Triggers | ✅ | Automated actions on ticket events |
| Views | ✅ | Saved filters for agent queues |
| Macros | ✅ | Predefined responses and actions |
| Ticket Fields | ✅ | Custom fields on tickets |
| Ticket Forms | ✅ | Different submission types |
| Groups | ✅ | Agent teams and routing |
| Webhooks | ✅ | External integrations |
| Routing | ✅ | Skills-based routing |
| Talk IVR | ⚠️ | Phone menu system (limited) |

Legend: ✅ Full support | ⚠️ Partial support | ❌ Not yet supported

## Environment Setup

### Recommended Structure
```text
my-zendesk-config/
├── .env                           # Credentials (gitignored)
├── configs/desired/zendesk/       # Desired state
├── snapshot/                      # Current state snapshots
│   ├── dev/
│   ├── staging/
│   └── prod/
├── diffs/                         # Generated diffs
├── plans/                         # Generated plans
└── scripts/task_sequences/        # Automation workflows
```
### Environment Variables
```bash
# Required (per environment; configure for each env you use)
ZENDESK_DEV_SUBDOMAIN=your-subdomain
ZENDESK_DEV_EMAIL=admin@example.com
ZENDESK_DEV_TOKEN=your-token
ZENDESK_STAGING_SUBDOMAIN=your-staging-subdomain
ZENDESK_STAGING_EMAIL=admin@example.com
ZENDESK_STAGING_TOKEN=your-staging-token
ZENDESK_PROD_SUBDOMAIN=your-prod-subdomain
ZENDESK_PROD_EMAIL=admin@example.com
ZENDESK_PROD_TOKEN=your-prod-token

# Optional
ZENDESK_RATE_LIMIT_DELAY=1.5      # Seconds between requests
ZENDESK_MAX_RETRIES=5              # Max retry attempts
CODEX_LOG_LEVEL=INFO              # DEBUG for verbose output
```

## CLI Reference

### Main Commands
```bash
# Snapshot operations
codex zendesk snapshot --env=<env> [--objects <types>] [--dry-run]

# Diff operations
codex zendesk diff <object_type> \
  --desired-file <path> \
  --current-file <path> \
  --output <path>

# Plan operations
codex zendesk plan <object_type> \
  --diff-file <path> \
  --output <path>

# Apply operations
codex zendesk apply <object_type> <plan_file> \
  --env=<env> [--dry-run] [--rate-limit]

# Utility commands
codex zendesk metrics [--since <date>] [--format <json|text>]
codex zendesk list-groups --env=<env>
codex zendesk list-schedules --env=<env>
```

### Task Sequence Automation
```bash
# Run predefined sequence
codex-task-sequence --sequence <yaml_file>

# List available sequences
ls scripts/task_sequences/zendesk_*.yaml
```

## Integration Examples

### With Version Control
```bash
# Create feature branch
git checkout -b feature/add-priority-triggers

# Make changes
vim configs/desired/zendesk/triggers.json

# Test in dev
codex zendesk apply triggers plans/triggers_plan.json --env=dev

# Commit with evidence
git add configs/desired/zendesk/triggers.json
git add diffs/triggers_diff.json plans/triggers_plan.json
git commit -m "Add priority-based auto-assignment triggers"

# Open PR for review
gh pr create --title "Add priority triggers" --body "Adds auto-assignment based on priority"
```

### With Monitoring
```bash
# Export metrics to Prometheus
codex zendesk metrics --format json | \
  python -m codex.zendesk.monitoring.prometheus_exporter

# Set up alerts
cat > alerts.yaml <<EOF
alerts:
  - name: ZendeskApplyFailure
    condition: apply_success_rate < 0.95
    action: notify_on_call
  - name: ZendeskRateLimitHigh
    condition: rate_limit_retries > 0.05
    action: notify_ops
EOF
```

## Support and Community

### Getting Help

1. **Documentation**: Start with [ZENDESK_NEWCOMER_GUIDE.md](ZENDESK_NEWCOMER_GUIDE.md)
2. **Runbooks**: Check [../runbooks/](../runbooks/)
3. **API Reference**: Consult [../zendesk_api_reference.md](../zendesk_api_reference.md)
4. **Issues**: Open an issue on GitHub
5. **Discussions**: Join community discussions

### Contributing

- Share your workflows in `examples/zendesk/`
- Contribute to documentation
- Report bugs and suggest features
- Help others in discussions

### Useful Links

- [Zendesk API Documentation](https://developer.zendesk.com/api-reference/)
- [Zendesk Developer Portal](https://developer.zendesk.com/)
- [_codex_ Repository](https://github.com/Aries-Serpent/_codex_)

---

**Ready to get started?** Head to [ZENDESK_NEWCOMER_GUIDE.md](ZENDESK_NEWCOMER_GUIDE.md) and begin your journey! 🚀
