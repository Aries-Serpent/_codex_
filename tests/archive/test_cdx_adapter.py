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
    raw = b"prefix\nsynthetic-match\n"
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
                            "StartLine": 2,
                            "EndLine": 2,
                            "StartColumn": 2,
                            "EndColumn": 16,
                            "Tags": [],
                            "Secret": "REDACTED",
                            "Match": "synthetic-match",
                        },
                        "start": 7,
                        "end": 22,
                        "mapping_status": "mapped_acquired_full_file",
                        "match_hmac": hmac.new(
                            bytes.fromhex(request["key"]), raw[7:22], hashlib.sha256
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
        "end_line",
        "end_column",
        "match",
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
        observation["record"]["StartColumn"] = 3
    elif mutation == "end_line":
        observation["record"]["EndLine"] = 1
    elif mutation == "end_column":
        observation["record"]["EndColumn"] += 1
    elif mutation == "match":
        observation["record"]["Match"] = "different synthetic match"
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


@pytest.mark.parametrize(
    "stock_count,adapter_count",
    [(0, 0), (1, 1), (2, 1), (1, 2), (2, 2), (1, 0), (0, 1)],
)
def test_reconciliation_retains_each_occurrence(bound_report, stock_count, adapter_count):
    snapshot, request, report, identity = bound_report
    rows = adapter._validate_report(snapshot, request, "e" * 64, report, identity)
    result = adapter._compatibility(rows * stock_count, rows * adapter_count)
    assert result["matched_observations"] == min(stock_count, adapter_count)
    assert result["missing_adapter_observations"] == max(0, stock_count - adapter_count)
    assert result["extra_adapter_observations"] == max(0, adapter_count - stock_count)
    assert result["stock_duplicate_observations"] == max(0, stock_count - 1)
    assert result["adapter_duplicate_observations"] == max(0, adapter_count - 1)
    assert result["unique_exact_associations"] == int(stock_count == adapter_count == 1)
    assert result["exact_record_multiset_equal"] == (stock_count == adapter_count)
    assert not result["packer_clearance_compatible"]
    if stock_count or adapter_count:
        group = result["groups"][0]
        assert group["stock_ordinals"] == list(range(stock_count))
        assert group["adapter_ordinals"] == list(range(adapter_count))
        if stock_count > 1 or adapter_count > 1:
            assert group["association"] == "ambiguous_duplicates"
    else:
        assert result["groups"] == []


@pytest.mark.parametrize("difference", ["context", "file_digest", "path"])
def test_reconciliation_does_not_guess_divergent_associations(bound_report, difference):
    snapshot, request, report, identity = bound_report
    stock = adapter._validate_report(snapshot, request, "e" * 64, report, identity)
    acquired = copy.deepcopy(stock)
    if difference == "context":
        acquired[0]["_record"]["StartColumn"] += 1
    elif difference == "file_digest":
        acquired[0]["file_sha256"] = "f" * 64
    else:
        acquired[0]["path"] = "different.txt"
        acquired[0]["_record"]["File"] = "different.txt"
    result = adapter._compatibility(stock, acquired)
    assert result["matched_observations"] == 0
    assert result["missing_adapter_observations"] == 1
    assert result["extra_adapter_observations"] == 1
    assert {group["association"] for group in result["groups"]} == {"stock_only", "adapter_only"}


@pytest.mark.parametrize("mutation", ["version", "digest", "path", "metadata", "tags"])
def test_reconciliation_rejects_invalid_observations(bound_report, mutation):
    snapshot, request, report, identity = bound_report
    rows = adapter._validate_report(snapshot, request, "e" * 64, report, identity)
    if mutation == "version":
        rows[0]["scanner_version"] = "8.0.0"
    elif mutation == "digest":
        rows[0]["file_sha256"] = "invalid"
    elif mutation == "path":
        rows[0]["_record"]["File"] = "different.txt"
    elif mutation == "metadata":
        rows[0]["start_line"] = 3
    else:
        rows[0]["_record"]["Tags"] = ["z", "a"]
    with pytest.raises(ValueError, match="invalid reconciliation observation"):
        adapter._compatibility(rows, rows)


def test_reconciliation_ordinals_preserve_other_scanner_positions(bound_report):
    snapshot, request, report, identity = bound_report
    rows = adapter._validate_report(snapshot, request, "e" * 64, report, identity)
    result = adapter._compatibility([{"scanner": "detect-secrets"}, *rows], rows)
    assert result["groups"][0]["stock_ordinals"] == [1]
    assert result["groups"][0]["adapter_ordinals"] == [0]


@pytest.mark.parametrize("ordinal", [True, -1, 1.0, "0", None])
def test_stock_relationship_rejects_invalid_ordinal(ordinal):
    with pytest.raises(ValueError, match="invalid stock observation ordinal"):
        adapter.stock_relationship(Path("/unused"), Path("/unused"), Path("/unused"), ordinal)


def test_stock_relationship_revalidates_and_preserves_ambiguity(bound_report, monkeypatch):
    snapshot, request, report, identity = bound_report
    rows = adapter._validate_report(snapshot, request, "e" * 64, report, identity)
    complete = {
        "bindings": {"run_namespace": "adapter-synthetic"},
        "stock_bindings": {"run_namespace": "stock-synthetic"},
        "compatibility": adapter._compatibility(rows * 2, rows),
    }
    calls = []

    def load(*args):
        calls.append(args)
        return complete, rows

    monkeypatch.setattr(adapter, "load_adapter", load)
    result = adapter.stock_relationship(snapshot, snapshot, snapshot / "tool", 1)
    assert len(calls) == 1
    assert result["relationship"]["association"] == "ambiguous_duplicates"
    assert result["relationship"]["stock_ordinals"] == [0, 1]
    assert result["stock_bindings"] != result["adapter_bindings"]
    assert not result["packer_clearance_compatible"]
    with pytest.raises(ValueError, match="unmatched stock observation ordinal"):
        adapter.stock_relationship(snapshot, snapshot, snapshot / "tool", 2)


def test_acquired_mapper_requires_current_run_not_origin_dict(tmp_path, monkeypatch):
    def missing(*_args):
        raise ValueError("no completed adapter run")

    monkeypatch.setattr(adapter, "load_adapter", missing)
    with pytest.raises(ValueError, match="no completed adapter run"):
        adapter.acquired_span(tmp_path, tmp_path, tmp_path / "tool", "caller-selected-id")


@pytest.mark.parametrize("count", [0, 1, 32, 33, 65, 100])
def test_list_batches_indexes_every_observation(count, monkeypatch):
    calls = []

    def load(*args):
        calls.append(args)
        return {"bindings": {"run_namespace": "synthetic"}}, [{}] * count

    monkeypatch.setattr(adapter, "load_adapter", load)
    paths = (Path("/source"), Path("/private"), Path("/tool"))
    result = adapter.list_batches(*paths)
    assert calls == [paths]
    assert result == adapter.list_batches(*paths)
    batches = result["batches"]
    assert result["index_base"] == 0
    assert [batch["batch_index"] for batch in batches] == list(range(len(batches)))
    assert all(1 <= batch["observations"] <= 32 for batch in batches)
    assert [
        ordinal
        for batch in batches
        for ordinal in range(batch["start_ordinal"], batch["end_ordinal_exclusive"])
    ] == list(range(count))
    assert sum(batch["observations"] for batch in batches) == count
    assert not result["packer_clearance_compatible"]


def test_list_batches_cli_reports_only_index(monkeypatch, capsys):
    monkeypatch.setattr(
        adapter, "load_adapter", lambda *_: ({"bindings": {}}, [{"Secret": "not-output"}] * 65)
    )
    assert (
        adapter.main(
            [
                "--list-batches",
                "--source",
                "/source",
                "--private-directory",
                "/private",
                "--gitleaks-adapter",
                "/tool",
            ]
        )
        == 0
    )
    output = capsys.readouterr().out
    assert "not-output" not in output
    assert len(json.loads(output)["batches"]) == 3
    assert json.loads(output)["batches"][0]["batch_index"] == 0


def test_list_batches_cli_fails_closed(monkeypatch, capsys):
    def fail(*_):
        raise ValueError("private matched value must not escape")

    monkeypatch.setattr(adapter, "load_adapter", fail)
    assert (
        adapter.main(
            [
                "--list-batches",
                "--source",
                "/source",
                "--private-directory",
                "/private",
                "--gitleaks-adapter",
                "/tool",
            ]
        )
        == 2
    )
    assert "private matched value" not in capsys.readouterr().out


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
    compatibility = result["compatibility"]
    assert compatibility["stock_observations"] == (
        compatibility["matched_observations"] + compatibility["missing_adapter_observations"]
    )
    assert compatibility["adapter_observations"] == (
        compatibility["matched_observations"] + compatibility["extra_adapter_observations"]
    )
    for group in compatibility["groups"]:
        for ordinal in group["stock_ordinals"]:
            relationship = adapter.stock_relationship(source, private, Path(executable), ordinal)
            assert relationship["relationship"] == group
            assert not relationship["packer_clearance_compatible"]
    # Forged association metadata is rejected even with unchanged reports.
    complete, _ = review.read_private_json(private / "adapter-complete.json")
    original_complete = copy.deepcopy(complete)
    complete["compatibility"]["groups"][0]["association"] = "forged_origin_proof"
    (private / "adapter-complete.json").write_text(json.dumps(complete))
    with pytest.raises(ValueError, match="adapter compatibility evidence changed"):
        adapter.load_adapter(source, private, Path(executable))
    (private / "adapter-complete.json").write_text(json.dumps(original_complete))
    # Corrupting even one retained byte fails before any mapping is returned.
    request, _ = review.read_private_json(private / "adapter-request.json")
    request["bindings"]["run_namespace"] = "0" * 32
    (private / "adapter-request.json").write_text(json.dumps(request))
    with pytest.raises(ValueError):
        adapter.load_adapter(source, private, Path(executable))
