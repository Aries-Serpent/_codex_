"""Tests for enhanced explain command using capability_scoring module."""

import json


def test_explain_score_integration():
    """Test that explain_score provides detailed partials."""
    from scripts.space_traversal.capability_scoring import (
        explain_score,
    )

    capability = {
        "id": "test-capability",
        "components": {
            "functionality": 0.8,
            "consistency": 0.9,
            "tests": 0.6,
            "safeguards": 0.7,
            "documentation": 0.5,
        },
        "score": 0.72,
    }

    weights = {
        "functionality": 0.25,
        "consistency": 0.20,
        "tests": 0.25,
        "safeguards": 0.15,
        "documentation": 0.15,
    }

    explanation = explain_score(capability, weights)

    # Check structure
    assert "id" in explanation, "Condition must be true"
    assert "score" in explanation, "Condition must be true"
    assert "partials" in explanation, "Condition must be true"
    assert explanation["id"] == "test-capability", "Condition must be true"

    # Check partials
    partials = explanation["partials"]
    assert len(partials) == 5, "Partials must not be empty"

    # Check functionality partial
    func = partials["functionality"]
    assert "component_value" in func, "Value must be initialized"
    assert "weight" in func, "Condition must be true"
    assert "contribution" in func, "Condition must be true"
    assert func["component_value"] == 0.8, "Value must be initialized"
    assert func["weight"] == 0.25, "Condition must be true"
    assert abs(func["contribution"] - 0.2) < 0.001, "Condition must be true"

    # Check tests partial
    tests = partials["tests"]
    assert tests["component_value"] == 0.6, "Value must be initialized"
    assert tests["weight"] == 0.25, "Condition must be true"
    assert abs(tests["contribution"] - 0.15) < 0.001, "Condition must be true"

    # Check total score calculation
    expected_score = (
        0.8 * 0.25  # functionality
        + 0.9 * 0.20  # consistency
        + 0.6 * 0.25  # tests
        + 0.7 * 0.15  # safeguards
        + 0.5 * 0.15  # documentation
    )
    assert abs(explanation["score"] - expected_score) < 0.001, "Condition must be true"


def test_explain_score_with_zero_components():
    """Test explain_score handles zero-valued components correctly."""
    from scripts.space_traversal.capability_scoring import explain_score

    capability = {
        "id": "low-maturity",
        "components": {
            "functionality": 0.0,
            "consistency": 0.5,
            "tests": 0.0,
            "safeguards": 0.0,
            "documentation": 0.3,
        },
    }

    weights = {
        "functionality": 0.25,
        "consistency": 0.20,
        "tests": 0.25,
        "safeguards": 0.15,
        "documentation": 0.15,
    }

    explanation = explain_score(capability, weights)

    # Zero components should contribute 0.0
    assert explanation["partials"]["functionality"]["contribution"] == 0.0, "Condition must be true"
    assert explanation["partials"]["tests"]["contribution"] == 0.0, "Condition must be true"
    assert explanation["partials"]["safeguards"]["contribution"] == 0.0, "Condition must be true"

    # Non-zero components should contribute
    assert explanation["partials"]["consistency"]["contribution"] > 0.0, "Value must be greater than zero"
    assert explanation["partials"]["documentation"]["contribution"] > 0.0, "Value must be greater than zero"


def test_normalize_weights():
    """Test weight normalization."""
    from scripts.space_traversal.capability_scoring import normalize_weights

    weights = {
        "functionality": 0.5,
        "consistency": 0.4,
        "tests": 0.5,
        "safeguards": 0.3,
        "documentation": 0.3,
    }

    normalized = normalize_weights(weights)

    # Should sum to 1.0
    assert abs(sum(normalized.values()) - 1.0) < 1e-9, "Value must be initialized"

    # Should preserve ratios
    total = sum(weights.values())
    for key in weights:
        expected = weights[key] / total
        assert abs(normalized[key] - expected) < 1e-9, "Condition must be true"


def test_command_explain_output_format(tmp_path, capsys):
    """Test that command_explain produces correctly formatted output."""
    import argparse

    from scripts.space_traversal.audit_runner import command_explain

    # Create test data
    artifacts_dir = tmp_path / "audit_artifacts"
    artifacts_dir.mkdir()

    scored_data = {
        "capabilities": [
            {
                "id": "checkpointing",
                "components": {
                    "functionality": 0.75,
                    "consistency": 0.85,
                    "tests": 0.60,
                    "safeguards": 0.70,
                    "documentation": 0.55,
                },
                "score": 0.69,
            }
        ]
    }

    scored_file = artifacts_dir / "capabilities_scored.json"
    scored_file.write_text(json.dumps(scored_data))

    # Create config
    cfg = {
        "output": {"artifacts_dir": str(artifacts_dir)},
        "weights": {
            "functionality": 0.25,
            "consistency": 0.20,
            "tests": 0.25,
            "safeguards": 0.15,
            "documentation": 0.15,
        },
    }

    # Create args
    args = argparse.Namespace(capability="checkpointing")

    # Run command
    command_explain(args, cfg)

    # Check output
    captured = capsys.readouterr()
    output = captured.out

    # Should contain capability ID
    assert "Capability: checkpointing" in output, "Condition must be true"

    # Should contain all components with proper formatting
    assert "functionality" in output, "Condition must be true"
    assert "consistency" in output, "Condition must be true"
    assert "tests" in output, "Condition must be true"
    assert "safeguards" in output, "Condition must be true"
    assert "documentation" in output, "Condition must be true"

    # Should show value, weight, and contribution for each
    assert "Value:" in output, "Value must be initialized"
    assert "Weight:" in output, "Condition must be true"
    assert "Contrib:" in output, "Condition must be true"

    # Should show overall score
    assert "Overall Score:" in output, "Condition must be true"
