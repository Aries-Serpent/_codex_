#!/bin/bash
# File: scripts/add_artifact_prefix.sh
# Purpose: Add Art_ prefix to all workflows producing downloadable artifacts
# Date: 2026-02-06

set -e -o pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Backup directory
BACKUP_DIR=".github/workflow-archive/backups/$(date +%Y-%m-%d-%H%M%S)-artifact-prefix"
mkdir -p "$BACKUP_DIR"

# Workflows requiring Art_ prefix
# Source: ARTIFACT_PREFIX_REQUIREMENTS.md + verification script findings
WORKFLOWS=(
  "agent-chain-orchestrator.yml"
  "artifact-monitoring.yml"
  "audit-improvement-pipeline.yml"
  "auth-compliance-report.yml"
  "auth-mfa-enrollment.yml"
  "auth-security-audit.yml"
  "auth-tests.yml"
  "batch-ci-triage.yml"
  "cache-suite.yml"
  "ci-diagnostic-automation.yml"
  "ci-health-suite.yml"
  "code-quality.yml"
  "codebase-qa-walkthrough.yml"
  "codeql-analysis.yml"
  "codeql-chunked.yml"
  "cognitive-action.yml"
  "cognitive-aftermath.yml"
  "cognitive-brain-feed.yml"
  "cognitive-decision.yml"
  "copilot-self-evolution.yml"
  "copilot-setup-steps.yml"
  "coverage_report.yml"
  "data_validation.yml"
  "decode-validate-artifact.yml"
  "determinism.yml"
  "documentation-link-checker.yml"
  "documentation-suite.yml"
  "docker-build-push.yml"
  "flatten-repo-download.yml"
  "generate-repository-structure.yml"
  "genesis-bootstrap.yml"
  "html_visual_baseline.yml"
  "html_visual_regression.yml"
  "notebooklm-sync.yml"
  "nox_gates.yml"
  "optimized-ci.yml"
  "phase34-codeql-alert-fetch.yml"
  "post-merge-validation-optimized.yml"
  "pre-release-deployment.yml"
  "publish_dashboard_release.yml"
  "pypi-publish.yml"
  "repo-organization.yml"
  "repository-health-monitoring.yml"
  "root-org-validation.yml"
  "rust_swarm_ci.yml"
  "sbom.yml"
  "scheduled-archival.yml"
  "scheduled-dependency-audit.yml"
  "security-scan.yml"
  "security-scanning-suite.yml"
  "security-suite.yml"
  "self-healing-ci.yml"
  "self-healing-feedback-loop.yml"
  "self-healing.yml"
  "semgrep_sarif.yml"
  "test-comprehensive.yml"
  "test-rag.yml"
  "test-suite.yml"
  "workflow-analytics-manual.yml"
  "workflow-analytics-scheduled.yml"
  "workflow-health-check.yml"
  "workflow-link-validation.yml"
  "zendesk-knowledge-sync.yml"
)

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}   Artifact Prefix Implementation Script${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "📋 Workflows to update: ${GREEN}${#WORKFLOWS[@]}${NC}"
echo -e "📦 Backup directory: ${YELLOW}$BACKUP_DIR${NC}"
echo ""

# Counters
UPDATED=0
SKIPPED_EXISTING=0
SKIPPED_NOTFOUND=0
ERRORS=0

# Process each workflow
for workflow in "${WORKFLOWS[@]}"; do
  WORKFLOW_PATH=".github/workflows/$workflow"

  # Check if file exists
  if [ ! -f "$WORKFLOW_PATH" ]; then
    echo -e "${YELLOW}⚠️  Skipping${NC} $workflow ${RED}(not found)${NC}"
    SKIPPED_NOTFOUND=$((SKIPPED_NOTFOUND + 1))
    continue
  fi

  # Check if already has prefix
  if grep -q "^name: Art_" "$WORKFLOW_PATH"; then
    echo -e "${YELLOW}⏭️  Skipping${NC} $workflow ${YELLOW}(already has prefix)${NC}"
    SKIPPED_EXISTING=$((SKIPPED_EXISTING + 1))
    continue
  fi

  # Backup original
  if ! cp "$WORKFLOW_PATH" "$BACKUP_DIR/$workflow"; then
    echo -e "${RED}❌ Error backing up${NC} $workflow"
    ERRORS=$((ERRORS + 1))
    continue
  fi

  # Add Art_ prefix to name field
  if sed -i 's/^name: \(.*\)/name: Art_\1/' "$WORKFLOW_PATH"; then
    echo -e "${GREEN}✅ Updated${NC} $workflow"
    UPDATED=$((UPDATED + 1))
  else
    echo -e "${RED}❌ Error updating${NC} $workflow"
    ERRORS=$((ERRORS + 1))
    # Restore from backup on error
    cp "$BACKUP_DIR/$workflow" "$WORKFLOW_PATH"
  fi
done

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 Complete!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "📊 Summary:"
echo -e "  ${GREEN}✅ Updated:${NC} $UPDATED workflows"
echo -e "  ${YELLOW}⏭️  Already had prefix:${NC} $SKIPPED_EXISTING workflows"
echo -e "  ${YELLOW}⚠️  Not found:${NC} $SKIPPED_NOTFOUND workflows"
if [ $ERRORS -gt 0 ]; then
  echo -e "  ${RED}❌ Errors:${NC} $ERRORS workflows"
fi
echo ""
echo -e "📦 Backups saved to: ${YELLOW}$BACKUP_DIR${NC}"
echo ""

# Show next steps
if [ $UPDATED -gt 0 ]; then
  echo -e "${BLUE}📝 Next steps:${NC}"
  echo -e "  1. Review changes: ${YELLOW}git diff .github/workflows/${NC}"
  echo -e "  2. Verify workflows: ${YELLOW}./scripts/verify_artifact_prefix.sh${NC}"
  echo -e "  3. Test workflows: ${YELLOW}gh workflow list${NC}"
  echo -e "  4. Commit changes: ${YELLOW}git add .github/workflows/ && git commit -m 'feat: Add Art_ prefix to artifact-producing workflows'${NC}"
  echo -e "  5. Push changes: ${YELLOW}git push${NC}"
  echo ""
fi

# Exit with error if any errors occurred
if [ $ERRORS -gt 0 ]; then
  exit 1
fi

exit 0
