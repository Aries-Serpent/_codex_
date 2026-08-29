"""
Smoke tests for scripts/migrations/001_userstore_to_sqlite.py

Covers:
- Round-trip migration of 10 users through the migration script
- Idempotent re-import (no duplicates on second run)
- Verification step
- Missing snapshot file → exit code 2
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

# Load migration module (filename starts with a digit — not a valid package name)
_MIGRATION_FILE = (
    Path(__file__).resolve().parent.parent.parent
    / "scripts"
    / "migrations"
    / "001_userstore_to_sqlite.py"
)
_spec = importlib.util.spec_from_file_location("migration_001", _MIGRATION_FILE)
assert _spec is not None and _spec.loader is not None, "_spec must be initialized"
_migration = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_migration)  # type: ignore[attr-defined]

export_userstore_snapshot = _migration.export_userstore_snapshot
import_snapshot_to_sqlite = _migration.import_snapshot_to_sqlite
verify_migration = _migration.verify_migration

from codex.auth.sqlite_user_repository import SQLiteUserRepository
from codex.auth.user_store import UserStore


def _populate_store(n: int = 10) -> UserStore:
    """Create a UserStore with *n* test users."""
    store = UserStore()
    for i in range(n):
        store.create_user(
            username=f"migtest_user{i}",
            email=f"migtest_user{i}@example.com",
            password=f"Password{i}!",
            roles=["user"],
            display_name=f"Migration Test User {i}",
        )
    return store


class TestMigration001RoundTrip:
    def test_export_produces_json_with_all_users(self, tmp_path: Path) -> None:
        store = _populate_store(10)
        snapshot = tmp_path / "snapshot.json"
        n = export_userstore_snapshot(store, snapshot)
        assert n == 10, "n is not valid"
        data = json.loads(snapshot.read_text())
        assert data["version"] == 1, "Data must not be empty"
        assert len(data["users"]) == 10, "Collection must not be empty"
        # password_hash must be included for migration
        for record in data["users"]:
            assert "password_hash" in record, "Condition must be true"
            assert ":" in record["password_hash"], "Condition must be true"

    def test_import_to_sqlite(self, tmp_path: Path) -> None:
        store = _populate_store(10)
        snapshot = tmp_path / "snapshot.json"
        export_userstore_snapshot(store, snapshot)

        db_path = str(tmp_path / "users.db")
        imported = import_snapshot_to_sqlite(snapshot, db_path)
        assert imported == 10, "imported is not valid"

        repo = SQLiteUserRepository(db_path)
        all_users = repo.list_all()
        assert len(all_users) == 10, "All_users must not be empty"

    def test_imported_users_match_original(self, tmp_path: Path) -> None:
        store = _populate_store(5)
        original = store.list_users(include_inactive=True)

        snapshot = tmp_path / "snapshot.json"
        export_userstore_snapshot(store, snapshot)

        db_path = str(tmp_path / "users.db")
        import_snapshot_to_sqlite(snapshot, db_path)

        repo = SQLiteUserRepository(db_path)
        for orig_user in original:
            migrated = repo.get_by_id(orig_user.user_id)
            assert migrated is not None, f"User {orig_user.username} missing after migration"
            assert migrated.username == orig_user.username, "username is not valid"
            assert migrated.email == orig_user.email, "email is not valid"
            assert migrated.password_hash == orig_user.password_hash, "password_hash is not valid"
            assert migrated.roles == orig_user.roles, "roles is not valid"
            assert migrated.display_name == orig_user.display_name, "display_name is not valid"

    def test_verify_migration_passes(self, tmp_path: Path) -> None:
        store = _populate_store(10)
        snapshot = tmp_path / "snapshot.json"
        export_userstore_snapshot(store, snapshot)

        db_path = str(tmp_path / "users.db")
        import_snapshot_to_sqlite(snapshot, db_path)

        assert verify_migration(snapshot, db_path) is True

    def test_verify_migration_fails_when_user_missing(self, tmp_path: Path) -> None:
        store = _populate_store(3)
        snapshot = tmp_path / "snapshot.json"
        export_userstore_snapshot(store, snapshot)

        # Empty DB — no users imported
        db_path = str(tmp_path / "empty.db")
        assert verify_migration(snapshot, db_path) is False

    def test_idempotent_reimport(self, tmp_path: Path) -> None:
        """Running import twice should not duplicate records."""
        store = _populate_store(5)
        snapshot = tmp_path / "snapshot.json"
        export_userstore_snapshot(store, snapshot)

        db_path = str(tmp_path / "users.db")
        first = import_snapshot_to_sqlite(snapshot, db_path)
        second = import_snapshot_to_sqlite(snapshot, db_path)

        assert first == 5, "first is not valid"
        assert second == 0, "second is not valid"

        repo = SQLiteUserRepository(db_path)
        assert len(repo.list_all()) == 5, "Collection must not be empty"

    def test_export_includes_inactive_users(self, tmp_path: Path) -> None:
        store = _populate_store(2)
        users = store.list_users(include_inactive=True)
        store.deactivate_user(users[0].user_id)

        snapshot = tmp_path / "snapshot.json"
        n = export_userstore_snapshot(store, snapshot)
        assert n == 2, "n is not valid"

        data = json.loads(snapshot.read_text())
        inactive = [r for r in data["users"] if not r["is_active"]]
        assert len(inactive) == 1, "Inactive must not be empty"

    def test_main_missing_snapshot_returns_exit_code_2(self, tmp_path: Path) -> None:
        """main() with --import pointing to a non-existent file exits with code 2."""
        missing = str(tmp_path / "does_not_exist.json")
        result = _migration.main(["--import", missing, "--db-path", str(tmp_path / "out.db")])
        assert result == 2, "Result must not be empty"
