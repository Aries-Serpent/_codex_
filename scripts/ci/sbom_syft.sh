#!/usr/bin/env bash
# Generate an SBOM for a container image using syft (SPDX JSON).
# Usage: scripts/ci/sbom_syft.sh <image> [output_dir]
set -euo pipefail

IMAGE="${1:-codex:local}"
OUT_DIR="${2:-artifacts/security}"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "${OUT_DIR}"

OUT_SBOM="${OUT_DIR}/sbom-${TS}.spdx.json"

if ! command -v syft >/dev/null 2>&1; then
  echo "[sbom] syft not found. Install https://github.com/anchore/syft" >&2
  echo "[sbom] Docker alternative:" >&2
  echo "  docker run --rm -v /var/run/docker.sock:/var/run/docker.sock ghcr.io/anchore/syft ${IMAGE} -o spdx-json > ${OUT_SBOM}" >&2
  exit 2
fi

echo "[sbom] Generating SBOM (SPDX JSON) for ${IMAGE} -> ${OUT_SBOM}"
syft "${IMAGE}" -o spdx-json > "${OUT_SBOM}"
echo "[sbom] Done: ${OUT_SBOM}"
