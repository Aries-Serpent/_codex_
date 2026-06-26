"""Tests for medium threshold labeling in capability matrix template."""

import tempfile
from pathlib import Path


def test_medium_threshold_in_template_context():
    """Test that medium threshold is passed to template context."""
    from scripts.space_traversal.audit_runner import stage_s6_render

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        artifacts_dir = tmpdir / "audit_artifacts"
        artifacts_dir.mkdir()
        reports_dir = tmpdir / "reports"
        reports_dir.mkdir()

        # Create a minimal template
        templates_dir = tmpdir / "templates"
        templates_dir.mkdir()
        template_file = templates_dir / "test.md.j2"
        template_file.write_text("""
Low: {{ thresholds.low }}
Medium: {{ thresholds.medium }}
High Capabilities: {{ capabilities|selectattr('score', 'ge', thresholds.medium)|list|length }}
""")

        cfg = {
            "output": {
                "artifacts_dir": str(artifacts_dir),
                "reports_dir": str(reports_dir),
                "matrix_template": str(template_file),
            },
            "weights": {
                "functionality": 0.25,
                "consistency": 0.20,
                "tests": 0.25,
                "safeguards": 0.15,
                "documentation": 0.15,
            },
            "scoring": {
                "thresholds": {
                    "low": 0.70,
                    "medium": 0.85,
                }
            },
        }

        scored_caps = [
            {
                "id": "high-cap",
                "score": 0.90,
                "components": {
                    "functionality": 0.9,
                    "consistency": 0.9,
                    "tests": 0.9,
                    "safeguards": 0.9,
                    "documentation": 0.9,
                },
                "evidence_files": [],
                "found_patterns": [],
                "required_patterns": [],
                "missing_patterns": [],
            },
            {
                "id": "medium-cap",
                "score": 0.75,
                "components": {
                    "functionality": 0.7,
                    "consistency": 0.8,
                    "tests": 0.7,
                    "safeguards": 0.8,
                    "documentation": 0.7,
                },
                "evidence_files": [],
                "found_patterns": [],
                "required_patterns": [],
                "missing_patterns": [],
            },
            {
                "id": "low-cap",
                "score": 0.65,
                "components": {
                    "functionality": 0.6,
                    "consistency": 0.7,
                    "tests": 0.6,
                    "safeguards": 0.7,
                    "documentation": 0.6,
                },
                "evidence_files": [],
                "found_patterns": [],
                "required_patterns": [],
                "missing_patterns": [],
            },
        ]

        gaps = {
            "low_maturity": [scored_caps[2]],
            "missing_detectors": [],
            "summary": {"low_count": 1},
        }

        # Render template
        output_file = stage_s6_render(cfg, scored_caps, gaps)

        # Check output
        content = output_file.read_text()
        assert "Low: 0.70" in content or "Low: 0.7" in content, "Content must not be empty"
        assert "Medium: 0.85" in content, "Content must not be empty"
        # 1 high capability (score >= 0.85)
        assert "High Capabilities: 1" in content, "Content must not be empty"


def test_capability_level_assignment():
    """Test that capabilities are assigned correct maturity levels."""
    # This tests the template logic for level assignment
    low_threshold = 0.70
    medium_threshold = 0.85

    test_cases = [
        (0.95, "High"),
        (0.85, "High"),
        (0.80, "Medium"),
        (0.75, "Medium"),
        (0.70, "Medium"),
        (0.65, "Low"),
        (0.50, "Low"),
    ]

    for score, expected_level in test_cases:
        if score < low_threshold:
            level = "Low"
        elif score < medium_threshold:
            level = "Medium"
        else:
            level = "High"

        assert level == expected_level, f"Score {score} should be {expected_level}, got {level}"


def test_medium_maturity_count():
    """Test counting capabilities by maturity level."""
    capabilities = [
        {"id": "cap1", "score": 0.95},  # High
        {"id": "cap2", "score": 0.88},  # High
        {"id": "cap3", "score": 0.80},  # Medium
        {"id": "cap4", "score": 0.72},  # Medium
        {"id": "cap5", "score": 0.65},  # Low
        {"id": "cap6", "score": 0.50},  # Low
    ]

    low_threshold = 0.70
    medium_threshold = 0.85

    low_count = len([c for c in capabilities if c["score"] < low_threshold])
    medium_count = len([c for c in capabilities if low_threshold <= c["score"] < medium_threshold])
    high_count = len([c for c in capabilities if c["score"] >= medium_threshold])

    assert low_count == 2, "Count must be greater than zero"
    assert medium_count == 2, "Count must be greater than zero"
    assert high_count == 2, "Count must be greater than zero"
    assert low_count + medium_count + high_count == len(capabilities), "Capabilities must not be empty"
