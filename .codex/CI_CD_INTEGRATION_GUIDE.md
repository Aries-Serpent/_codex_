# Documentation Quality CI/CD Integration

**Version:** 1.0  
**Last Updated:** 2026-07-08  
**Purpose:** Automate documentation quality checks in CI/CD pipeline

---

## Overview

This guide explains how to integrate documentation quality checks into your CI/CD pipeline. The automation ensures:

- ✅ All markdown follows style guide standards
- ✅ Internal links are valid
- ✅ Code examples are properly formatted
- ✅ Documentation is kept current

---

## Local Setup

### Prerequisites

```bash
# Node.js & npm (required)
node --version  # v16+
npm --version   # v8+

# Python 3.10+
python3 --version
```

### Install Local Tools

```bash
# Install markdownlint
npm install -g markdownlint-cli

# Install markdown-link-check
npm install -g markdown-link-check

# Install MkDocs
pip install mkdocs mkdocs-material mkdocs-mermaid2-plugin
```

### Configure Tools

**`.markdownlint.json` (already created):**
```json
{
  "default": true,
  "MD001": true,
  "MD003": { "style": "consistent" },
  "MD013": { "line_length": 120 }
}
```

**Markdown Link Check Config (create `.markdown-link-check.json`):**
```json
{
  "timeout": "5000",
  "retryOn": [429],
  "retryCount": 3,
  "ignorePatterns": [
    {
      "pattern": "^https://localhost"
    },
    {
      "pattern": "^https://example.com"
    }
  ]
}
```

---

## Local Testing

### Test Markdown Compliance

```bash
# Check all docs
markdownlint 'docs/**/*.md'

# Check specific file
markdownlint docs/README.md

# Fix automatically
markdownlint --fix 'docs/**/*.md'

# View rules
markdownlint --list-rules
```

### Test Links

```bash
# Check all links
markdown-link-check 'docs/**/*.md'

# Check specific file
markdown-link-check docs/README.md

# Verbose output
markdown-link-check --verbose 'docs/**/*.md'
```

### Test MkDocs Build

```bash
# Build locally
mkdocs build

# Build with strict mode (fail on warnings)
mkdocs build --strict

# Serve locally for preview
mkdocs serve
```

---

## GitHub Actions Workflow

Create `.github/workflows/docs-quality.yml`:

```yaml
name: Documentation Quality

on:
  push:
    paths:
      - 'docs/**'
      - '.markdownlint.json'
  pull_request:
    paths:
      - 'docs/**'
      - '.markdownlint.json'

jobs:
  markdown-lint:
    runs-on: ubuntu-latest
    name: Markdown Linting
    steps:
      - uses: actions/checkout@v4
      
      - name: Install markdownlint
        run: npm install -g markdownlint-cli
      
      - name: Check markdown compliance
        run: markdownlint 'docs/**/*.md'
      
      - name: Report results
        if: always()
        run: echo "✅ Markdown linting complete"

  link-check:
    runs-on: ubuntu-latest
    name: Link Validation
    steps:
      - uses: actions/checkout@v4
      
      - name: Check links
        run: |
          npm install -g markdown-link-check
          markdown-link-check 'docs/**/*.md'

  mkdocs-build:
    runs-on: ubuntu-latest
    name: MkDocs Build
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r requirements-dev.txt
          pip install mkdocs mkdocs-material mkdocs-mermaid2-plugin
      
      - name: Build documentation
        run: mkdocs build --strict
      
      - name: Upload site artifact
        uses: actions/upload-artifact@v3
        with:
          name: mkdocs-site
          path: site/
```

---

## GitHub Actions: PR Comment Feedback

Create `.github/workflows/docs-feedback.yml` to comment on PRs:

```yaml
name: Documentation Feedback

on:
  pull_request:
    paths:
      - 'docs/**'

jobs:
  quality-feedback:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v3
      
      - name: Install tools
        run: |
          npm install -g markdownlint-cli markdown-link-check
          pip install mkdocs mkdocs-material
      
      - name: Run checks
        id: checks
        run: |
          echo "## Documentation Quality Report" > report.md
          echo "" >> report.md
          
          echo "### Markdown Linting" >> report.md
          if markdownlint 'docs/**/*.md' >> /tmp/lint.txt 2>&1; then
            echo "✅ All files comply" >> report.md
          else
            echo "❌ Linting errors:" >> report.md
            cat /tmp/lint.txt >> report.md
          fi
          echo "" >> report.md
          
          echo "### MkDocs Build" >> report.md
          if mkdocs build --strict 2>&1 | grep -i error; then
            echo "❌ Build failed" >> report.md
          else
            echo "✅ Build successful" >> report.md
          fi
      
      - name: Comment on PR
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const report = fs.readFileSync('report.md', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: report
            });
```

---

## Pre-Commit Hook (Local)

Create `.pre-commit-config.yaml` entry:

```yaml
repos:
  - repo: https://github.com/igorshubovych/markdownlint-cli
    rev: v0.34.0
    hooks:
      - id: markdownlint
        args: ['--fix']

  - repo: https://github.com/tcort/markdown-link-check
    rev: v3.11.2
    hooks:
      - id: markdown-link-check
```

---

## Scheduled Checks

Create `.github/workflows/docs-scheduled.yml` for weekly audits:

```yaml
name: Documentation Audit (Weekly)

on:
  schedule:
    # Every Monday at 9 AM UTC
    - cron: '0 9 * * 1'

jobs:
  full-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run full checks
        run: |
          npm install -g markdownlint-cli markdown-link-check
          pip install mkdocs mkdocs-material
          
          echo "=== Markdown Linting ===" 
          markdownlint 'docs/**/*.md'
          
          echo -e "\n=== Link Checking ==="
          markdown-link-check 'docs/**/*.md' --verbose
          
          echo -e "\n=== MkDocs Build ==="
          mkdocs build --strict
      
      - name: Create issue if failures
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: '📚 Documentation Audit Issues',
              body: 'Weekly documentation audit found issues. See workflow logs.'
            });
```

---

## Manual CLI Testing

### Full Audit Command

```bash
#!/bin/bash
# Save as scripts/audit-docs.sh

set -e

echo "🔍 Starting documentation audit..."
echo ""

echo "1️⃣ Checking markdown compliance..."
markdownlint 'docs/**/*.md'
echo "✅ Markdown compliance passed"
echo ""

echo "2️⃣ Validating links..."
markdown-link-check 'docs/**/*.md'
echo "✅ Links validated"
echo ""

echo "3️⃣ Building MkDocs..."
mkdocs build --strict
echo "✅ MkDocs build successful"
echo ""

echo "🎉 Documentation audit complete!"
```

Run with:
```bash
bash scripts/audit-docs.sh
```

---

## Enforcement Strategy

### PR Requirements

Configure branch protection rules:

1. **Require status checks:** 
   - `docs-quality / markdown-lint`
   - `docs-quality / link-check`
   - `docs-quality / mkdocs-build`

2. **Require reviews:** 1 approving review

3. **Dismiss stale reviews:** When new commits pushed

### CI Status Page

Add to `docs/README.md`:

```markdown
## Documentation Status

| Check | Status |
|-------|--------|
| Markdown Compliance | [![Markdown Lint](https://github.com/.../actions/workflows/docs-quality.yml/badge.svg)](...) |
| Link Validity | [![Links](https://github.com/.../actions/workflows/docs-quality.yml/badge.svg)](...) |
| MkDocs Build | [![Build](https://github.com/.../actions/workflows/docs-quality.yml/badge.svg)](...) |
```

---

## Failure Diagnosis

### Markdown Linting Failures

**Issue:** `MD001: Multiple H1 headers`

```bash
# Find all H1 headers
grep '^# ' docs/README.md

# Fix: Keep only first one
```

**Issue:** `MD013: Line too long`

```bash
# Find long lines
markdownlint docs/README.md | grep MD013

# Fix: Break into multiple lines or code blocks
```

### Link Check Failures

**Issue:** `404 not found`

```bash
# Check if file exists
ls docs/path/to/file.md

# Fix: Use correct relative path
# Old: ../docs/README.md
# New: ../../README.md
```

**Issue:** `Timeout`

```bash
# Increase timeout in .markdown-link-check.json
{
  "timeout": "10000",  # 10 seconds
  "retryCount": 5
}
```

### MkDocs Build Failures

**Issue:** `ERROR: Page not found in nav`

```bash
# File exists but not in mkdocs.yml
# Fix: Add to nav in mkdocs.yml
```

**Issue:** `ERROR: Invalid YAML`

```bash
# Check YAML syntax
python3 -c "import yaml; yaml.safe_load(open('mkdocs.yml'))"
```

---

## Performance Optimization

### Parallel Checks

Run checks in parallel for speed:

```yaml
jobs:
  checks:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        check: [lint, links, build]
    steps:
      - uses: actions/checkout@v4
      - name: Run check
        run: |
          if [ "${{ matrix.check }}" == "lint" ]; then
            markdownlint 'docs/**/*.md'
          elif [ "${{ matrix.check }}" == "links" ]; then
            markdown-link-check 'docs/**/*.md'
          else
            mkdocs build --strict
          fi
```

### Skip Non-Doc Changes

Only run on doc file changes:

```yaml
on:
  pull_request:
    paths:
      - 'docs/**'        # Only if docs/ changes
      - '.markdownlint.json'
      - 'mkdocs.yml'
```

---

## Reporting & Metrics

### Weekly Summary Report

Create report with metrics:

```bash
#!/bin/bash
# scripts/generate-docs-report.sh

TOTAL_FILES=$(find docs -name "*.md" | wc -l)
LINT_ERRORS=$(markdownlint 'docs/**/*.md' 2>&1 | wc -l)
BROKEN_LINKS=$(markdown-link-check 'docs/**/*.md' 2>&1 | grep -c "ERROR" || true)

echo "📊 Documentation Quality Report"
echo "================================"
echo "Total Files: $TOTAL_FILES"
echo "Lint Errors: $LINT_ERRORS"
echo "Broken Links: $BROKEN_LINKS"
echo ""
echo "Quality Score: $(( 100 - LINT_ERRORS - (BROKEN_LINKS * 5) ))%"
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Workflow not triggering | Check `on:` paths match doc changes |
| Linting too strict | Adjust `.markdownlint.json` rules |
| Link check timeout | Increase timeout in config |
| MkDocs missing theme | Add to requirements: `mkdocs-material` |
| Permission denied | Add `permissions:` to workflow |

---

## Next Steps

1. ✅ Copy `.markdownlint.json` to repo root
2. ✅ Create `.github/workflows/docs-quality.yml`
3. ✅ Test locally: `bash scripts/audit-docs.sh`
4. ✅ Push and verify PR checks pass
5. ✅ Configure branch protection
6. ✅ Add status badges to README

---

*Documentation quality automation is now live! 🚀*
