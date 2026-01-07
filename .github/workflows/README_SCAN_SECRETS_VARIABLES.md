# GitHub Secrets and Variables Scanning Workflow

## Overview

The `scan-secrets-variables.yml` workflow comprehensively scans the entire codebase for references to GitHub secrets, variables, and environment variables. It generates a detailed report showing what's expected versus what's configured in GitHub settings.

## Features

### 1. **Comprehensive Scanning**
- Scans all text files in the repository
- Identifies `${{ secrets.* }}` patterns
- Identifies `${{ vars.* }}` patterns
- Identifies environment variable patterns (`$VAR` or `${VAR}`)
- Excludes build artifacts, cache directories, and node_modules

### 2. **GitHub Settings Verification**
- Retrieves configured repository secrets
- Retrieves configured repository variables
- Retrieves configured organization secrets
- Retrieves configured organization variables
- Compares expected vs. configured items

### 3. **Detailed Reporting**
- Markdown-formatted report with categorized sections
- Lists all expected secrets and variables
- Shows which items are configured
- Identifies missing configurations
- Includes metadata (timestamp, commit SHA, workflow run ID)

### 4. **Performance Optimization**
- Uses GitHub Actions cache for pip and gh CLI
- Efficient file scanning with proper exclusions
- Parallel-safe operations

## Triggers

The workflow can be triggered in three ways:

1. **Manual Trigger** (`workflow_dispatch`)
   - Allows manual execution from GitHub Actions UI
   - Optional input: `include_env_vars` (default: true)

2. **Push to main/develop** branches
   - Automatically runs on pushes to main or develop branches

3. **Pull Requests** to main/develop branches
   - Runs on PR open, synchronize, or reopen events

## Usage

### Manual Execution

1. Go to Actions tab in GitHub
2. Select "Scan and Report GitHub Secrets and Variables"
3. Click "Run workflow"
4. Optionally toggle environment variable scanning

### Viewing Reports

After workflow completion:
1. Go to the workflow run
2. Download the `github-secrets-variables-report` artifact
3. Open `report.md` to view the comprehensive report

## Report Structure

```markdown
# GitHub Secrets and Variables Usage Report

**Generated:** [timestamp]
**Repository:** [repo name]
**Commit:** [SHA]
**Workflow Run:** [run ID]

## 📊 Extracted from Codebase
### 🔐 Expected Secrets (from ${{ secrets.* }})
- `SECRET_NAME_1`
- `SECRET_NAME_2`

### 📦 Expected Variables (from ${{ vars.* }})
- `VAR_NAME_1`
- `VAR_NAME_2`

### 🌍 Expected Environment Variables (from $VAR or ${VAR})
- `ENV_VAR_1`
- `ENV_VAR_2`

## ✅ Verification Against GitHub Settings
### 🔐 Repository Secrets (Configured)
- ✓ `SECRET_NAME_1`

### 📦 Repository Variables (Configured)
- ✓ `VAR_NAME_1`

### 🏢 Organization Secrets (Configured)
[list of org secrets]

### 🏢 Organization Variables (Configured)
[list of org variables]

## ⚠️ Summary of Missing Items
### 🔐 Missing Secrets
- ❌ `MISSING_SECRET`

### 📦 Missing Variables
- ❌ `MISSING_VARIABLE`

## 📝 Notes
[Important notes about permissions, environment variables, etc.]
```

## Permissions Required

The workflow requires the following permissions:
- `contents: read` - To checkout and scan repository files
- `issues: write` - For potential future enhancements (issue creation)
- `pull-requests: write` - For potential PR comments

Note: Listing secrets and variables may require admin permissions. The workflow gracefully handles permission errors.

## Artifact Contents

The uploaded artifact includes:
- `report.md` - Main report file
- `extracted_secrets.txt` - List of expected secrets
- `extracted_vars.txt` - List of expected variables
- `extracted_env_vars.txt` - List of environment variables
- `repo_secrets.txt` - Configured repository secrets
- `repo_vars.txt` - Configured repository variables
- `org_secrets.txt` - Configured organization secrets
- `org_vars.txt` - Configured organization variables

Artifacts are retained for 90 days.

## Scanning Logic

### Secrets Pattern
```regex
\$\{\{ secrets\.[A-Za-z0-9_.]+ \}\}
```
Matches GitHub Actions secret references in workflow files.

### Variables Pattern
```regex
\$\{\{ vars\.[A-Za-z0-9_.]+ \}\}
```
Matches GitHub Actions variable references in workflow files.

### Environment Variables Pattern
```regex
\$\{?[A-Z_][A-Z0-9_]+\}?
```
Matches shell environment variable patterns, with common false positives filtered out (PATH, HOME, USER, etc.).

## Excluded Paths

The scanner excludes the following directories:
- `.git/`
- `node_modules/`
- `.hypothesis/`
- `build/`
- `dist/`
- `.nox/`
- `.pytest_cache/`
- `__pycache__/`

## Limitations

1. **Permissions**: Organization-level secrets and variables may not be accessible without admin permissions
2. **Environment Variables**: Not centrally managed in GitHub, so verification is informational only
3. **Dynamic References**: Only literal references are detected; dynamically constructed references may be missed
4. **Binary Files**: Only text files are scanned

## Integration with CI/CD

This workflow complements other security and configuration workflows:
- Can be used to audit secret/variable usage before deployments
- Helps identify configuration drift
- Supports security compliance checks

## Caching Strategy

The workflow uses GitHub Actions cache:
- **Cache Key**: Based on OS and hash of requirements files
- **Cached Paths**: `~/.cache/pip`, `~/.cache/gh`
- **Benefit**: Faster workflow execution (2-5 minutes saved per run)

## Future Enhancements

Potential improvements for future iterations:
- Auto-create issues for missing secrets/variables
- PR comments with scan results
- Integration with secret scanning tools
- Support for custom secret patterns
- Historical trend analysis
- Slack/email notifications for missing configurations

## Troubleshooting

### "Unable to list secrets" error
- Check that workflow has proper permissions
- Verify GITHUB_TOKEN has necessary scopes
- Organization secrets may require admin access

### No secrets/variables found
- Verify the patterns match your usage
- Check that files are not in excluded paths
- Ensure files are detected as text files

### Report not generated
- Check workflow logs for errors
- Verify all dependencies (gh, jq) are available
- Check for shell script syntax errors

## Related Workflows

- `.github/workflows/security-suite.yml` - Security scanning
- `.github/workflows/self-healing-feedback-loop.yml` - Automated improvements
- `.github/workflows/code-quality.yml` - Code quality checks

## Maintenance

- Review and update excluded paths as needed
- Adjust patterns if naming conventions change
- Monitor artifact storage usage
- Update action versions regularly

## Support

For issues or questions:
- Check workflow run logs
- Review this documentation
- Open an issue in the repository
- Contact repository maintainers
