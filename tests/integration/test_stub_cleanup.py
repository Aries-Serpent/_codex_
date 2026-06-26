import pytest

pytestmark = pytest.mark.integration

import pytest

from src.codex_ml.utils.stub_cleanup import (
    StubAnalyzer,
    find_stubs,
    generate_stub_report,
    prioritize_stubs,
)


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
    assert len(stubs) == len(stubs2), "Stubs must not be empty"

    assert len(stubs) > 0, "Stubs must not be empty"

    # Test prioritize_stubs
    prioritized = prioritize_stubs(stubs)
    assert prioritized[0].priority == "P0", "priority is not valid"

    # Test summary
    summary = analyzer.get_summary()
    assert summary["total"] == len(stubs), "Stubs must not be empty"
    assert summary["by_priority"]["P0"] > 0, "Value must be greater than zero"
    assert summary["by_priority"]["P1"] > 0, "Value must be greater than zero"
    assert summary["by_priority"]["P2"] > 0, "Value must be greater than zero"
    assert summary["by_type"]["NotImplementedError"] > 0, "Value must be greater than zero"
    assert summary["by_type"]["TODO"] > 0, "Value must be greater than zero"
    assert summary["by_type"]["FIXME"] > 0, "Value must be greater than zero"

    # Test generate_stub_report
    report_file = tmp_path / "report.md"
    generate_stub_report(report_file, source_dirs=[source_dir])

    assert report_file.exists(), "rep is not valid"
    report_content = report_file.read_text()
    assert "Total Stubs" in report_content, "Content must not be empty"
    assert "P0" in report_content, "Content must not be empty"
    assert "NotImplementedError" in report_content, "Content must not be empty"


def test_stub_cleanup_default_dirs(monkeypatch, tmp_path):
    # Change cwd so that default dirs "src" and "training" don't analyze the real codebase
    monkeypatch.chdir(tmp_path)

    # Create fake src and training dirs
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "test.py").write_text("raise NotImplementedError('foo')\n")

    training_dir = tmp_path / "training"
    training_dir.mkdir()
    (training_dir / "test2.py").write_text("# TODO: something\n")

    analyzer = StubAnalyzer()
    stubs = analyzer.analyze()
    assert len(stubs) == 2, "Stubs must not be empty"

    report_file = tmp_path / "report.md"
    generate_stub_report(report_file)
    assert report_file.exists(), "rep is not valid"


def test_stub_cleanup_edge_cases(tmp_path):
    source_dir = tmp_path / "src"
    source_dir.mkdir()

    # Unparseable python file containing NotImplementedError
    file_bad = source_dir / "bad.py"
    file_bad.write_text("""
def calculate():
    raise NotImplementedError
    this is invalid python syntax ++==--
    """)

    analyzer = StubAnalyzer([source_dir])
    stubs = analyzer.analyze()
    assert len(stubs) == 1, "Stubs must not be empty"
    assert str(stubs[0]).startswith("P0"), "Condition must be true"

    # Test __str__ explicit
    assert "bad.py" in str(stubs[0]), "Condition must be true"


def test_stub_cleanup_ast_attributes(tmp_path):
    source_dir = tmp_path / "src"
    source_dir.mkdir()

    file_ast = source_dir / "ast_test.py"
    file_ast.write_text("""
import abc
import typing

class MyABC(abc.ABC):
    @abc.abstractmethod
    def must_impl(self):
        raise NotImplementedError("abstract")

class MyProto(typing.Protocol):
    def proto_impl(self):
        raise NotImplementedError("abstract proto")

@abc.abstractmethod
def standalone():
    raise NotImplementedError("standalone")
    """)

    analyzer = StubAnalyzer([source_dir])
    stubs = analyzer.analyze()
    # these are abstract, so stubs should be 0
    assert len(stubs) == 0, "Stubs must not be empty"
