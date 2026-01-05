#!/bin/bash
# Safe removal script for cognitive_codex_app.zip
# Only run this after verifying successful deployment

echo "================================================"
echo "Cognitive Codex App - Zip File Removal Script"
echo "================================================"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "cognitive_codex_app.zip" ]; then
    echo -e "${RED}Error: cognitive_codex_app.zip not found in current directory${NC}"
    echo "Please run this script from the repository root"
    exit 1
fi

echo "⚠️  WARNING: This script will remove cognitive_codex_app.zip"
echo ""
echo "Before proceeding, please verify:"
echo "1. ✅ GitHub Actions deployment completed successfully"
echo "2. ✅ Application is accessible at: https://aries-serpent.github.io/_codex_/cognitive_app/"
echo "3. ✅ All components load correctly in the browser"
echo "4. ✅ No console errors in browser"
echo "5. ✅ cognitive_app/ directory contains all files"
echo ""

# Verification questions
read -p "Have you verified the deployment is successful? (yes/no): " deployment_verified

if [ "$deployment_verified" != "yes" ]; then
    echo -e "${YELLOW}Aborting removal. Please verify deployment first.${NC}"
    exit 0
fi

read -p "Have you tested the live application in a browser? (yes/no): " browser_tested

if [ "$browser_tested" != "yes" ]; then
    echo -e "${YELLOW}Aborting removal. Please test in browser first.${NC}"
    exit 0
fi

read -p "Are you sure you want to remove cognitive_codex_app.zip? (yes/no): " final_confirm

if [ "$final_confirm" != "yes" ]; then
    echo -e "${YELLOW}Removal cancelled.${NC}"
    exit 0
fi

echo ""
echo "Performing safety checks..."
echo ""

# Safety check 1: Verify cognitive_app directory exists
if [ ! -d "cognitive_app" ]; then
    echo -e "${RED}✗ Safety check failed: cognitive_app directory not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} cognitive_app directory exists"

# Safety check 2: Verify key files exist
key_files=(
    "cognitive_app/package.json"
    "cognitive_app/src/App.tsx"
    "cognitive_app/README_INTEGRATION.md"
)

all_files_present=true
for file in "${key_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}✗ Safety check failed: $file not found${NC}"
        all_files_present=false
    fi
done

if [ "$all_files_present" = false ]; then
    echo -e "${RED}Some critical files are missing. Aborting removal.${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} All key files present in cognitive_app/"

# Safety check 3: Verify file count
ts_count=$(find cognitive_app/src -name "*.tsx" -o -name "*.ts" 2>/dev/null | wc -l)
if [ "$ts_count" -lt 90 ]; then
    echo -e "${RED}✗ Safety check failed: Expected 90+ TypeScript files, found $ts_count${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} TypeScript file count OK ($ts_count files)"

echo ""
echo "All safety checks passed. Removing zip file..."
echo ""

# Get file size for logging
zip_size=$(ls -lh cognitive_codex_app.zip | awk '{print $5}')

# Remove the file
rm cognitive_codex_app.zip

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Successfully removed cognitive_codex_app.zip ($zip_size)${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Commit the removal:"
    echo "   git add -u"
    echo "   git commit -m 'Remove cognitive_codex_app.zip after successful integration and verification'"
    echo "   git push origin main"
    echo ""
    echo "2. Update documentation if needed"
    echo "3. Monitor application for any issues"
else
    echo -e "${RED}✗ Failed to remove file${NC}"
    exit 1
fi

echo ""
echo "Removal complete! ✅"
