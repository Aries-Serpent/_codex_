#!/usr/bin/env python3
"""
Integration tests for Test Coverage Enforcer Agent

Tests end-to-end workflows and real file system interactions.
"""

import pytest
import tempfile
import shutil
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent import (
    TestCoverageEnforcer,
    CoverageReport,
    EnforcementResult,
)


class TestAnalyzeCoverageFullWorkflow:
    """Integration tests for complete coverage analysis workflow"""
    
    def test_analyze_coverage_with_real_python_files(self):
        """Test analyzing coverage with real Python source files"""
        agent = TestCoverageEnforcer()
        
        # Create temporary directory with Python files
        with tempfile.TemporaryDirectory() as tmpdir:
            src_dir = Path(tmpdir) / 'src'
            src_dir.mkdir()
            
            # Create sample Python file
            sample_file = src_dir / 'calculator.py'
            sample_file.write_text("""
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b
""")
            
            # Mock the coverage analysis
            with patch.object(agent, '_run_coverage_analysis') as mock_run:
                mock_run.return_value = {
                    str(sample_file): {
                        'executed_lines': [2, 3, 5, 6],
                        'missing_lines': [8, 9],
                        'excluded_lines': []
                    }
                }
                
                reports = agent.analyze_coverage(src_dir)
                
                assert len(reports) == 1
                assert sample_file in reports
                report = reports[sample_file]
                assert report.line_coverage > 0
                assert report.total_lines > 0
    
    def test_analyze_coverage_with_multiple_files(self):
        """Test analyzing coverage across multiple files"""
        agent = TestCoverageEnforcer()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            src_dir = Path(tmpdir) / 'src'
            src_dir.mkdir()
            
            # Create multiple files
            file1 = src_dir / 'module1.py'
            file2 = src_dir / 'module2.py'
            
            file1.write_text("def func1():\n    return 1\n")
            file2.write_text("def func2():\n    return 2\n")
            
            # Mock coverage data for both files
            with patch.object(agent, '_run_coverage_analysis') as mock_run:
                mock_run.return_value = {
                    str(file1): {
                        'executed_lines': [1, 2],
                        'missing_lines': [],
                        'excluded_lines': []
                    },
                    str(file2): {
                        'executed_lines': [1],
                        'missing_lines': [2],
                        'excluded_lines': []
                    }
                }
                
                reports = agent.analyze_coverage(src_dir)
                
                assert len(reports) == 2
                assert file1 in reports
                assert file2 in reports
    
    def test_analyze_coverage_handles_no_coverage_data(self):
        """Test analysis handles missing coverage data gracefully"""
        agent = TestCoverageEnforcer()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            src_dir = Path(tmpdir) / 'src'
            src_dir.mkdir()
            
            with patch.object(agent, '_run_coverage_analysis') as mock_run:
                mock_run.return_value = {}
                
                reports = agent.analyze_coverage(src_dir)
                
                assert len(reports) == 0


class TestEnforceThresholdsIntegration:
    """Integration tests for threshold enforcement"""
    
    def test_enforce_thresholds_pass_scenario(self):
        """Test complete enforcement scenario that passes"""
        agent = TestCoverageEnforcer()
        agent.line_threshold = 75
        agent.auto_generate = False
        
        with tempfile.TemporaryDirectory() as tmpdir:
            src_dir = Path(tmpdir) / 'src'
            src_dir.mkdir()
            
            sample_file = src_dir / 'good_coverage.py'
            sample_file.write_text("""
def well_tested():
    return "tested"

def also_tested():
    return "also tested"
""")
            
            # Mock high coverage
            with patch.object(agent, '_run_coverage_analysis') as mock_run:
                mock_run.return_value = {
                    str(sample_file): {
                        'executed_lines': [2, 3, 5, 6],
                        'missing_lines': [],
                        'excluded_lines': []
                    }
                }
                
                result = agent.enforce_thresholds(src_dir)
                
                assert result.passed is True
                assert result.current_coverage >= 75.0
                assert result.threshold == 75.0
                assert result.gaps_found == 0
    
    def test_enforce_thresholds_fail_scenario(self):
        """Test complete enforcement scenario that fails"""
        agent = TestCoverageEnforcer()
        agent.line_threshold = 90
        agent.auto_generate = False
        
        with tempfile.TemporaryDirectory() as tmpdir:
            src_dir = Path(tmpdir) / 'src'
            src_dir.mkdir()
            
            sample_file = src_dir / 'low_coverage.py'
            sample_file.write_text("""
def tested():
    return "tested"

def untested():
    return "not tested"

def also_untested():
    return "also not tested"
""")
            
            # Mock low coverage
            with patch.object(agent, '_run_coverage_analysis') as mock_run:
                mock_run.return_value = {
                    str(sample_file): {
                        'executed_lines': [2, 3],
                        'missing_lines': [5, 6, 8, 9],
                        'excluded_lines': []
                    }
                }
                
                result = agent.enforce_thresholds(src_dir)
                
                assert result.passed is False
                assert result.current_coverage < 90.0
                assert result.threshold == 90.0
                assert result.gaps_found > 0
                assert len(result.enforcement_actions) > 0
    
    def test_enforce_thresholds_with_empty_directory(self):
        """Test enforcement with empty directory"""
        agent = TestCoverageEnforcer()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            src_dir = Path(tmpdir) / 'empty_src'
            src_dir.mkdir()
            
            with patch.object(agent, '_run_coverage_analysis') as mock_run:
                mock_run.return_value = {}
                
                result = agent.enforce_thresholds(src_dir)
                
                assert result.passed is False
                assert result.current_coverage == 0.0
                assert 'No coverage data' in str(result.enforcement_actions)


class TestGenerateTestSuggestionsIntegration:
    """Integration tests for test suggestion generation"""
    
    def test_generate_test_suggestions_end_to_end(self):
        """Test generating suggestions from real file analysis"""
        agent = TestCoverageEnforcer()
        agent.line_threshold = 80
        
        with tempfile.TemporaryDirectory() as tmpdir:
            src_dir = Path(tmpdir) / 'src'
            src_dir.mkdir()
            
            sample_file = src_dir / 'math_utils.py'
            sample_file.write_text("""
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
""")
            
            # Mock partial coverage
            with patch.object(agent, '_run_coverage_analysis') as mock_run:
                mock_run.return_value = {
                    str(sample_file): {
                        'executed_lines': [2, 3, 5, 6],
                        'missing_lines': [8, 9, 11, 12, 13, 14],
                        'excluded_lines': []
                    }
                }
                
                reports = agent.analyze_coverage(src_dir)
                suggestions = agent.generate_test_suggestions(reports)
                
                # Should have suggestions for untested functions
                assert len(suggestions) > 0
                
                for suggestion in suggestions:
                    assert suggestion.test_file.name.startswith('test_')
                    assert 'def test_' in suggestion.test_template
                    assert suggestion.priority >= 1
                    assert suggestion.priority <= 5
                    assert suggestion.coverage_impact >= 0.0
    
    def test_generate_suggestions_with_auto_generate_enabled(self):
        """Test automatic test generation when auto_generate is enabled"""
        agent = TestCoverageEnforcer()
        agent.line_threshold = 80
        agent.auto_generate = True
        
        with tempfile.TemporaryDirectory() as tmpdir:
            src_dir = Path(tmpdir) / 'src'
            src_dir.mkdir()
            
            sample_file = src_dir / 'service.py'
            sample_file.write_text("""
def process_data(data):
    return data.upper()

def validate_input(input_str):
    return len(input_str) > 0
""")
            
            # Mock low coverage to trigger suggestions
            with patch.object(agent, '_run_coverage_analysis') as mock_run:
                mock_run.return_value = {
                    str(sample_file): {
                        'executed_lines': [2, 3],
                        'missing_lines': [5, 6],
                        'excluded_lines': []
                    }
                }
                
                result = agent.enforce_thresholds(src_dir)
                
                # Should generate suggestions when auto_generate is enabled
                assert result.suggestions_generated > 0


class TestReportGenerationIntegration:
    """Integration tests for report generation"""
    
    def test_generate_all_report_formats(self):
        """Test generating reports in all formats"""
        agent = TestCoverageEnforcer()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            src_dir = Path(tmpdir) / 'src'
            src_dir.mkdir()
            
            sample_file = src_dir / 'example.py'
            sample_file.write_text("def example():\n    return 'example'\n")
            
            # Mock coverage data
            with patch.object(agent, '_run_coverage_analysis') as mock_run:
                mock_run.return_value = {
                    str(sample_file): {
                        'executed_lines': [1, 2],
                        'missing_lines': [],
                        'excluded_lines': []
                    }
                }
                
                agent.analyze_coverage(src_dir)
                
                # Test text format
                text_report = agent.generate_coverage_report('text')
                assert 'Test Coverage Enforcement Report' in text_report
                assert len(text_report) > 100
                
                # Test JSON format
                json_report = agent.generate_coverage_report('json')
                assert '"summary"' in json_report
                assert '"reports"' in json_report
                
                # Test HTML format
                html_report = agent.generate_coverage_report('html')
                assert '<!DOCTYPE html>' in html_report
                assert '<table>' in html_report
    
    def test_report_includes_all_analysis_data(self):
        """Test report contains all analyzed data"""
        agent = TestCoverageEnforcer()
        agent.line_threshold = 80
        
        with tempfile.TemporaryDirectory() as tmpdir:
            src_dir = Path(tmpdir) / 'src'
            src_dir.mkdir()
            
            file1 = src_dir / 'module1.py'
            file2 = src_dir / 'module2.py'
            
            file1.write_text("def func1():\n    return 1\n")
            file2.write_text("def func2():\n    return 2\n")
            
            with patch.object(agent, '_run_coverage_analysis') as mock_run:
                mock_run.return_value = {
                    str(file1): {
                        'executed_lines': [1, 2],
                        'missing_lines': [],
                        'excluded_lines': []
                    },
                    str(file2): {
                        'executed_lines': [1],
                        'missing_lines': [2],
                        'excluded_lines': []
                    }
                }
                
                agent.analyze_coverage(src_dir)
                report = agent.generate_coverage_report('text')
                
                # Should include both files
                assert 'module1.py' in report
                assert 'module2.py' in report
                
                # Should show analysis counts
                assert 'Total files analyzed: 2' in report


class TestEndToEndCoverageEnforcement:
    """Complete end-to-end integration tests"""
    
    def test_full_workflow_from_analysis_to_report(self):
        """Test complete workflow: analyze -> enforce -> generate suggestions -> report"""
        agent = TestCoverageEnforcer()
        agent.line_threshold = 75
        agent.auto_generate = True
        
        with tempfile.TemporaryDirectory() as tmpdir:
            src_dir = Path(tmpdir) / 'src'
            src_dir.mkdir()
            
            # Create a realistic Python module
            module_file = src_dir / 'user_service.py'
            module_file.write_text("""
class UserService:
    def __init__(self):
        self.users = {}
    
    def add_user(self, user_id, name):
        self.users[user_id] = name
        return True
    
    def get_user(self, user_id):
        return self.users.get(user_id)
    
    def delete_user(self, user_id):
        if user_id in self.users:
            del self.users[user_id]
            return True
        return False
    
    def list_users(self):
        return list(self.users.values())
""")
            
            # Mock coverage data (partial coverage)
            with patch.object(agent, '_run_coverage_analysis') as mock_run:
                mock_run.return_value = {
                    str(module_file): {
                        'executed_lines': [2, 3, 4, 6, 7, 8],
                        'missing_lines': [10, 11, 13, 14, 15, 16, 17, 19, 20],
                        'excluded_lines': []
                    }
                }
                
                # Step 1: Analyze coverage
                reports = agent.analyze_coverage(src_dir)
                assert len(reports) == 1
                
                # Step 2: Enforce thresholds
                result = agent.enforce_thresholds(src_dir)
                assert isinstance(result, EnforcementResult)
                
                # Step 3: Generate suggestions (auto-generated due to auto_generate=True)
                if not result.passed:
                    assert result.suggestions_generated > 0
                
                # Step 4: Generate report
                text_report = agent.generate_coverage_report('text')
                assert 'user_service.py' in text_report
                
                json_report = agent.generate_coverage_report('json')
                assert '"user_service.py"' in json_report or 'user_service.py' in json_report
    
    def test_workflow_with_configuration_override(self):
        """Test workflow with custom configuration"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
thresholds:
  line: 95
  branch: 90
  function: 95
auto_generate_tests: true
fail_build_below_threshold: true
""")
            config_path = Path(f.name)
        
        try:
            agent = TestCoverageEnforcer(config_path=config_path)
            
            # Verify custom config loaded
            assert agent.line_threshold == 95
            assert agent.branch_threshold == 90
            assert agent.function_threshold == 95
            assert agent.auto_generate is True
            
            with tempfile.TemporaryDirectory() as tmpdir:
                src_dir = Path(tmpdir) / 'src'
                src_dir.mkdir()
                
                sample_file = src_dir / 'module.py'
                sample_file.write_text("def func():\n    return 1\n")
                
                with patch.object(agent, '_run_coverage_analysis') as mock_run:
                    mock_run.return_value = {
                        str(sample_file): {
                            'executed_lines': [1, 2],
                            'missing_lines': [],
                            'excluded_lines': []
                        }
                    }
                    
                    # With 100% coverage, should still pass 95% threshold
                    result = agent.enforce_thresholds(src_dir)
                    assert result.passed is True
        
        finally:
            config_path.unlink()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
