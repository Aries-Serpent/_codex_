#!/usr/bin/env bash
set -euo pipefail
# Usage: sudo .codex/copilot_bridge/scripts/install-systemd.sh /srv/copilot-bridge
TARGET_DIR="${1:-/srv/copilot-bridge}"
echo "[+] Installing Copilot Bridge to ${TARGET_DIR}"
sudo mkdir -p "${TARGET_DIR}"
# Sync only the copilot_bridge subtree to keep artifacts confined
sudo rsync -a --delete ".codex/copilot_bridge/" "${TARGET_DIR}/.codex/copilot_bridge/"
echo "[+] Installing env file to /etc/copilot-bridge/env"
sudo mkdir -p /etc/copilot-bridge
if [[ ! -f /etc/copilot-bridge/env ]]; then
  sudo cp "${TARGET_DIR}/.codex/copilot_bridge/.env.example" /etc/copilot-bridge/env
  echo " -> Edit /etc/copilot-bridge/env to set DEFAULT_CWD to a trusted repo path"
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
cat <<'EON'
Next:
 1) Install Copilot CLI: npm install -g @github/copilot
 2) Pre-authenticate and trust the repo directory:
    cd "${DEFAULT_CWD}"; copilot /login
    # When prompted, trust the directory and approve necessary tools.
 3) Run a smoke test: .codex/copilot_bridge/scripts/test-bridge.sh
EON
