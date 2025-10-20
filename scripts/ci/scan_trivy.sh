#!/usr/bin/env bash
# Scan a container image using trivy. Produces summary text and SARIF.
# Usage: scripts/ci/scan_trivy.sh <image> [output_dir]
set -euo pipefail

IMAGE="${1:-codex:local}"
OUT_DIR="${2:-artifacts/security}"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "${OUT_DIR}"

OUT_TXT="${OUT_DIR}/trivy-${TS}.txt"
OUT_SARIF="${OUT_DIR}/trivy-${TS}.sarif"

if ! command -v trivy >/dev/null 2>&1; then
  echo "[scan] trivy not found. Install https://github.com/aquasecurity/trivy" >&2
  echo "[scan] Docker alternative (writes SARIF to /out):" >&2
  echo "  docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v ${PWD}/${OUT_DIR}:/out aquasec/trivy:latest image --timeout 10m --scanners vuln --severity CRITICAL,HIGH --format sarif -o /out/$(basename \"${OUT_SARIF}\") ${IMAGE}" >&2
  exit 2
fi

echo "[scan] Scanning ${IMAGE} (summary -> ${OUT_TXT}, SARIF -> ${OUT_SARIF})"
trivy image --timeout 10m --scanners vuln --severity CRITICAL,HIGH --format table "${IMAGE}" | tee "${OUT_TXT}"
trivy image --timeout 10m --scanners vuln --severity CRITICAL,HIGH --format sarif -o "${OUT_SARIF}" "${IMAGE}"
echo "[scan] Done. Outputs saved under ${OUT_DIR}"
