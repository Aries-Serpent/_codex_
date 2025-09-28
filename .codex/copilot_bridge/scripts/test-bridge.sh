#!/usr/bin/env bash
set -euo pipefail

BRIDGE_URL="${BRIDGE_URL:-http://127.0.0.1:7777}"
CWD="${CWD:-$PWD}"

echo "[*] Posting to ${BRIDGE_URL}/copilot/run (cwd=${CWD})"
PAYLOAD=$(jq -n --arg p "List repository files and suggest a README outline." \
               --arg cwd "$CWD" \
               '{prompt:$p, cwd:$cwd, timeoutMs:300000, allowAllTools:false, allowTools:["shell","git","gh","write"], denyTools:["shell(rm)","shell(sudo)","shell(dd)","shell(curl -X POST)","shell(wget)","shell(docker push)"]}')
curl -sS -X POST "${BRIDGE_URL}/copilot/run" \
     -H "Content-Type: application/json" \
     -d "$PAYLOAD" | jq .
