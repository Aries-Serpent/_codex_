"""Private advisory observation queues; never authorize scanner dispositions."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import secrets
import stat
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any

from .cdx_common import (
    FINDING_IDENTITY_VERSION,
    SECRET_SCANNER_VERSIONS,
    _validate_external_path,
)

MAX_DOCUMENT_BYTES = 16 * 1024 * 1024
MAX_FINDINGS = 50_000
FINDING_FIELDS = {
    "scanner",
    "scanner_version",
    "finding_id",
    "path",
    "file_sha256",
    "rule",
    "start_line",
    "end_line",
}
BINDING_FIELDS = {
    "identity_version",
    "run_namespace",
    "source_sha256",
    "selection_sha256",
    "toolchain_sha256",
    "config_sha256",
}
REVIEW_STATES = (
    "unreviewed",
    "evidenced_false_positive_awaiting_review",
    "accepted_exact_false_positive",
    "suspected_sensitive",
    "indeterminate",
    "stale_or_unmatched",
)
RESUMABLE_STATES = {
    "unreviewed",
    "suspected_sensitive",
    "indeterminate",
    "stale_or_unmatched",
}


def _digest(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def _directory(path: Path, *, private: bool) -> int:
    """Open each directory without following symlinks, including ancestors."""
    absolute = Path(os.path.abspath(path))
    fd = os.open("/", os.O_RDONLY | os.O_DIRECTORY)
    try:
        for component in absolute.parts[1:]:
            next_fd = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = next_fd
        info = os.fstat(fd)
        if info.st_uid != os.getuid() or (private and info.st_mode & 0o077):
            raise ValueError("artifact directory is not owner-private")
        return fd
    except BaseException:
        os.close(fd)
        raise


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate document key")
        result[key] = value
    return result


def _reject_constant(_value: str) -> Any:
    raise ValueError("invalid JSON constant")


def read_private_json(path: Path) -> tuple[dict[str, Any], str]:
    """Bound reads from an owner-only regular file in a private directory."""
    directory = _directory(path.parent, private=True)
    try:
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
    finally:
        os.close(directory)
    with os.fdopen(fd, "rb") as stream:
        before = os.fstat(stream.fileno())
        if (
            not stat.S_ISREG(before.st_mode)
            or before.st_uid != os.getuid()
            or before.st_mode & 0o077
            or before.st_nlink != 1
            or before.st_size > MAX_DOCUMENT_BYTES
        ):
            raise ValueError("artifact is not a bounded private regular file")
        raw = stream.read(MAX_DOCUMENT_BYTES + 1)
        after = os.fstat(stream.fileno())
        if len(raw) > MAX_DOCUMENT_BYTES or (
            before.st_size,
            before.st_mtime_ns,
            before.st_ctime_ns,
        ) != (after.st_size, after.st_mtime_ns, after.st_ctime_ns):
            raise ValueError("artifact changed or exceeded size limit")
    try:
        document = json.loads(raw, object_pairs_hook=_pairs, parse_constant=_reject_constant)
    except (ValueError, RecursionError) as exc:
        raise ValueError("invalid private JSON document") from exc
    if not isinstance(document, dict):
        raise ValueError("invalid private document shape")
    return document, hashlib.sha256(raw).hexdigest()


def validate_inventory(document: dict[str, Any]) -> list[dict[str, Any]]:
    if (
        set(document) != {"schema_version", "findings"}
        or type(document["schema_version"]) is not int
        or document["schema_version"] != 1
        or not isinstance(document["findings"], list)
        or len(document["findings"]) > MAX_FINDINGS
    ):
        raise ValueError("invalid inventory schema")
    seen = set()
    for row in document["findings"]:
        if not isinstance(row, dict) or set(row) != FINDING_FIELDS:
            raise ValueError("invalid finding fields")
        scanner = row["scanner"]
        if not isinstance(scanner, str) or (
            scanner not in SECRET_SCANNER_VERSIONS
            or row["scanner_version"] != SECRET_SCANNER_VERSIONS[scanner]
        ):
            raise ValueError("invalid scanner binding")
        if not _digest(row["finding_id"]) or not _digest(row["file_sha256"]):
            raise ValueError("invalid finding identity")
        path = row["path"]
        if (
            not isinstance(path, str)
            or not path
            or len(path) > 4096
            or "\\" in path
            or ":" in path
            or PurePosixPath(path).is_absolute()
            or any(part in {"", ".", ".."} for part in path.split("/"))
            or any(ord(char) < 32 for char in path)
        ):
            raise ValueError("invalid finding path")
        if (
            not isinstance(row["rule"], str)
            or not row["rule"]
            or len(row["rule"]) > 256
            or any(ord(char) < 32 for char in row["rule"])
            or type(row["start_line"]) is not int
            or row["start_line"] < 1
            or type(row["end_line"]) is not int
            or row["end_line"] < row["start_line"]
        ):
            raise ValueError("invalid finding location")
        if row["finding_id"] in seen:
            raise ValueError("duplicate observation identity")
        seen.add(row["finding_id"])
    return document["findings"]


def build_queue(
    inventory: dict[str, Any],
    inventory_sha256: str,
    bindings: dict[str, Any],
    *,
    previous: dict[str, Any] | None = None,
    source_kind: str = "real",
) -> dict[str, Any]:
    """Resume scheduling only; reject evidence/approval claims and stale context."""
    rows = validate_inventory(inventory)
    if set(bindings) != BINDING_FIELDS or (
        not isinstance(bindings["run_namespace"], str)
        or re.fullmatch(r"[0-9a-f]{32}", bindings["run_namespace"]) is None
        or type(bindings["identity_version"]) is not int
        or bindings["identity_version"] != FINDING_IDENTITY_VERSION
        or any(
            not _digest(bindings[field])
            for field in BINDING_FIELDS - {"run_namespace", "identity_version"}
        )
        or not _digest(inventory_sha256)
        or source_kind not in {"real", "synthetic"}
    ):
        raise ValueError("invalid run bindings")
    queue = {
        "schema_version": 1,
        "purpose": "advisory_only_not_clearance",
        "source_kind": source_kind,
        "bindings": dict(bindings),
        "inventory_sha256": inventory_sha256,
        "observations": [dict(row, state="unreviewed") for row in rows],
    }
    if previous is not None:
        if set(previous) != set(queue) or any(
            previous[field] != queue[field] for field in queue if field != "observations"
        ):
            raise ValueError("stale queue bindings")
        observations = previous["observations"]
        if not isinstance(observations, list) or len(observations) != len(rows):
            raise ValueError("incomplete queue coverage")
        by_id = {row["finding_id"]: row for row in rows}
        seen = set()
        for row in observations:
            if not isinstance(row, dict) or set(row) != FINDING_FIELDS | {"state"}:
                raise ValueError("invalid queue observation")
            identity = row["finding_id"]
            if (
                not isinstance(identity, str)
                or identity in seen
                or identity not in by_id
                or {field: row[field] for field in FINDING_FIELDS} != by_id[identity]
                or not isinstance(row["state"], str)
                or row["state"] not in RESUMABLE_STATES
            ):
                raise ValueError("unmatched observation or unsupported review claim")
            seen.add(identity)
        queue["observations"] = [dict(row) for row in observations]
    return queue


def queue_summary(queue: dict[str, Any]) -> dict[str, Any]:
    observations = queue["observations"]
    scanner_counts = Counter(row["scanner"] for row in observations)
    states = Counter(row["state"] for row in observations)
    return {
        "observed_total": len(observations),
        "by_scanner": {name: scanner_counts[name] for name in SECRET_SCANNER_VERSIONS},
        "by_state": {state: states[state] for state in REVIEW_STATES},
        "clearance": "not_evaluated",
    }


def write_checkpoint(path: Path, document: dict[str, Any], *, private: bool = True) -> str:
    """Publish a complete new checkpoint atomically; never overwrite history."""
    raw = (json.dumps(document, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()
    if len(raw) > MAX_DOCUMENT_BYTES:
        raise ValueError("checkpoint exceeds size limit")
    directory = _directory(path.parent, private=private)
    temporary = None
    created = False
    try:
        temporary = ".cdx-checkpoint-" + secrets.token_hex(16)
        fd = os.open(
            temporary,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
            0o600,
            dir_fd=directory,
        )
        created = True
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(
            temporary,
            path.name,
            src_dir_fd=directory,
            dst_dir_fd=directory,
            follow_symlinks=False,
        )
        os.fsync(directory)
    finally:
        try:
            if created and temporary is not None:
                os.unlink(temporary, dir_fd=directory)
                os.fsync(directory)
        finally:
            os.close(directory)
    return hashlib.sha256(raw).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--inventory", required=True, type=Path)
    parser.add_argument("--bindings", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--resume", type=Path)
    args = parser.parse_args(argv)
    try:
        source = args.source.resolve(strict=True)
        if not source.is_dir():
            raise ValueError("invalid source")
        for path in (args.inventory, args.bindings, args.resume):
            if path is not None:
                _validate_external_path([source], path, must_exist=True)
        _validate_external_path([source], args.output, must_exist=False)
        inventory, digest = read_private_json(args.inventory)
        bindings, _ = read_private_json(args.bindings)
        previous = read_private_json(args.resume)[0] if args.resume else None
        queue = build_queue(inventory, digest, bindings, previous=previous)
        checkpoint_digest = write_checkpoint(args.output, queue)
    except (OSError, ValueError, TypeError, RecursionError, RuntimeError):
        print("BLOCKED: private queue input, binding or checkpoint validation failed")
        return 2
    print(
        json.dumps(queue_summary(queue) | {"checkpoint_sha256": checkpoint_digest}, sort_keys=True)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
