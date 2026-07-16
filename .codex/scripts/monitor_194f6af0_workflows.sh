#!/bin/bash
# Workflow Monitor & Auto-Remediation Daemon for Commit 194f6af0
# Purpose: Continuously monitor workflows and trigger auto-remediation on failures
# Usage: bash .codex/scripts/monitor_194f6af0_workflows.sh [--interval 30] [--timeout 3600]

set -euo pipefail

# Configuration
COMMIT="194f6af0"
COMMIT_LONG="194f6af0dbef18c680f40b40a7d4cfd0b1ea6aee"
PR_NUMBER="5328"
REPO="aries-serpent/_codex_"
INTERVAL=${1:-30}  # Poll interval in seconds
TIMEOUT=${2:-3600}  # Timeout in seconds (default 1 hour)
TRACKING_FILE=".codex/CI_REMEDIATION_194F6AF0.md"
LOG_FILE=".codex/workflow_monitor_194f6af0.log"
REMEDIATION_SCRIPT=".codex/scripts/auto_remediate_194f6af0.sh"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging
log_msg() {
    local level=$1
    shift
    local msg="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[${timestamp}] [${level}] ${msg}" | tee -a "$LOG_FILE"
}

log_info() { log_msg "INFO" "$@"; }
log_success() { log_msg "SUCCESS" "$@"; }
log_warning() { log_msg "WARNING" "$@"; }
log_error() { log_msg "ERROR" "$@"; }

# Start monitoring
log_info "Workflow Monitor Started for Commit $COMMIT"
log_info "Repository: $REPO"
log_info "PR: #$PR_NUMBER"
log_info "Poll Interval: ${INTERVAL}s"
log_info "Timeout: ${TIMEOUT}s"
log_info ""

START_TIME=$(date +%s)
LAST_CHECK=0
REMEDIATION_TRIGGERED=false

# ============================================================================
# Monitoring Loop
# ============================================================================

while true; do
    CURRENT_TIME=$(date +%s)
    ELAPSED=$((CURRENT_TIME - START_TIME))
    
    # Check timeout
    if [[ $ELAPSED -gt $TIMEOUT ]]; then
        log_warning "Timeout reached ($TIMEOUT seconds). Exiting monitoring."
        break
    fi
    
    # Perform checks
    if [[ $((CURRENT_TIME - LAST_CHECK)) -ge $INTERVAL ]]; then
        LAST_CHECK=$CURRENT_TIME
        
        log_info "Polling workflow status (elapsed: ${ELAPSED}s)..."
        
        # Try to get workflow runs for this commit
        # Note: This requires valid GitHub token
        if workflow_runs=$(gh run list \
            --repo "$REPO" \
            --limit 10 \
            --json 'databaseId,name,status,conclusion,createdAt,headCommit' \
            2>/dev/null); then
            
            # Filter for runs on this commit
            matching_runs=$(echo "$workflow_runs" | \
                jq -r ".[] | select(.headCommit | startswith(\"${COMMIT}\")) | .databaseId" 2>/dev/null || echo "")
            
            if [[ -n "$matching_runs" ]]; then
                while IFS= read -r run_id; do
                    log_info "Found workflow run: $run_id"
                    
                    # Get run status
                    run_status=$(gh run view "$run_id" \
                        --repo "$REPO" \
                        --json 'status,conclusion' \
                        2>/dev/null || echo "{}")
                    
                    status=$(echo "$run_status" | jq -r '.status // "unknown"')
                    conclusion=$(echo "$run_status" | jq -r '.conclusion // "none"')
                    
                    log_info "  Status: $status | Conclusion: $conclusion"
                    
                    # Trigger remediation on failure
                    if [[ "$conclusion" == "failure" ]] && [[ "$REMEDIATION_TRIGGERED" == "false" ]]; then
                        log_warning "Workflow failure detected! Triggering auto-remediation..."
                        
                        if bash "$REMEDIATION_SCRIPT"; then
                            log_success "Auto-remediation script executed successfully"
                            REMEDIATION_TRIGGERED=true
                            
                            # Update tracking file
                            echo "" >> "$TRACKING_FILE"
                            echo "### Auto-Remediation Triggered" >> "$TRACKING_FILE"
                            echo "**Time:** $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$TRACKING_FILE"
                            echo "**Workflow Run ID:** $run_id" >> "$TRACKING_FILE"
                            echo "**Status:** Auto-remediation script executed" >> "$TRACKING_FILE"
                        else
                            log_error "Auto-remediation script failed with exit code $?"
                        fi
                    fi
                    
                    # Check if run is still in progress
                    if [[ "$status" == "completed" ]]; then
                        log_info "  Workflow run completed with conclusion: $conclusion"
                    fi
                done <<< "$matching_runs"
            else
                log_info "  No workflow runs found for commit $COMMIT"
            fi
        else
            log_warning "Could not fetch workflow runs (GitHub token may be invalid)"
            log_info "  Falling back to checking REQ-4 and REQ-5 compliance..."
            
            # Fallback: Check local compliance requirements
            if [[ ! -f "docs/accountability/.codex/archive/reports/AGENT_ACCOUNTABILITY_REPORT.md" ]] || \
               ! git diff HEAD~1 HEAD -- "docs/accountability/.codex/archive/reports/AGENT_ACCOUNTABILITY_REPORT.md" &>/dev/null; then
                log_warning "REQ-4 compliance issue detected. Triggering remediation..."
                if [[ "$REMEDIATION_TRIGGERED" == "false" ]]; then
                    bash "$REMEDIATION_SCRIPT" && REMEDIATION_TRIGGERED=true
                fi
            fi
            
            if [[ ! -f "CHANGELOG.md" ]] || \
               ! git diff HEAD~1 HEAD -- CHANGELOG.md &>/dev/null; then
                log_warning "REQ-5 compliance issue detected. Triggering remediation..."
                if [[ "$REMEDIATION_TRIGGERED" == "false" ]]; then
                    bash "$REMEDIATION_SCRIPT" && REMEDIATION_TRIGGERED=true
                fi
            fi
        fi
        
        log_info "Next check in ${INTERVAL}s"
        echo ""
    fi
    
    # Sleep before next check
    sleep 5
done

log_success "Workflow Monitoring Complete"
log_info "Monitor logs: $LOG_FILE"
log_info "Tracking file: $TRACKING_FILE"
