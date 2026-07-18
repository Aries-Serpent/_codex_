# PR #5336 - Lane 2: Consolidation Code Examples
**Date**: 2026-07-18  
**Purpose**: Implementation templates for workflow consolidation  
**Status**: Ready to implement

---

## 🔧 Consolidation Implementation Templates

### 1. Unified Security Scanning Consolidation

#### Current State (Before):
```
├── container-scan.yml (standalone container security)
├── scheduled-dependency-audit.yml (standalone dependency audit)
├── security-scan-phase-16.yml (phase-specific security)
└── security-scanning-suite.yml (main orchestrator)
```

#### Target State (After):
```
└── unified-security-scanning.yml (consolidated, all scan types)
```

#### Implementation:

```yaml
name: Unified Security Scanning Suite

on:
  push:
    branches:
      - main
      - develop
  pull_request:
    branches:
      - main
      - develop
  schedule:
    # Consolidated schedule - single entry point
    - cron: '0 2 * * *'     # Daily 2 AM UTC
    - cron: '0 3 * * 0'     # Weekly Sunday 3 AM UTC
  workflow_dispatch:
    inputs:
      scan-type:
        description: Security scan type to run
        required: true
        type: choice
        options:
          - all
          - codeql
          - containers
          - dependencies
        default: all
      lane-id:
        description: Optional lane ID for orchestration
        required: false
        type: string

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}-${{ github.event.inputs.scan-type || 'all' }}
  cancel-in-progress: true

env:
  PYTHON_VERSION: '3.12'
  REGISTRY: ghcr.io

permissions:
  contents: read
  security-events: write
  pull-requests: write

jobs:
  # ============================================
  # CODEQL ANALYSIS - Replaces container-scan.yml
  # ============================================
  codeql-analysis:
    name: CodeQL Analysis
    if: |
      github.event.inputs.scan-type == 'all' || 
      github.event.inputs.scan-type == 'codeql' ||
      github.event_name == 'push' ||
      github.event_name == 'schedule'
    runs-on: ubuntu-latest
    timeout-minutes: 45
    
    permissions:
      contents: read
      security-events: write
      
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
          
      - name: Initialize CodeQL
        uses: github/codeql-action/init@v2
        with:
          languages: 'python'
          
      - name: Autobuild
        uses: github/codeql-action/autobuild@v2
        
      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@v2
        with:
          category: '/language:python'

  # ============================================
  # CONTAINER SECURITY - Replaces container-scan.yml jobs
  # ============================================
  container-scan:
    name: Container Security Scan
    if: |
      github.event.inputs.scan-type == 'all' || 
      github.event.inputs.scan-type == 'containers' ||
      contains(github.event.pull_request.files[*].name, 'Dockerfile')
    runs-on: ubuntu-latest
    timeout-minutes: 30
    
    permissions:
      contents: read
      security-events: write
      
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        
      - name: Run Trivy container scan
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'container-scan-results.sarif'
          
      - name: Upload Trivy results to GitHub
        uses: github/codeql-action/upload-sarif@v2
        if: always()
        with:
          sarif_file: 'container-scan-results.sarif'
          category: 'container-scan'

  # ============================================
  # DEPENDENCY AUDIT - Replaces scheduled-dependency-audit.yml
  # ============================================
  dependency-audit:
    name: Dependency Audit
    if: |
      github.event.inputs.scan-type == 'all' || 
      github.event.inputs.scan-type == 'dependencies'
    runs-on: ubuntu-latest
    timeout-minutes: 30
    
    permissions:
      contents: read
      security-events: write
      
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'
          
      - name: Install security tools
        run: |
          python -m pip install --upgrade pip
          pip install safety pip-audit bandit[toml] semgrep gitleaks
          
      - name: Run safety check
        run: safety check --json > safety-report.json || true
        
      - name: Run pip-audit
        run: pip-audit --desc > pip-audit-report.txt || true
        
      - name: Run Bandit
        run: bandit -r src/ -f json -o bandit-report.json || true
        
      - name: Run SemGrep
        uses: returntocorp/semgrep-action@v1
        with:
          config: >-
            p/security-audit
            p/ci
            
      - name: Upload audit results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: dependency-audit-results
          path: |
            safety-report.json
            pip-audit-report.txt
            bandit-report.json

  # ============================================
  # SECRETS DETECTION
  # ============================================
  secrets-detection:
    name: Secrets Detection
    if: |
      github.event.inputs.scan-type == 'all' ||
      github.event_name != 'schedule'
    runs-on: ubuntu-latest
    timeout-minutes: 15
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
          
      - name: Run GitLeaks scan
        uses: gitleaks/gitleaks-action@v2
        with:
          verbose: true
          
      - name: Run TruffleHog
        uses: trufflesecurity/trufflescan@main
        with:
          extraArgs: --json --fail

  # ============================================
  # AGGREGATION & REPORTING
  # ============================================
  security-report:
    name: Security Scan Report
    if: always()
    needs: [codeql-analysis, container-scan, dependency-audit, secrets-detection]
    runs-on: ubuntu-latest
    
    steps:
      - name: Download all artifacts
        uses: actions/download-artifact@v3
        
      - name: Generate security report
        run: |
          echo "# Security Scan Report" > report.md
          echo "**Date**: $(date)" >> report.md
          echo "**Status**: $([ '${{ needs.codeql-analysis.result }}' == 'success' ] && echo '✅ PASS' || echo '⚠️ REVIEW')" >> report.md
          
      - name: Comment on PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: fs.readFileSync('report.md', 'utf8')
            })
```

---

### 2. Unified Dependabot Management

#### Implementation:

```yaml
name: Unified Dependabot Management

on:
  pull_request:
    types: [opened, synchronize, reopened]
  workflow_dispatch:
    inputs:
      operation:
        description: Dependabot operation to perform
        required: true
        type: choice
        options:
          - preflight-check
          - auto-absorb
          - approval-enforce
          - all
        default: all
      pr-number:
        description: Specific PR number (for absorb operations)
        required: false
        type: string

concurrency:
  group: dependabot-${{ github.event.pull_request.number || github.event.inputs.pr-number }}
  cancel-in-progress: false

permissions:
  contents: write
  pull-requests: write
  issues: write

jobs:
  # ============================================
  # PREFLIGHT VALIDATION - from dependabot-preflight.yml
  # ============================================
  preflight-check:
    name: Dependabot Preflight Check
    if: |
      github.actor == 'dependabot[bot]' ||
      github.event.inputs.operation == 'preflight-check' ||
      github.event.inputs.operation == 'all'
    runs-on: ubuntu-latest
    outputs:
      is-dependabot: ${{ steps.check.outputs.is-dependabot }}
      is-security: ${{ steps.check.outputs.is-security }}
      bump-type: ${{ steps.check.outputs.bump-type }}
      
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        
      - id: check
        name: Analyze Dependabot PR
        run: |
          if [[ "${{ github.actor }}" == "dependabot[bot]" ]]; then
            echo "is-dependabot=true" >> $GITHUB_OUTPUT
          else
            echo "is-dependabot=false" >> $GITHUB_OUTPUT
          fi
          
          # Check if security update
          if grep -q "security" "${{ github.event.pull_request.title }}"; then
            echo "is-security=true" >> $GITHUB_OUTPUT
          else
            echo "is-security=false" >> $GITHUB_OUTPUT
          fi
          
          # Detect bump type
          if grep -q "patch" "${{ github.event.pull_request.title }}"; then
            echo "bump-type=patch" >> $GITHUB_OUTPUT
          elif grep -q "minor" "${{ github.event.pull_request.title }}"; then
            echo "bump-type=minor" >> $GITHUB_OUTPUT
          else
            echo "bump-type=major" >> $GITHUB_OUTPUT
          fi
      
      - name: Comment on PR
        if: steps.check.outputs.is-dependabot == 'true'
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `✅ Dependabot PR detected\n- Type: ${{ steps.check.outputs.bump-type }}\n- Security: ${{ steps.check.outputs.is-security }}`
            })

  # ============================================
  # AUTO-ABSORB - from dependabot-auto-absorb.yml
  # ============================================
  auto-absorb:
    name: Auto-Absorb Single-File Dependabot Bumps
    if: |
      needs.preflight-check.outputs.is-dependabot == 'true' &&
      needs.preflight-check.outputs.bump-type == 'patch' &&
      (github.event.inputs.operation == 'auto-absorb' || 
       github.event.inputs.operation == 'all' ||
       github.event_name == 'pull_request')
    needs: preflight-check
    runs-on: ubuntu-latest
    outputs:
      absorbed: ${{ steps.absorb.outputs.absorbed }}
      
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          fetch-depth: 0
          
      - name: Configure git
        run: |
          git config user.name "dependabot-absorber"
          git config user.email "bot@github.com"
          
      - id: absorb
        name: Cherry-pick Dependabot bump
        run: |
          # Get changed files
          CHANGED_FILES=$(git diff --name-only ${{ github.event.pull_request.base.sha }})
          FILE_COUNT=$(echo "$CHANGED_FILES" | wc -l)
          
          if [ $FILE_COUNT -eq 1 ]; then
            # Single file change - can absorb
            echo "Single file change detected: $(echo $CHANGED_FILES)"
            
            # Cherry-pick commit to main
            TARGET_BRANCH="${{ github.event.inputs.target_branch || 'main' }}"
            git fetch origin $TARGET_BRANCH
            git checkout origin/$TARGET_BRANCH
            git cherry-pick ${{ github.event.pull_request.head.sha }}
            git push origin $TARGET_BRANCH
            
            echo "absorbed=true" >> $GITHUB_OUTPUT
          else
            echo "Multiple files changed - manual review needed"
            echo "absorbed=false" >> $GITHUB_OUTPUT
          fi

  # ============================================
  # APPROVAL ENFORCEMENT - from dependabot-sheriff.yml
  # ============================================
  approval-enforce:
    name: Approval Enforcement
    if: |
      always() &&
      (github.event.inputs.operation == 'approval-enforce' ||
       github.event.inputs.operation == 'all' ||
       github.event_name == 'pull_request')
    needs: [preflight-check, auto-absorb]
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        
      - name: Get PR details
        id: pr
        uses: actions/github-script@v7
        with:
          script: |
            const pr = await github.rest.pulls.get({
              owner: context.repo.owner,
              repo: context.repo.repo,
              pull_number: context.issue.number
            });
            
            const approvals = pr.data.reviews.filter(r => r.state === 'APPROVED').length;
            const isMinor = '${{ needs.preflight-check.outputs.bump-type }}' === 'patch';
            
            core.setOutput('approvals', approvals);
            core.setOutput('needs-approval', !isMinor || approvals < 1);
      
      - name: Request approval for major bumps
        if: steps.pr.outputs.needs-approval == 'true'
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '⚠️ This Dependabot PR requires approval before merging'
            })
      
      - name: Auto-approve patch updates
        if: steps.pr.outputs.needs-approval == 'false'
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.pulls.createReview({
              owner: context.repo.owner,
              repo: context.repo.repo,
              pull_number: context.issue.number,
              event: 'APPROVE'
            })
```

---

### 3. Unified Documentation Build

#### Implementation:

```yaml
name: Unified Documentation Build & Deploy

on:
  push:
    branches: [main, develop]
    paths:
      - 'docs/**'
      - 'docs_api/**'
      - 'mkdocs.yml'
      - '.github/workflows/unified-documentation.yml'
  pull_request:
    branches: [main, develop]
    paths:
      - 'docs/**'
      - 'docs_api/**'
      - 'mkdocs.yml'
  workflow_dispatch:
    inputs:
      build-type:
        type: choice
        options: [all, mkdocs, api-docs]
        default: all

concurrency:
  group: documentation-${{ github.ref }}
  cancel-in-progress: true

jobs:
  # ============================================
  # BUILD MKDOCS
  # ============================================
  build-mkdocs:
    name: Build MkDocs Site
    if: github.event.inputs.build-type == 'all' || github.event.inputs.build-type == 'mkdocs' || github.event_name != 'workflow_dispatch'
    runs-on: ubuntu-latest
    outputs:
      artifact-id: ${{ steps.artifact.outputs.artifact-id }}
      
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          pip install -q mkdocs mkdocs-material mkdocs-mermaid2-plugin
          pip install -q -r docs-requirements.txt || true
      
      - name: Build MkDocs
        run: mkdocs build --strict
      
      - name: Upload artifact
        id: artifact
        uses: actions/upload-artifact@v3
        with:
          name: mkdocs-site-${{ github.run_id }}
          path: site/
          retention-days: 1

  # ============================================
  # BUILD API DOCUMENTATION
  # ============================================
  build-api-docs:
    name: Build API Documentation
    if: github.event.inputs.build-type == 'all' || github.event.inputs.build-type == 'api-docs'
    runs-on: ubuntu-latest
    outputs:
      artifact-id: ${{ steps.artifact.outputs.artifact-id }}
      
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install -q sphinx sphinx-rtd-theme
          pip install -e .
      
      - name: Build API docs
        run: |
          cd docs_api
          sphinx-build -b html . _build/
      
      - name: Upload artifact
        id: artifact
        uses: actions/upload-artifact@v3
        with:
          name: api-docs-${{ github.run_id }}
          path: docs_api/_build/
          retention-days: 1

  # ============================================
  # DEPLOY TO PAGES
  # ============================================
  deploy-to-pages:
    name: Deploy to GitHub Pages
    if: |
      github.ref == 'refs/heads/main' &&
      (github.event_name == 'push' || github.event_name == 'workflow_dispatch')
    needs: [build-mkdocs, build-api-docs]
    runs-on: ubuntu-latest
    
    permissions:
      pages: write
      id-token: write
    
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    
    steps:
      - name: Download MkDocs artifact
        uses: actions/download-artifact@v3
        with:
          name: mkdocs-site-${{ github.run_id }}
          path: ./site
      
      - name: Download API docs
        uses: actions/download-artifact@v3
        with:
          name: api-docs-${{ github.run_id }}
          path: ./site/api
      
      - name: Upload to Pages
        uses: actions/upload-pages-artifact@v2
        with:
          path: './site'
      
      - id: deployment
        name: Deploy
        uses: actions/deploy-pages@v2
      
      - name: Comment on PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `✅ Documentation built successfully!\n📖 [Preview](${process.env.PAGES_URL})`
            })
```

---

### 4. Skip Condition Examples

#### Docs-Only Skip Pattern:

```yaml
# Add to workflows that shouldn't run on doc-only changes
name: Build & Test

on:
  push:
    branches: [main]
    # Skip if ONLY markdown files changed
    paths-ignore:
      - '**.md'
      - 'docs/**'
      - '.github/ISSUE_TEMPLATE/**'
      
  pull_request:
    branches: [main]
    paths-ignore:
      - '**.md'
      - 'docs/**'
      - '.github/ISSUE_TEMPLATE/**'

jobs:
  build:
    runs-on: ubuntu-latest
    # This job only runs if non-docs files changed
```

#### Config-Only Skip Pattern:

```yaml
# Add to security/performance-sensitive workflows
name: Security Scan

on:
  pull_request:
    branches: [main]
    # Skip if ONLY config files changed
    paths-ignore:
      - '**.yml'
      - '**.yaml'
      - '*.toml'
      - '*.ini'
      - '.github/**'

jobs:
  security-scan:
    runs-on: ubuntu-latest
```

#### Advanced Change Detection Pattern:

```yaml
jobs:
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      src-changed: ${{ steps.files.outputs.src }}
      test-changed: ${{ steps.files.outputs.tests }}
      docs-changed: ${{ steps.files.outputs.docs }}
      
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          
      - id: files
        run: |
          CHANGED=$(git diff --name-only ${{ github.event.pull_request.base.sha }})
          
          if echo "$CHANGED" | grep -q 'src/'; then
            echo "src=true" >> $GITHUB_OUTPUT
          else
            echo "src=false" >> $GITHUB_OUTPUT
          fi
          
          if echo "$CHANGED" | grep -q 'tests/'; then
            echo "tests=true" >> $GITHUB_OUTPUT
          else
            echo "tests=false" >> $GITHUB_OUTPUT
          fi
          
          if echo "$CHANGED" | grep -q 'docs/\|\.md$'; then
            echo "docs=true" >> $GITHUB_OUTPUT
          else
            echo "docs=false" >> $GITHUB_OUTPUT
          fi

  build-test:
    needs: detect-changes
    if: needs.detect-changes.outputs.src-changed == 'true'
    runs-on: ubuntu-latest
    # Runs only if src files changed
    
  unit-tests:
    needs: detect-changes
    if: needs.detect-changes.outputs.test-changed == 'true'
    runs-on: ubuntu-latest
    # Runs only if test files changed
    
  docs-build:
    needs: detect-changes
    if: needs.detect-changes.outputs.docs-changed == 'true'
    runs-on: ubuntu-latest
    # Runs only if docs changed
```

---

## 📊 Migration Checklist

### For Each Consolidation:

- [ ] Create consolidated workflow file
- [ ] Test consolidated workflow in branch
- [ ] Add migration guide to archived workflow
- [ ] Update team documentation
- [ ] Archive old workflows (don't delete)
- [ ] Monitor for issues
- [ ] Remove archived workflows after 2 weeks

### For Each Skip Condition:

- [ ] Add `paths-ignore` or custom detection
- [ ] Test with docs-only PR
- [ ] Test with code-only PR
- [ ] Test with mixed PR
- [ ] Update workflow documentation
- [ ] Monitor PR execution times

---

## ⚡ Expected Benefits

### Performance Improvements
- **PR Build Time**: 20-30 min faster on docs-only PRs
- **Execution Parallelization**: 15-20% faster on consolidated workflows
- **Cost Savings**: ~$500-1000/month in reduced runner time

### Maintainability Improvements
- **Configuration Clarity**: Single source of truth per domain
- **Debugging**: Fewer workflows to search through
- **Onboarding**: Easier to understand CI/CD architecture
- **Change Impact**: Clearer blast radius for workflow changes

---

**Note**: Implement these consolidations incrementally. Test each one thoroughly before moving to the next.
