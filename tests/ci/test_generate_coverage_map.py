from pathlib import Path

#         assert not set(entry.covered_lines) & set(, "Condition must be true"
#             entry.uncovered_lines
#         ), "A line must not appear in both covered and uncovered"
#     def test_extension_stripped(self):
#         result = _file_to_module("src/codex/foo/bar.py")
#         assert not result.endswith(".py"), "Result must not be empty"
#         assert result == "codex.foo.bar", "Result must not be empty"
#     length validation
#   - FunctionEntry.sufficient_coverage semantics (≥50% executable lines)
#   - pr_delta regression detection (covered→uncovered transition)
# 
# 
# Thread [7] (pullrequestreview-4033687302): the PR added generate_coverage_map.py
# with non-trivial behaviours but no unit tests.  These tests prevent regressions.
#     """Write coverage XML to a temp file and return the path."""
#     p = tmp_path / "coverage.xml"
#     p.write_text(textwrap.dedent(content))
#     return p
# <coverage version="7.4.0" timestamp="1743000000" lines-valid="6"
#           lines-covered="4" line-rate="0.666" branches-covered="0"
#           branches-valid="0" branch-rate="0.0" complexity="0">
#     <packages>
#         <package name="codex" line-rate="0.666" branch-rate="0.0">
#             <classes>
#                 <class name="utils.py" filename="src/codex/utils.py"
#                        line-rate="0.5" branch-rate="0.0">
#                     <lines>
#                         <line number="1" hits="1"/>
#                         <line number="2" hits="0"/>
#                     </lines>
#                 </class>
#                 <class name="utils.py" filename="src/codex/utils.py"
#                        line-rate="1.0" branch-rate="0.0">
#                     <lines>
#                         <line number="2" hits="1"/>
#                         <line number="3" hits="1"/>
#                     </lines>
#                 </class>
#             </classes>
#         </package>
#     </packages>
# </coverage>
# # ---------------------------------------------------------------------------
# # parse_coverage_xml — basic parsing
# # ---------------------------------------------------------------------------
# # ---------------------------------------------------------------------------
# # parse_coverage_xml — basic parsing
# # ---------------------------------------------------------------------------
# 
# 
# 
# 
# class TestParseCoverageXml:
#     def test_returns_module_entry(self, tmp_path):
#         xml = _write_coverage_xml(
#             tmp_path,
#             _minimal_xml("src/codex/utils.py", 0.8, [1, 2, 3, 4], [5]),
#         )
#         result = parse_coverage_xml(xml, suite_name="unit")
#         assert "codex.utils" in result, "Result must not be empty"
#         entry = result["codex.utils"]
#         assert entry.line_rate == pytest.approx(0.8), "line_rate is not valid"
#         assert entry.suite == "unit", "suite is not valid"
#         assert 1 in entry.covered_lines, "Condition must be true"
#         assert 5 in entry.uncovered_lines, "Condition must be true"
#     return f"""\
# <?xml version="1.0" ?>
# <coverage version="7.4.0" timestamp="1743000000" lines-valid="10"
#           lines-covered="{len(covered_lines)}" line-rate="{line_rate}"
#           branches-covered="0" branches-valid="0" branch-rate="{branch_rate}"
#           complexity="0">
#     <packages>
#         <package name="codex" line-rate="{line_rate}" branch-rate="{branch_rate}">
#             <classes>
#                 <class name="{Path(filename).name}" filename="{filename}"
#                        line-rate="{line_rate}" branch-rate="{branch_rate}">
#                     <lines>
# {lines_xml}                    </lines>
#                 </class>
#             </classes>
#         </package>
#     </packages>
# </coverage>
#     def test_duplicate_module_union_in_single_xml(self, tmp_path):
# """
#         assert not set(entry.covered_lines) & set(, "Condition must be true"
#             entry.uncovered_lines
#         ), "A line must not appear in both covered and uncovered"
# # ---------------------------------------------------------------------------
# 
# 
# 
# # ---------------------------------------------------------------------------
# # build_coverage_map — multi-suite merge
# # ---------------------------------------------------------------------------
# 
# 
# class TestBuildCoverageMap:
#     def test_single_suite(self, tmp_path):
#         xml = _write_coverage_xml(
#             tmp_path,
#             _minimal_xml("src/codex/cli.py", 0.75, [1, 2, 3], [4]),
#         )
#         result = build_coverage_map([xml], suite_names=["unit"], git_sha="abc123")
#         assert "codex.cli" in result["modules"], "Result must not be empty"
#         mod = result["modules"]["codex.cli"]
#         assert mod["line_rate"] == pytest.approx(0.75), "Condition must be true"
#         assert _file_to_module("src/codex/a/b/c/d.py") == "codex.a.b.c.d", "Condition must be true"
#         # No line should appear in both covered and uncovered
#         assert not set(entry.covered_lines) & set(, "Condition must be true"
#             entry.uncovered_lines
#         ), "A line must not appear in both covered and uncovered"
#         # Lines 1, 2, 3 were covered by at least one suite
#         assert 1 in covered, "Condition must be true"
#         assert 2 in covered, "Condition must be true"
#         assert 3 in covered, "Condition must be true"
#         # Line 4 was never covered
#         assert 4 in uncovered, "Condition must be true"
#         # No overlap
#         assert not covered & uncovered, "Condition must be true"
#         )
#         result = parse_coverage_xml(xml, suite_name="unit")
#         assert "codex.utils" in result, "Result must not be empty"
#         entry = result["codex.utils"]
#         assert entry.line_rate == pytest.approx(0.8), "line_rate is not valid"
#         assert entry.suite == "unit", "suite is not valid"
#         assert 1 in entry.covered_lines, "Condition must be true"
#         assert 5 in entry.uncovered_lines, "Condition must be true"
# 
#     def test_absolute_filename_normalised(self, tmp_path):
#     def test_absolute_filename_normalised(self, tmp_path):
#         """Absolute filename in coverage.xml must be normalised to repo-relative path."""
#         abs_filename = str(get_repo_root() / "src/codex/utils.py")
#         xml = _write_coverage_xml(
#             tmp_path,
#             _minimal_xml(abs_filename, 0.5, [1], [2]),
#         )
#         result = parse_coverage_xml(xml, suite_name="ci")
#         # Should resolve to "codex.utils", NOT contain filesystem root
#         assert any("codex.utils" in k for k in result), f"Keys: {list(result.keys())}"
#         for key in result:
#             assert not key.startswith("/"), f"Module key must not be absolute: {key}"
#     def test_duplicate_module_union_in_single_xml(self, tmp_path):
#     def test_duplicate_module_union_in_single_xml(self, tmp_path):
#         """Two <class> entries for the same module in one XML → lines unioned, not discarded."""
#         xml_content = """\
# <?xml version="1.0" ?>
# <coverage version="7.4.0" timestamp="1743000000" lines-valid="6"
#           lines-covered="4" line-rate="0.666" branches-covered="0"
#           branches-valid="0" branch-rate="0.0" complexity="0">
#     <packages>
#         <package name="codex" line-rate="0.666" branch-rate="0.0">
#             <classes>
#                 <class name="utils.py" filename="src/codex/utils.py"
#                        line-rate="0.5" branch-rate="0.0">
#                     <lines>
#                         <line number="1" hits="1"/>
#                         <line number="2" hits="0"/>
#                     </lines>
#                 </class>
#                 <class name="utils.py" filename="src/codex/utils.py"
#                        line-rate="1.0" branch-rate="0.0">
#                     <lines>
#                         <line number="2" hits="1"/>
#                         <line number="3" hits="1"/>
#                     </lines>
#                 </class>
#             </classes>
#         </package>
#     </packages>
# </coverage>
#         reflect the merged line data — Thread [4] regression guard."""
#         xml1 = tmp_path / "x.xml"
#         xml2 = tmp_path / "y.xml"
#         xml1.write_text(_minimal_xml("src/codex/cli.py", 0.5, [1, 2], [3, 4]))
#         xml2.write_text(_minimal_xml("src/codex/cli.py", 0.5, [3, 4], [1, 2]))
#         result = build_coverage_map([xml1, xml2], suite_names=["x", "y"])
#         mod = result["modules"]["codex.cli"]
#         # Function lists must exist (may be empty if AST annotation not run on tmp file,
#         # but must not be None)
#         assert "covered_functions" in mod, "Condition must be true"
#         assert "uncovered_functions" in mod, "Condition must be true"
#         assert isinstance(mod["covered_functions"], list)
#         assert isinstance(mod["uncovered_functions"], list)
#         assert 2 in covered, "Condition must be true"
#         assert 3 in covered, "Condition must be true"
#         # Line 4 was never covered
#         assert 4 in uncovered, "Condition must be true"
#         # No overlap
#         assert not covered & uncovered, "Condition must be true"
#     def test_single_suite(self, tmp_path):
#         xml = _write_coverage_xml(
#             tmp_path,
#             _minimal_xml("src/codex/cli.py", 0.75, [1, 2, 3], [4]),
#         )
#         result = build_coverage_map([xml], suite_names=["unit"], git_sha="abc123")
#         assert "codex.cli" in result["modules"], "Result must not be empty"
#         mod = result["modules"]["codex.cli"]
#         assert mod["line_rate"] == pytest.approx(0.75), "Condition must be true"
# 
#     def test_multi_suite_union(self, tmp_path):
#     def test_multi_suite_union(self, tmp_path):
#         """Lines covered by ANY suite appear in the merged covered set."""
#         xml1 = tmp_path / "cov1.xml"
#         xml2 = tmp_path / "cov2.xml"
#         xml1.write_text(_minimal_xml("src/codex/cli.py", 0.5, [1, 2], [3, 4]))
#         xml2.write_text(_minimal_xml("src/codex/cli.py", 0.75, [1, 3], [2, 4]))
#         result = build_coverage_map([xml1, xml2], suite_names=["unit", "integration"])
#         mod = result["modules"]["codex.cli"]
#         covered = set(mod["covered_lines"])
#         uncovered = set(mod["uncovered_lines"])
#         # Lines 1, 2, 3 were covered by at least one suite
#         assert 1 in covered, "Condition must be true"
#         assert 2 in covered, "Condition must be true"
#         assert 3 in covered, "Condition must be true"
#         # Line 4 was never covered
#         assert 4 in uncovered, "Condition must be true"
#         # No overlap
#         assert not covered & uncovered, "Condition must be true"
#     def test_suite_names_length_mismatch_raises(self, tmp_path):
#         xml = _write_coverage_xml(
#             tmp_path,
#             _minimal_xml("src/codex/utils.py", 1.0, [1, 2], []),
#         )
#         with pytest.raises(ValueError, match="same length"):
#             build_coverage_map([xml], suite_names=["a", "b"])
# 
#     def test_merged_suite_tag(self, tmp_path):
#     def test_merged_suite_tag(self, tmp_path):
#         """Multi-suite merge tags the module entry with '+merged'."""
#         xml1 = tmp_path / "a.xml"
#         xml2 = tmp_path / "b.xml"
#         xml1.write_text(_minimal_xml("src/codex/cli.py", 0.5, [1], [2]))
#         xml2.write_text(_minimal_xml("src/codex/cli.py", 0.5, [2], [1]))
#         result = build_coverage_map([xml1, xml2], suite_names=["s1", "s2"])
#         mod = result["modules"]["codex.cli"]
#         assert "+merged" in mod["suite"], "Condition must be true"
#     def test_function_coverage_consistent_with_merged_lines(self, tmp_path):
#     def test_function_coverage_consistent_with_merged_lines(self, tmp_path):
#         """After multi-suite merge, covered_functions / uncovered_functions must
#         reflect the merged line data — Thread [4] regression guard."""
#         xml1 = tmp_path / "x.xml"
#         xml2 = tmp_path / "y.xml"
#         xml1.write_text(_minimal_xml("src/codex/cli.py", 0.5, [1, 2], [3, 4]))
#         xml2.write_text(_minimal_xml("src/codex/cli.py", 0.5, [3, 4], [1, 2]))
#         result = build_coverage_map([xml1, xml2], suite_names=["x", "y"])
#         mod = result["modules"]["codex.cli"]
#         # Function lists must exist (may be empty if AST annotation not run on tmp file,
#         # but must not be None)
#         assert "covered_functions" in mod, "Condition must be true"
#         assert "uncovered_functions" in mod, "Condition must be true"
#         assert isinstance(mod["covered_functions"], list)
#         assert isinstance(mod["uncovered_functions"], list)
#         assert not hasattr(, "Condition must be true"
#             FunctionEntry(name="f", start_line=1, end_line=5, sufficient_coverage=False),
# # ---------------------------------------------------------------------------
# # FunctionEntry.sufficient_coverage semantics
# # ---------------------------------------------------------------------------
#         assert not hasattr(, "Condition must be true"
#             FunctionEntry(name="f", start_line=1, end_line=5, sufficient_coverage=False),
# class TestFunctionEntrySufficientCoverage:
#     def test_sufficient_coverage_true_when_majority_hit(self):
#         fn = FunctionEntry(
#             name="my_func",
#             start_line=10,
#             end_line=20,
#             sufficient_coverage=True,
#         )
#         assert fn.sufficient_coverage is True, "sufficient_coverage is not valid"
#     def test_sufficient_coverage_false_when_low_hit(self):
#         fn = FunctionEntry(
#             name="my_func",
#             start_line=10,
#             end_line=20,
#             sufficient_coverage=False,
#         )
#         assert fn.sufficient_coverage is False, "sufficient_coverage is not valid"
# 
#     def test_field_is_not_named_is_covered(self):
#     def test_field_is_not_named_is_covered(self):
#         """Thread [2] — field was renamed from is_covered to sufficient_coverage
#         to avoid confusion with standard 'any line executed' definition."""
#         assert not hasattr(, "Condition must be true"
#             FunctionEntry(name="f", start_line=1, end_line=5, sufficient_coverage=False),
#             "is_covered",
#         ), "Old field name 'is_covered' must not exist"


# ---------------------------------------------------------------------------
# pr_delta regression detection
# ---------------------------------------------------------------------------


class TestPrDelta:
    """Thread [4] + general regression: pr_delta must flag covered→uncovered transitions."""

    def test_pr_delta_import(self):
        from generate_coverage_map import pr_delta

        assert callable(pr_delta), "Condition must be true"

    def _make_map_json(self, tmp_path: Path, subdir: str, xml_content: str) -> Path:
        """Build a coverage_map.json from XML content and return its path."""
        import json as _json

        d = tmp_path / subdir
        d.mkdir()
        xml_path = _write_coverage_xml(d, xml_content)
        coverage_map = build_coverage_map([xml_path], suite_names=[subdir])
        map_path = d / "coverage_map.json"
        map_path.write_text(_json.dumps(coverage_map))
        return map_path

    def test_pr_delta_returns_int(self, tmp_path):
        from generate_coverage_map import pr_delta

        base_map = self._make_map_json(
            tmp_path, "base", _minimal_xml("src/codex/utils.py", 1.0, [1, 2, 3], [])
        )
        head_map = self._make_map_json(
            tmp_path, "head", _minimal_xml("src/codex/utils.py", 0.66, [1, 2], [3])
        )
        result = pr_delta(base_map, head_map)
        assert isinstance(result, int)

    def test_pr_delta_detects_regression(self, tmp_path):
        import io as _io
        from contextlib import redirect_stdout

        from generate_coverage_map import pr_delta

        base_map = self._make_map_json(
            tmp_path, "base", _minimal_xml("src/codex/utils.py", 1.0, [1, 2, 3], [])
        )
        head_map = self._make_map_json(
            tmp_path, "head", _minimal_xml("src/codex/utils.py", 0.33, [1], [2, 3])
        )
        buf = _io.StringIO()
        with redirect_stdout(buf):
            result = pr_delta(base_map, head_map)
        # Non-zero return code signals regression, OR output mentions regression
        output = buf.getvalue()
        assert (result != 0 or "regress" in output.lower() or "dropped" in output.lower()
        ), f"pr_delta should detect coverage regression. exit={result}, output={output[:200]}"
