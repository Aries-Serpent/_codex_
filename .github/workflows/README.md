# GitHub Actions Workflows

This directory contains GitHub Actions workflow definitions for CI/CD, automation, and security operations.

## Active baseline policy

The live workflow set is intentionally limited to the active baseline used by the repository today. Any workflow that is experimental, duplicate, or not part of the current operational baseline is disabled by renaming it to `.disabled` so it does not run in the normal CI surface.

The reusable gate workflow `cost-gate.yml` remains active because it is referenced by active pipelines (`data-quality-suite.yml`, `docker-build-push.yml`, `rust_swarm_ci.yml`, and `scheduled-archival.yml`).

## 📋 Table of Contents

- [Workflow Index](#workflow-index)
- [Token Configuration](#token-configuration)
- [Troubleshooting](#troubleshooting)
- [Rollback Strategies](#rollback-strategies)
- [Best Practices](#best-practices)

---

## Workflow Index

### Security Workflows

#### `phase34-codeql-alert-fetch.yml`
**Status**: ✅ Active  
**Last Updated**: 2026-01-26  
**Trigger**: Manual (`workflow_dispatch`)

**Purpose**: Fetch CodeQL code scanning alerts from GitHub API, generate inventory, and create tracking issue for AI agent analysis.

**Inputs**:
- `max_pages` (default: 60) - Maximum pages to fetch (100 alerts per page)
- `severity_filter` (default: all) - Filter by severity: all, critical, high, medium, low

**Permissions**:
- `security-events: read` - Fetch code scanning alerts
- `contents: write` - Commit alert inventory to repository
- `pull-requests: write` - Create PRs for fixes
- `issues: write` - Create tracking issues

**Outputs**:
- `.codex/security/alert_inventory.json` - Complete alert data
- `.codex/security/alert_inventory.csv` - Spreadsheet format
- `.codex/security/alert_summary.md` - Human-readable summary
- GitHub Issue - Tracking issue with @copilot instructions

**Usage**:
```bash
# Trigger manually
gh workflow run phase34-codeql-alert-fetch.yml \
  --field max_pages=10 \
  --field severity_filter=high

# Monitor execution
gh run watch

# View results
gh run view --log
```

**Debug Mode**:
Enable debug logging by setting `ACTIONS_RUNNER_DEBUG=true` in repository secrets:
```bash
gh secret set ACTIONS_RUNNER_DEBUG --body "true"
```

Then check debug output in workflow logs.

---

### Application Distribution Workflows

#### `app-package-download.yml`
**Status**: ✅ Active  
**Last Updated**: 2026-02-13  
**Trigger**: Manual (`workflow_dispatch`)

**Purpose**: Package and distribute applications from the `apps/` directory as ready-to-use ZIP or TAR.GZ archives for end users.

**Inputs**:
- `app_name` (default: zd_voice_lines) - Application to package: zd_voice_lines, all
- `branch` (default: copilot/add-zd-voice-lines-console-app) - Source branch: main, 0D_base_, copilot/add-zd-voice-lines-console-app
- `custom_branch` (optional) - Custom branch name (overrides dropdown selection)
- `include_dependencies` (default: true) - Include requirements.txt with dependencies
- `package_format` (default: zip) - Archive format: zip, tar.gz

**Permissions**:
- `contents: read` - Read repository contents
- `actions: read` - Read workflow information

**Outputs**:
- Package artifact (ZIP or TAR.GZ) - Complete application bundle with code, docs, tests
- Package manifest (JSON) - Metadata about package creation
- Retention: 30 days for packages, 90 days for manifests

**Usage**:
```bash
# Trigger manually via UI
# 1. Go to Actions > App Package Download
# 2. Click "Run workflow"
# 3. Select application, branch, and options
# 4. Download from Artifacts section

# Trigger via GitHub CLI
gh workflow run app-package-download.yml \
  --field app_name=zd_voice_lines \
  --field branch=copilot/add-zd-voice-lines-console-app \
  --field include_dependencies=true \
  --field package_format=zip

# Download artifact after run completes
gh run download <run-id> --name <package-name>
```

**Package Contents** (Zendesk Voice Lines):
- `zd_voice_lines.py` - Main GUI application (950 LOC)
- `test_api_client.py` - Component tests (7 tests)
- `requirements.txt` - Python dependencies
- `PACKAGE_INFO.md` - Quick start and installation guide
- `docs/` - Complete documentation (USER_GUIDE.md, DEVELOPMENT.md)
- Supporting files: README, CHANGELOG, specs, mockups

**Documentation**: See [app-package-download.md](./app-package-download.md) for complete guide.

---

## Token Configuration

**Last Token Refresh**: 2026-01-26T19:00:00Z  
**Token Expiry**: 2027-01-26T00:00:00Z  
**Next Rotation**: 2026-04-26 (90 days)

### Workflows Using CODEX_MASTER_KEY

The following workflows require elevated permissions via the `CODEX_MASTER_KEY` secret:

1. **phase34-codeql-alert-fetch.yml** - CodeQL alert operations
2. **auth-token-rotation.yml** - Token rotation automation
3. **phase10-automated-secrets-setup.yml** - Secret management

### Token Permissions Required

**For GitHub Actions Workflows**:
```yaml
permissions:
  security-events: read     # CodeQL alerts
  contents: write          # Repository modifications
  issues: write            # Issue creation
  pull-requests: write     # PR operations
```

**For Personal Access Tokens (PAT)**:
- `repo` (full control)
- `workflow` (update workflows)
- `security_events` (read/write security alerts)
- `admin:org` (organization operations)

**Note**: PAT scopes don't have `:read`/`:write` suffixes. In workflows, use `permission-name: read|write`.

### Token Regeneration

See comprehensive guide: `.codex/docs/TOKEN_REGENERATION_GUIDE.md`

Quick steps:
1. Generate new token at https://github.com/settings/tokens
2. Update repository secret: `gh secret set CODEX_MASTER_KEY --body "TOKEN"`
3. Update configuration files (`.codex/flags.json`, `.codex/flags.yml`)
4. Verify with test workflow run
5. Document in change log

---

## Troubleshooting

### Common Issues

#### Issue 1: "Bad credentials" (401 Error)

**Symptom**: Workflow fails with authentication error  
**Cause**: Token expired or not properly configured  
**Solution**:
```bash
# Check token expiry
gh api /user | jq '.login'

# Update token if expired
gh secret set CODEX_MASTER_KEY --body "NEW_TOKEN"
```

#### Issue 2: "Resource not accessible" (403 Error)

**Symptom**: Workflow can't access resources despite authentication  
**Cause**: Missing required permissions in token or workflow  
**Solution**:
```bash
# Check workflow permissions in YAML
grep -A 5 "permissions:" .github/workflows/phase34-codeql-alert-fetch.yml

# Verify token scopes
gh api /user --include | grep "x-oauth-scopes"

# Add missing permission to workflow or regenerate token with required scopes
```

#### Issue 3: YAML Syntax Errors

**Symptom**: Workflow doesn't appear in Actions UI or fails to parse  
**Cause**: Invalid YAML syntax  
**Solution**:
```bash
# Validate YAML syntax
yamllint .github/workflows/phase34-codeql-alert-fetch.yml

# Validate with Python
python -c "import yaml; yaml.safe_load(open('.github/workflows/FILENAME.yml'))"

# Common fixes:
# - Remove trailing spaces
# - Avoid heredocs (use echo commands or temp files)
# - Escape special characters in strings
# - Use proper indentation (2 spaces)
```

#### Issue 4: Workflow Not Triggering

**Symptom**: Manual trigger doesn't start workflow  
**Cause**: Workflow disabled or branch mismatch  
**Solution**:
```bash
# Check if workflow is enabled
gh workflow view phase34-codeql-alert-fetch.yml | grep "State:"

# Enable if disabled
gh workflow enable phase34-codeql-alert-fetch.yml

# Verify you're on correct branch
git branch --show-current

# Trigger from specific branch
gh workflow run phase34-codeql-alert-fetch.yml --ref main
```

---

## Rollback Strategies

### Phase 34 Workflow Rollback

If the Phase 34 workflow fails after deployment, use this rollback strategy:

#### Method 1: Git Revert (Recommended)

```bash
# Revert the fix commit
git revert a407495

# Or revert multiple commits
git revert a407495..HEAD

# Push revert
git push origin main
```

#### Method 2: Disable Workflow Temporarily

Add this to the workflow file:
```yaml
on:
  workflow_dispatch: {}
  # Disabled due to issues - see https://github.com/Aries-Serpent/_codex_/issues/XXXX
```

Or disable via CLI:
```bash
gh workflow disable phase34-codeql-alert-fetch.yml
```

#### Method 3: Restore Previous Version

```bash
# Find previous working version
git log --oneline .github/workflows/phase34-codeql-alert-fetch.yml

# Restore specific version
git checkout 34ba3a8 -- .github/workflows/phase34-codeql-alert-fetch.yml

# Commit restoration
git commit -m "rollback: Restore phase34 workflow to working version"
git push origin main
```

#### Method 4: Alternative Heredoc Implementation

If echo approach fails, alternative heredoc pattern:
```yaml
run: |
  # Use temp file with heredoc (quoted delimiter prevents expansion)
  cat > /tmp/body.md <<'EOF'
  Content here with $variables preserved literally
  EOF

  # Then replace placeholders with sed
  sed -i "s/PLACEHOLDER/$ACTUAL_VALUE/g" /tmp/body.md

  # Use file with gh CLI
  gh issue create --body-file /tmp/body.md
```

### Emergency Contacts

- **Primary**: @mbaetiong
- **Repository Issues**: https://github.com/Aries-Serpent/_codex_/issues
- **Security**: security@example.com (if applicable)

---

## Best Practices

### Workflow Development

1. **Test Locally First**
   ```bash
   # Validate YAML
   yamllint workflow.yml
   python -c "import yaml; yaml.safe_load(open('workflow.yml'))"

   # Test scripts locally
   bash -n script.sh  # Syntax check
   shellcheck script.sh  # Linting
   ```

2. **Use Minimal Permissions**
   - Only request permissions actually needed
   - Use `read` instead of `write` when possible
   - Document why each permission is required

3. **Avoid Heredocs in YAML**
   - Heredocs can confuse YAML parsers
   - Use echo commands, temp files, or --body-file flag
   - See Phase 34 workflow for working pattern

4. **Add Debug Logging**
   ```yaml
   - name: Debug Info
     if: runner.debug == '1'
     run: |
       echo "::group::Debug Information"
       echo "Workflow: ${{ github.workflow }}"
       echo "Actor: ${{ github.actor }}"
       # ... more debug info
       echo "::endgroup::"
   ```

5. **Use Semantic Commit Messages**
   ```
   fix: Fix YAML syntax error in phase34 workflow
   feat: Add debug logging to workflows
   docs: Update workflow documentation
   refactor: Simplify issue creation logic
   ```

### Security

1. **Never Commit Secrets**
   - Use repository secrets
   - Use `${{ secrets.SECRET_NAME }}`
   - Never echo secrets to logs

2. **Validate External Input**
   - Sanitize user inputs from `workflow_dispatch`
   - Validate file paths
   - Check for command injection

3. **Use Pinned Action Versions**
   ```yaml
   # Good - pinned to specific version
   uses: actions/checkout@v4

   # Better - pinned to commit SHA
   uses: actions/checkout@8e5e7e5ab8b370d6c329ec480221332ada57f0ab
   ```

4. **Scan for Vulnerabilities**
   - Run CodeQL on workflow changes
   - Review Dependabot alerts
   - Keep actions up to date

### Monitoring

1. **Set Up Alerts**
   - GitHub Actions failures → Email/Slack
   - Security alerts → Immediate notification
   - Token expiry → 30 iteration advance warning

2. **Track Metrics**
   - Workflow success rate
   - Average execution time
   - Token rotation schedule
   - Alert resolution time

3. **Maintain Logs**
   - Keep workflow run history
   - Document all changes in `.codex/change_log.md`
   - Create aftermath reports for incidents

---

## Additional Resources

- **GitHub Actions Documentation**: https://docs.github.com/en/actions
- **YAML Syntax Guide**: https://yaml.org/spec/1.2/spec.html
- **Token Regeneration Guide**: `.codex/docs/TOKEN_REGENERATION_GUIDE.md`
- **Phase 34 Implementation Plan**: `.codex/plans/PHASE34_YAML_SYNTAX_FIX_ITERATION_PLAN.md`
- **Repository Memory**: `.codex/AGENTS.md` (workflow patterns section)

---

**Document Version**: 1.0.0  
**Last Updated**: 2026-01-26T19:30:00Z  
**Maintained By**: @mbaetiong  
**Next Review**: 2026-02-26

---

**Workflow README Complete** ✅
