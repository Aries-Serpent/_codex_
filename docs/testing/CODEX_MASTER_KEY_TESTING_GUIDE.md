# Testing CODEX_MASTER_KEY: Comprehensive Guide
**Last Updated:** 2026-07-11
**Version:** v0.2.0

> **Version:** 1.0.0
> **Last Updated: 2026-06-29
> **Author:** GitHub Copilot Agent
> **Scope:** 10 GitHub API processes, 20+ GitHub API endpoints, all CODEX_MASTER_KEY scopes

---

## Overview

This guide documents the comprehensive test suite for GitHub API processes that leverage **CODEX_MASTER_KEY**, a GitHub Personal Access Token (PAT) with the following scopes:

- `repo` — Full repository control
- `workflow` — GitHub Actions management
- `security_events` — Security event read/write
- `admin:org` — Organization control
- `admin:repo_hook` — Repository hooks
- `admin:org_hook` — Organization hooks
- `packages` — Package management
- `user` — User profile data
- `codespace` — Codespaces management
- `audit_log` — Audit log access
- And 10+ additional scopes

---

## Top 10 Processes Tested

### 1⃣ Repository Variables Management

**Scope Required:** `repo`

**What it tests:**
- Creating, reading, updating, deleting repository-level variables
- Pagination and filtering
- Variable size limits (1,000 character maximum)
- Concurrent access and race conditions
- Proper error handling (404, 422, etc.)

**Key APIs:**
```
GET    /repos/{owner}/{repo}/actions/variables
GET    /repos/{owner}/{repo}/actions/variables/{name}
POST   /repos/{owner}/{repo}/actions/variables
PATCH  /repos/{owner}/{repo}/actions/variables/{name}
DELETE /repos/{owner}/{repo}/actions/variables/{name}
```

**Test File:** `tests/github/test_variables_comprehensive.py`

---

### 2⃣ Organization Variables Management

**Scope Required:** `admin:org`

**What it tests:**
- Creating organization-level variables
- Updating repository scope for variables
- Adding/removing repository access
- Variable precedence (org > repo)
- Scope restrictions and validation

**Key APIs:**
```
GET    /orgs/{org}/actions/variables
POST   /orgs/{org}/actions/variables
PATCH  /orgs/{org}/actions/variables/{name}
DELETE /orgs/{org}/actions/variables/{name}
GET    /orgs/{org}/actions/variables/{name}/repositories
PUT    /orgs/{org}/actions/variables/{name}/repositories
```

**Test File:** `tests/github/test_variables_comprehensive.py`

---

### 3⃣ Repository Secrets Management (Actions)

**Scope Required:** `repo`

**What it tests:**
- Fetching GitHub's public key
- Creating/updating secrets with sodium encryption
- Listing secrets (without values)
- Deleting secrets
- HMAC-SHA256 payload verification

**Key APIs:**
```
GET    /repos/{owner}/{repo}/actions/secrets/public-key
GET    /repos/{owner}/{repo}/actions/secrets
GET    /repos/{owner}/{repo}/actions/secrets/{name}
PUT    /repos/{owner}/{repo}/actions/secrets/{name}
DELETE /repos/{owner}/{repo}/actions/secrets/{name}
```

**Test File:** `tests/github/test_secrets_management_comprehensive.py`

---

### 4⃣ Organization Secrets Management (Actions)

**Scope Required:** `admin:org`

**What it tests:**
- Org-level secret CRUD operations
- Repository selection for secret scope
- Adding/removing repository access
- Org-repo secret precedence
- Scope and isolation validation

**Key APIs:**
```
GET    /orgs/{org}/actions/secrets
GET    /orgs/{org}/actions/secrets/{name}
PUT    /orgs/{org}/actions/secrets/{name}
DELETE /orgs/{org}/actions/secrets/{name}
GET    /orgs/{org}/actions/secrets/{name}/repositories
PUT    /orgs/{org}/actions/secrets/{name}/repositories
```

**Test File:** `tests/github/test_secrets_management_comprehensive.py`

---

### 5⃣ Dependabot Secrets Management

**Scope Required:** `repo`

**What it tests:**
- Creating Dependabot-specific secrets
- Encryption with Dependabot public key
- Isolation from Actions secrets
- Dependabot API specific behavior

**Key APIs:**
```
GET    /repos/{owner}/{repo}/dependabot/secrets/public-key
GET    /repos/{owner}/{repo}/dependabot/secrets
PUT    /repos/{owner}/{repo}/dependabot/secrets/{name}
DELETE /repos/{owner}/{repo}/dependabot/secrets/{name}
```

**Test File:** `tests/github/test_secrets_management_comprehensive.py`

---

### 6⃣ Codespaces Secrets Management

**Scope Required:** `codespace`

**What it tests:**
- Creating codespace-specific secrets
- User-level vs repo-level secrets
- Secret injection into codespace environments
- Codespace lifecycle management

**Key APIs:**
```
GET    /repos/{owner}/{repo}/codespaces/secrets/public-key
GET    /repos/{owner}/{repo}/codespaces/secrets
PUT    /repos/{owner}/{repo}/codespaces/secrets/{name}
DELETE /repos/{owner}/{repo}/codespaces/secrets/{name}
```

**Test File:** `tests/github/test_secrets_management_comprehensive.py`

---

### 7⃣ Workflow Dispatch & Execution

**Scope Required:** `workflow`

**What it tests:**
- Triggering workflow runs via API
- Passing input parameters
- Monitoring workflow execution status
- Canceling running workflows
- Querying workflow artifacts

**Key APIs:**
```
POST   /repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches
GET    /repos/{owner}/{repo}/actions/runs/{run_id}
POST   /repos/{owner}/{repo}/actions/runs/{run_id}/cancel
GET    /repos/{owner}/{repo}/actions/runs/{run_id}/artifacts
```

**Test File:** `tests/github/test_workflow_operations.py`

---

### 8⃣ Repository Hooks Management

**Scope Required:** `admin:repo_hook`

**What it tests:**
- Creating webhooks with custom events
- Updating hook configuration
- Deleting webhooks
- Testing webhook delivery
- Validating webhook payload signatures (HMAC-SHA256)

**Key APIs:**
```
GET    /repos/{owner}/{repo}/hooks
POST   /repos/{owner}/{repo}/hooks
GET    /repos/{owner}/{repo}/hooks/{hook_id}
PATCH  /repos/{owner}/{repo}/hooks/{hook_id}
DELETE /repos/{owner}/{repo}/hooks/{hook_id}
POST   /repos/{owner}/{repo}/hooks/{hook_id}/tests
```

**Test File:** `tests/github/test_webhook_management.py`

---

### 9⃣ Organization Hooks Management

**Scope Required:** `admin:org_hook`

**What it tests:**
- Creating org-wide webhooks
- Managing hooks across org repositories
- Updating hook delivery settings
- Monitoring hook delivery status
- Org-level event filtering

**Key APIs:**
```
GET    /orgs/{org}/hooks
POST   /orgs/{org}/hooks
GET    /orgs/{org}/hooks/{hook_id}
PATCH  /orgs/{org}/hooks/{hook_id}
DELETE /orgs/{org}/hooks/{hook_id}
POST   /orgs/{org}/hooks/{hook_id}/tests
```

**Test File:** `tests/github/test_webhook_management.py`

---

### Audit Log Access & Querying

**Scope Required:** `audit_log`

**What it tests:**
- Querying audit log entries
- Filtering by action, actor, date range
- Pagination through audit events
- Log retention and archival
- Parsing audit event payloads

**Key APIs:**
```
GET    /orgs/{org}/audit-log
GET    /enterprises/{enterprise}/audit-log
```

**Test File:** `tests/github/test_audit_log_access.py`

---

## Helper Scripts & Utilities

### `scripts/ci/_secrets_encryption_helper.py`

Provides utilities for encrypting secrets using GitHub's public key (libsodium).

**Key Functions:**
- `encrypt_secret()` — Encrypt secret with GitHub public key
- `validate_public_key()` — Validate key format and size
- `compute_webhook_signature()` — Compute HMAC-SHA256
- `validate_webhook_signature()` — Validate webhook payload
- `encrypt_secret_mock()` — Mock encryption for testing

**Usage:**
```python
from scripts.ci._secrets_encryption_helper import encrypt_secret

encrypted = encrypt_secret(
    secret_value="my-token",
    public_key="base64_encoded_key_from_github",
    key_type="actions"
)
print(encrypted["encrypted_value"])
```

---

### `scripts/ci/_webhook_signature_validator.py`

Validates GitHub webhook signatures using HMAC-SHA256 with constant-time comparison.

**Key Classes:**
- `WebhookValidator` — Full webhook validation
- `WebhookSignatureError` — Raised on validation failure

**Usage:**
```python
from scripts.ci._webhook_signature_validator import WebhookValidator

validator = WebhookValidator("webhook_secret")
is_valid = validator.validate(
    payload=request.body,
    signature=request.headers.get("X-Hub-Signature-256")
)
```

---

### `scripts/ci/test_codex_master_key_scopes.py`

Validates that CODEX_MASTER_KEY has required scopes for all 10 processes.

**Usage:**
```bash
# Check scopes
python scripts/ci/test_codex_master_key_scopes.py

# Generate JSON report
python scripts/ci/test_codex_master_key_scopes.py --report-json scopes.json
```

---

## Test Coverage Matrix

### Scope Coverage

| Scope | Process | Test File | Status |
|-------|---------|-----------|--------|
| `repo` | 1, 3, 5 | `test_variables_comprehensive.py`, `test_secrets_management_comprehensive.py` | |
| `admin:org` | 2, 4 | `test_variables_comprehensive.py`, `test_secrets_management_comprehensive.py` | |
| `codespace` | 6 | `test_secrets_management_comprehensive.py` | |
| `workflow` | 7 | `test_workflow_operations.py` | |
| `admin:repo_hook` | 8 | `test_webhook_management.py` | |
| `admin:org_hook` | 9 | `test_webhook_management.py` | |
| `audit_log` | 10 | `test_audit_log_access.py` | |

### API Endpoint Coverage

- **50+** GitHub API endpoints tested
- **Happy path** tests for all operations
- **Error path** tests for edge cases (404, 403, 422, etc.)
- **Rate limiting** and retry logic validated
- **Pagination** tested for list operations

---

## Running the Tests

### Prerequisites

```bash
# Install test dependencies
pip install -e ".[dev]"
pip install PyNaCl  # For encryption tests
```

### Run All CODEX_MASTER_KEY Tests

```bash
# Set token
export GH_TOKEN=<CODEX_MASTER_KEY>

# Run all tests
pytest tests/github/test_variables_comprehensive.py \
        tests/github/test_secrets_management_comprehensive.py \
        tests/github/test_workflow_operations.py \
        tests/github/test_webhook_management.py \
        tests/github/test_audit_log_access.py \
        -v --cov=scripts/ci

# Or use the consolidated test suite
pytest tests/github/ -k "codex_master" -v
```

### Validate Scopes Before Testing

```bash
python scripts/ci/test_codex_master_key_scopes.py --report-json .codex/scope_report.json
```

---

## Security Considerations

### Token Exposure Prevention

1. **Never log tokens** — Always redact in output
2. **Use environment variables** — Not command-line arguments
3. **Validate signatures** — Always verify webhook payloads
4. **Expire tokens** — Rotate CODEX_MASTER_KEY regularly
5. **Audit access** — Review audit logs for suspicious activity

### Encryption Best Practices

1. **Use libsodium** — Not custom crypto
2. **Validate public keys** — Check size and format
3. **One-way operations** — GitHub decrypts server-side
4. **Constant-time comparison** — Prevent timing attacks

---

## Troubleshooting

### 403 Forbidden Errors

**Cause:** Token missing required scopes

**Solution:**
```bash
python scripts/ci/test_codex_master_key_scopes.py
# Check which scopes are missing
# Update CODEX_MASTER_KEY with the missing scopes
```

### 401 Unauthorized

**Cause:** Invalid or expired token

**Solution:**
```bash
# Verify token is set correctly
echo $CODEX_MASTER_KEY | head -c 20

# Regenerate token if expired
# Update CODEX_MASTER_KEY in GitHub secrets
```

### Rate Limiting (429)

**Cause:** Too many API calls in short time

**Solution:**
1. Implement backoff in tests
2. Use cached responses when possible
3. Run tests with `--tb=short` to reduce output
4. Wait for rate limit reset: `X-RateLimit-Reset` header

### Encryption Failures

**Cause:** LibSodium not installed

**Solution:**
```bash
pip install PyNaCl

# Verify installation
python -c "import nacl; print(nacl.__version__)"
```

---

## Additional Resources

- [GitHub REST API Documentation](https://docs.github.com/en/rest)
- [GitHub Actions Variables](https://docs.github.com/en/rest/actions/variables)
- [GitHub Actions Secrets](https://docs.github.com/en/rest/actions/secrets)
- [GitHub Webhooks](https://docs.github.com/en/developers/webhooks-and-events/webhooks)
- [GitHub Audit Log API](https://docs.github.com/en/enterprise-cloud@latest/rest/enterprise-admin/audit-log)

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-06-29 | GitHub Copilot Agent | Initial comprehensive guide for all 10 processes |

