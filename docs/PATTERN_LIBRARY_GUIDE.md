# Pattern Library Guide
**Last Updated:** 2026-07-11
**Version:** v0.2.1

> Complete guide to discovering, applying, and integrating patterns from the Phase 15-16 Pattern Library (Lane 2 Output).

**Version**: 0.1.0 | **Last Updated**: 2026-07-11 | **Patterns**: 40+ curated patterns

---

## Table of Contents

1. [Overview](#overview)
2. [Pattern Categories](#pattern-categories)
3. [Discovery & Search](#discovery--search)
4. [Applying Patterns](#applying-patterns)
5. [Pattern Combinations](#pattern-combinations)
6. [CI/CD Integration](#cicd-integration)
7. [Best Practices](#best-practices)
8. [API Reference](#api-reference)

---

## Overview

The Phase 15-16 Pattern Library contains **40+ curated patterns** discovered through autonomous execution across 5 parallel lanes:

- **8** CI Failure Patterns
- **7** Test Flakiness Patterns
- **6** Performance Optimization Patterns
- **6** Security Patterns
- **5** Documentation Patterns
- **4** Deployment Patterns
- **4** Monitoring & Observability Patterns

### Quick Facts

| Metric | Value |
|--------|-------|
| **Total Patterns** | 40+ |
| **High Confidence** | 8 patterns (≥0.90) |
| **Medium-High Confidence** | 12 patterns (0.75-0.89) |
| **Medium Confidence** | 15 patterns (0.60-0.74) |
| **Acceptable** | 5 patterns (0.50-0.59) |
| **Average Confidence** | 0.78 |
| **Success Rate** | 90.5% |
| **Deployment** | SQLite + Redis Cache |

### Storage Locations

```
.codex/
 patterns/
 ci_failure_patterns.yaml # CI failure patterns
 test_flakiness_patterns.yaml # Test reliability patterns
 performance_patterns.yaml # Performance patterns
 security_patterns.yaml # Security patterns
 documentation_patterns.yaml # Documentation patterns
 deployment_patterns.yaml # Deployment patterns
 observability_patterns.yaml # Monitoring patterns
 pattern_library_metadata.json # Index and metadata
```

---

## Pattern Categories

### 1. CI Failure Patterns (8 patterns)

**Purpose**: Detect and automatically fix common CI pipeline failures.

#### High-Confidence Patterns (0.90+)

| Pattern | Confidence | Success Rate | Fix |
|---------|-----------|--------------|-----|
| Missing dependency | 0.95 | 98% | Run `pip install -r requirements.txt` |
| Python import error | 0.92 | 96% | Fix sys.path, install package |
| Flaky Docker build | 0.91 | 94% | Add retry logic, optimize Dockerfile |

#### Medium-Confidence Patterns (0.60-0.89)

| Pattern | Confidence | Success Rate |
|---------|-----------|--------------|
| Timeout in test suite | 0.87 | 91% |
| Network connectivity | 0.82 | 88% |
| Race condition | 0.78 | 85% |

### 2. Test Flakiness Patterns (7 patterns)

**Purpose**: Identify and stabilize unreliable tests.

**Common Causes**:
- Race conditions in concurrent tests
- Timing-dependent assertions
- Unordered collection comparisons
- Mock/stub timing issues
- External service timeouts

**Example Flaky Test Pattern**:
```yaml
pattern_id: flaky_test_concurrent
name: "Race Condition in Concurrent Test"
confidence: 0.88
root_causes:
 - "Missing mutex or lock primitive"
 - "Unordered list assertions"
 - "Timing-dependent sleeps"
fixes:
 - "Use thread-safe data structures"
 - "Add explicit synchronization"
 - "Use deterministic test conditions"
```

### 3. Performance Optimization Patterns (6 patterns)

**Purpose**: Improve system performance and resource efficiency.

**Common Areas**:
- Build parallelization (25 min 8 min)
- Cache optimization (cache hit: 20% 85%)
- Dependency resolution
- Test suite optimization
- Database query optimization

**Example Pattern**:
```yaml
pattern_id: perf_parallel_jobs
name: "Parallelization of Sequential Jobs"
confidence: 0.90
baseline_duration_minutes: 25
optimized_duration_minutes: 8
improvement_percent: 68
implementation:
 - "Identify independent job dependencies"
 - "Use GitHub Actions matrices"
 - "Add proper cache strategy"
```

### 4. Security Patterns (6 patterns)

**Purpose**: Detect and remediate security vulnerabilities.

**Categories**:
- Authentication/Authorization (2)
- Injection Vulnerabilities (2)
- Data Protection (1)
- Infrastructure Security (1)

**Example Pattern**:
```yaml
pattern_id: sec_sql_injection
name: "SQL Injection Vulnerability"
severity: CRITICAL
confidence: 0.93
indicators:
 - "String concatenation in SQL queries"
 - "Unvalidated user input in WHERE clause"
fixes:
 - "Use parameterized queries"
 - "Use ORM with prepared statements"
 - "Validate/sanitize all inputs"
```

### 5. Documentation Patterns (5 patterns)

**Purpose**: Maintain high-quality, current documentation.

**Patterns**:
- Broken internal links (0 target)
- Stale documentation (>90 days)
- Missing API examples
- Incomplete parameter documentation
- Inconsistent formatting

### 6. Deployment Patterns (4 patterns)

**Purpose**: Ensure reliable, consistent deployments.

**Patterns**:
- Container image optimization
- Kubernetes resource management
- Blue-green deployment validation
- Rollback trigger conditions

### 7. Monitoring & Observability Patterns (4 patterns)

**Purpose**: Implement comprehensive observability.

**Patterns**:
- Log collection and aggregation
- Metrics and alerting rules
- Distributed tracing setup
- Health check configuration

---

## Discovery & Search

### 1. Using the REST API

#### Search by Lane

```bash
# Get all security patterns
curl "http://localhost:8000/api/memory/retrieve?lane_name=security" \
 -H "Authorization: ******"

# Response
{
 "data": {
 "patterns": [
 {
 "id": "mem_sec_001",
 "pattern_type": "sql_injection",
 "confidence": 0.93,
 "usage_count": 23
 },
 {
 "id": "mem_sec_002",
 "pattern_type": "auth_bypass",
 "confidence": 0.89,
 "usage_count": 18
 }
 ]
 }
}
```

#### Search by Type

```bash
# Get all flaky test patterns
curl "http://localhost:8000/api/memory/retrieve?pattern_type=flaky_test&limit=10" \
 -H "Authorization: ******"
```

#### Search by Tags

```bash
# Get patterns related to concurrency
curl "http://localhost:8000/api/memory/retrieve?tag=concurrency&limit=5" \
 -H "Authorization: ******"
```

#### Advanced Search with Confidence Filtering

```bash
# Get high-confidence patterns
curl "http://localhost:8000/api/memory/retrieve?lane_name=ci&min_confidence=0.85&limit=10" \
 -H "Authorization: ******"
```

### 2. Python SDK Search

```python
from codex_sdk import PatternLibrary

lib = PatternLibrary(base_url="http://localhost:8000")

# Find patterns for your problem
patterns = lib.search(
 lane_name="ci",
 pattern_type="timeout",
 min_confidence=0.80
)

for pattern in patterns:
 print(f"Pattern: {pattern.name}")
 print(f"Confidence: {pattern.confidence:.0%}")
 print(f"Fix: {pattern.recommended_fix}")
```

### 3. YAML Pattern Index

Browse `.codex/patterns/` for direct access:

```bash
# List all CI patterns
cat .codex/patterns/ci_failure_patterns.yaml | grep "pattern_id:"

# View specific pattern
cat .codex/patterns/security_patterns.yaml | grep -A 20 "pattern_id: sec_sql_injection"
```

### 4. Documentation Search

Use `docs/PATTERN_LIBRARY_INDEX.md` for searchable index:

| Pattern | Category | Confidence | Lane | Link |
|---------|----------|-----------|------|------|
| Missing dependency | CI | 0.95 | ci | [Link](./patterns/ci_failure_patterns.yaml#missing-dependency) |
| Race condition | Test Flakiness | 0.88 | testing | [Link](./patterns/test_flakiness_patterns.yaml#race-condition) |

---

## Applying Patterns

### 1. CI Failure Pattern Example

**Scenario**: Your CI pipeline fails with "ModuleNotFoundError: No module named 'codex'"

**Step 1**: Identify the pattern
```bash
# Search for import error patterns
curl "http://localhost:8000/api/memory/retrieve?pattern_type=import_error" \
 -H "Authorization: ******"
```

**Step 2**: Review the pattern
```yaml
name: "Python Import Error - Module Not Found"
confidence: 0.92
root_causes:
 - Missing dependency in requirements.txt
 - Wrong Python path
 - Missing __init__.py files
 - Dependency not installed in CI environment

fixes:
 - Add to requirements.txt
 - Ensure pip install runs
 - Check Python sys.path
 - Verify package structure
```

**Step 3**: Apply the fix
```bash
# Option 1: Add dependency
echo "codex-ml>=0.1.0" >> requirements.txt

# Option 2: Ensure install in CI
- name: Install dependencies
 run: pip install -r requirements.txt

# Option 3: Fix sys.path
import sys
sys.path.insert(0, '/home/runner/work/_codex_/_codex_')
```

### 2. Security Pattern Example

**Scenario**: CodeQL detects SQL injection in query builder

**Step 1**: Identify the pattern
```python
patterns = lib.search(
 lane_name="security",
 pattern_type="sql_injection"
)
```

**Step 2**: Review vulnerability
```python
pattern = patterns[0]
print(pattern.indicators)
# Output:
# - "String concatenation in SQL queries"
# - "Unvalidated user input in WHERE clause"
```

**Step 3**: Apply fix
```python
# VULNERABLE
query = f"SELECT * FROM users WHERE id = {user_id}"
result = db.execute(query)

# SECURE - Use parameterized queries
query = "SELECT * FROM users WHERE id = ?"
result = db.execute(query, (user_id,))
```

### 3. Performance Pattern Example

**Scenario**: CI pipeline takes 25 minutes, targeting 12 minutes

**Pattern**: Parallelization of Sequential Jobs

```yaml
baseline: 25 minutes
target: 12 minutes
improvement: 52%

steps:
 1. Analyze job dependencies
 2. Identify independent jobs
 3. Convert to matrix strategy
 4. Configure artifact caching
 5. Optimize layer caching
```

**Implementation**:
```yaml
# .github/workflows/code-quality.yml
jobs:
 quality-analysis:
 strategy:
 matrix:
 analysis-type: [lint, type-check, complexity, security]
 runs-on: ubuntu-latest
 steps:
 - uses: actions/checkout@v4
 - run: python scripts/ci/run_analysis.py ${{ matrix.analysis-type }}

 # Reduced from 25 min sequential to ~8 min parallel
```

---

## Pattern Combinations

### 1. CI + Testing Pattern Combination

**Goal**: Fix flaky tests and improve CI reliability

**Patterns**:
1. Fix flaky tests (test_flakiness)
2. Fix race conditions (ci_failure)
3. Optimize parallel execution (performance)

**Example Workflow**:
```python
from codex_sdk import PatternLibrary, PatternCombo

lib = PatternLibrary()

# Create combination
combo = PatternCombo(
 name="Stabilize CI Pipeline",
 patterns=[
 "flaky_test_race_condition",
 "ci_timeout_handling",
 "perf_parallel_jobs"
 ]
)

# Apply patterns in sequence
results = combo.apply(
 workflow_path=".github/workflows/ci.yml",
 auto_commit=True
)
```

### 2. Security + Deployment Pattern Combination

**Goal**: Secure deployment pipeline

**Patterns**:
1. Security scanning patterns
2. Deployment validation patterns
3. Observability patterns

### 3. Documentation + Quality Pattern Combination

**Goal**: Improve documentation health

**Patterns**:
1. Fix broken links
2. Update stale documentation
3. Add missing examples

---

## CI/CD Integration

### 1. Automatic Pattern Application in GitHub Actions

```yaml
# .github/workflows/pattern-healer.yml
name: Automatic Pattern Application

on:
 pull_request:
 branches: [main]
 workflow_dispatch:

jobs:
 apply-patterns:
 runs-on: ubuntu-latest
 steps:
 - uses: actions/checkout@v4
 - uses: actions/setup-python@v4
 with:
 python-version: '3.10'
 
 - name: Install SDK
 run: pip install codex-sdk
 
 - name: Detect failures
 run: python scripts/ci/detect_patterns.py
 
 - name: Apply patterns
 run: python scripts/ci/apply_patterns.py
 
 - name: Create fix PR
 uses: peter-evans/create-pull-request@v5
 with:
 commit-message: "Fix: Apply patterns from library"
 branch: pattern-fix-${{ github.run_id }}
```

### 2. Pattern-Based Test Selection

```python
# scripts/ci/smart_test_selection.py
from codex_sdk import PatternLibrary

lib = PatternLibrary()

# Get flaky test patterns
flaky_patterns = lib.search(
 pattern_type="flaky_test",
 min_confidence=0.80
)

# Extract affected test files
test_files = set()
for pattern in flaky_patterns:
 for file in pattern.affected_files:
 test_files.add(file)

# Run only affected tests
print("::set-output name=tests::" + " ".join(test_files))
```

### 3. Dynamic Gate Configuration

```yaml
# .github/workflows/smart-gates.yml
jobs:
 determine-gates:
 runs-on: ubuntu-latest
 outputs:
 gates: ${{ steps.select.outputs.gates }}
 steps:
 - name: Select gates from patterns
 id: select
 run: |
 python scripts/ci/determine_gates.py
 echo "gates=$(cat gates.json)" >> $GITHUB_OUTPUT

 run-gates:
 needs: determine-gates
 runs-on: ubuntu-latest
 steps:
 - run: python scripts/ci/run_gates.py '${{ needs.determine-gates.outputs.gates }}'
```

---

## Best Practices

### 1. Pattern Selection

 **DO**:
- Choose patterns with confidence ≥ 0.75
- Match patterns to your problem domain
- Use combinations for complex issues
- Start with high-confidence patterns

 **DON'T**:
- Apply low-confidence patterns (< 0.50) without validation
- Mix incompatible patterns
- Skip reading pattern rationale
- Apply without understanding root cause

### 2. Pattern Application

 **DO**:
- Test patterns in branch first
- Review generated fixes before merging
- Update pattern feedback after use
- Document applied patterns

 **DON'T**:
- Auto-merge pattern fixes to main
- Apply multiple conflicting patterns simultaneously
- Ignore pattern validation failures
- Skip testing after pattern application

### 3. Pattern Maintenance

 **DO**:
- Update pattern confidence scores based on results
- Add new patterns as you discover them
- Archive patterns that stop working
- Share patterns across lanes

 **DON'T**:
- Let patterns become stale
- Forget to update affected_files list
- Mix old and new pattern versions
- Duplicate patterns across files

---

## API Reference

### Pattern Storage Schema

```python
class Pattern(BaseModel):
 id: str # Unique identifier
 name: str # Human-readable name
 pattern_type: str # Category (ci_failure, security, etc.)
 lane_name: str # Source lane
 
 # Quality metrics
 confidence: float # 0.0-1.0 confidence score
 success_rate: float # Historical success rate
 usage_count: int # Times applied
 
 # Description
 description: str # What this pattern solves
 root_causes: List[str] # Underlying issues
 indicators: List[str] # How to detect
 
 # Implementation
 fixes: List[str] # Recommended fixes
 implementation_steps: List[str] # How-to steps
 code_example: str # Code snippet
 
 # Metadata
 tags: List[str] # Searchable tags
 affected_files: List[str] # Files/patterns affected
 performance_impact: str # "high", "medium", "low"
 severity: str # "critical", "high", "medium", "low"
 
 # Tracking
 created_at: datetime
 last_used: datetime
 usage_history: List[dict] # Audit trail
 
 # Relations
 related_patterns: List[str] # IDs of related patterns
 conflicting_patterns: List[str] # Patterns to avoid combining
```

### REST Endpoints

```
GET /api/memory/retrieve # Search patterns
POST /api/memory/store # Add new pattern
GET /api/memory/stats # Pattern statistics
POST /api/memory/stm-push # Cache pattern access
```

### Search Query Examples

```bash
# Exact type match
curl ".../api/memory/retrieve?pattern_type=sql_injection"

# Multiple tags (OR)
curl ".../api/memory/retrieve?tag=security&tag=critical"

# Confidence threshold
curl ".../api/memory/retrieve?min_confidence=0.85"

# Lane-specific
curl ".../api/memory/retrieve?lane_name=security"

# Complex query
curl ".../api/memory/retrieve?lane_name=security&pattern_type=injection&min_confidence=0.80"
```

---

## Troubleshooting

### "Pattern not found for my problem"

1. Check pattern categories (40 patterns across 7 categories)
2. Try different search terms
3. Look for related patterns with `related_patterns` field
4. Request new pattern creation from lane team

### "Pattern applied but didn't work"

1. Verify problem matches pattern indicators
2. Check confidence score (≥0.75 recommended)
3. Review pattern notes and assumptions
4. Try related patterns
5. Report issue with fix_report flag

### "Pattern conflicts with my code"

1. Check `conflicting_patterns` field
2. Review pattern scope and limitations
3. Apply compatible patterns instead
4. Contact pattern maintainer

---

**Related Documentation**:
- [API Reference](./API_REFERENCE_PHASE_15_16.md)
- [Architecture Guide](./ARCHITECTURE_PHASE_15_16.md)
- [Pattern Library Index](./PATTERN_LIBRARY_INDEX.md)
- [Lane 2 Execution Report](../accountability/LANE_2_PATTERN_LIBRARY_REPORT.md)

