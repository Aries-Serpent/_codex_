#!/bin/bash
set -e

echo "══════════════════════════════════════════════════════════════"
echo "COPILOT CONTINUATION SYSTEM - COMPREHENSIVE VALIDATION"
echo "══════════════════════════════════════════════════════════════"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Test helper functions
test_start() {
    TESTS_RUN=$((TESTS_RUN + 1))
    echo -n "Test $TESTS_RUN: $1... "
}

test_pass() {
    TESTS_PASSED=$((TESTS_PASSED + 1))
    echo -e "${GREEN}✅ PASS${NC}"
}

test_fail() {
    TESTS_FAILED=$((TESTS_FAILED + 1))
    echo -e "${RED}❌ FAIL${NC}"
    if [ -n "$1" ]; then
        echo "  Error: $1"
    fi
}

echo "PHASE 1: FILE STRUCTURE VALIDATION"
echo "──────────────────────────────────────────────────────────────"

# Test 1: Check PR template exists
test_start "PR template exists"
if [ -f ".github/pull_request_template.md" ]; then
    test_pass
else
    test_fail "PR template not found"
fi

# Test 2: Check prompt directory structure
test_start "Prompt directory structure"
if [ -d ".github/copilot-prompts/templates" ] && \
   [ -d ".github/copilot-prompts/active" ] && \
   [ -f ".github/copilot-prompts/README.md" ]; then
    test_pass
else
    test_fail "Directory structure incomplete"
fi

# Test 3: Check template files
test_start "Template files exist"
TEMPLATES=(
    "pr-continuation.md"
    "multi-phase-implementation.md"
    "ci-fix-continuation.md"
    "consolidation.md"
)
MISSING=0
for template in "${TEMPLATES[@]}"; do
    if [ ! -f ".github/copilot-prompts/templates/$template" ]; then
        MISSING=$((MISSING + 1))
    fi
done
if [ $MISSING -eq 0 ]; then
    test_pass
else
    test_fail "$MISSING template(s) missing"
fi

# Test 4: Check generator script
test_start "Generator script exists and executable"
if [ -f "scripts/generate_pr_followup.py" ] && [ -x "scripts/generate_pr_followup.py" ]; then
    test_pass
else
    test_fail "Generator script missing or not executable"
fi

# Test 5: Check workflow file
test_start "Auto-generation workflow exists"
if [ -f ".github/workflows/pr-followup-generator.yml" ]; then
    test_pass
else
    test_fail "Workflow file missing"
fi

echo ""
echo "PHASE 2: PR TEMPLATE VALIDATION"
echo "──────────────────────────────────────────────────────────────"

# Test 6: Check for continuation directive
test_start "Continuation directive present"
if grep -q "@copilot continue" .github/pull_request_template.md; then
    test_pass
else
    test_fail "Continuation directive not found"
fi

# Test 7: Check for prompt link
test_start "Prompt reference present"
if grep -q "View Active Prompt" .github/pull_request_template.md; then
    test_pass
else
    test_fail "Prompt reference not found"
fi

# Test 8: Check template version
test_start "Template version updated"
if grep -q "Version.*1\.5\.0" .github/pull_request_template.md; then
    test_pass
else
    test_fail "Template version not updated to 1.5.0"
fi

# Test 9: WEC never-check defaults stay unchecked
test_start "WEC continuation-loop defaults unchecked"
if grep -q -- "- \\[ \\] copilot-agent-session-done.yml" .github/pull_request_template.md && \
   grep -q -- "- \\[ \\] copilot-iterative-self-healing.yml" .github/pull_request_template.md && \
   grep -q -- "- \\[ \\] auto-approve-workflows" .github/pull_request_template.md; then
    test_pass
else
    test_fail "Continuation-loop defaults are not safely unchecked"
fi

echo ""
echo "PHASE 3: GENERATOR SCRIPT VALIDATION"
echo "──────────────────────────────────────────────────────────────"

# Test 10: Script syntax check
test_start "Python syntax valid"
if python3 -m py_compile scripts/generate_pr_followup.py 2>/dev/null; then
    test_pass
else
    test_fail "Python syntax errors"
fi

# Test 11: Script help output
test_start "Script help works"
if python3 scripts/generate_pr_followup.py --help > /dev/null 2>&1; then
    test_pass
else
    test_fail "Script help failed"
fi

# Test 12: Test prompt generation
test_start "Generate test prompt"
export GITHUB_PR_NUMBER=9999
export GITHUB_HEAD_REF=test-branch
export GITHUB_ACTOR=test-user
export GITHUB_SHA=abc123def456
export PR_TITLE="Test PR"

mkdir -p .codex/test-outputs
if python3 scripts/generate_pr_followup.py 9999 \
    --immediate "Task 1" "Task 2" \
    --validation "Test 1" \
    --future "Enhancement 1" \
    --output .codex/test-outputs/test-prompt-$$.md > /dev/null 2>&1; then
    test_pass
    # Clean up
    rm -f .codex/test-outputs/test-prompt-$$.md
else
    test_fail "Prompt generation failed"
fi

echo ""
echo "PHASE 4: TEMPLATE CONTENT VALIDATION"
echo "──────────────────────────────────────────────────────────────"

# Test 13: Check template variables
test_start "Template variables present"
TEMPLATE_FILE=".github/copilot-prompts/templates/pr-continuation.md"
REQUIRED_VARS=(
    "{pr_number}"
    "{branch}"
    "{pr_title}"
    "{immediate_tasks}"
    "{validation_tasks}"
    "{future_tasks}"
)
MISSING_VARS=0
for var in "${REQUIRED_VARS[@]}"; do
    if ! grep -q "$var" "$TEMPLATE_FILE" 2>/dev/null; then
        MISSING_VARS=$((MISSING_VARS + 1))
    fi
done
if [ $MISSING_VARS -eq 0 ]; then
    test_pass
else
    test_fail "$MISSING_VARS variable(s) missing"
fi

# Test 14: Check self-review protocol
test_start "Self-review protocol in template"
if grep -qi "MANDATORY.*5.*self-review" "$TEMPLATE_FILE" 2>/dev/null || \
   grep -qi "5.*pass.*self-review" "$TEMPLATE_FILE" 2>/dev/null; then
    test_pass
else
    test_fail "Self-review protocol not found"
fi

# Test 15: Check execution checklist
test_start "Execution checklist in template"
if grep -q "EXECUTION CHECKLIST" "$TEMPLATE_FILE" 2>/dev/null; then
    test_pass
else
    test_fail "Execution checklist not found"
fi

echo ""
echo "PHASE 5: WORKFLOW VALIDATION"
echo "──────────────────────────────────────────────────────────────"

# Test 16: YAML syntax check
test_start "Workflow YAML syntax valid"
if python3 -c "import yaml; yaml.safe_load(open('.github/workflows/pr-followup-generator.yml'))" 2>/dev/null; then
    test_pass
else
    test_fail "YAML syntax errors"
fi

# Test 17: Check workflow triggers
test_start "Workflow triggers configured"
if grep -q "pull_request:" .github/workflows/pr-followup-generator.yml && \
   grep -q "workflow_dispatch:" .github/workflows/pr-followup-generator.yml; then
    test_pass
else
    test_fail "Workflow triggers incomplete"
fi

# Test 18: Check workflow permissions
test_start "Workflow permissions set"
if grep -q "contents:" .github/workflows/pr-followup-generator.yml && \
   grep -q "pull-requests:" .github/workflows/pr-followup-generator.yml; then
    test_pass
else
    test_fail "Workflow permissions missing"
fi

echo ""
echo "PHASE 6: INTEGRATION VALIDATION"
echo "──────────────────────────────────────────────────────────────"

# Test 19: Check README exists
test_start "System README exists"
if [ -f ".github/copilot-prompts/README.md" ]; then
    test_pass
else
    test_fail "README not found"
fi

# Test 20: Check for Python import errors
test_start "No Python import errors"
if python3 -c "
import sys
import importlib.util
sys.path.insert(0, 'scripts')
try:
    spec = importlib.util.spec_from_file_location('gen', 'scripts/generate_pr_followup.py')
    if spec is not None and spec.loader is not None:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
except SystemExit:
    pass  # Expected from argparse
except SyntaxError as e:
    print(f'Syntax error: {e}')
    exit(1)
except ImportError as e:
    print(f'Import error: {e}')
    exit(1)
" 2>/dev/null; then
    test_pass
else
    test_fail "Python import errors"
fi

# Test 20: Verify continuation section in PR template
test_start "Continuation section complete in PR template"
if grep -q "COPILOT CONTINUATION" .github/pull_request_template.md && \
   grep -q "Priority 1" .github/pull_request_template.md && \
   grep -q "Execution Instructions" .github/pull_request_template.md; then
    test_pass
else
    test_fail "Continuation section incomplete"
fi

echo ""
echo "══════════════════════════════════════════════════════════════"
echo "TEST SUMMARY"
echo "══════════════════════════════════════════════════════════════"
echo ""
echo "Tests Run:     $TESTS_RUN"
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ ALL TESTS PASSED${NC}"
    echo ""
    echo "System is ready for production use."
    echo ""
    echo "Next steps:"
    echo "  1. Open a test PR to validate auto-generation"
    echo "  2. Comment '@copilot continue' to test execution"
    echo "  3. Monitor prompt updates and task completion"
    exit 0
else
    echo -e "${RED}❌ SOME TESTS FAILED${NC}"
    echo ""
    echo "Please fix the failures above before proceeding."
    exit 1
fi
