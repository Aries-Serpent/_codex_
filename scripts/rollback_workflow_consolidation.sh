#!/bin/bash
# Workflow Consolidation Rollback Script
# Purpose: Quickly rollback workflow consolidation if issues are discovered
# Usage: ./scripts/rollback_workflow_consolidation.sh [--dry-run] [--phase1|--phase2|--all]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
WORKFLOWS_DIR="$REPO_ROOT/.github/workflows"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default options
DRY_RUN=false
PHASE="all"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --phase1)
      PHASE="phase1"
      shift
      ;;
    --phase2)
      PHASE="phase2"
      shift
      ;;
    --all)
      PHASE="all"
      shift
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--dry-run] [--phase1|--phase2|--all]"
      exit 1
      ;;
  esac
done

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Workflow Consolidation Rollback Script${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""
echo "Repository: $REPO_ROOT"
echo "Dry run: $DRY_RUN"
echo "Phase: $PHASE"
echo ""

if [ "$DRY_RUN" = true ]; then
  echo -e "${YELLOW}⚠️  DRY RUN MODE - No actual changes will be made${NC}"
  echo ""
fi

# Function to enable old workflow
enable_workflow() {
  local workflow=$1
  local disabled_file="$WORKFLOWS_DIR/$workflow.disabled"
  local enabled_file="$WORKFLOWS_DIR/$workflow"
  
  if [ -f "$disabled_file" ]; then
    echo -e "${GREEN}✅ Re-enabling: $workflow${NC}"
    if [ "$DRY_RUN" = false ]; then
      mv "$disabled_file" "$enabled_file"
    fi
    return 0
  else
    echo -e "${YELLOW}⚠️  Not found: $workflow.disabled${NC}"
    return 1
  fi
}

# Function to disable new workflow
disable_workflow() {
  local workflow=$1
  local enabled_file="$WORKFLOWS_DIR/$workflow"
  local disabled_file="$WORKFLOWS_DIR/$workflow.disabled"
  
  if [ -f "$enabled_file" ]; then
    echo -e "${RED}🔴 Disabling: $workflow${NC}"
    if [ "$DRY_RUN" = false ]; then
      mv "$enabled_file" "$disabled_file"
    fi
    return 0
  else
    echo -e "${YELLOW}⚠️  Not found: $workflow${NC}"
    return 1
  fi
}

# Phase 1: Test workflows
if [ "$PHASE" = "phase1" ] || [ "$PHASE" = "all" ]; then
  echo -e "${YELLOW}Phase 1: Rolling back test workflow consolidation${NC}"
  echo ""
  
  # Disable new consolidated workflow
  disable_workflow "test-suite.yml"
  
  # Re-enable old test workflows
  enable_workflow "ci.yml"
  enable_workflow "ci-pytest.yml"
  enable_workflow "tests.yml"
  enable_workflow "ml-tests.yml"
  enable_workflow "comprehensive_tests.yml"
  enable_workflow "multi-python-ci.yml"
  
  echo ""
fi

# Phase 1: Security workflows
if [ "$PHASE" = "phase1" ] || [ "$PHASE" = "all" ]; then
  echo -e "${YELLOW}Phase 1: Rolling back security workflow consolidation${NC}"
  echo ""
  
  # Disable new consolidated workflow
  disable_workflow "security-suite.yml"
  
  # Re-enable old security workflows
  enable_workflow "security.yml"
  enable_workflow "security-scanning.yml"
  enable_workflow "security_gates.yml"
  enable_workflow "security_policy_gate.yml"
  enable_workflow "secrets_baseline_check.yml"
  enable_workflow "semgrep_sarif.yml"
  
  echo ""
fi

# Phase 1: Audit workflows
if [ "$PHASE" = "phase1" ] || [ "$PHASE" = "all" ]; then
  echo -e "${YELLOW}Phase 1: Rolling back audit workflow consolidation${NC}"
  echo ""
  
  # Note: audit-improvement-pipeline.yml stays enabled
  echo "ℹ️  Keeping audit-improvement-pipeline.yml enabled (it's the primary audit workflow)"
  
  # Re-enable old audit workflows
  enable_workflow "audit_chain.yml"
  enable_workflow "capability-audit.yml"
  enable_workflow "nightly-audit.yml"
  enable_workflow "space-audit.yml"
  
  echo ""
fi

# Validation
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Rollback Summary${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""

active_count=$(find "$WORKFLOWS_DIR" -name "*.yml" ! -name "*.disabled" | wc -l)
disabled_count=$(find "$WORKFLOWS_DIR" -name "*.disabled" | wc -l)

echo "Active workflows: $active_count"
echo "Disabled workflows: $disabled_count"
echo ""

if [ "$DRY_RUN" = false ]; then
  echo -e "${GREEN}✅ Rollback completed successfully${NC}"
  echo ""
  echo "Next steps:"
  echo "1. Verify workflows are working: gh workflow list"
  echo "2. Monitor for any failures"
  echo "3. Update tracking documentation"
  echo "4. Consider what went wrong and plan next attempt"
else
  echo -e "${YELLOW}ℹ️  Dry run completed - no changes made${NC}"
  echo ""
  echo "To execute rollback, run without --dry-run:"
  echo "  $0 --phase1"
fi

echo ""
echo -e "${YELLOW}========================================${NC}"

exit 0
