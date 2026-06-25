# Automated Verification Workflow Guide

## Overview

The `automated-post-deployment-verification.yml` workflow provides automated post-deployment verification procedures that validate successful deployment across all environments.

**File Location:** `.github/workflows/automated-post-deployment-verification.yml`

**Purpose:** Automate the verification checklist and provide rapid go/no-go decisions after deployment.

## Quick Start

### Manual Trigger

1. Go to **Actions** tab in GitHub repository
2. Select **Automated Post-Deployment Verification** workflow
3. Click **Run workflow**
4. Fill in parameters:
   - **Environment:** development, staging, or production
   - **Service URL:** Full URL to deployed service (e.g., http://api.example.com)
   - **Notify Slack:** Check to send results to Slack
5. Click **Run workflow**

### Programmatic Trigger

```bash
# Trigger workflow via GitHub CLI
gh workflow run automated-post-deployment-verification.yml \
  -f environment=staging \
  -f service_url=http://staging-api.example.com \
  -f notify_slack=true
```

## Workflow Structure

### Jobs

#### 1. Setup Job
**Validates inputs and prepares environment**

- Validates environment parameter (development, staging, production)
- Validates service URL format
- Selects appropriate verification checklist
- Duration: ~10 seconds

#### 2. Service Startup Job
**Verifies service is accessible and responding**

- Attempts to reach service URL
- Retries up to 5 times with 10-second delays
- Duration: ~30 seconds

#### 3. Health Checks Job
**Runs comprehensive health checks**

- Calls `/health` endpoint
- Calls `/mcp/v1/health` endpoint
- Generates JSON and markdown reports
- Uploads health check artifacts
- Duration: ~30 seconds

#### 4. Smoke Tests Job
**Runs lightweight smoke tests**

- Tests core functionality
- Validates API endpoints
- Tests error handling
- Duration: ~2-3 minutes

#### 5. Critical Path Tests Job
**Tests critical business paths**

- Validates authentication flow
- Validates data persistence
- Validates API request processing
- Duration: ~2-3 minutes

#### 6. Generate Report Job
**Consolidates results and generates report**

- Downloads all artifacts
- Generates verification report
- Comments on PR with results
- Determines go/no-go decision
- Duration: ~30 seconds

#### 7. Slack Notification Job
**Sends results to Slack (optional)**

- Posts results summary to Slack
- Includes links to detailed reports
- Only runs if enabled
- Duration: ~10 seconds

#### 8. Create Issue Job
**Creates tracking issue on failure**

- Creates GitHub issue if verification fails
- Labels issue for tracking
- Only runs on failure
- Duration: ~10 seconds

## Parameters

### environment (required)

**Type:** choice  
**Options:** development, staging, production  
**Default:** None

Specifies which environment to verify. This determines:
- Which checklist to use
- Success criteria applied
- Approval requirements

### service_url (required)

**Type:** string  
**Example:** http://api.example.com, https://staging-api.example.com:8000

Full URL to the deployed service. Must include protocol (http/https).

### notify_slack (optional)

**Type:** boolean  
**Default:** true

Whether to send Slack notification with results.

## Output Artifacts

### Health Check Report

**Location:** `health-check-report/`  
**Files:**
- `health_report_<timestamp>.json` - Full health check results
- `health_summary.md` - Human-readable summary
- `health_latest.json` - Latest results

**Retention:** 30 days

### Smoke Test Results

**Location:** `smoke-test-results/`  
**Files:**
- `smoke_tests_report.json` - Test results
- `smoke_summary.json` - Test summary

**Retention:** 30 days

### Critical Path Results

**Location:** `critical-path-results/`  
**Files:**
- `critical_paths_report.json` - Test results
- `critical_paths_summary.json` - Test summary

**Retention:** 30 days

### Verification Report

**Location:** `verification-report/`  
**Files:**
- `verification_report.md` - Main report
- `artifacts/` - All sub-reports

**Retention:** 30 days

## Decision Logic

The workflow automatically determines deployment readiness:

### Development

```
IF all checks pass → ✅ GO
ELSE → ⚠️ INVESTIGATE
```

### Staging

```
IF all checks pass
   AND error rate = 0%
   → ✅ GO
ELSE IF minor warnings
   → 🟡 CONDITIONAL
ELSE → ❌ NO-GO
```

### Production

```
IF all checks pass
   AND security checks verified
   AND stakeholders approved
   → ✅ GO
ELSE → ❌ NO-GO
```

## Environment Variables

The workflow uses these environment variables:

```yaml
VERIFICATION_DIR: .codex/verification-results
```

## Secrets

The workflow requires this secret for Slack notifications:

- `SLACK_WEBHOOK_URL` - Slack webhook for sending notifications

### Setting Up Slack Webhook

1. Create Slack app at https://api.slack.com/apps
2. Enable Incoming Webhooks
3. Create new webhook for your channel
4. Copy webhook URL
5. Add to GitHub as secret: `SLACK_WEBHOOK_URL`

```bash
gh secret set SLACK_WEBHOOK_URL -b "https://hooks.slack.com/services/..." <!-- pragma: allowlist secret -->
```

## Integration Points

### Continuous Integration

Integrate verification into CI/CD pipeline:

```yaml
# .github/workflows/release.yml
name: Release

on: [push, tags]

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - name: Build and deploy
        run: ./deploy.sh

      - name: Trigger verification
        run: |
          gh workflow run automated-post-deployment-verification.yml \
            -f environment=staging \
            -f service_url=http://staging-api.example.com
```

### Pull Request Verification

Add verification check to PR workflow:

```yaml
# .github/workflows/pr-checks.yml
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - name: Verify PR changes
        run: |
          gh workflow run automated-post-deployment-verification.yml \
            -f environment=development \
            -f service_url=http://localhost:8000
```

### Post-Release Hook

Trigger verification after release:

```bash
# In post-release webhook
curl -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/OWNER/REPO/actions/workflows/automated-post-deployment-verification.yml/dispatches \
  -d "{
    \"ref\": \"main\",
    \"inputs\": {
      \"environment\": \"production\",
      \"service_url\": \"https://api.example.com\",
      \"notify_slack\": \"true\"
    }
  }"
```

## Troubleshooting

### Workflow Fails at Setup

**Symptom:** Setup job fails with input validation error

**Check:**
- Environment is one of: development, staging, production
- Service URL starts with http:// or https://
- Service URL is reachable

**Fix:**
```bash
# Test service URL
curl -I http://api.example.com

# Retry workflow with correct parameters
```

### Service Accessibility Check Fails

**Symptom:** Workflow fails at "Check Service Accessibility"

**Cause:** Service is not running or unreachable

**Fix:**
1. Verify service is deployed and running
2. Check service URL is correct
3. Verify network connectivity
4. Check firewall/security groups
5. Retry workflow

### Health Check Endpoint Not Found

**Symptom:** Health check job shows "Endpoint not found"

**Cause:** Service doesn't have health endpoints implemented

**Fix:**
1. Implement `/health` endpoint in service
2. Implement `/mcp/v1/health` endpoint
3. Verify endpoints return 200 status
4. Update service and retry

### Smoke Tests Not Running

**Symptom:** Smoke tests job passes with no tests run

**Cause:** pytest not installed or tests not found

**Fix:**
1. Install test dependencies: `pip install pytest`
2. Verify test files exist: `tests/e2e/smoke_tests.py`
3. Run tests locally to verify: `pytest tests/e2e/smoke_tests.py -v`
4. Retry workflow

### Slack Notification Not Sent

**Symptom:** Workflow completes but no Slack message appears

**Cause:** Webhook not configured or malformed

**Fix:**
1. Verify `SLACK_WEBHOOK_URL` secret is set: `gh secret list | grep SLACK`
2. Test webhook manually:
   ```bash
   curl -X POST -H 'Content-type: application/json' \
     --data '{"text":"test"}' \
     $SLACK_WEBHOOK_URL
   ```
3. Check webhook URL format: should start with `https://hooks.slack.com/` <!-- pragma: allowlist secret -->
4. Update secret if needed: `gh secret set SLACK_WEBHOOK_URL`

### Artifacts Not Available

**Symptom:** "Download Artifacts" fails with 404

**Cause:** Previous jobs didn't upload artifacts

**Fix:**
1. Check earlier jobs for errors
2. Verify artifact upload step completed
3. Check artifact retention settings
4. Re-run workflow

## Advanced Usage

### Custom Checklist

To use custom verification steps, modify the workflow:

```yaml
- name: Run Custom Verification
  run: |
    # Add custom verification logic
    ./scripts/custom_verify.sh ${{ needs.setup.outputs.service_url }}
```

### Conditional Approval

Add approval gate for production:

```yaml
- name: Request Approval for Production
  if: needs.setup.outputs.environment == 'production'
  uses: actions/github-script@v7
  with:
    script: |
      // Create approval request
      github.rest.issues.create({
        owner: context.repo.owner,
        repo: context.repo.repo,
        title: 'Deployment Approval Required',
        body: 'Please approve production deployment'
      });
```

### Parallel Verification

Run verifications in parallel for faster feedback:

```yaml
jobs:
  verify:
    strategy:
      matrix:
        check: [health, smoke, critical]
      max-parallel: 3
```

## Performance

**Typical Execution Times:**

| Environment | Total Time |
|-------------|-----------|
| Development | 5-7 minutes |
| Staging | 8-10 minutes |
| Production | 10-15 minutes |

**Optimization Tips:**
- Run jobs in parallel when possible
- Cache test dependencies
- Use smaller test data sets
- Increase concurrent job limits

## Security Considerations

1. **Secrets Management**
   - Store API credentials as secrets
   - Never log secrets in workflow output
   - Rotate secrets regularly

2. **Access Control**
   - Require approval for production verification
   - Audit all verification results
   - Restrict who can trigger workflows

3. **Data Protection**
   - Artifacts expire after 30 days
   - Don't store sensitive data in artifacts
   - Encrypt logs if needed

## Related Documentation

- [SUCCESS_CRITERIA_BY_ENVIRONMENT.md](../SUCCESS_CRITERIA_BY_ENVIRONMENT.md)
- [GO_NO_GO_DECISION_MATRIX.md](../GO_NO_GO_DECISION_MATRIX.md)
- [HEALTH_CHECK_PROCEDURES.md](../HEALTH_CHECK_PROCEDURES.md)
- [SMOKE_TEST_GUIDE.md](../SMOKE_TEST_GUIDE.md)

## Support

For workflow issues:
- Check Action logs: GitHub Actions tab → Workflow run
- Review job output: Click failing job for details
- Check artifacts: Download artifact for full reports
- Contact: #devops on Slack
