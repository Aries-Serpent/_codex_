"""Behavioral regression tests for stable ML sharding and the unit-only gate."""

from __future__ import annotations

import json
from html import escape
from pathlib import Path

import coverage
import pytest
from defusedxml import ElementTree as ET

from scripts.ci import ml_pytest_shards as shards
from scripts.ci.ml_slow_aggregate import aggregate, junit_summary, validate_selections

pytest_plugins = ["pytester"]


@pytest.fixture(autouse=True)
def _default_subprocess_cwd():
    """Keep pytester subprocesses in their isolated temporary directory."""


@pytest.mark.parametrize("count,index", [(0, 1), (2, 3)])
def test_invalid_shard_configuration_fails_collection(pytester, count, index):
    pytester.makepyfile(
        ml_pytest_shards=Path(shards.__file__).read_text(), test_example="def test_ok(): pass"
    )
    result = pytester.runpytest_subprocess(
        "-p", "ml_pytest_shards", f"--ml-shards={count}", f"--ml-shard={index}"
    )
    assert result.ret == pytest.ExitCode.USAGE_ERROR


def test_shards_preserve_marker_selection_across_random_seeds(pytester):
    source = Path(shards.__file__).read_text()
    pytester.makepyfile(ml_pytest_shards=source)
    pytester.makeini("[pytest]\nmarkers =\n integration\n slow\n")
    for index in range(20):
        pytester.makepyfile(**{f"test_file_{index}": """
import pytest
def test_unit(): pass
@pytest.mark.integration
def test_integration(): pass
@pytest.mark.slow
def test_slow(): pass
"""})
    for marker, count, suffix in (
        ("integration", 4, "::test_integration"),
        ("not slow and not integration", 4, "::test_unit"),
    ):
        all_selected = []
        digests = set()
        for index in range(1, count + 1):
            report = pytester.path / f"selection-{index}.json"
            result = pytester.runpytest_subprocess(
                "-p",
                "ml_pytest_shards",
                "-p",
                "pytest_randomly",
                "-m",
                marker,
                f"--ml-shards={count}",
                f"--ml-shard={index}",
                f"--ml-shard-report={report}",
                f"--randomly-seed={index * 37}",
                "--collect-only",
                "-q",
            )
            assert result.ret in (0, 5)
            manifest = json.loads(report.read_text())
            digests.add(manifest["collection_digest"])
            all_selected.extend(manifest["selected"])
        assert len(digests) == 1
        assert set(all_selected) == {f"test_file_{index}.py{suffix}" for index in range(20)}
        assert len(all_selected) == len(set(all_selected))


def make_reports(root: Path) -> None:
    for folder, prefix, count, marker, arg in (
        ("integration", "int-junit", 4, "integration", "tests/integration/"),
        ("unit", "unit-cov", 4, "not slow and not integration", "tests/"),
    ):
        nodeids = [f"{arg}test_{index}.py::test_example" for index in range(8)]
        for index in range(1, count + 1):
            directory = root / folder / f"{prefix}-{index}"
            directory.mkdir(parents=True)
            selected = [nodeid for nodeid in nodeids if shards.file_shard(nodeid, count) == index]
            (directory / "selection.json").write_text(
                json.dumps(
                    {
                        "shard": index,
                        "shards": count,
                        "args": [arg],
                        "marker": marker,
                        "keyword": "",
                        "eligible_count": len(nodeids),
                        "collection_digest": shards.collection_digest(nodeids),
                        "selected": selected,
                        "context": shards.execution_context(),
                        "collect_only": False,
                        "exitstatus": 0,
                    }
                )
            )
            suite = ET.fromstring("<testsuite/>")
            for case, nodeid in enumerate(selected):
                suite.append(
                    ET.fromstring(
                        f'<testcase classname="fixture" name="example-{case}">'
                        '<properties><property name="codex_ml_nodeid" '
                        f'value="{escape(nodeid, quote=True)}"/></properties></testcase>'
                    )
                )
            (directory / "junit.xml").write_text(ET.tostring(suite, encoding="unicode"))


@pytest.mark.parametrize(
    "damage",
    [
        "missing",
        "marker",
        "overlap",
        "digest",
        "GITHUB_REPOSITORY",
        "GITHUB_SHA",
        "GITHUB_RUN_ID",
        "GITHUB_RUN_ATTEMPT",
        "collect-only",
        "unfinished",
        "failed-producer",
        "empty-collection",
        "unexpected-shard",
        "boolean-status",
    ],
)
def test_selection_evidence_rejects_missing_changed_or_overlapping_shards(tmp_path, damage):
    make_reports(tmp_path)
    report = tmp_path / "unit/unit-cov-1/selection.json"
    if damage == "missing":
        report.unlink()
    elif damage == "unexpected-shard":
        (tmp_path / "unit/unit-cov-5").mkdir()
    elif damage == "empty-collection":
        for path in (tmp_path / "unit").glob("*/selection.json"):
            manifest = json.loads(path.read_text())
            manifest.update(
                eligible_count=0, selected=[], collection_digest=shards.collection_digest([])
            )
            path.write_text(json.dumps(manifest))
    else:
        manifest = json.loads(report.read_text())
        if damage == "marker":
            manifest["marker"] = "integration"
        elif damage == "overlap":
            manifest["selected"] *= 2
        elif damage.startswith("GITHUB_"):
            manifest["context"][damage] = "another-execution"
        elif damage == "collect-only":
            manifest["collect_only"] = True
        elif damage == "unfinished":
            manifest["exitstatus"] = None
        elif damage == "failed-producer":
            manifest["exitstatus"] = 1
        elif damage == "boolean-status":
            manifest["exitstatus"] = False
        else:
            manifest["collection_digest"] = "different"
        report.write_text(json.dumps(manifest))
    with pytest.raises((OSError, ValueError)):
        validate_selections(
            tmp_path / "unit", "unit-cov", 4, "not slow and not integration", "tests"
        )


def test_hosted_selection_rejects_missing_execution_context(tmp_path, monkeypatch):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    for key in shards.execution_context():
        monkeypatch.setenv(key, "expected")
    make_reports(tmp_path)
    monkeypatch.delenv("GITHUB_RUN_ATTEMPT")
    with pytest.raises(ValueError, match="Incomplete hosted ML execution context"):
        validate_selections(
            tmp_path / "unit", "unit-cov", 4, "not slow and not integration", "tests"
        )


def test_junit_failures_are_merged_and_escaped(tmp_path):
    directory = tmp_path / "integration"
    directory.mkdir()
    (directory / "report.xml").write_text(
        '<testsuites><testsuite><testcase classname="a" name="b">'
        "<failure>&lt;script&gt;bad&lt;/script&gt;</failure>"
        '</testcase><testcase name="skip"><skipped/></testcase></testsuite></testsuites>'
    )
    summary, failed = junit_summary(directory, "integration")
    assert failed is True
    assert "Tests: 2; failures/errors: 1; skipped: 1" in summary
    assert "&lt;script&gt;bad&lt;/script&gt;" in summary
    assert (tmp_path / "integration-merged.xml").is_file()


def test_aggregate_rejects_junit_dtd(tmp_path):
    make_reports(tmp_path)
    report = tmp_path / "unit/unit-cov-1/junit.xml"
    report.write_text(
        '<!DOCTYPE testsuite [<!ENTITY x SYSTEM "file:///nonexistent">]>'
        "<testsuite><testcase name='bad'>&x;</testcase></testsuite>"
    )
    needs = {
        name: {"result": "success"}
        for name in ("test-ml-components", "integration-shard", "coverage-shard")
    }

    summary, exit_code = aggregate(tmp_path, needs)

    assert exit_code == 1
    assert "Forbidden" in summary


def test_module_collection_skips_are_not_duplicate_selected_tests(pytester):
    pytester.makepyfile(ml_pytest_shards=Path(shards.__file__).read_text())
    directory = pytester.path / "tests"
    directory.mkdir()
    (directory / "test_unavailable.py").write_text(
        'import pytest\npytest.skip("optional dependency unavailable", allow_module_level=True)\n'
    )
    for index in range(8):
        (directory / f"test_file_{index}.py").write_text(
            "import pytest\n"
            "@pytest.mark.parametrize('value', ['a&b'], ids=['special::value.[x]'])\n"
            "def test_ok(value): assert value == 'a&b'\n"
        )
    reports = pytester.path / "reports"
    for index in (1, 2):
        report = reports / f"unit-cov-{index}"
        result = pytester.runpytest_subprocess(
            "tests",
            "-p",
            "ml_pytest_shards",
            "-m",
            "not slow and not integration",
            "--ml-shards=2",
            f"--ml-shard={index}",
            f"--ml-shard-report={report / 'selection.json'}",
            f"--junitxml={report / 'junit.xml'}",
        )
        assert result.ret == 0
        manifest = json.loads((report / "selection.json").read_text())
        cases = list(ET.parse(report / "junit.xml").getroot().iter("testcase"))
        assert len(cases) == len(manifest["selected"]) + 1
        reported = []
        for case in cases:
            property_ = case.find("./properties/property[@name='codex_ml_nodeid']")
            if property_ is not None:
                reported.append(property_.get("value"))
        assert sorted(reported) == sorted(manifest["selected"])
    validate_selections(reports, "unit-cov", 2, "not slow and not integration", "tests")
    summary, failed = junit_summary(reports, "unit")
    assert failed is False
    assert "Tests: 9; failures/errors: 0; skipped: 1" in summary


@pytest.mark.parametrize("phase", ["test-abort", "collection"])
def test_failure_summary_survives_without_final_junit(pytester, monkeypatch, phase):
    pytester.makepyfile(ml_pytest_shards=Path(shards.__file__).read_text())
    if phase == "collection":
        pytester.makepyfile(test_error='raise RuntimeError("<collection error>")')
        expected = pytest.ExitCode.INTERRUPTED
    else:
        pytester.makepyfile(test_error="""
import os
def test_1_failure():
    assert False, "<test failure>"
def test_2_abort():
    os._exit(3)
""")
        expected = pytest.ExitCode.INTERNAL_ERROR
    summary = pytester.path / "summary.md"
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary))
    result = pytester.runpytest_subprocess(
        "-p",
        "ml_pytest_shards",
        "-p",
        "no:randomly",
        "--ml-shard-report=selection.json",
        "--junitxml=report.xml",
    )
    assert result.ret == expected
    text = summary.read_text()
    assert "ML shard failures (reported as tests finish)" in text
    assert (
        "&lt;collection error&gt;" in text
        if phase == "collection"
        else "&lt;test failure&gt;" in text
    )
    if phase == "test-abort":
        assert not (pytester.path / "report.xml").exists()
        assert json.loads((pytester.path / "selection.json").read_text())["exitstatus"] is None


def write_coverage(path: Path, source: Path, lines: range) -> None:
    data = coverage.CoverageData(basename=str(path), suffix=False)
    data.add_lines({str(source): {line + 1 for line in lines}})
    data.write()


@pytest.mark.parametrize(
    ("unit_lines", "job_result", "expected"),
    [
        (range(0, 8), "success", 0),
        (range(0, 4), "success", 1),
        (range(0, 8), "failure", 1),
        (range(0, 8), "cancelled", 1),
        (range(0, 8), "skipped", 1),
        (range(0, 8), "junit-error", 1),
        (range(0, 8), "junit-substitution", 1),
        (range(0, 8), "junit-duplicate", 1),
        (range(0, 8), "junit-missing-id", 1),
        (range(0, 8), "junit-ambiguous-id", 1),
        (range(0, 8), "collection-skip", 0),
        (range(0, 8), "collection-skip-missing-test", 1),
        (range(0, 8), "collection-error", 1),
    ],
)
def test_gate_combines_only_unit_data_and_never_masks_shard_failure(
    tmp_path, monkeypatch, unit_lines, job_result, expected
):
    monkeypatch.chdir(tmp_path)
    reports = tmp_path / "reports"
    make_reports(reports)
    source = tmp_path / "sample.py"
    source.write_text("\n".join(f"x = {i}" for i in range(10)) + "\n")
    for index in range(1, 5):
        shard_lines = range(
            unit_lines.start + (index - 1) * len(unit_lines) // 4,
            unit_lines.start + index * len(unit_lines) // 4,
        )
        write_coverage(
            reports / "unit" / f"unit-cov-{index}" / f".coverage.unit-{index}", source, shard_lines
        )
    # A complete integration data file must never increase the gated percentage.
    write_coverage(reports / "integration/int-junit-1/.coverage.integration", source, range(0, 10))
    needs = {
        name: {"result": "success"}
        for name in ("test-ml-components", "integration-shard", "coverage-shard")
    }
    if job_result.startswith("collection-"):
        for report in reports.rglob("junit.xml"):
            suite = ET.parse(report).getroot()
            if job_result == "collection-skip-missing-test" and report.parent.name == "unit-cov-1":
                first = suite.find("testcase")
                assert first is not None
                suite.remove(first)
            case = ET.fromstring('<testcase classname="" name="missing.module"/>')
            suite.append(case)
            if job_result == "collection-error":
                case.append(ET.fromstring("<error>collection failed</error>"))
            else:
                case.append(
                    ET.fromstring('<skipped message="collection skipped">module skipped</skipped>')
                )
            report.write_text(ET.tostring(suite, encoding="unicode"))
    elif job_result.startswith("junit-"):
        report = next(
            path
            for path in (reports / "unit").glob("*/junit.xml")
            if len(ET.parse(path).getroot().findall("testcase")) >= 2
        )
        suite = ET.parse(report).getroot()
        first = suite.find("testcase")
        assert first is not None
        properties = first.find("properties")
        assert properties is not None
        nodeid = properties.find("property")
        assert nodeid is not None
        value = nodeid.get("value")
        assert value is not None
        if job_result == "junit-error":
            first.append(ET.fromstring("<error>fixture failed</error>"))
        elif job_result == "junit-substitution":
            nodeid.set("value", "tests/substituted.py::test_other")
        elif job_result == "junit-duplicate":
            second = suite.findall("testcase")[1].find("./properties/property")
            assert second is not None
            second.set("value", value)
        elif job_result == "junit-missing-id":
            first.remove(properties)
        else:
            properties.append(ET.fromstring(ET.tostring(nodeid, encoding="unicode")))
        report.write_text(ET.tostring(suite, encoding="unicode"))
    else:
        needs["integration-shard"]["result"] = job_result
    summary, exit_code = aggregate(reports, needs)
    assert exit_code == expected, summary
    assert "coverage report" in summary
    assert (tmp_path / "htmlcov/index.html").is_file(), summary
    if job_result == "collection-skip":
        assert "Tests: 9; failures/errors: 0; skipped: 1" in summary
    elif job_result == "collection-skip-missing-test":
        assert "incomplete JUnit report" in summary
    combined = coverage.Coverage(
        data_file=str(tmp_path / ".coverage.ml-unit-combined"), config_file=False
    )
    combined.load()
    assert set(combined.get_data().lines(str(source))) == {index + 1 for index in unit_lines}


@pytest.mark.parametrize("missing", [1, 2, 3, 4])
def test_missing_unit_coverage_fails_even_with_green_needs(tmp_path, missing):
    make_reports(tmp_path)
    source = tmp_path / "sample.py"
    source.write_text("\n".join(f"x = {i}" for i in range(10)) + "\n")
    for index in range(1, 5):
        write_coverage(
            tmp_path / "unit" / f"unit-cov-{index}" / f".coverage.unit-{index}",
            source,
            range(8),
        )
    (tmp_path / "unit" / f"unit-cov-{missing}" / f".coverage.unit-{missing}").unlink()
    needs = {
        name: {"result": "success"}
        for name in ("test-ml-components", "integration-shard", "coverage-shard")
    }
    summary, exit_code = aggregate(tmp_path, needs)
    assert exit_code == 1
    assert "missing unit shard data" in summary
