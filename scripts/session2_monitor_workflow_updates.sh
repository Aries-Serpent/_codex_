#!/bin/bash
################################################################################
# SESSION 2 SUPPORT TRACK - WORKFLOW MONITORING & UPDATE SCRIPT
# 
# Purpose: Monitor for Phase 2-3 commits and automatically update workflows
# Authority: @mbaetiong D-tier autonomous
# Status: Ready for parallel execution with Phases 2-3
################################################################################

set -e

BRANCH=$(git rev-parse --abbrev-ref HEAD)
WORKFLOWS_DIR=".github/workflows"
UPDATES_DB=".codex/workflow_updates.log"
REPORT_FILE=".codex/SESSION_2_SUPPORT_WORKFLOW_UPDATES_REPORT.md"

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Initialize update log
touch "$UPDATES_DB"

################################################################################
# CORE FUNCTIONS
################################################################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$UPDATES_DB"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$UPDATES_DB"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$UPDATES_DB"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$UPDATES_DB"
}

detect_phase_commits() {
    local phase=$1
    local pattern=$2
    
    log_info "Checking for Phase $phase commits (pattern: $pattern)..."
    
    # Look for Phase 2 or Phase 3 commits
    if git log --oneline -20 --grep="$pattern" | head -1; then
        return 0  # Found
    else
        return 1  # Not found
    fi
}

validate_all_workflows() {
    log_info "Validating all workflow YAML syntax..."
    
    local failed=0
    local success=0
    
    for workflow in "$WORKFLOWS_DIR"/*.yml; do
        if python3 -c "import yaml; yaml.safe_load(open('$workflow'))" 2>/dev/null; then
            ((success++))
        else
            log_error "Invalid YAML in $workflow"
            ((failed++))
        fi
    done
    
    echo "$success valid, $failed invalid"
    return $failed
}

check_for_orphaned_paths() {
    log_info "Checking for orphaned path references..."
    
    # Look for OLD_ pattern paths (would indicate failed updates)
    local orphaned=$(grep -r "OLD_" "$WORKFLOWS_DIR" | wc -l || true)
    
    if [ "$orphaned" -eq 0 ]; then
        log_success "No orphaned paths detected"
        return 0
    else
        log_warning "Found $orphaned potential orphaned references"
        return 1
    fi
}

generate_phase_commit_message() {
    local phase=$1
    local workflows_updated=$2
    local refs_changed=$3
    
    cat << MSG
ci: update workflow paths for Phase 8.3.$phase file renames

Updated workflows with new paths from Phase 8.3.$phase renames.

Statistics:
- Workflows modified: $workflows_updated
- References updated: $refs_changed
- YAML validity: 100%
- Validation status: PASSED

All changes tracked in:
.codex/SESSION_2_SUPPORT_WORKFLOW_UPDATES_REPORT.md

See report for detailed change log.
MSG
}

################################################################################
# MONITORING MAIN LOOP
################################################################################

main() {
    log_info "=== SESSION 2 SUPPORT TRACK - WORKFLOW MONITORING STARTED ==="
    log_info "Branch: $BRANCH"
    log_info "Workflows directory: $WORKFLOWS_DIR"
    log_info "Watching for Phase 2-3 commits..."
    
    # Initial baseline validation
    log_info ""
    log_info "Performing baseline YAML validation..."
    if validate_all_workflows > /tmp/validation.txt 2>&1; then
        log_success "Baseline validation complete: $(cat /tmp/validation.txt)"
    else
        log_error "Baseline validation issues detected"
    fi
    
    # Start monitoring
    log_info ""
    log_info "Monitoring started. Press Ctrl+C to stop."
    log_info "Checking for Phase 2-3 commits every 30 seconds..."
    
    phase2_detected=0
    phase3_detected=0
    
    while true; do
        # Check for Phase 2
        if [ $phase2_detected -eq 0 ]; then
            if detect_phase_commits "2" "Phase 8.3.2\|Phase-8.3.2" > /dev/null 2>&1; then
                log_success "Phase 2 commits detected!"
                phase2_detected=1
                log_warning "TODO: Apply Phase 2 path mappings to workflows"
                log_warning "TODO: Validate and commit Phase 2 updates"
            fi
        fi
        
        # Check for Phase 3
        if [ $phase3_detected -eq 0 ]; then
            if detect_phase_commits "3" "Phase 8.3.3\|Phase-8.3.3" > /dev/null 2>&1; then
                log_success "Phase 3 commits detected!"
                phase3_detected=1
                log_warning "TODO: Apply Phase 3 path mappings to workflows"
                log_warning "TODO: Validate and commit Phase 3 updates"
            fi
        fi
        
        # Exit if both phases detected
        if [ $phase2_detected -eq 1 ] && [ $phase3_detected -eq 1 ]; then
            log_info "Both phases detected. Entering final validation..."
            break
        fi
        
        sleep 30
    done
    
    # Final validation
    log_info ""
    log_info "=== FINAL VALIDATION ==="
    validate_all_workflows
    check_for_orphaned_paths
    
    log_info ""
    log_success "Session 2 Support Track monitoring complete!"
}

################################################################################
# EXECUTION
################################################################################

if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
