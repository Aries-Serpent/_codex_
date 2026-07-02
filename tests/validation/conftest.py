"""Pytest configuration for coverage validation tests.

Provides fixtures and shared configuration for coverage baseline monitoring
and validation tests (Phase 2 and beyond).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.fixture
def repo_root() -> Path:
    """Return the repository root directory."""
    return Path(__file__).resolve().parents[2]


@pytest.fixture
def baseline_file(repo_root: Path) -> Path:
    """Return path to baseline snapshot file."""
    return repo_root / ".codex" / "COVERAGE_BASELINE_34_63.json"


@pytest.fixture
def baseline_snapshot(baseline_file: Path) -> dict:
    """Load and return the baseline snapshot."""
    if baseline_file.exists():
        with open(baseline_file) as f:
            return json.load(f)
    return {}


@pytest.fixture
def tracking_file(repo_root: Path) -> Path:
    """Return path to baseline tracking report file."""
    return repo_root / ".codex" / "coverage" / "BASELINE_TRACKING_REPORT.json"


@pytest.fixture
def tracking_report(tracking_file: Path) -> dict:
    """Load and return the baseline tracking report."""
    if tracking_file.exists():
        with open(tracking_file) as f:
            return json.load(f)
    return {}


@pytest.fixture
def module_matrix_file(repo_root: Path) -> Path:
    """Return path to module baseline matrix file."""
    return repo_root / ".codex" / "coverage" / "MODULE_BASELINE_MATRIX.json"


@pytest.fixture
def module_matrix(module_matrix_file: Path) -> dict:
    """Load and return the module baseline matrix."""
    if module_matrix_file.exists():
        with open(module_matrix_file) as f:
            return json.load(f)
    return {}


@pytest.fixture
def phase_gates_file(repo_root: Path) -> Path:
    """Return path to phase validation gates file."""
    return repo_root / ".codex" / "PHASE_VALIDATION_GATES.yaml"


@pytest.fixture(scope="session")
def validation_report_dir(repo_root: Path) -> Path:
    """Create and return validation reports directory."""
    report_dir = repo_root / ".codex" / "coverage" / "validation_reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    return report_dir


# Markers for test categorization
def pytest_configure(config):
    """Register custom pytest markers."""
    config.addinivalue_line(
        "markers",
        "validation: mark test as a coverage validation test",
    )
    config.addinivalue_line(
        "markers",
        "determinism: mark test as testing determinism",
    )
    config.addinivalue_line(
        "markers",
        "regression: mark test as testing regression detection",
    )
    config.addinivalue_line(
        "markers",
        "module_gates: mark test as testing module-level gates",
    )
    config.addinivalue_line(
        "markers",
        "quality_metrics: mark test as testing quality metrics",
    )
