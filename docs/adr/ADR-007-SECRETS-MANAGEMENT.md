# ADR-007: Environment-Based Secrets Management
**Last Updated:** 2026-07-11
**Version:** v0.2.1

**Status:** Accepted  
**Date:** 2026-07-10  
**Author:** @mbaetiong  
**Session:** S250-doc-arch  

---

## Context

The platform needs to manage secrets (API keys, database passwords, tokens) securely:

1. **Never in code** — Git history retains secrets forever
2. **Never in config files** — Config files often checked in
3. **Different per environment** — Dev, test, prod have different secrets
4. **Must rotate** — Secrets should rotate without code changes

Previous approaches stored secrets in:
- Hardcoded strings 
- Config files 
- `.env` files (now only for local dev) 

---

## Decision

**Environment variable-based secrets** with encryption at rest for non-local environments:

**Principles:**
1. **Never commit secrets** — All secret sources are `.gitignore`d
2. **Local development** — `.env` files with example patterns
3. **CI/CD** — GitHub Actions secrets
4. **Production** — Vault or cloud parameter store
5. **Rotation** — Secrets can change without code change

**Storage locations:**

| Environment | Storage | Example |
|---|---|---|
| Local Dev | `.env` (gitignored) | `OPENAI_API_KEY=sk-...` |
| CI/CD | GitHub Secrets | Stored in repo settings |
| Production | Vault | Encrypted parameter store |
| Cloud (AWS) | Secrets Manager | KMS-encrypted |
| Cloud (GCP) | Secret Manager | IAM-controlled access |

**Access patterns:**

```python
import os
from typing import Optional

def get_secret(name: str, default: Optional[str] = None) -> str:
    """
    Get secret from environment.
    Raises if required secret missing.
    """
    value = os.getenv(name, default)
    if value is None:
        raise ValueError(f"Required secret '{name}' not found in environment")
    return value

# Usage
api_key = get_secret("OPENAI_API_KEY")
db_password = get_secret("DB_PASSWORD")
jwt_secret = get_secret("JWT_SECRET")
```

---

## Configuration Pattern

**`.env.example` (committed to repo):**

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-key-here-never-commit-real-key
OPENAI_MODEL=gpt-4

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=codex_dev
DB_USER=dev_user
DB_PASSWORD=dev_password_change_me

# JWT Configuration
JWT_SECRET=your-secret-key-change-me
JWT_EXPIRY=3600

# Monitoring
SENTRY_DSN=https://your-sentry-key@sentry.io/project-id
DATADOG_API_KEY=dd_your_key

# Feature Flags
ENABLE_RAG_PIPELINE=true
ENABLE_DISTRIBUTED_TRAINING=false
```

**`.env.local` (gitignored):**

```bash
# Copy from .env.example and fill with real local values
OPENAI_API_KEY=sk-real-local-key
DB_PASSWORD=actual-local-db-password
JWT_SECRET=local-testing-secret-only
```

---

## Loading Secrets in Code

**Initialization (before app starts):**

```python
from pathlib import Path
from dotenv import load_dotenv

# In main.py or __init__.py
env_file = Path(__file__).parent / ".env.local"
if env_file.exists():
    load_dotenv(env_file)

# Validate required secrets
REQUIRED_SECRETS = [
    "OPENAI_API_KEY",
    "JWT_SECRET",
    "DB_PASSWORD",
]

for secret in REQUIRED_SECRETS:
    if secret not in os.environ:
        raise RuntimeError(f"Missing required secret: {secret}")
```

**Usage throughout codebase:**

```python
# In any module
from codex.config import get_secret

openai_key = get_secret("OPENAI_API_KEY")
jwt_secret = get_secret("JWT_SECRET")

# Connect to database
db = Database(
    host=get_secret("DB_HOST", "localhost"),
    ******"DB_PASSWORD"),
    port=int(get_secret("DB_PORT", "5432")),
)
```

---

## Rotation Strategy

**1. Local Development:**
```bash
# Update .env.local with new values
echo "NEW_KEY=new-value" >> .env.local

# App picks up immediately (or restart for some loaders)
```

**2. CI/CD (GitHub Actions):**
```bash
# Update GitHub Actions secrets in repo settings
# No code change required, workflows automatically use new values
```

**3. Production (Vault):**
```python
# Vault client automatically rotates with lease renewal
vault_client = VaultClient(
    url="https://vault.example.com",
    auth_method="k8s"  # Kubernetes auth, no credentials in code
)

# Periodically fetch fresh secrets
@scheduler.every(1, 'hour').do
def refresh_secrets():
    global api_key, db_password
    api_key = vault_client.read("secret/codex/openai_key")
    db_password = vault_client.read("secret/codex/db_password")
```

---

## Security Guarantees

**What is protected:**
 API keys  
 Database passwords  
 Encryption keys  
 OAuth tokens  
 Webhook signing secrets  

**What is NOT in .env:**
 Public configuration (feature flags) — goes in Hydra config  
 Non-sensitive settings — in config files  
 Schema definitions — in code  

---

## CI/CD Integration

**GitHub Actions workflow:**

```yaml
name: Deploy to Production

on: [push]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy with secrets
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
          JWT_SECRET: ${{ secrets.JWT_SECRET }}
        run: |
          python deploy.py
```

**Setting secrets in GitHub UI:**
- Go to repo Settings → Secrets
- Click "New repository secret"
- Name: `OPENAI_API_KEY`, Value: actual key
- Secrets are masked in logs

---

## Consequences

### Positive
 Secrets never committed to Git  
 Easy rotation without code changes  
 Different secrets per environment  
 No hardcoded values in codebase  
 Clear separation of concerns (config vs secrets)  
 Compatible with all cloud providers  

### Negative
⚠️ Developers must manage local `.env` files  
⚠️ Missing secrets cause runtime errors (not startup)  
⚠️ Requires Vault setup for production  

### Mitigations
- `.env.example` as template for developers
- Pre-commit hook to detect accidental secrets
- Clear error messages when secrets missing
- Documentation on secret setup

---

## Incident Response

**If a secret is accidentally committed:**

1. **Immediately:**
   ```bash
   git filter-branch --force --index-filter \
     'git rm --cached --ignore-unmatch .env' \
     HEAD
   ```

2. **Rotate the secret** — change password/key at source
3. **Force push** — update the repository
4. **Monitor** — watch for unauthorized access using old secret
5. **Audit** — log who had access to the secret

---

## Related ADRs
- ADR-001: MCP Architecture (secrets isolation)
- ADR-010: Production Deployment Strategy
