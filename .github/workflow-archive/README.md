# Workflow Archive

This directory contains workflow management metadata, backups, and consolidation records.

## 🔐 Security Considerations

### WORKFLOW_INVENTORY.yaml

**Contains**: Tokenized secret names (SHA256 hashes + base64 encoding)

**Purpose**: Internal tooling use only - enables automated workflow analysis and consolidation

**Security Implementation**:
- Secret **names** are tokenized using SHA256 hashing
- Names are also base64-encoded for reversible obfuscation
- Only hints are exposed (e.g., "GIT***(12 chars)")
- Secret **values** are NEVER stored or logged
- This file should be treated as internal documentation

**Tokenization Format**:
```yaml
secrets_used:
  - token: "5d41402abc4b2a76b9719d911017c592..."  # SHA256 hash
    encoded: "R0lUSFVCX1RPS0VO"                    # Base64 encoded name
    hint: "GIT***(12 chars)"                       # Redacted preview
```

**Security Benefits**:
1. **No plain-text exposure**: Secret names never appear in clear text
2. **Reversible with authorization**: Base64 allows decoding for authorized tools
3. **Pattern matching**: SHA256 tokens enable duplicate detection
4. **Audit trail**: Hints provide human-readable context without full exposure

### Decoding Secret Names (Authorized Use Only)

Use `scripts/decode_workflow_secrets.py` for authorized secret name decoding:

```bash
# List tokens and hints (safe, no decoding)
python scripts/decode_workflow_secrets.py --list-tokens

# Decode single secret (authorized contexts only)
python scripts/decode_workflow_secrets.py --encoded "R0lUSFVCX1RPS0VO"

# Generate full report (requires explicit authorization)
python scripts/decode_workflow_secrets.py --report --authorized
```

**WARNING**: The `--report --authorized` command decodes all secret names. Only use in:
- Security audits
- Authorized tooling contexts
- Never in public logs or dashboards

### Best Practices

1. **Never log secret names**: Print statements and logs should not expose secret names or tokens
2. **Limit exposure**: Markdown reports (like INVENTORY_SUMMARY.md) omit all secret information
3. **Access control**: Only authorized tooling should parse WORKFLOW_INVENTORY.yaml
4. **Use tokenization**: Always use tokenized format when storing secret references
5. **Rotation**: Rotate secrets if decoded names are accidentally exposed in public contexts
6. **Authorized decoding only**: Use `decode_workflow_secrets.py` with explicit authorization flag

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

- `scripts/catalog_workflows.py` - Generate workflow inventory with tokenized secrets
- `scripts/decode_workflow_secrets.py` - Decode tokenized secrets (authorized use only)
- `scripts/consolidate_workflows.py` - Execute consolidation phases
- `scripts/backup_workflows.sh` - Create workflow backups
- `.github/workflows/workflow-restore.yml` - Self-service restoration

## Security Incident Response

If secret names (decoded or tokenized) are accidentally exposed in logs or public dashboards:

1. **Assess exposure**: Determine what secret names/tokens were disclosed
2. **Check if decoded**: If base64-encoded names were exposed, assess decoding risk
3. **Rotate secrets**: Rotate any secrets that could be targeted (high-priority first)
4. **Update tooling**: Add safeguards to prevent future exposure
5. **Document**: Create incident report in `.codex/security-incidents/`
6. **Notify**: Alert security team if high-value secrets were exposed
7. **Review access**: Audit who has access to `decode_workflow_secrets.py`

**Priority Rotation Order**:
1. API keys and tokens (OPENAI_API_KEY, external services)
2. Database credentials
3. Signing keys
4. GITHUB_TOKEN (if using PAT instead of workflow token)

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2025-12-28 | Added tokenization (SHA256 + base64) for secret names | @copilot |
| 2025-12-28 | Created decode_workflow_secrets.py for authorized decoding | @copilot |
| 2025-12-28 | Created README with security documentation | @copilot |
| 2025-12-28 | Removed secret exposure from INVENTORY_SUMMARY.md | @copilot |
