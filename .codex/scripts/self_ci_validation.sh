#!/bin/bash
# Self-CI Validation Script for PR #3248
# Simulates the resilient_validation.yml workflow locally
# Usage: bash .codex/scripts/self_ci_validation.sh [quick|slow|integration|documentation|all]

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
TEST_GROUP="${1:-quick}"
REPORT_DIR=".codex/self_ci_reports"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_FILE="$REPORT_DIR/self_ci_${TEST_GROUP}_${TIMESTAMP}.md"

mkdir -p "$REPORT_DIR"

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Self-CI Validation - PR #3248${NC}"
echo -e "${BLUE}================================${NC}"
echo ""
echo "Test Group: $TEST_GROUP"
echo "Report: $REPORT_FILE"
echo ""

# Initialize report
cat > "$REPORT_FILE" <<EOF
# Self-CI Validation Report - PR #3248

**Date:** $(date -u +%Y-%m-%dT%H:%M:%SZ)  
**Test Group:** $TEST_GROUP  
**Baseline:** 77.9% (53/68 tests passing)  
**Target Phase 1:** 80.9% (55/68 tests)  
**Target Phase 2:** 85.3% (58/68 tests)

---

## Environment Check

EOF

# Function to log and display
log_step() {
    local step="$1"
    local status="$2"
    echo -e "${BLUE}[STEP]${NC} $step: $status"
    echo "- **$step:** $status" >> "$REPORT_FILE"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
    echo "  - ✅ $1" >> "$REPORT_FILE"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    echo "  - ⚠️ $1" >> "$REPORT_FILE"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
    echo "  - ❌ $1" >> "$REPORT_FILE"
}

# Step 1: Environment validation
echo -e "\n${BLUE}Step 1: Environment Validation${NC}"
echo -e "\n## Step 1: Environment Validation\n" >> "$REPORT_FILE"

# Python version
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
log_step "Python Version" "$PYTHON_VERSION"
if [[ "$PYTHON_VERSION" == 3.12* ]]; then
    log_success "Python 3.12 detected (matches CI)"
else
    log_warning "Python version differs from CI (expected 3.12.x)"
fi

# Check pytest installation
if python -c "import pytest" 2>/dev/null; then
    PYTEST_VERSION=$(python -c "import pytest; print(pytest.__version__)")
    log_step "pytest" "v$PYTEST_VERSION installed"
    log_success "pytest available"
else
    log_error "pytest not installed - installing now..."
    pip install -q pytest pytest-timeout pytest-xdist pytest-cov pytest-asyncio pytest-mock
    log_success "pytest installed"
fi

# Check for required plugins
echo -e "\n### Plugin Verification\n" >> "$REPORT_FILE"
for plugin in pytest-timeout pytest-xdist pytest-cov pytest-asyncio pytest-mock; do
    if python -c "import ${plugin//-/_}" 2>/dev/null || pip show "$plugin" >/dev/null 2>&1; then
        PLUGIN_VERSION=$(pip show "$plugin" 2>/dev/null | grep Version | awk '{print $2}')
        log_success "$plugin v$PLUGIN_VERSION"
    else
        log_warning "$plugin not installed"
    fi
done

# Step 2: Test collection analysis
echo -e "\n${BLUE}Step 2: Test Collection Analysis${NC}"
echo -e "\n## Step 2: Test Collection Analysis\n" >> "$REPORT_FILE"

log_step "Test Collection" "Starting..."

case "$TEST_GROUP" in
    quick)
        PYTEST_MARKERS="-m 'not slow and not integration'"
        TIMEOUT=60
        MAXFAIL=20
        ;;
    slow)
        PYTEST_MARKERS="-m 'slow'"
        TIMEOUT=600
        MAXFAIL=5
        ;;
    integration)
        PYTEST_MARKERS="-m 'integration and not slow'"
        TIMEOUT=300
        MAXFAIL=10
        ;;
    documentation)
        echo "Documentation validation not yet implemented in self-test"
        exit 0
        ;;
    all)
        PYTEST_MARKERS=""
        TIMEOUT=600
        MAXFAIL=50
        ;;
    *)
        echo "Unknown test group: $TEST_GROUP"
        exit 1
        ;;
esac

# Collect tests with timeout
log_step "Collection Command" "pytest tests/ --co -q $PYTEST_MARKERS --timeout=$TIMEOUT"

COLLECTION_OUTPUT=$(timeout 30 python -m pytest tests/ --co -q $PYTEST_MARKERS 2>&1 || echo "COLLECTION_TIMEOUT")

if [[ "$COLLECTION_OUTPUT" == *"COLLECTION_TIMEOUT"* ]]; then
    log_error "Test collection timed out after 30 seconds"
    echo -e "\n\`\`\`\nTest collection timed out - this indicates a serious issue\n\`\`\`\n" >> "$REPORT_FILE"
    exit 1
fi

# Count collected tests
COLLECTED_COUNT=$(echo "$COLLECTION_OUTPUT" | grep -c "^tests/" || echo "0")
log_step "Tests Collected" "$COLLECTED_COUNT tests"
echo -e "\n**Total Collected:** $COLLECTED_COUNT tests\n" >> "$REPORT_FILE"

if [ "$COLLECTED_COUNT" -eq 0 ]; then
    log_warning "No tests collected - check markers and test availability"
fi

# Step 3: Run tests with monitoring
echo -e "\n${BLUE}Step 3: Test Execution${NC}"
echo -e "\n## Step 3: Test Execution\n" >> "$REPORT_FILE"

log_step "Execution Command" "pytest tests/ -v $PYTEST_MARKERS --timeout=$TIMEOUT --tb=short --maxfail=$MAXFAIL"

# Run tests and capture output
TEST_START=$(date +%s)
TEST_OUTPUT_FILE="$REPORT_DIR/pytest_output_${TEST_GROUP}_${TIMESTAMP}.txt"

echo "Running tests (this may take several minutes)..."
echo "Output being written to: $TEST_OUTPUT_FILE"

if python -m pytest tests/ -v $PYTEST_MARKERS --timeout=$TIMEOUT --tb=short --maxfail=$MAXFAIL > "$TEST_OUTPUT_FILE" 2>&1; then
    TEST_EXIT_CODE=0
    TEST_STATUS="PASSED"
    log_success "All tests passed"
else
    TEST_EXIT_CODE=$?
    TEST_STATUS="FAILED"
    log_error "Tests failed with exit code $TEST_EXIT_CODE"
fi

TEST_END=$(date +%s)
TEST_DURATION=$((TEST_END - TEST_START))

log_step "Test Duration" "${TEST_DURATION}s"

# Step 4: Analyze results
echo -e "\n${BLUE}Step 4: Result Analysis${NC}"
echo -e "\n## Step 4: Result Analysis\n" >> "$REPORT_FILE"

# Extract counts from pytest output
PASSED_COUNT=$(grep -c "PASSED" "$TEST_OUTPUT_FILE" || echo "0")
FAILED_COUNT=$(grep -c "FAILED" "$TEST_OUTPUT_FILE" || echo "0")
SKIPPED_COUNT=$(grep -c "SKIPPED" "$TEST_OUTPUT_FILE" || echo "0")
ERROR_COUNT=$(grep -c "ERROR" "$TEST_OUTPUT_FILE" || echo "0")

cat >> "$REPORT_FILE" <<EOF
### Test Results Summary

| Metric | Count |
|--------|-------|
| ✅ Passed | $PASSED_COUNT |
| ❌ Failed | $FAILED_COUNT |
| ⏭️  Skipped | $SKIPPED_COUNT |
| 💥 Errors | $ERROR_COUNT |
| ⏱️  Duration | ${TEST_DURATION}s |
| 📊 Status | $TEST_STATUS |

EOF

echo "Results:"
echo "  Passed:  $PASSED_COUNT"
echo "  Failed:  $FAILED_COUNT"
echo "  Skipped: $SKIPPED_COUNT"
echo "  Errors:  $ERROR_COUNT"

# Extract failure details
if [ "$FAILED_COUNT" -gt 0 ]; then
    echo -e "\n### Failed Tests\n" >> "$REPORT_FILE"
    echo -e "\n\`\`\`" >> "$REPORT_FILE"
    grep "FAILED" "$TEST_OUTPUT_FILE" | head -50 >> "$REPORT_FILE"
    echo -e "\`\`\`\n" >> "$REPORT_FILE"
    
    log_warning "$FAILED_COUNT test failures detected"
fi

# Extract timeout issues
TIMEOUT_COUNT=$(grep -c "Timeout" "$TEST_OUTPUT_FILE" || echo "0")
if [ "$TIMEOUT_COUNT" -gt 0 ]; then
    echo -e "\n### Timeout Issues\n" >> "$REPORT_FILE"
    echo -e "\n\`\`\`" >> "$REPORT_FILE"
    grep -B 2 -A 2 "Timeout" "$TEST_OUTPUT_FILE" | head -30 >> "$REPORT_FILE"
    echo -e "\`\`\`\n" >> "$REPORT_FILE"
    
    log_error "$TIMEOUT_COUNT timeout issues detected"
fi

# Step 5: Coverage analysis
echo -e "\n${BLUE}Step 5: Coverage Analysis${NC}"
echo -e "\n## Step 5: Coverage Analysis\n" >> "$REPORT_FILE"

# Calculate coverage percentage
TOTAL_TESTS=68  # Baseline total from documentation
CURRENT_PASSING=$PASSED_COUNT

if [ "$TEST_GROUP" = "quick" ] || [ "$TEST_GROUP" = "all" ]; then
    COVERAGE_PCT=$(awk "BEGIN {printf \"%.1f\", ($CURRENT_PASSING / $TOTAL_TESTS) * 100}")
    
    cat >> "$REPORT_FILE" <<EOF
**Coverage Calculation:**
- Total Tests (baseline): $TOTAL_TESTS
- Currently Passing: $CURRENT_PASSING
- Coverage: $COVERAGE_PCT%

**Targets:**
- Baseline: 77.9% (53/68 tests)
- Phase 1: 80.9% (55/68 tests) - need +2 tests
- Phase 2: 85.3% (58/68 tests) - need +5 tests

EOF

    echo "Coverage: $COVERAGE_PCT% ($CURRENT_PASSING/$TOTAL_TESTS)"
    
    # Check if we've reached targets
    if [ "$CURRENT_PASSING" -ge 58 ]; then
        log_success "Phase 2 target reached (85.3%+)"
    elif [ "$CURRENT_PASSING" -ge 55 ]; then
        log_success "Phase 1 target reached (80.9%+)"
        log_warning "Phase 2 target not yet reached (need $((58 - CURRENT_PASSING)) more tests)"
    elif [ "$CURRENT_PASSING" -ge 53 ]; then
        log_warning "Baseline maintained (77.9%)"
        log_warning "Phase 1 target not yet reached (need $((55 - CURRENT_PASSING)) more tests)"
    else
        log_error "Below baseline (need $((53 - CURRENT_PASSING)) tests to restore baseline)"
    fi
fi

# Step 6: Failure categorization
echo -e "\n${BLUE}Step 6: Failure Categorization${NC}"
echo -e "\n## Step 6: Failure Categorization\n" >> "$REPORT_FILE"

if [ "$FAILED_COUNT" -gt 0 ]; then
    echo "Categorizing failures..."
    
    # Category detection
    PROTOCOL_FAILURES=$(grep -c "isinstance.*Protocol\|Protocol.*isinstance" "$TEST_OUTPUT_FILE" || echo "0")
    IMPORT_FAILURES=$(grep -c "ImportError\|ModuleNotFoundError" "$TEST_OUTPUT_FILE" || echo "0")
    ASSERTION_FAILURES=$(grep -c "AssertionError" "$TEST_OUTPUT_FILE" || echo "0")
    ATTRIBUTE_FAILURES=$(grep -c "AttributeError" "$TEST_OUTPUT_FILE" || echo "0")
    TYPE_FAILURES=$(grep -c "TypeError" "$TEST_OUTPUT_FILE" || echo "0")
    
    cat >> "$REPORT_FILE" <<EOF
### Failure Categories

| Category | Count | Priority |
|----------|-------|----------|
| Protocol isinstance | $PROTOCOL_FAILURES | High (Phase 2 target) |
| Import errors | $IMPORT_FAILURES | Critical |
| Assertion failures | $ASSERTION_FAILURES | Medium |
| Attribute errors | $ATTRIBUTE_FAILURES | High |
| Type errors | $TYPE_FAILURES | High |

EOF

    if [ "$PROTOCOL_FAILURES" -gt 0 ]; then
        log_warning "$PROTOCOL_FAILURES Protocol isinstance failures (add @runtime_checkable)"
    fi
    if [ "$IMPORT_FAILURES" -gt 0 ]; then
        log_error "$IMPORT_FAILURES import failures (dependency issue)"
    fi
fi

# Step 7: Recommendations
echo -e "\n${BLUE}Step 7: Recommendations${NC}"
echo -e "\n## Step 7: Recommendations\n" >> "$REPORT_FILE"

cat >> "$REPORT_FILE" <<EOF
### Action Items

EOF

if [ "$TEST_STATUS" = "PASSED" ]; then
    echo "✅ **Ready for CI push** - all tests passing locally" >> "$REPORT_FILE"
    log_success "Ready for CI push"
elif [ "$FAILED_COUNT" -le 5 ]; then
    echo "⚠️ **Fix $FAILED_COUNT failures before push** - manageable count" >> "$REPORT_FILE"
    log_warning "Fix $FAILED_COUNT failures before push"
elif [ "$FAILED_COUNT" -le 20 ]; then
    echo "❌ **Significant issues detected** - $FAILED_COUNT failures need investigation" >> "$REPORT_FILE"
    log_error "$FAILED_COUNT failures - investigate before push"
else
    echo "🚨 **Major problems** - $FAILED_COUNT failures indicate systemic issues" >> "$REPORT_FILE"
    log_error "MAJOR ISSUES: $FAILED_COUNT failures"
fi

# Duration check
if [ "$TEST_DURATION" -gt 780 ]; then  # 13 minutes
    echo "⚠️ **CI timeout risk** - execution took ${TEST_DURATION}s (>13min)" >> "$REPORT_FILE"
    log_error "CI timeout risk: ${TEST_DURATION}s execution time"
elif [ "$TEST_DURATION" -gt 600 ]; then  # 10 minutes
    echo "⚠️ **Long execution** - ${TEST_DURATION}s may approach CI limits" >> "$REPORT_FILE"
    log_warning "Long execution: ${TEST_DURATION}s"
else
    echo "✅ **Good execution time** - ${TEST_DURATION}s well within CI limits" >> "$REPORT_FILE"
    log_success "Execution time: ${TEST_DURATION}s (safe)"
fi

# Final summary
echo -e "\n---\n" >> "$REPORT_FILE"
echo "**Full pytest output:** \`$TEST_OUTPUT_FILE\`" >> "$REPORT_FILE"
echo "**Report generated:** $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$REPORT_FILE"

echo -e "\n${BLUE}================================${NC}"
echo -e "${BLUE}Self-CI Validation Complete${NC}"
echo -e "${BLUE}================================${NC}"
echo ""
echo "Report saved to: $REPORT_FILE"
echo "Full output: $TEST_OUTPUT_FILE"
echo ""

if [ "$TEST_STATUS" = "PASSED" ]; then
    echo -e "${GREEN}Status: READY FOR CI${NC}"
    exit 0
else
    echo -e "${RED}Status: NEEDS FIXES (Exit code: $TEST_EXIT_CODE)${NC}"
    exit "$TEST_EXIT_CODE"
fi
