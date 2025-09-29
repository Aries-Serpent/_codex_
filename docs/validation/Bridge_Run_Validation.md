# [Validation]: Bridge Run Validation — Copilot CLI via Bridge
> Generated: 2025-09-28 | Author: mbaetiong

## Refactor & change log summary
- **Canonical bridge:** Node/Express at `.codex/copilot_bridge/bridge/server.js`.
- **Python variant:** archived under `docs/examples/python-variant/README.md` with deprecation note.
- **Automation confinement:** all runnable artifacts under `.codex/copilot_bridge/`.
- **No active workflows:** example YAML moved to `docs/examples/self_hosted_example.yml`.
- **Audit artifacts:** bridge manifests → `.codex/copilot_bridge/var/manifests/`; CLI manifests remain in `cwd`.
- **Security defaults:** deny-by-default beyond allow-list; pre-seeded denies applied.

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
    "cwd":"'"$PWD"'",
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
echo "CLI: $CLI_MANIFEST"; sha256sum "$CLI_MANIFEST"
echo "BRIDG: $BR_MANIFEST"; sha256sum "$BR_MANIFEST"
echo "From API (CLI) : $CLI_HASH"
echo "From API (BRIDG): $BR_HASH"
```

