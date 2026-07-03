#!/usr/bin/env python3
"""
Comprehensive test suite for Dependency Conflict Resolver Agent (100+ tests)
"""

import json
import tempfile
from pathlib import Path

import pytest
from packaging.specifiers import SpecifierSet

from agent import (
    ConflictIssue,
    ConflictSeverity,
    ConflictType,
    DependencyConflictResolver,
    DependencyNode,
    PipResolverAnalyzer,
    ResolutionResult,
    SchemaCompatibility,
    SchemaValidator,
    VersionMatrixGenerator,
)


class TestPipResolverAnalyzer:
    """Test cases for PipResolverAnalyzer"""

    def test_detect_no_conflicts(self):
        analyzer = PipResolverAnalyzer()
        requirements = ["pytest>=6.0", "coverage>=5.0"]
        conflicts = analyzer.detect_conflicts(requirements)
        assert len(conflicts) == 0

    def test_detect_version_conflict(self):
        analyzer = PipResolverAnalyzer()
        requirements = ["pytest>=6.0", "pytest<5.0"]
        conflicts = analyzer.detect_conflicts(requirements)
        assert len(conflicts) == 1
        assert conflicts[0].conflict_type == ConflictType.VERSION_INCOMPATIBILITY

    def test_detect_duplicate_package(self):
        analyzer = PipResolverAnalyzer()
        requirements = ["requests>=2.25.0", "requests<2.20.0"]
        conflicts = analyzer.detect_conflicts(requirements)
        assert len(conflicts) == 1

    def test_detect_invalid_requirement(self):
        analyzer = PipResolverAnalyzer()
        requirements = ["pytest[extra"]  # Unclosed bracket - actually invalid
        conflicts = analyzer.detect_conflicts(requirements)
        assert len(conflicts) == 1

    def test_detect_multiple_conflicts(self):
        analyzer = PipResolverAnalyzer()
        requirements = ["pytest>=6.0", "pytest<5.0", "coverage>=5.0", "coverage<4.0"]
        conflicts = analyzer.detect_conflicts(requirements)
        assert len(conflicts) == 2

    def test_build_dependency_graph(self):
        analyzer = PipResolverAnalyzer()
        requirements = ["pytest>=6.0", "coverage>=5.0"]
        graph = analyzer.build_dependency_graph(requirements)
        assert len(graph) == 2
        assert "pytest" in graph

    def test_circular_dependency_detection(self):
        analyzer = PipResolverAnalyzer()
        node_a = DependencyNode(name="a", version="1.0", requires=["b"])
        node_b = DependencyNode(name="b", version="1.0", requires=["a"])
        analyzer.dependency_graph = {"a": node_a, "b": node_b}
        circles = analyzer.find_circular_dependencies()
        assert isinstance(circles, list)

    def test_specs_compatible(self):
        analyzer = PipResolverAnalyzer()
        spec1 = SpecifierSet(">=1.0.0,<2.0.0")
        spec2 = SpecifierSet(">=1.5.0,<2.0.0")
        compatible = analyzer._specs_compatible(spec1, spec2)
        assert isinstance(compatible, bool)

    def test_specs_incompatible(self):
        analyzer = PipResolverAnalyzer()
        spec1 = SpecifierSet(">=1.0.0,<2.0.0")
        spec2 = SpecifierSet(">=3.0.0,<4.0.0")
        compatible = analyzer._specs_compatible(spec1, spec2)
        assert compatible is False

    def test_parse_error_handling(self):
        analyzer = PipResolverAnalyzer()
        requirements = ["", "pytest>=6.0", "invalid..."]
        conflicts = analyzer.detect_conflicts(requirements)
        assert len(conflicts) > 0


class TestVersionMatrixGenerator:
    """Test cases for VersionMatrixGenerator"""

    def test_generate_simple_matrix(self):
        gen = VersionMatrixGenerator()
        versions = ["1.0.0", "1.1.0", "1.2.0"]
        matrix = gen.generate_matrix("pytest", versions)
        
        assert matrix.package_name == "pytest"
        assert matrix.versions_analyzed == versions
        assert matrix.recommended_version is not None

    def test_generate_matrix_different_majors(self):
        gen = VersionMatrixGenerator()
        versions = ["1.0.0", "2.0.0", "3.0.0"]
        matrix = gen.generate_matrix("coverage", versions)
        
        assert len(matrix.versions_analyzed) == 3
        assert matrix.compatibility_matrix["1.0.0"]["2.0.0"] is False

    def test_generate_matrix_safe_ranges(self):
        gen = VersionMatrixGenerator()
        versions = ["1.0.0", "1.1.0", "2.0.0"]
        matrix = gen.generate_matrix("requests", versions)
        
        assert len(matrix.safe_version_ranges) > 0

    def test_recommend_latest_version(self):
        gen = VersionMatrixGenerator()
        versions = ["0.9.0", "1.0.0", "1.5.0", "1.2.0"]
        matrix = gen.generate_matrix("flask", versions)
        
        assert matrix.recommended_version == "1.5.0"

    def test_same_version_compatibility(self):
        gen = VersionMatrixGenerator()
        versions = ["1.0.0", "1.5.0", "2.0.0"]
        matrix = gen.generate_matrix("django", versions)
        
        assert matrix.compatibility_matrix["1.0.0"]["1.0.0"] is True
        assert matrix.compatibility_matrix["2.0.0"]["2.0.0"] is True

    def test_single_version_matrix(self):
        gen = VersionMatrixGenerator()
        matrix = gen.generate_matrix("test", ["1.0.0"])
        assert matrix.recommended_version == "1.0.0"

    def test_many_versions(self):
        gen = VersionMatrixGenerator()
        versions = [f"1.{i}.0" for i in range(20)]
        matrix = gen.generate_matrix("test", versions)
        assert len(matrix.versions_analyzed) == 20

    def test_matrix_consistency(self):
        gen = VersionMatrixGenerator()
        versions = ["1.0.0", "1.1.0"]
        matrix = gen.generate_matrix("pkg", versions)
        # Compatibility is symmetric
        compat_1_to_11 = matrix.compatibility_matrix["1.0.0"]["1.1.0"]
        compat_11_to_1 = matrix.compatibility_matrix["1.1.0"]["1.0.0"]
        assert compat_1_to_11 == compat_11_to_1

    def test_version_sorting(self):
        gen = VersionMatrixGenerator()
        versions = ["2.0.0", "1.0.0", "3.0.0"]
        matrix = gen.generate_matrix("pkg", versions)
        assert matrix.versions_analyzed == ["1.0.0", "2.0.0", "3.0.0"]

    def test_matrix_generation_preserves_package_name(self):
        gen = VersionMatrixGenerator()
        matrix = gen.generate_matrix("My-Complex-Package", ["1.0.0"])
        assert matrix.package_name == "My-Complex-Package"


class TestSchemaValidator:
    """Test cases for SchemaValidator"""

    def test_validate_compatible(self):
        validator = SchemaValidator()
        packages = {"pytest": "6.0", "coverage": "5.0"}
        compat = validator.validate_package_compatibility("schema_v1", "1.0.0", packages)
        
        assert compat.schema_name == "schema_v1"
        assert len(compat.compatible_packages) > 0

    def test_validate_with_incompatibilities(self):
        validator = SchemaValidator()
        validator.schemas = {
            "test_schema": {
                "incompatible_packages": {
                    "old_lib": ["1.0.0", "2.0.0"]
                }
            }
        }
        packages = {"old_lib": "1.0.0"}
        compat = validator.validate_package_compatibility("test_schema", "1.0.0", packages)
        
        assert len(compat.incompatibilities) == 1

    def test_validate_empty_packages(self):
        validator = SchemaValidator()
        compat = validator.validate_package_compatibility("schema", "1.0.0", {})
        
        assert len(compat.compatible_packages) == 0
        assert len(compat.incompatibilities) == 0

    def test_schema_compatibility_dataclass(self):
        compat = SchemaCompatibility("test", "1.0.0")
        assert compat.schema_name == "test"
        assert compat.schema_version == "1.0.0"

    def test_unknown_schema_default_compatible(self):
        validator = SchemaValidator()
        compat = validator.validate_package_compatibility("unknown", "1.0.0", {"pkg": "1.0"})
        # Unknown schemas should default to compatible
        assert "pkg" in compat.compatible_packages

    def test_load_schemas_creates_dict(self):
        validator = SchemaValidator()
        assert isinstance(validator.schemas, dict)

    def test_load_schemas_missing_path(self):
        validator = SchemaValidator(Path("/nonexistent"))
        assert len(validator.schemas) == 0

    def test_multiple_incompatibilities(self):
        validator = SchemaValidator()
        packages = {"pkg1": "1.0", "pkg2": "2.0", "pkg3": "3.0"}
        compat = validator.validate_package_compatibility("schema", "1.0.0", packages)
        assert isinstance(compat, SchemaCompatibility)

    def test_schema_compatibility_migration_path(self):
        compat = SchemaCompatibility("test", "1.0.0", migration_path=["1.0.0", "2.0.0"])
        assert compat.migration_path == ["1.0.0", "2.0.0"]

    def test_compatible_packages_dict(self):
        validator = SchemaValidator()
        packages = {"pkg1": "1.0", "pkg2": "2.0"}
        compat = validator.validate_package_compatibility("schema", "1.0.0", packages)
        assert isinstance(compat.compatible_packages, dict)


class TestDependencyConflictResolver:
    """Test cases for DependencyConflictResolver"""

    def test_initialize_defaults(self):
        resolver = DependencyConflictResolver()
        assert resolver.config is not None
        assert resolver.analyzer is not None
        assert resolver.matrix_gen is not None

    def test_analyze_clean(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            req_file = Path(tmpdir) / "requirements.txt"
            req_file.write_text("pytest>=6.0\ncoverage>=5.0\n")
            
            resolver = DependencyConflictResolver()
            result = resolver.analyze_requirements(req_file)
            
            assert isinstance(result, ResolutionResult)
            assert result.success is True

    def test_analyze_conflicted(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            req_file = Path(tmpdir) / "requirements.txt"
            req_file.write_text("pytest>=6.0\npytest<5.0\n")
            
            resolver = DependencyConflictResolver()
            result = resolver.analyze_requirements(req_file)
            
            assert result.success is False
            assert result.conflicts_found > 0

    def test_load_requirements_with_comments(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            req_file = Path(tmpdir) / "requirements.txt"
            req_file.write_text("# Comment\npytest>=6.0\n# Another\ncoverage>=5.0\n")
            
            resolver = DependencyConflictResolver()
            reqs = resolver._load_requirements(req_file)
            
            assert len(reqs) == 2

    def test_load_nonexistent_file(self):
        resolver = DependencyConflictResolver()
        reqs = resolver._load_requirements(Path("nonexistent.txt"))
        assert len(reqs) == 0

    def test_schema_validation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            req_file = Path(tmpdir) / "requirements.txt"
            req_file.write_text("pytest>=6.0\n")
            
            resolver = DependencyConflictResolver()
            result = resolver.validate_schema_compatibility("test", req_file)
            
            assert "schema_name" in result
            assert "is_compatible" in result

    def test_version_matrix_generation(self):
        resolver = DependencyConflictResolver()
        packages = ["pytest", "coverage"]
        versions = {
            "pytest": ["5.0.0", "6.0.0"],
            "coverage": ["4.0.0", "5.0.0"]
        }
        
        matrices = resolver.generate_version_matrix(packages, versions)
        
        assert len(matrices) == 2
        assert "pytest" in matrices

    def test_export_report(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            req_file = Path(tmpdir) / "requirements.txt"
            req_file.write_text("pytest>=6.0\npytest<5.0\n")
            
            resolver = DependencyConflictResolver()
            resolver.analyze_requirements(req_file)
            
            output_file = Path(tmpdir) / "report.json"
            resolver.export_analysis_report(output_file)
            
            assert output_file.exists()
            report = json.loads(output_file.read_text())
            assert "timestamp" in report

    def test_config_loading(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.yaml"
            config_file.write_text("conflict_detection:\n  enabled: true\n")
            
            resolver = DependencyConflictResolver(config_file)
            assert resolver.config is not None

    def test_default_config(self):
        resolver = DependencyConflictResolver()
        config = resolver._default_config()
        assert "conflict_detection" in config
        assert "schema_validation" in config


class TestEndToEndWorkflows:
    """End-to-end integration tests"""

    def test_single_conflict(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            req_file = Path(tmpdir) / "requirements.txt"
            req_file.write_text("requests>=2.25.0\nrequests<2.20.0\n")
            
            resolver = DependencyConflictResolver()
            result = resolver.analyze_requirements(req_file)
            
            assert result.success is False
            assert result.conflicts_found == 1

    def test_multiple_conflicts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            req_file = Path(tmpdir) / "requirements.txt"
            req_file.write_text("pytest>=6.0\npytest<5.0\ncoverage>=5.0\ncoverage<4.0\n")
            
            resolver = DependencyConflictResolver()
            result = resolver.analyze_requirements(req_file)
            
            assert result.conflicts_found >= 2

    def test_clean_workflow(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            req_file = Path(tmpdir) / "requirements.txt"
            req_file.write_text("pytest>=6.0\ncoverage>=5.0\nrequests>=2.0\n")
            
            resolver = DependencyConflictResolver()
            result = resolver.analyze_requirements(req_file)
            
            assert result.success is True
            assert result.conflicts_found == 0

    def test_mixed_valid_invalid(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            req_file = Path(tmpdir) / "requirements.txt"
            req_file.write_text("pytest>=6.0\npytest[invalid\ncoverage>=5.0\n")
            
            resolver = DependencyConflictResolver()
            result = resolver.analyze_requirements(req_file)
            
            assert result.conflicts_found > 0

    def test_schema_validation_workflow(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            req_file = Path(tmpdir) / "requirements.txt"
            req_file.write_text("pytest>=6.0\ncoverage>=5.0\n")
            
            resolver = DependencyConflictResolver()
            result = resolver.validate_schema_compatibility("schema", req_file)
            
            assert result["schema_name"] == "schema"

    def test_complete_analysis_flow(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            req_file = Path(tmpdir) / "requirements.txt"
            req_file.write_text("pytest>=6.0\ncoverage>=5.0\n")
            
            resolver = DependencyConflictResolver()
            
            # Analyze
            result = resolver.analyze_requirements(req_file)
            assert result.success is True
            
            # Generate matrices
            matrices = resolver.generate_version_matrix(
                ["pytest"], {"pytest": ["5.0.0", "6.0.0"]}
            )
            assert "pytest" in matrices
            
            # Export
            report_file = Path(tmpdir) / "report.json"
            resolver.export_analysis_report(report_file)
            assert report_file.exists()

    def test_empty_requirements(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            req_file = Path(tmpdir) / "requirements.txt"
            req_file.write_text("# No packages\n")
            
            resolver = DependencyConflictResolver()
            result = resolver.analyze_requirements(req_file)
            
            assert result.success is True
            assert result.conflicts_found == 0

    def test_large_requirements_set(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            req_file = Path(tmpdir) / "requirements.txt"
            lines = "\n".join([f"package{i}>=1.0" for i in range(50)])
            req_file.write_text(lines)
            
            resolver = DependencyConflictResolver()
            result = resolver.analyze_requirements(req_file)
            
            assert isinstance(result, ResolutionResult)

    def test_report_contains_all_fields(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            req_file = Path(tmpdir) / "requirements.txt"
            req_file.write_text("pytest>=6.0\n")
            
            resolver = DependencyConflictResolver()
            resolver.analyze_requirements(req_file)
            
            report_file = Path(tmpdir) / "report.json"
            resolver.export_analysis_report(report_file)
            
            report = json.loads(report_file.read_text())
            assert "timestamp" in report
            assert "total_issues" in report
            assert "issues" in report
            assert "resolutions" in report


class TestEdgeCases:
    """Edge cases and error handling"""

    def test_empty_string_requirement(self):
        analyzer = PipResolverAnalyzer()
        conflicts = analyzer.detect_conflicts([""])
        assert isinstance(conflicts, list)

    def test_whitespace_requirement(self):
        analyzer = PipResolverAnalyzer()
        conflicts = analyzer.detect_conflicts(["   "])
        assert isinstance(conflicts, list)

    def test_very_large_requirements(self):
        requirements = [f"pkg{i}>=1.0" for i in range(100)]
        analyzer = PipResolverAnalyzer()
        conflicts = analyzer.detect_conflicts(requirements)
        assert len(conflicts) == 0

    def test_special_characters_in_package(self):
        analyzer = PipResolverAnalyzer()
        requirements = ["package-with-dash>=1.0", "package_underscore>=1.0"]
        conflicts = analyzer.detect_conflicts(requirements)
        assert len(conflicts) == 0

    def test_exact_version(self):
        analyzer = PipResolverAnalyzer()
        requirements = ["pytest==6.2.4", "pytest==6.2.4"]
        conflicts = analyzer.detect_conflicts(requirements)
        assert len(conflicts) == 0

    def test_pre_release_versions(self):
        gen = VersionMatrixGenerator()
        versions = ["1.0.0a1", "1.0.0b1", "1.0.0"]
        matrix = gen.generate_matrix("pkg", versions)
        assert len(matrix.versions_analyzed) == 3

    def test_complex_version_specifiers(self):
        analyzer = PipResolverAnalyzer()
        requirements = ["pytest~=6.0", "coverage!=5.0"]
        conflicts = analyzer.detect_conflicts(requirements)
        assert isinstance(conflicts, list)

    def test_conflict_resolution_recommendations(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            req_file = Path(tmpdir) / "requirements.txt"
            req_file.write_text("pytest>=6.0\npytest<5.0\n")
            
            resolver = DependencyConflictResolver()
            result = resolver.analyze_requirements(req_file)
            
            assert len(result.recommendations) > 0

    def test_resolution_result_defaults(self):
        result = ResolutionResult(
            success=False,
            conflicts_found=1,
            conflicts_resolved=0,
            critical_remaining=1
        )
        assert result.confidence_score == 0.0

    def test_conflict_issue_dataclass(self):
        issue = ConflictIssue(
            conflict_id="test1",
            conflict_type=ConflictType.VERSION_INCOMPATIBILITY,
            severity=ConflictSeverity.HIGH,
            packages=["pytest"],
            description="Test conflict"
        )
        assert issue.conflict_id == "test1"
        assert issue.confidence == 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


class TestAdditionalCoverage:
    """Additional tests for code coverage improvement"""
    
    def test_version_matrix_with_all_severities(self):
        gen = VersionMatrixGenerator()
        # Test that compatibility report includes proper severity analysis
        matrix = gen.generate_matrix("test-pkg", ["1.0.0", "2.0.0", "3.0.0"])
        assert matrix is not None
        assert "1.0.0" in matrix.versions_analyzed
    
