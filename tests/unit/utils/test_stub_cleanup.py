import pytest
from pathlib import Path
from src.codex_ml.utils.stub_cleanup import StubAnalyzer, StubInfo, find_stubs, prioritize_stubs

def test_stub_info():
    info = StubInfo(
        file_path=Path("test.py"),
        line_number=10,
        stub_type="TODO",
        message="Fix this",
        priority="P1"
    )
    assert "P1 test.py:10 [TODO] Fix this" == str(info)

def test_stub_analyzer_basic(tmp_path):
    py_file = tmp_path / "test_code.py"
    py_file.write_text("""
def my_func():
    # TODO: Implement this
    raise NotImplementedError("Not done yet")

def another_func():
    # FIXME: Bug here
    pass
""")
    
    analyzer = StubAnalyzer(source_dirs=[tmp_path])
    stubs = analyzer.analyze()
    
    assert len(stubs) >= 3 # TODO, NotImplementedError, FIXME
    
    todo_stubs = [s for s in stubs if s.stub_type == "TODO"]
    assert len(todo_stubs) == 1
    assert todo_stubs[0].line_number == 3
    
    nie_stubs = [s for s in stubs if s.stub_type == "NotImplementedError"]
    assert len(nie_stubs) == 1
    assert "Not done yet" in nie_stubs[0].message
    
    fixme_stubs = [s for s in stubs if s.stub_type == "FIXME"]
    assert len(fixme_stubs) == 1
    assert fixme_stubs[0].line_number == 7

def test_stub_analyzer_abstract_method(tmp_path):
    py_file = tmp_path / "test_abstract.py"
    py_file.write_text("""
from abc import ABC, abstractmethod

class MyInterface(ABC):
    @abstractmethod
    def do_something(self):
        raise NotImplementedError("abstract")
""")
    
    analyzer = StubAnalyzer(source_dirs=[tmp_path])
    stubs = analyzer.analyze()
    # abstractmethod NotImplementedError should be ignored if analyzer handles it
    nie_stubs = [s for s in stubs if s.stub_type == "NotImplementedError"]
    assert len(nie_stubs) == 0

def test_find_stubs_and_prioritize(tmp_path):
    py_file = tmp_path / "test_code.py"
    py_file.write_text("""
# FIXME: Critical bug
# TODO: Minor enhancement
""")
    
    stubs = find_stubs([tmp_path])
    assert len(stubs) == 2
    
    prioritized = prioritize_stubs(stubs)
    assert len(prioritized) == 2
    assert prioritized[0].stub_type == "FIXME" # FIXMEs are usually higher priority
