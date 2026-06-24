#!/bin/bash
#
# Installation script for consistency checks
# Sets up pre-commit hooks and required tools for the _codex_ repository
#

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Consistency Checks Setup for _codex_${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}\n"

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || REPO_ROOT="."

# ============================================================================
# Check prerequisites
# ============================================================================
echo -e "${BLUE}[1/4]${NC} Checking prerequisites...\n"

MISSING_TOOLS=()

if ! command -v python3 &> /dev/null; then
    MISSING_TOOLS+=("python3")
fi

if ! command -v git &> /dev/null; then
    MISSING_TOOLS+=("git")
fi

if [ ${#MISSING_TOOLS[@]} -gt 0 ]; then
    echo -e "${RED}✗ Missing required tools: ${MISSING_TOOLS[*]}${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python 3 found${NC}"
echo -e "${GREEN}✓ Git found${NC}"

# Optional tools
OPTIONAL_TOOLS=()

if ! command -v npm &> /dev/null; then
    OPTIONAL_TOOLS+=("npm (markdownlint)")
else
    echo -e "${GREEN}✓ npm found${NC}"
fi

if ! command -v markdownlint &> /dev/null; then
    if command -v npm &> /dev/null; then
        OPTIONAL_TOOLS+=("markdownlint-cli")
    fi
else
    echo -e "${GREEN}✓ markdownlint found${NC}"
fi

if ! command -v yamllint &> /dev/null; then
    OPTIONAL_TOOLS+=("yamllint")
else
    echo -e "${GREEN}✓ yamllint found${NC}"
fi

if ! command -v gitleaks &> /dev/null; then
    echo -e "${YELLOW}⚠ gitleaks not installed (secret scanning disabled)${NC}"
else
    echo -e "${GREEN}✓ gitleaks found${NC}"
fi

# ============================================================================
# Install optional tools
# ============================================================================
if [ ${#OPTIONAL_TOOLS[@]} -gt 0 ]; then
    echo -e "\n${BLUE}[2/4]${NC} Installing optional tools...\n"

    echo -e "${YELLOW}The following optional tools are missing:${NC}"
    for tool in "${OPTIONAL_TOOLS[@]}"; do
        echo "  • $tool"
    done

    read -p "Would you like to install them? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if command -v npm &> /dev/null; then
            if [[ "${OPTIONAL_TOOLS[*]}" == *"markdownlint-cli"* ]]; then
                echo -e "${BLUE}Installing markdownlint-cli...${NC}"
                npm install -g markdownlint-cli
            fi
        fi

        if [[ "${OPTIONAL_TOOLS[*]}" == *"yamllint"* ]]; then
            echo -e "${BLUE}Installing yamllint...${NC}"
            if command -v brew &> /dev/null; then
                brew install yamllint
            elif command -v apt-get &> /dev/null; then
                sudo apt-get update && sudo apt-get install -y yamllint
            else
                echo -e "${YELLOW}⚠ Please install yamllint manually${NC}"
            fi
        fi
    else
        echo -e "${YELLOW}Skipping optional tool installation${NC}"
        echo -e "${YELLOW}Some pre-commit checks will be disabled${NC}"
    fi
else
    echo -e "\n${BLUE}[2/4]${NC} All optional tools installed${NC}"
fi

# ============================================================================
# Install pre-commit hook
# ============================================================================
echo -e "\n${BLUE}[3/4]${NC} Installing pre-commit hook...\n"

HOOKS_DIR="$REPO_ROOT/.git/hooks"
HOOK_SRC="$REPO_ROOT/.github/scripts/pre-commit-hook.sh"
HOOK_DEST="$HOOKS_DIR/pre-commit"

if [ ! -d "$HOOKS_DIR" ]; then
    echo -e "${RED}✗ Git hooks directory not found: $HOOKS_DIR${NC}"
    exit 1
fi

if [ ! -f "$HOOK_SRC" ]; then
    echo -e "${RED}✗ Hook source not found: $HOOK_SRC${NC}"
    exit 1
fi

# Backup existing hook if present
if [ -f "$HOOK_DEST" ] && [ ! -L "$HOOK_DEST" ]; then
    echo -e "${YELLOW}⚠ Existing pre-commit hook found, backing up...${NC}"
    cp "$HOOK_DEST" "$HOOK_DEST.bak"
fi

# Install hook
cp "$HOOK_SRC" "$HOOK_DEST"
chmod +x "$HOOK_DEST"

if [ -x "$HOOK_DEST" ]; then
    echo -e "${GREEN}✓ Pre-commit hook installed to: $HOOK_DEST${NC}"
else
    echo -e "${RED}✗ Failed to make hook executable${NC}"
    exit 1
fi

# ============================================================================
# Install Python dependencies
# ============================================================================
echo -e "\n${BLUE}[4/4]${NC} Checking Python dependencies...\n"

PYTHON_DEPS="pathlib"  # Built-in modules, no installation needed
echo -e "${GREEN}✓ All Python dependencies available (built-in)${NC}"

# ============================================================================
# Verify installation
# ============================================================================
echo -e "\n${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Verification${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}\n"

if [ -x "$HOOK_DEST" ]; then
    echo -e "${GREEN}✓ Pre-commit hook is installed and executable${NC}"
else
    echo -e "${RED}✗ Pre-commit hook is not executable${NC}"
fi

if [ -f "$REPO_ROOT/.markdownlintrc" ]; then
    echo -e "${GREEN}✓ Markdownlint configuration found${NC}"
else
    echo -e "${RED}✗ Markdownlint configuration not found${NC}"
fi

if [ -f "$REPO_ROOT/.github/scripts/check-cross-references.py" ]; then
    echo -e "${GREEN}✓ Cross-reference checker found${NC}"
else
    echo -e "${RED}✗ Cross-reference checker not found${NC}"
fi

if [ -f "$REPO_ROOT/.github/workflows/consistency-checks.yml" ]; then
    echo -e "${GREEN}✓ GitHub Actions workflow found${NC}"
else
    echo -e "${RED}✗ GitHub Actions workflow not found${NC}"
fi

# ============================================================================
# Summary
# ============================================================================
echo -e "\n${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Setup Complete!${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}\n"

echo -e "Next steps:"
echo -e "  1. Make your changes and commit:"
echo -e "     ${BLUE}git add .${NC}"
echo -e "     ${BLUE}git commit -m 'docs: update documentation'${NC}"
echo -e ""
echo -e "  2. The pre-commit hook will run automatically"
echo -e ""
echo -e "  3. For more information, see:"
echo -e "     ${BLUE}docs/CONSISTENCY_CHECKS_SETUP.md${NC}"
echo -e ""
echo -e "  4. To run checks manually:"
echo -e "     ${BLUE}python3 .github/scripts/check-cross-references.py${NC}"
echo -e "     ${BLUE}markdownlint --fix docs/**/*.md${NC}"
echo -e ""

echo -e "${GREEN}✓ Consistency checks setup complete!${NC}\n"
