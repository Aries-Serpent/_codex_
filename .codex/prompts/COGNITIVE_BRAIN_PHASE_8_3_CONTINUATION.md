# Cognitive Brain Phase 8.3: Adaptive Learning Engine - Continuation Prompt

**Generated:** 2026-01-05T16:44:00Z  
**For:** GitHub Copilot Agent  
**Purpose:** Implement Adaptive Learning Engine with Reinforcement Learning  
**Duration:** 6 weeks (Phase 1 13 - Phase 2 23, Current Cycle)

---

## 🎯 Quick Start (Copy to PR Comment)

```
@copilot Begin Cognitive Brain Phase 8.3 implementation following `.codex/prompts/COGNITIVE_BRAIN_PHASE_8_3_CONTINUATION.md`.

**Phase 8.3: Adaptive Learning Engine** (Pre-commit cycles 1-12)

**Pre-commit 1-4: Outcome Analyzer:**
1. Create `src/cognitive_brain/learning/outcome_analyzer.py`
2. Create `src/cognitive_brain/models/learning_outcome.py`
3. Create `tests/cognitive_brain/learning/test_outcome_analyzer.py`
4. Integrate with AfterMath feedback system

**Success Criteria:**
- 10+ tests passing
- Pattern detection >80% accuracy
- Reward calculation validated
- Integration with existing cognitive brain

**Pre-commit 5-8: Strategy Optimizer:**
1. Implement Q-Learning algorithm
2. Implement Deep Q-Network (DQN)
3. Implement Proximal Policy Optimization (PPO)
4. Create comprehensive test suite (15+ tests)

**Success Criteria:**
- >20% strategy improvement over baseline
- Convergence in <1000 episodes
- Stable performance (std < 0.1)

**Policy:** Follow `.codex/CODEBASE_AGENCY_POLICY.md` - address ALL issues, plan first, 5+ iterations.
```

---

## 📋 Phase 8.3 Overview

### Goal
Implement adaptive learning engine that continuously improves decision-making strategies through reinforcement learning and meta-learning.

### Components (3 phases × 2 pre-commit cycles each)

1. **Outcome Analyzer** (Pre-commit 1-4)
   - Extract learnings from decision outcomes
   - Pattern detection and classification
   - Reward signal calculation for RL

2. **Strategy Optimizer** (Pre-commit 5-8)
   - Q-Learning for discrete actions
   - Deep Q-Network for complex states
   - Proximal Policy Optimization
   - Policy gradient methods

3. **Meta-Learner** (Pre-commit 9-12)
   - Cross-domain knowledge transfer
   - Few-shot learning (3-5 examples)
   - Knowledge graph construction
   - Transfer success metrics

### Performance Targets

| Metric | Current (8.2) | Target (8.3) | Improvement |
|--------|---------------|--------------|-------------|
| k₁ Factor | 0.32 | ≤0.30 | 6.3% |
| Quantum Advantage | 3.1× | >3.3× | 6.5% |
| Test Coverage | 92% | >93% | 1% |
| Strategy Improvement | - | >20% | NEW |
| Learning Convergence | - | <1000 episodes | NEW |

---

## 📅 Pre-commit 1-4: Outcome Analyzer

### Overview
Extract structured learnings from AfterMath feedback loop. Analyze decision outcomes to identify success/failure patterns and calculate reward signals for RL algorithms.

### Task 1: Learning Outcome Model
**File:** `src/cognitive_brain/models/learning_outcome.py`

```python
"""
Learning Outcome Data Models.

Structures for capturing and analyzing decision outcomes in the cognitive brain.
Integrates with AfterMath feedback system for continuous improvement.

AfterMath: Phase 8.3 - Adaptive Learning Engine
PDA: Active - Outcome tracking and pattern extraction
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum


class OutcomeType(Enum):
    """Types of decision outcomes."""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    TIMEOUT = "timeout"
    ERROR = "error"


class PatternCategory(Enum):
    """Categories of identified patterns."""
    TEMPORAL = "temporal"        # Time-based patterns
    CONTEXTUAL = "contextual"    # Context-dependent patterns
    SEQUENTIAL = "sequential"    # Action sequence patterns
    CAUSAL = "causal"           # Cause-effect patterns


@dataclass
class DecisionContext:
    """
    Context in which a decision was made.
    
    Attributes:
        task_type: Type of task being solved
        complexity: Estimated complexity (0-1)
        resource_constraints: Available resources
        time_pressure: Time pressure level (0-1)
        agent_ids: Agents involved in decision
        metadata: Additional contextual information
    """
    task_type: str
    complexity: float
    resource_constraints: Dict[str, float]
    time_pressure: float = 0.5
    agent_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate decision context."""
        if not 0.0 <= self.complexity <= 1.0:
            raise ValueError(f"Complexity must be in [0,1], got {self.complexity}")
        if not 0.0 <= self.time_pressure <= 1.0:
            raise ValueError(f"Time pressure must be in [0,1], got {self.time_pressure}")


@dataclass
class LearningOutcome:
    """
    Structured outcome of a decision for learning purposes.
    
    Attributes:
        outcome_id: Unique identifier
        decision_id: Associated decision ID
        outcome_type: Type of outcome (success/failure/etc)
        reward: Reward signal for RL (-1 to +1)
        context: Decision context
        result_metrics: Quantitative metrics
        patterns_identified: Detected patterns
        lessons_learned: Extracted lessons
        timestamp: When outcome was recorded
        
    PDA: [DATA] Learning outcome container for adaptive algorithms
    """
    outcome_id: str
    decision_id: str
    outcome_type: OutcomeType
    reward: float
    context: DecisionContext
    result_metrics: Dict[str, float] = field(default_factory=dict)
    patterns_identified: List[str] = field(default_factory=list)
    lessons_learned: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate learning outcome."""
        if not -1.0 <= self.reward <= 1.0:
            raise ValueError(f"Reward must be in [-1,1], got {self.reward}")
        if not self.outcome_id:
            raise ValueError("outcome_id cannot be empty")
        if not self.decision_id:
            raise ValueError("decision_id cannot be empty")


@dataclass
class Pattern:
    """
    Identified pattern in decision-making.
    
    Attributes:
        pattern_id: Unique identifier
        category: Pattern category
        description: Human-readable description
        confidence: Confidence in pattern (0-1)
        support_count: Number of occurrences
        examples: Example instances
        applicability: When pattern applies
    """
    pattern_id: str
    category: PatternCategory
    description: str
    confidence: float
    support_count: int = 0
    examples: List[str] = field(default_factory=list)
    applicability: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate pattern."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be in [0,1], got {self.confidence}")
        if self.support_count < 0:
            raise ValueError(f"Support count cannot be negative: {self.support_count}")


@dataclass
class PatternSet:
    """
    Collection of related patterns.
    
    Attributes:
        patterns: List of patterns
        domain: Problem domain
        extraction_date: When patterns were extracted
        statistics: Pattern set statistics
    """
    patterns: List[Pattern]
    domain: str
    extraction_date: datetime = field(default_factory=datetime.now)
    statistics: Dict[str, Any] = field(default_factory=dict)
    
    def get_by_category(self, category: PatternCategory) -> List[Pattern]:
        """Get patterns by category."""
        return [p for p in self.patterns if p.category == category]
    
    def get_high_confidence(self, threshold: float = 0.8) -> List[Pattern]:
        """Get high-confidence patterns."""
        return [p for p in self.patterns if p.confidence >= threshold]
```

**Validation Criteria:**
- All dataclasses properly validated
- Type hints comprehensive
- Integration points with AfterMath clear

### Task 2: Outcome Analyzer Implementation
**File:** `src/cognitive_brain/learning/outcome_analyzer.py`

```python
"""
Outcome Analyzer for Adaptive Learning.

Analyzes decision outcomes from the AfterMath feedback system to extract
learnings, identify patterns, and calculate reward signals for RL algorithms.

AfterMath: Phase 8.3 - Adaptive Learning Engine
PDA: Active - Continuous outcome analysis and pattern extraction
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from cognitive_brain.models.learning_outcome import (
    LearningOutcome,
    OutcomeType,
    Pattern,
    PatternSet,
    PatternCategory,
    DecisionContext
)

logger = logging.getLogger(__name__)


class OutcomeAnalyzer:
    """
    Analyze decision outcomes and extract learnings.
    
    Integrates with AfterMath feedback system to continuously improve
    decision-making strategies through pattern detection and reward calculation.
    
    PDA Loop:
        - [PLAN] Design outcome analysis strategy
        - [DO] Extract patterns and calculate rewards
        - [AFTERMATH] Track learning improvements over time
    
    Attributes:
        outcomes: Stored learning outcomes
        patterns: Identified patterns
        reward_history: Historical reward signals
    """
    
    def __init__(self):
        """Initialize outcome analyzer."""
        self.outcomes: Dict[str, LearningOutcome] = {}
        self.patterns: Dict[str, Pattern] = {}
        self.reward_history: List[float] = []
        self.pattern_extraction_count = 0
        
        logger.info("OutcomeAnalyzer initialized")
    
    def analyze_outcome(
        self,
        decision_id: str,
        outcome_type: OutcomeType,
        result_metrics: Dict[str, float],
        context: DecisionContext,
        outcome_id: Optional[str] = None
    ) -> LearningOutcome:
        """
        Analyze a decision outcome and extract learnings.
        
        Args:
            decision_id: ID of decision that was made
            outcome_type: Type of outcome (success/failure/etc)
            result_metrics: Quantitative results (e.g., accuracy, latency)
            context: Context in which decision was made
            outcome_id: Optional custom outcome ID
        
        Returns:
            LearningOutcome object with extracted learnings
        
        PDA: [PLAN] Validate inputs → [DO] Extract patterns → [AFTERMATH] Calculate reward
        """
        # Generate outcome ID if not provided
        if outcome_id is None:
            outcome_id = f"outcome_{len(self.outcomes) + 1}"
        
        # Calculate reward signal
        reward = self._calculate_reward(outcome_type, result_metrics, context)
        
        # Identify patterns
        patterns_identified = self._identify_patterns(
            outcome_type, result_metrics, context
        )
        
        # Extract lessons
        lessons_learned = self._extract_lessons(
            outcome_type, result_metrics, context, patterns_identified
        )
        
        # Create learning outcome
        learning_outcome = LearningOutcome(
            outcome_id=outcome_id,
            decision_id=decision_id,
            outcome_type=outcome_type,
            reward=reward,
            context=context,
            result_metrics=result_metrics,
            patterns_identified=patterns_identified,
            lessons_learned=lessons_learned,
            timestamp=datetime.now()
        )
        
        # Store outcome
        self.outcomes[outcome_id] = learning_outcome
        self.reward_history.append(reward)
        
        logger.info(
            f"Analyzed outcome '{outcome_id}': type={outcome_type.value}, "
            f"reward={reward:.3f}, patterns={len(patterns_identified)}"
        )
        
        return learning_outcome
    
    def _calculate_reward(
        self,
        outcome_type: OutcomeType,
        result_metrics: Dict[str, float],
        context: DecisionContext
    ) -> float:
        """
        Calculate reward signal for RL algorithms.
        
        Formula:
            R = base_reward × efficiency × (1 - time_penalty)
        
        where:
            - base_reward: +1.0 (success), -1.0 (failure), 0.5 (partial)
            - efficiency: result quality metric (0-1)
            - time_penalty: context.time_pressure adjusted
        
        Returns:
            Reward in [-1, +1]
        """
        # Base reward by outcome type
        base_rewards = {
            OutcomeType.SUCCESS: 1.0,
            OutcomeType.FAILURE: -1.0,
            OutcomeType.PARTIAL: 0.5,
            OutcomeType.TIMEOUT: -0.5,
            OutcomeType.ERROR: -0.8
        }
        base_reward = base_rewards.get(outcome_type, 0.0)
        
        # Efficiency factor from metrics
        efficiency = result_metrics.get("efficiency", 1.0)
        efficiency = max(0.0, min(1.0, efficiency))  # Clamp to [0,1]
        
        # Time penalty based on time pressure
        time_penalty = context.time_pressure * 0.2  # Max 20% penalty
        
        # Complexity bonus for harder tasks
        complexity_bonus = context.complexity * 0.1  # Max 10% bonus
        
        # Calculate final reward
        reward = base_reward * efficiency * (1 - time_penalty) + complexity_bonus
        
        # Clamp to [-1, +1]
        reward = max(-1.0, min(1.0, reward))
        
        return reward
    
    def _identify_patterns(
        self,
        outcome_type: OutcomeType,
        result_metrics: Dict[str, float],
        context: DecisionContext
    ) -> List[str]:
        """
        Identify patterns in the outcome.
        
        Returns:
            List of pattern IDs
        """
        identified_patterns = []
        
        # Temporal pattern: Time-of-day effects
        hour = datetime.now().hour
        if outcome_type == OutcomeType.SUCCESS and 9 <= hour <= 17:
            identified_patterns.append("temporal_business_hours_success")
        
        # Contextual pattern: Complexity vs success
        if context.complexity > 0.7 and outcome_type == OutcomeType.SUCCESS:
            identified_patterns.append("contextual_high_complexity_success")
        elif context.complexity < 0.3 and outcome_type == OutcomeType.FAILURE:
            identified_patterns.append("contextual_low_complexity_failure")
        
        # Sequential pattern: Multi-agent coordination
        if len(context.agent_ids) > 2 and outcome_type == OutcomeType.SUCCESS:
            identified_patterns.append("sequential_multi_agent_success")
        
        # Resource constraint pattern
        if context.resource_constraints.get("cpu", 1.0) < 0.5:
            if outcome_type == OutcomeType.SUCCESS:
                identified_patterns.append("causal_low_resource_success")
            else:
                identified_patterns.append("causal_low_resource_failure")
        
        return identified_patterns
    
    def _extract_lessons(
        self,
        outcome_type: OutcomeType,
        result_metrics: Dict[str, float],
        context: DecisionContext,
        patterns: List[str]
    ) -> List[str]:
        """
        Extract actionable lessons from the outcome.
        
        Returns:
            List of lesson strings
        """
        lessons = []
        
        if outcome_type == OutcomeType.SUCCESS:
            lessons.append(f"Strategy effective for {context.task_type}")
            if context.complexity > 0.7:
                lessons.append("Can handle high-complexity tasks successfully")
        elif outcome_type == OutcomeType.FAILURE:
            lessons.append(f"Strategy ineffective for {context.task_type}")
            if context.time_pressure > 0.8:
                lessons.append("High time pressure may have contributed to failure")
        
        # Pattern-based lessons
        if "multi_agent_success" in str(patterns):
            lessons.append("Multi-agent coordination is beneficial")
        if "low_resource_failure" in str(patterns):
            lessons.append("Need better resource allocation strategy")
        
        return lessons
    
    def identify_patterns(
        self,
        lookback_window: int = 100
    ) -> PatternSet:
        """
        Find recurring success/failure patterns across recent outcomes.
        
        Args:
            lookback_window: Number of recent outcomes to analyze
        
        Returns:
            PatternSet with identified patterns
        
        PDA: [PLAN] Define search space → [DO] Extract patterns → [AFTERMATH] Validate
        """
        recent_outcomes = list(self.outcomes.values())[-lookback_window:]
        
        if not recent_outcomes:
            return PatternSet(patterns=[], domain="general")
        
        # Track pattern occurrences
        pattern_counts = defaultdict(int)
        pattern_examples = defaultdict(list)
        
        for outcome in recent_outcomes:
            for pattern_id in outcome.patterns_identified:
                pattern_counts[pattern_id] += 1
                pattern_examples[pattern_id].append(outcome.outcome_id)
        
        # Create Pattern objects
        patterns = []
        for pattern_id, count in pattern_counts.items():
            # Determine category from pattern ID
            if "temporal" in pattern_id:
                category = PatternCategory.TEMPORAL
            elif "contextual" in pattern_id:
                category = PatternCategory.CONTEXTUAL
            elif "sequential" in pattern_id:
                category = PatternCategory.SEQUENTIAL
            else:
                category = PatternCategory.CAUSAL
            
            # Calculate confidence based on support
            confidence = min(1.0, count / lookback_window * 2)
            
            pattern = Pattern(
                pattern_id=pattern_id,
                category=category,
                description=pattern_id.replace("_", " ").title(),
                confidence=confidence,
                support_count=count,
                examples=pattern_examples[pattern_id][:5]  # Top 5 examples
            )
            patterns.append(pattern)
        
        self.pattern_extraction_count += 1
        
        pattern_set = PatternSet(
            patterns=patterns,
            domain="cognitive_brain",
            extraction_date=datetime.now(),
            statistics={
                "total_patterns": len(patterns),
                "outcomes_analyzed": len(recent_outcomes),
                "extraction_number": self.pattern_extraction_count
            }
        )
        
        # Store patterns
        for pattern in patterns:
            self.patterns[pattern.pattern_id] = pattern
        
        logger.info(
            f"Extracted {len(patterns)} patterns from {len(recent_outcomes)} outcomes"
        )
        
        return pattern_set
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get analyzer statistics.
        
        Returns:
            Dictionary with outcomes analyzed, patterns identified, avg reward
        """
        avg_reward = (
            sum(self.reward_history) / len(self.reward_history)
            if self.reward_history
            else 0.0
        )
        
        success_count = sum(
            1 for o in self.outcomes.values()
            if o.outcome_type == OutcomeType.SUCCESS
        )
        
        return {
            "outcomes_analyzed": len(self.outcomes),
            "patterns_identified": len(self.patterns),
            "pattern_extractions": self.pattern_extraction_count,
            "average_reward": avg_reward,
            "success_rate": success_count / len(self.outcomes) if self.outcomes else 0.0
        }
```

**Validation Criteria:**
- Reward calculation validated: [-1, +1]
- Pattern detection >80% accuracy
- Lessons extraction comprehensive
- Integration with AfterMath system working

### Task 3: Tests
**File:** `tests/cognitive_brain/learning/test_outcome_analyzer.py`

Minimum 10 tests:
1. `test_analyze_success_outcome()` - Success with positive reward
2. `test_analyze_failure_outcome()` - Failure with negative reward
3. `test_reward_calculation_formula()` - Reward formula correctness
4. `test_pattern_identification()` - Pattern detection works
5. `test_lessons_extraction()` - Lessons are actionable
6. `test_identify_patterns_batch()` - Batch pattern extraction
7. `test_high_confidence_patterns()` - Confidence thresholds
8. `test_pattern_categories()` - All 4 categories covered
9. `test_statistics_calculation()` - Statistics accurate
10. `test_aftermath_integration()` - AfterMath integration

---

## 📅 Pre-commit 5-8: Strategy Optimizer

### Implementation Summary

**File:** `src/cognitive_brain/learning/strategy_optimizer.py`

Implement 3 RL algorithms:
1. **Q-Learning**: Discrete action spaces
2. **Deep Q-Network (DQN)**: Complex state spaces
3. **Proximal Policy Optimization (PPO)**: Policy gradient method

**File:** `src/cognitive_brain/learning/rl_algorithms.py`

Support classes for RL:
- Experience replay buffer
- Policy network
- Value network
- Exploration strategies (ε-greedy, Boltzmann)

**Success Criteria:**
- >20% improvement over random baseline
- Convergence in <1000 episodes
- Stable performance (std < 0.1)
- 15+ tests passing

---

## 📅 Pre-commit 9-12: Meta-Learner

### Implementation Summary

**File:** `src/cognitive_brain/learning/meta_learner.py`

Cross-domain knowledge transfer:
- Domain embedding
- Knowledge graph construction
- Transfer success metrics
- Few-shot learning (3-5 examples)

**File:** `src/cognitive_brain/models/knowledge_graph.py`

Knowledge representation:
- Node types (concepts, patterns, strategies)
- Edge types (similarity, causation, hierarchy)
- Graph algorithms (shortest path, clustering)

**Success Criteria:**
- Transfer success >75%
- Few-shot learning validated
- Knowledge graph >100 nodes
- 10+ tests passing

---

## 🔄 AfterMath/PDA Loop Requirements

**MANDATORY**: All Phase 8.3 modules MUST integrate with AfterMath.

### Integration Pattern
```python
# In every new function/method:
def adaptive_learning_function(...):
    """Function with AfterMath integration."""
    # PLAN phase
    plan = create_learning_plan(...)
    log_plan_to_aftermath(plan)
    
    # DO phase  
    result = execute_learning(plan)
    
    # ASSESS phase
    feedback = {
        'success': bool,
        'learning_rate': float,
        'convergence': bool,
        'lessons': [...]
    }
    update_aftermath_log(feedback)  # REQUIRED
    
    return result
```

### AfterMath Tags
Add to ALL new files:
```python
# AfterMath: Phase 8.3 - Adaptive Learning Engine
# PDA: Active - Continuous learning and strategy optimization
# Monitoring: Learning rate, convergence, strategy improvement
```

---

## 📈 Progress Tracking

### Weekly Report Template

```markdown
## Cognitive Brain Phase 8.3 - Week X Progress

**Date:** YYYY-MM-DD  
**Phase:** 8.3 Adaptive Learning Engine  
**Week:** X of 6

### Completed Tasks
- [x] Task 1: OutcomeAnalyzer implemented
- [x] Task 2: LearningOutcome model created
- [ ] Task 3: Strategy Optimizer (in progress)

### Metrics
- **Tests:** X/25 passing (target: 25)
- **Coverage:** Y% (target: >95%)
- **k₁ Factor:** 0.XX (target: ≤0.30)
- **Strategy Improvement:** XX% (target: >20%)
- **Convergence:** XXX episodes (target: <1000)

### Code Quality
- Files added: X
- Lines of code: XXX
- Documentation: Complete/Partial/None
- Self-reviews: X iterations

### Issues & Resolutions
1. **Issue:** Description
   **Resolution:** Solution
   **Iterations:** X

### Next Week Priorities
1. Priority 1
2. Priority 2
3. Priority 3

### AfterMath Feedback
- Lesson 1 learned
- Improvement 1 identified
- Pattern 1 for Phase 8.4

### Policy Compliance
- [x] All issues addressed
- [x] Planning before execution
- [x] 5+ self-review iterations
- [x] AfterMath/PDA loop active
```

---

## 🎯 Success Criteria Checklist

### Phase 8.3 Complete When:
- [ ] All 25+ tests passing
- [ ] Outcome Analyzer operational
- [ ] 3 RL algorithms implemented
- [ ] Meta-Learner with knowledge transfer
- [ ] >20% strategy improvement demonstrated
- [ ] Convergence <1000 episodes
- [ ] Transfer success >75%
- [ ] No regressions (Phase 8.0-8.2 tests pass)
- [ ] Documentation complete
- [ ] AfterMath integration verified
- [ ] Continuation prompt created for Phase 8.4

---

## 📚 Essential References

1. **Phase 8.2 Implementation:** `src/cognitive_brain/quantum/`
2. **Status Assessment:** `.codex/plans/COGNITIVE_BRAIN_PHASE_8_STATUS_ASSESSMENT.md`
3. **Policy:** `.codex/CODEBASE_AGENCY_POLICY.md`
4. **Guidelines:** `AGENTS.md`

---

## 🔄 Continuation Protocol

At end of EACH week:

1. **Commit work** with descriptive message
2. **Update** `.codex/plans/COGNITIVE_BRAIN_PHASE_8_STATUS_ASSESSMENT.md`
3. **Create PR comment** (if not complete):

```
@copilot Continue Cognitive Brain Phase 8.3 Week X

**Completed This Week:**
- OutcomeAnalyzer: [status + file]
- Tests: X/25 passing

**Current Metrics:**
- k₁: 0.XX (target: ≤0.30)
- Strategy improvement: XX% (target: >20%)
- Convergence: XXX episodes (target: <1000)

**Next Week Tasks:**
1. [Specific task + file]
2. [Specific task + file]
3. [Specific task + file]

**Blockers:** None / [list]

**Reference:** `.codex/prompts/COGNITIVE_BRAIN_PHASE_8_3_CONTINUATION.md` - Week X
```

---

**Start:** 2026-01-13  
**End:** 2026-02-23  
**Priority:** HIGH

Execute with precision. Learn continuously. Optimize iteratively. 🚀
