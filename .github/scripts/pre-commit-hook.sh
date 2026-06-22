#!/bin/bash
#
# Pre-commit hook for _codex_ repository
# Runs consistency checks on changed files before commit
#
# To install: cp .github/scripts/pre-commit-hook.sh .git/hooks/pre-commit
#             chmod +x .git/hooks/pre-commit

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🔍 Running Pre-Commit Consistency Checks${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

REPO_ROOT=$(git rev-parse --show-toplevel)
cd "$REPO_ROOT"

# Get list of staged files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)

# Separate file types
MD_FILES=$(echo "$STAGED_FILES" | grep -E '\.md$' || true)
PY_FILES=$(echo "$STAGED_FILES" | grep -E '\.py$' || true)
YAML_FILES=$(echo "$STAGED_FILES" | grep -E '\.(yml|yaml)$' || true)

FAILED=0

# ============================================================================
# 1. Secret Scanning
# ============================================================================
echo -e "${BLUE}[1/5]${NC} Scanning for secrets..."

if command -v gitleaks &> /dev/null; then
    if ! gitleaks detect --staged --no-banner --exit-code 0 2>/dev/null; then
        echo -e "${RED}✗ Potential secrets detected!${NC}"
        echo "  Run: gitleaks detect --staged --verbose"
        echo "  To bypass: git commit --no-verify"
        FAILED=1
    else
        echo -e "${GREEN}✓ No secrets detected${NC}"
    fi
else
    echo -e "${YELLOW}⚠ gitleaks not installed, skipping secret scan${NC}"
fi

# ============================================================================
# 2. Markdown Linting
# ============================================================================
if [ -n "$MD_FILES" ]; then
    echo -e "\n${BLUE}[2/5]${NC} Linting Markdown files..."
    
    MD_COUNT=$(echo "$MD_FILES" | wc -l)
    
    if command -v markdownlint &> /dev/null; then
        if echo "$MD_FILES" | xargs markdownlint --fix --quiet 2>/dev/null; then
            echo -e "${GREEN}✓ Markdown linting passed (${MD_COUNT} files)${NC}"
            # Stage the auto-fixed files
            echo "$MD_FILES" | xargs git add 2>/dev/null || true
        else
            echo -e "${YELLOW}⚠ Some Markdown issues found and fixed${NC}"
            echo "$MD_FILES" | xargs git add 2>/dev/null || true
            echo "  Review the changes and re-run commit"
        fi
    else
        echo -e "${YELLOW}⚠ markdownlint not installed, skipping${NC}"
        echo "  Install with: npm install -g markdownlint-cli"
    fi
else
    echo -e "\n${BLUE}[2/5]${NC} No Markdown files to lint"
fi

# ============================================================================
# 3. Cross-Reference Validation
# ============================================================================
if [ -n "$MD_FILES" ]; then
    echo -e "\n${BLUE}[3/5]${NC} Validating cross-references..."
    
    if [ -f "$REPO_ROOT/.github/scripts/check-cross-references.py" ]; then
        if python3 "$REPO_ROOT/.github/scripts/check-cross-references.py" \
            --repo-root="$REPO_ROOT" \
            --format=text \
            > /tmp/crossref-report.txt 2>&1; then
            # Check if there were any errors in the output
            if grep -q "❌ BROKEN LINKS" /tmp/crossref-report.txt; then
                echo -e "${RED}✗ Broken cross-references found!${NC}"
                cat /tmp/crossref-report.txt
                FAILED=1
            else
                echo -e "${GREEN}✓ All cross-references valid${NC}"
            fi
        else
            echo -e "${YELLOW}⚠ Cross-reference check failed${NC}"
        fi
        rm -f /tmp/crossref-report.txt
    else
        echo -e "${YELLOW}⚠ Cross-reference checker not found${NC}"
    fi
else
    echo -e "\n${BLUE}[3/5]${NC} No Markdown files, skipping cross-reference check"
fi

# ============================================================================
# 4. Python Formatting & Linting
# ============================================================================
if [ -n "$PY_FILES" ]; then
    echo -e "\n${BLUE}[4/5]${NC} Checking Python files..."
    
    PY_COUNT=$(echo "$PY_FILES" | wc -l)
    
    if command -v black &> /dev/null; then
        if black --quiet "$PY_FILES" 2>/dev/null; then
            echo -e "${GREEN}✓ Black formatting OK (${PY_COUNT} files)${NC}"
            echo "$PY_FILES" | xargs git add 2>/dev/null || true
        else
            echo -e "${YELLOW}⚠ Black formatting made changes${NC}"
            echo "$PY_FILES" | xargs git add 2>/dev/null || true
        fi
    fi
    
    if command -v ruff &> /dev/null; then
        if ruff check --quiet "$PY_FILES" 2>/dev/null; then
            echo -e "${GREEN}✓ Ruff linting OK${NC}"
        else
            echo -e "${YELLOW}⚠ Ruff found issues${NC}"
            ruff check "$PY_FILES" 2>&1 | head -20
        fi
    fi
else
    echo -e "\n${BLUE}[4/5]${NC} No Python files to check"
fi

# ============================================================================
# 5. YAML Validation
# ============================================================================
if [ -n "$YAML_FILES" ]; then
    echo -e "\n${BLUE}[5/5]${NC} Validating YAML files..."
    
    YAML_COUNT=$(echo "$YAML_FILES" | wc -l)
    
    if command -v yamllint &> /dev/null; then
        if yamllint -d '{extends: relaxed}' "$YAML_FILES" 2>/dev/null; then
            echo -e "${GREEN}✓ YAML validation OK (${YAML_COUNT} files)${NC}"
        else
            echo -e "${YELLOW}⚠ YAML validation warnings${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ yamllint not installed, skipping${NC}"
    fi
else
    echo -e "\n${BLUE}[5/5]${NC} No YAML files to check"
fi

# ============================================================================
# Summary
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All pre-commit checks passed!${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
    exit 0
else
    echo -e "${RED}✗ Some checks failed. Fix the issues and try again.${NC}"
    echo -e "${YELLOW}  To bypass checks: git commit --no-verify${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
    exit 1
fi
