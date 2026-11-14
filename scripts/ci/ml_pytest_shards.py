"""File-stable pytest sharding, applied after normal marker deselection."""

from __future__ import annotations

import hashlib
import html
import json
import os
import re
from collections.abc import Generator, Mapping
from pathlib import Path
from typing import Any

import pytest

_REPORTED_FAILURES = pytest.StashKey[int]()
_QUARANTINED = pytest.StashKey[set[str]]()
_QUARANTINE_RESULTS = pytest.StashKey[dict[str, str]]()
_SELECTION = pytest.StashKey[dict[str, object]]()

QUARANTINE_FIELDS = ("nodeid", "cluster", "issue", "owner", "reason", "added_sha")
_ISSUE = re.compile(r"#[1-9][0-9]*|https://[^\s]+")
_SHA = re.compile(r"[0-9a-f]{7,40}")


def execution_context() -> dict[str, str | None]:
    return {
        key: os.environ.get(key)
        for key in ("GITHUB_REPOSITORY", "GITHUB_SHA", "GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT")
    }


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    report.user_properties.append(("codex_ml_nodeid", report.nodeid))


def pytest_exception_interact(
    node: pytest.Item | pytest.Collector, report: pytest.TestReport | pytest.CollectReport
) -> None:
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary or not report.failed:
        return
    count = node.config.stash.get(_REPORTED_FAILURES, 0)
    if count <= 30:
        with Path(summary).open("a", encoding="utf-8") as output:
            if count == 0:
                output.write("## ML shard failures (reported as tests finish)\n\n")
            if count < 30:
                output.write(
                    f"<details><summary>{html.escape(report.nodeid[:500])}</summary>"
                    f"<pre>{html.escape(str(report.longrepr)[:4000])}</pre></details>\n\n"
                )
            else:
                output.write("Additional failures require the JUnit report or job logs.\n")
    node.config.stash[_REPORTED_FAILURES] = count + 1


def collection_digest(nodeids: list[str]) -> str:
    return hashlib.sha256(json.dumps(sorted(nodeids)).encode()).hexdigest()


def parse_quarantine(data: Any) -> dict[str, dict[str, str]]:
    """Strictly validate a quarantine manifest and index its entries by node ID.

    Entries must name test items (``path::test``); collection errors have no
    item ID and can therefore never be quarantined.
    """
    if not isinstance(data, Mapping) or set(data) != {"version", "entries"}:
        raise ValueError("quarantine manifest must contain exactly 'version' and 'entries'")
    if data["version"] != 1 or isinstance(data["version"], bool):
        raise ValueError("quarantine manifest version must be 1")
    if not isinstance(data["entries"], list):
        raise ValueError("quarantine manifest 'entries' must be a list")
    entries: dict[str, dict[str, str]] = {}
    for index, entry in enumerate(data["entries"]):
        where = f"quarantine entry {index}"
        if not isinstance(entry, Mapping) or set(entry) != set(QUARANTINE_FIELDS):
            raise ValueError(f"{where}: fields must be exactly {', '.join(QUARANTINE_FIELDS)}")
        if any(not isinstance(entry[key], str) or not entry[key].strip() for key in entry):
            raise ValueError(f"{where}: every field must be a non-empty string")
        nodeid = entry["nodeid"]
        if "::" not in nodeid or nodeid != nodeid.strip():
            raise ValueError(f"{where}: nodeid must be a test item ID (path::test)")
        if nodeid in entries:
            raise ValueError(f"{where}: duplicate nodeid {nodeid}")
        if not _ISSUE.fullmatch(entry["issue"]):
            raise ValueError(f"{where}: issue must be an https URL or #<number>")
        if not _SHA.fullmatch(entry["added_sha"]):
            raise ValueError(f"{where}: added_sha must be a 7-40 character hex commit")
        entries[nodeid] = dict(entry)
    return entries


def load_quarantine(path: Path) -> dict[str, dict[str, str]]:
    return parse_quarantine(json.loads(path.read_text(encoding="utf-8")))


def quarantine_digest(entries: Mapping[str, Any]) -> str:
    return collection_digest(list(entries))


def file_shard(nodeid: str, count: int) -> int:
    filename = nodeid.split("::", 1)[0]
    return int.from_bytes(hashlib.sha256(filename.encode()).digest()[:8], "big") % count + 1


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("ml-shards")
    group.addoption("--ml-shards", type=int, default=1)
    group.addoption("--ml-shard", type=int, default=1)
    group.addoption("--ml-shard-report", type=Path)
    group.addoption(
        "--ml-quarantine",
        type=Path,
        help="JSON manifest of known-failing test IDs to run as strict xfail.",
    )


@pytest.hookimpl(trylast=True)
def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    count = config.getoption("ml_shards")
    shard = config.getoption("ml_shard")
    if count < 1 or not 1 <= shard <= count:
        raise pytest.UsageError("--ml-shard must be between 1 and --ml-shards")
    nodeids = [item.nodeid for item in items]
    if len(set(nodeids)) != len(nodeids):
        raise pytest.UsageError("ML sharding requires unique collected test IDs")
    selected = [item for item in items if file_shard(item.nodeid, count) == shard]
    deselected = [item for item in items if file_shard(item.nodeid, count) != shard]
    items[:] = selected
    config.hook.pytest_deselected(items=deselected)
    quarantine_path = config.getoption("ml_quarantine")
    quarantine: dict[str, dict[str, str]] | None = None
    if quarantine_path is not None:
        try:
            quarantine = load_quarantine(quarantine_path)
        except (OSError, ValueError) as exc:
            raise pytest.UsageError(f"invalid --ml-quarantine manifest: {exc}") from exc
        config.stash[_QUARANTINED] = {item.nodeid for item in selected} & set(quarantine)
        config.stash[_QUARANTINE_RESULTS] = {}
        for item in selected:
            entry = quarantine.get(item.nodeid)
            if entry is not None:
                # strict: an unexpected pass fails the run so the manifest must shrink.
                # Prepended so it is evaluated before any xfail the test itself declares.
                item.add_marker(
                    pytest.mark.xfail(
                        strict=True,
                        reason=f"quarantined: {entry['issue']} {entry['cluster']}",
                    ),
                    append=False,
                )
    report = config.getoption("ml_shard_report")
    if report is not None:
        report.parent.mkdir(parents=True, exist_ok=True)
        manifest: dict[str, object] = {
            "shard": shard,
            "shards": count,
            "args": config.args,
            "marker": config.getoption("markexpr"),
            "keyword": config.getoption("keyword"),
            "eligible_count": len(nodeids),
            "collection_digest": collection_digest(nodeids),
            "selected": sorted(item.nodeid for item in selected),
            "context": execution_context(),
            "collect_only": config.getoption("collectonly"),
            "exitstatus": None,
            **quarantine_report(quarantine, selected),
        }
        config.stash[_SELECTION] = manifest
        report.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def quarantine_report(
    quarantine: Mapping[str, Any] | None, selected: list[pytest.Item]
) -> dict[str, Any]:
    if quarantine is None:
        return {}
    selected_ids = {item.nodeid for item in selected}
    return {
        "quarantine_digest": quarantine_digest(quarantine),
        "quarantined": sorted(selected_ids & set(quarantine)),
        "quarantine_not_selected": sorted(set(quarantine) - selected_ids),
    }


@pytest.hookimpl(wrapper=True, tryfirst=True)
def pytest_runtest_makereport(
    item: pytest.Item, call: pytest.CallInfo[None]
) -> Generator[None, pytest.TestReport, pytest.TestReport]:
    """Classify quarantined outcomes after pytest's own xfail handling.

    Only a failure of the test body counts as the quarantined failure. A
    passing body always fails (XPASS), whatever other xfail marks say. Setup
    and teardown errors are fixture/environment breakage, not the tracked
    failure, so they stay errors instead of being absorbed by the xfail mark.
    """
    report = yield
    if item.nodeid not in item.config.stash.get(_QUARANTINED, set()):
        return report
    results = item.config.stash[_QUARANTINE_RESULTS]
    if call.when == "call":
        if call.excinfo is None:
            results[item.nodeid] = "xpassed"
            if not report.failed:
                report.outcome = "failed"
                report.longrepr = (
                    "[XPASS(quarantine)] quarantined test passed; remove it from the manifest"
                )
            if hasattr(report, "wasxfail"):
                del report.wasxfail
        else:
            results[item.nodeid] = "xfailed" if hasattr(report, "wasxfail") else report.outcome
    elif call.excinfo is not None and not call.excinfo.errisinstance(pytest.skip.Exception):
        results[item.nodeid] = f"{call.when}-error"
        if hasattr(report, "wasxfail"):
            del report.wasxfail
            report.outcome = "failed"
    return report



def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    config = session.config
    manifest = config.stash.get(_SELECTION, None)
    if manifest is None:
        return
    manifest["exitstatus"] = int(exitstatus)
    if _QUARANTINE_RESULTS in config.stash:
        manifest["quarantine_results"] = dict(sorted(config.stash[_QUARANTINE_RESULTS].items()))
    report = config.getoption("ml_shard_report")
    if report is not None:
        report.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
