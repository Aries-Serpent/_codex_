#!/bin/bash
# Analyze CI Failure Script
# Downloads and analyzes logs for a failed workflow run
#
# Usage:
#   ./analyze_failure.sh <run_id>

set -euo pipefail

RUN_ID="${1:-}"
REPO="${GITHUB_REPOSITORY:-Aries-Serpent/_codex_}"

if [ -z "$RUN_ID" ]; then
    echo "Usage: $0 <run_id>"
    exit 1
fi

echo "🔍 Analyzing failure for run ID: $RUN_ID"

# Create logs directory
mkdir -p .codex/logs

# Get workflow details
echo "📥 Downloading workflow logs..."
if gh run view "$RUN_ID" --repo "$REPO" --log > ".codex/logs/run_${RUN_ID}.log" 2>/dev/null; then
    echo "✅ Logs downloaded to .codex/logs/run_${RUN_ID}.log"
else
    echo "❌ Failed to download logs for run $RUN_ID"
    exit 1
fi

LOG_FILE=".codex/logs/run_${RUN_ID}.log"

# Pattern matching for common failures
echo ""
echo "🔍 Analyzing failure patterns..."

if grep -q "ModuleNotFoundError" "$LOG_FILE"; then
    echo "🐍 Detected: Missing Python dependency"
    grep "ModuleNotFoundError" "$LOG_FILE" | head -5
elif grep -q "syntax error" "$LOG_FILE"; then
    echo "⚠️  Detected: Syntax error"
    grep -i "syntax error" "$LOG_FILE" | head -5
elif grep -q "SARIF upload" "$LOG_FILE"; then
    echo "🔒 Detected: SARIF upload issue"
    grep -i "SARIF" "$LOG_FILE" | head -5
elif grep -q "coverage.*below\|fail-under" "$LOG_FILE"; then
    echo "📊 Detected: Coverage threshold not met"
    grep -i "coverage\|fail-under" "$LOG_FILE" | head -5
elif grep -q "SyntaxError\|linting" "$LOG_FILE"; then
    echo "✨ Detected: Code quality issue"
    grep -i "SyntaxError\|linting\|ruff\|black" "$LOG_FILE" | head -5
elif grep -q "FAILED.*test_\|AssertionError" "$LOG_FILE"; then
    echo "🧪 Detected: Test failure"
    grep -i "FAILED\|AssertionError" "$LOG_FILE" | head -10
else
    echo "❓ Unknown failure pattern - manual review required"
    echo "$RUN_ID" >> .codex/logs/manual_review_needed.txt
fi

# Run Python diagnosis if available
if [ -f ".codex/scripts/diagnose_ci_failure.py" ]; then
    echo ""
    echo "🔬 Running detailed diagnosis..."
    python .codex/scripts/diagnose_ci_failure.py "$RUN_ID" 2>/dev/null || true
fi

echo ""
echo "📋 Log file: $LOG_FILE"
