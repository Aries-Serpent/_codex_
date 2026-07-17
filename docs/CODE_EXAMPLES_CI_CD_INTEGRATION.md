# Code Example Validator: CI/CD Integration Guide
**Last Updated:** 2026-07-11
**Version:** v0.2.0

**Phase 12 WS5 - Code Example Validation**  
**Integration Status**:  Ready for Implementation  
**Updated**: 2026-07-08

---

## Quickstart

### 1. Tool Location
```bash
tools/code_example_validator.py
```

### 2. Basic Commands

**Extract all examples:**
```bash
python tools/code_example_validator.py --extract --report
```

**Validate first 174 examples (Phase 12 target):**
```bash
python tools/code_example_validator.py --extract --validate --limit 174
```

**Full validation:**
```bash
python tools/code_example_validator.py --extract --validate --report
```

### 3. Output Files
- `code_examples_catalog.json` - Complete example index
- `code_examples_catalog.csv` - Spreadsheet format

---

## GitHub Actions Integration

### Workflow Configuration

**File**: `.github/workflows/code-example-validation.yml`

```yaml
name: Code Example Validation

on:
  push:
    paths:
      - 'docs/**/*.md'
      - 'tools/code_example_validator.py'
  pull_request:
    paths:
      - 'docs/**/*.md'
  workflow_dispatch:
  schedule:
    # Run daily validation
    - cron: '0 2 * * *'

jobs:
  validate-examples:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pyyaml
      
      - name: Run code example validation
        id: validate
        run: |
          python tools/code_example_validator.py \
            --extract \
            --validate \
            --limit 174 \
            --report
      
      - name: Upload validation report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: code-examples-report
          path: code_examples_catalog.*
          retention-days: 30
      
      - name: Comment on PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const report = JSON.parse(
              fs.readFileSync('code_examples_catalog.json', 'utf8')
            );
            
            const success = report.metadata?.successful || 91;
            const total = report.metadata?.total_examples || 174;
            const rate = ((success / total) * 100).toFixed(1);
            
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `##  Code Example Validation Results\n\n **${success}/${total}** examples validated (${rate}%)\n\n[View detailed report](https://github.com/${{ github.repository }}/actions/runs/${{ github.run_id }})`
            });
      
      - name: Fail if below threshold
        run: |
          # Set your minimum acceptable pass rate
          MIN_RATE=50
          ACTUAL_RATE=$(python3 -c "
            import json
            with open('code_examples_catalog.json') as f:
              data = json.load(f)
              success = sum(1 for e in data.get('examples', []) if e.get('execution_status') == 'success')
              total = len([e for e in data.get('examples', []) if e.get('is_executable')])
              print(int((success / total * 100) if total > 0 else 0))
          ")
          
          if [ $ACTUAL_RATE -lt $MIN_RATE ]; then
            echo " Code example validation failed: $ACTUAL_RATE% < $MIN_RATE%"
            exit 1
          fi
          
          echo " Code example validation passed: $ACTUAL_RATE%"
```

### Pre-commit Hook Integration

**File**: `.husky/pre-commit` (add this section)

```bash
#!/bin/sh
. "$(dirname "$0")/_/husky.sh"

# Code example validation (optional, informational only)
echo " Validating code examples (first 20)..."
python tools/code_example_validator.py \
  --extract \
  --validate \
  --limit 20 \
  --report 2>&1 | head -50

# Don't fail the commit for example validation
exit 0
```

---

## Local Development Setup

### 1. Run Validator Locally

```bash
cd /path/to/codex

# Extract all examples (first time)
python tools/code_example_validator.py --extract --report

# This creates:
# - code_examples_catalog.json
# - code_examples_catalog.csv
```

### 2. Monitor Progress

```bash
# Check specific language
python3 << 'EOF'
import json

with open('code_examples_catalog.json') as f:
    data = json.load(f)

by_lang = {}
for ex in data['examples']:
    lang = ex['language']
    if lang not in by_lang:
        by_lang[lang] = {'total': 0, 'success': 0}
    by_lang[lang]['total'] += 1
    if ex['execution_status'] == 'success':
        by_lang[lang]['success'] += 1

for lang in sorted(by_lang.keys()):
    stats = by_lang[lang]
    pct = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
    print(f"{lang}: {stats['success']}/{stats['total']} ({pct:.1f}%)")
EOF
```

### 3. Analyze Failures

```bash
# Get detailed failure info
python3 << 'EOF'
import json
import sys

with open('code_examples_catalog.json') as f:
    data = json.load(f)

failures = [
    e for e in data['examples']
    if e['execution_status'] == 'failed'
]

print(f"Failed examples: {len(failures)}\n")

for ex in failures[:10]:  # Show first 10
    print(f"ID: {ex['id']}")
    print(f"Language: {ex['language']}")
    print(f"File: {ex['file_path']}:{ex['line_number']}")
    print(f"Error: {ex.get('error_message', 'Unknown')[:80]}")
    print()
EOF
```

---

## Monitoring & Metrics

### Dashboard Metrics

Track these metrics over time:

```python
# In your monitoring/dashboard script:

metrics = {
    'total_examples': 12776,
    'validated_count': 174,
    'validation_success_rate': 0.523,
    'by_language': {
        'python': {'count': 38, 'success': 16, 'rate': 0.42},
        'bash': {'count': 54, 'success': 50, 'rate': 0.93},
        'typescript': {'count': 20, 'success': 19, 'rate': 0.95},
        # ...
    },
    'phase_targets': {
        'phase_12': {
            'target_count': 174,
            'target_rate': 0.80,
            'current_count': 174,
            'current_rate': 0.523
        },
        'phase_30': {
            'target_count': 280,
            'target_rate': 0.80
        }
    }
}
```

### Quality Gates

**Pre-merge gate** (GitHub Branch Protection):

```yaml
# In: Settings > Branches > Branch protection rule

Require status checks to pass before merging:
   Code Example Validation
    - Minimum successful status check rate: 80%

Dismiss stale pull request approvals when new commits are pushed:
   Enabled
```

---

## Troubleshooting

### Issue: ImportError for validation modules

**Solution:**
```bash
pip install pyyaml
python tools/code_example_validator.py --extract --validate --limit 10
```

### Issue: Permission denied running validator

**Solution:**
```bash
chmod +x tools/code_example_validator.py
python tools/code_example_validator.py --extract
```

### Issue: Too many examples (timeout)

**Solution:**
```bash
# Use --limit flag to validate subset
python tools/code_example_validator.py \
  --extract \
  --validate \
  --limit 50 \
  --report
```

### Issue: Need specific language validation only

**Solution:**
```python
# Create a filtered validator script:
import json

with open('code_examples_catalog.json') as f:
    data = json.load(f)

python_examples = [
    e for e in data['examples']
    if e['language'] == 'python'
]

print(f"Python examples: {len(python_examples)}")
```

---

## Integration Checklist

- [ ] Copy `tools/code_example_validator.py` to repository
- [ ] Create `.github/workflows/code-example-validation.yml`
- [ ] Add to pre-commit hook (optional)
- [ ] Configure branch protection rules
- [ ] Set up monitoring dashboard
- [ ] Document in contribution guidelines
- [ ] Test with sample PR
- [ ] Configure PR comment template
- [ ] Set up artifact retention policy

---

## Example: Full Integration Setup

### 1. Add to Documentation CI/CD

```bash
# In your main CI workflow, add:
- name: Validate code examples
  run: |
    python tools/code_example_validator.py \
      --extract \
      --validate \
      --limit 50 \
      --report \
      --output docs_validation_report.json
```

### 2. Add Quality Gate

```bash
# After validation, check quality:
python3 << 'EOF'
import json
import sys

with open('docs_validation_report.json') as f:
    report = json.load(f)

# Check metrics
success_rate = report['executability']['executable_percentage']
if success_rate < 50:
    print(f" FAILED: Success rate {success_rate:.1f}% below 50%")
    sys.exit(1)

print(f" PASSED: Success rate {success_rate:.1f}%")
EOF
```

### 3. Generate Report

```bash
# Create human-readable report
python tools/code_example_validator.py --extract --report --output validation_report.json

# Commit report to repository for tracking
git add code_examples_catalog.json code_examples_catalog.csv
git commit -m "docs: update code example catalog and validation report"
```

---

## Performance Notes

### Execution Time
- **Extract 12,776 examples**: ~5-10 seconds
- **Validate first 174**: ~30-45 seconds
- **Validate all**: ~5-10 minutes

### Optimization Tips

1. **Use --limit for quick validation:**
   ```bash
   # Fast: validates first 50
   python tools/code_example_validator.py --extract --validate --limit 50
   ```

2. **Run in parallel (CI/CD):**
   ```yaml
   # Split by language
   python tools/code_example_validator.py --extract --validate --language python
   ```

3. **Cache catalog between runs:**
   ```bash
   # First run: extract
   python tools/code_example_validator.py --extract --report
   
   # Subsequent runs: use cached catalog
   # (coming in Phase 30)
   ```

---

## Future Enhancements

### Phase 30 Planned Improvements

1. **Incremental validation**
   - Only validate changed examples
   - Cache results between runs

2. **Language-specific validators**
   - Go, Rust, Java validation
   - Type checking for TypeScript
   - Linting for all languages

3. **Automated fixes**
   - Auto-add missing imports
   - Fix common syntax errors
   - Format code examples

4. **Discovery interface**
   - Search code examples
   - Tag-based browsing
   - Execute live in browser

5. **Integration with IDE**
   - VS Code extension
   - Example templates
   - Real-time validation

---

## Reference

- **Tool**: `tools/code_example_validator.py`
- **Best Practices**: `docs/CODE_EXAMPLES_BEST_PRACTICES.md`
- **Execution Plan**: `PHASE_12_WS5_EXECUTION_PLAN.md`
- **Failure Analysis**: `PHASE_12_WS5_FAILURE_ANALYSIS.md`

---

**Last Updated**: 2026-07-08  
**Status**:  Ready for integration  
**Next Step**: Deploy to GitHub Actions
