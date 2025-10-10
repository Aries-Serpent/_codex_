# [How-to]: Bootstrap Self‑Hosted GitHub Actions Runner  
> Generated: 2025-10-09 20:33:41 UTC | Author: mbaetiong  
Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5

Prereqs
- Online opt‑in: CODEX_NET_MODE=online_allowlist; CODEX_ALLOWLIST_HOSTS=api.github.com
- GitHub App credentials: GITHUB_APP_ID, GITHUB_APP_INSTALLATION_ID, and private key (path or PEM)

Dry‑run
```bash
python -m scripts.ops.bootstrap_self_hosted_runner --owner <org> --repo <name> --dry-run
```

Apply
```bash
export CODEX_NET_MODE=online_allowlist
export CODEX_ALLOWLIST_HOSTS=api.github.com
export GITHUB_APP_ID=...
export GITHUB_APP_INSTALLATION_ID=...
export GITHUB_APP_PRIVATE_KEY_PATH=/secure/github-app.pem

python -m scripts.ops.bootstrap_self_hosted_runner --owner <org> --repo <name> --labels codex,linux,x64
```

Notes
- Uses ephemeral App→Installation tokens, then a short‑lived runner registration token.
- No tokens are persisted to disk.
- Service install requires sudo; use --no-service to skip.

*End*