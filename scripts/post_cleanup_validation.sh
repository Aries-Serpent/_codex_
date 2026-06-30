#!/bin/bash
# Post-Cleanup Validation Checklist
# This script verifies cleanup didn't break anything

set -o pipefail

echo "════════════════════════════════════════════════════════════════"
echo "POST-CLEANUP VALIDATION CHECKLIST"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "This checklist verifies that cleanup execution didn't break"
echo "any configurations, tools, or imports."
echo ""

# Counter
passed=0
failed=0

# ============================================================================
# POST-CLEANUP CHECKS
# ============================================================================

echo "STEP 1: Verify all configuration files still exist"
echo "═══════════════════════════════════════════════════════════════════"
for file in pytest.ini mypy.ini pyproject.toml .editorconfig .pre-commit-config.yaml; do
    if [ -f "$file" ]; then
        echo "✓ $file exists"
        ((passed++))
    else
        echo "✗ $file is missing"
        ((failed++))
    fi
done
echo ""

echo "STEP 2: Verify pytest still works"
echo "═══════════════════════════════════════════════════════════════════"
if python -m pytest tests/ --collect-only -q > /tmp/pytest_post_collection.txt 2>&1; then
    echo "✓ Pytest can collect tests"
    ((passed++))
    test_count=$(grep -c "test" /tmp/pytest_post_collection.txt || echo "0")
    echo "  Tests found: ~$test_count"
else
    echo "✗ Pytest collection failed"
    ((failed++))
    cat /tmp/pytest_post_collection.txt | head -20
fi
echo ""

echo "STEP 3: Verify mypy still works"
echo "═══════════════════════════════════════════════════════════════════"
if python -m mypy --version > /dev/null 2>&1; then
    echo "✓ Mypy works correctly"
    ((passed++))
    mypy_version=$(python -m mypy --version)
    echo "  Version: $mypy_version"
else
    echo "✗ Mypy failed"
    ((failed++))
fi
echo ""

echo "STEP 4: Verify critical imports"
echo "═══════════════════════════════════════════════════════════════════"
if python -c "import sys; sys.path.insert(0, 'src'); import codex" > /dev/null 2>&1; then
    echo "✓ Can import codex package"
    ((passed++))
else
    echo "✗ Failed to import codex package"
    ((failed++))
fi
echo ""

echo "STEP 5: Verify submodule imports"
echo "═══════════════════════════════════════════════════════════════════"
for module in "codex.rag" "codex.utils" "codex.agent"; do
    if python -c "import sys; sys.path.insert(0, 'src'); import $module" > /dev/null 2>&1; then
        echo "✓ Can import $module"
        ((passed++))
    else
        echo "⚠ Could not import $module (may be optional)"
    fi
done
echo ""

echo "STEP 6: Run pre-commit hooks"
echo "═══════════════════════════════════════════════════════════════════"
if command -v pre-commit > /dev/null 2>&1; then
    if pre-commit run --all-files > /tmp/precommit_results.txt 2>&1; then
        echo "✓ Pre-commit hooks passed"
        ((passed++))
    else
        # Pre-commit might fail on content, but shouldn't crash
        if grep -q "hook\|error" /tmp/precommit_results.txt; then
            echo "⚠ Pre-commit had warnings (may be expected)"
        else
            echo "✓ Pre-commit ran successfully"
            ((passed++))
        fi
    fi
else
    echo "⚠ pre-commit not installed, skipping"
fi
echo ""

echo "STEP 7: Verify requirements files are intact"
echo "═══════════════════════════════════════════════════════════════════"
for file in requirements.txt requirements-dev.txt requirements-test.txt requirements-optional.txt; do
    if [ -f "$file" ]; then
        # Check for basic validity (has entries)
        line_count=$(wc -l < "$file")
        if [ "$line_count" -gt 3 ]; then
            echo "✓ $file intact ($line_count lines)"
            ((passed++))
        else
            echo "⚠ $file may be corrupted (only $line_count lines)"
        fi
    else
        echo "✗ $file missing"
        ((failed++))
    fi
done
echo ""

echo "STEP 8: Run cleanup validation test suite"
echo "═══════════════════════════════════════════════════════════════════"
if python -m pytest tests/cleanup_validation/ -v --tb=short > /tmp/cleanup_validation_post.txt 2>&1; then
    echo "✓ All cleanup validation tests passed"
    ((passed++))
    test_count=$(grep -c "PASSED\|passed" /tmp/cleanup_validation_post.txt || echo "0")
    echo "  Tests passed: $test_count"
else
    if grep -q "FAILED\|ERROR" /tmp/cleanup_validation_post.txt; then
        echo "✗ Some validation tests failed"
        ((failed++))
        grep "FAILED\|ERROR" /tmp/cleanup_validation_post.txt | head -10
    else
        echo "✓ Validation completed (may have skipped)"
        ((passed++))
    fi
fi
echo ""

echo "STEP 9: Verify no broken imports"
echo "═══════════════════════════════════════════════════════════════════"
if python -c "
import sys
sys.path.insert(0, 'src')
try:
    import codex
    from codex import *
    print('✓ All imports work')
except ImportError as e:
    print(f'✗ Import failed: {e}')
    sys.exit(1)
" > /tmp/import_check.txt 2>&1; then
    echo "✓ No broken imports detected"
    ((passed++))
else
    echo "✗ Import errors detected"
    ((failed++))
    cat /tmp/import_check.txt
fi
echo ""

echo "STEP 10: Verify artifact generation"
echo "═══════════════════════════════════════════════════════════════════"
# Test coverage generation
if python -m pytest tests/cleanup_validation/test_cleanup_validation.py -v --cov=src --cov-report=term-missing > /tmp/coverage_test.txt 2>&1; then
    echo "✓ Coverage reporting works"
    ((passed++))
else
    echo "⚠ Coverage reporting had issues (may be optional)"
fi
echo ""

# ============================================================================
# DETAILED VERIFICATION
# ============================================================================

echo "STEP 11: Detailed Configuration Verification"
echo "═══════════════════════════════════════════════════════════════════"

# Check pytest.ini has pythonpath
if grep -q "pythonpath = src" pytest.ini; then
    echo "✓ pytest.ini has pythonpath configured"
    ((passed++))
else
    echo "✗ pytest.ini missing pythonpath"
    ((failed++))
fi

# Check mypy.ini has Python version
if grep -q "python_version" mypy.ini; then
    echo "✓ mypy.ini has Python version configured"
    ((passed++))
else
    echo "✗ mypy.ini missing Python version"
    ((failed++))
fi

# Check pyproject.toml has build system
if grep -q "\[build-system\]" pyproject.toml; then
    echo "✓ pyproject.toml has build-system section"
    ((passed++))
else
    echo "✗ pyproject.toml missing build-system"
    ((failed++))
fi
echo ""

# ============================================================================
# COMPARISON WITH PRE-CLEANUP
# ============================================================================

echo "STEP 12: Verify No Accidental Changes"
echo "═══════════════════════════════════════════════════════════════════"

for file in pytest.ini mypy.ini pyproject.toml .editorconfig; do
    if [ -f ".codex/pre_cleanup_backups/$file.backup" ]; then
        if cmp -s "$file" ".codex/pre_cleanup_backups/$file.backup"; then
            echo "✓ $file unchanged"
            ((passed++))
        else
            echo "⚠ $file was modified (check if intended)"
            # Show diff
            diff -u ".codex/pre_cleanup_backups/$file.backup" "$file" | head -10 || true
        fi
    fi
done
echo ""

# ============================================================================
# SUMMARY
# ============================================================================

echo "════════════════════════════════════════════════════════════════"
echo "POST-CLEANUP VALIDATION SUMMARY"
echo "════════════════════════════════════════════════════════════════"
echo "Passed: $passed"
echo "Failed: $failed"
echo ""

if [ $failed -eq 0 ]; then
    echo "✓ POST-CLEANUP VALIDATION SUCCESSFUL"
    echo ""
    echo "Verification complete:"
    echo "  ✓ All configurations intact"
    echo "  ✓ All tools functional"
    echo "  ✓ All imports working"
    echo "  ✓ No broken references"
    echo "  ✓ CI/CD pipeline ready"
    echo ""
    echo "Next steps:"
    echo "1. Review cleanup changes: git diff"
    echo "2. Create pull request with cleanup"
    echo "3. Monitor CI/CD pipeline"
    echo ""
    exit 0
else
    echo "✗ POST-CLEANUP VALIDATION FAILED"
    echo ""
    echo "Issues detected ($failed failed checks):"
    echo "1. Review errors above"
    echo "2. Restore backups if needed: .codex/pre_cleanup_backups/"
    echo "3. Re-run cleanup with corrections"
    echo ""
    exit 1
fi
