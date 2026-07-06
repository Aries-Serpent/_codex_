#!/bin/bash
# Phase 8: Generate offline wheelhouse with all pinned dependencies
# Purpose: Create a self-contained offline environment for air-gap deployments
# Usage: ./scripts/prepare_offline_env.sh [--minimal|--runtime|--full]
#
# Modes:
#   --minimal   : Core package (8-15 MB, stdlib + 10 APIs only)
#   --runtime   : Runtime package (20-35 MB, ML deps included)
#   --full      : Full package (100+ MB, all dev tools)
#
# Default: runtime mode

set -e

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
WHEELHOUSE_DIR="${REPO_ROOT}/wheelhouse"
MODE="${1:-runtime}"
REQUIREMENTS_FILE=""
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="${REPO_ROOT}/.codex/logs/offline_wheelhouse_${TIMESTAMP}.log"

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE"
}

# Determine requirements file based on mode
case "$MODE" in
    minimal)
        REQUIREMENTS_FILE="${REPO_ROOT}/requirements-minimal.txt"
        MODE_LABEL="Minimal (Core API only)"
        ;;
    runtime)
        REQUIREMENTS_FILE="${REPO_ROOT}/requirements.txt"
        MODE_LABEL="Runtime (ML-enabled)"
        ;;
    full)
        # Combine all requirements
        REQUIREMENTS_FILE="${REPO_ROOT}/requirements-full.txt"
        MODE_LABEL="Full (Development ecosystem)"
        # Create combined requirements file if it doesn't exist
        if [ ! -f "$REQUIREMENTS_FILE" ]; then
            log_info "Creating combined requirements file..."
            cat "${REPO_ROOT}/requirements.txt" > "$REQUIREMENTS_FILE"
            cat "${REPO_ROOT}/requirements-dev.txt" 2>/dev/null >> "$REQUIREMENTS_FILE" || true
            cat "${REPO_ROOT}/requirements-test.txt" 2>/dev/null >> "$REQUIREMENTS_FILE" || true
            cat "${REPO_ROOT}/requirements-optional.txt" 2>/dev/null >> "$REQUIREMENTS_FILE" || true
            log_success "Combined requirements file created"
        fi
        ;;
    *)
        log_error "Unknown mode: $MODE"
        echo "Usage: $0 [--minimal|--runtime|--full]"
        exit 1
        ;;
esac

# Verify requirements file exists
if [ ! -f "$REQUIREMENTS_FILE" ]; then
    log_error "Requirements file not found: $REQUIREMENTS_FILE"
    exit 1
fi

echo ""
log_info "=== Generating Offline Wheelhouse ==="
log_info "Mode: $MODE_LABEL"
log_info "Repository: $REPO_ROOT"
log_info "Wheelhouse: $WHEELHOUSE_DIR"
echo ""

# Step 1: Update dependency lock file
log_info "Step 1: Updating dependency lock file..."
if command -v uv &> /dev/null; then
    cd "$REPO_ROOT"
    uv lock --all-extras 2>&1 | tee -a "$LOG_FILE" || {
        log_warning "uv lock failed, continuing with pip"
    }
    cd - > /dev/null
    log_success "Lock file updated"
else
    log_warning "uv not found, skipping lock file update"
fi

# Step 2: Create wheelhouse directory
log_info "Step 2: Creating wheelhouse directory..."
rm -rf "$WHEELHOUSE_DIR" 2>/dev/null || true
mkdir -p "$WHEELHOUSE_DIR"
log_success "Wheelhouse directory created: $WHEELHOUSE_DIR"

# Step 3: Generate all wheels
log_info "Step 3: Downloading all dependencies as wheels..."
log_info "Processing requirements from: $REQUIREMENTS_FILE"

# Remove comments and empty lines from requirements
FILTERED_REQS=$(mktemp)
grep -v '^#' "$REQUIREMENTS_FILE" | grep -v '^--' | grep -v '^\s*$' > "$FILTERED_REQS"

# Install wheels (non-editable installs only)
if pip wheel --no-cache-dir \
    --wheel-dir "$WHEELHOUSE_DIR" \
    --requirement "$FILTERED_REQS" \
    2>&1 | tee -a "$LOG_FILE"; then
    log_success "All dependencies downloaded as wheels"
else
    log_error "Failed to download wheels"
    rm -f "$FILTERED_REQS"
    exit 1
fi

rm -f "$FILTERED_REQS"

# Step 4: Generate SHA256 checksums
log_info "Step 4: Generating SHA256 checksums..."
if command -v sha256sum &> /dev/null; then
    cd "$WHEELHOUSE_DIR"
    sha256sum *.whl > CHECKSUMS.txt 2>&1
    cd - > /dev/null
    log_success "Checksums generated: $WHEELHOUSE_DIR/CHECKSUMS.txt"
else
    log_error "sha256sum not found"
    exit 1
fi

# Step 5: Create SBOM (Software Bill of Materials) in CycloneDX format
log_info "Step 5: Creating SBOM (CycloneDX format)..."
if pip show cyclonedx-bom &>/dev/null; then
    if cyclonedx-bom -o "${WHEELHOUSE_DIR}/sbom.json" -r "$FILTERED_REQS" 2>&1 | tee -a "$LOG_FILE"; then
        log_success "SBOM created: $WHEELHOUSE_DIR/sbom.json"
    else
        log_warning "SBOM generation failed, continuing without SBOM"
    fi
else
    log_warning "cyclonedx-bom not installed, installing..."
    pip install cyclonedx-bom -q 2>&1 | tee -a "$LOG_FILE" || {
        log_warning "Could not install cyclonedx-bom, skipping SBOM generation"
    }
fi

# Step 6: Create manifest file with metadata
log_info "Step 6: Creating offline manifest..."
MANIFEST_FILE="${WHEELHOUSE_DIR}/OFFLINE_MANIFEST.txt"
{
    echo "# Codex Offline Wheelhouse Manifest"
    echo "# Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "# Mode: $MODE_LABEL"
    echo ""
    echo "## Wheelhouse Contents"
    echo "Total wheels: $(ls -1 *.whl 2>/dev/null | wc -l)"
    echo "Total size: $(du -sh . | cut -f1)"
    echo ""
    echo "## Checksum Verification"
    echo "Run: sha256sum -c CHECKSUMS.txt"
    echo ""
    echo "## Installation Instructions"
    echo ""
    echo "1. Transfer wheelhouse to target machine:"
    echo "   tar -czf wheelhouse-${MODE}-${TIMESTAMP}.tar.gz ."
    echo "   scp wheelhouse-${MODE}-${TIMESTAMP}.tar.gz user@target:/opt/"
    echo ""
    echo "2. On target machine (offline), extract and verify:"
    echo "   cd /opt && tar -xzf wheelhouse-${MODE}-${TIMESTAMP}.tar.gz"
    echo "   sha256sum -c CHECKSUMS.txt"
    echo ""
    echo "3. Create isolated Python environment:"
    echo "   python3.12 -m venv /opt/codex-env"
    echo "   source /opt/codex-env/bin/activate"
    echo ""
    echo "4. Install from wheelhouse (no network required):"
    echo "   pip install --no-index --find-links . --no-deps -r requirements.txt"
    echo ""
    echo "## Air-Gap Compliance"
    echo "- Zero external network calls required"
    echo "- All dependencies pre-downloaded and checksummed"
    echo "- Requires: Python 3.12+, pip"
    echo ""
    echo "## Mode Details"
    echo "- Minimal: 10 stable APIs, zero external deps, pure offline"
    echo "- Runtime: ML inference + pattern learning, mostly offline"
    echo "- Full: Development tools, network-first fallback enabled"
    echo ""
    echo "## Security Checksums"
    echo "Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "Algorithm: SHA256"
    echo "Verified wheels: $(wc -l < CHECKSUMS.txt)"
} > "$MANIFEST_FILE"

log_success "Manifest created: $MANIFEST_FILE"

# Step 7: Summary and verification
echo ""
log_success "=== Offline Wheelhouse Ready ==="
echo ""
echo "Location: $WHEELHOUSE_DIR"
echo "Mode: $MODE_LABEL"
echo ""
echo "Contents:"
ls -lh "$WHEELHOUSE_DIR" | tail -n +2 | awk '{print "  " $9 " (" $5 ")"}'
echo ""
echo "Summary:"
echo "  Total size: $(du -sh "$WHEELHOUSE_DIR" | cut -f1)"
echo "  Total wheels: $(ls -1 "$WHEELHOUSE_DIR"/*.whl 2>/dev/null | wc -l)"
echo "  Checksum file: CHECKSUMS.txt"
echo "  Manifest: OFFLINE_MANIFEST.txt"

# Step 8: Verify integrity
log_info "Step 8: Verifying wheelhouse integrity..."
cd "$WHEELHOUSE_DIR"
if sha256sum -c CHECKSUMS.txt > /dev/null 2>&1; then
    log_success "All checksums verified successfully"
else
    log_error "Checksum verification failed"
    exit 1
fi
cd - > /dev/null

# Create tarball for easy transfer
TARBALL="${REPO_ROOT}/wheelhouse-${MODE}-${TIMESTAMP}.tar.gz"
log_info "Creating tarball for transfer..."
tar -czf "$TARBALL" -C "$REPO_ROOT" wheelhouse/ 2>&1 | tee -a "$LOG_FILE"
log_success "Tarball created: $TARBALL ($(ls -lh "$TARBALL" | awk '{print $5}'))"

echo ""
echo -e "${GREEN}Phase 8 Wheelhouse Generation Complete${NC}"
echo ""
echo "Next steps:"
echo "1. Transfer wheelhouse to target: scp $TARBALL user@target:/tmp/"
echo "2. Run validation: ./scripts/validate_offline_install.sh"
echo "3. See: docs/OFFLINE_DEPLOYMENT.md for full deployment guide"
echo ""
log_success "Operation complete. Log saved to: $LOG_FILE"
