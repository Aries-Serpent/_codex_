#!/bin/bash
# Emergency Fix: Remove Windows-Illegal Characters from Filenames
# Phase 1 Critical Fixes
# Created: 2026-01-23

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

echo "🔧 Phase 1: Emergency Filename Fixes"
echo "=================================="

# Fix 1: Rename files with parentheses (CRITICAL)
if [[ -f ".codex/reports/_codex_status_update-(2025-12-06).md" ]]; then
    echo "✏️  Renaming: .codex/reports/_codex_status_update-(2025-12-06).md"
    git mv ".codex/reports/_codex_status_update-(2025-12-06).md" ".codex/reports/_codex_status_update_2025-12-06.md" || true
fi

# Verification
echo ""
echo "✅ Verification:"
VIOLATIONS=$(git ls-tree -r HEAD --name-only | grep -E '[\[\]()\"<>:|?*]' || true)
if [[ -z "$VIOLATIONS" ]]; then
    echo "   No Windows-illegal characters found in tracked files"
else
    echo "   ⚠️  Remaining violations:"
    echo "$VIOLATIONS"
fi

echo ""
echo "✨ Phase 1 Complete"
echo "Next: Run Phase 2 code remediation"
