"""Validate ML shard selections and report unit-only combined coverage."""

from __future__ import annotations

import argparse
import html
import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

if __package__:
    from . import ml_pytest_shards as package_shards

    shards = package_shards
else:
    import ml_pytest_shards as script_shards

    shards = script_shards


def validate_selections(root: Path, prefix: str, count: int, marker: str, path: str) -> None:
    manifests = [
        json.loads((root / f"{prefix}-{index}" / "selection.json").read_text())
        for index in range(1, count + 1)
    ]
    selected: list[str] = []
    for index, manifest in enumerate(manifests, 1):
        if (
            manifest["shard"] != index
            or manifest["shards"] != count
            or manifest["marker"] != marker
            or manifest["keyword"]
            or [arg.rstrip("/") for arg in manifest["args"]] != [path]
            or manifest["collection_digest"] != manifests[0]["collection_digest"]
            or manifest["eligible_count"] != manifests[0]["eligible_count"]
            or not isinstance(manifest["selected"], list)
            or any(
                not isinstance(nodeid, str) or shards.file_shard(nodeid, count) != index
                for nodeid in manifest["selected"]
            )
        ):
            raise ValueError(f"{prefix}-{index}: inconsistent test selection")
        selected.extend(manifest["selected"])
    if (
        len(set(selected)) != len(selected)
        or len(selected) != manifests[0]["eligible_count"]
        or shards.collection_digest(selected) != manifests[0]["collection_digest"]
    ):
        raise ValueError(f"{prefix}: overlapping or incomplete test selection")


def junit_summary(root: Path, label: str) -> tuple[str, bool]:
    files = sorted(root.rglob("*.xml"))
    if not files:
        raise ValueError(f"{label}: no JUnit reports")
    cases: list[ET.Element] = []
    for report in files:
        cases.extend(ET.parse(report).getroot().iter("testcase"))
    failures = [
        (case, failure)
        for case in cases
        for tag in ("failure", "error")
        for failure in case.findall(tag)
    ]
    skipped = sum(case.find("skipped") is not None for case in cases)
    text = (
        f"## {html.escape(label)}\n\n"
        f"Tests: {len(cases)}; failures/errors: {len(failures)}; skipped: {skipped}.\n\n"
    )
    for case, failure in failures[:30]:
        name = f"{case.get('classname', '')}::{case.get('name', '')}"
        detail = failure.text or failure.get("message") or ""
        text += (
            f"<details><summary>{html.escape(name)}</summary>"
            f"<pre>{html.escape(detail[:4000])}</pre></details>\n\n"
        )
    if len(failures) > 30:
        text += "Additional failures are in the uploaded JUnit reports.\n"
    merged = ET.Element("testsuite", name=label, tests=str(len(cases)))
    merged.set("failures", str(len(failures)))
    merged.set("skipped", str(skipped))
    merged.extend(cases)
    # Keep the merged report outside the downloaded input directory.
    ET.ElementTree(merged).write(root.parent / f"{root.name}-merged.xml", encoding="utf-8")
    return text, bool(failures)


def aggregate(root: Path, needs: dict[str, dict[str, str]]) -> tuple[str, int]:
    if not isinstance(needs, dict) or any(not isinstance(value, dict) for value in needs.values()):
        raise ValueError("Invalid shard job results")
    text = "## ML slow aggregate\n\n"
    failed = False
    for job in ("test-ml-components", "integration-shard", "coverage-shard"):
        result = needs.get(job, {}).get("result")
        text += f"- {job}: {html.escape(str(result))}\n"
        if result != "success":
            failed = True
    for folder, prefix, count, marker, path in (
        ("integration", "int-junit", 4, "integration", "tests/integration"),
        ("unit", "unit-cov", 2, "not slow and not integration", "tests"),
    ):
        try:
            validate_selections(root / folder, prefix, count, marker, path)
            for index in range(1, count + 1):
                directory = root / folder / f"{prefix}-{index}"
                manifest = json.loads((directory / "selection.json").read_text())
                cases = list(ET.parse(directory / "junit.xml").getroot().iter("testcase"))
                if len(cases) != len(manifest["selected"]):
                    raise ValueError(f"{prefix}-{index}: incomplete JUnit report")
        except (OSError, ValueError, KeyError, TypeError, ET.ParseError) as exc:
            text += f"\n**{folder} evidence failed:** {html.escape(str(exc))}\n"
            failed = True
        try:
            summary, junit_failed = junit_summary(root / folder, folder)
            text += "\n" + summary
            failed |= junit_failed
        except (OSError, ValueError, ET.ParseError) as exc:
            text += f"\n**{folder} JUnit failed:** {html.escape(str(exc))}\n"
            failed = True

    coverage_files = [
        root / "unit" / f"unit-cov-{index}" / f".coverage.unit-{index}" for index in (1, 2)
    ]
    if not all(path.is_file() for path in coverage_files):
        text += "\n**Coverage failed:** missing unit shard data.\n"
        failed = True
    else:
        env = dict(os.environ, COVERAGE_FILE=str(Path.cwd() / ".coverage.ml-unit-combined"))
        commands = (
            ["combine", "--keep", *(str(path) for path in coverage_files)],
            ["report", "--fail-under=70"],
            ["html", "-d", "htmlcov"],
        )
        for args in commands:
            try:
                proc = subprocess.run(
                    [sys.executable, "-m", "coverage", *args],
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
            except (OSError, subprocess.TimeoutExpired) as exc:
                text += f"\n**coverage {args[0]} failed:** {html.escape(str(exc))}\n"
                failed = True
                break
            text += (
                f"\n### coverage {args[0]}\n<pre>{html.escape(proc.stdout + proc.stderr)}</pre>\n"
            )
            if proc.returncode:
                failed = True
                if args[0] == "combine":
                    break
    return text, int(failed)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("summarize", "aggregate"))
    parser.add_argument("--reports", type=Path, required=True)
    parser.add_argument("--label", default="ML shard")
    args = parser.parse_args()
    try:
        if args.mode == "summarize":
            summary, failed = junit_summary(args.reports, args.label)
            exit_code = int(failed)
        else:
            summary, exit_code = aggregate(args.reports, json.loads(os.environ["NEEDS_JSON"]))
        with Path(os.environ["GITHUB_STEP_SUMMARY"]).open("a", encoding="utf-8") as output:
            output.write(summary)
        print(summary)
        return exit_code
    except (
        OSError,
        ValueError,
        KeyError,
        TypeError,
        ET.ParseError,
        subprocess.TimeoutExpired,
    ) as exc:
        summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary_path:
            with Path(summary_path).open("a", encoding="utf-8") as output:
                output.write(f"## ML reporting failed\n\n{html.escape(str(exc))}\n")
        print(f"::error::ML reporting failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
