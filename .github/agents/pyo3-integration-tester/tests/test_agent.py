"""Comprehensive unit tests for PyO3 Integration Tester Agent."""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent import PyO3IntegrationTester, Binding, TestGenerator


class TestPyO3IntegrationTester:
    """Test suite for PyO3IntegrationTester class."""
    
    def test_tester_initialization(self):
        """Test tester initializes with default config."""
        tester = PyO3IntegrationTester()
        assert tester.config is not None
        assert tester.config['enabled'] is True
        assert tester.patterns is not None
    
    def test_parse_pyfunction(self, tmp_path):
        """Test parsing #[pyfunction] from Rust file."""
        rust_file = tmp_path / "test.rs"
        rust_file.write_text("""
#[pyfunction]
pub fn process_data(input: &str) -> PyResult<String> {
    Ok(input.to_string())
}
""")
        
        tester = PyO3IntegrationTester()
        bindings = tester.parse_rust_file(rust_file)
        
        assert len(bindings) >= 1
        assert any(b.name == 'process_data' for b in bindings)
        assert any(b.has_error_handling for b in bindings)
    
    def test_parse_async_function(self, tmp_path):
        """Test parsing async PyO3 functions."""
        rust_file = tmp_path / "async.rs"
        rust_file.write_text("""
#[pyfunction]
pub async fn fetch_data() -> PyResult<Vec<u8>> {
    Ok(vec![])
}
""")
        
        tester = PyO3IntegrationTester()
        bindings = tester.parse_rust_file(rust_file)
        
        assert len(bindings) >= 1
        binding = bindings[0]
        assert binding.is_async is True
    
    def test_scan_directory_recursive(self, tmp_path):
        """Test scanning directory recursively."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        
        (tmp_path / "file1.rs").write_text("#[pyfunction]\nfn f1() {}")
        (subdir / "file2.rs").write_text("#[pyfunction]\nfn f2() {}")
        
        tester = PyO3IntegrationTester()
        bindings = tester.scan_directory(tmp_path, recursive=True)
        
        assert len(bindings) == 2
    
    def test_generate_tests(self, tmp_path):
        """Test generating test files."""
        binding = Binding(
            type='function',
            name='test_func',
            return_type='PyResult<String>',
            parameters=[],
            file='test.rs',
            line=10,
            has_error_handling=True
        )
        
        tester = PyO3IntegrationTester()
        output_dir = tmp_path / "tests"
        generated = tester.generate_tests([binding], output_dir)
        
        assert len(generated) == 1
        assert 'test_func' in generated
        assert generated['test_func'].exists()
    
    def test_generate_report(self):
        """Test report generation."""
        bindings = [
            Binding('function', 'f1', 'String', [], 'file1.rs', 1, False, False),
            Binding('function', 'f2', 'PyResult<int>', [], 'file1.rs', 10, True, True),
            Binding('function', 'f3', 'None', [], 'file2.rs', 5, False, False),
        ]
        
        tester = PyO3IntegrationTester()
        report = tester.generate_report(bindings)
        
        assert report['total_bindings'] == 3
        assert report['unique_files'] == 2
        assert report['async_functions'] == 1
        assert report['functions_with_error_handling'] == 1


class TestTestGenerator:
    """Test suite for TestGenerator class."""
    
    def test_generate_basic_test(self):
        """Test generating basic test code."""
        binding = Binding(
            type='function',
            name='simple_func',
            return_type='String',
            parameters=[],
            file='test.rs',
            line=1
        )
        
        generator = TestGenerator()
        test_code = generator.generate_test(binding)
        
        assert 'def test_simple_func_happy_path():' in test_code
        assert 'def test_simple_func_type_validation():' in test_code
        assert 'def test_simple_func_performance():' in test_code
    
    def test_generate_error_handling_test(self):
        """Test generating error handling test."""
        binding = Binding(
            type='function',
            name='fallible_func',
            return_type='PyResult<Vec<u8>>',
            parameters=[],
            file='test.rs',
            line=1,
            has_error_handling=True
        )
        
        generator = TestGenerator()
        test_code = generator.generate_test(binding)
        
        assert 'def test_fallible_func_error_handling():' in test_code
        assert 'pytest.raises(Exception)' in test_code
    
    def test_generate_async_test(self):
        """Test generating async test."""
        binding = Binding(
            type='function',
            name='async_func',
            return_type='PyResult<String>',
            parameters=[],
            file='test.rs',
            line=1,
            is_async=True,
            has_error_handling=True
        )
        
        generator = TestGenerator()
        test_code = generator.generate_test(binding)
        
        assert '@pytest.mark.asyncio' in test_code
        assert 'async def test_async_func_async():' in test_code
        assert 'await async_func()' in test_code
    
    def test_identifier_validation(self):
        """Test that invalid identifiers are rejected."""
        binding = Binding(
            type='function',
            name='invalid-name',  # Invalid Python identifier
            return_type='String',
            parameters=[],
            file='test.rs',
            line=1
        )
        
        generator = TestGenerator()
        with pytest.raises(ValueError):
            generator.generate_test(binding)


def test_real_world_scenario(tmp_path):
    """Test complete workflow with realistic Rust code."""
    rust_file = tmp_path / "lib.rs"
    rust_file.write_text("""
use pyo3::prelude::*;

#[pyfunction]
pub fn compress_data(data: &[u8]) -> PyResult<Vec<u8>> {
    // Implementation
    Ok(vec![])
}

#[pyfunction]
pub async fn fetch_remote(url: &str) -> PyResult<String> {
    // Implementation
    Ok(String::new())
}

#[pyfunction]
fn helper_function() -> String {
    String::new()
}
""")
    
    tester = PyO3IntegrationTester()
    bindings = tester.scan_directory(tmp_path)
    
    assert len(bindings) == 3
    
    # Generate tests
    output_dir = tmp_path / "tests"
    generated = tester.generate_tests(bindings, output_dir)
    
    assert len(generated) == 3
    assert all(Path(f).exists() for f in generated.values())
    
    # Check report
    report = tester.generate_report(bindings)
    assert report['total_bindings'] == 3
    assert report['async_functions'] >= 1
