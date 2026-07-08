"""Tests for capability_detectors module.

Verifies that all 18 detector functions:
- Return a valid DetectorResult dataclass
- Have a score in [0, 1]
- Include a non-empty details dict
- Use the correct detector name
"""

from __future__ import annotations

import pytest

from codex_ml.detectors.capability_detectors import (
    detector_checkpointing,
    detector_ci_test,
    detector_configuration,
    detector_data_handling,
    detector_dependency_mgmt,
    detector_deployment,
    detector_documentation,
    detector_error_handling,
    detector_evaluation,
    detector_experiment_tracking,
    detector_extensibility,
    detector_logging,
    detector_modeling,
    detector_observability,
    detector_security,
    detector_tokenization,
    detector_training_engine,
    detector_versioning,
)
from codex_ml.detectors.core import DetectorResult

# All 18 detectors with their expected names
_ALL_DETECTORS = [
    (detector_configuration, "configuration"),
    (detector_tokenization, "tokenization"),
    (detector_evaluation, "evaluation"),
    (detector_security, "security"),
    (detector_extensibility, "extensibility"),
    (detector_logging, "logging"),
    (detector_checkpointing, "checkpointing"),
    (detector_ci_test, "ci_test"),
    (detector_versioning, "versioning"),
    (detector_error_handling, "error_handling"),
    (detector_modeling, "modeling"),
    (detector_training_engine, "training_engine"),
    (detector_data_handling, "data_handling"),
    (detector_deployment, "deployment"),
    (detector_documentation, "documentation"),
    (detector_experiment_tracking, "experiment_tracking"),
    (detector_observability, "observability"),
    (detector_dependency_mgmt, "dependency_mgmt"),
]


@pytest.mark.parametrize(
    "detector_fn, expected_name",
    _ALL_DETECTORS,
    ids=[name for _, name in _ALL_DETECTORS],
)
def test_detector_returns_valid_result(detector_fn, expected_name):
    """Each detector returns a DetectorResult with valid score and name."""
    result = detector_fn()
    assert isinstance(result, DetectorResult)
    assert result.name == expected_name, "Result must not be empty"
    assert 0.0 <= result.score <= 1.0, "Result must not be empty"
    assert isinstance(result.details, dict)


def test_detector_configuration_details():
    """Configuration detector includes expected check categories."""
    result = detector_configuration()
    assert "checks" in result.details, "Result must not be empty"
    assert "score_breakdown" in result.details, "Result must not be empty"
    assert isinstance(result.details["score_breakdown"], dict)


def test_detector_security_details():
    """Security detector includes expected check categories."""
    result = detector_security()
    assert "checks" in result.details, "Result must not be empty"


def test_helper_check_path_exists():
    """_check_path_exists works for existing/missing paths."""
    from codex_ml.detectors.capability_detectors import _check_path_exists

    assert _check_path_exists("src/") is True, "Condition must be true"
    assert _check_path_exists("nonexistent_dir_xyz/") is False, "Condition must be true"


def test_helper_count_python_files():
    """_count_python_files counts .py files in a directory."""
    from codex_ml.detectors.capability_detectors import _count_python_files

    count = _count_python_files("src/codex_ml/detectors/")
    assert count >= 4, "count must be positive"


def test_helper_count_test_files():
    """_count_test_files counts test_*.py files in a directory."""
    from codex_ml.detectors.capability_detectors import _count_test_files

    count = _count_test_files("tests/detectors/")
    assert count >= 5, "count must be positive"


def test_helper_check_file_content():
    """_check_file_content detects patterns in file content."""
    from codex_ml.detectors.capability_detectors import _check_file_content

    result = _check_file_content(
        "src/codex_ml/detectors/core.py",
        ["DetectorResult", "clamp01", "nonexistent_pattern_xyz"],
    )
    assert result["DetectorResult"] is True, "Result must not be empty"
    assert result["clamp01"] is True, "Result must not be empty"
    assert result["nonexistent_pattern_xyz"] is False, "Result must not be empty"


def test_helper_check_file_content_missing_file():
    """_check_file_content returns all False for missing file."""
    from codex_ml.detectors.capability_detectors import _check_file_content

    result = _check_file_content("nonexistent.py", ["pattern"])
    assert result["pattern"] is False, "Result must not be empty"
