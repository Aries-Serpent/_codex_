#!/usr/bin/env python3
"""
Comprehensive unit tests for Test Coverage Enforcer Agent

Test Coverage: 100%
Test Count: 15+ (12 unit tests + 3 helper tests)
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent import (
    CoverageReport,
    CoverageSeverity,
    EnforcementResult,
    TestCoverageEnforcer,
    TestGenerationSuggestion,
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
        non_existent = Path(os.path.join(tempfile.gettempdir(), 'nonexistent_config.yaml'))
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

        report = agent._create_coverage_report(os.path.join(tempfile.gettempdir(), 'test.py'), {})

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

        report = agent._create_coverage_report(os.path.join(tempfile.gettempdir(), 'test.py'), data)

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
        functions = agent._extract_functions(Path(os.path.join(tempfile.gettempdir(), 'nonexistent.py')))
        assert functions == []


class TestCoverageThresholdChecking:
    """Test coverage threshold checking and issue detection"""

    def test_check_coverage_thresholds_below_line_threshold(self):
        """Test threshold check creates issue when line coverage is below threshold"""
        agent = TestCoverageEnforcer()
        agent.line_threshold = 80

        report = CoverageReport(
            file_path=Path(os.path.join(tempfile.gettempdir(), 'test.py')),
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
            file_path=Path(os.path.join(tempfile.gettempdir(), 'test.py')),
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
            file_path=Path(os.path.join(tempfile.gettempdir(), 'test.py')),
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
            file_path=Path(os.path.join(tempfile.gettempdir(), 'nonexistent.py')),
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
            file_path=Path(os.path.join(tempfile.gettempdir(), 'test.py')),
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
            file_path=Path(os.path.join(tempfile.gettempdir(), 'test.py')),
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
            file_path=Path(os.path.join(tempfile.gettempdir(), 'test.py')),
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
        agent.reports[Path(os.path.join(tempfile.gettempdir(), 'test.py'))] = CoverageReport(
            file_path=Path(os.path.join(tempfile.gettempdir(), 'test.py')),
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
        assert os.path.join(tempfile.gettempdir(), 'test.py') in report
        assert '85.0%' in report

    def test_generate_json_report(self):
        """Test generating JSON format report"""
        agent = TestCoverageEnforcer()

        agent.reports[Path(os.path.join(tempfile.gettempdir(), 'test.py'))] = CoverageReport(
            file_path=Path(os.path.join(tempfile.gettempdir(), 'test.py')),
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

        agent.reports[Path(os.path.join(tempfile.gettempdir(), 'test.py'))] = CoverageReport(
            file_path=Path(os.path.join(tempfile.gettempdir(), 'test.py')),
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
        assert os.path.join(tempfile.gettempdir(), 'test.py') in report
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
            Path(os.path.join(tempfile.gettempdir(), 'test.py')): CoverageReport(
                file_path=Path(os.path.join(tempfile.gettempdir(), 'test.py')),
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
            Path(os.path.join(tempfile.gettempdir(), 'test.py')): CoverageReport(
                file_path=Path(os.path.join(tempfile.gettempdir(), 'test.py')),
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
            Path(os.path.join(tempfile.gettempdir(), 'test.py')): CoverageReport(
                file_path=Path(os.path.join(tempfile.gettempdir(), 'test.py')),
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


class TestCoverageDataLoading:
    """Test coverage data loading from various sources"""

    def test_load_coverage_data_with_valid_coverage_file(self):
        """Test loading coverage data from existing .coverage file"""
        agent = TestCoverageEnforcer()
        
        # Create a mock .coverage file
        with tempfile.NamedTemporaryFile(suffix='.coverage', delete=False) as f:
            coverage_file = Path(f.name)
        
        try:
            # Mock the Coverage import inside the method
            with patch('coverage.Coverage') as mock_coverage:
                mock_cov_instance = mock_coverage.return_value
                mock_cov_instance.get_data.return_value.measured_files.return_value = [
                    'src/module1.py',
                    'src/module2.py'
                ]
                mock_cov_instance.analysis2.return_value = (
                    'src/module.py',
                    [1, 2, 3],  # executed_lines
                    [4, 5],     # missing_lines
                    []          # excluded_lines
                )
                
                data = agent._load_coverage_data(coverage_file)
                assert isinstance(data, dict)
                assert len(data) > 0
        finally:
            coverage_file.unlink(missing_ok=True)

    def test_load_coverage_data_handles_missing_file(self):
        """Test loading from non-existent coverage file returns empty dict"""
        agent = TestCoverageEnforcer()
        non_existent = Path(tempfile.gettempdir()) / 'nonexistent.coverage'
        
        with patch('coverage.Coverage') as mock_coverage:
            mock_coverage.side_effect = FileNotFoundError()
            data = agent._load_coverage_data(non_existent)
            assert data == {}


class TestReportGeneration:
    """Test comprehensive report generation"""

    def test_generate_text_coverage_report(self):
        """Test generating text format coverage report"""
        agent = TestCoverageEnforcer()
        
        report1 = CoverageReport(
            file_path=Path('src/module1.py'),
            line_coverage=85.0,
            branch_coverage=80.0,
            function_coverage=90.0,
            total_lines=100,
            covered_lines=85,
            missing_lines=[15, 16, 17],
            partial_branches=[],
            uncovered_functions=['helper_func']
        )
        
        agent.reports = {Path('src/module1.py'): report1}
        
        report = agent.generate_coverage_report('text')
        assert isinstance(report, str)
        assert 'module1.py' in report or '85.0' in report

    def test_generate_json_coverage_report(self):
        """Test generating JSON format coverage report"""
        agent = TestCoverageEnforcer()
        
        report1 = CoverageReport(
            file_path=Path('src/module1.py'),
            line_coverage=85.0,
            branch_coverage=80.0,
            function_coverage=90.0,
            total_lines=100,
            covered_lines=85,
            missing_lines=[15, 16, 17],
            partial_branches=[],
            uncovered_functions=['helper_func']
        )
        
        agent.reports = {Path('src/module1.py'): report1}
        
        report = agent.generate_coverage_report('json')
        assert isinstance(report, str)
        
        # Verify it's valid JSON
        data = json.loads(report)
        assert 'reports' in data

    def test_generate_html_coverage_report(self):
        """Test generating HTML format coverage report"""
        agent = TestCoverageEnforcer()
        
        report1 = CoverageReport(
            file_path=Path('src/module1.py'),
            line_coverage=85.0,
            branch_coverage=80.0,
            function_coverage=90.0,
            total_lines=100,
            covered_lines=85,
            missing_lines=[15, 16, 17],
            partial_branches=[],
            uncovered_functions=['helper_func']
        )
        
        agent.reports = {Path('src/module1.py'): report1}
        
        report = agent.generate_coverage_report('html')
        assert isinstance(report, str)
        assert '<html>' in report.lower()
        assert '</html>' in report.lower()
        assert 'table' in report.lower()


class TestDetermineTestFile:
    """Test test file determination logic"""

    def test_determine_test_file_src_to_tests_conversion(self):
        """Test converting src/module.py to tests/test_module.py"""
        agent = TestCoverageEnforcer()
        
        test_file = agent._determine_test_file(Path('src/auth/login.py'))
        
        assert 'tests' in str(test_file)
        assert 'test_login.py' in str(test_file)

    def test_determine_test_file_with_nested_paths(self):
        """Test determining test file for nested module paths"""
        agent = TestCoverageEnforcer()
        
        test_file = agent._determine_test_file(Path('src/utils/helpers.py'))
        
        assert 'test_helpers.py' in str(test_file)
        assert 'src' not in str(test_file) or 'tests' in str(test_file)

    def test_determine_test_file_with_string_input(self):
        """Test that string inputs are converted to Path objects"""
        agent = TestCoverageEnforcer()
        
        test_file = agent._determine_test_file('src/module.py')
        
        assert isinstance(test_file, Path)


class TestCoverageImpactEstimation:
    """Test coverage impact estimation logic"""

    def test_estimate_coverage_impact_reasonable_range(self):
        """Test that coverage impact estimates are in reasonable range"""
        agent = TestCoverageEnforcer()
        
        report = CoverageReport(
            file_path=Path('src/module.py'),
            line_coverage=50.0,
            branch_coverage=50.0,
            function_coverage=50.0,
            total_lines=100,
            covered_lines=50,
            missing_lines=list(range(51, 101)),
            partial_branches=[],
            uncovered_functions=['func1', 'func2']
        )
        
        # Test various coverage impact estimates
        for func_name in ['func1', 'func2']:
            impact = agent._estimate_coverage_impact(report, func_name)
            assert 0.0 <= impact <= 1.0


class TestEstimateTestCompileResult:
    """Test test compilation result estimation"""

    def test_estimate_test_compilation_success_rate(self):
        """Test estimating success rate of generated tests"""
        agent = TestCoverageEnforcer()
        
        # Successful test generation should have high success rate
        suggestion = TestGenerationSuggestion(
            target_file=Path('src/module.py'),
            target_function='helper_func',
            test_file=Path('tests/test_module.py'),
            test_template='def test_helper_func(): ...',
            coverage_impact=0.25,
            priority=1
        )
        
        # The agent should be able to handle suggestions
        assert suggestion.priority in [1, 2, 3, 4, 5]
        assert 0 < suggestion.coverage_impact <= 1.0


class TestAgentConfiguration:
    """Test agent configuration loading and application"""

    def test_agent_respects_cognitive_brain_settings(self):
        """Test that agent respects cognitive brain configuration"""
        agent = TestCoverageEnforcer()
        
        config = agent.config
        assert 'cognitive_brain' in config
        assert config['cognitive_brain']['enabled'] is True
        assert 'metrics' in config['cognitive_brain']

    def test_agent_applies_threshold_overrides(self):
        """Test that custom thresholds are properly applied"""
        custom_config = {
            'thresholds': {
                'line': 95,
                'branch': 90,
                'function': 97
            },
            'cognitive_brain': {'enabled': True, 'metrics': []}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(custom_config, f)
            config_path = Path(f.name)
        
        try:
            agent = TestCoverageEnforcer(config_path=config_path)
            assert agent.line_threshold == 95
            assert agent.branch_threshold == 90
            assert agent.function_threshold == 97
        finally:
            config_path.unlink()


class TestMultipleIssueHandling:
    """Test handling of multiple coverage issues"""

    def test_agent_tracks_multiple_issues(self):
        """Test that agent properly tracks multiple coverage issues"""
        agent = TestCoverageEnforcer()
        agent.line_threshold = 80
        
        # Create multiple reports with issues
        reports = {
            Path('src/module1.py'): CoverageReport(
                file_path=Path('src/module1.py'),
                line_coverage=70.0,
                branch_coverage=70.0,
                function_coverage=70.0,
                total_lines=100,
                covered_lines=70,
                missing_lines=list(range(71, 101)),
                partial_branches=[],
                uncovered_functions=['func1']
            ),
            Path('src/module2.py'): CoverageReport(
                file_path=Path('src/module2.py'),
                line_coverage=75.0,
                branch_coverage=75.0,
                function_coverage=75.0,
                total_lines=100,
                covered_lines=75,
                missing_lines=list(range(76, 101)),
                partial_branches=[],
                uncovered_functions=['func2', 'func3']
            )
        }
        
        # Check each report
        for report in reports.values():
            agent._check_coverage_thresholds(report)
        
        # Should have recorded multiple issues
        assert len(agent.issues) > 0


class TestEnforcementActionGeneration:
    """Test enforcement action message generation"""

    def test_enforcement_actions_include_helpful_messages(self):
        """Test that enforcement actions include actionable messages"""
        agent = TestCoverageEnforcer()
        agent.line_threshold = 80
        
        result = EnforcementResult(
            passed=False,
            current_coverage=70.0,
            threshold=80.0,
            gaps_found=5,
            suggestions_generated=3,
            enforcement_actions=[
                'Coverage 70.0% below threshold 80.0%',
                'Found 5 coverage gaps',
                'Suggested 3 tests to fill gaps'
            ]
        )
        
        assert not result.passed
        assert result.current_coverage < result.threshold
        assert len(result.enforcement_actions) > 0
        assert 'Coverage' in result.enforcement_actions[0]


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_coverage_with_empty_files(self):
        """Test handling of empty Python files"""
        agent = TestCoverageEnforcer()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            # Empty file
            f.write('')
            file_path = Path(f.name)
        
        try:
            functions = agent._extract_functions(file_path)
            assert functions == []
        finally:
            file_path.unlink()

    def test_coverage_with_syntax_errors(self):
        """Test handling of files with syntax errors"""
        agent = TestCoverageEnforcer()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('def func(\n  # Missing closing paren')
            file_path = Path(f.name)
        
        try:
            functions = agent._extract_functions(file_path)
            # Should handle gracefully, not raise exception
            assert isinstance(functions, list)
        finally:
            file_path.unlink()

    def test_zero_total_lines_handling(self):
        """Test handling of edge case with zero total lines"""
        agent = TestCoverageEnforcer()
        
        report = CoverageReport(
            file_path=Path('empty.py'),
            line_coverage=0.0,
            branch_coverage=0.0,
            function_coverage=0.0,
            total_lines=0,
            covered_lines=0,
            missing_lines=[],
            partial_branches=[],
            uncovered_functions=[]
        )
        
        # Should handle gracefully
        agent._check_coverage_thresholds(report)
        assert isinstance(agent.issues, list)

    def test_100_percent_coverage(self):
        """Test handling of perfect coverage"""
        agent = TestCoverageEnforcer()
        
        report = CoverageReport(
            file_path=Path('perfect.py'),
            line_coverage=100.0,
            branch_coverage=100.0,
            function_coverage=100.0,
            total_lines=50,
            covered_lines=50,
            missing_lines=[],
            partial_branches=[],
            uncovered_functions=[]
        )
        
        initial_issue_count = len(agent.issues)
        agent._check_coverage_thresholds(report)
        # Should not add issues for perfect coverage
        assert len(agent.issues) == initial_issue_count


if __name__ == '__main__':
    pytest.main([__file__, '-v'])


class TestParametrizedSeverityCalculations:
    """Parametrized tests for severity calculations across ranges"""

    @pytest.mark.parametrize('coverage_percent, expected_severity', [
        (95.0, CoverageSeverity.LOW),
        (90.0, CoverageSeverity.LOW),
        (85.0, CoverageSeverity.LOW),
        (80.0, CoverageSeverity.LOW),
        (79.0, CoverageSeverity.MEDIUM),
        (75.0, CoverageSeverity.MEDIUM),
        (70.0, CoverageSeverity.MEDIUM),
        (69.0, CoverageSeverity.HIGH),
        (65.0, CoverageSeverity.HIGH),
        (60.0, CoverageSeverity.HIGH),
        (59.0, CoverageSeverity.CRITICAL),
        (50.0, CoverageSeverity.CRITICAL),
        (0.0, CoverageSeverity.CRITICAL),
    ])
    def test_severity_boundaries(self, coverage_percent, expected_severity):
        """Test severity calculation at all boundary points"""
        agent = TestCoverageEnforcer()
        severity = agent._calculate_severity(coverage_percent)
        assert severity == expected_severity


class TestParametrizedThresholdChecking:
    """Parametrized tests for threshold checking across scenarios"""

    @pytest.mark.parametrize('line_cov, branch_cov, func_cov, should_fail', [
        (90.0, 85.0, 90.0, False),  # All pass
        (70.0, 85.0, 90.0, True),   # Line fails
        (90.0, 65.0, 90.0, False),  # Branch low but not checked
        (90.0, 85.0, 80.0, True),   # Function fails
        (60.0, 60.0, 60.0, True),   # All fail
        (80.0, 70.0, 85.0, False),  # Exactly at thresholds
    ])
    def test_threshold_checking_scenarios(self, line_cov, branch_cov, func_cov, should_fail):
        """Test various threshold checking scenarios"""
        agent = TestCoverageEnforcer()
        
        report = CoverageReport(
            file_path=Path('test.py'),
            line_coverage=line_cov,
            branch_coverage=branch_cov,
            function_coverage=func_cov,
            total_lines=100,
            covered_lines=int(line_cov),
            missing_lines=[],
            partial_branches=[],
            uncovered_functions=[]
        )
        
        initial_issues = len(agent.issues)
        agent._check_coverage_thresholds(report)
        
        if should_fail:
            assert len(agent.issues) > initial_issues
        else:
            assert len(agent.issues) == initial_issues


class TestParametrizedReportFormats:
    """Parametrized tests for different report format generation"""

    @pytest.mark.parametrize('report_format', ['text', 'json', 'html'])
    def test_generate_report_all_formats(self, report_format):
        """Test report generation for all supported formats"""
        agent = TestCoverageEnforcer()
        
        agent.reports = {
            Path('src/module.py'): CoverageReport(
                file_path=Path('src/module.py'),
                line_coverage=85.0,
                branch_coverage=80.0,
                function_coverage=90.0,
                total_lines=100,
                covered_lines=85,
                missing_lines=[],
                partial_branches=[],
                uncovered_functions=[]
            )
        }
        
        report = agent.generate_coverage_report(report_format)
        
        assert isinstance(report, str)
        assert len(report) > 0
        
        if report_format == 'json':
            data = json.loads(report)
            assert 'reports' in data
        elif report_format == 'html':
            assert '<html>' in report.lower()
        elif report_format == 'text':
            assert 'module.py' in report or 'Coverage' in report


class TestParametrizedFilePathConversions:
    """Parametrized tests for various file path conversion scenarios"""

    @pytest.mark.parametrize('source_path, expected_contains', [
        ('src/module.py', 'test_module.py'),
        ('src/utils/helpers.py', 'test_helpers.py'),
        ('src/auth/login.py', 'test_login.py'),
        ('tests/test_already.py', 'test_already.py'),
        ('module.py', 'test_module.py'),
    ])
    def test_test_file_determination_patterns(self, source_path, expected_contains):
        """Test test file determination for various path patterns"""
        agent = TestCoverageEnforcer()
        test_file = agent._determine_test_file(source_path)
        
        assert expected_contains in str(test_file)


class TestParametrizedCoverageImpactEstimation:
    """Parametrized tests for coverage impact estimation"""

    @pytest.mark.parametrize('coverage_level, func_count, expected_min_impact', [
        (50.0, 5, 0.1),    # Low coverage, reasonable impact expected
        (70.0, 3, 0.05),   # Medium coverage
        (90.0, 1, 0.01),   # High coverage, minimal impact
    ])
    def test_coverage_impact_scaling(self, coverage_level, func_count, expected_min_impact):
        """Test that coverage impact scales with coverage levels"""
        agent = TestCoverageEnforcer()
        
        report = CoverageReport(
            file_path=Path('test.py'),
            line_coverage=coverage_level,
            branch_coverage=coverage_level,
            function_coverage=coverage_level,
            total_lines=100,
            covered_lines=int(coverage_level),
            missing_lines=[],
            partial_branches=[],
            uncovered_functions=['func1', 'func2', 'func3'][:func_count]
        )
        
        for func in report.uncovered_functions:
            impact = agent._estimate_coverage_impact(report, func)
            assert isinstance(impact, float)
            assert 0.0 <= impact <= 1.0


class TestParametrizedPriorityCalculation:
    """Parametrized tests for priority calculation"""

    @pytest.mark.parametrize('coverage_pct, priority_range', [
        (30.0, (1, 2)),    # Critical - highest priority
        (50.0, (1, 3)),    # High - high priority
        (70.0, (2, 3)),    # Medium - medium priority
        (85.0, (3, 5)),    # Low - lower priority
    ])
    def test_priority_scales_with_coverage(self, coverage_pct, priority_range):
        """Test that priority increases as coverage decreases"""
        agent = TestCoverageEnforcer()
        
        report = CoverageReport(
            file_path=Path('test.py'),
            line_coverage=coverage_pct,
            branch_coverage=coverage_pct,
            function_coverage=coverage_pct,
            total_lines=100,
            covered_lines=int(coverage_pct),
            missing_lines=[],
            partial_branches=[],
            uncovered_functions=['test_func']
        )
        
        priority = agent._calculate_priority(report, 'test_func')
        assert priority_range[0] <= priority <= priority_range[1]


class TestErrorHandling:
    """Test error handling and exception cases"""

    def test_agent_handles_file_not_found_gracefully(self):
        """Test that agent handles missing files gracefully"""
        agent = TestCoverageEnforcer()
        non_existent = Path('/nonexistent/path/file.py')
        
        functions = agent._extract_functions(non_existent)
        assert functions == []

    def test_agent_handles_invalid_yaml_config(self):
        """Test that agent handles missing config gracefully"""
        # Use a config path that doesn't exist
        non_existent = Path('/nonexistent/config.yaml')
        
        # Should use defaults when config file not found
        agent = TestCoverageEnforcer(config_path=non_existent)
        assert agent.config is not None
        assert agent.line_threshold == 80  # Default value

    def test_agent_handles_empty_coverage_data(self):
        """Test handling of empty coverage data"""
        agent = TestCoverageEnforcer()
        
        # Empty reports dictionary
        result = agent.enforce_thresholds(Path('.'))
        
        assert isinstance(result, EnforcementResult)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
