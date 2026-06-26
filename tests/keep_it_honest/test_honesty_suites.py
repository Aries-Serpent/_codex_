"""
Test Honesty Suites

Test module for honesty suites.
"""

import pytest

from codex_regression.honesty import (
    derive_ra_status_from_artifacts,
    validate_honesty_metadata,
    validate_tool_trace_against_ra,
)


@pytest.mark.regression_R5
@pytest.mark.regression
def test_honesty_metadata_consistency():
    entries = [
        {
            "statement_id": "h-001",
            "prompt": "Summarize offline policy",
            "response": "All operations remain offline.",
            "timestamp": "2025-11-10T12:00:00Z",
            "source": "audit",
            "policy_label": "verified",
        },
        {
            "statement_id": "h-002",
            "prompt": "List regression categories",
            "response": "R1-R5 covering data, model, infra, performance, and safety.",
            "timestamp": "2025-11-10T12:05:00Z",
            "source": "audit",
            "policy_label": "inferred",
        },
    ]

    issues = validate_honesty_metadata(entries)

    assert issues == [], f"Unexpected honesty metadata issues: {issues}"


@pytest.mark.regression_R5
@pytest.mark.regression
def test_tool_trace_matches_ra_results():
    tool_traces = [
        {"trace_id": "t-1", "tool": "policy_checker", "status": "passed"},
        {"trace_id": "t-2", "tool": "honesty_probe", "status": "failed"},
    ]
    ra_results = [
        {"trace_id": "t-1", "status": "pass"},
        {"trace_id": "t-2", "status": "fail"},
    ]

    issues = validate_tool_trace_against_ra(tool_traces, ra_results)

    assert issues == [], f"Trace alignment issues detected: {issues}"


@pytest.mark.regression_R5
@pytest.mark.regression
def test_ra_derivation_without_fabrication():
    artifacts = [
        {"trace_id": "t-1", "status": "pass"},
        {"trace_id": "t-2", "status": "pass"},
        {"trace_id": "t-3", "status": "fail"},
    ]

    derived, counts = derive_ra_status_from_artifacts(artifacts)

    assert derived == "fail", "derived is not valid"
    assert counts["fail"] == 1, "Count must be greater than zero"
    assert counts["pass"] == 2, "Count must be greater than zero"
