# Mint GitHub App tokens per run

This script mints short-lived GitHub App installation tokens that can be scoped
to specific repositories and permissions. It is intended for operational tasks
that need a token just-in-time and prefer to avoid long-lived secrets.

## Environment prerequisites

Set the GitHub App credentials via environment variables:

```bash
export GITHUB_APP_ID=<app-id>
export GITHUB_APP_INSTALLATION_ID=<installation-id>
export GITHUB_APP_PRIVATE_KEY="$(cat app-private-key.pem)"
```

Because the script speaks to the GitHub REST API it is gated behind the Codex
network guardrails. Real calls require `CODEX_NET_MODE=online_allowlist` and the
GitHub host present in `CODEX_NET_ALLOWLIST`.

## Dry run

Validate configuration without touching the network:

```bash
python scripts/ops/codex_mint_tokens_per_run.py --action print-rate-limit --dry-run \
  --repos owner/repo --permissions contents=read
```

## Usage

Mint a scoped installation token and print rate-limit buckets:

```bash
python scripts/ops/codex_mint_tokens_per_run.py --action print-rate-limit \
  --repos Aries-Serpent/_codex_ \
  --permissions contents=read \
  --print-headers
```

Probe a repository while keeping the token scoped to the target project:

```bash
python scripts/ops/codex_mint_tokens_per_run.py --action probe-repo \
  --owner Aries-Serpent --repo _codex_ \
  --repos Aries-Serpent/_codex_
```

Request a self-hosted runner registration token:

```bash
python scripts/ops/codex_mint_tokens_per_run.py --action runner-token \
  --owner Aries-Serpent --repo _codex_
```

Revoke the installation token once the action completes:

```bash
python scripts/ops/codex_mint_tokens_per_run.py --action print-rate-limit --revoke-on-exit
```

## Rate-limit headers

Pass `--print-headers` to inspect the core rate-limit buckets after the main
operation. This is useful when running multiple actions sequentially to avoid
exhausting the quota.
