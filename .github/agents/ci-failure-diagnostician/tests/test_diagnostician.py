"""
Unit tests for CI Failure Diagnostician

Tests root cause analysis, dependency detection, evidence building,
and report generation capabilities.
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from datetime import datetime

# Import the diagnostician
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
from diagnostician import CIFailureDiagnostician, DiagnosticReport


class TestCIFailureDiagnostician:
    """Test suite for CI failure diagnostician"""
    
    @pytest.fixture
    def diagnostician(self):
        """Create diagnostician instance"""
        return CIFailureDiagnostician()
    
    @pytest.fixture
    def temp_log_file(self):
        """Create temporary log file"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            yield Path(f.name)
        Path(f.name).unlink(missing_ok=True)
    
    @pytest.fixture
    def mock_cognitive_brain(self, tmp_path):
        """Create mock cognitive brain directory"""
        brain_path = tmp_path / "self_healing"
        brain_path.mkdir()
        
        # Create sample attempt file
        attempt = {
            'timestamp': '2026-01-10T12:00:00Z',
            'fix_type': 'dependency_conflict',
            'outcome': 'success',
            'confidence': 85
        }
        
        attempt_file = brain_path / "attempt_001.yaml"
        with open(attempt_file, 'w') as f:
            yaml.dump(attempt, f)
        
        return brain_path
    
    def test_diagnostician_initialization(self, diagnostician):
        """Test diagnostician initializes correctly"""
        assert diagnostician is not None
        assert diagnostician.config is not None
        assert 'max_log_lines' in diagnostician.config
        assert diagnostician.cognitive_brain_path == Path('.codex/self_healing')
    
    def test_dependency_conflict_detection(self, diagnostician):
        """Test detection of dependency conflicts"""
        logs = """
        error: failed to select a version for `tokio`
        conflicting versions for tokio
        Dependency tree shows:
          tokio 1.28.0 (required by axum)
          tokio 1.35.0 (required by hyper)
        """
        
        report = diagnostician.diagnose("12345", logs)
        
        assert report.root_cause['type'] == 'dependency_conflict'
        assert 'tokio' in report.root_cause['description'].lower()
        assert report.confidence >= 80
        assert not report.root_cause['automated_fix']
        assert len(report.manual_steps) > 0
    
    def test_missing_dependency_detection(self, diagnostician):
        """Test detection of missing dependencies"""
        logs = """
        Traceback (most recent call last):
          File "test_api.py", line 5, in <module>
            import requests
        ModuleNotFoundError: No module named 'requests'
        """
        
        report = diagnostician.diagnose("12346", logs)
        
        assert report.root_cause['type'] == 'missing_dependency'
        assert 'requests' in report.root_cause['description']
        assert report.confidence >= 85
        assert report.root_cause['automated_fix'] is True
        assert any('requirements' in step.lower() for step in report.manual_steps)
    
    def test_runtime_error_detection(self, diagnostician):
        """Test detection of runtime errors with stack trace"""
        logs = """
        Running tests...
        Traceback (most recent call last):
          File "src/utils.py", line 45, in process_data
            result = data['key']
        KeyError: 'key'
        """
        
        report = diagnostician.diagnose("12347", logs)
        
        assert report.root_cause['type'] == 'runtime_error'
        assert 'python' in report.root_cause['description'].lower()
        assert report.confidence >= 60
        assert len(report.evidence) > 0
        assert any('stack trace' in evidence.lower() for evidence in report.evidence)
    
    def test_generic_error_detection(self, diagnostician):
        """Test detection of generic build errors"""
        logs = """
        Building project...
        error: could not compile `my_project`
        FAILED: build failed with exit code 1
        """
        
        report = diagnostician.diagnose("12348", logs)
        
        assert report.root_cause['type'] in ['generic_error', 'test_failure']
        assert report.confidence >= 0
        assert len(report.evidence) > 0
    
    def test_unknown_failure_handling(self, diagnostician):
        """Test handling of unknown failures"""
        logs = """
        Some random output
        No clear error patterns
        """
        
        report = diagnostician.diagnose("12349", logs)
        
        assert report.root_cause['type'] == 'unknown'
        assert report.confidence == 0
        assert 'Unable to determine' in report.root_cause['description']
        assert len(report.manual_steps) > 0
    
    def test_error_pattern_extraction(self, diagnostician):
        """Test error pattern extraction"""
        logs = """
        error: something went wrong
        Error: another issue
        FAILED test_api.py::test_endpoint
        ValueError: invalid value
        panicked at 'assertion failed', src/main.rs:42
        """
        
        patterns = diagnostician._extract_error_patterns(logs)
        
        assert len(patterns) >= 4
        assert any(p['type'] == 'generic_error' for p in patterns)
        assert any(p['type'] == 'test_failure' for p in patterns)
        assert any(p['type'] == 'python_exception' for p in patterns)
        assert any(p['type'] == 'rust_panic' for p in patterns)
    
    def test_stack_trace_extraction(self, diagnostician):
        """Test stack trace extraction"""
        logs = """
        Running tests...
        Traceback (most recent call last):
          File "test.py", line 10, in test_function
            result = process()
          File "utils.py", line 20, in process
            return data['key']
        KeyError: 'key'
        """
        
        traces = diagnostician._extract_stack_traces(logs)
        
        assert len(traces) == 1
        assert traces[0]['type'] == 'python'
        assert traces[0]['length'] > 0
        assert 'test.py' in traces[0]['trace'] or 'utils.py' in traces[0]['trace']
    
    def test_dependency_analysis(self, diagnostician):
        """Test dependency analysis"""
        logs = """
        error: conflicting versions for serde
        ModuleNotFoundError: No module named 'numpy'
        cargo: command not found
        requires tokio ^1.0 but found 0.9
        """
        
        dep_info = diagnostician._analyze_dependencies(logs)
        
        assert len(dep_info['version_conflicts']) > 0
        assert len(dep_info['missing_packages']) > 0
        assert 'serde' in str(dep_info['version_conflicts']) or 'tokio' in str(dep_info['version_conflicts'])
        assert 'numpy' in dep_info['missing_packages'] or 'cargo' in dep_info['missing_packages']
    
    def test_evidence_chain_building(self, diagnostician):
        """Test evidence chain construction"""
        error_patterns = [
            {'line': 45, 'message': 'error: build failed', 'type': 'generic_error'},
            {'line': 50, 'message': 'FAILED test', 'type': 'test_failure'}
        ]
        stack_traces = [
            {'type': 'python', 'start_line': 60, 'length': 5, 'trace': 'test trace'}
        ]
        root_cause = {'type': 'runtime_error'}
        
        evidence = diagnostician._build_evidence_chain(error_patterns, stack_traces, root_cause)
        
        assert len(evidence) > 0
        assert any('error' in e.lower() for e in evidence)
        assert any('stack trace' in e.lower() for e in evidence)
    
    def test_manual_steps_generation_dependency(self, diagnostician):
        """Test manual steps for dependency conflicts"""
        root_cause = {
            'type': 'dependency_conflict',
            'description': 'tokio version mismatch'
        }
        
        steps = diagnostician._generate_manual_steps(root_cause, [])
        
        assert len(steps) > 0
        assert any('cargo' in step.lower() or 'lock' in step.lower() for step in steps)
        assert any('update' in step.lower() for step in steps)
    
    def test_manual_steps_generation_runtime(self, diagnostician):
        """Test manual steps for runtime errors"""
        root_cause = {
            'type': 'runtime_error',
            'description': 'KeyError in process()'
        }
        
        steps = diagnostician._generate_manual_steps(root_cause, [])
        
        assert len(steps) > 0
        assert any('stack trace' in step.lower() for step in steps)
        assert any('debug' in step.lower() or 'review' in step.lower() for step in steps)
    
    def test_time_estimation(self, diagnostician):
        """Test fix time estimation"""
        root_causes = [
            {'type': 'dependency_conflict'},
            {'type': 'missing_dependency'},
            {'type': 'runtime_error'},
            {'type': 'unknown'}
        ]
        
        for root_cause in root_causes:
            time_estimate = diagnostician._estimate_fix_time(root_cause, [])
            assert time_estimate is not None
            assert 'minute' in time_estimate.lower() or 'hour' in time_estimate.lower()
    
    def test_time_estimation_with_history(self, diagnostician):
        """Test time estimation considers historical data"""
        root_cause = {'type': 'dependency_conflict'}
        similar_failures = [
            {'outcome': 'success', 'fix_type': 'dependency_conflict'},
            {'outcome': 'success', 'fix_type': 'dependency_conflict'}
        ]
        
        time_estimate = diagnostician._estimate_fix_time(root_cause, similar_failures)
        
        assert 'similar' in time_estimate.lower() or '10-15' in time_estimate
    
    def test_cognitive_brain_query(self, diagnostician, mock_cognitive_brain, monkeypatch):
        """Test querying cognitive brain for similar failures"""
        # Override cognitive brain path
        monkeypatch.setattr(diagnostician, 'cognitive_brain_path', mock_cognitive_brain)
        
        root_cause = {'type': 'dependency_conflict'}
        similar = diagnostician._query_similar_failures(root_cause)
        
        assert len(similar) > 0
        assert similar[0]['outcome'] == 'success'
        assert similar[0]['fix_type'] == 'dependency_conflict'
    
    def test_report_markdown_generation(self, diagnostician):
        """Test markdown report generation"""
        report = DiagnosticReport(
            timestamp='2026-01-12T13:00:00Z',
            workflow_run_id='12345',
            root_cause={
                'type': 'dependency_conflict',
                'description': 'tokio version mismatch',
                'category': 'dependencies',
                'automated_fix': False
            },
            evidence=['Line 45: conflicting versions', 'Dependency tree shows conflict'],
            manual_steps=['Update Cargo.toml', 'Run cargo update'],
            similar_past_failures=[
                {'date': '2026-01-10T12:00:00Z', 'fix_type': 'dependency_conflict', 'outcome': 'success'}
            ],
            estimated_fix_time='15 minutes',
            confidence=85
        )
        
        markdown = diagnostician.generate_report_markdown(report)
        
        assert '# CI Failure Diagnostic Report' in markdown
        assert '12345' in markdown
        assert 'dependency_conflict' in markdown
        assert '85%' in markdown
        assert 'tokio' in markdown
        assert 'Update Cargo.toml' in markdown
        assert '15 minutes' in markdown
    
    def test_multiple_error_types(self, diagnostician):
        """Test handling logs with multiple error types"""
        logs = """
        error: build failed
        ModuleNotFoundError: No module named 'requests'
        Traceback (most recent call last):
          File "test.py", line 1
        KeyError: 'key'
        conflicting versions for tokio
        """
        
        report = diagnostician.diagnose("12350", logs)
        
        # Should prioritize dependency issues
        assert report.root_cause['type'] in ['dependency_conflict', 'missing_dependency']
        assert report.confidence > 0
        assert len(report.evidence) > 0
    
    def test_configuration_loading(self, tmp_path):
        """Test configuration file loading"""
        config_file = tmp_path / "config.yaml"
        config_data = {
            'max_log_lines': 5000,
            'min_confidence': 70,
            'cognitive_brain_enabled': False
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        diagnostician = CIFailureDiagnostician(config_path=config_file)
        
        assert diagnostician.config['max_log_lines'] == 5000
        assert diagnostician.config['min_confidence'] == 70
        assert diagnostician.config['cognitive_brain_enabled'] is False
    
    def test_report_completeness(self, diagnostician):
        """Test that diagnostic reports are complete"""
        logs = """
        error: something failed
        FAILED test
        """
        
        report = diagnostician.diagnose("12351", logs)
        
        # Verify all required fields are present
        assert report.timestamp is not None
        assert report.workflow_run_id == "12351"
        assert report.root_cause is not None
        assert 'type' in report.root_cause
        assert 'description' in report.root_cause
        assert report.evidence is not None
        assert report.manual_steps is not None
        assert report.estimated_fix_time is not None
        assert isinstance(report.confidence, int)
        assert 0 <= report.confidence <= 100
    
    def test_long_log_handling(self, diagnostician):
        """Test handling of very long logs"""
        # Create a log with many lines
        lines = [f"line {i}: some output" for i in range(1000)]
        lines.insert(500, "error: critical failure")
        logs = '\n'.join(lines)
        
        report = diagnostician.diagnose("12352", logs)
        
        # Should still find the error
        assert report.root_cause['type'] != 'unknown'
        assert len(report.evidence) > 0
    
    def test_empty_log_handling(self, diagnostician):
        """Test handling of empty logs"""
        logs = ""
        
        report = diagnostician.diagnose("12353", logs)
        
        assert report.root_cause['type'] == 'unknown'
        assert report.confidence == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
