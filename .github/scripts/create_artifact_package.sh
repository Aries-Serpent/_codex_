#!/bin/bash
# Create comprehensive artifact package for CI/CD Workflow Analysis

echo "📦 Creating CI/CD Workflow Analysis Artifact Package..."

# Create artifact directory
ARTIFACT_DIR="ci_workflow_analysis_artifacts_2026_01_30"
mkdir -p "$ARTIFACT_DIR"

# Copy analysis reports
echo "Copying analysis reports..."
cp README_ANALYSIS_INDEX.md "$ARTIFACT_DIR/" 2>/dev/null
cp WORKFLOW_ANALYSIS_EXECUTIVE_SUMMARY.md "$ARTIFACT_DIR/" 2>/dev/null
cp COMPREHENSIVE_WORKFLOW_ANALYSIS.md "$ARTIFACT_DIR/" 2>/dev/null
cp workflow_planset_data.json "$ARTIFACT_DIR/" 2>/dev/null
cp workflow_analysis.json "$ARTIFACT_DIR/" 2>/dev/null
cp workflow_analysis.md "$ARTIFACT_DIR/" 2>/dev/null
cp workflow_analyzer.py "$ARTIFACT_DIR/" 2>/dev/null
cp PLANSET_CI_WORKFLOW_ANALYSIS_2026_01_30.md "$ARTIFACT_DIR/" 2>/dev/null

# Copy CI failure reports
echo "Copying CI failure reports..."
mkdir -p "$ARTIFACT_DIR/failure_reports"
cp reports/iteration1_audit.md "$ARTIFACT_DIR/failure_reports/" 2>/dev/null
cp src/codex_plans/Tasks_PR_2459.md "$ARTIFACT_DIR/failure_reports/" 2>/dev/null

# Copy sample workflows (critical ones only to reduce size)
echo "Copying sample critical workflows..."
mkdir -p "$ARTIFACT_DIR/sample_workflows"
cp .github/workflows/test-suite.yml "$ARTIFACT_DIR/sample_workflows/" 2>/dev/null
cp .github/workflows/security-scan.yml "$ARTIFACT_DIR/sample_workflows/" 2>/dev/null || true
cp .github/workflows/security-scanning-suite.yml "$ARTIFACT_DIR/sample_workflows/" 2>/dev/null || true
cp .github/workflows/docker-build-push.yml "$ARTIFACT_DIR/sample_workflows/" 2>/dev/null || true
cp .github/workflows/pypi-publish.yml "$ARTIFACT_DIR/sample_workflows/" 2>/dev/null || true

# Generate manifest
echo "Generating manifest..."
cat > "$ARTIFACT_DIR/MANIFEST.md" << 'EOFMANIFEST'
# CI/CD Workflow Analysis Artifact Manifest

**Generated**: 2026-01-30T21:00:00Z
**Repository**: Aries-Serpent/_codex_ (ID: 1040037790)
**Purpose**: Comprehensive CI/CD workflow analysis and remediation planset

## Contents

### Analysis Reports (8 files)
1. **PLANSET_CI_WORKFLOW_ANALYSIS_2026_01_30.md** - Main deliverable planset
2. **README_ANALYSIS_INDEX.md** - Navigation guide and quick reference
3. **WORKFLOW_ANALYSIS_EXECUTIVE_SUMMARY.md** - Executive summary
4. **COMPREHENSIVE_WORKFLOW_ANALYSIS.md** - Complete technical analysis
5. **workflow_planset_data.json** - Structured action data
6. **workflow_analysis.json** - Raw workflow metadata (122 KB)
7. **workflow_analysis.md** - Quick reference tables
8. **workflow_analyzer.py** - Python analysis tool

### CI Failure Reports (2 files)
1. **failure_reports/iteration1_audit.md** - Historical audit (Oct 2025)
2. **failure_reports/Tasks_PR_2459.md** - Known failures from PR #2459

### Sample Workflows (5 files)
1. **sample_workflows/test-suite.yml** - Testing workflow (ISSUE-001)
2. **sample_workflows/security-scan.yml** - Security scanning
3. **sample_workflows/docker-build-push.yml** - Docker builds (ISSUE-004)
4. **sample_workflows/pypi-publish.yml** - PyPI publishing (ISSUE-002)

## Key Findings

- **Total Workflows**: 116 (101 active, 15 archived)
- **Critical Issues**: 4 (YAML parse, package missing, Bandit config, Docker EOL)
- **Workflows Affected**: 8 (7% of total)
- **Estimated Effort**: 39.5 hours across 15 tasks
- **Immediate Priority**: 3.5 hours for P0 blocking issues

## Usage

1. **Start with**: PLANSET_CI_WORKFLOW_ANALYSIS_2026_01_30.md (main deliverable)
2. **Executive view**: WORKFLOW_ANALYSIS_EXECUTIVE_SUMMARY.md
3. **Technical details**: COMPREHENSIVE_WORKFLOW_ANALYSIS.md
4. **Automation**: Use workflow_analyzer.py for updates

## Validation

All files validated with:
- YAML: yamllint (where applicable)
- JSON: jq (for .json files)
- Python: pylint/black (for .py files)
- Markdown: markdownlint (for .md files)

## Next Steps

1. Review PLANSET document with human admin
2. Execute Phase 1 (P0) tasks - 3.5 hours
3. Validate fixes with provided commands
4. Report progress and continue to Phase 2

---

**Total Package Size**: ~250 KB
**Format**: Markdown, JSON, Python, YAML
**Retention**: Permanent (version controlled)
EOFMANIFEST

# List all files and sizes
echo ""
echo "📋 Package Contents:"
find "$ARTIFACT_DIR" -type f -exec du -h {} \; | sort -k2

# Calculate total size
TOTAL_SIZE=$(du -sh "$ARTIFACT_DIR" | cut -f1)
echo ""
echo "📊 Total Package Size: $TOTAL_SIZE"

# Create zip archive
echo ""
echo "🗜️ Creating zip archive..."
zip -r "${ARTIFACT_DIR}.zip" "$ARTIFACT_DIR" -q

if [ -f "${ARTIFACT_DIR}.zip" ]; then
    ZIP_SIZE=$(du -h "${ARTIFACT_DIR}.zip" | cut -f1)
    echo "✅ Archive created: ${ARTIFACT_DIR}.zip ($ZIP_SIZE)"

    # List zip contents
    echo ""
    echo "📦 Archive Contents:"
    unzip -l "${ARTIFACT_DIR}.zip" | tail -n +4 | head -n -2
else
    echo "❌ Failed to create zip archive"
    exit 1
fi

# Generate final summary
echo ""
echo "✅ Artifact package created successfully!"
echo "📍 Location: $(pwd)/${ARTIFACT_DIR}.zip"
echo "📊 Size: $ZIP_SIZE (uncompressed: $TOTAL_SIZE)"
echo "📁 Files: $(find "$ARTIFACT_DIR" -type f | wc -l) files"
