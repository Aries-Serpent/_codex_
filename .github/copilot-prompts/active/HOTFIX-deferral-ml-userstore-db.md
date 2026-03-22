# HOTFIX Follow-Up Prompt — Separate PR: Deferral Scanner ML + UserStore Persistence

**Generated:** 2026-03-13 — Session 31 (PR #3571)  
**Priority:** 🟡 P2 (must complete before Phase 4 launch)  
**Target Branch:** `copilot/hotfix-deferral-ml-userstore-db`  
**Blocks:** Phase 4 Enhancement PoCs (phase4_DESIGN.md)

---

## 🎯 Scope

Two items documented as "future scope" in PR #3571 now have formal design requirements. This prompt drives a **dedicated PR** (separate from #3571) to complete both work streams.

---

## Work Stream 1: scikit-learn/transformers Dependency Security Review

### Background
The deferral scanner (`scripts/ci/check_deferral_language.py`) uses regex pattern matching (18 categories). PR #3571 documented that ML-based intent detection would improve precision but requires a dependency security review before adding `scikit-learn` and/or `transformers` to the project.

### Required Tasks

#### 1.1 Dependency Vulnerability Scan
```bash
# Run before adding any new dependency
gh-advisory-database check scikit-learn <version>
gh-advisory-database check transformers <version>
gh-advisory-database check torch <version>  # if not already pinned
```

#### 1.2 Version Pinning Analysis
- Identify current `scikit-learn` / `transformers` versions compatible with:
  - Python 3.12
  - Current `torch` pin in `pyproject.toml`
  - CI runner memory limits (ubuntu-latest: 7GB RAM)

#### 1.3 Offline-Mode Enforcement
- Transformers model must be bundled locally (no `from_pretrained` network call in CI)
- Acceptable approaches:
  - Lightweight TF-IDF vectorizer (scikit-learn only, no network) ← **preferred**
  - Distilled sentence-transformer cached in `.codex/models/` with SHA256 manifest
- Update `.codex/CODEBASE_AGENCY_POLICY.md` Network Safety section with offline-mode proof

#### 1.4 Implementation
```python
# Target: scripts/ci/check_deferral_language.py
# Add ML classifier as optional enhancement (regex fallback always present)
# Feature flag: DEFERRAL_SCANNER_ML=1 (off by default)

class DeferralMLClassifier:
    """Lightweight TF-IDF + LinearSVC classifier for intent detection.

    Falls back to regex patterns if model not available.
    Trained on 200 labeled examples in .codex/training_data/deferral_examples.jsonl
    """
    ...
```

#### 1.5 Training Data
- Create `.codex/training_data/deferral_examples.jsonl` with ≥200 labeled examples
- 100 positive (deferral language), 100 negative (legitimate similar phrases)
- Include edge cases: "follow-up prompt", "future process", "related issue" (negative)
- Include violations: "future PR", "not my responsibility", "different branch" (positive)

#### 1.6 CI Gate Update
- Update `.github/workflows/deferral-language-gate.yml` to optionally run ML classifier
- ML classifier runs only when `DEFERRAL_SCANNER_ML=1` (opt-in, not default)

---

## Work Stream 2: UserStore Persistence Backend (DB Migration Strategy + Design Doc)

### Background
`src/codex/auth/user_store.py` currently uses an in-memory dict. Session 26 added thread-safety (RLock). Users are lost on process restart. Production deployments require durable storage.

### Required Tasks

#### 2.1 Design Document
Create `docs/arch/ADR-20260313-userstore-persistence.md`:

```markdown
# ADR-20260313: UserStore Persistence Backend

## Status: Proposed

## Context
UserStore is in-memory, thread-safe (RLock), single-process only.
Production multi-worker deployments (uvicorn --workers N) need shared storage.

## Decision
Implement SQLite backend (dev/single-node) + PostgreSQL backend (prod/multi-node)
with abstract `UserRepository` interface.

## Implementation Plan
...
```

#### 2.2 Abstract Interface
```python
# src/codex/auth/user_repository.py
from abc import ABC, abstractmethod
from codex.auth.models import User

class UserRepository(ABC):
    @abstractmethod
    def create(self, user: User) -> User: ...
    @abstractmethod
    def get_by_id(self, user_id: str) -> User | None: ...
    @abstractmethod
    def get_by_username(self, username: str) -> User | None: ...
    @abstractmethod
    def get_by_email(self, email: str) -> User | None: ...
    @abstractmethod
    def update(self, user: User) -> User: ...
    @abstractmethod
    def delete(self, user_id: str) -> None: ...
    @abstractmethod
    def list_all(self) -> list[User]: ...
```

#### 2.3 SQLite Backend
```python
# src/codex/auth/sqlite_user_repository.py
class SQLiteUserRepository(UserRepository):
    """Thread-safe SQLite backend for single-node deployments."""

    def __init__(self, db_path: str | Path = ":memory:") -> None:
        self._db_path = str(db_path)
        self._lock = threading.RLock()
        self._init_schema()

    def _init_schema(self) -> None:
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
```

#### 2.4 Migration Script
```python
# scripts/migrations/001_userstore_to_sqlite.py
"""One-shot migration: in-memory UserStore → SQLite UserRepository."""
```

#### 2.5 UserStore Backward Compatibility
- `UserStore` becomes a thin wrapper around `UserRepository`
- Default: `InMemoryUserRepository` (current behaviour preserved)
- Production: `SQLiteUserRepository` (set via `CODEX_USERSTORE_BACKEND=sqlite`)
- Thread-safety: `RLock` moves into each concrete repository

#### 2.6 Tests
- Unit tests for `SQLiteUserRepository` — all 8 CRUD operations
- Migration smoke test — round-trip 10 users through `001_userstore_to_sqlite.py`
- Multi-worker integration test — 2× `SQLiteUserRepository` sharing same SQLite file

---

## Acceptance Criteria

### Work Stream 1 (ML Deferral Scanner)
- [ ] `gh-advisory-database` scan passes for all new deps (0 HIGH/MEDIUM vulnerabilities)
- [ ] Classifier runs offline (no network requests in CI)
- [ ] Feature-flagged (`DEFERRAL_SCANNER_ML=1`) — regex always runs first
- [ ] ≥200 labeled training examples in `.codex/training_data/`
- [ ] Precision ≥0.95, Recall ≥0.90 on held-out test set (20% split)
- [ ] `ruff check` + `mypy` pass on new code
- [ ] `python scripts/ci/check_deferral_language.py --git-log` still exits 0

### Work Stream 2 (UserStore Persistence)
- [ ] ADR drafted at `docs/arch/ADR-20260313-userstore-persistence.md`
- [ ] `UserRepository` ABC committed to `src/codex/auth/user_repository.py`
- [ ] `SQLiteUserRepository` passes all CRUD + thread-safety tests
- [ ] Backward compatibility: existing tests still pass with `InMemoryUserRepository`
- [ ] Migration script tested end-to-end
- [ ] `CODEX_USERSTORE_BACKEND` env var documented in `.env.example`

---

## Activation

```bash
# Create the hotfix branch
git checkout -b copilot/hotfix-deferral-ml-userstore-db main

# Then post this prompt as a PR comment:
@copilot complete tasks in .github/copilot-prompts/active/HOTFIX-deferral-ml-userstore-db.md
```

---

## References
- PR #3571 Notes: "ML intent detection requires scikit-learn/transformers dep security review"
- PR #3571 Notes: "UserStore persistence requires DB migration strategy + design doc"
- `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` Sessions 26–31
- `src/codex/auth/user_store.py` — current in-memory implementation
- `scripts/ci/check_deferral_language.py` — current regex-only scanner
