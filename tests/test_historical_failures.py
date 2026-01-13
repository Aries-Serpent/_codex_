"""
Historical CI Failure Testing Framework

Tests the CI Diagnostic Agent against historical failure patterns
to validate accuracy and effectiveness.

Target: 85%+ accuracy on known failure types
"""

import pytest
import json
import sys
import os
from pathlib import Path

# Add agent to path
agent_path = Path(__file__).parent.parent / ".github" / "agents" / "ci-diagnostic-agent" / "src"
sys.path.insert(0, str(agent_path))

try:
    from agent import CIDiagnosticAgent, DiagnosticReport
except ImportError:
    pytest.skip("CI Diagnostic Agent not available", allow_module_level=True)


class TestHistoricalFailures:
    """Test suite for historical CI failure patterns"""
    
    @pytest.fixture
    def agent(self):
        """Initialize CI Diagnostic Agent"""
        return CIDiagnosticAgent()
    
    @pytest.fixture
    def import_error_log(self):
        """Sample log with import error"""
        return """
Traceback (most recent call last):
  File "test_integration.py", line 5, in <module>
    from ingestion import Ingestor, ingest
ImportError: cannot import name 'Ingestor' from 'ingestion'
Make sure the module is installed and the import path is correct.
"""
    
    @pytest.fixture
    def rust_compile_error_log(self):
        """Sample log with Rust compilation error"""
        return """
error[E0308]: mismatched types
  --> benches/swarm_benchmarks.rs:78:13
   |
78 |             b.iter(|| Compression::decompress(black_box(&compressed)));
   |                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ expected `()`, found `Result<Vec<u8>, PyErr>`
   |
   = note: expected unit type `()`
                   found enum `Result<Vec<u8>, PyErr>`

error: aborting due to previous error
"""
    
    @pytest.fixture
    def disk_full_log(self):
        """Sample log with disk space error"""
        return """
pip install -r requirements.txt
Collecting package-name
Downloading package-name.tar.gz
ERROR: Could not install packages due to an OSError: [Errno 28] No space left on device
Available: 99 MB
"""
    
    @pytest.fixture
    def timeout_log(self):
        """Sample log with timeout"""
        return """
pytest tests/rag/ -v
test_rag_query_basic PASSED
test_rag_embedding_generation 
Error: Timeout after 300 seconds
"""
    
    @pytest.fixture
    def cache_miss_log(self):
        """Sample log with cache miss"""
        return """
Restore cache
Cache not found for input keys: pytest-cache-v1-...
No cache available for restoration
"""
    
    @pytest.fixture
    def dependency_error_log(self):
        """Sample log with dependency error"""
        return """
pip install pyo3
ERROR: Could not find a version that satisfies the requirement pyo3>=0.24.1
ERROR: No matching distribution found for pyo3>=0.24.1
"""
    
    @pytest.fixture
    def artifact_missing_log(self):
        """Sample log with missing artifact"""
        return """
Download artifact 'coverage-reports'
Error: Unable to find any artifacts for the associated workflow
Artifact 'coverage-reports' not found in workflow run
"""
    
    # Test Cases
    
    def test_import_error_detection(self, agent, import_error_log):
        """Test detection of import errors"""
        report = agent.analyze_logs("test-import", import_error_log)
        
        assert report.root_cause == "import_error"
        assert report.confidence >= 0.85
        assert report.severity in ["high", "critical"]
        assert report.auto_fixable is True
    
    def test_rust_compile_error_detection(self, agent, rust_compile_error_log):
        """Test detection of Rust compilation errors"""
        report = agent.analyze_logs("test-rust", rust_compile_error_log)
        
        assert report.root_cause == "rust_compile_error"
        assert report.confidence >= 0.90
        assert report.severity == "critical"
        assert "error[E" in str(report.findings)
    
    def test_disk_full_detection(self, agent, disk_full_log):
        """Test detection of disk space issues"""
        report = agent.analyze_logs("test-disk", disk_full_log)
        
        assert report.root_cause == "disk_full"
        assert report.confidence >= 0.95
        assert report.severity == "critical"
        assert report.auto_fixable is True
        
        # Check remediation suggests disk cleanup
        assert any("disk" in str(r).lower() for r in report.remediation)
    
    def test_timeout_detection(self, agent, timeout_log):
        """Test detection of timeout issues"""
        report = agent.analyze_logs("test-timeout", timeout_log)
        
        assert report.root_cause == "timeout"
        assert report.confidence >= 0.80
        assert report.severity == "medium"
        assert report.auto_fixable is True
    
    def test_cache_miss_detection(self, agent, cache_miss_log):
        """Test detection of cache misses"""
        report = agent.analyze_logs("test-cache", cache_miss_log)
        
        assert report.root_cause == "cache_miss"
        assert report.confidence >= 0.70
        assert report.severity == "low"
        assert report.auto_fixable is True
    
    def test_dependency_error_detection(self, agent, dependency_error_log):
        """Test detection of dependency errors"""
        report = agent.analyze_logs("test-dep", dependency_error_log)
        
        assert report.root_cause == "dependency_error"
        assert report.confidence >= 0.85
        assert report.severity == "high"
        assert report.auto_fixable is True
    
    def test_artifact_missing_detection(self, agent, artifact_missing_log):
        """Test detection of missing artifacts"""
        report = agent.analyze_logs("test-artifact", artifact_missing_log)
        
        assert report.root_cause == "artifact_missing"
        assert report.confidence >= 0.80
        assert report.severity == "medium"
    
    def test_multi_failure_prioritization(self, agent):
        """Test handling of multiple failure types"""
        combined_log = """
ImportError: cannot import name 'Ingestor'
error[E0308]: mismatched types
No space left on device
"""
        
        report = agent.analyze_logs("test-multi", combined_log)
        
        # Should prioritize critical issues (disk full or compile error)
        assert report.severity in ["critical", "high"]
        assert len(report.findings) >= 2
    
    def test_confidence_scoring(self, agent, disk_full_log):
        """Test confidence score calculation"""
        report = agent.analyze_logs("test-confidence", disk_full_log)
        
        # High confidence for clear patterns
        assert 0.0 <= report.confidence <= 1.0
        assert report.confidence >= 0.85  # Disk full should be very clear
    
    def test_json_output_schema(self, agent, import_error_log):
        """Test JSON report schema compliance"""
        report = agent.analyze_logs("test-json", import_error_log)
        json_output = report.to_json()
        
        data = json.loads(json_output)
        
        # Verify required fields
        assert "run_id" in data
        assert "root_cause" in data
        assert "confidence" in data
        assert "severity" in data
        assert "auto_fixable" in data
        assert "findings" in data
        assert "remediation" in data


class TestIntegration:
    """Integration tests for CI Diagnostic Agent"""
    
    def test_agent_initialization(self):
        """Test agent initializes correctly"""
        agent = CIDiagnosticAgent()
        assert agent is not None
        assert len(agent.patterns) > 0
    
    def test_end_to_end_analysis(self, tmp_path):
        """Test complete analysis workflow"""
        agent = CIDiagnosticAgent()
        
        # Create test log file
        log_file = tmp_path / "test.log"
        log_file.write_text("ImportError: cannot import name 'test'")
        
        # Run analysis
        report = agent.analyze_logs("test-e2e", log_file.read_text())
        
        # Verify report
        assert report.root_cause is not None
        assert report.confidence > 0
        
        # Test report generation
        md_report = report.to_markdown()
        assert "## 🔍 CI Diagnostic Report" in md_report
        
        json_report = report.to_json()
        assert json.loads(json_report) is not None


@pytest.mark.parametrize("failure_type,expected_pattern", [
    ("import_error", "ImportError"),
    ("rust_compile_error", "error[E"),
    ("disk_full", "No space left"),
    ("timeout", "Timeout after"),
    ("cache_miss", "Cache not found"),
    ("dependency_error", "Could not find.*requirement"),
    ("artifact_missing", "Unable to find.*artifact"),
])
def test_pattern_coverage(failure_type, expected_pattern):
    """Test that all expected patterns are defined"""
    agent = CIDiagnosticAgent()
    
    # Check pattern exists
    patterns = {p['id']: p for p in agent.patterns}
    assert failure_type in patterns
    
    # Verify pattern can match expected strings
    import re
    pattern = patterns[failure_type]['pattern']
    assert re.search(pattern, expected_pattern, re.IGNORECASE) is not None


def test_accuracy_benchmark():
    """
    Benchmark test: Validate 85%+ accuracy on historical data
    
    This test should be run against a dataset of historical CI failures
    to validate the agent's accuracy meets the target threshold.
    """
    agent = CIDiagnosticAgent()
    
    # Sample test data (in production, load from historical dataset)
    test_cases = [
        ("ImportError: test", "import_error"),
        ("error[E0308]: type mismatch", "rust_compile_error"),
        ("No space left on device", "disk_full"),
        ("Timeout after 300 seconds", "timeout"),
        ("Cache not found", "cache_miss"),
        ("Could not find requirement", "dependency_error"),
        ("Unable to find artifacts", "artifact_missing"),
    ]
    
    correct = 0
    total = len(test_cases)
    
    for log, expected_cause in test_cases:
        report = agent.analyze_logs("benchmark", log)
        if report.root_cause == expected_cause:
            correct += 1
    
    accuracy = correct / total
    
    # Assert 85%+ accuracy
    assert accuracy >= 0.85, f"Accuracy {accuracy:.1%} below 85% threshold"
    print(f"✅ Accuracy: {accuracy:.1%} ({correct}/{total})")
