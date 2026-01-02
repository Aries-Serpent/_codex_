#!/usr/bin/env bash
# Pre-commit hook to check environment variable candidate file sizes
# Install: ln -s ../../.github/scripts/pre-commit-env-check.sh .git/hooks/pre-commit

set -e

# Maximum file size (36KB = 36,956 bytes)
MAX_SIZE=36956

# Candidate files to check
CANDIDATE_FILES=(
    "src/cognitive_brain/quantum/ghz_states.py"
    "src/cognitive_brain/quantum/multi_agent_coordinator.py"
    "src/cognitive_brain/quantum/topology_manager.py"
    "src/codex_ml/data/validation.py"
    "src/codex_ml/config/__init__.py"
)

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo "🔍 Checking environment variable candidate files..."

warnings=0
errors=0

for file in "${CANDIDATE_FILES[@]}"; do
    # Check if file is staged
    if git diff --cached --name-only | grep -q "^${file}$"; then
        # File is being committed, check its size
        if [ -f "$file" ]; then
            size=$(wc -c < "$file")
            encoded_size=$(echo "scale=0; $size * 1.33 / 1" | bc)
            max_env_size=49152
            pct=$(echo "scale=1; $encoded_size * 100 / $max_env_size" | bc)
            
            echo ""
            echo "📄 $file"
            echo "   Original: $size bytes"
            echo "   Base64: ~$encoded_size bytes"
            echo "   Usage: $pct% of 48KB"
            
            if [ "$size" -gt "$MAX_SIZE" ]; then
                echo -e "   ${RED}❌ ERROR: File exceeds 36KB limit!${NC}"
                echo "   This file will NOT fit in a 48KB GitHub environment variable."
                echo "   Consider splitting the file or removing it from candidates."
                errors=$((errors + 1))
            elif [ "$size" -gt 30000 ]; then
                echo -e "   ${YELLOW}⚠️  WARNING: File is getting large (>30KB)${NC}"
                echo "   Monitor size carefully. Close to 36KB limit."
                warnings=$((warnings + 1))
            else
                echo -e "   ${GREEN}✅ OK${NC}"
            fi
        fi
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$errors" -gt 0 ]; then
    echo -e "${RED}❌ $errors file(s) exceed size limits!${NC}"
    echo ""
    echo "Options:"
    echo "  1. Reduce file size to fit in 36KB limit"
    echo "  2. Remove file from CANDIDATE_FILES list"
    echo "  3. Skip check with: git commit --no-verify"
    echo ""
    exit 1
fi

if [ "$warnings" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  $warnings file(s) approaching size limits${NC}"
    echo "Consider monitoring these files carefully."
else
    echo -e "${GREEN}✅ All environment variable candidates are within limits${NC}"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

exit 0
