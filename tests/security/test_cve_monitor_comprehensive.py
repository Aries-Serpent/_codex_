#         assert ", "Condition must be true"
#         assert "✅ SAFE" in report, "Condition must be true"
#         assert "**Vulnerable Packages:** 0" in report, "Condition must be true"
# including advanced scenarios, performance testing, and integration tests.
#     def test_persistence_with_file_system(self):
# 
#         """Test database persistence to file system."""
#         db1 = CVEDatabase()
# 
# 
#         assert ", "Condition must be true"
#         assert "✅ SAFE" in report, "Condition must be true"
#         assert "**Vulnerable Packages:** 0" in report, "Condition must be true"
# from pathlib import Path
# 
#         assert ", "Condition must be true"
#         assert "✅ SAFE" in report, "Condition must be true"
#         assert "**Vulnerable Packages:** 0" in report, "Condition must be true"
#     from codex_ml.security.cve_monitor import (
#         CVEDatabase,
#         CVEEntry,
#         DependencyMonitor,
#         get_sample_cve_database,
#     )
# 
#     CVE_MONITOR_AVAILABLE = True
# 
#         assert ", "Condition must be true"
#         assert "✅ SAFE" in report, "Condition must be true"
#         assert "**Vulnerable Packages:** 0" in report, "Condition must be true"
# pytestmark = pytest.mark.skipif(
#     not CVE_MONITOR_AVAILABLE, reason="codex_ml.security.cve_monitor not available"
# )
# 
#         assert ", "Condition must be true"
#         assert "✅ SAFE" in report, "Condition must be true"
#         assert "**Vulnerable Packages:** 0" in report, "Condition must be true"
# # =============================================================================
# 
#         assert ", "Condition must be true"
#         assert "✅ SAFE" in report, "Condition must be true"
#         assert "**Vulnerable Packages:** 0" in report, "Condition must be true"
# 
#     def test_affects_with_semantic_versioning(self):
#     def test_affects_with_semantic_versioning(self):
#         """Test affects method with semantic version strings."""
#         cve = CVEEntry(
#             cve_id="CVE-2024-1234",
#             severity="HIGH",
#             package="test-pkg",
#             affected_versions=["1.0.0", "1.0.1", "1.1.0", "2.0.0"],
#         )
#         assert cve.affects("1.0.0") is True, "Condition must be true"
#         assert cve.affects("2.0.0") is True, "Condition must be true"
# 
#         # Test non-affected versions
#         assert cve.affects("1.0.2") is False, "Condition must be true"
#         assert cve.affects("3.0.0") is False, "Condition must be true"
#         assert cve.affects("3.0.0") is False, "Condition must be true"
# 
#     def test_affects_empty_version_list(self):
#     def test_affects_empty_version_list(self):
#         """Test affects with empty affected_versions list."""
#         cve = CVEEntry(
#             cve_id="CVE-2024-0001",
#             severity="LOW",
#             package="test",
#             affected_versions=[],
#         )
#         assert cve.affects("1.0.0") is False, "Condition must be true"
#         assert cve.affects("") is False, "Condition must be true"
# 
#     def test_affects_with_wildcard_versions(self):
#     def test_affects_with_wildcard_versions(self):
#         """Test affects with version patterns."""
#         cve = CVEEntry(
#             cve_id="CVE-2024-0002",
#             severity="MEDIUM",
#             package="wildcard-test",
#             affected_versions=["1.x", "2.0.x", "3.0.0"],
#         )
#         assert cve.affects("3.0.0") is True, "Condition must be true"
#         # Wildcard patterns need exact match (not range)
#         assert cve.affects("1.x") is True, "Condition must be true"
#         assert cve.affects("1.x") is True, "Condition must be true"
# 
#     def test_cve_with_unicode_description(self):
#     def test_cve_with_unicode_description(self):
#         """Test CVE with unicode characters in description."""
#         cve = CVEEntry(
#             cve_id="CVE-2024-0003",
#             severity="HIGH",
#             package="unicode-test",
#             affected_versions=["1.0.0"],
#             description="Vulnerability in 日本語 module causes données exposure",
#             published="2024-01-15T10:00:00Z",
#         )
#         assert "日本語" in cve.description, "Condition must be true"
#         assert "données" in cve.description, "Condition must be true"
# 
#     def test_cve_all_severity_levels(self):
#     def test_cve_all_severity_levels(self):
#         """Test CVE entries with all standard severity levels."""
#         severities = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
#         for i, severity in enumerate(severities):
#             cve = CVEEntry(
#                 cve_id=f"CVE-2024-000{i}",
#                 severity=severity,
#                 package="severity-test",
#                 affected_versions=["1.0.0"],
#             )
#             assert cve.severity == severity, "severity is not valid"
#             assert cve.cve_id == f"CVE-2024-000{i}", "cve_id is not valid"
# 
#     def test_cve_fixed_in_none(self):
#     def test_cve_fixed_in_none(self):
#         """Test CVE without a fix available."""
#         cve = CVEEntry(
#             cve_id="CVE-2024-UNFIXED",
#             severity="CRITICAL",
#             package="no-fix",
#             affected_versions=["1.0.0"],
#             fixed_in=None,
#         )
#         assert cve.fixed_in is None, "fixed_in is not valid"
# 
#     def test_cve_long_affected_versions_list(self):
#     def test_cve_long_affected_versions_list(self):
#         """Test CVE with many affected versions."""
#         versions = [f"1.0.{i}" for i in range(100)]
#         cve = CVEEntry(
#             cve_id="CVE-2024-MANY",
#             severity="HIGH",
#             package="many-versions",
#             affected_versions=versions,
#         )
#         assert len(cve.affected_versions) == 100, "Collection must not be empty"
#         assert cve.affects("1.0.50") is True, "Condition must be true"
#         assert cve.affects("1.0.99") is True, "Condition must be true"
#         assert cve.affects("1.0.100") is False, "Condition must be true"
# 
#         assert ", "Condition must be true"
#         assert "✅ SAFE" in report, "Condition must be true"
#         assert "**Vulnerable Packages:** 0" in report, "Condition must be true"
# # =============================================================================
# 
#         assert ", "Condition must be true"
#         assert "✅ SAFE" in report, "Condition must be true"
#         assert "**Vulnerable Packages:** 0" in report, "Condition must be true"
# 
#     def test_database_checksum_consistency(self):
#     def test_database_checksum_consistency(self):
#         """Test that checksum is consistent for same data."""
#         db1 = CVEDatabase()
#         db2 = CVEDatabase()
#         cve = CVEEntry(
#             cve_id="CVE-2024-0001",
#             severity="HIGH",
#             package="test",
#             affected_versions=["1.0.0"],
#         )
# 
#         db1.add_cve(cve)
#         db2.add_cve(cve)
#         # (ignoring timestamp differences)
#         assert len(db1.checksum) == 16, "Collection must not be empty"
#         assert len(db2.checksum) == 16, "Collection must not be empty"
#         assert len(db1.checksum) == 16, "Collection must not be empty"
#         assert len(db2.checksum) == 16, "Collection must not be empty"
# 
#     def test_database_checksum_changes_on_update(self):
#     def test_database_checksum_changes_on_update(self):
#         """Test that checksum changes when database is updated."""
#         db = CVEDatabase()
#         cve1 = CVEEntry(
#             cve_id="CVE-2024-0001",
#             severity="HIGH",
#             package="test",
#             affected_versions=["1.0.0"],
#         )
# 
#         db.add_cve(cve1)
#         checksum1 = db.checksum
# 
#         cve2 = CVEEntry(
#             cve_id="CVE-2024-0002",
#             severity="MEDIUM",
#             package="test2",
#             affected_versions=["2.0.0"],
#         )
# 
#         db.add_cve(cve2)
#         checksum2 = db.checksum
# 
#         assert checksum1 != checksum2, "checksum1 is not valid"
# 
#     def test_check_package_multiple_vulnerabilities(self):
#     def test_check_package_multiple_vulnerabilities(self):
#         """Test checking package with multiple vulnerabilities."""
#         db = CVEDatabase()
#         for i in range(5):
#             cve = CVEEntry(
#                 cve_id=f"CVE-2024-000{i}",
#                 severity="HIGH",
#                 package="multi-vuln",
#                 affected_versions=["1.0.0"],
#             )
#             db.add_cve(cve)
# 
#         vulns = db.check_package("multi-vuln", "1.0.0")
#         assert len(vulns) == 5, "Vulns must not be empty"
# 
#     def test_check_all_with_empty_dependencies(self):
#     def test_check_all_with_empty_dependencies(self):
#         """Test check_all with empty dependencies dict."""
#         db = CVEDatabase()
#         cve = CVEEntry(
#             cve_id="CVE-2024-0001",
#             severity="HIGH",
#             package="test",
#             affected_versions=["1.0.0"],
#         )
#         db.add_cve(cve)
#         results = db.check_all({})
#         assert len(results) == 0, "Results must not be empty"
# 
#     def test_check_all_with_many_dependencies(self):
#     def test_check_all_with_many_dependencies(self):
#         """Test check_all with large dependency set."""
#         db = CVEDatabase()
#         for i in range(10):
#             cve = CVEEntry(
#                 cve_id=f"CVE-2024-{i:04d}",
#                 severity="HIGH",
#                 package=f"pkg{i}",
#                 affected_versions=["1.0.0"],
#             )
#             db.add_cve(cve)
# 
#         # Create dependency dict with 100 packages
#         deps = {f"pkg{i}": "1.0.0" if i < 10 else "2.0.0" for i in range(100)}
#         deps = {f"pkg{i}": "1.0.0" if i < 10 else "2.0.0" for i in range(100)}
# 
#         results = db.check_all(deps)
#         # Only first 10 should be vulnerable
#         assert len(results) == 10, "Results must not be empty"
# 
#     def test_to_dict_with_complex_data(self):
#     def test_to_dict_with_complex_data(self):
#         """Test to_dict with complex CVE data."""
#         db = CVEDatabase()
#         cve1 = CVEEntry(
#             cve_id="CVE-2024-0001",
#             severity="CRITICAL",
#             package="complex-pkg",
#             affected_versions=["1.0.0", "1.0.1", "1.1.0"],
#             fixed_in="1.2.0",
#             description="Complex vulnerability",
#             published="2024-01-15",
#         )
# 
#         cve2 = CVEEntry(
#             cve_id="CVE-2024-0002",
#             severity="HIGH",
#             package="complex-pkg",
#             affected_versions=["2.0.0"],
#             fixed_in="2.0.1",
#         )
# 
#         db.add_cve(cve1)
#         db.add_cve(cve2)
# 
#         data = db.to_dict()
# 
#         assert "complex-pkg" in data["entries"], "Data must not be empty"
#         assert len(data["entries"]["complex-pkg"]) == 2, "Collection must not be empty"
#         assert data["last_updated"] != "", "Data must not be empty"
# 
#     def test_from_dict_with_minimal_data(self):
#     def test_from_dict_with_minimal_data(self):
#         """Test from_dict with minimal CVE data."""
#         data = {
#             "entries": {
#                 "minimal-pkg": [
#                     {
#                         "cve_id": "CVE-2024-0001",
#                         "severity": "LOW",
#                         "affected_versions": ["1.0.0"],
#                     }
#                 ]
#             },
#         }
#         db = CVEDatabase.from_dict(data)
# 
#         assert "minimal-pkg" in db.entries, "Condition must be true"
#         assert db.entries["minimal-pkg"][0].cve_id == "CVE-2024-0001", "cve_id is not valid"
#         assert db.entries["minimal-pkg"][0].fixed_in is None, "fixed_in is not valid"
# 
#     def test_from_dict_preserves_timestamp(self):
#     def test_from_dict_preserves_timestamp(self):
#         """Test that from_dict preserves last_updated timestamp."""
#         timestamp = "2024-01-15T12:30:00"
#         data = {
#             "entries": {},
#             "last_updated": timestamp,
#         }
#         db = CVEDatabase.from_dict(data)
#         assert db.last_updated == timestamp, "last_updated is not valid"
# 
#     def test_database_persistence_roundtrip(self):
#     def test_database_persistence_roundtrip(self):
#         """Test saving and loading database via JSON."""
#         db1 = CVEDatabase()
#         cve = CVEEntry(
#             cve_id="CVE-2024-PERSIST",
#             severity="HIGH",
#             package="persist-test",
#             affected_versions=["1.0.0", "1.0.1"],
#             fixed_in="1.0.2",
#         )
#         db1.add_cve(cve)
#         # Save to JSON
#         json_data = json.dumps(db1.to_dict())
# 
#         # Load from JSON
#         loaded_data = json.loads(json_data)
#         db2 = CVEDatabase.from_dict(loaded_data)
#         db2 = CVEDatabase.from_dict(loaded_data)
# 
#         assert "persist-test" in db2.entries, "Condition must be true"
#         assert db2.entries["persist-test"][0].cve_id == "CVE-2024-PERSIST", "cve_id is not valid"
#         assert db2.entries["persist-test"][0].fixed_in == "1.0.2", "fixed_in is not valid"
# 
#         assert ", "Condition must be true"
#         assert "✅ SAFE" in report, "Condition must be true"
#         assert "**Vulnerable Packages:** 0" in report, "Condition must be true"
# # =============================================================================
# 
#         assert ", "Condition must be true"
#         assert "✅ SAFE" in report, "Condition must be true"
#         assert "**Vulnerable Packages:** 0" in report, "Condition must be true"
# 
#     def test_monitor_initialization(self):
#     def test_monitor_initialization(self):
#         """Test DependencyMonitor initialization."""
#         db = CVEDatabase()
#         monitor = DependencyMonitor(db)
#         assert monitor.cve_db == db, "cve_db is not valid"
#         assert monitor.alerts == [], "alerts is not valid"
# 
#     def test_scan_clean_dependencies(self):
#     def test_scan_clean_dependencies(self):
#         """Test scanning dependencies with no vulnerabilities."""
#         db = CVEDatabase()
#         monitor = DependencyMonitor(db)
#         deps = {
#         deps = {
#             "safe-pkg-1": "1.0.0",
#             "safe-pkg-2": "2.0.0",
#         }
#         results = monitor.scan(deps)
# 
#         assert results["vulnerable_packages"] == 0, "Result must not be empty"
#         assert results["total_vulnerabilities"] == 0, "Result must not be empty"
#         assert results["safe"] is True, "Result must not be empty"
#         assert len(results["critical"]) == 0, "Collection must not be empty"
# 
#     def test_scan_with_critical_vulnerabilities(self):
#     def test_scan_with_critical_vulnerabilities(self):
#         """Test scanning with CRITICAL severity vulnerabilities."""
#         db = CVEDatabase()
#         cve = CVEEntry(
#             cve_id="CVE-2024-CRITICAL",
#             severity="CRITICAL",
#             package="critical-pkg",
#             affected_versions=["1.0.0"],
#             fixed_in="1.0.1",
#         )
#         db.add_cve(cve)
# 
#         monitor = DependencyMonitor(db)
#         deps = {"critical-pkg": "1.0.0"}
# 
#         results = monitor.scan(deps)
# 
#         assert results["vulnerable_packages"] == 1, "Result must not be empty"
#         assert results["safe"] is False, "Result must not be empty"
#         assert len(results["critical"]) == 1, "Collection must not be empty"
#         assert results["critical"][0]["cve"] == "CVE-2024-CRITICAL", "Result must not be empty"
# 
#     def test_scan_with_mixed_severities(self):
#     def test_scan_with_mixed_severities(self):
#         """Test scanning with mixed severity levels."""
#         db = CVEDatabase()
#         cves = [
#             CVEEntry("CVE-2024-C", "CRITICAL", "pkg1", ["1.0.0"], "1.0.1"),
#             CVEEntry("CVE-2024-H", "HIGH", "pkg2", ["2.0.0"], "2.0.1"),
#             CVEEntry("CVE-2024-M", "MEDIUM", "pkg3", ["3.0.0"], "3.0.1"),
#             CVEEntry("CVE-2024-L", "LOW", "pkg4", ["4.0.0"], "4.0.1"),
#         ]
# 
#         for cve in cves:
#             db.add_cve(cve)
# 
#         monitor = DependencyMonitor(db)
#         deps = {
#         deps = {
#             "pkg1": "1.0.0",
#             "pkg2": "2.0.0",
#             "pkg3": "3.0.0",
#             "pkg4": "4.0.0",
#         }
#         results = monitor.scan(deps)
# 
#         assert results["vulnerable_packages"] == 4, "Result must not be empty"
#         assert results["total_vulnerabilities"] == 4, "Result must not be empty"
#         assert len(results["critical"]) == 1, "Collection must not be empty"
#         assert len(results["high"]) == 1, "Collection must not be empty"
#         assert len(results["medium"]) == 1, "Collection must not be empty"
#         assert len(results["low"]) == 1, "Collection must not be empty"
# 
#     def test_scan_package_with_multiple_cves(self):
#     def test_scan_package_with_multiple_cves(self):
#         """Test scanning package with multiple CVEs."""
#         db = CVEDatabase()
#         cve1 = CVEEntry(
#             cve_id="CVE-2024-0001",
#             severity="HIGH",
#             package="multi-cve",
#             affected_versions=["1.0.0"],
#             fixed_in="1.0.1",
#         )
#         cve2 = CVEEntry(
#             cve_id="CVE-2024-0002",
#             severity="CRITICAL",
#             package="multi-cve",
#             affected_versions=["1.0.0"],
#             fixed_in="1.0.2",
#         )
# 
#         db.add_cve(cve1)
#         db.add_cve(cve2)
# 
#         monitor = DependencyMonitor(db)
#         deps = {"multi-cve": "1.0.0"}
# 
#         results = monitor.scan(deps)
# 
#         assert results["vulnerable_packages"] == 1, "Result must not be empty"
#         assert results["total_vulnerabilities"] == 2, "Result must not be empty"
# 
#     def test_generate_report_safe(self):
#     def test_generate_report_safe(self):
#         """Test report generation for safe dependencies."""
#         db = CVEDatabase()
#         monitor = DependencyMonitor(db)
#         scan_results = {
#         scan_results = {
#             "vulnerable_packages": 0,
#             "total_vulnerabilities": 0,
#             "critical": [],
#             "high": [],
#             "medium": [],
#             "low": [],
#             "safe": True,
#         }
#         report = monitor.generate_report(scan_results)
# 
#         assert ", "Condition must be true"
#         assert "✅ SAFE" in report, "Condition must be true"
#         assert "**Vulnerable Packages:** 0" in report, "Condition must be true"
# 
#     def test_generate_report_with_vulnerabilities(self):
#     def test_generate_report_with_vulnerabilities(self):
#         """Test report generation with vulnerabilities."""
#         db = CVEDatabase()
#         monitor = DependencyMonitor(db)
#         scan_results = {
#         scan_results = {
#             "vulnerable_packages": 2,
#             "total_vulnerabilities": 3,
#             "critical": [{"package": "pkg1", "cve": "CVE-2024-0001", "fixed_in": "1.0.1"}],
#             "high": [
#                 {"package": "pkg2", "cve": "CVE-2024-0002", "fixed_in": "2.0.1"},
#                 {"package": "pkg2", "cve": "CVE-2024-0003", "fixed_in": "2.0.2"},
#             ],
#             "medium": [],
#             "low": [],
#             "safe": False,
#         }
#         report = monitor.generate_report(scan_results)
# 
#         assert "⚠️ VULNERABILITIES FOUND" in report, "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert "CVE-2024-0001" in report, "Condition must be true"
#         assert "CVE-2024-0002" in report, "Condition must be true"
# 
#     def test_generate_report_format(self):
#     def test_generate_report_format(self):
#         """Test that generated report has proper markdown format."""
#         db = CVEDatabase()
#         monitor = DependencyMonitor(db)
#         scan_results = {
#         scan_results = {
#             "vulnerable_packages": 1,
#             "total_vulnerabilities": 1,
#             "critical": [{"package": "vuln-pkg", "cve": "CVE-2024-TEST", "fixed_in": "2.0.0"}],
#             "high": [],
#             "medium": [],
#             "low": [],
#             "safe": False,
#         }
#         report = monitor.generate_report(scan_results)
# 
#         lines = report.split("\n")
#         assert any("**Vulnerable Packages:**" in line for line in lines), "Condition must be true"
#         assert any("**Total Vulnerabilities:**" in line for line in lines), "Condition must be true"


# =============================================================================
# Integration and Realistic Scenario Tests
# =============================================================================


class TestIntegrationScenarios:
    """Integration tests with realistic scenarios."""

    def test_get_sample_cve_database(self):
        """Test the sample CVE database helper."""
        db = get_sample_cve_database()

        assert isinstance(db, CVEDatabase)
        assert len(db.entries) > 0, "Collection must not be empty"

    def test_full_scan_workflow(self):
        """Test complete workflow: database -> monitor -> scan -> report."""
        # Create database
        db = CVEDatabase()

        # Add realistic CVEs
        db.add_cve(
            CVEEntry(
                cve_id="CVE-2023-45853",
                severity="HIGH",
                package="zipp",
                affected_versions=["3.15.0", "3.16.0"],
                fixed_in="3.17.0",
                description="Path traversal vulnerability",
            )
        )

        db.add_cve(
            CVEEntry(
                cve_id="CVE-2023-43804",
                severity="MEDIUM",
                package="urllib3",
                affected_versions=["2.0.0", "2.0.1"],
                fixed_in="2.0.7",
                description="Cookie request header leak",
            )
        )

        # Create monitor
        monitor = DependencyMonitor(db)

        # Scan project dependencies
        project_deps = {
            "zipp": "3.15.0",  # Vulnerable
            "urllib3": "2.0.7",  # Fixed
            "requests": "2.31.0",  # Not in database
        }

        results = monitor.scan(project_deps)

        # Verify results
        assert results["vulnerable_packages"] == 1, "Result must not be empty"
        assert results["safe"] is False, "Result must not be empty"
        assert len(results["high"]) == 1, "Collection must not be empty"

        # Generate report
        report = monitor.generate_report(results)
        assert "zipp" in report, "Condition must be true"
        assert "CVE-2023-45853" in report, "Condition must be true"

    def test_database_update_scenario(self):
        """Test scenario of updating database with new CVEs."""
        db = CVEDatabase()
        initial_checksum = db.checksum

        # First batch of CVEs
        db.add_cve(
            CVEEntry(
                cve_id="CVE-2024-0001",
                severity="HIGH",
                package="old-vuln",
                affected_versions=["1.0.0"],
            )
        )

        checksum_after_first = db.checksum
        assert checksum_after_first != initial_checksum, "checksum_after_first is not valid"

        # Second batch (simulating update)
        db.add_cve(
            CVEEntry(
                cve_id="CVE-2024-0002",
                severity="CRITICAL",
                package="new-vuln",
                affected_versions=["2.0.0"],
            )
        )

        checksum_after_second = db.checksum
        assert checksum_after_second != checksum_after_first, "checksum_after_second is not valid"

    def test_large_scale_scanning(self):
        """Test scanning with large number of dependencies."""
        db = CVEDatabase()

        # Add 50 CVEs
        for i in range(50):
            db.add_cve(
                CVEEntry(
                    cve_id=f"CVE-2024-{i:04d}",
                    severity=["LOW", "MEDIUM", "HIGH", "CRITICAL"][i % 4],
                    package=f"pkg-{i}",
                    affected_versions=["1.0.0"],
                )
            )

        monitor = DependencyMonitor(db)

        # Create 200 dependencies (50 vulnerable, 150 safe)
        deps = {}
        for i in range(200):
            if i < 50:
                deps[f"pkg-{i}"] = "1.0.0"  # Vulnerable
            else:
                deps[f"safe-pkg-{i}"] = "1.0.0"  # Safe

        results = monitor.scan(deps)

        assert results["vulnerable_packages"] == 50, "Result must not be empty"
        assert results["total_vulnerabilities"] == 50, "Result must not be empty"

    def test_no_fix_available_scenario(self):
        """Test scenario where CVE has no fix available."""
        db = CVEDatabase()

        db.add_cve(
            CVEEntry(
                cve_id="CVE-2024-NOFIX",
                severity="CRITICAL",
                package="zero-day",
                affected_versions=["1.0.0", "1.0.1", "1.0.2"],
                fixed_in=None,  # No fix available
                description="Zero-day vulnerability",
            )
        )

        monitor = DependencyMonitor(db)
        deps = {"zero-day": "1.0.1"}

        results = monitor.scan(deps)

        assert results["vulnerable_packages"] == 1, "Result must not be empty"
        assert results["critical"][0]["fixed_in"] is None, "Result must not be empty"

    def test_persistence_with_file_system(self):
        """Test database persistence to file system."""
        db1 = CVEDatabase()

        db1.add_cve(
            CVEEntry(
                cve_id="CVE-2024-FILE",
                severity="HIGH",
                package="file-test",
                affected_versions=["1.0.0"],
                fixed_in="1.0.1",
            )
        )

        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(db1.to_dict(), f)
            temp_path = f.name

        try:
            # Load from file
            with open(temp_path, "r") as f:
                data = json.load(f)

            db2 = CVEDatabase.from_dict(data)

            assert "file-test" in db2.entries, "Condition must be true"
            assert db2.entries["file-test"][0].cve_id == "CVE-2024-FILE", "cve_id is not valid"
        finally:
            Path(temp_path).unlink(missing_ok=True)
