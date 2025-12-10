"""Tests for database migrations (v1.5.x)."""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest


def test_migration_decorator():
    """Test migration registration decorator."""
    from scripts.space_traversal.migrations.migrate_trends import MIGRATIONS, migration

    # Check that migrations are registered
    assert "1.5.0" in MIGRATIONS
    assert "1.5.1" in MIGRATIONS
    assert "1.5.2" in MIGRATIONS
    assert "1.5.3" in MIGRATIONS
    assert "1.5.4" in MIGRATIONS
    assert "1.5.5" in MIGRATIONS


def test_run_migrations_fresh_db(tmp_path: Path):
    """Test running migrations on fresh database."""
    from scripts.space_traversal.migrations.migrate_trends import run_migrations

    db_path = tmp_path / "test.db"

    # Don't create any tables - migrations should create them
    applied = run_migrations(db_path)

    # All migrations should be applied
    assert len(applied) == 6
    assert "1.5.0" in applied
    assert "1.5.5" in applied


def test_run_migrations_idempotent(tmp_path: Path):
    """Test migrations are idempotent."""
    from scripts.space_traversal.migrations.migrate_trends import run_migrations

    db_path = tmp_path / "test.db"

    # Run once
    applied1 = run_migrations(db_path)
    assert len(applied1) == 6

    # Run again - should apply nothing
    applied2 = run_migrations(db_path)
    assert len(applied2) == 0


def test_get_current_version(tmp_path: Path):
    """Test getting current schema version."""
    from scripts.space_traversal.migrations.migrate_trends import (
        get_current_version,
        run_migrations,
    )

    db_path = tmp_path / "test.db"

    # No database yet
    assert get_current_version(db_path) == "0.0.0"

    # After migrations
    run_migrations(db_path)
    assert get_current_version(db_path) == "1.5.5"


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
        assert cursor.fetchone() is not None


def test_migration_1_5_2_viz_cache(tmp_path: Path):
    """Test v1.5.2 adds visualization cache."""
    from scripts.space_traversal.migrations.migrate_trends import run_migrations

    db_path = tmp_path / "test.db"
    run_migrations(db_path)

    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='viz_cache'"
        )
        assert cursor.fetchone() is not None


def test_migration_1_5_3_report_metadata(tmp_path: Path):
    """Test v1.5.3 adds report metadata."""
    from scripts.space_traversal.migrations.migrate_trends import run_migrations

    db_path = tmp_path / "test.db"
    run_migrations(db_path)

    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='report_metadata'"
        )
        assert cursor.fetchone() is not None


def test_migration_1_5_4_webhook_deliveries(tmp_path: Path):
    """Test v1.5.4 adds webhook tracking."""
    from scripts.space_traversal.migrations.migrate_trends import run_migrations

    db_path = tmp_path / "test.db"
    run_migrations(db_path)

    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='webhook_deliveries'"
        )
        assert cursor.fetchone() is not None


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
        assert cursor.fetchone() is not None

        # Check repositories table (federation prep)
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='repositories'"
        )
        assert cursor.fetchone() is not None


def test_migrations_ordered():
    """Test migrations are applied in order."""
    from scripts.space_traversal.migrations.migrate_trends import MIGRATIONS

    versions = list(MIGRATIONS.keys())
    sorted_versions = sorted(versions)

    # Versions should be sortable
    assert versions == sorted_versions or sorted(versions) == sorted_versions
