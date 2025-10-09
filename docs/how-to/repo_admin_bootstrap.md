# How-to: Repo Admin Bootstrap (Local, Dry-Run by Default)

This guide hardens a repository **without GitHub Actions** using local scripts:

- Standard labels (create/update)
- Ensure `.github/CODEOWNERS`
- Branch protection on default branch: required PR reviews, **code owner reviews**, conversation resolution, status checks
- Repo security toggles: **secret scanning**, **push protection**, **Dependabot security updates**

## Usage

```bash
# Dry-run (prints plan as JSON)
python scripts/ops/codex_repo_admin_bootstrap.py \
  --owner Aries-Serpent --repo _codex_ \
  --labels-json docs/reference/labels_preset.json \
  --codeowners .github/CODEOWNERS \
  --status-check "ruff" --status-check "pytest"

# Apply (requires env allowlist + token)
export CODEX_NET_MODE=online_allowlist
export CODEX_ALLOWLIST_HOSTS=api.github.com
export GITHUB_APP_INSTALLATION_TOKEN=<token>  # or GITHUB_TOKEN
python scripts/ops/codex_repo_admin_bootstrap.py --owner Aries-Serpent --repo _codex_ --apply
```

## Notes
* Uses `PATCH /repos/{owner}/{repo}` to enable `security_and_analysis` (secret scanning + push protection).
* Uses `PUT /repos/{owner}/{repo}/branches/{branch}/protection` to enforce code owner reviews and conversation resolution.
* Uses `PUT /repos/{owner}/{repo}/contents/.github/CODEOWNERS` to upsert CODEOWNERS via Contents API.
* Uses `/labels` POST/PATCH to upsert labels.

See script docstring for endpoint references.
