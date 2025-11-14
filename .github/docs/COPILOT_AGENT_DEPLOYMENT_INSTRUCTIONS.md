# GitHub Copilot Agent Deployment Instructions

## For: PR #2207 Deployment to Main Branch

### Quick Start

1. **Create Deployment Issue**
   - Use template: [.github/templates/DEPLOYMENT_ORCHESTRATION_TASK.md](https://github.com/Aries-Serpent/_codex_/raw/refs/heads/0D_base_/.github/templates/DEPLOYMENT_ORCHESTRATION_TASK.md)
   - Mention: @copilot-swe-agent
   - Priority: CRITICAL

2. **Copilot Agent Activates**
   - Reads specification: [.github/docs/DEPLOYMENT_ORCHESTRATION_PR2207.md](https://github.com/Aries-Serpent/_codex_/raw/refs/heads/0D_base_/.github/docs/DEPLOYMENT_ORCHESTRATION_PR2207.md)
   - Reviews approval status
   - Initiates Phase 1

3. **Monitor Dashboard**
   - Open: GitHub Actions tab
   - Watch: Real-time progress
   - Intervene if: Critical issues detected

4. **Deployment Completes**
   - All phases successful ✅
   - Audit trail generated
   - Stakeholder notifications sent

###Key Commands for Manual Intervention

```bash
# Check deployment status
gh pr view 2207 --json mergeable,mergeStateStatus

# View post-merge workflow
gh run list --workflow=post-merge-validation-optimized.yml -b main -n 1

# If rollback needed
gh pr revert 2207
```

### Human Decision Points

**Before Phase 2 (Merge)**:
- Review Phase 1 report
- Confirm readiness to merge
- Reply: "APPROVE MERGE" or "HALT"

**During Phase 3 (Validation)**:
- Watch progress passively
- Can pause with: "PAUSE DEPLOYMENT"
- Can continue with: "RESUME"

**If Failure at Any Phase**:
- Copilot Agent notifies: @on-call
- Reviews options: Rollback vs. Remediate
- Waits for decision

### What NOT to Do

❌ **Don't interrupt Copilot Agent during execution**
   - Phase transitions are automatic
   - Interruption causes restart

❌ **Don't force merge without Copilot Agent approval**
   - Use the autonomous orchestration
   - Bypass compromises audit trail

❌ **Don't assume success**
   - Monitor dashboard throughout
   - Be ready to intervene

### What TO Do

✅ **Maintain real-time dashboard visibility**
   - Open GitHub Actions dashboard
   - Watch metrics in real-time
   - Be ready to pause if issues arise

✅ **Trust the specification**
   - Copilot Agent follows exact specification
   - All gates properly configured
   - Safety built into automation

✅ **Document decisions**
   - If pausing: Why?
   - If rolling back: Document reason
   - Enables post-mortem analysis

---

**Instructions Version**: 1.0
**Last Updated**: 2025-11-14 19:03:56 UTC
