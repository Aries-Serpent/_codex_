#!/usr/bin/env bash
# ==============================================================================
# Zendesk AI Package Builder
# ==============================================================================
# Builds and packages Zendesk API integrations for various AI platforms.
#
# Usage:
#   ./build_zendesk_packages.sh [options]
#
# Options:
#   --all           Build all packages (ChatGPT, Zendesk AI, Generic)
#   --chatgpt       Build ChatGPT package only
#   --zendesk       Build Zendesk AI package only
#   --generic       Build generic package only
#   --validate      Validate packages after building
#   --output-dir    Output directory (default: dist/zendesk)
#   --help          Show this help message
#
# Requirements:
#   - Python 3.11+
#   - pip install pyyaml (for YAML validation)
# ==============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Default configuration
OUTPUT_DIR="$PROJECT_ROOT/dist/zendesk"
BUILD_CHATGPT=false
BUILD_ZENDESK=false
BUILD_GENERIC=false
VALIDATE=false
VERSION="1.0.0"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# ==============================================================================
# Utility Functions
# ==============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

show_help() {
    cat << EOF
Zendesk AI Package Builder

Usage:
  $0 [options]

Options:
  --all           Build all packages (ChatGPT, Zendesk AI, Generic)
  --chatgpt       Build ChatGPT package only
  --zendesk       Build Zendesk AI package only
  --generic       Build generic package only
  --validate      Validate packages after building
  --output-dir    Output directory (default: dist/zendesk)
  --version       Package version (default: 1.0.0)
  --help          Show this help message

Examples:
  $0 --all --validate
  $0 --chatgpt --output-dir ./packages
  $0 --zendesk --version 2.0.0

EOF
}

# ==============================================================================
# Validation Functions
# ==============================================================================

validate_json() {
    local file="$1"
    if python3 -c "import json; json.load(open('$file'))" 2>/dev/null; then
        return 0
    else
        return 1
    fi
}

validate_yaml() {
    local file="$1"
    if python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null; then
        return 0
    else
        return 1
    fi
}

validate_package_structure() {
    local package_file="$1"
    local package_type="$2"
    
    log_info "Validating $package_type package structure..."
    
    # Check JSON validity
    if ! validate_json "$package_file"; then
        log_error "Invalid JSON in $package_file"
        return 1
    fi
    
    # Check required fields based on package type
    case "$package_type" in
        chatgpt)
            if ! python3 -c "
import json
with open('$package_file') as f:
    data = json.load(f)
    assert 'name' in data, 'Missing name'
    assert 'actions' in data, 'Missing actions'
    assert 'version' in data, 'Missing version'
" 2>/dev/null; then
                log_error "ChatGPT package missing required fields"
                return 1
            fi
            ;;
        zendesk)
            if ! python3 -c "
import json
with open('$package_file') as f:
    data = json.load(f)
    assert 'integration' in data, 'Missing integration'
    assert 'patterns' in data, 'Missing patterns'
" 2>/dev/null; then
                log_error "Zendesk AI package missing required fields"
                return 1
            fi
            ;;
        generic)
            if ! python3 -c "
import json
with open('$package_file') as f:
    data = json.load(f)
    assert 'patterns' in data, 'Missing patterns'
    assert 'workflows' in data, 'Missing workflows'
" 2>/dev/null; then
                log_error "Generic package missing required fields"
                return 1
            fi
            ;;
    esac
    
    log_success "Package structure valid"
    return 0
}

# ==============================================================================
# Build Functions
# ==============================================================================

setup_output_dir() {
    log_info "Setting up output directory: $OUTPUT_DIR"
    mkdir -p "$OUTPUT_DIR"
}

copy_documentation() {
    log_info "Copying documentation files..."
    
    # Copy OpenAPI spec if it exists
    if [ -f "$PROJECT_ROOT/docs/zendesk/openapi.yaml" ]; then
        cp "$PROJECT_ROOT/docs/zendesk/openapi.yaml" "$OUTPUT_DIR/"
        if [ "$VALIDATE" = true ]; then
            if validate_yaml "$OUTPUT_DIR/openapi.yaml"; then
                log_success "OpenAPI spec copied and validated"
            else
                log_warning "OpenAPI spec copied but validation failed"
            fi
        else
            log_success "OpenAPI spec copied"
        fi
    fi
    
    # Copy Swagger HTML if it exists
    if [ -f "$PROJECT_ROOT/docs/zendesk/swagger.html" ]; then
        cp "$PROJECT_ROOT/docs/zendesk/swagger.html" "$OUTPUT_DIR/"
        log_success "Swagger documentation copied"
    fi
    
    # Copy README files
    if [ -f "$PROJECT_ROOT/docs/zendesk/README.md" ]; then
        cp "$PROJECT_ROOT/docs/zendesk/README.md" "$OUTPUT_DIR/"
    fi
}

build_chatgpt_package() {
    log_info "Building ChatGPT package..."
    
    local output_file="$OUTPUT_DIR/zendesk-chatgpt-package.json"
    
    python3 "$PROJECT_ROOT/tools/zendesk_package_curator.py" \
        --platform chatgpt \
        --output "$output_file"
    
    if [ -f "$output_file" ]; then
        log_success "ChatGPT package built: $output_file"
        
        if [ "$VALIDATE" = true ]; then
            validate_package_structure "$output_file" "chatgpt"
        fi
    else
        log_error "Failed to build ChatGPT package"
        return 1
    fi
}

build_zendesk_package() {
    log_info "Building Zendesk AI package..."
    
    local output_file="$OUTPUT_DIR/zendesk-ai-assistant-package.json"
    
    python3 "$PROJECT_ROOT/tools/zendesk_package_curator.py" \
        --platform zendesk \
        --output "$output_file"
    
    if [ -f "$output_file" ]; then
        log_success "Zendesk AI package built: $output_file"
        
        if [ "$VALIDATE" = true ]; then
            validate_package_structure "$output_file" "zendesk"
        fi
    else
        log_error "Failed to build Zendesk AI package"
        return 1
    fi
}

build_generic_package() {
    log_info "Building generic package..."
    
    local output_file="$OUTPUT_DIR/zendesk-generic-package.json"
    
    python3 "$PROJECT_ROOT/tools/zendesk_package_curator.py" \
        --platform generic \
        --output "$output_file"
    
    if [ -f "$output_file" ]; then
        log_success "Generic package built: $output_file"
        
        if [ "$VALIDATE" = true ]; then
            validate_package_structure "$output_file" "generic"
        fi
    else
        log_error "Failed to build generic package"
        return 1
    fi
}

create_manifest() {
    log_info "Creating package manifest..."
    
    local manifest_file="$OUTPUT_DIR/manifest.json"
    
    python3 << EOF
import json
import os
from datetime import datetime

manifest = {
    "name": "zendesk-ai-packages",
    "version": "$VERSION",
    "generated_at": "$TIMESTAMP",
    "packages": []
}

# List all JSON files in output directory
for filename in os.listdir("$OUTPUT_DIR"):
    if filename.endswith(".json") and filename != "manifest.json":
        filepath = os.path.join("$OUTPUT_DIR", filename)
        with open(filepath) as f:
            data = json.load(f)
            manifest["packages"].append({
                "filename": filename,
                "platform": data.get("platform", data.get("integration", "generic")),
                "version": data.get("version", "$VERSION")
            })

with open("$manifest_file", "w") as f:
    json.dump(manifest, f, indent=2)

print(f"Manifest created with {len(manifest['packages'])} packages")
EOF
    
    log_success "Manifest created: $manifest_file"
}

create_archive() {
    log_info "Creating distribution archive..."
    
    local archive_name="zendesk-ai-packages-${VERSION}.zip"
    local archive_path="$PROJECT_ROOT/dist/$archive_name"
    
    # Create archive
    (cd "$OUTPUT_DIR" && zip -r "../$archive_name" .)
    
    if [ -f "$archive_path" ]; then
        local size
        size=$(du -h "$archive_path" | cut -f1)
        log_success "Archive created: $archive_path ($size)"
    else
        log_warning "Failed to create archive"
    fi
}

run_tests() {
    log_info "Running package tests..."
    
    # Test Python imports
    if python3 -c "
from tools.zendesk_package_curator import ZendeskPackageCurator
from src.zendesk.json_generator import ZendeskJSONGenerator
from src.zendesk.api_client import ZendeskAPIClient

print('All imports successful')
" 2>/dev/null; then
        log_success "Python imports verified"
    else
        log_warning "Some Python imports failed"
    fi
    
    # Run pytest for zendesk tests if available
    if command -v pytest &> /dev/null; then
        log_info "Running pytest for zendesk tests..."
        if pytest "$PROJECT_ROOT/tests/zendesk/" -v --tb=short 2>/dev/null; then
            log_success "All tests passed"
        else
            log_warning "Some tests failed"
        fi
    fi
}

print_summary() {
    echo ""
    echo "============================================================"
    echo "                    Build Summary"
    echo "============================================================"
    echo ""
    echo "Output Directory: $OUTPUT_DIR"
    echo "Version: $VERSION"
    echo "Timestamp: $TIMESTAMP"
    echo ""
    echo "Files created:"
    ls -la "$OUTPUT_DIR"
    echo ""
    echo "============================================================"
}

# ==============================================================================
# Main
# ==============================================================================

main() {
    echo ""
    echo "============================================================"
    echo "           Zendesk AI Package Builder"
    echo "============================================================"
    echo ""
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --all)
                BUILD_CHATGPT=true
                BUILD_ZENDESK=true
                BUILD_GENERIC=true
                shift
                ;;
            --chatgpt)
                BUILD_CHATGPT=true
                shift
                ;;
            --zendesk)
                BUILD_ZENDESK=true
                shift
                ;;
            --generic)
                BUILD_GENERIC=true
                shift
                ;;
            --validate)
                VALIDATE=true
                shift
                ;;
            --output-dir)
                OUTPUT_DIR="$2"
                shift 2
                ;;
            --version)
                VERSION="$2"
                shift 2
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # If no packages specified, build all
    if [ "$BUILD_CHATGPT" = false ] && [ "$BUILD_ZENDESK" = false ] && [ "$BUILD_GENERIC" = false ]; then
        log_info "No packages specified, building all..."
        BUILD_CHATGPT=true
        BUILD_ZENDESK=true
        BUILD_GENERIC=true
    fi
    
    # Setup
    setup_output_dir
    
    # Build packages
    if [ "$BUILD_CHATGPT" = true ]; then
        build_chatgpt_package
    fi
    
    if [ "$BUILD_ZENDESK" = true ]; then
        build_zendesk_package
    fi
    
    if [ "$BUILD_GENERIC" = true ]; then
        build_generic_package
    fi
    
    # Copy documentation
    copy_documentation
    
    # Create manifest
    create_manifest
    
    # Run tests if validating
    if [ "$VALIDATE" = true ]; then
        run_tests
    fi
    
    # Create archive
    create_archive
    
    # Print summary
    print_summary
    
    log_success "Build completed successfully!"
}

main "$@"
