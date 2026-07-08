"""Tests for trend database (v1.5.0)."""

from __future__ import annotations

import json
import time
from pathlib import Path


def test_trend_database_init(tmp_path: Path):
    """Test trend database initialization."""
    from scripts.space_traversal.trend_db import TrendDatabase

    db_path = tmp_path / "test_trends.db"
    db = TrendDatabase(db_path)

    assert db_path.exists(), "Condition must be true"
    assert db.get_schema_version() == "1.5.0", "Condition must be true"
    assert db.get_run_count() == 0, "Count must be greater than zero"


def test_store_and_retrieve_snapshot(tmp_path: Path):
    """Test storing and retrieving an audit snapshot."""
    from scripts.space_traversal.trend_db import AuditSnapshot, TrendDatabase

    db_path = tmp_path / "test_trends.db"
    db = TrendDatabase(db_path)

    snapshot = AuditSnapshot(
        run_id="test-run-001",
        timestamp=time.time(),
        repo_root_sha="abc123",
        git_commit="def456",
        git_branch="main",
        version="1.5.0",
        capabilities={"cap1": 0.85, "cap2": 0.78},
        components={
            "cap1": {
                "functionality": 1.0,
                "consistency": 0.9,
                "tests": 0.8,
                "safeguards": 0.7,
                "documentation": 0.6,
            },
            "cap2": {
                "functionality": 0.9,
                "consistency": 0.8,
                "tests": 0.7,
                "safeguards": 0.6,
                "documentation": 0.5,
            },
        },
        weights={"functionality": 0.25, "consistency": 0.2},
        coverage_stats={"covered": 100, "total": 120},
        manifest_sha="sha256:xyz",
    )

    run_id = db.store_snapshot(snapshot)
    assert run_id == "test-run-001", "run_id is not valid"
    assert db.get_run_count() == 1, "Count must be greater than zero"


def test_get_trend(tmp_path: Path):
    """Test getting trend for a capability."""
    from scripts.space_traversal.trend_db import AuditSnapshot, TrendDatabase

    db_path = tmp_path / "test_trends.db"
    db = TrendDatabase(db_path)

    # Store multiple snapshots
    for i, score in enumerate([0.75, 0.78, 0.82, 0.80, 0.85]):
        snapshot = AuditSnapshot(
            run_id=f"run-{i:03d}",
            timestamp=time.time() - (4 - i) * 86400,  # Spread over 5 days
            repo_root_sha=f"sha{i}",
            git_commit=f"commit{i}",
            git_branch="main",
            version="1.5.0",
            capabilities={"cap1": score},
            components={"cap1": {"functionality": score}},
            weights={},
            coverage_stats=None,
            manifest_sha=f"manifest{i}",
        )
        db.store_snapshot(snapshot)

    # Get trend
    trend = db.get_trend("cap1", limit=10)
    assert len(trend) == 5, "Trend must not be empty"
    # Should be in descending timestamp order
    assert trend[0]["score"] == 0.85, "Condition must be true"
    assert trend[-1]["score"] == 0.75, "Condition must be true"


def test_get_trend_with_branch_filter(tmp_path: Path):
    """Test trend filtering by branch."""
    from scripts.space_traversal.trend_db import AuditSnapshot, TrendDatabase

    db_path = tmp_path / "test_trends.db"
    db = TrendDatabase(db_path)

    # Store snapshots on different branches
    for i, (branch, score) in enumerate([("main", 0.8), ("feature", 0.7), ("main", 0.85)]):
        snapshot = AuditSnapshot(
            run_id=f"run-{i:03d}",
            timestamp=time.time() - (2 - i) * 86400,
            repo_root_sha=f"sha{i}",
            git_commit=f"commit{i}",
            git_branch=branch,
            version="1.5.0",
            capabilities={"cap1": score},
            components={},
            weights={},
            coverage_stats=None,
            manifest_sha=f"manifest{i}",
        )
        db.store_snapshot(snapshot)

    # Filter by main branch
    trend = db.get_trend("cap1", branch="main")
    assert len(trend) == 2, "Trend must not be empty"
    assert all(t["git_branch"] == "main" for t in trend), "Condition must be true"


def test_get_latest_scores(tmp_path: Path):
    """Test getting latest scores for all capabilities."""
    from scripts.space_traversal.trend_db import AuditSnapshot, TrendDatabase

    db_path = tmp_path / "test_trends.db"
    db = TrendDatabase(db_path)

    # Store two runs
    snapshot1 = AuditSnapshot(
        run_id="run-001",
        timestamp=time.time() - 86400,
        repo_root_sha="sha1",
        git_commit="commit1",
        git_branch="main",
        version="1.5.0",
        capabilities={"cap1": 0.7, "cap2": 0.6},
        components={},
        weights={},
        coverage_stats=None,
        manifest_sha="manifest1",
    )
    db.store_snapshot(snapshot1)

    snapshot2 = AuditSnapshot(
        run_id="run-002",
        timestamp=time.time(),
        repo_root_sha="sha2",
        git_commit="commit2",
        git_branch="main",
        version="1.5.0",
        capabilities={"cap1": 0.8, "cap3": 0.9},  # cap2 not present
        components={},
        weights={},
        coverage_stats=None,
        manifest_sha="manifest2",
    )
    db.store_snapshot(snapshot2)

    latest = db.get_latest_scores()
    assert latest["cap1"] == 0.8, "Condition must be true"
    assert latest["cap2"] == 0.6, "Condition must be true"
    assert latest["cap3"] == 0.9, "Condition must be true"


def test_get_regressions(tmp_path: Path):
    """Test regression detection."""
    from scripts.space_traversal.trend_db import AuditSnapshot, TrendDatabase

    db_path = tmp_path / "test_trends.db"
    db = TrendDatabase(db_path)

    # Store runs with a regression
    scores = [0.85, 0.84, 0.83, 0.82, 0.75]  # Last one is a regression
    for i, score in enumerate(scores):
        snapshot = AuditSnapshot(
            run_id=f"run-{i:03d}",
            timestamp=time.time() - (4 - i) * 86400,
            repo_root_sha=f"sha{i}",
            git_commit=f"commit{i}",
            git_branch="main",
            version="1.5.0",
            capabilities={"regressing_cap": score},
            components={},
            weights={},
            coverage_stats=None,
            manifest_sha=f"manifest{i}",
        )
        db.store_snapshot(snapshot)

    regressions = db.get_regressions(threshold=0.02, lookback_runs=4)
    assert len(regressions) == 1, "Regressions must not be empty"
    assert regressions[0]["capability_id"] == "regressing_cap", "Condition must be true"
    assert regressions[0]["delta"] < 0, "Condition must be true"
    assert regressions[0]["severity"] in ("high", "medium")


def test_get_capability_ids(tmp_path: Path):
    """Test getting all capability IDs."""
    from scripts.space_traversal.trend_db import AuditSnapshot, TrendDatabase

    db_path = tmp_path / "test_trends.db"
    db = TrendDatabase(db_path)

    snapshot = AuditSnapshot(
        run_id="run-001",
        timestamp=time.time(),
        repo_root_sha="sha1",
        git_commit="commit1",
        git_branch="main",
        version="1.5.0",
        capabilities={"cap-z": 0.8, "cap-a": 0.9, "cap-m": 0.7},
        components={},
        weights={},
        coverage_stats=None,
        manifest_sha="manifest1",
    )
    db.store_snapshot(snapshot)

    cap_ids = db.get_capability_ids()
    assert cap_ids == ["cap-a", "cap-m", "cap-z"]  # Sorted


def test_export_csv(tmp_path: Path):
    """Test CSV export."""
    from scripts.space_traversal.trend_db import AuditSnapshot, TrendDatabase

    db_path = tmp_path / "test_trends.db"
    db = TrendDatabase(db_path)

    snapshot = AuditSnapshot(
        run_id="run-001",
        timestamp=time.time(),
        repo_root_sha="sha1",
        git_commit="commit1",
        git_branch="main",
        version="1.5.0",
        capabilities={"cap1": 0.85},
        components={"cap1": {"functionality": 1.0, "tests": 0.8}},
        weights={},
        coverage_stats=None,
        manifest_sha="manifest1",
    )
    db.store_snapshot(snapshot)

    csv_path = tmp_path / "export.csv"
    db.export_csv(csv_path)

    assert csv_path.exists(), "Condition must be true"
    content = csv_path.read_text()
    assert "cap1" in content, "Content must not be empty"
    assert "0.85" in content, "Content must not be empty"


def test_cleanup_old_runs(tmp_path: Path):
    """Test cleanup of old runs."""
    from scripts.space_traversal.trend_db import AuditSnapshot, TrendDatabase

    db_path = tmp_path / "test_trends.db"
    db = TrendDatabase(db_path)

    # Store 10 runs
    for i in range(10):
        snapshot = AuditSnapshot(
            run_id=f"run-{i:03d}",
            timestamp=time.time() - i * 86400,
            repo_root_sha=f"sha{i}",
            git_commit=f"commit{i}",
            git_branch="main",
            version="1.5.0",
            capabilities={"cap1": 0.8 + i * 0.01},
            components={},
            weights={},
            coverage_stats=None,
            manifest_sha=f"manifest{i}",
        )
        db.store_snapshot(snapshot)

    assert db.get_run_count() == 10, "Count must be greater than zero"

    # Keep only 5 runs
    deleted = db.cleanup_old_runs(max_runs=5, max_age_days=365)
    assert deleted == 5, "deleted is not valid"
    assert db.get_run_count() == 5, "Count must be greater than zero"


def test_create_snapshot_from_artifacts(tmp_path: Path):
    """Test creating snapshot from artifacts."""
    from scripts.space_traversal.trend_db import create_snapshot_from_artifacts

    # Create mock artifacts
    artifacts_dir = tmp_path / "audit_artifacts"
    artifacts_dir.mkdir()

    scored_data = {
        "capabilities": [
            {
                "id": "cap1",
                "score": 0.85,
                "components": {
                    "functionality": 1.0,
                    "consistency": 0.9,
                    "tests": 0.8,
                    "safeguards": 0.7,
                    "documentation": 0.6,
                },
            },
            {"id": "cap2", "score": 0.78, "components": {}},
        ]
    }
    (artifacts_dir / "capabilities_scored.json").write_text(json.dumps(scored_data))

    manifest_data = {
        "timestamp": time.time(),
        "version": "1.5.0",
        "repo_root_sha": "abc123",
        "weights": {"functionality": 0.25},
        "coverage_stats": {"covered": 100},
        "artifacts": [{"sha": "sha256:xyz"}],
    }
    (tmp_path / "audit_run_manifest.json").write_text(json.dumps(manifest_data))

    snapshot = create_snapshot_from_artifacts(artifacts_dir, git_commit="def456", git_branch="main")

    assert snapshot.git_commit == "def456", "git_commit is not valid"
    assert snapshot.git_branch == "main", "git_branch is not valid"
    assert "cap1" in snapshot.capabilities, "Condition must be true"
    assert snapshot.capabilities["cap1"] == 0.85, "Condition must be true"
    assert snapshot.components["cap1"]["functionality"] == 1.0, "Condition must be true"


def test_audit_snapshot_dataclass():
    """Test AuditSnapshot dataclass."""
    from dataclasses import asdict

    from scripts.space_traversal.trend_db import AuditSnapshot

    snapshot = AuditSnapshot(
        run_id="test-run",
        timestamp=1234567890.0,
        repo_root_sha="abc",
        git_commit="def",
        git_branch="main",
        version="1.5.0",
        capabilities={"cap1": 0.8},
        components={},
        weights={},
        coverage_stats=None,
        manifest_sha="xyz",
    )

    data = asdict(snapshot)
    assert data["run_id"] == "test-run", "Data must not be empty"
    assert data["capabilities"]["cap1"] == 0.8, "Data must not be empty"
