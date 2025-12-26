#!/bin/bash
# Generated: 2025-12-26T08:25:00Z | Author: mbaetiong
# Genesis Rollback Script
# Safely rolls back Genesis setup in case of issues

set -e

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║              Genesis Protocol - Emergency Rollback               ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running in Genesis directory
if [ ! -f ".codex/autonomous_agent.yaml" ]; then
    echo -e "${RED}❌ Error: Not in repository root directory${NC}"
    echo "Please run this script from the repository root."
    exit 1
fi

echo -e "${YELLOW}⚠️  WARNING: This will rollback Genesis setup${NC}"
echo ""
echo "This script will:"
echo "  1. Disable autonomous actions"
echo "  2. Enable SAFE_MODE in agent script"
echo "  3. Disable Genesis bootstrap workflow"
echo "  4. Create rollback record in change log"
echo ""
read -p "Are you sure you want to proceed? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Rollback cancelled."
    exit 0
fi

echo ""
echo "🔄 Starting rollback..."
echo ""

# Step 1: Disable autonomous actions
echo "📝 Step 1: Disabling autonomous actions..."
if [ -f ".codex/autonomous_agent.yaml" ]; then
    sed -i 's/autonomous_actions_enabled: true/autonomous_actions_enabled: false/' .codex/autonomous_agent.yaml
    echo -e "${GREEN}✅ Autonomous actions disabled${NC}"
else
    echo -e "${YELLOW}⚠️  autonomous_agent.yaml not found${NC}"
fi

# Step 2: Enable SAFE_MODE
echo ""
echo "📝 Step 2: Enabling SAFE_MODE..."
if [ -f "scripts/autonomous_agent.py" ]; then
    sed -i 's/SAFE_MODE = False/SAFE_MODE = True/' scripts/autonomous_agent.py
    echo -e "${GREEN}✅ SAFE_MODE enabled${NC}"
else
    echo -e "${YELLOW}⚠️  autonomous_agent.py not found${NC}"
fi

# Step 3: Disable Genesis bootstrap workflow
echo ""
echo "📝 Step 3: Disabling Genesis bootstrap workflow..."
if [ -f ".github/workflows/genesis-bootstrap.yml" ]; then
    # Add if: false guard if not already present
    if ! grep -q "if: false" .github/workflows/genesis-bootstrap.yml; then
        # Find the validate-genesis job and add the guard
        sed -i '/validate-genesis:/a\    if: false # Disabled by rollback script' .github/workflows/genesis-bootstrap.yml
        echo -e "${GREEN}✅ Genesis bootstrap workflow disabled${NC}"
    else
        echo -e "${GREEN}✅ Genesis bootstrap workflow already disabled${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  genesis-bootstrap.yml not found${NC}"
fi

# Step 4: Create rollback record
echo ""
echo "📝 Step 4: Creating rollback record..."
ROLLBACK_ENTRY="
## Genesis Protocol Rollback - $(date -u +"%Y-%m-%dT%H:%M:%SZ")

**Reason**: Emergency rollback initiated by human admin
**Actions taken**:
- Disabled autonomous_actions_enabled in autonomous_agent.yaml
- Enabled SAFE_MODE in autonomous_agent.py
- Disabled genesis-bootstrap workflow
- Agent operations suspended until further review

**Next steps**:
1. Review system logs and identify root cause
2. Document issues in GitHub issue
3. Plan corrective actions
4. Test fixes in isolated environment
5. Re-enable after validation
"

if [ -f ".codex/change_log.md" ]; then
    # Create temporary file with rollback entry
    echo "$ROLLBACK_ENTRY" | cat - .codex/change_log.md > /tmp/change_log_temp.md
    mv /tmp/change_log_temp.md .codex/change_log.md
    echo -e "${GREEN}✅ Rollback record created${NC}"
else
    echo -e "${YELLOW}⚠️  change_log.md not found, creating new one${NC}"
    echo "# Change Log" > .codex/change_log.md
    echo "$ROLLBACK_ENTRY" >> .codex/change_log.md
fi

# Step 5: Git commit
echo ""
echo "📝 Step 5: Committing changes..."
git add .codex/autonomous_agent.yaml scripts/autonomous_agent.py .github/workflows/genesis-bootstrap.yml .codex/change_log.md
git commit -m "chore(genesis): emergency rollback - disable autonomous operations

Rollback performed: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
- autonomous_actions_enabled: false
- SAFE_MODE: True  
- genesis-bootstrap workflow: disabled
- Record added to change_log.md

Reason: Emergency rollback by human admin" || echo -e "${YELLOW}⚠️  No changes to commit${NC}"

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║                   ✅ Rollback Complete                          ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
echo "Summary:"
echo "  • Autonomous actions: DISABLED"
echo "  • SAFE_MODE: ENABLED"
echo "  • Genesis workflow: DISABLED"
echo "  • Change log: UPDATED"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Review .codex/change_log.md for rollback record"
echo "  2. Create GitHub issue documenting the problem"
echo "  3. Investigate root cause in logs and artifacts"
echo "  4. Plan and test fixes before re-enabling"
echo "  5. Push changes: git push origin <branch>"
echo ""
echo -e "${GREEN}Safe mode restored. Agent operations suspended.${NC}"
