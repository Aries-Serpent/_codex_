#!/usr/bin/env python3
"""
Unit tests for @copilot scan-summary command parsing and response generation.

Tests the Phase 7 implementation of conversational commands for security findings.
"""

import pytest

from scripts.ci.copilot_security_agent_handoff import (
    SEVERITY_EMOJI,
    ScanSummaryQuery,
    generate_scan_summary_response,
    parse_scan_summary_command,
)


class TestParseScanSummaryCommand:
    """Test the command parser for @copilot scan-summary"""
    
    def test_basic_scan_summary_command(self):
        """Test basic @copilot scan-summary without filters"""
        comment = "Please run @copilot scan-summary"
        result = parse_scan_summary_command(comment)
        
        assert result is not None
        assert result.command == 'scan-summary'
        assert result.query_type is None
        assert result.value is None
        assert result.scope is None
    
    def test_command_not_found(self):
        """Test comment without @copilot scan-summary command"""
        comment = "This is just a regular comment without the command"
        result = parse_scan_summary_command(comment)
        
        assert result is None
    
    def test_cwe_filter(self):
        """Test CWE filter parsing"""
        comment = "@copilot scan-summary cwe:CWE-79"
        result = parse_scan_summary_command(comment)
        
        assert result is not None
        assert result.query_type == 'cwe'
        assert result.value == 'CWE-79'
    
    def test_cwe_filter_lowercase(self):
        """Test CWE filter with lowercase"""
        comment = "@copilot scan-summary cwe:cwe-22"
        result = parse_scan_summary_command(comment)
        
        assert result is not None
        assert result.query_type == 'cwe'
        assert result.value == 'cwe-22'
    
    def test_severity_filter_by_name(self):
        """Test severity filter by name"""
        comment = "@copilot scan-summary critical"
        result = parse_scan_summary_command(comment)
        
        assert result is not None
        assert result.query_type == 'severity'
        assert result.value == 'CRITICAL'
    
    def test_severity_filter_by_name_mixed_case(self):
        """Test severity filter with mixed case"""
        comment = "@copilot scan-summary HIGH"
        result = parse_scan_summary_command(comment)
        
        assert result is not None
        assert result.query_type == 'severity'
        assert result.value == 'HIGH'
    
    def test_severity_filter_explicit(self):
        """Test severity filter with explicit prefix"""
        comment = "@copilot scan-summary severity:MEDIUM"
        result = parse_scan_summary_command(comment)
        
        assert result is not None
        assert result.query_type == 'severity'
        assert result.value == 'MEDIUM'
    
    def test_file_scope(self):
        """Test file scope filter"""
        comment = "@copilot scan-summary for src/cli.py"
        result = parse_scan_summary_command(comment)
        
        assert result is not None
        assert result.scope == 'src/cli.py'
    
    def test_file_scope_directory(self):
        """Test directory scope"""
        comment = "@copilot scan-summary for src/"
        result = parse_scan_summary_command(comment)
        
        assert result is not None
        assert result.scope == 'src/'
    
    def test_package_filter(self):
        """Test package filter"""
        comment = "@copilot scan-summary package:numpy"
        result = parse_scan_summary_command(comment)
        
        assert result is not None
        assert result.query_type == 'package'
        assert result.value == 'numpy'
    
    def test_combined_filters_cwe_and_file(self):
        """Test combined CWE and file filters"""
        comment = "@copilot scan-summary cwe:CWE-79 for src/cli"
        result = parse_scan_summary_command(comment)
        
        assert result is not None
        assert result.query_type == 'cwe'
        assert result.value == 'CWE-79'
        assert result.scope == 'src/cli'
    
    def test_combined_filters_severity_and_file(self):
        """Test combined severity and file filters"""
        comment = "@copilot scan-summary critical for src/cognitive_brain"
        result = parse_scan_summary_command(comment)
        
        assert result is not None
        assert result.query_type == 'severity'
        assert result.value == 'CRITICAL'
        assert result.scope == 'src/cognitive_brain'
    
    def test_command_case_insensitive(self):
        """Test that command is case-insensitive"""
        comment = "@Copilot SCAN-SUMMARY critical"
        result = parse_scan_summary_command(comment)
        
        assert result is not None
        assert result.query_type == 'severity'
    
    def test_multiline_comment(self):
        """Test command in multiline comment"""
        comment = """
        Here's some context about the security issue.
        
        @copilot scan-summary critical
        
        Looking forward to the findings.
        """
        result = parse_scan_summary_command(comment)
        
        assert result is not None
        assert result.query_type == 'severity'
        assert result.value == 'CRITICAL'
    
    def test_file_path_with_spaces(self):
        """Test file path with multiple segments"""
        comment = "@copilot scan-summary for src/path/to/module"
        result = parse_scan_summary_command(comment)
        
        assert result is not None
        assert result.scope == 'src/path/to/module'


class TestGenerateScanSummaryResponse:
    """Test the response generator for scan-summary"""
    
    def test_empty_findings(self):
        """Test response generation with no findings"""
        findings = []
        response = generate_scan_summary_response(findings)
        
        assert "✅ No findings matched" in response
        assert "Good news" in response
    
    def test_single_finding(self):
        """Test response with a single finding"""
        findings = [
            {
                'id': '1',
                'title': 'SQL Injection',
                'severity': 'CRITICAL',
                'cwe_id': 'CWE-89',
                'tool': 'CodeQL',
                'file': 'src/db.py',
                'line': 42,
                'description': 'Unsanitized user input in SQL query'
            }
        ]
        query_info = ScanSummaryQuery(
            command='scan-summary',
            query_type='severity',
            value='CRITICAL',
            scope=None,
            raw_filters='critical'
        )
        response = generate_scan_summary_response(findings, query_info)
        
        assert "🔍 Security Scan Summary" in response
        assert "CRITICAL" in response
        assert "CWE-89" in response
        assert "SQL Injection" in response
        assert "src/db.py" in response
        assert "CodeQL" in response
    
    def test_multiple_findings_by_severity(self):
        """Test response with multiple findings of different severities"""
        findings = [
            {
                'title': 'Critical Issue',
                'severity': 'CRITICAL',
                'cwe_id': 'CWE-89',
                'tool': 'CodeQL',
                'file': 'src/a.py'
            },
            {
                'title': 'High Issue',
                'severity': 'HIGH',
                'cwe_id': 'CWE-22',
                'tool': 'Semgrep',
                'file': 'src/b.py'
            },
            {
                'title': 'Medium Issue',
                'severity': 'MEDIUM',
                'cwe_id': 'CWE-352',
                'tool': 'Safety',
                'file': 'src/c.py'
            },
        ]
        response = generate_scan_summary_response(findings)
        
        # Check summary table is present
        assert "| Severity | Count | Status |" in response
        assert "CRITICAL | 1 |" in response
        assert "HIGH | 1 |" in response
        assert "MEDIUM | 1 |" in response
    
    def test_response_includes_summary_table(self):
        """Test that response includes the severity summary table"""
        findings = [
            {
                'title': 'Test Finding',
                'severity': 'CRITICAL',
                'tool': 'CodeQL',
                'file': 'test.py'
            }
        ]
        response = generate_scan_summary_response(findings)
        
        assert "### Summary" in response
        assert "| Severity | Count | Status |" in response
        assert "|----------|-------|--------|" in response
    
    def test_response_includes_top_issues(self):
        """Test that response includes top issues section"""
        findings = [
            {
                'title': 'Issue 1',
                'severity': 'CRITICAL',
                'tool': 'CodeQL',
                'file': 'src/a.py'
            },
            {
                'title': 'Issue 2',
                'severity': 'HIGH',
                'tool': 'Semgrep',
                'file': 'src/b.py'
            }
        ]
        response = generate_scan_summary_response(findings)
        
        assert "### Top Issues" in response
        assert "Issue 1" in response
        assert "Issue 2" in response
    
    def test_response_includes_recommended_actions(self):
        """Test that response includes recommended actions section"""
        findings = [
            {
                'title': 'CWE Finding',
                'severity': 'HIGH',
                'cwe_id': 'CWE-79',
                'tool': 'CodeQL',
                'file': 'src/a.py'
            }
        ]
        response = generate_scan_summary_response(findings)
        
        assert "### Recommended Actions" in response
        assert "codeql-alert-resolution-agent" in response
    
    def test_response_includes_resource_links(self):
        """Test that response includes resource links"""
        findings = [
            {
                'title': 'Test',
                'severity': 'MEDIUM',
                'tool': 'Test',
                'file': 'test.py'
            }
        ]
        response = generate_scan_summary_response(findings)
        
        assert "View Full Dashboard" in response
        assert "View Full Report" in response
        assert ".codex/security-findings" in response
    
    def test_response_severity_emoji(self):
        """Test that response includes correct severity emojis"""
        findings = [
            {
                'title': 'Critical',
                'severity': 'CRITICAL',
                'tool': 'Test',
                'file': 'test.py'
            },
            {
                'title': 'High',
                'severity': 'HIGH',
                'tool': 'Test',
                'file': 'test.py'
            },
        ]
        response = generate_scan_summary_response(findings)
        
        assert SEVERITY_EMOJI['CRITICAL'] in response
        assert SEVERITY_EMOJI['HIGH'] in response
    
    def test_response_with_query_info(self):
        """Test response includes query information"""
        findings = [
            {
                'title': 'Finding',
                'severity': 'HIGH',
                'cwe_id': 'CWE-79',
                'tool': 'CodeQL',
                'file': 'src/test.py'
            }
        ]
        query_info = ScanSummaryQuery(
            command='scan-summary',
            query_type='cwe',
            value='CWE-79',
            scope=None,
            raw_filters='cwe:CWE-79'
        )
        response = generate_scan_summary_response(findings, query_info)
        
        assert "Query" in response
        assert "CWE-79" in response
    
    def test_response_with_cache_age(self):
        """Test response includes cache age information"""
        findings = [
            {
                'title': 'Finding',
                'severity': 'MEDIUM',
                'tool': 'Test',
                'file': 'test.py'
            }
        ]
        response = generate_scan_summary_response(findings, cache_age_minutes=30)
        
        assert "30m ago" in response
    
    def test_response_with_cache_age_hours(self):
        """Test cache age formatting in hours"""
        findings = [
            {
                'title': 'Finding',
                'severity': 'MEDIUM',
                'tool': 'Test',
                'file': 'test.py'
            }
        ]
        response = generate_scan_summary_response(findings, cache_age_minutes=120)
        
        assert "2h ago" in response
    
    def test_response_with_package_findings(self):
        """Test response with package vulnerability findings"""
        findings = [
            {
                'title': 'Numpy vulnerability',
                'severity': 'HIGH',
                'package': 'numpy',
                'version': '1.21.0',
                'tool': 'pip-audit',
                'file': 'requirements.txt'
            }
        ]
        response = generate_scan_summary_response(findings)
        
        assert "dependency-security-review-agent" in response
        assert "numpy" in response
    
    def test_response_truncates_long_descriptions(self):
        """Test that long descriptions are truncated"""
        findings = [
            {
                'title': 'Finding',
                'severity': 'MEDIUM',
                'tool': 'Test',
                'file': 'test.py',
                'description': 'A' * 200  # Very long description
            }
        ]
        response = generate_scan_summary_response(findings)
        
        # Should contain truncated description with ellipsis
        assert "A" * 100 not in response  # Not the full original
        assert "..." in response  # But has ellipsis
    
    def test_response_limits_top_findings_to_three(self):
        """Test that response shows top 3 findings"""
        findings = [
            {'title': f'Finding {i}', 'severity': 'MEDIUM', 'tool': 'Test', 'file': 'test.py'}
            for i in range(10)
        ]
        response = generate_scan_summary_response(findings)
        
        # Should show "showing 3 of 10"
        assert "showing 3 of 10" in response or "3 of 10" in response
    
    def test_response_with_file_info(self):
        """Test response includes file and line information"""
        findings = [
            {
                'title': 'Test Finding',
                'severity': 'HIGH',
                'tool': 'Semgrep',
                'file': 'src/module.py',
                'line': 42
            }
        ]
        response = generate_scan_summary_response(findings)
        
        assert "src/module.py" in response
        assert "line 42" in response


class TestIntegration:
    """Integration tests for parse and generate together"""
    
    def test_parse_and_generate_workflow(self):
        """Test complete workflow: parse command, then generate response"""
        comment = "@copilot scan-summary critical"
        findings = [
            {
                'title': 'Critical Issue',
                'severity': 'CRITICAL',
                'cwe_id': 'CWE-89',
                'tool': 'CodeQL',
                'file': 'src/app.py',
                'line': 10
            }
        ]
        
        # Parse the command
        query = parse_scan_summary_command(comment)
        assert query is not None
        
        # Generate response
        response = generate_scan_summary_response(findings, query)
        assert "🔍 Security Scan Summary" in response
        assert "CRITICAL" in response
    
    def test_parse_and_generate_no_matches(self):
        """Test workflow when no findings match the query"""
        comment = "@copilot scan-summary cwe:CWE-999"
        findings = [
            {
                'title': 'Other Issue',
                'severity': 'MEDIUM',
                'cwe_id': 'CWE-79',
                'tool': 'CodeQL',
                'file': 'src/app.py'
            }
        ]
        
        query = parse_scan_summary_command(comment)
        assert query is not None
        
        # Filter findings (simulating what would happen)
        matching = [f for f in findings if f.get('cwe_id') == query.value]
        
        response = generate_scan_summary_response(matching, query)
        assert "✅ No findings matched" in response


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
