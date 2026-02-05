# Agent Brain Protocol Specification

> **Version:** 1.0.0  
> **Created:** 2026-02-05  
> **Status:** ✅ IMPLEMENTED  
> **Owner:** Cognitive Brain System

---

## Overview

This document specifies the protocol for communication between AI agents and the Cognitive Brain infrastructure. The protocol enables:

1. **Pattern Store Access** - Query and submit learned patterns
2. **Objective Alignment** - Verify actions align with goals
3. **Session State Sharing** - Read and update session state
4. **Learning Feedback** - Report outcomes for continuous improvement

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Cognitive Brain Hub                       │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Pattern  │  │Objective │  │ Session  │  │ Learning │   │
│  │  Store   │  │ Tracker  │  │ Manager  │  │ Pipeline │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │              │              │              │        │
│       └──────────────┼──────────────┼──────────────┘        │
│                      │              │                        │
│              ┌───────┴──────────────┴───────┐               │
│              │    AgentBrainInterface       │               │
│              └───────────────┬──────────────┘               │
└──────────────────────────────┼──────────────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
   ┌────┴────┐           ┌─────┴─────┐          ┌────┴────┐
   │ CI/CD   │           │  Testing  │          │ Security│
   │ Agents  │           │  Agents   │          │ Agents  │
   └─────────┘           └───────────┘          └─────────┘
```

---

## Interface Definition

### AgentBrainInterface

The `AgentBrainInterface` class is the primary interface for agent-brain communication.

```python
from codex.cognitive.brain_interface import AgentBrainInterface

# Initialize with agent ID
brain = AgentBrainInterface(agent_id="ci-testing-agent")
```

### Core Methods

#### 1. Pattern Query

```python
patterns = brain.query_patterns(
    symptoms="pytest collection error",
    category="testing",           # Optional filter
    min_confidence=PatternConfidence.MEDIUM,
    limit=5
)
```

**Returns:** `List[PatternMatch]`

#### 2. Pattern Submission

```python
brain.submit_pattern(
    pattern_id="NEW-001",
    category="testing",
    symptoms=["specific error message"],
    solutions=["solution steps"],
    diagnosis_steps=["step 1", "step 2"]
)
```

**Returns:** `bool`

#### 3. Objective Alignment Check

```python
alignment = brain.check_alignment(
    proposed_action="run additional tests",
    context=AgentContext(...)
)
```

**Returns:** `ObjectiveAlignment` (ALIGNED, PARTIALLY_ALIGNED, MISALIGNED, UNKNOWN)

#### 4. Session State Access

```python
# Read state
state = brain.get_session_state()

# Update state
brain.update_session_state({
    "current_phase": "testing",
    "progress": 0.75
})
```

#### 5. Learning Feedback

```python
brain.submit_learning(
    pattern_id="TFR-001",
    outcome="success",
    context={"issue": "import error", "resolution": "added mock"},
    resolution_details="Added mock for optional dependency"
)
```

**Returns:** `bool`

---

## Data Types

### AgentContext

```python
@dataclass
class AgentContext:
    agent_id: str
    agent_category: AgentCategory
    session_id: Optional[str]
    pr_number: Optional[int]
    symptoms: List[str]
    current_phase: str
    metadata: Dict[str, Any]
```

### PatternMatch

```python
@dataclass
class PatternMatch:
    pattern_id: str
    category: str
    confidence: PatternConfidence
    match_score: float
    symptoms: List[str]
    solutions: List[str]
    success_rate: float
    times_applied: int
    related_prs: List[str]
    diagnosis_steps: List[str]
```

### LearningFeedback

```python
@dataclass
class LearningFeedback:
    pattern_id: str
    outcome: str  # "success", "failure", "partial"
    agent_id: str
    context: Dict[str, Any]
    resolution_details: str
    new_symptoms: List[str]
    suggested_improvements: List[str]
```

### BrainResponse

```python
@dataclass
class BrainResponse:
    success: bool
    message: str
    patterns: List[PatternMatch]
    objectives: List[str]
    session_state: Dict[str, Any]
    recommendations: List[str]
    metadata: Dict[str, Any]
```

---

## Agent Categories

| Category | Agents |
|----------|--------|
| `CI_CD` | ci-testing-agent, ci-log-retrieval-agent, workflow-ci-fixer, artifact-monitor-agent |
| `TESTING` | coverage-roadmap-agent, test-alignment-fixer, test-coverage-monitor, qa-walkthrough-agent |
| `SECURITY` | security-alert-verification-agent, codeql-alert-resolution-agent, security-audit-agent |
| `DOCUMENTATION` | documentation-consolidator, link-validator-agent, doc-freshness-checker |
| `RAG_ML` | rag-index-manager, meta-tensor-validator, rag-meta-tensor-regression-agent |
| `REPOSITORY` | repository-hygiene-agent, root-organizer-agent, reference-updater-agent |
| `CONFIG` | config-validator, config-migration-assistant |
| `SESSION` | session-analysis-agent, session-log-retrieval-agent |

---

## Integration Pattern

### Standard Integration Flow

1. **Initialize Interface**
   ```python
   from codex.cognitive.brain_interface import AgentBrainInterface
   
   brain = AgentBrainInterface(agent_id="my-agent")
   ```

2. **Query Patterns Before Diagnosis**
   ```python
   symptoms = ["error message from logs"]
   patterns = brain.query_patterns(symptoms)
   
   if patterns:
       # Apply most relevant pattern
       best_pattern = patterns[0]
       for step in best_pattern.diagnosis_steps:
           # Execute diagnosis step
           pass
   ```

3. **Check Alignment Before Action**
   ```python
   alignment = brain.check_alignment("proposed action")
   
   if alignment == ObjectiveAlignment.MISALIGNED:
       # Reconsider action
       pass
   ```

4. **Report Learnings After Resolution**
   ```python
   brain.submit_learning(
       pattern_id="TFR-001",
       outcome="success",
       context={"resolution": "description"}
   )
   ```

5. **Update Session State**
   ```python
   brain.update_session_state({
       "last_action": "completed diagnosis",
       "patterns_applied": ["TFR-001"]
   })
   ```

---

## Message Schemas

### Pattern Query Request

```json
{
    "method": "query_patterns",
    "params": {
        "symptoms": ["error message"],
        "category": "testing",
        "min_confidence": "medium",
        "limit": 5
    }
}
```

### Pattern Query Response

```json
{
    "success": true,
    "patterns": [
        {
            "pattern_id": "TFR-001",
            "category": "testing",
            "confidence": "high",
            "match_score": 0.92,
            "symptoms": ["pytest collection error"],
            "solutions": ["Add missing imports"],
            "success_rate": 0.95,
            "times_applied": 5
        }
    ]
}
```

### Learning Feedback Request

```json
{
    "method": "submit_learning",
    "params": {
        "pattern_id": "TFR-001",
        "outcome": "success",
        "agent_id": "ci-testing-agent",
        "context": {
            "error": "import error",
            "fix": "added mock"
        },
        "resolution_details": "Added mock for optional dependency"
    }
}
```

---

## File Locations

| File | Purpose |
|------|---------|
| `src/codex/cognitive/brain_interface.py` | Core interface implementation |
| `src/codex/cognitive/adapters/__init__.py` | Category-specific adapters |
| `.codex/cognitive_brain/pattern_learning_store.json` | Pattern storage |
| `.codex/cognitive_brain/session_tracker.md` | Session state |
| `.codex/cognitive_brain/objectives_tracker.md` | Objectives |

---

## Success Rate Calculation

Pattern success rates are updated using Exponential Moving Average (EMA):

```
new_rate = α × outcome + (1 - α) × old_rate

Where:
- α = 0.3 (smoothing factor)
- outcome = 1.0 (success), 0.5 (partial), 0.0 (failure)
```

---

## Confidence Levels

| Level | Score Range | Description |
|-------|-------------|-------------|
| HIGH | ≥ 85% | Strong pattern match |
| MEDIUM | 60-84% | Partial pattern match |
| LOW | < 60% | Weak pattern match |

---

## Best Practices

### For Agents

1. **Always query patterns first** before attempting diagnosis
2. **Check alignment** for significant actions
3. **Submit learning feedback** after applying patterns
4. **Update session state** at meaningful checkpoints
5. **Use category-specific adapters** when available

### For Pattern Submission

1. Use unique, descriptive pattern IDs (e.g., "TFR-001" for test failure resolution)
2. Include multiple symptoms for better matching
3. Provide step-by-step diagnosis procedures
4. List solutions from most to least common
5. Reference related PRs for context

---

## Error Handling

The interface handles errors gracefully:

```python
try:
    patterns = brain.query_patterns(symptoms)
except Exception as e:
    logger.error(f"Pattern query failed: {e}")
    patterns = []  # Graceful degradation
```

All methods return safe defaults on failure:
- `query_patterns()` → `[]`
- `check_alignment()` → `ObjectiveAlignment.UNKNOWN`
- `get_session_state()` → `{}`
- `submit_learning()` → `False`

---

## Related Documentation

- [Agent Selection Guide](../../.github/agents/AGENT_SELECTION_GUIDE.md)
- [Agent Chaining Guide](../../.github/agents/AGENT_CHAINING_GUIDE.md)
- [Cognitive Brain Architecture](../../.github/agents/COGNITIVE_BRAIN_ARCHITECTURE_DIAGRAMS.md)
- [Session Analysis Agent](../../.github/agents/session-analysis-agent.md)

---

**Last Updated:** 2026-02-05  
**Next Review:** After Phase 1.2 completion
