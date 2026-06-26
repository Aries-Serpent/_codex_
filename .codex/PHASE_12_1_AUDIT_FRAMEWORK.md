# Phase 12.1 — Audit Framework Design Document

**Track:** 12.1 — Role-Based Access Control  
**Status:** ✅ Implemented  
**Location:** `src/codex/governance/` + `src/codex/authz/audit_logger.py`

---

## 1. Overview

Every security-relevant operation in the Codex ecosystem must be auditable.
The audit framework records who did what, when, to which resource, and with
what outcome — providing the evidence chain required for compliance reviews,
incident investigations, and governance reporting.

The framework is built on top of the existing `AuditLogger` class from
`src/codex/authz/audit_logger.py` and extended by the governance layer to
capture RBAC-specific events (permission checks, role changes) and approval
workflow events (submission, approval, rejection, expiry).

---

## 2. Audit Log Schema

Each audit record is stored as a JSON object. The canonical schema is:

```json
{
  "event_id":    "550e8400-e29b-41d4-a716-446655440000",
  "event_type":  "permission.check.allow",
  "timestamp":   1720000000.123456,
  "timestamp_iso": "2024-07-03T12:00:00.123456Z",
  "actor":       "alice",
  "action":      "execute",
  "resource":    "agents",
  "resource_id": "my-agent-v2",
  "outcome":     "allow",
  "roles":       ["agent_operator"],
  "metadata": {
    "source":    "rbac_enforcer",
    "trace_id":  "abc-123",
    "context":   {}
  }
}
```

### 2.1 Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `event_id` | UUID string | Yes | Globally unique identifier for this audit record |
| `event_type` | string | Yes | Dotted-path event classifier (see §3) |
| `timestamp` | float | Yes | Unix epoch with microsecond precision |
| `timestamp_iso` | string | Yes | ISO 8601 UTC timestamp for human readability |
| `actor` | string | Yes | Identity (user ID, agent ID, or `__system__`) that triggered the event |
| `action` | string | Yes | The action attempted (`create`, `read`, `execute`, `approve`, …) |
| `resource` | string | Yes | Resource type (`agents`, `workflows`, `secrets`, …) |
| `resource_id` | string | No | Specific resource instance identifier |
| `outcome` | string | Yes | `allow`, `deny`, `approve`, `reject`, `expire`, `auto_approve` |
| `roles` | list[string] | No | Roles held by the actor at time of check |
| `metadata` | object | No | Arbitrary key-value context (trace IDs, PR numbers, etc.) |

### 2.2 Approval-Specific Fields

Approval workflow events extend the base schema with:

```json
{
  "event_type":   "approval.approve",
  "request_id":  "550e8400-…",
  "requester":   "bob",
  "approver":    "alice",
  "reason":      "LGTM — confirmed no side effects",
  "auto_approved": false,
  "age_seconds": 47.3,
  "expires_at":  1720000300.0
}
```

---

## 3. Event Taxonomy

All events use a three-part dotted namespace: `<domain>.<operation>.<outcome>`.

### 3.1 RBAC Events

| Event Type | Trigger |
|------------|---------|
| `rbac.permission.allow` | `check_permission()` returns `True` |
| `rbac.permission.deny` | `check_permission()` raises `PermissionDeniedError` |
| `rbac.role.assign` | `assign_role()` succeeds |
| `rbac.role.revoke` | `revoke_role()` succeeds |
| `rbac.role.assign_fail` | `assign_role()` called with unknown role |
| `rbac.role.revoke_fail` | `revoke_role()` called for unassigned role |

### 3.2 Approval Workflow Events

| Event Type | Trigger |
|------------|---------|
| `approval.submit` | New `ApprovalRequest` created |
| `approval.auto_approve` | RBAC auto-approval applied at submission time |
| `approval.approve` | Approver calls `approve()` |
| `approval.reject` | Approver calls `reject()` |
| `approval.expire` | Request exceeded timeout without resolution |

### 3.3 System Events

| Event Type | Trigger |
|------------|---------|
| `system.bootstrap` | `RBACEnforcer` initialised and roles registered |
| `system.purge` | `purge_resolved()` removes stale requests |

---

## 4. What Is Audited

The audit framework captures **every** security-relevant state change:

```
┌──────────────────────────────────────────────────────────────────────┐
│  ALWAYS AUDITED                                                       │
│                                                                      │
│  • Every permission check (allow AND deny)                           │
│  • Every role assignment / revocation                                │
│  • Every approval request submission                                 │
│  • Every approval decision (approve / reject)                        │
│  • Every request expiry                                              │
│  • Every RBAC auto-approval                                          │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│  NOT AUDITED (by design)                                             │
│                                                                      │
│  • The content of resources (only metadata is recorded)             │
│  • Read operations on non-sensitive resources (configurable)        │
│  • Internal bootstrap permission registration                        │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 5. Retention Policy

| Category | Retention Period | Rationale |
|----------|-----------------|-----------|
| Permission deny events | 365 days | Security incident investigation window |
| Approval decisions | 730 days (2 years) | Regulatory compliance |
| Role assignment/revocation | 730 days (2 years) | Access-control audit trail |
| Permission allow events | 90 days | Operational troubleshooting |
| Expired approval requests | 90 days | Workflow performance analysis |

These periods align with common SOC 2 Type II and ISO 27001 requirements.
Immutable append-only storage should be used in production to prevent tampering.

---

## 6. Query Patterns for Compliance Reports

### 6.1 "Who approved what in the last 30 days?"

```python
from codex.governance import ApprovalWorkflowEngine

engine = ApprovalWorkflowEngine()
recent_approvals = [
    req for req in engine.list_all()
    if any(d.decision.value == "approved" for d in req.decisions)
    and (time.time() - req.created_at) < 30 * 86400
]
```

In a production store (e.g. SQLite or Elasticsearch):

```sql
SELECT
    request_id,
    actor       AS approver,
    resource,
    action,
    timestamp_iso
FROM audit_log
WHERE event_type = 'approval.approve'
  AND timestamp > UNIXEPOCH() - 30 * 86400
ORDER BY timestamp DESC;
```

### 6.2 "All permission denials for a specific user"

```sql
SELECT *
FROM audit_log
WHERE event_type = 'rbac.permission.deny'
  AND actor = 'eve'
ORDER BY timestamp DESC;
```

### 6.3 "Role changes in the last 7 days"

```sql
SELECT actor, action, resource, outcome, timestamp_iso
FROM audit_log
WHERE event_type IN ('rbac.role.assign', 'rbac.role.revoke')
  AND timestamp > UNIXEPOCH() - 7 * 86400
ORDER BY timestamp DESC;
```

### 6.4 "Approval SLA compliance (requests resolved within 5 minutes)"

```sql
SELECT
    request_id,
    requester,
    resource,
    action,
    age_seconds,
    CASE WHEN age_seconds <= 300 THEN 'compliant' ELSE 'breach' END AS sla_status
FROM audit_log
WHERE event_type IN ('approval.approve', 'approval.reject')
ORDER BY timestamp DESC;
```

### 6.5 "Unapproved secrets access attempts"

```sql
SELECT *
FROM audit_log
WHERE event_type = 'rbac.permission.deny'
  AND resource = 'secrets'
ORDER BY timestamp DESC;
```

---

## 7. Integration with `src/codex/authz/audit_logger.py`

```
┌──────────────────────────────────────────────────────────┐
│         src/codex/governance/                             │
│                                                          │
│   RBACEnforcer._audit_logger  ──► AuditLogger._data      │
│   ApprovalWorkflowEngine._audit ──► AuditLogger._data    │
└──────────────────────────────────────────────────────────┘
                          │
                          ▼
              src/codex/authz/audit_logger.py
              AuditLogger (Phase 11 primitive)
```

The current implementation writes to `AuditLogger._data` (an in-memory dict)
using a structured key format:

```
"<outcome>:<actor>:<permission_string>:<unix_timestamp>"
→ True | False
```

For approval events:

```
"approval:<event>:<request_id>:<unix_timestamp>"
→ { event, request_id, action, resource, requester, status, ... }
```

### 7.1 Production Hardening Steps

When moving to production, extend `AuditLogger` to support:

1. **Persistent backend**: Flush records to an append-only log store
   (SQLite WAL, Kafka topic, or S3 with object lock).
2. **Structured emit API**: Replace `_data` dict with `log_event(record: dict)`
   method to decouple consumers from internal storage format.
3. **Tamper-evidence**: Apply HMAC-SHA256 chained signatures so that deleted
   or modified records are detectable.
4. **Real-time streaming**: Emit events to a SIEM (e.g. Splunk, Datadog) for
   alerting on anomalous permission denial spikes.

---

## 8. Security Considerations

### 8.1 Audit Log Integrity

- Audit records must be **append-only** — no UPDATE or DELETE on committed records.
- Access to audit logs is itself RBAC-gated: only `system_admin`, `agent_operator`,
  `ci_operator`, and `security_reviewer` may read audit logs.
- Modification of audit log schemas or retention policies requires `system_admin` approval.

### 8.2 Sensitive Data Scrubbing

Audit records must **never** contain:
- Secret values, credentials, or tokens
- Personal Identifiable Information beyond user IDs
- Full source code diffs (record metadata only)

### 8.3 Log Availability

- Audit service must be available before any permission check is executed.
- If the audit backend is unavailable, permission checks must **fail-closed**
  (deny access) rather than proceed without recording.

---

## 9. Implementation Checklist

- [x] `AuditLogger` instantiated in `RBACEnforcer`
- [x] All `check_permission()` allow/deny outcomes written to `AuditLogger`
- [x] All `assign_role()` / `revoke_role()` calls recorded
- [x] All approval lifecycle events (submit, approve, reject, expire) recorded
- [x] Structured payload format in approval events
- [ ] Persistent backend (post-Phase-12 work item)
- [ ] HMAC chained signatures (post-Phase-12 work item)
- [ ] Real-time SIEM streaming (post-Phase-12 work item)
