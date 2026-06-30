---
title: "PHASE 9.2 Session Context Injection Specification"
version: "1.0"
date: "2026-06-26"
status: "FINAL"
---

# PHASE 9.2 Session Context Injection Specification

## Overview

This document defines how LTM patterns are injected into **session context** for Cognitive Brain integration. The session context is the memory provided to AI agents at the start of each task to ground them in known patterns and fix strategies.

**Key Constraints:**
- **Token Budget:** 2000 tokens maximum per session context
- **Priority Ordering:** Patterns ranked by recency, confidence, success rate, and relevance
- **Fallback Strategy:** Graceful degradation when budget exceeded; preserve highest-impact patterns
- **Versioning:** Support both old and new pattern formats; provide migration path

---

## Token Budget Allocation

### Total Budget: 2000 tokens

```
├─ Pattern Descriptions: 800 tokens (40%)
│  └─ 15-20 top patterns × ~40-50 tokens each
├─ Routing Rules: 600 tokens (30%)
│  └─ Agent assignments, conflict resolution, escalation paths
├─ Recent Fixes: 400 tokens (20%)
│  └─ Last 10-15 successful fixes with outcomes
└─ Escalation Guidance: 200 tokens (10%)
   └─ When to escalate, contact info, fallback strategies
```

### Dynamic Allocation

If one category exceeds budget:
1. Truncate descriptions (preserve pattern ID and confidence)
2. Remove oldest fixes from recent fixes section
3. Collapse routing rules (list agent only, no detail)
4. Remove escalation guidance (treat as optional)

---

## Priority Ordering Algorithm

### Scoring Function

```python
def calculate_session_priority(pattern):
    """
    Calculate priority score for session context injection.
    
    Higher score = higher priority for inclusion
    Range: [0.0, 1.0]
    """
    
    # 1. Recency component (35% weight)
    days_old = (now() - pattern.last_seen).days
    if days_old <= 7:
        recency_score = 1.0
    elif days_old <= 30:
        recency_score = 0.9 - ((days_old - 7) / 23 * 0.2)
    else:
        recency_score = max(0.0, 0.7 - ((days_old - 30) / 180 * 0.7))
    
    # 2. Confidence component (25% weight)
    confidence_score = pattern.confidence
    
    # 3. Success rate component (20% weight)
    success_score = min(1.0, pattern.success_rate / 0.95)  # Normalize to 95%
    
    # 4. Relevance component (20% weight)
    relevance_score = calculate_relevance_to_current_task(pattern)
    
    # Weighted sum
    priority = (
        recency_score * 0.35 +
        confidence_score * 0.25 +
        success_score * 0.20 +
        relevance_score * 0.20
    )
    
    return round(priority, 2)


def calculate_relevance_to_current_task(pattern):
    """
    Estimate pattern relevance to current failure domain.
    
    Examples:
    - Failure in tests/ directory → boost test-related patterns
    - Workflow failure → boost workflow-related patterns
    - Import error → boost import patterns
    """
    current_failure = get_current_failure_context()
    
    if not current_failure:
        return 0.5  # Neutral if no context
    
    # Check category match
    category_match = pattern.category in current_failure.categories
    file_type_match = any(
        ft in current_failure.file_types 
        for ft in pattern.typical_files
    )
    
    relevance = 0.0
    if category_match:
        relevance += 0.6
    if file_type_match:
        relevance += 0.4
    
    return min(1.0, relevance)
```

### Priority Tiers

```yaml
tier_1_critical:
  score: 0.95-1.0
  criteria: "Recent (< 7 days) + High confidence (> 0.95) + High success (> 95%)"
  allocation: 400 tokens
  example_patterns: [RP-005, RP-001, L-002]

tier_2_high:
  score: 0.85-0.94
  criteria: "Recent + High confidence + Medium-high success"
  allocation: 600 tokens
  example_patterns: [RP-006, RP-003, L-003]

tier_3_medium:
  score: 0.70-0.84
  criteria: "Moderate recency or confidence, stable success rate"
  allocation: 700 tokens
  example_patterns: [RP-008, RP-010, L-005]

tier_4_low:
  score: 0.50-0.69
  criteria: "Older patterns or lower confidence, but still relevant"
  allocation: 300 tokens
  example_patterns: [RP-009, RP-004]

tier_5_reference:
  score: < 0.50
  criteria: "Archived or very old patterns; reference only"
  allocation: 0 tokens (not included by default)
```

---

## Session Context Injection Format

### YAML Header

```yaml
---
session_context_version: "1.0"
injected_at: "2026-06-26T14:30:45Z"
budget_used: "1987 tokens"
budget_available: "2000 tokens"
budget_utilization: "99.35%"
patterns_included: 18
top_pattern_confidence: 0.97
avg_pattern_confidence: 0.84
---
```

### Pattern Entry Format

```markdown
## Pattern: RP-001 [Unused Imports]

**Confidence:** 0.97 (Tier 1)  
**Success Rate:** 92%  
**Last Seen:** 2 days ago  
**Routing Agent:** ci-auto-healer-agent

**Signature:** `F401 [^ ]+ '([^']+)' imported but unused`

**Quick Fix:**
```bash
ruff check --select F401 <file>
ruff check --fix --select F401 <file>
```

**When to Use:**
- Linter reports F401 error
- Unused imports detected in code review

**Fallback Agent:** code-scanning-remediation-agent

---
```

### Compact Format (Low Token Budget)

```markdown
### Patterns (Compact)

| Pattern | Confidence | Success | Routing Agent |
|---------|-----------|---------|----------------|
| RP-001  | 0.97      | 92%     | ci-auto-healer |
| RP-005  | 0.92      | 94%     | workflow-ci-fixer |
| L-002   | 0.91      | 93%     | python-312-type-fixer |

---
```

---

## Full Injection Algorithm

### Phase 1: Collection

```python
def collect_ltm_patterns():
    """Gather all LTM patterns for prioritization."""
    return [p for p in ltm.patterns if p.status != 'archived']
```

### Phase 2: Scoring & Ranking

```python
def rank_patterns_for_injection():
    """Score and sort patterns by priority."""
    patterns = collect_ltm_patterns()
    
    scores = []
    for pattern in patterns:
        priority = calculate_session_priority(pattern)
        scores.append({
            'pattern_id': pattern.id,
            'priority': priority,
            'tier': assign_tier(priority),
            'token_estimate': estimate_tokens(pattern)
        })
    
    # Sort by priority descending
    return sorted(scores, key=lambda x: x['priority'], reverse=True)
```

### Phase 3: Token-Aware Selection

```python
def select_patterns_for_injection(ranked_patterns, budget=2000):
    """Select patterns that fit within token budget."""
    selected = []
    tokens_used = 300  # Reserve for header, routing rules, escalation
    
    # Always include Tier 1 patterns (critical)
    tier_1 = [p for p in ranked_patterns if p['tier'] == 1]
    for pattern in tier_1:
        if tokens_used + pattern['token_estimate'] <= budget:
            selected.append(pattern)
            tokens_used += pattern['token_estimate']
    
    # Add Tier 2, 3, 4 patterns until budget exhausted
    for tier in [2, 3, 4]:
        tier_patterns = [p for p in ranked_patterns if p['tier'] == tier]
        for pattern in tier_patterns:
            if tokens_used + pattern['token_estimate'] <= budget:
                selected.append(pattern)
                tokens_used += pattern['token_estimate']
            else:
                break  # Budget exhausted for this tier
    
    return selected, tokens_used
```

### Phase 4: Formatting & Truncation

```python
def format_session_context(selected_patterns, tokens_used):
    """Format patterns for injection; apply intelligent truncation."""
    context = {
        'version': '1.0',
        'timestamp': now(),
        'budget_used': tokens_used,
        'budget_available': 2000,
        'patterns': []
    }
    
    for sp in selected_patterns:
        pattern = get_pattern(sp['pattern_id'])
        
        # Format based on tier
        if sp['tier'] <= 2:
            # Full format: description + fix + agents
            formatted = format_full(pattern)
        elif sp['tier'] == 3:
            # Medium format: description + quick fix
            formatted = format_medium(pattern)
        else:
            # Compact format: ID + confidence + routing
            formatted = format_compact(pattern)
        
        context['patterns'].append(formatted)
    
    return context
```

### Phase 5: Injection into Agent Session

```python
def inject_into_session(session_context):
    """Inject context into agent system prompt."""
    system_prompt = f"""
You are a CI/CD failure diagnostics and repair agent.

## Known Patterns

{format_patterns_for_prompt(session_context['patterns'])}

## Routing Rules

- For import errors → ci-importerror-agent (primary) or reference-updater-agent (fallback)
- For type errors → python-312-type-fixer (primary) or code-analysis-agent (fallback)
- For test failures → autonomous-test-healer-agent (primary) or test-enhancement-agent (fallback)

[Additional routing rules...]

## When to Escalate

- Unknown pattern (5+ attempts failed)
- Security vulnerability (CodeQL alert with severity > medium)
- Multi-pattern interaction (requires 3+ patterns simultaneously)

Escalate to: @mbaetiong with context logs
"""
    
    return system_prompt
```

---

## Versioning & Migration

### Pattern Format Versions

```yaml
version_1_0:
  released: "2026-06-26"
  format: "YAML with Markdown description"
  fields:
    - pattern_id
    - category
    - confidence
    - success_rate
    - routing_agent
    - fix_signature
    - quick_fix
  
version_0_9_deprecated:
  released: "2026-05-01"
  format: "JSON with inline fixes"
  fields:
    - id (now pattern_id)
    - score (now confidence)
    - success (now success_rate)
    - agent (now routing_agent)
  migration: "Auto-convert via migrate_v0_9_to_v1_0()"
```

### Migration Procedure

```python
def migrate_v0_9_to_v1_0(old_pattern):
    """Convert v0.9 format to v1.0."""
    return {
        'pattern_id': old_pattern['id'],
        'category': infer_category(old_pattern),
        'confidence': old_pattern['score'],
        'success_rate': old_pattern['success'],
        'routing_agent': old_pattern['agent'],
        'fix_signature': old_pattern.get('signature', ''),
        'quick_fix': old_pattern.get('fix', ''),
        'version': '1.0',
        'migrated_at': now(),
        'migrated_from': '0.9'
    }
```

### Backward Compatibility

When receiving v0.9 patterns in session:
1. Attempt to use as-is (most fields compatible)
2. Log deprecation warning
3. Migrate to v1.0 on next cycle
4. Support v0.9 for 30 days (until 2026-07-26)

---

## Fallback & Degradation

### Budget Exceeded Scenarios

```python
def handle_budget_exceeded(selected_patterns, tokens_used, budget=2000):
    """Apply intelligent degradation when budget exceeded."""
    
    if tokens_used <= budget:
        return selected_patterns  # No action needed
    
    excess = tokens_used - budget
    
    # Strategy 1: Remove Tier 4 patterns
    trimmed = [p for p in selected_patterns if p['tier'] <= 3]
    tokens_after_tier4_removal = sum(p['token_estimate'] for p in trimmed) + 300
    
    if tokens_after_tier4_removal <= budget:
        return trimmed
    
    excess = tokens_after_tier4_removal - budget
    
    # Strategy 2: Collapse descriptions (remove details, keep ID + confidence)
    collapsed = [
        {**p, 'token_estimate': p['token_estimate'] * 0.4}
        for p in trimmed
    ]
    tokens_after_collapse = sum(p['token_estimate'] for p in collapsed) + 300
    
    if tokens_after_collapse <= budget:
        return collapsed
    
    # Strategy 3: Remove Tier 3 patterns
    minimal = [p for p in collapsed if p['tier'] <= 2]
    return minimal
```

### Pattern Unavailability

If LTM patterns unavailable at session start:
1. Load from cache (if available, age < 24 hours)
2. Load default pattern set (hardcoded fallback)
3. Log warning and continue (session continues with reduced context)

```python
def load_session_context_with_fallback():
    """Load context with graceful fallback."""
    try:
        return load_ltm_session_context()
    except LTMUnavailableError:
        log_warning("LTM patterns unavailable; loading from cache")
        try:
            return load_cached_context(max_age=86400)  # 24 hours
        except CacheUnavailableError:
            log_warning("Cache unavailable; loading default patterns")
            return load_default_patterns()
```

---

## Integration Points

### Cognitive Brain CLI

```bash
# Inject session context for a given failure
cogbrain inject-session --failure-type import_error --session-id abc123

# Preview session context (without injection)
cogbrain preview-session --failure-type import_error

# Update LTM patterns before session
cogbrain sync-ltm-patterns --from-checkpoint latest
```

### Copilot Agent Integration

```python
# In agent system prompt initialization
session_context = CognitiveBrain.get_session_context(
    failure_type='ci_failure',
    budget=2000,
    include_recent_fixes=True,
    include_routing_rules=True
)

# Inject into system prompt
system_prompt += f"\n## Known CI Patterns\n\n{session_context.format()}"
```

### Session Checkpoint

```python
# At checkpoint creation
checkpoint = {
    'session_context': session_context,
    'patterns_injected': len(session_context.patterns),
    'timestamp': now(),
    'tokens_used': session_context.tokens_used,
}
```

---

## Metrics & Monitoring

### Context Utilization

```yaml
metrics:
  avg_budget_utilization: "94.5%"  # Target: 85-95%
  patterns_per_session: "18.2"     # Target: 15-25
  tier_1_inclusion_rate: "100%"    # Target: 100%
  tier_4_inclusion_rate: "45%"     # Target: 40-60%
  
trend_analysis:
  budget_utilization_7d_avg: "93.8%"
  pattern_count_increasing: true
  avg_confidence_stable: true
```

### Injection Success Rate

```
Patterns_Successfully_Used / Patterns_Injected × 100
Target: >75% (indicates relevant pattern selection)
```

---

## Reference

**See Also:**
- `PHASE_9_2_LTM_PATTERNS.md` - Full pattern catalog (50+ patterns)
- `PHASE_9_2_PATTERN_PROMOTION_RULES.md` - STM → LTM promotion algorithm
- `PHASE_9_2_CHECKPOINT_PROCEDURES.md` - Session checkpointing including context
- `PHASE_9_2_RECOVERY_PROCEDURES.md` - Recovery when context unavailable
