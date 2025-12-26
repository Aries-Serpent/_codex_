# Autonomous Agent - README (template)

Generated: 2025-12-26T07:54:45Z | Author: mbaetiong

## Quick Start - Human Admin Instructions

This file documents the manual steps required to enable the agent at Genesis.

### Prerequisites

Before starting, ensure you have:
- Repository admin access to `Aries-Serpent/_codex_`
- GitHub Copilot Pro+ subscription
- Access to create Personal Access Tokens
- Access to repository Secrets and Variables settings

### Step-by-Step Guide

#### 1. Create CODEX_MASTER_KEY Secret

Navigate to: https://github.com/settings/personal-access-tokens/new

Create a Fine-grained Personal Access Token with:
- **Name**: `CODEX_MASTER_KEY_Aries-Serpent`
- **Expiration**: 90 days
- **Resource**: `Aries-Serpent/_codex_`  (only)
- **Permissions**: Actions (RW), Administration (RW), Contents (RW), Pull Requests (RW), Workflows (W), and others as documented

Then inject at: https://github.com/Aries-Serpent/_codex_/settings/secrets/actions

#### 2. Review Configuration Files

Review these critical files:
- `.codex/autonomous_agent.yaml` - Agent configuration with safe defaults
- `.codex/guardrails.md` - Operational policies and constraints

Verify:
- `autonomous_actions_enabled: false` (should be false initially)
- Placeholder comments are clear (`<<HUMAN:` markers)
- Policy requirements align with organization standards

#### 3. Enable Genesis Bootstrap Workflow

Edit `.github/workflows/genesis-bootstrap.yml`:
- Find line: `if: false # <<< HUMAN: remove this guard...`
- Remove or comment: `# if: false # Guard removed by mbaetiong on 2025-12-26`
- Commit: `chore(genesis): enable bootstrap workflow`

#### 4. Execute Workflow

Navigate to: https://github.com/Aries-Serpent/_codex_/actions/workflows/genesis-bootstrap.yml

Click "Run workflow" and configure:
- **genesis_validation**: ✅ true
- **human_admin**: `mbaetiong`

Monitor execution (should complete in 1-2 minutes).

#### 5. Validate Results

After successful workflow run:
- Download artifact: `genesis-validation-report`
- Review `.codex/genesis_validation.json`
- Check `.codex/change_log.md` for Genesis entry
- Verify no errors in workflow logs

#### 6. Enable Autonomous Operations

Only after validation succeeds:

1. Edit `.codex/autonomous_agent.yaml`:
   - Change: `autonomous_actions_enabled: false` → `autonomous_actions_enabled: true`

2. Edit `scripts/autonomous_agent.py`:
   - Change: `SAFE_MODE = True` → `SAFE_MODE = False`

3. Commit changes:
   ```bash
   git add .codex/autonomous_agent.yaml scripts/autonomous_agent.py
   git commit -m "chore(genesis): enable autonomous operations"
   git push
   ```

### Verification

Run the autonomous agent locally to verify:

```bash
cd /path/to/_codex_
python scripts/autonomous_agent.py
```

Expected output: Status summary showing all checks passed.

### Troubleshooting

**Workflow fails with "Missing secrets"**
- Solution: Verify CODEX_MASTER_KEY is present in repository secrets
- Check: Settings → Secrets and variables → Actions

**PAT permissions insufficient**
- Solution: Regenerate PAT with all required permissions
- Reference: docs/admin/GENESIS_SETUP_GUIDE.md Step 0.1

**Genesis validation fails**
- Solution: Ensure all required files exist
- Run: `python scripts/autonomous_agent.py` to check local validation

### Security Reminders

- ✅ Never commit secrets to repository
- ✅ Store PAT securely in password manager
- ✅ Set calendar reminder for token rotation (90 days)
- ✅ Review audit logs regularly (`.codex/action_log.ndjson`)

### Detailed Documentation

For comprehensive instructions, see:
- **Admin Guide**: [docs/admin/GENESIS_SETUP_GUIDE.md](docs/admin/GENESIS_SETUP_GUIDE.md)
- **Agent Guidelines**: [docs/agent/OPERATIONAL_GUIDELINES.md](docs/agent/OPERATIONAL_GUIDELINES.md)
- **Guardrails**: [.codex/guardrails.md](.codex/guardrails.md)

### Support

For issues or questions:
- **Critical**: Contact @mbaetiong immediately
- **General**: Create issue in repository
- **Documentation**: Open discussion thread

---

**Last Updated**: 2025-12-26T07:54:45Z  
**Version**: 1.0.0-template  
**Status**: Pre-Genesis (awaiting human setup)
