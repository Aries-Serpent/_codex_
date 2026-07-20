# Phase 3-4 Testing Framework

**Status**: ✅ Production Ready  
**Version**: 1.0.0  
**Date**: 2026-07-20

Complete validation framework for cognitive_app and MkDocs deployment pipeline.

---

## Quick Start

### Prerequisites

- Node.js 22+
- npm 10+
- Python 3.12+
- MkDocs with material theme

### Run All Tests

```bash
# Pre-deployment validation
python pre_deploy_validation.py

# Integration tests
python integration_tests.py

# Regression tests
python regression_tests.py

# Post-deployment validation (after deploy)
python post_deploy_validation.py https://your-deployed-site/cognitive_app/
```

---

## Test Suites

### 1. Pre-Deployment Validation (`pre_deploy_validation.py`)

Validates cognitive_app build before deployment.

**Runs**: 10 checks  
**Time**: ~5-10 minutes  
**Output**: JSON results to `.codex/pre_deploy_results.json`

**Checks**:
- Node version (>=22)
- Package.json structure
- Package-lock.json format
- Build execution (npm ci && npm run build)
- Dist directory structure
- Required asset files (JS, CSS)
- HTML structure with React root div
- Vite configuration
- Asset paths (relative vs absolute)
- Build output analysis

**Usage**:
```bash
python pre_deploy_validation.py
```

**Success Output**:
```
=== Starting Pre-Deployment Validation ===
✅ PASS: Node Version Check
✅ PASS: Package.json Check
...
=== PRE-DEPLOYMENT VALIDATION SUMMARY ===
Status: PASS
Total Checks: 10
Passed: 10
```

### 2. Post-Deployment Validation (`post_deploy_validation.py`)

Validates deployed site after deployment to GitHub Pages.

**Runs**: 8 checks  
**Time**: ~2-5 minutes (includes retries)  
**Output**: JSON results to `.codex/post_deploy_results.json`

**Checks**:
- Site HTTP status (200)
- Index.html retrieval
- React root div presence
- Script tags
- Asset accessibility
- HTML meta tags
- Security headers
- Performance metrics

**Usage**:
```bash
# With default URL
python post_deploy_validation.py

# With custom URL
python post_deploy_validation.py https://example.com/cognitive_app/
```

**Success Output**:
```
=== Starting Post-Deployment Validation ===
Site URL: https://aries-serpent.github.io/_codex_/cognitive_app/
✅ PASS: Site HTTP Status
✅ PASS: React Root Div
...
=== POST-DEPLOYMENT VALIDATION SUMMARY ===
Status: PASS
Total Checks: 8
Passed: 8
```

### 3. Integration Tests (`integration_tests.py`)

Tests cognitive_app + MkDocs deployment integration.

**Runs**: 8 tests  
**Time**: ~10-15 minutes  
**Output**: JSON results to `.codex/integration_test_results.json`

**Tests**:
- MkDocs build
- Cognitive app build
- Non-interference between builds
- Artifact structure
- Documentation presence
- App presence in site/
- Configuration validation
- Dependency resolution

**Usage**:
```bash
python integration_tests.py
```

**Success Output**:
```
=== Starting Integration Test Suite ===
✅ PASS: MkDocs Build Test
✅ PASS: Cognitive App Build Test
...
=== INTEGRATION TEST SUMMARY ===
Status: PASS
Total Tests: 8
Passed: 8
```

### 4. Regression Tests (`regression_tests.py`)

Validates against v0.3.0 baseline to prevent regressions.

**Runs**: 9 tests  
**Time**: ~2-3 minutes  
**Output**: JSON results to `.codex/regression_test_results.json`

**Tests**:
- Node.js version baseline (>=22.0.0)
- npm version baseline (>=10.0.0)
- Python version baseline (>=3.12)
- Critical package versions
- Previous build configuration
- Configuration stability
- Dependency lock files
- Asset generation pipeline
- Previous test suite availability

**Usage**:
```bash
python regression_tests.py
```

**Success Output**:
```
=== Starting Regression Test Suite ===
Baseline: v0.3.0 deployment validation
✅ PASS: Node.js Version Baseline
✅ PASS: npm Version Baseline
...
=== REGRESSION TEST SUMMARY ===
Status: PASS
Total Tests: 9
Passed: 9
```

---

## Test Results

All test suites output JSON results to `.codex/` directory:

```
.codex/
├── pre_deploy_results.json       # Pre-deployment results
├── post_deploy_results.json      # Post-deployment results
├── integration_test_results.json # Integration test results
└── regression_test_results.json  # Regression test results
```

### Result Format

```json
{
  "status": "PASS",
  "timestamp": "2026-07-20T17:17:38Z",
  "checks": [
    {
      "name": "Check Name",
      "passed": true,
      "message": "Check passed successfully"
    }
  ],
  "errors": [],
  "warnings": []
}
```

### Parse Results in CI

```bash
# Example: Check if validation passed
python -c "
import json
import sys

with open('.codex/pre_deploy_results.json') as f:
    result = json.load(f)

if result['status'] != 'PASS':
    print(f\"Tests failed: {len(result['errors'])} errors\")
    for error in result['errors']:
        print(f\"  - {error}\")
    sys.exit(1)
"
```

---

## CI/CD Integration

### GitHub Actions Workflow

Add to `.github/workflows/` (example below):

```yaml
name: Validate Deployment

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Node.js 22
        uses: actions/setup-node@v4
        with:
          node-version: '22'
          cache: npm
          cache-dependency-path: cognitive_app/package-lock.json

      - name: Set up Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: pip

      - name: Pre-deployment validation
        run: python .codex/tests/pre_deploy_validation.py

      - name: Integration tests
        run: python .codex/tests/integration_tests.py

      - name: Regression tests
        run: python .codex/tests/regression_tests.py

      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-results
          path: .codex/*_results.json

  post-deploy:
    needs: validate
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Wait for deployment
        run: sleep 60

      - name: Post-deployment validation
        run: python .codex/tests/post_deploy_validation.py
```

---

## Common Issues & Solutions

### Node Version Error
```
❌ Node 20.x.x is below minimum requirement of 22
```
**Solution**: Install Node 22+
```bash
nvm install 22
nvm use 22
```

### npm Lock File Error
```
❌ npm ci failed: lock file mismatch
```
**Solution**: Reinstall dependencies
```bash
rm cognitive_app/package-lock.json
cd cognitive_app && npm install
```

### Build Timeout
```
❌ Build process timed out (300s)
```
**Solution**: Increase timeout or check for missing dependencies
```bash
cd cognitive_app
npm ci --verbose
npm run build --verbose
```

### React Root Div Not Found
```
❌ React root div (id='root') not found in index.html
```
**Solution**: Verify cognitive_app/src/main.tsx
```jsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'

ReactDOM.createRoot(document.getElementById('root')!).render(...)
```

### Post-Deployment Connection Failed
```
❌ Site unreachable after retries
```
**Solution**: Check site deployment status
- Verify GitHub Pages is enabled
- Check Pages deployment in settings
- Wait for CDN propagation (~1 minute)

---

## Expected Results Summary

| Test Suite | Status | Time | Output |
|---|---|---|---|
| Pre-deployment | ✅ PASS | 5-10 min | 10/10 checks |
| Integration | ✅ PASS | 10-15 min | 8/8 tests |
| Regression | ✅ PASS | 2-3 min | 9/9 tests |
| Post-deployment | ✅ PASS | 2-5 min | 8/8 checks |

---

## Documentation

- **Dependency Report**: See `../DEPENDENCY_REPORT.md`
- **Test Framework Report**: See `../TEST_FRAMEWORK_REPORT.md`

---

## Troubleshooting

### Verbose Output
Add `--verbose` flag (built-in to each script):
```python
validator = PreDeployValidator(verbose=True)
```

### Debug Mode
Add `print()` statements or use Python debugger:
```bash
python -m pdb pre_deploy_validation.py
```

### Clear Caches
```bash
# npm cache
npm cache clean --force

# pip cache
pip cache purge

# Remove node_modules
rm -rf cognitive_app/node_modules

# Reinstall
cd cognitive_app && npm ci
```

---

## Support

For issues or questions:
1. Check the test output for diagnostic messages
2. Review common issues section above
3. Check logs in `.codex/*_results.json`
4. Run with verbose mode enabled

---

**Framework Version**: 1.0.0  
**Status**: Production Ready  
**Last Updated**: 2026-07-20
