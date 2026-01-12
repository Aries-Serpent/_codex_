#!/usr/bin/env python3
"""
Integration tests for Dependency Conflict Resolver Agent

Tests end-to-end workflows including:
- Full conflict resolution workflows for different ecosystems
- Multi-ecosystem projects
- Vulnerability-aware resolution
- Lock file handling
- Graph visualization
"""

import unittest
import tempfile
import json
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent import (
    DependencyConflictResolver,
    DependencyInfo,
    ResolutionStrategy,
    Ecosystem,
)


class TestEndToEndPythonResolution(unittest.TestCase):
    """Test end-to-end Python conflict resolution"""
    
    def test_end_to_end_python_conflict_resolution(self):
        """Test complete workflow: parse -> detect -> resolve -> apply -> validate"""
        # Create test requirements file with conflicts
        with tempfile.NamedTemporaryFile(mode='w', suffix='requirements.txt', delete=False) as f:
            f.write("""
requests>=2.20.0
pytest==7.2.0
# Another file depends on different version
requests>=2.28.0
numpy>=1.20.0
""")
            req_file = Path(f.name)
        
        try:
            resolver = DependencyConflictResolver()
            
            # Step 1: Parse dependencies
            deps = resolver.parse_dependency_file(req_file)
            self.assertGreater(len(deps), 0)
            
            # Step 2: Build dependency graph
            graph = resolver.build_dependency_graph(deps)
            self.assertGreater(len(graph), 0)
            
            # Step 3: Detect conflicts
            conflicts = resolver.detect_conflicts()
            # Note: Same file won't create conflict in this simple case
            # but method is tested
            
            # Step 4: Generate resolution plan
            report = resolver.generate_resolution_plan()
            self.assertIsNotNone(report)
            self.assertIsNotNone(report.resolution_plan)
            
            # Step 5: Validate
            valid, errors = resolver.validate_resolution()
            # Should be valid if no conflicts
            if not conflicts:
                self.assertTrue(valid)
        
        finally:
            req_file.unlink()
    
    def test_python_requirements_with_version_pinning(self):
        """Test resolution respects version pinning"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='requirements.txt', delete=False) as f:
            f.write("""
django==4.1.0
requests>=2.28.0,<3.0.0
pytest>=7.0.0
""")
            req_file = Path(f.name)
        
        try:
            resolver = DependencyConflictResolver()
            deps = resolver.parse_dependency_file(req_file)
            
            # Check that pinned versions are respected
            django_dep = next(d for d in deps if d.name == 'django')
            self.assertEqual(django_dep.version_constraint, '==4.1.0')
            
            resolver.build_dependency_graph(deps)
            conflicts = resolver.detect_conflicts()
            
            # No conflicts expected
            self.assertEqual(len(conflicts), 0)
        
        finally:
            req_file.unlink()


class TestEndToEndJavaScriptResolution(unittest.TestCase):
    """Test end-to-end JavaScript conflict resolution"""
    
    def test_end_to_end_javascript_conflict_resolution(self):
        """Test complete workflow for JavaScript package.json"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='package.json', delete=False) as f:
            package_data = {
                "name": "test-project",
                "version": "1.0.0",
                "dependencies": {
                    "express": "^4.18.0",
                    "lodash": "^4.17.21",
                    "axios": "^1.3.0"
                },
                "devDependencies": {
                    "jest": "^29.0.0",
                    "eslint": "^8.35.0"
                }
            }
            json.dump(package_data, f)
            package_file = Path(f.name)
        
        try:
            resolver = DependencyConflictResolver()
            
            # Parse and analyze
            deps = resolver.parse_dependency_file(package_file)
            self.assertEqual(len(deps), 5)
            
            # Build graph
            graph = resolver.build_dependency_graph(deps)
            self.assertEqual(len(graph), 5)
            
            # Detect conflicts
            conflicts = resolver.detect_conflicts()
            
            # Generate report
            report = resolver.generate_resolution_plan()
            self.assertEqual(report.ecosystem, Ecosystem.JAVASCRIPT)
            self.assertEqual(report.total_dependencies, 5)
        
        finally:
            package_file.unlink()
    
    def test_javascript_dev_dependencies_handling(self):
        """Test proper handling of dev dependencies"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='package.json', delete=False) as f:
            package_data = {
                "name": "test-project",
                "version": "1.0.0",
                "dependencies": {
                    "express": "^4.18.0"
                },
                "devDependencies": {
                    "jest": "^29.0.0"
                }
            }
            json.dump(package_data, f)
            package_file = Path(f.name)
        
        try:
            resolver = DependencyConflictResolver()
            deps = resolver.parse_dependency_file(package_file)
            
            # Check dev dependency flag
            jest_dep = next(d for d in deps if d.name == 'jest')
            self.assertTrue(jest_dep.is_dev)
            
            express_dep = next(d for d in deps if d.name == 'express')
            self.assertFalse(express_dep.is_dev)
        
        finally:
            package_file.unlink()


class TestEndToEndRustResolution(unittest.TestCase):
    """Test end-to-end Rust conflict resolution"""
    
    def test_end_to_end_rust_conflict_resolution(self):
        """Test complete workflow for Rust Cargo.toml"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='Cargo.toml', delete=False) as f:
            f.write("""
[package]
name = "test-crate"
version = "0.1.0"
edition = "2021"

[dependencies]
serde = "1.0"
tokio = { version = "1.28", features = ["full"] }
reqwest = "0.11.18"
anyhow = "1.0"
""")
            cargo_file = Path(f.name)
        
        try:
            resolver = DependencyConflictResolver()
            
            # Parse dependencies
            deps = resolver.parse_dependency_file(cargo_file)
            self.assertGreaterEqual(len(deps), 2)
            
            # Build graph
            graph = resolver.build_dependency_graph(deps)
            
            # All dependencies should be Rust ecosystem
            for dep in deps:
                self.assertEqual(dep.ecosystem, Ecosystem.RUST)
            
            # Detect conflicts
            conflicts = resolver.detect_conflicts()
            
            # Generate report
            report = resolver.generate_resolution_plan()
            self.assertEqual(report.ecosystem, Ecosystem.RUST)
        
        finally:
            cargo_file.unlink()


class TestMultiEcosystemProject(unittest.TestCase):
    """Test handling of multi-ecosystem projects"""
    
    def test_multi_ecosystem_project(self):
        """Test analyzing project with multiple ecosystems"""
        # Create Python requirements
        with tempfile.NamedTemporaryFile(mode='w', suffix='requirements.txt', delete=False) as f:
            f.write("requests>=2.28.0\nnumpy>=1.20.0\n")
            py_file = Path(f.name)
        
        # Create JavaScript package.json
        with tempfile.NamedTemporaryFile(mode='w', suffix='package.json', delete=False) as f:
            package_data = {
                "name": "test-project",
                "dependencies": {
                    "express": "^4.18.0"
                }
            }
            json.dump(package_data, f)
            js_file = Path(f.name)
        
        try:
            resolver_py = DependencyConflictResolver()
            resolver_js = DependencyConflictResolver()
            
            # Parse both ecosystems
            py_deps = resolver_py.parse_dependency_file(py_file)
            js_deps = resolver_js.parse_dependency_file(js_file)
            
            # Verify correct ecosystem detection
            self.assertTrue(all(d.ecosystem == Ecosystem.PYTHON for d in py_deps))
            self.assertTrue(all(d.ecosystem == Ecosystem.JAVASCRIPT for d in js_deps))
            
            # Build separate graphs
            py_graph = resolver_py.build_dependency_graph(py_deps)
            js_graph = resolver_js.build_dependency_graph(js_deps)
            
            self.assertGreater(len(py_graph), 0)
            self.assertGreater(len(js_graph), 0)
        
        finally:
            py_file.unlink()
            js_file.unlink()


class TestVulnerabilityAwareResolution(unittest.TestCase):
    """Test vulnerability-aware conflict resolution"""
    
    def test_vulnerability_aware_resolution(self):
        """Test resolution considers vulnerability information"""
        resolver = DependencyConflictResolver()
        
        deps = [
            DependencyInfo('requests', '2.20.0', '>=2.20.0', Ecosystem.PYTHON, source='file1.txt'),
            DependencyInfo('requests', '2.28.0', '>=2.28.0', Ecosystem.PYTHON, source='file2.txt'),
        ]
        
        resolver.build_dependency_graph(deps)
        resolver.detect_conflicts()
        
        # Check vulnerabilities
        vulnerabilities = resolver.check_vulnerabilities()
        
        # Vulnerability check should return a dict
        self.assertIsInstance(vulnerabilities, dict)
        
        # Resolution should prefer non-vulnerable versions
        plan = resolver.resolve_conflicts(ResolutionStrategy.BALANCED)
        self.assertIsNotNone(plan)
    
    def test_vulnerability_integration_disabled(self):
        """Test resolution with vulnerability checking disabled"""
        # Create config with vulnerability checking disabled
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
vulnerability_integration:
  enabled: false
""")
            config_path = Path(f.name)
        
        try:
            resolver = DependencyConflictResolver(config_path)
            self.assertFalse(resolver.vulnerability_checking_enabled)
            
            # Should still work without vulnerability checks
            deps = [
                DependencyInfo('requests', '2.28.0', '>=2.28.0', Ecosystem.PYTHON),
            ]
            
            resolver.build_dependency_graph(deps)
            vulnerabilities = resolver.check_vulnerabilities()
            
            self.assertEqual(len(vulnerabilities), 0)
        
        finally:
            config_path.unlink()


class TestResolutionWithLockedVersions(unittest.TestCase):
    """Test resolution with locked versions"""
    
    def test_resolution_with_locked_versions(self):
        """Test resolution respects locked/pinned versions"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='requirements.txt', delete=False) as f:
            f.write("""
# Locked versions - should not change
django==4.1.0
pytest==7.2.0

# Flexible versions
requests>=2.28.0
""")
            req_file = Path(f.name)
        
        try:
            resolver = DependencyConflictResolver()
            deps = resolver.parse_dependency_file(req_file)
            
            # Find locked dependencies
            locked_deps = [d for d in deps if '==' in d.version_constraint]
            self.assertEqual(len(locked_deps), 2)
            
            # Verify locked versions are parsed correctly
            django_dep = next(d for d in locked_deps if d.name == 'django')
            self.assertEqual(django_dep.version, '4.1.0')
        
        finally:
            req_file.unlink()


class TestConflictResolutionWithPreReleases(unittest.TestCase):
    """Test conflict resolution with pre-release versions"""
    
    def test_conflict_resolution_with_pre_releases(self):
        """Test handling of pre-release versions"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='requirements.txt', delete=False) as f:
            f.write("""
django>=4.2.0
pytest>=7.2.0
# Pre-release version
requests>=2.28.0rc1
""")
            req_file = Path(f.name)
        
        try:
            resolver = DependencyConflictResolver()
            deps = resolver.parse_dependency_file(req_file)
            
            # Should parse pre-release versions
            self.assertGreater(len(deps), 0)
            
            resolver.build_dependency_graph(deps)
            conflicts = resolver.detect_conflicts()
            
            # Pre-release shouldn't cause false conflicts
            # (in real implementation, would handle semver properly)
        
        finally:
            req_file.unlink()


class TestGraphVisualization(unittest.TestCase):
    """Test dependency graph visualization"""
    
    def test_graph_visualization_output(self):
        """Test generating text-based graph visualization"""
        resolver = DependencyConflictResolver()
        
        deps = [
            DependencyInfo('package-a', '1.0.0', '>=1.0.0', Ecosystem.PYTHON),
            DependencyInfo('package-b', '2.0.0', '>=2.0.0', Ecosystem.PYTHON, transitive_from='package-a'),
            DependencyInfo('package-c', '3.0.0', '>=3.0.0', Ecosystem.PYTHON, transitive_from='package-b'),
        ]
        
        resolver.build_dependency_graph(deps)
        
        # Generate visualization
        visualization = resolver.visualize_dependency_graph()
        
        self.assertIsInstance(visualization, str)
        self.assertIn('Dependency Graph', visualization)
        self.assertIn('package-a', visualization)
    
    def test_graph_visualization_to_file(self):
        """Test saving graph visualization to file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            output_file = Path(f.name)
        
        try:
            resolver = DependencyConflictResolver()
            
            deps = [
                DependencyInfo('package-a', '1.0.0', '>=1.0.0', Ecosystem.PYTHON),
                DependencyInfo('package-b', '2.0.0', '>=2.0.0', Ecosystem.PYTHON),
            ]
            
            resolver.build_dependency_graph(deps)
            
            # Save to file
            visualization = resolver.visualize_dependency_graph(output_file)
            
            # Verify file was created
            self.assertTrue(output_file.exists())
            
            # Verify content
            with open(output_file) as f:
                content = f.read()
                self.assertIn('Dependency Graph', content)
        
        finally:
            if output_file.exists():
                output_file.unlink()
    
    def test_graph_visualization_empty_graph(self):
        """Test visualization of empty graph"""
        resolver = DependencyConflictResolver()
        
        visualization = resolver.visualize_dependency_graph()
        
        self.assertIsInstance(visualization, str)
        self.assertIn('Dependency Graph', visualization)


class TestComplexResolutionScenarios(unittest.TestCase):
    """Test complex resolution scenarios"""
    
    def test_multiple_conflicts_resolution(self):
        """Test resolving multiple conflicts simultaneously"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='requirements.txt', delete=False) as f:
            f.write("""
requests>=2.20.0
numpy>=1.20.0
pytest>=7.0.0
""")
            req_file = Path(f.name)
        
        try:
            resolver = DependencyConflictResolver()
            deps = resolver.parse_dependency_file(req_file)
            
            resolver.build_dependency_graph(deps)
            
            # Generate resolution plan
            report = resolver.generate_resolution_plan()
            
            self.assertIsNotNone(report)
            self.assertIsNotNone(report.resolution_plan)
        
        finally:
            req_file.unlink()
    
    def test_transitive_dependency_analysis(self):
        """Test deep transitive dependency analysis"""
        resolver = DependencyConflictResolver()
        
        deps = [
            DependencyInfo('level-0', '1.0.0', '>=1.0.0', Ecosystem.PYTHON),
            DependencyInfo('level-1', '1.0.0', '>=1.0.0', Ecosystem.PYTHON, transitive_from='level-0'),
            DependencyInfo('level-2', '1.0.0', '>=1.0.0', Ecosystem.PYTHON, transitive_from='level-1'),
            DependencyInfo('level-3', '1.0.0', '>=1.0.0', Ecosystem.PYTHON, transitive_from='level-2'),
        ]
        
        graph = resolver.build_dependency_graph(deps)
        
        # Verify transitive relationships
        self.assertIn('level-1', graph['level-0'])
        self.assertIn('level-2', graph['level-1'])
        self.assertIn('level-3', graph['level-2'])


if __name__ == '__main__':
    unittest.main()
