from __future__ import annotations

import copy
import hashlib
import hmac
import json
import os
from pathlib import Path

import pytest

from scripts.archive import cdx_adapter as adapter
from scripts.archive import cdx_preflight as preflight
from scripts.archive import cdx_review as review


@pytest.fixture
def bound_report(tmp_path):
    raw = b"synthetic-match\n"
    (tmp_path / "fixture.txt").write_bytes(raw)
    identity = {
        "mode": adapter.MODE,
        "module": adapter.MODULE,
        "version": adapter.VERSION,
        "module_sum": adapter.MODULE_SUM,
        "config_sha256": "a" * 64,
        "executable_sha256": "b" * 64,
    }
    request = {
        "schema_version": 1,
        "source": str(tmp_path),
        "key": "c" * 64,
        "bindings": {"run_namespace": "d" * 32},
        "files": [
            {"path": "fixture.txt", "size": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
        ],
    }
    report = {
        **identity,
        "schema_version": 1,
        "request_sha256": "e" * 64,
        "bindings": request["bindings"],
        "acquisitions": [
            {
                **request["files"][0],
                "origin_start": 0,
                "origin_end": len(raw),
                "detector_calls": 1,
                "observations": [
                    {
                        "record": {
                            "File": "fixture.txt",
                            "RuleID": "synthetic-only",
                            "StartLine": 1,
                            "EndLine": 1,
                            "StartColumn": 1,
                            "EndColumn": 15,
                            "Tags": [],
                            "Secret": "REDACTED",
                            "Match": "REDACTED",
                        },
                        "start": 0,
                        "end": 15,
                        "mapping_status": "mapped_acquired_full_file",
                        "match_hmac": hmac.new(
                            bytes.fromhex(request["key"]), raw[:15], hashlib.sha256
                        ).hexdigest(),
                    }
                ],
            }
        ],
    }
    return tmp_path, request, report, identity


@pytest.mark.parametrize(
    "mutation",
    [
        "origin",
        "file",
        "tool",
        "config",
        "run",
        "request",
        "span",
        "hmac",
        "column",
        "calls",
        "missing",
    ],
)
def test_bound_report_rejects_mismatch(bound_report, mutation):
    snapshot, request, report, identity = bound_report
    report = copy.deepcopy(report)
    acquired = report["acquisitions"][0]
    observation = acquired["observations"][0]
    if mutation == "origin":
        acquired["origin_start"] = 1
    elif mutation == "file":
        acquired["sha256"] = "f" * 64
    elif mutation == "tool":
        report["executable_sha256"] = "f" * 64
    elif mutation == "config":
        report["config_sha256"] = "f" * 64
    elif mutation == "run":
        report["bindings"]["run_namespace"] = "f" * 32
    elif mutation == "request":
        report["request_sha256"] = "f" * 64
    elif mutation == "span":
        observation["end"] = 100
    elif mutation == "hmac":
        observation["match_hmac"] = "f" * 64
    elif mutation == "column":
        observation["record"]["StartColumn"] = 2
    elif mutation == "calls":
        acquired["detector_calls"] = 2
    else:
        report["acquisitions"] = []
    with pytest.raises((ValueError, RuntimeError)):
        adapter._validate_report(snapshot, request, "e" * 64, report, identity)


def test_compatibility_is_multiset_not_deduplicated(bound_report):
    snapshot, request, report, identity = bound_report
    rows = adapter._validate_report(snapshot, request, "e" * 64, report, identity)
    assert adapter._compatibility(rows, rows)["exact_record_multiset_equal"]
    assert not adapter._compatibility(rows * 2, rows)["exact_record_multiset_equal"]
    assert not adapter._compatibility(rows, rows)["packer_clearance_compatible"]


def test_acquired_mapper_requires_current_run_not_origin_dict(tmp_path, monkeypatch):
    def missing(*_args):
        raise ValueError("no completed adapter run")

    monkeypatch.setattr(adapter, "load_adapter", missing)
    with pytest.raises(ValueError, match="no completed adapter run"):
        adapter.acquired_span(tmp_path, tmp_path, tmp_path / "tool", "caller-selected-id")


@pytest.mark.parametrize(
    "prefix,newline,fragment_boundary",
    [
        (0, "\n", False),
        (100000, "\n", False),
        (100000, "\r\n", False),
        (100000, "\n", True),
        (100000, "\r\n", True),
    ],
)
def test_actual_maintained_adapter_end_to_end(tmp_path, prefix, newline, fragment_boundary):
    executable = os.environ.get("CDX_TEST_ADAPTER_EXECUTABLE")
    if executable is None:
        pytest.skip("actual pinned adapter integration requires explicitly supplied executable")
    source, private = tmp_path / "source", tmp_path / "private"
    source.mkdir(mode=0o700)
    private.mkdir(mode=0o700)
    value = "".join(["wE4r", "T6yU", "9iO2", "pA5s", "D8fG", "3hJ7", "kL0z"])
    padding = "x" * prefix + newline
    if fragment_boundary:
        padding = "x" * (prefix - 2 * len(newline)) + newline * 2
    raw = (padding + 'λapi_key="' + value + '"' + newline).encode()
    (source / "fixture.txt").write_bytes(raw)
    before = preflight.measure_tree(source)
    stock = preflight.run_preflight(source, private)
    assert stock["scanner_execution"] == "both_completed"
    result = adapter.run_adapter(source, private, Path(executable))
    _, rows = adapter.load_adapter(source, private, Path(executable))
    assert result["detector_calls"] == 1
    assert result["observations"] >= 1
    assert result["mapped"] == result["observations"]
    assert result["compatibility"]["exact_record_multiset_equal"] is not fragment_boundary
    assert not result["compatibility"]["packer_clearance_compatible"]
    assert preflight.measure_tree(source) == before
    span, status = adapter.acquired_span(source, private, Path(executable), rows[0]["finding_id"])
    assert status == "mapped_acquired_full_file"
    assert value.encode() in span
    assert not result["archive_created"]
    # Corrupting even one retained byte fails before any mapping is returned.
    request, _ = review.read_private_json(private / "adapter-request.json")
    request["bindings"]["run_namespace"] = "0" * 32
    (private / "adapter-request.json").write_text(json.dumps(request))
    with pytest.raises(ValueError):
        adapter.load_adapter(source, private, Path(executable))
