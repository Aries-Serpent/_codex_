#!/usr/bin/env bash
# Zendesk Quick Start Script
# This script helps you get started with Zendesk configuration management using _codex_

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions for colored output
info() {
    echo -e "${BLUE}ℹ ${NC}$1"
}

success() {
    echo -e "${GREEN}✓${NC} $1"
}

warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1"
}

# Print header
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   Zendesk Configuration Management - Quick Start${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# Check prerequisites
info "Checking prerequisites..."

# Check if _codex_ is installed
if ! command -v codex &> /dev/null; then
    error "_codex_ is not installed or not in PATH"
    echo "  Please install _codex_ first:"
    echo "  pip install -e ."
    exit 1
fi
success "_codex_ is installed"

# Check for required environment variables
MISSING_VARS=false

if [ -z "$ZENDESK_SUBDOMAIN" ]; then
    warning "ZENDESK_SUBDOMAIN is not set"
    MISSING_VARS=true
fi

if [ -z "$ZENDESK_EMAIL" ]; then
    warning "ZENDESK_EMAIL is not set"
    MISSING_VARS=true
fi

if [ -z "$ZENDESK_API_TOKEN" ]; then
    warning "ZENDESK_API_TOKEN is not set"
    MISSING_VARS=true
fi

if [ "$MISSING_VARS" = true ]; then
    echo ""
    warning "Required environment variables are missing."
    echo "  Please set them in your environment or create a .env file:"
    echo ""
    echo "  export ZENDESK_SUBDOMAIN=your-subdomain"
    echo "  export ZENDESK_EMAIL=admin@example.com"
    echo "  export ZENDESK_API_TOKEN=your-api-token"
    echo ""
    read -p "Do you want to configure them now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Zendesk Subdomain: " ZENDESK_SUBDOMAIN
        read -p "Zendesk Email: " ZENDESK_EMAIL
        read -sp "Zendesk API Token: " ZENDESK_API_TOKEN
        echo ""
        export ZENDESK_SUBDOMAIN
        export ZENDESK_EMAIL
        export ZENDESK_API_TOKEN
        success "Environment variables configured"
    else
        error "Cannot proceed without credentials"
        exit 1
    fi
else
    success "Environment variables are set"
fi

# Select environment
echo ""
info "Select Zendesk environment:"
echo "  1) dev"
echo "  2) staging"
echo "  3) prod"
read -p "Environment (1-3, default: 1): " ENV_CHOICE

case $ENV_CHOICE in
    2) ENVIRONMENT="staging" ;;
    3) ENVIRONMENT="prod" ;;
    *) ENVIRONMENT="dev" ;;
esac

info "Using environment: $ENVIRONMENT"

# Create directory structure
echo ""
info "Creating directory structure..."

mkdir -p "configs/desired/zendesk"
mkdir -p "snapshot/$ENVIRONMENT"
mkdir -p "diffs"
mkdir -p "plans"
mkdir -p ".codex/logs"

success "Directories created"

# Test API connectivity
echo ""
info "Testing Zendesk API connectivity..."

if codex zendesk snapshot --env="$ENVIRONMENT" --dry-run 2>/dev/null; then
    success "API connectivity verified"
else
    error "Failed to connect to Zendesk API"
    echo "  Please check your credentials and try again"
    exit 1
fi

# Take first snapshot
echo ""
info "Taking initial snapshot of Zendesk configuration..."

if codex zendesk snapshot --env="$ENVIRONMENT"; then
    success "Snapshot complete: snapshot/$ENVIRONMENT/latest/"
else
    error "Snapshot failed"
    exit 1
fi

# Display snapshot contents
echo ""
info "Snapshot contents:"
ls -lh "snapshot/$ENVIRONMENT/latest/" 2>/dev/null | tail -n +2 | while read line; do
    echo "  $line"
done || echo "  (no files yet)"

# Offer to create sample desired state
echo ""
read -p "Create sample desired state files? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    info "Creating sample configurations..."
    
    # Create sample trigger
    cat > "configs/desired/zendesk/triggers.sample.json" <<EOF
{
  "triggers": [
    {
      "title": "Auto-assign high priority tickets",
      "active": true,
      "position": 1,
      "conditions": {
        "all": [
          {
            "field": "status",
            "operator": "is",
            "value": "new"
          },
          {
            "field": "priority",
            "operator": "is",
            "value": "high"
          }
        ]
      },
      "actions": [
        {
          "field": "status",
          "value": "open"
        }
      ],
      "description": "Automatically opens high priority tickets"
    }
  ]
}
EOF
    success "Created configs/desired/zendesk/triggers.sample.json"
    
    # Create sample macro
    cat > "configs/desired/zendesk/macros.sample.json" <<EOF
{
  "macros": [
    {
      "title": "Resolved - Thank you",
      "active": true,
      "actions": [
        {
          "field": "status",
          "value": "solved"
        },
        {
          "field": "comment_value",
          "value": "Thank you for contacting support. This issue has been resolved."
        },
        {
          "field": "comment_mode_is_public",
          "value": true
        }
      ],
      "description": "Standard resolution macro"
    }
  ]
}
EOF
    success "Created configs/desired/zendesk/macros.sample.json"
fi

# Show next steps
echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}   Setup Complete!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Next steps:"
echo ""
echo "1. Review your snapshot:"
echo "   ls -la snapshot/$ENVIRONMENT/latest/"
echo ""
echo "2. Edit desired state files:"
echo "   vim configs/desired/zendesk/triggers.json"
echo ""
echo "3. Generate diff to see changes:"
echo "   codex zendesk diff triggers \\"
echo "     --desired-file configs/desired/zendesk/triggers.json \\"
echo "     --current-file snapshot/$ENVIRONMENT/latest/triggers.json \\"
echo "     --output diffs/triggers_diff.json"
echo ""
echo "4. Create a plan:"
echo "   codex zendesk plan triggers \\"
echo "     --diff-file diffs/triggers_diff.json \\"
echo "     --output plans/triggers_plan.json"
echo ""
echo "5. Apply changes (dry run first!):"
echo "   codex zendesk apply triggers plans/triggers_plan.json \\"
echo "     --env=$ENVIRONMENT --dry-run"
echo ""
echo "6. Apply for real:"
echo "   codex zendesk apply triggers plans/triggers_plan.json \\"
echo "     --env=$ENVIRONMENT"
echo ""
echo "7. Monitor metrics:"
echo "   codex zendesk metrics"
echo ""
echo -e "${BLUE}Documentation:${NC}"
echo "  • Newcomer Guide: docs/zendesk/ZENDESK_NEWCOMER_GUIDE.md"
echo "  • Workflow Diagrams: docs/zendesk/WORKFLOW_DIAGRAMS.md"
echo "  • AI Agent App Builder: docs/zendesk/AI_AGENT_APP_BUILDER.md"
echo "  • Admin Runbook: docs/runbooks/zendesk_admin_workflow.md"
echo ""
echo -e "${GREEN}Happy automating! 🎫${NC}"
