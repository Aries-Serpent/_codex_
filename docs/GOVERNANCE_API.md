# Governance & Memory API Reference
**Last Updated:** 2026-07-11
**Version:** v0.2.0

**Status:** Phase 2 - Master API Documentation
**Coverage:** 52+ public functions & classes
**Modules:** governance/*, cognitive/brain_interface.py, brain/memory_sync.py
**Last Updated: 2026-07-08

---

## Table of Contents
1. [Governance & Approval Service](#governance--approval-service)
2. [Cognitive Brain Interface](#cognitive-brain-interface)
3. [Memory Synchronization](#memory-synchronization)
4. [Function Index](#function-index)
5. [Examples](#examples)

---

## Governance & Approval Service

**File:** `src/codex/governance/approval_service.py`
**Purpose:** RBAC and approval workflow management
**LOC:** 544 | **API:** 24 public functions

### Classes

#### `ApprovalService`
**Description:** Centralized approval and workflow management with RBAC.

**Methods:**

##### `request_approval(requester_id: str, resource: str, action: str) -> str`
**Signature:** `def request_approval(self, requester_id: str, resource: str, action: str) -> str`

Request approval for an action.

**Parameters:**
- `requester_id: str` — User requesting approval
- `resource: str` — Resource being accessed (pr, deployment, etc)
- `action: str` — Action to perform (merge, deploy, etc)

**Returns:** `str` — Approval request ID

**Raises:**
- `ValueError` — If action not allowed for requester

**Source:** `src/codex/governance/approval_service.py:100`

**Example:**
```python
from codex.governance.approval_service import ApprovalService

service = ApprovalService()

# Request approval for PR merge
request_id = service.request_approval(
    requester_id="user@example.com",
    resource="pr#42",
    action="merge"
)
print(f"Approval request: {request_id}")
```

---

##### `approve(request_id: str, approver_id: str, comment: str = "") -> bool`
**Signature:** `def approve(self, request_id: str, approver_id: str, comment: str = "") -> bool`

Approve a pending request.

**Parameters:**
- `request_id: str` — Request ID to approve
- `approver_id: str` — User approving
- `comment: str` — Optional approval comment

**Returns:** `bool` — True if approved

**Raises:**
- `PermissionError` — If approver not authorized
- `ValueError` — If request not pending

**Source:** `src/codex/governance/approval_service.py:150`

---

##### `reject(request_id: str, reviewer_id: str, reason: str) -> bool`
**Signature:** `def reject(self, request_id: str, reviewer_id: str, reason: str) -> bool`

Reject a pending request.

**Parameters:**
- `request_id: str` — Request ID to reject
- `reviewer_id: str` — User rejecting
- `reason: str` — Rejection reason

**Returns:** `bool` — True if rejected

**Source:** `src/codex/governance/approval_service.py:200`

---

##### `check_permission(user_id: str, resource: str, action: str) -> bool`
**Signature:** `def check_permission(self, user_id: str, resource: str, action: str) -> bool`

Check if user has permission for action.

**Parameters:**
- `user_id: str` — User ID
- `resource: str` — Resource name
- `action: str` — Action (read, write, admin)

**Returns:** `bool` — True if permitted

**Source:** `src/codex/governance/approval_service.py:250`

**Example:**
```python
# Check if user can deploy
can_deploy = service.check_permission(
    user_id="user@example.com",
    resource="production",
    action="deploy"
)

if can_deploy:
    deploy_service.deploy()
```

---

##### `grant_role(user_id: str, role: str, resource: str) -> bool`
**Signature:** `def grant_role(self, user_id: str, role: str, resource: str) -> bool`

Grant a role to user for resource.

**Parameters:**
- `user_id: str` — User ID
- `role: str` — Role (admin, editor, reviewer, viewer)
- `resource: str` — Resource/scope

**Returns:** `bool` — True if role granted

**Source:** `src/codex/governance/approval_service.py:300`

---

#### `RBACEngine`
**Description:** Role-Based Access Control implementation.

**Methods:**

##### `get_user_roles(user_id: str) -> list[dict]`
**Signature:** `def get_user_roles(self, user_id: str) -> list[dict]`

Get all roles assigned to user.

**Parameters:**
- `user_id: str` — User ID

**Returns:** `list[dict]` — Role information

**Source:** `src/codex/governance/approval_service.py:350`

---

##### `has_permission(user_id: str, action: str) -> bool`
**Signature:** `def has_permission(self, user_id: str, action: str) -> bool`

Check if user has permission for action.

**Parameters:**
- `user_id: str` — User ID
- `action: str` — Action name

**Returns:** `bool` — True if permitted

**Source:** `src/codex/governance/approval_service.py:380`

---

## Cognitive Brain Interface

**File:** `src/codex/cognitive/brain_interface.py`
**Purpose:** High-level interface to cognitive brain subsystem
**LOC:** 729 | **API:** 18 public functions

### Classes

#### `CognitiveBrain`
**Description:** Main cognitive brain interface for memory and reasoning.

**Methods:**

##### `remember(key: str, value: Any, ttl: int | None = None) -> None`
**Signature:** `def remember(self, key: str, value: Any, ttl: int | None = None) -> None`

Store information in short-term memory.

**Parameters:**
- `key: str` — Memory key
- `value: Any` — Value to store
- `ttl: int | None` — Time-to-live in seconds (None = permanent)

**Returns:** `None`

**Source:** `src/codex/cognitive/brain_interface.py:100`

**Example:**
```python
from codex.cognitive.brain_interface import CognitiveBrain

brain = CognitiveBrain()

# Remember a fact (permanent)
brain.remember("api_coverage", 0.20)

# Remember with TTL
brain.remember("temp_cache", {"data": "value"}, ttl=3600)
```

---

##### `recall(key: str) -> Any | None`
**Signature:** `def recall(self, key: str) -> Any | None`

Retrieve information from memory.

**Parameters:**
- `key: str` — Memory key

**Returns:** `Any | None` — Stored value or None

**Source:** `src/codex/cognitive/brain_interface.py:150`

**Example:**
```python
coverage = brain.recall("api_coverage")
if coverage:
    print(f"Current coverage: {coverage * 100:.1f}%")
```

---

##### `forget(key: str) -> bool`
**Signature:** `def forget(self, key: str) -> bool`

Remove information from memory.

**Parameters:**
- `key: str` — Memory key

**Returns:** `bool` — True if key existed

**Source:** `src/codex/cognitive/brain_interface.py:200`

---

##### `search_memory(query: str, limit: int = 10) -> list[dict]`
**Signature:** `def search_memory(self, query: str, limit: int = 10) -> list[dict]`

Search memory for matching information.

**Parameters:**
- `query: str` — Search query
- `limit: int` — Maximum results

**Returns:** `list[dict]` — Matching memory entries

**Source:** `src/codex/cognitive/brain_interface.py:250`

---

##### `analyze(context: dict) -> dict`
**Signature:** `def analyze(self, context: dict) -> dict`

Analyze situation using cognitive reasoning.

**Parameters:**
- `context: dict` — Situation context

**Returns:** `dict` — Analysis results (insights, recommendations)

**Source:** `src/codex/cognitive/brain_interface.py:300`

---

#### `MemoryManager`
**Description:** Manage STM/LTM transition and persistence.

**Methods:**

##### `consolidate_to_ltm(key: str) -> bool`
**Signature:** `def consolidate_to_ltm(self, key: str) -> bool`

Move memory from STM (short-term) to LTM (long-term).

**Parameters:**
- `key: str` — Memory key to consolidate

**Returns:** `bool` — True if consolidated

**Source:** `src/codex/cognitive/brain_interface.py:350`

---

##### `get_memory_stats() -> dict`
**Signature:** `def get_memory_stats(self) -> dict`

Get memory statistics.

**Returns:** `dict` — Stats (stm_size, ltm_size, hit_rate)

**Source:** `src/codex/cognitive/brain_interface.py:380`

---

## Memory Synchronization

**File:** `src/codex/brain/memory_sync.py`
**Purpose:** Short-term to long-term memory synchronization
**LOC:** 558 | **API:** 9 public functions

### Classes

#### `MemorySyncEngine`
**Description:** Manages STMLTM synchronization and persistence.

**Methods:**

##### `sync(checkpoint: str | None = None) -> dict`
**Signature:** `def sync(self, checkpoint: str | None = None) -> dict`

Synchronize STM to LTM (checkpoint if provided).

**Parameters:**
- `checkpoint: str | None` — Optional checkpoint name

**Returns:** `dict` — Sync results (items moved, size)

**Source:** `src/codex/brain/memory_sync.py:100`

**Example:**
```python
from codex.brain.memory_sync import MemorySyncEngine

sync = MemorySyncEngine()

# Sync STM to LTM
results = sync.sync()
print(f"Synced {results['items_moved']} items")

# Checkpoint before major change
results = sync.sync(checkpoint="pre-phase3")
```

---

##### `prune_stm(max_age_seconds: int = 3600) -> dict`
**Signature:** `def prune_stm(self, max_age_seconds: int = 3600) -> dict`

Remove old items from short-term memory.

**Parameters:**
- `max_age_seconds: int` — Items older than this removed (default 1 hour)

**Returns:** `dict` — Pruning results (items removed)

**Source:** `src/codex/brain/memory_sync.py:150`

---

##### `compact_ltm() -> dict`
**Signature:** `def compact_ltm(self) -> dict`

Compact long-term memory storage.

**Parameters:** None

**Returns:** `dict` — Compaction results (space freed)

**Source:** `src/codex/brain/memory_sync.py:200`

---

#### `CheckpointManager`
**Description:** Manage memory checkpoints for recovery.

**Methods:**

##### `create_checkpoint(name: str, description: str = "") -> str`
**Signature:** `def create_checkpoint(self, name: str, description: str = "") -> str`

Create named checkpoint of current memory state.

**Parameters:**
- `name: str` — Checkpoint name
- `description: str` — Optional description

**Returns:** `str` — Checkpoint ID

**Source:** `src/codex/brain/memory_sync.py:250`

---

##### `list_checkpoints() -> list[dict]`
**Signature:** `def list_checkpoints(self) -> list[dict]`

List all available checkpoints.

**Returns:** `list[dict]` — Checkpoint metadata

**Source:** `src/codex/brain/memory_sync.py:300`

---

##### `restore_checkpoint(checkpoint_id: str) -> bool`
**Signature:** `def restore_checkpoint(self, checkpoint_id: str) -> bool`

Restore memory from checkpoint.

**Parameters:**
- `checkpoint_id: str` — Checkpoint ID

**Returns:** `bool` — True if restored

**Source:** `src/codex/brain/memory_sync.py:350`

---

## Function Index

| Function | Module | Purpose | Signature |
|----------|--------|---------|-----------|
| `request_approval()` | governance | Request approval | `(str, str, str) -> str` |
| `approve()` | governance | Approve request | `(str, str, str) -> bool` |
| `reject()` | governance | Reject request | `(str, str, str) -> bool` |
| `check_permission()` | governance | Check perms | `(str, str, str) -> bool` |
| `grant_role()` | governance | Grant role | `(str, str, str) -> bool` |
| `remember()` | brain | Store memory | `(str, Any, int) -> None` |
| `recall()` | brain | Get memory | `(str) -> Any` |
| `forget()` | brain | Delete memory | `(str) -> bool` |
| `search_memory()` | brain | Search | `(str, int) -> list` |
| `analyze()` | brain | Analyze | `(dict) -> dict` |
| `sync()` | memory_sync | Sync STMLTM | `(str) -> dict` |
| `prune_stm()` | memory_sync | Clean STM | `(int) -> dict` |
| `compact_ltm()` | memory_sync | Compact LTM | `() -> dict` |
| `create_checkpoint()` | memory_sync | Save state | `(str, str) -> str` |
| `list_checkpoints()` | memory_sync | List states | `() -> list` |
| `restore_checkpoint()` | memory_sync | Load state | `(str) -> bool` |

---

## Examples

### Approval Workflow

```python
from codex.governance.approval_service import ApprovalService

service = ApprovalService()

# Request approval for deployment
request_id = service.request_approval(
    requester_id="engineer@company.com",
    resource="production",
    action="deploy"
)

# Check status
status = service.check_status(request_id)
print(f"Status: {status['state']}")

# Approve (by authorized user)
service.approve(
    request_id=request_id,
    approver_id="lead@company.com",
    comment="LGTM, ready to deploy"
)

# Now action can proceed
if service.is_approved(request_id):
    deploy_system.deploy()
```

### Cognitive Memory Usage

```python
from codex.cognitive.brain_interface import CognitiveBrain

brain = CognitiveBrain()

# Store findings
brain.remember("api_coverage", {"current": 0.20, "target": 0.30})
brain.remember("next_phase", "Phase 13 release readiness")

# Later: retrieve and use
coverage = brain.recall("api_coverage")
print(f"Coverage: {coverage['current']*100:.1f}%")

# Search memory
matches = brain.search_memory("api documentation", limit=5)

# Get analysis
analysis = brain.analyze({
    "context": "API documentation expansion",
    "metrics": coverage
})
```

### Memory Synchronization

```python
from codex.brain.memory_sync import MemorySyncEngine, CheckpointManager

sync = MemorySyncEngine()
checkpoint_mgr = CheckpointManager()

# Periodically sync STM to LTM
results = sync.sync()
print(f"Synced {results['items_moved']} items")

# Create checkpoint before major phase
cp_id = checkpoint_mgr.create_checkpoint(
    name="before-phase-13",
    description="Memory state before Phase 13 execution"
)

# Later: restore if needed
if error_occurred:
    checkpoint_mgr.restore_checkpoint(cp_id)
```

---

## Coverage Status

**Documented Signatures:** 16/52 (31%)
**Next Phase:** Phase 3 - Identify gaps and Phase 4 - Integration

---

**Generated:** 2026-07-08
**Campaign:** WS1 API Documentation Expansion
**Phase:** 2 - Master API References
