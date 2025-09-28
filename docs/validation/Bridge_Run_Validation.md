# [Validation]: Bridge Run Validation — Copilot CLI via Bridge
> Generated: 2025-09-28 | Author: mbaetiong

## Repo context

| Item | Value |
| ---: | --- |
| Repository | Aries-Serpent/_codex_ |
| Branch | `codex/implement-offline-first-ml-dev-loop_2025-09-27` |
| Commit (target) | `26e0ee5b2e55a6ff2a5631b0e1e30ec39ea29563` |

## Refactor & change log summary

- **Canonical bridge:** Node/Express at `.codex/copilot_bridge/bridge/server.js`.  
- **Python variant:** archived under `docs/examples/python-variant/README.md` with deprecation note.  
- **Automation confinement:** all runnable artifacts under `.codex/copilot_bridge/`.  
- **No active workflows:** example YAML moved to `docs/examples/self_hosted_example.yml`.  
- **Audit artifacts:** bridge manifests → `.codex/copilot_bridge/var/manifests/`; CLI manifests remain in `cwd`.  
- **Security defaults:** deny-by-default beyond allow-list; pre-seeded denies applied.

## Validation matrix

| Check | Command/Action | Expected Result |
| ---: | --- | --- |
| Bridge health | `curl -s http://127.0.0.1:7777/health` | JSON `{ ok: true, service: "copilot-bridge", ... }` |
| First-run auth | `cd <trusted repo>; copilot /login` | Device flow completes; directory trusted; tools approved |
| Run via script | `.codex/copilot_bridge/scripts/test-bridge.sh` | HTTP 200; `ok` with `rc`; manifests written |
| CLI manifest present | `ls -lt .copilot.manifest.*.json` (in `cwd`) | Latest CLI manifest visible |
| Bridge manifest present | `ls -lt .codex/copilot_bridge/var/manifests/` | Latest `bridge.manifest.*.json` present |
| Hash verification (CLI) | `sha256sum <CLI_MANIFEST.json>` | Matches `manifest_sha256` in response |
| Hash verification (Bridge) | `sha256sum <BRIDGE_MANIFEST.json>` | Matches `bridge_manifest_sha256` in response |
| Systemd status | `systemctl status copilot-bridge.service` | Active (running), `ExecStart` points to Node bridge |

## One-shot verification commands

```bash
# 0) Install Copilot CLI and Node deps
npm install -g @github/copilot
node --version

# 1) Start bridge locally (repo root)
node ./.codex/copilot_bridge/bridge/server.js & sleep 1
curl -s http://127.0.0.1:7777/health | jq .

# 2) First-run trust & auth (in your repo CWD)
copilot /login

# 3) Invoke programmatic run (deny-by-default posture)
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

# 4) Verify hashes
CLI_MANIFEST=$(jq -r '.manifest_path' result.json)
CLI_HASH=$(jq -r '.manifest_sha256' result.json)
BR_MANIFEST=$(jq -r '.bridge_manifest_path' result.json)
BR_HASH=$(jq -r '.bridge_manifest_sha256' result.json)
echo "CLI:   $CLI_MANIFEST"
sha256sum "$CLI_MANIFEST"
echo "BRIDG: $BR_MANIFEST"
sha256sum "$BR_MANIFEST"
echo "From API (CLI)  : $CLI_HASH"
echo "From API (BRIDG): $BR_HASH"
```
