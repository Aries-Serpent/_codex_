# ⚡ AGENT PERFORMANCE & OPTIMIZATION GUIDE

**Version:** 2.0.0  
**Generated:** 2026-06-20T06:51:49.390052  
**Purpose:** Classify agents by performance and optimize execution

---

## Performance Classification

Agents are classified into three tiers based on typical execution time:

---

## TIER 1: FAST AGENTS (<1 minute)

### Agents (18)
- policy-coach-agent
- owner-approval-guard
- dependency-conflict-agent
- link-validator-agent (basic check)
- secret-detection-agent (pre-commit)
- pii-scrubber
- cross-platform-filename-validator
- terminology-consistency-agent (lightweight)
- session-analysis-agent
- recon-scout-agent

### Characteristics
- ✅ Model: Haiku 4.5 (optimal)
- ✅ Token Usage: <500 tokens typical
- ✅ Perfect for: Pre-commit gates, policy checks
- ✅ Parallelizable: Yes (up to 20+)

### Optimization Tips
1. **Batch operations:** Run 5+ checks in parallel
2. **Cache trivial decisions:** Policy validation results
3. **Use Haiku exclusively:** Cost <$0.01 per run
4. **Pre-filter inputs:** Skip obvious passes

### Example Execution
```yaml
workflow:
  parallel_lanes: 10  # No resource contention
  agents:
    - policy-coach-agent (policy/1.md)
    - policy-coach-agent (policy/2.md)
    - policy-coach-agent (policy/3.md)
    ... up to 10
```

---

## TIER 2: MEDIUM AGENTS (1-10 minutes)

### Key Agents (35+)
- ci-failure-resolution-agent (5-8 min)
- test-alignment-fixer (3-5 min)
- code-analysis-agent (5-7 min)
- unified-coverage-agent (5-15 min depending on test suite)
- link-validator-agent (full scan, 5-10 min)
- git-repository-cleanup (2-5 min)
- performance-regression-detector (5-8 min)
- config-validator (2-4 min)
- documentation-quality-agent (3-7 min)
- keyword-migration-assistant (5-10 min)

### Characteristics
- ✅ Model: Haiku 4.5 or Sonnet 4.6 (context-dependent)
- ✅ Token Usage: 1K-5K tokens
- ✅ Perfect for: Main workflows, quality gates
- ✅ Parallelizable: Yes (4-lane limit recommended)

### Optimization Tips
1. **Limit parallelism:** Max 4 medium agents in parallel
2. **Use Haiku when possible:** Model selection (see Pattern 9)
3. **Cache baselines:** Config/structure from previous runs
4. **Stream results:** Don't wait for everything

### Performance Breakdown by Agent Type

**Analysis Agents (5-7 min):**
- code-analysis-agent: Analyzes code patterns
- test-failure-analyzer-agent: Examines test failures
- dependency-vulnerability-scanner: Scans dependencies
- performance-regression-detector: Detects regressions

**Fixing Agents (3-5 min):**
- test-alignment-fixer: Aligns tests to code changes
- config-validator: Validates configurations
- link-validator-agent: Validates/fixes links

**Coverage Agents (5-15 min):**
- unified-coverage-agent: Depends on test suite size
  - Small (<100 tests): 5 min
  - Medium (100-1000): 10 min
  - Large (>1000): 15 min

### Parallelization Strategy
```yaml
workflow:
  phase1_parallel:
    - code-analysis-agent
    - test-failure-analyzer-agent
    - dependency-vulnerability-scanner
    - performance-regression-detector
  phase2_sequential:
    - test-alignment-fixer
    - config-validator
```

### Cost Analysis
- Single Sonnet run: ~$0.05
- 4 parallel Haiku runs: ~$0.02 total
- Sequential vs Parallel: 5 min vs 2 min (2.5x faster)

---

## TIER 3: SLOW AGENTS (10+ minutes)

### Key Agents (12)
- unified-security-scanner (15-45 min)
  - SAST: 10-20 min
  - Dependency check: 5-10 min
  - Secret scan: 5-10 min
- unified-doc-agent (10-30 min)
- autonomous-test-healer-agent (10-30 min)
- ml-validation-suite-agent (15-30 min)
- codeql-alert-resolution-agent (15-40 min)
- mutation-testing-agent (20-60 min)
- integration-test-runner (10-60 min)

### Characteristics
- ✅ Model: Sonnet 4.6 (required for complexity)
- ✅ Token Usage: 5K-20K tokens
- ✅ Perfect for: Critical workflows, pre-release
- ✅ Parallelizable: Limited (1-2 at a time recommended)

### Optimization Tips
1. **Run independently:** Don't parallelize with other slow agents
2. **Use Sonnet exclusively:** Complex analysis required
3. **Parallelize internal components:** Many break down into faster tasks
4. **Timeout gracefully:** Set limits and fallback

### Why Slow Agents Are Slow

**unified-security-scanner (15-45 min):**
- Multiple scan types (SAST + dependency + secrets)
- Can run in parallel internally (4 lanes)
- Complex vulnerability correlation
- Integration with multiple external tools

**autonomous-test-healer-agent (10-30 min):**
- Runs tests to diagnose
- Applies fixes iteratively
- Re-runs to verify
- Could have 3-5 iterations

**mutation-testing-agent (20-60 min):**
- Generates mutations (~1000s)
- Runs tests for each mutation
- Analyzes kill rate
- Extremely expensive but valuable

### Parallelization Within Slow Agents
```yaml
unified-security-scanner:
  internal_parallelization: 4_lanes
  lanes:
    - lane1: SAST_scanning (10 min)
    - lane2: dependency_check (8 min)
    - lane3: secret_detection (8 min)
    - lane4: correlation (2 min)
  total_time: max(10, 8, 8, 2) + correlation = 12 min
```

### Cost Analysis
- Single slow agent: ~$0.20-0.50
- Sonnet 4.6 at 15 min: ~0.30-50K tokens
- Better than 3x sequential: parallel internal lanes

### When to Use Slow Agents
- Pre-release verification
- Critical PR reviews
- Security audits
- Comprehensive coverage analysis
- **NOT** for every commit

### When to Avoid
- Simple PRs (<100 lines)
- Hot-fix branches
- Documentation-only changes
- CI-only workflow runs

---

## Performance Optimization Strategies

### Strategy 1: Adaptive Model Selection

**Decision Logic:**
```python
def select_model(task_complexity):
    if task_complexity < 3:
        return "haiku-4.5"      # <0.01 cost
    elif task_complexity < 6:
        return "haiku-4.5"      # 60% tasks
    else:
        return "sonnet-4.6"     # 30% tasks
```

**Cost Savings:** 50-60% reduction

### Strategy 2: Result Caching

**Implementation:**
```yaml
cache:
  key: "{module}_{commit_sha}"
  ttl: 24h
  scope: organization
```

**Cost Savings:** 80-90% on re-runs

### Strategy 3: Batch Operations

**Good:**
```yaml
unified-coverage-agent:
  modules: [src/auth, src/api, src/utils]  # Batch 3
  time: 10 min
```

**Better:**
```yaml
unified-coverage-agent:
  modules: [src/auth]  # Single
  time: 8 min
# Cost: 8 min instead of 10 min, but 3x throughput
```

### Strategy 4: Staging Pipelines

**Phase 1 (Fast):** Policy, link validation (2 min)
**Phase 2 (Medium):** Code analysis, tests (7 min)
**Phase 3 (Slow):** Security, mutation (30 min, only if phase 1-2 pass)

**Cost Savings:** Block at gate instead of running all

### Strategy 5: Resource Pooling

**Shared Cache:**
```
Session 1: SAST scan → cache baseline
Session 2: Reuse cached baseline → 80% faster
```

**Parallel Execution:**
```
4 independent medium agents in parallel
vs
Sequential execution (4x slower)
```

---

## Token Usage by Agent Class

### Fast Agents (<1 min)
- Tokens: 100-500
- Model: Haiku 4.5
- Cost: <$0.01
- Example: policy-coach-agent (150 tokens)

### Medium Agents (1-10 min)
- Tokens: 1K-5K
- Model: Haiku (50%) or Sonnet (50%)
- Cost: $0.01-0.10
- Example: test-alignment-fixer (2K tokens, 5 min)

### Slow Agents (10+ min)
- Tokens: 5K-20K
- Model: Sonnet 4.6 (required)
- Cost: $0.20-0.50
- Example: unified-security-scanner (12K tokens, 25 min)

### Total Budget Estimates
- **Per PR:** 5K-15K tokens (~$0.10-0.30)
- **Per Release:** 50K tokens (~$1.00)
- **Per Month:** 1M+ tokens (~$20)

---

## Recommended Execution Profiles

### Profile 1: Fast (2 min)
**Use for:** Every commit
```
policy-coach-agent +
link-validator-agent (basic) +
secret-detection-agent
Total: 2 min, <$0.01
```

### Profile 2: Standard (10 min)
**Use for:** Every PR
```
phase1: policy + secrets (2 min)
phase2: code-analysis + test-alignment (7 min)
phase3: reject if phase1 fails
Total: 10 min, ~$0.10
```

### Profile 3: Comprehensive (35 min)
**Use for:** Pre-release only
```
phase1: policy + secrets (2 min)
phase2: code + tests + performance (7 min)
phase3: security + coverage (15 min)
phase4: mutation testing (10 min)
phase5: reject if any phase fails
Total: 35 min, ~$0.50
```

### Profile 4: Critical Release (60+ min)
**Use for:** Major releases, security fixes
```
all agents from comprehensive +
external audit tooling +
manual review gates
Total: 60+ min, >$1.00
```

---

## Performance Dashboard Metrics

Track these metrics for each agent:

| Metric | Fast | Medium | Slow |
|--------|------|--------|------|
| Avg Runtime | <1 min | 5 min | 25 min |
| P95 Runtime | <1.5 min | 8 min | 35 min |
| Token Usage | <500 | 2K | 10K |
| Success Rate | >99% | >95% | >90% |
| Cost/Run | <$0.01 | $0.05 | $0.30 |

---

## Metadata

- **Generated:** 2026-06-20T06:51:49.390062
- **Classification Basis:** 2026-06 execution metrics
- **Authority:** @mbaetiong
- **Next Update:** 2026-07-20

