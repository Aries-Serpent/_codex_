#!/usr/bin/env bash
# emit_precommit_summary.sh — Surface failing pre-commit hook details to $GITHUB_STEP_SUMMARY
#
# Usage: emit_precommit_summary.sh <validation.log> <artifact-name>
#
# S236/OBJ-001: Makes the failing hook name visible directly in the CI job log
# so agents never need to download the validation artifact to identify the hook.
#
# Output goes to $GITHUB_STEP_SUMMARY (set by GitHub Actions runner).
# When run locally, outputs to stdout.

set -euo pipefail

LOG_FILE="${1:-validation.log}"
ARTIFACT_NAME="${2:-validation-log}"
SUMMARY_TARGET="${GITHUB_STEP_SUMMARY:-/dev/stdout}"

if [ ! -f "$LOG_FILE" ]; then
  # The validation step may not have run (e.g., early-exit before pre-commit stage).
  # This is non-fatal for the summary step itself; the real failure is captured by
  # the validation job exit code, not this diagnostic step.
  echo "⚠️ $LOG_FILE not found — validation step may have failed before pre-commit ran" >> "$SUMMARY_TARGET"
  exit 0
fi

# Extract the block between "Running pre-commit hooks" and "pre-commit checks failed"
HOOK_BLOCK=$(awk '/Running pre-commit hooks/{found=1} found{print} /pre-commit checks failed/{exit}' "$LOG_FILE")

# Find failure-signal lines:
#   - hook result lines ending in "Failed" (e.g., "fix end of files.......Failed")
#   - hook id annotation lines (e.g., "- hook id: end-of-file-fixer")
#   - exit code lines  (e.g., "- exit code: 1")
#   - files modified   (e.g., "- files were modified by this hook")
#   - file fix lines   (e.g., "Fixing .github/workflows/resilient_validation.yml")
# `|| true` suppresses grep exit-1 when no lines match (expected when pre-commit
# passed all hooks); FAILED will be empty and the summary will say so below.
FAILED=$(echo "$HOOK_BLOCK" | \
  grep -E "\.{3,}\s*Failed$|^- hook id:|^- exit code:|^- files were modified|^Fixing " \
  || true)

{
  echo "## ❌ Pre-commit Failure Summary"
  echo ""
  if [ -n "$FAILED" ]; then
    echo "\`\`\`"
    echo "$FAILED"
    echo "\`\`\`"
  else
    echo "_No hook-level failure lines extracted — download the full log artifact for details._"
  fi
  echo ""
  echo "**Full log:** download artifact \`${ARTIFACT_NAME}\` for complete output including diffs."
  echo ""
  echo "> **Local reproduction:** \`pre-commit run --show-diff-on-failure --files <changed-files>\`"
  echo ""
  echo "> **Hook catalog:** \`.codex/cognitive_brain/objectives_tracker.md\` — OBJ-001 (28 hooks documented)"
} >> "$SUMMARY_TARGET"
