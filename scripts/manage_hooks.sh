#!/usr/bin/env bash
# Pre-commit hook management utility
# Purpose: Disable/enable hooks for performance or debugging
# Usage: bash scripts/manage_hooks.sh <action>

set -euo pipefail

HOOKS_DIR=".git/hooks"
BACKUP_DIR=".git/hooks.backup"

log_info() { echo "ℹ️  $1"; }
log_pass() { echo "✅ $1"; }
log_warn() { echo "⚠️  $1"; }
log_fail() { echo "❌ $1"; return 1; }

disable_hooks() {
  log_info "Disabling pre-commit hooks..."
  
  if [[ ! -d "$HOOKS_DIR" ]]; then
    log_fail "Hooks directory not found: $HOOKS_DIR"
    return 1
  fi

  # Backup existing hooks
  if [[ -f "$HOOKS_DIR/pre-commit" ]]; then
    mkdir -p "$BACKUP_DIR"
    cp "$HOOKS_DIR/pre-commit" "$BACKUP_DIR/pre-commit.bak"
    log_pass "Backed up pre-commit hook"
  fi

  # Rename hook to disable
  if [[ -f "$HOOKS_DIR/pre-commit" ]]; then
    mv "$HOOKS_DIR/pre-commit" "$HOOKS_DIR/pre-commit.disabled"
    log_pass "Pre-commit hook disabled"
  fi

  if [[ -f "$HOOKS_DIR/prepare-commit-msg" ]]; then
    mv "$HOOKS_DIR/prepare-commit-msg" "$HOOKS_DIR/prepare-commit-msg.disabled"
    log_pass "Prepare-commit-msg hook disabled"
  fi
}

enable_hooks() {
  log_info "Enabling pre-commit hooks..."

  if [[ -f "$HOOKS_DIR/pre-commit.disabled" ]]; then
    mv "$HOOKS_DIR/pre-commit.disabled" "$HOOKS_DIR/pre-commit"
    log_pass "Pre-commit hook enabled"
  fi

  if [[ -f "$HOOKS_DIR/prepare-commit-msg.disabled" ]]; then
    mv "$HOOKS_DIR/prepare-commit-msg.disabled" "$HOOKS_DIR/prepare-commit-msg"
    log_pass "Prepare-commit-msg hook enabled"
  fi
}

status() {
  log_info "Checking hook status..."
  
  if [[ -f "$HOOKS_DIR/pre-commit" ]]; then
    log_pass "Pre-commit hook: ENABLED"
  elif [[ -f "$HOOKS_DIR/pre-commit.disabled" ]]; then
    log_warn "Pre-commit hook: DISABLED"
  else
    log_warn "Pre-commit hook: NOT FOUND"
  fi

  if [[ -f "$HOOKS_DIR/prepare-commit-msg" ]]; then
    log_pass "Prepare-commit-msg hook: ENABLED"
  elif [[ -f "$HOOKS_DIR/prepare-commit-msg.disabled" ]]; then
    log_warn "Prepare-commit-msg hook: DISABLED"
  else
    log_warn "Prepare-commit-msg hook: NOT FOUND"
  fi
}

# Main
action="${1:-status}"
case "$action" in
  disable)
    disable_hooks
    ;;
  enable)
    enable_hooks
    ;;
  status)
    status
    ;;
  *)
    echo "Usage: $0 {disable|enable|status}"
    exit 2
    ;;
esac
