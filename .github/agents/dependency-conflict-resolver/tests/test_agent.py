#!/usr/bin/env python3
"""
Unit tests for Dependency Conflict Resolver Agent

Tests core functionality including:
- Agent initialization
- Dependency file parsing (Python, JS, Rust, Go)
- Dependency graph building
- Conflict detection
- Resolution strategies
- Validation
"""

import unittest
import tempfile
import json
from pathlib import Path
from datetime import datetime, timezone

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent import (
    DependencyConflictResolver,
    DependencyInfo,
    DependencyConflict,
    ResolutionStrategy,
    ConflictType,
    Ecosystem,
    ResolutionPlan,
    ConflictReport
)


class TestAgentInitialization(unittest.TestCase):
    """Test agent initialization and configuration"""
    
    def test_agent_initialization_default_config(self):
        """Test agent initializes with default config"""
        resolver = DependencyConflictResolver()
        
        self.assertIsNotNone(resolver.config)
        self.assertEqual(resolver.config['agent_name'], 'dependency-conflict-resolver')
        self.assertEqual(resolver.config['version'], '1.0.0')
        self.assertEqual(resolver.max_graph_depth, 10)
        self.assertTrue(resolver.check_transitive)
    
    def test_agent_initialization_custom_config(self):
        """Test agent initializes with custom config"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
agent_name: test-resolver
version: 2.0.0
conflict_detection:
  max_depth: 5
  check_transitive: false
""")
            config_path = Path(f.name)
        
        try:
            resolver = DependencyConflictResolver(config_path)
            self.assertEqual(resolver.max_graph_depth, 5)
            self.assertFalse(resolver.check_transitive)
        finally:
            config_path.unlink()
    
    def test_default_config_structure(self):
        """Test default config has all required fields"""
        resolver = DependencyConflictResolver()
        config = resolver.config
        
        self.assertIn('agent_name', config)
        self.assertIn('version', config)
        self.assertIn('supported_ecosystems', config)
        self.assertIn('resolution_strategies', config)
        self.assertIn('conflict_detection', config)
        self.assertIn('vulnerability_integration', config)


class TestDependencyParsing(unittest.TestCase):
    """Test dependency file parsing for different ecosystems"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.resolver = DependencyConflictResolver()
    
    def test_parse_requirements_txt(self):
        """Test parsing Python requirements.txt"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='requirements.txt', delete=False) as f:
            f.write("""
# Test requirements
requests>=2.28.0
pytest==7.2.0
numpy>=1.20,<2.0
django~=4.1.0
""")
            req_file = Path(f.name)
        
        try:
            deps = self.resolver.parse_dependency_file(req_file)
            
            self.assertEqual(len(deps), 4)
            
            # Check requests
            requests_dep = next(d for d in deps if d.name == 'requests')
            self.assertEqual(requests_dep.ecosystem, Ecosystem.PYTHON)
            self.assertEqual(requests_dep.version, '2.28.0')
            self.assertEqual(requests_dep.version_constraint, '>=2.28.0')
            
            # Check pytest
            pytest_dep = next(d for d in deps if d.name == 'pytest')
            self.assertEqual(pytest_dep.version, '7.2.0')
            self.assertEqual(pytest_dep.version_constraint, '==7.2.0')
        finally:
            req_file.unlink()
    
    def test_parse_package_json(self):
        """Test parsing JavaScript package.json"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='package.json', delete=False) as f:
            package_data = {
                "name": "test-project",
                "version": "1.0.0",
                "dependencies": {
                    "express": "^4.18.0",
                    "lodash": "~4.17.21"
                },
                "devDependencies": {
                    "jest": "^29.0.0"
                }
            }
            json.dump(package_data, f)
            package_file = Path(f.name)
        
        try:
            deps = self.resolver.parse_dependency_file(package_file)
            
            self.assertEqual(len(deps), 3)
            
            # Check express
            express_dep = next(d for d in deps if d.name == 'express')
            self.assertEqual(express_dep.ecosystem, Ecosystem.JAVASCRIPT)
            self.assertEqual(express_dep.version, '4.18.0')
            self.assertFalse(express_dep.is_dev)
            
            # Check jest
            jest_dep = next(d for d in deps if d.name == 'jest')
            self.assertTrue(jest_dep.is_dev)
        finally:
            package_file.unlink()
    
    def test_parse_cargo_toml(self):
        """Test parsing Rust Cargo.toml"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='Cargo.toml', delete=False) as f:
            f.write("""
[package]
name = "test-crate"
version = "0.1.0"

[dependencies]
serde = "1.0"
tokio = { version = "1.28", features = ["full"] }
reqwest = "0.11.18"
""")
            cargo_file = Path(f.name)
        
        try:
            deps = self.resolver.parse_dependency_file(cargo_file)
            
            self.assertGreaterEqual(len(deps), 2)
            
            # Check serde
            serde_dep = next((d for d in deps if d.name == 'serde'), None)
            if serde_dep:
                self.assertEqual(serde_dep.ecosystem, Ecosystem.RUST)
                self.assertEqual(serde_dep.version, '1.0')
        finally:
            cargo_file.unlink()
    
    def test_parse_go_mod(self):
        """Test parsing Go go.mod"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='go.mod', delete=False) as f:
            f.write("""
module example.com/myproject

go 1.20

require (
    github.com/gin-gonic/gin v1.9.0
    github.com/stretchr/testify v1.8.2
)

require github.com/gorilla/mux v1.8.0
""")
            go_file = Path(f.name)
        
        try:
            deps = self.resolver.parse_dependency_file(go_file)
            
            self.assertGreaterEqual(len(deps), 2)
            
            # Check gin
            gin_dep = next((d for d in deps if 'gin' in d.name), None)
            if gin_dep:
                self.assertEqual(gin_dep.ecosystem, Ecosystem.GO)
        finally:
            go_file.unlink()
    
    def test_parse_empty_file(self):
        """Test parsing empty dependency file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='requirements.txt', delete=False) as f:
            f.write("")
            req_file = Path(f.name)
        
        try:
            deps = self.resolver.parse_dependency_file(req_file)
            self.assertEqual(len(deps), 0)
        finally:
            req_file.unlink()
    
    def test_parse_nonexistent_file(self):
        """Test parsing nonexistent file raises error"""
        with self.assertRaises(FileNotFoundError):
            self.resolver.parse_dependency_file(Path('/nonexistent/file.txt'))


class TestDependencyGraphBuilding(unittest.TestCase):
    """Test dependency graph construction"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.resolver = DependencyConflictResolver()
    
    def test_build_dependency_graph_simple(self):
        """Test building simple dependency graph"""
        deps = [
            DependencyInfo('package-a', '1.0.0', '>=1.0.0', Ecosystem.PYTHON),
            DependencyInfo('package-b', '2.0.0', '>=2.0.0', Ecosystem.PYTHON),
            DependencyInfo('package-c', '3.0.0', '>=3.0.0', Ecosystem.PYTHON),
        ]
        
        graph = self.resolver.build_dependency_graph(deps)
        
        self.assertEqual(len(graph), 3)
        self.assertIn('package-a', graph)
        self.assertIn('package-b', graph)
        self.assertIn('package-c', graph)
    
    def test_build_dependency_graph_with_transitive(self):
        """Test building graph with transitive dependencies"""
        deps = [
            DependencyInfo('package-a', '1.0.0', '>=1.0.0', Ecosystem.PYTHON),
            DependencyInfo('package-b', '2.0.0', '>=2.0.0', Ecosystem.PYTHON, transitive_from='package-a'),
            DependencyInfo('package-c', '3.0.0', '>=3.0.0', Ecosystem.PYTHON, transitive_from='package-b'),
        ]
        
        graph = self.resolver.build_dependency_graph(deps)
        
        self.assertEqual(len(graph), 3)
        self.assertIn('package-b', graph['package-a'])
        self.assertIn('package-c', graph['package-b'])
    
    def test_build_empty_graph(self):
        """Test building empty dependency graph"""
        graph = self.resolver.build_dependency_graph([])
        self.assertEqual(len(graph), 0)


class TestConflictDetection(unittest.TestCase):
    """Test dependency conflict detection"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.resolver = DependencyConflictResolver()
    
    def test_detect_direct_conflict(self):
        """Test detecting direct version conflict"""
        deps = [
            DependencyInfo('requests', '2.28.0', '>=2.28.0', Ecosystem.PYTHON, source='file1.txt'),
            DependencyInfo('requests', '2.20.0', '>=2.20.0', Ecosystem.PYTHON, source='file2.txt'),
        ]
        
        self.resolver.build_dependency_graph(deps)
        conflicts = self.resolver.detect_conflicts()
        
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0].conflict_type, ConflictType.DIRECT)
        self.assertEqual(conflicts[0].package_name, 'requests')
        self.assertEqual(len(conflicts[0].conflicting_versions), 2)
    
    def test_detect_transitive_conflict(self):
        """Test detecting transitive dependency conflict"""
        deps = [
            DependencyInfo('package-a', '1.0.0', '>=1.0.0', Ecosystem.PYTHON),
            DependencyInfo('requests', '2.28.0', '>=2.28.0', Ecosystem.PYTHON, transitive_from='package-a'),
            DependencyInfo('requests', '2.20.0', '>=2.20.0', Ecosystem.PYTHON, transitive_from='package-b'),
        ]
        
        self.resolver.build_dependency_graph(deps)
        conflicts = self.resolver.detect_conflicts()
        
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0].conflict_type, ConflictType.TRANSITIVE)
    
    def test_detect_no_conflicts(self):
        """Test no conflicts detected for compatible versions"""
        deps = [
            DependencyInfo('requests', '2.28.0', '>=2.28.0', Ecosystem.PYTHON),
            DependencyInfo('numpy', '1.20.0', '>=1.20.0', Ecosystem.PYTHON),
        ]
        
        self.resolver.build_dependency_graph(deps)
        conflicts = self.resolver.detect_conflicts()
        
        self.assertEqual(len(conflicts), 0)
    
    def test_detect_compatible_versions(self):
        """Test compatible versions don't trigger conflict"""
        deps = [
            DependencyInfo('requests', '2.28.0', '>=2.28.0', Ecosystem.PYTHON),
            DependencyInfo('requests', '2.28.0', '>=2.28.0', Ecosystem.PYTHON),
        ]
        
        self.resolver.build_dependency_graph(deps)
        conflicts = self.resolver.detect_conflicts()
        
        self.assertEqual(len(conflicts), 0)


class TestCircularDependencies(unittest.TestCase):
    """Test circular dependency detection"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.resolver = DependencyConflictResolver()
    
    def test_check_circular_dependencies_simple(self):
        """Test detecting simple circular dependency"""
        deps = [
            DependencyInfo('package-a', '1.0.0', '>=1.0.0', Ecosystem.PYTHON),
            DependencyInfo('package-b', '1.0.0', '>=1.0.0', Ecosystem.PYTHON, transitive_from='package-a'),
        ]
        
        self.resolver.build_dependency_graph(deps)
        
        # Manually create circular dependency
        self.resolver.dependency_graph['package-b'].add('package-a')
        
        circular = self.resolver._detect_circular_dependencies()
        
        self.assertGreaterEqual(len(circular), 1)
    
    def test_check_no_circular_dependencies(self):
        """Test no circular dependencies in clean graph"""
        deps = [
            DependencyInfo('package-a', '1.0.0', '>=1.0.0', Ecosystem.PYTHON),
            DependencyInfo('package-b', '1.0.0', '>=1.0.0', Ecosystem.PYTHON, transitive_from='package-a'),
            DependencyInfo('package-c', '1.0.0', '>=1.0.0', Ecosystem.PYTHON, transitive_from='package-b'),
        ]
        
        self.resolver.build_dependency_graph(deps)
        circular = self.resolver._detect_circular_dependencies()
        
        self.assertEqual(len(circular), 0)


class TestSemanticVersioning(unittest.TestCase):
    """Test semantic version comparison"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.resolver = DependencyConflictResolver()
    
    def test_semantic_version_comparison_compatible(self):
        """Test compatible semantic versions"""
        versions = ['2.28.0', '2.28.1', '2.28.2']
        compatible = self.resolver._are_versions_compatible(versions, Ecosystem.PYTHON)
        
        self.assertTrue(compatible)
    
    def test_semantic_version_comparison_incompatible(self):
        """Test incompatible semantic versions"""
        versions = ['2.28.0', '3.0.0']
        compatible = self.resolver._are_versions_compatible(versions, Ecosystem.PYTHON)
        
        self.assertFalse(compatible)
    
    def test_extract_version_from_constraint(self):
        """Test extracting version from constraint string"""
        test_cases = [
            ('>=2.28.0', '2.28.0'),
            ('==7.2.0', '7.2.0'),
            ('~=4.1.0', '4.1.0'),
            ('^4.18.0', '4.18.0'),
            ('', 'latest'),
        ]
        
        for constraint, expected in test_cases:
            result = self.resolver._extract_version_from_constraint(constraint)
            self.assertEqual(result, expected)


class TestResolutionStrategies(unittest.TestCase):
    """Test conflict resolution strategies"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.resolver = DependencyConflictResolver()
    
    def test_resolve_conflict_upgrade_strategy(self):
        """Test resolving conflict with aggressive (upgrade) strategy"""
        deps = [
            DependencyInfo('requests', '2.20.0', '>=2.20.0', Ecosystem.PYTHON, source='file1.txt'),
            DependencyInfo('requests', '2.28.0', '>=2.28.0', Ecosystem.PYTHON, source='file2.txt'),
        ]
        
        self.resolver.build_dependency_graph(deps)
        self.resolver.detect_conflicts()
        
        plan = self.resolver.resolve_conflicts(ResolutionStrategy.AGGRESSIVE)
        
        self.assertGreater(plan.conflicts_detected, 0)
        self.assertEqual(plan.strategy, ResolutionStrategy.AGGRESSIVE)
        self.assertGreater(len(plan.actions), 0)
        
        # Check that highest version is selected
        action = plan.actions[0]
        if action['type'] == 'update_version':
            self.assertEqual(action['to_version'], '2.28.0')
    
    def test_resolve_conflict_conservative_strategy(self):
        """Test resolving conflict with conservative strategy"""
        deps = [
            DependencyInfo('requests', '2.20.0', '>=2.20.0', Ecosystem.PYTHON, source='file1.txt'),
            DependencyInfo('requests', '2.28.0', '>=2.28.0', Ecosystem.PYTHON, source='file2.txt'),
        ]
        
        self.resolver.build_dependency_graph(deps)
        self.resolver.detect_conflicts()
        
        plan = self.resolver.resolve_conflicts(ResolutionStrategy.CONSERVATIVE)
        
        self.assertEqual(plan.strategy, ResolutionStrategy.CONSERVATIVE)
        
        # Check that lowest version is selected
        action = plan.actions[0]
        if action['type'] == 'update_version':
            self.assertEqual(action['to_version'], '2.20.0')
    
    def test_resolve_no_conflicts(self):
        """Test resolution plan when no conflicts exist"""
        deps = [
            DependencyInfo('requests', '2.28.0', '>=2.28.0', Ecosystem.PYTHON),
        ]
        
        self.resolver.build_dependency_graph(deps)
        self.resolver.detect_conflicts()
        
        plan = self.resolver.resolve_conflicts()
        
        self.assertEqual(plan.conflicts_detected, 0)
        self.assertEqual(len(plan.actions), 0)


class TestResolutionPlan(unittest.TestCase):
    """Test resolution plan generation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.resolver = DependencyConflictResolver()
    
    def test_generate_resolution_plan(self):
        """Test generating comprehensive resolution plan"""
        deps = [
            DependencyInfo('requests', '2.20.0', '>=2.20.0', Ecosystem.PYTHON, source='file1.txt'),
            DependencyInfo('requests', '2.28.0', '>=2.28.0', Ecosystem.PYTHON, source='file2.txt'),
        ]
        
        self.resolver.build_dependency_graph(deps)
        self.resolver.detect_conflicts()
        
        report = self.resolver.generate_resolution_plan()
        
        self.assertIsInstance(report, ConflictReport)
        self.assertEqual(report.total_dependencies, 2)
        self.assertGreater(report.conflicts_found, 0)
        self.assertIsNotNone(report.resolution_plan)
    
    def test_assess_resolution_risk(self):
        """Test risk assessment of resolution plan"""
        deps = [
            DependencyInfo('requests', '2.28.0', '>=2.28.0', Ecosystem.PYTHON, source='file1.txt'),
            DependencyInfo('requests', '3.0.0', '>=3.0.0', Ecosystem.PYTHON, source='file2.txt'),
        ]
        
        self.resolver.build_dependency_graph(deps)
        self.resolver.detect_conflicts()
        
        plan = self.resolver.resolve_conflicts()
        
        # Major version change should have higher risk
        self.assertIn(plan.estimated_risk, ['medium', 'high'])


class TestResolutionApplication(unittest.TestCase):
    """Test applying resolution to dependency files"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.resolver = DependencyConflictResolver()
    
    def test_apply_resolution_to_file(self):
        """Test applying resolution updates to dependency file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='requirements.txt', delete=False) as f:
            f.write("requests>=2.20.0\nnumpy>=1.20.0\n")
            req_file = Path(f.name)
        
        try:
            deps = self.resolver.parse_dependency_file(req_file)
            self.resolver.build_dependency_graph(deps)
            
            # Update to new version
            self.resolver._update_dependency_file('requests', '2.28.0', [str(req_file)])
            
            # Verify update
            with open(req_file) as f:
                content = f.read()
                self.assertIn('2.28.0', content)
        finally:
            req_file.unlink()
    
    def test_apply_empty_plan(self):
        """Test applying empty resolution plan"""
        plan = ResolutionPlan(
            conflicts_detected=0,
            conflicts_to_resolve=[],
            strategy=ResolutionStrategy.CONSERVATIVE
        )
        
        result = self.resolver.apply_resolution(plan)
        self.assertTrue(result)


class TestResolutionValidation(unittest.TestCase):
    """Test validation after resolution"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.resolver = DependencyConflictResolver()
    
    def test_validate_no_conflicts_after_resolution(self):
        """Test validation passes when no conflicts remain"""
        deps = [
            DependencyInfo('requests', '2.28.0', '>=2.28.0', Ecosystem.PYTHON),
        ]
        
        self.resolver.build_dependency_graph(deps)
        
        valid, errors = self.resolver.validate_resolution()
        
        self.assertTrue(valid)
        self.assertEqual(len(errors), 0)
    
    def test_validate_conflicts_remain(self):
        """Test validation fails when conflicts remain"""
        deps = [
            DependencyInfo('requests', '2.20.0', '>=2.20.0', Ecosystem.PYTHON, source='file1.txt'),
            DependencyInfo('requests', '3.0.0', '>=3.0.0', Ecosystem.PYTHON, source='file2.txt'),
        ]
        
        self.resolver.build_dependency_graph(deps)
        self.resolver.detect_conflicts()
        
        valid, errors = self.resolver.validate_resolution()
        
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)


if __name__ == '__main__':
    unittest.main()
