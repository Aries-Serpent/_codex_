# Mint GitHub tokens per run

The `scripts/ops/codex_mint_tokens_per_run.py` helper mints a short-lived GitHub
installation token and, optionally, a runner registration token. The script is
geared toward Codex operational workflows where each run should produce fresh
credentials.

## Prerequisites

1. Install dependencies:

   ```bash
   pip install requests PyJWT
   ```

2. Set the GitHub App credentials via environment variables (use **either** inline
   PEM or a file path):

   ```bash
   export GITHUB_APP_ID=<app-id>
   export GITHUB_APP_INSTALLATION_ID=<installation-id>
   # Option A: inline PEM (supports \n escapes)
   export GITHUB_APP_PRIVATE_KEY_PEM="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"
   # Option B: file path
   export GITHUB_APP_PRIVATE_KEY_PATH=/secure/app-private-key.pem
   ```

3. Allow outbound requests to GitHub via the Codex network guardrails:

   ```bash
   export CODEX_NET_MODE=online_allowlist
   export CODEX_NET_ALLOWLIST=api.github.com
   ```

   The script also honours the alias `CODEX_ALLOWLIST_HOSTS` if that better fits
   your existing automation.

## Create a scoped installation token

```bash
python scripts/ops/codex_mint_tokens_per_run.py \
  --owner octo-org \
  --repo secret-repo \
  --repositories secret-repo \
  --permissions contents:read actions:write \
  mint
```

The script prints JSON with a `token_masked` field so the raw secret never hits
stdout. Additional context such as the expiration timestamp is included to help
with runbook logging.

## Request a self-hosted runner registration token (output is **masked**)

```bash
python scripts/ops/codex_mint_tokens_per_run.py \
  --owner octo-org \
  --repo builders \
  runner-token
```

The command first mints an installation token, then exchanges it for a runner
registration token. Only the masked representation is printed.

## Revoke the installation token once the action completes

```bash
python scripts/ops/codex_mint_tokens_per_run.py revoke
```

Revocation uses the same short-lived installation token minted for the run.

## Rate-limit headers

Pass `--print-headers` to inspect the core rate-limit buckets after the main
operation. This is useful when running multiple actions sequentially to avoid
exhausting the quota.
