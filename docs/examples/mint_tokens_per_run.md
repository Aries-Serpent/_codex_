# Mint GitHub tokens per run

This script mints short-lived GitHub installation tokens scoped for a single
run. Use it when you need ephemeral credentials for Codex workflows that touch
GitHub resources (cloning private repositories, registering self-hosted
runners, etc.).

## Prerequisites

Set the GitHub App credentials via environment variables (use **either** inline
PEM or a file path):

```bash
export GITHUB_APP_ID=<app-id>
export GITHUB_APP_INSTALLATION_ID=<installation-id>
# Option A: inline PEM (supports \n escapes)
export GITHUB_APP_PRIVATE_KEY_PEM="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"  # pragma: allowlist secret
# Option B: file path
export GITHUB_APP_PRIVATE_KEY_PATH=/secure/app-private-key.pem
```

Because the script speaks to the GitHub REST API it is gated behind the Codex
network guardrails. Real calls require `CODEX_NET_MODE=online_allowlist` **and**
the GitHub host present in `CODEX_NET_ALLOWLIST` (or alias `CODEX_ALLOWLIST_HOSTS`).

## Usage

Dry-run the scoping payload to verify repositories and permissions parsing:

```bash
python -m scripts.ops.codex_mint_tokens_per_run --dry-run \
  --repositories your-org/private-repo \
  --permissions contents=read metadata=read
```

Create a scoped installation token and print the masked value:

```bash
python -m scripts.ops.codex_mint_tokens_per_run --repositories your-org/private-repo \
  --permissions contents=read metadata=read
```

Request a self-hosted runner registration token (output is **masked**):

```bash
python -m scripts.ops.codex_mint_tokens_per_run --runner --owner your-org --repo private-repo
```

Revoke the installation token once the action completes:

```bash
python -m scripts.ops.codex_mint_tokens_per_run --repositories your-org/private-repo \
  --permissions contents=read metadata=read --verbose
```

## Rate-limit headers
Pass `--print-headers` to inspect the core rate-limit buckets after the main operation.
This is useful when running multiple actions sequentially to avoid exhausting the quota.
