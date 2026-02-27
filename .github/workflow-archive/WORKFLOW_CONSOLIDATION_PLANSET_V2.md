# Workflow Consolidation Planset V2

**Project**: GitHub Actions Workflow Consolidation (Phase 2)
**Date**: 2026-02-06
**Target**: Reduce from 108 to 48 workflows (-56% reduction)
**Timeline**: 12 phases (3 phases)
**Previous**: 67 → 48 workflows (2025-12-28)
**Current**: 108 workflows (workflow sprawl +125%)

---

## 📊 Consolidation Overview

### Target Summary

| Phase | Weeks | Workflows Consolidated | Remaining | Progress |
|-------|-------|----------------------|-----------|----------|
| **Start** | 0 | - | 108 | 0% |
| **Phase 1** | 1-4 | -30 | 78 | 28% |
| **Phase 2** | 5-8 | -20 | 58 | 46% |
| **Phase 3** | 9-12 | -10 | 48 | 56% |
| **Complete** | 12 | -60 | **48** | **100%** ✅ |

---

## 🎯 Phase 1: High-Priority Consolidations (Weeks 1-4)

**Goal**: Consolidate 30 workflows with highest overlap and lowest risk

### Consolidation Group 1: Security Suites
**Current**: 3 workflows  
**Target**: 1 unified workflow  
**Reduction**: -2 workflows

#### Workflows to Consolidate
1. `security-scanning-suite.yml` (3 artifacts)
2. `security-suite.yml` (1 artifact)
3. `security-scan.yml` (1 artifact)

#### Consolidated Workflow: `unified-security-suite.yml`
```yaml
name: Art_Unified Security Suite
on:
  push:
    branches: [main]
  pull_request:
  schedule:
    - cron: '0 2 * * *'
  workflow_dispatch:

jobs:
  semgrep-scan:
    name: Semgrep SAST
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Semgrep
        run: semgrep ci --sarif --output semgrep.sarif
      - name: Upload SARIF
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: semgrep.sarif

  dependency-audit:
    name: Dependency Security Audit
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run npm audit
        run: npm audit --audit-level=moderate
      - name: Run pip audit
        run: pip-audit

  secret-scan:
    name: Secret Scanning
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Gitleaks
        uses: gitleaks/gitleaks-action@v2

  unified-results:
    name: Aggregate Security Results
    runs-on: ubuntu-latest
    needs: [semgrep-scan, dependency-audit, secret-scan]
    steps:
      - name: Collect Results
        run: echo "All security scans complete"
      - name: Upload Artifacts
        uses: actions/upload-artifact@v6
        with:
          name: security-suite-results-${{ github.run_number }}
          path: |
            semgrep.sarif
            audit_results.json
            secret_scan_results.json
          retention-days: 90
```

**Migration Plan**:
1. Create `unified-security-suite.yml`
2. Test on feature branch
3. Disable old workflows
4. Move to `.github/workflow-archive/disabled/`
5. Update ARTIFACT_CATALOG.md

---

### Consolidation Group 2: Test Suites
**Current**: 3 workflows (test-suite.yml, test-comprehensive.yml, optimized-ci.yml overlaps)
**Target**: Enhance optimized-ci.yml, deprecate others
**Reduction**: -2 workflows

#### Workflows to Deprecate
1. `test-suite.yml` (5 artifacts) → Already covered by optimized-ci.yml
2. `test-comprehensive.yml` (4 artifacts) → Merge unique features into optimized-ci.yml

#### Enhanced: `optimized-ci.yml`
**Current Jobs**: 4 (setup, test, benchmark, report)
**Added Jobs**:
- RAG-specific tests (from test-rag.yml)
- Performance metrics (from test-comprehensive.yml)
- Comprehensive benchmarks (from test-suite.yml)

**Migration Plan**:
1. Add matrix strategy for Python versions (3.11, 3.12, 3.13)
2. Add RAG test job
3. Consolidate all artifact uploads
4. Test thoroughly
5. Disable test-suite.yml and test-comprehensive.yml
6. Keep test-rag.yml for specialized RAG testing

---

### Consolidation Group 3: Cache Management
**Current**: 5 workflows
**Target**: 0 workflows (distributed caching + GitHub auto-cleanup)
**Reduction**: -5 workflows

#### Workflows to Deprecate
1. `cache-cleanup.yml` → GitHub auto-cleanup (30 iteration TTL)
2. `cache-management.yml` → Distributed to individual workflows
3. `cache-suite.yml` → Distributed to individual workflows
4. `cache-warmup.yml` → Natural warming during workflow execution
5. `cleanup-ci-caches.yml` → GitHub auto-cleanup

**Rationale**: Per previous consolidation (2025-12-28), distributed caching is superior:
- Each workflow manages own cache
- GitHub automatic expiry (30 iterations)
- No single point of failure
- Automatic invalidation via hash-based keys

**Migration Plan**:
1. Verify all workflows use `actions/cache@v5`
2. Confirm cache keys use dependency file hashes
3. Disable all 5 cache workflows
4. Document distributed caching pattern
5. Monitor for 2 phases

---

### Consolidation Group 4: CI Health Monitoring
**Current**: 3 workflows
**Target**: 1 comprehensive workflow
**Reduction**: -2 workflows

#### Workflows to Consolidate
1. `ci-health-monitor.yml` (created in previous consolidation)
2. `ci-health-suite.yml` (1 artifact)
3. `ci-diagnostic-automation.yml`

#### Consolidated: `ci-health-monitor-v2.yml`
```yaml
name: CI Health Monitor (Enhanced)
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:

jobs:
  health-check:
    name: CI Health Assessment
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Count Workflows
        id: count
        run: |
          ACTIVE=$(find .github/workflows -name "*.yml" | wc -l)
          DISABLED=$(find .github/workflow-archive/disabled -name "*.yml" | wc -l)
          echo "active=$ACTIVE" >> $GITHUB_OUTPUT
          echo "disabled=$DISABLED" >> $GITHUB_OUTPUT

      - name: Validate YAML
        run: yamllint .github/workflows/*.yml

      - name: Workflow Success Rate
        run: |
          gh run list --limit 100 --json conclusion | \
            jq '[.[] | select(.conclusion == "success")] | length'

      - name: Diagnostic Analysis
        run: |
          # Check for common failure patterns
          gh run list --status failure --limit 20 --json name,conclusion

      - name: Generate Health Report
        run: |
          cat > ci-health-report.json << EOF
          {
            "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
            "active_workflows": ${{ steps.count.outputs.active }},
            "disabled_workflows": ${{ steps.count.outputs.disabled }},
            "target": 48,
            "variance": $(( ${{ steps.count.outputs.active }} - 48 ))
          }
          EOF

      - name: Upload Report
        uses: actions/upload-artifact@v6
        with:
          name: ci-health-report-${{ github.run_number }}
          path: ci-health-report.json
          retention-days: 30
```

**Migration Plan**:
1. Create enhanced ci-health-monitor-v2.yml
2. Test on feature branch
3. Disable old health workflows
4. Update monitoring dashboards

---

### Consolidation Group 5: Authentication Management
**Current**: 8 workflows
**Target**: 1 unified suite
**Reduction**: -7 workflows

#### Workflows to Consolidate
1. `auth-compliance-report.yml` (1 artifact)
2. `auth-mfa-enrollment.yml`
3. `auth-oauth-app-sync.yml`
4. `auth-secret-rotation.yml`
5. `auth-security-audit.yml`
6. `auth-tests.yml`
7. `auth-token-rotation.yml`
8. `token-rotation.yml`

#### Consolidated: `auth-management-suite.yml`
```yaml
name: Authentication Management Suite
on:
  schedule:
    - cron: '0 3 * * 1'  # Weekly on Monday
  workflow_dispatch:
    inputs:
      task:
        description: 'Auth task to run'
        required: true
        type: choice
        options:
          - compliance-report
          - mfa-enrollment
          - oauth-sync
          - secret-rotation
          - security-audit
          - token-rotation
          - all

jobs:
  compliance-report:
    name: Generate Compliance Report
    runs-on: ubuntu-latest
    if: inputs.task == 'compliance-report' || inputs.task == 'all'
    steps:
      - name: Generate Report
        run: |
          # Compliance check logic
          echo '{"status": "compliant"}' > compliance-report.json
      - name: Upload Artifact
        uses: actions/upload-artifact@v6
        with:
          name: auth-compliance-report-${{ github.run_number }}
          path: compliance-report.json
          retention-days: 90

  mfa-enrollment:
    name: MFA Enrollment Check
    runs-on: ubuntu-latest
    if: inputs.task == 'mfa-enrollment' || inputs.task == 'all'
    steps:
      - name: Check MFA Status
        run: gh api /orgs/Aries-Serpent/members --jq '.[] | select(.two_factor_authentication == false)'

  oauth-sync:
    name: OAuth App Sync
    runs-on: ubuntu-latest
    if: inputs.task == 'oauth-sync' || inputs.task == 'all'
    steps:
      - name: Sync OAuth Apps
        run: gh api /user/installations

  secret-rotation:
    name: Secret Rotation
    runs-on: ubuntu-latest
    if: inputs.task == 'secret-rotation' || inputs.task == 'all'
    steps:
      - name: Rotate Secrets
        run: echo "Secret rotation logic"

  token-rotation:
    name: Token Rotation
    runs-on: ubuntu-latest
    if: inputs.task == 'token-rotation' || inputs.task == 'all'
    steps:
      - name: Rotate Tokens
        run: echo "Token rotation logic"

  security-audit:
    name: Security Audit
    runs-on: ubuntu-latest
    if: inputs.task == 'security-audit' || inputs.task == 'all'
    steps:
      - name: Run Audit
        run: echo "Security audit logic"

  auth-tests:
    name: Authentication Tests
    runs-on: ubuntu-latest
    if: inputs.task == 'all'
    steps:
      - uses: actions/checkout@v4
      - name: Run Auth Tests
        run: pytest tests/auth/ -v
```

**Migration Plan**:
1. Create auth-management-suite.yml
2. Test each job independently
3. Verify secret access
4. Disable old auth workflows
5. Update documentation

---

### Consolidation Group 6: CodeQL Analysis
**Current**: 2 workflows
**Target**: 1 with chunking option
**Reduction**: -1 workflow

#### Workflows to Consolidate
1. `codeql-analysis.yml` (standard analysis)
2. `codeql-chunked.yml` (3 artifacts, chunked for large repos)

#### Consolidated: `codeql-analysis-unified.yml`
```yaml
name: Art_CodeQL Security Analysis
on:
  push:
    branches: [main]
  pull_request:
  schedule:
    - cron: '0 0 * * 1'  # Weekly

jobs:
  analyze:
    name: CodeQL Analysis
    runs-on: ubuntu-latest
    strategy:
      matrix:
        language: [python, javascript]
        chunk: ${{ github.event_name == 'schedule' && '[1, 2, 3]' || '[1]' }}
    steps:
      - uses: actions/checkout@v4

      - name: Initialize CodeQL
        uses: github/codeql-action/init@v3
        with:
          languages: ${{ matrix.language }}
          queries: security-and-quality

      - name: Perform Analysis (Chunk ${{ matrix.chunk }})
        if: matrix.chunk > 1
        run: |
          # Chunked analysis for scheduled runs
          codeql database analyze --threads=4 \
            --chunk=${{ matrix.chunk }}/3

      - name: Perform Analysis (Standard)
        if: matrix.chunk == 1 && github.event_name != 'schedule'
        uses: github/codeql-action/analyze@v3

      - name: Upload Results
        if: github.event_name == 'schedule'
        uses: actions/upload-artifact@v6
        with:
          name: codeql-results-${{ matrix.language }}-chunk-${{ matrix.chunk }}
          path: codeql-results/
          retention-days: 90
```

**Migration Plan**:
1. Create unified CodeQL workflow
2. Test chunking logic
3. Verify SARIF uploads to Security tab
4. Disable old workflows

---

### Consolidation Group 7: Workflow Analytics
**Current**: 3 workflows
**Target**: 1 with both triggers
**Reduction**: -2 workflows

#### Workflows to Consolidate
1. `workflow-analytics-manual.yml` (manual trigger, 1 artifact)
2. `workflow-analytics-scheduled.yml` (scheduled, 1 artifact)
3. `workflow-health-check.yml` (health metrics, 1 artifact)

#### Consolidated: `workflow-analytics-unified.yml`
```yaml
name: Art_Workflow Analytics & Health
on:
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM UTC
  workflow_dispatch:
    inputs:
      analysis_type:
        description: 'Type of analysis'
        required: false
        type: choice
        options:
          - full
          - health-only
          - trends-only
        default: 'full'

jobs:
  collect-metrics:
    name: Collect Workflow Metrics
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Gather Workflow Data
        id: metrics
        run: |
          # Collect workflow run data
          gh run list --limit 100 --json name,conclusion,startedAt,durationMs > workflow_data.json

          # Calculate metrics
          python3 << EOF
          import json
          with open('workflow_data.json') as f:
              data = json.load(f)

          success_rate = len([r for r in data if r['conclusion'] == 'success']) / len(data) * 100
          avg_duration = sum(r['durationMs'] for r in data) / len(data) / 1000 / 60  # minutes

          print(f"SUCCESS_RATE={success_rate:.2f}" >> $GITHUB_OUTPUT)
          print(f"AVG_DURATION={avg_duration:.2f}" >> $GITHUB_OUTPUT)
          EOF

      - name: Health Assessment
        run: |
          cat > workflow-health-report.json << EOF
          {
            "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
            "success_rate": ${{ steps.metrics.outputs.SUCCESS_RATE }},
            "avg_duration_minutes": ${{ steps.metrics.outputs.AVG_DURATION }},
            "active_workflows": $(find .github/workflows -name "*.yml" | wc -l)
          }
          EOF

      - name: Generate Trends
        if: inputs.analysis_type != 'health-only'
        run: |
          # Generate trend CSV
          echo "timestamp,active,disabled,success_rate" > workflow_trends.csv
          echo "$(date -u +%Y-%m-%dT%H:%M:%SZ),$(find .github/workflows -name "*.yml" | wc -l),$(find .github/workflow-archive/disabled -name "*.yml" | wc -l),${{ steps.metrics.outputs.SUCCESS_RATE }}" >> workflow_trends.csv

      - name: Upload Artifacts
        uses: actions/upload-artifact@v6
        with:
          name: workflow-analytics-${{ github.run_number }}
          path: |
            workflow-health-report.json
            workflow_trends.csv
            workflow_data.json
          retention-days: 60
```

**Migration Plan**:
1. Create unified workflow
2. Test both scheduled and manual triggers
3. Verify artifact uploads
4. Disable old workflows

---

### Consolidation Group 8: Self-Healing Workflows
**Current**: 3 workflows
**Target**: 1 unified system
**Reduction**: -2 workflows

#### Workflows to Consolidate
1. `self-healing.yml` (1 artifact)
2. `self-healing-ci.yml`
3. `self-healing-feedback-loop.yml`

#### Consolidated: `self-healing-system.yml`
```yaml
name: Art_Self-Healing System
on:
  workflow_run:
    workflows: ["*"]
    types: [completed]
  schedule:
    - cron: '0 */4 * * *'  # Every 4 hours
  workflow_dispatch:

jobs:
  detect-failures:
    name: Detect Recent Failures
    runs-on: ubuntu-latest
    if: github.event.workflow_run.conclusion == 'failure' || github.event_name == 'schedule'
    steps:
      - uses: actions/checkout@v4

      - name: Analyze Failure
        id: analyze
        run: |
          # Get failed workflow info
          WORKFLOW_NAME="${{ github.event.workflow_run.name }}"
          RUN_ID="${{ github.event.workflow_run.id }}"

          # Download logs and analyze
          gh run view $RUN_ID --log > failure_log.txt

          # Detect common patterns
          if grep -q "ENOSPC" failure_log.txt; then
            echo "recovery_action=cleanup_disk" >> $GITHUB_OUTPUT
          elif grep -q "rate limit" failure_log.txt; then
            echo "recovery_action=wait_and_retry" >> $GITHUB_OUTPUT
          elif grep -q "ModuleNotFoundError" failure_log.txt; then
            echo "recovery_action=reinstall_dependencies" >> $GITHUB_OUTPUT
          else
            echo "recovery_action=manual_review" >> $GITHUB_OUTPUT
          fi

      - name: Execute Recovery
        if: steps.analyze.outputs.recovery_action != 'manual_review'
        run: |
          case "${{ steps.analyze.outputs.recovery_action }}" in
            cleanup_disk)
              echo "Cleaning up disk space..."
              docker system prune -af
              ;;
            wait_and_retry)
              echo "Waiting for rate limit reset..."
              sleep 300
              gh workflow run "${{ github.event.workflow_run.name }}"
              ;;
            reinstall_dependencies)
              echo "Reinstalling dependencies..."
              pip install -r requirements.txt --force-reinstall
              ;;
          esac

      - name: Feedback Loop
        run: |
          # Record recovery attempt
          cat > recovery_log.json << EOF
          {
            "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
            "workflow": "${{ github.event.workflow_run.name }}",
            "run_id": "${{ github.event.workflow_run.id }}",
            "recovery_action": "${{ steps.analyze.outputs.recovery_action }}",
            "success": true
          }
          EOF

      - name: Upload Report
        uses: actions/upload-artifact@v6
        with:
          name: self-healing-report-${{ github.run_number }}
          path: recovery_log.json
          retention-days: 30
```

**Migration Plan**:
1. Create self-healing-system.yml
2. Test failure detection
3. Verify recovery actions
4. Disable old workflows

---

### Consolidation Group 9: Cognitive Workflows
**Current**: 4 workflows
**Target**: 2 workflows (action+decision, aftermath+feed)
**Reduction**: -2 workflows

#### Workflows to Consolidate
1. `cognitive-action.yml` (1 artifact) + `cognitive-decision.yml` (1 artifact) → `cognitive-action-decision.yml`
2. `cognitive-aftermath.yml` (1 artifact) + `cognitive-brain-feed.yml` (1 artifact) → `cognitive-analysis-feed.yml`

**Migration Plan**:
1. Create 2 consolidated workflows
2. Test cognitive brain integration
3. Verify artifact uploads
4. Disable old workflows

---

### Consolidation Group 10: Misc/Deprecated Workflows
**Current**: 5+ workflows
**Target**: 0 (move to misc/)
**Reduction**: -5 workflows

#### Workflows to Move
1. `aftermath.yml` (deprecated, empty triggers)
2. `flatten-repo-download.yml` (one-time use)
3. `zendesk-quantum-packaging.yml` (experimental)
4. `biweekly-research-digest.yml` (low priority)
5. Other experimental/one-off workflows

**Migration Plan**:
1. Create `.github/misc/` directory
2. Move deprecated workflows
3. Add README explaining misc folder
4. Update documentation

---

## 🎯 Phase 1 Summary

**Consolidations**: 10 groups  
**Workflows Reduced**: 30 (108 → 78)  
**New Workflows Created**: 8  
**Workflows Deprecated**: 38 (net -30)  
**Timeline**: 4 phases  
**Risk**: Low-Medium (comprehensive testing required)

---

*Document continues with Phase 2 and Phase 3 in next sections...*
*This is Part 1 of 3 - See continuation below*
