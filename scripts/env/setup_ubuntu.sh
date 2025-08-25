#!/usr/bin/env bash
set -euo pipefail

# Detect Ubuntu
if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    if [[ ${ID} != "ubuntu" ]]; then
        echo "setup_ubuntu.sh: skipped (ID=${ID})" >&2
        exit 0
    fi
else
    echo "setup_ubuntu.sh: /etc/os-release not found" >&2
    exit 1
fi

# Use sudo if not running as root
SUDO=""
if [[ $(id -u) -ne 0 ]]; then
    SUDO="sudo"
fi

$SUDO apt-get update -y
$SUDO apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    python3 \
    python3-venv \
    python3-pip \
    python3-dev

# Optional CUDA installation
if [[ -n "${CODEX_ENABLE_CUDA:-}" ]]; then
    echo "CODEX_ENABLE_CUDA set; installing CUDA toolkit" >&2
    $SUDO apt-get install -y --no-install-recommends nvidia-cuda-toolkit
fi
