#!/usr/bin/env bash
# CI Test Fix Validation Script
# Validates that pytest configuration and workflow changes are correct

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "======================================"
echo "CI Test Fix Validation"
echo "======================================"
echo ""

# Check 1: Verify pytest.ini doesn't have timeout in addopts
echo "Check 1: pytest.ini configuration..."
if grep -A 5 "^\[pytest\]" pytest.ini | grep "addopts" -A 5 | grep -q "timeout"; then
    echo -e "${RED}❌ FAIL: pytest.ini still contains 'timeout' in addopts${NC}"
    echo "   This will cause xdist worker crashes"
    exit 1
else
    echo -e "${GREEN}✅ PASS: pytest.ini does not have timeout in addopts${NC}"
fi

# Check 2: Verify workflows use python -m pytest
echo ""
echo "Check 2: Workflow pytest invocations..."
FAILED=0

for workflow in \
    .github/workflows/test-comprehensive.yml \
    .github/workflows/test-rag.yml \
    .github/workflows/pr-checks.yml \
    .github/workflows/auth-tests.yml \
    .github/workflows/determinism.yml \
    .github/workflows/rust_swarm_ci.yml; do
    
    if [ -f "$workflow" ]; then
        # Check if file uses pytest without python -m
        if grep -E "^\s+pytest\s+tests" "$workflow" > /dev/null 2>&1; then
            echo -e "${RED}❌ FAIL: $workflow uses bare 'pytest' command${NC}"
            echo "   Should use 'python -m pytest' instead"
            FAILED=1
        else
            echo -e "${GREEN}✅ PASS: $workflow uses proper pytest invocation${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  SKIP: $workflow not found${NC}"
    fi
done

if [ $FAILED -eq 1 ]; then
    exit 1
fi

# Check 3: Verify timeout args in critical workflows
echo ""
echo "Check 3: Timeout configuration in workflows..."
for workflow in \
    .github/workflows/test-comprehensive.yml \
    .github/workflows/test-rag.yml; do
    
    if [ -f "$workflow" ]; then
        if grep -q "\-\-timeout=300" "$workflow"; then
            echo -e "${GREEN}✅ PASS: $workflow has explicit timeout args${NC}"
        else
            echo -e "${YELLOW}⚠️  WARN: $workflow missing explicit timeout args${NC}"
            echo "   Tests may run without timeout protection"
        fi
    fi
done

# Check 4: Verify xdist configuration
echo ""
echo "Check 4: xdist configuration..."
for workflow in \
    .github/workflows/test-comprehensive.yml \
    .github/workflows/test-rag.yml; do
    
    if [ -f "$workflow" ]; then
        if grep -q "\-n auto" "$workflow" && grep -q "\-\-dist=loadfile" "$workflow"; then
            echo -e "${GREEN}✅ PASS: $workflow has xdist configuration${NC}"
        else
            echo -e "${YELLOW}⚠️  WARN: $workflow may not use xdist${NC}"
        fi
    fi
done

# Check 5: Verify documentation exists
echo ""
echo "Check 5: Documentation..."
if [ -f "CI_TEST_FIXES_PR2883.md" ]; then
    echo -e "${GREEN}✅ PASS: CI_TEST_FIXES_PR2883.md exists${NC}"
    
    # Check documentation completeness
    if grep -q "Issue 1" CI_TEST_FIXES_PR2883.md && \
       grep -q "Issue 2" CI_TEST_FIXES_PR2883.md && \
       grep -q "Root Cause" CI_TEST_FIXES_PR2883.md; then
        echo -e "${GREEN}✅ PASS: Documentation is comprehensive${NC}"
    else
        echo -e "${YELLOW}⚠️  WARN: Documentation may be incomplete${NC}"
    fi
else
    echo -e "${RED}❌ FAIL: CI_TEST_FIXES_PR2883.md not found${NC}"
    exit 1
fi

# Summary
echo ""
echo "======================================"
echo -e "${GREEN}All validation checks passed!${NC}"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Commit changes if not already done"
echo "2. Push to remote branch"
echo "3. Monitor CI workflows in PR"
echo "4. Verify tests run successfully"
echo ""
echo "Expected CI results:"
echo "  ✅ test-comprehensive.yml: Tests discovered and run"
echo "  ✅ test-rag.yml: xdist workers spawn without crashes"
echo "  ✅ All Python versions (3.11, 3.12) pass"
echo ""
