"""Behavioral regression tests for stable ML sharding and the unit-only gate."""

from __future__ import annotations

import json
import subprocess
import sys
from html import escape
from pathlib import Path

import coverage
import pytest
from defusedxml import ElementTree as ET

from scripts.ci import ml_pytest_shards as shards
from scripts.ci import ml_slow_aggregate
from scripts.ci.ml_slow_aggregate import (
    aggregate,
    junit_summary,
    parse_floor,
    ratchet,
    validate_selections,
)

pytest_plugins = ["pytester"]

FLOOR = {"floor": 70, "target": 70, "measured_sha": "abc1234"}

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


def make_reports(root: Path, quarantine: dict | None = None) -> None:
    quarantine = quarantine or {}
    for folder, prefix, count, marker, arg in (
        ("integration", "int-junit", 4, "integration", "tests/integration/"),
        ("unit", "unit-cov", 4, "not slow and not integration", "tests/"),
    ):
        nodeids = [f"{arg}test_{index}.py::test_example" for index in range(8)]
        for index in range(1, count + 1):
            directory = root / folder / f"{prefix}-{index}"
            directory.mkdir(parents=True)
            selected = [nodeid for nodeid in nodeids if shards.file_shard(nodeid, count) == index]
            extra = {}
            if folder == "unit":
                (directory / "pytest-exit-code").write_text("0\n")
                extra = {
                    "quarantine_digest": shards.quarantine_digest(quarantine),
                    "quarantined": sorted(set(quarantine) & set(selected)),
                    "quarantine_not_selected": sorted(set(quarantine) - set(selected)),
                    "quarantine_results": {},
                }
            (directory / "selection.json").write_text(
                json.dumps(
                    {
                        **extra,
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

    summary, exit_code = aggregate(tmp_path, needs, floor=FLOOR, quarantine={})

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
    summary, exit_code = aggregate(reports, needs, floor=FLOOR, quarantine={})
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
    summary, exit_code = aggregate(tmp_path, needs, floor=FLOOR, quarantine={})
    assert exit_code == 1
    assert "missing unit shard data" in summary


QUARANTINE_TESTS = """
def test_fails():
    assert False, "known failure"
def test_passes():
    pass
"""


def write_manifest(path: Path, nodeids: list[str]) -> Path:
    path.write_text(
        json.dumps(
            {
                "version": 1,
                "entries": [
                    {
                        "nodeid": nodeid,
                        "cluster": "api-drift",
                        "issue": "#5784",
                        "owner": "ml",
                        "reason": "pre-existing",
                        "added_sha": "2865b571ab",
                    }
                    for nodeid in nodeids
                ],
            }
        )
    )
    return path


@pytest.mark.parametrize(
    ("quarantined", "expected"),
    [
        (["test_q.py::test_fails"], pytest.ExitCode.OK),
        (["test_q.py::test_fails", "test_q.py::test_passes"], pytest.ExitCode.TESTS_FAILED),
        ([], pytest.ExitCode.TESTS_FAILED),
    ],
    ids=["quarantined-failure", "quarantined-xpass-strict", "unquarantined-failure"],
)
def test_quarantine_runs_entries_as_strict_xfail(pytester, quarantined, expected):
    pytester.makepyfile(ml_pytest_shards=Path(shards.__file__).read_text(), test_q=QUARANTINE_TESTS)
    manifest = write_manifest(pytester.path / "quarantine.json", quarantined)
    report = pytester.path / "selection.json"
    result = pytester.runpytest_subprocess(
        "test_q.py",
        "-p",
        "ml_pytest_shards",
        "-p",
        "no:randomly",
        f"--ml-quarantine={manifest}",
        f"--ml-shard-report={report}",
        "--junitxml=junit.xml",
    )
    assert result.ret == expected
    selection = json.loads(report.read_text())
    assert selection["quarantined"] == sorted(quarantined)
    assert selection["quarantine_not_selected"] == []
    assert selection["quarantine_results"] == {
        nodeid: "xfailed" if nodeid.endswith("fails") else "xpassed" for nodeid in quarantined
    }
    summary, failed = junit_summary(pytester.path, "unit")
    assert failed is (expected != pytest.ExitCode.OK)
    if quarantined:
        assert "Quarantined (strict xfail): 1." in summary
    if len(quarantined) == 2:
        assert "XPASS(strict)" in (pytester.path / "junit.xml").read_text()


def test_quarantine_never_hides_collection_errors(pytester):
    pytester.makepyfile(
        ml_pytest_shards=Path(shards.__file__).read_text(),
        test_broken='raise ImportError("gone")\ndef test_x(): pass\n',
    )
    manifest = write_manifest(pytester.path / "quarantine.json", ["test_broken.py::test_x"])
    result = pytester.runpytest_subprocess(
        "-p", "ml_pytest_shards", f"--ml-quarantine={manifest}", "--junitxml=junit.xml"
    )
    assert result.ret == pytest.ExitCode.INTERRUPTED
    summary, failed = junit_summary(pytester.path, "unit")
    assert failed is True
    assert "Collection errors (never quarantinable):** 1" in summary
    with pytest.raises(ValueError, match="test item ID"):
        shards.parse_quarantine(
            {"version": 1, "entries": [{**_entry(), "nodeid": "tests/test_broken.py"}]}
        )


def test_invalid_quarantine_is_a_usage_error(pytester):
    pytester.makepyfile(ml_pytest_shards=Path(shards.__file__).read_text(), test_q=QUARANTINE_TESTS)
    (pytester.path / "quarantine.json").write_text('{"version": 1, "entries": [{}]}')
    result = pytester.runpytest_subprocess(
        "-p", "ml_pytest_shards", "--ml-quarantine=quarantine.json"
    )
    assert result.ret == pytest.ExitCode.USAGE_ERROR


def _entry(**changes: object) -> dict:
    return {
        "nodeid": "tests/test_a.py::test_b",
        "cluster": "api-drift",
        "issue": "https://github.com/Aries-Serpent/_codex_/issues/1",
        "owner": "ml",
        "reason": "pre-existing",
        "added_sha": "2865b571ab",
        **changes,
    }


@pytest.mark.parametrize(
    "data",
    [
        {"entries": []},
        {"version": 2, "entries": []},
        {"version": 1, "entries": {}},
        {"version": 1, "entries": [], "extra": 1},
        {"version": 1, "entries": [{k: v for k, v in _entry().items() if k != "owner"}]},
        {"version": 1, "entries": [{**_entry(), "extra": "x"}]},
        {"version": 1, "entries": [_entry(reason=" ")]},
        {"version": 1, "entries": [_entry(issue="issue 12")]},
        {"version": 1, "entries": [_entry(issue="http://example.com/1")]},
        {"version": 1, "entries": [_entry(added_sha="main")]},
        {"version": 1, "entries": [_entry(), _entry()]},
    ],
)
def test_quarantine_schema_violations_are_rejected(data):
    with pytest.raises(ValueError):
        shards.parse_quarantine(data)


def test_committed_baselines_are_valid():
    root = Path(__file__).resolve().parents[2] / ".codex/baselines"
    shards.load_quarantine(root / "ml_unit_quarantine.json")
    assert ml_slow_aggregate.load_floor(root / "ml_unit_coverage_floor.json")["target"] == 70


@pytest.mark.parametrize(
    "data",
    [
        {"floor": 54, "target": 70},
        {"floor": "54", "target": 70, "measured_sha": "abc"},
        {"floor": 71, "target": 70, "measured_sha": "abc"},
        {"floor": True, "target": 70, "measured_sha": "abc"},
        {"floor": 54, "target": 70, "measured_sha": ""},
    ],
)
def test_floor_schema_violations_are_rejected(data):
    with pytest.raises(ValueError):
        parse_floor(data)


def _green_coverage(tmp_path: Path, reports: Path, percent_lines: range) -> dict:
    source = tmp_path / "sample.py"
    source.write_text("\n".join(f"x = {i}" for i in range(10)) + "\n")
    for index in range(1, 5):
        write_coverage(
            reports / "unit" / f"unit-cov-{index}" / f".coverage.unit-{index}",
            source,
            percent_lines if index == 1 else range(0),
        )
    return {
        name: {"result": "success"}
        for name in ("test-ml-components", "integration-shard", "coverage-shard")
    }


@pytest.mark.parametrize(
    ("floor", "expected", "message"),
    [
        (61, 1, "below the floor"),
        (60, 0, "Combined unit coverage: 60.00%"),
        (54, 0, "consider raising floor"),
    ],
)
def test_coverage_floor_ratchet(tmp_path, monkeypatch, floor, expected, message):
    monkeypatch.chdir(tmp_path)
    reports = tmp_path / "reports"
    make_reports(reports)
    needs = _green_coverage(tmp_path, reports, range(0, 6))
    summary, exit_code = aggregate(reports, needs, floor={**FLOOR, "floor": floor}, quarantine={})
    assert exit_code == expected, summary
    assert message in summary
    assert ("consider raising" in summary) is (floor == 54)


@pytest.mark.parametrize(
    ("selected", "expected"), [(True, 0), (False, 1)], ids=["collected", "stale"]
)
def test_quarantine_entries_must_be_collected_by_some_shard(
    tmp_path, monkeypatch, selected, expected
):
    monkeypatch.chdir(tmp_path)
    nodeid = "tests/test_3.py::test_example" if selected else "tests/test_gone.py::test_x"
    quarantine = {nodeid: _entry(nodeid=nodeid)}
    reports = tmp_path / "reports"
    make_reports(reports, quarantine)
    needs = _green_coverage(tmp_path, reports, range(0, 10))
    summary, exit_code = aggregate(reports, needs, floor=FLOOR, quarantine=quarantine)
    assert exit_code == expected, summary
    assert ("Stale quarantine entries" in summary) is not selected
    # Shards that ran without (or with a different) manifest are rejected.
    summary, exit_code = aggregate(reports, needs, floor=FLOOR, quarantine={})
    assert exit_code == 1
    assert "did not apply the quarantine manifest" in summary


@pytest.mark.parametrize("code", ["2", "1", None])
def test_recorded_pytest_exit_code_is_checked(tmp_path, monkeypatch, code):
    monkeypatch.chdir(tmp_path)
    reports = tmp_path / "reports"
    make_reports(reports)
    needs = _green_coverage(tmp_path, reports, range(0, 10))
    exit_file = reports / "unit/unit-cov-2/pytest-exit-code"
    if code is None:
        exit_file.unlink()
    else:
        exit_file.write_text(code)
    summary, exit_code = aggregate(reports, needs, floor=FLOOR, quarantine={})
    assert exit_code == 1
    assert "unit-cov-2: " in summary


def test_summarize_report_only_does_not_gate_test_failures(tmp_path):
    (tmp_path / "junit.xml").write_text(
        '<testsuite><testcase classname="a" name="b"><failure>x</failure></testcase></testsuite>'
    )
    script = Path(ml_slow_aggregate.__file__)
    for extra, expected in (([], 1), (["--report-only"], 0)):
        proc = subprocess.run(
            [sys.executable, str(script), "summarize", "--reports", str(tmp_path), *extra],
            capture_output=True,
            text=True,
            env={"PATH": "", "PYTHONPATH": str(script.parent)},
        )
        assert proc.returncode == expected, proc.stderr


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *args],
        cwd=repo,
        check=True,
        capture_output=True,
    )


@pytest.mark.parametrize(
    ("base", "head", "approved", "expected"),
    [
        (([], 54), (["tests/a.py::t"], 54), False, 1),
        (([], 54), (["tests/a.py::t"], 54), True, 0),
        ((["tests/a.py::t"], 54), ([], 55), False, 0),
        ((["tests/a.py::t"], 54), (["tests/b.py::t"], 54), False, 1),
        (([], 54), ([], 53), False, 1),
        (([], 54), ([], 53), True, 0),
        (None, (["tests/a.py::t"], 40), False, 0),
    ],
    ids=[
        "growth",
        "growth-approved",
        "shrink-raise",
        "swap",
        "floor-down",
        "floor-approved",
        "no-base",
    ],
)
def test_ratchet_against_base(tmp_path, monkeypatch, base, head, approved, expected):
    monkeypatch.chdir(tmp_path)
    if approved:
        monkeypatch.setenv(ml_slow_aggregate.APPROVAL_ENV, "1")
    else:
        monkeypatch.delenv(ml_slow_aggregate.APPROVAL_ENV, raising=False)
    _git(tmp_path, "init", "-q")
    baselines = tmp_path / "baselines"
    baselines.mkdir()
    quarantine, floor = baselines / "q.json", baselines / "floor.json"

    def write(state):
        write_manifest(quarantine, state[0])
        floor.write_text(json.dumps({"floor": state[1], "target": 70, "measured_sha": "abc"}))

    if base is None:
        (tmp_path / "README").write_text("base")
        _git(tmp_path, "add", "README")
    else:
        write(base)
        _git(tmp_path, "add", "baselines")
    _git(tmp_path, "commit", "-q", "-m", "base")
    write(head)
    summary, exit_code = ratchet("HEAD", Path("baselines/q.json"), Path("baselines/floor.json"))
    assert exit_code == expected, summary
    if approved and expected == 0 and base is not None:
        # Push events run with --no-approval: the label/env can never waive the ratchet.
        script = Path(ml_slow_aggregate.__file__)
        proc = subprocess.run(
            [
                sys.executable,
                str(script),
                "ratchet",
                "--no-approval",
                "--base-ref",
                "HEAD",
                "--quarantine",
                "baselines/q.json",
                "--floor-file",
                "baselines/floor.json",
            ],
            capture_output=True,
            text=True,
            env={
                "PATH": "/usr/bin:/bin",
                "PYTHONPATH": str(script.parent),
                ml_slow_aggregate.APPROVAL_ENV: "1",
            },
        )
        assert proc.returncode == 1, proc.stdout + proc.stderr
    with pytest.raises(ValueError, match="not an available commit"):
        ratchet("no-such-ref", Path("baselines/q.json"), Path("baselines/floor.json"))


XFAIL_DECLARING_TESTS = {
    "function": """
import pytest
@pytest.mark.xfail(strict=False, reason="author xfail")
def test_flaky():
    pass
""",
    "module": """
import pytest
pytestmark = pytest.mark.xfail(strict=False, reason="author xfail")
def test_flaky():
    pass
""",
}


@pytest.mark.parametrize("scope", sorted(XFAIL_DECLARING_TESTS))
def test_quarantined_xpass_fails_despite_non_strict_xfail(pytester, tmp_path, monkeypatch, scope):
    pytester.makepyfile(
        ml_pytest_shards=Path(shards.__file__).read_text(),
        test_x=XFAIL_DECLARING_TESTS[scope],
    )
    nodeid = "test_x.py::test_flaky"
    manifest = write_manifest(pytester.path / "quarantine.json", [nodeid])
    report = pytester.path / "selection.json"
    result = pytester.runpytest_subprocess(
        "test_x.py",
        "-p",
        "ml_pytest_shards",
        f"--ml-quarantine={manifest}",
        f"--ml-shard-report={report}",
        "--junitxml=junit.xml",
    )
    assert result.ret == pytest.ExitCode.TESTS_FAILED
    result.assert_outcomes(failed=1)
    assert json.loads(report.read_text())["quarantine_results"] == {nodeid: "xpassed"}
    assert junit_summary(pytester.path, "unit")[1] is True
    # The prepended strict quarantine marker is the one pytest evaluates.
    assert (
        "[XPASS(strict)] quarantined: #5784 api-drift" in (pytester.path / "junit.xml").read_text()
    )

    # The aggregate rejects a recorded XPASS even when JUnit shows a plain pass.
    monkeypatch.chdir(tmp_path)
    unit = "tests/test_3.py::test_example"
    quarantine = {unit: _entry(nodeid=unit)}
    reports = tmp_path / "reports"
    make_reports(reports, quarantine)
    for selection_path in (reports / "unit").glob("unit-cov-*/selection.json"):
        selection = json.loads(selection_path.read_text())
        if unit in selection["quarantined"]:
            selection["quarantine_results"] = {unit: "xpassed"}
            selection_path.write_text(json.dumps(selection))
    needs = _green_coverage(tmp_path, reports, range(0, 10))
    summary, exit_code = aggregate(reports, needs, floor=FLOOR, quarantine=quarantine)
    assert exit_code == 1
    assert "quarantined tests passed (XPASS)" in summary


def test_quarantined_setup_error_stays_an_error(pytester):
    """Fixture errors are not the tracked failure, so quarantine does not absorb them."""
    pytester.makepyfile(
        ml_pytest_shards=Path(shards.__file__).read_text(),
        test_s="""
import pytest
@pytest.fixture
def broken():
    raise RuntimeError("fixture broke")
def test_uses_fixture(broken):
    assert False
""",
    )
    nodeid = "test_s.py::test_uses_fixture"
    manifest = write_manifest(pytester.path / "quarantine.json", [nodeid])
    report = pytester.path / "selection.json"
    result = pytester.runpytest_subprocess(
        "test_s.py",
        "-p",
        "ml_pytest_shards",
        f"--ml-quarantine={manifest}",
        f"--ml-shard-report={report}",
        "--junitxml=junit.xml",
    )
    assert result.ret == pytest.ExitCode.TESTS_FAILED
    result.assert_outcomes(errors=1)
    assert json.loads(report.read_text())["quarantine_results"] == {nodeid: "setup-error"}
    summary, failed = junit_summary(pytester.path, "unit")
    assert failed is True
    assert "failures/errors: 1" in summary
