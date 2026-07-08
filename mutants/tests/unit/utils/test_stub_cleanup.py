from pathlib import Path

from src.codex_ml.utils.stub_cleanup import StubAnalyzer, StubInfo, find_stubs, prioritize_stubs


def test_stub_info():
    info = StubInfo(
        file_path=Path("test.py"),
        line_number=10,
        stub_type="TODO",
        message="Fix this",
        priority="P1",
    )
    assert "P1 test.py:10 [TODO] Fix this" == str(info), "Condition must be true"


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

    assert len(stubs) == 3, "Stubs must not be empty"

    todo_stubs = [s for s in stubs if s.stub_type == "TODO"]
    assert len(todo_stubs) == 1, "Todo_stubs must not be empty"
    assert todo_stubs[0].line_number == 3, "line_number is not valid"

    nie_stubs = [s for s in stubs if s.stub_type == "NotImplementedError"]
    assert len(nie_stubs) == 1, "Nie_stubs must not be empty"
    assert "Not done yet" in nie_stubs[0].message, "Condition must be true"

    fixme_stubs = [s for s in stubs if s.stub_type == "FIXME"]
    assert len(fixme_stubs) == 1, "Fixme_stubs must not be empty"
    assert fixme_stubs[0].line_number == 7, "line_number is not valid"


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
    nie_stubs = [s for s in stubs if s.stub_type == "NotImplementedError"]
    assert len(nie_stubs) == 0, "Abstract method stubs should be ignored"


def test_find_stubs_and_prioritize(tmp_path):
    py_file = tmp_path / "test_code.py"
    py_file.write_text("""
# FIXME: Critical bug
# TODO: Minor enhancement
""")

    stubs = find_stubs([tmp_path])
    assert len(stubs) == 2, "Stubs must not be empty"

    prioritized = prioritize_stubs(stubs)
    assert len(prioritized) == 2, "Prioritized must not be empty"
    assert prioritized[0].stub_type == "FIXME", "stub_type is not valid"
