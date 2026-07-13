# GitHub API Usage Patterns — Code Examples
**Last Updated:** 2026-07-11
**Version:** v0.2.1

> **Version:** 1.0.0  
> **Date:** 2026-06-29  
> **Audience:** Developers, CI/CD automation, test engineers

---

##  Quick Reference Examples

All examples use the token chain: `CODEX_MASTER_KEY` → `CODEX_BACKUP_KEY` → `GH_TOKEN` → `GITHUB_TOKEN`

---

## Pattern 1: Repository Variables (Process 1)

### Create a Repository Variable

```python
from scripts.ci._gh_api import resolve_token, api_post

token = resolve_token()
repo = "Aries-Serpent/_codex_"

# Create a repository variable
response = api_post(
    endpoint=f"/repos/{repo}/actions/variables",
    token=token,
    body={
        "name": "MY_TEST_VAR",
        "value": "test_value_12345",
    }
)

print(f"Created variable: {response}")
# Output: {"name": "MY_TEST_VAR", "value": "test_value_12345", "created_at": "...", "updated_at": "..."}
```

### List Repository Variables

```python
from scripts.ci._gh_api import resolve_token, api_get_cached, paginate_cached
from pathlib import Path

token = resolve_token()
repo = "Aries-Serpent/_codex_"
cache_dir = Path.home() / ".cache/codex_gh_api"

# List all repository variables with caching
variables = paginate_cached(
    endpoint=f"/repos/{repo}/actions/variables",
    token=token,
    cache_dir=cache_dir,
    ttl_seconds=3600,  # 1 hour cache
)

for var in variables:
    print(f"Variable: {var['name']} = {var['value']}")
```

### Update a Repository Variable

```python
from scripts.ci._gh_api import resolve_token, api_patch

token = resolve_token()
repo = "Aries-Serpent/_codex_"

# Update a repository variable
response = api_patch(
    endpoint=f"/repos/{repo}/actions/variables/MY_TEST_VAR",
    token=token,
    body={
        "value": "updated_value_67890",
    }
)

print(f"Updated variable: {response}")
```

### Delete a Repository Variable

```python
from scripts.ci._gh_api import resolve_token, api_delete

token = resolve_token()
repo = "Aries-Serpent/_codex_"

# Delete a repository variable
api_delete(
    endpoint=f"/repos/{repo}/actions/variables/MY_TEST_VAR",
    token=token,
)

print("Variable deleted")
```

---

## Pattern 2: Organization Variables (Process 2)

### Create an Organization Variable

```python
from scripts.ci._gh_api import resolve_token, api_post

token = resolve_token()
org = "Aries-Serpent"

# Create an organization variable
response = api_post(
    endpoint=f"/orgs/{org}/actions/variables",
    token=token,
    body={
        "name": "ORG_WIDE_VAR",
        "value": "org_value_xyz",
    }
)

print(f"Created org variable: {response}")
```

### Restrict Organization Variable to Specific Repositories

```python
from scripts.ci._gh_api import resolve_token, api_put

token = resolve_token()
org = "Aries-Serpent"
var_name = "ORG_WIDE_VAR"

# Set which repositories can access this org variable
response = api_put(
    endpoint=f"/orgs/{org}/actions/variables/{var_name}/repositories",
    token=token,
    body={
        "selected_repository_ids": [1040037790],  # Repository ID for _codex_
    }
)

print(f"Restricted org variable to specific repos: {response}")
```

---

## Pattern 3: Repository Secrets (Process 3)

### Encrypt and Store a Secret

```python
from scripts.ci._gh_api import resolve_token, api_get, api_put
from scripts.ci._secrets_encryption_helper import encrypt_secret
import base64

token = resolve_token()
repo = "Aries-Serpent/_codex_"

# Step 1: Fetch GitHub's public key
status, key_response = api_get(
    endpoint=f"/repos/{repo}/actions/secrets/public-key",
    token=token,
)

public_key = key_response["key"]
key_id = key_response["key_id"]

# Step 2: Encrypt the secret
encrypted = encrypt_secret(
    secret_value="my-super-secret-token",
    public_key=public_key,
    key_id=key_id,
    key_type="actions",
)

# Step 3: Store the encrypted secret
response = api_put(
    endpoint=f"/repos/{repo}/actions/secrets/MY_SECRET",
    token=token,
    body={
        "encrypted_value": encrypted["encrypted_value"],
        "key_id": encrypted["key_id"],
    }
)

print(f"Secret stored: {response['created_at']}")
```

### Delete a Secret

```python
from scripts.ci._gh_api import resolve_token, api_delete

token = resolve_token()
repo = "Aries-Serpent/_codex_"

# Delete a secret
api_delete(
    endpoint=f"/repos/{repo}/actions/secrets/MY_SECRET",
    token=token,
)

print("Secret deleted")
```

---

## Pattern 4: Webhook Management (Processes 8 & 9)

### Create a Repository Webhook

```python
from scripts.ci._gh_api import resolve_token, api_post

token = resolve_token()
repo = "Aries-Serpent/_codex_"

# Create a webhook for push events
response = api_post(
    endpoint=f"/repos/{repo}/hooks",
    token=token,
    body={
        "name": "web",
        "active": True,
        "events": ["push", "pull_request"],
        "config": {
            "url": "https://example.com/webhook",
            "content_type": "json",
            "insecure_ssl": "0",
            "secret": "my-webhook-secret",
        }
    }
)

webhook_id = response["id"]
print(f"Created webhook {webhook_id}")
```

### Validate Webhook Signature

```python
from scripts.ci._webhook_signature_validator import WebhookValidator
from flask import request

# Initialize validator
validator = WebhookValidator(webhook_secret="my-webhook-secret")

# Validate incoming webhook
is_valid, payload = validator.validate_and_parse(
    payload=request.get_data(),
    signature=request.headers.get("X-Hub-Signature-256"),
)

if is_valid:
    print(f"Webhook validated: {payload['action']}")
else:
    raise SecurityError("Invalid webhook signature")
```

### Test Webhook Delivery

```python
from scripts.ci._gh_api import resolve_token, api_post

token = resolve_token()
repo = "Aries-Serpent/_codex_"
webhook_id = 12345

# Test webhook delivery
response = api_post(
    endpoint=f"/repos/{repo}/hooks/{webhook_id}/tests",
    token=token,
)

print(f"Webhook test sent: {response}")
```

---

## Pattern 5: Workflow Dispatch (Process 7)

### Trigger a Workflow Run

```python
from scripts.ci._gh_api import resolve_token, api_post

token = resolve_token()
repo = "Aries-Serpent/_codex_"
workflow_id = "tests.yml"

# Dispatch workflow with inputs
response = api_post(
    endpoint=f"/repos/{repo}/actions/workflows/{workflow_id}/dispatches",
    token=token,
    body={
        "ref": "main",  # Branch to run workflow on
        "inputs": {
            "scope": "all-tests",
            "environment": "staging",
        }
    }
)

print(f"Workflow dispatched: {response['status']}")
```

### Monitor Workflow Execution

```python
from scripts.ci._gh_api import resolve_token, api_get
import time

token = resolve_token()
repo = "Aries-Serpent/_codex_"
run_id = 123456

# Poll workflow status
for attempt in range(30):  # Max 5 minutes
    status, response = api_get(
        endpoint=f"/repos/{repo}/actions/runs/{run_id}",
        token=token,
    )
    
    if response["status"] == "completed":
        print(f"Workflow completed: {response['conclusion']}")
        break
    
    print(f"Status: {response['status']}... (attempt {attempt + 1})")
    time.sleep(10)
```

---

## Pattern 6: Audit Log Querying (Process 10)

### Query Organization Audit Log

```python
from scripts.ci._gh_api import resolve_token, paginate_cached
from pathlib import Path

token = resolve_token()
org = "Aries-Serpent"
cache_dir = Path.home() / ".cache/codex_gh_api"

# Query audit log with filtering
logs = paginate_cached(
    endpoint=(
        f"/orgs/{org}/audit-log"
        "?action=repo.create"
        "&include=all"
        "&per_page=100"
    ),
    token=token,
    cache_dir=cache_dir,
    ttl_seconds=3600,
)

for entry in logs:
    print(f"{entry['timestamp']}: {entry['action']} by {entry['actor']}")
```

### Filter Audit Log by Date Range

```python
from scripts.ci._gh_api import resolve_token, paginate
from datetime import datetime, timedelta

token = resolve_token()
org = "Aries-Serpent"

# Calculate date range (last 7 days)
until = datetime.utcnow().isoformat() + "Z"
since = (datetime.utcnow() - timedelta(days=7)).isoformat() + "Z"

# Query audit log with date filter
logs = paginate(
    endpoint=(
        f"/orgs/{org}/audit-log"
        f"?include=all"
        f"&since={since}"
        f"&until={until}"
        f"&per_page=100"
    ),
    token=token,
)

print(f"Found {len(logs)} audit log entries")
```

---

## Pattern 7: Error Handling

### Handle Rate Limiting

```python
from scripts.ci._gh_api import resolve_token, api_get
import time

token = resolve_token()
repo = "Aries-Serpent/_codex_"

max_retries = 3
retry_count = 0

while retry_count < max_retries:
    try:
        status, response = api_get(
            endpoint=f"/repos/{repo}",
            token=token,
        )
        break
    except Exception as err:
        if "rate limit" in str(err).lower():
            retry_count += 1
            wait_time = 60 * retry_count
            print(f"Rate limited. Waiting {wait_time}s...")
            time.sleep(wait_time)
        else:
            raise
```

### Handle 403 Forbidden (Missing Scope)

```python
from scripts.ci._gh_api import resolve_token, api_get

token = resolve_token()
repo = "Aries-Serpent/_codex_"

try:
    status, response = api_get(
        endpoint=f"/repos/{repo}/actions/variables",
        token=token,
    )
    
    if status == 403:
        print(" Token missing 'repo' scope")
        print("Required: CODEX_MASTER_KEY with 'repo' scope")
    
except Exception as err:
    print(f"API Error: {err}")
```

---

## Pattern 8: Caching for Performance

### Cache API Responses

```python
from scripts.ci._gh_api import resolve_token, api_get_cached
from pathlib import Path

token = resolve_token()
repo = "Aries-Serpent/_codex_"
cache_dir = Path.home() / ".cache/codex_gh_api"
cache_dir.mkdir(parents=True, exist_ok=True)

# First call: fetches from API
status, response = api_get_cached(
    endpoint=f"/repos/{repo}",
    token=token,
    cache_dir=cache_dir,
    ttl_seconds=3600,  # Cache for 1 hour
)

# Second call: uses cache (same query within 1 hour)
status2, response2 = api_get_cached(
    endpoint=f"/repos/{repo}",
    token=token,
    cache_dir=cache_dir,
    ttl_seconds=3600,
)

assert response == response2
```

---

## Pattern 9: Pagination

### Paginate Through Large Result Sets

```python
from scripts.ci._gh_api import resolve_token, paginate_cached
from pathlib import Path

token = resolve_token()
org = "Aries-Serpent"
cache_dir = Path.home() / ".cache/codex_gh_api"

# Automatically handles pagination
members = paginate_cached(
    endpoint=f"/orgs/{org}/members?per_page=100",
    token=token,
    cache_dir=cache_dir,
    max_pages=10,  # Max 1000 results
    page_sleep=1.0,  # 1 second between pages
)

print(f"Total members: {len(members)}")
```

---

## Pattern 10: Token Chain Resolution

### Automatic Token Selection

```python
from scripts.ci._gh_api import resolve_token

# Automatically tries in order:
# 1. CODEX_MASTER_KEY
# 2. CODEX_BACKUP_KEY
# 3. GH_TOKEN
# 4. GITHUB_TOKEN

token = resolve_token()

if not token:
    print(" No GitHub token found")
    print("Set one of: CODEX_MASTER_KEY, CODEX_BACKUP_KEY, GH_TOKEN, GITHUB_TOKEN")
    exit(1)

print(f" Using token from: {resolve_token() and 'environment'}")
```

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-06-29 | Initial comprehensive usage patterns for all 10 processes |

