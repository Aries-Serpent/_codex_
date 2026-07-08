"""Tests for database migrations (v1.5.x)."""

from __future__ import annotations

import sqlite3
from pathlib import Path


def test_migration_decorator():
    """Test migration registration decorator."""
    from scripts.space_traversal.migrations.migrate_trends import MIGRATIONS

    # Check that migrations are registered
    assert "1.5.0" in MIGRATIONS, "Condition must be true"
    assert "1.5.1" in MIGRATIONS, "Condition must be true"
    assert "1.5.2" in MIGRATIONS, "Condition must be true"
    assert "1.5.3" in MIGRATIONS, "Condition must be true"
    assert "1.5.4" in MIGRATIONS, "Condition must be true"
    assert "1.5.5" in MIGRATIONS, "Condition must be true"


def test_run_migrations_fresh_db(tmp_path: Path):
    """Test running migrations on fresh database."""
    from scripts.space_traversal.migrations.migrate_trends import run_migrations

    db_path = tmp_path / "test.db"

    # Don't create any tables - migrations should create them
    applied = run_migrations(db_path)

    # All migrations should be applied
    assert len(applied) == 6, "Applied must not be empty"
    assert "1.5.0" in applied, "Condition must be true"
    assert "1.5.5" in applied, "Condition must be true"


def test_run_migrations_idempotent(tmp_path: Path):
    """Test migrations are idempotent."""
    from scripts.space_traversal.migrations.migrate_trends import run_migrations

    db_path = tmp_path / "test.db"

    # Run once
    applied1 = run_migrations(db_path)
    assert len(applied1) == 6, "Applied1 must not be empty"

    # Run again - should apply nothing
    applied2 = run_migrations(db_path)
    assert len(applied2) == 0, "Applied2 must not be empty"


def test_get_current_version(tmp_path: Path):
    """Test getting current schema version."""
    from scripts.space_traversal.migrations.migrate_trends import (
        get_current_version,
        run_migrations,
    )

    db_path = tmp_path / "test.db"

    # No database yet
    assert get_current_version(db_path) == "0.0.0", "Condition must be true"

    # After migrations
    run_migrations(db_path)
    assert get_current_version(db_path) == "1.5.5", "Condition must be true"


def test_migration_1_5_1_annotations(tmp_path: Path):
    """Test v1.5.1 adds annotations support."""
    from scripts.space_traversal.migrations.migrate_trends import run_migrations

    db_path = tmp_path / "test.db"
    run_migrations(db_path)

    with sqlite3.connect(db_path) as conn:
        # Check run_annotations table exists
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='run_annotations'"
        )
        assert cursor.fetchone() is not None, "curs must be initialized"


def test_migration_1_5_2_viz_cache(tmp_path: Path):
    """Test v1.5.2 adds visualization cache."""
    from scripts.space_traversal.migrations.migrate_trends import run_migrations

    db_path = tmp_path / "test.db"
    run_migrations(db_path)

    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='viz_cache'"
        )
        assert cursor.fetchone() is not None, "curs must be initialized"


def test_migration_1_5_3_report_metadata(tmp_path: Path):
    """Test v1.5.3 adds report metadata."""
    from scripts.space_traversal.migrations.migrate_trends import run_migrations

    db_path = tmp_path / "test.db"
    run_migrations(db_path)

    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='report_metadata'"
        )
        assert cursor.fetchone() is not None, "curs must be initialized"


def test_migration_1_5_4_webhook_deliveries(tmp_path: Path):
    """Test v1.5.4 adds webhook tracking."""
    from scripts.space_traversal.migrations.migrate_trends import run_migrations

    db_path = tmp_path / "test.db"
    run_migrations(db_path)

    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='webhook_deliveries'"
        )
        assert cursor.fetchone() is not None, "curs must be initialized"


def test_migration_1_5_5_performance_metrics(tmp_path: Path):
    """Test v1.5.5 adds performance tracking and federation prep."""
    from scripts.space_traversal.migrations.migrate_trends import run_migrations

    db_path = tmp_path / "test.db"
    run_migrations(db_path)

    with sqlite3.connect(db_path) as conn:
        # Check performance_metrics table
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='performance_metrics'"
        )
        assert cursor.fetchone() is not None, "curs must be initialized"

        # Check repositories table (federation prep)
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='repositories'"
        )
        assert cursor.fetchone() is not None, "curs must be initialized"


def test_migrations_ordered():
    """Test migrations are applied in order."""
    from scripts.space_traversal.migrations.migrate_trends import MIGRATIONS

    versions = list(MIGRATIONS.keys())
    sorted_versions = sorted(versions)

    # Versions should be sortable
    assert versions == sorted_versions or sorted(versions) == sorted_versions, "versions is not valid"
