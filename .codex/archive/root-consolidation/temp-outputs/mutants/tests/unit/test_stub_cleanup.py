"""Unit tests for codex_ml.utils.stub_cleanup module.

Covers StubInfo, StubAnalyzer, find_stubs, prioritize_stubs, and
generate_stub_report.  All filesystem interactions use pytest's
tmp_path fixture – no real source directories are touched.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

from codex_ml.utils.stub_cleanup import (
    StubAnalyzer,
    StubInfo,
    find_stubs,
    generate_stub_report,
    prioritize_stubs,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write(tmp_path: Path, name: str, source: str) -> Path:
    """Write *source* into *tmp_path/name* and return the path."""
    p = tmp_path / name
    p.write_text(textwrap.dedent(source), encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# StubInfo
# ---------------------------------------------------------------------------


class TestStubInfo:
    """Tests for the StubInfo dataclass."""

    def test_minimal_creation(self, tmp_path: Path) -> None:
        fp = tmp_path / "x.py"
        stub = StubInfo(
            file_path=fp,
            line_number=5,
            stub_type="TODO",
            message="do something",
        )
        assert stub.file_path == fp, "file_path is not valid"
        assert stub.line_number == 5, "line_number is not valid"
        assert stub.stub_type == "TODO", "stub_type is not valid"
        assert stub.message == "do something", "message is not valid"

    def test_default_priority(self, tmp_path: Path) -> None:
        stub = StubInfo(file_path=tmp_path / "x.py", line_number=1, stub_type="FIXME", message="m")
        assert stub.priority == "P2", "priority is not valid"

    def test_custom_priority_and_context(self, tmp_path: Path) -> None:
        stub = StubInfo(
            file_path=tmp_path / "x.py",
            line_number=10,
            stub_type="NotImplementedError",
            message="not done",
            priority="P0",
            context="    raise NotImplementedError('not done')",
        )
        assert stub.priority == "P0", "priority is not valid"
        assert stub.context == "    raise NotImplementedError('not done')", "Error should be raised or set"

    def test_str_representation(self, tmp_path: Path) -> None:
        fp = tmp_path / "module.py"
        stub = StubInfo(
            file_path=fp,
            line_number=42,
            stub_type="TODO",
            message="finish me",
            priority="P1",
        )
        result = str(stub)
        assert "P1" in result, "Result must not be empty"
        assert "42" in result, "Result must not be empty"
        assert "TODO" in result, "Result must not be empty"
        assert "finish me" in result, "Result must not be empty"

    def test_str_contains_filepath(self, tmp_path: Path) -> None:
        fp = tmp_path / "deep" / "path.py"
        stub = StubInfo(file_path=fp, line_number=1, stub_type="FIXME", message="x", priority="P2")
        assert str(fp) in str(stub), "Condition must be true"

    def test_context_none_by_default(self, tmp_path: Path) -> None:
        stub = StubInfo(file_path=tmp_path / "x.py", line_number=1, stub_type="TODO", message="m")
        assert stub.context is None, "context is not valid"


# ---------------------------------------------------------------------------
# StubAnalyzer – initialisation
# ---------------------------------------------------------------------------


class TestStubAnalyzerInit:
    """Tests for StubAnalyzer.__init__."""

    def test_default_source_dirs(self) -> None:
        analyzer = StubAnalyzer()
        names = [d.name for d in analyzer.source_dirs]
        assert "src" in names, "Condition must be true"
        assert "training" in names, "Condition must be true"

    def test_custom_source_dirs(self, tmp_path: Path) -> None:
        custom = [tmp_path / "a", tmp_path / "b"]
        analyzer = StubAnalyzer(source_dirs=custom)
        assert analyzer.source_dirs == custom, "source_dirs is not valid"

    def test_source_dirs_coerced_to_path(self, tmp_path: Path) -> None:
        # Pass plain strings; init should coerce to Path objects
        analyzer = StubAnalyzer(source_dirs=[str(tmp_path / "foo")])
        assert all(isinstance(d, Path) for d in analyzer.source_dirs)

    def test_empty_stubs_on_init(self) -> None:
        analyzer = StubAnalyzer()
        assert analyzer.stubs == [], "stubs is not valid"


# ---------------------------------------------------------------------------
# StubAnalyzer.analyze
# ---------------------------------------------------------------------------


class TestStubAnalyzerAnalyze:
    """Tests for StubAnalyzer.analyze."""

    def test_nonexistent_dir_skipped(self, tmp_path: Path) -> None:
        analyzer = StubAnalyzer(source_dirs=[tmp_path / "does_not_exist"])
        stubs = analyzer.analyze()
        assert stubs == [], "stubs is not valid"

    def test_empty_dir_returns_no_stubs(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        src.mkdir()
        analyzer = StubAnalyzer(source_dirs=[src])
        assert analyzer.analyze() == [], "Condition must be true"

    def test_returns_list_of_stub_info(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        src.mkdir()
        _write(src, "mod.py", "# TODO: implement this\n")
        stubs = StubAnalyzer(source_dirs=[src]).analyze()
        assert all(isinstance(s, StubInfo) for s in stubs)

    def test_analyze_resets_stubs_between_calls(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        src.mkdir()
        _write(src, "a.py", "# TODO first\n")
        analyzer = StubAnalyzer(source_dirs=[src])
        first = analyzer.analyze()
        second = analyzer.analyze()
        # Results must be identical (stubs list is reset each call)
        assert len(first) == len(second), "First must not be empty"

    def test_multiple_source_dirs(self, tmp_path: Path) -> None:
        d1 = tmp_path / "d1"
        d2 = tmp_path / "d2"
        d1.mkdir()
        d2.mkdir()
        _write(d1, "a.py", "# TODO in d1\n")
        _write(d2, "b.py", "# TODO in d2\n")
        stubs = StubAnalyzer(source_dirs=[d1, d2]).analyze()
        assert len(stubs) == 2, "Stubs must not be empty"

    def test_recurses_into_subdirectories(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        sub = src / "sub"
        sub.mkdir(parents=True)
        _write(sub, "deep.py", "# TODO deep\n")
        stubs = StubAnalyzer(source_dirs=[src]).analyze()
        assert len(stubs) == 1, "Stubs must not be empty"

    def test_ignores_non_python_files(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        src.mkdir()
        (src / "notes.txt").write_text("# TODO ignore me\n", encoding="utf-8")
        stubs = StubAnalyzer(source_dirs=[src]).analyze()
        assert stubs == [], "stubs is not valid"


# ---------------------------------------------------------------------------
# StubAnalyzer._analyze_file – NotImplementedError detection
# ---------------------------------------------------------------------------


class TestAnalyzeFileNotImplementedError:
    """Tests for NotImplementedError detection in _analyze_file."""

    def test_plain_raise_not_implemented(self, tmp_path: Path) -> None:
        f = _write(
            tmp_path,
            "mod.py",
            """\
            def do_thing():
                raise NotImplementedError("not done yet")
        """,
        )
        analyzer = StubAnalyzer(source_dirs=[])
        analyzer._analyze_file(f)
        assert len(analyzer.stubs) == 1, "Collection must not be empty"
        stub = analyzer.stubs[0]
        assert stub.stub_type == "NotImplementedError", "Error should be raised or set"
        assert stub.priority == "P0", "priority is not valid"
        assert "not done yet" in stub.message, "Condition must be true"

    def test_raise_without_message(self, tmp_path: Path) -> None:
        f = _write(
            tmp_path,
            "mod.py",
            """\
            def do_thing():
                raise NotImplementedError
        """,
        )
        analyzer = StubAnalyzer(source_dirs=[])
        analyzer._analyze_file(f)
        # line does not start with "raise NotImplementedError(" so no parentheses → message fallback
        # The stripped line IS "raise NotImplementedError" which starts with "raise "
        assert len(analyzer.stubs) == 1, "Collection must not be empty"
        assert analyzer.stubs[0].stub_type == "NotImplementedError", "Error should be raised or set"

    def test_abstract_method_is_skipped(self, tmp_path: Path) -> None:
        f = _write(
            tmp_path,
            "mod.py",
            """\
            from abc import abstractmethod

            class Base:
                @abstractmethod
                def do_thing(self):
                    raise NotImplementedError
        """,
        )
        analyzer = StubAnalyzer(source_dirs=[])
        analyzer._analyze_file(f)
        assert len(analyzer.stubs) == 0, "Collection must not be empty"

    def test_abc_base_class_skipped(self, tmp_path: Path) -> None:
        f = _write(
            tmp_path,
            "mod.py",
            """\
            from abc import ABC

            class Base(ABC):
                def do_thing(self):
                    raise NotImplementedError
        """,
        )
        analyzer = StubAnalyzer(source_dirs=[])
        analyzer._analyze_file(f)
        assert len(analyzer.stubs) == 0, "Collection must not be empty"

    def test_not_raise_statement_ignored(self, tmp_path: Path) -> None:
        # A comment mentioning NotImplementedError should be ignored
        f = _write(tmp_path, "mod.py", "# NotImplementedError example\n")
        analyzer = StubAnalyzer(source_dirs=[])
        analyzer._analyze_file(f)
        assert analyzer.stubs == [], "stubs is not valid"

    def test_context_is_stripped_line(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "mod.py", "    raise NotImplementedError('ctx')\n")
        analyzer = StubAnalyzer(source_dirs=[])
        analyzer._analyze_file(f)
        assert len(analyzer.stubs) == 1, "Collection must not be empty"
        assert analyzer.stubs[0].context == "raise NotImplementedError('ctx')", "Error should be raised or set"


# ---------------------------------------------------------------------------
# StubAnalyzer._analyze_file – TODO / FIXME detection
# ---------------------------------------------------------------------------


class TestAnalyzeFileTodoFixme:
    """Tests for TODO and FIXME detection in _analyze_file."""

    def test_todo_detected(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "mod.py", "x = 1  # TODO: refactor this\n")
        analyzer = StubAnalyzer(source_dirs=[])
        analyzer._analyze_file(f)
        todos = [s for s in analyzer.stubs if s.stub_type == "TODO"]
        assert len(todos) == 1, "Todos must not be empty"
        assert "refactor this" in todos[0].message, "Condition must be true"

    def test_fixme_detected(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "mod.py", "x = 1  # FIXME: broken logic\n")
        analyzer = StubAnalyzer(source_dirs=[])
        analyzer._analyze_file(f)
        fixmes = [s for s in analyzer.stubs if s.stub_type == "FIXME"]
        assert len(fixmes) == 1, "Fixmes must not be empty"
        assert "broken logic" in fixmes[0].message, "Condition must be true"

    def test_todo_lowercase(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "mod.py", "# todo: lowercase check\n")
        analyzer = StubAnalyzer(source_dirs=[])
        analyzer._analyze_file(f)
        assert len(analyzer.stubs) == 1, "Collection must not be empty"

    def test_fixme_lowercase(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "mod.py", "# fixme: lowercase check\n")
        analyzer = StubAnalyzer(source_dirs=[])
        analyzer._analyze_file(f)
        assert len(analyzer.stubs) == 1, "Collection must not be empty"

    def test_todo_without_hash_ignored(self, tmp_path: Path) -> None:
        # "TODO" in a string literal without a "#" should not match
        f = _write(tmp_path, "mod.py", 'msg = "TODO: not a comment"\n')
        analyzer = StubAnalyzer(source_dirs=[])
        analyzer._analyze_file(f)
        assert analyzer.stubs == [], "stubs is not valid"

    def test_fixme_without_hash_ignored(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "mod.py", 'msg = "FIXME: not a comment"\n')
        analyzer = StubAnalyzer(source_dirs=[])
        analyzer._analyze_file(f)
        assert analyzer.stubs == [], "stubs is not valid"

    def test_line_number_correct(self, tmp_path: Path) -> None:
        source = "x = 1\ny = 2\n# TODO: third line\n"
        f = _write(tmp_path, "mod.py", source)
        analyzer = StubAnalyzer(source_dirs=[])
        analyzer._analyze_file(f)
        assert analyzer.stubs[0].line_number == 3, "line_number is not valid"

    def test_multiple_stubs_same_file(self, tmp_path: Path) -> None:
        f = _write(
            tmp_path,
            "mod.py",
            """\
            # TODO: first
            # FIXME: second
            raise NotImplementedError("third")
        """,
        )
        analyzer = StubAnalyzer(source_dirs=[])
        analyzer._analyze_file(f)
        types = {s.stub_type for s in analyzer.stubs}
        assert "TODO" in types, "Condition must be true"
        assert "FIXME" in types, "Condition must be true"
        assert "NotImplementedError" in types, "Error should be raised or set"

    def test_unreadable_file_doesnt_crash(self, tmp_path: Path) -> None:
        # Pass a path that doesn't exist – should log and continue, not raise
        missing = tmp_path / "ghost.py"
        analyzer = StubAnalyzer(source_dirs=[])
        analyzer._analyze_file(missing)  # must not raise
        assert analyzer.stubs == [], "stubs is not valid"


# ---------------------------------------------------------------------------
# StubAnalyzer._determine_priority
# ---------------------------------------------------------------------------


class TestDeterminePriority:
    """Tests for StubAnalyzer._determine_priority."""

    def setup_method(self) -> None:
        self.analyzer = StubAnalyzer(source_dirs=[])

    def test_p0_keyword(self) -> None:
        result = self.analyzer._determine_priority("P0: critical issue")
        assert result == "P0", "Condition must be true"

    def test_critical_keyword(self) -> None:
        result = self.analyzer._determine_priority("CRITICAL: system failure")
        assert result == "P0", "Condition must be true"

    def test_blocking_keyword(self) -> None:
        result = self.analyzer._determine_priority("BLOCKING: merge blocker")
        assert result == "P0", "Condition must be true"

    def test_p1_keyword(self) -> None:
        result = self.analyzer._determine_priority("P1: high priority")
        assert result == "P1", "Condition must be true"

    def test_high_keyword(self) -> None:
        result = self.analyzer._determine_priority("HIGH: high priority")
        assert result == "P1", "Condition must be true"

    def test_important_keyword(self) -> None:
        result = self.analyzer._determine_priority("IMPORTANT: important fix")
        assert result == "P1", "Condition must be true"

    def test_default_p2(self) -> None:
        result = self.analyzer._determine_priority("some random text")
        assert result == "P2", "Condition must be true"

    def test_case_insensitive(self) -> None:
        result = self.analyzer._determine_priority("critical: lowercase critical")
        assert result == "P0", "Condition must be true"


# ---------------------------------------------------------------------------
# StubAnalyzer.get_by_priority / get_by_type / get_summary
# ---------------------------------------------------------------------------


class TestStubAnalyzerFiltersAndSummary:
    """Tests for get_by_priority, get_by_type, and get_summary."""

    def _make_analyzer_with_stubs(self, tmp_path: Path) -> StubAnalyzer:
        analyzer = StubAnalyzer(source_dirs=[])
        fp = tmp_path / "x.py"
        analyzer.stubs = [
            StubInfo(fp, 1, "TODO", "low", "P2"),
            StubInfo(fp, 2, "FIXME", "important", "P1"),
            StubInfo(fp, 3, "NotImplementedError", "critical", "P0"),
            StubInfo(fp, 4, "TODO", "another p0", "P0"),
        ]
        return analyzer

    def test_get_by_priority_p0(self, tmp_path: Path) -> None:
        analyzer = self._make_analyzer_with_stubs(tmp_path)
        p0 = analyzer.get_by_priority("P0")
        assert len(p0) == 2, "P0 must not be empty"
        assert all(s.priority == "P0" for s in p0), "priority is not valid"

    def test_get_by_priority_p1(self, tmp_path: Path) -> None:
        analyzer = self._make_analyzer_with_stubs(tmp_path)
        p1 = analyzer.get_by_priority("P1")
        assert len(p1) == 1, "P1 must not be empty"
        assert p1[0].stub_type == "FIXME", "stub_type is not valid"

    def test_get_by_priority_p2(self, tmp_path: Path) -> None:
        analyzer = self._make_analyzer_with_stubs(tmp_path)
        p2 = analyzer.get_by_priority("P2")
        assert len(p2) == 1, "P2 must not be empty"
        assert p2[0].stub_type == "TODO", "stub_type is not valid"

    def test_get_by_priority_empty(self, tmp_path: Path) -> None:
        analyzer = StubAnalyzer(source_dirs=[])
        assert analyzer.get_by_priority("P0") == [], "Condition must be true"

    def test_get_by_type_todo(self, tmp_path: Path) -> None:
        analyzer = self._make_analyzer_with_stubs(tmp_path)
        todos = analyzer.get_by_type("TODO")
        assert len(todos) == 2, "Todos must not be empty"

    def test_get_by_type_fixme(self, tmp_path: Path) -> None:
        analyzer = self._make_analyzer_with_stubs(tmp_path)
        fixmes = analyzer.get_by_type("FIXME")
        assert len(fixmes) == 1, "Fixmes must not be empty"

    def test_get_by_type_not_implemented(self, tmp_path: Path) -> None:
        analyzer = self._make_analyzer_with_stubs(tmp_path)
        nie = analyzer.get_by_type("NotImplementedError")
        assert len(nie) == 1, "Nie must not be empty"

    def test_get_by_type_unknown_returns_empty(self, tmp_path: Path) -> None:
        analyzer = self._make_analyzer_with_stubs(tmp_path)
        assert analyzer.get_by_type("UNKNOWN") == [], "Condition must be true"

    def test_get_summary_structure(self, tmp_path: Path) -> None:
        analyzer = self._make_analyzer_with_stubs(tmp_path)
        summary = analyzer.get_summary()
        assert "total" in summary, "Condition must be true"
        assert "by_priority" in summary, "Condition must be true"
        assert "by_type" in summary, "Condition must be true"

    def test_get_summary_counts(self, tmp_path: Path) -> None:
        analyzer = self._make_analyzer_with_stubs(tmp_path)
        summary = analyzer.get_summary()
        assert summary["total"] == 4, "Condition must be true"
        assert summary["by_priority"]["P0"] == 2, "Condition must be true"
        assert summary["by_priority"]["P1"] == 1, "Condition must be true"
        assert summary["by_priority"]["P2"] == 1, "Condition must be true"
        assert summary["by_type"]["TODO"] == 2, "Condition must be true"
        assert summary["by_type"]["FIXME"] == 1, "Condition must be true"
        assert summary["by_type"]["NotImplementedError"] == 1, "Error should be raised or set"

    def test_get_summary_empty(self) -> None:
        analyzer = StubAnalyzer(source_dirs=[])
        summary = analyzer.get_summary()
        assert summary["total"] == 0, "Condition must be true"
        assert all(v == 0 for v in summary["by_priority"].values()), "Value must be initialized"
        assert all(v == 0 for v in summary["by_type"].values()), "Value must be initialized"


# ---------------------------------------------------------------------------
# StubAnalyzer._is_abstract_method
# ---------------------------------------------------------------------------


class TestIsAbstractMethod:
    """Tests for StubAnalyzer._is_abstract_method."""

    def setup_method(self) -> None:
        self.analyzer = StubAnalyzer(source_dirs=[])

    def test_abstractmethod_decorator(self, tmp_path: Path) -> None:
        f = _write(
            tmp_path,
            "mod.py",
            """\
            from abc import abstractmethod

            class Base:
                @abstractmethod
                def run(self):
                    raise NotImplementedError
        """,
        )
        # line 6 is "raise NotImplementedError"
        assert self.analyzer._is_abstract_method(f, 6) is True

    def test_abc_base_class(self, tmp_path: Path) -> None:
        f = _write(
            tmp_path,
            "mod.py",
            """\
            from abc import ABC

            class Base(ABC):
                def run(self):
                    raise NotImplementedError
        """,
        )
        assert self.analyzer._is_abstract_method(f, 5) is True

    def test_regular_method_not_abstract(self, tmp_path: Path) -> None:
        f = _write(
            tmp_path,
            "mod.py",
            """\
            class Concrete:
                def run(self):
                    raise NotImplementedError
        """,
        )
        assert self.analyzer._is_abstract_method(f, 3) is False

    def test_nonexistent_file_returns_false(self, tmp_path: Path) -> None:
        missing = tmp_path / "ghost.py"
        assert self.analyzer._is_abstract_method(missing, 1) is False

    def test_invalid_python_returns_false(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "bad.py", "def (:\n    pass\n")
        assert self.analyzer._is_abstract_method(f, 2) is False

    def test_abstractmethod_attribute_form(self, tmp_path: Path) -> None:
        """abc.abstractmethod decorator (attribute form) should be recognised."""
        f = _write(
            tmp_path,
            "mod.py",
            """\
            import abc

            class Base:
                @abc.abstractmethod
                def run(self):
                    raise NotImplementedError
        """,
        )
        assert self.analyzer._is_abstract_method(f, 6) is True

    def test_abc_attribute_base(self, tmp_path: Path) -> None:
        """abc.ABC base class (attribute form) should be recognised."""
        f = _write(
            tmp_path,
            "mod.py",
            """\
            import abc

            class Base(abc.ABC):
                def run(self):
                    raise NotImplementedError
        """,
        )
        assert self.analyzer._is_abstract_method(f, 5) is True

    def test_standalone_function_with_abstractmethod(self, tmp_path: Path) -> None:
        """Standalone function decorated with @abstractmethod is recognised."""
        f = _write(
            tmp_path,
            "mod.py",
            """\
            from abc import abstractmethod

            @abstractmethod
            def standalone():
                raise NotImplementedError
        """,
        )
        assert self.analyzer._is_abstract_method(f, 5) is True


# ---------------------------------------------------------------------------
# find_stubs (module-level convenience function)
# ---------------------------------------------------------------------------


class TestFindStubs:
    """Tests for the find_stubs convenience function."""

    def test_returns_list(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        src.mkdir()
        result = find_stubs(source_dirs=[src])
        assert isinstance(result, list)

    def test_finds_todo(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        src.mkdir()
        _write(src, "m.py", "# TODO: from find_stubs\n")
        stubs = find_stubs(source_dirs=[src])
        assert len(stubs) == 1, "Stubs must not be empty"
        assert stubs[0].stub_type == "TODO", "stub_type is not valid"

    def test_no_stubs_in_empty_dir(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        src.mkdir()
        assert find_stubs(source_dirs=[src]) == [], "Condition must be true"


# ---------------------------------------------------------------------------
# prioritize_stubs
# ---------------------------------------------------------------------------


class TestPrioritizeStubs:
    """Tests for the prioritize_stubs function."""

    def _stubs(self, tmp_path: Path) -> list[StubInfo]:
        fp = tmp_path / "x.py"
        return [
            StubInfo(fp, 3, "TODO", "p2", "P2"),
            StubInfo(fp, 1, "FIXME", "p0", "P0"),
            StubInfo(fp, 2, "TODO", "p1", "P1"),
        ]

    def test_p0_first(self, tmp_path: Path) -> None:
        result = prioritize_stubs(self._stubs(tmp_path))
        assert result[0].priority == "P0", "Result must not be empty"

    def test_p2_last(self, tmp_path: Path) -> None:
        result = prioritize_stubs(self._stubs(tmp_path))
        assert result[-1].priority == "P2", "Result must not be empty"

    def test_order_p0_p1_p2(self, tmp_path: Path) -> None:
        result = prioritize_stubs(self._stubs(tmp_path))
        priorities = [s.priority for s in result]
        assert priorities == ["P0", "P1", "P2"]

    def test_empty_input(self) -> None:
        assert prioritize_stubs([]) == [], "pri is not valid"

    def test_same_priority_sorted_by_file_then_line(self, tmp_path: Path) -> None:
        fp_a = tmp_path / "a.py"
        fp_b = tmp_path / "b.py"
        stubs = [
            StubInfo(fp_b, 5, "TODO", "b5", "P1"),
            StubInfo(fp_a, 10, "TODO", "a10", "P1"),
            StubInfo(fp_a, 3, "TODO", "a3", "P1"),
        ]
        result = prioritize_stubs(stubs)
        assert result[0].line_number == 3, "Result must not be empty"
        assert result[1].line_number == 10, "Result must not be empty"
        assert result[2].line_number == 5, "Result must not be empty"

    def test_unknown_priority_sorted_last(self, tmp_path: Path) -> None:
        fp = tmp_path / "x.py"
        stubs = [
            StubInfo(fp, 1, "TODO", "x", "P3"),  # unknown priority
            StubInfo(fp, 2, "TODO", "y", "P0"),
        ]
        result = prioritize_stubs(stubs)
        assert result[0].priority == "P0", "Result must not be empty"

    def test_does_not_mutate_input(self, tmp_path: Path) -> None:
        original = self._stubs(tmp_path)
        original_order = [s.priority for s in original]
        prioritize_stubs(original)
        assert [s.priority for s in original] == original_order, "Condition must be true"


# ---------------------------------------------------------------------------
# generate_stub_report
# ---------------------------------------------------------------------------


class TestGenerateStubReport:
    """Tests for generate_stub_report."""

    def test_creates_report_file(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        src.mkdir()
        out = tmp_path / "reports" / "stub_report.md"
        generate_stub_report(output_path=out, source_dirs=[src])
        assert out.exists(), "Condition must be true"

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        src.mkdir()
        out = tmp_path / "deep" / "nested" / "report.md"
        generate_stub_report(output_path=out, source_dirs=[src])
        assert out.exists(), "Condition must be true"

    def test_report_contains_header(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        src.mkdir()
        out = tmp_path / "report.md"
        generate_stub_report(output_path=out, source_dirs=[src])
        content = out.read_text(encoding="utf-8")
        assert "Stub Analysis Report" in content, "Condition must be true"

    def test_report_contains_summary_sections(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        src.mkdir()
        out = tmp_path / "report.md"
        generate_stub_report(output_path=out, source_dirs=[src])
        content = out.read_text(encoding="utf-8")
        assert "Summary by Priority" in content, "Content must not be empty"
        assert "Summary by Type" in content, "Content must not be empty"

    def test_report_lists_stubs(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        src.mkdir()
        _write(src, "m.py", "# TODO P0: critical item\n")
        out = tmp_path / "report.md"
        generate_stub_report(output_path=out, source_dirs=[src])
        content = out.read_text(encoding="utf-8")
        assert "TODO" in content, "Content must not be empty"
        assert "critical item" in content, "Content must not be empty"

    def test_report_total_count_correct(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        src.mkdir()
        _write(src, "m.py", "# TODO one\n# FIXME two\n")
        out = tmp_path / "report.md"
        generate_stub_report(output_path=out, source_dirs=[src])
        content = out.read_text(encoding="utf-8")
        assert "Total Stubs**: 2" in content, "Content must not be empty"

    def test_report_accepts_string_path(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        src.mkdir()
        out = str(tmp_path / "report.md")
        generate_stub_report(output_path=out, source_dirs=[src])
        assert Path(out).exists(), "Condition must be true"

    def test_report_no_stubs_empty_section(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        src.mkdir()
        out = tmp_path / "report.md"
        generate_stub_report(output_path=out, source_dirs=[src])
        content = out.read_text(encoding="utf-8")
        assert "Total Stubs**: 0" in content, "Content must not be empty"

    def test_report_priority_sections_for_populated(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        src.mkdir()
        _write(src, "m.py", "# TODO P0: blocker\n# TODO: normal\n")
        out = tmp_path / "report.md"
        generate_stub_report(output_path=out, source_dirs=[src])
        content = out.read_text(encoding="utf-8")
        assert "P0 Priority" in content, "Content must not be empty"
        assert "P2 Priority" in content, "Content must not be empty"
