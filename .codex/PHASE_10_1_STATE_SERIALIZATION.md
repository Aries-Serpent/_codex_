# Phase 10.1: State Serialization Specification

**Version:** 1.0.0  
**Status:** ✅ Complete  

---

## Overview

Session state serialization enables capture and restoration of complete agent execution context at checkpoint time. The serialization system supports multiple formats (JSON, binary) and compression for efficient storage.

---

## Serialization Formats

### JSON Format (Human-Readable)

**Best for:** Debugging, monitoring, human inspection

```json
{
  "schema_version": 1,
  "serializer_version": "1.0.0",
  "timestamp": "2026-07-01T14:30:00Z",
  "agent_state": {
    "agent_id": "semantic_search",
    "agent_type": "custom",
    "status": "running",
    "version": "1.0.0",
    "metadata": {
      "start_time": "2026-07-01T10:00:00Z",
      "elapsed_seconds": 16200,
      "tasks_assigned": 5,
      "tasks_completed": 3
    }
  },
  "decision_history": [
    {
      "decision_id": "d_001",
      "timestamp": "2026-07-01T10:05:00Z",
      "decision_type": "code_change",
      "description": "Optimized search algorithm",
      "confidence": 0.95,
      "outcome": "success",
      "work_items_affected": ["refactor-search-v2"],
      "metrics": {
        "lines_changed": 42,
        "test_coverage": 0.87
      }
    }
  ],
  "memory_snapshot": {
    "short_term_memory": [
      {
        "pattern_id": "p_043",
        "category": "optimization",
        "relevance_score": 0.92,
        "last_used": "2026-07-01T14:25:00Z"
      }
    ],
    "long_term_memory": [],
    "total_patterns": 47,
    "memory_usage_bytes": 245892
  },
  "execution_progress": {
    "current_task": "implementation",
    "completed_tasks": ["analysis", "design"],
    "pending_tasks": ["testing", "deployment"],
    "failed_tasks": [],
    "work_items": {
      "total": 10,
      "completed": 3,
      "failed": 0,
      "pending": 7
    },
    "milestones": {
      "completed": ["analysis_phase", "design_phase"],
      "current": "implementation_phase",
      "pending": ["testing_phase", "deployment_phase"]
    }
  },
  "repository_state": {
    "branch": "main",
    "commit_sha": "a1b2c3d4e5f6...",
    "uncommitted_changes": 0,
    "tracked_files_count": 1245,
    "last_commit_time": "2026-07-01T14:30:00Z"
  },
  "context_snapshot": {
    "system_prompt_hash": "sha256:e3b0c44298fc1c14...",
    "user_context": {
      "github_actor": "mbaetiong",
      "pull_request": 3401,
      "repository": "Aries-Serpent/_codex_"
    },
    "configuration": {
      "checkpoint_trigger_type": "commit",
      "checkpoint_interval": 5
    }
  }
}
```

### Binary Format (msgpack)

**Best for:** Storage efficiency, high-volume checkpointing

- Compact binary encoding via msgpack
- ~50% smaller than JSON
- Efficient for large sessions (100+ decisions, 1000+ patterns)
- Transparently decompressed by SessionResume

**Compression**: gzip applied to both JSON and binary formats

---

## Serialization Classes

### SessionSerializer

Core serialization class supporting multiple formats and compression.

```python
from codex.brain.session_serializer import SessionSerializer

serializer = SessionSerializer()

# Serialize to JSON
json_str = serializer.serialize_to_json(state_dict)

# Serialize to binary
binary_data = serializer.serialize_to_binary(state_dict)

# Compress payload
compressed = serializer.compress_payload(json_data.encode())

# Decompress payload
decompressed = serializer.decompress_payload(compressed_data)
```

### Snapshot Classes

Dataclasses for structured state capture:

- **AgentStateSnapshot** — Agent metadata and status
- **DecisionSnapshot** — Individual decision records with confidence
- **MemorySnapshot** — STM, LTM, pattern library state
- **ExecutionProgressSnapshot** — Task and milestone tracking
- **RepositoryStateSnapshot** — Git state (branch, commit, changes)
- **ContextSnapshot** — System context and configuration

```python
from codex.brain.session_serializer import (
    create_agent_state_snapshot,
    create_decision_snapshot,
    create_memory_snapshot,
)

# Create snapshots
agent = create_agent_state_snapshot("agent_id", "custom", version="1.0.0")
decision = create_decision_snapshot("d_001", "refactor", "Optimized code", 0.95)
memory = create_memory_snapshot(total_patterns=47, memory_usage_bytes=5000)

# Combine into complete session state
state = serializer.serialize_session_state(
    agent_state=agent,
    decision_history=[decision],
    memory_snapshot=memory,
)
```

---

## Serialization Workflow

### Capturing Session State

```
Agent Execution
    ↓
    Collect:
    - Agent ID, type, version
    - All decisions made (with timestamps, confidence)
    - Memory snapshots (STM, LTM, patterns)
    - Task progress (completed, pending, failed)
    - Milestone tracking
    - Repository state (branch, commit, changes)
    ↓
    Create snapshots via SessionSerializer
    ↓
    Serialize to JSON or Binary
    ↓
    Compress with gzip (9x compression)
    ↓
    Write to checkpoint file
```

### Restoring Session State

```
Checkpoint File (gzip compressed)
    ↓
    Decompress with gzip
    ↓
    Deserialize from JSON or Binary
    ↓
    Restore snapshots:
    - Agent state injected
    - Decision history restored
    - Memory re-populated
    - Progress tracking reset
    - Context re-applied
    ↓
    Agent resumes from last task
```

---

## Field Specifications

### AgentStateSnapshot

| Field | Type | Example | Notes |
|-------|------|---------|-------|
| agent_id | str | "semantic_search" | Unique agent identifier |
| agent_type | str | "custom" or "builtin" | Agent classification |
| status | str | "running", "paused", "completed" | Current execution status |
| version | str | "1.0.0" | Agent version |
| metadata | dict | {"start_time": "...", ...} | Additional agent metadata |

### DecisionSnapshot

| Field | Type | Example | Notes |
|-------|------|---------|-------|
| decision_id | str | "d_001" | Unique decision identifier |
| timestamp | str | "2026-07-01T10:05:00Z" | ISO 8601 timestamp |
| decision_type | str | "code_change", "analysis" | Type of decision |
| description | str | "Optimized search" | Human-readable description |
| confidence | float | 0.95 | Confidence score (0-1) |
| outcome | str | "success", "pending", "failed" | Decision outcome |
| work_items_affected | list[str] | ["task_001"] | Affected work items |
| metrics | dict | {"lines_changed": 42} | Decision metrics |

### MemorySnapshot

| Field | Type | Example | Notes |
|-------|------|---------|-------|
| short_term_memory | list | [{"pattern_id": "p_043", ...}] | STM entries |
| long_term_memory | list | [...] | LTM entries |
| total_patterns | int | 47 | Number of patterns |
| memory_usage_bytes | int | 245892 | Total memory consumed |

### ExecutionProgressSnapshot

| Field | Type | Example | Notes |
|-------|------|---------|-------|
| current_task | str | "implementation" | Currently executing task |
| completed_tasks | list[str] | ["t1", "t2"] | Completed tasks |
| pending_tasks | list[str] | ["t3", "t4"] | Pending tasks |
| failed_tasks | list[str] | [] | Failed tasks |
| work_items | dict | {"total": 10, "completed": 3, ...} | Work item counts |
| milestones | dict | {"completed": [...], "current": "..."} | Milestone tracking |

### RepositoryStateSnapshot

| Field | Type | Example | Notes |
|-------|------|---------|-------|
| branch | str | "main" | Current branch |
| commit_sha | str | "abc123..." | Current commit SHA |
| uncommitted_changes | int | 0 | Number of uncommitted changes |
| tracked_files_count | int | 1245 | Total tracked files |
| last_commit_time | str | "2026-07-01T..." | Last commit timestamp |

---

## Size Characteristics

### Typical Session Sizes

| Session Type | Decisions | Patterns | Uncompressed | Compressed | Ratio |
|---|---|---|---|---|---|
| Short (1 hour) | 10 | 25 | 15 KB | 4 KB | 3.75x |
| Medium (4 hours) | 50 | 75 | 75 KB | 18 KB | 4.17x |
| Large (8 hours) | 150 | 200 | 225 KB | 45 KB | 5.0x |
| Very Large (16 hours) | 500 | 500 | 750 KB | 135 KB | 5.56x |

---

## Compression Algorithm

**Algorithm:** gzip (RFC 1952)  
**Compression Level:** 9 (maximum compression)  
**Typical Compression Ratios:**
- JSON text: 4-6x compression
- Binary msgpack: 2-3x compression (already compact)

---

## Error Handling

### Serialization Failures

```python
try:
    json_str = serializer.serialize_to_json(state_dict)
except Exception as e:
    logger.error(f"Serialization failed: {e}")
    # Gracefully handle or retry
```

### Deserialization Failures

```python
try:
    state_dict = serializer.deserialize_from_json(json_str)
except json.JSONDecodeError:
    logger.error("JSON decode failed")
    # Fall back to previous checkpoint or manual recovery
except KeyError:
    logger.error("Missing required fields in state")
    # Attempt partial recovery
```

---

## Testing

Comprehensive tests cover:
- ✅ Empty state serialization
- ✅ Complete state serialization with all fields
- ✅ JSON format roundtrip
- ✅ Binary format roundtrip
- ✅ Compression/decompression
- ✅ Large session handling (500+ decisions)
- ✅ Error conditions (corruption, missing fields)

All tests in `tests/integration/test_phase_10_1_session_resume.py`

---

## Performance

| Operation | Time (ms) | Notes |
|-----------|-----------|-------|
| Serialize complete state | 2-5 | For medium session (50 decisions) |
| Serialize to JSON | 1-2 | JSON encoding |
| Serialize to binary | 1-3 | Msgpack encoding |
| Compress 50KB → 10KB | 5-10 | gzip level 9 |
| Deserialize from JSON | 3-8 | JSON parsing |
| Decompress 10KB → 50KB | 2-5 | gzip decompression |

---

## Future Enhancements

- **Incremental Serialization** — Only serialize deltas since last checkpoint
- **Schema Evolution** — Support multiple schema versions with migrations
- **Streaming Serialization** — Real-time state updates during execution
- **Custom Serializers** — Pluggable serialization backends
