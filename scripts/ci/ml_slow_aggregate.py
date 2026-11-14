"""Validate ML shard selections and report unit-only combined coverage."""

from __future__ import annotations

import argparse
import html
import json
import math
import os
import subprocess
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any
from xml.etree.ElementTree import Element

from defusedxml import ElementTree as ET
from defusedxml.common import DefusedXmlException

if __package__:
    from . import ml_pytest_shards as package_shards

    shards = package_shards
else:
    import ml_pytest_shards as script_shards

    shards = script_shards


APPROVAL_ENV = "ML_QUARANTINE_GROWTH_APPROVED"
FLOOR_FIELDS = {"floor", "target", "measured_sha"}


def parse_floor(data: Any) -> dict[str, Any]:
    """Validate ``{"floor": int, "target": int, "measured_sha": str}``."""
    if not isinstance(data, Mapping) or set(data) != FLOOR_FIELDS:
        raise ValueError("coverage floor must contain exactly floor, target, measured_sha")
    for key in ("floor", "target"):
        value = data[key]
        if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 100:
            raise ValueError(f"coverage floor '{key}' must be an integer from 0 to 100")
    if data["floor"] > data["target"]:
        raise ValueError("coverage floor must not exceed its target")
    if not isinstance(data["measured_sha"], str) or not data["measured_sha"].strip():
        raise ValueError("coverage floor 'measured_sha' must be a non-empty string")
    return dict(data)


def load_floor(path: Path) -> dict[str, Any]:
    return parse_floor(json.loads(path.read_text(encoding="utf-8")))


def check_floor(percent: float, floor: dict[str, Any]) -> tuple[str, bool]:
    """Return a summary and whether combined coverage is below the ratchet floor."""
    text = (
        f"\nCombined unit coverage: {percent:.2f}% (floor {floor['floor']}%, "
        f"target {floor['target']}%).\n"
    )
    if percent < floor["floor"]:
        return text + f"\n**Coverage failed:** {percent:.2f}% is below the floor.\n", True
    if percent >= floor["floor"] + 1 and floor["floor"] < floor["target"]:
        # Same rule as the initial floor: floor(measured - 0.5), capped at the target.
        suggested = max(floor["floor"], min(math.floor(percent - 0.5), floor["target"]))
        notice = (
            f"Coverage {percent:.2f}% is at least 1 point above the floor; consider raising "
            f"floor in .codex/baselines/ml_unit_coverage_floor.json to {suggested} "
            "(not changed automatically)."
        )
        print(f"::notice::{notice}")
        text += f"\n{notice}\n"
    return text, False


def ratchet_problems(
    current_quarantine: Mapping[str, Any],
    base_quarantine: Mapping[str, Any] | None,
    current_floor: Mapping[str, Any],
    base_floor: Mapping[str, Any] | None,
) -> list[str]:
    """Compare baselines with the PR base; a missing base file imposes no constraint."""
    problems = []
    if base_quarantine is not None:
        added = sorted(set(current_quarantine) - set(base_quarantine))
        if added:
            problems.append(
                f"quarantine manifest grew by {len(added)} entr"
                f"{'y' if len(added) == 1 else 'ies'}: {', '.join(added[:20])}"
            )
    if base_floor is not None and current_floor["floor"] < base_floor["floor"]:
        problems.append(
            f"coverage floor decreased from {base_floor['floor']} to {current_floor['floor']}"
        )
    return problems


def git_show(ref: str, path: str) -> str | None:
    """Return ``path`` at ``ref``; None only when the (valid) ref lacks the file."""
    verify = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if verify.returncode:
        raise ValueError(f"base ref {ref!r} is not an available commit")
    spec = f"{ref}:./{Path(path).as_posix()}"
    exists = subprocess.run(["git", "cat-file", "-e", spec], capture_output=True, timeout=60)
    if exists.returncode:
        return None
    shown = subprocess.run(
        ["git", "show", spec], capture_output=True, text=True, timeout=60, check=True
    )
    return shown.stdout


def ratchet(
    base_ref: str, quarantine_path: Path, floor_path: Path, *, allow_approval: bool = True
) -> tuple[str, int]:
    current_quarantine = shards.load_quarantine(quarantine_path)
    current_floor = load_floor(floor_path)
    base_text = git_show(base_ref, str(quarantine_path))
    base_quarantine = None if base_text is None else shards.parse_quarantine(json.loads(base_text))
    base_text = git_show(base_ref, str(floor_path))
    base_floor = None if base_text is None else parse_floor(json.loads(base_text))
    problems = ratchet_problems(current_quarantine, base_quarantine, current_floor, base_floor)
    text = (
        f"## ML baseline ratchet\n\nBase: {html.escape(base_ref)}; quarantined: "
        f"{len(current_quarantine)}; floor: {current_floor['floor']}%.\n"
    )
    if not problems:
        return text + "\nNo quarantine growth or floor decrease.\n", 0
    approved = allow_approval and os.environ.get(APPROVAL_ENV) == "1"
    for problem in problems:
        text += f"\n- {html.escape(problem)}"
        prefix = "::warning::" if approved else "::error::"
        print(f"{prefix}{problem}", file=sys.stderr)
    if approved:
        return text + "\n\nAccepted: PR carries the `quarantine-approved` label.\n", 0
    return (
        text + "\n\n**Ratchet failed:** shrink the manifest / keep the floor, or obtain "
        "the `quarantine-approved` label.\n",
        1,
    )


def validate_selections(
    root: Path,
    prefix: str,
    count: int,
    marker: str,
    path: str,
    quarantine: Mapping[str, Any] | None = None,
) -> list[str]:
    """Validate shard selections; return quarantine entries no shard selected (stale)."""
    expected = {f"{prefix}-{index}" for index in range(1, count + 1)}
    if {entry.name for entry in root.iterdir()} != expected:
        raise ValueError(f"{prefix}: missing or unexpected shard artifacts")
    context = shards.execution_context()
    if os.environ.get("GITHUB_ACTIONS") == "true" and not all(context.values()):
        raise ValueError("Incomplete hosted ML execution context")
    manifests = [
        json.loads((root / f"{prefix}-{index}" / "selection.json").read_text())
        for index in range(1, count + 1)
    ]
    if not manifests or type(manifests[0]["eligible_count"]) is not int:
        raise ValueError(f"{prefix}: invalid eligible collection size")
    if manifests[0]["eligible_count"] < 1:
        raise ValueError(f"{prefix}: empty eligible collection")
    selected: list[str] = []
    for index, manifest in enumerate(manifests, 1):
        exitstatus = manifest.get("exitstatus")
        allowed_exitstatuses = (0, 1) if quarantine is not None else (0,)
        if (
            manifest["shard"] != index
            or manifest["shards"] != count
            or manifest["marker"] != marker
            or manifest["keyword"]
            or manifest["context"] != context
            or manifest["collect_only"] is not False
            or type(exitstatus) is not int
            or exitstatus not in allowed_exitstatuses
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
    if quarantine is None:
        return []
    stale = set(quarantine)
    for index, manifest in enumerate(manifests, 1):
        quarantined = manifest.get("quarantined")
        not_selected = manifest.get("quarantine_not_selected")
        if (
            manifest.get("quarantine_digest") != shards.quarantine_digest(quarantine)
            or not isinstance(quarantined, list)
            or not isinstance(not_selected, list)
            or set(quarantined) != set(quarantine) & set(manifest["selected"])
            or set(quarantined) | set(not_selected) != set(quarantine)
        ):
            raise ValueError(f"{prefix}-{index}: shard did not apply the quarantine manifest")
        results = manifest.get("quarantine_results")
        if not isinstance(results, dict) or not set(results) <= set(quarantined):
            raise ValueError(f"{prefix}-{index}: missing quarantine outcomes")
        # Defense in depth: JUnit may record a non-strict XPASS as a plain pass.
        xpassed = sorted(nodeid for nodeid, outcome in results.items() if outcome == "xpassed")
        if xpassed:
            raise ValueError(
                f"{prefix}-{index}: quarantined tests passed (XPASS), remove them from "
                f"the manifest: {', '.join(xpassed)}"
            )
        stale &= set(not_selected)
    return sorted(stale)


def collection_skip_key(case: Element) -> tuple[str, str] | None:
    skipped = case.find("skipped")
    if (
        not case.get("classname")
        and skipped is not None
        and skipped.get("message") == "collection skipped"
    ):
        return case.get("name", ""), skipped.text or ""
    return None


def is_collection_error(case: Element) -> bool:
    return not case.get("classname") and (
        case.find("error") is not None or case.find("failure") is not None
    )


def junit_summary(root: Path, label: str) -> tuple[str, bool]:
    files = sorted(root.rglob("*.xml"))
    if not files:
        raise ValueError(f"{label}: no JUnit reports")
    cases: list[Element] = []
    collection_skips: set[tuple[str, str]] = set()
    for report in files:
        for case in ET.parse(report).getroot().iter("testcase"):
            key = collection_skip_key(case)
            if key is not None:
                if key in collection_skips:
                    continue
                collection_skips.add(key)
            cases.append(case)
    failures = [
        (case, failure)
        for case in cases
        for tag in ("failure", "error")
        for failure in case.findall(tag)
    ]
    skips = [skip for case in cases if (skip := case.find("skipped")) is not None]
    skipped = len(skips)
    quarantined = sum((skip.get("message") or "").startswith("quarantined:") for skip in skips)
    collection_errors = sum(is_collection_error(case) for case in cases)
    text = (
        f"## {html.escape(label)}\n\n"
        f"Tests: {len(cases)}; failures/errors: {len(failures)}; skipped: {skipped}.\n\n"
    )
    if quarantined:
        text += f"Quarantined (strict xfail): {quarantined}.\n\n"
    if collection_errors:
        text += f"**Collection errors (never quarantinable):** {collection_errors}.\n\n"
    for case, failure in failures[:30]:
        name = f"{case.get('classname', '')}::{case.get('name', '')}"
        detail = failure.text or failure.get("message") or ""
        text += (
            f"<details><summary>{html.escape(name)}</summary>"
            f"<pre>{html.escape(detail[:4000])}</pre></details>\n\n"
        )
    if len(failures) > 30:
        text += "Additional failures are in the uploaded JUnit reports.\n"
    merged = (
        f'<testsuite name="{html.escape(label, quote=True)}" tests="{len(cases)}" '
        f'failures="{len(failures)}" skipped="{skipped}">'
        + "".join(ET.tostring(case, encoding="unicode") for case in cases)
        + "</testsuite>"
    )
    # Keep the merged report outside the downloaded input directory.
    (root.parent / f"{root.name}-merged.xml").write_text(merged, encoding="utf-8")
    return text, bool(failures)


def pytest_exit_problem(directory: Path, label: str, failed: bool) -> str | None:
    """Check the exit code a coverage shard recorded instead of failing its job."""
    try:
        code = (directory / "pytest-exit-code").read_text().strip()
    except OSError:
        return f"{label}: missing pytest exit code"
    if code not in ("0", "1"):
        return f"{label}: pytest exited {code}"
    if code == "1" and not failed:
        return f"{label}: pytest failed without JUnit failure evidence"
    return None


def aggregate(
    root: Path,
    needs: dict[str, dict[str, str]],
    *,
    floor: Mapping[str, Any],
    quarantine: Mapping[str, Any],
) -> tuple[str, int]:
    if not isinstance(needs, dict) or any(not isinstance(value, dict) for value in needs.values()):
        raise ValueError("Invalid shard job results")
    text = "## ML slow aggregate\n\n"
    failed = False
    for job in ("test-ml-components", "integration-shard", "coverage-shard"):
        result = needs.get(job, {}).get("result")
        text += f"- {job}: {html.escape(str(result))}\n"
        if result != "success":
            failed = True
    for folder, prefix, count, marker, path, shard_quarantine in (
        ("integration", "int-junit", 4, "integration", "tests/integration", None),
        ("unit", "unit-cov", 4, "not slow and not integration", "tests", quarantine),
    ):
        try:
            stale = validate_selections(
                root / folder, prefix, count, marker, path, shard_quarantine
            )
            if stale:
                text += (
                    f"\n**Stale quarantine entries (collected by no shard):** "
                    f"{html.escape(', '.join(stale))}\n"
                )
                failed = True
            for index in range(1, count + 1):
                directory = root / folder / f"{prefix}-{index}"
                manifest = json.loads((directory / "selection.json").read_text())
                cases = list(ET.parse(directory / "junit.xml").getroot().iter("testcase"))
                # Module-level skips are reported by every collector, not selected items.
                selected_cases = [case for case in cases if collection_skip_key(case) is None]
                if len(selected_cases) != len(manifest["selected"]):
                    raise ValueError(f"{prefix}-{index}: incomplete JUnit report")
                if shard_quarantine is not None:
                    shard_failed = any(
                        case.find(tag) is not None for case in cases for tag in ("failure", "error")
                    )
                    problem = pytest_exit_problem(directory, f"{prefix}-{index}", shard_failed)
                    if problem:
                        raise ValueError(problem)
                reported: list[str] = []
                for case in selected_cases:
                    properties = case.findall("./properties/property[@name='codex_ml_nodeid']")
                    nodeid = properties[0].get("value") if len(properties) == 1 else None
                    if not nodeid:
                        raise ValueError(f"{prefix}-{index}: missing or ambiguous pytest node ID")
                    reported.append(nodeid)
                if sorted(reported) != sorted(manifest["selected"]):
                    raise ValueError(f"{prefix}-{index}: mismatched JUnit test identities")
        except (
            OSError,
            ValueError,
            KeyError,
            TypeError,
            ET.ParseError,
            DefusedXmlException,
        ) as exc:
            text += f"\n**{folder} evidence failed:** {html.escape(str(exc))}\n"
            failed = True
        try:
            summary, junit_failed = junit_summary(root / folder, folder)
            text += "\n" + summary
            failed |= junit_failed
        except (OSError, ValueError, ET.ParseError, DefusedXmlException) as exc:
            text += f"\n**{folder} JUnit failed:** {html.escape(str(exc))}\n"
            failed = True

    coverage_files = [
        root / "unit" / f"unit-cov-{index}" / f".coverage.unit-{index}" for index in range(1, 5)
    ]
    if not all(path.is_file() for path in coverage_files):
        text += "\n**Coverage failed:** missing unit shard data.\n"
        return text, 1
    env = dict(os.environ, COVERAGE_FILE=str(Path.cwd() / ".coverage.ml-unit-combined"))
    totals = Path.cwd() / "coverage-ml-unit.json"
    commands = (
        ["combine", "--keep", *(str(path) for path in coverage_files)],
        ["report", "--precision=2", "--fail-under=0"],
        ["json", "-q", "-o", str(totals)],
        ["html", "-d", "htmlcov"],
    )
    for args in commands:
        try:
            proc = subprocess.run(
                [sys.executable, "-m", "coverage", *args],
                env=env,
                cwd=Path.cwd(),
                capture_output=True,
                text=True,
                timeout=120,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            text += f"\n**coverage {args[0]} failed:** {html.escape(str(exc))}\n"
            return text, 1
        if args[0] != "json":
            text += (
                f"\n### coverage {args[0]}\n<pre>{html.escape(proc.stdout + proc.stderr)}</pre>\n"
            )
        if proc.returncode:
            text += f"\n**coverage {args[0]} failed** (exit {proc.returncode}).\n"
            failed = True
            if args[0] == "combine":
                return text, 1
    try:
        percent = float(json.loads(totals.read_text())["totals"]["percent_covered"])
    except (OSError, ValueError, KeyError, TypeError) as exc:
        text += f"\n**Coverage failed:** unreadable totals: {html.escape(str(exc))}\n"
        return text, 1
    floor_text, below = check_floor(percent, dict(floor))
    return text + floor_text, int(failed or below)


def write_summary(summary: str) -> None:
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with Path(summary_path).open("a", encoding="utf-8") as output:
            output.write(summary)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("summarize", "aggregate", "ratchet"))
    parser.add_argument("--reports", type=Path)
    parser.add_argument("--label", default="ML shard")
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="summarize: do not fail on test failures (the aggregate is the gate)",
    )
    parser.add_argument("--floor-file", type=Path)
    parser.add_argument("--quarantine", type=Path)
    parser.add_argument("--base-ref", help="ratchet: git ref of the PR or push base")
    parser.add_argument(
        "--no-approval",
        action="store_true",
        help=f"ratchet: ignore {APPROVAL_ENV} (push events cannot be approved)",
    )
    args = parser.parse_args()
    required = {
        "summarize": ("reports",),
        "aggregate": ("reports", "floor_file", "quarantine"),
        "ratchet": ("base_ref", "floor_file", "quarantine"),
    }[args.mode]
    missing = [name for name in required if getattr(args, name) is None]
    if missing:
        parser.error(
            f"{args.mode} requires " + ", ".join(f"--{m.replace('_', '-')}" for m in missing)
        )
    try:
        if args.mode == "summarize":
            summary, failed = junit_summary(args.reports, args.label)
            exit_code = 0 if args.report_only else int(failed)
        elif args.mode == "aggregate":
            summary, exit_code = aggregate(
                args.reports,
                json.loads(os.environ["NEEDS_JSON"]),
                floor=load_floor(args.floor_file),
                quarantine=shards.load_quarantine(args.quarantine),
            )
        else:
            summary, exit_code = ratchet(
                args.base_ref,
                args.quarantine,
                args.floor_file,
                allow_approval=not args.no_approval,
            )
        write_summary(summary)
        print(summary)
        return exit_code
    except (
        OSError,
        ValueError,
        KeyError,
        TypeError,
        ET.ParseError,
        DefusedXmlException,
        subprocess.SubprocessError,
    ) as exc:
        write_summary(f"## ML reporting failed\n\n{html.escape(str(exc))}\n")
        print(f"::error::ML reporting failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
