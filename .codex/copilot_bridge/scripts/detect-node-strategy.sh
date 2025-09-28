#!/usr/bin/env bash
# Decide how to meet the Copilot CLI Node 22 requirement:
#  - "unified"  : host default node >= 22
#  - "scoped"   : use PATH override to a Node 22 install only for the service
# Prints a summary and suggested next steps.

set -euo pipefail

want_major=22
node_bin="${NODE_BIN:-$(command -v node || true)}"

parse_major() {
  local v="$1"
  # Expect formats like v22.3.1 or 22.3.1
  v="${v#v}"
  echo "${v%%.*}"
}

have_major=""
if [[ -n "${node_bin}" ]]; then
  vstr="$("${node_bin}" -v 2>/dev/null || true)"
  if [[ -n "${vstr}" ]]; then
    have_major="$(parse_major "${vstr}")"
  fi
fi

if [[ -n "${have_major}" && "${have_major}" -ge "${want_major}" ]]; then
  echo "strategy=unified"
  echo "node_bin=${node_bin}"
  echo "node_version=$("${node_bin}" -v)"
  exit 0
fi

echo "strategy=scoped"
echo "node_bin=${node_bin:-/usr/bin/node}"
echo "node_version=${vstr:-unknown}"
echo "hint=Install Node ${want_major} under /opt/node-v22 and set PATH in /etc/copilot-bridge/env"
exit 0
