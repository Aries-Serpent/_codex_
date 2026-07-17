#!/bin/bash
# Continuous workflow monitor for PR #5328
set -e

PR=5328
OWNER="Aries-Serpent"
REPO="_codex_"
OUTPUT_FILE=".codex/workflow_monitoring_log_2026_07_17.txt"

echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] Workflow Monitor Started" > "$OUTPUT_FILE"

poll=0
max_polls=180  # 90 minutes

while [ $poll -lt $max_polls ]; do
  poll=$((poll + 1))
  ts=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
  
  # Get all check runs
  in_progress=$(gh api repos/$OWNER/$REPO/commits/HEAD/check-runs --jq '[.check_runs[] | select(.status=="in_progress")] | length' 2>/dev/null || echo "ERROR")
  queued=$(gh api repos/$OWNER/$REPO/commits/HEAD/check-runs --jq '[.check_runs[] | select(.status=="queued")] | length' 2>/dev/null || echo "ERROR")
  completed=$(gh api repos/$OWNER/$REPO/commits/HEAD/check-runs --jq '[.check_runs[] | select(.status=="completed")] | length' 2>/dev/null || echo "ERROR")
  
  if [ "$in_progress" != "ERROR" ]; then
    echo "[$ts] Poll #$poll | IN_PROGRESS: $in_progress | QUEUED: $queued | COMPLETED: $completed" | tee -a "$OUTPUT_FILE"
    
    if [ "$in_progress" == "0" ] && [ "$queued" == "0" ]; then
      echo "[$ts] ✅ ALL WORKFLOWS COMPLETE (poll #$poll after $((poll * 30))s)" | tee -a "$OUTPUT_FILE"
      exit 0
    fi
  else
    echo "[$ts] Poll #$poll | API Error - retrying..." | tee -a "$OUTPUT_FILE"
  fi
  
  sleep 30
done

echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] ⚠️  TIMEOUT after $((poll * 30))s" | tee -a "$OUTPUT_FILE"
