#!/usr/bin/env bash
# Pre-commit hook to prevent test_*.py naming in utility modules
#
# Purpose: pytest collects ANY file matching test_*.py pattern, even if it's
# a utility module. This hook prevents that naming pattern outside actual test files.
#
# Usage: Called automatically by pre-commit framework

set -e

echo "🔍 Checking for test_*.py utility files that should not be collected by pytest..."

# Find test_*.py files in specific utility directories (more portable approach)
EXIT_CODE=0

# Check for test_*.py files in framework, utils, helpers directories
# Only flag files that do NOT contain actual test functions/classes (i.e., real utilities)
ALL_CANDIDATE_FILES=$(find tests/framework tests/utils tests/helpers -name "test_*.py" -type f 2>/dev/null || true)
UTILITY_FILES=""
while IFS= read -r f; do
  [[ -z "$f" ]] && continue
  # Skip if file contains actual test functions or test classes — it's a real test
  if grep -qE "^(def test_|class Test)" "$f" 2>/dev/null; then
    continue
  fi
  UTILITY_FILES="${UTILITY_FILES}${f}"$'\n'
done <<< "$ALL_CANDIDATE_FILES"
UTILITY_FILES="${UTILITY_FILES%$'\n'}"

if [ -n "$UTILITY_FILES" ]; then
    echo "❌ Found utility files matching test_*.py pattern:"
    echo "$UTILITY_FILES"
    echo ""
    echo "💡 Recommendation: Rename utility modules to avoid 'test_' prefix"
    echo "   Example: test_generator.py → generator.py"
    echo "   Example: test_helpers.py → helpers.py"
    echo ""
    EXIT_CODE=1
fi

# Check for common utility module patterns that might be misnamed
# Use find with -exec and + for better performance (batch processing)
SUSPICIOUS_FILES=$(find tests/ -type f -name "test_*.py" -exec grep -l "def.*generator\|class.*Helper\|class.*Util\|class.*Factory" {} + 2>/dev/null | head -5 || true)

if [ -n "$SUSPICIOUS_FILES" ]; then
    echo "⚠️  Warning: Found test_*.py files that may be utility modules:"
    echo "$SUSPICIOUS_FILES"
    echo ""
    echo "💡 If these are utility modules (not actual tests), rename them without 'test_' prefix"
    echo ""
fi

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ No problematic test_*.py utility files found"
fi

exit $EXIT_CODE
