#!/bin/bash
# verify_implementation_claims.sh
# Validates that files claimed in PR descriptions actually exist
# Usage: ./verify_implementation_claims.sh [file_list.txt]

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔍 Implementation Claims Verification"
echo "====================================="
echo ""

FAILURES=0
SUCCESSES=0
TOTAL=0

# Function to verify a single file
verify_file() {
    local file=$1
    ((TOTAL++))
    
    if [ ! -e "$file" ]; then
        echo -e "${RED}❌ MISSING${NC}: $file"
        ((FAILURES++))
        return 1
    fi
    
    if [ ! -s "$file" ]; then
        echo -e "${YELLOW}⚠️  EMPTY${NC}: $file"
        ((FAILURES++))
        return 1
    fi
    
    SIZE=$(wc -l < "$file" 2>/dev/null || echo "N/A")
    echo -e "${GREEN}✅ EXISTS${NC}: $file ($SIZE lines)"
    ((SUCCESSES++))
    return 0
}

# If file list provided as argument, read from it
if [ $# -gt 0 ] && [ -f "$1" ]; then
    echo "Reading file list from: $1"
    echo ""
    while IFS= read -r file; do
        # Skip empty lines and comments
        [[ -z "$file" || "$file" =~ ^# ]] && continue
        verify_file "$file"
    done < "$1"
else
    # Default list of commonly claimed but missing files
    echo "Checking default critical files..."
    echo ""
    
    # GitHub Secrets CLI
    verify_file "tools/github-secrets-cli/main.go" || true
    verify_file "tools/github-secrets-cli/go.mod" || true
    verify_file "tools/github-secrets-cli/README.md" || true
    
    # Testing Orchestrator Agent
    verify_file ".github/agents/github-testing-orchestrator-agent/src/agent.py" || true
    verify_file ".github/agents/github-testing-orchestrator-agent/config/agent.yml" || true
    verify_file ".github/agents/github-testing-orchestrator-agent/README.md" || true
    
    # Security Validator Agent
    verify_file ".github/agents/github-security-validator-agent/src/agent.py" || true
    verify_file ".github/agents/github-security-validator-agent/config/agent.yml" || true
    verify_file ".github/agents/github-security-validator-agent/README.md" || true
fi

echo ""
echo "====================================="
echo "📊 Summary"
echo "====================================="
echo "Total files checked: $TOTAL"
echo -e "${GREEN}✅ Verified${NC}: $SUCCESSES"
echo -e "${RED}❌ Missing/Empty${NC}: $FAILURES"

if [ $FAILURES -gt 0 ]; then
    echo ""
    echo -e "${RED}⚠️  VALIDATION FAILED${NC}"
    echo "Fix: Create the missing files before claiming implementation is complete"
    exit 1
else
    echo ""
    echo -e "${GREEN}✅ ALL CHECKS PASSED${NC}"
    exit 0
fi
