#!/bin/bash
# Workflow Restoration Tool
# ========================
# Safely restore archived workflows from .github/workflow-archive/disabled/
#
# Usage:
#   ./restore_workflow.sh <workflow_name>                    # Restore single workflow
#   ./restore_workflow.sh --list                              # List all archived workflows
#   ./restore_workflow.sh --search <pattern>                  # Search for workflow
#   ./restore_workflow.sh --restore-category <category>      # Restore all in category
#   ./restore_workflow.sh --info <workflow_name>              # Show workflow info
#
# Examples:
#   ./restore_workflow.sh ci.yml
#   ./restore_workflow.sh --list
#   ./restore_workflow.sh --search security
#   ./restore_workflow.sh --restore-category testing
#   ./restore_workflow.sh --info codeql.yml

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
ARCHIVE_DIR="$REPO_ROOT/.github/workflow-archive/disabled"
WORKFLOWS_DIR="$REPO_ROOT/.github/workflows"
DRY_RUN=false
VERBOSE=false

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# Utility Functions
# ============================================================================

log_info() {
  echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
  echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
  echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
  echo -e "${RED}❌ $1${NC}"
}

# ============================================================================
# Archive Operations
# ============================================================================

list_workflows() {
  echo -e "${BLUE}Archived Workflows (in .github/workflow-archive/disabled/):${NC}\n"
  
  if [ ! -d "$ARCHIVE_DIR" ]; then
    log_error "Archive directory not found: $ARCHIVE_DIR"
    exit 1
  fi
  
  local count=0
  while IFS= read -r -d '' file; do
    if [[ "$file" == *.yml ]]; then
      local basename=$(basename "$file")
      local size=$(du -h "$file" | cut -f1)
      
      # Try to get workflow name from YAML
      local name=$(grep "^name:" "$file" 2>/dev/null | head -1 | sed 's/^name: *//' || echo "N/A")
      
      printf "  %-40s %6s  %s\n" "$basename" "$size" "$name"
      ((count++))
    fi
  done < <(find "$ARCHIVE_DIR" -maxdepth 1 -name "*.yml" -print0 | sort -z)
  
  echo ""
  log_info "Total archived workflows: $count"
}

search_workflows() {
  local pattern=$1
  echo -e "${BLUE}Searching for workflows matching: $pattern${NC}\n"
  
  local count=0
  while IFS= read -r -d '' file; do
    if grep -qi "$pattern" "$file" 2>/dev/null; then
      local basename=$(basename "$file")
      echo "  • $basename"
      ((count++))
    fi
  done < <(find "$ARCHIVE_DIR" -maxdepth 1 -name "*.yml" -print0)
  
  if [ $count -eq 0 ]; then
    log_warning "No workflows found matching: $pattern"
  else
    log_info "Found $count workflow(s) matching: $pattern"
  fi
}

show_workflow_info() {
  local workflow=$1
  local filepath="$ARCHIVE_DIR/$workflow"
  
  if [ ! -f "$filepath" ]; then
    log_error "Workflow not found: $workflow"
    echo ""
    search_workflows "$workflow"
    exit 1
  fi
  
  echo -e "${BLUE}Workflow Information: $workflow${NC}\n"
  
  # Extract metadata from YAML
  echo "Name:"
  grep "^name:" "$filepath" | head -1 | sed 's/^/  /'
  
  echo ""
  echo "Purpose (from comments):"
  grep -A2 "^# Purpose:" "$filepath" 2>/dev/null | sed 's/^#//' | sed 's/^/  /' || echo "  (No purpose documented)"
  
  echo ""
  echo "Triggers:"
  sed -n '/^on:/,/^[a-z]/p' "$filepath" 2>/dev/null | head -15 | sed 's/^/  /' || echo "  (Unable to parse triggers)"
  
  echo ""
  echo "File Stats:"
  local size=$(du -h "$filepath" | cut -f1)
  local modified=$(stat -c %y "$filepath" 2>/dev/null | cut -d' ' -f1,2 || stat -f %Sm -t "%Y-%m-%d %H:%M:%S" "$filepath" 2>/dev/null || echo "Unknown")
  echo "  Size: $size"
  echo "  Last Modified: $modified"
  
  echo ""
  echo "Metadata File:"
  if [ -f "$filepath.meta" ]; then
    echo "  ✅ Metadata exists:"
    cat "$filepath.meta" | sed 's/^/    /'
  else
    log_warning "No metadata file found: $workflow.meta"
  fi
}

# ============================================================================
# Restoration Functions
# ============================================================================

restore_single_workflow() {
  local workflow=$1
  local filepath="$ARCHIVE_DIR/$workflow"
  local target="$WORKFLOWS_DIR/$workflow"
  
  # Validate input
  if [ ! -f "$filepath" ]; then
    log_error "Workflow not found in archive: $workflow"
    echo ""
    echo "Did you mean one of these?"
    find "$ARCHIVE_DIR" -maxdepth 1 -name "*$(echo $workflow | cut -d. -f1)*" -type f 2>/dev/null | head -5 || true
    exit 1
  fi
  
  # Check for conflicts
  if [ -f "$target" ]; then
    log_warning "Workflow already exists in active directory: $target"
    read -p "Overwrite? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
      log_info "Restoration cancelled"
      exit 0
    fi
  fi
  
  # Perform restoration
  if [ "$DRY_RUN" = true ]; then
    log_info "[DRY RUN] Would restore: $workflow"
    log_info "[DRY RUN] From: $filepath"
    log_info "[DRY RUN] To:   $target"
  else
    cp "$filepath" "$target"
    log_success "Restored $workflow to .github/workflows/"
    
    echo ""
    log_warning "IMPORTANT POST-RESTORATION STEPS:"
    echo "  1. Review the workflow file:"
    echo "     cat $target"
    echo ""
    echo "  2. Check for hardcoded secrets or outdated patterns"
    echo ""
    echo "  3. Validate trigger conditions (paths, branches, events)"
    echo ""
    echo "  4. Test in staging before merging to main:"
    echo "     git checkout -b restore/$workflow"
    echo "     git add $target"
    echo "     git commit -m 'Restore archived workflow: $workflow'"
    echo ""
    echo "  5. Run workflow validation:"
    echo "     actionlint $target"
    echo ""
    echo "  6. Check for conflicts with similar active workflows"
    echo ""
    echo "  7. After verification, merge to main"
  fi
}

restore_category() {
  local category=$1
  local category_dir="$ARCHIVE_DIR/$category"
  
  if [ ! -d "$category_dir" ]; then
    log_error "Category directory not found: $category"
    echo ""
    log_info "Available categories:"
    ls -d "$ARCHIVE_DIR"/*/ 2>/dev/null | xargs -n1 basename || log_warning "No category directories found"
    exit 1
  fi
  
  echo -e "${BLUE}Restoring workflows from category: $category${NC}\n"
  
  local count=0
  while IFS= read -r -d '' file; do
    if [[ "$file" == *.yml ]]; then
      local basename=$(basename "$file")
      if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would restore: $basename"
      else
        cp "$file" "$WORKFLOWS_DIR/$basename"
        log_success "Restored: $basename"
      fi
      ((count++))
    fi
  done < <(find "$category_dir" -maxdepth 1 -name "*.yml" -print0 | sort -z)
  
  echo ""
  log_success "Restored $count workflow(s) from category: $category"
  log_warning "Don't forget to validate all restored workflows!"
}

# ============================================================================
# Main Command Router
# ============================================================================

main() {
  if [ $# -eq 0 ]; then
    show_help
    exit 0
  fi
  
  case "${1:-}" in
    --help|-h)
      show_help
      exit 0
      ;;
    --list|-l)
      list_workflows
      ;;
    --search|-s)
      if [ $# -lt 2 ]; then
        log_error "search requires a pattern"
        exit 1
      fi
      search_workflows "$2"
      ;;
    --info|-i)
      if [ $# -lt 2 ]; then
        log_error "info requires a workflow name"
        exit 1
      fi
      show_workflow_info "$2"
      ;;
    --restore-category|-c)
      if [ $# -lt 2 ]; then
        log_error "restore-category requires a category name"
        exit 1
      fi
      restore_category "$2"
      ;;
    --dry-run)
      DRY_RUN=true
      if [ $# -lt 2 ]; then
        show_help
        exit 0
      fi
      restore_single_workflow "$2"
      ;;
    *)
      # Assume it's a workflow name to restore
      restore_single_workflow "$1"
      ;;
  esac
}

show_help() {
  cat << 'EOF'
Workflow Restoration Tool
=========================

USAGE:
  restore_workflow.sh [COMMAND] [ARGS]

COMMANDS:
  <workflow_name>              Restore a single workflow
                               Example: restore_workflow.sh ci.yml

  --list, -l                   List all archived workflows
                               Example: restore_workflow.sh --list

  --search, -s <pattern>       Search for workflows by name or content
                               Example: restore_workflow.sh --search security

  --info, -i <workflow_name>   Show detailed information about a workflow
                               Example: restore_workflow.sh --info codeql.yml

  --restore-category, -c       Restore all workflows in a category
  <category>                   Example: restore_workflow.sh --restore-category testing

  --dry-run <workflow_name>    Preview what would be restored (no changes)
                               Example: restore_workflow.sh --dry-run ci.yml

  --help, -h                   Show this help message

ENVIRONMENT VARIABLES:
  REPO_ROOT                    Override repository root directory

EXAMPLES:

  # List all archived workflows
  ./restore_workflow.sh --list

  # Search for security-related workflows
  ./restore_workflow.sh --search security

  # Show info about a specific workflow
  ./restore_workflow.sh --info codeql.yml

  # Preview restoration (no changes)
  ./restore_workflow.sh --dry-run ci.yml

  # Actually restore a workflow
  ./restore_workflow.sh ci.yml

  # Restore all workflows in testing category
  ./restore_workflow.sh --restore-category testing

IMPORTANT:
  • Always review restored workflows before committing
  • Check for hardcoded secrets or outdated patterns
  • Validate trigger conditions
  • Test in staging first
  • Consider why the workflow was archived
  • Plan for consolidation if restoring long-term

RESTORATION CHECKLIST:
  ☐ Review workflow file for outdated patterns
  ☐ Check for hardcoded secrets or credentials
  ☐ Validate trigger conditions (paths, branches)
  ☐ Check for conflicts with active workflows
  ☐ Run actionlint for syntax validation
  ☐ Test in staging environment
  ☐ Update documentation if restoring
  ☐ Merge only after validation

DOCUMENTATION:
  See .codex/ARCHIVED_WORKFLOWS_CATALOG.md for detailed information
  about each archived workflow and restoration procedures.

EOF
}

# ============================================================================
# Run Main
# ============================================================================

main "$@"
