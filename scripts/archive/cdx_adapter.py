"""Acquisition-bound advisory adapter; never a disposition or packer scan."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import stat
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from . import cdx_common as common
from . import cdx_preflight as preflight
from . import cdx_review as review

MODULE = "github.com/zricethezav/gitleaks/v8"
VERSION = "v8.30.1"
MODULE_SUM = "h1:PmEvCfVI7ti9dV3s5aMZUY7sS2GxRvG3yzih7E+cS3w="
MODE = "cdx-full-file-v1"
LIMITS = {"file_bytes": 8 * 1024 * 1024, "tree_bytes": 256 * 1024 * 1024, "files": 10000}
CONFIGURATION = {
    "mode": MODE,
    "limits": LIMITS,
    "encoding": "utf8_lf_crlf_no_nul_bare_cr_blocks_not_skips",
    "fragment": "one_acquired_full_file_per_regular_file",
    "ignore_gitleaks_allow": True,
    "decode_depth": 0,
    "archive_depth": 0,
    "deadline_seconds": 120,
    "process_timeout_seconds": 150,
    "address_space_bytes": 4 * 1024 * 1024 * 1024,
    "soft_memory_bytes": 512 * 1024 * 1024,
    "report_bytes": review.MAX_DOCUMENT_BYTES,
    "findings": review.MAX_FINDINGS,
    "symlinks": "maintained_snapshot_records_internal_links_never_follow",
    "built_in_heuristics_and_allowlists": "unchanged_pinned_library",
}


def _execute(executable: Path, private: Path, payload: bytes | None = None) -> bytes:
    arguments = [str(executable)] + (["identity"] if payload is None else [])
    completed = subprocess.run(
        arguments,
        input=payload,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=150,
        check=False,
        cwd=private,
        env={"PATH": os.defpath, "HOME": str(private), "LC_ALL": "C.UTF-8"},
    )
    if completed.returncode != 0 or completed.stderr:
        raise ValueError("adapter execution failed")
    if len(completed.stdout) > review.MAX_DOCUMENT_BYTES:
        raise ValueError("adapter report exceeded limit")
    return completed.stdout


def _parse(raw: bytes) -> dict[str, Any]:
    document = json.loads(
        raw, object_pairs_hook=review._pairs, parse_constant=review._reject_constant
    )
    if not isinstance(document, dict):
        raise ValueError("invalid adapter document")
    return document


def measure_adapter(executable: Path, private: Path) -> dict[str, Any]:
    if not executable.is_absolute():
        raise ValueError("absolute adapter executable required")
    raw = preflight.read_source_file(executable.parent, executable.name)
    identity = _parse(_execute(executable, private))
    if (
        set(identity)
        != {"mode", "module", "version", "module_sum", "executable_sha256", "config_sha256"}
        or identity["mode"] != MODE
        or identity["module"] != MODULE
        or identity["version"] != VERSION
        or identity["module_sum"] != MODULE_SUM
        or identity["executable_sha256"] != hashlib.sha256(raw).hexdigest()
        or not review._digest(identity["config_sha256"])
    ):
        raise ValueError("adapter measured provenance mismatch")
    return identity


def _manifest(snapshot: Path) -> list[dict[str, Any]]:
    files: list[dict[str, Any]] = []
    total = 0
    for _, relative, info in common.iter_deterministic_tree(snapshot, set(), set()):
        if not stat.S_ISREG(info.st_mode):
            continue
        total += info.st_size
        if (
            info.st_size > LIMITS["file_bytes"]
            or total > LIMITS["tree_bytes"]
            or len(files) >= LIMITS["files"]
            or info.st_nlink != 1
        ):
            raise ValueError("adapter selection exceeds supported budget")
        raw = preflight.read_source_file(snapshot, relative, limit=LIMITS["file_bytes"])
        files.append(
            {"path": relative, "size": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
        )
    return sorted(files, key=lambda row: row["path"])


def _toolchain_binding(stock: str, identity: dict[str, Any]) -> str:
    return preflight.digest_document(
        {
            "stock": stock,
            "adapter": identity,
            "consumer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        }
    )


def _compatibility(stock: list[dict[str, Any]], acquired: list[dict[str, Any]]) -> dict[str, Any]:
    """Account for every occurrence; record equality never establishes byte origin."""

    def records(
        findings: list[dict[str, Any]],
    ) -> tuple[Counter[str], dict[str, list[int]], dict[str, str]]:
        counts: Counter[str] = Counter()
        ordinals: dict[str, list[int]] = defaultdict(list)
        digests = {}
        for ordinal, finding in enumerate(findings):
            if finding["scanner"] != "gitleaks":
                continue
            record = finding["_record"]
            canonical = common._canonical_scanner_finding(
                "gitleaks",
                finding["scanner_version"],
                finding["path"],
                finding["file_sha256"],
                record,
            )
            if (
                finding["scanner_version"] != common.SECRET_SCANNER_VERSIONS["gitleaks"]
                or not review._digest(finding["file_sha256"])
                or any(finding[field] != value for field, value in canonical.items())
                or record.get("File") != finding["path"]
            ):
                raise ValueError("invalid reconciliation observation")
            record_digest = preflight.digest_document(record)
            identity = preflight.digest_document(
                {
                    "scanner_version": finding["scanner_version"],
                    "path": finding["path"],
                    "file_sha256": finding["file_sha256"],
                    "record_sha256": record_digest,
                }
            )
            counts[identity] += 1
            ordinals[identity].append(ordinal)
            digests[identity] = record_digest
        return counts, ordinals, digests

    stock_records, stock_ordinals, stock_digests = records(stock)
    acquired_records, acquired_ordinals, acquired_digests = records(acquired)
    equal = stock_records == acquired_records
    groups = []
    for identity in sorted(stock_records.keys() | acquired_records.keys()):
        left, right = stock_ordinals.get(identity, []), acquired_ordinals.get(identity, [])
        association = (
            "ambiguous_duplicates"
            if len(left) > 1 or len(right) > 1
            else (
                "unique_exact_record"
                if left and right
                else "stock_only" if left else "adapter_only"
            )
        )
        groups.append(
            {
                "identity_sha256": identity,
                "record_sha256": stock_digests.get(identity) or acquired_digests[identity],
                "stock_ordinals": left,
                "adapter_ordinals": right,
                "association": association,
            }
        )
    return {
        "reconciliation_version": 1,
        "ordinal_basis": "separate_loaded_stock_and_adapter_finding_lists_zero_based",
        "stock_observations": sum(stock_records.values()),
        "adapter_observations": sum(acquired_records.values()),
        "matched_observations": sum((stock_records & acquired_records).values()),
        "missing_adapter_observations": sum((stock_records - acquired_records).values()),
        "extra_adapter_observations": sum((acquired_records - stock_records).values()),
        "stock_duplicate_observations": sum(count - 1 for count in stock_records.values()),
        "adapter_duplicate_observations": sum(count - 1 for count in acquired_records.values()),
        "unique_exact_associations": sum(
            group["association"] == "unique_exact_record" for group in groups
        ),
        "groups": groups,
        "exact_record_multiset_equal": equal,
        "assessment": (
            "equal_this_snapshot_only" if equal else "BLOCKED_CONTEXT_OR_COVERAGE_DIVERGENCE"
        ),
        "packer_clearance_compatible": False,
        "reason": "adapter_namespace_never_authorizes_stock_independent_snapshot_rescan",
        "proof": "record_association_only_not_stock_fragment_origin_use_or_harmlessness",
    }


def _validate_report(
    snapshot: Path,
    request: dict[str, Any],
    request_digest: str,
    report: dict[str, Any],
    identity: dict[str, Any],
) -> list[dict[str, Any]]:
    if (
        set(report)
        != set(identity) | {"schema_version", "request_sha256", "bindings", "acquisitions"}
        or report["schema_version"] != 1
        or type(report["schema_version"]) is not int
        or any(report[field] != value for field, value in identity.items())
        or report["request_sha256"] != request_digest
        or report["bindings"] != request["bindings"]
        or not isinstance(report["acquisitions"], list)
        or len(report["acquisitions"]) != len(request["files"])
    ):
        raise ValueError("adapter invocation binding mismatch")
    key = bytes.fromhex(request["key"])
    findings = []
    mapped_bytes = 0
    for expected, acquired in zip(request["files"], report["acquisitions"], strict=True):
        if (
            not isinstance(acquired, dict)
            or set(acquired)
            != {
                "path",
                "sha256",
                "size",
                "origin_start",
                "origin_end",
                "detector_calls",
                "observations",
            }
            or any(acquired[field] != value for field, value in expected.items())
            or type(acquired["origin_start"]) is not int
            or acquired["origin_start"] != 0
            or type(acquired["origin_end"]) is not int
            or acquired["origin_end"] != expected["size"]
            or type(acquired["detector_calls"]) is not int
            or acquired["detector_calls"] != 1
            or not isinstance(acquired["observations"], list)
        ):
            raise ValueError("adapter acquisition mismatch")
        raw = preflight.read_source_file(snapshot, expected["path"], limit=LIMITS["file_bytes"])
        if len(raw) != expected["size"] or hashlib.sha256(raw).hexdigest() != expected["sha256"]:
            raise ValueError("adapter acquired source changed")
        raw.decode("utf-8")
        origins = [0] + [index for index, value in enumerate(raw) if value == 10]
        for ordinal, observation in enumerate(acquired["observations"]):
            if (
                not isinstance(observation, dict)
                or set(observation) != {"record", "start", "end", "match_hmac", "mapping_status"}
                or not isinstance(observation["record"], dict)
            ):
                raise ValueError("invalid adapter observation")
            record = observation["record"]
            if record.get("File") != expected["path"] or record.get("Fragment") is not None:
                raise ValueError("adapter observation source mismatch")
            finding = common._canonical_scanner_finding(
                "gitleaks", "8.30.1", expected["path"], expected["sha256"], record
            )
            start, end = observation["start"], observation["end"]
            status = observation["mapping_status"]
            if status == "mapped_acquired_full_file":
                line, column = record.get("StartLine"), record.get("StartColumn")
                if type(start) is int and type(end) is int:
                    mapped_bytes += end - start
                if (
                    type(start) is not int
                    or type(end) is not int
                    or not 0 <= start < end <= len(raw)
                    or type(line) is not int
                    or type(column) is not int
                    or not 1 <= line <= len(origins)
                    or column < 1
                    or start != origins[line - 1] + column - 1
                    or mapped_bytes > LIMITS["tree_bytes"]
                    or not isinstance(observation["match_hmac"], str)
                    or not hmac.compare_digest(
                        observation["match_hmac"],
                        hmac.new(key, raw[start:end], hashlib.sha256).hexdigest(),
                    )
                ):
                    raise ValueError("adapter observed span mismatch")
                # The whole acquisition was decoded once; boundaries cannot split a rune.
                if raw[start] & 0xC0 == 0x80 or (end < len(raw) and raw[end] & 0xC0 == 0x80):
                    raise ValueError("adapter span splits UTF-8 code point")
            elif status not in {"unsupported_coordinates", "unsupported_match_interval"} or (
                start != 0 or end != 0 or observation["match_hmac"] != ""
            ):
                raise ValueError("invalid unsupported adapter mapping")
            if record.get("Secret") != "REDACTED":
                raise ValueError("adapter returned unredacted observation")
            origin = {
                "mode": MODE,
                "invocation": request["bindings"],
                "ordinal": ordinal,
                "file_sha256": expected["sha256"],
                "origin_start": 0,
                "origin_end": len(raw),
                "start": start,
                "end": end,
                "match_hmac": observation["match_hmac"],
                "mapping_status": status,
            }
            finding["_acquisition"] = origin
            finding["finding_id"] = hmac.new(
                key,
                json.dumps(
                    {"origin": origin, "record": finding["_record"]}, sort_keys=True
                ).encode(),
                hashlib.sha256,
            ).hexdigest()
            findings.append(finding)
            if len(findings) > review.MAX_FINDINGS:
                raise ValueError("adapter observation budget exceeded")
    return findings


def run_adapter(source: Path, private: Path, executable: Path) -> dict[str, Any]:
    """Supplement an actual maintained preflight; publish adapter completion last."""
    if not source.is_absolute() or not private.is_absolute():
        raise ValueError("absolute adapter source and private directory required")
    for name in (
        "adapter-request.json",
        "adapter-report.json",
        "adapter-complete.json",
        "adapter-failure.json",
    ):
        try:
            (private / name).lstat()
        except FileNotFoundError:
            continue
        raise FileExistsError("adapter history already exists")
    complete, stock = preflight.load_preflight(source, private)
    try:
        return _run_adapter(source, private, executable, complete, stock)
    except Exception:
        review.write_checkpoint(
            private / "adapter-failure.json",
            {
                "status": "BLOCKED_ADAPTER",
                "stock_preflight_separate": True,
                "adapter_completed": False,
                "archive_created": False,
            },
        )
        raise


def _run_adapter(
    source: Path, private: Path, executable: Path, complete: dict[str, Any], stock: dict[str, Any]
) -> dict[str, Any]:
    identity = measure_adapter(executable, private)
    request: dict[str, Any] = {
        "schema_version": 1,
        "source": str(private / "snapshot"),
        "bindings": {
            "run_namespace": secrets.token_hex(16),
            "source_sha256": complete["source"]["sha256"],
            "selection_sha256": preflight.digest_document(preflight.FULL_SELECTION),
            "config_sha256": preflight.digest_document(
                {"configuration": CONFIGURATION, "identity": identity}
            ),
            "toolchain_sha256": _toolchain_binding(
                complete["bindings"]["toolchain_sha256"], identity
            ),
        },
        "key": secrets.token_hex(32),
        "files": _manifest(private / "snapshot"),
    }
    request_digest = review.write_checkpoint(private / "adapter-request.json", request)
    raw_request = preflight.read_source_file(private, "adapter-request.json")
    report = _parse(_execute(executable, private, raw_request))
    findings = _validate_report(private / "snapshot", request, request_digest, report, identity)
    report_digest = review.write_checkpoint(private / "adapter-report.json", report)
    if (
        preflight.load_preflight(source, private)[0] != complete
        or measure_adapter(executable, private) != identity
        or review.read_private_json(private / "adapter-request.json")[1] != request_digest
    ):
        raise ValueError("adapter post-execution binding drift")
    summary = {
        "purpose": "acquisition_localization_not_origin_use_or_false_positive_proof",
        "bindings": request["bindings"],
        "identity": identity,
        "stock_bindings": complete["bindings"],
        "request_sha256": request_digest,
        "report_sha256": report_digest,
        "configuration": CONFIGURATION,
        "files": len(request["files"]),
        "detector_calls": len(request["files"]),
        "observations": len(findings),
        "mapped": sum(
            row["_acquisition"]["mapping_status"] == "mapped_acquired_full_file" for row in findings
        ),
        "compatibility": _compatibility(stock["findings"], findings),
        "approval": "unavailable",
        "archive_created": False,
        "retention": "owner_only_session_nondurable",
        "trust": "measured_local_execution_not_same_user_isolation_or_external_authentication",
    }
    summary["checkpoint_sha256"] = review.write_checkpoint(
        private / "adapter-complete.json", summary
    )
    return summary


def load_adapter(
    source: Path, private: Path, executable: Path
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Recheck execution-bound artifacts, not caller-selected standalone origins."""
    stock_complete, stock = preflight.load_preflight(source, private)
    complete, _ = review.read_private_json(private / "adapter-complete.json")
    request, request_digest = review.read_private_json(private / "adapter-request.json")
    report, report_digest = review.read_private_json(private / "adapter-report.json")
    identity = measure_adapter(executable, private)
    if (
        complete["stock_bindings"] != stock_complete["bindings"]
        or complete["bindings"] != request["bindings"]
        or request["source"] != str(private / "snapshot")
        or request["files"] != _manifest(private / "snapshot")
        or request["bindings"]["source_sha256"] != stock_complete["source"]["sha256"]
        or request["bindings"]["selection_sha256"]
        != preflight.digest_document(preflight.FULL_SELECTION)
        or request["bindings"]["config_sha256"]
        != preflight.digest_document({"configuration": CONFIGURATION, "identity": identity})
        or request["bindings"]["toolchain_sha256"]
        != _toolchain_binding(stock_complete["bindings"]["toolchain_sha256"], identity)
        or complete["request_sha256"] != request_digest
        or complete["report_sha256"] != report_digest
        or complete["identity"] != identity
        or complete["configuration"] != CONFIGURATION
    ):
        raise ValueError("current adapter run binding mismatch")
    findings = _validate_report(private / "snapshot", request, request_digest, report, identity)
    if (
        complete["compatibility"] != _compatibility(stock["findings"], findings)
        or complete["files"] != len(request["files"])
        or complete["detector_calls"] != len(request["files"])
        or complete["observations"] != len(findings)
        or complete["mapped"]
        != sum(
            row["_acquisition"]["mapping_status"] == "mapped_acquired_full_file" for row in findings
        )
    ):
        raise ValueError("adapter compatibility evidence changed")
    return complete, findings


def stock_relationship(
    source: Path, private: Path, executable: Path, stock_ordinal: int
) -> dict[str, Any]:
    """Return a private, freshly reverified relationship, never a stock byte span."""
    if type(stock_ordinal) is not int or stock_ordinal < 0:
        raise ValueError("invalid stock observation ordinal")
    complete, _ = load_adapter(source, private, executable)
    selected = [
        group
        for group in complete["compatibility"]["groups"]
        if stock_ordinal in group["stock_ordinals"]
    ]
    if len(selected) != 1:
        raise ValueError("unmatched stock observation ordinal")
    return {
        "stock_bindings": complete["stock_bindings"],
        "adapter_bindings": complete["bindings"],
        "relationship": selected[0],
        "proof": complete["compatibility"]["proof"],
        "packer_clearance_compatible": False,
    }


def acquired_span(
    source: Path, private: Path, executable: Path, finding_id: str
) -> tuple[bytes | None, str]:
    """Consume only an observation loaded from a reverified actual adapter run."""
    _, findings = load_adapter(source, private, executable)
    selected = [finding for finding in findings if finding["finding_id"] == finding_id]
    if len(selected) != 1:
        raise ValueError("unmatched adapter observation")
    finding = selected[0]
    origin = finding["_acquisition"]
    if origin["mapping_status"] != "mapped_acquired_full_file":
        return None, origin["mapping_status"]
    raw = preflight.read_source_file(
        private / "snapshot", finding["path"], limit=LIMITS["file_bytes"]
    )
    request, _ = review.read_private_json(private / "adapter-request.json")
    if hashlib.sha256(raw).hexdigest() != finding["file_sha256"] or not hmac.compare_digest(
        origin["match_hmac"],
        hmac.new(
            bytes.fromhex(request["key"]), raw[origin["start"] : origin["end"]], hashlib.sha256
        ).hexdigest(),
    ):
        raise ValueError("adapter source changed before returning span")
    return raw[origin["start"] : origin["end"]], origin["mapping_status"]
