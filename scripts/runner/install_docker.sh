#!/usr/bin/env bash
# Install Docker Engine on Ubuntu/Debian and add a user to the docker group.
# Usage: sudo bash scripts/runner/install_docker.sh <runner-user>
set -euo pipefail

if [[ $(id -u) -ne 0 ]]; then
  echo "Please run as root (sudo)." >&2
  exit 1
fi

RUNNER_USER="${1:-}"
if [[ -z "${RUNNER_USER}" ]]; then
  echo "Usage: $0 <runner-user>" >&2
  exit 2
fi

apt-get update -y
apt-get install -y ca-certificates curl gnupg lsb-release

install -m 0755 -d /etc/apt/keyrings
if [[ ! -f /etc/apt/keyrings/docker.gpg ]]; then
  curl -fsSL "https://download.docker.com/linux/$(. /etc/os-release; echo "$ID")/gpg" | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
fi
chmod a+r /etc/apt/keyrings/docker.gpg
. /etc/os-release
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/${ID} ${VERSION_CODENAME} stable" > /etc/apt/sources.list.d/docker.list

apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

systemctl enable docker
systemctl start docker

if ! id -nG "${RUNNER_USER}" | grep -qw docker; then
  usermod -aG docker "${RUNNER_USER}"
  echo "[docker] Added ${RUNNER_USER} to docker group. Re-login or run 'newgrp docker' to apply."
fi

docker info >/dev/null
docker buildx version || true
echo "[docker] Installation complete."
