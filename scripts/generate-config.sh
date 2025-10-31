#!/usr/bin/env bash
set -euo pipefail

echo "Generating config from environment..."
mkdir -p config

: "${SBOM_OUTPUT:=sbom.json}"
: "${SBOM_FORMAT:=cyclonedx}"

cat > config/sbom-config.yaml <<EOF
apiVersion: v1
sbom:
  output: ${SBOM_OUTPUT}
  format: ${SBOM_FORMAT}
EOF

echo "Wrote config/sbom-config.yaml"
