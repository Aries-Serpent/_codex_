#!/usr/bin/env bash
#
# IMDS Diagnostic Tool v1.6 (Canonical)
# ======================================
# 
# Purpose: Comprehensive Azure Instance Metadata Service (IMDS) diagnostic tool
# Author: IMDS Diagnostic Team
# Version: 1.6.0
# License: MIT
#
# Description:
#   This script performs comprehensive diagnostics on Azure IMDS connectivity,
#   including network tests, firewall detection, DNS resolution, and metadata
#   retrieval. It outputs structured JSON for aggregation and analysis.
#
# Usage:
#   ./imds_diagnostic.sh [OPTIONS]
#
# Options:
#   -v, --verbose       Enable verbose output
#   -o, --output FILE   Output results to specified JSON file
#   -q, --quiet         Suppress non-error output
#   -h, --help          Display this help message
#   --timeout SECONDS   Set timeout for IMDS requests (default: 5)
#   --skip-firewall     Skip firewall detection tests
#   --skip-dns          Skip DNS resolution tests
#
# Exit Codes:
#   0 - IMDS accessible and working correctly
#   1 - IMDS inaccessible or errors detected
#   2 - Invalid arguments or configuration
#   3 - Missing required dependencies
#
# Environment Variables:
#   IMDS_ENDPOINT       - Override default IMDS endpoint (default: 169.254.169.254)
#   IMDS_API_VERSION    - Override API version (default: 2021-02-01)
#   IMDS_TIMEOUT        - Default timeout in seconds (default: 5)
#

set -euo pipefail

# Script metadata
readonly SCRIPT_VERSION="1.6.0"
readonly SCRIPT_NAME="$(basename "$0")"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Default configuration
IMDS_ENDPOINT="${IMDS_ENDPOINT:-169.254.169.254}"
IMDS_API_VERSION="${IMDS_API_VERSION:-2021-02-01}"
IMDS_TIMEOUT="${IMDS_TIMEOUT:-5}"
VERBOSE=0
QUIET=0
OUTPUT_FILE=""
SKIP_FIREWALL=0
SKIP_DNS=0

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Result storage
declare -A RESULTS
RESULTS[timestamp]="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
RESULTS[version]="$SCRIPT_VERSION"
RESULTS[hostname]="$(hostname -f 2>/dev/null || hostname)"
RESULTS[exit_code]=0

# Logging functions
log_info() {
    if [[ $QUIET -eq 0 ]]; then
        echo -e "${BLUE}[INFO]${NC} $*" >&2
    fi
}

log_success() {
    if [[ $QUIET -eq 0 ]]; then
        echo -e "${GREEN}[SUCCESS]${NC} $*" >&2
    fi
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $*" >&2
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

log_verbose() {
    if [[ $VERBOSE -eq 1 ]]; then
        echo -e "${BLUE}[VERBOSE]${NC} $*" >&2
    fi
}

# Display usage information
usage() {
    cat << EOF
Usage: $SCRIPT_NAME [OPTIONS]

IMDS Diagnostic Tool v$SCRIPT_VERSION

Comprehensive Azure Instance Metadata Service (IMDS) diagnostic tool that
performs network tests, firewall detection, DNS resolution, and metadata
retrieval. Outputs structured JSON for aggregation and analysis.

OPTIONS:
    -v, --verbose           Enable verbose output
    -o, --output FILE       Output results to specified JSON file
    -q, --quiet             Suppress non-error output
    -h, --help              Display this help message
    --timeout SECONDS       Set timeout for IMDS requests (default: $IMDS_TIMEOUT)
    --skip-firewall         Skip firewall detection tests
    --skip-dns              Skip DNS resolution tests

ENVIRONMENT VARIABLES:
    IMDS_ENDPOINT           Override default IMDS endpoint (default: $IMDS_ENDPOINT)
    IMDS_API_VERSION        Override API version (default: $IMDS_API_VERSION)
    IMDS_TIMEOUT            Default timeout in seconds (default: $IMDS_TIMEOUT)

EXIT CODES:
    0 - IMDS accessible and working correctly
    1 - IMDS inaccessible or errors detected
    2 - Invalid arguments or configuration
    3 - Missing required dependencies

EXAMPLES:
    # Basic diagnostic
    $SCRIPT_NAME

    # Verbose output with custom timeout
    $SCRIPT_NAME --verbose --timeout 10

    # Output to JSON file
    $SCRIPT_NAME --output /tmp/imds_results.json

    # Skip optional tests
    $SCRIPT_NAME --skip-firewall --skip-dns

For more information, see: .github/docs/imds_diagnostic_RUNBOOK.md
EOF
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -v|--verbose)
                VERBOSE=1
                shift
                ;;
            -q|--quiet)
                QUIET=1
                shift
                ;;
            -o|--output)
                OUTPUT_FILE="$2"
                shift 2
                ;;
            --timeout)
                IMDS_TIMEOUT="$2"
                shift 2
                ;;
            --skip-firewall)
                SKIP_FIREWALL=1
                shift
                ;;
            --skip-dns)
                SKIP_DNS=1
                shift
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                usage
                exit 2
                ;;
        esac
    done
}

# Check for required dependencies
check_dependencies() {
    local missing_deps=()
    local required_commands=("curl" "jq" "ping" "timeout")
    
    log_verbose "Checking for required dependencies..."
    
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            missing_deps+=("$cmd")
        fi
    done
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        log_error "Missing required dependencies: ${missing_deps[*]}"
        log_error "Please install missing packages and try again."
        RESULTS[dependency_check]="failed"
        RESULTS[missing_dependencies]="${missing_deps[*]}"
        exit 3
    fi
    
    log_success "All dependencies are installed"
    RESULTS[dependency_check]="passed"
}

# Test basic network connectivity to IMDS endpoint
test_network_connectivity() {
    log_info "Testing network connectivity to $IMDS_ENDPOINT..."
    
    local ping_result
    if timeout "$IMDS_TIMEOUT" ping -c 3 "$IMDS_ENDPOINT" &> /dev/null; then
        log_success "IMDS endpoint is reachable via ping"
        RESULTS[network_ping]="success"
        ping_result="true"
    else
        log_warning "IMDS endpoint is not reachable via ping (expected in some configurations)"
        RESULTS[network_ping]="failed"
        ping_result="false"
    fi
    
    log_verbose "Ping result: $ping_result"
}

# Test DNS resolution
test_dns_resolution() {
    if [[ $SKIP_DNS -eq 1 ]]; then
        log_verbose "Skipping DNS resolution tests"
        RESULTS[dns_check]="skipped"
        return
    fi
    
    log_info "Testing DNS resolution..."
    
    # IMDS uses a link-local IP, so DNS shouldn't be involved
    # But we check if the IP is properly configured
    if ip addr show | grep -q "$IMDS_ENDPOINT"; then
        log_warning "IMDS IP found in local interface (unusual configuration)"
        RESULTS[dns_check]="local_interface"
    else
        log_verbose "IMDS IP not on local interface (expected)"
        RESULTS[dns_check]="expected"
    fi
}

# Detect firewall rules blocking IMDS
detect_firewall_rules() {
    if [[ $SKIP_FIREWALL -eq 1 ]]; then
        log_verbose "Skipping firewall detection tests"
        RESULTS[firewall_check]="skipped"
        return
    fi
    
    log_info "Checking for firewall rules affecting IMDS..."
    
    local firewall_detected=0
    
    # Check iptables if available
    if command -v iptables &> /dev/null; then
        if sudo -n iptables -L -n 2>/dev/null | grep -q "$IMDS_ENDPOINT"; then
            log_warning "Firewall rules detected for IMDS endpoint"
            RESULTS[firewall_iptables]="detected"
            firewall_detected=1
        else
            log_verbose "No iptables rules blocking IMDS"
            RESULTS[firewall_iptables]="none"
        fi
    else
        log_verbose "iptables not available"
        RESULTS[firewall_iptables]="unavailable"
    fi
    
    # Check nftables if available
    if command -v nft &> /dev/null; then
        if sudo -n nft list ruleset 2>/dev/null | grep -q "$IMDS_ENDPOINT"; then
            log_warning "nftables rules detected for IMDS endpoint"
            RESULTS[firewall_nftables]="detected"
            firewall_detected=1
        else
            log_verbose "No nftables rules blocking IMDS"
            RESULTS[firewall_nftables]="none"
        fi
    else
        log_verbose "nftables not available"
        RESULTS[firewall_nftables]="unavailable"
    fi
    
    if [[ $firewall_detected -eq 0 ]]; then
        log_success "No firewall rules detected blocking IMDS"
        RESULTS[firewall_check]="passed"
    else
        log_warning "Firewall rules may be blocking IMDS access"
        RESULTS[firewall_check]="warning"
    fi
}

# Test IMDS endpoint accessibility
test_imds_endpoint() {
    log_info "Testing IMDS endpoint accessibility..."
    
    local url="http://${IMDS_ENDPOINT}/metadata/instance?api-version=${IMDS_API_VERSION}"
    local response
    local http_code
    
    log_verbose "Requesting: $url"
    
    # Attempt to retrieve metadata
    response=$(curl -s -w "\n%{http_code}" \
        -H "Metadata: true" \
        --max-time "$IMDS_TIMEOUT" \
        "$url" 2>&1)
    
    local curl_exit=$?
    http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | sed '$d')
    
    log_verbose "Curl exit code: $curl_exit"
    log_verbose "HTTP status code: $http_code"
    
    RESULTS[imds_http_code]="$http_code"
    RESULTS[imds_curl_exit]="$curl_exit"
    
    if [[ $curl_exit -eq 0 ]] && [[ "$http_code" == "200" ]]; then
        log_success "IMDS endpoint is accessible (HTTP $http_code)"
        RESULTS[imds_accessible]="true"
        RESULTS[imds_response_sample]="${body:0:200}..."
        
        # Parse and validate JSON response
        if echo "$body" | jq empty 2>/dev/null; then
            log_success "IMDS response is valid JSON"
            RESULTS[imds_json_valid]="true"
            
            # Extract key metadata fields
            local vm_id=$(echo "$body" | jq -r '.compute.vmId // "N/A"' 2>/dev/null)
            local location=$(echo "$body" | jq -r '.compute.location // "N/A"' 2>/dev/null)
            
            RESULTS[vm_id]="$vm_id"
            RESULTS[azure_location]="$location"
            
            log_verbose "VM ID: $vm_id"
            log_verbose "Location: $location"
        else
            log_warning "IMDS response is not valid JSON"
            RESULTS[imds_json_valid]="false"
        fi
    else
        log_error "IMDS endpoint is not accessible"
        RESULTS[imds_accessible]="false"
        RESULTS[exit_code]=1
        
        # Provide diagnostic information
        case $curl_exit in
            6)
                log_error "Could not resolve host (DNS issue)"
                RESULTS[error_reason]="dns_resolution"
                ;;
            7)
                log_error "Failed to connect to host (network/firewall issue)"
                RESULTS[error_reason]="connection_failed"
                ;;
            28)
                log_error "Operation timeout (IMDS not responding)"
                RESULTS[error_reason]="timeout"
                ;;
            *)
                log_error "Curl error code: $curl_exit"
                RESULTS[error_reason]="curl_error_$curl_exit"
                ;;
        esac
    fi
}

# Test attested data endpoint
test_attested_data() {
    log_info "Testing IMDS attested data endpoint..."
    
    local url="http://${IMDS_ENDPOINT}/metadata/attested/document?api-version=${IMDS_API_VERSION}"
    local response
    local http_code
    
    log_verbose "Requesting: $url"
    
    response=$(curl -s -w "\n%{http_code}" \
        -H "Metadata: true" \
        --max-time "$IMDS_TIMEOUT" \
        "$url" 2>&1)
    
    local curl_exit=$?
    http_code=$(echo "$response" | tail -n1)
    
    log_verbose "Attested data HTTP code: $http_code"
    
    if [[ $curl_exit -eq 0 ]] && [[ "$http_code" == "200" ]]; then
        log_success "Attested data endpoint is accessible"
        RESULTS[attested_data_accessible]="true"
    else
        log_warning "Attested data endpoint is not accessible (HTTP $http_code)"
        RESULTS[attested_data_accessible]="false"
    fi
}

# Generate summary report
generate_summary() {
    log_info "Generating diagnostic summary..."
    
    local total_tests=0
    local passed_tests=0
    local failed_tests=0
    local warnings=0
    
    # Count test results
    for key in "${!RESULTS[@]}"; do
        case "${RESULTS[$key]}" in
            "success"|"passed"|"true")
                ((passed_tests++))
                ((total_tests++))
                ;;
            "failed"|"false")
                ((failed_tests++))
                ((total_tests++))
                ;;
            "warning")
                ((warnings++))
                ((total_tests++))
                ;;
        esac
    done
    
    RESULTS[summary_total_tests]="$total_tests"
    RESULTS[summary_passed]="$passed_tests"
    RESULTS[summary_failed]="$failed_tests"
    RESULTS[summary_warnings]="$warnings"
    
    log_info "Summary: $passed_tests passed, $failed_tests failed, $warnings warnings (out of $total_tests tests)"
}

# Output results as JSON
output_json() {
    local json_output
    
    # Build JSON from associative array
    json_output=$(jq -n \
        --arg version "${RESULTS[version]}" \
        --arg timestamp "${RESULTS[timestamp]}" \
        --arg hostname "${RESULTS[hostname]}" \
        --arg imds_accessible "${RESULTS[imds_accessible]:-unknown}" \
        --arg exit_code "${RESULTS[exit_code]}" \
        '$ARGS.named')
    
    # Add all results to JSON
    for key in "${!RESULTS[@]}"; do
        json_output=$(echo "$json_output" | jq --arg k "$key" --arg v "${RESULTS[$key]}" '. + {($k): $v}')
    done
    
    # Output to file or stdout
    if [[ -n "$OUTPUT_FILE" ]]; then
        echo "$json_output" | jq '.' > "$OUTPUT_FILE"
        log_success "Results written to $OUTPUT_FILE"
    else
        echo "$json_output" | jq '.'
    fi
}

# Main execution
main() {
    parse_args "$@"
    
    log_info "IMDS Diagnostic Tool v$SCRIPT_VERSION"
    log_info "=========================================="
    
    check_dependencies
    test_network_connectivity
    test_dns_resolution
    detect_firewall_rules
    test_imds_endpoint
    test_attested_data
    generate_summary
    output_json
    
    log_info "Diagnostic complete"
    
    exit "${RESULTS[exit_code]}"
}

# Run main function
main "$@"
