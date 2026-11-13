"""Behavioral regression tests for stable ML sharding and the unit-only gate."""

from __future__ import annotations

import json
from pathlib import Path

import coverage
import pytest

from scripts.ci import ml_pytest_shards as shards
from scripts.ci.ml_slow_aggregate import aggregate, junit_summary, validate_selections

pytest_plugins = ["pytester"]


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
        ("not slow and not integration", 2, "::test_unit"),
    ):
        all_selected = []
        digests = set()
        for index in range(1, count + 1):
            report = pytester.path / f"selection-{index}.json"
            result = pytester.runpytest_subprocess(
                "-p",
                "ml_pytest_shards",
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
        ("unit", "unit-cov", 2, "not slow and not integration", "tests/"),
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
                    }
                )
            )
            (directory / "junit.xml").write_text(
                "<testsuite>"
                + "".join(
                    f'<testcase classname="fixture" name="example-{case}"/>'
                    for case in range(len(selected))
                )
                + "</testsuite>"
            )


@pytest.mark.parametrize("damage", ["missing", "marker", "overlap", "digest"])
def test_selection_evidence_rejects_missing_changed_or_overlapping_shards(tmp_path, damage):
    make_reports(tmp_path)
    report = tmp_path / "unit/unit-cov-1/selection.json"
    if damage == "missing":
        report.unlink()
    else:
        manifest = json.loads(report.read_text())
        if damage == "marker":
            manifest["marker"] = "integration"
        elif damage == "overlap":
            manifest["selected"] *= 2
        else:
            manifest["collection_digest"] = "different"
        report.write_text(json.dumps(manifest))
    with pytest.raises((OSError, ValueError)):
        validate_selections(
            tmp_path / "unit", "unit-cov", 2, "not slow and not integration", "tests"
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


def write_coverage(path: Path, source: Path, lines: range) -> None:
    cov = coverage.Coverage(data_file=str(path), config_file=False, include=[str(source)])
    cov.start()
    exec(compile("\n" * lines.start + "\n".join(f"x = {i}" for i in lines), str(source), "exec"))
    cov.stop()
    cov.save()


@pytest.mark.parametrize(
    ("unit_lines", "job_result", "expected"),
    [
        (range(0, 8), "success", 0),
        (range(0, 4), "success", 1),
        (range(0, 8), "failure", 1),
        (range(0, 8), "cancelled", 1),
        (range(0, 8), "skipped", 1),
        (range(0, 8), "junit-error", 1),
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
    for index in (1, 2):
        midpoint = unit_lines.start + len(unit_lines) // 2
        shard_lines = (
            range(unit_lines.start, midpoint) if index == 1 else range(midpoint, unit_lines.stop)
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
    if job_result == "junit-error":
        report = reports / "unit/unit-cov-1/junit.xml"
        report.write_text(
            report.read_text().replace("/>", "><error>fixture failed</error></testcase>", 1)
        )
    else:
        needs["integration-shard"]["result"] = job_result
    summary, exit_code = aggregate(reports, needs)
    assert exit_code == expected, summary
    assert "coverage report" in summary
    assert (tmp_path / "htmlcov/index.html").is_file()
    combined = coverage.Coverage(
        data_file=str(tmp_path / ".coverage.ml-unit-combined"), config_file=False
    )
    combined.load()
    assert set(combined.get_data().lines(str(source))) == {index + 1 for index in unit_lines}


def test_missing_unit_coverage_fails_even_with_green_needs(tmp_path):
    make_reports(tmp_path)
    needs = {
        name: {"result": "success"}
        for name in ("test-ml-components", "integration-shard", "coverage-shard")
    }
    summary, exit_code = aggregate(tmp_path, needs)
    assert exit_code == 1
    assert "missing unit shard data" in summary
