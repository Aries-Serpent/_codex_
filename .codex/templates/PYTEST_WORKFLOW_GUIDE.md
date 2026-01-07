# PyTest Workflow Implementation Guide

**Status**: TEMPLATE READY - Requires Human Admin Approval  
**Created**: 2024-12-27  
**Template Location**: `.codex/templates/tests-workflow-TEMPLATE.yml`

---

## ⚠️ Important Notice

Per repository guidelines (`.github/copilot-instructions.md`):
> "Do NOT create or activate any GitHub Actions workflow files."

This document provides a complete pytest workflow TEMPLATE that **requires human admin review and approval** before activation.

---

## Quick Start for Human Admin

### Step 1: Review Template
```bash
# Review the template
cat .codex/templates/tests-workflow-TEMPLATE.yml
```

### Step 2: Customize (Optional)
Edit the template to adjust:
- Python versions (currently: 3.11, 3.12)
- Test paths
- Coverage thresholds
- Timeout settings

### Step 3: Activate
```bash
# Copy template to workflows directory
cp .codex/templates/tests-workflow-TEMPLATE.yml .github/workflows/tests.yml

# Commit and push
git add .github/workflows/tests.yml
git commit -m "feat: add pytest workflow for automated testing"
git push
```

### Step 4: Verify
- Go to Actions tab in GitHub
- Workflow should appear as "Run Tests"
- Trigger manually or wait for next push/PR

---

## Features

### 1. Matrix Testing
- **Python Versions**: 3.11, 3.12
- **OS**: Ubuntu Latest only (Linux)
- **Fail-Fast**: Disabled (test all versions even if one fails)

### 2. Caching
- **Pip Cache**: Speeds up dependency installation
- **Cache Key**: Includes Python version and dependency files
- **Restore Keys**: Fallback to similar cache entries

### 3. Test Execution
- **pytest**: Main test runner
- **Coverage**: Code coverage reporting with multiple formats
- **Parallel**: Tests run in parallel (`-n auto`)
- **Distribution**: Load-balanced test distribution

### 4. Artifacts
- **Coverage Reports**: HTML and XML formats
- **Test Results**: pytest cache for debugging
- **Retention**: 30 days for coverage, 7 days for test results

### 5. PR Integration
- **Coverage Comments**: Automatic coverage comments on PRs (Python 3.12 only)
- **Thresholds**: Green ≥70%, Orange ≥60%

### 6. Advanced Features (Optional Jobs)
- **Integration Tests**: Run on PRs and main branch
- **Advanced Features**: Interpretability, attention scoring, MLP scoring
- **Manual Trigger**: workflow_dispatch for full testing

---

## Configuration

### Python Versions
```yaml
matrix:
  python-version: ['3.11', '3.12']
```

To add Python 3.13:
```yaml
matrix:
  python-version: ['3.11', '3.12', '3.13']
```

### Test Command
```bash
pytest tests/ \
  -v \                    # Verbose output
  --tb=short \            # Short traceback format
  --cov=agents \          # Coverage for agents module
  --cov=scripts \         # Coverage for scripts
  --cov-report=term-missing \  # Show missing lines
  --cov-report=xml \      # XML report for tools
  --cov-report=html \     # HTML report for viewing
  -n auto \               # Parallel execution
  --dist=loadscope        # Load-balanced distribution
```

### Coverage Thresholds
```yaml
MINIMUM_GREEN: 70   # ≥70% = green
MINIMUM_ORANGE: 60  # 60-69% = orange, <60% = red
```

---

## Security Considerations

### 1. Token Usage
- Uses built-in `${{ github.token }}` with minimal permissions
- **NO** personal access tokens (PATs) exposed
- Scoped to repository operations only

### 2. Dependency Security
- All actions pinned to major versions (@v4, @v5)
- Python packages installed from official PyPI
- Consider adding dependency scanning (Dependabot, Snyk)

### 3. Secrets Management
- No secrets required for basic operation
- If adding ML integrations, use repository secrets
- Never expose secrets to untrusted code

---

## Next Steps

1. **Review** this template thoroughly
2. **Customize** configurations as needed
3. **Test locally** before activating:
   ```bash
   pytest tests/ -v --tb=short
   ```
4. **Activate** workflow by copying to `.github/workflows/`
5. **Monitor** first few runs and adjust as needed
6. **Iterate** based on results and feedback

---

**Template Version**: 1.0.0  
**Last Updated**: 2024-12-27  
**Status**: Ready for Human Review
