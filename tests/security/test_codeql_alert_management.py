"""
Tests for CodeQL alert management scripts.

This module tests the alert fetcher and closer scripts to ensure
they handle GitHub API interactions correctly.
"""

from __future__ import annotations

import json

# Import the classes we're testing
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "security"))

from close_codeql_alert import AlertCloser
from fetch_codeql_alerts import (
    AlertExporter,
    CodeQLAlertFetcher,
    CodeScanningAlert,
)


class TestCodeScanningAlert:
    """Tests for CodeScanningAlert dataclass."""

    def test_alert_creation(self):
        """Test creating a CodeScanningAlert."""
        alert = CodeScanningAlert(
            alert_number=123,
            rule_id="py/sql-injection",
            severity="high",
            state="open",
            file_path="src/database.py",
            line_start=45,
            line_end=48,
            description="SQL injection vulnerability",
            created_at="2026-01-26T10:00:00Z",
            html_url="https://github.com/test/test/security/code-scanning/123",
            cwe_id="CWE-89",
        )

        assert alert.alert_number == 123
        assert alert.severity == "high"
        assert alert.cwe_id == "CWE-89"

    def test_alert_to_dict(self):
        """Test converting alert to dictionary."""
        alert = CodeScanningAlert(
            alert_number=456,
            rule_id="py/xss",
            severity="medium",
            state="open",
            file_path="src/web.py",
            line_start=10,
            line_end=10,
            description="Cross-site scripting",
            created_at="2026-01-26T11:00:00Z",
            html_url="https://github.com/test/test/security/code-scanning/456",
        )

        data = alert.to_dict()
        assert isinstance(data, dict)
        assert data["alert_number"] == 456
        assert data["rule_id"] == "py/xss"
        assert "metadata" not in data  # Should exclude empty metadata


class TestCodeQLAlertFetcher:
    """Tests for CodeQLAlertFetcher class."""

    @patch('fetch_codeql_alerts.requests.Session')
    def test_fetcher_initialization(self, mock_session):
        """Test initializing the fetcher."""
        fetcher = CodeQLAlertFetcher(
            owner="test-owner",
            repo="test-repo",
            token="test-token",
        )

        assert fetcher.owner == "test-owner"
        assert fetcher.repo == "test-repo"
        assert fetcher.token == "test-token"

    @patch('fetch_codeql_alerts.requests.Session')
    def test_fetcher_without_token_warning(self, mock_session):
        """Test fetcher logs warning without token."""
        fetcher = CodeQLAlertFetcher(
            owner="test-owner",
            repo="test-repo",
            token="",
        )

        # Should still initialize but without auth headers
        assert fetcher.token == ""

    def test_extract_cwe_id(self):
        """Test extracting CWE ID from rule tags."""
        fetcher = CodeQLAlertFetcher("owner", "repo", "token")

        rule = {"tags": ["security", "external/cwe/cwe-89"]}
        cwe = fetcher._extract_cwe_id(rule)
        assert cwe == "CWE-89"

        rule_no_cwe = {"tags": ["security"]}
        cwe_none = fetcher._extract_cwe_id(rule_no_cwe)
        assert cwe_none is None

    def test_determine_category(self):
        """Test categorizing vulnerabilities by rule ID."""
        fetcher = CodeQLAlertFetcher("owner", "repo", "token")

        assert fetcher._determine_category("py/sql-injection") == "injection"
        assert fetcher._determine_category("py/path-traversal") == "path-traversal"
        assert fetcher._determine_category("py/weak-crypto") == "cryptography"
        assert fetcher._determine_category("py/broken-auth") == "authentication"
        assert fetcher._determine_category("py/unknown") == "security"


class TestAlertExporter:
    """Tests for AlertExporter class."""

    def test_export_json(self, tmp_path):
        """Test exporting alerts to JSON."""
        alerts = [
            CodeScanningAlert(
                alert_number=1,
                rule_id="test-rule",
                severity="low",
                state="open",
                file_path="test.py",
                line_start=1,
                line_end=1,
                description="Test alert",
                created_at="2026-01-26T12:00:00Z",
                html_url="https://test.com",
            )
        ]

        output_file = tmp_path / "test_alerts.json"
        AlertExporter.export_json(alerts, output_file)

        assert output_file.exists()
        with open(output_file) as f:
            data = json.load(f)

        assert data["total_alerts"] == 1
        assert len(data["alerts"]) == 1
        assert data["alerts"][0]["alert_number"] == 1

    def test_export_csv(self, tmp_path):
        """Test exporting alerts to CSV."""
        alerts = [
            CodeScanningAlert(
                alert_number=2,
                rule_id="test-rule-2",
                severity="high",
                state="open",
                file_path="test2.py",
                line_start=10,
                line_end=12,
                description="Test alert 2",
                created_at="2026-01-26T13:00:00Z",
                html_url="https://test.com/2",
            )
        ]

        output_file = tmp_path / "test_alerts.csv"
        AlertExporter.export_csv(alerts, output_file)

        assert output_file.exists()
        content = output_file.read_text()
        assert "alert_number" in content
        assert "test-rule-2" in content

    def test_export_markdown(self, tmp_path):
        """Test exporting alerts to Markdown."""
        alerts = [
            CodeScanningAlert(
                alert_number=3,
                rule_id="test-rule-3",
                severity="critical",
                state="open",
                file_path="test3.py",
                line_start=20,
                line_end=25,
                description="Test alert 3",
                created_at="2026-01-26T14:00:00Z",
                html_url="https://test.com/3",
            )
        ]

        output_file = tmp_path / "test_alerts.md"
        AlertExporter.export_markdown(alerts, output_file)

        assert output_file.exists()
        content = output_file.read_text()
        assert "# CodeQL Code Scanning Alerts" in content
        assert "Summary Statistics" in content
        assert "critical" in content.lower()


class TestAlertCloser:
    """Tests for AlertCloser class."""

    @patch('close_codeql_alert.requests.Session')
    def test_closer_initialization(self, mock_session):
        """Test initializing the closer."""
        closer = AlertCloser(
            owner="test-owner",
            repo="test-repo",
            token="test-token",
        )

        assert closer.owner == "test-owner"
        assert closer.repo == "test-repo"
        assert closer.token == "test-token"

    @patch('close_codeql_alert.requests.Session')
    def test_closer_dry_run(self, mock_session):
        """Test dry run mode doesn't make API calls."""
        closer = AlertCloser(
            owner="test-owner",
            repo="test-repo",
            token="test-token",
            dry_run=True,
        )

        # Should succeed without making actual API call
        success = closer.close_alert(
            alert_number=123,
            reason="fixed",
            comment="Test fix",
        )

        assert success is True
        # Verify no API call was made
        assert not mock_session.return_value.patch.called

    def test_invalid_dismissal_reason(self):
        """Test that invalid dismissal reason is rejected."""
        closer = AlertCloser(
            owner="test-owner",
            repo="test-repo",
            token="test-token",
        )

        success = closer.close_alert(
            alert_number=123,
            reason="invalid_reason",
            comment="Test",
        )

        assert success is False

    def test_build_comment_with_pr(self):
        """Test building comment with PR reference."""
        closer = AlertCloser(
            owner="test-owner",
            repo="test-repo",
            token="test-token",
        )

        comment = closer._build_comment(
            comment="Fixed vulnerability",
            pr_number=456,
            commit_sha="abc123def",
        )

        assert "Fixed vulnerability" in comment
        assert "#456" in comment
        assert "abc123" in comment
        assert "Closed:" in comment


class TestIntegration:
    """Integration tests for the full workflow."""

    @pytest.mark.skip("Requires live GitHub API access")
    def test_fetch_and_export_workflow(self):
        """Test fetching alerts and exporting them."""
        # This would require a real GitHub token and repo

    @pytest.mark.skip("Requires live GitHub API access")
    def test_close_alert_workflow(self):
        """Test closing an alert."""
        # This would require a real GitHub token and repo


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
