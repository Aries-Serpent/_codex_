# Genesis Protocol

**Status:** Phase 1 Complete | Phase 2 Pending Human Action  
**Purpose:** Establish autonomous AI agent authority through secure, auditable initialization  
**Repository:** Aries-Serpent/_codex_  
**Agent:** ai_org_repo_admin (v0.0.0-template)

---

## Overview

The **Genesis Protocol** is a structured process for safely transitioning from human-only repository management to supervised autonomous AI agent operations. It establishes clear authorization levels, safety mechanisms, and audit trails before enabling any autonomous actions.

### Philosophy

> "Trust, but verify. Automate, but with guardrails."

Genesis Protocol embodies this philosophy through:
- **Explicit Authorization:** Every capability explicitly granted
- **Defense in Depth:** Multiple safety layers
- **Full Auditability:** Every action logged and reviewable
- **Human Override:** Always maintain human control

---

## Three-Phase Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     GENESIS PROTOCOL                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Phase 1: Template Creation (COMPLETE ✅)                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ • Configuration files with safe defaults           │   │
│  │ • Documentation and guidelines                      │   │
│  │ • Workflow templates (disabled by default)          │   │
│  │ • Safety guards active (3-layer protection)         │   │
│  └─────────────────────────────────────────────────────┘   │
│                          ↓                                  │
│  Phase 2: Human Activation (PENDING ⏳)                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ • Human admin reviews templates                     │   │
│  │ • Secrets injected (CODEX_MASTER_KEY, etc.)         │   │
│  │ • Workflows enabled (remove if: false guard)        │   │
│  │ • Genesis validation executed                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                          ↓                                  │
│  Phase 3: Autonomous Operations (FUTURE 🔮)               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ • Agent operates within guardrails                  │   │
│  │ • Maintenance tasks automated                       │   │
│  │ • Escalation for high-risk actions                  │   │
│  │ • Continuous audit and monitoring                   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Template Creation ✅ COMPLETE

**Objective:** Create safe, reviewed templates before any automation.

### Completed Actions

**Configuration Files:**
- ✅ `.codex/autonomous_agent.yaml` - Agent configuration with `autonomous_actions_enabled: false`
- ✅ `.codex/guardrails.md` - Operational constraints and policies
- ✅ `.codex/change_log.md` - Audit trail initialization

**Documentation:**
- ✅ `AGENTS.md` - AI agent orientation guide
- ✅ `scripts/AUTONOMOUS_AGENT_README.md` - Setup instructions
- ✅ `docs/admin/GENESIS_SETUP_GUIDE.md` - Comprehensive admin guide
- ✅ `docs/agent/OPERATIONAL_GUIDELINES.md` - Agent operational framework

**Implementation:**
- ✅ `scripts/autonomous_agent.py` - Full implementation with complete API
  - Contains AutonomousAgent, CodeHealthSensor, ActionProposer classes
  - All enums (HealthStatus, ActionType, DecisionLevel) available
  - **Dual Mode:** Functions as both development tool and test infrastructure
  - **Test Status:** 23/23 tests passing
  - **Safety:** Respects `autonomous_actions_enabled: false` configuration

**Workflow Templates:**
- ✅ `.github/workflows/genesis-bootstrap.yml` - Validation workflow (enabled: `if: true`)
- ✅ `.github/workflows/workflow-lint.yml` - YAML linting
- ✅ All workflows have `if: false` guard for safety

**Safety Mechanisms:**
1. ✅ **Workflow Guard:** `if: false` in genesis-bootstrap.yml
2. ✅ **Script Guard:** `SAFE_MODE = True` in autonomous_agent.py
3. ✅ **Config Guard:** `autonomous_actions_enabled: false`

### Validation

**How to verify Phase 1 completion:**

```bash
# Check configuration files exist
ls -la .codex/autonomous_agent.yaml
ls -la .codex/guardrails.md
ls -la .codex/change_log.md

# Verify safety guards
grep "autonomous_actions_enabled: false" .codex/autonomous_agent.yaml
grep "if: false" .github/workflows/genesis-bootstrap.yml
grep "SAFE_MODE = True" scripts/autonomous_agent.py

# Review documentation
cat AGENTS.md | head -50
cat docs/admin/GENESIS_SETUP_GUIDE.md | head -50
```

---

## Phase 2: Human Activation ⏳ PENDING

**Objective:** Human admin enables automation with proper secrets and validation.

### Required Actions (Human Admin Only)

#### Step 1: Review Templates

**What to review:**
- [ ] Read `.codex/guardrails.md` - Understand operational constraints
- [ ] Review `.codex/autonomous_agent.yaml` - Verify configuration
- [ ] Read `docs/admin/GENESIS_SETUP_GUIDE.md` - Full setup guide
- [ ] Check all workflow files in `.github/workflows/`

**Key questions to answer:**
- Do the guardrails align with organizational policies?
- Are the authorization levels appropriate?
- Is the escalation process clear?
- Are rate limits and quotas reasonable?

#### Step 2: Create Secrets

**Required secrets:**

```bash
# Navigate to GitHub Settings → Secrets and variables → Actions
# https://github.com/Aries-Serpent/_codex_/settings/secrets/actions

# 1. CODEX_MASTER_KEY (Required)
#    - Fine-grained Personal Access Token
#    - Expiration: 90 days
#    - Permissions: Actions (RW), Administration (RW), Contents (RW), 
#                   Pull Requests (RW), Workflows (W)

# 2. CODEX_WEBHOOK_SECRET (Optional but recommended)
#    - Generate with: openssl rand -hex 32
#    - Purpose: Webhook signature verification

# 3. CODEX_BACKUP_KEY (Optional)
#    - Same permissions as CODEX_MASTER_KEY
#    - Purpose: Fallback authentication
```

**Creating CODEX_MASTER_KEY:**

1. Go to https://github.com/settings/personal-access-tokens/new
2. Configure:
   - **Name:** `CODEX_MASTER_KEY_Aries-Serpent`
   - **Expiration:** 90 days
   - **Repository access:** Only `Aries-Serpent/_codex_`
   - **Permissions:**
     - Actions: Read and write
     - Administration: Read and write
     - Contents: Read and write
     - Pull requests: Read and write
     - Workflows: Write
3. Generate token
4. Copy token (only shown once!)
5. Add to repository secrets as `CODEX_MASTER_KEY`

#### Step 3: Enable Genesis Workflow

**Edit `.github/workflows/genesis-bootstrap.yml`:**

```yaml
# BEFORE:
on:
  workflow_dispatch:
    inputs:
      genesis_validation:
        description: 'Run Genesis validation'
        required: true
        type: boolean
        default: false
jobs:
  genesis-validation:
    runs-on: ubuntu-latest
    if: false  # <<< HUMAN: remove this guard after secrets are configured

# AFTER:
on:
  workflow_dispatch:
    inputs:
      genesis_validation:
        description: 'Run Genesis validation'
        required: true
        type: boolean
        default: false
jobs:
  genesis-validation:
    runs-on: ubuntu-latest
    # Guard removed by @mbaetiong on Previous Cycle-12-26 - Genesis Phase 2 activated
```

**Commit the change:**
```bash
git checkout -b genesis/phase2-activation
git add .github/workflows/genesis-bootstrap.yml
git commit -m "chore(genesis): enable genesis-bootstrap workflow"
git push origin genesis/phase2-activation
# Create PR for review
```

#### Step 4: Execute Genesis Validation

**Run the workflow:**

1. Navigate to: https://github.com/Aries-Serpent/_codex_/actions/workflows/genesis-bootstrap.yml
2. Click "Run workflow"
3. Configure inputs:
   - **genesis_validation:** `true` ✅
   - **human_admin:** `mbaetiong` (or your GitHub username)
4. Click "Run workflow" (green button)

**Expected behavior:**
- Workflow executes in 1-2 minutes
- Validates all configuration files
- Checks secret availability
- Generates validation report
- Creates artifact: `genesis-validation-report`

**On success:**
- ✅ All checks pass
- ✅ Artifact uploaded
- ✅ Change log updated
- ✅ Ready for Phase 3

**On failure:**
- ❌ Review workflow logs
- ❌ Check error messages
- ❌ Verify secrets are set correctly
- ❌ Retry after fixing issues

#### Step 5: Review Validation Results

**Download and review:**

```bash
# Download artifact from workflow run
# Artifact name: genesis-validation-report
unzip genesis-validation-report.zip

# Review validation results
cat .codex/genesis_validation.json

# Check audit trail
cat .codex/change_log.md | tail -50
```

**Validation checklist:**
- [ ] All configuration files validated
- [ ] Secrets accessible (not exposed)
- [ ] Workflow syntax correct
- [ ] Safety guards verified
- [ ] Audit trail updated

#### Step 6: Enable Autonomous Operations

**Only after successful validation:**

```bash
# Edit configuration
vim .codex/autonomous_agent.yaml

# Change line:
# FROM: autonomous_actions_enabled: false
# TO:   autonomous_actions_enabled: true

# Edit script
vim scripts/autonomous_agent.py

# Change line:
# FROM: SAFE_MODE = True
# TO:   SAFE_MODE = False

# Commit changes
git add .codex/autonomous_agent.yaml scripts/autonomous_agent.py
git commit -m "chore(genesis): enable autonomous operations (Phase 3)"
git push origin genesis/phase2-activation
```

**Review and merge PR:**
- Human admin reviews final changes
- At least one approver required
- Merge only if confident in configuration
- Monitor initial agent operations closely

---

## Phase 3: Autonomous Operations 🔮 FUTURE

**Objective:** Agent operates within defined guardrails.

### Agent Capabilities (Post-Genesis)

**Allowed Operations:**

✅ **Maintenance (Autonomous):**
- Code formatting (Black, isort)
- Dependency updates (security patches)
- Documentation updates
- Test execution and reporting

✅ **Testing (Autonomous):**
- Run test suites
- Generate coverage reports
- Create test result artifacts
- Update test documentation

✅ **Documentation (Autonomous):**
- Update README and docs
- Generate API documentation
- Create changelog entries
- Update wiki pages

**Approval Required:**

⚠️ **Optimization:**
- Performance improvements
- Code refactoring
- Algorithm changes

⚠️ **Dependency Updates:**
- Major version upgrades
- New dependencies
- Breaking changes

**Escalation Required:**

🚨 **Security:**
- Security vulnerability fixes
- Authentication changes
- Authorization modifications

🚨 **Configuration:**
- Workflow changes
- Secret management
- Repository settings

### Agent Decision Framework

```
┌─────────────────────────────────────────────┐
│          AGENT DECISION TREE                │
├─────────────────────────────────────────────┤
│                                             │
│  Task Received                              │
│       ↓                                     │
│  Risk Assessment                            │
│       ↓                                     │
│  ┌─────────┬──────────┬──────────┐         │
│  │   LOW   │  MEDIUM  │   HIGH   │         │
│  └────┬────┴────┬─────┴────┬─────┘         │
│       ↓         ↓          ↓               │
│   Execute   Create PR   Escalate           │
│   (Automated) (Wait)   (Human)             │
│       ↓         ↓          ↓               │
│   Log to    Assign    Create Issue         │
│  Audit Trail Reviewers Tag @mbaetiong      │
│       ↓         ↓          ↓               │
│  Verify &   Monitor PR  Wait for           │
│   Report     Status     Response           │
│                                             │
└─────────────────────────────────────────────┘
```

### Audit and Monitoring

**Continuous Logging:**
- All operations logged to `.codex/action_log.ndjson`
- Change audit in `.codex/change_log.md`
- Results summary in `.codex/results.md`

**Monitoring Dashboard:**
- Daily status reports
- Action success/failure rates
- Escalation frequency
- Resource usage

**Review Schedule:**
- **Daily:** Automated logs review
- **Weekly:** Human review of PRs and actions
- **Monthly:** Guardrails effectiveness assessment
- **Quarterly:** Full security audit

---

## Security Considerations

### Defense in Depth

**Multiple Protection Layers:**

1. **Configuration Layer:** `autonomous_actions_enabled` flag
2. **Code Layer:** `SAFE_MODE` in scripts
3. **Workflow Layer:** Conditional execution guards
4. **Permission Layer:** Limited PAT permissions
5. **Audit Layer:** Full operation logging

### Secret Management

**Best Practices:**
- ✅ Rotate tokens every 90 days
- ✅ Use fine-grained PATs (not classic tokens)
- ✅ Limit token scope to minimum required
- ✅ Store tokens only in GitHub Secrets
- ✅ Never commit secrets to repository
- ✅ Use webhook secrets for verification
- ✅ Monitor token usage and expiration

**Token Rotation:**
```bash
# Set calendar reminder 14 days before expiration
# When notified:
# 1. Generate new token with same permissions
# 2. Update GitHub secret CODEX_MASTER_KEY
# 3. Verify agent operations continue
# 4. Revoke old token
# 5. Update documentation with rotation date
```

### Risk Mitigation

**Potential Risks & Mitigations:**

| Risk | Mitigation |
|------|-----------|
| Unauthorized access | Fine-grained PAT with minimal permissions |
| Secret exposure | Never log or display secrets; GitHub Secrets only |
| Runaway automation | Rate limits (max 5 PRs/day); human approval for medium/high risk |
| Data loss | Git history; no force push; no branch deletion |
| Configuration drift | Daily validation; change log audit; weekly reviews |
| Token compromise | Short expiration (90 days); revocation capability; backup key |

---

## Rollback Procedures

### Emergency Disable

**If agent misbehaves:**

```bash
# Immediate action (< 1 minute):
# 1. Navigate to repository Secrets
#    https://github.com/Aries-Serpent/_codex_/settings/secrets/actions
# 2. Delete or rename CODEX_MASTER_KEY
# 3. Agent loses access immediately

# Alternative (< 2 minutes):
# 1. Edit .codex/autonomous_agent.yaml
# 2. Set: autonomous_actions_enabled: false
# 3. Commit and push to main branch
# 4. Agent respects configuration on next operation
```

### Graceful Disable

**For planned maintenance:**

```bash
git checkout -b maintenance/disable-agent
vim .codex/autonomous_agent.yaml
# Change: autonomous_actions_enabled: true → false

git add .codex/autonomous_agent.yaml
git commit -m "chore: disable agent for maintenance"
git push origin maintenance/disable-agent
# Create PR, review, merge
```

### Full Rollback to Pre-Genesis

**Complete reversal (rare):**

```bash
# 1. Disable agent (see above)
# 2. Remove all Genesis files
git checkout -b rollback/remove-genesis
git rm .codex/autonomous_agent.yaml
git rm .codex/guardrails.md
git rm .github/workflows/genesis-bootstrap.yml
# ... remove other Genesis artifacts

git commit -m "chore: rollback Genesis Protocol"
git push origin rollback/remove-genesis
# Create PR for review and approval
```

---

## Troubleshooting

### Common Issues

**Workflow fails with "Missing secrets"**
- **Cause:** CODEX_MASTER_KEY not set
- **Solution:** Add secret in repository settings
- **Verification:** Re-run workflow

**Genesis validation fails**
- **Cause:** Configuration file syntax error
- **Solution:** Validate YAML syntax: `python -c "import yaml; yaml.safe_load(open('file.yml'))"`
- **Verification:** Fix syntax and re-run

**Agent doesn't perform operations**
- **Cause:** `autonomous_actions_enabled: false` or `SAFE_MODE = True`
- **Solution:** Complete Phase 2 activation
- **Verification:** Check configuration files

**PAT permissions insufficient**
- **Cause:** Token created with wrong permissions
- **Solution:** Regenerate token with correct permissions
- **Verification:** Test with workflow run

### Getting Help

**Escalation Path:**
1. Check documentation in `docs/admin/`
2. Review troubleshooting in `scripts/AUTONOMOUS_AGENT_README.md`
3. Search GitHub Issues for similar problems
4. Create new issue with `[GENESIS]` tag
5. Contact @mbaetiong for critical issues

---

## Compliance and Governance

### Organizational Policies

**Ensure Genesis Protocol aligns with:**
- Information security policies
- Change management procedures
- Audit and compliance requirements
- Data protection regulations

**Customization:**
- Modify guardrails in `.codex/guardrails.md`
- Adjust authorization levels in `.codex/autonomous_agent.yaml`
- Update escalation contacts
- Set organization-specific rate limits

### Audit Requirements

**For compliance, maintain:**
- Complete audit trail in `.codex/change_log.md`
- Action logs in `.codex/action_log.ndjson`
- Validation reports in `.codex/genesis_validation.json`
- PR history with approval records

**Retention:**
- Audit logs: 90 days minimum (configurable)
- Change log: Permanent (part of git history)
- Validation reports: Until next Genesis update

---

## Next Steps

### After Genesis Completion

**Continuous Improvement:**
1. Monitor agent performance
2. Collect feedback from team
3. Refine guardrails based on experience
4. Update documentation as needed
5. Plan for advanced features (Phase 4+)

**Future Enhancements:**
- ML-based decision making
- Automated issue triage
- Advanced code review capabilities
- Predictive maintenance
- Cross-repository coordination

---

## References

**Key Documents:**
- [Guardrails](../guardrails.md) - Operational constraints
- [Agent Operations](Agent-Operations.md) - Decision framework
- [AGENTS.md](../../AGENTS.md) - AI agent orientation
- [Admin Setup Guide](../../docs/admin/GENESIS_SETUP_GUIDE.md) - Detailed instructions

**External Resources:**
- GitHub Actions Security Best Practices
- Fine-grained PAT Documentation
- Secrets Management Guide

---

**Document Version:** 1.0.0  
**Last Updated:** Previous Cycle-12-26  
**Next Review:** After Phase 2 completion  
**Status:** Phase 1 Complete | Phase 2 Pending

**For questions or assistance:** Contact @mbaetiong or create an issue with `[GENESIS]` tag.
