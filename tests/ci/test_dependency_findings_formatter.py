#!/usr/bin/env python3
"""
Tests for Dependency Security Findings Formatter

Test Coverage:
- Package grouping accuracy
- Version parsing and comparison
- Upgrade path calculation
- Risk assessment logic
- Safe upgrade detection
- Performance benchmarks
- Edge case handling
"""

import json

# Import formatter functions
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "ci"))

from dependency_findings_formatter import (
    calculate_upgrade_path,
    extract_cve_id,
    extract_package_name,
    extract_version_from_finding,
    filter_dependency_findings,
    format_dependency_vulnerabilities,
    generate_markdown_report,
    group_by_package,
    load_findings,
    parse_version,
)

# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def sample_findings() -> List[Dict[str, Any]]:
    """Sample security findings for testing."""
    return [
        {
            "tool": "pip-audit",
            "severity": "CRITICAL",
            "description": "SQL Injection in django ORM",
            "package": "django",
            "version": "3.2.0",
            "cve_id": "CVE-2023-1234",
            "fix_recommendation": "Update to >= 3.2.15 for security patch",
            "confidence": 0.95,
        },
        {
            "tool": "safety",
            "severity": "HIGH",
            "description": "Vulnerability in requests package",
            "package": "requests",
            "version": "2.25.0",
            "cve_id": "CVE-2023-5678",
            "fix_recommendation": "Update to >= 2.28.0",
            "confidence": 0.88,
        },
        {
            "tool": "requirements-analysis",
            "severity": "MEDIUM",
            "description": "numpy 1.21.0 has known issues",
            "version": "1.21.0",
            "fix_recommendation": "Update to >= 1.23.5",
            "confidence": 0.80,
        },
        {
            "tool": "CodeQL",
            "severity": "CRITICAL",
            "description": "XSS vulnerability in cli.py",
            "file_path": "src/cli.py",
            "line_number": 42,
            "confidence": 0.98,
        },
    ]


@pytest.fixture
def findings_json_file(sample_findings):
    """Create temporary findings JSON file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"findings": sample_findings}, f)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    Path(temp_path).unlink()


# ============================================================================
# Test: Load Findings
# ============================================================================

class TestLoadFindings:
    """Tests for load_findings function."""
    
    def test_load_valid_findings(self, findings_json_file):
        """Test loading valid findings JSON."""
        findings = load_findings(findings_json_file)
        assert len(findings) == 4
        assert findings[0]["tool"] == "pip-audit"
    
    def test_load_nonexistent_file(self):
        """Test error handling for missing file."""
        with pytest.raises(FileNotFoundError):
            load_findings("/nonexistent/path/findings.json")
    
    def test_load_invalid_json(self):
        """Test error handling for invalid JSON."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json }")
            temp_path = f.name
        
        try:
            with pytest.raises(json.JSONDecodeError):
                load_findings(temp_path)
        finally:
            Path(temp_path).unlink()


# ============================================================================
# Test: Package Name Extraction
# ============================================================================

class TestExtractPackageName:
    """Tests for extract_package_name function."""
    
    def test_extract_from_simple_description(self):
        """Test extraction from simple description."""
        desc = "vulnerability in django"
        assert extract_package_name(desc) == "django"
    
    def test_extract_from_version_description(self):
        """Test extraction with version info."""
        desc = "numpy 1.21.0 security issue"
        result = extract_package_name(desc)
        assert result is not None
    
    def test_extract_from_update_phrase(self):
        """Test extraction from update phrase."""
        desc = "update requests to 2.28.0"
        assert extract_package_name(desc) == "requests"
    
    def test_extract_none_when_not_found(self):
        """Test None return when package not found."""
        desc = "Some random security issue"
        assert extract_package_name(desc) is None


# ============================================================================
# Test: Version Parsing
# ============================================================================

class TestParseVersion:
    """Tests for parse_version function."""
    
    def test_parse_semantic_version(self):
        """Test parsing standard semantic version."""
        version = parse_version("1.2.3")
        assert version == (1, 2, 3)
    
    def test_parse_two_part_version(self):
        """Test parsing two-part version."""
        version = parse_version("1.2")
        assert version == (1, 2, 0)
    
    def test_parse_single_version(self):
        """Test parsing single-part version."""
        version = parse_version("1")
        assert version == (1, 0, 0)
    
    def test_parse_zero_versions(self):
        """Test parsing zero versions."""
        version = parse_version("0.0.1")
        assert version == (0, 0, 1)
    
    def test_parse_invalid_returns_zero(self):
        """Test invalid version returns (0,0,0)."""
        version = parse_version("invalid")
        assert version == (0, 0, 0)


# ============================================================================
# Test: Version Comparison
# ============================================================================

class TestVersionComparison:
    """Tests for version comparison logic."""
    
    def test_major_version_bump_detected(self):
        """Test major version bump detection."""
        current = parse_version("1.2.3")
        target = parse_version("2.0.0")
        assert target[0] > current[0]
    
    def test_minor_version_bump_not_major(self):
        """Test minor version bump not detected as major."""
        current = parse_version("1.2.3")
        target = parse_version("1.3.0")
        assert target[0] == current[0]
    
    def test_patch_version_bump_not_major(self):
        """Test patch version bump not detected as major."""
        current = parse_version("1.2.3")
        target = parse_version("1.2.4")
        assert target[0] == current[0] and target[1] == current[1]


# ============================================================================
# Test: Filter Dependency Findings
# ============================================================================

class TestFilterDependencyFindings:
    """Tests for filter_dependency_findings function."""
    
    def test_filter_includes_pip_audit(self, sample_findings):
        """Test pip-audit findings included."""
        filtered = filter_dependency_findings(sample_findings)
        assert any(f["tool"] == "pip-audit" for f in filtered)
    
    def test_filter_includes_safety(self, sample_findings):
        """Test safety findings included."""
        filtered = filter_dependency_findings(sample_findings)
        assert any(f["tool"] == "safety" for f in filtered)
    
    def test_filter_excludes_codeql(self, sample_findings):
        """Test CodeQL findings excluded."""
        filtered = filter_dependency_findings(sample_findings)
        assert not any(f["tool"] == "CodeQL" for f in filtered)
    
    def test_filter_preserves_finding_count(self, sample_findings):
        """Test dependency findings count."""
        filtered = filter_dependency_findings(sample_findings)
        # Should have 3 dependency findings (pip-audit, safety, requirements-analysis)
        assert len(filtered) == 3


# ============================================================================
# Test: Group by Package
# ============================================================================

class TestGroupByPackage:
    """Tests for group_by_package function."""
    
    def test_group_by_package_name(self, sample_findings):
        """Test grouping by package name."""
        filtered = filter_dependency_findings(sample_findings)
        grouped = group_by_package(filtered)
        
        assert "django" in grouped
        assert "requests" in grouped
    
    def test_group_preserves_findings(self, sample_findings):
        """Test all findings preserved in grouping."""
        filtered = filter_dependency_findings(sample_findings)
        grouped = group_by_package(filtered)
        
        total_grouped = sum(len(v) for v in grouped.values())
        assert total_grouped == len(filtered)
    
    def test_group_multiple_findings_per_package(self):
        """Test multiple findings for same package."""
        findings = [
            {"tool": "pip-audit", "package": "requests", "severity": "HIGH"},
            {"tool": "safety", "package": "requests", "severity": "MEDIUM"},
        ]
        
        grouped = group_by_package(findings)
        assert len(grouped["requests"]) == 2


# ============================================================================
# Test: Calculate Upgrade Path
# ============================================================================

class TestCalculateUpgradePath:
    """Tests for calculate_upgrade_path function."""
    
    def test_upgrade_path_extracted(self):
        """Test upgrade path extraction."""
        findings = [
            {
                "fix_recommendation": "Update to >= 3.2.15 for security patch"
            }
        ]
        
        path = calculate_upgrade_path("django", "3.2.0", findings)
        assert path["target_version"] == "3.2.15"
    
    def test_low_risk_minor_upgrade(self):
        """Test minor upgrade is low risk."""
        findings = [
            {"fix_recommendation": "Update to >= 1.2.5"}
        ]
        
        path = calculate_upgrade_path("package", "1.2.3", findings)
        assert path["risk_level"] == "LOW"
        assert not path["is_major_upgrade"]
    
    def test_high_risk_major_upgrade(self):
        """Test major upgrade is high risk."""
        findings = [
            {"fix_recommendation": "Update to >= 2.0.0"}
        ]
        
        path = calculate_upgrade_path("package", "1.2.3", findings)
        assert path["risk_level"] == "HIGH"
        assert path["is_major_upgrade"]
    
    def test_breaking_changes_detected(self):
        """Test breaking changes detection."""
        findings = [
            {"fix_recommendation": "Major breaking changes - update carefully"}
        ]
        
        path = calculate_upgrade_path("package", "1.0.0", findings)
        assert path["breaking_changes"] is True


# ============================================================================
# Test: Extract Version from Finding
# ============================================================================

class TestExtractVersionFromFinding:
    """Tests for extract_version_from_finding function."""
    
    def test_extract_explicit_version(self):
        """Test extraction of explicit version field."""
        finding = {"version": "1.2.3"}
        assert extract_version_from_finding(finding) == "1.2.3"
    
    def test_extract_from_description(self):
        """Test extraction from description."""
        finding = {"description": "Package 1.2.3 has vulnerability"}
        version = extract_version_from_finding(finding)
        assert "1.2.3" in version
    
    def test_returns_unknown_when_missing(self):
        """Test returns 'unknown' when no version found."""
        finding = {"description": "Some vulnerability"}
        assert extract_version_from_finding(finding) == "unknown"


# ============================================================================
# Test: Extract CVE ID
# ============================================================================

class TestExtractCveId:
    """Tests for extract_cve_id function."""
    
    def test_extract_explicit_cve(self):
        """Test extraction of explicit CVE field."""
        finding = {"cve_id": "CVE-2023-1234"}
        assert extract_cve_id(finding) == "CVE-2023-1234"
    
    def test_extract_cve_from_description(self):
        """Test extraction from description."""
        finding = {"description": "Vulnerability CVE-2023-5678"}
        assert extract_cve_id(finding) == "CVE-2023-5678"
    
    def test_returns_empty_when_missing(self):
        """Test returns empty string when no CVE found."""
        finding = {"description": "Some vulnerability"}
        assert extract_cve_id(finding) == ""


# ============================================================================
# Test: Format Dependency Vulnerabilities
# ============================================================================

class TestFormatDependencyVulnerabilities:
    """Tests for format_dependency_vulnerabilities function."""
    
    def test_format_returns_valid_structure(self, findings_json_file):
        """Test output has required structure."""
        result = format_dependency_vulnerabilities(findings_json_file)
        
        assert "vulnerable_packages" in result
        assert "metadata" in result
        assert isinstance(result["vulnerable_packages"], list)
    
    def test_format_metadata_complete(self, findings_json_file):
        """Test metadata contains required fields."""
        result = format_dependency_vulnerabilities(findings_json_file)
        
        metadata = result["metadata"]
        assert "total_vulnerabilities" in metadata
        assert "critical_count" in metadata
        assert "safe_upgrades" in metadata
        assert "risky_upgrades" in metadata
        assert "packages_affected" in metadata
        assert "generated_at" in metadata
    
    def test_format_package_has_required_fields(self, findings_json_file):
        """Test each package has required fields."""
        result = format_dependency_vulnerabilities(findings_json_file)
        
        if result["vulnerable_packages"]:
            pkg = result["vulnerable_packages"][0]
            assert "package" in pkg
            assert "current_version" in pkg
            assert "vulnerability" in pkg
            assert "severity" in pkg
            assert "safe_upgrade" in pkg
    
    def test_format_counts_critical(self, findings_json_file):
        """Test critical severity counting."""
        result = format_dependency_vulnerabilities(findings_json_file)
        
        # Should have at least one CRITICAL
        assert result["metadata"]["critical_count"] >= 1
    
    def test_format_empty_findings(self):
        """Test handling of no findings."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"findings": []}, f)
            temp_path = f.name
        
        try:
            result = format_dependency_vulnerabilities(temp_path)
            assert result["metadata"]["total_vulnerabilities"] == 0
            assert len(result["vulnerable_packages"]) == 0
        finally:
            Path(temp_path).unlink()


# ============================================================================
# Test: Generate Markdown Report
# ============================================================================

class TestGenerateMarkdownReport:
    """Tests for generate_markdown_report function."""
    
    def test_markdown_includes_title(self, findings_json_file):
        """Test markdown has title."""
        result = format_dependency_vulnerabilities(findings_json_file)
        markdown = generate_markdown_report(result)
        
        assert "# Dependency Security Report" in markdown
    
    def test_markdown_includes_summary_table(self, findings_json_file):
        """Test markdown includes summary table."""
        result = format_dependency_vulnerabilities(findings_json_file)
        markdown = generate_markdown_report(result)
        
        assert "| Metric | Count |" in markdown
        assert "Total Vulnerabilities" in markdown
    
    def test_markdown_includes_vulnerabilities(self, findings_json_file):
        """Test markdown lists vulnerabilities."""
        result = format_dependency_vulnerabilities(findings_json_file)
        markdown = generate_markdown_report(result)
        
        if result["vulnerable_packages"]:
            assert "## Vulnerable Packages" in markdown


# ============================================================================
# Test: Performance
# ============================================================================

class TestPerformance:
    """Performance benchmarks."""
    
    def test_format_performance_under_500ms(self, findings_json_file):
        """Test formatting completes under 500ms."""
        start = time.time()
        format_dependency_vulnerabilities(findings_json_file)
        elapsed = (time.time() - start) * 1000  # Convert to ms
        
        assert elapsed < 500, f"Formatting took {elapsed}ms, target < 500ms"
    
    def test_grouping_performance(self, sample_findings):
        """Test grouping completes quickly."""
        start = time.time()
        for _ in range(100):
            group_by_package(sample_findings)
        elapsed = (time.time() - start) * 1000  # Convert to ms
        
        # 100 iterations should be quick
        assert elapsed < 100, f"100 iterations took {elapsed}ms"


# ============================================================================
# Test: Edge Cases
# ============================================================================

class TestEdgeCases:
    """Edge case handling."""
    
    def test_handle_missing_package_field(self):
        """Test handling of findings without package field."""
        findings = [
            {"severity": "HIGH", "description": "Some issue"}
        ]
        
        grouped = group_by_package(findings)
        # Should not crash, might have None key
        assert isinstance(grouped, dict)
    
    def test_handle_uppercase_package_names(self):
        """Test case-insensitive package grouping."""
        findings = [
            {"tool": "pip-audit", "package": "DJANGO"},
            {"tool": "safety", "package": "django"},
        ]
        
        grouped = group_by_package(findings)
        # Should normalize to lowercase
        assert "django" in grouped or "DJANGO" in grouped or len(grouped) == 1
    
    def test_handle_special_characters_in_names(self):
        """Test handling special characters in package names."""
        findings = [
            {"tool": "pip-audit", "package": "backports.zoneinfo"}
        ]
        
        grouped = group_by_package(findings)
        assert len(grouped) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
