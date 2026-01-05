#!/usr/bin/env bash
#
# fix_broken_documentation_links.sh
# Comprehensive script to fix all broken documentation links
#
# Usage: ./fix_broken_documentation_links.sh

set -euo pipefail

REPO_ROOT="/home/runner/work/_codex_/_codex_"
LOG_FILE="${REPO_ROOT}/.codex/broken_links_fixed.log"

echo "=== Documentation Link Fixer ===" | tee "$LOG_FILE"
echo "Started: $(date)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Counter for fixes
FIXES=0

#############################################################################
# 1. Fix placeholder PR #9999 links
#############################################################################
echo "[1/8] Fixing placeholder PR #9999 links..." | tee -a "$LOG_FILE"

if grep -r "/pull/9999" "$REPO_ROOT" --include="*.md" -l 2>/dev/null; then
  grep -r "/pull/9999" "$REPO_ROOT" --include="*.md" -l | while read -r file; do
    echo "  - Updating: $file" | tee -a "$LOG_FILE"
    sed -i 's|https://github.com/Aries-Serpent/_codex_/pull/9999|<!-- Placeholder PR link removed -->|g' "$file"
    FIXES=$((FIXES + 1))
  done
fi

#############################################################################
# 2. Fix broken branch links (0A_base, 0B_base, */*)
#############################################################################
echo "[2/8] Fixing broken branch links..." | tee -a "$LOG_FILE"

grep -r "/tree/0A_base\|/tree/0B_base\|/tree/\\*/" "$REPO_ROOT" --include="*.md" -l 2>/dev/null | while read -r file; do
  echo "  - Updating: $file" | tee -a "$LOG_FILE"
  sed -i 's|https://github.com/Aries-Serpent/_codex_/tree/0A_base|<!-- Branch no longer exists -->|g' "$file"
  sed -i 's|https://github.com/Aries-Serpent/_codex_/tree/0B_base|<!-- Branch no longer exists -->|g' "$file"
  sed -i 's|https://github.com/Aries-Serpent/_codex_/tree/\\*/|<!-- Invalid branch reference -->|g' "$file"
  FIXES=$((FIXES + 1))
done

#############################################################################
# 3. Fix example.com placeholder links
#############################################################################
echo "[3/8] Fixing example.com placeholder links..." | tee -a "$LOG_FILE"

grep -r "example\.com" "$REPO_ROOT/docs" --include="*.md" -l 2>/dev/null | while read -r file; do
  echo "  - Updating: $file" | tee -a "$LOG_FILE"
  # Replace wiki.example.com with comment
  sed -i 's|https://wiki\.example\.com/security|<!-- Security documentation placeholder -->|g' "$file"
  # Replace security@example.com with generic
  sed -i 's|security@example\.com|security@localhost|g' "$file"
  # Replace other example.com URLs with localhost (more specific subdomain pattern)
  sed -i 's|https://\([a-zA-Z0-9.-]*\)\.example\.com|http://localhost:8080|g' "$file"
  sed -i 's|http://\([a-zA-Z0-9.-]*\)\.example\.com|http://localhost:8080|g' "$file"
  # Replace example.com emails
  sed -i 's|support@codex-ml\.example\.com|support@localhost|g' "$file"
  FIXES=$((FIXES + 1))
done

#############################################################################
# 4. Fix broken GitHub repo URL (missing underscore)
#############################################################################
echo "[4/8] Fixing broken GitHub repo URLs..." | tee -a "$LOG_FILE"

grep -r "https://github.com/Aries-Serpent/_codex\>" "$REPO_ROOT/docs" --include="*.md" -l 2>/dev/null | while read -r file; do
  echo "  - Updating: $file" | tee -a "$LOG_FILE"
  # Fix repo URL - should be _codex_ not _codex
  sed -i 's|https://github\.com/Aries-Serpent/_codex\>|https://github.com/Aries-Serpent/_codex_|g' "$file"
  FIXES=$((FIXES + 1))
done

#############################################################################
# 5. Fix broken security/dependabot links
#############################################################################
echo "[5/8] Fixing security/dependabot links..." | tee -a "$LOG_FILE"

grep -r "/security/dependabot" "$REPO_ROOT/docs" --include="*.md" -l 2>/dev/null | while read -r file; do
  echo "  - Updating: $file" | tee -a "$LOG_FILE"
  # Fix path - should be /security not /security/dependabot
  sed -i 's|https://github\.com/Aries-Serpent/_codex_/security/dependabot|https://github.com/Aries-Serpent/_codex_/security|g' "$file"
  FIXES=$((FIXES + 1))
done

#############################################################################
# 6. Fix broken MCP servers GitHub links
#############################################################################
echo "[6/8] Fixing MCP servers GitHub links..." | tee -a "$LOG_FILE"

grep -r "github.com/modelcontextprotocol/servers/tree/main/src/github" "$REPO_ROOT/docs" --include="*.md" -l 2>/dev/null | while read -r file; do
  echo "  - Updating: $file" | tee -a "$LOG_FILE"
  # Remove /tree/main/src/github - path doesn't exist
  sed -i 's|https://github\.com/modelcontextprotocol/servers/tree/main/src/github|https://github.com/modelcontextprotocol/servers|g' "$file"
  FIXES=$((FIXES + 1))
done

#############################################################################
# 7. Fix broken Copilot extensions documentation
#############################################################################
echo "[7/8] Fixing Copilot extensions documentation links..." | tee -a "$LOG_FILE"

grep -r "docs.github.com/en/copilot/building-copilot-extensions" "$REPO_ROOT/docs" --include="*.md" -l 2>/dev/null | while read -r file; do
  echo "  - Updating: $file" | tee -a "$LOG_FILE"
  # Update to correct documentation path
  sed -i 's|https://docs\.github\.com/en/copilot/building-copilot-extensions|https://docs.github.com/en/copilot/using-github-copilot|g' "$file"
  FIXES=$((FIXES + 1))
done

#############################################################################
# 8. Document interactive-codebase-navigator.html status
#############################################################################
echo "[8/8] Documenting GitHub Pages references..." | tee -a "$LOG_FILE"

if grep -r "interactive-codebase-navigator.html" "$REPO_ROOT/docs" --include="*.md" -l 2>/dev/null; then
  echo "  Note: interactive-codebase-navigator.html references found" | tee -a "$LOG_FILE"
  echo "  These will become valid after GitHub Pages deployment" | tee -a "$LOG_FILE"
fi

#############################################################################
# Summary
#############################################################################
echo "" | tee -a "$LOG_FILE"
echo "=== Summary ===" | tee -a "$LOG_FILE"
echo "Total files fixed: $FIXES" | tee -a "$LOG_FILE"
echo "Completed: $(date)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "Review log: $LOG_FILE"

exit 0
