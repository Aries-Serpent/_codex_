"""
Unit tests for CI Failure Analyzer
"""

import pytest
from pathlib import Path
import tempfile
import json
from analyzer import CIFailureAnalyzer, FailureAnalysis


class TestCIFailureAnalyzer:
    """Test suite for CI failure analyzer"""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance"""
        return CIFailureAnalyzer()
    
    @pytest.fixture
    def temp_log_file(self):
        """Create temporary log file"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            yield Path(f.name)
        Path(f.name).unlink(missing_ok=True)
    
    def test_analyzer_initialization(self, analyzer):
        """Test analyzer initializes with patterns"""
        assert analyzer is not None
        assert len(analyzer.patterns) > 0
        assert 'rust_formatting' in analyzer.patterns
        assert 'python_linting' in analyzer.patterns
    
    def test_rust_formatting_detection(self, analyzer, temp_log_file):
        """Test detection of Rust formatting issues"""
        log_content = """
        error: running `rustfmt --check --edition 2021 src/main.rs`
        Diff in /path/to/src/main.rs at line 10:
        -fn main(){
        +fn main() {
        """
        temp_log_file.write_text(log_content)
        
        analysis = analyzer.analyze(temp_log_file)
        
        assert analysis.fix_available is True
        assert analysis.fix_type == 'rust_format'
        assert analysis.confidence == 95
        assert analysis.failure_type == 'rust_formatting'
        assert 'main.rs' in str(analysis.fix_params.get('files', []))
    
    def test_python_linting_detection(self, analyzer, temp_log_file):
        """Test detection of Python linting issues"""
        log_content = """
        ruff check src/
        src/utils.py:15:1: F401 [*] `sys` imported but unused
        src/utils.py:20:5: E501 Line too long (120 > 88 characters)
        Found 2 errors.
        """
        temp_log_file.write_text(log_content)
        
        analysis = analyzer.analyze(temp_log_file)
        
        assert analysis.fix_available is True
        assert analysis.fix_type == 'python_lint'
        assert analysis.confidence == 85
        assert analysis.failure_type == 'python_linting'
    
    def test_timeout_detection(self, analyzer, temp_log_file):
        """Test detection of timeout issues"""
        log_content = """
        ============================= test session starts ==============================
        test_long_running.py::test_heavy_computation FAILED
        
        E       TimeoutError: Test timed out after 60 seconds
        """
        temp_log_file.write_text(log_content)
        
        analysis = analyzer.analyze(temp_log_file)
        
        assert analysis.fix_available is True
        assert analysis.fix_type == 'increase_timeout'
        assert analysis.confidence == 70
        assert analysis.failure_type == 'test_timeout'
        assert analysis.fix_params.get('current_timeout') == 60
        assert analysis.fix_params.get('suggested_timeout') == 120
    
    def test_import_error_detection(self, analyzer, temp_log_file):
        """Test detection of missing dependencies"""
        log_content = """
        Traceback (most recent call last):
          File "test_api.py", line 5, in <module>
            import requests
        ModuleNotFoundError: No module named 'requests'
        """
        temp_log_file.write_text(log_content)
        
        analysis = analyzer.analyze(temp_log_file)
        
        assert analysis.fix_available is True
        assert analysis.fix_type == 'add_dependency'
        assert analysis.confidence == 80
        assert analysis.failure_type == 'import_error'
        assert analysis.fix_params.get('missing_module') == 'requests'
    
    def test_cache_corruption_detection(self, analyzer, temp_log_file):
        """Test detection of cache issues"""
        log_content = """
        Restoring cache from key: rust-cargo-target-x86_64-unknown-linux-gnu-
        Error: failed to restore cache: cache is corrupt or invalid
        """
        temp_log_file.write_text(log_content)
        
        analysis = analyzer.analyze(temp_log_file)
        
        assert analysis.fix_available is True
        assert analysis.fix_type == 'clear_cache'
        assert analysis.confidence == 90
        assert analysis.failure_type == 'cache_corruption'
    
    def test_unknown_failure(self, analyzer, temp_log_file):
        """Test handling of unknown failures"""
        log_content = """
        Some random error that doesn't match any pattern
        This is a completely unknown failure type
        """
        temp_log_file.write_text(log_content)
        
        analysis = analyzer.analyze(temp_log_file)
        
        assert analysis.fix_available is False
        assert analysis.fix_type == 'unknown'
        assert analysis.confidence == 0
        assert analysis.failure_type == 'unknown'
    
    def test_cargo_lock_conflict(self, analyzer, temp_log_file):
        """Test detection of Cargo.lock conflicts"""
        log_content = """
        error: failed to update Cargo.lock
        Caused by:
          Cargo.lock conflict detected for package `tokio`
        """
        temp_log_file.write_text(log_content)
        
        analysis = analyzer.analyze(temp_log_file)
        
        assert analysis.fix_available is True
        assert analysis.fix_type == 'cargo_update'
        assert analysis.confidence == 85
        assert 'tokio' in analysis.fix_params.get('package', '')
    
    def test_network_timeout(self, analyzer, temp_log_file):
        """Test detection of network timeouts"""
        log_content = """
        Downloading crates.io index
        error: failed to download from `https://crates.io/api/v1/crates`
        Caused by:
          connection timed out
        """
        temp_log_file.write_text(log_content)
        
        analysis = analyzer.analyze(temp_log_file)
        
        assert analysis.fix_available is True
        assert analysis.fix_type == 'retry'
        assert analysis.confidence == 75
    
    def test_disk_space(self, analyzer, temp_log_file):
        """Test detection of disk space issues"""
        log_content = """
        ENOSPC: no space left on device, write
        error: failed to write to disk
        """
        temp_log_file.write_text(log_content)
        
        analysis = analyzer.analyze(temp_log_file)
        
        assert analysis.fix_available is True
        assert analysis.fix_type == 'cleanup_disk'
        assert analysis.confidence == 95
    
    def test_analysis_timestamp(self, analyzer, temp_log_file):
        """Test that analysis includes timestamp"""
        temp_log_file.write_text("Diff in src/main.rs")
        
        analysis = analyzer.analyze(temp_log_file)
        
        assert analysis.timestamp is not None
        assert 'T' in analysis.timestamp  # ISO format check
    
    def test_parameter_extraction_timeout(self, analyzer):
        """Test parameter extraction for timeout"""
        log = "Test timed out after 120 seconds"
        pattern = analyzer.patterns['test_timeout']
        
        params = analyzer._extract_params(log, pattern)
        
        assert params['current_timeout'] == 120
        assert params['suggested_timeout'] == 240
    
    def test_parameter_extraction_default_timeout(self, analyzer):
        """Test default timeout parameters when not found in log"""
        log = "TIMEOUT occurred"
        pattern = analyzer.patterns['test_timeout']
        
        params = analyzer._extract_params(log, pattern)
        
        assert params['current_timeout'] == 60
        assert params['suggested_timeout'] == 120
    
    def test_json_output_format(self, analyzer, temp_log_file):
        """Test that analysis can be serialized to JSON"""
        temp_log_file.write_text("Diff in src/main.rs")
        
        analysis = analyzer.analyze(temp_log_file)
        from dataclasses import asdict
        
        # Should not raise exception
        json_str = json.dumps(asdict(analysis))
        assert json_str is not None
        
        # Should be deserializable
        data = json.loads(json_str)
        assert data['fix_available'] is True
        assert data['fix_type'] == 'rust_format'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
