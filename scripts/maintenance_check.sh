#!/bin/bash
# Automated dependency update checker and maintenance script
# Run monthly or as needed

set -e

echo "========================================="
echo "Codex ML - Dependency Maintenance Check"
echo "========================================="
echo "Date: $(date)"
echo ""

# Check if we're in the repo root
if [ ! -f "pyproject.toml" ]; then
    echo "Error: Must run from repository root"
    exit 1
fi

# Create maintenance report directory
REPORT_DIR=".codex/reports/maintenance/$(date +%Y-%m)"
mkdir -p "$REPORT_DIR"
REPORT_FILE="$REPORT_DIR/dependency_check_$(date +%Y-%m-%d).txt"

echo "Report will be saved to: $REPORT_FILE"
echo ""

# Function to log to both console and file
log() {
    echo "$1" | tee -a "$REPORT_FILE"
}

log "========================================="
log "1. Checking for Outdated Dependencies"
log "========================================="
log ""

# Check outdated packages
if command -v pip &> /dev/null; then
    log "Outdated pip packages:"
    pip list --outdated | tee -a "$REPORT_FILE" || log "No outdated packages found"
else
    log "pip not found, skipping pip check"
fi

log ""
log "========================================="
log "2. Security Vulnerability Scan"
log "========================================="
log ""

# Install pip-audit if not available
if ! command -v pip-audit &> /dev/null; then
    log "Installing pip-audit..."
    pip install pip-audit
fi

# Run security audit
log "Running pip-audit..."
if pip-audit --skip-editable 2>&1 | tee -a "$REPORT_FILE"; then
    log "✅ No vulnerabilities found"
else
    log "⚠️  Vulnerabilities detected - review required"
fi

log ""
log "========================================="
log "3. Dependency License Check"
log "========================================="
log ""

# Check licenses
if command -v pip-licenses &> /dev/null || pip install pip-licenses; then
    log "Checking licenses..."
    pip-licenses --format=markdown | tee -a "$REPORT_FILE"
else
    log "pip-licenses not available, skipping license check"
fi

log ""
log "========================================="
log "4. Test Coverage Verification"
log "========================================="
log ""

# Run tests with coverage
log "Running test suite with coverage..."
if pytest tests/ --cov=src --cov=training --cov-report=term --cov-report=html --cov-fail-under=70 2>&1 | tee -a "$REPORT_FILE"; then
    log "✅ Test coverage meets 70% threshold"
else
    log "❌ Test coverage below 70% - action required"
fi

log ""
log "========================================="
log "5. Code Quality Checks"
log "========================================="
log ""

# Run linters
log "Running ruff..."
if ruff check src training cli tests 2>&1 | tee -a "$REPORT_FILE"; then
    log "✅ Ruff checks passed"
else
    log "⚠️  Ruff found issues"
fi

log ""
log "Running black check..."
if black --check src training cli tests 2>&1 | tee -a "$REPORT_FILE"; then
    log "✅ Black formatting correct"
else
    log "⚠️  Black formatting needed"
fi

log ""
log "========================================="
log "6. Documentation Check"
log "========================================="
log ""

# Count documentation files
DOC_COUNT=$(find docs -name "*.md" 2>/dev/null | wc -l)
log "Documentation files: $DOC_COUNT"

# Check for broken links (if markdown-link-check is available)
if command -v markdown-link-check &> /dev/null; then
    log "Checking for broken links in documentation..."
    find docs -name "*.md" -exec markdown-link-check {} \; 2>&1 | tee -a "$REPORT_FILE"
else
    log "markdown-link-check not available, skipping link check"
fi

log ""
log "========================================="
log "7. Security Baseline Check"
log "========================================="
log ""

# Check detect-secrets baseline
if [ -f ".secrets.baseline" ]; then
    log "Running detect-secrets scan..."
    if detect-secrets scan --baseline .secrets.baseline 2>&1 | tee -a "$REPORT_FILE"; then
        log "✅ No new secrets detected"
    else
        log "⚠️  New secrets detected - review required"
    fi
else
    log "No .secrets.baseline found, skipping secrets check"
fi

log ""
log "========================================="
log "8. Stub Analysis"
log "========================================="
log ""

# Run stub analysis
if [ -f "scripts/analyze_stubs.py" ]; then
    log "Running stub analysis..."
    python scripts/analyze_stubs.py 2>&1 | tee -a "$REPORT_FILE"
else
    log "Stub analyzer not found, skipping"
fi

log ""
log "========================================="
log "9. Disk Usage Check"
log "========================================="
log ""

# Check disk usage
log "Repository size:"
du -sh . | tee -a "$REPORT_FILE"

log ""
log "Cache directories:"
du -sh .nox htmlcov .pytest_cache __pycache__ 2>/dev/null | tee -a "$REPORT_FILE" || log "No cache directories found"

log ""
log "========================================="
log "10. Summary & Recommendations"
log "========================================="
log ""

# Generate summary
log "Maintenance Check Complete!"
log ""
log "Next Steps:"
log "1. Review outdated dependencies and update as needed"
log "2. Address any security vulnerabilities immediately"
log "3. Fix code quality issues if any"
log "4. Ensure test coverage remains above 70%"
log "5. Update documentation as needed"
log ""
log "Report saved to: $REPORT_FILE"
log ""
log "To update dependencies:"
log "  pip install --upgrade <package>"
log ""
log "To fix formatting:"
log "  black src training cli tests"
log "  isort src training cli tests"
log ""
log "To run full test suite:"
log "  nox -s tests"

echo ""
echo "========================================="
echo "Maintenance check complete!"
echo "========================================="
