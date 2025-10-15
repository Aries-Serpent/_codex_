# [Guide]: GitHub App Integration (Local & Offline-Safe JWT Build)

> Scope: generate a short-lived installation token from a GitHub App, log in `gh`, and (optionally) register a self-hosted runner—without adding any workflows or Actions.

## Why GitHub App (vs PAT)
- App installation tokens are short-lived (≈1h) and scope-limited to the app’s granted permissions and repositories.
- The JWT for the app is also short-lived (≤10m) and used only to request the installation token.
- This reduces blast radius vs. long-lived PATs and aligns with least-privilege.

See GitHub’s documentation for background on JWT and installation tokens.

## Variables
Provide these via environment (e.g., direnv or your shell).

| Variable | Meaning |
|---|---|
| `GITHUB_APP_ID` | Your GitHub App ID |
| `GITHUB_APP_INSTALLATION_ID` | Installation ID for the org/repo |
| `GITHUB_APP_PRIVATE_KEY_PATH` or `GITHUB_APP_PRIVATE_KEY` | PEM private key for the App |
| `GITHUB_API` | (optional) API base, defaults to `https://api.github.com` |
| `GH_TOKEN` | (optional) When logging in `gh`, set to the installation token |
| `CODEX_RUNNER_TOKEN` | (optional) Short-lived runner registration/removal token |
| `CODEX_RUNNER_URL` | (optional) Repo/Org URL for runner registration |
| `CODEX_RUNNER_DIR` | (optional) Runner directory when unregistering (default `.runner`) |

## Token generation (Python)
```bash
python tools/github/app_token.py --help
GITHUB_APP_ID=12345 \
GITHUB_APP_PRIVATE_KEY_PATH=./app-private-key.pem \
python tools/github/app_token.py --print-jwt | sed 's/..../XXXX/g'  # redact for logs
```

Exchange for installation token (network):
```bash
GITHUB_APP_ID=12345 \
GITHUB_APP_INSTALLATION_ID=67890 \
GITHUB_APP_PRIVATE_KEY_PATH=./app-private-key.pem \
python tools/github/app_token.py --print-installation-token > .gh_inst_token
```

Login `gh` using the token (optional):
```bash
export GH_TOKEN=$(cat .gh_inst_token)
make gh-app-login
```

## Token generation (Bash + openssl)
```bash
GITHUB_APP_ID=12345 \
GITHUB_APP_INSTALLATION_ID=67890 \
GITHUB_APP_PRIVATE_KEY_PATH=./app-private-key.pem \
bash tools/github/app_token.sh > .gh_inst_token
```

## Self-hosted runner (optional)
Prepare short-lived runner token and target URL:
```bash
export CODEX_RUNNER_TOKEN=...   # from org/repo settings
export CODEX_RUNNER_URL=https://github.com/Aries-Serpent/_codex_
DRY_RUN=1 tools/github/runner_register.sh   # inspect steps
```

### Unregistering a runner
Safely remove a runner configuration when decommissioning a host:
```bash
export CODEX_RUNNER_TOKEN=...   # removal token (short-lived)
DRY_RUN=1 tools/github/runner_unregister.sh   # review
tools/github/runner_unregister.sh             # execute
```

## GitHub API wrapper (App token or PAT)
The wrapper emits a sanitized curl for review or performs the request:
```bash
# Redacted curl (no network)
GH_TOKEN=xxxxx python tools/github/gh_api.py \
  --method GET \
  --path /repos/Aries-Serpent/_codex_/branches \
  --print-curl

# Actual call (prints JSON to stdout)
GH_TOKEN=$INSTALLATION_TOKEN python tools/github/gh_api.py \
  --method GET \
  --path /repos/Aries-Serpent/_codex_/branches
```
Use `--param key=value` to add query params, `--data/--data-file` for JSON body, and set `GITHUB_AUTH_SCHEME=Bearer` if you must use a non-default header scheme.

## Copilot CLI (optional)
If you use the GitHub Copilot CLI:
```bash
make copilot-version
copilot --banner   # then /login or export GH_TOKEN/GITHUB_TOKEN with Copilot Requests permission
```

## Security notes
- Never commit tokens or keys. Prefer `direnv`, `pass`, or OS keychain.
- Rotate keys; prefer App tokens over PATs for automation.
- Only generate tokens when needed; keep TTLs minimal.

*End*
