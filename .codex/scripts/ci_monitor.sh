#!/bin/bash
# CI Monitoring Script
# Monitors GitHub Actions workflow runs and detects failures
#
# Usage:
#   ./ci_monitor.sh [MAX_DURATION_SECONDS] [POLL_INTERVAL_SECONDS]
#   Example: ./ci_monitor.sh 3000 30
#
# Environment:
#   GITHUB_REPOSITORY - Repository in owner/repo format (default: Aries-Serpent/_codex_)

set -euo pipefail

REPO="${GITHUB_REPOSITORY:-Aries-Serpent/_codex_}"
MAX_DURATION="${1:-3000}"  # 50 minutes default
POLL_INTERVAL="${2:-30}"

# Validate numeric inputs to prevent command injection
if ! [[ "$MAX_DURATION" =~ ^[0-9]+$ ]]; then
    echo "Error: MAX_DURATION must be a positive integer" >&2
    exit 1
fi
if ! [[ "$POLL_INTERVAL" =~ ^[0-9]+$ ]]; then
    echo "Error: POLL_INTERVAL must be a positive integer" >&2
    exit 1
fi

START_TIME=$(date +%s)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

monitor_workflows() {
    local completed=0
    local failed=0
    local in_progress=0
    local action_required=0
    
    # Get recent workflow runs
    local runs=$(gh run list --repo "$REPO" --limit 30 --json databaseId,name,status,conclusion 2>/dev/null || echo "[]")
    
    if [ "$runs" = "[]" ]; then
        log_warning "No workflow runs found or GitHub CLI not authenticated"
        return 1
    fi
    
    # Parse and count statuses
    completed=$(echo "$runs" | jq '[.[] | select(.status == "completed")] | length')
    in_progress=$(echo "$runs" | jq '[.[] | select(.status == "in_progress" or .status == "queued")] | length')
    failed=$(echo "$runs" | jq '[.[] | select(.conclusion == "failure")] | length')
    action_required=$(echo "$runs" | jq '[.[] | select(.conclusion == "action_required")] | length')
    
    echo ""
    echo "📊 Workflow Status Summary:"
    echo "   Completed: $completed"
    echo "   In Progress: $in_progress"
    echo "   Failed: $failed"
    echo "   Action Required: $action_required"
    
    # List any failed workflows
    if [ "$failed" -gt 0 ]; then
        log_error "Failed Workflows:"
        echo "$runs" | jq -r '.[] | select(.conclusion == "failure") | "   - \(.name) (ID: \(.databaseId))"'
    fi
    
    # Return number of in-progress workflows
    echo "$in_progress"
}

analyze_failure() {
    local run_id=$1
    
    log_info "Analyzing failure for run ID: $run_id"
    
    # Create logs directory
    mkdir -p .codex/logs
    
    # Download logs
    if gh run view "$run_id" --repo "$REPO" --log > ".codex/logs/run_${run_id}.log" 2>/dev/null; then
        log_success "Downloaded logs for run $run_id"
        
        # Run diagnosis if Python script exists
        if [ -f ".codex/scripts/diagnose_ci_failure.py" ]; then
            python .codex/scripts/diagnose_ci_failure.py "$run_id"
        fi
    else
        log_warning "Could not download logs for run $run_id"
    fi
}

main() {
    log_info "Starting CI Monitoring"
    log_info "Repository: $REPO"
    log_info "Max Duration: $MAX_DURATION seconds"
    log_info "Poll Interval: $POLL_INTERVAL seconds"
    echo ""
    
    while true; do
        current_time=$(date +%s)
        elapsed=$((current_time - START_TIME))
        
        if [[ "$elapsed" -ge "$MAX_DURATION" ]]; then
            log_warning "Maximum monitoring duration reached (${MAX_DURATION}s)"
            break
        fi
        
        log_info "Polling workflows... (${elapsed}s elapsed)"
        
        in_progress=$(monitor_workflows)
        
        # Check if all workflows completed (use [[ for safer string comparison)
        if [[ "$in_progress" == "0" ]]; then
            log_success "All workflows completed"
            break
        fi
        
        log_info "Waiting ${POLL_INTERVAL}s before next poll..."
        sleep "$POLL_INTERVAL"
    done
    
    log_success "Monitoring complete"
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
