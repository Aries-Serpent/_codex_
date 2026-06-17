import pytest
from pathlib import Path
from src.codex_ml.utils.stub_cleanup import StubAnalyzer, generate_stub_report, find_stubs, prioritize_stubs

def test_integration_stub_cleanup(tmp_path):
    source_dir = tmp_path / "src"
    source_dir.mkdir()
    
    # Create some files with real code patterns
    file1 = source_dir / "file1.py"
    file1.write_text("""
def calculate():
    # TODO: implement calculation # P1
    raise NotImplementedError("Calculate not implemented")

class Base:
    def method1(self):
        # FIXME: bug here
        pass
        
    def method2(self):
        # P0 TODO: critical fix
        pass
        
    def method3(self):
        # P2 TODO: low priority
        pass
    """)

    file2 = source_dir / "file2.py"
    file2.write_text("""
from abc import ABC, abstractmethod
from typing import Protocol

class AbstractBase(ABC):
    @abstractmethod
    def must_implement(self):
        raise NotImplementedError("abstract")

class Prot(Protocol):
    def proto_method(self):
        raise NotImplementedError
        
def standalone():
    # TODO: Add logic here
    pass
    
@abstractmethod
def standalone_abstract():
    raise NotImplementedError
    """)
    
    file3 = source_dir / "file3.py"
    file3.write_text("""
class Invalid:
    def missing(self):
        raise NotImplementedError
        
    def another(self):
        raise NotImplementedError()
    """)
    
    # Analyze with all source dirs
    analyzer = StubAnalyzer(source_dirs=[source_dir])
    stubs = analyzer.analyze()
    
    # find_stubs convenience function
    stubs2 = find_stubs([source_dir])
    assert len(stubs) == len(stubs2)
    
    assert len(stubs) > 0
    
    # Test prioritize_stubs
    prioritized = prioritize_stubs(stubs)
    assert prioritized[0].priority == "P0"
    
    # Test summary
    summary = analyzer.get_summary()
    assert summary["total"] == len(stubs)
    assert summary["by_priority"]["P0"] > 0
    assert summary["by_priority"]["P1"] > 0
    assert summary["by_priority"]["P2"] > 0
    assert summary["by_type"]["NotImplementedError"] > 0
    assert summary["by_type"]["TODO"] > 0
    assert summary["by_type"]["FIXME"] > 0
    
    # Test generate_stub_report
    report_file = tmp_path / "report.md"
    generate_stub_report(report_file, source_dirs=[source_dir])
    
    assert report_file.exists()
    report_content = report_file.read_text()
    assert "Total Stubs" in report_content
    assert "P0" in report_content
    assert "NotImplementedError" in report_content
