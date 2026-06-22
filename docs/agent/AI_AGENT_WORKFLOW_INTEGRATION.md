# AI Agent Integration Guide for Consolidated Workflows

**Last Updated:** 2026-06-22

## Overview

This guide explains how AI agents can effectively use the new consolidated workflow suites. All consolidated workflows support `workflow_call` for programmatic invocation with fine-grained control.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Available Workflows](#available-workflows)
3. [Integration Patterns](#integration-patterns)
4. [Advanced Usage](#advanced-usage)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

## Quick Start

### Basic Workflow Invocation

```yaml
# In your AI agent workflow
jobs:
  invoke-test-suite:
    uses: ./.github/workflows/test-suite.yml
    with:
      test-scope: core
      python-version: '3.12'
```

### With Permissions

```yaml
jobs:
  invoke-security-scan:
    permissions:
      contents: read
      security-events: write
    uses: ./.github/workflows/security-scanning-suite.yml
    with:
      scan-type: codeql
```

## Available Workflows

### 1. Cache Management Suite

**File:** `.github/workflows/cache-suite.yml`

**Purpose:** Manage cache operations (warmup, cleanup, analysis)

**Inputs:**
```yaml
with:
  operation: 'warmup'  # Options: all, warmup, cleanup, management, validate
  dry-run: false       # Boolean: preview changes without executing
```

**Use Cases:**
- Pre-warm cache before expensive operations
- Clean up old caches to free space
- Validate cache health before critical workflows

**Example:**
```yaml
jobs:
  warm-cache:
    uses: ./.github/workflows/cache-suite.yml
    with:
      operation: 'warmup'
      dry-run: false
```

### 2. Testing Suite

**File:** `.github/workflows/test-suite.yml`

**Purpose:** Run comprehensive tests with selective scopes

**Inputs:**
```yaml
with:
  test-scope: 'core'       # Options: all, core, rag, auth, integration, determinism
  python-version: '3.12'   # Python version to use
```

**Use Cases:**
- Run targeted tests after code changes
- Validate specific functionality
- Quick feedback during development

**Example:**
```yaml
jobs:
  test-auth-changes:
    uses: ./.github/workflows/test-suite.yml
    with:
      test-scope: 'auth'
      python-version: '3.12'
```

### 3. CI/CD Health Suite

**File:** `.github/workflows/ci-health-suite.yml`

**Purpose:** Monitor CI/CD health and diagnose issues

**Inputs:**
```yaml
with:
  operation: 'health-monitor'  # Options: all, health-monitor, diagnostics, artifact-check, runner-check
```

**Use Cases:**
- Check workflow health before major operations
- Diagnose CI issues
- Monitor artifact expiration

**Example:**
```yaml
jobs:
  check-ci-health:
    uses: ./.github/workflows/ci-health-suite.yml
    with:
      operation: 'health-monitor'
```

### 4. Security Scanning Suite

**File:** `.github/workflows/security-scanning-suite.yml`

**Purpose:** Comprehensive security scanning

**Inputs:**
```yaml
with:
  scan-type: 'codeql'  # Options: all, codeql, semgrep, dependency, secrets, sbom
```

**Use Cases:**
- Security validation before deployment
- Targeted scans after dependency updates
- Compliance reporting

**Example:**
```yaml
jobs:
  security-check:
    permissions:
      contents: read
      security-events: write
    uses: ./.github/workflows/security-scanning-suite.yml
    with:
      scan-type: 'dependency'
```

### 5. Documentation Suite

**File:** `.github/workflows/documentation-suite.yml`

**Purpose:** Build, validate, and deploy documentation

**Inputs:**
```yaml
with:
  operation: 'build'      # Options: all, build, deploy, api-docs, link-check, wiki
  strict-mode: false      # Boolean: fail on warnings
```

**Use Cases:**
- Validate documentation before PR merge
- Generate API documentation
- Check for broken links

**Example:**
```yaml
jobs:
  validate-docs:
    uses: ./.github/workflows/documentation-suite.yml
    with:
      operation: 'link-check'
      strict-mode: false
```

## Integration Patterns

### Pattern 1: Sequential Execution

Execute workflows in sequence, each depending on the previous:

```yaml
jobs:
  warm-cache:
    uses: ./.github/workflows/cache-suite.yml
    with:
      operation: 'warmup'

  run-tests:
    needs: warm-cache
    uses: ./.github/workflows/test-suite.yml
    with:
      test-scope: 'all'

  security-scan:
    needs: run-tests
    uses: ./.github/workflows/security-scanning-suite.yml
    with:
      scan-type: 'all'
```

### Pattern 2: Parallel Execution

Run multiple scopes simultaneously for faster feedback:

```yaml
jobs:
  test-core:
    uses: ./.github/workflows/test-suite.yml
    with:
      test-scope: 'core'

  test-auth:
    uses: ./.github/workflows/test-suite.yml
    with:
      test-scope: 'auth'

  test-rag:
    uses: ./.github/workflows/test-suite.yml
    with:
      test-scope: 'rag'
```

### Pattern 3: Conditional Execution

Execute workflows based on conditions:

```yaml
jobs:
  check-changes:
    runs-on: ubuntu-latest
    outputs:
      has-python: ${{ steps.changes.outputs.python }}
      has-docs: ${{ steps.changes.outputs.docs }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v3
        id: changes
        with:
          filters: |
            python:
              - 'src/**/*.py'
            docs:
              - 'docs/**'

  test-python:
    needs: check-changes
    if: needs.check-changes.outputs.has-python == 'true'
    uses: ./.github/workflows/test-suite.yml
    with:
      test-scope: 'core'

  validate-docs:
    needs: check-changes
    if: needs.check-changes.outputs.has-docs == 'true'
    uses: ./.github/workflows/documentation-suite.yml
    with:
      operation: 'link-check'
```

### Pattern 4: Error Handling

Handle failures gracefully:

```yaml
jobs:
  run-tests:
    uses: ./.github/workflows/test-suite.yml
    with:
      test-scope: 'all'

  handle-failure:
    needs: run-tests
    if: failure()
    runs-on: ubuntu-latest
    steps:
      - name: Create issue on failure
        uses: actions/github-script@v7
        with:
          script: |
            await github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: 'Test Suite Failed',
              body: 'The test suite failed. Please investigate.',
              labels: ['test-failure', 'automated']
            })
```

### Pattern 5: Chained Workflows

Chain multiple suites for comprehensive validation:

```yaml
jobs:
  # Stage 1: Preparation
  warmup:
    uses: ./.github/workflows/cache-suite.yml
    with:
      operation: 'warmup'

  # Stage 2: Quality Checks
  tests:
    needs: warmup
    uses: ./.github/workflows/test-suite.yml
    with:
      test-scope: 'all'

  security:
    needs: warmup
    uses: ./.github/workflows/security-scanning-suite.yml
    with:
      scan-type: 'all'

  docs:
    needs: warmup
    uses: ./.github/workflows/documentation-suite.yml
    with:
      operation: 'build'

  # Stage 3: Health Check
  ci-health:
    needs: [tests, security, docs]
    if: always()
    uses: ./.github/workflows/ci-health-suite.yml
    with:
      operation: 'all'
```

## Advanced Usage

### Dynamic Input Selection

Use expressions to dynamically select inputs:

```yaml
jobs:
  adaptive-tests:
    uses: ./.github/workflows/test-suite.yml
    with:
      test-scope: ${{ github.event.pull_request.draft && 'core' || 'all' }}
      python-version: ${{ matrix.python-version }}
    strategy:
      matrix:
        python-version: ['3.12']
```

### Secrets Passing

Pass secrets to called workflows:

```yaml
jobs:
  secure-scan:
    uses: ./.github/workflows/security-scanning-suite.yml
    secrets: inherit  # Pass all secrets
    with:
      scan-type: 'all'
```

### Output Consumption

Use outputs from called workflows:

```yaml
jobs:
  run-tests:
    uses: ./.github/workflows/test-suite.yml
    with:
      test-scope: 'core'

  process-results:
    needs: run-tests
    runs-on: ubuntu-latest
    steps:
      - name: Process test results
        run: |
          echo "Tests completed with status: ${{ needs.run-tests.result }}"
```

## Best Practices

### 1. Cache Warmup Before Expensive Operations

Always warm cache before running multiple workflows:

```yaml
jobs:
  prepare:
    uses: ./.github/workflows/cache-suite.yml
    with:
      operation: 'warmup'

  expensive-operation:
    needs: prepare
    uses: ./.github/workflows/test-suite.yml
    with:
      test-scope: 'all'
```

### 2. Use Selective Scopes

Don't run everything if you don't need to:

```yaml
# ❌ Bad: Always runs all tests
jobs:
  tests:
    uses: ./.github/workflows/test-suite.yml
    with:
      test-scope: 'all'

# ✅ Good: Only runs relevant tests
jobs:
  tests:
    uses: ./.github/workflows/test-suite.yml
    with:
      test-scope: ${{ contains(github.event.pull_request.labels.*.name, 'rag') && 'rag' || 'core' }}
```

### 3. Parallel When Possible

Run independent operations in parallel:

```yaml
# ✅ Good: Parallel execution
jobs:
  tests:
    uses: ./.github/workflows/test-suite.yml
    with:
      test-scope: 'core'

  security:
    uses: ./.github/workflows/security-scanning-suite.yml
    with:
      scan-type: 'codeql'
```

### 4. Handle Failures Gracefully

Always plan for failure scenarios:

```yaml
jobs:
  critical-tests:
    uses: ./.github/workflows/test-suite.yml
    with:
      test-scope: 'core'

  optional-tests:
    uses: ./.github/workflows/test-suite.yml
    with:
      test-scope: 'rag'
    continue-on-error: true

  always-run:
    needs: [critical-tests, optional-tests]
    if: always()
    uses: ./.github/workflows/ci-health-suite.yml
    with:
      operation: 'health-monitor'
```

### 5. Use Appropriate Permissions

Grant only necessary permissions:

```yaml
jobs:
  readonly-test:
    permissions:
      contents: read
    uses: ./.github/workflows/test-suite.yml
    with:
      test-scope: 'core'

  security-scan:
    permissions:
      contents: read
      security-events: write
    uses: ./.github/workflows/security-scanning-suite.yml
    with:
      scan-type: 'codeql'
```

## Troubleshooting

### Issue: Workflow not found

**Error:** `Could not resolve to a repository/workflow`

**Solution:** Ensure you're using the correct path:
```yaml
# ✅ Correct
uses: ./.github/workflows/test-suite.yml

# ❌ Wrong
uses: test-suite.yml
```

### Issue: Permission denied

**Error:** `Resource not accessible by integration`

**Solution:** Add required permissions:
```yaml
jobs:
  my-job:
    permissions:
      contents: read
      security-events: write
    uses: ./.github/workflows/security-scanning-suite.yml
```

### Issue: Cache miss

**Problem:** Cache is not being hit, workflows are slow

**Solution:** Run cache warmup first:
```yaml
jobs:
  warmup:
    uses: ./.github/workflows/cache-suite.yml
    with:
      operation: 'warmup'

  tests:
    needs: warmup
    uses: ./.github/workflows/test-suite.yml
```

### Issue: Workflow takes too long

**Problem:** Workflow is slower than expected

**Solution:** Use selective scopes and parallel execution:
```yaml
jobs:
  quick-tests:
    strategy:
      matrix:
        scope: ['core', 'auth', 'rag']
    uses: ./.github/workflows/test-suite.yml
    with:
      test-scope: ${{ matrix.scope }}
```

## Support

For issues or questions:
1. Check workflow run logs for detailed error messages
2. Review CONSOLIDATION_GUIDE.md
3. Use CI Health Suite to diagnose issues
4. Create an issue with `workflow-consolidation` label

---

**Last Updated:** 2026-01-26
**Version:** 1.0.0
**Maintained by:** @mbaetiong
