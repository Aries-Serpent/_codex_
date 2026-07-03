#!/bin/bash

# DependaBot Sheriff - Adapted for Aries-Serpent/_codex_
# Consolidates Dependabot PRs into a single mergeable PR
#
# Based on: https://github.com/kiba-d/dependabot-sheriff
# Adapted for: Aries-Serpent/_codex_ repository conventions

set -e

# ============================================================================
# Configuration
# ============================================================================

# Define log file location (in .codex/ to follow repo conventions)
# Use dynamic path discovery instead of hardcoding repo path
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"
LOG_DIR="$REPO_ROOT/.codex/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/dependabot_sheriff_$(date +%Y%m%d_%H%M%S).log"

# Base branch (main for this repo)
BASE_BRANCH="${BASE_BRANCH:-main}"

# Get current date in YYYYMMDD format
DATE=$(date +%Y%m%d)

# Define branch name with current date
BRANCH_NAME="dependabot-consolidated-$DATE"

# Assignee for the consolidated PR (can be overridden with environment variable)
ASSIGNEE="${DEPENDABOT_ASSIGNEE:-mbaetiong}"

# ============================================================================
# Logging Functions
# ============================================================================

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ ERROR: $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ SUCCESS: $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️  WARNING: $1" | tee -a "$LOG_FILE"
}

log_info() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ℹ️  INFO: $1" | tee -a "$LOG_FILE"
}

# ============================================================================
# Prerequisite Checks
# ============================================================================

check_prerequisites() {
    log "🔍 Checking prerequisites..."

    # Check Git
    if ! command -v git &> /dev/null; then
        log_error "Git is not installed. Please install Git first."
        exit 1
    fi

    # Check GitHub CLI
    if ! command -v gh &> /dev/null; then
        log_error "GitHub CLI (gh) is not installed. Please install it first."
        log_info "Install: brew install gh (macOS) or visit https://cli.github.com/"
        exit 1
    fi

    # Check GitHub CLI authentication
    if ! gh auth status &> /dev/null; then
        log_error "GitHub CLI is not authenticated. Please run 'gh auth login'"
        exit 1
    fi

    log_success "All prerequisites met"
}

# ============================================================================
# Main Script Logic
# ============================================================================

main() {
    log "🤠 DependaBot Sheriff starting..."
    log "📁 Working directory: $(pwd)"
    log "📝 Log file: $LOG_FILE"

    # Check prerequisites
    check_prerequisites

    # Check for uncommitted tracked changes (ignores untracked files)
    if [[ -n $(git status --porcelain | grep -E '^(M| M|A| D|D)') ]]; then
        log_error "Uncommitted tracked changes detected!"
        log_info "Please commit or stash them before running this script."
        git status --short
        exit 1
    fi

    # Switch to base branch and update
    log "🔄 Switching to $BASE_BRANCH branch and updating..."
    git checkout "$BASE_BRANCH"
    git pull origin "$BASE_BRANCH"

    # Check if the branch already exists and delete it if present
    if git show-ref --verify --quiet refs/heads/"$BRANCH_NAME"; then
        log_warning "Branch $BRANCH_NAME already exists. Deleting it..."
        git branch -D "$BRANCH_NAME"
    fi

    # Create a new branch
    log "🚀 Creating new branch: $BRANCH_NAME"
    git checkout -b "$BRANCH_NAME"

    # Fetch PRs from Dependabot (app/dependabot or dependabot[bot])
    log "🔍 Searching for Dependabot PRs..."
    PR_NUMBERS=$(gh pr list --json number,author --jq '.[] | select(.author.login | test("dependabot"; "i")) | .number')

    if [ -z "$PR_NUMBERS" ]; then
        log_warning "No Dependabot PRs found."
        log_info "Cleaning up and exiting..."
        git checkout "$BASE_BRANCH"
        git branch -D "$BRANCH_NAME" 2>/dev/null || true
        exit 0
    fi

    log_info "Found Dependabot PRs: $PR_NUMBERS"

    # Arrays to track PR processing
    declare -a MERGED_PRS
    declare -a SKIPPED_PRS
    declare -a FAILED_PRS

    # Loop through each PR and check if checks have passed
    for PR in $PR_NUMBERS; do
        log "🔍 Checking PR #$PR status..."

        # Get PR details
        PR_TITLE=$(gh pr view "$PR" --json title --jq '.title')
        log_info "PR #$PR: $PR_TITLE"

        # Get the PR's status check rollup (CI/CD results)
        CHECK_STATUS=$(gh pr view "$PR" --json statusCheckRollup --jq '.statusCheckRollup[]?.conclusion' 2>/dev/null || echo "")

        # Skip PRs with failed checks
        if echo "$CHECK_STATUS" | grep -q "FAILURE"; then
            log_warning "PR #$PR has failed checks. Skipping."
            SKIPPED_PRS+=("$PR (failed checks)")
            continue
        elif [ -z "$CHECK_STATUS" ]; then
            log_warning "PR #$PR has no completed checks. Skipping."
            SKIPPED_PRS+=("$PR (no checks)")
            continue
        fi

        log_success "PR #$PR passed checks. Proceeding to merge."

        # Fetch and merge the PR branch
        log "🔀 Fetching PR #$PR branch..."
        if git fetch origin pull/"$PR"/head:dependabot-pr-"$PR"; then
            log "🔀 Merging PR #$PR..."
            if git merge --no-edit dependabot-pr-"$PR"; then
                log_success "PR #$PR merged successfully"
                MERGED_PRS+=("$PR: $PR_TITLE")
            else
                log_error "Merge conflict in PR #$PR"
                log_info "Aborting merge and continuing with other PRs..."
                git merge --abort
                FAILED_PRS+=("$PR (merge conflict)")
            fi
        else
            log_error "Failed to fetch PR #$PR"
            FAILED_PRS+=("$PR (fetch failed)")
        fi
    done

    # Check if any PRs were merged
    if [ ${#MERGED_PRS[@]} -eq 0 ]; then
        log_warning "No PRs were successfully merged."
        log_info "Cleaning up and exiting..."
        git checkout "$BASE_BRANCH"
        git branch -D "$BRANCH_NAME"
        exit 0
    fi

    # Push the new merged branch
    log "🚀 Pushing branch $BRANCH_NAME to origin..."
    git push origin "$BRANCH_NAME"

    # Create PR body with details
    PR_BODY="# 🤖 Consolidated Dependabot Updates - $DATE

## 📊 Summary

This PR consolidates **${#MERGED_PRS[@]}** Dependabot updates into a single pull request.

## ✅ Merged PRs (${#MERGED_PRS[@]})

$(printf "- #%s\n" "${MERGED_PRS[@]}")

"

    if [ ${#SKIPPED_PRS[@]} -gt 0 ]; then
        PR_BODY+="## ⚠️ Skipped PRs (${#SKIPPED_PRS[@]})

$(printf "- #%s\n" "${SKIPPED_PRS[@]}")

"
    fi

    if [ ${#FAILED_PRS[@]} -gt 0 ]; then
        PR_BODY+="## ❌ Failed PRs (${#FAILED_PRS[@]})

$(printf "- #%s\n" "${FAILED_PRS[@]}")

"
    fi

    PR_BODY+="## 🔍 Review Notes

- All merged PRs had passing CI checks at the time of consolidation
- Please review the consolidated changes carefully
- Test the combined changes together to ensure no conflicts
- Refer to individual PR descriptions for detailed change information

## 📝 Log File

Log file for this consolidation: \`$LOG_FILE\`

---

*Generated by DependaBot Sheriff on $(date)*
*Based on: https://github.com/kiba-d/dependabot-sheriff*"

    # Create a new PR for all merged Dependabot updates
    log "📌 Creating consolidated PR..."
    PR_URL=$(gh pr create \
        --base "$BASE_BRANCH" \
        --head "$BRANCH_NAME" \
        --title "deps: Consolidated Dependabot updates ($DATE)" \
        --body "$PR_BODY" \
        --label "dependencies" \
        --label "dependabot" \
        2>&1 || echo "")

    if [ -z "$PR_URL" ]; then
        log_error "Failed to create PR"
        exit 1
    fi

    log_success "PR created: $PR_URL"

    # Assign the PR to the designated reviewer
    log "👤 Assigning PR to @$ASSIGNEE..."
    if gh pr edit "$PR_URL" --add-assignee "$ASSIGNEE"; then
        log_success "PR assigned to @$ASSIGNEE"
    else
        log_warning "Failed to assign PR to @$ASSIGNEE"
    fi

    # Print summary
    echo ""
    log "╔════════════════════════════════════════════════════════════════╗"
    log "║              🎉 Process Completed Successfully! 🎉              ║"
    log "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    log_info "📊 Summary:"
    log_info "  • Merged PRs: ${#MERGED_PRS[@]}"
    log_info "  • Skipped PRs: ${#SKIPPED_PRS[@]}"
    log_info "  • Failed PRs: ${#FAILED_PRS[@]}"
    log_info "  • Consolidated PR: $PR_URL"
    log_info "  • Log file: $LOG_FILE"
    echo ""

    # Create summary document
    SUMMARY_FILE="$LOG_DIR/dependabot_sheriff_summary_$DATE.md"
    cat > "$SUMMARY_FILE" << EOF
# DependaBot Sheriff Summary - $DATE

**Generated:** $(date)
**Consolidated PR:** $PR_URL
**Branch:** $BRANCH_NAME

## Statistics

- **Merged PRs:** ${#MERGED_PRS[@]}
- **Skipped PRs:** ${#SKIPPED_PRS[@]}
- **Failed PRs:** ${#FAILED_PRS[@]}

## Merged PRs

$(printf "- #%s\n" "${MERGED_PRS[@]}")

$(if [ ${#SKIPPED_PRS[@]} -gt 0 ]; then
    echo "## Skipped PRs"
    printf "- #%s\n" "${SKIPPED_PRS[@]}"
fi)

$(if [ ${#FAILED_PRS[@]} -gt 0 ]; then
    echo "## Failed PRs"
    printf "- #%s\n" "${FAILED_PRS[@]}"
fi)

## Log File

Full log: \`$LOG_FILE\`

---

*Generated by DependaBot Sheriff*
EOF

    log_success "Summary document created: $SUMMARY_FILE"
}

# ============================================================================
# Script Entry Point
# ============================================================================

# Run main function
main

exit 0
