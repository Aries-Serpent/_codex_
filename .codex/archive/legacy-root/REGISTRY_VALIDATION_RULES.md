# Registry Validation Rules

**Version:** 1.0.0  
**Last Updated:** 2026-06-20  
**Status:** Active

---

## Overview

This document defines the validation rules used to check registry configurations against discovered patterns and best practices. Each rule has a name, description, weight in the overall confidence calculation, and specific acceptance criteria.

---

## Validation Rules

### Rule 1: Required Fields Check

**Name:** Required Fields Check  
**Weight:** 0.25 (25% of total score)  
**Priority:** Critical

**Description:**
Validates that all required fields for the registry type are present in the configuration.

**Implementation:**
```python
Required fields per registry type:
- dockerhub: ["username", "password"]
- ghcr: ["github_token", "github_user"]
- private: ["endpoint", "username", "password"]
- ecr: ["aws_account_id", "aws_region"]
- gcr: ["service_account_key", "project_id"]
```

**Acceptance Criteria:**
- All required fields must be present
- Fields must not be empty strings
- Field values must be non-null

**Pass Condition:** `missing_fields.length == 0`

**Remediation:**
If this check fails:
1. Verify all required fields are defined in configuration
2. Check that credentials are properly loaded from environment or secrets
3. Ensure no typos in field names

---

### Rule 2: Endpoint Check

**Name:** Endpoint Check  
**Weight:** 0.20 (20% of total score)  
**Priority:** High

**Description:**
Validates that the registry endpoint URL is valid and matches the expected pattern for the registry type.

**Implementation:**
```python
Validation patterns:
- dockerhub: Must be "docker.io"
- ghcr: Must be "ghcr.io"
- private: Must match pattern or be custom
- ecr: Must match "*.dkr.ecr.*.amazonaws.com"
- gcr: Must be "gcr.io"
```

**Acceptance Criteria:**
- Endpoint must be provided and non-empty
- Endpoint must match registry-specific pattern
- Endpoint must be resolvable (DNS check recommended)
- Endpoint must be accessible via HTTPS

**Pass Condition:** `endpoint_matches_pattern && endpoint_not_empty`

**Remediation:**
If this check fails:
1. Verify registry endpoint URL is correct
2. Check DNS resolution: `nslookup <endpoint>`
3. Test connectivity: `curl -I https://<endpoint>`
4. Verify registry type matches endpoint

---

### Rule 3: Authentication Method Check

**Name:** Authentication Method Check  
**Weight:** 0.15 (15% of total score)  
**Priority:** High

**Description:**
Validates that the authentication method matches the expected method for the registry type.

**Implementation:**
```python
Expected authentication methods:
- dockerhub: "username_password"
- ghcr: "github_token"
- private: "http_basic_or_oauth2"
- ecr: "iam_role_or_access_key"
- gcr: "service_account_key"
```

**Acceptance Criteria:**
- Authentication method must be explicitly defined
- Must match the registry type's expected method
- Multiple methods allowed for flexible registries (private, ecr)

**Pass Condition:** `auth_method in expected_methods[registry_type]`

**Remediation:**
If this check fails:
1. Review registry type specification
2. Update authentication method to match registry type
3. Verify credentials are provided for the correct method
4. Check GitHub Secrets or environment variables

---

### Rule 4: Credentials Storage Check

**Name:** Credentials Storage Check  
**Weight:** 0.20 (20% of total score)  
**Priority:** Critical

**Description:**
Validates that credentials are provided and are being stored securely (in GitHub Secrets or environment variables, not in code).

**Implementation:**
```python
Validation flags:
- credentials_provided: True (must not be False)
- credentials_in_code: False (must not be True)
- credentials_in_env_or_secrets: True (must be True)
```

**Acceptance Criteria:**
- `credentials_provided` flag must be True
- Credentials must not appear in configuration files
- Credentials must be loaded from:
  - GitHub Secrets (`${{ secrets.REGISTRY_CREDS }}`)
  - Environment variables (`$REGISTRY_PASSWORD`)
  - GitHub Actions secrets context

**Pass Condition:** `credentials_provided == True && credentials_not_in_code`

**Remediation:**
If this check fails:
1. Remove credentials from configuration files
2. Store credentials in GitHub Secrets
3. Update workflows to use `${{ secrets.* }}`
4. Use `--mask-logs` to prevent credential leaks
5. Never commit `.env` files with credentials

**Security Note:**
```yaml
DO NOT:
❌ Store credentials in config files
❌ Commit .env files
❌ Print credentials to logs
❌ Use credentials in unmasked steps

DO:
✅ Store in GitHub Secrets
✅ Reference as ${{ secrets.CREDS }}
✅ Use GitHub Actions masking
✅ Rotate credentials regularly
```

---

### Rule 5: Namespace Structure Check

**Name:** Namespace Structure Check  
**Weight:** 0.10 (10% of total score)  
**Priority:** Medium

**Description:**
Validates that the namespace/organization structure is properly defined according to registry standards.

**Implementation:**
```python
Expected namespace structures:
- dockerhub: "username/imagename"
- ghcr: "ghcr.io/owner/imagename"
- private: "registry.company.internal/team/imagename"
- ecr: "account.dkr.ecr.region.amazonaws.com/imagename"
- gcr: "gcr.io/project-id/imagename"
```

**Acceptance Criteria:**
- Namespace must be provided and non-empty
- Namespace must follow registry-specific format
- Organization/team/project prefix must be present
- Image name component must be valid

**Pass Condition:** `namespace_provided && namespace_format_valid`

**Remediation:**
If this check fails:
1. Verify namespace format matches registry type
2. Ensure organization/team prefix is included
3. Check image naming conventions (lowercase, hyphens, underscores only)
4. Review registry's namespace documentation

---

### Rule 6: Security Settings Check

**Name:** Security Settings Check  
**Weight:** 0.10 (10% of total score)  
**Priority:** Medium

**Description:**
Validates that recommended security features are enabled for the registry type.

**Implementation:**
```python
Required security features:
- dockerhub: image_scanning_enabled, content_trust_enabled
- ghcr: ghas_scanning_enabled, container_signing_enabled
- private: tls_enabled, authentication_enabled
- ecr: image_scanning_enabled, kms_encryption_enabled
- gcr: binary_authorization_enabled, artifact_analysis_enabled
```

**Acceptance Criteria:**
- At least one recommended security feature must be enabled
- TLS/HTTPS must be enabled for all registries
- Vulnerability scanning should be enabled
- Image signing/verification recommended

**Pass Condition:** `enabled_security_features.length > 0`

**Remediation:**
If this check fails:
1. Enable image vulnerability scanning
2. Activate image signing/verification
3. Enable TLS/HTTPS encryption
4. Configure authentication properly
5. Review registry's security documentation

---

## Confidence Score Calculation

**Formula:**
```
confidence = sum(check_weight × (1.0 if passed else 0.0)) / sum(all_weights)
```

**Score Interpretation:**

| Score | Status | Recommendation |
|-------|--------|-----------------|
| 1.0 | Perfect | Approved for production |
| 0.90-0.99 | Excellent | Approved for production |
| 0.80-0.89 | Good | Approved; minor issues |
| 0.70-0.79 | Fair | Manual review required |
| <0.70 | Poor | Reject; requires fixes |

**Default Threshold:** 0.80 (80% confidence)
- Configurations scoring 0.80+ are approved
- Configurations scoring <0.80 require manual review or fixes

---

## Validation Workflow

### 1. Configuration Input
```python
config = {
    "registry_type": "ghcr",
    "endpoint": "ghcr.io",
    "github_token": "***",
    "namespace": "org/imagename",
    "authentication_method": "github_token",
    "credentials_provided": True,
    "ghas_scanning_enabled": True,
}
```

### 2. Check Execution
Each rule is evaluated independently:
- Check 1: Required Fields
- Check 2: Endpoint
- Check 3: Authentication Method
- Check 4: Credentials Storage
- Check 5: Namespace Structure
- Check 6: Security Settings

### 3. Result Compilation
```python
result = {
    "valid": confidence >= threshold,
    "confidence": 0.85,
    "checks": [
        {"name": "...", "passed": True, "weight": 0.25},
        ...
    ],
    "issues": [...],
    "recommendations": [...],
}
```

### 4. Decision
- **Approved:** confidence >= 0.80
- **Manual Review:** 0.70 <= confidence < 0.80
- **Rejected:** confidence < 0.70

---

## Integration with Other Components

### Task 4.2: Validation Script
- Uses these rules to check configurations
- Returns detailed check results
- Provides confidence scores

### Task 4.3: Connectivity Testing
- Uses validated endpoint and credentials
- Skips testing if endpoint check fails
- Attempts re-validation after fixes

### Task 4.4: Workflow Template
- Calls validator before testing
- Uses validation result in approval gate
- Implements confidence threshold in workflow

### Task 4.5: Webhook Integration
- Reports validation results to Cognitive Brain
- Tracks which rules pass/fail over time
- Enables pattern learning

---

## Extensibility

### Adding New Rules
To add a new validation rule:

1. Define rule metadata (name, weight, priority)
2. Implement check function
3. Add to `_run_checks()` method
4. Test with sample configurations
5. Update documentation
6. Update weights if necessary

### Custom Thresholds
Organizations can customize:
- Confidence threshold (currently 0.80)
- Rule weights (total must equal 1.0)
- Required security features
- Endpoint patterns

---

## Examples

### Example 1: GHCR Configuration (Passing)
```json
{
  "registry_type": "ghcr",
  "endpoint": "ghcr.io",
  "github_token": "ghs_***",
  "github_user": "octocat",
  "namespace": "myorg/myimage",
  "authentication_method": "github_token",
  "credentials_provided": true,
  "ghas_scanning_enabled": true,
  "container_signing_enabled": true
}
```
**Expected Result:** ✅ confidence: 0.95, valid: true

### Example 2: ECR Configuration (Partial)
```json
{
  "registry_type": "ecr",
  "endpoint": "123456789.dkr.ecr.us-east-1.amazonaws.com",
  "aws_account_id": "123456789",
  "aws_region": "us-east-1",
  "namespace": "myteam/myimage",
  "authentication_method": "iam_role",
  "credentials_provided": true
}
```
**Expected Result:** ⚠️ confidence: 0.85, valid: true (security features not enabled)

### Example 3: Configuration (Failing)
```json
{
  "registry_type": "private",
  "endpoint": "registry.internal",
  "authentication_method": "oauth2"
}
```
**Expected Result:** ❌ confidence: 0.60, valid: false (missing credentials)

---

## Testing

### Running Validation Tests
```bash
# Run validation script
python scripts/cognitive/validate_registry_config.py

# Validate specific configuration
python scripts/cognitive/validate_registry_config.py --config config.json

# Generate validation report
python scripts/cognitive/validate_registry_config.py --report validation_report.json
```

---

## Maintenance

**Last Updated:** 2026-06-20T09:33:38Z  
**Review Frequency:** Quarterly  
**Next Review:** 2026-09-20

**Maintainer:** Cognitive Brain Registry Team  
**Escalation:** @mbaetiong
