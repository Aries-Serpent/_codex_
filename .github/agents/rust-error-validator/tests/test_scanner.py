"""Tests for Rust Error Validator"""
import pytest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from scanner import RustErrorScanner, Finding

def test_scanner_detects_unwrap():
    """Test scanner detects unwrap() calls"""
    scanner = RustErrorScanner()
    test_file = Path(__file__).parent / "fixtures" / "test.rs"
    test_file.parent.mkdir(exist_ok=True)
    test_file.write_text("#[pyfunction]\nfn test() {\n    let x = something().unwrap();\n}")
    findings = scanner.scan_file(test_file)
    assert len(findings) >= 1
    assert any('unwrap' in f.issue for f in findings)

def test_scanner_ignores_tests():
    """Test scanner ignores unwrap in test code"""
    scanner = RustErrorScanner()
    test_file = Path(__file__).parent / "fixtures" / "test_code.rs"
    test_file.parent.mkdir(exist_ok=True)
    test_file.write_text("#[test]\nfn test() {\n    let x = something().unwrap();\n}")
    findings = scanner.scan_file(test_file)
    assert len(findings) == 0
