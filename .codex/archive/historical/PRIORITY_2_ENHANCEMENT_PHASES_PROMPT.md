# Next Session: Priority 2 Enhancement Phases - Continuation Prompt

> **For Next Copilot Agent Session**  
> **Repository:** Aries-Serpent/_codex_  
> **Branch:** copilot/sub-pr-2705-again (or new branch)  
> **Prerequisites:** All Priority 1 tasks complete (100% test pass rate achieved)

---

## Context from Previous Session

**Previous Session Summary:**
- ✅ Achieved 100% test pass rate (14/14 unit tests passing)
- ✅ Created 26 E2E tests (ready for execution)
- ✅ Comprehensive documentation delivered (125KB)
- ✅ All code review feedback addressed
- ✅ Security analysis complete (8 alerts resolved)

**Session Date:** 2026-01-06T06:35:00Z  
**PR Number:** #2711  
**Status:** Ready for Priority 2 enhancement phases

---

## @copilot Execute Priority 2 Enhancement Phases

Continue with the following comprehensive task list to complete all enhancement phases for the cognitive app testing infrastructure and repository optimization:

## PRIORITY 2: Enhancement Phases Implementation

### Phase 1: Execute E2E Test Suite with Playwright

**Status:** 26 E2E test scenarios created, ready for execution

**Objective:** Validate all end-to-end user workflows in real browser environments

#### Implementation Steps

```bash
cd /home/runner/work/_codex_/_codex_/cognitive_app

# Step 1: Install Playwright with browsers
npm install --save-dev @playwright/test
npx playwright install --with-deps chromium firefox webkit

# Step 2: Create Playwright configuration (if not exists)
# File: playwright.config.ts
```

**Create `playwright.config.ts`:**
```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:5000',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5000',
    reuseExistingServer: !process.env.CI,
  },
});
```

**Step 3: Run E2E Tests**
```bash
# Run all E2E tests
npx playwright test e2e/code-generator-lazy-init.spec.ts

# Run with UI mode for debugging
npx playwright test e2e/code-generator-lazy-init.spec.ts --ui

# Run specific browser
npx playwright test e2e/code-generator-lazy-init.spec.ts --project=chromium

# Generate HTML report
npx playwright show-report
```

**Expected Results:**
- 26 E2E scenarios executed across 3 browsers (78 total tests)
- HTML report generated in `playwright-report/`
- Screenshots captured for failures
- Traces available for debugging

**Acceptance Criteria:**
- [ ] All 26 scenarios pass in Chromium
- [ ] All 26 scenarios pass in Firefox
- [ ] All 26 scenarios pass in WebKit
- [ ] E2E test execution report created
- [ ] Any failures documented with screenshots
- [ ] Update `reports/e2e_test_execution_results_2026-01-06.md`

**Estimated Time:** 1-2 hours

---

### Phase 2: Link Checker - Per-Folder Checksum Caching

**Status:** Phase 1 documentation complete, implementation pending

**Objective:** Implement SHA-1 checksum-based caching to skip link checking when files haven't changed

#### Background

**Current State:** 
- Check-links workflow runs on all markdown files every time
- Slow execution when no changes made
- Wastes CI/CD resources

**Target State:**
- Compute aggregate checksum of tracked files
- Use checksum as cache key
- Skip link checking if cache hit
- Fast skip when nothing changed (< 5 seconds vs 5+ minutes)

#### Implementation Steps

**Step 1: Create Checksum Computation Script**

Create `.github/scripts/compute-checksum.sh`:

```bash
#!/bin/bash
# compute-checksum.sh - Compute SHA-1 checksum for link checker caching
# Usage: ./compute-checksum.sh <directory> [file-pattern]

set -e

DIRECTORY="${1:-.}"
PATTERN="${2:-*.md}"

echo "Computing checksum for ${PATTERN} files in ${DIRECTORY}..." >&2

# Find all matching files, sort for consistency, compute combined checksum
find "${DIRECTORY}" -type f -name "${PATTERN}" -print0 | \
  sort -z | \
  xargs -0 cat | \
  sha1sum | \
  awk '{print $1}'
```

**Make executable:**
```bash
chmod +x .github/scripts/compute-checksum.sh
```

**Step 2: Update Check-Links Workflow**

Edit `.github/workflows/check-links.yml`:

```yaml
name: Check Links

on:
  pull_request:
    paths:
      - '**.md'
  push:
    branches: [main]
    paths:
      - '**.md'
  workflow_dispatch:
  schedule:
    - cron: '0 0 * * 0' # Weekly on Sunday

jobs:
  check-links:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      # NEW: Compute checksum for caching
      - name: Compute file checksum
        id: checksum
        run: |
          CHECKSUM=$(bash .github/scripts/compute-checksum.sh . "*.md")
          echo "checksum=${CHECKSUM}" >> $GITHUB_OUTPUT
          echo "Computed checksum: ${CHECKSUM}"
      
      # NEW: Try to restore cache
      - name: Restore link check cache
        id: cache
        uses: actions/cache/restore@v4
        with:
          path: .link-check-cache
          key: link-check-${{ steps.checksum.outputs.checksum }}
      
      # NEW: Skip if cache hit
      - name: Check if links already validated
        id: skip
        run: |
          if [ "${{ steps.cache.hit }}" == "true" ]; then
            echo "Cache hit! Links already validated for this content."
            echo "skip=true" >> $GITHUB_OUTPUT
          else
            echo "Cache miss. Will check links."
            echo "skip=false" >> $GITHUB_OUTPUT
          fi
      
      # EXISTING: Run link checker (only if no cache hit)
      - name: Check links
        if: steps.skip.outputs.skip != 'true'
        uses: lycheeverse/lychee-action@v2
        with:
          args: --verbose --no-progress './**/*.md'
          fail: true
      
      # NEW: Save cache on success
      - name: Save link check cache
        if: steps.skip.outputs.skip != 'true' && success()
        uses: actions/cache/save@v4
        with:
          path: .link-check-cache
          key: link-check-${{ steps.checksum.outputs.checksum }}
      
      # NEW: Create cache marker file
      - name: Create cache marker
        if: steps.skip.outputs.skip != 'true' && success()
        run: |
          mkdir -p .link-check-cache
          echo "Links validated on $(date -u +"%Y-%m-%dT%H:%M:%SZ")" > .link-check-cache/last-check.txt
          echo "Checksum: ${{ steps.checksum.outputs.checksum }}" >> .link-check-cache/last-check.txt
```

**Step 3: Test the Implementation**

```bash
# Test checksum script locally
cd /home/runner/work/_codex_/_codex_
bash .github/scripts/compute-checksum.sh . "*.md"

# Modify a markdown file and verify checksum changes
echo "Test change" >> README.md
bash .github/scripts/compute-checksum.sh . "*.md"

# Verify it's different
git checkout README.md
```

**Step 4: Validate Workflow**

```bash
# Validate workflow YAML syntax
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/check-links.yml'))"

# If validation passes, commit changes
git add .github/scripts/compute-checksum.sh .github/workflows/check-links.yml
git commit -m "feat: Add checksum-based caching to link checker workflow"
```

**Acceptance Criteria:**
- [ ] Checksum script created and executable
- [ ] Workflow updated with caching logic
- [ ] YAML validation passes
- [ ] Test run shows cache hit on unchanged files
- [ ] Test run shows cache miss after file changes
- [ ] Documentation updated with caching explanation
- [ ] Performance improvement documented (time savings)

**Estimated Time:** 1-2 hours

---

### Phase 3: Per-Folder Granular Caching (Extension of Phase 2)

**Status:** Design complete, implementation pending

**Objective:** Extend Phase 2 to support per-folder checksums for selective link checking

#### Implementation Steps

**Step 1: Update Checksum Script for Per-Folder Mode**

Edit `.github/scripts/compute-checksum.sh`:

```bash
#!/bin/bash
# compute-checksum.sh - Compute SHA-1 checksums for link checker caching
# Usage: 
#   ./compute-checksum.sh <directory> [file-pattern]          # Aggregate checksum
#   ./compute-checksum.sh <directory> [file-pattern] --folders # Per-folder checksums

set -e

DIRECTORY="${1:-.}"
PATTERN="${2:-*.md}"
MODE="${3:-aggregate}"

if [ "$MODE" == "--folders" ]; then
  # Per-folder mode: compute checksum for each folder
  echo "Computing per-folder checksums for ${PATTERN} files..." >&2
  
  find "${DIRECTORY}" -type f -name "${PATTERN}" -print0 | \
    xargs -0 dirname | \
    sort -u | \
    while read folder; do
      checksum=$(find "${folder}" -maxdepth 1 -type f -name "${PATTERN}" -print0 | \
                 sort -z | \
                 xargs -0 cat | \
                 sha1sum | \
                 awk '{print $1}')
      echo "${folder}:${checksum}"
    done
else
  # Aggregate mode: single checksum for all files
  echo "Computing aggregate checksum for ${PATTERN} files..." >&2
  
  find "${DIRECTORY}" -type f -name "${PATTERN}" -print0 | \
    sort -z | \
    xargs -0 cat | \
    sha1sum | \
    awk '{print $1}'
fi
```

**Step 2: Create Workflow with Matrix Strategy**

Create `.github/workflows/check-links-granular.yml`:

```yaml
name: Check Links (Granular)

on:
  pull_request:
    paths:
      - '**.md'
  push:
    branches: [main]
    paths:
      - '**.md'
  workflow_dispatch:

jobs:
  prepare:
    runs-on: ubuntu-latest
    outputs:
      folders: ${{ steps.folders.outputs.folders }}
      checksums: ${{ steps.checksums.outputs.checksums }}
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Find folders with markdown files
        id: folders
        run: |
          FOLDERS=$(find . -type f -name "*.md" -print0 | \
                    xargs -0 dirname | \
                    sort -u | \
                    jq -R -s -c 'split("\n")[:-1]')
          echo "folders=${FOLDERS}" >> $GITHUB_OUTPUT
      
      - name: Compute per-folder checksums
        id: checksums
        run: |
          CHECKSUMS=$(bash .github/scripts/compute-checksum.sh . "*.md" --folders | \
                      jq -R -s -c 'split("\n")[:-1] | map(select(length > 0))')
          echo "checksums=${CHECKSUMS}" >> $GITHUB_OUTPUT
  
  check-links-matrix:
    needs: prepare
    runs-on: ubuntu-latest
    strategy:
      matrix:
        folder: ${{ fromJson(needs.prepare.outputs.folders) }}
      fail-fast: false
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Get folder checksum
        id: checksum
        run: |
          CHECKSUM=$(echo '${{ needs.prepare.outputs.checksums }}' | \
                     jq -r '.[] | select(startswith("${{ matrix.folder }}:")) | split(":")[1]')
          echo "checksum=${CHECKSUM}" >> $GITHUB_OUTPUT
      
      - name: Restore cache for folder
        id: cache
        uses: actions/cache/restore@v4
        with:
          path: .link-check-cache/${{ matrix.folder }}
          key: link-check-${{ matrix.folder }}-${{ steps.checksum.outputs.checksum }}
      
      - name: Check if folder needs validation
        id: skip
        run: |
          if [ "${{ steps.cache.hit }}" == "true" ]; then
            echo "Cache hit for ${{ matrix.folder }}!"
            echo "skip=true" >> $GITHUB_OUTPUT
          else
            echo "Cache miss for ${{ matrix.folder }}. Will check links."
            echo "skip=false" >> $GITHUB_OUTPUT
          fi
      
      - name: Check links in folder
        if: steps.skip.outputs.skip != 'true'
        uses: lycheeverse/lychee-action@v2
        with:
          args: --verbose --no-progress '${{ matrix.folder }}/**/*.md'
          fail: true
      
      - name: Save cache for folder
        if: steps.skip.outputs.skip != 'true' && success()
        uses: actions/cache/save@v4
        with:
          path: .link-check-cache/${{ matrix.folder }}
          key: link-check-${{ matrix.folder }}-${{ steps.checksum.outputs.checksum }}
```

**Acceptance Criteria:**
- [ ] Per-folder checksum mode implemented
- [ ] Matrix workflow created
- [ ] Parallel execution of folder checks
- [ ] Individual folder caching works
- [ ] Only changed folders are checked
- [ ] Performance improvement > 70% on partial changes
- [ ] Documentation updated

**Estimated Time:** 2-3 hours

---

### Phase 4: Workflow Consolidation

**Status:** Audit complete (`reports/workflow_consolidation_audit.md`), implementation pending

**Objective:** Consolidate 6-8 duplicate workflows to reduce maintenance overhead

#### Priority Consolidations

**Consolidation 1: Cache Management (3 → 1 workflow)**

**Files to Merge:**
- `.github/workflows/cache-cleanup.yml`
- `.github/workflows/cache-management.yml`
- `.github/workflows/cache-warmup.yml`

**Target:** `.github/workflows/cache-lifecycle.yml`

**Implementation:**

```yaml
name: Cache Lifecycle Management

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
  workflow_dispatch:
    inputs:
      operation:
        description: 'Cache operation to perform'
        required: true
        type: choice
        options:
          - cleanup
          - warmup
          - full-cycle

jobs:
  cache-cleanup:
    if: github.event_name == 'schedule' || github.event.inputs.operation == 'cleanup' || github.event.inputs.operation == 'full-cycle'
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Clean old caches
        run: |
          # Delete caches older than 7 days
          gh cache list --limit 100 | \
            awk '{if ($3 < 7) print $1}' | \
            xargs -I {} gh cache delete {}
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  
  cache-warmup:
    if: github.event_name == 'schedule' || github.event.inputs.operation == 'warmup' || github.event.inputs.operation == 'full-cycle'
    needs: [cache-cleanup]
    runs-on: ubuntu-latest
    strategy:
      matrix:
        cache-key:
          - node-modules
          - python-packages
          - test-results
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Warmup ${{ matrix.cache-key }} cache
        uses: actions/cache@v4
        with:
          path: .cache/${{ matrix.cache-key }}
          key: ${{ matrix.cache-key }}-${{ hashFiles('**/package-lock.json', '**/requirements/lock.txt') }}
      
      - name: Populate cache
        run: |
          # Install dependencies to populate cache
          case "${{ matrix.cache-key }}" in
            node-modules)
              npm ci --cache .cache/node-modules
              ;;
            python-packages)
              pip install -r requirements/lock.txt --cache-dir .cache/python-packages
              ;;
            test-results)
              # Warmup test result caches
              echo "Warmup test caches"
              ;;
          esac
```

**Consolidation 2: Self-Healing (2 → 1 workflow)**

**Files to Merge:**
- `.github/workflows/self-healing-ci.yml`
- `.github/workflows/self-healing-feedback-loop.yml`

**Target:** `.github/workflows/self-healing-system.yml`

**Implementation:**

```yaml
name: Self-Healing System

on:
  push:
    branches: [main, develop]
  pull_request:
  workflow_dispatch:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours

jobs:
  detect-issues:
    runs-on: ubuntu-latest
    outputs:
      has-issues: ${{ steps.check.outputs.has-issues }}
      issue-types: ${{ steps.check.outputs.issue-types }}
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Detect issues
        id: check
        run: |
          # Check for common issues
          ISSUES=""
          
          # Check for failing tests
          if npm test 2>&1 | grep -q "FAIL"; then
            ISSUES="${ISSUES}test-failures,"
          fi
          
          # Check for linting errors
          if npm run lint 2>&1 | grep -q "error"; then
            ISSUES="${ISSUES}lint-errors,"
          fi
          
          # Check for outdated dependencies
          if npm outdated | grep -q "Packages"; then
            ISSUES="${ISSUES}outdated-deps,"
          fi
          
          if [ -n "$ISSUES" ]; then
            echo "has-issues=true" >> $GITHUB_OUTPUT
            echo "issue-types=${ISSUES}" >> $GITHUB_OUTPUT
          else
            echo "has-issues=false" >> $GITHUB_OUTPUT
          fi
  
  auto-fix:
    needs: detect-issues
    if: needs.detect-issues.outputs.has-issues == 'true'
    runs-on: ubuntu-latest
    strategy:
      matrix:
        issue-type: ${{ fromJson(format('["{0}"]', needs.detect-issues.outputs.issue-types)) }}
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Auto-fix ${{ matrix.issue-type }}
        run: |
          case "${{ matrix.issue-type }}" in
            test-failures)
              # Attempt to fix test failures
              npm test -- --updateSnapshot
              ;;
            lint-errors)
              # Auto-fix linting errors
              npm run lint -- --fix
              ;;
            outdated-deps)
              # Update dependencies
              npm update
              ;;
          esac
      
      - name: Create PR with fixes
        uses: peter-evans/create-pull-request@v5
        with:
          title: "🤖 Self-Healing: Fix ${{ matrix.issue-type }}"
          body: |
            Automated fixes for detected issues.
            
            **Issue Type:** ${{ matrix.issue-type }}
            **Detection Time:** ${{ github.event.head_commit.timestamp }}
            **Workflow Run:** ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}
          branch: self-healing/${{ matrix.issue-type }}-${{ github.run_id }}
          delete-branch: true
```

**Consolidation 3: Visual Testing (2 → 1 workflow)**

**Files to Merge:**
- `.github/workflows/html_visual_baseline.yml`
- `.github/workflows/html_visual_regression.yml`

**Target:** `.github/workflows/visual-testing.yml`

**Implementation:**

```yaml
name: Visual Testing

on:
  pull_request:
    paths:
      - 'cognitive_app/**/*.tsx'
      - 'cognitive_app/**/*.css'
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      mode:
        description: 'Testing mode'
        required: true
        type: choice
        options:
          - regression
          - baseline
          - both

jobs:
  visual-baseline:
    if: github.event_name == 'push' || github.event.inputs.mode == 'baseline' || github.event.inputs.mode == 'both'
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Install dependencies
        run: |
          cd cognitive_app
          npm ci
      
      - name: Capture visual baselines
        run: |
          cd cognitive_app
          npm run test:visual -- --update-snapshots
      
      - name: Upload baselines
        uses: actions/upload-artifact@v4
        with:
          name: visual-baselines
          path: cognitive_app/__image_snapshots__
  
  visual-regression:
    if: github.event_name == 'pull_request' || github.event.inputs.mode == 'regression' || github.event.inputs.mode == 'both'
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Install dependencies
        run: |
          cd cognitive_app
          npm ci
      
      - name: Download baselines
        uses: actions/download-artifact@v4
        with:
          name: visual-baselines
          path: cognitive_app/__image_snapshots__
      
      - name: Run visual regression tests
        run: |
          cd cognitive_app
          npm run test:visual
      
      - name: Upload diff images on failure
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: visual-diffs
          path: cognitive_app/__image_snapshots__/__diff_output__
```

**Step 4: Test and Validate**

```bash
# Validate all new workflow files
for file in .github/workflows/cache-lifecycle.yml \
            .github/workflows/self-healing-system.yml \
            .github/workflows/visual-testing.yml; do
  echo "Validating ${file}..."
  python3 -c "import yaml; yaml.safe_load(open('${file}'))"
done

# Commit changes
git add .github/workflows/cache-lifecycle.yml \
        .github/workflows/self-healing-system.yml \
        .github/workflows/visual-testing.yml

git commit -m "feat: Consolidate workflows - cache, self-healing, and visual testing"
```

**Step 5: Deprecate Old Workflows**

Add deprecation notice to old workflow files:

```yaml
# At the top of each old workflow file
# DEPRECATED: This workflow has been consolidated into [new-workflow-name].yml
# This file will be removed in v2.0.0 (Cycle 2)
# Please use the new workflow instead.
# 
# if: false  # Disabled - use new consolidated workflow
```

**Acceptance Criteria:**
- [ ] 3 consolidated workflows created
- [ ] All YAML files validated
- [ ] Old workflows deprecated (not deleted yet)
- [ ] Documentation updated in `reports/workflow_consolidation_audit.md`
- [ ] Test runs confirm new workflows work
- [ ] Performance/maintenance improvement quantified

**Estimated Time:** 3-4 hours

---

### Phase 5: Automated CVE Scanning

**Status:** Foundation laid with security-alert-notification.yml, expansion needed

**Objective:** Implement automated CVE scanning for all Python dependencies in CI/CD

#### Implementation Steps

**Step 1: Create CVE Scanning Script**

Create `.github/scripts/scan-dependencies.py`:

```python
#!/usr/bin/env python3
"""
scan-dependencies.py - Scan Python dependencies for CVEs
"""

import json
import subprocess
import sys
from typing import List, Dict, Any

def run_safety_check() -> Dict[str, Any]:
    """Run safety check on dependencies."""
    try:
        result = subprocess.run(
            ['safety', 'check', '--file', 'requirements/lock.txt', '--json'],
            capture_output=True,
            text=True,
            check=False
        )
        return json.loads(result.stdout) if result.stdout else {}
    except Exception as e:
        print(f"Error running safety check: {e}", file=sys.stderr)
        return {}

def filter_by_severity(vulns: List[Dict], min_severity: str = 'low') -> List[Dict]:
    """Filter vulnerabilities by severity."""
    severity_order = {'low': 0, 'medium': 1, 'high': 2, 'critical': 3}
    min_level = severity_order.get(min_severity.lower(), 0)
    
    filtered = []
    for vuln in vulns:
        severity = vuln.get('severity', 'low').lower()
        if severity_order.get(severity, 0) >= min_level:
            filtered.append(vuln)
    return filtered

def format_report(vulns: List[Dict]) -> str:
    """Format vulnerabilities as markdown report."""
    if not vulns:
        return "✅ No vulnerabilities found!"
    
    report = f"# Security Scan Report\n\n"
    report += f"**Total Vulnerabilities:** {len(vulns)}\n\n"
    
    # Group by severity
    by_severity = {}
    for vuln in vulns:
        severity = vuln.get('severity', 'low').title()
        by_severity.setdefault(severity, []).append(vuln)
    
    for severity in ['Critical', 'High', 'Medium', 'Low']:
        if severity in by_severity:
            report += f"## {severity} Severity ({len(by_severity[severity])})\n\n"
            for vuln in by_severity[severity]:
                report += f"### {vuln.get('package')} {vuln.get('vulnerable_version')}\n"
                report += f"- **CVE:** {vuln.get('cve', 'N/A')}\n"
                report += f"- **Description:** {vuln.get('description', 'N/A')}\n"
                report += f"- **Recommendation:** {vuln.get('recommendation', 'N/A')}\n\n"
    
    return report

def main():
    print("Running security scan on Python dependencies...")
    
    # Run safety check
    results = run_safety_check()
    vulns = results.get('vulnerabilities', [])
    
    # Filter high and critical
    critical_vulns = filter_by_severity(vulns, 'high')
    
    # Generate report
    report = format_report(vulns)
    print(report)
    
    # Write to file
    with open('security-scan-report.md', 'w') as f:
        f.write(report)
    
    # Exit with error if critical/high vulnerabilities found
    if critical_vulns:
        print(f"\n❌ Found {len(critical_vulns)} high/critical vulnerabilities!", file=sys.stderr)
        sys.exit(1)
    else:
        print("\n✅ No high/critical vulnerabilities found!")
        sys.exit(0)

if __name__ == '__main__':
    main()
```

**Step 2: Create CVE Scanning Workflow**

Create `.github/workflows/security-cve-scan.yml`:

```yaml
name: CVE Security Scan

on:
  pull_request:
    paths:
      - 'requirements/**'
      - 'pyproject.toml'
  push:
    branches: [main]
    paths:
      - 'requirements/**'
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight
  workflow_dispatch:

jobs:
  scan-dependencies:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install safety
        run: pip install safety
      
      - name: Run CVE scan
        id: scan
        continue-on-error: true
        run: |
          python .github/scripts/scan-dependencies.py
      
      - name: Upload scan report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: security-scan-report
          path: security-scan-report.md
      
      - name: Post results as comment (PR only)
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const report = fs.readFileSync('security-scan-report.md', 'utf8');
            
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## 🔒 Security CVE Scan Results\n\n${report}`
            });
      
      - name: Fail on high/critical vulnerabilities
        if: steps.scan.outcome == 'failure'
        run: |
          echo "❌ High or critical vulnerabilities found!"
          echo "Review the security-scan-report.md for details."
          exit 1
```

**Step 3: Integrate with Dependency Updates**

Edit `.github/dependabot.yml`:

```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    reviewers:
      - "security-team"
    labels:
      - "dependencies"
      - "security"
    # Auto-merge patch updates for packages without CVEs
    groups:
      security-patches:
        patterns:
          - "*"
        update-types:
          - "patch"
```

**Acceptance Criteria:**
- [ ] CVE scanning script created
- [ ] Workflow created and validated
- [ ] Daily scans configured
- [ ] PR comment integration works
- [ ] High/critical vulnerabilities block merge
- [ ] Scan reports archived
- [ ] Integration with Dependabot configured
- [ ] Documentation updated in `.github/SECURITY.md`

**Estimated Time:** 2-3 hours

---

## Execution Strategy

### Recommended Order

1. **Phase 1: E2E Tests** (1-2 hours)
   - High value, validates all previous work
   - Straightforward execution
   - Immediate feedback

2. **Phase 2: Link Checker Caching** (1-2 hours)
   - Quick wins for CI/CD performance
   - Foundation for Phase 3
   - Low risk

3. **Phase 4: Workflow Consolidation** (3-4 hours)
   - Reduces maintenance overhead
   - Can be done in parallel with others
   - Moderate complexity

4. **Phase 5: CVE Scanning** (2-3 hours)
   - Critical for security posture
   - Builds on existing security work
   - Important for production

5. **Phase 3: Granular Caching** (2-3 hours)
   - Optional enhancement
   - Extends Phase 2
   - Can be deferred if time-constrained

### Total Estimated Time: 9-14 hours (2-3 sessions)

---

## Success Criteria

**Session Complete When:**
- [ ] All 26 E2E tests executed and passing (or failures documented)
- [ ] Link checker caching implemented and tested
- [ ] At least 3 workflows consolidated
- [ ] CVE scanning workflow operational
- [ ] All YAML files validated
- [ ] Documentation updated
- [ ] Performance improvements quantified
- [ ] Code review completed (0 issues)
- [ ] Continuation prompt created (if work remains)

---

## Documentation Updates Required

Update the following files:

1. `reports/e2e_test_execution_results_2026-01-06.md` - E2E test results
2. `reports/workflow_consolidation_audit.md` - Update with implementation status
3. `.github/SECURITY.md` - Add CVE scanning process
4. `cognitive_app/TEST_SUITE_README.md` - Add E2E testing instructions
5. `README.md` - Update with new workflow information

---

## Self-Review Checklist

Before concluding:

- [ ] All phases attempted (or blockers documented)
- [ ] Test pass rates documented
- [ ] Performance improvements quantified
- [ ] Code review performed (aim for 0 issues)
- [ ] Documentation comprehensive
- [ ] Workflows validated with `python -c "import yaml; yaml.safe_load(open('file.yml'))"`
- [ ] Scripts executable: `chmod +x .github/scripts/*.sh`
- [ ] Commit messages follow conventional commits
- [ ] PR description updated
- [ ] Continuation prompt created (if incomplete)

---

## Troubleshooting Guide

### E2E Test Issues

**Problem:** Playwright browsers not installing
```bash
# Solution: Manual installation
npx playwright install-deps
npx playwright install
```

**Problem:** Dev server not starting
```bash
# Solution: Check port availability
lsof -i :5000
# Kill process if needed
kill -9 $(lsof -t -i:5000)
```

### Workflow Issues

**Problem:** YAML validation failing
```bash
# Solution: Check syntax with detailed error
python3 << 'EOF'
import yaml
try:
    with open('.github/workflows/your-workflow.yml', 'r') as f:
        yaml.safe_load(f)
    print("✅ Valid YAML")
except yaml.YAMLError as e:
    print(f"❌ YAML Error: {e}")
EOF
```

**Problem:** Cache not working
```bash
# Solution: Check cache key uniqueness
# Ensure checksums are different for different content
bash .github/scripts/compute-checksum.sh . "*.md"
```

### CVE Scanning Issues

**Problem:** Safety not finding vulnerabilities
```bash
# Solution: Update safety database
pip install --upgrade safety
safety check --file requirements/lock.txt --json
```

---

## Reference Documentation

**Previous Work:**
- PR #2711 (base work)
- `cognitive_app/DEV_TEST_COMPREHENSIVE_WALKTHROUGH.md` (45KB, 15 diagrams)
- `reports/test_execution_results_FINAL_2026-01-06.md`
- `reports/workflow_consolidation_audit.md`
- `.github/SECURITY.md`

**Workflow Templates:**
- `.github/workflows/security-alert-notification.yml` (existing)
- `.github/workflows/check-links.yml` (existing, to be updated)

**Scripts:**
- `.github/scripts/compute-checksum.sh` (to be created)
- `.github/scripts/scan-dependencies.py` (to be created)

---

## Expected Deliverables

**Code:**
- [ ] `playwright.config.ts`
- [ ] `.github/scripts/compute-checksum.sh`
- [ ] `.github/scripts/scan-dependencies.py`
- [ ] `.github/workflows/cache-lifecycle.yml`
- [ ] `.github/workflows/self-healing-system.yml`
- [ ] `.github/workflows/visual-testing.yml`
- [ ] `.github/workflows/security-cve-scan.yml`
- [ ] Updated `.github/workflows/check-links.yml`

**Documentation:**
- [ ] `reports/e2e_test_execution_results_2026-01-06.md`
- [ ] Updated `reports/workflow_consolidation_audit.md`
- [ ] Updated `.github/SECURITY.md`
- [ ] Updated `cognitive_app/TEST_SUITE_README.md`

**Reports:**
- [ ] E2E test HTML report
- [ ] Performance improvement metrics
- [ ] CVE scan reports

---

## Final Notes

**Session Context:**
- Previous session achieved 100% unit test pass rate (14/14)
- All primary objectives complete
- This is optional enhancement work
- Can be split across multiple sessions

**Best Practices:**
- Commit incrementally after each phase
- Use `report_progress` to update PR
- Run code_review before final commit
- Create continuation prompt if unable to complete

**If Unable to Complete:**
Create a similar continuation prompt following this format, documenting:
- What was completed
- What remains
- Any blockers encountered
- Updated time estimates

---

**Start Command:**
```
@copilot continue
```

**Review Before Starting:**
- [ ] All Priority 1 tasks complete (100% test pass rate)
- [ ] Documentation from previous session reviewed
- [ ] Repository in clean state
- [ ] Ready to begin Priority 2 enhancements
