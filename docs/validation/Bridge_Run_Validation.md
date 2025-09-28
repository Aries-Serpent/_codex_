# [Validation]: Bridge Run Validation — Copilot CLI via Bridge
> Updated: 2025-09-28

## New preflight checks
- **Node 22 present (unified):**
  ```bash
  node -v   # expect v22.x.y
  ```
- **OR Scoped PATH set for service:** open `/etc/copilot-bridge/env`, ensure Node 22 bin dir precedes others:
  ```bash
  grep '^PATH=' /etc/copilot-bridge/env || echo "PATH override not set"
  ```
- **Copilot CLI requires Node 22+** — install with:
  ```bash
  npm install -g @github/copilot
  ```
  Reference: Installing GitHub Copilot CLI (prereqs: Node.js 22 or later). :contentReference[oaicite:9]{index=9}

## Lock-drift remediation (uv)
If you see:
```text
error: The lockfile at `uv.lock` needs to be updated, but `--locked` was provided.
```
do:
```bash
uv lock
uv sync --locked
```
(Background: `--locked` asserts the lockfile matches requirements, otherwise you must refresh the lock.) :contentReference[oaicite:10]{index=10}

## Programmatic flags reference
The bridge relies on Copilot CLI programmatic mode and tool-gating flags:
- `-p/--prompt`
- `--allow-tool`, `--deny-tool`, `--allow-all-tools` :contentReference[oaicite:11]{index=11}

## One-shot verification (unchanged core flow)
```bash
# Bridge health
curl -s http://127.0.0.1:7777/health | jq .

# First-run trust & auth
copilot /login

# Programmatic run with deny-by-default posture
curl -s -X POST http://127.0.0.1:7777/copilot/run \
  -H 'Content-Type: application/json' \
  -d '{
        "prompt":"List repository files and suggest a README outline.",
        "cwd":"'$PWD'",
        "timeoutMs":300000,
        "allowAllTools":false,
        "allowTools":["shell","git","gh","write"],
        "denyTools":["shell(rm)","shell(sudo)","shell(dd)","shell(curl -X POST)","shell(wget)","shell(docker push)"]
      }' | tee result.json | jq .
```
