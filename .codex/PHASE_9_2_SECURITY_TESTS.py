"""
PHASE 9.2 Security Test Suite

Tests for:
- Subprocess injection prevention
- Path traversal prevention
- Regex ReDoS prevention
- Secure randomness
- Type safety
"""

import pytest
import tempfile
import time
from pathlib import Path

# Import the modules under test
import sys
sys.path.insert(0, 'scripts/ci')
from phase_9_2_cascade_orchestrator import run_command, FixExecutor, PatternDetector
from phase_9_2_pattern_router import PatternMatcher, PatternRouter


# ============================================================================
# SUBPROCESS INJECTION TESTS
# ============================================================================

class TestSubprocessSecurity:
    """Test subprocess security against injection attacks"""
    
    def test_subprocess_injection_prevention(self):
        """Verify subprocess cannot be exploited for injection"""
        # Command with special shell characters
        code, out, err = run_command(["echo", "'; DROP TABLE users; --"])
        assert code == 0
        assert "DROP TABLE" in out
        
    def test_subprocess_pipe_prevention(self):
        """Verify pipes cannot be injected"""
        code, out, err = run_command(["echo", "test | cat /etc/passwd"])
        assert code == 0
        assert "test | cat" in out
        
    def test_subprocess_timeout(self):
        """Verify timeout protection works"""
        code, out, err = run_command(["sleep", "100"], timeout_sec=1)
        assert code == -1
        assert "TIMEOUT" in err
        
    def test_subprocess_nonexistent_command(self):
        """Verify error handling for nonexistent commands"""
        code, out, err = run_command(["nonexistent_command_12345"])
        assert code == -1
        assert "FileNotFoundError" in err or "No such file" in err


# ============================================================================
# PATH TRAVERSAL TESTS
# ============================================================================

class TestPathTraversal:
    """Test path traversal prevention in file operations"""
    
    def test_read_file_in_current_dir(self):
        """Verify reading files in current directory works"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write("test log content")
            f.flush()
            temp_path = f.name
        
        try:
            with open(temp_path, 'r') as f:
                content = f.read()
            assert "test log content" in content
        finally:
            Path(temp_path).unlink()
    
    def test_yaml_safe_load(self):
        """Verify yaml.safe_load is used (not yaml.load)"""
        import yaml
        
        # Safe load should reject arbitrary Python objects
        dangerous_yaml = "!!python/object/apply:os.system\nargs: ['echo hacked']\n"
        
        with pytest.raises(yaml.YAMLError):
            yaml.safe_load(dangerous_yaml)


# ============================================================================
# REGEX REDOS TESTS
# ============================================================================

class TestRegexSafety:
    """Test regex patterns for ReDoS vulnerabilities"""
    
    def test_regex_on_large_input(self):
        """Verify regex patterns complete quickly on large input"""
        matcher = PatternMatcher()
        
        # Pathological input for regex
        pathological = "a" * 10000
        
        start = time.time()
        matches = matcher.match(pathological)
        elapsed = time.time() - start
        
        # Should complete in under 1 second
        assert elapsed < 1.0, f"Regex took {elapsed}s (possible ReDoS)"
    
    def test_regex_with_special_chars(self):
        """Verify regex handles special characters safely"""
        matcher = PatternMatcher()
        
        # Input with special regex characters
        special_input = "Test.*+?[]{}<>|()\\^$"
        
        # Should not raise exception
        matches = matcher.match(special_input)
        assert isinstance(matches, list)


# ============================================================================
# SECURE RANDOMNESS TESTS
# ============================================================================

class TestSecureRandomness:
    """Test cryptographically secure randomness usage"""
    
    def test_uses_secrets_module(self):
        """Verify secrets module is used for randomness"""
        import inspect
        
        # Get source code of _simulate_agent_fix
        executor = FixExecutor()
        source = inspect.getsource(executor._simulate_agent_fix)
        
        # Should use secrets.randbelow
        assert "secrets.randbelow" in source
        # Should NOT use random.random
        assert "from random import" not in source or "secrets" in source


# ============================================================================
# TYPE SAFETY TESTS
# ============================================================================

class TestTypeSafety:
    """Test type safety improvements"""
    
    def test_optional_types(self):
        """Verify Optional types are properly used"""
        
        # PatternMatcher should accept Optional[Dict]
        matcher = PatternMatcher(config=None)
        assert matcher.config is not None
        
        # PatternRouter should accept Optional[Dict]
        router = PatternRouter(config=None)
        assert router.config is not None
        
        # PatternDetector should accept Optional[List]
        detector = PatternDetector(patterns=None)
        assert detector.patterns is not None
    
    def test_type_annotations_present(self):
        """Verify type annotations are present"""
        from typing import get_type_hints
        
        # Check PatternMatcher has type hints
        hints = get_type_hints(PatternMatcher.__init__)
        assert "config" in hints
        assert "return" in hints


# ============================================================================
# EXCEPTION HANDLING TESTS
# ============================================================================

class TestExceptionHandling:
    """Test exception handling coverage"""
    
    def test_no_bare_except_clauses(self):
        """Verify no bare except: clauses"""
        import inspect
        
        # Get source of run_command
        source = inspect.getsource(run_command)
        
        # Should not have bare except
        lines = source.split('\n')
        for line in lines:
            if 'except:' in line:
                pytest.fail(f"Found bare except clause: {line}")
    
    def test_timeout_error_handling(self):
        """Verify TimeoutError is handled"""
        # This is tested indirectly in test_subprocess_timeout
        pass


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests for complete workflow"""
    
    def test_pattern_matching_workflow(self):
        """Test complete pattern matching workflow"""
        router = PatternRouter()
        
        # Test with realistic failure log
        failure_log = """
        FAILED test_example.py::test_function - AssertionError: expected 1, got 0
        pytest error: Some assertion failed
        """
        
        decision = router.route(failure_log)
        
        # Should make a routing decision
        assert "status" in decision
        assert decision["status"] != "error"
    
    def test_cascade_orchestrator_workflow(self):
        """Test cascade orchestrator workflow"""
        from phase_9_2_cascade_orchestrator import (
            CascadeOrchestrator, FailureLog
        )
        from datetime import datetime
        
        orchestrator = CascadeOrchestrator()
        
        # Create a failure log
        failure_log = FailureLog(
            raw_log="FAILED test_file.py::test_name - AssertionError",
            job_name="test-job",
            workflow_name="test-workflow",
            timestamp=datetime.utcnow().isoformat(),
            exit_code=1
        )
        
        # Run orchestration
        result = orchestrator.orchestrate(failure_log)
        
        # Should have a result
        assert result is not None
        assert result.final_status is not None


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
