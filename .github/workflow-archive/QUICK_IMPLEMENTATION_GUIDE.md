# Quick Implementation Guide
**Project**: Workflow Consolidation & Artifact Prefix  
**Date**: 2026-02-06  
**Purpose**: Fast-track guide for immediate implementation

---

## 🚀 Phase 0: Artifact Prefix Implementation (Week 1)

### ⚡ Quick Start: Add `Art_` Prefix to 42 Workflows

**Time Estimate**: 2-4 hours  
**Risk**: Minimal  
**Impact**: High visibility improvement

#### Option 1: Automated Script (Recommended)

```bash
#!/bin/bash
# File: scripts/add_artifact_prefix.sh

set -e

# Backup directory
BACKUP_DIR=".github/workflow-archive/backups/$(date +%Y-%m-%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Workflows requiring Art_ prefix (42 total)
WORKFLOWS=(
  "agent-chain-orchestrator.yml"
  "audit-improvement-pipeline.yml"
  "auth-compliance-report.yml"
  "batch-ci-triage.yml"
  "ci-health-suite.yml"
  "code-quality.yml"
  "codeql-analysis.yml"
  "codeql-chunked.yml"
  "cognitive-action.yml"
  "cognitive-aftermath.yml"
  "cognitive-brain-feed.yml"
  "cognitive-decision.yml"
  "copilot-self-evolution.yml"
  "coverage_report.yml"
  "data_validation.yml"
  "decode-validate-artifact.yml"
  "determinism.yml"
  "documentation-link-checker.yml"
  "documentation-suite.yml"
  "docker-build-push.yml"
  "html_visual_baseline.yml"
  "html_visual_regression.yml"
  "nox_gates.yml"
  "optimized-ci.yml"
  "post-merge-validation-optimized.yml"
  "pre-release-deployment.yml"
  "publish_dashboard_release.yml"
  "repo-organization.yml"
  "repository-health-monitoring.yml"
  "rust_swarm_ci.yml"
  "sbom.yml"
  "scheduled-archival.yml"
  "scheduled-dependency-audit.yml"
  "security-scanning-suite.yml"
  "security-suite.yml"
  "self-healing-ci.yml"
  "self-healing-feedback-loop.yml"
  "self-healing.yml"
  "test-comprehensive.yml"
  "test-rag.yml"
  "test-suite.yml"
  "workflow-health-check.yml"
)

echo "🔄 Adding Art_ prefix to ${#WORKFLOWS[@]} workflows..."

for workflow in "${WORKFLOWS[@]}"; do
  WORKFLOW_PATH=".github/workflows/$workflow"
  
  # Check if file exists
  if [ ! -f "$WORKFLOW_PATH" ]; then
    echo "⚠️  Skipping $workflow (not found)"
    continue
  fi
  
  # Backup original
  cp "$WORKFLOW_PATH" "$BACKUP_DIR/$workflow"
  
  # Add Art_ prefix to name field (only if not already present)
  if ! grep -q "^name: Art_" "$WORKFLOW_PATH"; then
    sed -i 's/^name: \(.*\)/name: Art_\1/' "$WORKFLOW_PATH"
    echo "✅ Updated: $workflow"
  else
    echo "⏭️  Skipped: $workflow (already has prefix)"
  fi
done

echo ""
echo "🎉 Complete! Updated ${#WORKFLOWS[@]} workflows"
echo "📦 Backups saved to: $BACKUP_DIR"
echo ""
echo "Next steps:"
echo "1. Review changes: git diff .github/workflows/"
echo "2. Test workflows: gh workflow list"
echo "3. Commit changes: git add .github/workflows/ && git commit -m 'Add Art_ prefix to artifact-producing workflows'"
echo "4. Push to branch: git push"
```

**Run the script**:
```bash
chmod +x scripts/add_artifact_prefix.sh
./scripts/add_artifact_prefix.sh
```

#### Option 2: Manual Implementation

For each of the 42 workflows, update the `name:` field:

```yaml
# BEFORE
name: Rust-Python Hybrid Swarm CI/CD

# AFTER
name: Art_Rust-Python Hybrid Swarm CI/CD
```

**Priority Order**:
1. **Critical** (4 workflows): rust_swarm_ci.yml, codeql-chunked.yml, docker-build-push.yml, scheduled-dependency-audit.yml
2. **High** (24 workflows): All CI/CD, testing, and security workflows
3. **Medium** (16 workflows): Documentation, cognitive, monitoring workflows
4. **Low** (4 workflows): Experimental and periodic workflows

#### Verification Script

```bash
#!/bin/bash
# Verify all artifact-producing workflows have Art_ prefix

echo "🔍 Verifying Art_ prefix implementation..."

MISSING=0

while read -r workflow; do
  if ! grep -q "^name: Art_" "$workflow"; then
    echo "❌ Missing prefix: $workflow"
    ((MISSING++))
  fi
done < <(grep -l "actions/upload-artifact" .github/workflows/*.yml)

if [ $MISSING -eq 0 ]; then
  echo "✅ All artifact-producing workflows have Art_ prefix!"
else
  echo "⚠️  $MISSING workflows missing Art_ prefix"
  exit 1
fi
```

---

## 📋 Phase 1: Security Suite Consolidation (Week 2)

### Quick Consolidation: Security Suites (3 → 1)

**Time Estimate**: 4-6 hours  
**Risk**: Low  
**Workflows**: security-scanning-suite.yml, security-suite.yml, security-scan.yml

#### Step 1: Create New Consolidated Workflow

```bash
# Create the new unified workflow
cat > .github/workflows/unified-security-suite.yml << 'EOF'
name: Art_Unified Security Suite
on:
  push:
    branches: [main]
  pull_request:
  schedule:
    - cron: '0 2 * * *'
  workflow_dispatch:

jobs:
  semgrep-scan:
    name: Semgrep SAST
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Semgrep
        run: semgrep ci --sarif --output semgrep.sarif
      - name: Upload SARIF
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: semgrep.sarif
  
  dependency-audit:
    name: Dependency Security Audit
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install pip-audit
        run: pip install pip-audit
      - name: Run pip audit
        run: pip-audit --format json --output audit_results.json
      - name: Upload Results
        uses: actions/upload-artifact@v6
        with:
          name: dependency-audit-${{ github.run_number }}
          path: audit_results.json
  
  secret-scan:
    name: Secret Scanning
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Gitleaks
        uses: gitleaks/gitleaks-action@v2
  
  unified-results:
    name: Aggregate Security Results
    runs-on: ubuntu-latest
    needs: [semgrep-scan, dependency-audit, secret-scan]
    steps:
      - name: Collect Results
        run: echo "All security scans complete"
      - name: Upload Artifacts
        uses: actions/upload-artifact@v6
        with:
          name: security-suite-results-${{ github.run_number }}
          path: |
            semgrep.sarif
            audit_results.json
          retention-days: 90
EOF
```

#### Step 2: Test New Workflow

```bash
# Push to feature branch
git checkout -b consolidate-security-suite
git add .github/workflows/unified-security-suite.yml
git commit -m "Add unified security suite workflow"
git push -u origin consolidate-security-suite

# Trigger manual run
gh workflow run unified-security-suite.yml

# Monitor execution
gh run watch
```

#### Step 3: Disable Old Workflows

```bash
# After successful test, disable old workflows
for workflow in security-scanning-suite.yml security-suite.yml security-scan.yml; do
  # Move to archive
  mv .github/workflows/$workflow .github/workflow-archive/disabled/
  
  # Create metadata
  cat > .github/workflow-archive/disabled/$workflow.meta << EOF
disabled_at: $(date -Iseconds)
reason: Consolidated into unified-security-suite.yml
backup_location: .github/workflow-archive/backups/$(date +%Y-%m-%d)/
consolidated_to: unified-security-suite.yml
EOF
done

# Commit changes
git add .github/workflows/ .github/workflow-archive/
git commit -m "Consolidate security workflows into unified-security-suite.yml"
```

---

## 📊 Validation Checklist

### After Artifact Prefix Implementation

- [ ] All 42 workflows have `Art_` prefix in `name:` field
- [ ] No workflows have duplicate `Art_Art_` prefix
- [ ] All workflows still upload artifacts correctly
- [ ] GitHub Actions UI shows prefixed names
- [ ] ARTIFACT_CATALOG.md updated with new names
- [ ] No CI failures from name changes

### After Each Consolidation

- [ ] New consolidated workflow tested successfully
- [ ] All jobs complete without errors
- [ ] Artifacts upload correctly
- [ ] Old workflows disabled and archived
- [ ] Metadata files created for tracking
- [ ] Documentation updated
- [ ] No functionality lost
- [ ] Team notified of changes

---

## 🔄 Rollback Procedures

### Rollback Artifact Prefix Changes

```bash
# Restore from backup
BACKUP_DIR=".github/workflow-archive/backups/YYYY-MM-DD-HHMMSS"
cp $BACKUP_DIR/*.yml .github/workflows/

# Commit rollback
git add .github/workflows/
git commit -m "Rollback: Remove Art_ prefix from workflows"
git push
```

### Rollback Consolidation

```bash
# Restore disabled workflow
WORKFLOW="security-scanning-suite.yml"
cp .github/workflow-archive/disabled/$WORKFLOW .github/workflows/

# Remove consolidated workflow
rm .github/workflows/unified-security-suite.yml

# Commit rollback
git add .github/workflows/
git commit -m "Rollback: Restore $WORKFLOW"
git push
```

---

## 📈 Progress Tracking

### Week 1: Artifact Prefix
- [ ] Day 1: Review implementation plan
- [ ] Day 2: Run automated script
- [ ] Day 3: Test and verify
- [ ] Day 4: Update documentation
- [ ] Day 5: Final review and merge

### Week 2: Security Consolidation
- [ ] Day 1-2: Create unified-security-suite.yml
- [ ] Day 3: Test on feature branch
- [ ] Day 4: Disable old workflows
- [ ] Day 5: Documentation and monitoring

### Weekly Reporting Template

```markdown
## Week X Progress Report

### Completed
- ✅ [Task description]
- ✅ [Task description]

### In Progress
- 🔄 [Task description]

### Blocked
- 🚫 [Task description] - [Blocker reason]

### Metrics
- Workflows reduced: X → Y (-Z)
- Artifact prefixes added: X/42
- Tests passing: X/Y

### Next Week Plan
- [ ] [Planned task]
- [ ] [Planned task]
```

---

## 🎯 Quick Reference

### Key Files
- **Analysis**: `.github/workflow-archive/WORKFLOW_ANALYSIS_COMPLETE.md`
- **Artifact List**: `.github/workflow-archive/ARTIFACT_PREFIX_REQUIREMENTS.md`
- **Consolidation Plan**: `.github/workflow-archive/WORKFLOW_CONSOLIDATION_PLANSET_V2.md`
- **Agent Mapping**: `.github/workflow-archive/WORKFLOW_TO_AGENT_MAPPING.md`
- **Executive Summary**: `.github/workflow-archive/EXECUTIVE_SUMMARY_WORKFLOW_REVIEW_2026-02-06.md`

### Commands
```bash
# List workflows
gh workflow list

# Run workflow manually
gh workflow run WORKFLOW_NAME.yml

# Monitor run
gh run watch

# List recent runs
gh run list --limit 10

# View workflow file
gh workflow view WORKFLOW_NAME.yml

# Disable workflow
gh workflow disable WORKFLOW_NAME.yml

# Enable workflow
gh workflow enable WORKFLOW_NAME.yml
```

### Agent Integration

Involve these custom agents during implementation:

| Phase | Recommended Agent |
|-------|------------------|
| Artifact Prefix | artifact-monitor-agent |
| Security Consolidation | security-alert-verification-agent |
| Test Consolidation | test-coverage-monitor |
| CI Health | ci-testing-agent, workflow-ci-fixer |
| Documentation | documentation-quality-agent |

---

## ❓ FAQ

**Q: Will adding `Art_` prefix break anything?**  
A: No. The `name:` field is only for display. Workflow file names remain unchanged.

**Q: How do I test a workflow without triggering it?**  
A: Use `workflow_dispatch` trigger and run manually: `gh workflow run WORKFLOW.yml`

**Q: What if a consolidation causes failures?**  
A: Follow rollback procedure to restore original workflows immediately.

**Q: Can I do this in smaller batches?**  
A: Yes! The artifact prefix script can be modified to process batches of 10-15 workflows.

**Q: Who approves these changes?**  
A: Repository owner (@mbaetiong) should review and approve before implementation.

---

**Quick Start**: Begin with Phase 0 (artifact prefix) - lowest risk, highest visibility impact.

---

*Generated: 2026-02-06*  
*Version: 1.0*  
*Status: Ready for implementation*
