#!/bin/bash
#
# Docker Security Scanning Script (D1)
#
# Scans Docker images for vulnerabilities using multiple tools:
# - Trivy (comprehensive vulnerability scanner)
# - Docker Scout (if available)
# - Hadolint (Dockerfile linter)
#
# Usage:
#   ./scripts/docker_security_scan.sh <image_name>
#   ./scripts/docker_security_scan.sh codex:latest
#

set -e

IMAGE_NAME="${1:-codex:latest}"
REPORT_DIR="./security-reports"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "========================================"
echo "Docker Security Scan"
echo "========================================"
echo "Image: ${IMAGE_NAME}"
echo "Report directory: ${REPORT_DIR}"
echo "========================================"

# Create reports directory
mkdir -p "${REPORT_DIR}"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

##############################################################################
# 1. Hadolint - Dockerfile Linting
##############################################################################
echo ""
echo "1. Running Hadolint (Dockerfile linter)..."
if command_exists hadolint; then
    # Find Dockerfiles
    for dockerfile in Dockerfile Dockerfile.optimized Dockerfile.gpu; do
        if [ -f "${dockerfile}" ]; then
            echo "  Scanning ${dockerfile}..."
            hadolint "${dockerfile}" | tee "${REPORT_DIR}/hadolint_${dockerfile}_${TIMESTAMP}.txt" || true
        fi
    done
    echo "  ✓ Hadolint scan complete"
else
    echo "  ⚠ Hadolint not found. Install with:"
    echo "    docker pull hadolint/hadolint"
    echo "    # Or: brew install hadolint"
fi

##############################################################################
# 2. Trivy - Vulnerability Scanning
##############################################################################
echo ""
echo "2. Running Trivy (vulnerability scanner)..."
if command_exists trivy; then
    echo "  Scanning image: ${IMAGE_NAME}..."
    
    # Full scan with all severity levels
    trivy image \
        --severity CRITICAL,HIGH,MEDIUM \
        --format table \
        "${IMAGE_NAME}" | tee "${REPORT_DIR}/trivy_${TIMESTAMP}.txt"
    
    # JSON report for CI integration
    trivy image \
        --severity CRITICAL,HIGH,MEDIUM \
        --format json \
        --output "${REPORT_DIR}/trivy_${TIMESTAMP}.json" \
        "${IMAGE_NAME}"
    
    # Check for critical vulnerabilities
    CRITICAL_COUNT=$(trivy image --severity CRITICAL --format json "${IMAGE_NAME}" | jq '[.Results[].Vulnerabilities[]? | select(.Severity == "CRITICAL")] | length')
    
    if [ "${CRITICAL_COUNT:-0}" -gt 0 ]; then
        echo "  ⚠ WARNING: Found ${CRITICAL_COUNT} critical vulnerabilities!"
    else
        echo "  ✓ No critical vulnerabilities found"
    fi
else
    echo "  ⚠ Trivy not found. Install with:"
    echo "    brew install trivy"
    echo "    # Or: https://github.com/aquasecurity/trivy"
fi

##############################################################################
# 3. Docker Scout (if available)
##############################################################################
echo ""
echo "3. Running Docker Scout (CVE scanning)..."
if docker scout --help >/dev/null 2>&1; then
    echo "  Scanning image: ${IMAGE_NAME}..."
    docker scout cves "${IMAGE_NAME}" > "${REPORT_DIR}/scout_${TIMESTAMP}.txt" 2>&1 || true
    echo "  ✓ Docker Scout scan complete"
else
    echo "  ⚠ Docker Scout not available"
    echo "    Enable with: docker scout quickview"
fi

##############################################################################
# 4. Image Analysis
##############################################################################
echo ""
echo "4. Analyzing image properties..."

# Image size
IMAGE_SIZE=$(docker images "${IMAGE_NAME}" --format "{{.Size}}")
echo "  Image size: ${IMAGE_SIZE}"

# Image layers
LAYER_COUNT=$(docker history "${IMAGE_NAME}" --no-trunc | wc -l)
echo "  Layer count: ${LAYER_COUNT}"

# Check if running as non-root
if docker inspect "${IMAGE_NAME}" --format='{{.Config.User}}' | grep -q "^[0-9]"; then
    echo "  ✓ Running as non-root user"
else
    USER=$(docker inspect "${IMAGE_NAME}" --format='{{.Config.User}}')
    if [ -n "${USER}" ] && [ "${USER}" != "root" ]; then
        echo "  ✓ Running as user: ${USER}"
    else
        echo "  ⚠ WARNING: Running as root!"
    fi
fi

# Check exposed ports
PORTS=$(docker inspect "${IMAGE_NAME}" --format='{{json .Config.ExposedPorts}}')
echo "  Exposed ports: ${PORTS}"

# Check health check
HEALTHCHECK=$(docker inspect "${IMAGE_NAME}" --format='{{json .Config.Healthcheck}}')
if [ "${HEALTHCHECK}" != "null" ]; then
    echo "  ✓ Health check configured"
else
    echo "  ⚠ No health check configured"
fi

##############################################################################
# 5. Best Practices Check
##############################################################################
echo ""
echo "5. Checking Docker best practices..."

# Check for latest tag
if [[ "${IMAGE_NAME}" == *":latest" ]] || [[ "${IMAGE_NAME}" != *":"* ]]; then
    echo "  ⚠ WARNING: Using 'latest' tag is not recommended for production"
else
    echo "  ✓ Using versioned tag"
fi

# Check for multi-stage build
BUILD_STAGES=$(docker history "${IMAGE_NAME}" --format "{{.CreatedBy}}" | grep -c "FROM" || true)
if [ "${BUILD_STAGES}" -gt 1 ]; then
    echo "  ✓ Multi-stage build detected"
else
    echo "  ⚠ Single-stage build (consider multi-stage for smaller images)"
fi

##############################################################################
# Summary
##############################################################################
echo ""
echo "========================================"
echo "Scan Summary"
echo "========================================"
echo "Reports saved to: ${REPORT_DIR}/"
echo ""
echo "Review files:"
ls -lh "${REPORT_DIR}/"*"${TIMESTAMP}"* 2>/dev/null || echo "  No reports generated"
echo ""
echo "========================================"
echo "Security scan complete!"
echo "========================================"

# Exit with error if critical vulnerabilities found
if [ "${CRITICAL_COUNT:-0}" -gt 0 ]; then
    echo ""
    echo "⚠ CRITICAL: Found ${CRITICAL_COUNT} critical vulnerabilities"
    echo "   Please review and remediate before deploying to production"
    exit 1
fi

exit 0
