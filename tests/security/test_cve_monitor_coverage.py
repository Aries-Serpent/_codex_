"""
Tests for src/codex_ml/security/cve_monitor.py

This module contains comprehensive tests for the CVE monitoring system.
Covers CVEEntry, CVEDatabase, and vulnerability checking functionality.

Test Coverage Target: 15+ tests for ~80% coverage of cve_monitor module.

Created: 2026-01-18 (Phase 14.2)
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

import pytest

# Import module under test
try:
    from codex_ml.security.cve_monitor import CVEDatabase, CVEEntry
    CVE_MONITOR_AVAILABLE = True
except ImportError:
    CVE_MONITOR_AVAILABLE = False


# Skip all tests if module not available
pytestmark = pytest.mark.skipif(
    not CVE_MONITOR_AVAILABLE,
    reason="codex_ml.security.cve_monitor not available"
)


# =============================================================================
# CVEEntry Tests
# =============================================================================


class TestCVEEntry:
    """Tests for CVEEntry dataclass."""

    def test_basic_creation(self):
        """Test basic CVEEntry creation."""
        cve = CVEEntry(
            cve_id="CVE-2024-1234",
            severity="HIGH",
            package="requests",
            affected_versions=["2.25.0", "2.25.1"],
        )
        assert cve.cve_id == "CVE-2024-1234"
        assert cve.severity == "HIGH"
        assert cve.package == "requests"
        assert cve.affected_versions == ["2.25.0", "2.25.1"]

    def test_full_creation(self):
        """Test CVEEntry creation with all fields."""
        cve = CVEEntry(
            cve_id="CVE-2024-5678",
            severity="CRITICAL",
            package="flask",
            affected_versions=["1.0.0", "1.0.1", "1.0.2"],
            fixed_in="1.0.3",
            description="Security vulnerability in Flask",
            published="2024-01-15",
        )
        assert cve.fixed_in == "1.0.3"
        assert cve.description == "Security vulnerability in Flask"
        assert cve.published == "2024-01-15"

    def test_default_values(self):
        """Test CVEEntry default values."""
        cve = CVEEntry(
            cve_id="CVE-2024-0001",
            severity="LOW",
            package="test-pkg",
            affected_versions=["1.0.0"],
        )
        assert cve.fixed_in is None
        assert cve.description == ""
        assert cve.published == ""

    def test_affects_true(self):
        """Test affects method returns True for affected version."""
        cve = CVEEntry(
            cve_id="CVE-2024-1111",
            severity="MEDIUM",
            package="vulnerable-pkg",
            affected_versions=["1.0.0", "1.0.1", "1.1.0"],
        )
        assert cve.affects("1.0.0") is True
        assert cve.affects("1.1.0") is True

    def test_affects_false(self):
        """Test affects method returns False for unaffected version."""
        cve = CVEEntry(
            cve_id="CVE-2024-1111",
            severity="MEDIUM",
            package="vulnerable-pkg",
            affected_versions=["1.0.0", "1.0.1"],
        )
        assert cve.affects("2.0.0") is False
        assert cve.affects("1.0.2") is False

    def test_severity_levels(self):
        """Test different severity levels."""
        severities = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        for severity in severities:
            cve = CVEEntry(
                cve_id=f"CVE-2024-{severity}",
                severity=severity,
                package="test",
                affected_versions=["1.0"],
            )
            assert cve.severity == severity


# =============================================================================
# CVEDatabase Tests
# =============================================================================


class TestCVEDatabase:
    """Tests for CVEDatabase dataclass."""

    def test_empty_database(self):
        """Test empty database creation."""
        db = CVEDatabase()
        assert db.entries == {}
        assert db.last_updated == ""
        assert db.checksum == ""

    def test_add_single_cve(self):
        """Test adding a single CVE to database."""
        db = CVEDatabase()
        cve = CVEEntry(
            cve_id="CVE-2024-0001",
            severity="HIGH",
            package="requests",
            affected_versions=["2.25.0"],
        )
        db.add_cve(cve)
        
        assert "requests" in db.entries
        assert len(db.entries["requests"]) == 1
        assert db.entries["requests"][0].cve_id == "CVE-2024-0001"

    def test_add_multiple_cves_same_package(self):
        """Test adding multiple CVEs for the same package."""
        db = CVEDatabase()
        
        cve1 = CVEEntry(
            cve_id="CVE-2024-0001",
            severity="HIGH",
            package="requests",
            affected_versions=["2.25.0"],
        )
        cve2 = CVEEntry(
            cve_id="CVE-2024-0002",
            severity="CRITICAL",
            package="requests",
            affected_versions=["2.26.0"],
        )
        
        db.add_cve(cve1)
        db.add_cve(cve2)
        
        assert len(db.entries["requests"]) == 2

    def test_add_cves_different_packages(self):
        """Test adding CVEs for different packages."""
        db = CVEDatabase()
        
        cve1 = CVEEntry(
            cve_id="CVE-2024-0001",
            severity="HIGH",
            package="requests",
            affected_versions=["2.25.0"],
        )
        cve2 = CVEEntry(
            cve_id="CVE-2024-0002",
            severity="MEDIUM",
            package="flask",
            affected_versions=["1.0.0"],
        )
        
        db.add_cve(cve1)
        db.add_cve(cve2)
        
        assert "requests" in db.entries
        assert "flask" in db.entries

    def test_checksum_updates_on_add(self):
        """Test that checksum is updated when CVE is added."""
        db = CVEDatabase()
        initial_checksum = db.checksum
        
        cve = CVEEntry(
            cve_id="CVE-2024-0001",
            severity="HIGH",
            package="test",
            affected_versions=["1.0.0"],
        )
        db.add_cve(cve)
        
        assert db.checksum != initial_checksum
        assert len(db.checksum) == 16  # SHA256 truncated to 16 chars

    def test_last_updated_changes(self):
        """Test that last_updated is set when CVE is added."""
        db = CVEDatabase()
        assert db.last_updated == ""
        
        cve = CVEEntry(
            cve_id="CVE-2024-0001",
            severity="HIGH",
            package="test",
            affected_versions=["1.0.0"],
        )
        db.add_cve(cve)
        
        assert db.last_updated != ""
        # Verify it's a valid ISO timestamp
        datetime.fromisoformat(db.last_updated)

    def test_check_package_with_vulnerability(self):
        """Test checking a vulnerable package."""
        db = CVEDatabase()
        cve = CVEEntry(
            cve_id="CVE-2024-0001",
            severity="HIGH",
            package="requests",
            affected_versions=["2.25.0", "2.25.1"],
        )
        db.add_cve(cve)
        
        vulns = db.check_package("requests", "2.25.0")
        assert len(vulns) == 1
        assert vulns[0].cve_id == "CVE-2024-0001"

    def test_check_package_no_vulnerability(self):
        """Test checking a package without vulnerabilities."""
        db = CVEDatabase()
        cve = CVEEntry(
            cve_id="CVE-2024-0001",
            severity="HIGH",
            package="requests",
            affected_versions=["2.25.0"],
        )
        db.add_cve(cve)
        
        vulns = db.check_package("requests", "2.26.0")
        assert len(vulns) == 0

    def test_check_package_unknown(self):
        """Test checking an unknown package."""
        db = CVEDatabase()
        vulns = db.check_package("unknown-package", "1.0.0")
        assert len(vulns) == 0

    def test_check_all_dependencies(self):
        """Test checking all dependencies at once."""
        db = CVEDatabase()
        
        cve1 = CVEEntry(
            cve_id="CVE-2024-0001",
            severity="HIGH",
            package="requests",
            affected_versions=["2.25.0"],
        )
        cve2 = CVEEntry(
            cve_id="CVE-2024-0002",
            severity="CRITICAL",
            package="flask",
            affected_versions=["1.0.0"],
        )
        db.add_cve(cve1)
        db.add_cve(cve2)
        
        dependencies = {
            "requests": "2.25.0",  # Vulnerable
            "flask": "2.0.0",      # Not vulnerable
            "django": "4.0.0",     # Unknown
        }
        
        results = db.check_all(dependencies)
        
        assert "requests" in results
        assert "flask" not in results
        assert "django" not in results

    def test_to_dict(self):
        """Test converting database to dictionary."""
        db = CVEDatabase()
        cve = CVEEntry(
            cve_id="CVE-2024-0001",
            severity="HIGH",
            package="requests",
            affected_versions=["2.25.0"],
            fixed_in="2.26.0",
        )
        db.add_cve(cve)
        
        data = db.to_dict()
        
        assert "entries" in data
        assert "last_updated" in data
        assert "requests" in data["entries"]

    def test_from_dict(self):
        """Test creating database from dictionary."""
        data = {
            "entries": {
                "requests": [
                    {
                        "cve_id": "CVE-2024-0001",
                        "severity": "HIGH",
                        "affected_versions": ["2.25.0"],
                        "fixed_in": "2.26.0",
                    }
                ]
            },
            "last_updated": "2024-01-15T12:00:00",
        }
        
        db = CVEDatabase.from_dict(data)
        
        assert db.last_updated == "2024-01-15T12:00:00"
        assert "requests" in db.entries
        assert db.entries["requests"][0].cve_id == "CVE-2024-0001"

    def test_roundtrip_dict(self):
        """Test roundtrip to/from dictionary."""
        db = CVEDatabase()
        cve = CVEEntry(
            cve_id="CVE-2024-0001",
            severity="HIGH",
            package="requests",
            affected_versions=["2.25.0", "2.25.1"],
            fixed_in="2.26.0",
        )
        db.add_cve(cve)
        
        # Convert to dict and back
        data = db.to_dict()
        restored = CVEDatabase.from_dict(data)
        
        assert "requests" in restored.entries
        assert restored.entries["requests"][0].cve_id == "CVE-2024-0001"


# =============================================================================
# Integration Tests
# =============================================================================


class TestCVEDatabaseIntegration:
    """Integration tests for CVE database functionality."""

    def test_realistic_vulnerability_check(self):
        """Test realistic vulnerability checking scenario."""
        db = CVEDatabase()
        
        # Add several known CVEs
        cves = [
            CVEEntry(
                cve_id="CVE-2021-33503",
                severity="HIGH",
                package="urllib3",
                affected_versions=["1.26.0", "1.26.1", "1.26.2"],
                fixed_in="1.26.5",
                description="ReDoS vulnerability",
            ),
            CVEEntry(
                cve_id="CVE-2022-23491",
                severity="MEDIUM",
                package="certifi",
                affected_versions=["2022.5.18.1", "2022.6.15"],
                fixed_in="2022.12.7",
            ),
            CVEEntry(
                cve_id="CVE-2023-32681",
                severity="HIGH",
                package="requests",
                affected_versions=["2.28.0", "2.28.1"],
                fixed_in="2.31.0",
            ),
        ]
        
        for cve in cves:
            db.add_cve(cve)
        
        # Check project dependencies
        project_deps = {
            "requests": "2.28.1",     # Vulnerable
            "urllib3": "1.26.5",      # Fixed version
            "certifi": "2023.1.1",    # Not affected
        }
        
        vulns = db.check_all(project_deps)
        
        # Only requests should be flagged
        assert "requests" in vulns
        assert "urllib3" not in vulns
        assert "certifi" not in vulns

    def test_multiple_vulns_same_package(self):
        """Test package with multiple vulnerabilities."""
        db = CVEDatabase()
        
        # Add multiple CVEs for same package
        cve1 = CVEEntry(
            cve_id="CVE-2024-0001",
            severity="HIGH",
            package="vulnerable-lib",
            affected_versions=["1.0.0"],
        )
        cve2 = CVEEntry(
            cve_id="CVE-2024-0002",
            severity="CRITICAL",
            package="vulnerable-lib",
            affected_versions=["1.0.0", "1.0.1"],
        )
        db.add_cve(cve1)
        db.add_cve(cve2)
        
        vulns = db.check_package("vulnerable-lib", "1.0.0")
        
        assert len(vulns) == 2
        cve_ids = {v.cve_id for v in vulns}
        assert "CVE-2024-0001" in cve_ids
        assert "CVE-2024-0002" in cve_ids
