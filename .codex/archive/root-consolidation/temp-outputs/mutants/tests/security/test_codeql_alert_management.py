#         assert ", "Condition must be true"
#         assert "Summary Statistics" in content, "Content must not be empty"
#         assert "critical" in content.lower(), "Content must not be empty"
# 
#                 rule_id="test-rule",
#                 severity="low",
#                 state="open",
#                 file_path="test.py",
#                 line_start=1,
#                 line_end=1,
#                 description="Test alert",
#                 created_at="2026-01-26T12:00:00Z",
#                 html_url="https://test.com",
#             )
#         ]
# import pytest
#         content = output_file.read_text()
#         assert ", "Condition must be true"
#         assert "Summary Statistics" in content, "Content must not be empty"
#         assert "critical" in content.lower(), "Content must not be empty"
#     @patch("fetch_codeql_alerts.requests.Session")
#     def test_fetcher_without_token_warning(self, mock_session):
# from fetch_codeql_alerts import (
#     AlertExporter,
#     CodeQLAlertFetcher,
#     CodeScanningAlert,
# )
#         assert ", "Condition must be true"
#         assert "Summary Statistics" in content, "Content must not be empty"
#         assert "critical" in content.lower(), "Content must not be empty"
#         assert fetcher.token == "", "token is not valid"
#     def test_alert_creation(self):
#     def test_alert_creation(self):
#         """Test creating a CodeScanningAlert."""
#         alert = CodeScanningAlert(
#             alert_number=123,
#             rule_id="py/sql-injection",
#             severity="high",
#             state="open",
#             file_path="src/database.py",
#             line_start=45,
#             line_end=48,
#             description="SQL injection vulnerability",
#             created_at="2026-01-26T10:00:00Z",
#             html_url="https://github.com/test/test/security/code-scanning/123",
#             cwe_id="CWE-89",
#         )
#         assert alert.alert_number == 123, "alert_number is not valid"
#         assert alert.severity == "high", "severity is not valid"
#         assert alert.cwe_id == "CWE-89", "cwe_id is not valid"
# 
#     def test_alert_to_dict(self):
#     def test_alert_to_dict(self):
#         """Test converting alert to dictionary."""
#         alert = CodeScanningAlert(
#             alert_number=456,
#             rule_id="py/xss",
#             severity="medium",
#             state="open",
#             file_path="src/web.py",
#             line_start=10,
#             line_end=10,
#             description="Cross-site scripting",
#             created_at="2026-01-26T11:00:00Z",
#             html_url="https://github.com/test/test/security/code-scanning/456",
#         )
#         data = alert.to_dict()
#         assert isinstance(data, dict)
#         assert data["alert_number"] == 456, "Data must not be empty"
#         assert data["rule_id"] == "py/xss", "Data must not be empty"
#         assert "metadata" not in data, "Data must not be empty"
#         content = output_file.read_text()
#         assert ", "Condition must be true"
#         assert "Summary Statistics" in content, "Content must not be empty"
#         assert "critical" in content.lower(), "Content must not be empty"
#         output_file = tmp_path / "test_alerts.json"
#         AlertExporter.export_json(alerts, output_file)
#     def test_fetcher_initialization(self, mock_session):
#     def test_fetcher_initialization(self, mock_session):
#         """Test initializing the fetcher."""
#         fetcher = CodeQLAlertFetcher(
#             owner="test-owner",
#             repo="test-repo",
#             token="test-token",
#         )
#         assert fetcher.owner == "test-owner", "owner is not valid"
#         assert fetcher.repo == "test-repo", "repo is not valid"
#         assert fetcher.token == "test-token", "token is not valid"
# 
#     @patch("fetch_codeql_alerts.requests.Session")
#     def test_fetcher_without_token_warning(self, mock_session):
#     def test_fetcher_without_token_warning(self, mock_session):
#         """Test fetcher logs warning without token."""
#         fetcher = CodeQLAlertFetcher(
#             owner="test-owner",
#             repo="test-repo",
#             token="",
#         )
#         assert fetcher.token == "", "token is not valid"
#         assert fetcher.token == "", "token is not valid"
# 
#     def test_extract_cwe_id(self):
#     def test_extract_cwe_id(self):
#         """Test extracting CWE ID from rule tags."""
#         fetcher = CodeQLAlertFetcher("owner", "repo", "token")
#         rule = {"tags": ["security", "external/cwe/cwe-89"]}
#         cwe = fetcher._extract_cwe_id(rule)
#         assert cwe == "CWE-89", "cwe is not valid"
# 
#         rule_no_cwe = {"tags": ["security"]}
#         cwe_none = fetcher._extract_cwe_id(rule_no_cwe)
#         assert cwe_none is None, "cwe_none is not valid"
# 
#     def test_determine_category(self):
#     def test_determine_category(self):
#         """Test categorizing vulnerabilities by rule ID."""
#         fetcher = CodeQLAlertFetcher("owner", "repo", "token")
#         assert fetcher._determine_category("py/sql-injection") == "injection", "Condition must be true"
#         assert fetcher._determine_category("py/path-traversal") == "path-traversal", "Condition must be true"
#         assert fetcher._determine_category("py/weak-crypto") == "cryptography", "Condition must be true"
#         assert fetcher._determine_category("py/broken-auth") == "authentication", "Condition must be true"
#         assert fetcher._determine_category("py/unknown") == "security", "Condition must be true"
#         content = output_file.read_text()
#         assert ", "Condition must be true"
#         assert "Summary Statistics" in content, "Content must not be empty"
#         assert "critical" in content.lower(), "Content must not be empty"
#         ]
#     def test_export_json(self, tmp_path):
#     def test_export_json(self, tmp_path):
#         """Test exporting alerts to JSON."""
#         alerts = [
#             CodeScanningAlert(
#                 alert_number=1,
#                 rule_id="test-rule",
#                 severity="low",
#                 state="open",
#                 file_path="test.py",
#                 line_start=1,
#                 line_end=1,
#                 description="Test alert",
#                 created_at="2026-01-26T12:00:00Z",
#                 html_url="https://test.com",
#             )
#         ]
#         output_file = tmp_path / "test_alerts.json"
#         AlertExporter.export_json(alerts, output_file)
# 
#         assert output_file.exists(), "Condition must be true"
#         with open(output_file) as f:
#             data = json.load(f)
# 
#         assert data["total_alerts"] == 1, "Data must not be empty"
#         assert len(data["alerts"]) == 1, "Collection must not be empty"
#         assert data["alerts"][0]["alert_number"] == 1, "Data must not be empty"
# 
#     def test_export_csv(self, tmp_path):
#     def test_export_csv(self, tmp_path):
#         """Test exporting alerts to CSV."""
#         alerts = [
#             CodeScanningAlert(
#                 alert_number=2,
#                 rule_id="test-rule-2",
#                 severity="high",
#                 state="open",
#                 file_path="test2.py",
#                 line_start=10,
#                 line_end=12,
#                 description="Test alert 2",
#                 created_at="2026-01-26T13:00:00Z",
#                 html_url="https://test.com/2",
#             )
#         ]
#         output_file = tmp_path / "test_alerts.csv"
#         AlertExporter.export_csv(alerts, output_file)
# 
#         assert output_file.exists(), "Condition must be true"
#         content = output_file.read_text()
#         assert "alert_number" in content, "Content must not be empty"
#         assert "test-rule-2" in content, "Content must not be empty"
# 
#     def test_export_markdown(self, tmp_path):
#     def test_export_markdown(self, tmp_path):
#         """Test exporting alerts to Markdown."""
#         alerts = [
#             CodeScanningAlert(
#                 alert_number=3,
#                 rule_id="test-rule-3",
#                 severity="critical",
#                 state="open",
#                 file_path="test3.py",
#                 line_start=20,
#                 line_end=25,
#                 description="Test alert 3",
#                 created_at="2026-01-26T14:00:00Z",
#                 html_url="https://test.com/3",
#             )
#         ]
#         output_file = tmp_path / "test_alerts.md"
#         AlertExporter.export_markdown(alerts, output_file)
# 
#         assert output_file.exists(), "Condition must be true"
#         content = output_file.read_text()
#         assert ", "Condition must be true"
#         assert "Summary Statistics" in content, "Content must not be empty"
#         assert "critical" in content.lower(), "Content must not be empty"
#         assert "Fixed vulnerability" in comment, "Condition must be true"
#         assert ", "Condition must be true"
#         assert "abc123" in comment, "Condition must be true"
#         assert "Closed:" in comment, "Condition must be true"


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
