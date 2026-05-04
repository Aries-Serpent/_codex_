#!/usr/bin/env python3
"""
scripts/migrations/001_userstore_to_sqlite.py
─────────────────────────────────────────────
One-shot migration: export users from an existing UserStore snapshot
(JSON file) into a SQLiteUserRepository.

Usage
-----
1. Export your current UserStore to JSON (if you have custom population
   logic, call ``export_userstore_snapshot()`` from your application code):

   python scripts/migrations/001_userstore_to_sqlite.py \\
       --export /tmp/users_snapshot.json

2. Import the JSON snapshot into a target SQLite database:

   python scripts/migrations/001_userstore_to_sqlite.py \\
       --import /tmp/users_snapshot.json \\
       --db-path /var/data/codex_users.db

3. Verify the migration:

   python scripts/migrations/001_userstore_to_sqlite.py \\
       --verify \\
       --import /tmp/users_snapshot.json \\
       --db-path /var/data/codex_users.db

Exit codes
----------
0  — success
1  — migration error
2  — usage / file error
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from codex.auth.user_store import User, UserStore

# Ensure the repo root is on the path when run from anywhere
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src"))

# Sentinel used when source records omit timestamps during migration.
# `0.0` (Unix epoch) is treated by consumers as "unknown timestamp".
# Unknown timestamp sentinel (Unix epoch, 0.0) used during migration when source timestamps are missing.
UNKNOWN_TIMESTAMP = 0.0


def _build_user_from_record(record: dict) -> User:
    """Reconstruct a :class:`User` from a snapshot record."""
    from codex.auth.user_store import User  # noqa: PLC0415

    is_active_raw = record.get("is_active")
    if is_active_raw is None:
        raise ValueError(
            f"record for user '{record.get('username', record.get('user_id', '?'))}'"
            " is missing required field 'is_active'; cannot migrate without an"
            " explicit value — update the source record and retry"
        )
    return User(
        user_id=record["user_id"],
        username=record["username"],
        email=record["email"],
        password_hash=record["password_hash"],
        is_active=bool(is_active_raw),
        roles=record.get("roles", ["user"]),
        display_name=record.get("display_name"),
        # Preserve data integrity during migration: if source timestamps are
        # missing, use an explicit "unknown" sentinel (Unix epoch 1970-01-01 00:00:00 UTC)
        # instead of fabricating the current time.
        created_at=record.get("created_at", UNKNOWN_TIMESTAMP),
        updated_at=record.get("updated_at", UNKNOWN_TIMESTAMP),
    )


def export_userstore_snapshot(store: UserStore, output_path: Path) -> int:
    """Export all users from *store* to a JSON snapshot file.

    Args:
        store: Populated :class:`~codex.auth.user_store.UserStore` instance.
        output_path: Destination file (will be overwritten).

    Returns:
        Number of users exported.
    """
    users = store.list_users(include_inactive=True)
    records = []
    for user in users:
        record = user.to_dict()
        # Include password_hash for migration purposes (not exposed by to_dict)
        record["password_hash"] = user.password_hash
        records.append(record)

    output_path.write_text(
        json.dumps(
            {"version": 1, "exported_at": time.time(), "users": records},
            indent=2,
        ),
        encoding="utf-8",
    )
    return len(records)


def import_snapshot_to_sqlite(snapshot_path: Path, db_path: str) -> int:
    """Import users from a JSON snapshot into a :class:`SQLiteUserRepository`.

    Existing records with the same ``user_id`` are skipped (idempotent).

    Args:
        snapshot_path: Path to a JSON snapshot produced by
            :func:`export_userstore_snapshot`.
        db_path: Target SQLite database file path.

    Returns:
        Number of users imported.
    """
    from codex.auth.sqlite_user_repository import SQLiteUserRepository  # noqa: PLC0415

    data = json.loads(snapshot_path.read_text(encoding="utf-8"))
    records = data.get("users", [])

    repo = SQLiteUserRepository(db_path)
    imported = 0
    skipped = 0

    for record in records:
        user = _build_user_from_record(record)
        # Check if already migrated (idempotent)
        existing = repo.get_by_id(user.user_id)
        if existing is not None:
            compared_fields = [
                "username",
                "email",
                "password_hash",
                "is_active",
                "roles",
                "display_name",
            ]
            differing_fields = [
                field
                for field in compared_fields
                if getattr(existing, field, None) != getattr(user, field, None)
            ]
            if differing_fields:
                print(
                    "  ⚠️  ID collision for "
                    f"user_id '{user.user_id}' (username '{user.username}'): "
                    f"existing record differs in fields: {', '.join(differing_fields)}",
                    file=sys.stderr,
                )
            skipped += 1
            continue
        try:
            repo.create(user)
            imported += 1
        except ValueError as exc:
            print(f"  ⚠️  Skipped user '{user.username}': {exc}", file=sys.stderr)
            skipped += 1

    print(f"  Imported: {imported}  Skipped (already exists): {skipped}")
    return imported


def verify_migration(snapshot_path: Path, db_path: str) -> bool:
    """Verify that all users in the snapshot are present in the SQLite DB.

    Args:
        snapshot_path: JSON snapshot file.
        db_path: SQLite database to verify against.

    Returns:
        ``True`` if all users are found, ``False`` otherwise.
    """
    from codex.auth.sqlite_user_repository import SQLiteUserRepository  # noqa: PLC0415

    data = json.loads(snapshot_path.read_text(encoding="utf-8"))
    records = data.get("users", [])
    repo = SQLiteUserRepository(db_path)
    missing = []

    for record in records:
        user = repo.get_by_id(record["user_id"])
        if user is None:
            missing.append(record["username"])

    if missing:
        print(f"  ❌ Missing users in SQLite: {missing}", file=sys.stderr)
        return False

    print(f"  ✅ All {len(records)} users verified in SQLite database.")
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Migrate UserStore data to SQLite (001_userstore_to_sqlite)"
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--export",
        metavar="FILE",
        help="Export users from CODEX_USERSTORE_* env to a JSON snapshot file",
    )
    mode.add_argument(
        "--import",
        dest="import_file",
        metavar="FILE",
        help="Import a JSON snapshot into the target SQLite database",
    )
    parser.add_argument(
        "--db-path",
        default="codex_users.db",
        help="Target SQLite database path (default: codex_users.db)",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="After --import, verify all users are present in SQLite",
    )
    args = parser.parse_args(argv)

    if args.export:
        # Export from the current live UserStore (uses env-configured backend)
        from codex.auth.user_store import UserStore  # noqa: PLC0415

        store = UserStore()
        output = Path(args.export)
        print(f"Exporting users to {output} …")
        n = export_userstore_snapshot(store, output)
        print(f"✅ Exported {n} user(s) to {output}")
        return 0

    if args.import_file:
        source = Path(args.import_file)
        if not source.exists():
            print(f"ERROR: Snapshot file not found: {source}", file=sys.stderr)
            return 2
        print(f"Importing from {source} → {args.db_path} …")
        try:
            import_snapshot_to_sqlite(source, args.db_path)
        except Exception as exc:  # noqa: BLE001
            print(f"ERROR during import: {exc}", file=sys.stderr)
            return 1

        if args.verify:
            print("Verifying migration …")
            ok = verify_migration(source, args.db_path)
            return 0 if ok else 1

        print("✅ Import complete.")
        return 0

    return 2  # unreachable, but satisfies type checker


if __name__ == "__main__":
    sys.exit(main())
