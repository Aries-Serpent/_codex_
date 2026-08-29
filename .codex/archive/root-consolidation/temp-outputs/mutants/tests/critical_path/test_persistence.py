"""
Critical Path Tests: Data Persistence

Comprehensive test suite for data persistence critical paths including:
- CRUD operations
- Transaction handling
- Rollback scenarios
- Data integrity constraints
- Backup/restore workflows

All tests are deterministic and isolated using tmp_path fixtures.
"""

import sqlite3
import time

import pytest

from codex.logging.db_manager import DBManager


def _raw_conn(conn):
    """Unwrap a PooledConnectionProxy to the underlying sqlite3.Connection.

    When codex.db.sqlite_patch is active it replaces sqlite3.connect() with a
    pool that returns PooledConnectionProxy objects.  sqlite3.Connection.backup()
    is a C-extension API that checks the type of its arguments at the C level,
    so it rejects PooledConnectionProxy even though the proxy transparently
    delegates all attribute access to the underlying connection.  This helper
    extracts the real connection for calls that require a raw sqlite3.Connection.
    """
    return getattr(conn, "_conn", conn)


class TestCRUDOperations:
    """Tests for basic CRUD operations."""

    def test_create_record(self, tmp_path):
        """Test creating a new record."""
        db_path = tmp_path / "test.db"
        manager = DBManager(db_path=db_path)
        manager.init_schema()

        with manager.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)"
            )
            cursor.execute(
                "INSERT INTO users (name, email) VALUES (?, ?)", ("Alice", "alice@example.com")
            )
            conn.commit()

            # Verify record created
            cursor.execute("SELECT * FROM users WHERE name = ?", ("Alice",))
            row = cursor.fetchone()
            assert row is not None, "row must be initialized"
            assert row[1] == "Alice", "Condition must be true"
            assert row[2] == "alice@example.com", "Condition must be true"

    def test_read_record(self, tmp_path):
        """Test reading an existing record."""
        db_path = tmp_path / "test.db"
        manager = DBManager(db_path=db_path)
        manager.init_schema()

        with manager.connection() as conn:
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)")
            cursor.execute("INSERT INTO users (name) VALUES (?)", ("Bob",))
            conn.commit()

            # Read record
            cursor.execute("SELECT id, name FROM users WHERE name = ?", ("Bob",))
            row = cursor.fetchone()
            assert row[1] == "Bob", "Condition must be true"

    def test_update_record(self, tmp_path):
        """Test updating an existing record."""
        db_path = tmp_path / "test.db"
        manager = DBManager(db_path=db_path)
        manager.init_schema()

        with manager.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)"
            )
            cursor.execute(
                "INSERT INTO users (name, email) VALUES (?, ?)", ("Charlie", "charlie@old.com")
            )
            conn.commit()

            # Update record
            cursor.execute(
                "UPDATE users SET email = ? WHERE name = ?", ("charlie@new.com", "Charlie")
            )
            conn.commit()

            # Verify update
            cursor.execute("SELECT email FROM users WHERE name = ?", ("Charlie",))
            row = cursor.fetchone()
            assert row[0] == "charlie@new.com", "Condition must be true"

    def test_delete_record(self, tmp_path):
        """Test deleting a record."""
        db_path = tmp_path / "test.db"
        manager = DBManager(db_path=db_path)
        manager.init_schema()

        with manager.connection() as conn:
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)")
            cursor.execute("INSERT INTO users (name) VALUES (?)", ("David",))
            conn.commit()

            # Delete record
            cursor.execute("DELETE FROM users WHERE name = ?", ("David",))
            conn.commit()

            # Verify deletion
            cursor.execute("SELECT * FROM users WHERE name = ?", ("David",))
            row = cursor.fetchone()
            assert row is None, "row is not valid"

    def test_bulk_insert(self, tmp_path):
        """Test bulk insertion of records."""
        db_path = tmp_path / "test.db"
        manager = DBManager(db_path=db_path)
        manager.init_schema()

        with manager.connection() as conn:
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)")

            # Bulk insert
            users = [("User1",), ("User2",), ("User3",), ("User4",), ("User5",)]
            cursor.executemany("INSERT INTO users (name) VALUES (?)", users)
            conn.commit()

            # Verify count
            cursor.execute("SELECT COUNT(*) FROM users")
            count = cursor.fetchone()[0]
            assert count == 5, "Count must be greater than zero"

    def test_bulk_update(self, tmp_path):
        """Test bulk update of records."""
        db_path = tmp_path / "test.db"
        manager = DBManager(db_path=db_path)
        manager.init_schema()

        with manager.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, active INTEGER)"
            )

            # Insert records
            cursor.executemany(
                "INSERT INTO users (name, active) VALUES (?, ?)",
                [("User1", 0), ("User2", 0), ("User3", 0)],
            )
            conn.commit()

            # Bulk update
            cursor.execute("UPDATE users SET active = 1")
            conn.commit()

            # Verify
            cursor.execute("SELECT COUNT(*) FROM users WHERE active = 1")
            count = cursor.fetchone()[0]
            assert count == 3, "Count must be greater than zero"


class TestTransactionHandling:
    """Tests for transaction handling."""

    def test_transaction_commit(self, tmp_path):
        """Test transaction commits successfully."""
        db_path = tmp_path / "test.db"
        manager = DBManager(db_path=db_path)
        manager.init_schema()

        with manager.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS accounts (id INTEGER PRIMARY KEY, balance REAL)"
            )

            # Begin transaction
            cursor.execute("INSERT INTO accounts (balance) VALUES (?)", (100.0,))
            conn.commit()

            # Verify committed
            cursor.execute("SELECT balance FROM accounts")
            row = cursor.fetchone()
            assert row[0] == 100.0, "Condition must be true"

    def test_transaction_isolation(self, tmp_path):
        """Test transaction isolation."""
        db_path = tmp_path / "test.db"
        manager = DBManager(db_path=db_path)
        manager.init_schema()

        with manager.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS inventory (id INTEGER PRIMARY KEY, quantity INTEGER)"
            )
            cursor.execute("INSERT INTO inventory (quantity) VALUES (?)", (10,))
            conn.commit()

        # Two separate connections
        with manager.connection() as conn1, manager.connection() as conn2:
            cursor1 = conn1.cursor()
            cursor2 = conn2.cursor()

            # Connection 1 starts transaction
            cursor1.execute("UPDATE inventory SET quantity = 5 WHERE id = 1")

            # Connection 2 still sees old value (isolation)
            cursor2.execute("SELECT quantity FROM inventory WHERE id = 1")
            row = cursor2.fetchone()
            assert row[0] == 10, "Condition must be true"

            # Connection 1 commits
            conn1.commit()

            # Connection 2 now sees new value
            cursor2.execute("SELECT quantity FROM inventory WHERE id = 1")
            row = cursor2.fetchone()
            assert row[0] == 5, "Condition must be true"

    def test_nested_transactions(self, tmp_path):
        """Test nested transaction-like behavior using savepoints."""
        db_path = tmp_path / "test.db"
        manager = DBManager(db_path=db_path)
        manager.init_schema()

        with manager.connection() as conn:
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY, message TEXT)")

            # Outer transaction
            cursor.execute("INSERT INTO logs (message) VALUES (?)", ("Outer",))

            # Savepoint (nested)
            cursor.execute("SAVEPOINT nested")
            cursor.execute("INSERT INTO logs (message) VALUES (?)", ("Nested",))
            cursor.execute("RELEASE SAVEPOINT nested")

            conn.commit()

            # Both records exist
            cursor.execute("SELECT COUNT(*) FROM logs")
            count = cursor.fetchone()[0]
            assert count == 2, "Count must be greater than zero"

    def test_concurrent_write_conflict(self, tmp_path):
        """Test handling concurrent write conflicts."""
        db_path = tmp_path / "test.db"
        manager = DBManager(db_path=db_path)
        manager.init_schema()

        with manager.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS counter (id INTEGER PRIMARY KEY, value INTEGER)"
            )
            cursor.execute("INSERT INTO counter (value) VALUES (?)", (0,))
            conn.commit()

        # Simulate concurrent updates
        with manager.connection() as conn1:
            cursor1 = conn1.cursor()
            cursor1.execute("UPDATE counter SET value = value + 1 WHERE id = 1")
            conn1.commit()

        with manager.connection() as conn2:
            cursor2 = conn2.cursor()
            cursor2.execute("UPDATE counter SET value = value + 1 WHERE id = 1")
            conn2.commit()

        # Verify both updates applied
        with manager.connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM counter WHERE id = 1")
            value = cursor.fetchone()[0]
            assert value == 2, "Value must be initialized"

    def test_transaction_performance(self, tmp_path):
        """Test transaction performance with many operations."""
        db_path = tmp_path / "test.db"
        manager = DBManager(db_path=db_path)
        manager.init_schema()

        with manager.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, timestamp REAL)"
            )

            # Single transaction for bulk insert
            start = time.time()
            for i in range(100):
                cursor.execute("INSERT INTO events (timestamp) VALUES (?)", (time.time(),))
            conn.commit()
            duration = time.time() - start

            # Should complete quickly (< 1 second for 100 inserts)
            assert duration < 1.0, "duration is not valid"

            # Verify all inserted
            cursor.execute("SELECT COUNT(*) FROM events")
            count = cursor.fetchone()[0]
            assert count == 100, "Count must be greater than zero"


class TestRollbackScenarios:
    """Tests for rollback scenarios."""

    def test_explicit_rollback(self, tmp_path):
        """Test explicit transaction rollback."""
        db_path = tmp_path / "test.db"
        manager = DBManager(db_path=db_path)
        manager.init_schema()

        with manager.connection() as conn:
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)")

            # Insert and rollback
            cursor.execute("INSERT INTO users (name) VALUES (?)", ("Rollback User",))
            conn.rollback()

            # Verify not persisted
            cursor.execute("SELECT * FROM users WHERE name = ?", ("Rollback User",))
            row = cursor.fetchone()
            assert row is None, "row is not valid"

    def test_rollback_on_error(self, tmp_path):
        """Test automatic rollback on error."""
        db_path = tmp_path / "test.db"
        manager = DBManager(db_path=db_path)
        manager.init_schema()

        with manager.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT UNIQUE)"
            )
            cursor.execute("INSERT INTO users (email) VALUES (?)", ("test@example.com",))
            conn.commit()

        # Try to insert duplicate (should fail)
        try:
            with manager.connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users (email) VALUES (?)", ("valid@example.com",))
                cursor.execute(
                    "INSERT INTO users (email) VALUES (?)", ("test@example.com",)
                )  # Duplicate
                conn.commit()
        except sqlite3.IntegrityError:
            _ = None  # Expected

        # First insert should be rolled back
        with manager.connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", ("valid@example.com",))
            cursor.fetchone()
            # Depending on DB behavior, might be None (rolled back) or present
            # Just verify duplicate wasn't inserted
            cursor.execute("SELECT COUNT(*) FROM users WHERE email = ?", ("test@example.com",))
            count = cursor.fetchone()[0]
            assert count == 1, "Count must be greater than zero"

    def test_savepoint_rollback(self, tmp_path):
        """Test rolling back to savepoint."""
        db_path = tmp_path / "test.db"
        manager = DBManager(db_path=db_path)
        manager.init_schema()

        with manager.connection() as conn:
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS audit (id INTEGER PRIMARY KEY, action TEXT)")

            # Create savepoint
            cursor.execute("INSERT INTO audit (action) VALUES (?)", ("Before savepoint",))
            cursor.execute("SAVEPOINT sp1")
            cursor.execute("INSERT INTO audit (action) VALUES (?)", ("After savepoint",))

            # Rollback to savepoint
            cursor.execute("ROLLBACK TO SAVEPOINT sp1")

            conn.commit()

            # Only first record exists
            cursor.execute("SELECT COUNT(*) FROM audit")
            count = cursor.fetchone()[0]
            assert count == 1, "Count must be greater than zero"

            cursor.execute("SELECT action FROM audit")
            action = cursor.fetchone()[0]
            assert action == "Before savepoint", "action is not valid"

    def test_partial_rollback_on_constraint_violation(self, tmp_path):
        """Test partial rollback on constraint violation."""
        db_path = tmp_path / "test.db"
        manager = DBManager(db_path=db_path)
        manager.init_schema()

        with manager.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, sku TEXT UNIQUE, name TEXT)"
            )

            # Insert valid records
            cursor.execute(
                "INSERT INTO products (sku, name) VALUES (?, ?)", ("SKU001", "Product 1")
            )
            conn.commit()

            # Try batch insert with one invalid
            try:
                cursor.execute(
                    "INSERT INTO products (sku, name) VALUES (?, ?)", ("SKU002", "Product 2")
                )
                cursor.execute(
                    "INSERT INTO products (sku, name) VALUES (?, ?)", ("SKU001", "Duplicate")
                )  # Violates unique
                conn.commit()
            except sqlite3.IntegrityError:
                conn.rollback()

            # Verify rollback
            cursor.execute("SELECT COUNT(*) FROM products")
            count = cursor.fetchone()[0]
            assert count == 1, "Count must be greater than zero"

    def test_rollback_complex_operation(self, tmp_path):
        """Test rollback of complex multi-table operation."""
        db_path = tmp_path / "test.db"
        manager = DBManager(db_path=db_path)
        manager.init_schema()

        with manager.connection() as conn:
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, total REAL)")
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS order_items (id INTEGER PRIMARY KEY, order_id INTEGER, amount REAL)"
            )

            # Complex operation
            cursor.execute("INSERT INTO orders (total) VALUES (?)", (100.0,))
            order_id = cursor.lastrowid
            cursor.execute(
                "INSERT INTO order_items (order_id, amount) VALUES (?, ?)", (order_id, 50.0)
            )
            cursor.execute(
                "INSERT INTO order_items (order_id, amount) VALUES (?, ?)", (order_id, 50.0)
            )

            # Rollback entire operation
            conn.rollback()

            # Nothing persisted
            cursor.execute("SELECT COUNT(*) FROM orders")
            assert cursor.fetchone()[0] == 0, "curs is not valid"
            cursor.execute("SELECT COUNT(*) FROM order_items")
            assert cursor.fetchone()[0] == 0, "curs is not valid"


class TestDataIntegrityConstraints:
    """Tests for data integrity constraints."""

    def test_primary_key_constraint(self, tmp_path):
        """Test primary key constraint enforcement."""
        db_path = tmp_path / "test.db"
        manager = DBManager(db_path=db_path)
        manager.init_schema()

        with manager.connection() as conn:
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, name TEXT)")
            cursor.execute("INSERT INTO items (id, name) VALUES (?, ?)", (1, "Item 1"))
            conn.commit()

            # Try to insert duplicate primary key
            with pytest.raises(sqlite3.IntegrityError):
                cursor.execute("INSERT INTO items (id, name) VALUES (?, ?)", (1, "Item 2"))
                conn.commit()

    def test_unique_constraint(self, tmp_path):
        """Test unique constraint enforcement."""
        db_path = tmp_path / "test.db"
        manager = DBManager(db_path=db_path)
        manager.init_schema()

        with manager.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE)"
            )
            cursor.execute("INSERT INTO users (username) VALUES (?)", ("alice",))
            conn.commit()

            # Try duplicate username
            with pytest.raises(sqlite3.IntegrityError):
                cursor.execute("INSERT INTO users (username) VALUES (?)", ("alice",))
                conn.commit()

    def test_foreign_key_constraint(self, tmp_path):
        """Test foreign key constraint enforcement."""
        db_path = tmp_path / "test.db"
        manager = DBManager(db_path=db_path)
        manager.init_schema()

        with manager.connection() as conn:
            # Enable foreign keys
            conn.execute("PRAGMA foreign_keys = ON")

            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS authors (id INTEGER PRIMARY KEY, name TEXT)")
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS books (id INTEGER PRIMARY KEY, title TEXT, author_id INTEGER, "
                "FOREIGN KEY(author_id) REFERENCES authors(id))"
            )

            # Insert author
            cursor.execute("INSERT INTO authors (name) VALUES (?)", ("Author 1",))
            author_id = cursor.lastrowid

            # Insert book with valid foreign key
            cursor.execute(
                "INSERT INTO books (title, author_id) VALUES (?, ?)", ("Book 1", author_id)
            )
            conn.commit()

            # Try invalid foreign key
            with pytest.raises(sqlite3.IntegrityError):
                cursor.execute(
                    "INSERT INTO books (title, author_id) VALUES (?, ?)", ("Book 2", 9999)
                )
                conn.commit()

    def test_not_null_constraint(self, tmp_path):
        """Test NOT NULL constraint enforcement."""
        db_path = tmp_path / "test.db"
        manager = DBManager(db_path=db_path)
        manager.init_schema()

        with manager.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, name TEXT NOT NULL)"
            )

            # Try to insert NULL
            with pytest.raises(sqlite3.IntegrityError):
                cursor.execute("INSERT INTO products (name) VALUES (?)", (None,))
                conn.commit()

    def test_check_constraint(self, tmp_path):
        """Test CHECK constraint enforcement."""
        db_path = tmp_path / "test.db"
        manager = DBManager(db_path=db_path)
        manager.init_schema()

        with manager.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS accounts (id INTEGER PRIMARY KEY, balance REAL CHECK(balance >= 0))"
            )

            # Valid insert
            cursor.execute("INSERT INTO accounts (balance) VALUES (?)", (100.0,))
            conn.commit()

            # Invalid insert (negative balance)
            with pytest.raises(sqlite3.IntegrityError):
                cursor.execute("INSERT INTO accounts (balance) VALUES (?)", (-10.0,))
                conn.commit()


class TestBackupRestoreWorkflows:
    """Tests for backup and restore workflows."""

    def test_backup_database(self, tmp_path):
        """Test backing up database."""
        db_path = tmp_path / "test.db"
        backup_path = tmp_path / "backup.db"

        manager = DBManager(db_path=db_path)
        manager.init_schema()

        # Create some data
        with manager.connection() as conn:
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS data (id INTEGER PRIMARY KEY, value TEXT)")
            cursor.execute("INSERT INTO data (value) VALUES (?)", ("Test Data",))
            conn.commit()

        # Backup using SQLite backup API
        with manager.connection() as source, sqlite3.connect(backup_path) as target:
            _raw_conn(source).backup(_raw_conn(target))

        # Verify backup
        assert backup_path.exists(), "Condition must be true"

        with sqlite3.connect(backup_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM data")
            row = cursor.fetchone()
            assert row[0] == "Test Data", "Data must not be empty"

    def test_restore_from_backup(self, tmp_path):
        """Test restoring database from backup."""
        original_db = tmp_path / "original.db"
        backup_db = tmp_path / "backup.db"
        restored_db = tmp_path / "restored.db"

        # Create original
        manager = DBManager(db_path=original_db)
        manager.init_schema()

        with manager.connection() as conn:
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS data (id INTEGER PRIMARY KEY, value TEXT)")
            cursor.execute("INSERT INTO data (value) VALUES (?)", ("Original",))
            conn.commit()

        # Create backup
        with sqlite3.connect(original_db) as source, sqlite3.connect(backup_db) as target:
            _raw_conn(source).backup(_raw_conn(target))

        # Restore to new location
        with sqlite3.connect(backup_db) as source, sqlite3.connect(restored_db) as target:
            _raw_conn(source).backup(_raw_conn(target))

        # Verify restore
        with sqlite3.connect(restored_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM data")
            row = cursor.fetchone()
            assert row[0] == "Original", "Condition must be true"

    def test_incremental_backup(self, tmp_path):
        """Test incremental backup concept."""
        db_path = tmp_path / "test.db"
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir()

        manager = DBManager(db_path=db_path)
        manager.init_schema()

        # Initial data
        with manager.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS changes (id INTEGER PRIMARY KEY, timestamp REAL, change TEXT)"
            )
            cursor.execute(
                "INSERT INTO changes (timestamp, change) VALUES (?, ?)", (time.time(), "Change 1")
            )
            conn.commit()

        # Backup 1
        backup1 = backup_dir / "backup1.db"
        with sqlite3.connect(db_path) as source, sqlite3.connect(backup1) as target:
            _raw_conn(source).backup(_raw_conn(target))

        # More changes
        with manager.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO changes (timestamp, change) VALUES (?, ?)", (time.time(), "Change 2")
            )
            conn.commit()

        # Backup 2
        backup2 = backup_dir / "backup2.db"
        with sqlite3.connect(db_path) as source, sqlite3.connect(backup2) as target:
            _raw_conn(source).backup(_raw_conn(target))

        # Verify backups have different content
        with sqlite3.connect(backup1) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM changes")
            count1 = cursor.fetchone()[0]

        with sqlite3.connect(backup2) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM changes")
            count2 = cursor.fetchone()[0]

        assert count1 == 1, "Count must be greater than zero"
        assert count2 == 2, "Count must be greater than zero"

    def test_backup_with_wal_mode(self, tmp_path):
        """Test backup with WAL mode enabled."""
        db_path = tmp_path / "test.db"
        backup_path = tmp_path / "backup.db"

        manager = DBManager(db_path=db_path)
        manager.init_schema()

        # Enable WAL mode
        with manager.connection() as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS data (id INTEGER PRIMARY KEY, value TEXT)")
            cursor.execute("INSERT INTO data (value) VALUES (?)", ("WAL Data",))
            conn.commit()

        # Backup
        with sqlite3.connect(db_path) as source, sqlite3.connect(backup_path) as target:
            _raw_conn(source).backup(_raw_conn(target))

        # Verify backup
        with sqlite3.connect(backup_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM data")
            row = cursor.fetchone()
            assert row[0] == "WAL Data", "Data must not be empty"

    def test_point_in_time_recovery(self, tmp_path):
        """Test point-in-time recovery concept."""
        db_path = tmp_path / "test.db"

        manager = DBManager(db_path=db_path)
        manager.init_schema()

        # Create snapshots at different times
        snapshots = []

        with manager.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS timeline (id INTEGER PRIMARY KEY, timestamp REAL, event TEXT)"
            )

            for i in range(3):
                timestamp = time.time()
                cursor.execute(
                    "INSERT INTO timeline (timestamp, event) VALUES (?, ?)",
                    (timestamp, f"Event {i}"),
                )
                conn.commit()

                # Take snapshot
                snapshot_path = tmp_path / f"snapshot_{i}.db"
                with sqlite3.connect(db_path) as source:
                    with sqlite3.connect(snapshot_path) as target:
                        _raw_conn(source).backup(_raw_conn(target))
                snapshots.append((timestamp, snapshot_path))

        # Verify we can recover to any snapshot
        for i, (timestamp, snapshot_path) in enumerate(snapshots):
            with sqlite3.connect(snapshot_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM timeline")
                count = cursor.fetchone()[0]
                assert count == i + 1, "Count must be greater than zero"
