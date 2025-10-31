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

ENVIRONMENT_UPPER=$(echo "$ENVIRONMENT" | tr '[:lower:]' '[:upper:]')
PREFIX="ZENDESK_${ENVIRONMENT_UPPER}_"
SUBDOMAIN_VAR="${PREFIX}SUBDOMAIN"
EMAIL_VAR="${PREFIX}EMAIL"
TOKEN_VAR="${PREFIX}TOKEN"

info "Using environment: $ENVIRONMENT"

# Check for required environment variables
echo ""
info "Checking credentials for $ENVIRONMENT environment..."

MISSING_VARS=false

SUBDOMAIN_VALUE=${!SUBDOMAIN_VAR}
EMAIL_VALUE=${!EMAIL_VAR}
TOKEN_VALUE=${!TOKEN_VAR}

# Support legacy unscoped variables by copying them into the environment-specific ones
if [ -z "$SUBDOMAIN_VALUE" ] && [ -n "$ZENDESK_SUBDOMAIN" ]; then
    export "$SUBDOMAIN_VAR=$ZENDESK_SUBDOMAIN"
    SUBDOMAIN_VALUE=${!SUBDOMAIN_VAR}
    info "Imported $SUBDOMAIN_VAR from ZENDESK_SUBDOMAIN"
fi

if [ -z "$EMAIL_VALUE" ] && [ -n "$ZENDESK_EMAIL" ]; then
    export "$EMAIL_VAR=$ZENDESK_EMAIL"
    EMAIL_VALUE=${!EMAIL_VAR}
    info "Imported $EMAIL_VAR from ZENDESK_EMAIL"
fi

if [ -z "$TOKEN_VALUE" ] && [ -n "$ZENDESK_API_TOKEN" ]; then
    export "$TOKEN_VAR=$ZENDESK_API_TOKEN"
    TOKEN_VALUE=${!TOKEN_VAR}
    info "Imported $TOKEN_VAR from ZENDESK_API_TOKEN"
fi

if [ -z "$SUBDOMAIN_VALUE" ]; then
    warning "$SUBDOMAIN_VAR is not set"
    MISSING_VARS=true
fi

if [ -z "$EMAIL_VALUE" ]; then
    warning "$EMAIL_VAR is not set"
    MISSING_VARS=true
fi

if [ -z "$TOKEN_VALUE" ]; then
    warning "$TOKEN_VAR is not set"
    MISSING_VARS=true
fi

if [ "$MISSING_VARS" = true ]; then
    echo ""
    warning "Required environment variables are missing."
    echo "  Please set them in your environment or create a .env file:"
    echo ""
    echo "  export ${PREFIX}SUBDOMAIN=your-subdomain"
    echo "  export ${PREFIX}EMAIL=admin@example.com"
    echo "  export ${PREFIX}TOKEN=your-api-token"
    echo ""
    read -p "Do you want to configure them now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Zendesk Subdomain (${ENVIRONMENT}): " SUBDOMAIN_VALUE
        read -p "Zendesk Email (${ENVIRONMENT}): " EMAIL_VALUE
        read -sp "Zendesk API Token (${ENVIRONMENT}): " TOKEN_VALUE
        echo ""
        export "$SUBDOMAIN_VAR=$SUBDOMAIN_VALUE"
        export "$EMAIL_VAR=$EMAIL_VALUE"
        export "$TOKEN_VAR=$TOKEN_VALUE"
        success "Environment variables configured for $ENVIRONMENT"
    else
        error "Cannot proceed without credentials"
        exit 1
    fi
else
    success "Environment variables are set for $ENVIRONMENT"
fi

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
