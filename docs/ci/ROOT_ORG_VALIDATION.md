# Root Organization CI/CD Validation

Automated validation workflow for root folder organization operations.

## Overview

The `root-org-validation.yml` workflow provides automated validation for root organization operations, ensuring zero-break guarantee through pre/post validation checks.

## Workflow File

**Location:** `.github/workflows/root-org-validation.yml`

## Triggers

### Automatic (Pull Request)
Triggered when PR affects root-level files:
- `*.md`, `*.py`, `*.yml`, `*.yaml`, `*.json`, `*.toml`, `*.txt`
- `scripts/root_org/**`
- `.codex/plans/**`
- `.codex/inventory.json`

### Manual (workflow_dispatch)
```yaml
inputs:
  file_to_validate: 'README.md'  # Optional
  dry_run: true                   # Default: true
```

**Usage:**
```bash
# Via GitHub UI: Actions → Root Organization Validation → Run workflow

# Via GitHub CLI:
gh workflow run root-org-validation.yml \
  -f file_to_validate=QUICKSTART.md \
  -f dry_run=true
```

## Jobs

### 1. Pre-Validation
**Purpose:** Establish baseline metrics before any changes

**Steps:**
- Link checker (markdown-link-check)
- Pytest baseline
- Ruff linter
- MkDocs build (if mkdocs.yml exists)

**Outputs:**
- `baseline_metrics` - JSON with results
- `validation-baseline` artifact

### 2. Reference Check
**Purpose:** Validate all references and imports

**Steps:**
- Scan changed files for broken references
- Validate Python import paths
- Check GitHub Actions workflow paths
- Generate reference validation report

**Outputs:**
- `reference-validation-report` artifact

### 3. Post-Validation
**Purpose:** Compare current state with baseline

**Steps:**
- Download baseline metrics
- Compare with current state
- Detect regressions
- Generate final report
- Comment on PR (if applicable)

**Outputs:**
- `root-org-validation-report` artifact
- PR comment with results

### 4. Summary
**Purpose:** Aggregate all results

**Steps:**
- Generate GitHub step summary
- List all artifacts
- Report overall status

## Artifacts

### validation-baseline
**Retention:** 7 days  
**Content:** Baseline metrics from pre-validation
**Format:** Text file with timestamped results

### reference-validation-report
**Retention:** 30 days  
**Content:** Reference check results
**Format:** Markdown report

### root-org-validation-report
**Retention:** 90 days  
**Content:** Complete validation report
**Format:** Markdown with all job results

## Integration

### With Root Organization Scripts

```yaml
# Example: Validate before move
- name: Validate file
  run: python scripts/root_org/validate_references.py ${{ matrix.file }} --dry-run

# Example: Check references after move
- name: Check references
  run: |
    python scripts/root_org/validate_references.py ${{ matrix.new_path }}
```

### With Custom Agents

```yaml
# Example: Use root-organizer-agent
- name: Assess risk
  run: |
    # Agent would analyze risk level
    # And provide recommendations
```

## Validation Checks

### Link Checker
- Checks all Markdown links
- Validates relative and absolute paths
- Reports broken links
- Continues on error (baseline recorded)

### Pytest Baseline
- Runs full test suite
- Records pass/fail status
- Continues on error (establishes baseline)

### Ruff Linter
- Checks code quality
- Identifies import errors
- Reports statistics
- Continues on error (baseline recorded)

### MkDocs Build
- Attempts strict build
- Records warnings
- Only runs if mkdocs.yml exists
- Continues on error (baseline recorded)

### Python Import Validation
- Compiles Python files
- Checks import statements
- Reports ModuleNotFoundError
- Validates up to 20 files (performance)

### Workflow Path Validation
- Validates YAML syntax
- Checks workflow file structure
- Reports parsing errors

## Error Handling

### Continue-on-Error Strategy
Most validation steps use `continue-on-error: true` to:
- Establish baseline even if checks fail
- Record current state for comparison
- Not block on pre-existing issues
- Focus on regressions

### Failure Conditions
Workflow fails if:
- Critical job failure (pre-validation, reference-check)
- Post-validation detects regressions
- Unable to generate reports

## Usage Examples

### Example 1: PR Validation
```bash
# Automatically triggered on PR
git checkout -b feature/move-files
git mv QUICKSTART.md docs/QUICKSTART.md
python scripts/root_org/update_links_atomic.py --old QUICKSTART.md --new docs/QUICKSTART.md
git commit -m "Move QUICKSTART.md to docs/"
git push origin feature/move-files
# Create PR → Workflow runs automatically
```

### Example 2: Manual Validation
```bash
# Via GitHub CLI
gh workflow run root-org-validation.yml \
  -f file_to_validate=AGENTS.md \
  -f dry_run=false

# Check run status
gh run list --workflow=root-org-validation.yml --limit 1

# Download artifacts
gh run download <run_id> -n root-org-validation-report
```

### Example 3: Local Testing
```bash
# Install dependencies
pip install pytest ruff mypy markdown-link-check

# Run validation steps locally
python scripts/root_org/validate_references.py README.md --dry-run
pytest tests/ -v
ruff check . --select E,F,W --statistics
mkdocs build --strict
```

## Monitoring

### Check Workflow Status
```bash
# List recent runs
gh run list --workflow=root-org-validation.yml

# View specific run
gh run view <run_id>

# Download artifacts
gh run download <run_id>
```

### Review PR Comments
Workflow automatically comments on PRs with:
- Validation status
- Link to artifacts
- Recommendations
- Any issues found

## Troubleshooting

### "Workflow not triggering"
**Cause:** Changed files don't match paths filter
**Solution:** Check paths in workflow trigger, add file patterns if needed

### "Baseline artifact not found"
**Cause:** Pre-validation job failed
**Solution:** Review pre-validation logs, fix critical errors

### "Reference check fails"
**Cause:** Broken references detected
**Solution:** Run `validate_references.py` locally, fix references

### "Post-validation detects regressions"
**Cause:** Current state worse than baseline
**Solution:** Review changes, run validation locally before committing

## Configuration

### Customize Validation
Edit `.github/workflows/root-org-validation.yml`:

**Change file patterns:**
```yaml
paths:
  - '*.md'
  - 'custom/**/*.txt'  # Add custom patterns
```

**Adjust retention:**
```yaml
retention-days: 90  # Default, can be changed per artifact
```

**Add custom checks:**
```yaml
- name: Custom validation
  run: |
    # Your custom validation logic
    ./scripts/custom_check.sh
```

## Best Practices

1. **Run locally first** - Test validation before pushing
2. **Check artifacts** - Review reports for detailed findings
3. **Monitor baselines** - Track metrics over time
4. **Address regressions** - Fix issues detected by post-validation
5. **Keep workflow updated** - Add checks as needed

## Metrics Tracked

- Link check pass/fail rate
- Pytest test count and failures
- Ruff violations count
- MkDocs build success rate
- Import errors count
- Workflow run duration

## Future Enhancements

Planned improvements:
- [ ] Parallel validation for speed
- [ ] Advanced diff analysis (pre vs post)
- [ ] Integration with GitHub Status API
- [ ] Slack/email notifications
- [ ] Automatic issue creation on failure
- [ ] Historical metrics dashboard
- [ ] Performance benchmarking

## Support

For issues:
- Check workflow logs in GitHub Actions
- Review artifact reports
- Run validation scripts locally
- Contact: @mbaetiong

---

**Version:** 1.0.0  
**Created:** 2026-01-21  
**Status:** ✅ Production Ready  
**Integration:** root-org scripts, custom agents
