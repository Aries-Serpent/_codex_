# Cognitive Registry Workflow Operational Guide

**Version:** 1.0.0  
**Last Updated:** 2026-06-20  
**Status:** Active

---

## Overview

The Cognitive Registry Validation Workflow is a GitHub Actions workflow that automates registry configuration validation, connectivity testing, and credential injection approval. It integrates with the Cognitive Brain pattern recognition system to ensure registry configurations meet best practices before deployment.

---

## Workflow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Workflow Input (Manual Dispatch)                            │
├─────────────────────────────────────────────────────────────┤
│ • Registry Type (dockerhub, ghcr, private, ecr, gcr)       │
│ • Registry Endpoint URL                                     │
│ • Namespace/Organization Name                              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Job 1: Validate Registry Configuration                      │
├─────────────────────────────────────────────────────────────┤
│ • Query Cognitive Brain patterns                            │
│ • Run validation script against patterns                    │
│ • Calculate confidence score                                │
│ • Upload validation results                                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
              ┌─────────────┴─────────────┐
              ↓ (if valid ≥ 0.80)         ↓ (if invalid)
    ┌──────────────────────┐      ┌──────────────────┐
    │ Job 2: Test          │      │ Job 3: Approval  │
    │ Connectivity         │      │ Gate (Fail)      │
    │                      │      └──────────────────┘
    │ • Run 5 connectivity │
    │   tests              │
    │ • Upload results     │
    └──────────────────────┘
              ↓ (if all pass)
    ┌──────────────────────┐
    │ Job 4: Approval Gate │
    │ • Manual review req  │
    │ • Summary report     │
    └──────────────────────┘
              ↓
    ┌──────────────────────┐
    │ Job 5: Store Vars    │
    │ • Store in repo vars │
    │ • Update metadata    │
    └──────────────────────┘
              ↓
    ┌──────────────────────┐
    │ Job 6: Webhook       │
    │ • Notify CB          │
    │ • Send payload       │
    └──────────────────────┘
              ↓
    ┌──────────────────────┐
    │ Job 7: Summary       │
    │ • Report results     │
    │ • Save artifacts     │
    └──────────────────────┘
```

---

## Triggering the Workflow

### Manual Dispatch

The workflow is triggered manually via GitHub Actions UI:

1. Go to **Actions** tab
2. Select **Cognitive Registry Validation Workflow**
3. Click **Run workflow**
4. Enter inputs:
   - **registry_type:** Select from (dockerhub, ghcr, private, ecr, gcr)
   - **registry_endpoint:** Full endpoint URL
   - **namespace:** Organization/team namespace

### Example Trigger (GitHub CLI)

```bash
gh workflow run cognitive-registry-validation.yml \
  -f registry_type=ghcr \
  -f registry_endpoint=ghcr.io \
  -f namespace=myorg/myteam
```

---

## Workflow Jobs

### Job 1: Validate Registry Configuration

**Purpose:** Validate configuration against Cognitive Brain patterns

**Steps:**
1. Checkout repository
2. Set up Python 3.12
3. Query Cognitive Brain for patterns
4. Run validation script
5. Extract confidence score
6. Upload results to artifacts

**Outputs:**
- `validation_confidence`: Confidence score (0.0-1.0)
- `validation_valid`: Boolean (true/false)
- `validation_issues`: Number of issues found

**Success Criteria:**
- Confidence score ≥ 0.80
- No critical validation failures
- Configuration meets pattern requirements

**Artifacts:**
- `validation_output.json` - Detailed validation results
- `patterns_output.json` - Queried patterns

---

### Job 2: Test Registry Connectivity

**Purpose:** Test registry endpoint and authentication

**Triggers:**
- Only runs if validation succeeds (confidence ≥ 0.80)

**Steps:**
1. Checkout repository
2. Set up Python 3.12
3. Create test configuration
4. Run connectivity tests
5. Extract test results
6. Upload to artifacts

**Outputs:**
- `connectivity_status`: "passed" or "failed"
- `connectivity_tests_passed`: Number of passed tests

**Tests Performed:**
1. DNS resolution
2. Endpoint availability (HTTPS)
3. Authentication verification
4. Image pull permission
5. Image push permission

**Artifacts:**
- `connectivity_output.json` - Test results

---

### Job 3: Approval Gate

**Purpose:** Request manual approval for credential injection

**Triggers:**
- Runs if both validation and connectivity succeed

**Actions:**
1. Display configuration summary
2. Show validation results
3. Show connectivity test results
4. Request manual review
5. Provide next steps

**Manual Review Checklist:**
- [ ] Registry type correct
- [ ] Endpoint URL verified
- [ ] Namespace appropriate
- [ ] Validation confidence acceptable
- [ ] All connectivity tests passed
- [ ] Ready for credential injection

---

### Job 4: Store Repository Variables

**Purpose:** Store registry metadata in GitHub repository variables

**Variables Stored:**
- `REGISTRY_TYPE` - Registry type (dockerhub, ghcr, etc.)
- `REGISTRY_ENDPOINT` - Endpoint URL
- `REGISTRY_NAMESPACE` - Namespace/organization
- `REGISTRY_VALIDATION_STATUS` - "valid" (if validation passed)
- `REGISTRY_LAST_VALIDATED` - ISO 8601 timestamp

**Access in Other Workflows:**
```yaml
- name: Use registry variables
  run: |
    echo "Registry Type: ${{ vars.REGISTRY_TYPE }}"
    echo "Endpoint: ${{ vars.REGISTRY_ENDPOINT }}"
```

---

### Job 5: Webhook Notification

**Purpose:** Notify Cognitive Brain of validation completion

**Webhook Payload Structure:**
```json
{
  "event": "registry_validation_complete",
  "registry_type": "ghcr",
  "endpoint": "ghcr.io",
  "namespace": "myorg/myteam",
  "validation_confidence": 0.95,
  "connectivity_status": "passed",
  "timestamp": "2026-06-20T09:35:04Z",
  "repository": "owner/repo",
  "run_id": "1234567890"
}
```

**Webhook Configuration:**
1. Set `COGNITIVE_BRAIN_WEBHOOK_URL` in repository secrets
2. Set `WEBHOOK_SECRET` for HMAC-SHA256 signing
3. Webhook will be sent on validation completion

**Webhook Signature:**
- Uses HMAC-SHA256 algorithm
- Header: `X-Webhook-Signature`
- Format: `sha256=<signature>`

---

### Job 6: Workflow Summary

**Purpose:** Generate comprehensive summary of workflow execution

**Summary Includes:**
- Registry configuration (type, endpoint, namespace)
- Validation results (confidence, validity, issues)
- Connectivity test results (status, tests passed)
- Workflow job statuses
- Next steps

**Artifacts:**
- `workflow-summary.md` - Complete summary

---

## Workflow Variables & Secrets

### Required Environment Variables
```yaml
REGISTRY_TYPE: Registry type (input)
REGISTRY_ENDPOINT: Endpoint URL (input)
REGISTRY_NAMESPACE: Namespace (input)
```

### Required Secrets (Optional)
```yaml
COGNITIVE_BRAIN_WEBHOOK_URL: Webhook endpoint for Cognitive Brain
WEBHOOK_SECRET: Secret for webhook HMAC signing
```

### Generated Variables
After successful completion:
```yaml
REGISTRY_TYPE: Stored in repository variables
REGISTRY_ENDPOINT: Stored in repository variables
REGISTRY_NAMESPACE: Stored in repository variables
REGISTRY_VALIDATION_STATUS: "valid"
REGISTRY_LAST_VALIDATED: Timestamp of last validation
```

---

## Permissions

The workflow requires:
- `contents: read` - Read repository files
- `checks: write` - Create check runs
- `pull-requests: write` - Comment on pull requests

---

## Artifacts

All workflow runs generate artifacts (30-day retention):

| Artifact | Contents | Usage |
|----------|----------|-------|
| validation-results | Validation and pattern data | Review validation process |
| connectivity-results | Connectivity test results | Verify registry access |
| workflow-summary | Complete execution summary | Document validation run |

### Accessing Artifacts
```bash
# List artifacts from latest run
gh run list --workflow cognitive-registry-validation.yml --limit 1

# Download specific artifact
gh run download <run-id> -n validation-results
```

---

## Success Paths

### Path 1: Full Success
```
Validation (✅) → Connectivity (✅) → Approval Gate → Variables (✅) → Webhook (✅)
```
- All validation checks passed
- All connectivity tests passed
- Configuration ready for deployment
- Metadata stored in repository
- Cognitive Brain notified

### Path 2: Validation Failure
```
Validation (❌) → Blocked
```
- Configuration does not meet requirements
- Confidence score below 0.80
- Required fixes documented
- No further steps executed

### Path 3: Connectivity Failure
```
Validation (✅) → Connectivity (❌) → Blocked
```
- Configuration valid
- Registry not accessible
- Connectivity issues documented
- Manual investigation required

---

## Troubleshooting

### Validation Fails (Confidence < 0.80)

**Possible Causes:**
- Missing required fields in configuration
- Invalid endpoint URL format
- Unsupported authentication method
- Security settings not enabled

**Resolution:**
1. Review validation output
2. Check specific failed checks
3. Implement recommended fixes
4. Re-run workflow

**Details:**
```json
{
  "issues": [
    {
      "check": "Required Fields Check",
      "details": {
        "missing": ["field_name"]
      }
    }
  ],
  "recommendations": [
    "Provide all required configuration fields"
  ]
}
```

### Connectivity Tests Fail

**Possible Causes:**
- Registry endpoint unreachable
- Invalid credentials
- Firewall blocking connections
- Network issues

**Resolution:**
1. Verify endpoint URL is correct
2. Test DNS resolution: `nslookup <endpoint>`
3. Test connectivity: `curl -I https://<endpoint>`
4. Check credentials are valid
5. Verify network access

---

## Integration with Deployments

### Using Validated Registry in Workflows

After successful validation, use registry variables in other workflows:

```yaml
name: Deploy with Validated Registry

on: push

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Use registry configuration
        env:
          REGISTRY_TYPE: ${{ vars.REGISTRY_TYPE }}
          REGISTRY_ENDPOINT: ${{ vars.REGISTRY_ENDPOINT }}
          REGISTRY_NAMESPACE: ${{ vars.REGISTRY_NAMESPACE }}
        run: |
          echo "Deploying to $REGISTRY_TYPE registry"
          echo "Endpoint: $REGISTRY_ENDPOINT"
          echo "Namespace: $REGISTRY_NAMESPACE"
```

### Pre-Deployment Validation

Ensure registry validation is current before deployment:

```yaml
- name: Check registry validation
  run: |
    LAST_VALIDATED=$(gh variable get REGISTRY_LAST_VALIDATED)
    HOURS_AGO=$(( ($(date +%s) - $(date -d "$LAST_VALIDATED" +%s)) / 3600 ))
    
    if [ $HOURS_AGO -gt 24 ]; then
      echo "ERROR: Registry not validated in last 24 hours"
      exit 1
    fi
```

---

## Best Practices

### Before Running Workflow
1. ✅ Verify registry endpoint is correct
2. ✅ Ensure registry type is supported
3. ✅ Confirm namespace exists
4. ✅ Check credentials are valid
5. ✅ Configure webhook secrets if needed

### During Workflow
1. ✅ Monitor workflow execution
2. ✅ Review any warnings
3. ✅ Check artifact outputs
4. ✅ Verify all steps complete

### After Workflow
1. ✅ Review validation results
2. ✅ Verify connectivity tests passed
3. ✅ Check repository variables are set
4. ✅ Confirm webhook notification received
5. ✅ Use registry in deployments

---

## Performance

### Expected Execution Time
- Validation: ~30 seconds
- Connectivity Tests: ~10 seconds
- Variable Storage: ~5 seconds
- Webhook Notification: ~2 seconds
- **Total: ~50-60 seconds**

### Optimization Tips
- Parallel job execution reduces overall time
- Caching Python dependencies speeds setup
- Artifact upload runs in background

---

## Maintenance & Updates

**Last Updated:** 2026-06-20  
**Review Frequency:** Quarterly  
**Next Review:** 2026-09-20

**Maintainer:** Cognitive Brain Registry Team  
**Escalation:** @mbaetiong

---

## Related Tasks

- Task 4.1: Cognitive Brain Registry Pattern Query
- Task 4.2: Registry Validation Against Patterns
- Task 4.3: Registry Connectivity Testing
- Task 4.5: Webhook Integration & Repository Variables
