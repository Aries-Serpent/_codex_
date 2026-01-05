#!/bin/bash
# Cognitive Codex App - Integration Verification Script

echo "========================================"
echo "Cognitive Codex App Integration Verification"
echo "========================================"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Change to cognitive_app directory
cd "$(dirname "$0")" || exit 1

echo "📁 Directory Structure Verification"
echo "-----------------------------------"

# Check key directories
directories=(
    "src"
    "src/components"
    "src/components/code"
    "src/components/quantum"
    "src/components/ui"
    "src/hooks"
    "src/lib"
    "src/styles"
)

for dir in "${directories[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✓${NC} $dir exists"
    else
        echo -e "${RED}✗${NC} $dir missing"
    fi
done

echo ""
echo "📝 File Count Verification"
echo "--------------------------"

# Count TypeScript files
ts_count=$(find src -name "*.tsx" -o -name "*.ts" | wc -l)
echo "TypeScript files: $ts_count (expected: ~92)"

# Count quantum components
quantum_count=$(ls -1 src/components/quantum/*.tsx 2>/dev/null | wc -l)
echo "Quantum components: $quantum_count (expected: 27+)"

# Count UI components
ui_count=$(ls -1 src/components/ui/*.tsx 2>/dev/null | wc -l)
echo "UI components: $ui_count (expected: 44+)"

# Count code components
code_count=$(ls -1 src/components/code/*.tsx 2>/dev/null | wc -l)
echo "Code components: $code_count (expected: 3)"

# Count hooks
hooks_count=$(ls -1 src/hooks/*.ts 2>/dev/null | wc -l)
echo "Custom hooks: $hooks_count (expected: 5)"

echo ""
echo "📦 Configuration Files"
echo "---------------------"

config_files=(
    "package.json"
    "package-lock.json"
    "tsconfig.json"
    "vite.config.ts"
    "tailwind.config.js"
    "components.json"
    "index.html"
)

for file in "${config_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${RED}✗${NC} $file missing"
    fi
done

echo ""
echo "📚 Documentation Files"
echo "---------------------"

doc_files=(
    "README.md"
    "README_INTEGRATION.md"
    "CODEX_INTEGRATION_MASTER_PLAN.md"
    "IMPLEMENTATION_STATUS.md"
    "PRD.md"
    "SECURITY.md"
    "LICENSE"
)

for file in "${doc_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${RED}✗${NC} $file missing"
    fi
done

echo ""
echo "🔧 Build System Check"
echo "--------------------"

# Check if node_modules exists
if [ -d "node_modules" ]; then
    echo -e "${GREEN}✓${NC} Dependencies installed"
    pkg_count=$(ls -1 node_modules | wc -l)
    echo "  Packages: $pkg_count"
else
    echo -e "${YELLOW}⚠${NC} Dependencies not installed (run: npm install)"
fi

# Check if build was successful
if [ -d "dist" ]; then
    echo -e "${GREEN}✓${NC} Build output exists"
    if [ -f "dist/index.html" ]; then
        echo -e "${GREEN}✓${NC} Built index.html exists"
        # Check for base path
        if grep -q "/_codex_/cognitive_app/" "dist/index.html"; then
            echo -e "${GREEN}✓${NC} GitHub Pages base path configured correctly"
        else
            echo -e "${RED}✗${NC} Base path not configured for GitHub Pages"
        fi
    fi
else
    echo -e "${YELLOW}⚠${NC} Build not performed (run: npm run build)"
fi

echo ""
echo "🎨 Component Categories"
echo "----------------------"

# List quantum components
echo "Quantum Components:"
quantum_files=(
    "QuantumDecisionEngine.tsx"
    "QuantumVisualizer.tsx"
    "SuperpositionCard.tsx"
    "EntanglementCard.tsx"
    "QuantumMemoryViewer.tsx"
    "AgentOrchestrationPanel.tsx"
    "AgentCard.tsx"
    "WorkflowTokenOrchestrator.tsx"
    "MemoryManagementDashboard.tsx"
    "MetricsDashboard.tsx"
)

present=0
for file in "${quantum_files[@]}"; do
    if [ -f "src/components/quantum/$file" ]; then
        present=$((present + 1))
    fi
done
echo "  $present/${#quantum_files[@]} key components present"

echo ""
echo "✅ Integration Verification Complete"
echo ""
echo "Summary:"
echo "--------"
if [ $ts_count -ge 90 ] && [ $quantum_count -ge 27 ] && [ $ui_count -ge 44 ]; then
    echo -e "${GREEN}✓ All files successfully integrated${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Deploy via GitHub Actions (automatic on push to main)"
    echo "2. Verify at: https://aries-serpent.github.io/_codex_/cognitive_app/"
    echo "3. Remove cognitive_codex_app.zip after verification"
else
    echo -e "${RED}✗ Some files may be missing${NC}"
    echo "Please review the output above"
fi
