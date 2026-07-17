#!/bin/bash

# Continuous workflow monitoring for PR #5328
# Alerts when workflows need approval

REPO="Aries-Serpent/_codex_"
BRANCH="0D_base_"
CHECK_INTERVAL=30  # seconds
MAX_CHECKS=720  # 6 hours

check_count=0

echo "🔍 Starting workflow monitoring for PR #5328 (branch: $BRANCH)"
echo "📊 Monitoring interval: ${CHECK_INTERVAL}s | Max duration: $((MAX_CHECKS * CHECK_INTERVAL))s"
echo "---"

while [ $check_count -lt $MAX_CHECKS ]; do
    check_count=$((check_count + 1))
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Check for action_required workflows
    action_required=$(curl -s -H "Accept: application/vnd.github+json" \
        "https://api.github.com/repos/$REPO/actions/runs?status=action_required" \
        | jq '.workflow_runs[] | select(.head_branch == "'$BRANCH'") | {id: .id, name: .name}')
    
    if [ ! -z "$action_required" ]; then
        echo "🚨 [$timestamp] APPROVAL REQUIRED!"
        echo "$action_required" | jq '.'
        echo ""
        echo "⚠️  ALERT: Workflows are waiting for approval!"
        echo "📋 Next step: Click 'Approve and run' in the GitHub Actions tab or use:"
        echo "   gh run approve <run_id> --repo $REPO"
        echo ""
        exit 0
    fi
    
    # Check for in_progress workflows
    in_progress=$(curl -s -H "Accept: application/vnd.github+json" \
        "https://api.github.com/repos/$REPO/actions/runs?status=in_progress&per_page=50" \
        | jq '.workflow_runs[] | select(.head_branch == "'$BRANCH'") | {id: .id, name: .name, created_at: .created_at}' | wc -l)
    
    # Count queued
    queued=$(curl -s -H "Accept: application/vnd.github+json" \
        "https://api.github.com/repos/$REPO/actions/runs?status=queued&per_page=50" \
        | jq '.workflow_runs[] | select(.head_branch == "'$BRANCH'") | {id: .id, name: .name}' | wc -l)
    
    printf "\r📍 Check #%d: %s | In-Progress: ~%d | Queued: ~%d" $check_count "$timestamp" $((in_progress / 15)) $((queued / 15))
    
    sleep $CHECK_INTERVAL
done

echo ""
echo "⏰ Monitoring timeout - no approval required during this period"
