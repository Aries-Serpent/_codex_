# Brain Module API Reference
**Last Updated:** 2026-07-11
**Version:** v0.2.1

**Module Path**: `src/codex/brain/`
**Version**: Phase 10+
**Purpose**: Cognitive brain orchestration, session management, checkpoints, memory consolidation

---

## Overview

The Brain module provides core functionality for session management, checkpoint/recovery mechanisms, and OODA-based orchestration. It enables stateful agent execution with automatic recovery capabilities.

## Table of Contents

1. [Core Classes](#core-classes)
2. [Function Signatures](#function-signatures)
3. [Usage Examples](#usage-examples)
4. [Best Practices](#best-practices)
5. [Error Handling](#error-handling)

---

## Core Classes

### CheckpointManager

Manages the lifecycle of session checkpoints, enabling recovery and state restoration.

```python
class CheckpointManager:
 """Manage session checkpoints and recovery.
 
 Handles checkpoint creation, listing, retrieval, and conditional checkpointing
 based on task progress thresholds.
 """
```

**Key Methods**:

#### `create_checkpoint(session_id, agent_state, context, title, metadata=None)`

Create a new checkpoint for a session.

**Parameters**:
- `session_id` (str): Unique session identifier
- `agent_state` (dict): Current agent state/context
- `context` (dict): Execution context (variables, config, etc.)
- `title` (str): Descriptive checkpoint title
- `metadata` (dict, optional): Additional checkpoint metadata

**Returns**: `Checkpoint` object with id, timestamp, and state

**Example**:
```python
checkpoint = manager.create_checkpoint(
 session_id="sess-001",
 agent_state={"progress": 0.5, "completed_tasks": [...]},
 context={"repo": "...", "branch": "main"},
 title="Data processing phase 1 complete",
 metadata={"phase": 1, "records_processed": 50000}
)
```

#### `list_checkpoints(session_id, limit=50)`

List all checkpoints for a session.

**Parameters**:
- `session_id` (str): Session to query
- `limit` (int): Maximum results to return (default: 50)

**Returns**: List of `Checkpoint` objects, newest first

**Example**:
```python
checkpoints = manager.list_checkpoints(session_id="sess-001")
for cp in checkpoints:
 print(f"{cp.title} - Created: {cp.created_at}")
```

#### `get_checkpoint(checkpoint_id)`

Retrieve a specific checkpoint by ID.

**Parameters**:
- `checkpoint_id` (str): Checkpoint identifier

**Returns**: `Checkpoint` object or None if not found

**Example**:
```python
checkpoint = manager.get_checkpoint(checkpoint_id="cp-12345")
if checkpoint:
 print(f"Checkpoint: {checkpoint.title}")
 print(f"State: {checkpoint.agent_state}")
```

#### `maybe_checkpoint(session_id, threshold=0.5)`

Conditionally create a checkpoint based on progress.

**Parameters**:
- `session_id` (str): Session identifier
- `threshold` (float): Progress threshold (0.0-1.0). Creates checkpoint if progress >= threshold

**Returns**: `Checkpoint` object if created, None otherwise

**Example**:
```python
# Create checkpoint if 80% through task
checkpoint = manager.maybe_checkpoint(session_id="sess-001", threshold=0.8)
if checkpoint:
 print(f"Checkpoint created at {checkpoint.created_at}")
```

---

### SessionResume

Handles session recovery from checkpoints.

```python
class SessionResume:
 """Resume sessions from checkpoint state.
 
 Restores agent state, context, and execution state from checkpoints,
 enabling stateful recovery and continuation.
 """
```

**Key Methods**:

#### `resume_from_checkpoint(checkpoint_id)`

Load and resume a session from checkpoint.

**Parameters**:
- `checkpoint_id` (str): ID of checkpoint to resume from

**Returns**: `ResumeResult` object containing restored state

**Example**:
```python
resume = SessionResume()
result = resume.resume_from_checkpoint(checkpoint_id="cp-12345")

if result.success:
 restored_state = result.agent_state
 restored_context = result.context
 print(f"Resumed at: {result.timestamp}")
else:
 print(f"Resume failed: {result.error}")
```

#### `get_resume_result()`

Get the last resume result.

**Returns**: `ResumeResult` from most recent resume operation

---

### MemorySyncEngine

Consolidates short-term memory (STM) to long-term memory (LTM) with pattern discovery.

```python
class MemorySyncEngine:
 """STMLTM consolidation and pattern discovery.
 
 Automatically consolidates memory, discovers patterns, and tags
 improvement areas for continuous learning.
 """
```

**Key Methods**:

#### `consolidate_memories()`

Move STM entries to LTM with deduplication.

**Returns**: `ConsolidationMetrics` with consolidation statistics

**Example**:
```python
engine = MemorySyncEngine()
metrics = engine.consolidate_memories()

print(f"Consolidated: {metrics.stm_entries_moved}")
print(f"Duplicates found: {metrics.duplicates_detected}")
print(f"Patterns discovered: {metrics.patterns_discovered}")
```

#### `discover_patterns()`

Identify patterns in consolidated memory.

**Returns**: List of `PatternEntry` objects

**Example**:
```python
patterns = engine.discover_patterns()
for pattern in patterns:
 print(f"Pattern: {pattern.name}")
 print(f"Type: {pattern.pattern_type}")
 print(f"Frequency: {pattern.frequency}")
```

#### `tag_improvement_areas()`

Auto-tag patterns with improvement areas.

**Returns**: Dictionary mapping patterns to improvement areas

**Example**:
```python
improvement_tags = engine.tag_improvement_areas()
for pattern_id, areas in improvement_tags.items():
 print(f"{pattern_id}: {areas}")
```

---

### OODAOrchestrator

Coordinates OODA (Observe, Orient, Decide, Act) loop execution.

```python
class OODAOrchestrator:
 """Orchestrate OODA loop execution.
 
 Manages the observe orient decide act cycle with
 decision caching and optimization.
 """
```

**Key Methods**:

#### `execute_cycle(observation, context)`

Execute one complete OODA cycle.

**Parameters**:
- `observation` (dict): Current observations from environment
- `context` (dict): Execution context

**Returns**: `OODAResult` with decision and actions

**Example**:
```python
orchestrator = OODAOrchestrator()

result = orchestrator.execute_cycle(
 observation={"task_status": "in_progress", "progress": 0.5},
 context={"session_id": "sess-001"}
)

if result.success:
 print(f"Decision: {result.decision}")
 print(f"Actions: {result.actions}")
```

---

## Function Signatures

Complete API signatures for all public functions:

```python
# Session & Checkpoint Management
def create_checkpoint(
 session_id: str,
 agent_state: Dict[str, Any],
 context: Dict[str, Any],
 title: str,
 metadata: Optional[Dict[str, Any]] = None
) -> Checkpoint: ...

def list_checkpoints(
 session_id: str,
 limit: int = 50,
 offset: int = 0
) -> List[Checkpoint]: ...

def get_checkpoint(checkpoint_id: str) -> Optional[Checkpoint]: ...

def maybe_checkpoint(
 session_id: str,
 threshold: float = 0.5
) -> Optional[Checkpoint]: ...

def delete_checkpoint(
 checkpoint_id: str,
 audit_reason: Optional[str] = None
) -> bool: ...

# Session Resume
def resume_from_checkpoint(
 checkpoint_id: str
) -> ResumeResult: ...

# Memory Management
def consolidate_memories() -> ConsolidationMetrics: ...

def discover_patterns() -> List[PatternEntry]: ...

def tag_improvement_areas() -> Dict[str, List[str]]: ...

# OODA Orchestration
def execute_ooda_cycle(
 observation: Dict[str, Any],
 context: Dict[str, Any]
) -> OODAResult: ...
```

---

## Usage Examples

### Example 1: Basic Checkpoint & Recovery

```python
from codex.brain import CheckpointManager, SessionResume, RetentionPolicy

# Initialize checkpoint manager
manager = CheckpointManager(
 storage_path="/data/checkpoints",
 retention_policy=RetentionPolicy(max_age_days=90)
)

# Create checkpoint at milestone
state = {
 "progress": 0.5,
 "completed_items": ["task1", "task2"],
 "current_task": "task3"
}

checkpoint = manager.create_checkpoint(
 session_id="my-session",
 agent_state=state,
 context={"repo": "my-repo", "branch": "main"},
 title="Milestone: 50% complete"
)

print(f"Created checkpoint: {checkpoint.id}")

# ... later, restore from checkpoint
resume = SessionResume()
result = resume.resume_from_checkpoint(checkpoint_id=checkpoint.id)

if result.success:
 print("Session restored successfully")
 print(f"Progress: {result.agent_state['progress']}")
```

### Example 2: Conditional Checkpointing

```python
from codex.brain import CheckpointManager

manager = CheckpointManager()

# Check every N iterations
for i in range(1000):
 # Do work...
 current_progress = i / 1000
 
 # Create checkpoint at 25%, 50%, 75% milestones
 checkpoint = manager.maybe_checkpoint(
 session_id="long-task",
 threshold=current_progress
 )
 
 if checkpoint:
 print(f"Checkpoint created at {current_progress*100:.0f}%")
```

### Example 3: Memory Consolidation

```python
from codex.brain import MemorySyncEngine, ImprovementArea

engine = MemorySyncEngine()

# Consolidate STM to LTM
metrics = engine.consolidate_memories()
print(f"STMLTM: {metrics.stm_entries_moved} entries")
print(f"Duplicates: {metrics.duplicates_detected}")

# Discover patterns
patterns = engine.discover_patterns()
for pattern in patterns:
 print(f"Pattern: {pattern.name} (frequency: {pattern.frequency})")

# Tag with improvement areas
tags = engine.tag_improvement_areas()
for pattern_id, areas in tags.items():
 if ImprovementArea.PERFORMANCE in areas:
 print(f"Performance improvement opportunity: {pattern_id}")
```

### Example 4: OODA Loop

```python
from codex.brain import OODAOrchestrator

orchestrator = OODAOrchestrator()

# Execute OODA cycle
observation = {
 "current_task": "code-review",
 "queue_length": 5,
 "recent_errors": []
}

result = orchestrator.execute_cycle(
 observation=observation,
 context={"session_id": "sess-001"}
)

if result.success:
 print(f"Decision: {result.decision}")
 for action in result.actions:
 print(f" - {action.type}: {action.details}")
 
 # Execute recommended actions
 for action in result.actions:
 execute_action(action)
```

---

## Best Practices

### 1. Checkpoint Strategy

```python
# GOOD: Regular checkpoints with meaningful titles
def checkpoint_at_milestones(manager, session_id, phase):
 manager.create_checkpoint(
 session_id=session_id,
 agent_state=get_current_state(),
 context=get_context(),
 title=f"Phase {phase} complete - Data validated",
 metadata={"phase": phase, "checkpoint_type": "milestone"}
 )

# POOR: Vague, infrequent checkpoints
def poor_checkpointing(manager, session_id):
 manager.create_checkpoint(
 session_id=session_id,
 agent_state=state,
 context=context,
 title="Checkpoint"
 )
```

### 2. Memory Management

```python
# GOOD: Regular consolidation with analysis
def manage_memory(engine, consolidation_interval=3600):
 metrics = engine.consolidate_memories()
 
 if metrics.duplicates_detected > 100:
 logger.warning(f"High duplication: {metrics.duplicates_detected}")
 
 patterns = engine.discover_patterns()
 tags = engine.tag_improvement_areas()
 
 return {"metrics": metrics, "patterns": patterns, "tags": tags}

# POOR: No consolidation or analysis
def poor_memory_mgmt():
 # Memory grows unbounded without consolidation
 pass
```

### 3. Error Recovery

```python
# GOOD: Graceful recovery with fallback
def safe_resume(session_id, fallback_checkpoint=None):
 resume = SessionResume()
 result = resume.resume_from_checkpoint(session_id)
 
 if not result.success:
 logger.error(f"Resume failed: {result.error}")
 
 if fallback_checkpoint:
 return resume_from_checkpoint(fallback_checkpoint)
 else:
 return None
 
 return result

# POOR: Crash on resume failure
def unsafe_resume(session_id):
 resume = SessionResume()
 result = resume.resume_from_checkpoint(session_id)
 # Assumes result.success is always true
 return result
```

---

## Error Handling

### Common Errors and Solutions

**CheckpointNotFound**:
```python
try:
 checkpoint = manager.get_checkpoint(cp_id)
except CheckpointNotFound:
 print(f"Checkpoint {cp_id} not found")
 # Fall back to latest checkpoint
 checkpoints = manager.list_checkpoints(session_id, limit=1)
 checkpoint = checkpoints[0] if checkpoints else None
```

**ResumeFailed**:
```python
try:
 result = resume.resume_from_checkpoint(cp_id)
 if not result.success:
 raise ResumeFailed(result.error)
except ResumeFailed as e:
 logger.error(f"Could not resume: {e}")
 # Create fresh session
 initialize_new_session()
```

**ConsolidationFailed**:
```python
try:
 metrics = engine.consolidate_memories()
except ConsolidationFailed as e:
 logger.error(f"Memory consolidation failed: {e}")
 # Retry with cleanup
 engine.cleanup_corrupted_entries()
 metrics = engine.consolidate_memories()
```

---

## Related APIs

- [Session Context API](session-api-reference.md)
- [Governance API](governance-api-reference.md)
- [Observability API](observability-api-reference.md)

---

**Last Updated**: 2026-07-08
**Status**: Phase 10+ (Active)
**Author**: Codex Brain Team

