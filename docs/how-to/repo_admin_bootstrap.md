# Codex Repo Admin Bootstrap (no workflows)

This guide shows how to standardize a repo (settings, protections, labels, templates) using short-lived GitHub App tokens.

## Prereqs
```bash
export CODEX_NET_MODE=online_allowlist
export CODEX_ALLOWLIST_HOSTS=api.github.com
export GITHUB_APP_ID=<app-id>
export GITHUB_APP_INSTALLATION_ID=<installation-id>
# provide App private key via PEM env or path (see docs/examples/mint_tokens_per_run.md)
```

## Dry-run first
```bash
python -m scripts.ops.codex_repo_admin_bootstrap --owner <org> --repo <name>
```

## Apply standard settings
```bash
python -m scripts.ops.codex_repo_admin_bootstrap --owner <org> --repo <name> --apply
```

## Also add hygiene files (CODEOWNERS, PR/Issue templates)
```bash
python -m scripts.ops.codex_repo_admin_bootstrap --owner <org> --repo <name> --apply --with-templates \
  --codeowners @Aries-Serpent/codex-admins
```

Notes:
- No GitHub Actions workflows are created or touched (see AGENTS.md). :contentReference[oaicite:3]{index=3}
- If Advanced Security features are unavailable on the org/plan, the script skips them gracefully.
