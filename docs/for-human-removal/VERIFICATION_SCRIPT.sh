#!/bin/bash
# Verification script for files marked for removal
# Run this before deleting anything

set -e

echo "=============================================="
echo "VERIFICATION SCRIPT FOR REMOVAL CANDIDATES"
echo "=============================================="
echo ""

check_references() {
    local item=$1
    echo "Checking references to: $item"
    
    # Check Python files
    py_refs=$(grep -r "$item" --include="*.py" --exclude-dir=".git" --exclude-dir="docs/for-human-removal" . 2>/dev/null | wc -l)
    echo "  Python references: $py_refs"
    
    # Check scripts
    sh_refs=$(grep -r "$item" --include="*.sh" --exclude-dir=".git" --exclude-dir="docs/for-human-removal" . 2>/dev/null | wc -l)
    echo "  Script references: $sh_refs"
    
    # Check workflows
    wf_refs=$(grep -r "$item" .github/workflows/ 2>/dev/null | wc -l)
    echo "  Workflow references: $wf_refs"
    
    # Check docs
    doc_refs=$(grep -r "$item" --include="*.md" --exclude-dir=".git" --exclude-dir="docs/for-human-removal" . 2>/dev/null | wc -l)
    echo "  Documentation references: $doc_refs"
    
    total=$((py_refs + sh_refs + wf_refs + doc_refs))
    
    if [ $total -eq 0 ]; then
        echo "  ✅ SAFE TO REMOVE (no references found)"
    else
        echo "  ⚠️  HAS REFERENCES ($total total) - REVIEW BEFORE REMOVAL"
    fi
    echo ""
}

echo "1. Checking deprecated directories..."
echo "======================================="
check_references "conf/"
check_references "config_legacy"
check_references "yaml_legacy"

echo ""
echo "2. Checking duplicate files..."
echo "======================================="
check_references ".bandit.yml"
check_references "AGENTS.md.original"

echo ""
echo "3. Checking large files..."
echo "======================================="
echo "Checking .secrets.baseline usage..."
wf_usage=$(grep -r "secrets.baseline" .github/workflows/ 2>/dev/null | wc -l)
echo "  Workflow usage: $wf_usage"
if [ $wf_usage -gt 0 ]; then
    echo "  ⚠️  USED IN WORKFLOWS - Do NOT remove"
    grep -r "secrets.baseline" .github/workflows/ 2>/dev/null
else
    echo "  ✅ Not used in workflows"
fi

echo ""
echo "4. Checking temp directories..."
echo "======================================="
echo "Verifying temp directories in .gitignore..."
for dir in temp logs coverage_reports .reports; do
    if grep -q "^${dir}/" .gitignore 2>/dev/null; then
        echo "  ✅ $dir/ in .gitignore"
    else
        echo "  ⚠️  $dir/ NOT in .gitignore - should be added"
    fi
done

echo ""
echo "=============================================="
echo "VERIFICATION COMPLETE"
echo "=============================================="
echo ""
echo "Review the output above before proceeding with removal."
echo "Items marked ✅ are safe to remove."
echo "Items marked ⚠️  require additional review."
