# Workflow Compliance Checklist (Phase 3.7)

## Status: 22 Critical Violations Identified | 89.6% Overall Compliance

---

## TIER 1: CRITICAL FIXES (Do This Week)

### Concurrency Rule Violations (3 workflows)

- [ ] **ci-pattern-healer.yml**
  - [ ] Add concurrency block with branch-scoped group
  - [ ] Set `cancel-in-progress: true`
  - [ ] Validate via `python3 -c "import yaml; yaml.safe_load(open(...))"`
  - [ ] Test: Push to feature branch, verify run cancellation

- [ ] **copilot-agent-session-done.yml**
  - [ ] Add concurrency block with branch-scoped group
  - [ ] Set `cancel-in-progress: true`
  - [ ] Validate YAML syntax
  - [ ] Test in PR environment

- [ ] **phase-8-3-perf-monitor.yml**
  - [ ] Add concurrency block with branch-scoped group
  - [ ] Set `cancel-in-progress: true`
  - [ ] Validate YAML syntax
  - [ ] Test scheduled trigger

### Job Timeout Violations (7 workflows)

- [ ] **build-preview-image.yml**
  - [ ] Add `timeout-minutes: 60` to main job (Docker build - heavy)
  - [ ] Reason: Container image builds can take 45-55 minutes

- [ ] **data-quality-suite.yml**
  - [ ] Add `timeout-minutes: 45` to main job (Quality analysis - medium)
  - [ ] Reason: Full data quality checks require time

- [ ] **docker-build-push.yml**
  - [ ] Add `timeout-minutes: 60` to main job (Docker build - heavy)
  - [ ] Note: This is a deployment workflow (also needs approval gate)

- [ ] **embedding-index-rebuild.yml**
  - [ ] Add `timeout-minutes: 60` to main job (Index rebuild - heavy)
  - [ ] Reason: Vector index generation is compute-intensive

- [ ] **release.yml**
  - [ ] Add `timeout-minutes: 30` to main job (Release - standard)
  - [ ] Reason: Standard CI workflow

- [ ] **rust_swarm_ci.yml**
  - [ ] Add `timeout-minutes: 60` to main job (Rust build - heavy)
  - [ ] Reason: Rust compilation is memory/CPU intensive

- [ ] **scheduled-archival.yml**
  - [ ] Add `timeout-minutes: 30` to main job (Archival - standard)
  - [ ] Reason: Standard maintenance workflow

**Validation Script:**
```bash
for wf in build-preview-image data-quality-suite docker-build-push \
          embedding-index-rebuild release rust_swarm_ci scheduled-archival; do
  echo "Checking $wf..."
  grep -q "timeout-minutes" ".github/workflows/${wf}.yml" && \
    echo "✅ PASS" || echo "❌ FAIL"
done
```

---

## TIER 2: HIGH-PRIORITY FIXES (Next 1-2 weeks)

### Action Version Updates (65 violations across workflows)

**Priority Actions to Update:**

- [ ] `actions/setup-rust-toolchain`
  - [ ] 7 workflows affected
  - [ ] Update from SHA-pin to `@v1`
  - [ ] Reason: Enables maintenance updates, security patches

- [ ] `actions/checkout`
  - [ ] 6 workflows affected
  - [ ] Update from SHA-pin to `@v4`
  - [ ] Reason: v4 has performance improvements, better caching

- [ ] `create-github-app-token`
  - [ ] 4 workflows affected
  - [ ] Update from SHA-pin to `@v1`
  - [ ] Reason: Version-tagged enables upstream maintenance

- [ ] `codecov-action`
  - [ ] 4 workflows affected
  - [ ] Upgrade from v3 to `@v4`
  - [ ] Reason: v4 includes security fixes, new features

- [ ] `setup-buildx-action`
  - [ ] 4 workflows affected
  - [ ] Update from SHA-pin to `@v3`
  - [ ] Reason: Version-tagged enables auto-updates

**Verification:**
```bash
# Find all SHA-pinned actions
grep -r "@[a-f0-9]\{40\}" .github/workflows/ | wc -l
# Target: 0 SHA pins (after fixes)

# Find all v4+ pinned actions
grep -r "@v[4-9]" .github/workflows/ | wc -l
# Target: 100% of actions at v4+
```

---

## TIER 3: MEDIUM-PRIORITY FIXES (This month)

### Approval Gates for Deployment Workflows (5 workflows)

These workflows affect production and need approval gates.

- [ ] **pypi-publish.yml**
  - [ ] Add environment: production
  - [ ] Require approval in GitHub UI before publish
  - [ ] Document approval checklist

- [ ] **docker-build-push.yml**
  - [ ] Add environment: production-docker
  - [ ] Require approval before pushing to registry
  - [ ] Include docker image digest in approval context

- [ ] **release.yml**
  - [ ] Add environment: production-github
  - [ ] Require approval for version releases
  - [ ] Pin to v3+ action versions

- [ ] **publish_dashboard_release.yml**
  - [ ] Add environment: production-dashboard
  - [ ] Public dashboard requires governance

- [ ] **unified-deployment.yml**
  - [ ] Review current approval setup
  - [ ] Ensure all deployment jobs have environments

**Implementation Template:**
```yaml
jobs:
  deploy:
    environment:
      name: production
      url: https://pypi.org/project/codex/
    runs-on: ubuntu-latest
    timeout-minutes: 60
    steps:
      # deployment logic
```

### WEC (Workflow Execution Checklist) Integration

- [ ] **Review PR template** (`.github/pull_request_template.md`)
  - [ ] Ensure WEC section is present
  - [ ] Add checkboxes for:
    - [ ] Concurrency groups use branch-scoped pattern
    - [ ] All jobs have explicit `timeout-minutes`
    - [ ] Deployment workflows use `cancel-in-progress: false`
    - [ ] YAML validated (no parse errors)
    - [ ] Actions are version-pinned (v4+)

- [ ] **Update workflow-execution-gate.yml**
  - [ ] Ensure it parses WEC section
  - [ ] Block merges if checklist incomplete

- [ ] **Wire 50+ workflows** into WEC system
  - [ ] Focus on: agent coordination, security, deployment
  - [ ] Test: Create PR, verify checklist enforcement

---

## TIER 4: ONGOING MAINTENANCE (Quarterly)

### Monthly Compliance Audit

- [ ] Run ghalint linter
  ```bash
  ghalint lint --config .ghalint.yaml .github/workflows/
  ```
  
- [ ] Check for new action versions
  ```bash
  gh workflow list --all | wc -l  # Should be ~212
  ```

- [ ] Verify token health
  ```bash
  # Triggers token-probe.yml
  ```

### Quarterly Review

- [ ] CODEX_MASTER_KEY rotation (90-day cycle)
  - [ ] Generate new PAT
  - [ ] Update repository secrets
  - [ ] Verify with token-probe
  - [ ] Update .codex/archive/reports/AGENT_ACCOUNTABILITY_REPORT.md

- [ ] Matrix strategy consistency check
  - [ ] Ensure all matrix jobs have proper strategy
  - [ ] Check `fail-fast` and `max-parallel` settings

- [ ] Coverage: Ensure 100% of workflows in scope

---

## Validation Checklist

### Before Committing Changes

- [ ] **YAML Syntax:**
  ```bash
  python3 -c "
  import yaml
  for wf in *.yml:
    yaml.safe_load(open(wf))
    print(f'✅ {wf}')
  "
  ```

- [ ] **Concurrency:**
  ```bash
  grep -c "github.head_ref\|github.ref" *.yml | awk -F: '{sum += $2} END {print sum " workflows with branch scoping"}'
  ```

- [ ] **Timeouts:**
  ```bash
  for wf in *.yml; do
    jobs=$(python3 -c "import yaml; print(len(yaml.safe_load(open('$wf')).get('jobs', {})))")
    timeouts=$(grep -c "timeout-minutes" "$wf")
    if [ "$jobs" -eq "$timeouts" ]; then echo "✅ $wf"; else echo "❌ $wf"; fi
  done
  ```

- [ ] **Actions Updated:**
  ```bash
  # Should return 0 (no SHA pins)
  grep -r "@[a-f0-9]\{40\}" .github/workflows/ | wc -l
  ```

### After Merging PR

- [ ] **Watch workflows** on main branch
  - [ ] All should complete within expected timeframes
  - [ ] No hung jobs

- [ ] **Verify CI health**
  - [ ] `ci-health-monitor.yml` should pass
  - [ ] No unexplained failures

- [ ] **Check audit trail**
  - [ ] `.codex/audit/operations.jsonl` updated
  - [ ] All changes logged

---

## Remediation Scripts

### 1. Add Concurrency to Workflow

```bash
#!/bin/bash
# Usage: ./add_concurrency.sh ci-pattern-healer.yml

WF=$1
cat > /tmp/concurrency.yaml << 'EOF'
concurrency:
  group: ${{ github.workflow }}-${{ github.head_ref || github.ref }}
  cancel-in-progress: true

EOF

# Insert after 'on:' section
python3 << PYTHON
import yaml

with open('$WF', 'r') as f:
    doc = yaml.safe_load(f)

# Add concurrency if missing
if 'concurrency' not in doc:
    doc['concurrency'] = {
        'group': '${{ github.workflow }}-${{ github.head_ref || github.ref }}',
        'cancel-in-progress': True
    }
    
    with open('$WF', 'w') as f:
        yaml.dump(doc, f, default_flow_style=False, sort_keys=False)
    print(f"✅ Added concurrency to $WF")
else:
    print(f"✅ {WF} already has concurrency")
PYTHON
```

### 2. Add Timeout to Job

```bash
#!/bin/bash
# Usage: ./add_timeout.sh docker-build-push.yml build 60

WF=$1
JOB=$2
TIMEOUT=$3

python3 << PYTHON
import yaml

with open('$WF', 'r') as f:
    doc = yaml.safe_load(f)

jobs = doc.get('jobs', {})
if '$JOB' in jobs:
    if 'timeout-minutes' not in jobs['$JOB']:
        jobs['$JOB']['timeout-minutes'] = int($TIMEOUT)
        with open('$WF', 'w') as f:
            yaml.dump(doc, f, default_flow_style=False, sort_keys=False)
        print(f"✅ Added timeout-minutes: $TIMEOUT to $JOB in $WF")
    else:
        print(f"✅ $JOB already has timeout-minutes")
PYTHON
```

### 3. Validate All Workflows

```bash
#!/bin/bash
# Comprehensive validation

echo "=== YAML VALIDATION ==="
for wf in .github/workflows/*.yml; do
  python3 -c "import yaml; yaml.safe_load(open('$wf'))" && echo "✅ $wf" || echo "❌ $wf"
done

echo ""
echo "=== CONCURRENCY CHECK ==="
for wf in .github/workflows/*.yml; do
  grep -q "github.head_ref\|github.ref" "$wf" && echo "✅ $wf" || echo "⚠️  $wf"
done

echo ""
echo "=== TIMEOUT CHECK ==="
for wf in .github/workflows/*.yml; do
  jobs=$(python3 -c "import yaml; doc=yaml.safe_load(open('$wf')); print(len(doc.get('jobs',{})))")
  timeouts=$(grep -c "timeout-minutes" "$wf" || echo 0)
  if [ "$jobs" -eq "$timeouts" ]; then 
    echo "✅ $wf ($jobs jobs)"
  else 
    echo "⚠️  $wf ($jobs jobs, $timeouts timeouts)"
  fi
done
```

---

## Sign-Off

- [ ] **Governance Guardian** reviews all 10 CRITICAL violations
- [ ] **Security Team** approves action version updates
- [ ] **Infrastructure Team** validates timeout assignments
- [ ] **DevOps Lead** signs off on deployment approval gates
- [ ] **All fixes merged** to main branch
- [ ] **CI passes** on all remediated workflows
- [ ] **Post-merge audit** confirms 99%+ compliance

---

## Links & References

- **Audit Report:** `.codex/PHASE_3_7_WORKFLOW_COMPLIANCE_AUDIT.md`
- **Best Practices:** `.codex/docs/WORKFLOW_BEST_PRACTICES.md`
- **Execution Gate:** `.github/workflows/workflow-execution-gate.yml`
- **Token Rotation:** WORKFLOW_BEST_PRACTICES.md §9
- **ghalint:** https://github.com/suzuki-shunsuke/ghalint

---

**Checklist Version:** 1.0 | Phase 3.7 | Compliance Guardian  
**Last Updated:** 2026-03-15  
**Next Review:** 2026-04-15 (30-day follow-up)

