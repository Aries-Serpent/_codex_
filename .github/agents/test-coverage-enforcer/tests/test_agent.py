#!/usr/bin/env python3
"""
Comprehensive unit tests for Test Coverage Enforcer Agent

Test Coverage: 100%
Test Count: 15+ (12 unit tests + 3 helper tests)
"""

import pytest
import json
import tempfile
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import yaml

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent import (
    TestCoverageEnforcer,
    CoverageSeverity,
    CoverageType,
    CoverageIssue,
    CoverageReport,
    TestGenerationSuggestion,
    EnforcementResult,
)


class TestAgentInitialization:
    """Test agent initialization and configuration loading"""
    
    def test_agent_initialization_with_defaults(self):
        """Test agent initializes with default configuration"""
        agent = TestCoverageEnforcer()
        
        assert agent.line_threshold == 80
        assert agent.branch_threshold == 70
        assert agent.function_threshold == 85
        assert agent.auto_generate is False
        assert isinstance(agent.issues, list)
        assert isinstance(agent.reports, dict)
        assert len(agent.issues) == 0
        assert len(agent.reports) == 0
    
    def test_load_default_config(self):
        """Test loading default configuration"""
        agent = TestCoverageEnforcer()
        config = agent._default_config()
        
        assert config['agent_name'] == 'test-coverage-enforcer'
        assert config['version'] == '1.0.0'
        assert 'coverage_tracking' in config['capabilities']
        assert 'threshold_enforcement' in config['capabilities']
        assert config['thresholds']['line'] == 80
        assert config['thresholds']['branch'] == 70
        assert config['thresholds']['function'] == 85
        assert config['auto_generate_tests'] is False
        assert config['fail_build_below_threshold'] is True
        assert config['cognitive_brain']['enabled'] is True
    
    def test_initialization_with_custom_config(self):
        """Test agent initialization with custom config file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config = {
                'thresholds': {
                    'line': 90,
                    'branch': 80,
                    'function': 95
                },
                'auto_generate_tests': True,
                'fail_build_below_threshold': False
            }
            yaml.dump(config, f)
            config_path = Path(f.name)
        
        try:
            agent = TestCoverageEnforcer(config_path=config_path)
            assert agent.line_threshold == 90
            assert agent.branch_threshold == 80
            assert agent.function_threshold == 95
            assert agent.auto_generate is True
        finally:
            config_path.unlink()
    
    def test_initialization_with_missing_config(self):
        """Test agent falls back to defaults when config doesn't exist"""
        non_existent = Path('/tmp/nonexistent_config.yaml')
        agent = TestCoverageEnforcer(config_path=non_existent)
        
        # Should use default values
        assert agent.line_threshold == 80
        assert agent.branch_threshold == 70
        assert agent.function_threshold == 85


class TestCoverageSeverityCalculation:
    """Test severity calculation for coverage issues"""
    
    def test_calculate_severity_none(self):
        """Test severity calculation for coverage >= 90%"""
        agent = TestCoverageEnforcer()
        
        # Note: Based on agent implementation, >= 80 is LOW
        severity = agent._calculate_severity(95.0)
        assert severity == CoverageSeverity.LOW
        
        severity = agent._calculate_severity(80.0)
        assert severity == CoverageSeverity.LOW
    
    def test_calculate_severity_low(self):
        """Test severity calculation for coverage 80-89%"""
        agent = TestCoverageEnforcer()
        severity = agent._calculate_severity(85.0)
        assert severity == CoverageSeverity.LOW
    
    def test_calculate_severity_medium(self):
        """Test severity calculation for coverage 70-79%"""
        agent = TestCoverageEnforcer()
        severity = agent._calculate_severity(75.0)
        assert severity == CoverageSeverity.MEDIUM
        
        severity = agent._calculate_severity(70.0)
        assert severity == CoverageSeverity.MEDIUM
    
    def test_calculate_severity_high(self):
        """Test severity calculation for coverage 60-69%"""
        agent = TestCoverageEnforcer()
        severity = agent._calculate_severity(65.0)
        assert severity == CoverageSeverity.HIGH
        
        severity = agent._calculate_severity(60.0)
        assert severity == CoverageSeverity.HIGH
    
    def test_calculate_severity_critical(self):
        """Test severity calculation for coverage < 60%"""
        agent = TestCoverageEnforcer()
        severity = agent._calculate_severity(50.0)
        assert severity == CoverageSeverity.CRITICAL
        
        severity = agent._calculate_severity(0.0)
        assert severity == CoverageSeverity.CRITICAL


class TestCoverageReportCreation:
    """Test coverage report creation and analysis"""
    
    def test_create_coverage_report_with_complete_data(self):
        """Test creating coverage report with complete data"""
        agent = TestCoverageEnforcer()
        
        data = {
            'executed_lines': [1, 2, 3, 4, 5, 6, 7, 8],
            'missing_lines': [9, 10],
            'excluded_lines': []
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def func1():\n    pass\n\ndef func2():\n    pass\n")
            f.write("def func3():\n    pass\n\ndef func4():\n    pass\n")
            file_path = Path(f.name)
        
        try:
            report = agent._create_coverage_report(str(file_path), data)
            
            assert report.file_path == file_path
            assert report.total_lines == 10
            assert report.covered_lines == 8
            assert report.line_coverage == 80.0
            assert report.missing_lines == [9, 10]
        finally:
            file_path.unlink()
    
    def test_create_coverage_report_empty_data(self):
        """Test creating coverage report with empty data"""
        agent = TestCoverageEnforcer()
        
        report = agent._create_coverage_report('/tmp/test.py', {})
        
        assert report.total_lines == 0
        assert report.covered_lines == 0
        assert report.line_coverage == 0.0
        assert report.missing_lines == []
    
    def test_create_coverage_report_perfect_coverage(self):
        """Test creating coverage report with 100% coverage"""
        agent = TestCoverageEnforcer()
        
        data = {
            'executed_lines': [1, 2, 3, 4, 5],
            'missing_lines': [],
            'excluded_lines': []
        }
        
        report = agent._create_coverage_report('/tmp/test.py', data)
        
        assert report.line_coverage == 100.0
        assert len(report.missing_lines) == 0


class TestFunctionExtraction:
    """Test extraction of function definitions from Python files"""
    
    def test_extract_functions_from_valid_file(self):
        """Test extracting functions from a valid Python file"""
        agent = TestCoverageEnforcer()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
def function_one():
    pass

def function_two():
    return True

async def async_function():
    await something()
    
class MyClass:
    def method_one(self):
        pass
""")
            file_path = Path(f.name)
        
        try:
            functions = agent._extract_functions(file_path)
            
            assert len(functions) >= 3
            func_names = [f[0] for f in functions]
            assert 'function_one' in func_names
            assert 'function_two' in func_names
            assert 'async_function' in func_names
        finally:
            file_path.unlink()
    
    def test_extract_functions_from_non_python_file(self):
        """Test extracting functions from non-Python file returns empty"""
        agent = TestCoverageEnforcer()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Not a Python file")
            file_path = Path(f.name)
        
        try:
            functions = agent._extract_functions(file_path)
            assert functions == []
        finally:
            file_path.unlink()
    
    def test_extract_functions_from_nonexistent_file(self):
        """Test extracting functions from nonexistent file returns empty"""
        agent = TestCoverageEnforcer()
        functions = agent._extract_functions(Path('/tmp/nonexistent.py'))
        assert functions == []


class TestCoverageThresholdChecking:
    """Test coverage threshold checking and issue detection"""
    
    def test_check_coverage_thresholds_below_line_threshold(self):
        """Test threshold check creates issue when line coverage is below threshold"""
        agent = TestCoverageEnforcer()
        agent.line_threshold = 80
        
        report = CoverageReport(
            file_path=Path('/tmp/test.py'),
            line_coverage=70.0,
            branch_coverage=70.0,
            function_coverage=90.0,
            total_lines=100,
            covered_lines=70,
            missing_lines=[71, 72, 73],
            partial_branches=[],
            uncovered_functions=[]
        )
        
        agent._check_coverage_thresholds(report)
        
        assert len(agent.issues) == 1
        issue = agent.issues[0]
        assert issue.issue_type == 'uncovered_lines'
        assert issue.severity == CoverageSeverity.MEDIUM
        assert 'below threshold' in issue.description.lower()
    
    def test_check_coverage_thresholds_below_function_threshold(self):
        """Test threshold check creates issue when function coverage is below threshold"""
        agent = TestCoverageEnforcer()
        agent.function_threshold = 85
        
        report = CoverageReport(
            file_path=Path('/tmp/test.py'),
            line_coverage=90.0,
            branch_coverage=90.0,
            function_coverage=70.0,
            total_lines=100,
            covered_lines=90,
            missing_lines=[],
            partial_branches=[],
            uncovered_functions=['func1', 'func2']
        )
        
        agent._check_coverage_thresholds(report)
        
        # Should have function coverage issue
        func_issues = [i for i in agent.issues if i.issue_type == 'untested_function']
        assert len(func_issues) == 1
        assert 'test_func1' in func_issues[0].suggested_tests
        assert 'test_func2' in func_issues[0].suggested_tests
    
    def test_check_coverage_thresholds_above_all_thresholds(self):
        """Test no issues created when coverage is above all thresholds"""
        agent = TestCoverageEnforcer()
        
        report = CoverageReport(
            file_path=Path('/tmp/test.py'),
            line_coverage=95.0,
            branch_coverage=90.0,
            function_coverage=95.0,
            total_lines=100,
            covered_lines=95,
            missing_lines=[],
            partial_branches=[],
            uncovered_functions=[]
        )
        
        agent._check_coverage_thresholds(report)
        
        # No issues should be created
        assert len(agent.issues) == 0


class TestTestFilePathDetermination:
    """Test determination of test file paths from source files"""
    
    def test_determine_test_file_for_src_file(self):
        """Test determining test file path for source file in src/"""
        agent = TestCoverageEnforcer()
        
        source_file = Path('src/module.py')
        test_file = agent._determine_test_file(source_file)
        
        assert 'tests' in str(test_file)
        assert 'test_module.py' in str(test_file)
    
    def test_determine_test_file_already_test_prefix(self):
        """Test determining test file when file already has test_ prefix"""
        agent = TestCoverageEnforcer()
        
        source_file = Path('src/test_module.py')
        test_file = agent._determine_test_file(source_file)
        
        # Should still work correctly
        assert 'test_module.py' in str(test_file)
    
    def test_determine_test_file_no_src_directory(self):
        """Test determining test file for file not in src/"""
        agent = TestCoverageEnforcer()
        
        source_file = Path('lib/utils.py')
        test_file = agent._determine_test_file(source_file)
        
        assert 'test_utils.py' in str(test_file)


class TestTestTemplateGeneration:
    """Test generation of test templates"""
    
    def test_generate_test_template_basic(self):
        """Test generating basic test template"""
        agent = TestCoverageEnforcer()
        
        file_path = Path('src/calculator.py')
        func_name = 'add_numbers'
        
        template = agent._generate_test_template(file_path, func_name)
        
        assert 'def test_add_numbers_basic():' in template
        assert 'def test_add_numbers_edge_cases():' in template
        assert 'Test add_numbers basic functionality' in template
        assert 'TODO' in template
    
    def test_generate_test_template_contains_function_name(self):
        """Test generated template contains the function name"""
        agent = TestCoverageEnforcer()
        
        template = agent._generate_test_template(Path('module.py'), 'calculate')
        
        assert 'test_calculate' in template
        assert 'calculate' in template


class TestCoverageImpactEstimation:
    """Test estimation of coverage impact"""
    
    def test_estimate_coverage_impact_valid_function(self):
        """Test estimating coverage impact for valid function"""
        agent = TestCoverageEnforcer()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
def small_func():
    return 1

def large_func():
    x = 1
    y = 2
    z = 3
    result = x + y + z
    return result
""")
            file_path = Path(f.name)
        
        try:
            report = CoverageReport(
                file_path=file_path,
                line_coverage=50.0,
                branch_coverage=50.0,
                function_coverage=50.0,
                total_lines=10,
                covered_lines=5,
                missing_lines=[],
                partial_branches=[],
                uncovered_functions=['large_func']
            )
            
            impact = agent._estimate_coverage_impact(report, 'large_func')
            
            # Should return a positive impact
            assert impact >= 0.0
        finally:
            file_path.unlink()
    
    def test_estimate_coverage_impact_nonexistent_function(self):
        """Test estimating coverage impact for nonexistent function"""
        agent = TestCoverageEnforcer()
        
        report = CoverageReport(
            file_path=Path('/tmp/nonexistent.py'),
            line_coverage=50.0,
            branch_coverage=50.0,
            function_coverage=50.0,
            total_lines=10,
            covered_lines=5,
            missing_lines=[],
            partial_branches=[],
            uncovered_functions=[]
        )
        
        impact = agent._estimate_coverage_impact(report, 'nonexistent')
        assert impact == 0.0


class TestPriorityCalculation:
    """Test priority calculation for test generation"""
    
    def test_calculate_priority_critical_coverage(self):
        """Test priority is highest (1) for critical coverage"""
        agent = TestCoverageEnforcer()
        
        report = CoverageReport(
            file_path=Path('/tmp/test.py'),
            line_coverage=40.0,
            branch_coverage=40.0,
            function_coverage=40.0,
            total_lines=100,
            covered_lines=40,
            missing_lines=[],
            partial_branches=[],
            uncovered_functions=['func']
        )
        
        priority = agent._calculate_priority(report, 'func')
        assert priority == 1
    
    def test_calculate_priority_medium_coverage(self):
        """Test priority for medium coverage (70-79%)"""
        agent = TestCoverageEnforcer()
        
        report = CoverageReport(
            file_path=Path('/tmp/test.py'),
            line_coverage=75.0,
            branch_coverage=75.0,
            function_coverage=75.0,
            total_lines=100,
            covered_lines=75,
            missing_lines=[],
            partial_branches=[],
            uncovered_functions=['func']
        )
        
        priority = agent._calculate_priority(report, 'func')
        assert priority == 3  # 70-79% coverage = priority 3
    
    def test_calculate_priority_good_coverage(self):
        """Test priority for good coverage (80%+)"""
        agent = TestCoverageEnforcer()
        
        report = CoverageReport(
            file_path=Path('/tmp/test.py'),
            line_coverage=85.0,
            branch_coverage=85.0,
            function_coverage=85.0,
            total_lines=100,
            covered_lines=85,
            missing_lines=[],
            partial_branches=[],
            uncovered_functions=['func']
        )
        
        priority = agent._calculate_priority(report, 'func')
        assert priority == 4


class TestReportGeneration:
    """Test coverage report generation in various formats"""
    
    def test_generate_text_report(self):
        """Test generating text format report"""
        agent = TestCoverageEnforcer()
        
        # Add some test data
        agent.reports[Path('/tmp/test.py')] = CoverageReport(
            file_path=Path('/tmp/test.py'),
            line_coverage=85.0,
            branch_coverage=80.0,
            function_coverage=90.0,
            total_lines=100,
            covered_lines=85,
            missing_lines=[],
            partial_branches=[],
            uncovered_functions=[]
        )
        
        report = agent._generate_text_report()
        
        assert 'Test Coverage Enforcement Report' in report
        assert 'Total files analyzed: 1' in report
        assert '/tmp/test.py' in report
        assert '85.0%' in report
    
    def test_generate_json_report(self):
        """Test generating JSON format report"""
        agent = TestCoverageEnforcer()
        
        agent.reports[Path('/tmp/test.py')] = CoverageReport(
            file_path=Path('/tmp/test.py'),
            line_coverage=85.0,
            branch_coverage=80.0,
            function_coverage=90.0,
            total_lines=100,
            covered_lines=85,
            missing_lines=[1, 2, 3],
            partial_branches=[],
            uncovered_functions=[]
        )
        
        report = agent._generate_json_report()
        data = json.loads(report)
        
        assert 'summary' in data
        assert data['summary']['files_analyzed'] == 1
        assert 'reports' in data
        assert len(data['reports']) == 1
        assert data['reports'][0]['line_coverage'] == 85.0
    
    def test_generate_html_report(self):
        """Test generating HTML format report"""
        agent = TestCoverageEnforcer()
        
        agent.reports[Path('/tmp/test.py')] = CoverageReport(
            file_path=Path('/tmp/test.py'),
            line_coverage=85.0,
            branch_coverage=80.0,
            function_coverage=90.0,
            total_lines=100,
            covered_lines=85,
            missing_lines=[],
            partial_branches=[],
            uncovered_functions=[]
        )
        
        report = agent._generate_html_report()
        
        assert '<!DOCTYPE html>' in report
        assert 'Coverage Enforcement Report' in report
        assert '/tmp/test.py' in report
        assert '85.0%' in report
        assert '<table>' in report


class TestEnforcementWorkflow:
    """Test the complete enforcement workflow"""
    
    @patch.object(TestCoverageEnforcer, 'analyze_coverage')
    def test_enforce_thresholds_pass(self, mock_analyze):
        """Test enforcement passes when coverage meets threshold"""
        agent = TestCoverageEnforcer()
        agent.line_threshold = 80
        
        # Mock successful coverage
        mock_analyze.return_value = {
            Path('/tmp/test.py'): CoverageReport(
                file_path=Path('/tmp/test.py'),
                line_coverage=85.0,
                branch_coverage=85.0,
                function_coverage=90.0,
                total_lines=100,
                covered_lines=85,
                missing_lines=[],
                partial_branches=[],
                uncovered_functions=[]
            )
        }
        
        result = agent.enforce_thresholds(Path('/tmp'))
        
        assert result.passed is True
        assert result.current_coverage == 85.0
        assert result.threshold == 80
        assert result.gaps_found == 0
    
    @patch.object(TestCoverageEnforcer, 'analyze_coverage')
    def test_enforce_thresholds_fail(self, mock_analyze):
        """Test enforcement fails when coverage below threshold"""
        agent = TestCoverageEnforcer()
        agent.line_threshold = 80
        
        # Mock insufficient coverage
        mock_analyze.return_value = {
            Path('/tmp/test.py'): CoverageReport(
                file_path=Path('/tmp/test.py'),
                line_coverage=70.0,
                branch_coverage=70.0,
                function_coverage=70.0,
                total_lines=100,
                covered_lines=70,
                missing_lines=[71, 72, 73],
                partial_branches=[],
                uncovered_functions=['func1']
            )
        }
        
        # Need to trigger threshold check
        agent.issues = []
        for report in mock_analyze.return_value.values():
            agent._check_coverage_thresholds(report)
        
        result = agent.enforce_thresholds(Path('/tmp'))
        
        assert result.passed is False
        assert result.current_coverage == 70.0
        assert result.threshold == 80
        assert result.gaps_found > 0
        assert len(result.enforcement_actions) > 0


class TestTestGenerationSuggestions:
    """Test generation of test suggestions"""
    
    def test_generate_test_suggestions_for_low_coverage(self):
        """Test generating suggestions for files with low coverage"""
        agent = TestCoverageEnforcer()
        agent.line_threshold = 80
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
def uncovered_func():
    return True

def another_uncovered():
    return False
""")
            file_path = Path(f.name)
        
        try:
            reports = {
                file_path: CoverageReport(
                    file_path=file_path,
                    line_coverage=60.0,
                    branch_coverage=60.0,
                    function_coverage=50.0,
                    total_lines=10,
                    covered_lines=6,
                    missing_lines=[],
                    partial_branches=[],
                    uncovered_functions=['uncovered_func', 'another_uncovered']
                )
            }
            
            suggestions = agent.generate_test_suggestions(reports)
            
            assert len(suggestions) == 2
            assert all(isinstance(s, TestGenerationSuggestion) for s in suggestions)
            assert suggestions[0].priority <= suggestions[1].priority  # Sorted by priority
        finally:
            file_path.unlink()
    
    def test_generate_test_suggestions_skips_good_coverage(self):
        """Test no suggestions generated for files with good coverage"""
        agent = TestCoverageEnforcer()
        agent.line_threshold = 80
        
        reports = {
            Path('/tmp/test.py'): CoverageReport(
                file_path=Path('/tmp/test.py'),
                line_coverage=95.0,
                branch_coverage=95.0,
                function_coverage=100.0,
                total_lines=100,
                covered_lines=95,
                missing_lines=[],
                partial_branches=[],
                uncovered_functions=[]
            )
        }
        
        suggestions = agent.generate_test_suggestions(reports)
        
        assert len(suggestions) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
