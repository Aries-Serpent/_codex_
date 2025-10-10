#!/usr/bin/env bash
# Comprehensive capability validation suite
# Author: mbaetiong
# Generated: 2025-10-10 06:11:06
# Compliance: AGENTS.md (local validation only)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "================================================"
echo "Capability Validation Suite (AGENTS.md)"
echo "================================================"

EXIT_CODE=0

# ========================================
# 1. Security Validation
# ========================================
echo ""
echo -e "${YELLOW}[1/8] Security Validation${NC}"
if [ -x scripts/validate_security.sh ]; then
    if bash scripts/validate_security.sh; then
        echo -e "${GREEN}✓ Security validation passed${NC}"
    else
        echo -e "${RED}✗ Security validation failed${NC}"
        EXIT_CODE=1
    fi
else
    echo -e "${YELLOW}⚠ scripts/validate_security.sh not found${NC}"
fi

# ========================================
# 2. Code Quality Validation
# ========================================
echo ""
echo -e "${YELLOW}[2/8] Code Quality Validation${NC}"

# Black formatting
if command -v black &> /dev/null; then
    if black --check --line-length=100 src/ tests/ scripts/ 2>/dev/null; then
        echo -e "${GREEN}✓ Black formatting passed${NC}"
    else
        echo -e "${RED}✗ Black formatting violations found${NC}"
        EXIT_CODE=1
    fi
else
    echo -e "${YELLOW}⚠ Black not installed${NC}"
fi

# Ruff linting
if command -v ruff &> /dev/null; then
    if ruff check src/ tests/ scripts/ 2>/dev/null; then
        echo -e "${GREEN}✓ Ruff linting passed${NC}"
    else
        echo -e "${RED}✗ Ruff linting violations found${NC}"
        EXIT_CODE=1
    fi
else
    echo -e "${YELLOW}⚠ Ruff not installed${NC}"
fi

# ========================================
# 3. Type Checking
# ========================================
echo ""
echo -e "${YELLOW}[3/8] Type Checking${NC}"
if command -v mypy &> /dev/null; then
    if mypy src/security/ --config-file=pyproject.toml 2>/dev/null; then
        echo -e "${GREEN}✓ Type checking passed (security module)${NC}"
    else
        echo -e "${YELLOW}⚠ Type checking warnings (acceptable for gradual adoption)${NC}"
    fi
else
    echo -e "${YELLOW}⚠ mypy not installed${NC}"
fi

# ========================================
# 4. Testing Infrastructure
# ========================================
echo ""
echo -e "${YELLOW}[4/8] Testing Infrastructure${NC}"
if PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/ -q --tb=short -m "not slow" 2>/dev/null; then
    echo -e "${GREEN}✓ Fast test suite passed${NC}"
else
    echo -e "${RED}✗ Tests failed${NC}"
    EXIT_CODE=1
fi

# ========================================
# 5. Documentation Validation
# ========================================
echo ""
echo -e "${YELLOW}[5/8] Documentation Validation${NC}"
if [ -f mkdocs.yml ] && command -v mkdocs &> /dev/null; then
    if mkdocs build --strict --site-dir /tmp/mkdocs_test 2>/dev/null; then
        echo -e "${GREEN}✓ Documentation build passed${NC}"
    else
        echo -e "${YELLOW}⚠ Documentation build warnings${NC}"
    fi
else
    echo -e "${YELLOW}⚠ MkDocs not configured or installed${NC}"
fi

# ========================================
# 6. Reproducibility Checks
# ========================================
echo ""
echo -e "${YELLOW}[6/8] Reproducibility Checks${NC}"
REPRO_SCORE=0

# Check for seed management
if grep -r "seed" src/ --include="*.py" | grep -q "def.*seed"; then
    REPRO_SCORE=$((REPRO_SCORE + 1))
fi

# Check for SHA256 usage
if grep -r "sha256" src/ --include="*.py" | wc -l | grep -q "[1-9]"; then
    REPRO_SCORE=$((REPRO_SCORE + 1))
fi

# Check for offline mode guards
if grep -r "WANDB_MODE\|offline" src/ --include="*.py" | wc -l | grep -q "[1-9]"; then
    REPRO_SCORE=$((REPRO_SCORE + 1))
fi

if [ $REPRO_SCORE -ge 2 ]; then
    echo -e "${GREEN}✓ Reproducibility safeguards present ($REPRO_SCORE/3)${NC}"
else
    echo -e "${YELLOW}⚠ Limited reproducibility safeguards ($REPRO_SCORE/3)${NC}"
fi

# ========================================
# 7. Deployment Infrastructure
# ========================================
echo ""
echo -e "${YELLOW}[7/8] Deployment Infrastructure${NC}"
if [ -f Dockerfile ]; then
    # Check for multi-stage build
    if grep -q "AS.*runtime" Dockerfile; then
        echo -e "${GREEN}✓ Multi-stage Dockerfile present${NC}"
    else
        echo -e "${YELLOW}⚠ Dockerfile exists but not multi-stage${NC}"
    fi

    # Check for health check
    if grep -q "HEALTHCHECK" Dockerfile; then
        echo -e "${GREEN}✓ Health check configured${NC}"
    else
        echo -e "${YELLOW}⚠ No health check in Dockerfile${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Dockerfile not found${NC}"
fi

# ========================================
# 8. Space Traversal Audit
# ========================================
echo ""
echo -e "${YELLOW}[8/8] Space Traversal Audit${NC}"
if [ -f scripts/space_traversal/audit_runner.py ]; then
    if python scripts/space_traversal/audit_runner.py stage S1 2>/dev/null; then
        echo -e "${GREEN}✓ Audit pipeline S1 (context index) passed${NC}"
    else
        echo -e "${RED}✗ Audit pipeline failed${NC}"
        EXIT_CODE=1
    fi
else
    echo -e "${YELLOW}⚠ Audit runner not found${NC}"
fi

# ========================================
# Summary
# ========================================
echo ""
echo "================================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}All critical validations passed!${NC}"
else
    echo -e "${RED}Some validations failed (see above)${NC}"
fi
echo "================================================"

exit $EXIT_CODE
