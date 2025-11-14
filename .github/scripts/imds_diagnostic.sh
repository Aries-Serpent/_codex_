#!/usr/bin/env bash
#
# IMDS Diagnostic Script
# =====================
# Diagnoses Instance Metadata Service (IMDS) connectivity issues in cloud environments.
#
# Usage:
#   ./imds_diagnostic.sh              # Read-only diagnostic mode (default)
#   ./imds_diagnostic.sh --apply      # Remediation mode (requires approval)
#
# See .github/docs/imds_diagnostic_RUNBOOK.md for detailed documentation.
#
# Exit Codes:
#   0 - Success (IMDS is healthy)
#   1 - IMDS connectivity issues detected
#   2 - Invalid arguments or permissions
#   3 - Remediation failed
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
IMDS_ENDPOINT="${IMDS_ENDPOINT:-169.254.169.254}"
TIMEOUT="${IMDS_TIMEOUT:-5}"
OUTPUT_FILE="${IMDS_OUTPUT_FILE:-diagnostic_results.txt}"
APPLY_MODE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --apply)
            APPLY_MODE=true
            shift
            ;;
        --help|-h)
            echo "IMDS Diagnostic Script"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --apply    Enable remediation mode (requires approval)"
            echo "  --help     Show this help message"
            echo ""
            echo "Environment Variables:"
            echo "  IMDS_ENDPOINT    IMDS endpoint (default: 169.254.169.254)"
            echo "  IMDS_TIMEOUT     Timeout in seconds (default: 5)"
            echo "  IMDS_OUTPUT_FILE Output file (default: diagnostic_results.txt)"
            exit 0
            ;;
        *)
            echo -e "${RED}Error: Unknown argument '$1'${NC}" >&2
            exit 2
            ;;
    esac
done

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $*" | tee -a "$OUTPUT_FILE"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $*" | tee -a "$OUTPUT_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $*" | tee -a "$OUTPUT_FILE"
}

log_error() {
    echo -e "${RED}[✗]${NC} $*" | tee -a "$OUTPUT_FILE"
}

check_root() {
    if [[ $APPLY_MODE == true && $EUID -ne 0 ]]; then
        log_error "Remediation mode requires root privileges"
        log_info "Please run with sudo: sudo $0 --apply"
        exit 2
    fi
}

check_imds_connectivity() {
    log_info "Checking IMDS connectivity at ${IMDS_ENDPOINT}..."
    
    # Test basic connectivity
    if timeout "$TIMEOUT" curl -sf "http://${IMDS_ENDPOINT}/latest/meta-data/" > /dev/null 2>&1; then
        log_success "IMDS endpoint is reachable"
        return 0
    else
        log_error "IMDS endpoint is NOT reachable"
        return 1
    fi
}

check_network_routes() {
    log_info "Checking network routes to IMDS..."
    
    # Check if route to IMDS exists
    if ip route get "$IMDS_ENDPOINT" > /dev/null 2>&1; then
        local route_info
        route_info=$(ip route get "$IMDS_ENDPOINT" 2>&1)
        log_success "Route to IMDS exists: $route_info"
        echo "  $route_info" >> "$OUTPUT_FILE"
        return 0
    else
        log_error "No route to IMDS endpoint"
        return 1
    fi
}

check_firewall_rules() {
    log_info "Checking firewall rules..."
    
    # Check iptables if available
    if command -v iptables > /dev/null 2>&1; then
        if sudo iptables -L -n 2>/dev/null | grep -q "$IMDS_ENDPOINT"; then
            log_warning "Found iptables rules mentioning IMDS endpoint"
            sudo iptables -L -n | grep "$IMDS_ENDPOINT" >> "$OUTPUT_FILE" 2>&1 || true
        else
            log_success "No blocking iptables rules detected"
        fi
    else
        log_info "iptables not available, skipping firewall check"
    fi
    
    return 0
}

check_dns_resolution() {
    log_info "Checking DNS resolution (if applicable)..."
    
    # IMDS uses IP address, but check if DNS is working
    if command -v nslookup > /dev/null 2>&1; then
        if nslookup google.com > /dev/null 2>&1; then
            log_success "DNS resolution is working"
        else
            log_warning "DNS resolution may be impaired"
        fi
    fi
    
    return 0
}

test_imds_endpoints() {
    log_info "Testing IMDS endpoints..."
    
    local endpoints=(
        "latest/meta-data/"
        "latest/meta-data/instance-id"
        "latest/meta-data/instance-type"
        "latest/meta-data/placement/availability-zone"
    )
    
    local success_count=0
    local total_count=${#endpoints[@]}
    
    for endpoint in "${endpoints[@]}"; do
        local url="http://${IMDS_ENDPOINT}/${endpoint}"
        if timeout "$TIMEOUT" curl -sf "$url" > /dev/null 2>&1; then
            log_success "Endpoint accessible: $endpoint"
            ((success_count++))
        else
            log_error "Endpoint NOT accessible: $endpoint"
        fi
    done
    
    echo "Endpoint Test Results: $success_count/$total_count successful" >> "$OUTPUT_FILE"
    
    if [[ $success_count -eq $total_count ]]; then
        return 0
    else
        return 1
    fi
}

check_cloud_provider() {
    log_info "Detecting cloud provider..."
    
    # Try to detect cloud provider
    if timeout "$TIMEOUT" curl -sf "http://${IMDS_ENDPOINT}/latest/meta-data/instance-id" > /dev/null 2>&1; then
        log_success "Cloud provider detected (AWS-compatible IMDS)"
    elif timeout "$TIMEOUT" curl -sf -H "Metadata:true" "http://${IMDS_ENDPOINT}/metadata/instance?api-version=2021-02-01" > /dev/null 2>&1; then
        log_success "Cloud provider detected (Azure IMDS)"
    elif timeout "$TIMEOUT" curl -sf -H "Metadata-Flavor: Google" "http://metadata.google.internal/computeMetadata/v1/" > /dev/null 2>&1; then
        log_success "Cloud provider detected (GCP Metadata Service)"
    else
        log_warning "Could not determine cloud provider or IMDS not available"
    fi
    
    return 0
}

remediate_imds_issues() {
    log_info "Starting IMDS remediation (--apply mode)..."
    
    # Check for approval
    if [[ "${IMDS_REMEDIATE_APPROVED:-}" != "true" ]]; then
        log_error "Remediation requires explicit approval from @mbaetiong"
        log_info "Set IMDS_REMEDIATE_APPROVED=true environment variable to proceed"
        exit 2
    fi
    
    log_warning "Attempting to remediate IMDS connectivity issues..."
    
    # Try to add route if missing
    if ! ip route get "$IMDS_ENDPOINT" > /dev/null 2>&1; then
        log_info "Attempting to add route to IMDS endpoint..."
        if ip route add "$IMDS_ENDPOINT" dev eth0 2>&1 | tee -a "$OUTPUT_FILE"; then
            log_success "Route added successfully"
        else
            log_error "Failed to add route"
            return 1
        fi
    fi
    
    # Check if issues are resolved
    if check_imds_connectivity; then
        log_success "IMDS connectivity restored!"
        return 0
    else
        log_error "Remediation did not resolve IMDS issues"
        return 1
    fi
}

generate_summary() {
    log_info "Generating diagnostic summary..."
    
    echo "" >> "$OUTPUT_FILE"
    echo "========================================" >> "$OUTPUT_FILE"
    echo "DIAGNOSTIC SUMMARY" >> "$OUTPUT_FILE"
    echo "========================================" >> "$OUTPUT_FILE"
    echo "Timestamp: $(date -u '+%Y-%m-%d %H:%M:%S UTC')" >> "$OUTPUT_FILE"
    echo "Hostname: $(hostname)" >> "$OUTPUT_FILE"
    echo "IMDS Endpoint: $IMDS_ENDPOINT" >> "$OUTPUT_FILE"
    echo "Mode: $([ "$APPLY_MODE" = true ] && echo "Remediation" || echo "Read-only")" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    log_info "Full diagnostic results saved to: $OUTPUT_FILE"
}

# Main execution
main() {
    echo "IMDS Diagnostic Script" | tee "$OUTPUT_FILE"
    echo "======================" | tee -a "$OUTPUT_FILE"
    echo "" | tee -a "$OUTPUT_FILE"
    
    check_root
    
    local exit_code=0
    
    # Run diagnostics
    check_cloud_provider || true
    check_network_routes || exit_code=1
    check_firewall_rules || true
    check_dns_resolution || true
    
    if ! check_imds_connectivity; then
        exit_code=1
        test_imds_endpoints || true
        
        if [[ $APPLY_MODE == true ]]; then
            if remediate_imds_issues; then
                exit_code=0
            else
                exit_code=3
            fi
        else
            log_info ""
            log_info "To attempt remediation, run with --apply flag:"
            log_info "  sudo IMDS_REMEDIATE_APPROVED=true $0 --apply"
            log_warning "Note: Remediation requires approval from @mbaetiong"
        fi
    else
        test_imds_endpoints || exit_code=1
    fi
    
    generate_summary
    
    echo ""
    if [[ $exit_code -eq 0 ]]; then
        log_success "IMDS diagnostics completed successfully"
    else
        log_error "IMDS diagnostics detected issues (exit code: $exit_code)"
        log_info "Please attach $OUTPUT_FILE to issue #2226"
    fi
    
    exit $exit_code
}

# Run main function
main
