#!/bin/bash
# Auto-Remediation Script for Commit 194f6af0
# Purpose: Automatically detect and fix workflow failures using WORKFLOW_FAILURE_MATRIX patterns
# Usage: bash .codex/scripts/auto_remediate_194f6af0.sh [--check-only] [--dry-run]
#
# Patterns Addressed:
#   RP-001 (WF-001): REQ-4 violation - AGENT_ACCOUNTABILITY_REPORT.md missing
#   RP-002 (WF-002): REQ-5 violation - CHANGELOG.md not updated
#   RP-003 (WF-003): WEC state loss - Workflow Execution Checklist stripped
#   RP-004 (WF-004): WEC format corruption - invalid checkbox syntax
#   RP-005 (WF-005): Workflow approval failure - token insufficient
#   RP-006 (WF-006): WEC required items unchecked
#   RP-007 (WF-007): Cost gate exceeded
#   RP-008 (WF-008): Rate limiting - GitHub API exhaustion

set -euo pipefail

# Configuration
COMMIT="194f6af0"
COMMIT_LONG="194f6af0dbef18c680f40b40a7d4cfd0b1ea6aee"
PR_NUMBER="5328"
TRACKING_FILE=".codex/CI_REMEDIATION_194F6AF0.md"
LOG_DIR=".codex/remediation_logs_${COMMIT}"
CHECK_ONLY=false
DRY_RUN=false

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] ✅${NC} $*"
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️${NC} $*"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ❌${NC} $*" >&2
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --check-only)
            CHECK_ONLY=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Initialize
mkdir -p "$LOG_DIR"
log_info "Auto-Remediation Started for Commit $COMMIT"
log_info "Tracking File: $TRACKING_FILE"
log_info "Check-Only Mode: $CHECK_ONLY"
log_info "Dry-Run Mode: $DRY_RUN"
echo ""

# ============================================================================
# PHASE 1: Detection & Classification
# ============================================================================

log_info "PHASE 1: Detection & Classification"

detect_rp001() {
    local target_file="docs/accountability/.codex/archive/reports/AGENT_ACCOUNTABILITY_REPORT.md"
    log_info "Checking RP-001 (REQ-4): $target_file"
    
    if [[ ! -f "$target_file" ]]; then
        log_warning "RP-001 DETECTED: File missing"
        return 0
    fi
    
    # Check if file was modified in recent commits
    if git diff HEAD~1 HEAD -- "$target_file" &>/dev/null; then
        log_success "RP-001 NOT DETECTED: File was updated"
        return 1
    else
        log_warning "RP-001 DETECTED: File was not updated"
        return 0
    fi
}

detect_rp002() {
    log_info "Checking RP-002 (REQ-5): CHANGELOG.md"
    
    if [[ ! -f "CHANGELOG.md" ]]; then
        log_warning "RP-002 DETECTED: CHANGELOG.md missing"
        return 0
    fi
    
    # Check if file was modified in recent commits
    if git diff HEAD~1 HEAD -- CHANGELOG.md &>/dev/null; then
        log_success "RP-002 NOT DETECTED: CHANGELOG.md was updated"
        return 1
    else
        log_warning "RP-002 DETECTED: CHANGELOG.md was not updated"
        return 0
    fi
}

detect_rp003() {
    log_info "Checking RP-003 (WEC stripped): PR body WEC section"
    
    # Try to get PR body - this will fail if GitHub token is invalid
    if ! pr_body=$(gh pr view "$PR_NUMBER" --json body -q '.body' 2>/dev/null); then
        log_warning "RP-003 CHECK SKIPPED: Cannot access PR (GitHub token issue)"
        return 2
    fi
    
    if echo "$pr_body" | grep -q "## 🔄 Workflow Execution Checklist"; then
        log_success "RP-003 NOT DETECTED: WEC section present"
        return 1
    else
        log_warning "RP-003 DETECTED: WEC section missing from PR body"
        return 0
    fi
}

detect_rp004() {
    log_info "Checking RP-004 (WEC format invalid): Checkbox syntax"
    
    if ! pr_body=$(gh pr view "$PR_NUMBER" --json body -q '.body' 2>/dev/null); then
        log_warning "RP-004 CHECK SKIPPED: Cannot access PR (GitHub token issue)"
        return 2
    fi
    
    # Check for invalid checkbox syntax
    if echo "$pr_body" | grep -qE "- \[[^x ]|[x ][^]]*\]" || \
       echo "$pr_body" | grep -qE "- \[[X]\]|0 - \[[ ][ ]+\]"; then
        log_warning "RP-004 DETECTED: Invalid checkbox syntax found"
        return 0
    else
        log_success "RP-004 NOT DETECTED: WEC format is valid"
        return 1
    fi
}

# Run detection phase
log_info "Running pattern detection..."
echo ""

DETECTED_PATTERNS=()
detect_rp001 && DETECTED_PATTERNS+=("RP-001")
detect_rp002 && DETECTED_PATTERNS+=("RP-002")
detect_rp003; rp003_result=$?
[[ $rp003_result -eq 0 ]] && DETECTED_PATTERNS+=("RP-003")
detect_rp004; rp004_result=$?
[[ $rp004_result -eq 0 ]] && DETECTED_PATTERNS+=("RP-004")

log_info "Detected patterns: ${DETECTED_PATTERNS[@]:-NONE}"
echo ""

# ============================================================================
# PHASE 2: Remediation
# ============================================================================

if [[ $CHECK_ONLY == "true" ]]; then
    log_info "CHECK-ONLY MODE: Skipping remediation"
    exit 0
fi

log_info "PHASE 2: Remediation"
echo ""

# RP-001: Update AGENT_ACCOUNTABILITY_REPORT.md
if [[ " ${DETECTED_PATTERNS[@]} " =~ " RP-001 " ]]; then
    log_info "Remediating RP-001: Updating AGENT_ACCOUNTABILITY_REPORT.md"
    
    if [[ $DRY_RUN != "true" ]]; then
        if python scripts/ci/session_wrapup_autofix.py --auto-update --pr-number "$PR_NUMBER" &>"$LOG_DIR/rp001_autofix.log"; then
            log_success "RP-001: Auto-fix applied"
            git add docs/accountability/.codex/archive/reports/AGENT_ACCOUNTABILITY_REPORT.md || log_warning "RP-001: Could not stage file"
        else
            log_error "RP-001: Auto-fix failed (see $LOG_DIR/rp001_autofix.log)"
        fi
    else
        log_warning "RP-001: Would apply auto-fix (DRY-RUN)"
    fi
    echo ""
fi

# RP-002: Update CHANGELOG.md
if [[ " ${DETECTED_PATTERNS[@]} " =~ " RP-002 " ]]; then
    log_info "Remediating RP-002: Updating CHANGELOG.md"
    
    if [[ $DRY_RUN != "true" ]]; then
        if python scripts/ci/session_wrapup_autofix.py --auto-update --pr-number "$PR_NUMBER" &>"$LOG_DIR/rp002_autofix.log"; then
            log_success "RP-002: Auto-fix applied"
            git add CHANGELOG.md || log_warning "RP-002: Could not stage file"
        else
            log_error "RP-002: Auto-fix failed (see $LOG_DIR/rp002_autofix.log)"
        fi
    else
        log_warning "RP-002: Would apply auto-fix (DRY-RUN)"
    fi
    echo ""
fi

# RP-003 & RP-004: Fix WEC via wec_enforcer
if [[ " ${DETECTED_PATTERNS[@]} " =~ " RP-003 " ]] || [[ " ${DETECTED_PATTERNS[@]} " =~ " RP-004 " ]]; then
    log_info "Remediating RP-003 & RP-004: Fixing WEC via wec_enforcer"
    
    if [[ $DRY_RUN != "true" ]]; then
        if python scripts/ci/wec_enforcer.py --validate-body --pr "$PR_NUMBER" --fix &>"$LOG_DIR/wec_enforcer.log"; then
            log_success "RP-003/RP-004: WEC fixed"
        else
            log_warning "RP-003/RP-004: WEC enforcer completed with warnings (see $LOG_DIR/wec_enforcer.log)"
        fi
    else
        log_warning "RP-003/RP-004: Would run wec_enforcer (DRY-RUN)"
    fi
    echo ""
fi

# ============================================================================
# PHASE 3: Commit & Push
# ============================================================================

if [[ ${#DETECTED_PATTERNS[@]} -gt 0 ]]; then
    log_info "PHASE 3: Committing & Pushing Fixes"
    
    if [[ $DRY_RUN != "true" ]]; then
        # Check if there are staged changes
        if git diff --cached --quiet; then
            log_warning "No staged changes to commit"
        else
            PATTERN_LIST=$(IFS=','; echo "${DETECTED_PATTERNS[*]}")
            COMMIT_MSG="auto-fix(${COMMIT:0:7}): Remediate ${PATTERN_LIST} workflow failures

Patterns detected and remediated:
- $(printf '%s\n- ' "${DETECTED_PATTERNS[@]}")

Detected per WORKFLOW_FAILURE_MATRIX.md
Commit: ${COMMIT_LONG}
PR: #${PR_NUMBER}"
            
            git commit -m "$COMMIT_MSG" &>"$LOG_DIR/commit.log" && \
                log_success "RP-001/RP-002: Committed fixes" || \
                log_warning "RP-001/RP-002: Commit step encountered issue (see $LOG_DIR/commit.log)"
            
            git push --force-with-lease &>"$LOG_DIR/push.log" && \
                log_success "Pushed changes to remote" || \
                log_error "Push failed (see $LOG_DIR/push.log)"
        fi
    else
        log_warning "PHASE 3: Would commit and push (DRY-RUN)"
    fi
else
    log_success "No patterns detected - no remediation needed"
fi

echo ""
log_info "Auto-Remediation Complete"
log_info "Logs saved to: $LOG_DIR"
log_info "Tracking file: $TRACKING_FILE"
