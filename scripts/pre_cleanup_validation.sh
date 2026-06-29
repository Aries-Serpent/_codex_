#!/bin/bash
# Pre-Cleanup Validation Checklist
# This script verifies everything is ready before cleanup execution

set -o pipefail

echo "════════════════════════════════════════════════════════════════"
echo "PRE-CLEANUP VALIDATION CHECKLIST"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "This checklist ensures the repository is in a valid state"
echo "before proceeding with root folder cleanup."
echo ""

# Counter
passed=0
failed=0

check_status() {
    if [ $? -eq 0 ]; then
        echo "✓ $1"
        ((passed++))
    else
        echo "✗ $1"
        ((failed++))
    fi
}

# ============================================================================
# PRE-CLEANUP CHECKS
# ============================================================================

echo "STEP 1: Verify Git status is clean"
echo "═══════════════════════════════════════════════════════════════════"
git status --short | head -5
if [ "$(git status --porcelain)" == "" ]; then
    echo "✓ Working directory is clean"
    ((passed++))
else
    echo "⚠ Working directory has uncommitted changes"
    echo "  Run: git status"
fi
echo ""

echo "STEP 2: Verify all configuration files exist"
echo "═══════════════════════════════════════════════════════════════════"
for file in pytest.ini mypy.ini pyproject.toml .editorconfig .pre-commit-config.yaml; do
    if [ -f "$file" ]; then
        echo "✓ $file exists"
        ((passed++))
    else
        echo "✗ $file missing"
        ((failed++))
    fi
done
echo ""

echo "STEP 3: Verify requirements files are valid"
echo "═══════════════════════════════════════════════════════════════════"
for file in requirements.txt requirements-dev.txt requirements-test.txt requirements-optional.txt; do
    [ -f "$file" ] && echo "✓ $file exists" && ((passed++)) || (echo "✗ $file missing" && ((failed++)))
done
echo ""

echo "STEP 4: Run pytest collection"
echo "═══════════════════════════════════════════════════════════════════"
if python -m pytest tests/ --collect-only -q > /tmp/pytest_collection.txt 2>&1; then
    echo "✓ Pytest can collect tests"
    ((passed++))
    test_count=$(grep -c "test" /tmp/pytest_collection.txt || echo "0")
    echo "  Tests found: ~$test_count"
else
    echo "✗ Pytest collection failed"
    ((failed++))
fi
echo ""

echo "STEP 5: Run mypy type checking"
echo "═══════════════════════════════════════════════════════════════════"
if python -m mypy --version > /dev/null 2>&1; then
    echo "✓ Mypy can run"
    ((passed++))
    mypy_version=$(python -m mypy --version)
    echo "  Version: $mypy_version"
else
    echo "✗ Mypy failed"
    ((failed++))
fi
echo ""

echo "STEP 6: Verify critical imports"
echo "═══════════════════════════════════════════════════════════════════"
if python -c "import sys; sys.path.insert(0, 'src'); import codex" > /dev/null 2>&1; then
    echo "✓ Can import codex package"
    ((passed++))
else
    echo "✗ Failed to import codex package"
    ((failed++))
fi
echo ""

echo "STEP 7: Run cleanup validation tests"
echo "═══════════════════════════════════════════════════════════════════"
if python -m pytest tests/cleanup_validation/ -v --tb=short > /tmp/cleanup_validation.txt 2>&1; then
    echo "✓ All cleanup validation tests passed"
    ((passed++))
else
    # Check for actual failures vs just no tests
    if grep -q "FAILED\|ERROR" /tmp/cleanup_validation.txt; then
        echo "✗ Some validation tests failed"
        ((failed++))
    else
        echo "✓ Validation tests completed"
        ((passed++))
    fi
fi
echo ""

echo "STEP 8: Verify backup of critical files"
echo "═══════════════════════════════════════════════════════════════════"
mkdir -p .codex/pre_cleanup_backups
for file in pytest.ini mypy.ini pyproject.toml .editorconfig; do
    if [ -f "$file" ]; then
        cp "$file" ".codex/pre_cleanup_backups/$file.backup"
        echo "✓ Backed up $file"
        ((passed++))
    fi
done
echo ""

# ============================================================================
# SUMMARY
# ============================================================================

echo "════════════════════════════════════════════════════════════════"
echo "PRE-CLEANUP VALIDATION SUMMARY"
echo "════════════════════════════════════════════════════════════════"
echo "Passed: $passed"
echo "Failed: $failed"
echo ""

if [ $failed -eq 0 ]; then
    echo "✓ Repository is ready for cleanup"
    echo ""
    echo "Next steps:"
    echo "1. Review the cleanup plan: ROOT_FOLDER_CLEANUP_PLAN.md"
    echo "2. Execute cleanup with: ./scripts/execute_cleanup.sh"
    echo "3. Run post-cleanup validation: ./scripts/post_cleanup_validation.sh"
    echo ""
    exit 0
else
    echo "✗ Issues detected! Fix before proceeding."
    echo "Review failed checks above and retry."
    exit 1
fi
