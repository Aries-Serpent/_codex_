# GitHub API Scope Matrix — All Scopes & Operations
**Last Updated:** 2026-07-11
**Version:** v0.2.1

> **Version:** 1.0.0
> **Date:** 2026-06-29
> **API Version:** 2026-03-10
> **Generated:** Comprehensive scope-to-operation mapping for CODEX_MASTER_KEY

---

## Scope Hierarchy

GitHub API scopes follow a hierarchy from broad to narrow access:

```
admin:*          → Most permissive; full control of resource category
write:*          → Create, update, delete operations
read:*           → Read-only access
(unscoped)       → Specific narrow permissions
```

---

## Scope Matrix: All Granted Scopes

### 1. Repository Control (`repo`)

| Scope | Access Level | Operations | Test Process |
|-------|--------------|-----------|--------------|
| `repo` | Full control | All repo operations (read, create, update, delete) | Process 1, 3, 5 |
| `repo:status` | Limited | Read commit status | (Supplementary) |
| `repo:invite` | Limited | Manage repository invitations | (Supplementary) |
| `repo:deployment` | Limited | Read deployment status | (Supplementary) |
| `public_repo` | Limited | Access public repositories only | (Supplementary) |

**Key APIs:**
- `/repos/{owner}/{repo}` — Repository metadata
- `/repos/{owner}/{repo}/contents` — File operations
- `/repos/{owner}/{repo}/actions/variables` — Variables (Process 1)
- `/repos/{owner}/{repo}/actions/secrets` — Secrets (Process 3)
- `/repos/{owner}/{repo}/dependabot/secrets` — Dependabot (Process 5)

---

### 2. Workflow Control (`workflow`)

| Scope | Access Level | Operations | Test Process |
|-------|--------------|-----------|--------------|
| `workflow` | Write | Update GitHub Actions workflows | Process 7 |

**Key APIs:**
- `/repos/{owner}/{repo}/actions/workflows` — List workflows
- `/repos/{owner}/{repo}/actions/workflows/{id}/dispatches` — Trigger workflow (Process 7)
- `/repos/{owner}/{repo}/actions/runs` — Query execution status
- `/repos/{owner}/{repo}/actions/runs/{id}/cancel` — Cancel workflow

---

### 3. Security Events (`security_events`)

| Scope | Access Level | Operations | Test Process |
|-------|--------------|-----------|--------------|
| `security_events` | Read/Write | Access security event data | (Specialized) |

**Key APIs:**
- `/repos/{owner}/{repo}/secret-scanning/alerts` — Secret scanning
- `/repos/{owner}/{repo}/code-scanning/alerts` — CodeQL alerts

---

### 4. Organization Control (`admin:org`)

| Scope | Access Level | Operations | Test Process |
|-------|--------------|-----------|--------------|
| `admin:org` | Full control | Full org control + all sub-scopes | Process 2, 4 |
| `write:org` | Write | Read/write org and team membership | (Supplementary) |
| `read:org` | Read | Read-only org membership | (Supplementary) |
| `manage_runners:org` | Write | Manage org runners and groups | (Supplementary) |

**Key APIs:**
- `/orgs/{org}/actions/variables` — Org variables (Process 2)
- `/orgs/{org}/actions/secrets` — Org secrets (Process 4)
- `/orgs/{org}/members` — Member management
- `/orgs/{org}/teams` — Team management
- `/orgs/{org}/hooks` — Organization webhooks (Process 9)

---

### 5. Repository Hooks (`admin:repo_hook`)

| Scope | Access Level | Operations | Test Process |
|-------|--------------|-----------|--------------|
| `admin:repo_hook` | Full control | Full webhook control | Process 8 |
| `write:repo_hook` | Write | Create/update webhooks | (Supplementary) |
| `read:repo_hook` | Read | Read-only webhook access | (Supplementary) |

**Key APIs:**
- `/repos/{owner}/{repo}/hooks` — Repository webhooks (Process 8)
- `/repos/{owner}/{repo}/hooks/{id}` — Individual hook management
- `/repos/{owner}/{repo}/hooks/{id}/tests` — Test webhook delivery

---

### 6. Organization Hooks (`admin:org_hook`)

| Scope | Access Level | Operations | Test Process |
|-------|--------------|-----------|--------------|
| `admin:org_hook` | Full control | Full org webhook control | Process 9 |

**Key APIs:**
- `/orgs/{org}/hooks` — Organization webhooks (Process 9)
- `/orgs/{org}/hooks/{id}` — Individual hook management

---

### 7. Package Management

| Scope | Access Level | Operations | Test Process |
|-------|--------------|-----------|--------------|
| `write:packages` | Write | Upload to GitHub Package Registry | (Supplementary) |
| `read:packages` | Read | Download from GitHub Package Registry | (Supplementary) |
| `delete:packages` | Write | Delete packages | (Supplementary) |

**Key APIs:**
- `/repos/{owner}/{repo}/packages` — Package management

---

### 8. User Profile (`user`)

| Scope | Access Level | Operations | Test Process |
|-------|--------------|-----------|--------------|
| `user` | Full control | Update ALL user data | (Supplementary) |
| `read:user` | Read | Read ALL user profile data | (Supplementary) |
| `user:email` | Read | Read-only user email | (Supplementary) |

**Key APIs:**
- `/user` — Current user profile
- `/user/emails` — User email addresses

---

### 9. Repository Deletion (`delete_repo`)

| Scope | Access Level | Operations | Test Process |
|-------|--------------|-----------|--------------|
| `delete_repo` | Write | Delete repositories | (Supplementary) |

**Key APIs:**
- `DELETE /repos/{owner}/{repo}` — Delete repository

---

### 10. Public Keys Management

| Scope | Access Level | Operations | Test Process |
|-------|--------------|-----------|--------------|
| `admin:public_key` | Full control | Full control of SSH keys | (Lower Priority 11) |
| `write:public_key` | Write | Create/update SSH keys | (Supplementary) |
| `read:public_key` | Read | Read SSH keys | (Supplementary) |

**Key APIs:**
- `/user/keys` — User SSH public keys

---

### 11. GPG Keys Management

| Scope | Access Level | Operations | Test Process |
|-------|--------------|-----------|--------------|
| `admin:gpg_key` | Full control | Full control of GPG keys | (Supplementary) |
| `write:gpg_key` | Write | Create/update GPG keys | (Supplementary) |
| `read:gpg_key` | Read | Read GPG keys | (Supplementary) |

**Key APIs:**
- `/user/gpg_keys` — User GPG public keys

---

### 12. SSH Signing Keys

| Scope | Access Level | Operations | Test Process |
|-------|--------------|-----------|--------------|
| `admin:ssh_signing_key` | Full control | Full control of SSH signing keys | (Supplementary) |
| `write:ssh_signing_key` | Write | Create/update SSH signing keys | (Supplementary) |
| `read:ssh_signing_key` | Read | Read SSH signing keys | (Supplementary) |

**Key APIs:**
- `/user/ssh_signing_keys` — User SSH signing keys

---

### 13. Codespaces (`codespace`)

| Scope | Access Level | Operations | Test Process |
|-------|--------------|-----------|--------------|
| `codespace` | Full control | Full codespace control | Process 6 |
| `codespace:secrets` | Full control | Manage codespace secrets | Process 6 |

**Key APIs:**
- `/repos/{owner}/{repo}/codespaces` — Codespace management
- `/repos/{owner}/{repo}/codespaces/secrets` — Codespace secrets (Process 6)

---

### 14. Gist Management (`gist`)

| Scope | Access Level | Operations | Test Process |
|-------|--------------|-----------|--------------|
| `gist` | Write | Create/update gists | (Lower Priority 12) |

**Key APIs:**
- `/gists` — Gist management

---

### 15. Notifications (`notifications`)

| Scope | Access Level | Operations | Test Process |
|-------|--------------|-----------|--------------|
| `notifications` | Read | Mark notifications as read | (Lower Priority 13) |

**Key APIs:**
- `/notifications` — Notification management

---

### 16. Team Discussions

| Scope | Access Level | Operations | Test Process |
|-------|--------------|-----------|--------------|
| `write:discussion` | Write | Read/write team discussions | (Lower Priority) |
| `read:discussion` | Read | Read team discussions | (Lower Priority) |

**Key APIs:**
- `/orgs/{org}/teams/{team_slug}/discussions` — Team discussions

---

### 17. Audit Log (`audit_log`)

| Scope | Access Level | Operations | Test Process |
|-------|--------------|-----------|--------------|
| `audit_log` | Read | Read audit logs | Process 10 |
| `read:audit_log` | Read | Read audit log access | Process 10 |

**Key APIs:**
- `/orgs/{org}/audit-log` — Organization audit log (Process 10)
- `/enterprises/{enterprise}/audit-log` — Enterprise audit log

---

### 18. Enterprise Management

| Scope | Access Level | Operations | Test Process |
|-------|--------------|-----------|--------------|
| `admin:enterprise` | Full control | Full enterprise control | (Lower Priority 15) |
| `manage_runners:enterprise` | Write | Manage enterprise runners | (Lower Priority) |
| `read:enterprise` | Read | Read enterprise profile | (Lower Priority) |

**Key APIs:**
- `/enterprises/{enterprise}` — Enterprise data
- `/enterprises/{enterprise}/audit-log` — Enterprise audit log

---

### 19. Network Configurations

| Scope | Access Level | Operations | Test Process |
|-------|--------------|-----------|--------------|
| `write:network_configurations` | Write | Write network configs | (Supplementary) |
| `read:network_configurations` | Read | Read network configs | (Supplementary) |

---

### 20. Projects Management

| Scope | Access Level | Operations | Test Process |
|-------|--------------|-----------|--------------|
| `project` | Write | Full project control | (Supplementary) |
| `read:project` | Read | Read-only projects | (Supplementary) |

---

## Scope-to-Process Mapping

| Process | Required Scopes | Primary API Endpoint |
|---------|-----------------|---------------------|
| 1. Repo Variables | `repo` | `/repos/{owner}/{repo}/actions/variables` |
| 2. Org Variables | `admin:org` | `/orgs/{org}/actions/variables` |
| 3. Repo Secrets (Actions) | `repo` | `/repos/{owner}/{repo}/actions/secrets` |
| 4. Org Secrets (Actions) | `admin:org` | `/orgs/{org}/actions/secrets` |
| 5. Dependabot Secrets | `repo` | `/repos/{owner}/{repo}/dependabot/secrets` |
| 6. Codespaces Secrets | `codespace` | `/repos/{owner}/{repo}/codespaces/secrets` |
| 7. Workflow Dispatch | `workflow` | `/repos/{owner}/{repo}/actions/workflows/{id}/dispatches` |
| 8. Repo Webhooks | `admin:repo_hook` | `/repos/{owner}/{repo}/hooks` |
| 9. Org Webhooks | `admin:org_hook` | `/orgs/{org}/hooks` |
| 10. Audit Log | `audit_log` | `/orgs/{org}/audit-log` |

---

## Error Responses by Scope

### 403 Forbidden (Missing Scope)

```json
{
  "message": "API rate limit exceeded",
  "documentation_url": "https://docs.github.com/rest/overview/rate-limits-for-the-rest-api"
}
```

**Common Causes:**
- Token missing required scope
- Token expired
- Organization restrictions

### 401 Unauthorized

```json
{
  "message": "Bad credentials",
  "documentation_url": "https://docs.github.com/rest"
}
```

**Common Causes:**
- Invalid token
- Malformed Authorization header

---

## Token Chain & Fallback

CODEX_MASTER_KEY implementation uses:

```
1. CODEX_MASTER_KEY    (repo + workflow + security_events + admin:org + ...)
   ↓ (if not available)
2. CODEX_BACKUP_KEY    (same scopes as CODEX_MASTER_KEY)
   ↓ (if not available)
3. GH_TOKEN            (user's personal token or gh CLI token)
   ↓ (if not available)
4. GITHUB_TOKEN        (installation token — limited scopes)
```

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-06-29 | Initial comprehensive scope matrix for all 20+ scopes |

