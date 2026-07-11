# PATTERN LIBRARY USAGE BRIEF — DISCOVER & APPLY REUSABLE DECISION TEMPLATES

**Version:** 2.0.0  
**Created:** 2026-07-11T02:11:00Z  
**Status:** READY FOR ALL AGENTS  
**Scope:** Discovering, matching, and applying high-recurrence patterns from knowledge graph  
**Campaign:** Cognitive App Enhancement — Phase 15  

---

## 1. PATTERN LIBRARY OVERVIEW

The **Pattern Library** is a curated, high-confidence subset of the Long-Term Memory (LTM) containing the **50+ most successful patterns** across all prior campaigns.

### Pattern Categories (by Lane)

#### Security Lane Patterns
- `cve-token-rotation-fix` — Fix token rotation timing issues (confidence: 0.92, usage: 3)
- `oauth-scope-validation` — Validate OAuth scope before token generation (0.91, usage: 5)
- `sql-injection-prevention` — Parameterize queries to prevent SQL injection (0.88, usage: 2)
- `jwt-expiration-handler` — Handle JWT expiration gracefully (0.86, usage: 4)

#### Coverage Lane Patterns
- `ml-module-unit-test-generation` — Generate unit tests for ML trainer (0.78, usage: 2)
- `async-function-coverage` — Add coverage for async/await code (0.82, usage: 3)
- `exception-handling-tests` — Add tests for exception paths (0.85, usage: 6)
- `edge-case-test-generation` — Identify and test edge cases (0.79, usage: 4)

#### Stability Lane Patterns
- `flaky-test-threading-fix` — Fix threading.Race via Barrier sync (0.88, usage: 7)
- `random-seed-determinism` — Use seed_control for deterministic tests (0.91, usage: 9)
- `async-timeout-fix` — Add asyncio.wait_for timeouts (0.84, usage: 5)
- `concurrent-resource-cleanup` — Proper cleanup in concurrent tests (0.86, usage: 3)

#### Complexity Lane Patterns
- `extract-helper-methods` — Break large functions into smaller helpers (0.82, usage: 8)
- `simplify-conditionals` — Replace nested ifs with guards (0.87, usage: 6)
- `reduce-parameter-count` — Group related parameters into objects (0.80, usage: 4)

#### Docs Lane Patterns
- `fix-broken-markdown-links` — Correct internal link paths (0.95, usage: 15)
- `consolidate-duplicate-sections` — Merge redundant documentation (0.78, usage: 2)
- `update-api-reference` — Keep API docs in sync with code (0.89, usage: 7)

---

## 2. PATTERN DISCOVERY WORKFLOW

### Step 1: Query Pattern Library at Lane Start

When a lane begins execution, query the pattern library for applicable patterns:

```bash
#!/usr/bin/env bash
set -euo pipefail

LANE="security"  # Replace with lane name
COGNITIVE_APP_HOST="http://localhost:8765"

# Query high-recurrence patterns for this lane
PATTERNS=$(curl -s "${COGNITIVE_APP_HOST}/api/memory/retrieve" \
    -H "Authorization: ******" \
    -G \
    --data-urlencode "lane=${LANE}" \
    --data-urlencode "high_recurrence=true" \
    --data-urlencode "limit=20")

echo "🎯 High-recurrence patterns for lane: ${LANE}"
echo "$PATTERNS" | jq '.patterns[] | {pattern_name, confidence, usage_count, success_rate}'
```

### Step 2: Assess Pattern Applicability

Each pattern has metadata that helps determine if it applies to current objective:

```python
def assess_pattern_applicability(pattern, current_objective):
    """Assess if pattern is applicable to current lane objective"""
    
    # Score factors (0-1 each, higher is better)
    factors = {
        "confidence": pattern["confidence"],  # How sure are we?
        "usage": min(pattern["usage_count"] / 10, 1.0),  # How proven is it?
        "recency": 1.0 if (now() - pattern["last_used"]) < timedelta(days=7) else 0.8,
        "relevance": assess_keyword_overlap(pattern["tags"], current_objective)
    }
    
    # Weighted score
    weights = {"confidence": 0.40, "usage": 0.25, "recency": 0.15, "relevance": 0.20}
    applicability_score = sum(factors[k] * weights[k] for k in factors)
    
    print(f"Pattern: {pattern['pattern_name']}")
    print(f"  Applicability: {applicability_score:.2%}")
    print(f"  Factors: confidence={factors['confidence']:.0%}, usage={factors['usage']:.0%}, "
          f"recency={factors['recency']:.0%}, relevance={factors['relevance']:.0%}")
    
    # Recommendation
    if applicability_score >= 0.75:
        print(f"  ✅ RECOMMEND: Apply this pattern")
        return True
    elif applicability_score >= 0.50:
        print(f"  ⚠️ MAYBE: Apply with caution")
        return "caution"
    else:
        print(f"  ❌ NOT APPLICABLE: Skip this pattern")
        return False
```

### Step 3: Match Pattern to Specific Tasks

Once a pattern is deemed applicable, map it to specific tasks:

```python
def match_pattern_to_tasks(pattern, lane_tasks):
    """Map pattern to specific lane tasks"""
    
    matches = []
    
    for task in lane_tasks:
        # Keyword overlap
        pattern_keywords = set(pattern.get("tags", []))
        task_keywords = set(task.get("tags", []))
        overlap = pattern_keywords & task_keywords
        
        # Semantic similarity (simple: check if pattern description contains task keywords)
        semantic_match = any(
            keyword.lower() in pattern["description"].lower()
            for keyword in task_keywords
        )
        
        if overlap or semantic_match:
            matches.append({
                "task": task["name"],
                "pattern": pattern["pattern_name"],
                "match_type": "keyword" if overlap else "semantic",
                "confidence": pattern["confidence"]
            })
    
    return matches

# Example usage
lane_tasks = [
    {"name": "Fix CVE-2026-XXXXX", "tags": ["security", "cve", "token-rotation"]},
    {"name": "Validate OAuth scope", "tags": ["security", "oauth", "validation"]}
]

patterns = query_pattern_library(lane="security", high_recurrence=True)
for pattern in patterns[:5]:  # Top 5 patterns
    matches = match_pattern_to_tasks(pattern, lane_tasks)
    if matches:
        print(f"Pattern {pattern['pattern_name']} matches {len(matches)} tasks")
        for match in matches:
            print(f"  - {match['task']} (match_type: {match['match_type']}, conf: {match['confidence']:.0%})")
```

---

## 3. PATTERN APPLICATION WORKFLOW

### Step 1: Apply Pattern to Lane

Once a pattern is matched to a task, apply it:

```python
def apply_pattern_to_task(pattern, task, lane):
    """Apply a pattern to a specific lane task"""
    
    print(f"📋 Applying pattern: {pattern['pattern_name']}")
    print(f"   Task: {task['name']}")
    print(f"   Description: {pattern['description']}")
    
    # 1. Extract pattern implementation details
    implementation = parse_pattern_description(pattern["description"])
    
    # 2. Adapt implementation to current task
    adapted_impl = adapt_implementation(implementation, task)
    
    # 3. Execute adaptation
    try:
        result = execute_implementation(adapted_impl)
        print(f"   ✅ Successfully applied")
        
        # 4. Record success in outcome tracking
        record_pattern_outcome(
            pattern_id=pattern["pattern_id"],
            task=task["name"],
            outcome="success",
            confidence=pattern["confidence"]
        )
        
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        
        # 4. Record failure for future learning
        record_pattern_outcome(
            pattern_id=pattern["pattern_id"],
            task=task["name"],
            outcome="failure",
            error=str(e)
        )
        
        return False
```

### Step 2: Validate Pattern Outcome

After applying a pattern, validate that it achieved the intended effect:

```python
def validate_pattern_outcome(task, pattern, expected_effect):
    """Validate that applying pattern achieved expected effect"""
    
    print(f"🔍 Validating pattern outcome for task: {task['name']}")
    
    # Check multiple validation signals
    validations = {
        "code_change": validate_code_changed(task),
        "tests_pass": validate_tests_pass(task),
        "objective_met": validate_objective_met(task, expected_effect),
        "no_regressions": validate_no_regressions(task)
    }
    
    success_count = sum(1 for v in validations.values() if v)
    
    if success_count >= 3:  # At least 3/4 validations pass
        print(f"   ✅ VALIDATED: Pattern successfully applied ({success_count}/4 checks)")
        return True
    else:
        print(f"   ⚠️ INCONCLUSIVE: Only {success_count}/4 validations passed")
        print(f"     {validations}")
        return None  # Inconclusive
```

### Step 3: Record Outcome for Future Learning

```python
def record_pattern_outcome(pattern_id, task, outcome, confidence=None, error=None):
    """Record pattern application outcome for future learning"""
    
    # This data feeds back into the ML scoring system
    # to adjust pattern confidence scores over time
    
    payload = {
        "pattern_id": pattern_id,
        "task": task,
        "outcome": outcome,  # "success", "failure", "inconclusive"
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    
    if confidence:
        payload["confidence"] = confidence
    if error:
        payload["error_type"] = classify_error(error)
    
    # POST to Cognitive App (logs outcome, updates pattern scoring)
    requests.post(
        "http://localhost:8765/api/patterns/outcome",
        json=payload,
        headers={"Authorization": f"******"}
    )
    
    print(f"   📊 Outcome recorded: {outcome}")
```

---

## 4. LANE-SPECIFIC PATTERN APPLICATION GUIDE

### Security Lane

**Objective:** Fix 8+ high/critical vulnerabilities

**Applicable Patterns:**
1. `cve-token-rotation-fix` (confidence: 0.92)
   - Apply to: Any token rotation timing issues
   - Steps: Add barrier sync between token generation and usage

2. `oauth-scope-validation` (confidence: 0.91)
   - Apply to: OAuth flow vulnerabilities
   - Steps: Validate scope before token generation

3. `sql-injection-prevention` (confidence: 0.88)
   - Apply to: Database access vulnerabilities
   - Steps: Parameterize all SQL queries

**Implementation Example:**
```python
def apply_cve_fix_via_pattern(cve_id, vulnerability_type):
    """Apply appropriate pattern to CVE fix"""
    
    if vulnerability_type == "token_rotation":
        # Use cve-token-rotation-fix pattern
        pattern = retrieve_pattern("cve-token-rotation-fix")
        
        # Pattern implementation:
        # 1. Add threading.Barrier to sync token generation
        # 2. Add timeout for token expiration checks
        # 3. Add logging for token lifecycle
        
        return apply_pattern(pattern, cve_id)
    
    elif vulnerability_type == "oauth":
        # Use oauth-scope-validation pattern
        pattern = retrieve_pattern("oauth-scope-validation")
        
        # Pattern implementation:
        # 1. Validate scope before token generation
        # 2. Log validation failures
        # 3. Reject invalid scopes
        
        return apply_pattern(pattern, cve_id)
```

### Coverage Lane

**Objective:** Gap-fill coverage from 34.63% → 36%+ (≥1.5 point increase)

**Applicable Patterns:**
1. `ml-module-unit-test-generation` (confidence: 0.78)
   - Apply to: Untested ML trainer functions
   - Steps: Use AST to identify coverage gaps, generate unit tests

2. `exception-handling-tests` (confidence: 0.85)
   - Apply to: Exception paths with <50% coverage
   - Steps: Add tests for all raise/except blocks

3. `edge-case-test-generation` (confidence: 0.79)
   - Apply to: Functions with low branch coverage
   - Steps: Identify edge cases, add boundary tests

**Implementation Example:**
```python
def generate_coverage_tests_via_patterns(target_module):
    """Generate tests using applicable patterns"""
    
    # Query patterns applicable to coverage gap-filling
    patterns = query_pattern_library(
        lane="coverage",
        confidence_min=0.75,
        high_recurrence=True
    )
    
    for pattern in patterns:
        if pattern["pattern_name"] == "ml-module-unit-test-generation":
            # Apply AST-based test generation
            tests = generate_tests_ast(target_module)
            add_tests_to_suite(tests)
        
        elif pattern["pattern_name"] == "exception-handling-tests":
            # Generate tests for exception paths
            exception_tests = generate_exception_tests(target_module)
            add_tests_to_suite(exception_tests)
    
    # Run tests and measure coverage increase
    coverage_before = get_coverage_percentage()
    run_tests()
    coverage_after = get_coverage_percentage()
    
    return coverage_after - coverage_before  # Gap-fill amount
```

### Stability Lane

**Objective:** Eliminate 3 flaky tests (test failure rate ≤0.5%)

**Applicable Patterns:**
1. `flaky-test-threading-fix` (confidence: 0.88, usage: 7)
   - Apply to: Tests failing with threading errors
   - Steps: Add `threading.Barrier` for sync

2. `random-seed-determinism` (confidence: 0.91, usage: 9)
   - Apply to: Tests with non-deterministic failures
   - Steps: Use `random.seed(42)` with seed_control fixture

3. `async-timeout-fix` (confidence: 0.84, usage: 5)
   - Apply to: Async tests with timeout issues
   - Steps: Add `asyncio.wait_for` with reasonable timeout

**Implementation Example:**
```python
def fix_flaky_test_via_patterns(test_file, failure_patterns):
    """Identify and fix flaky test root causes"""
    
    # Classify failure pattern
    failure_type = classify_failure(failure_patterns)  # threading, async, random, etc.
    
    # Select appropriate pattern
    if failure_type == "threading":
        pattern = retrieve_pattern("flaky-test-threading-fix")
        # Add threading.Barrier to test
        
    elif failure_type == "random":
        pattern = retrieve_pattern("random-seed-determinism")
        # Add seed_control fixture
        
    elif failure_type == "async":
        pattern = retrieve_pattern("async-timeout-fix")
        # Add asyncio.wait_for with timeout
    
    # Apply pattern
    apply_pattern(pattern, test_file)
    
    # Re-run test 5x to confirm stability
    for i in range(5):
        if not run_test(test_file):
            return False  # Still failing
    
    return True  # Stable
```

### Complexity Lane

**Objective:** Reduce cyclomatic complexity by 15+ points

**Applicable Patterns:**
1. `extract-helper-methods` (confidence: 0.82, usage: 8)
   - Apply to: Functions with complexity >20
   - Steps: Extract sub-logic into helper methods

2. `simplify-conditionals` (confidence: 0.87, usage: 6)
   - Apply to: Nested if/else chains
   - Steps: Replace with guards and early returns

3. `reduce-parameter-count` (confidence: 0.80, usage: 4)
   - Apply to: Functions with 5+ parameters
   - Steps: Group related parameters into objects

**Implementation Example:**
```python
def refactor_complexity_via_patterns(target_function, target_complexity=18):
    """Refactor high-complexity functions using patterns"""
    
    current_complexity = calculate_cyclomatic_complexity(target_function)
    
    if current_complexity <= target_complexity:
        return True  # Already within target
    
    # Select refactoring patterns
    patterns = query_pattern_library(
        lane="complexity",
        high_recurrence=True
    )
    
    for pattern in patterns:
        if pattern["pattern_name"] == "extract-helper-methods":
            # Extract sub-logic into helpers
            helpers = extract_helpers(target_function)
            refactor_with_helpers(target_function, helpers)
        
        elif pattern["pattern_name"] == "simplify-conditionals":
            # Replace nested ifs with guards
            refactor_conditionals(target_function)
        
        # Re-measure complexity
        current_complexity = calculate_cyclomatic_complexity(target_function)
        if current_complexity <= target_complexity:
            return True
    
    return False  # Could not reach target
```

### Docs Lane

**Objective:** Fix 40+ broken internal links (100% link health)

**Applicable Patterns:**
1. `fix-broken-markdown-links` (confidence: 0.95, usage: 15)
   - Apply to: Any broken internal link
   - Steps: Identify correct path, update reference

2. `update-api-reference` (confidence: 0.89, usage: 7)
   - Apply to: API docs out of sync with code
   - Steps: Extract current API from code, regenerate docs

**Implementation Example:**
```python
def fix_links_via_patterns(doc_file):
    """Fix broken links using high-recurrence patterns"""
    
    broken_links = validate_markdown_links(doc_file)
    
    pattern = retrieve_pattern("fix-broken-markdown-links")
    
    for link in broken_links:
        # Pattern implementation: find correct path
        correct_path = find_correct_path(link["target"])
        
        if correct_path:
            update_link(doc_file, link["text"], correct_path)
            print(f"✅ Fixed: {link['text']} → {correct_path}")
        else:
            print(f"❌ Could not fix: {link['text']}")
    
    # Validate all links after fixes
    remaining_broken = validate_markdown_links(doc_file)
    
    return len(remaining_broken) == 0  # All fixed?
```

---

## 5. PATTERN LIFECYCLE & FEEDBACK LOOP

### Pattern Quality Evolution
```
Pattern Created (Campaign N)
  ↓ (if success_rate ≥ 80%)
Pattern Added to Library (Low Recurrence)
  ↓ (if used_count ≥ 3 and success ≥ 90%)
Pattern Promoted to High-Recurrence
  ↓ (if used_count ≥ 5 and success ≥ 95%)
Pattern Ranked Top-20 in Library
  ↓ (if used_count ≥ 7 and zero recent failures)
Pattern Featured in Lane Best-Practices
```

### Feedback Mechanism
```python
def update_pattern_confidence(pattern_id, outcome, effectiveness_score):
    """Update pattern confidence based on application outcomes"""
    
    # Bayesian update: P(effective | observed outcomes)
    # Using prior confidence and new evidence
    
    prior_confidence = get_pattern_confidence(pattern_id)
    
    if outcome == "success":
        # Boost confidence if effective
        new_confidence = prior_confidence + (0.05 * effectiveness_score)
    elif outcome == "failure":
        # Reduce confidence if ineffective
        new_confidence = prior_confidence - (0.10 * effectiveness_score)
    else:  # inconclusive
        # Slight adjustment for inconclusive
        new_confidence = prior_confidence * 0.98
    
    new_confidence = max(0.0, min(1.0, new_confidence))  # Clamp to [0, 1]
    
    # Store updated confidence
    requests.post(
        "http://localhost:8765/api/patterns/update-confidence",
        json={
            "pattern_id": pattern_id,
            "confidence": new_confidence,
            "outcome": outcome
        },
        headers={"Authorization": f"******"}
    )
    
    print(f"Pattern confidence updated: {prior_confidence:.2%} → {new_confidence:.2%}")
```

---

## 6. ESCALATION MATRIX (When NOT to Apply Pattern)

| Condition | Action |
|-----------|--------|
| Applicability score <0.50 | Skip pattern, don't force fit |
| Pattern confidence <0.75 | Proceed with caution, manual review |
| Pattern never used in current lane | Get approval from lane owner before applying |
| Pattern failed in last 2 uses | Mark as potentially broken, escalate to @mbaetiong |
| Pattern conflicts with task constraints | Adapt pattern (don't skip) or choose different pattern |

---

**Pattern Library Usage Brief Complete.** ✅  
**All agents use this guide** to discover, assess, and apply high-confidence patterns from the knowledge graph.  
**Key Takeaway:** Patterns are your accelerators—reuse what works, learn from what doesn't.
