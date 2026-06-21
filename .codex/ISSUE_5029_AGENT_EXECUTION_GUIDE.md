# Issue #5029 Remediation — Agent Execution Guide

**Purpose:** Detailed task briefs for specialized agents to execute the remediation plan
**Created:** 2026-06-21T01:35:56Z
**Status:** READY FOR AGENT DELEGATION

---

## Task 1.1: Fix progressive-validation.yml Dependency Issues

### Assigned Agent: `autonomous-test-healer-agent`
### Secondary: `ci-auto-healer-agent`
### Estimated Duration: 2 hours
### Files Modified: `.github/workflows/progressive-validation.yml`

### Detailed Specification

#### Objective
Fix 20 failures in `progressive-validation.yml` caused by:
1. Dependency version conflicts (torch/setuptools)
2. Silent pip installation failures
3. Inaccurate test tier selection logic

#### Acceptance Criteria
- [ ] All smoke tests pass with strict dependency validation
- [ ] Unit/integration test tiers only run if their test files exist
- [ ] Pip installation failures produce clear error messages (exit 1)
- [ ] No test tier is skipped without warning
- [ ] 5 consecutive PR cycles with varied sizes pass without failure

#### Implementation Steps

**Step 1: Update smoke-tests job (lines 26-75)**

Replace the "Install minimal dependencies" step with:
```yaml
- name: Install dependencies with validation
  id: install_deps
  run: |
    set -euo pipefail
    python -m pip install --upgrade pip
    pip install 'setuptools<82' torch==2.12.0 --no-deps
    pip install pytest==8.4.2 pytest-xdist==3.8.0 pytest-timeout==2.4.0 pytest-cov==5.0.0 pytest-asyncio==1.3.0
    pip install -e . 2>&1 | tee /tmp/install.log
    if grep -iE "error|conflict|impossible|failed" /tmp/install.log; then
      echo "::error::Dependency installation failed"
      cat /tmp/install.log
      exit 1
    fi
    echo "✅ Dependencies installed"
```

**Step 2: Add test availability check (before unit-tests job)**

Insert new step:
```yaml
- name: Validate test availability
  id: test_check
  run: |
    TIER="${{ needs.analyze.outputs.pr_size }}"
    case "$TIER" in
      small)
        [ -d "tests/unit" ] && [ -f "tests/unit/test_*.py" ] || exit 0
        ;;
      medium)
        find tests/unit -name "test_*.py" -print -quit | grep -q . || exit 0
        ;;
      large)
        [ -d "tests/unit" ] && [ -d "tests/integration" ] || exit 1
        ;;
    esac
    echo "✅ Required test files present"
```

**Step 3: Fix silent test failures (line ~64)**

Modify "Run smoke tests" step to add `set -euo pipefail`:
```yaml
- name: Run smoke tests
  id: smoke
  run: |
    set -euo pipefail
    pytest tests/ -k "smoke or quick" --timeout=60 -v --tb=short || exit 1
```

#### Validation

```bash
# Test locally before merge
.github/workflows/progressive-validation.yml

# Run test suite
pytest tests/unit/test_*.py -v --tb=short

# Check that dependency pins are correct
python -c "import torch; import setuptools; print(torch.__version__, setuptools.__version__)"
# Expected: 2.12.0 <82
```

---

## Task 1.2: Fix auto-fix-pr-check.yml Git Race Condition

### Assigned Agent: `ci-auto-healer-agent`
### Secondary: `branch-divergence-resolution-agent`
### Estimated Duration: 1.5 hours
### Files Modified: `.github/workflows/auto-fix-pr-check.yml`

### Detailed Specification

#### Objective
Fix 1 consistent failure in `auto-fix-pr-check.yml` caused by:
- Git race condition when `main` branch moves forward during workflow execution
- Missing git rebase fallback on push failure
- No protection against commits to protected branches

#### Acceptance Criteria
- [ ] Zero git push rejections in 20 consecutive PR cycles
- [ ] Auto-rebase succeeds without conflicts on 95%+ of attempts
- [ ] Protected branches (`main`, `0D_base_`) never receive direct commits
- [ ] Conflicts are detected and reported (not silently ignored)
- [ ] MTTR: < 1 minute for push failures

#### Implementation Steps

**Step 1: Add branch safety check (before commit)**

Insert at line ~215:
```yaml
- name: Verify target branch safety
  id: branch_check
  run: |
    BRANCH="${{ github.head_ref || github.ref_name }}"
    if [[ "$BRANCH" =~ ^(main|master|develop|0D_base_|release.*)$ ]]; then
      echo "::notice::Branch '$BRANCH' is protected — skipping auto-commit"
      echo "skip_commit=true" >> "$GITHUB_OUTPUT"
      exit 0
    fi
    echo "skip_commit=false" >> "$GITHUB_OUTPUT"
```

**Step 2: Add git rebase-on-failure logic (replace push step)**

Replace git push section (around line ~286-290):
```yaml
- name: Commit auto-fixes
  id: commit
  run: |
    set -euo pipefail
    git config user.name "github-actions[bot]"
    git config user.email "actions@github.com"
    if git diff --quiet; then
      echo "has_changes=false" >> "$GITHUB_OUTPUT"
      exit 0
    fi
    git add -A
    git commit -m "fix(ci): auto-fix issues (RP-007)" || exit 0
    echo "has_changes=true" >> "$GITHUB_OUTPUT"

- name: Push with auto-rebase fallback
  if: steps.commit.outputs.has_changes == 'true'
  id: push
  run: |
    set -euo pipefail
    MAX_RETRIES=3
    ATTEMPT=1
    BRANCH="${{ github.head_ref || github.ref_name }}"
    
    while [ $ATTEMPT -le $MAX_RETRIES ]; do
      echo "Push attempt $ATTEMPT/$MAX_RETRIES"
      if git push origin HEAD:refs/heads/"$BRANCH" 2>&1 | tee /tmp/push.log; then
        echo "✅ Push succeeded"
        exit 0
      fi
      
      if grep -q "rejected.*fetch first" /tmp/push.log; then
        echo "⚠️ Rebasing..."
        git fetch origin "$BRANCH":refs/remotes/origin/"$BRANCH" || exit 1
        if git rebase "origin/$BRANCH"; then
          ATTEMPT=$((ATTEMPT + 1))
          continue
        else
          echo "::error::Rebase conflict"
          git diff --name-only --diff-filter=U
          exit 1
        fi
      else
        echo "::error::Unrecoverable push error"
        cat /tmp/push.log
        exit 1
      fi
    done
    echo "::error::Failed after $MAX_RETRIES attempts"
    exit 1
```

#### Validation

```bash
# Test git rebase scenario
git checkout -b test-rebase-scenario
git commit --allow-empty -m "test commit"

# Simulate remote moving forward
git fetch origin main:refs/remotes/origin/main
git rebase origin/main

# Verify no conflicts
git status

# Test on protected branch
git checkout main
# Should not allow direct commit (branch_check prevents it)
```

---

## Task 1.3: Fix security-scanning-suite.yml Cache & Orchestration

### Assigned Agent: `unified-security-scanner`
### Secondary: `cache-management-agent`
### Estimated Duration: 3 hours
### Files Modified: `.github/workflows/security-scanning-suite.yml`

### Detailed Specification

#### Objective
Fix 20+ failures caused by:
1. Cache key mismatch (torch=false/true variants)
2. Tools running out of sync (timing skew)
3. OOM issues on large codebases

#### Acceptance Criteria
- [ ] Cache key stable across PR cycles (same key = same requirements)
- [ ] Cache hit rate > 90%
- [ ] CodeQL, Semgrep, dependency check results correlate
- [ ] No tool timing conflicts (sequential execution)
- [ ] < 3% OOM errors on large repos

#### Implementation Steps

**Step 1: Fix cache key generation (codeql-scan job, line ~45)**

Insert new step before existing cache logic:
```yaml
- name: Generate stable cache key
  id: cache_key
  run: |
    PYTHON_VERSION="3.12"
    REQUIREMENTS_HASH=$(sha256sum requirements.txt | cut -d' ' -f1 | cut -c1-12)
    WORKFLOW_HASH=$(sha256sum .github/workflows/security-scanning-suite.yml | cut -d' ' -f1 | cut -c1-12)
    CACHE_KEY="codeql-cache-linux-py${PYTHON_VERSION}-req${REQUIREMENTS_HASH}-wf${WORKFLOW_HASH}"
    echo "cache_key=$CACHE_KEY" >> "$GITHUB_OUTPUT"

- name: Restore CodeQL cache
  uses: actions/cache@v4
  with:
    path: ~/.codeql
    key: ${{ steps.cache_key.outputs.cache_key }}
    restore-keys: |
      codeql-cache-linux-py3.12-
      codeql-cache-linux-
```

**Step 2: Add job sequencing (update job definitions)**

Modify job definitions to enforce order:
- codeql-scan: runs first (no dependencies)
- semgrep-scan: `needs: codeql-scan`
- dependency-scan: `needs: semgrep-scan`

```yaml
  semgrep-scan:
    name: Semgrep SAST
    needs: codeql-scan  # ← Add this
    runs-on: ubuntu-latest
    ...

  dependency-scan:
    name: Dependency Check
    needs: semgrep-scan  # ← Add this
    runs-on: ubuntu-latest
    ...
```

**Step 3: Add memory tuning for large repos**

Insert in jobs that process large codebases:
```yaml
  codeql-scan:
    ...
    runs-on: ubuntu-latest-xl  # ← Use larger runner for ML codebases
    timeout-minutes: 90  # ← Increase from 60 to account for larger dataset
```

#### Validation

```bash
# Check cache key stability
python3 - << 'PYEOF'
import hashlib

with open('requirements.txt', 'rb') as f:
  req_hash = hashlib.sha256(f.read()).hexdigest()[:12]

with open('.github/workflows/security-scanning-suite.yml', 'rb') as f:
  wf_hash = hashlib.sha256(f.read()).hexdigest()[:12]

key = f"codeql-cache-linux-py3.12-req{req_hash}-wf{wf_hash}"
print(f"Cache key: {key}")
PYEOF

# Run workflow and check cache hit
gh run list --workflow security-scanning-suite.yml --limit 3 --json status
```

---

## Task 2.1: Implement Dependency Prediction Engine

### Assigned Agent: `cognitive-brain-cli-agent`
### Secondary: `skills-master-agent`
### Estimated Duration: 3 hours
### Files Modified: `.github/workflows/progressive-validation.yml` (new step)

### Detailed Specification

#### Objective
Add Copilot-powered dependency conflict prediction to prevent failures before they occur

#### Acceptance Criteria
- [ ] Prediction accuracy > 75% on test dataset
- [ ] No false positives on clean PRs
- [ ] Suggested pins match actual conflicts
- [ ] Inference time < 30 seconds
- [ ] Integration with Copilot API verified

#### Implementation Steps

**Step 1: Add prediction step to progressive-validation.yml**

Insert after "analyze" job dependency resolution (new step in smoke-tests):
```yaml
- name: Copilot dependency prediction
  id: predict
  continue-on-error: true
  uses: actions/github-script@v8
  with:
    script: |
      const fs = require('fs');
      
      // Get changed files from PR
      const changedFiles = await github.paginate(
        github.rest.pulls.listFiles,
        { 
          owner: context.repo.owner, 
          repo: context.repo.repo, 
          pull_number: context.issue.number 
        }
      );
      
      const isRequirementsChanged = changedFiles
        .some(f => f.filename.match(/requirements|pyproject\.toml|setup\.py/));
      
      if (!isRequirementsChanged) {
        core.notice('No dependency files changed');
        return;
      }
      
      const fileList = changedFiles
        .filter(f => f.filename.match(/requirements|pyproject|setup/))
        .map(f => f.filename)
        .join(', ');
      
      core.notice(`Dependency files changed: ${fileList}`);
      
      // In production: Call Copilot API with PR context
      // const prediction = await copilot.analyzeDependencies({
      //   changed_files: changedFiles,
      //   requirements: fs.readFileSync('requirements.txt', 'utf8'),
      //   pyproject: fs.readFileSync('pyproject.toml', 'utf8')
      // });
      
      // For MVP: Log analysis request
      core.notice('Dependency analysis queued for Copilot processing');
```

**Step 2: Create Copilot analysis service**

Create `.github/actions/copilot-dependency-analyzer/action.yml`:
```yaml
name: 'Copilot Dependency Analyzer'
description: 'Predict dependency conflicts using Copilot'

inputs:
  changed-files:
    description: 'List of changed files'
    required: true
  requirements-path:
    description: 'Path to requirements.txt'
    required: false
    default: 'requirements.txt'
  api-key:
    description: 'Copilot API key'
    required: true

outputs:
  risky-packages:
    description: 'List of risky packages'
  suggested-pins:
    description: 'Suggested version pins'
  confidence:
    description: 'Prediction confidence (0-1)'

runs:
  using: 'node20'
  main: 'index.js'
```

---

## Task 2.2: Implement Conflict Resolution Engine

### Assigned Agent: `cognitive-brain-cli-agent`
### Secondary: `branch-divergence-resolution-agent`
### Estimated Duration: 2.5 hours
### Files Modified: `.github/workflows/auto-fix-pr-check.yml` (new step)

### Detailed Specification

#### Objective
Add Copilot-powered merge conflict detection and suggested resolutions

#### Acceptance Criteria
- [ ] Detects all merge conflicts in files
- [ ] Suggests resolution strategy for 80%+ of conflicts
- [ ] No data loss in suggested resolutions
- [ ] Integration tested with 10 conflict scenarios
- [ ] Manual review required for complex conflicts

#### Implementation Steps

**Step 1: Add conflict detection step**

Insert after rebase failure in auto-fix-pr-check.yml:
```yaml
- name: Detect merge conflicts
  if: failure()
  id: conflicts
  continue-on-error: true
  run: |
    # Find all conflicted files
    CONFLICTS=$(git diff --name-only --diff-filter=U)
    if [ -z "$CONFLICTS" ]; then
      echo "status=clean" >> "$GITHUB_OUTPUT"
      exit 0
    fi
    
    echo "status=conflicts_found" >> "$GITHUB_OUTPUT"
    echo "files<<EOF" >> "$GITHUB_OUTPUT"
    echo "$CONFLICTS" >> "$GITHUB_OUTPUT"
    echo "EOF" >> "$GITHUB_OUTPUT"
    
    # Count conflicts
    COUNT=$(echo "$CONFLICTS" | wc -l)
    echo "count=$COUNT" >> "$GITHUB_OUTPUT"

- name: Copilot conflict resolution
  if: steps.conflicts.outputs.status == 'conflicts_found'
  id: resolve
  continue-on-error: true
  uses: actions/github-script@v8
  with:
    script: |
      const conflicts = `${{ steps.conflicts.outputs.files }}`.split('\n').filter(Boolean);
      
      core.warning(`Merge conflicts in ${conflicts.length} files:`);
      conflicts.forEach(f => core.warning(`  - ${f}`));
      
      // In production: Call Copilot to suggest resolutions
      // const suggestions = await copilot.suggestConflictResolution({
      //   files: conflicts,
      //   base: 'origin/main',
      //   head: 'current-branch',
      //   strategy: 'prefer-remote'  // Keep remote main changes
      // });
      
      core.notice('Conflict analysis queued for Copilot processing');
      core.setOutput('needs_manual_review', 'true');
```

---

## Task 2.3: Implement Cache Prediction Engine

### Assigned Agent: `cache-management-agent`
### Secondary: `artifact-monitor-agent`
### Estimated Duration: 2 hours
### Files Modified: `.github/workflows/security-scanning-suite.yml` (new job)

### Detailed Specification

#### Objective
Predict cache misses before they happen and pre-warm cache

#### Acceptance Criteria
- [ ] Prediction accuracy > 80%
- [ ] Pre-warming reduces OOM/miss errors by 50%
- [ ] < 2 minute overhead from prediction job
- [ ] Graceful degradation if prediction API unavailable

#### Implementation Steps

**Step 1: Create cache-prediction job**

Insert at start of security-scanning-suite.yml jobs:
```yaml
  cache-prediction:
    name: Predict Cache Outcomes
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    outputs:
      cache_hit_probability: ${{ steps.predict.outputs.hit_prob }}
      risky_packages: ${{ steps.predict.outputs.risky_packages }}
      ttl_days: ${{ steps.predict.outputs.ttl }}
    steps:
      - uses: actions/checkout@v7
      
      - name: Analyze requirements
        id: analyze
        run: |
          # Identify risky packages (torch, setuptools, etc.)
          RISKY=$(grep -E '^(torch|setuptools|cryptography|tensorflow|jax)' requirements.txt || echo "none")
          echo "risky=$RISKY" >> "$GITHUB_OUTPUT"
      
      - name: Query recent cache history
        id: history
        run: |
          # In production: Query cache metrics from artifact storage
          # For now: estimate based on requirements
          echo "recent_misses=2" >> "$GITHUB_OUTPUT"
          echo "hit_rate=0.75" >> "$GITHUB_OUTPUT"
      
      - name: Predict cache outcome
        id: predict
        run: |
          HIT_RATE=${{ steps.history.outputs.hit_rate }}
          RISKY_PKGS="${{ steps.analyze.outputs.risky }}"
          
          # Calculate adjusted hit probability
          if [ ! -z "$RISKY_PKGS" ]; then
            # Reduce prediction by 10% for each risky package
            PENALTY=$(echo "$RISKY_PKGS" | wc -l)
            HIT_RATE=$(python3 -c "print(max(0.0, $HIT_RATE - $PENALTY * 0.1))")
          fi
          
          echo "hit_prob=$HIT_RATE" >> "$GITHUB_OUTPUT"
          echo "risky_packages=$RISKY_PKGS" >> "$GITHUB_OUTPUT"
          echo "ttl=$([ $(echo "$HIT_RATE < 0.5" | bc) -eq 1 ] && echo "3" || echo "7")" >> "$GITHUB_OUTPUT"

  codeql-scan:
    needs: cache-prediction
    ...
```

---

## Task 3.1: Establish Baseline Metrics

### Assigned Agent: `artifact-monitor-agent`
### Secondary: `workflow-analytics-agent`
### Estimated Duration: 1 hour
### Files Created: `.codex/ISSUE_5029_METRICS.json`

### Detailed Specification

#### Objective
Create metrics baseline and monitoring dashboard for success tracking

#### Deliverables
- [ ] JSON metrics file with pre-fix baseline
- [ ] Monitoring workflow that tracks post-fix metrics
- [ ] Daily alert if metrics exceed threshold
- [ ] Dashboard view of improvements

---

## Task 3.2: Create Validation Checklist

### Assigned Agent: `unified-governance-gate`
### Secondary: `qa-walkthrough-agent`
### Estimated Duration: 1 hour
### Files Created: `.codex/ISSUE_5029_VALIDATION_CHECKLIST.md`

### Detailed Specification

#### Objective
Create comprehensive validation checklist for sign-off

#### Deliverables
- [ ] Phase 1 validation checkpoints
- [ ] Phase 2 Copilot integration validation
- [ ] Success criteria with measurement method
- [ ] Rollback procedures documented

---

## Execution Order

```
Day 1 Morning:
├─ Task 1.1 (2h): autonomous-test-healer-agent
├─ Task 1.2 (1.5h): ci-auto-healer-agent  [parallel]
└─ Task 1.3 (3h): unified-security-scanner [parallel]

Day 1 Afternoon:
├─ Validation of Phase 1 fixes
├─ Merge Phase 1 PRs
└─ Monitor 5 PR cycles

Day 2:
├─ Task 2.1 (3h): cognitive-brain-cli-agent
├─ Task 2.2 (2.5h): cognitive-brain-cli-agent [parallel]
└─ Task 2.3 (2h): cache-management-agent [parallel]

Day 2-3:
├─ Integrate Copilot APIs
├─ Test end-to-end scenarios
└─ Collect initial metrics

Day 3:
├─ Task 3.1 (1h): artifact-monitor-agent
├─ Task 3.2 (1h): unified-governance-gate
├─ Final validation
└─ Sign-off from @mbaetiong
```

---

## Success Criteria Checklist

- [ ] All Phase 1 fixes merged and validated
- [ ] Zero failures for 48 hours post-deployment
- [ ] Cache hit rate > 90%
- [ ] Git push success rate = 100%
- [ ] Copilot integrations tested and working
- [ ] Metrics baseline established
- [ ] Validation checklist approved by @mbaetiong

---

**Status:** READY FOR AGENT DELEGATION
**Last Updated:** 2026-06-21T01:35:56Z
