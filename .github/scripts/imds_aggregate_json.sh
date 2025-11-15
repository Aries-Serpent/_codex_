#!/usr/bin/env bash
#
# IMDS JSON Aggregator
# ====================
#
# Purpose: Aggregate multiple IMDS diagnostic JSON outputs into a single report
# Version: 1.0.0
# License: MIT
#
# Description:
#   This script collects multiple IMDS diagnostic JSON files and aggregates
#   them into a single comprehensive report with summary statistics and
#   trend analysis.
#
# Usage:
#   ./imds_aggregate_json.sh [OPTIONS] <input_dir> [output_file]
#
# Options:
#   -v, --verbose       Enable verbose output
#   -f, --format FORMAT Output format: json, html, markdown (default: json)
#   -h, --help          Display this help message
#

set -euo pipefail

# Script metadata
readonly SCRIPT_VERSION="1.0.0"
readonly SCRIPT_NAME="$(basename "$0")"

# Default configuration
VERBOSE=0
OUTPUT_FORMAT="json"
INPUT_DIR=""
OUTPUT_FILE=""

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $*" >&2
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*" >&2
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

# Display usage
usage() {
    cat << EOF
Usage: $SCRIPT_NAME [OPTIONS] <input_dir> [output_file]

IMDS JSON Aggregator v$SCRIPT_VERSION

Aggregate multiple IMDS diagnostic JSON outputs into a single comprehensive
report with summary statistics and trend analysis.

ARGUMENTS:
    input_dir           Directory containing IMDS diagnostic JSON files
    output_file         Output file path (optional, defaults to stdout)

OPTIONS:
    -v, --verbose       Enable verbose output
    -f, --format FORMAT Output format: json, html, markdown (default: json)
    -h, --help          Display this help message

EXAMPLES:
    # Aggregate all JSON files in a directory
    $SCRIPT_NAME /path/to/results

    # Output to file with verbose logging
    $SCRIPT_NAME -v /path/to/results output.json

    # Generate markdown report
    $SCRIPT_NAME -f markdown /path/to/results report.md

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
            -f|--format)
                OUTPUT_FORMAT="$2"
                shift 2
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            -*)
                log_error "Unknown option: $1"
                usage
                exit 2
                ;;
            *)
                if [[ -z "$INPUT_DIR" ]]; then
                    INPUT_DIR="$1"
                elif [[ -z "$OUTPUT_FILE" ]]; then
                    OUTPUT_FILE="$1"
                else
                    log_error "Too many arguments"
                    usage
                    exit 2
                fi
                shift
                ;;
        esac
    done
    
    if [[ -z "$INPUT_DIR" ]]; then
        log_error "Input directory is required"
        usage
        exit 2
    fi
    
    if [[ ! -d "$INPUT_DIR" ]]; then
        log_error "Input directory does not exist: $INPUT_DIR"
        exit 1
    fi
}

# Check dependencies
check_dependencies() {
    local missing_deps=()
    
    if ! command -v jq &> /dev/null; then
        missing_deps+=("jq")
    fi
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        log_error "Missing required dependencies: ${missing_deps[*]}"
        exit 3
    fi
}

# Collect all JSON files
collect_json_files() {
    local json_files=()
    
    log_info "Scanning directory: $INPUT_DIR"
    
    while IFS= read -r -d '' file; do
        if jq empty "$file" 2>/dev/null; then
            json_files+=("$file")
            log_verbose "Found valid JSON: $file"
        else
            log_warning "Skipping invalid JSON: $file"
        fi
    done < <(find "$INPUT_DIR" -type f -name "*.json" -print0)
    
    echo "${json_files[@]}"
}

# Aggregate JSON data
aggregate_json() {
    local files=("$@")
    local aggregated_data="[]"
    
    log_info "Aggregating ${#files[@]} JSON file(s)..."
    
    for file in "${files[@]}"; do
        local content
        content=$(jq '.' "$file")
        aggregated_data=$(echo "$aggregated_data" | jq --argjson item "$content" '. + [$item]')
    done
    
    # Calculate summary statistics
    local total_hosts
    local accessible_count
    local inaccessible_count
    
    total_hosts=$(echo "$aggregated_data" | jq 'length')
    accessible_count=$(echo "$aggregated_data" | jq '[.[] | select(.imds_accessible == "true")] | length')
    inaccessible_count=$(echo "$aggregated_data" | jq '[.[] | select(.imds_accessible == "false")] | length')
    
    log_verbose "Total hosts: $total_hosts"
    log_verbose "Accessible: $accessible_count"
    log_verbose "Inaccessible: $inaccessible_count"
    
    # Build final report
    local report
    report=$(jq -n \
        --arg version "$SCRIPT_VERSION" \
        --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        --argjson total "$total_hosts" \
        --argjson accessible "$accessible_count" \
        --argjson inaccessible "$inaccessible_count" \
        --argjson data "$aggregated_data" \
        '{
            aggregator_version: $version,
            report_timestamp: $timestamp,
            summary: {
                total_hosts: $total,
                imds_accessible: $accessible,
                imds_inaccessible: $inaccessible,
                success_rate: (($accessible / $total) * 100 | floor)
            },
            diagnostics: $data
        }')
    
    echo "$report"
}

# Generate markdown report
generate_markdown() {
    local json_data="$1"
    
    cat << EOF
# IMDS Diagnostic Aggregation Report

**Generated:** $(date -u +%Y-%m-%dT%H:%M:%SZ)
**Aggregator Version:** $SCRIPT_VERSION

## Summary

$(echo "$json_data" | jq -r '
    "- **Total Hosts:** \(.summary.total_hosts)\n" +
    "- **IMDS Accessible:** \(.summary.imds_accessible)\n" +
    "- **IMDS Inaccessible:** \(.summary.imds_inaccessible)\n" +
    "- **Success Rate:** \(.summary.success_rate)%"
')

## Detailed Results

$(echo "$json_data" | jq -r '
    .diagnostics[] | 
    "### \(.hostname // "Unknown Host")\n\n" +
    "- **Timestamp:** \(.timestamp)\n" +
    "- **IMDS Accessible:** \(.imds_accessible)\n" +
    "- **VM ID:** \(.vm_id // "N/A")\n" +
    "- **Location:** \(.azure_location // "N/A")\n" +
    "- **Exit Code:** \(.exit_code)\n"
')

## Recommendations

$(echo "$json_data" | jq -r '
    if .summary.imds_inaccessible > 0 then
        "⚠️  **Action Required:** \(.summary.imds_inaccessible) host(s) cannot access IMDS.\n\n" +
        "Please review the detailed results above and check:\n" +
        "1. Network connectivity to 169.254.169.254\n" +
        "2. Firewall rules blocking IMDS\n" +
        "3. Azure VM configuration\n"
    else
        "✅ All hosts can successfully access IMDS."
    end
')

---
*Report generated by IMDS JSON Aggregator v$SCRIPT_VERSION*
EOF
}

# Output results
output_results() {
    local data="$1"
    
    case "$OUTPUT_FORMAT" in
        json)
            local output
            output=$(echo "$data" | jq '.')
            ;;
        markdown)
            local output
            output=$(generate_markdown "$data")
            ;;
        html)
            log_error "HTML output format not yet implemented"
            exit 2
            ;;
        *)
            log_error "Unknown output format: $OUTPUT_FORMAT"
            exit 2
            ;;
    esac
    
    if [[ -n "$OUTPUT_FILE" ]]; then
        echo "$output" > "$OUTPUT_FILE"
        log_success "Report written to $OUTPUT_FILE"
    else
        echo "$output"
    fi
}

# Main execution
main() {
    parse_args "$@"
    check_dependencies
    
    local json_files
    json_files=$(collect_json_files)
    
    if [[ -z "$json_files" ]]; then
        log_error "No valid JSON files found in $INPUT_DIR"
        exit 1
    fi
    
    local aggregated_data
    aggregated_data=$(aggregate_json $json_files)
    
    output_results "$aggregated_data"
    
    log_success "Aggregation complete"
}

main "$@"
