"""
Tests for SQLiteUserRepository — all CRUD + thread-safety operations.
"""

from __future__ import annotations

import sqlite3
import threading
import time
from pathlib import Path

import pytest

import codex.auth.sqlite_user_repository as repository_module
from codex.auth.sqlite_user_repository import SQLiteUserRepository
from codex.auth.user_store import User


def _make_user(
    username: str = "alice", # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
    email: str = "alice@example.com",
    user_id: str | None = None,
) -> User:
    return User(
        user_id=user_id or f"id-{username}",
        username=username,
        email=email,
        password_hash="salt:hash",
    )


@pytest.fixture()
def repo() -> SQLiteUserRepository:
    """Fresh in-memory SQLiteUserRepository for each test."""
    return SQLiteUserRepository(":memory:")


class TestSQLiteUserRepositoryCreate:
    def test_create_and_get_by_id(self, repo: SQLiteUserRepository) -> None:
        user = _make_user()
        repo.create(user)
        found = repo.get_by_id(user.user_id)
        assert found is not None, "found must be initialized"
        assert found.user_id == user.user_id, "user_id is not valid"
        assert found.username == user.username, "username is not valid"

    def test_create_returns_user(self, repo: SQLiteUserRepository) -> None:
        user = _make_user()
        returned = repo.create(user)
        assert returned.user_id == user.user_id, "user_id is not valid"

    def test_create_duplicate_username_raises(self, repo: SQLiteUserRepository) -> None:
        repo.create(_make_user("bob", "bob@example.com", "id-bob"))
        with pytest.raises(ValueError, match="already taken"):
            repo.create(_make_user("bob", "bob2@example.com", "id-bob2"))

    def test_create_duplicate_email_raises(self, repo: SQLiteUserRepository) -> None:
        repo.create(_make_user("carol", "carol@example.com", "id-carol"))
        with pytest.raises(ValueError, match="already registered"):
            repo.create(_make_user("carol2", "carol@example.com", "id-carol2"))

    def test_create_persists_all_fields(self, repo: SQLiteUserRepository) -> None:
        user = User(
            user_id="uid-full",
            username="dave",
            email="dave@example.com",
            password_hash="s:h",
            is_active=False,
            roles=["admin", "user"],
            display_name="Dave Smith",
            created_at=1_700_000_000.0,
            updated_at=1_700_000_001.0,
        )
        repo.create(user)
        found = repo.get_by_id("uid-full")
        assert found is not None, "found must be initialized"
        assert found.is_active is False, "is_active is not valid"
        assert found.roles == ["admin", "user"]
        assert found.display_name == "Dave Smith", "display_name is not valid"
        assert found.created_at == pytest.approx(1_700_000_000.0), "created_at is not valid"


class TestSQLiteUserRepositoryReadQueries:
    def test_get_by_username(self, repo: SQLiteUserRepository) -> None:
        user = _make_user("eve", "eve@example.com")
        repo.create(user)
        found = repo.get_by_username("eve")
        assert found is not None, "found must be initialized"
        assert found.email == "eve@example.com", "email is not valid"

    def test_get_by_username_missing(self, repo: SQLiteUserRepository) -> None:
        assert repo.get_by_username("nobody") is None, "Condition must be true"

    def test_get_by_email(self, repo: SQLiteUserRepository) -> None:
        user = _make_user("frank", "frank@example.com")
        repo.create(user)
        found = repo.get_by_email("frank@example.com")
        assert found is not None, "found must be initialized"
        assert found.username == "frank", "username is not valid"

    def test_get_by_email_case_insensitive(self, repo: SQLiteUserRepository) -> None:
        user = _make_user("grace", "grace@example.com")
        repo.create(user)
        found = repo.get_by_email("GRACE@EXAMPLE.COM")
        assert found is not None, "found must be initialized"

    def test_get_by_id_missing(self, repo: SQLiteUserRepository) -> None:
        assert repo.get_by_id("nonexistent") is None, "Condition must be true"

    def test_list_all_returns_all_users(self, repo: SQLiteUserRepository) -> None:
        repo.create(_make_user("henry", "henry@example.com", "id-henry"))
        repo.create(_make_user("iris", "iris@example.com", "id-iris"))
        users = repo.list_all()
        ids = {u.user_id for u in users}
        assert "id-henry" in ids, "Condition must be true"
        assert "id-iris" in ids, "Condition must be true"

    def test_list_all_empty(self, repo: SQLiteUserRepository) -> None:
        assert repo.list_all() == [], "Condition must be true"

    def test_list_all_includes_inactive(self, repo: SQLiteUserRepository) -> None:
        inactive = User(
            user_id="id-inactive",
            username="jan",
            email="jan@example.com",
            password_hash="s:h",
            is_active=False,
        )
        repo.create(inactive)
        users = repo.list_all()
        assert any(u.user_id == "id-inactive" for u in users), "user_id is not valid"


class TestSQLiteUserRepositoryUpdate:
    def test_update_password_hash(self, repo: SQLiteUserRepository) -> None:
        user = _make_user("ken", "ken@example.com")
        repo.create(user)
        user.password_hash = "newsalt:newhash"
        user.updated_at = time.time()
        repo.update(user)
        found = repo.get_by_id(user.user_id)
        assert found is not None, "found must be initialized"
        assert found.password_hash == "newsalt:newhash", "password_hash is not valid"

    def test_update_deactivates_user(self, repo: SQLiteUserRepository) -> None:
        user = _make_user("leo", "leo@example.com")
        repo.create(user)
        user.is_active = False
        repo.update(user)
        found = repo.get_by_id(user.user_id)
        assert found is not None, "found must be initialized"
        assert found.is_active is False, "is_active is not valid"

    def test_update_nonexistent_raises(self, repo: SQLiteUserRepository) -> None:
        ghost = _make_user("ghost", "ghost@example.com", "id-ghost")
        with pytest.raises(KeyError):
            repo.update(ghost)


class TestSQLiteUserRepositoryDelete:
    def test_delete_user(self, repo: SQLiteUserRepository) -> None:
        user = _make_user("mia", "mia@example.com")
        repo.create(user)
        repo.delete(user.user_id)
        assert repo.get_by_id(user.user_id) is None, "Condition must be true"

    def test_delete_nonexistent_raises(self, repo: SQLiteUserRepository) -> None:
        with pytest.raises(KeyError):
            repo.delete("ghost-id")


class TestSQLiteUserRepositoryThreadSafety:
    """Concurrent write test — 2 threads sharing the same in-memory DB."""

    def test_concurrent_creates(self, repo: SQLiteUserRepository) -> None:
        errors: list[Exception] = []

        def worker(idx: int) -> None:
            try:
                user = User(
                    user_id=f"thread-{idx}",
                    username=f"user{idx}",
                    email=f"user{idx}@example.com",
                    password_hash="s:h",
                )
                repo.create(user)
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert errors == [], f"Thread errors: {errors}"
        assert len(repo.list_all()) == 20, "Collection must not be empty"

    def test_concurrent_reads_and_writes(self, repo: SQLiteUserRepository) -> None:
        """Read-while-write should not raise or deadlock."""
        # Seed one user first
        repo.create(_make_user("seed", "seed@example.com", "id-seed"))

        errors: list[Exception] = []

        def writer(idx: int) -> None:
            try:
                user = User(
                    user_id=f"w-{idx}",
                    username=f"writer{idx}",
                    email=f"writer{idx}@example.com",
                    password_hash="s:h",
                )
                repo.create(user)
            except Exception as exc:
                errors.append(exc)

        def reader() -> None:
            try:
                repo.list_all()
                repo.get_by_username("seed")
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=writer, args=(i,)) for i in range(10)] + [
            threading.Thread(target=reader) for _ in range(10)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert errors == [], f"Thread errors: {errors}"


class TestSQLiteUserRepositoryTwoInstances:
    """Two SQLiteUserRepository instances sharing the same SQLite file."""

    def test_shared_file_visibility(self, tmp_path: "Path") -> None:
        db_file = str(tmp_path / "shared_users.db")
        repo_a = SQLiteUserRepository(db_file)
        repo_b = SQLiteUserRepository(db_file)

        user = _make_user("shared", "shared@example.com")
        repo_a.create(user)

        # repo_b should see the user written by repo_a
        found = repo_b.get_by_id(user.user_id)
        assert found is not None, "found must be initialized"
        assert found.username == "shared", "username is not valid"


class _Clock:
    """Deterministic monotonic clock advanced only by sleeps and busy waits."""

    def __init__(self) -> None:
        self.now = 0.0
        self.sleeps: list[float] = []

    def monotonic(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds


class _ScriptedConnection:
    """Connection whose WAL pragma fails as scripted before succeeding.

    Each scripted failure is ``(message, cost)``. A ``None`` cost models SQLite's
    busy handler: the attempt blocks for the whole current busy timeout first.
    """

    def __init__(self, failures: list[tuple[str, float | None]], clock: _Clock) -> None:
        self.failures = list(failures)
        self.clock = clock
        self.busy_timeout_ms = 0
        self.statements: list[str] = []
        self.closed = False

    def execute(self, sql: str) -> None:
        self.statements.append(sql)
        if sql.startswith("PRAGMA busy_timeout="):
            self.busy_timeout_ms = int(sql.partition("=")[2])
        elif sql == "PRAGMA journal_mode=WAL" and self.failures:
            message, cost = self.failures.pop(0)
            self.clock.now += self.busy_timeout_ms / 1000 if cost is None else cost
            raise sqlite3.OperationalError(message)

    def close(self) -> None:
        self.closed = True


def _open_connection() -> sqlite3.Connection:
    repository = SQLiteUserRepository.__new__(SQLiteUserRepository)
    repository._db_path = "unused.db"
    return repository._make_conn()


TIMEOUT = repository_module._SQLITE_LOCK_RETRY_TIMEOUT_SECONDS
WAL = "PRAGMA journal_mode=WAL"


class TestSQLiteUserRepositoryWALInitialization:
    @pytest.fixture()
    def scripted(self, monkeypatch: pytest.MonkeyPatch):
        clock = _Clock()
        monkeypatch.setattr(repository_module.time, "monotonic", clock.monotonic)
        monkeypatch.setattr(repository_module.time, "sleep", clock.sleep)

        def install(failures: list[tuple[str, float | None]]) -> _ScriptedConnection:
            conn = _ScriptedConnection(failures, clock)

            def connect(*args, **kwargs):
                conn.busy_timeout_ms = int(kwargs["timeout"] * 1000)
                return conn

            monkeypatch.setattr(repository_module.sqlite3, "connect", connect)
            return conn

        return install, clock

    def test_retries_locked_wal_pragma_until_it_succeeds(self, scripted) -> None:
        install, clock = scripted
        conn = install([("database is locked", 0.0)] * 5)
        assert _open_connection() is conn
        assert conn.statements.count(WAL) == 6
        assert clock.sleeps == [0.01, 0.02, 0.04, 0.08, 0.1]
        assert conn.statements[-2:] == ["PRAGMA busy_timeout=30000", "PRAGMA foreign_keys=ON"]
        assert not conn.closed

    def test_non_lock_error_is_raised_and_closes_connection(self, scripted) -> None:
        install, clock = scripted
        conn = install([("disk I/O error", 0.0)])
        with pytest.raises(sqlite3.OperationalError, match="disk I/O error"):
            _open_connection()
        assert conn.closed
        assert clock.sleeps == []

    def test_busy_wait_exhausting_the_deadline_raises_and_closes(self, scripted) -> None:
        install, clock = scripted
        conn = install([("database is locked", None)] * 100)
        with pytest.raises(sqlite3.OperationalError, match="locked"):
            _open_connection()
        assert conn.closed
        assert conn.statements == ["PRAGMA busy_timeout=30000", WAL]
        assert clock.now == pytest.approx(TIMEOUT)

    def test_late_retry_busy_wait_is_bounded_by_the_deadline(self, scripted) -> None:
        install, clock = scripted
        conn = install(
            [("database is locked", TIMEOUT - 0.5)] + [("database is locked", None)] * 100
        )
        with pytest.raises(sqlite3.OperationalError, match="locked"):
            _open_connection()
        assert conn.closed
        assert clock.now <= TIMEOUT + 1e-9

    def test_sub_millisecond_remainder_never_busy_waits_past_deadline(self, scripted) -> None:
        install, clock = scripted
        # The first backoff (10 ms) leaves 0.5 ms, which truncates to a 0 ms busy timeout.
        conn = install(
            [("database is locked", TIMEOUT - 0.0105)] + [("database is locked", None)] * 100
        )
        with pytest.raises(sqlite3.OperationalError, match="locked"):
            _open_connection()
        assert conn.closed
        assert "PRAGMA busy_timeout=0" in conn.statements
        assert clock.now <= TIMEOUT + 1e-9

    def test_final_backoff_is_clamped_to_the_deadline(self, scripted) -> None:
        install, clock = scripted
        install([("database is locked", TIMEOUT - 0.004)] + [("database is locked", None)] * 100)
        with pytest.raises(sqlite3.OperationalError, match="locked"):
            _open_connection()
        assert clock.sleeps == [pytest.approx(0.004)]

    def test_real_exclusive_lock_is_bounded_by_the_deadline(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db_path = tmp_path / "locked.db"
        holder = sqlite3.connect(db_path, isolation_level=None)
        holder.execute("CREATE TABLE t (x INTEGER)")
        holder.execute("BEGIN EXCLUSIVE")
        monkeypatch.setattr(repository_module, "_SQLITE_LOCK_RETRY_TIMEOUT_SECONDS", 0.3)
        repository = SQLiteUserRepository.__new__(SQLiteUserRepository)
        repository._db_path = str(db_path)
        started = time.monotonic()
        try:
            with pytest.raises(sqlite3.OperationalError, match="locked"):
                repository._make_conn()
        finally:
            holder.rollback()
            holder.close()
        assert time.monotonic() - started < 5
