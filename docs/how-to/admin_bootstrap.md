# [How-to]: Admin Bootstrap (GitHub App + Protection & Hygiene)  
> Generated: 2025-10-09 20:20:37 UTC | Author: mbaetiong  
Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5

Purpose
- Safely standardize repo settings with ephemeral GitHub App tokens.
- Apply branch protection (approvals, CODEOWNER reviews, conversation resolution).
- Seed hygiene files (CODEOWNERS, PR/Issue templates) without enabling workflows.

Prereqs (offline-by-default; opt-in online)
| Var | Meaning | Example |
|-----|---------|---------|
| CODEX_NET_MODE | Enable online connectors | online_allowlist |
| CODEX_ALLOWLIST_HOSTS | Allowlisted hosts | api.github.com |
| GITHUB_APP_ID | GitHub App ID | 123456 |
| GITHUB_APP_INSTALLATION_ID | Installation ID | 987654 |
| GITHUB_APP_PRIVATE_KEY_PATH | PEM path (or use PEM env) | /secure/github-app.pem |

Dry-run (plan only)
```bash
python -m scripts.ops.codex_repo_admin_bootstrap --owner <org> --repo <name>
```

Apply defaults
```bash
export CODEX_NET_MODE=online_allowlist
export CODEX_ALLOWLIST_HOSTS=api.github.com
export GITHUB_APP_ID=...
export GITHUB_APP_INSTALLATION_ID=...
export GITHUB_APP_PRIVATE_KEY_PATH=/secure/github-app.pem

python -m scripts.ops.codex_repo_admin_bootstrap \
  --owner <org> --repo <name> \
  --preset default --required-approvals 1 \
  --with-templates --apply
```

What it does
- PATCH /repos: squash-only, delete-branch-on-merge, auto-merge (preset dependent), security_and_analysis best-effort.
- PUT protection on main: required approvals, CODEOWNER reviews, conversation resolution.
- PUT vulnerability alerts: best-effort (skips 403/404).
- PUT contents: .github/CODEOWNERS and templates (skip if exists).

Notes
- No workflows enabled/modified.
- Idempotent; dry-run prints plan.
- Pair with CODEOWNERS validation (see separate guide).

*End*