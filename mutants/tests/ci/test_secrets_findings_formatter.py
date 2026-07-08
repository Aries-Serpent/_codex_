#!/usr/bin/env python3
"""
Test suite for Secrets Detection Categorizer Module (Phase 8C).

Tests cover:
- Secret type classification
- Rotation deadline calculation
- Remediation step generation
- Finding categorization
- Metadata accuracy
- Performance benchmarks
"""

import json
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List

# Add scripts/ci to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "ci"))

from secrets_findings_formatter import (
    _calculate_rotation_deadline,
    _convert_confidence_to_percent,
    _filter_secret_findings,
    _generate_remediation_steps,
    _parse_secret_type,
    categorize_secret_findings,
)


def create_test_findings_file(findings: List[Dict[str, Any]]) -> Path:
    """
    Create temporary test findings file.

    Args:
        findings: List of finding dictionaries

    Returns:
        Path to temporary file
    """
    temp_file = tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    )
    json.dump({"findings": findings}, temp_file)
    temp_file.close()
    return Path(temp_file.name)


def test_parse_secret_type_aws():
    """Test AWS API key detection."""
    finding = {
        "description": "AWS API Key exposure",
        "cwe": "CWE-798",
        "tool": "detect-secrets",
    }
    assert _parse_secret_type(finding) == "AWS_API_KEY"
    print("✓ test_parse_secret_type_aws")


def test_parse_secret_type_github():
    """Test GitHub PAT detection."""
    finding = {
        "description": "GitHub Personal Access Token",
        "cwe": "CWE-798",
        "tool": "gitLeaks",
    }
    assert _parse_secret_type(finding) == "GITHUB_PAT"
    print("✓ test_parse_secret_type_github")


def test_parse_secret_type_openai():
    """Test OpenAI key detection."""
    finding = {
        "description": "OpenAI secret key",
        "cwe": "CWE-798",
    }
    assert _parse_secret_type(finding) == "OPENAI_KEY"
    print("✓ test_parse_secret_type_openai")


def test_parse_secret_type_private_key():
    """Test private key detection."""
    finding = {
        "description": "Private RSA key in repository",
        "cwe": "CWE-798",
        "tool": "truffleHog",
    }
    assert _parse_secret_type(finding) == "PRIVATE_KEY"
    print("✓ test_parse_secret_type_private_key")


def test_parse_secret_type_db_password():
    """Test database password detection."""
    finding = {
        "description": "PostgreSQL connection string",
        "cwe": "CWE-798",
    }
    assert _parse_secret_type(finding) == "DB_PASSWORD"
    print("✓ test_parse_secret_type_db_password")


def test_parse_secret_type_stripe():
    """Test Stripe key detection."""
    finding = {
        "description": "Stripe API key exposed",
        "cwe": "CWE-798",
    }
    assert _parse_secret_type(finding) == "STRIPE_KEY"
    print("✓ test_parse_secret_type_stripe")


def test_convert_confidence_to_percent_float():
    """Test confidence conversion from float."""
    assert _convert_confidence_to_percent(0.95) == "95%"
    assert _convert_confidence_to_percent(1.0) == "100%"
    print("✓ test_convert_confidence_to_percent_float")


def test_convert_confidence_to_percent_int():
    """Test confidence conversion from int."""
    assert _convert_confidence_to_percent(95) == "95%"
    assert _convert_confidence_to_percent(100) == "100%"
    print("✓ test_convert_confidence_to_percent_int")


def test_convert_confidence_to_percent_string():
    """Test confidence conversion from string."""
    assert _convert_confidence_to_percent("95%") == "95%"
    assert _convert_confidence_to_percent("95") == "95%"
    print("✓ test_convert_confidence_to_percent_string")


def test_calculate_rotation_deadline():
    """Test rotation deadline calculation."""
    deadline = _calculate_rotation_deadline("CRITICAL")
    # Deadline should be a valid ISO 8601 string
    assert deadline.endswith("Z")
    assert "T" in deadline
    print("✓ test_calculate_rotation_deadline")


def test_filter_secret_findings():
    """Test secret findings filtering."""
    all_findings = [
        {
            "cwe": "CWE-79",
            "tool": "CodeQL",
            "description": "XSS vulnerability",
        },
        {
            "cwe": "CWE-798",
            "tool": "detect-secrets",
            "description": "Hardcoded credential",
        },
        {
            "cwe": "CWE-798",
            "tool": "truffleHog",
            "description": "API key found",
        },
    ]

    filtered = _filter_secret_findings(all_findings)
    assert len(filtered) == 2
    assert all(f.get("cwe") == "CWE-798" for f in filtered)
    print("✓ test_filter_secret_findings")


def test_generate_remediation_steps_aws():
    """Test AWS key remediation steps."""
    steps = _generate_remediation_steps("AWS_API_KEY", "config/.env:15")
    assert "Revoke" in steps or "revoke" in steps
    assert "IAM" in steps or "iam" in steps
    assert "Rotate" in steps or "rotate" in steps
    assert "MESSAGE" in steps
    print("✓ test_generate_remediation_steps_aws")


def test_generate_remediation_steps_github():
    """Test GitHub PAT remediation steps."""
    steps = _generate_remediation_steps("GITHUB_PAT", ".env:5")
    assert "GitHub" in steps or "github" in steps or "PAT" in steps
    assert "MESSAGE" in steps
    print("✓ test_generate_remediation_steps_github")


def test_categorize_secret_findings_basic():
    """Test basic secret findings categorization."""
    findings = [
        {
            "file_path": "config/.env",
            "line_number": 15,
            "description": "AWS API Key exposure",
            "cwe": "CWE-798",
            "tool": "detect-secrets",
            "confidence": 1.0,
        },
        {
            "file_path": "src/auth.py",
            "line_number": 42,
            "description": "GitHub Personal Access Token",
            "cwe": "CWE-798",
            "tool": "gitLeaks",
            "confidence": 0.98,
        },
    ]

    test_file = create_test_findings_file(findings)
    try:
        result = categorize_secret_findings(str(test_file))

        assert "secret_categories" in result
        assert "metadata" in result
        assert result["metadata"]["total_secrets"] == 2
        assert result["metadata"]["critical_count"] == 2
        assert len(result["secret_categories"]) == 2
        print("✓ test_categorize_secret_findings_basic")
    finally:
        test_file.unlink()


def test_categorize_secret_findings_metadata():
    """Test metadata accuracy in categorization."""
    findings = [
        {
            "file_path": "config/.env",
            "line_number": 15,
            "description": "AWS API Key",
            "cwe": "CWE-798",
            "tool": "detect-secrets",
            "confidence": 1.0,
        },
        {
            "file_path": "src/config.py",
            "line_number": 10,
            "description": "Slack token",
            "cwe": "CWE-798",
            "tool": "truffleHog",
            "confidence": 0.99,
        },
    ]

    test_file = create_test_findings_file(findings)
    try:
        result = categorize_secret_findings(str(test_file))
        meta = result["metadata"]

        assert "generated_at" in meta
        assert "Z" in meta["generated_at"]
        assert meta["total_secrets"] == 2
        assert "secret_types" in meta
        print("✓ test_categorize_secret_findings_metadata")
    finally:
        test_file.unlink()


def test_categorize_secret_findings_empty():
    """Test categorization with no secrets."""
    findings = [
        {
            "file_path": "src/main.py",
            "line_number": 5,
            "description": "XSS vulnerability",
            "cwe": "CWE-79",
            "tool": "CodeQL",
            "confidence": 0.95,
        },
    ]

    test_file = create_test_findings_file(findings)
    try:
        result = categorize_secret_findings(str(test_file))

        assert result["metadata"]["total_secrets"] == 0
        assert len(result["secret_categories"]) == 0
        print("✓ test_categorize_secret_findings_empty")
    finally:
        test_file.unlink()


def test_categorize_secret_findings_rotation_deadlines():
    """Test that rotation deadlines are set correctly."""
    findings = [
        {
            "file_path": "config/.env",
            "line_number": 15,
            "description": "AWS API Key",
            "cwe": "CWE-798",
            "tool": "detect-secrets",
            "confidence": 1.0,
        },
    ]

    test_file = create_test_findings_file(findings)
    try:
        result = categorize_secret_findings(str(test_file))
        category = result["secret_categories"][0]

        assert "rotation_deadline" in category
        assert "Z" in category["rotation_deadline"]
        assert "rotation_urgency" in category
        print("✓ test_categorize_secret_findings_rotation_deadlines")
    finally:
        test_file.unlink()


def test_categorize_secret_findings_performance():
    """Test performance of categorization (target: < 500ms)."""
    # Create 100 findings
    findings = []
    for i in range(100):
        findings.append(
            {
                "file_path": f"config/.env.{i}",
                "line_number": i,
                "description": "Secret" if i % 2 == 0 else "Other",
                "cwe": "CWE-798" if i % 2 == 0 else "CWE-79",
                "tool": "detect-secrets",
                "confidence": 0.95 + (i % 5) * 0.01,
            }
        )

    test_file = create_test_findings_file(findings)
    try:
        start_time = time.time()
        result = categorize_secret_findings(str(test_file))
        elapsed_ms = (time.time() - start_time) * 1000

        assert elapsed_ms < 500, f"Performance: {elapsed_ms}ms > 500ms threshold"
        print(f"✓ test_categorize_secret_findings_performance ({elapsed_ms:.1f}ms)")
    finally:
        test_file.unlink()


def test_categorize_secret_findings_mixed_tools():
    """Test categorization with multiple tools."""
    findings = [
        {
            "file_path": "config/.env",
            "line_number": 15,
            "description": "AWS API Key",
            "cwe": "CWE-798",
            "tool": "detect-secrets",
            "confidence": 1.0,
        },
        {
            "file_path": "secrets/key.pem",
            "line_number": 1,
            "description": "Private key",
            "cwe": "CWE-798",
            "tool": "truffleHog",
            "confidence": 1.0,
        },
        {
            "file_path": "src/auth.py",
            "line_number": 42,
            "description": "GitHub token",
            "cwe": "CWE-798",
            "tool": "gitLeaks",
            "confidence": 0.98,
        },
    ]

    test_file = create_test_findings_file(findings)
    try:
        result = categorize_secret_findings(str(test_file))

        # Verify tools are recorded
        tools_found = {
            finding["tool"]
            for cat in result["secret_categories"]
            for finding in cat["findings"]
        }
        assert "detect-secrets" in tools_found
        assert "truffleHog" in tools_found
        assert "gitLeaks" in tools_found
        print("✓ test_categorize_secret_findings_mixed_tools")
    finally:
        test_file.unlink()


def run_all_tests() -> int:
    """
    Run all test cases.

    Returns:
        Exit code (0 if all pass, 1 if any fail)
    """
    tests = [
        test_parse_secret_type_aws,
        test_parse_secret_type_github,
        test_parse_secret_type_openai,
        test_parse_secret_type_private_key,
        test_parse_secret_type_db_password,
        test_parse_secret_type_stripe,
        test_convert_confidence_to_percent_float,
        test_convert_confidence_to_percent_int,
        test_convert_confidence_to_percent_string,
        test_calculate_rotation_deadline,
        test_filter_secret_findings,
        test_generate_remediation_steps_aws,
        test_generate_remediation_steps_github,
        test_categorize_secret_findings_basic,
        test_categorize_secret_findings_metadata,
        test_categorize_secret_findings_empty,
        test_categorize_secret_findings_rotation_deadlines,
        test_categorize_secret_findings_performance,
        test_categorize_secret_findings_mixed_tools,
    ]

    print(f"\nRunning {len(tests)} test cases...\n")
    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__}: Unexpected error: {e}")
            failed += 1

    print(f"\n{'=' * 60}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'=' * 60}\n")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
