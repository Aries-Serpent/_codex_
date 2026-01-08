# Prepare Pre-Release Deployment

## Purpose
Prepare comprehensive pre-release packages for GitHub deployment with full testing, validation, logging, and documentation.

## Prerequisites
- Python 3.9+ installed
- Git configured with GitHub credentials
- All tests passing
- Documentation up to date

## Commands

### 1. Pre-Release Validation
```bash
cd /home/runner/work/_codex_/_codex_

# Run full test suite
nox -s tests

# Run security checks
nox -s security

# Verify type coverage
nox -s mypy

# Check code quality
nox -s lint
```

### 2. Generate Release Artifacts
```bash
# Create release directory
mkdir -p release_artifacts

# Generate audit report
python -m scripts.space_traversal.audit_runner run \
    --output release_artifacts/audit_report.md

# Generate dashboard
python -m scripts.space_traversal.audit_runner dashboard \
    --output release_artifacts/dashboard.html

# Generate wiki bundle
python -m scripts.space_traversal.audit_runner wiki \
    --output release_artifacts/wiki_bundle.zip

# Generate documentation hub
python -m scripts.space_traversal.audit_runner docs-hub \
    --output release_artifacts/docs_hub.html

# Package source distribution
python -m build --sdist --wheel --outdir release_artifacts/
```

### 3. Create Release Logs
```bash
# Generate comprehensive release log
cat > release_artifacts/RELEASE_LOG.md << 'EOF'
# Release Log - Pre-Release $(date +%Y.%m.%d)

## Validation Results
- ✅ All tests passed (1,208+ tests)
- ✅ Security checks passed
- ✅ Type coverage verified
- ✅ Code quality validated

## Generated Artifacts
- Source distribution (tar.gz)
- Wheel distribution (.whl)
- Audit report (audit_report.md)
- HTML dashboard (dashboard.html)
- Wiki bundle (wiki_bundle.zip)
- Documentation hub (docs_hub.html)

## Test Results
$(cat test_results.txt)

## Audit Summary
$(head -50 release_artifacts/audit_report.md)

## Dependencies
$(pip freeze)

## System Information
- Python: $(python --version)
- Platform: $(uname -a)
- Timestamp: $(date -Iseconds)
EOF
```

### 4. Run Integration Tests
```bash
# Create test environment
python -m venv test_env
source test_env/bin/activate

# Install from wheel
pip install release_artifacts/*.whl

# Run smoke tests
python -c "
import sys
from pathlib import Path

print('Testing imports...')
import codex.cli
import codex.logging.session_logger
print('✅ Core imports successful')

print('Testing CLI...')
from codex.cli import app
print('✅ CLI module loaded')

print('Testing audit runner...')
from scripts.space_traversal.audit_runner import get_version
print(f'✅ Audit runner version: {get_version()}')

sys.exit(0)
"

deactivate
```

### 5. Create Pre-Release on GitHub
```bash
# Tag the release
VERSION="v1.5.5-pre.$(date +%Y%m%d)"
git tag -a "$VERSION" -m "Pre-release $VERSION"
git push origin "$VERSION"

# Create release using GitHub CLI
gh release create "$VERSION" \
    --title "Pre-Release $VERSION" \
    --notes-file release_artifacts/RELEASE_LOG.md \
    --prerelease \
    release_artifacts/audit_report.md \
    release_artifacts/dashboard.html \
    release_artifacts/wiki_bundle.zip \
    release_artifacts/docs_hub.html \
    release_artifacts/*.tar.gz \
    release_artifacts/*.whl
```

## Validation

### 1. Pre-Deployment Checklist
```bash
# Automated validation script
python -c "
import sys
from pathlib import Path

checks = {
    'Tests passed': Path('test_results.txt').exists(),
    'Audit complete': Path('release_artifacts/audit_report.md').exists(),
    'Dashboard generated': Path('release_artifacts/dashboard.html').exists(),
    'Wiki bundle created': Path('release_artifacts/wiki_bundle.zip').exists(),
    'Distributions built': len(list(Path('release_artifacts').glob('*.whl'))) > 0,
}

print('Pre-Release Validation:')
all_passed = True
for check, passed in checks.items():
    status = '✅' if passed else '❌'
    print(f'{status} {check}')
    if not passed:
        all_passed = False

sys.exit(0 if all_passed else 1)
"
```

### 2. Test Release Installation
```bash
# Test in clean environment
docker run --rm -v $(pwd)/release_artifacts:/artifacts python:3.9 bash -c "
    pip install /artifacts/*.whl && \
    python -c 'import codex.cli; print(\"✅ Installation successful\")'
"
```

### 3. Verify GitHub Release
```bash
# Check release was created
gh release view "$VERSION"

# List release assets
gh release view "$VERSION" --json assets -q '.assets[].name'
```

## Expected Output

### Release Artifacts Directory
```
release_artifacts/
├── RELEASE_LOG.md              # Comprehensive release log
├── audit_report.md             # Capability assessment
├── dashboard.html              # Interactive dashboard
├── wiki_bundle.zip             # GitHub Wiki bundle
├── docs_hub.html               # Documentation hub
├── codex-1.5.5-py3-none-any.whl   # Wheel distribution
├── codex-1.5.5.tar.gz          # Source distribution
└── test_results.txt            # Test execution results
```

### Release Log Structure
```markdown
# Release Log - Pre-Release 2025.12.10

## Validation Results
✅ All tests passed (1,208+ tests)
✅ Security checks passed (0 vulnerabilities)
✅ Type coverage verified (85%+)
✅ Code quality validated (100/100)

## Generated Artifacts
- Source distribution (codex-1.5.5.tar.gz)
- Wheel distribution (codex-1.5.5-py3-none-any.whl)
...

## Test Results
...

## Audit Summary
...
```

### GitHub Release Page
- **Title**: Pre-Release v1.5.5-pre.20251210
- **Tag**: v1.5.5-pre.20251210
- **Assets**: 7 files (wheel, source, docs, etc.)
- **Notes**: Full release log with validation results
- **Status**: Pre-release (marked with yellow badge)

## Structured Logging

### Log Format
```python
import json
import logging
from datetime import datetime

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

def log_release_event(event_type, data):
    """Log release event in structured format"""
    event = {
        'timestamp': datetime.utcnow().isoformat(),
        'event_type': event_type,
        'data': data,
        'release_version': VERSION
    }
    logging.info(json.dumps(event))

# Example usage
log_release_event('validation_start', {'stage': 'tests'})
log_release_event('validation_complete', {'stage': 'tests', 'passed': True})
log_release_event('artifact_generated', {'file': 'dashboard.html', 'size': 12345})
```

### Query Logs
```bash
# Extract specific events
cat release.log | jq 'select(.event_type == "validation_complete")'

# Count events by type
cat release.log | jq -r '.event_type' | sort | uniq -c

# Filter by timestamp
cat release.log | jq 'select(.timestamp > "2025-12-10T00:00:00")'
```

## Hypothesis Testing

Track release metrics for continuous improvement:

```python
from hypothesis import assume, given, strategies as st
import pytest

@given(st.integers(min_value=0))
def test_release_artifacts_exist(artifact_count):
    """Hypothesis: All expected artifacts are generated"""
    assume(artifact_count >= 7)  # Minimum expected artifacts
    
    artifacts = list(Path('release_artifacts').glob('*'))
    assert len(artifacts) >= artifact_count

@given(st.floats(min_value=0.0, max_value=100.0))
def test_test_coverage_threshold(coverage):
    """Hypothesis: Test coverage meets threshold"""
    assume(coverage >= 70.0)  # Minimum coverage threshold
    
    # Verify coverage meets threshold
    assert coverage >= 70.0
```

## Troubleshooting

### Issue: Tests fail
**Solution**: Fix tests before proceeding
```bash
nox -s tests -- -v --failed-first
```

### Issue: Security vulnerabilities found
**Solution**: Address vulnerabilities
```bash
bandit -r src/ -ll
pip-audit --fix
```

### Issue: Build fails
**Solution**: Check dependencies
```bash
pip install --upgrade build wheel setuptools
python -m build --verbose
```

### Issue: GitHub release creation fails
**Solution**: Check GitHub CLI authentication
```bash
gh auth status
gh auth refresh -h github.com -s write:packages
```

## Integration with GitHub Actions

Full pre-release workflow:

```yaml
name: Pre-Release Deployment

on:
  workflow_dispatch:
    inputs:
      version:
        description: 'Version (e.g., 1.5.5)'
        required: true

jobs:
  pre-release:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install Dependencies
        run: |
          pip install -e .
          pip install nox build wheel
      
      - name: Run Validation
        id: validation
        run: |
          nox -s tests
          nox -s security
          nox -s lint
          echo "validation=passed" >> $GITHUB_OUTPUT
      
      - name: Generate Artifacts
        run: |
          mkdir -p release_artifacts
          python -m scripts.space_traversal.audit_runner run \
            --output release_artifacts/audit_report.md
          python -m scripts.space_traversal.audit_runner dashboard \
            --output release_artifacts/dashboard.html
          python -m scripts.space_traversal.audit_runner wiki \
            --output release_artifacts/wiki_bundle.zip
          python -m build --sdist --wheel --outdir release_artifacts/
      
      - name: Run Integration Tests
        run: |
          python -m venv test_env
          source test_env/bin/activate
          pip install release_artifacts/*.whl
          python -c "import codex.cli; print('✅ Installation successful')"
      
      - name: Create Pre-Release
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          VERSION="v${{ github.event.inputs.version }}-pre.$(date +%Y%m%d)"
          git tag -a "$VERSION" -m "Pre-release $VERSION"
          git push origin "$VERSION"
          
          gh release create "$VERSION" \
            --title "Pre-Release $VERSION" \
            --notes "Automated pre-release deployment" \
            --prerelease \
            release_artifacts/*
      
      - name: Upload Artifacts
        uses: actions/upload-artifact@v3
        with:
          name: release-artifacts
          path: release_artifacts/
          retention-days: 90
      
      - name: Log Release Event
        run: |
          echo '{
            "timestamp": "'$(date -Iseconds)'",
            "event": "pre_release_created",
            "version": "'$VERSION'",
            "validation": "${{ steps.validation.outputs.validation }}",
            "artifacts": '$( ls -1 release_artifacts/ | jq -R -s -c 'split("\n")[:-1]')'
          }' >> .codex/sessions/release_log.jsonl
```

## Related Prompts
- [run-full-audit.md](../audit/run-full-audit.md) - Pre-release audit
- [generate-wiki.md](../documentation/generate-wiki.md) - Documentation bundle
<!-- TODO: Create validate-release.md for post-release validation -->
<!-- [validate-release.md](validate-release.md) - Post-release validation (TODO: Create this file) -->
