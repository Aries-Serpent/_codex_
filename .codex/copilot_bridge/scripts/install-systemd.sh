#!/usr/bin/env bash
set -euo pipefail

# Usage: sudo .codex/copilot_bridge/scripts/install-systemd.sh /srv/copilot-bridge
TARGET_DIR="${1:-/srv/copilot-bridge}"

echo "[+] Installing Copilot Bridge to ${TARGET_DIR}"
sudo mkdir -p "${TARGET_DIR}"
sudo rsync -a --delete ".codex/copilot_bridge/" "${TARGET_DIR}/.codex/copilot_bridge/"

echo "[+] Preparing /etc/copilot-bridge/env (may set PATH for scoped Node 22)"
sudo mkdir -p /etc/copilot-bridge
if [[ ! -f /etc/copilot-bridge/env ]]; then
  sudo cp "${TARGET_DIR}/.codex/copilot_bridge/.env.example" /etc/copilot-bridge/env
fi

echo "[+] Detecting Node strategy (unified vs scoped)"
pushd "${TARGET_DIR}" >/dev/null
bash ".codex/copilot_bridge/scripts/detect-node-strategy.sh" | tee /tmp/bridge_node_strategy.txt
popd >/dev/null

STRAT="$(grep -E '^strategy=' /tmp/bridge_node_strategy.txt | cut -d= -f2 || true)"
if [[ "${STRAT}" == "unified" ]]; then
  echo "    -> Using UNIFIED Node 22 (host default). No PATH override needed."
else
  echo "    -> Using SCOPED Node 22 (service-only PATH)."
  echo "       Edit /etc/copilot-bridge/env and ensure PATH points to Node 22 bin directory first."
  echo "       Example:"
  echo "         PATH=/opt/node-v22/bin:\$PATH"
fi

echo "[+] Installing systemd unit"
UNIT_SRC="${TARGET_DIR}/.codex/copilot_bridge/ops/systemd/copilot-bridge.service"
UNIT_TMP="$(mktemp)"
sed "s|^WorkingDirectory=.*|WorkingDirectory=${TARGET_DIR}|" "${UNIT_SRC}" > "${UNIT_TMP}"
sudo cp "${UNIT_TMP}" /etc/systemd/system/copilot-bridge.service
rm -f "${UNIT_TMP}"

sudo systemctl daemon-reload
sudo systemctl enable copilot-bridge.service
sudo systemctl restart copilot-bridge.service
sleep 1
sudo systemctl status --no-pager copilot-bridge.service || true

echo "[+] Health check"
curl -sS http://127.0.0.1:7777/health | jq . || true

cat <<'EOF'

Next:
1) Install Copilot CLI (requires Node 22+):
   npm install -g @github/copilot
2) Pre-authenticate and trust the repo directory:
   cd "${DEFAULT_CWD}"; copilot /login
   # Approve necessary tools (shell/git/gh/write).
3) Smoke test:
   .codex/copilot_bridge/scripts/test-bridge.sh

EOF
