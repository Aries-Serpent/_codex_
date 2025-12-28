# Workflow Archive

This directory contains workflow management metadata, backups, and consolidation records.

## 🔐 Security Considerations

### WORKFLOW_INVENTORY.yaml

**Contains**: Secret names (NOT values) extracted from workflow files

**Purpose**: Internal tooling use only - enables automated workflow analysis and consolidation

**Security Notes**:
- Secret **names** are stored (e.g., `GITHUB_TOKEN`, `OPENAI_API_KEY`)
- Secret **values** are NEVER stored or logged
- This file should be treated as internal documentation
- Do not expose secret names in public dashboards or external systems
- Secret names could aid in social engineering attacks

### Best Practices

1. **Never log secret names**: Print statements and logs should not expose secret names
2. **Limit exposure**: Markdown reports (like INVENTORY_SUMMARY.md) omit secret information
3. **Access control**: Only authorized tooling should parse WORKFLOW_INVENTORY.yaml
4. **Rotation**: Rotate secrets if secret names are accidentally exposed in public contexts

## Directory Structure

```
workflow-archive/
├── README.md                      # This file (security documentation)
├── WORKFLOW_INVENTORY.yaml        # Internal metadata (contains secret names)
├── INVENTORY_SUMMARY.md           # Human-readable report (secrets omitted)
├── CONSOLIDATION_REPORT.md        # Consolidation status report
├── PARITY_CHECKLIST.md            # Feature parity validation
├── backups/                       # Timestamped workflow backups
│   └── YYYY-MM-DD/               # Daily backup snapshots
│       ├── *.yml                 # Workflow backup files
│       └── MANIFEST.txt          # SHA256 checksums
└── disabled/                      # Disabled workflow archive
    ├── *.yml                     # Disabled workflow files
    └── *.yml.meta                # Metadata about disablement
```

## Usage

### For Humans
- Read: `INVENTORY_SUMMARY.md`, `CONSOLIDATION_REPORT.md`, `PARITY_CHECKLIST.md`
- Avoid: Direct inspection of `WORKFLOW_INVENTORY.yaml` (use tooling instead)

### For Automation
- Parse: `WORKFLOW_INVENTORY.yaml` (via `scripts/catalog_workflows.py`)
- Process: Consolidation planning, backup management, restoration
- Output: Filtered reports that omit sensitive information

## Related Scripts

- `scripts/catalog_workflows.py` - Generate workflow inventory
- `scripts/consolidate_workflows.py` - Execute consolidation phases
- `scripts/backup_workflows.sh` - Create workflow backups
- `.github/workflows/workflow-restore.yml` - Self-service restoration

## Security Incident Response

If secret names are accidentally exposed in logs or public dashboards:

1. **Assess exposure**: Determine what secret names were disclosed
2. **Rotate secrets**: Rotate any secrets that could be targeted
3. **Update tooling**: Add safeguards to prevent future exposure
4. **Document**: Create incident report in `.codex/security-incidents/`
5. **Notify**: Alert security team if high-value secrets were exposed

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2025-12-28 | Created README with security documentation | @copilot |
| 2025-12-28 | Removed secret exposure from INVENTORY_SUMMARY.md | @copilot |
