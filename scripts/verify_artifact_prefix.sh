#!/bin/bash
# File: scripts/verify_artifact_prefix.sh
# Purpose: Verify all artifact-producing workflows have Art_ prefix
# Date: 2026-02-06

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}   Artifact Prefix Verification${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Find all workflows with upload-artifact
ARTIFACT_WORKFLOWS=$(grep -l "actions/upload-artifact" .github/workflows/*.yml 2>/dev/null || true)

if [ -z "$ARTIFACT_WORKFLOWS" ]; then
  echo -e "${YELLOW}⚠️  No workflows found with upload-artifact${NC}"
  exit 0
fi

TOTAL=$(echo "$ARTIFACT_WORKFLOWS" | wc -l)
MISSING=0
VALID=0

echo -e "🔍 Checking ${BLUE}$TOTAL${NC} artifact-producing workflows..."
echo ""

# Check each workflow
while IFS= read -r workflow; do
  BASENAME=$(basename "$workflow")
  
  if ! grep -q "^name: Art_" "$workflow"; then
    echo -e "${RED}❌ Missing prefix:${NC} $BASENAME"
    ((MISSING++))
  else
    echo -e "${GREEN}✅ Has prefix:${NC} $BASENAME"
    ((VALID++))
  fi
done <<< "$ARTIFACT_WORKFLOWS"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ $MISSING -eq 0 ]; then
  echo -e "${GREEN}✅ SUCCESS: All $TOTAL artifact-producing workflows have Art_ prefix!${NC}"
  echo ""
  exit 0
else
  echo -e "${RED}⚠️  INCOMPLETE: $MISSING of $TOTAL workflows missing Art_ prefix${NC}"
  echo -e "${GREEN}   Valid:${NC} $VALID workflows"
  echo ""
  echo -e "${YELLOW}Run the following to fix:${NC}"
  echo -e "  ${BLUE}./scripts/add_artifact_prefix.sh${NC}"
  echo ""
  exit 1
fi
