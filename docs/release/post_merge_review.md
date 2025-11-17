# Post-Merge Review Checklist

## Overview

This checklist ensures that merges to the main branch maintain quality and don't introduce regressions.

## Automated Checks

The post-merge validation workflow (`.github/workflows/post-merge-validation.yml`) runs automatically on pushes to main.

### What Gets Validated

1. **Import Validation**
   - Torch imports from site-packages (not local stubs)
   - Core modules import successfully
   - OmegaConf compatibility verified

2. **Test Suite**
   - Smoke tests pass
   - Quick test subset runs
   - Critical functionality verified

3. **Lint Checks**
   - No syntax warnings
   - Code quality maintained

### Viewing Results

Check the Actions tab:
```text
https://github.com/Aries-Serpent/_codex_/actions/workflows/post-merge-validation.yml
```text

## Manual Post-Merge Verification

### Step 1: Local Environment Check

```bash
# Pull latest main
git checkout main
git pull origin main

# Clean install
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```text

### Step 2: Import Verification

```bash
# Verify torch import location
python -c "import torch; print(torch.__file__)"
# Should show: .../site-packages/torch/__init__.py

# Verify core imports
python -c "from src.codex_ml.training.unified_training import UnifiedTrainingConfig"
python -c "from omegaconf import OmegaConf; from src.codex_ml.training.unified_training import UnifiedTrainingConfig; OmegaConf.structured(UnifiedTrainingConfig())"
```text

### Step 3: Run Critical Tests

```bash
# Config tests
pytest tests/config/test_config_schema.py -v

# Core unit tests
pytest tests/unit/test_data_cache_locking.py -v

# Smoke tests
pytest -m smoke -v
```text

### Step 4: Quality Gates

```bash
# Run all gates
nox -s gates

# Or individually:
nox -s lint
nox -s typecheck
nox -s tests
```text

### Step 5: Documentation Check

```bash
# Run fence fixer in dry-run mode
python tools/fence_fixer.py . --dry-run --verbose

# Should report low or zero fence issues
```text

## Regression Detection

### Performance Regression

If tests are taking significantly longer:

```bash
# Run performance benchmarks
pytest -m perf_smoke --durations=10
```text

### Test Failure Regression

If new failures appear:

1. Check if they're flaky:
   ```bash
   pytest path/to/failing_test.py --count=10
   ```

2. Bisect to find breaking commit:
   ```bash
   git bisect start
   git bisect bad HEAD
   git bisect good <last-known-good-commit>
   # Follow bisect prompts
   ```

### Import/Dependency Regression

If imports fail:

```bash
# Check for namespace conflicts
python -c "import sys; import torch; assert 'site-packages' in torch.__file__, f'Wrong torch location: {torch.__file__}'"

# Verify package installation
pip list | grep -E "torch|omegaconf|hydra"
```text

## Issue Creation on Failure

If post-merge validation fails, an issue is automatically created with:
- Commit hash that failed
- Failure details
- Labels: `bug`, `urgent`, `post-merge`

### Handling Post-Merge Issues

1. **Immediate action required** for:
   - Import failures
   - Critical test failures
   - Lint/syntax errors

2. **Can be queued** for:
   - Documentation issues
   - Non-critical test warnings
   - Performance degradation < 20%

3. **Hotfix process**:
   ```bash
   git checkout main
   git checkout -b hotfix/post-merge-<issue-number>
   # Fix the issue
   git commit -m "hotfix: <description> (fixes #<issue-number>)"
   # Create PR, get quick review, merge
   ```

## Health Metrics

Track these over time:

| Metric | Target | Action if Outside Target |
|--------|--------|-------------------------|
| Test success rate | > 95% | Investigate failures |
| Average test time | < 5 min | Optimize slow tests |
| Fence errors | < 10 | Run bulk fix |
| Syntax warnings | 0 | Fix immediately |
| Import errors | 0 | Fix immediately |

## Release Readiness

Before cutting a release from main:

- [ ] All post-merge validations passing
- [ ] No open `post-merge` issues
- [ ] Documentation up to date
- [ ] CHANGELOG updated
- [ ] Version bumped in `pyproject.toml`
- [ ] All markers documented
- [ ] Fence errors < 10

## Tools and Scripts

### Quick Health Check

```bash
# Run full health check
./scripts/health_check.sh  # If exists

# Or manually:
python -c "import torch; from src.codex_ml.training.unified_training import UnifiedTrainingConfig; print('✓ Imports OK')"
pytest -m smoke --tb=no -q && echo "✓ Smoke tests OK"
python tools/fence_fixer.py . --dry-run | grep "Files changed: 0" && echo "✓ Fences OK"
```text

### Monitoring

Set up monitoring for:
- GitHub Actions status
- Test duration trends
- Failure rate trends

## Rollback Procedure

If a merge causes serious issues:

```bash
# Create revert PR
git checkout main
git pull
git revert <bad-commit-hash>
git checkout -b revert/<bad-commit-hash>
git push origin revert/<bad-commit-hash>
# Create PR with explanation
```text

## Documentation

After merge, verify:
- [ ] New features documented
- [ ] API docs updated (if applicable)
- [ ] Migration guide (if breaking changes)
- [ ] CHANGELOG entry
- [ ] Release notes (if applicable)

## Contact

For post-merge issues:
- Create issue with `post-merge` label
- Tag relevant maintainers
- Include commit hash and failure details
