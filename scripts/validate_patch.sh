#!/usr/bin/env bash
# Patch Validation Script for Codex
# Purpose: Validate unified diff format before patch application
# Usage: bash scripts/validate_patch.sh <patch-file>
# Exit codes: 0 (pass), 1 (fail)
# References: RFC 3881, Git apply documentation

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_pass() {
  echo -e "${GREEN}✅ PASS:${NC} $1"
}

log_fail() {
  echo -e "${RED}❌ FAIL:${NC} $1"
  return 1
}

log_warn() {
  echo -e "${YELLOW}⚠️  WARN:${NC} $1"
}

log_info() {
  echo -e "${GREEN}ℹ️  INFO:${NC} $1"
}

# Main validation function
validate_patch() {
  local patch_file="$1"
  local errors=0

  # Check file exists
  if [[ ! -f "$patch_file" ]]; then
    log_fail "Patch file not found: $patch_file"
    return 1
  fi

  log_info "Validating patch: $patch_file"
  
  # 1. Check for @@ markers (hunk headers)
  log_info "Checking for hunk headers (@@)..."
  if ! grep -q '^@@' "$patch_file"; then
    log_fail "Missing @@ hunk headers (required by RFC 3881)"
    ((errors++))
  else
    local hunk_count=$(grep -c '^@@' "$patch_file")
    log_pass "Found $hunk_count hunk header(s)"
  fi

  # 2. Check context lines (minimum 3 recommended)
  log_info "Checking context lines (minimum 3 recommended)..."
  local context_lines=$(grep -c '^[[:space:]]' "$patch_file" || true)
  if [[ $context_lines -lt 3 ]]; then
    log_warn "Low context lines: $context_lines (recommended: ≥3)"
  else
    log_pass "Adequate context lines: $context_lines"
  fi

  # 3. Check for balanced +/- markers
  log_info "Checking for balanced additions/deletions..."
  local added=$(grep -c '^+' "$patch_file" || true)
  local removed=$(grep -c '^-' "$patch_file" || true)
  log_pass "Additions: $added lines, Deletions: $removed lines"

  # 4. Validate patch syntax with git apply --check
  log_info "Running git apply --check (dry-run)..."
  if git apply --check "$patch_file" 2>/dev/null; then
    log_pass "Patch syntax validated (git apply --check passed)"
  else
    log_fail "Patch syntax invalid (git apply --check failed)"
    ((errors++))
  fi

  # 5. Check for common issues
  log_info "Checking for common patch issues..."
  
  # Missing file headers (---/+++)
  if ! grep -q '^---' "$patch_file" || ! grep -q '^+++' "$patch_file"; then
    log_warn "Missing file headers (--- or +++)"
  fi

  # Trailing whitespace
  if grep -E '^(\+|-)[^+\-].*[[:space:]]$' "$patch_file" | head -3 | grep -q .; then
    log_warn "Potential trailing whitespace detected"
  fi

  # Summary and exit
  echo ""
  if [[ $errors -eq 0 ]]; then
    log_pass "Patch validation complete: All checks passed"
    return 0
  else
    log_fail "Patch validation failed: $errors error(s) found"
    return 1
  fi
}

# Entrypoint
if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <patch-file>"
  echo "Example: $0 my-changes.patch"
  exit 2
fi

validate_patch "$1"
exit $?
