#!/bin/bash
# Validate all Jupyter notebooks can execute
# Part of optional CI enhancements

set -e

echo "🔍 Validating Jupyter notebooks..."

# Find all notebooks
notebooks=$(find examples notebooks -name "*.ipynb" 2>/dev/null || echo "")

if [ -z "$notebooks" ]; then
    echo "✓ No notebooks found to validate"
    exit 0
fi

# Count notebooks
count=$(echo "$notebooks" | wc -l)
echo "Found $count notebook(s) to validate"

# Check if papermill is available
if ! command -v papermill &> /dev/null; then
    echo "⚠️  papermill not installed. Install with: pip install papermill"
    echo "ℹ️  Skipping notebook validation (optional check)"
    exit 0
fi

# Validate each notebook
failed=0
passed=0

for notebook in $notebooks; do
    echo ""
    echo "Validating: $notebook"
    
    # Create temp output file
    output_nb="/tmp/$(basename "$notebook" .ipynb)_output.ipynb"
    
    # Run notebook with papermill (timeout after 5 minutes)
    output_log=$(mktemp)
    timeout 300 papermill "$notebook" "$output_nb" \
        --log-output \
        --no-progress-bar \
        >"$output_log" 2>&1
    exit_code=$?
    head -50 "$output_log"
    rm -f "$output_log"
    
    if [ $exit_code -eq 0 ]; then
        echo "  ✓ Passed"
        ((passed++))
    else
        if [ $exit_code -eq 124 ]; then
            echo "  ⏱️  Timeout (5 minutes exceeded)"
        else
            echo "  ✗ Failed (exit code: $exit_code)"
        fi
        ((failed++))
    fi
    
    # Cleanup
    rm -f "$output_nb"
done

echo ""
echo "================================================"
echo "Notebook Validation Summary"
echo "================================================"
echo "Total notebooks: $count"
echo "Passed: $passed"
echo "Failed: $failed"
echo "================================================"

if [ $failed -gt 0 ]; then
    echo "❌ $failed notebook(s) failed validation"
    exit 1
else
    echo "✅ All notebooks validated successfully"
fi
