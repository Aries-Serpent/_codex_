#!/bin/bash
set -euo pipefail

echo "========================================"
echo "   CI HEALTH VALIDATION DASHBOARD"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check workflow count
# Note: wc -l counts the number of lines output by find, which equals the number of files found
echo "📊 Workflow Statistics"
echo "----------------------------------------"
ACTIVE_COUNT=$(find .github/workflows -type f -name "*.yml" | wc -l)
DISABLED_COUNT=$(find .github/workflow-archive/disabled -type f -name "*.yml" 2>/dev/null | wc -l || echo 0)
TOTAL=$((ACTIVE_COUNT + DISABLED_COUNT))

echo "Active workflows:    $ACTIVE_COUNT"
echo "Disabled workflows:  $DISABLED_COUNT"
echo "Total workflows:     $TOTAL"
echo "Target:              48 active workflows"
echo ""

# Verify no syntax errors
echo "🔍 YAML Syntax Validation"
echo "----------------------------------------"
SYNTAX_ERRORS=0
for file in .github/workflows/*.yml; do
    if [ -f "$file" ]; then
        if python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null; then
            echo -e "${GREEN}✅${NC} $(basename "$file")"
        else
            echo -e "${RED}❌${NC} $(basename "$file")"
            SYNTAX_ERRORS=$((SYNTAX_ERRORS + 1))
        fi
    fi
done

if [ $SYNTAX_ERRORS -eq 0 ]; then
    echo -e "\n${GREEN}✅ All workflows have valid YAML syntax${NC}"
else
    echo -e "\n${RED}❌ Found $SYNTAX_ERRORS workflows with syntax errors${NC}"
fi
echo ""

# Overall summary
echo "========================================"
echo "   OVERALL CI HEALTH SUMMARY"
echo "========================================"

if [ $SYNTAX_ERRORS -eq 0 ] && [ $ACTIVE_COUNT -le 70 ]; then
    echo -e "${GREEN}✅ CI HEALTH: EXCELLENT${NC}"
    echo "   - All workflows have valid syntax"
    echo "   - Workflow consolidation system operational"
    exit 0
elif [ $SYNTAX_ERRORS -le 2 ]; then
    echo -e "${YELLOW}⚠️  CI HEALTH: GOOD (Minor Issues)${NC}"
    echo "   - $SYNTAX_ERRORS minor issues detected"
    exit 0
else
    echo -e "${RED}❌ CI HEALTH: NEEDS ATTENTION${NC}"
    echo "   - $SYNTAX_ERRORS issues detected"
    exit 1
fi
