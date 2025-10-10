# How-to: Repo Admin Bootstrap (Local, Dry-Run by Default)

This guide hardens a repository **without GitHub Actions** using local scripts:

- Standard labels (create/update)
- Ensure `.github/CODEOWNERS`
- Branch protection on default branch: required PR reviews, **code owner reviews**, conversation resolution, status checks
- Repo security toggles: **secret scanning**, **push protection**, **Dependabot security updates**

## 1) Quickstart

```bash
# Dry-run (detect branch locally, no network calls)
python -m scripts.ops.codex_repo_admin_bootstrap --owner <org> --repo <name> --detect-default-branch

# Apply (requires network allowlist + auth env)
export CODEX_NET_MODE=online_allowlist
export CODEX_ALLOWLIST_HOSTS=api.github.com
# Prefer GitHub App credentials; PAT fallback supported
export GITHUB_APP_ID=<app id>
export GITHUB_APP_INSTALLATION_ID=<installation id>
export GITHUB_APP_PRIVATE_KEY_PATH=/path/to/private-key.pem
# or: export GITHUB_TOKEN=<fine-grained PAT>
python -m scripts.ops.codex_repo_admin_bootstrap --owner <org> --repo <name> --apply --detect-default-branch --dependabot-updates
```

## 2) Prerequisites

| Item | Value |
|---|---|
| Online policy | `CODEX_NET_MODE=online_allowlist`; `CODEX_ALLOWLIST_HOSTS=api.github.com` |
| GitHub App | `GITHUB_APP_ID`, `GITHUB_APP_INSTALLATION_ID`, `GITHUB_APP_PRIVATE_KEY_PATH` or `GITHUB_APP_PRIVATE_KEY_PEM` |
| Scope | Repo admin for target repository (via App installation) |
| Alt auth | `GITHUB_TOKEN` (PAT) fallback supported |

> ⚠️ Online calls require the host to be present in the allowlist guard. The script exits fast when the mode/hosts are missing.

## 3) Flags at a Glance

| Flag | Purpose |
|---|---|
| `--preset` | Merge policy toggles (`default`, `strict`, `relaxed`) |
| `--status-check` | Repeatable flag for required status checks |
| `--required-approvals` | Number of PR approvals enforced in branch protection |
| `--detect-default-branch` | REST lookup for repo default branch (used when `--branch` omitted) |
| `--dependabot-updates` | Enables Dependabot security updates (best-effort) |
| `--labels-json` | Path to labels JSON (created/updated) |
| `--codeowners` | Path to CODEOWNERS template committed via Contents API |

## 4) Dry-Run Output

Dry-run mode prints the planned operations without contacting GitHub:

```json
{
  "dry_run": true,
  "plan": {
    "target": {"owner": "o", "repo": "r", "branch": "main"},
    "repo_settings": {...},
    "branch_protection": {...},
    "labels": [...],
    "files": [...]
  }
}
```

Use this to verify presets and required checks before enabling `--apply`.

## 5) What's Applied (Endpoints)

| Area | Endpoint | Notes |
|---|---|---|
| Repo settings | `PATCH /repos/{owner}/{repo}` | Merge settings; `security_and_analysis` best-effort (plan dependent) |
| Vulnerability alerts | `PUT /repos/{owner}/{repo}/vulnerability-alerts` | `204/202` OK; `403/404` skipped |
| Dependabot updates | `PUT /repos/{owner}/{repo}/automated-security-fixes` | Best-effort enable; `204/202` OK; `403/404` skipped |
| Branch protection | `PUT /repos/{owner}/{repo}/branches/{branch}/protection` | Approvals, CODEOWNERS reviews |
| Labels | `GET/POST/PATCH /repos/{owner}/{repo}/labels` | Create missing; update color/description |
| Hygiene files | `PUT /repos/{owner}/{repo}/contents/{path}` | Base64 contents; skip if exists |

> References: Update repository, labels, contents, branch protection, vulnerability alerts, and automated security fixes endpoints (see GitHub REST docs).

## 6) Cautions

- **Best-effort security features:** GitHub may return `403/404` when the plan is not available (e.g., Free tier). The script reports "skipped" for those cases.
- **No workflow changes:** Scripts intentionally avoid workflow YAML creation/modification.
- **Verbose logs:** Add `--verbose` to surface masked auth headers and target branch detection.
