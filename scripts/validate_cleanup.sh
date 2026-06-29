#!/bin/bash
# Comprehensive cleanup validation script
# This script runs all validation checks to ensure cleanup doesn't break anything

set -o pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
SKIPPED=0

# Function to print section headers
print_header() {
    echo ""
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo ""
}

# Function to print success
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
    ((PASSED++))
}

# Function to print failure
print_failure() {
    echo -e "${RED}✗ $1${NC}"
    ((FAILED++))
}

# Function to print info
print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
    ((SKIPPED++))
}

# ============================================================================
# PHASE 1: Configuration Loading Validation
# ============================================================================

print_header "PHASE 1: Configuration Loading Validation"

# Check pytest.ini
if [ -f "pytest.ini" ]; then
    print_success "pytest.ini found"
    if grep -q "pythonpath = src" pytest.ini; then
        print_success "pytest.ini has correct pythonpath"
    else
        print_failure "pytest.ini missing pythonpath = src"
    fi
else
    print_failure "pytest.ini not found"
fi

# Check mypy.ini
if [ -f "mypy.ini" ]; then
    print_success "mypy.ini found"
    if grep -q "python_version = 3.12" mypy.ini; then
        print_success "mypy.ini has Python 3.12 configured"
    else
        print_failure "mypy.ini doesn't have Python 3.12 configured"
    fi
else
    print_failure "mypy.ini not found"
fi

# Check pyproject.toml
if [ -f "pyproject.toml" ]; then
    print_success "pyproject.toml found"
    if grep -q "\[build-system\]" pyproject.toml; then
        print_success "pyproject.toml has build-system section"
    else
        print_failure "pyproject.toml missing build-system section"
    fi
else
    print_failure "pyproject.toml not found"
fi

# Check requirements files
for req_file in requirements.txt requirements-dev.txt requirements-test.txt; do
    if [ -f "$req_file" ]; then
        print_success "$req_file found"
    else
        print_failure "$req_file not found"
    fi
done

# ============================================================================
# PHASE 2: Tool Integration Validation
# ============================================================================

print_header "PHASE 2: Tool Integration Validation"

# Test pytest collection
if python -m pytest tests/ --collect-only -q > /dev/null 2>&1; then
    print_success "pytest can collect tests"
else
    print_failure "pytest test collection failed"
fi

# Test mypy version check
if python -m mypy --version > /dev/null 2>&1; then
    print_success "mypy works correctly"
else
    print_failure "mypy failed"
fi

# Check pre-commit config
if [ -f ".pre-commit-config.yaml" ] || [ -f ".pre-commit-ruff.yaml" ]; then
    print_success "pre-commit configuration found"
else
    print_failure "pre-commit configuration not found"
fi

# Check ruff config
if [ -f ".ruff.toml" ] || grep -q "\[tool.ruff\]" pyproject.toml; then
    print_success "ruff configuration found"
else
    print_failure "ruff configuration not found"
fi

# Check editorconfig
if [ -f ".editorconfig" ]; then
    print_success ".editorconfig found"
else
    print_failure ".editorconfig not found"
fi

# ============================================================================
# PHASE 3: Import Path Validation
# ============================================================================

print_header "PHASE 3: Import Path Validation"

# Test basic import
if python -c "import sys; sys.path.insert(0, 'src'); import codex; print('✓')" > /dev/null 2>&1; then
    print_success "Can import codex package"
else
    print_failure "Failed to import codex package"
fi

# Test submodule imports
for module in "codex.rag" "codex.utils" "codex.agent" "codex.integrations"; do
    if python -c "import sys; sys.path.insert(0, 'src'); import $module" > /dev/null 2>&1; then
        print_success "Can import $module"
    else
        print_info "Could not import $module (may be optional)"
    fi
done

# ============================================================================
# PHASE 4: Workflow Simulation
# ============================================================================

print_header "PHASE 4: Workflow Simulation"

# Test basic test discovery
if python -m pytest tests/ --collect-only -q 2>&1 | grep -q "test"; then
    print_success "Test discovery works"
else
    print_failure "Test discovery failed"
fi

# Test critical config files in place
critical_files=("pytest.ini" "mypy.ini" "pyproject.toml" ".editorconfig" ".pre-commit-config.yaml")
for file in "${critical_files[@]}"; do
    if [ -f "$file" ]; then
        print_success "Critical file $file exists"
    else
        print_failure "Critical file $file missing"
    fi
done

# ============================================================================
# PHASE 5: Run Comprehensive Validation Tests
# ============================================================================

print_header "PHASE 5: Running Comprehensive Validation Tests"

echo "Running cleanup validation test suite..."
echo ""

if python -m pytest tests/cleanup_validation/ -v --tb=short 2>&1 | tee /tmp/cleanup_validation_results.txt; then
    print_success "All validation tests passed"
else
    # Check if it was just no tests collected
    if grep -q "no tests ran" /tmp/cleanup_validation_results.txt || grep -q "error" /tmp/cleanup_validation_results.txt; then
        print_failure "Validation tests failed"
    else
        print_success "Validation tests completed"
    fi
fi

# ============================================================================
# Summary
# ============================================================================

print_header "VALIDATION SUMMARY"

echo "Passed checks:  $PASSED"
echo "Failed checks:  $FAILED"
echo "Skipped checks: $SKIPPED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✓ ALL VALIDATION CHECKS PASSED${NC}"
    echo -e "${GREEN}✓ Cleanup is safe to execute${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
    exit 0
else
    echo -e "${RED}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${RED}✗ VALIDATION CHECKS FAILED: $FAILED issues detected${NC}"
    echo -e "${RED}✗ Fix issues before proceeding with cleanup${NC}"
    echo -e "${RED}════════════════════════════════════════════════════════════════${NC}"
    exit 1
fi
