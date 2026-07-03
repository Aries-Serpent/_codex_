---
title: "PHASE 9.2 Pattern Promotion Rules (STM → LTM)"
version: "1.0"
date: "2026-06-26"
status: "FINAL"
---

# PHASE 9.2 Pattern Promotion Rules (STM → LTM)

## Overview

This document defines the rules and algorithms for promoting patterns from **Short-Term Memory (STM)** to **Long-Term Memory (LTM)** in the cognitive brain. Patterns are automatically evaluated for promotion based on confidence scoring, success rate thresholds, recency weighting, and conflict detection.

---

## Promotion Criteria

### Minimum Observations Requirement

| Tier | Min Observations | Use Case |
|------|-----------------|----------|
| **Bronze** | 1 | First encounter; eligible for STM |
| **Silver** | 3 | Pattern emerging; candidate for validation |
| **Gold** | 5 | Validated pattern; eligible for LTM promotion |
| **Platinum** | 10+ | Highly validated; fast-track promotion |

**Promotion Flow:**
```
First Encounter (STM)
    ↓
3+ observations detected
    ↓
Aggregate metrics (success rate, confidence)
    ↓
5+ observations AND ≥80% success rate
    ↓
LTM Promotion Eligible ✓
```

### Success Rate Threshold

**Minimum:** 80% success rate (baseline)  
**Recommended:** 85%+ for high-confidence promotion

**Calculation:**
```
success_rate = (successful_fixes / total_attempts) × 100
```

**Tiered Thresholds:**

| Pattern Complexity | Min Success Rate | Confidence Impact |
|-------------------|-----------------|-------------------|
| Low (e.g., YAML fixes) | 85%+ | Confidence ×1.1 |
| Medium (e.g., Type fixes) | 80%+ | Confidence ×1.0 |
| High (e.g., Flaky tests) | 75%+ | Confidence ×0.95 |

---

## Confidence Scoring Algorithm

### Base Confidence Score

```python
def calculate_base_confidence(pattern):
    """
    Base confidence from pattern characteristics.
    
    Range: [0.0, 1.0]
    Inputs:
      - pattern_determinism: 0.0 (non-deterministic) to 1.0 (deterministic)
      - false_positive_risk: 0.0 (very low) to 0.5 (very high)
      - agent_specialty: 0.7 (generalist) to 1.0 (specialist)
    """
    base = (
        (pattern_determinism * 0.5) +          # 50% weight on determinism
        ((1.0 - false_positive_risk) * 0.3) +  # 30% weight on low false positive risk
        (agent_specialty * 0.2)                 # 20% weight on agent specialty
    )
    return round(min(1.0, base), 2)


# Examples:
# YAML fixes (deterministic):       0.5×1.0 + 0.3×0.98 + 0.2×1.0 = 0.984 → 0.98
# Flaky test fixes (non-deterministic): 0.5×0.4 + 0.3×0.85 + 0.2×0.95 = 0.686 → 0.69
```

### Recency Boost

```python
def calculate_recency_boost(pattern):
    """
    Boost confidence for recently-seen patterns.
    
    Applies: -20% confidence decay per 30 days old
    New patterns (0-7 days): +10% boost
    """
    days_old = (now() - pattern.last_seen).days
    
    if days_old <= 7:
        return +0.10  # Recent pattern boost
    elif days_old <= 30:
        return 0.0    # No decay in first month
    else:
        # Decay: -20% per 30-day period
        periods = (days_old - 30) / 30
        return -0.20 * periods
```

### Conflict Penalty

```python
def calculate_conflict_penalty(pattern, ltm_patterns):
    """
    Reduce confidence if pattern conflicts with existing LTM patterns.
    
    Returns: negative penalty [0.0 to -0.20]
    """
    conflicts = detect_conflicts(pattern, ltm_patterns)
    
    if not conflicts:
        return 0.0
    
    # Penalty based on conflict severity
    penalty_per_conflict = -0.05
    total_penalty = penalty_per_conflict * len(conflicts)
    return max(-0.20, total_penalty)  # Cap at -20%
```

### Success Rate Multiplier

```python
def calculate_success_multiplier(success_rate):
    """
    Apply multiplier based on success rate performance.
    
    Range: [0.8x to 1.2x] depending on success rate vs threshold
    """
    if success_rate >= 95:
        return 1.20  # Excellent performance
    elif success_rate >= 90:
        return 1.15  # Very good
    elif success_rate >= 85:
        return 1.10  # Good
    elif success_rate >= 80:
        return 1.00  # Acceptable
    elif success_rate >= 75:
        return 0.90  # Marginal
    else:
        return 0.80  # Below threshold
```

### Final Confidence Score

```python
def promote_to_ltm(pattern):
    """
    Calculate final confidence and decide on promotion.
    """
    base_conf = calculate_base_confidence(pattern)
    recency_boost = calculate_recency_boost(pattern)
    conflict_penalty = calculate_conflict_penalty(pattern, ltm_patterns)
    success_mult = calculate_success_multiplier(pattern.success_rate)
    
    final_confidence = (
        base_conf +
        recency_boost +
        conflict_penalty
    ) * success_mult
    
    # Clamp to [0.0, 1.0]
    final_confidence = max(0.0, min(1.0, final_confidence))
    
    # Promotion decision
    if (pattern.observations >= 5 and 
        pattern.success_rate >= 0.80 and 
        final_confidence >= pattern.confidence_threshold):
        return {
            'status': 'PROMOTE_TO_LTM',
            'confidence': final_confidence,
            'reason': f'Meets all criteria: {pattern.observations} observations, {pattern.success_rate*100:.1f}% success'
        }
    else:
        return {
            'status': 'REMAIN_IN_STM',
            'confidence': final_confidence,
            'reason': f'Insufficient data: {pattern.observations} observations, {pattern.success_rate*100:.1f}% success'
        }
```

---

## Recency Decay Rules

### Decay Schedule

```yaml
age_category: decay_rate
  fresh (0-7 days): +10% confidence boost
  current (8-30 days): 0% (no decay)
  stale (31-60 days): -10% per 30 days (-10%)
  very_stale (61-90 days): -10% per 30 days (-20%)
  archival (91+ days): -10% per 30 days (max -30%)
```

### Example Decay Calculation

```python
# Pattern last used: 45 days ago
# Base confidence: 0.85
# Days over 30-day threshold: 45 - 30 = 15 days
# Decay periods: 15 / 30 = 0.5 periods
# Decay amount: -0.20 * 0.5 = -0.10
# Final: 0.85 - 0.10 = 0.75 confidence

decay_amount = -0.20 * ((45 - 30) / 30)  # -0.10
final_confidence = 0.85 + decay_amount    # 0.75
```

### Preventing Pattern Decay

To prevent a pattern from decaying (e.g., proven stable patterns):
1. **Re-observe pattern**: Using it again resets last_seen timestamp
2. **Mark as stable**: Set `stability_flag=True` to exempt from decay
3. **Archive to reference**: Move to reference collection if no longer active

---

## Conflict Detection

### Conflict Categories

#### 1. Contradictory Fix Strategies

```python
# Conflict Example: RP-004 (Dependency pinning) vs RP-001 (Unused import removal)
# Pattern A: "Pin numpy==1.20.0"
# Pattern B: "Remove numpy import"
# Resolution: Apply sequentially; RP-001 after RP-004 removal

conflict_type = "contradictory_fix"
severity = "low"  # Fixable via sequencing
resolution = "apply_pattern_a_then_pattern_b"
```

#### 2. Overlapping Signatures

```python
# Conflict Example: L-002 (Deprecated typing) vs RP-002 (Type annotations)
# Both patterns identify Python 3.9+ type issues
# Resolution: Merge into single pattern with extended signature

conflict_type = "overlapping_signature"
severity = "medium"
resolution = "merge_patterns_into_single_comprehensive_pattern"
```

#### 3. Agent Capability Conflicts

```python
# Conflict Example: Two agents claim ownership of same pattern
# Agent A: ci-auto-healer-agent (general CI fixer)
# Agent B: python-312-type-fixer (specialist type fixer)
# Resolution: Assign to specialist (Agent B) with fallback to generalist

conflict_type = "agent_ownership"
severity = "medium"
resolution = "assign_to_specialist_agent_with_fallback"
```

### Conflict Detection Algorithm

```python
def detect_conflicts(new_pattern, ltm_patterns):
    """
    Identify conflicts between new pattern and existing LTM patterns.
    """
    conflicts = []
    
    for ltm_pattern in ltm_patterns:
        # Check 1: Overlapping fix signatures
        if signatures_overlap(new_pattern.fix_sig, ltm_pattern.fix_sig):
            conflicts.append({
                'type': 'overlapping_signature',
                'conflicting_pattern': ltm_pattern.id,
                'severity': 'medium'
            })
        
        # Check 2: Contradictory effects
        if fixes_contradict(new_pattern.fix, ltm_pattern.fix):
            conflicts.append({
                'type': 'contradictory_fix',
                'conflicting_pattern': ltm_pattern.id,
                'severity': 'low'  # Can be sequenced
            })
        
        # Check 3: Agent ownership
        if new_pattern.routing_agent == ltm_pattern.routing_agent:
            if new_pattern.prerequisite_patterns and ltm_pattern.id in new_pattern.prerequisite_patterns:
                conflicts.append({
                    'type': 'prerequisite_ordering',
                    'conflicting_pattern': ltm_pattern.id,
                    'severity': 'low'
                })
    
    return conflicts
```

---

## Automated Promotion Workflow

### Step 1: Detection

```python
def detect_promotion_candidates():
    """Scan STM for patterns meeting observation threshold."""
    candidates = []
    
    for stm_pattern in stm.patterns:
        if stm_pattern.observations >= 3:
            candidates.append({
                'pattern_id': stm_pattern.id,
                'observations': stm_pattern.observations,
                'success_rate': stm_pattern.success_rate,
                'ready_for_validation': True
            })
    
    return candidates
```

### Step 2: Aggregation

```python
def aggregate_metrics(pattern_id, observations):
    """Aggregate metrics across observations."""
    fixes = load_all_fix_attempts(pattern_id)
    
    return {
        'pattern_id': pattern_id,
        'observations': len(fixes),
        'successful': sum(1 for f in fixes if f.success),
        'failed': sum(1 for f in fixes if not f.success),
        'success_rate': sum(1 for f in fixes if f.success) / len(fixes),
        'avg_fix_time_seconds': mean([f.duration for f in fixes]),
        'false_positives': sum(1 for f in fixes if f.false_positive),
        'false_positive_rate': sum(1 for f in fixes if f.false_positive) / len(fixes),
    }
```

### Step 3: Confidence Scoring

```python
def score_for_promotion(pattern_id, aggregated_metrics):
    """Calculate promotion score."""
    pattern = get_pattern(pattern_id)
    
    base_confidence = calculate_base_confidence(pattern)
    recency_boost = calculate_recency_boost(pattern)
    conflict_penalty = calculate_conflict_penalty(pattern, ltm_patterns)
    success_mult = calculate_success_multiplier(aggregated_metrics['success_rate'] * 100)
    
    final_score = (base_confidence + recency_boost + conflict_penalty) * success_mult
    final_score = max(0.0, min(1.0, final_score))
    
    return {
        'base_confidence': base_confidence,
        'recency_boost': recency_boost,
        'conflict_penalty': conflict_penalty,
        'success_multiplier': success_mult,
        'final_score': round(final_score, 2),
        'promotion_eligible': (
            aggregated_metrics['observations'] >= 5 and
            aggregated_metrics['success_rate'] >= 0.80 and
            final_score >= pattern.confidence_threshold
        )
    }
```

### Step 4: Promotion Decision

```python
def make_promotion_decision(pattern_id, scoring_results):
    """Decide whether to promote."""
    if scoring_results['promotion_eligible']:
        conflicts = detect_conflicts(get_pattern(pattern_id), ltm_patterns)
        
        if not conflicts or all(c['severity'] == 'low' for c in conflicts):
            return 'APPROVE_PROMOTION'
        elif any(c['severity'] == 'high' for c in conflicts):
            return 'HOLD_FOR_CONFLICT_RESOLUTION'
        else:
            return 'APPROVE_WITH_CONFLICT_MITIGATION'
    else:
        return 'REMAIN_IN_STM'
```

### Step 5: Integration into LTM

```python
def promote_to_ltm(pattern_id, scoring_results):
    """Move pattern from STM to LTM."""
    pattern = get_pattern(pattern_id)
    
    # Create LTM entry
    ltm_entry = {
        'pattern_id': pattern.id,
        'name': pattern.name,
        'category': pattern.category,
        'confidence': scoring_results['final_score'],
        'promoted_at': now(),
        'observations': scoring_results['aggregated_metrics']['observations'],
        'success_rate': scoring_results['aggregated_metrics']['success_rate'],
        'false_positive_rate': scoring_results['aggregated_metrics']['false_positive_rate'],
        'avg_fix_time_seconds': scoring_results['aggregated_metrics']['avg_fix_time_seconds'],
        'routing_agent': pattern.routing_agent,
        'improvement_areas': pattern.improvement_areas,
        'prerequisite_patterns': pattern.prerequisite_patterns,
    }
    
    # Store in LTM
    ltm.patterns.append(ltm_entry)
    
    # Log promotion
    log_event({
        'event': 'pattern_promoted_to_ltm',
        'pattern_id': pattern_id,
        'confidence': ltm_entry['confidence'],
        'timestamp': now(),
    })
    
    # Update STM (optional: keep for reference or remove)
    stm.patterns.remove(pattern_id)
```

---

## Maintenance & Periodic Review

### Quarterly Decay Assessment

Every 90 days:
1. Calculate decay for all LTM patterns
2. Identify patterns with confidence < 0.70
3. Demote patterns to STM if unused for 180+ days
4. Archive patterns with age > 365 days and low confidence

### Pattern Supersession

When a newer pattern emerges that obsoletes an older one:

```python
def supersede_pattern(old_pattern_id, new_pattern_id):
    """Mark old pattern as superseded."""
    old_pattern = get_ltm_pattern(old_pattern_id)
    old_pattern['status'] = 'superseded'
    old_pattern['superseded_by'] = new_pattern_id
    old_pattern['supersession_date'] = now()
    
    # Redirect future fixes to new pattern
    # but keep old pattern in LTM for historical reference
```

---

## Integration with Session Context

LTM patterns are injected into session context according to priorities:

1. **Recent patterns** (< 7 days): +20% priority boost
2. **High confidence** (> 0.90): +15% priority boost
3. **High success rate** (> 85%): +10% priority boost
4. **Improvement areas matching** (e.g., CI, Security): +5% priority boost

See `PHASE_9_2_SESSION_CONTEXT.md` for full injection algorithm.

---

## Metrics & KPIs

### Promotion Success Rate

```
Promoted_Patterns / Total_Candidates × 100
Target: 70-80% (rest remain in STM for additional validation)
```

### LTM Pattern Stability

```
Patterns_Demoted / Total_LTM_Patterns × 100
Target: <5% per quarter (indicates stable promotion decisions)
```

### Average Confidence Trend

```
Mean(LTM_Pattern_Confidence) over time
Target: Stable at 0.82-0.88 range
```

### Conflict Resolution Efficiency

```
Conflicts_Resolved / Conflicts_Detected × 100
Target: >95% auto-resolution rate
```

---

## Reference

**See Also:**
- `PHASE_9_2_LTM_PATTERNS.md` - Full pattern catalog (50+ patterns)
- `PHASE_9_2_SESSION_CONTEXT.md` - Session context injection algorithm
- `PHASE_9_2_CHECKPOINT_PROCEDURES.md` - State checkpointing for pattern tracking
- `PHASE_9_2_RECOVERY_PROCEDURES.md` - Recovery from promotion-related failures
