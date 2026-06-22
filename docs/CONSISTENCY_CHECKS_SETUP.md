# Consistency Checks Setup Guide

This guide explains how to set up and use the CI/CD consistency checks for the _codex_ repository.

## Overview

The consistency checks system includes:

1. **Markdownlint** - Validates Markdown syntax and style consistency
2. **Cross-Reference Validator** - Checks internal links and anchors
3. **Heading Hierarchy Checker** - Ensures proper heading structure
4. **Pre-commit Hook** - Runs checks before each commit
5. **GitHub Actions Workflow** - Runs checks on PRs and pushes

## Installation

### Option 1: Automatic Setup (Recommended)

```bash
# From repository root
bash .github/scripts/install-consistency-hooks.sh
```

## Option 2: Manual Setup

### 1. Install Required Tools

**macOS (using Homebrew):**
```bash
brew install node
npm install -g markdownlint-cli
brew install yamllint
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install nodejs npm yamllint
npm install -g markdownlint-cli
```

**General (npm):**
```bash
npm install -g markdownlint-cli yamllint
```

#### 2. Install Pre-commit Hook

```bash
# Copy hook to .git/hooks/
cp .github/scripts/pre-commit-hook.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## Usage

**Note**: All commands in this section should be run from the **repository root** directory unless otherwise specified.

### Local Validation

#### Run Markdownlint

```bash
# Check all markdown files
markdownlint docs/*.md *.md

# Auto-fix issues
markdownlint --fix docs/*.md *.md

# Check specific file
markdownlint docs/my-doc.md
```

## Run Cross-Reference Checker

```bash
# Check all links (run from repository root)
python3 .github/scripts/check-cross-references.py --repo-root="."

# Generate JSON report
python3 .github/scripts/check-cross-references.py --repo-root="." --format=json

# GitHub Actions annotations
python3 .github/scripts/check-cross-references.py --github-annotations --fail-on-errors
```

## Run Heading Validator

```bash
# Via GitHub Actions (see workflow)
# Or manually using the Python script embedded in the workflow
```

## Pre-commit Hook

The pre-commit hook runs automatically before each commit and validates:

1. **Secrets** - Scans for potential secrets (requires gitleaks)
2. **Markdown Linting** - Validates Markdown syntax
3. **Cross-References** - Checks for broken links
4. **Python Code** - Formats and lints Python files
5. **YAML Files** - Validates YAML syntax

**Sample output:**
```
🔍 Running Pre-Commit Consistency Checks
════════════════════════════════════════════════════════════════════

[1/5] Scanning for secrets...
✓ No secrets detected

[2/5] Linting Markdown files...
✓ Markdown linting passed (5 files)

[3/5] Validating cross-references...
✓ All cross-references valid

[4/5] Checking Python files...
✓ Black formatting OK (2 files)
✓ Ruff linting OK

[5/5] Validating YAML files...
✓ YAML validation OK (3 files)

════════════════════════════════════════════════════════════════════
✓ All pre-commit checks passed!
```

**To bypass the hook (not recommended):**
```bash
git commit --no-verify
```

### GitHub Actions Workflow

The workflow runs automatically on:
- Push to `main` or `0D_base_` branches
- Pull requests to `main` or `0D_base_` branches
- Changes to documentation files

**Workflow file:** `../.github/workflows/consistency-checks.yml`

## Configuration

### Markdownlint Rules

Configuration file: `../.markdownlintrc`

Key rules enforced:
- **MD003**: Consistent heading style (atx: `#`, not underlines)
- **MD024**: Headings must not contain duplicate text (siblings only)
- **MD025**: Single H1 per document
- **MD041**: First heading must be H1
- **MD013**: Line length limit (120 chars, except code blocks)
- **Terminology**: Consistent terminology patterns
- **Alt text**: Images must have alt text

**To disable a rule:**
```json
{
  "MD025": false
}
```

### Cross-Reference Patterns

The checker validates:
- Internal file links: `[text](path/to/file.md)`
- Anchor references: `[text](file.md#anchor)`
- Relative paths: `../docs/file.md`
- Absolute repo paths: `/docs/file.md`

**Supported:**
- ✅ Relative paths
- ✅ Absolute repo paths
- ✅ Anchor references
- ✅ External URLs (HTTP/HTTPS)

**Skipped:**
- 🔄 External URLs (not fully validated)
- 🔄 Email links (mailto:)

### Heading Hierarchy Rules

All documents must follow:
1. ✅ First heading is H1 (`#`)
2. ✅ No hierarchy jumps (H1 → H3 invalid, must use H2)
3. ✅ Consistent nesting within documents
4. ✅ Unique headings within sections (MD024)

## Troubleshooting

### Issue: Pre-commit hook not running

**Solution:**
```bash
# Verify hook is executable
ls -la .git/hooks/pre-commit

# If not executable:
chmod +x .git/hooks/pre-commit
```

## Issue: Markdownlint not found

**Solution:**
```bash
npm install -g markdownlint-cli

# Or install locally
npm install --save-dev markdownlint-cli
npx markdownlint docs/*.md
```

## Issue: Broken links reported but files exist

**Possible causes:**
- Symlinks not resolved correctly
- Case sensitivity issues on case-insensitive filesystems
- Special characters in filenames

**Solution:**
```bash
# Check exact file path
ls -la path/to/file.md

# Verify anchor text matches heading exactly
grep "## My Heading" docs/file.md
```

## Issue: Too many warnings from cross-reference checker

**Solution:**
The checker reports external links as warnings. To ignore them:
```bash
python3 .github/scripts/check-cross-references.py --format=text | grep "❌ BROKEN"
```

## Common Errors & Fixes

### Markdownlint Errors

| Error | Fix |
|-------|-----|
| `MD003 - heading style` | Use `#` for all headings, not `===` underlines |
| `MD025 - single H1` | Ensure only one `#` heading per file |
| `MD041 - first heading` | First heading in file must be `# H1` |
| `MD013 - line length` | Keep lines under 120 characters |

### Cross-Reference Errors

| Error | Fix |
|-------|-----|
| `File not found` | Verify the file path is correct and relative |
| `Anchor not found` | Check anchor matches heading text exactly |
| `Case mismatch` | Use exact heading text for anchor |

### Heading Hierarchy Errors

| Error | Fix |
|-------|-----|
| `First heading should be H1` | Change first heading to `# Title` |
| `Hierarchy jump` | Add missing heading level(s) |

## CI/CD Integration

### GitHub Actions

The workflow file `.github/workflows/consistency-checks.yml` includes:

1. **Markdownlint Job** - Full repository scan
2. **Cross-References Job** - Link validation
3. **Heading Hierarchy Job** - Structure validation
4. **Summary Job** - Aggregates results

**PR Annotations:**
- Errors appear as ❌ annotations on PR
- Warnings appear as ⚠️ (external links)
- PR comments with detailed issues

**Artifacts:**
- Cross-reference reports (30-day retention)
- Workflow logs for debugging

### Status Checks

For merging PRs:
- ✅ All consistency checks must pass
- ⚠️ Warnings do not block merge
- 🔄 External link warnings are informational

## Best Practices

### Writing Documentation

1. **Start with H1:**
   ```markdown
   # Document Title
   
   ## Section
   ```

2. **Use consistent anchors:**
   ```markdown
   ## My Section
   [Link to section](#my-section)
   ```

3. **Verify internal links:**
   ```bash
   python3 .github/scripts/check-cross-references.py --fail-on-errors
   ```

4. **Keep line lengths reasonable:**
   - Max 120 characters
   - Code blocks exempt
   - Tables exempt

### Fixing Issues

1. **Run locally first:**
   ```bash
   markdownlint --fix docs/**/*.md
   python3 ../.github/scripts/check-cross-references.py
   ```

2. **Review changes:**
   ```bash
   git diff
   ```

3. **Stage and commit:**
   ```bash
   git add docs/
   git commit -m "docs: fix consistency issues"
   ```

## Disabling Checks (Not Recommended)

### Disable pre-commit hook for single commit:
```bash
git commit --no-verify
```

### Disable pre-commit hook permanently:
```bash
# Uninstall hook
rm .git/hooks/pre-commit
```

## Disable GitHub Actions workflow:
```yaml
# In .github/workflows/consistency-checks.yml
on:
  push:
    branches: []  # No branches trigger it
```

## Reporting Issues

If you encounter problems:

1. Check the troubleshooting section above
2. Run checks manually to get detailed output
3. Open an issue with:
   - Error message and stack trace
   - File(s) affected
   - Steps to reproduce
   - Output of consistency check

## Further Reading

- [Markdownlint Rules](https://github.com/DavidAnson/markdownlint/blob/main/README.md)
- [Repository Markdown Standards](../.markdownlintrc)
- [Cross-Reference Validator Source](../.github/scripts/check-cross-references.py)
- [Workflow Configuration](../.github/workflows/consistency-checks.yml)

## Support

For questions or issues:
- 📧 Contact: @mbaetiong
- 📝 Issues: Create GitHub issue with label `documentation`
- 🔍 Logs: Check GitHub Actions workflow runs for details
