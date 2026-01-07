# Deployment Orchestration Script

## Overview

The `deployment_orchestrator.py` script implements an autonomous 5-phase deployment workflow for merging Pull Requests to the main branch with comprehensive validation, monitoring, and audit trails.

## Features

- **5-Phase Autonomous Workflow**
  - Phase 1: Pre-Deployment Verification
  - Phase 2: Merge Execution
  - Phase 3: Post-Merge Validation
  - Phase 4: Health Check & Validation
  - Phase 5: Notification & Documentation

- **Comprehensive Validation**
  - YAML syntax validation
  - Security pre-flight checks (Bandit)
  - PR merge state verification
  - Status checks validation
  - Critical file validation

- **Audit Trail**
  - Detailed execution logs
  - Phase-by-phase results
  - Deployment manifests (JSON)
  - Deployment summaries (Markdown)

- **Error Handling**
  - Automatic failure detection
  - Phase-level error tracking
  - Graceful degradation
  - Human escalation points

## Usage

### Basic Usage

```bash
# Dry run (recommended for testing)
python scripts/deployment_orchestrator.py --pr-number 2207 --dry-run

# Execute actual deployment (requires GH_TOKEN environment variable)
export GH_TOKEN="your-github-token"
python scripts/deployment_orchestrator.py --pr-number 2207
```text

### Command-Line Options

```text
--pr-number PR_NUMBER
    Required. Pull request number to deploy.

--dry-run
    Optional. Simulate deployment without executing actual operations.
    Recommended for testing and validation.

--output-dir OUTPUT_DIR
    Optional. Directory for deployment artifacts.
    Default: .codex/deployments
```text

## Requirements

### Dependencies

- Python 3.10+
- GitHub CLI (`gh`) - for PR operations
- yamllint - for YAML validation
- bandit - for security scanning

### Environment Variables

- `GH_TOKEN` - GitHub Personal Access Token (required for actual execution)
  - Scopes needed: `repo`, `workflow`

## Deployment Phases

### Phase 1: Pre-Deployment Verification

Ensures all preconditions are met before merge:

1. **YAML Validation**: Validates workflow file syntax
2. **Security Scan**: Runs Bandit to detect HIGH/CRITICAL issues
3. **Merge State**: Verifies PR is mergeable
4. **Status Checks**: Confirms all required checks passing
5. **Pre-Check Report**: Generates JSON report of results

**Success Criteria**: All checks PASS, no conflicts

**Artifacts**:
- `pre_check_report_{pr_number}.json`

### Phase 2: Merge Execution

Executes the actual merge operation:

1. **Execute Merge**: Runs `gh pr merge` command
2. **Log Commit SHA**: Records merge commit hash
3. **Verify Update**: Confirms main branch updated
4. **Confirm Status**: Validates PR marked as merged

**Success Criteria**: Merge successful, commit SHA logged

**Skipped If**: Dry-run mode or missing GH_TOKEN

### Phase 3: Post-Merge Validation

Monitors post-merge validation workflow:

1. **Trigger Workflow**: Waits for automatic trigger
2. **Monitor Jobs**: Tracks job execution
3. **Collect Metrics**: Gathers coverage data
4. **Report Progress**: Updates status periodically
5. **Aggregate Results**: Compiles final results

**Success Criteria**: All jobs complete, coverage ≥ 96%

**Duration**: 35-40 minutes (estimated)

### Phase 4: Health Check & Validation

Verifies system health and readiness:

1. **Branch State**: Checks main branch commits
2. **Artifacts**: Validates workflow artifacts
3. **Critical Files**: Confirms required files present
4. **Health Report**: Generates health check report
5. **Readiness**: Assesses production readiness

**Success Criteria**: All validations pass

**Artifacts**:
- `health_check_report_{pr_number}.json`

### Phase 5: Notification & Documentation

Creates audit trail and notifications:

1. **Deployment Summary**: Generates comprehensive summary
2. **Release Notes**: Creates release documentation
3. **Manifest Archive**: Archives deployment manifest
4. **Follow-Up Issues**: Creates tracking issues (if needed)

**Success Criteria**: All notifications sent, documentation complete

**Artifacts**:
- `deployment_summary_{pr_number}.md`
- `deployment_manifest_{pr_number}.json`
- `deployment_{pr_number}_{timestamp}.log`

## Output Artifacts

All artifacts are stored in the output directory (default: `.codex/deployments/`):

### Logs

- `deployment_{pr_number}_{timestamp}.log` - Detailed execution log

### Reports

- `pre_check_report_{pr_number}.json` - Pre-deployment verification results
- `health_check_report_{pr_number}.json` - Health check results
- `deployment_summary_{pr_number}.md` - Human-readable summary
- `deployment_manifest_{pr_number}.json` - Complete deployment manifest

### Manifest Structure

```json
{
  "pr_number": 2207,
  "source_branch": "0D_base_",
  "target_branch": "main",
  "started_at": "Previous Cycle-11-14T21:00:00Z",
  "completed_at": "Previous Cycle-11-14T21:45:00Z",
  "status": "success",
  "phase_results": [
    {
      "phase": "Phase 1: Pre-Deployment Verification",
      "status": "success",
      "duration_seconds": 12.5,
      "details": {...},
      "errors": []
    }
  ],
  "merge_commit_sha": "abc123...",
  "workflow_run_id": "123456",
  "coverage_percentage": 97.8
}
```text

## Error Handling

### Automatic Escalation Triggers

The script automatically detects and escalates:

- Merge fails (exit code ≠ 0)
- Coverage drops below 96%
- Security scan finds HIGH/CRITICAL issues
- Workflow timeout (> 60 minutes)
- Workflow job failure

### Failure Response

When a phase fails:

1. Error is logged with details
2. Phase marked as FAILED
3. Subsequent phases halted (except notification)
4. Notification phase runs to document failure
5. Script exits with non-zero code

### Human Intervention Points

**Required Human Approval**:
- Initial deployment authorization
- Pre-check review (Phase 1 complete)
- Merge authorization (pre-checks pass)

**Optional Monitoring**:
- Validation monitoring (Phase 3 running)
- Rollback decision (if validation fails)
- Post-deployment sign-off

## Testing

### Unit Tests

Run the test suite:

```bash
pytest tests/test_deployment_orchestrator.py -v
```text

Test coverage includes:
- Phase result data structures
- Deployment manifest handling
- All 5 deployment phases
- Command execution (dry-run and actual)
- Error handling scenarios
- Artifact generation
- CLI interface

### Integration Testing

Test with dry-run mode:

```bash
# Test full workflow without actual execution
python scripts/deployment_orchestrator.py --pr-number 2207 --dry-run

# Verify artifacts generated
ls -la .codex/deployments/
```text

## Security Considerations

### Sensitive Data

- Never commit `GH_TOKEN` to version control
- Deployment logs Phase 5 contain sensitive information
- Artifacts are excluded from git via `.gitignore`

### Authentication

- GitHub token must have appropriate scopes
- Token should be rotated regularly
- Use GitHub Actions secrets for CI/CD

### Audit Trail

- All actions are logged with timestamps
- Deployment manifests include complete history
- Logs stored in `.codex/deployments/` (excluded from git)

## Rollback Procedures

If deployment needs to be rolled back:

1. **Identify Issue**: Check deployment logs and manifest
2. **Create Revert PR**: Use GitHub CLI
   ```bash
   gh pr revert <pr_number>
   ```
3. **Document Reason**: Create incident issue
4. **Post-Mortem**: Schedule review within 24 hours

## Troubleshooting

### Common Issues

**Problem**: `gh: command not found`
```bash
# Install GitHub CLI
# See: https://cli.github.com/manual/installation
```text

**Problem**: `GH_TOKEN` not set
```bash
# Set environment variable
export GH_TOKEN="your-token-here"
```text

**Problem**: YAML validation fails
```bash
# Install yamllint
pip install yamllint

# Check YAML manually
yamllint .github/workflows/post-merge-validation-optimized.yml
```text

**Problem**: Security scan fails
```bash
# Install bandit
pip install bandit

# Run scan manually
bandit -r src/ --severity-level=HIGH -f json
```text

### Debug Mode

For detailed debugging:

```bash
# Run with Python debug output
python -u scripts/deployment_orchestrator.py --pr-number 2207 --dry-run 2>&1 | tee debug.log
```text

## Best Practices

1. **Always Test First**: Use `--dry-run` before actual execution
2. **Review Artifacts**: Check generated reports before proceeding
3. **Monitor Progress**: Watch logs in real-time during execution
4. **Keep Records**: Archive deployment manifests for compliance
5. **Human Oversight**: Maintain approval gates for critical phases
6. **Regular Updates**: Keep dependencies and tokens current

## References

- [Deployment Orchestration Specification](.github/docs/DEPLOYMENT_ORCHESTRATION_PR2207.md)
- [Deployment Playbook](.github/docs/PR_2207_DEPLOYMENT_PLAYBOOK.md)
- [Sign-Off Checklist](.github/docs/PR_2207_FINAL_SIGN_OFF_CHECKLIST.md)
- [Copilot Agent Instructions](.github/docs/COPILOT_AGENT_DEPLOYMENT_INSTRUCTIONS.md)

## Version History

- **1.0.0** (Previous Cycle-11-14): Initial implementation
  - 5-phase autonomous workflow
  - Comprehensive validation and monitoring
  - Full audit trail generation
  - Error handling and escalation
  - Unit test coverage (23 tests)

## Support

For issues or questions:

1. Check troubleshooting section above
2. Review deployment logs in `.codex/deployments/`
3. Consult deployment specification documentation
4. Create issue in repository with `deployment` label

---

**Author**: GitHub Copilot Agent  
**Version**: 1.0.0  
**Last Updated**: Previous Cycle-11-14
