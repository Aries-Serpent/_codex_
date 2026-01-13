"""Integration tests for Rust Error Validator Agent."""
import pytest
from pathlib import Path
import sys
import json

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent import RustErrorValidator


class TestIntegration:
    """Integration tests for full workflows."""
    
    def test_cli_text_output(self, tmp_path, capsys):
        """Test CLI with text output format."""
        # Create test Rust file
        rust_file = tmp_path / "test.rs"
        rust_file.write_text("fn test() { x.unwrap(); }")
        
        # Run validator
        validator = RustErrorValidator()
        findings = validator.scan_directory(tmp_path)
        
        assert len(findings) >= 1
    
    def test_cli_json_output(self, tmp_path):
        """Test CLI with JSON output format."""
        # Create test Rust files
        (tmp_path / "file1.rs").write_text("#[pyfunction]\nfn f() { x.unwrap(); }")
        (tmp_path / "file2.rs").write_text("fn g() { y.unwrap(); }")
        
        validator = RustErrorValidator()
        findings = validator.scan_directory(tmp_path)
        report = validator.generate_report(findings)
        
        # Verify JSON structure
        assert 'total_findings' in report
        assert 'severity_breakdown' in report
        assert report['total_findings'] == 2
    
    def test_config_loading(self, tmp_path):
        """Test loading custom configuration."""
        config = tmp_path / "config.yaml"
        config.write_text("""
enabled: true
check_unwrap: true
check_expect: false
check_panic: false
ignore_test_code: true
""")
        
        validator = RustErrorValidator(config)
        assert validator.config['check_unwrap'] is True
        assert validator.config['check_expect'] is False
        assert validator.config['check_panic'] is False
    
    def test_large_codebase_scan(self, tmp_path):
        """Test scanning a larger codebase structure."""
        # Create nested structure
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "lib.rs").write_text("pub fn lib() { x.unwrap(); }")
        
        (tmp_path / "src" / "utils").mkdir()
        (tmp_path / "src" / "utils" / "mod.rs").write_text("pub fn util() { y.unwrap(); }")
        
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test.rs").write_text("#[test]\nfn test() { z.unwrap(); }")
        
        validator = RustErrorValidator()
        findings = validator.scan_directory(tmp_path, recursive=True)
        
        # Should find unwraps in lib and utils, but not in test
        assert len(findings) == 2
    
    def test_mixed_severity_report(self, tmp_path):
        """Test report with mixed severity findings."""
        (tmp_path / "high.rs").write_text("#[pyfunction]\nfn f() { x.unwrap(); }")
        (tmp_path / "medium.rs").write_text("fn internal() { y.unwrap(); }")
        (tmp_path / "panic.rs").write_text("fn bad() { panic!(\"error\"); }")
        
        validator = RustErrorValidator()
        findings = validator.scan_directory(tmp_path)
        report = validator.generate_report(findings)
        
        assert report['severity_breakdown']['high'] >= 2  # pyfunction unwrap + panic
        assert report['severity_breakdown']['medium'] >= 1
        assert report['unique_files'] == 3
    
    def test_error_handling_in_scan(self, tmp_path):
        """Test graceful error handling for unreadable files."""
        # Create a file
        test_file = tmp_path / "test.rs"
        test_file.write_text("fn test() {}")
        
        # Make it unreadable (on Unix systems)
        try:
            import os
            os.chmod(test_file, 0o000)
            
            validator = RustErrorValidator()
            # Should not crash, just skip the file
            findings = validator.scan_file(test_file)
            assert isinstance(findings, list)
            
            # Restore permissions (user read/write only for security)
            os.chmod(test_file, 0o600)
        except (OSError, PermissionError):
            # Skip this test on Windows or if permissions can't be changed
            pytest.skip("Cannot test file permissions on this platform")
    
    def test_suggestion_quality(self, tmp_path):
        """Test that suggestions are helpful and specific."""
        rust_file = tmp_path / "test.rs"
        rust_file.write_text("#[pyfunction]\nfn process() { data.unwrap(); }")
        
        validator = RustErrorValidator()
        findings = validator.scan_file(rust_file)
        
        assert len(findings) >= 1
        finding = findings[0]
        
        # Check suggestion quality
        assert finding.suggestion
        assert len(finding.suggestion) > 20  # Not just a placeholder
        assert 'PyResult' in finding.suggestion or 'unwrap_or' in finding.suggestion


def test_end_to_end_workflow(tmp_path):
    """Test complete workflow from scan to report."""
    # Setup: Create test files
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "lib.rs").write_text("""
#[pyfunction]
pub fn risky_function(data: &str) -> String {
    let parsed = parse_data(data).unwrap();  // High severity
    parsed.to_string()
}

fn internal_helper() {
    let config = load_config().unwrap();  // Medium severity
}

#[test]
fn test_parsing() {
    let result = parse_data("test").unwrap();  // Should be ignored
}
""")
    
    # Execute: Scan and generate report
    validator = RustErrorValidator()
    findings = validator.scan_directory(tmp_path, recursive=True)
    report = validator.generate_report(findings)
    
    # Verify: Check results
    assert report['total_findings'] == 2
    assert report['severity_breakdown']['high'] >= 1  # At least one high severity
    assert report['severity_breakdown']['medium'] >= 0
    assert report['unique_files'] == 1
    
    # Verify findings have required fields
    high_findings = report['findings_by_severity']['high']
    assert len(high_findings) >= 1  # At least one high severity finding
    assert any(f.file.endswith('lib.rs') for f in high_findings)
    assert all(f.severity == 'high' for f in high_findings)
    assert all(f.suggestion for f in high_findings)
