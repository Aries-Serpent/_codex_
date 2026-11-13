"""File-stable pytest sharding, applied after normal marker deselection."""

from __future__ import annotations

import hashlib
import html
import json
import os
from pathlib import Path

import pytest

_REPORTED_FAILURES = pytest.StashKey[int]()


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


def file_shard(nodeid: str, count: int) -> int:
    filename = nodeid.split("::", 1)[0]
    return int.from_bytes(hashlib.sha256(filename.encode()).digest()[:8], "big") % count + 1


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("ml-shards")
    group.addoption("--ml-shards", type=int, default=1)
    group.addoption("--ml-shard", type=int, default=1)
    group.addoption("--ml-shard-report", type=Path)


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
    report = config.getoption("ml_shard_report")
    if report is not None:
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(
            json.dumps(
                {
                    "shard": shard,
                    "shards": count,
                    "args": config.args,
                    "marker": config.getoption("markexpr"),
                    "keyword": config.getoption("keyword"),
                    "eligible_count": len(nodeids),
                    "collection_digest": collection_digest(nodeids),
                    "selected": sorted(item.nodeid for item in selected),
                },
                indent=2,
            ),
            encoding="utf-8",
        )
