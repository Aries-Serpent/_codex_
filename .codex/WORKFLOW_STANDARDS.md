# GitHub Actions Workflow Standards
## Phase 2 Lane 3 - Concurrency & Timeout Standards

**Effective Date**: 2026-07-18  
**Compliance Requirement**: Mandatory for all new and modified workflows  
**Enforcement**: Automated via PR gates and CI health monitoring

---

## Standard 1: Branch-Scoped Concurrency

### Requirement

All workflows MUST implement branch-scoped concurrency to prevent duplicate execution when multiple commits are pushed to the same branch.

### Format

```yaml
name: <Workflow Name>

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main, develop]

# REQUIRED: Branch-scoped concurrency group
concurrency:
  group: ${{ github.workflow }}-${{ github.head_ref || github.ref }}
  cancel-in-progress: true  # See exceptions below
```

### Rationale

- **Prevents wasted CI resources**: Cancels previous runs when new code is pushed
- **Improves developer experience**: Faster feedback on latest changes
- **Reduces queue time**: Allows other workflows to execute
- **Cost savings**: Lower GitHub Actions minutes consumption

### Exceptions

#### For Deployment Workflows
Use `cancel-in-progress: false` to allow deployment jobs to complete even when new code is pushed:

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.head_ref || github.ref }}
  cancel-in-progress: false  # Don't cancel deployments in progress
```

**Deployment workflow keywords** (detected automatically):
- `deploy`, `release`, `publish`, `pypi`, `docker`, `push-image`

### Testing Your Implementation

```bash
# Verify concurrency block exists
grep -A2 "^concurrency:" .github/workflows/your-workflow.yml

# Verify format
grep "github.workflow.*github.head_ref.*github.ref" .github/workflows/your-workflow.yml
```

---

## Standard 2: Job-Level Timeouts

### Requirement

All jobs MUST have an explicit `timeout-minutes` setting. This prevents jobs from hanging indefinitely.

### Format

```yaml
jobs:
  my-job:
    name: My Job
    runs-on: ubuntu-latest
    timeout-minutes: 30  # REQUIRED
    steps:
      - name: Step 1
        run: echo "This job will timeout after 30 minutes"
```

### Timeout Recommendations

| Workflow Type | Jobs | Timeout | Examples |
|---|---|---|---|
| **Cleanup/Labels** | cleanup, label-pr, watchdog | 10 min | Automatic maintenance tasks |
| **Linting/Format** | lint, format, style-check | 15 min | Code quality checks |
| **Documentation** | pages, docs, validate-links | 20 min | GitHub Pages, doc validation |
| **Testing** | test, unit-test, pytest | 30 min | Standard unit tests |
| **Coverage/Analysis** | coverage, codeql, audit, security | 45 min | Code analysis tools |
| **Heavy Compute** | docker-build, rust-build, ml-training, deploy | 60 min | Compilation, ML training |

### Timeout Matrix by Runner Type

| Runner | Default | Max Allowed | Rationale |
|--------|---------|-------------|-----------|
| ubuntu-latest | 30 min | 60 min | Standard Linux runner |
| windows-latest | 45 min | 60 min | Slower compilation |
| macos-latest | 40 min | 60 min | Variable performance |
| self-hosted | 60 min | 360 min | Potentially overprovisioned |

### Testing Your Implementation

```bash
# Verify all jobs have timeout
grep -c "timeout-minutes:" .github/workflows/your-workflow.yml

# Expected: number of jobs in your workflow

# Find jobs WITHOUT timeout
sed -n '/^jobs:/,/^[a-z]/p' .github/workflows/your-workflow.yml | \
  grep -B5 "^\s\s[a-z]" | grep -v "timeout-minutes" | grep "run:"
```

---

## Standard 3: GitHub Actions Permissions

### Requirement

All workflows SHOULD explicitly define `permissions` to follow principle of least privilege.

### Format

```yaml
permissions:
  contents: read          # Read-only access to repository contents
  pull-requests: write    # Can create/update PR comments
  checks: write          # Can create check runs
  security-events: write # For CodeQL and security scanning
```

### Common Permission Sets

**Read-Only (Default)**:
```yaml
permissions:
  contents: read
```

**CI Check Runs**:
```yaml
permissions:
  contents: read
  checks: write
```

**Security Scanning**:
```yaml
permissions:
  contents: read
  security-events: write
```

**PR Automation**:
```yaml
permissions:
  contents: read
  pull-requests: write
  checks: write
```

---

## Standard 4: Workflow Triggers

### Requirement

Workflows should be selective about their triggers to avoid unnecessary execution.

### Recommended Triggers

**For PR validation**:
```yaml
on:
  pull_request:
    branches: [main, develop]
    paths:
      - "src/**"
      - ".github/workflows/*.yml"
      - "!docs/**"  # Skip when only docs change
```

**For commit validation**:
```yaml
on:
  push:
    branches: [main, develop]
```

**For scheduled tasks**:
```yaml
on:
  schedule:
    - cron: "0 2 * * *"  # Run at 2 AM UTC daily
  workflow_dispatch:     # Manual trigger option
```

---

## Standard 5: Step-Level Timeouts

### Requirement (Optional but Recommended)

Individual steps can have timeouts for additional granularity:

```yaml
jobs:
  long-running:
    timeout-minutes: 60  # Job-level
    steps:
      - name: Long Step
        timeout-minutes: 45  # Step-level (overrides job default)
        run: |
          # This step can run max 45 minutes
          long-running-command
```

---

## Checklist for New Workflows

Use this checklist when creating or modifying workflows:

- [ ] **Concurrency**: Branch-scoped concurrency group defined
  ```yaml
  concurrency:
    group: ${{ github.workflow }}-${{ github.head_ref || github.ref }}
    cancel-in-progress: true  # (false for deployments)
  ```

- [ ] **Timeouts**: All jobs have `timeout-minutes` configured
  ```yaml
  jobs:
    my-job:
      timeout-minutes: 30
  ```

- [ ] **Permissions**: Explicit permissions defined (if needed)
  ```yaml
  permissions:
    contents: read
  ```

- [ ] **Triggers**: Selective triggers with path filters (if applicable)
  ```yaml
  on:
    pull_request:
      paths: ["src/**", ".github/workflows/**"]
  ```

- [ ] **Error handling**: `continue-on-error` used judiciously
  - Only for non-critical steps
  - Documented in comments

- [ ] **Secrets**: No hardcoded secrets or credentials
  - Use `secrets.MY_SECRET` format
  - Use `${{ secrets.GITHUB_TOKEN }}` for default auth

- [ ] **Testing**: Workflow has been tested locally or in dry-run
  - Use `act` to test locally: `act pull_request`
  - Or create in draft PR first

---

## Migration Guide

### For Existing Workflows

#### Step 1: Add Branch-Scoped Concurrency

```bash
# Backup existing workflow
cp .github/workflows/my-workflow.yml .github/workflows/my-workflow.yml.bak

# Edit and add after the 'on:' section:
concurrency:
  group: ${{ github.workflow }}-${{ github.head_ref || github.ref }}
  cancel-in-progress: true
```

#### Step 2: Add Job Timeouts

```yaml
# For each job, add timeout-minutes:
jobs:
  my-job:
    runs-on: ubuntu-latest
    timeout-minutes: 30  # ADD THIS LINE
    steps:
      ...
```

#### Step 3: Validate

```bash
# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/my-workflow.yml'))"

# Test with act (local testing)
act pull_request -j my-job
```

---

## Compliance Verification

### Automated Checks

Compliance is verified via:

1. **PR Gate**: `workflow-compliance-guardian`
   - Checks concurrency format
   - Verifies timeout settings
   - Blocks merge if non-compliant

2. **Health Monitor**: `workflow-health-monitor`
   - Alerts on compliance drift
   - Tracks timeout violations
   - Reports on cancellation rates

3. **CI Triage**: `ci-triage-pipeline-agent`
   - Routes non-compliant workflows
   - Suggests fixes
   - Provides remediation guidance

### Manual Verification

```bash
# Check all workflows for compliance
.codex/scripts/verify_workflow_compliance.sh

# Check specific workflow
grep -A2 "^concurrency:" .github/workflows/my-workflow.yml
grep "timeout-minutes:" .github/workflows/my-workflow.yml
```

---

## Troubleshooting

### Job timeout too aggressive

**Symptom**: Job gets cancelled even though it's still working  
**Solution**: Increase `timeout-minutes` (check logs to determine needed time)

```yaml
# Increase timeout
timeout-minutes: 45  # was 30
```

### Job timeout too lenient

**Symptom**: Stuck jobs consume runner hours  
**Solution**: Decrease `timeout-minutes` or add step-level timeouts

```yaml
- name: Long operation
  timeout-minutes: 20  # Add step timeout
  run: |
    long-running-command || exit 1
```

### Concurrency cancelling deployments

**Symptom**: Deployment gets cancelled when new code is pushed  
**Solution**: Set `cancel-in-progress: false`

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.head_ref || github.ref }}
  cancel-in-progress: false  # Don't cancel deployment workflows
```

### Duplicate workflow runs

**Symptom**: Same workflow runs multiple times for one commit  
**Solution**: Verify concurrency group is correctly formatted

```yaml
# Correct format (includes workflow and branch)
concurrency:
  group: ${{ github.workflow }}-${{ github.head_ref || github.ref }}
  
# Incorrect (just workflow name):
# concurrency: ${{ github.workflow }}
```

---

## References

- **GitHub Docs**: [Using Concurrency](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#concurrency)
- **GitHub Docs**: [Job timeouts](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#jobsjob_idtimeout-minutes)
- **Phase 2 Baseline**: `.codex/PHASE_2_CONCURRENCY_BASELINE.json`
- **Deployment Report**: `.codex/PHASE_2_LANE_3_DEPLOYMENT_REPORT.md`

---

## Questions?

For questions or exceptions:
1. Check the troubleshooting section above
2. Review example workflows in `.github/workflows/` for working implementations
3. File an issue with `workflow-standards` label
4. Tag `@workflow-compliance-guardian` in PR comments

---

**Last Updated**: 2026-07-18  
**Version**: 1.0 (Phase 2 Lane 3)  
**Status**: ✅ In Effect
