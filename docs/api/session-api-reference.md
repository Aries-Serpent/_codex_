# Session Context API Reference
**Last Updated:** 2026-07-11
**Version:** v0.2.1

**Status**: Active  
**Phase**: Phase 12+ Documentation  
**Author**: Phase 12 WS3 Documentation Team

## Overview

Session Context API provides programmatic access to session state, context management, and session-scoped operations within the Codex ecosystem.

---

## Core Concepts

### Session Context
- Encapsulates user session state
- Manages authentication context
- Maintains request-scoped variables
- Provides session isolation

### Context Lifecycle
1. **Initialization**: Session creation and context setup
2. **Active**: Session in use with active context
3. **Suspension**: Session paused with context preserved
4. **Termination**: Session cleanup and context destruction

---

## API Endpoints

### Session Management

#### GET /api/sessions/{session_id}
Retrieve session context information.

**Request**:
```json
{
  "session_id": "sess_abc123"
}
```

**Response**:
```json
{
  "id": "sess_abc123",
  "user_id": "user_xyz",
  "created_at": "2026-07-08T16:52:26Z",
  "expires_at": "2026-07-08T17:52:26Z",
  "context": {
    "workspace": "/home/runner/work/_codex_/_codex_",
    "branch": "main",
    "environment": "production"
  }
}
```

#### POST /api/sessions
Create a new session context.

**Request**:
```json
{
  "user_id": "user_xyz",
  "duration_minutes": 60,
  "workspace": "/path/to/workspace"
}
```

#### DELETE /api/sessions/{session_id}
Terminate a session and clear context.

---

## Context Variables

| Variable | Type | Description |
|----------|------|-------------|
| `session_id` | string | Unique session identifier |
| `user_id` | string | Associated user ID |
| `workspace` | string | Working directory path |
| `branch` | string | Current git branch |
| `created_at` | timestamp | Session creation time |
| `expires_at` | timestamp | Session expiration time |

---

## Related APIs

- [Brain API](brain-api-reference.md)
- [Governance API](governance-api-reference.md)
- [Observability API](observability-api-reference.md)

---

**Last Updated**: 2026-07-08  
**Status**: Phase 12+ (Active)  
**Author**: Codex API Team
