#!/usr/bin/env python3
"""
Unit tests for Security Cache Manager
"""

import json
from datetime import datetime, timezone

import pytest

from scripts.ci.security_cache_manager import SecurityCacheManager
from scripts.ci.security_findings_trend_analyzer import SecurityFindingsTrendAnalyzer


@pytest.fixture
def temp_cache_dir(tmp_path):
    """Create temporary cache directory"""
    return tmp_path / "security-cache" # pragma: allowlist secret


@pytest.fixture
def sample_findings_json(tmp_path):
    """Create sample findings JSON"""
    findings = {
        "scan_metadata": {
            "repository": "Aries-Serpent/_codex_",
            "commit": "abc123",
            "run_id": "12345",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
        "summary": {
            "total_findings": 10,
            "critical_count": 2,
            "high_count": 3,
            "medium_count": 4,
            "low_count": 1,
        },
        "finding_index": [
            {
                "id": "CODEQL-CWE-79-001",
                "tool": "codeql",
                "cwe_id": "CWE-79",
                "severity": "CRITICAL",
                "file": "codex/cli.py",
                "line": 125,
            },
            {
                "id": "CODEQL-CWE-79-002",
                "tool": "codeql",
                "cwe_id": "CWE-79",
                "severity": "HIGH",
                "file": "codex/api.py",
                "line": 45,
            },
            {
                "id": "SEMGREP-CWE-22-001",
                "tool": "semgrep",
                "cwe_id": "CWE-22",
                "severity": "HIGH",
                "file": "codex/utils.py",
                "line": 78,
            },
        ],
    }
    
    json_file = tmp_path / "findings.json"
    json_file.write_text(json.dumps(findings, indent=2))
    return json_file


class TestSecurityCacheManager:
    """Test suite for SecurityCacheManager"""

    def test_cache_manager_initialization(self, temp_cache_dir):
        """Test cache manager initialization"""
        manager = SecurityCacheManager(temp_cache_dir)
        assert temp_cache_dir.exists()
        assert (temp_cache_dir / "runs").exists()
        assert (temp_cache_dir / "index.json").exists()

    def test_cache_findings(self, temp_cache_dir, sample_findings_json):
        """Test caching findings"""
        manager = SecurityCacheManager(temp_cache_dir)
        cache_path = manager.cache_findings(
            run_id="12345",
            commit_sha="abc123def",
            findings_json_path=sample_findings_json,
            repo="Aries-Serpent/_codex_",
        )

        assert cache_path is not None
        assert cache_path.exists()
        
        # Verify cache content
        cache_data = json.loads(cache_path.read_text())
        assert cache_data["metadata"]["run_id"] == "12345"
        assert cache_data["summary"]["total_findings"] == 10
        assert cache_data["summary"]["critical_count"] == 2

    def test_index_update(self, temp_cache_dir, sample_findings_json):
        """Test index file is updated"""
        manager = SecurityCacheManager(temp_cache_dir)
        manager.cache_findings(
            run_id="12345",
            commit_sha="abc123",
            findings_json_path=sample_findings_json,
        )

        index = json.loads((temp_cache_dir / "index.json").read_text())
        assert len(index["runs"]) > 0
        assert index["runs"][0]["run_id"] == "12345"

    def test_prune_old_runs(self, temp_cache_dir, sample_findings_json):
        """Test pruning of old cached runs"""
        manager = SecurityCacheManager(temp_cache_dir)

        # Cache 35 runs (exceeds MAX_CACHED_RUNS)
        for i in range(35):
            manager.cache_findings(
                run_id=f"run-{i}",
                commit_sha=f"sha-{i}",
                findings_json_path=sample_findings_json,
            )

        # Should only have 30 runs
        cache_files = list((temp_cache_dir / "runs").glob("run-*.json"))
        assert len(cache_files) <= 30

    def test_compute_trend_deltas(self, temp_cache_dir, sample_findings_json):
        """Test trend delta computation"""
        manager = SecurityCacheManager(temp_cache_dir)

        # Cache two runs
        manager.cache_findings(
            run_id="run-1",
            commit_sha="sha-1",
            findings_json_path=sample_findings_json,
        )
        manager.cache_findings(
            run_id="run-2",
            commit_sha="sha-2",
            findings_json_path=sample_findings_json,
        )

        deltas = manager.compute_trend_deltas()
        assert "new_findings" in deltas
        assert "resolved_findings" in deltas
        assert "unchanged_findings" in deltas

    def test_get_historical_findings(self, temp_cache_dir, sample_findings_json):
        """Test historical findings retrieval"""
        manager = SecurityCacheManager(temp_cache_dir)
        manager.cache_findings(
            run_id="12345",
            commit_sha="abc123",
            findings_json_path=sample_findings_json,
        )

        findings = manager.get_historical_findings("CWE-79")
        assert len(findings) > 0
        assert all(f["cwe_id"] == "CWE-79" for f in findings)

    def test_compute_aggregate_metrics(self, temp_cache_dir, sample_findings_json):
        """Test aggregate metrics computation"""
        manager = SecurityCacheManager(temp_cache_dir)
        manager.cache_findings(
            run_id="12345",
            commit_sha="abc123",
            findings_json_path=sample_findings_json,
        )

        metrics = manager.compute_aggregate_metrics()
        assert metrics.run_count >= 1
        assert metrics.total_findings > 0
        assert metrics.avg_critical >= 0


class TestSecurityFindingsTrendAnalyzer:
    """Test suite for SecurityFindingsTrendAnalyzer"""

    def test_analyzer_initialization(self, temp_cache_dir):
        """Test analyzer initialization"""
        analyzer = SecurityFindingsTrendAnalyzer(temp_cache_dir)
        assert analyzer.cache_dir == temp_cache_dir

    def test_analyze_with_no_data(self, temp_cache_dir):
        """Test analyze with no cached data"""
        analyzer = SecurityFindingsTrendAnalyzer(temp_cache_dir)
        report = analyzer.analyze()
        assert report is None

    def test_analyze_with_data(self, temp_cache_dir, sample_findings_json):
        """Test analyze with cached data"""
        # First populate cache
        manager = SecurityCacheManager(temp_cache_dir)
        manager.cache_findings(
            run_id="run-1",
            commit_sha="sha-1",
            findings_json_path=sample_findings_json,
        )
        manager.cache_findings(
            run_id="run-2",
            commit_sha="sha-2",
            findings_json_path=sample_findings_json,
        )

        # Now analyze
        analyzer = SecurityFindingsTrendAnalyzer(temp_cache_dir)
        report = analyzer.analyze()
        
        assert report is not None
        assert report.runs_analyzed >= 2
        assert report.total_findings_span[0] > 0

    def test_generate_ascii_bar_chart(self, temp_cache_dir):
        """Test ASCII bar chart generation"""
        analyzer = SecurityFindingsTrendAnalyzer(temp_cache_dir)
        data = [("Item A", 10), ("Item B", 25), ("Item C", 15)]
        chart = analyzer._generate_ascii_bar_chart(data, max_width=40)
        
        assert "Item A" in chart
        assert "Item B" in chart
        assert "█" in chart
        assert len(chart) > 0

    def test_generate_severity_distribution(self, temp_cache_dir, sample_findings_json):
        """Test severity distribution chart"""
        manager = SecurityCacheManager(temp_cache_dir)
        manager.cache_findings(
            run_id="12345",
            commit_sha="abc123",
            findings_json_path=sample_findings_json,
        )

        analyzer = SecurityFindingsTrendAnalyzer(temp_cache_dir)
        run_list = analyzer._parse_run_metadata([
            {
                "run_id": "12345",
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "findings_count": 10,
                "critical_count": 2,
                "high_count": 3,
                "medium_count": 4,
                "low_count": 1,
            }
        ])

        distribution = analyzer._generate_severity_distribution(run_list)
        assert "CRITICAL" in distribution
        assert "HIGH" in distribution
        assert "MEDIUM" in distribution
        assert "LOW" in distribution

    def test_generate_trend_sparkline(self, temp_cache_dir):
        """Test trend sparkline generation"""
        analyzer = SecurityFindingsTrendAnalyzer(temp_cache_dir)
        counts = [10, 15, 12, 18, 14, 20, 16, 22, 19, 25]
        sparkline = analyzer._generate_trend_sparkline(counts, width=30)
        
        assert len(sparkline) > 0
        assert any(c in sparkline for c in "▁▂▃▄▅▆▇█")

    def test_generate_dashboard_markdown_no_data(self, temp_cache_dir):
        """Test dashboard generation with no data"""
        analyzer = SecurityFindingsTrendAnalyzer(temp_cache_dir)
        dashboard = analyzer.generate_dashboard_markdown(temp_cache_dir, temp_cache_dir / "dashboard.md")
        assert dashboard is None

    def test_generate_dashboard_markdown_with_data(self, temp_cache_dir, sample_findings_json):
        """Test dashboard generation with data"""
        # Populate cache
        manager = SecurityCacheManager(temp_cache_dir)
        for i in range(3):
            manager.cache_findings(
                run_id=f"run-{i}",
                commit_sha=f"sha-{i}",
                findings_json_path=sample_findings_json,
            )

        # Generate dashboard
        analyzer = SecurityFindingsTrendAnalyzer(temp_cache_dir)
        dashboard_path = temp_cache_dir / "dashboard.md"
        dashboard = analyzer.generate_dashboard_markdown(temp_cache_dir, dashboard_path)
        
        assert dashboard is not None
        assert "Security Findings Dashboard" in dashboard
        assert "7-Day Trend" in dashboard
        assert "30-Day Trend" in dashboard
        assert "Severity Distribution" in dashboard
        assert "Remediation Velocity" in dashboard
        assert dashboard_path.exists()

    def test_dashboard_markdown_contains_sections(self, temp_cache_dir, sample_findings_json):
        """Test that dashboard contains all required sections"""
        manager = SecurityCacheManager(temp_cache_dir)
        manager.cache_findings(
            run_id="12345",
            commit_sha="abc123",
            findings_json_path=sample_findings_json,
        )

        analyzer = SecurityFindingsTrendAnalyzer(temp_cache_dir)
        dashboard_path = temp_cache_dir / "dashboard.md"
        dashboard = analyzer.generate_dashboard_markdown(temp_cache_dir, dashboard_path)
        
        # Verify all required sections
        required_sections = [
            "Security Findings Dashboard",
            "Summary Stats",
            "7-Day Trend",
            "30-Day Trend",
            "Severity Distribution",
            "Top 5 Recurring Issues",
            "Remediation Velocity",
            "Top CWEs",
        ]
        
        for section in required_sections:
            assert section in dashboard, f"Missing section: {section}"

    def test_dashboard_markdown_renders_valid(self, temp_cache_dir, sample_findings_json):
        """Test that generated dashboard markdown is valid"""
        manager = SecurityCacheManager(temp_cache_dir)
        manager.cache_findings(
            run_id="12345",
            commit_sha="abc123",
            findings_json_path=sample_findings_json,
        )

        analyzer = SecurityFindingsTrendAnalyzer(temp_cache_dir)
        dashboard_path = temp_cache_dir / "dashboard.md"
        dashboard = analyzer.generate_dashboard_markdown(temp_cache_dir, dashboard_path)
        
        # Verify markdown structure
        assert dashboard.startswith("# 🛡️")
        assert "---" in dashboard
        assert dashboard.endswith("*Generated:")

    def test_generate_markdown_report(self, temp_cache_dir, sample_findings_json):
        """Test traditional markdown report generation"""
        manager = SecurityCacheManager(temp_cache_dir)
        manager.cache_findings(
            run_id="run-1",
            commit_sha="sha-1",
            findings_json_path=sample_findings_json,
        )
        manager.cache_findings(
            run_id="run-2",
            commit_sha="sha-2",
            findings_json_path=sample_findings_json,
        )

        analyzer = SecurityFindingsTrendAnalyzer(temp_cache_dir)
        report = analyzer.analyze()
        
        assert report is not None
        
        md_report = analyzer.generate_markdown_report(report)
        assert md_report is not None
        assert "Security Findings Trend Analysis Report" in md_report
        assert "Overall Trend" in md_report


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
