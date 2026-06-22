# ADR-20260313: UserStore Persistence Backend

**Last Updated:** 2026-06-22

**Status:** Proposed  
**Date:** 2026-03-13  
**Authors:** GitHub Copilot (Session 32, PR #3572)  
**Supersedes:** N/A  
**Related:** `src/codex/auth/user_store.py`, `src/codex/auth/user_repository.py`

---

## Context

`UserStore` (introduced in PR #3571, Session 26) is an in-memory, thread-safe
(RLock-protected) user store.  It works correctly for single-process
deployments but has two hard limitations:

1. **No persistence** — all users are lost on process restart.
2. **No cross-process sharing** — multiple uvicorn workers (e.g.
   `uvicorn --workers 4`) each maintain an independent copy of the user table,
   so a user created in worker A is invisible to worker B.

Production deployments require durable, shared storage.

---

## Decision

Introduce a `UserRepository` abstract base class (ABC) with two concrete
implementations shipped in this PR:

| Backend | Class | Env value | Use case |
|---------|-------|-----------|----------|
| In-memory dict | `InMemoryUserRepository` | `memory` (default) | Development, tests, single-process |
| SQLite file | `SQLiteUserRepository` | `sqlite` | Dev/staging, single-node production |

`UserStore` becomes a **thin façade** that:
- Selects the backend from `CODEX_USERSTORE_BACKEND` at construction time.
- Delegates all storage operations to the repository.
- Retains its full public API (no breaking changes).

A future PR may add a `PostgresUserRepository` for true multi-node
deployments (beyond the scope of this ADR).

---

## Implementation Plan

### Phase 1 (this PR — 2026-03-13)

1. **`src/codex/auth/user_repository.py`** — `UserRepository` ABC with 7
   abstract methods: `create`, `update`, `delete`, `get_by_id`,
   `get_by_username`, `get_by_email`, `list_all`.

2. **`src/codex/auth/in_memory_user_repository.py`** — Direct replacement for
   the legacy `_users: dict` internals.  Thread-safe via `threading.RLock`.

3. **`src/codex/auth/sqlite_user_repository.py`** — SQLite backend with:
   - WAL mode for concurrent reads.
   - Full CRUD via parameterised queries (no SQL injection).
   - Indexes on `username` and `email` for O(1) lookups.
   - JSON-serialised `roles` column.

4. **`src/codex/auth/user_store.py`** — Refactored to delegate all I/O to the
   selected repository.  Legacy `_lock` attribute preserved for
   backward-compatibility.

5. **`scripts/migrations/001_userstore_to_sqlite.py`** — One-shot migration
   script: export in-memory snapshot → import to SQLite → verify.

6. **`.env.example`** — Documents `CODEX_USERSTORE_BACKEND` and
   `CODEX_USERSTORE_DB_PATH`.

### Phase 2 (future PR)

- `PostgresUserRepository` using `asyncpg` or `psycopg3` for multi-node
  deployments.
- Connection pooling.
- Schema migrations via Alembic.

---

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `CODEX_USERSTORE_BACKEND` | `memory` | Backend selector: `memory` or `sqlite` |
| `CODEX_USERSTORE_DB_PATH` | `codex_users.db` | SQLite database file path (only when `CODEX_USERSTORE_BACKEND=sqlite`) |

---

## Consequences

### Positive

- **Durability** — Users survive process restarts when SQLite is enabled.
- **No breaking changes** — All existing tests pass unchanged; `UserStore`
  public API is identical.
- **Testability** — `SQLiteUserRepository(":memory:")` provides fast, isolated
  in-process tests without a real file.
- **Extensible** — New backends only need to implement the 7-method ABC.

### Negative / Risks

- **SQLite single-writer** — WAL mode allows concurrent reads but only one
  write at a time.  Under heavy write load, use PostgreSQL (Phase 2).
- **Schema migrations** — Adding columns to the `users` table requires manual
  `ALTER TABLE` or a migration tool.  Covered in Phase 2 (Alembic).
- **No connection pooling** — Each call opens/closes a connection.  Acceptable
  for typical auth workloads; revisit if profiling reveals it as a bottleneck.

---

## Alternatives Considered

### 1. Keep in-memory store + periodic snapshot

Simple, but still loses writes between snapshots and does not solve the
multi-worker problem.

### 2. Direct PostgreSQL dependency

Adds `psycopg3`/`asyncpg` as a mandatory runtime dependency and requires a
running Postgres for development.  Higher operational overhead than SQLite.
Deferred to Phase 2.

### 3. Redis

Good for session data but not an authoritative user store (no relational
integrity, persistence requires tuning).  Not appropriate here.

---

## References

- PR #3571, Session 26: `UserStore` thread-safety (RLock)
- PR #3572, Session 32: This implementation
- `src/codex/auth/user_store.py`
- `src/codex/auth/user_repository.py`
- `src/codex/auth/sqlite_user_repository.py`
- `scripts/migrations/001_userstore_to_sqlite.py`
