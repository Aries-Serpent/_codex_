"""Comprehensive unit tests for Rust Error Validator Agent."""
import pytest
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent import RustErrorValidator, Finding


class TestRustErrorValidator:
    """Test suite for RustErrorValidator class."""
    
    def test_validator_initialization(self):
        """Test validator initializes with default config."""
        validator = RustErrorValidator()
        assert validator.config is not None
        assert validator.config['enabled'] is True
        assert validator.patterns is not None
    
    def test_validator_with_custom_config(self, tmp_path):
        """Test validator loads custom configuration."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("enabled: false\ncheck_unwrap: false")
        
        validator = RustErrorValidator(config_file)
        assert validator.config['enabled'] is False
        assert validator.config['check_unwrap'] is False
    
    def test_scan_file_detects_unwrap(self, tmp_path):
        """Test scanner detects .unwrap() calls."""
        test_file = tmp_path / "test.rs"
        test_file.write_text("""
#[pyfunction]
fn process_data() {
    let result = some_operation().unwrap();
}
""")
        
        validator = RustErrorValidator()
        findings = validator.scan_file(test_file)
        
        assert len(findings) >= 1
        assert any('unwrap' in f.issue.lower() for f in findings)
        assert any(f.severity == 'high' for f in findings)  # PyO3 context
    
    def test_scan_file_ignores_test_unwrap(self, tmp_path):
        """Test scanner ignores .unwrap() in test code."""
        test_file = tmp_path / "test_code.rs"
        test_file.write_text("""
#[test]
fn test_something() {
    let x = operation().unwrap();
}
""")
        
        validator = RustErrorValidator()
        findings = validator.scan_file(test_file)
        
        assert len(findings) == 0
    
    def test_scan_file_detects_expect(self, tmp_path):
        """Test scanner detects .expect() calls."""
        test_file = tmp_path / "test.rs"
        test_file.write_text("""
fn process() {
    let val = get_value().expect("Failed to get value");
}
""")
        
        validator = RustErrorValidator()
        findings = validator.scan_file(test_file)
        
        assert len(findings) >= 1
        assert any('expect' in f.issue.lower() for f in findings)
    
    def test_scan_file_detects_panic(self, tmp_path):
        """Test scanner detects panic!() macros."""
        test_file = tmp_path / "test.rs"
        test_file.write_text("""
fn handle_error() {
    panic!("Critical error occurred");
}
""")
        
        validator = RustErrorValidator()
        findings = validator.scan_file(test_file)
        
        assert len(findings) >= 1
        assert any('panic' in f.issue.lower() for f in findings)
        assert any(f.severity == 'high' for f in findings)
    
    def test_scan_directory_recursive(self, tmp_path):
        """Test scanner scans directories recursively."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        
        file1 = tmp_path / "file1.rs"
        file1.write_text("fn test() { x.unwrap(); }")
        
        file2 = subdir / "file2.rs"
        file2.write_text("fn test2() { y.unwrap(); }")
        
        validator = RustErrorValidator()
        findings = validator.scan_directory(tmp_path, recursive=True)
        
        assert len(findings) >= 2
    
    def test_scan_directory_non_recursive(self, tmp_path):
        """Test scanner scans only top-level directory."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        
        file1 = tmp_path / "file1.rs"
        file1.write_text("fn test() { x.unwrap(); }")
        
        file2 = subdir / "file2.rs"
        file2.write_text("fn test2() { y.unwrap(); }")
        
        validator = RustErrorValidator()
        findings = validator.scan_directory(tmp_path, recursive=False)
        
        assert len(findings) == 1
    
    def test_generate_report(self, tmp_path):
        """Test report generation from findings."""
        test_file1 = tmp_path / "file1.rs"
        test_file1.write_text("#[pyfunction]\nfn test() { x.unwrap(); }")
        
        test_file2 = tmp_path / "file2.rs"
        test_file2.write_text("fn test() { y.unwrap(); }")
        
        validator = RustErrorValidator()
        findings = validator.scan_directory(tmp_path)
        report = validator.generate_report(findings)
        
        assert 'total_findings' in report
        assert 'severity_breakdown' in report
        assert 'unique_files' in report
        assert report['total_findings'] >= 2
        assert report['unique_files'] == 2
    
    def test_severity_levels(self, tmp_path):
        """Test severity assignment based on context."""
        # High severity: PyO3 unwrap
        pyo3_file = tmp_path / "pyo3.rs"
        pyo3_file.write_text("""
#[pyfunction]
fn exposed_function() {
    result.unwrap();
}
""")
        
        # Medium severity: regular unwrap
        regular_file = tmp_path / "regular.rs"
        regular_file.write_text("""
fn internal_function() {
    result.unwrap();
}
""")
        
        validator = RustErrorValidator()
        
        pyo3_findings = validator.scan_file(pyo3_file)
        assert any(f.severity == 'high' for f in pyo3_findings)
        
        regular_findings = validator.scan_file(regular_file)
        assert any(f.severity == 'medium' for f in regular_findings)
    
    def test_finding_has_suggestions(self, tmp_path):
        """Test findings include helpful suggestions."""
        test_file = tmp_path / "test.rs"
        test_file.write_text("fn test() { x.unwrap(); }")
        
        validator = RustErrorValidator()
        findings = validator.scan_file(test_file)
        
        assert len(findings) >= 1
        assert findings[0].suggestion
        assert 'PyResult' in findings[0].suggestion or 'unwrap_or' in findings[0].suggestion


class TestFindingDataclass:
    """Test Finding dataclass."""
    
    def test_finding_creation(self):
        """Test Finding can be created with required fields."""
        finding = Finding(
            file="test.rs",
            line=10,
            severity="high",
            issue="unwrap() detected"
        )
        assert finding.file == "test.rs"
        assert finding.line == 10
        assert finding.severity == "high"
        assert finding.issue == "unwrap() detected"
    
    def test_finding_with_suggestion(self):
        """Test Finding with optional suggestion field."""
        finding = Finding(
            file="test.rs",
            line=10,
            severity="high",
            issue="unwrap() detected",
            suggestion="Use PyResult instead"
        )
        assert finding.suggestion == "Use PyResult instead"


@pytest.fixture
def sample_rust_code():
    """Provide sample Rust code for testing."""
    return """
#[pyfunction]
fn process_data(input: &str) -> PyResult<String> {
    let data = parse_input(input).unwrap();  // Bad: can panic
    Ok(data.to_string())
}

#[test]
fn test_process() {
    let result = process_data("test").unwrap();  // OK: in test
}

fn internal_helper() {
    panic!("Not implemented");  // Bad: explicit panic
}
"""


def test_real_world_scenario(tmp_path, sample_rust_code):
    """Test validator on realistic Rust code."""
    rust_file = tmp_path / "real_code.rs"
    rust_file.write_text(sample_rust_code)
    
    validator = RustErrorValidator()
    findings = validator.scan_file(rust_file)
    
    # Should detect unwrap in pyfunction and panic (not unwrap in test)
    assert len(findings) >= 1
    
    # Should have at least one high severity finding (PyO3 unwrap or panic)
    high_severity_findings = [f for f in findings if f.severity == 'high']
    assert len(high_severity_findings) >= 1
