#!/usr/bin/env bash
#
# IMDS Diagnostic Script
# Purpose: Detect and optionally remediate issues blocking access to Azure Instance Metadata Service
# Issue: #2226
# Author: mbaetiong
# Generated: 2025-11-14 21:33:15 UTC
#
# Usage:
#   ./imds_diagnostic.sh              # Read-only diagnostic mode
#   ./imds_diagnostic.sh --dry-run    # Simulate remediation (no changes)
#   ./imds_diagnostic.sh --apply      # Apply remediation (requires root)
#
# Exit codes:
#   0 = diagnostics ran, no remediation required
#   1 = error occurred
#   2 = remediation recommended but not applied
#   3 = remediation applied successfully
#

set -euo pipefail

readonly IMDS_ENDPOINT="169.254.169.254"
readonly IMDS_URL="http://169.254.169.254/metadata/instance?api-version=2021-02-01"
readonly OUTPUT_FILE="diagnostic_results.txt"
readonly TIMESTAMP=$(date -u '+%Y-%m-%d %H:%M:%S UTC')

# Parse command-line arguments
MODE="diagnostic"  # diagnostic, dry-run, or apply

for arg in "$@"; do
    case "$arg" in
        --dry-run)
            MODE="dry-run"
            ;;
        --apply)
            MODE="apply"
            ;;
        --help|-h)
            echo "IMDS Diagnostic Script"
            echo ""
            echo "Usage:"
            echo "  $0              # Read-only diagnostic mode"
            echo "  $0 --dry-run    # Simulate remediation (no changes)"
            echo "  $0 --apply      # Apply remediation (requires root)"
            echo ""
            echo "Output: $OUTPUT_FILE"
            exit 0
            ;;
        *)
            echo "Unknown argument: $arg" >&2
            echo "Use --help for usage information" >&2
            exit 1
            ;;
    esac
done

# Logging functions
log() {
    echo "[$(date -u '+%Y-%m-%d %H:%M:%S UTC')] $*" | tee -a "$OUTPUT_FILE"
}

log_header() {
    echo "" | tee -a "$OUTPUT_FILE"
    echo "========================================" | tee -a "$OUTPUT_FILE"
    echo "$*" | tee -a "$OUTPUT_FILE"
    echo "========================================" | tee -a "$OUTPUT_FILE"
}

log_check() {
    echo "[CHECK] $*" | tee -a "$OUTPUT_FILE"
}

log_ok() {
    echo "[OK] $*" | tee -a "$OUTPUT_FILE"
}

log_warn() {
    echo "[WARNING] $*" | tee -a "$OUTPUT_FILE"
}

log_error() {
    echo "[ERROR] $*" | tee -a "$OUTPUT_FILE"
}

log_fix() {
    echo "[FIX] $*" | tee -a "$OUTPUT_FILE"
}

# Initialize output file
{
    echo "IMDS Diagnostic Report"
    echo "Generated: $TIMESTAMP"
    echo "Mode: $MODE"
    echo "Host: $(hostname)"
    echo "User: $(whoami)"
    echo ""
} > "$OUTPUT_FILE"

NEEDS_REMEDIATION=0
REMEDIATION_APPLIED=0

# Check 1: Basic network connectivity
log_header "Check 1: Basic Network Connectivity"

log_check "Testing if IMDS endpoint $IMDS_ENDPOINT is reachable via ping"
if ping -c 1 -W 2 "$IMDS_ENDPOINT" &>/dev/null; then
    log_ok "IMDS endpoint is reachable via ping"
else
    log_warn "IMDS endpoint is NOT reachable via ping (this may be normal if ICMP is blocked)"
fi

log_check "Testing TCP connectivity to IMDS on port 80"
if timeout 5 bash -c "cat < /dev/null > /dev/tcp/$IMDS_ENDPOINT/80" 2>/dev/null; then
    log_ok "TCP connection to IMDS port 80 successful"
else
    log_error "Cannot establish TCP connection to IMDS port 80"
    NEEDS_REMEDIATION=1
fi

# Check 2: HTTP request to IMDS
log_header "Check 2: HTTP Request to IMDS"

log_check "Attempting HTTP GET request to IMDS metadata endpoint"
CURL_OUTPUT=$(mktemp)
CURL_EXIT=0
if curl -f -s -H "Metadata:true" --max-time 5 "$IMDS_URL" > "$CURL_OUTPUT" 2>&1; then
    log_ok "Successfully retrieved IMDS metadata"
    log "Response size: $(wc -c < "$CURL_OUTPUT") bytes"
else
    CURL_EXIT=$?
    log_error "Failed to retrieve IMDS metadata (curl exit code: $CURL_EXIT)"
    log "Error output: $(cat "$CURL_OUTPUT")"
    NEEDS_REMEDIATION=1
fi
rm -f "$CURL_OUTPUT"

# Check 3: Firewall rules
log_header "Check 3: Firewall Configuration"

log_check "Checking iptables rules that might block IMDS"
if command -v iptables >/dev/null 2>&1; then
    if iptables -L -n 2>/dev/null | grep -q "$IMDS_ENDPOINT"; then
        log_warn "Found iptables rules mentioning IMDS endpoint"
        iptables -L -n | grep "$IMDS_ENDPOINT" | tee -a "$OUTPUT_FILE"
        NEEDS_REMEDIATION=1
    else
        log_ok "No iptables rules blocking IMDS found"
    fi
else
    log "iptables command not available"
fi

# Check 4: /etc/hosts file
log_header "Check 4: /etc/hosts Configuration"

log_check "Checking /etc/hosts for IMDS endpoint overrides"
if grep -q "$IMDS_ENDPOINT" /etc/hosts 2>/dev/null; then
    log_warn "Found IMDS endpoint in /etc/hosts - this may cause issues"
    grep "$IMDS_ENDPOINT" /etc/hosts | tee -a "$OUTPUT_FILE"
    NEEDS_REMEDIATION=1
else
    log_ok "/etc/hosts does not contain IMDS endpoint overrides"
fi

# Check 5: Routing
log_header "Check 5: Routing Table"

log_check "Checking routing table for IMDS endpoint"
if command -v ip >/dev/null 2>&1; then
    ROUTE_OUTPUT=$(ip route get "$IMDS_ENDPOINT" 2>&1 || true)
    log "Route to IMDS: $ROUTE_OUTPUT"
    
    if echo "$ROUTE_OUTPUT" | grep -q "Network is unreachable"; then
        log_error "IMDS endpoint is unreachable according to routing table"
        NEEDS_REMEDIATION=1
    else
        log_ok "Route to IMDS appears to be configured"
    fi
else
    log "ip command not available"
fi

# Check 6: DNS resolution (should NOT resolve IMDS)
log_header "Check 6: DNS Resolution"

log_check "Verifying that IMDS IP is not being resolved via DNS"
if command -v nslookup >/dev/null 2>&1; then
    if nslookup "$IMDS_ENDPOINT" 2>&1 | grep -q "can't find"; then
        log_ok "IMDS IP is not in DNS (expected)"
    else
        log_warn "Unexpected DNS response for IMDS IP"
    fi
else
    log "nslookup command not available"
fi

# Remediation section
if [ "$NEEDS_REMEDIATION" -eq 1 ]; then
    log_header "Remediation Required"
    
    if [ "$MODE" = "diagnostic" ]; then
        log "Remediation is needed but not requested."
        log "Run with --dry-run to see what would be done."
        log "Run with --apply to apply fixes (requires root)."
        exit 2
        
    elif [ "$MODE" = "dry-run" ]; then
        log_header "Remediation Steps (DRY RUN - no changes will be made)"
        
        log_fix "[DRY RUN] Would backup /etc/hosts to /etc/hosts.backup.$(date +%Y%m%d_%H%M%S)"
        
        if grep -q "$IMDS_ENDPOINT" /etc/hosts 2>/dev/null; then
            log_fix "[DRY RUN] Would remove IMDS entries from /etc/hosts"
        fi
        
        if command -v iptables >/dev/null 2>&1; then
            if iptables -L -n 2>/dev/null | grep -q "$IMDS_ENDPOINT"; then
                log_fix "[DRY RUN] Would review and potentially remove blocking iptables rules"
                log_fix "[DRY RUN] Note: iptables rules require manual review for safety"
            fi
        fi
        
        log "Dry run complete. No changes were made."
        log "Run with --apply to perform these changes (requires root)."
        exit 2
        
    elif [ "$MODE" = "apply" ]; then
        log_header "Applying Remediation"
        
        # Check for root privileges
        if [ "$(id -u)" -ne 0 ]; then
            log_error "Remediation requires root privileges. Please run with sudo."
            exit 1
        fi
        
        # Backup /etc/hosts
        BACKUP_FILE="/etc/hosts.backup.$(date +%Y%m%d_%H%M%S)"
        log_fix "Backing up /etc/hosts to $BACKUP_FILE"
        cp /etc/hosts "$BACKUP_FILE"
        
        # Remove IMDS entries from /etc/hosts
        if grep -q "$IMDS_ENDPOINT" /etc/hosts 2>/dev/null; then
            log_fix "Removing IMDS entries from /etc/hosts"
            sed -i.bak "/$IMDS_ENDPOINT/d" /etc/hosts
            REMEDIATION_APPLIED=1
        fi
        
        # Note about iptables
        if command -v iptables >/dev/null 2>&1; then
            if iptables -L -n 2>/dev/null | grep -q "$IMDS_ENDPOINT"; then
                log_warn "iptables rules blocking IMDS detected but not automatically removed"
                log_warn "Please review iptables rules manually and remove if appropriate"
                log_warn "Suggested: iptables -D <chain> <rule-number>"
            fi
        fi
        
        log "Remediation applied. Please re-run diagnostics to verify."
        exit 3
    fi
else
    log_header "Summary"
    log_ok "All checks passed. IMDS appears to be accessible."
    log "No remediation required."
    exit 0
fi
