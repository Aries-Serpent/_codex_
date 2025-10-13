# Zendesk Admin Runbook (Codex CRM)

Use the unified CLI to generate Zendesk assets offline:

```bash
python -m codex_crm.cli apply-zd --out ./config/zd
```

The command produces JSON scaffolds for forms, triggers, and SLA policies based
on the canonical data model. Review the generated files, adjust IDs to match
local instances if required, and import them via the Zendesk Admin Center.
