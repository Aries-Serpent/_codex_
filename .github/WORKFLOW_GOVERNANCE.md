# GitHub Actions Workflow Governance Standards

**Document Version:** 1.0.0  
**Effective Date:** 2026-07-13  
**Phase:** 3 - Workflow Lifecycle Consolidation  
**Authority:** Workflow Management Agent  
**Status:** ✅ ACTIVE

---

## Table of Contents

1. [Overview](#overview)
2. [Workflow Classification](#workflow-classification)
3. [Mandatory Standards](#mandatory-standards)
4. [YAML Structure Requirements](#yaml-structure-requirements)
5. [Permissions & Security](#permissions--security)
6. [Concurrency & Cancellation](#concurrency--cancellation)
7. [Action Version Management](#action-version-management)
8. [Testing & Validation](#testing--validation)
9. [Monitoring & Health](#monitoring--health)
10. [Workflow Lifecycle](#workflow-lifecycle)
11. [Consolidation Strategy](#consolidation-strategy)
12. [Review & Approval](#review--approval)
13. [Troubleshooting](#troubleshooting)

---

## Overview

This document defines mandatory standards for all GitHub Actions workflows in the Aries-Serpent/_codex_ repository. Compliance is enforced via:

- **Pre-commit hooks** - Validate before staging
- **PR checks** - Actionlint validation on all workflow changes
- **Quarterly audits** - Compliance reporting
- **Automated enforcement** - `enforce_actions_versions.py` script

**Scope:** All files in `.github/workflows/` directory

**Non-Compliance:** Workflow files failing validation will be blocked from merging.

---

## Workflow Classification

### Active Workflows (Auto-Triggering)

**Trigger Patterns:**
- `push` (main/0D_base_ branches)
- `pull_request` (PR events)
- `schedule` (cron jobs)
- `workflow_dispatch` (manual trigger)
- Event-based: `issues`, `discussions`, `release`, etc.

**Requirements:**
- ✅ Production-ready
- ✅ Error handling implemented
- ✅ Tested and validated
- ✅ Owner documented
- ✅ Timeout configured

**Example:**
```yaml
name: CI Pipeline
on:
  push:
    branches: [main, 0D_base_]
    paths:
      - 'src/**'
      - '.github/workflows/ci-*.yml'
  pull_request:
    branches: [main, 0D_base_]
  schedule:
    - cron: '0 */4 * * *'  # Every 4 hours
```

### Dormant Workflows (Manual-Only)

**Trigger Pattern:**
- `workflow_dispatch` ONLY

**Purpose:**
- Ad-hoc diagnostics
- On-demand maintenance
- Experimental validations
- Force-retry scenarios

**Requirements:**
- ✅ No scheduled triggers
- ✅ Clear input documentation
- ✅ Owner/expert-only access (future: branch protection)
- ✅ Safety checks implemented

**Example:**
```yaml
name: Manual Diagnostics
on:
  workflow_dispatch:
    inputs:
      diagnostic_type:
        description: 'Type of diagnostic'
        required: true
        type: choice
        options:
          - cache-analysis
          - security-scan
          - performance-profile
```

### Archived Workflows (No Triggers)

**Location:** `.github/workflow-archive/disabled/`

**Requirements:**
- ✅ Never run automatically
- ✅ Preserved for reference
- ✅ Documented with archival reason
- ✅ Metadata file present

**Restoration:** See `.codex/ARCHIVED_WORKFLOWS_CATALOG.md`

---

## Mandatory Standards

### 1. File Naming

**Pattern:** `<category>-<function>[-<variant>].yml`

**Valid Examples:**
- ✅ `codeql-analysis.yml` (security category)
- ✅ `ci-pattern-healer.yml` (ci category)
- ✅ `pages-mkdocs.yml` (pages category)
- ✅ `security-scanning-suite.yml` (security suite)

**Invalid Examples:**
- ❌ `script.yml` (too generic)
- ❌ `agent_orchestration_unified.yml` (use hyphens, not underscores)
- ❌ `CI.yml` (uppercase not allowed)

**Categories:**
- `ci-` : CI/CD operations
- `security-` : Security scanning & gates
- `test-` : Testing workflows
- `deploy-` : Deployment & release
- `pages-` : GitHub Pages operations
- `doc-` : Documentation workflows
- `agent-` : Agent management & orchestration
- `cognitive-` : Cognitive/AI operations
- `data-` : Data quality & validation
- `performance-` : Performance monitoring
- `cache-` : Cache management
- `monitor-` : Health & monitoring

### 2. Required Metadata

Every workflow MUST include:

```yaml
name: Human-Readable Workflow Name

# Metadata block (comment)
# Purpose: Brief description (1-2 sentences)
# Owner: @responsible-person or team
# Category: ci|security|testing|deployment|documentation|other
# Critical: yes|no (if yes, requires special testing)
# Last Updated: YYYY-MM-DD

# Environment: production|staging|development
# Timeout: Expected max duration in minutes
```

**Example:**
```yaml
name: CodeQL Security Analysis

# Purpose: Run CodeQL analysis on code changes to detect vulnerabilities
# Owner: @security-team
# Category: security
# Critical: yes
# Last Updated: 2026-07-13
# Environment: production
# Timeout: 45
```

### 3. Workflow Structure

**Required Sections:**

```yaml
name: Workflow Name

# 1. Metadata block (comments)
# Purpose: ...

# 2. Triggers
on:
  push:
    branches: [main, 0D_base_]
  pull_request:
    branches: [main, 0D_base_]

# 3. Permissions (explicit, never use '*')
permissions:
  contents: read
  security-events: write
  pull-requests: write

# 4. Environment variables (if needed)
env:
  PYTHON_VERSION: '3.12'
  CI: true

# 5. Jobs
jobs:
  job-name:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    
    steps:
      # 6. Job steps
      - uses: actions/checkout@v5
      
      # ... other steps
```

**Forbidden Patterns:**
- ❌ No blank lines between section headers (e.g., `name:` and `on:`)
- ❌ Using `permissions: {}` (must be explicit)
- ❌ Hardcoded secrets in workflow files
- ❌ Using `runs-on: [self-hosted]` without approval

---

## YAML Structure Requirements

### 1. Indentation

**Rule:** 2 spaces per indentation level (NEVER tabs)

```yaml
# ✅ CORRECT
on:
  push:
    branches:
      - main
      - 0D_base_

# ❌ WRONG (using tabs)
on:
→	push:
→	→	branches:
```

### 2. String Handling

**Rule:** Use simple strings, avoid heredocs

```yaml
# ✅ CORRECT
script: |
  echo "Starting tests"
  pytest tests/

# ✅ ALSO CORRECT
run: pytest tests/ --cov=src --cov-report=xml

# ❌ WRONG (unnecessary complexity)
script: |
  cat << 'EOF'
  Complex heredoc
  EOF
```

### 3. Special Keywords

**Rule:** Quote keywords to avoid YAML interpretation

```yaml
# ✅ CORRECT
env:
  KEEP_GOING: 'yes'  # Quote boolean-like strings
  ACTION: 'on'       # Quote keyword-like strings

# ❌ WRONG (will be interpreted as boolean)
env:
  KEEP_GOING: yes    # Parsed as true
  ACTION: on         # Parsed as on (event trigger)
```

### 4. Validation

**Required:** All workflows must pass YAML validation

```bash
# Manual validation
python -m yaml .github/workflows/*.yml

# With actionlint (recommended)
actionlint .github/workflows/*.yml

# Automatic CI validation (on PR)
# See: pr-checks.yml
```

---

## Permissions & Security

### 1. Explicit Permission Declarations

**Rule:** Never use implicit permissions. Always declare explicitly.

```yaml
# ✅ CORRECT - Explicit permissions
permissions:
  contents: read           # Read repository contents
  pull-requests: write     # Write PR comments
  security-events: write   # Write security findings
  issues: read             # Read issue data

# ❌ WRONG - Implicit or overly broad
permissions:
  contents: write          # Writing to contents is rare
  
# ❌ WRONG - No permissions declaration
# (inherits from GitHub defaults, unclear)
```

### 2. Token Management

**Rule:** Use provided `secrets.GITHUB_TOKEN` unless special access required

```yaml
# ✅ CORRECT - Using GITHUB_TOKEN
- uses: actions/checkout@v5
  with:
    token: ${{ secrets.GITHUB_TOKEN }}

# ✅ ALSO CORRECT - Fallback for special access
- name: Use master key if available
  env:
    TOKEN: ${{ secrets.CODEX_MASTER_KEY || secrets.GITHUB_TOKEN }}
  run: |
    echo "::add-mask::$TOKEN"
    curl -H "Authorization: token $TOKEN" https://api.github.com/repos/Aries-Serpent/_codex_
```

### 3. Secret Handling

**Rule:** Never commit secrets. Use GitHub Secrets only.

```yaml
# ✅ CORRECT
env:
  API_KEY: ${{ secrets.API_KEY }}

# ❌ WRONG - Hardcoded secret
env:
  API_KEY: 'sk-12345678901234567890'

# ❌ WRONG - Secret in workflow file
with:
  token: '******'
```

### 4. Security Events

**Rule:** Only `security-events: write` for workflows writing security findings

```yaml
# ✅ CORRECT - Only CodeQL/SAST workflows write security events
jobs:
  security-scan:
    permissions:
      security-events: write
    steps:
      - uses: github/codeql-action/analyze@v3

# ❌ WRONG - Test workflows don't need security-events
jobs:
  tests:
    permissions:
      security-events: write  # Don't need this!
```

---

## Concurrency & Cancellation

### 1. Concurrency Groups

**Rule:** All workflows MUST define concurrency (except rare exceptions)

```yaml
# ✅ CORRECT - Standard pattern
concurrency:
  group: ${{ github.workflow }}-${{ github.head_ref || github.ref }}
  cancel-in-progress: true

# ✅ ALSO CORRECT - For matrix workflows
concurrency:
  group: ${{ github.workflow }}-${{ matrix.python-version }}-${{ github.head_ref || github.ref }}
  cancel-in-progress: true

# ✅ FOR SEQUENTIAL WORKFLOWS (don't cancel)
concurrency:
  group: ${{ github.workflow }}-${{ github.head_ref || github.ref }}
  cancel-in-progress: false

# ❌ WRONG - No concurrency control
# (allows unlimited parallel runs)
```

### 2. When NOT to Use Concurrency

**Exceptions** (rare):
- Deployment workflows (must run sequentially)
- Release workflows (production safety)
- Archive/cleanup operations

```yaml
# Deployment workflows: Sequential execution
concurrency:
  group: deployment-${{ github.ref }}
  cancel-in-progress: false  # Never cancel deployment in progress
```

### 3. Matrix Isolation

**Rule:** Use matrix index in concurrency group for proper isolation

```yaml
# ✅ CORRECT - Each matrix job gets own concurrency group
jobs:
  test:
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']
    concurrency:
      group: ${{ github.workflow }}-test-py${{ matrix.python-version }}-${{ github.head_ref || github.ref }}
      cancel-in-progress: true
```

---

## Action Version Management

### 1. Mandatory Action Versions

**Rule:** Use exact versions from pinned list. No version ranges.

**Currently Pinned:**
```
- actions/checkout@v5
- actions/setup-node@v5
- actions/setup-python@v6
- actions/github-script@v8
- actions/upload-artifact@v5
- github/codeql-action/*@v3
- actions/cache@v4
- docker/setup-buildx-action@v3
```

### 2. Usage Requirements

```yaml
# ✅ CORRECT - Exact version
- uses: actions/checkout@v5
- uses: actions/setup-python@v6
- uses: github/codeql-action/analyze@v3

# ❌ WRONG - Version ranges not allowed
- uses: actions/checkout@v5.*     # No range
- uses: actions/checkout@latest   # No floating tags

# ❌ WRONG - Unpinned versions
- uses: actions/checkout          # Must have version
```

### 3. Version Update Process

**Procedure:**
1. Update in `scripts/enforce_actions_versions.py`
2. Run: `python scripts/enforce_actions_versions.py`
3. Validates all workflows use correct versions
4. Can auto-fix or report-only (depending on flag)

```bash
# Check current versions
python scripts/enforce_actions_versions.py --check

# Auto-update all workflows
python scripts/enforce_actions_versions.py --update

# Report only (no changes)
python scripts/enforce_actions_versions.py --report
```

### 4. Action Version Policy

**Approval Required For:**
- Downgrading action versions (security concern)
- Using experimental/beta actions
- Custom/private actions (must be justified)

**No Approval Needed For:**
- Updating to newer patch version (v6.1 → v6.2)
- Using GitHub-recommended versions
- Updating in consolidation phase

---

## Testing & Validation

### 1. Pre-Commit Validation

**Rule:** All workflows must pass local validation before commit

```bash
# Install validation tools
pip install actionlint yamllint

# Validate before staging
actionlint .github/workflows/your-workflow.yml

# Fix issues
actionlint .github/workflows/ --fix
```

### 2. Workflow Timeout Configuration

**Rule:** Every job MUST have `timeout-minutes` set

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 30     # Must be present
    
    steps:
      - uses: actions/checkout@v5
```

**Recommended Timeouts:**
- Quick checks (lint, format): 5-10 minutes
- Unit tests: 20-30 minutes
- Integration tests: 30-45 minutes
- Security scans: 20-40 minutes
- Deployments: 15-30 minutes
- Long-running: 60-120 minutes (rare)

### 3. Error Handling

**Rule:** Jobs should handle failures gracefully

```yaml
# ✅ CORRECT - Explicit failure handling
jobs:
  analyze:
    steps:
      - uses: github/codeql-action/analyze@v3
        continue-on-error: true  # Optional: allow continuation
        if: always()              # Run regardless of previous steps
        
      - name: Upload results
        if: always()              # Always upload, even if analyze fails
        uses: actions/upload-artifact@v5
```

### 4. Validation Workflow

**Automatic on PR:**
- `actionlint` checks all workflow changes
- Syntax validation
- Version pinning validation
- Permission validation

**Result:** PR fails if any workflow is non-compliant

---

## Monitoring & Health

### 1. Success Rate Monitoring

**Target:** ≥95% workflow success rate

**Monitored By:** `ci-health-monitor.yml`

**Alert Threshold:** >10% failure rate over last 24 hours

### 2. CodeQL Special Monitoring

**Critical Metric:** CodeQL runs must succeed ≥99% of the time

**Monitoring:** `nightly-codeql-alert-triage.yml`

**Escalation:** Critical alert if CodeQL fails

### 3. Performance Monitoring

**Tracked Metrics:**
- Workflow execution time
- Cache hit rate
- Cost per workflow run
- Number of re-runs

**Monitoring:** `performance-gate.yml`

---

## Workflow Lifecycle

### 1. Workflow States

```
ACTIVE
  ↓ (disable workflow)
DISABLED (.disabled extension)
  ↓ (after 3-7 days)
ARCHIVED (moved to .github/workflow-archive/disabled/)
  ↓ (after 6-12 months)
DELETED (removed from archive)
```

### 2. From Active to Disabled

**When to disable:**
- Replacing with improved version
- Consolidating multiple workflows
- Security/compliance concerns
- Temporary pause needed

**How to disable:**
```bash
mv .github/workflows/workflow.yml .github/workflows/workflow.yml.disabled
```

**Required:** Document disable reason in YAML header

### 3. From Disabled to Archived

**Timeline:** After 3-7 days of disablement

**How to archive:**
```bash
mv .github/workflows/workflow.yml.disabled .github/workflow-archive/disabled/workflow.yml
```

**Required:** Create .meta file with archival metadata

### 4. Archival Metadata (.meta files)

```json
{
  "original_purpose": "Describe what the workflow did",
  "archived_date": "2026-07-13T16:15:52Z",
  "archived_reason": "CONSOLIDATION|SUPERSEDED|LEGACY|EXPERIMENTAL|OTHER",
  "phase_archived": "Phase 1|2|3|...",
  "replacement": "name-of-replacement-workflow.yml",
  "restoration_difficulty": "easy|medium|hard",
  "restoration_recommended": "yes|no",
  "last_execution": "2026-07-10T12:34:56Z",
  "execution_count": "234",
  "owner": "@original-owner",
  "notes": "Additional context for future reference"
}
```

### 5. Deletion Policy

**Safe to Delete:**
- Archived >12 months with no restoration requests
- Functionality completely replaced (confirmed via testing)
- Experimental workflows not referenced elsewhere

**Never Delete:**
- Without archival first (always archive first)
- Without checking git history for learn-ability
- During active debugging/troubleshooting

---

## Consolidation Strategy

### Phase 3 Consolidation Target: 238 → ~180 workflows (24% reduction)

**Consolidation Approach:** Mode-based unified workflows

```yaml
# EXAMPLE: Unified Security Suite
name: Security Scanning Suite

on:
  push:
    branches: [main, 0D_base_]
  pull_request:
    branches: [main, 0D_base_]
  workflow_dispatch:
    inputs:
      scan-type:
        description: 'Type of security scan'
        type: choice
        options:
          - codeql
          - secrets
          - dependencies
          - all
        default: 'all'

jobs:
  codeql:
    if: github.event.inputs.scan-type == 'codeql' || github.event.inputs.scan-type == 'all'
    runs-on: ubuntu-latest
    timeout-minutes: 30
    # ... codeql job steps
    
  secrets:
    if: github.event.inputs.scan-type == 'secrets' || github.event.inputs.scan-type == 'all'
    runs-on: ubuntu-latest
    timeout-minutes: 20
    # ... secrets job steps
```

**Benefits:**
- Reduced workflow file count (60+ eliminated)
- Simpler maintenance (centralized)
- Better error handling
- Clear job dependencies
- Easier monitoring

**Current Phase 3 Consolidations:**
- Security scanning: 12 → 4 workflows
- Testing: 8 → 3 workflows
- Deployment: 7 → 2 workflows
- Monitoring: 10 → 3 workflows
- Documentation: 8 → 3 workflows
- Agents: 6 → 2 workflows

---

## Review & Approval

### 1. Mandatory Review

**All workflow changes require:**
- ✅ Code review (minimum 1 approval)
- ✅ `actionlint` validation pass
- ✅ No hardcoded secrets

### 2. Consolidation Reviews

**Extra requirements for consolidation PRs:**
- ✅ Deduplication analysis documented
- ✅ All jobs tested independently
- ✅ No breaking changes to triggers
- ✅ Error handling verified
- ✅ Performance metrics provided

### 3. Security Review

**Triggered for workflows that:**
- Write to security events
- Access secrets
- Modify permissions
- Deploy to production

---

## Troubleshooting

### Issue: "Workflow syntax is invalid"

**Cause:** YAML indentation or syntax error

**Solution:**
```bash
actionlint .github/workflows/workflow.yml --fix
```

### Issue: "Unexpected action version"

**Cause:** Using unpinned or wrong version

**Solution:**
1. Check `.codex/enforce_actions_versions.py` for correct version
2. Update to correct version
3. Run: `python scripts/enforce_actions_versions.py --update`

### Issue: "Permission denied" in workflow

**Cause:** Missing or insufficient permissions

**Solution:**
```yaml
permissions:
  contents: read
  # Add needed permission
  pull-requests: write
```

### Issue: Workflow runs forever / times out

**Cause:** Missing `timeout-minutes` or infinite loop

**Solution:**
```yaml
timeout-minutes: 30
```

### Issue: Concurrency group conflicts

**Cause:** Multiple workflows use same concurrency group

**Solution:**
- Make concurrency group more specific
- Add matrix variable to group name
- Add workflow name to group identifier

---

## Related Documents

- `.codex/PHASE_3_DEDUPLICATION_ANALYSIS.md` - Consolidation strategy
- `.codex/PHASE_3_DISABLED_AUDIT.md` - Disabled workflow decisions
- `.codex/ARCHIVED_WORKFLOWS_CATALOG.md` - Archive management
- `.codex/restore_workflow.sh` - Restoration tool

---

## Compliance Checklist

Use this checklist for new or modified workflows:

```
Workflow Governance Compliance Checklist
========================================

File Naming:
  ☐ Uses hyphen-separated naming: <category>-<function>[-<variant>].yml
  ☐ Category is valid (ci, security, test, deploy, pages, doc, etc.)
  ☐ Filename is lowercase
  ☐ No underscores (use hyphens)

Metadata:
  ☐ Includes 'name' field
  ☐ Includes 'Purpose' comment
  ☐ Includes 'Owner' comment
  ☐ Includes 'Category' comment
  ☐ Includes 'Critical' designation
  ☐ Includes 'Last Updated' date

Structure:
  ☐ Contains all required sections (name, on, permissions, jobs)
  ☐ Uses 2-space indentation consistently
  ☐ No tabs in YAML
  ☐ Quotes special keywords (yes, no, on, off, true, false)

Permissions:
  ☐ Permissions section is explicit (not empty)
  ☐ Uses GITHUB_TOKEN by default
  ☐ No hardcoded secrets
  ☐ Only security-events: write when necessary

Concurrency:
  ☐ Defines concurrency group
  ☐ Sets cancel-in-progress appropriately
  ☐ Includes workflow name and ref
  ☐ Includes matrix variables if applicable

Actions:
  ☐ All actions use pinned versions
  ☐ Versions match enforce_actions_versions.py list
  ☐ No floating tags (latest, main, etc.)
  ☐ No version ranges

Testing:
  ☐ All jobs have timeout-minutes
  ☐ Timeout is reasonable for job purpose
  ☐ Error handling implemented
  ☐ Uses 'if' conditions for optional steps

Validation:
  ☐ Passes actionlint: actionlint .github/workflows/workflow.yml
  ☐ Passes YAML validation
  ☐ No secrets exposed
  ☐ Tested in staging first

Documentation:
  ☐ Purpose is clear and specific
  ☐ Owner is current and responsive
  ☐ Triggers are well-documented
  ☐ Any special requirements noted
```

---

**Document Authority:** Workflow Management Agent  
**Last Updated:** 2026-07-13  
**Effective Until:** Until superseded by newer governance version  
**Contact:** @mbaetiong (for questions/clarifications)

---

## Appendix: Quick Reference

### File Structure Template

```yaml
name: Brief Workflow Name

# Purpose: What this workflow does (1-2 sentences)
# Owner: @responsible-team-or-person
# Category: ci|security|testing|deployment|documentation|other
# Critical: yes|no
# Last Updated: 2026-07-13

on:
  push:
    branches: [main, 0D_base_]
  pull_request:
    branches: [main, 0D_base_]

permissions:
  contents: read

concurrency:
  group: ${{ github.workflow }}-${{ github.head_ref || github.ref }}
  cancel-in-progress: true

jobs:
  job-name:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    
    steps:
      - uses: actions/checkout@v5
      
      - name: Step description
        run: echo "Hello, workflow!"
```

### Common Action Versions

```yaml
# Checkout
- uses: actions/checkout@v5

# Setup Python (cached)
- uses: ./.github/actions/setup-python-cached@main

# GitHub Script
- uses: actions/github-script@v8

# Upload Artifact
- uses: actions/upload-artifact@v5

# CodeQL
- uses: github/codeql-action/init@v3
- uses: github/codeql-action/analyze@v3

# Cache
- uses: actions/cache@v4
```

---

**Status:** ✅ COMPLETE & ACTIVE  
**Governance Authority:** Phase 3 consolidation authority  
**Next Review:** 2026-10-13 (quarterly)
