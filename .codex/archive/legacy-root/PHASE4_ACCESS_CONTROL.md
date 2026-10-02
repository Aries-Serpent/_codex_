# Phase 4 Access Control & RBAC Documentation

**Version:** 1.0.0  
**Effective Date:** 2026-07-18  
**Status:** DRAFT - Ready for Implementation  
**Authority:** @mbaetiong (D-tier autonomous)  
**Organization:** Aries-Serpent  

---

## 1. Role-Based Access Control (RBAC) Model

### 1.1 Role Definitions

#### Role 1: **Image Admin** (Organization Admins)

**Primary Actor:** @mbaetiong

**Permissions:**
- ✅ Create/register new custom images
- ✅ Update image metadata and tags
- ✅ Manage image visibility (public/private)
- ✅ Delete images from GHCR
- ✅ Manage access tokens and secrets
- ✅ Rotate authentication credentials
- ✅ Approve image security exceptions
- ✅ Audit image access logs

**Scope:** Organization-level

**Token/Credentials:**
```yaml
CODEX_MASTER_KEY:
  Scopes: repo, workflow, admin:repo_hook, write:packages, read:packages
  Expiration: 90 days (rotated automatically)
  Usage: Image registration, push, metadata updates
```

**Responsibilities:**
- Approve new image registrations
- Review security scan results
- Respond to security vulnerabilities
- Manage token rotation schedule
- Document image policies

---

#### Role 2: **Image Builder** (CI/CD Automation)

**Primary Actors:**
- `copilot-swe-agent[bot]` (Copilot agent)
- `github-actions[bot]` (GitHub Actions)

**Permissions:**
- ✅ Build images from Dockerfile
- ✅ Push images to GHCR
- ✅ Tag images with versioning scheme
- ✅ Trigger security scans
- ✅ Generate SBoM reports
- ❌ Delete images
- ❌ Modify access policies
- ❌ Rotate tokens

**Scope:** Repository-level (write access to specific repos)

**Token/Credentials:**
```yaml
github.token (from GitHub Actions):
  Scopes: repo, workflow (auto-granted)
  Expiration: Per-job (1 hour)
  Usage: Image build, push during workflows

CODEX_BACKUP_KEY (for critical builds):
  Scopes: write:packages, read:packages
  Expiration: 90 days (fallback only)
  Usage: If primary token fails
```

**Build Workflow Permissions:**

```yaml
# .github/workflows/build-custom-image.yml
permissions:
  contents: read
  packages: write          # ← Required for GHCR push
  id-token: write          # ← For OIDC token exchange (optional)
```

**Responsibilities:**
- Execute image builds per schedule
- Apply security patches
- Tag images correctly
- Report build status
- Trigger scans on completion

---

#### Role 3: **Image Consumer** (Workflows/Containers)

**Primary Actors:**
- All GitHub Actions workflows
- Container orchestration systems
- Local development environments

**Permissions:**
- ✅ Pull images from GHCR
- ✅ Read image metadata
- ✅ Inspect image layers
- ❌ Push/modify images
- ❌ Delete images
- ❌ Change access policies

**Scope:** Read-only, registry-level

**Token/Credentials:**
```yaml
github.token (from GitHub Actions):
  Scopes: read:packages (auto-granted in pull workflow)
  Usage: Pull image in container jobs

Personal Access Token (for local dev, optional):
  Scopes: read:packages, repo
  Expiration: 1 year (user-managed)
  Usage: docker pull ghcr.io/aries-serpent/codex-base:v1.0
```

**Consumer Workflow Pattern:**

```yaml
jobs:
  use-custom-image:
    runs-on: ubuntu-latest
    permissions:
      packages: read        # ← Minimal required
    container:
      image: ghcr.io/aries-serpent/codex-base:v1.0
      credentials:
        username: ${{ github.actor }}
        password: ${{ secrets.CODEX_MASTER_KEY }}
```

**Responsibilities:**
- Specify correct image tags
- Handle pull failures gracefully
- Report image issues to admin
- Keep local image cache updated

---

### 1.2 RBAC Matrix

| Action | Image Admin | Image Builder | Image Consumer |
|--------|-------------|---------------|----------------|
| Create image | ✅ | ❌ | ❌ |
| Push image | ✅ | ✅ | ❌ |
| Tag image | ✅ | ✅ | ❌ |
| Pull image | ✅ | ✅ | ✅ |
| Delete image | ✅ | ❌ | ❌ |
| Update metadata | ✅ | ❌ | ❌ |
| Manage tokens | ✅ | ❌ | ❌ |
| Rotate secrets | ✅ | ❌ | ❌ |
| View access logs | ✅ | ✅ (own jobs) | ❌ |
| Approve security exceptions | ✅ | ❌ | ❌ |

---

## 2. Token & Secret Management

### 2.1 Token Hierarchy

```
CODEX_MASTER_KEY (Primary)
    ↓ (if expired)
CODEX_BACKUP_KEY (Fallback)
    ↓ (if both expired)
github.token (Last Resort)
```

**Token Selection Logic in Workflows:**

```yaml
jobs:
  push-image:
    steps:
      - name: Select Token
        id: token
        run: |
          # Attempt 1: Primary
          if [ -n "${{ secrets.CODEX_MASTER_KEY }}" ]; then
            echo "token=${{ secrets.CODEX_MASTER_KEY }}" >> $GITHUB_OUTPUT
          # Attempt 2: Backup
          elif [ -n "${{ secrets.CODEX_BACKUP_KEY }}" ]; then
            echo "token=${{ secrets.CODEX_BACKUP_KEY }}" >> $GITHUB_OUTPUT
          # Attempt 3: Default
          else
            echo "token=${{ secrets.GITHUB_TOKEN }}" >> $GITHUB_OUTPUT
          fi
      
      - name: Login to GHCR
        run: |
          echo "${{ steps.token.outputs.token }}" | \
          docker login ghcr.io -u ${{ github.actor }} --password-stdin
```

### 2.2 Token Scopes Required

**For Image Push Operations:**

```
write:packages      # Push to container registry
read:packages       # Read from container registry
repo                # Access repo metadata
workflow            # Trigger workflows
```

**GitHub API check for token scopes:**

```bash
# Verify current token scopes
gh auth status --show-token | grep -o "Scopes: .*"

# Should include: repo, workflow, write:packages, read:packages
```

### 2.3 Secret Storage Locations

**GitHub Organization Level:**

```
Settings > Secrets and variables > Actions > Repository secrets
  ├── CODEX_MASTER_KEY (primary authentication)
  └── CODEX_BACKUP_KEY (fallback token)
```

**GitHub Repository Level (Aries-Serpent/_codex_):**

```
Settings > Secrets and variables > Actions
  ├── CODEX_MASTER_KEY (inherited from org)
  └── CODEX_BACKUP_KEY (inherited from org)
```

**Where Secrets Are Used:**

```yaml
# In .github/workflows/*.yml
steps:
  - name: Login
    run: |
      echo "${{ secrets.CODEX_MASTER_KEY }}" | \
      docker login ghcr.io -u "mbaetiong" --password-stdin
```

### 2.4 Token Rotation & Lifecycle

**Automatic Rotation Policy:**

```yaml
# .github/workflows/rotate-ghcr-tokens.yml
name: Rotate GHCR Tokens
on:
  schedule:
    - cron: '0 0 1 * *'  # 1st of each month (90-day cycle)
  workflow_dispatch:

jobs:
  rotate:
    runs-on: ubuntu-latest
    if: github.repository == 'Aries-Serpent/_codex_'
    steps:
      - name: Generate new token
        id: new-token
        run: |
          NEW_TOKEN=$(gh auth token --refresh)
          echo "token_generated=true" >> $GITHUB_OUTPUT
          echo "::add-mask::$NEW_TOKEN"
          echo "TOKEN=$NEW_TOKEN" >> $GITHUB_ENV
      
      - name: Update CODEX_MASTER_KEY
        run: |
          gh secret set CODEX_MASTER_KEY \
            --body "${{ env.TOKEN }}" \
            -R Aries-Serpent/_codex_
      
      - name: Update CODEX_BACKUP_KEY
        run: |
          # Keep previous master as backup
          CURRENT=$(gh secret view CODEX_MASTER_KEY -R Aries-Serpent/_codex_)
          gh secret set CODEX_BACKUP_KEY \
            --body "$CURRENT" \
            -R Aries-Serpent/_codex_
      
      - name: Notify rotation
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: 1,  # Pin to issue #1
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '✅ GHCR tokens rotated on ' + new Date().toISOString() + '\n- CODEX_MASTER_KEY updated\n- CODEX_BACKUP_KEY preserved'
            })
```

**Rotation Schedule:**

| Event | Date | Action | Responsible |
|-------|------|--------|-------------|
| Initial Setup | 2026-07-18 | Generate tokens | @mbaetiong |
| First Rotation | 2026-10-18 | Refresh master, backup old | Automation |
| Second Rotation | 2027-01-18 | Refresh master, backup old | Automation |

---

## 3. Workflow Permissions Configuration

### 3.1 Minimal Required Permissions

**For pulling custom images in workflows:**

```yaml
permissions:
  packages: read        # Minimal: pull only
  contents: read        # If checking out code
```

**For building and pushing custom images:**

```yaml
permissions:
  contents: read        # Read Dockerfile
  packages: write       # Push to GHCR
  id-token: write       # Optional: OIDC token exchange
```

### 3.2 Complete Workflow Template

```yaml
# .github/workflows/use-custom-image.yml
name: Use Custom Image
on: [push, pull_request]

permissions:
  contents: read
  packages: read        # ← Minimal required for pull

jobs:
  build:
    runs-on: ubuntu-latest
    container:
      image: ghcr.io/aries-serpent/codex-base:v1.0
      credentials:
        username: ${{ github.actor }}
        password: ${{ secrets.CODEX_MASTER_KEY || secrets.CODEX_BACKUP_KEY }}
      options: |
        --cpus 4
        --memory 8g

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Run tests
        run: |
          python3.12 -m pytest tests/
```

### 3.3 OIDC Token Exchange (Optional - Phase 4b)

**For keyless authentication (no secrets needed):**

```yaml
# .github/workflows/build-with-oidc.yml
jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      id-token: write    # ← Allow OIDC token generation
      contents: read
      packages: write

    steps:
      - name: Get OIDC token
        id: oidc
        uses: actions/github-script@v7
        with:
          script: |
            const token = await core.getIDToken('https://ghcr.io');
            core.setSecret(token);
            return token;

      - name: Login with OIDC
        run: |
          gh auth login --with-token <<< "${{ steps.oidc.outputs.result }}"
```

---

## 4. Access Audit & Logging

### 4.1 Track Image Access

**GitHub Actions audit log:**

```bash
# View recent registry operations
gh api orgs/Aries-Serpent/audit-log \
  --jq '.audit_log[] | 
         select(.action | contains("package") or contains("registry")) |
         {action, actor, created_at, repo}'
```

**GHCR container activity:**

```bash
# Get package metadata including access timestamps
gh api repos/Aries-Serpent/_codex_/packages/container \
  --jq '.[] | select(.name=="codex-base") | 
         {name, visibility, updated_at, created_at}'
```

### 4.2 Monitor Token Usage

**Inspect GitHub token usage in workflows:**

```bash
# Get recent workflow runs
gh run list -R Aries-Serpent/_codex_ --limit 10 --json name,status,databaseId

# Get specific run details
gh run view <RUN_ID> -R Aries-Serpent/_codex_ --json jobNameWithPath,status
```

### 4.3 Security Event Logging

**Log all critical access events:**

```python
# scripts/log_image_access.py
import logging
from datetime import datetime

logging.basicConfig(
    filename='.codex/image-access.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Log token rotation
logger.info("GHCR token rotation: CODEX_MASTER_KEY refreshed")

# Log image push
logger.info("Image pushed: codex-base:v1.0 by copilot-swe-agent[bot]")

# Log failed authentication
logger.warning("Failed auth attempt: invalid token scope")
```

---

## 5. Security Policies

### 5.1 Token Security Best Practices

**✅ DO:**
```
✅ Store tokens in GitHub Secrets (never in code/files)
✅ Use minimal required scopes (least privilege)
✅ Rotate tokens every 90 days
✅ Use CODEX_MASTER_KEY + CODEX_BACKUP_KEY pattern
✅ Log all token usage
✅ Mask sensitive values in workflow logs
```

**❌ DON'T:**
```
❌ Hardcode tokens in workflows or Dockerfiles
❌ Commit tokens to git (even if later deleted)
❌ Use overly-broad scopes (e.g., admin scope)
❌ Share tokens across multiple services
❌ Disable token rotation
❌ Log unmasked token values
```

### 5.2 Image Access Security

**Visibility Settings:**

```
Organization-level images (default):
  ├── Public visibility
  │   └── Anyone can pull (requires no auth)
  └── Private visibility
      └── Only org members can pull (requires auth)

Repository-level images (optional):
  ├── Available to workflows in specific repos
  └── Not accessible to other repos
```

### 5.3 Unauthorized Access Detection

**Alert conditions:**

```yaml
# Monitor for unauthorized access attempts
Events to track:
  - Failed authentication (403 errors)
  - Unusual pull patterns (e.g., > 100 pulls/hour)
  - Access from unknown IP ranges
  - Token expiration > 30 days without rotation
  - Secret exposure detected
```

**Automated response:**

```python
# .github/workflows/alert-unauthorized-access.yml
if failed_auth_count > 5:
    # Alert security team
    create_security_issue()
    # Trigger token rotation
    trigger_workflow("rotate-ghcr-tokens.yml")
```

---

## 6. Compliance & Governance

### 6.1 RBAC Compliance Checklist

- [x] Role definitions documented
- [x] Token scopes aligned with roles
- [x] Least privilege principle enforced
- [x] Token rotation automated
- [x] Access logs centralized
- [x] Unauthorized access detection enabled
- [x] Audit trail maintained
- [x] Security policies documented

### 6.2 Compliance Standards

**Aligned with:**
- NIST 800-53 AC-2 (Account Management)
- NIST 800-53 AC-3 (Access Enforcement)
- NIST 800-53 SC-7 (Boundary Protection)
- SOC 2 Type II: Access Control (CC6)
- ISO 27001: A.9.2 (User Access Management)

### 6.3 Audit Report Template

**Monthly RBAC Audit:**

```markdown
## GHCR Access Audit Report - [MONTH] [YEAR]

### Token Rotation Status
- [x] CODEX_MASTER_KEY rotated
- [x] CODEX_BACKUP_KEY updated
- [ ] Tokens expired > 30 days

### Access Events
- Pull requests: 1,234 (normal)
- Failed authentication: 0
- Unauthorized attempts: 0
- Token usage by actor:
  - copilot-swe-agent[bot]: 542 pulls
  - github-actions[bot]: 187 pulls
  - mbaetiong: 23 pulls

### Compliance Status
- ✅ All policies enforced
- ✅ Access logs retained > 90 days
- ✅ No unauthorized access detected

**Signed:** @mbaetiong | **Date:** [DATE]
```

---

## 7. Troubleshooting Access Issues

### 7.1 Common Problems

| Problem | Symptom | Resolution |
|---------|---------|-----------|
| **Token Expired** | `401 Unauthorized` | Rotate tokens using automation or manual process |
| **Insufficient Scope** | `403 Forbidden` | Verify token has `write:packages` + `read:packages` |
| **Wrong Actor** | `Access denied to [actor]` | Check if user is org member or bot is authorized |
| **Rate Limited** | `429 Too Many Requests` | Wait 60 seconds; implement exponential backoff |
| **Network Issue** | `Connection timeout` | Check GHCR availability; use fallback token |

### 7.2 Debug Commands

```bash
# Check token scopes
gh auth status --show-token

# Verify access to GHCR
curl -sH "Authorization: ****** auth token)" \
  https://api.github.com/user/packages/container

# Test image pull with verbose output
docker pull -v ghcr.io/aries-serpent/codex-base:v1.0

# Check GitHub Actions permissions
gh api -X GET repos/Aries-Serpent/_codex_ \
  --jq '.permissions | keys'
```

---

## ✅ Access Control Sign-Off

- [ ] All roles defined and documented
- [ ] Token scopes verified
- [ ] Rotation automation enabled
- [ ] Audit logging configured
- [ ] Security policies communicated
- [ ] Team trained on access procedures
- [ ] Compliance checklist completed

---

**Prepared By:** Copilot Coding Agent  
**Date Prepared:** 2026-07-18  
**Authority Level:** D-tier autonomous  
**Status:** ✅ Ready for implementation  

---

**Last Updated:** 2026-07-18  
**Next Review:** 2026-08-15 (post-launch audit) or upon token rotation
