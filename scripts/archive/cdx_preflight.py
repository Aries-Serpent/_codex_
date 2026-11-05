"""Measured, private full-tree preparation. No dispositions or archive creation."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import re
import secrets
import shutil
import stat
import sys
from pathlib import Path
from typing import Any

from . import cdx_common as common
from . import cdx_review as review

MAX_FILE_BYTES = 512 * 1024 * 1024
MAX_TREE_BYTES = 4 * 1024 * 1024 * 1024
MAX_ENTRIES = 100_000
FULL_SELECTION = {
    "kind": "full_tree_preflight",
    "version": 1,
    "exclusions": [],
    "oversized_files": "block_not_skip",
    "symlinks": "record_internal_relative_links_never_follow",
}
PACKER_SELECTION = {
    "kind": "packer_defaults_not_scanned_by_this_producer",
    "denied_components": sorted(common.DEFAULT_DENIED_COMPONENTS),
    "denied_globs": sorted(common.DEFAULT_DENIED_GLOBS),
    "max_file_bytes": 8 * 1024 * 1024,
    "max_blob_bytes": common.DEFAULT_MAX_BLOB_BYTES,
}


def digest_document(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    ).hexdigest()


def _stable(info: os.stat_result) -> tuple[int, ...]:
    return (
        info.st_dev,
        info.st_ino,
        info.st_mode,
        info.st_size,
        info.st_mtime_ns,
        info.st_ctime_ns,
    )


def read_source_file(root: Path, relative: str, *, limit: int = MAX_FILE_BYTES) -> bytes:
    """Bound a regular-file read through pinned no-follow ancestor descriptors."""
    parts = relative.split("/")
    if not parts or any(part in {"", ".", ".."} for part in parts):
        raise ValueError("invalid source reference")
    directory = review._directory(root, private=False)
    try:
        for component in parts[:-1]:
            child = os.open(
                component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory
            )
            os.close(directory)
            directory = child
        fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
    finally:
        os.close(directory)
    with os.fdopen(fd, "rb") as stream:
        before = os.fstat(stream.fileno())
        if not stat.S_ISREG(before.st_mode) or before.st_size > limit:
            raise ValueError("unsupported or oversized source file")
        raw = stream.read(limit + 1)
        if len(raw) > limit or _stable(before) != _stable(os.fstat(stream.fileno())):
            raise ValueError("source changed during read")
    return raw


def measure_tree(root: Path, *, snapshot: Path | None = None) -> dict[str, Any]:
    """Fingerprint every entry using the checkpoint record format; optionally copy."""
    fingerprint = hashlib.sha256()
    count = 0
    total = 0
    root_fd = review._directory(root, private=False)
    if snapshot is not None:
        snapshot.mkdir(mode=0o700)

    def walk(directory: int, prefix: str) -> None:
        nonlocal count, total
        before = os.fstat(directory)
        children = sorted(os.listdir(directory))
        descend = []
        for name in children:
            count += 1
            if count > MAX_ENTRIES:
                raise ValueError("tree exceeds entry budget")
            relative = f"{prefix}/{name}" if prefix else name
            info = os.stat(name, dir_fd=directory, follow_symlinks=False)
            mode = stat.S_IMODE(info.st_mode)
            if mode & (stat.S_ISUID | stat.S_ISGID):
                raise ValueError("privileged source mode is unsupported")
            payload: str | None = None
            target = snapshot / relative if snapshot is not None else None
            if stat.S_ISREG(info.st_mode):
                kind = "file"
                total += info.st_size
                if total > MAX_TREE_BYTES:
                    raise ValueError("tree exceeds byte budget")
                raw = read_source_file(root, relative)
                if _stable(info) != _stable(os.stat(name, dir_fd=directory, follow_symlinks=False)):
                    raise ValueError("source entry changed during read")
                payload = hashlib.sha256(raw).hexdigest()
                if target is not None:
                    with target.open("xb") as stream:
                        stream.write(raw)
                    target.chmod(mode)
                    os.utime(target, ns=(info.st_mtime_ns, info.st_mtime_ns))
            elif stat.S_ISDIR(info.st_mode):
                kind = "dir"
                if target is not None:
                    target.mkdir(mode=0o700)
                descend.append((name, relative, info, target))
            elif stat.S_ISLNK(info.st_mode):
                kind = "symlink"
                payload = os.readlink(name, dir_fd=directory)
                resolved = (root / relative).parent.joinpath(payload).resolve()
                if os.path.isabs(payload) or not resolved.is_relative_to(root.resolve()):
                    raise ValueError("external source symlink")
                if target is not None:
                    target.symlink_to(payload)
                    os.utime(target, ns=(info.st_mtime_ns, info.st_mtime_ns), follow_symlinks=False)
            else:
                raise ValueError("unsupported source entry type")
            row = [
                relative,
                kind,
                mode,
                info.st_mtime_ns,
                0 if kind == "dir" else info.st_size,
                payload,
            ]
            fingerprint.update(
                json.dumps(row, ensure_ascii=True, separators=(",", ":")).encode() + b"\n"
            )
        for name, relative, info, target in descend:
            child = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
            try:
                if _stable(info) != _stable(os.fstat(child)):
                    raise ValueError("source directory changed")
                walk(child, relative)
            finally:
                os.close(child)
            if target is not None:
                target.chmod(stat.S_IMODE(info.st_mode))
                os.utime(target, ns=(info.st_mtime_ns, info.st_mtime_ns))
        if _stable(before) != _stable(os.fstat(directory)):
            raise ValueError("source directory changed during traversal")

    try:
        walk(root_fd, "")
    finally:
        os.close(root_fd)
    return {"sha256": fingerprint.hexdigest(), "entries": count, "file_bytes": total}


def measure_toolchain() -> dict[str, Any]:
    """Measure actual launchers, runtime, installed distributions and producer bytes."""
    tools = {}
    for name in common.SECRET_SCANNER_VERSIONS:
        executable = shutil.which(name)
        if executable is None:
            raise ValueError("both pinned scanner executables are required")
        path = Path(executable).absolute()
        raw = read_source_file(path.parent, path.name)
        tools[name] = {"path": str(path), "sha256": hashlib.sha256(raw).hexdigest()}
        if name == "detect-secrets" and raw.splitlines()[0] != ("#!" + sys.executable).encode():
            raise ValueError("detect-secrets must use the measured Python environment")
    packages = {}
    # Include the installed runtime closure, not just detect-secrets' launcher.
    for distribution in importlib.metadata.distributions():
        name = distribution.metadata["Name"]
        rows = []
        for entry in distribution.files or []:
            if ".." in entry.parts:
                continue
            path = Path(str(distribution.locate_file(entry)))
            if path.is_file():
                raw = read_source_file(path.parent, path.name)
                rows.append([str(entry), hashlib.sha256(raw).hexdigest()])
        packages[name] = digest_document(sorted(rows))
    if importlib.metadata.version("detect-secrets") != "1.5.0":
        raise ValueError("detect-secrets package version drift")
    return {
        "executables": tools,
        "python_sha256": hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(),
        "packages": packages,
        "implementation": {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (Path(__file__), Path(common.__file__), Path(review.__file__))
        },
    }


def run_preflight(source: Path, private: Path) -> dict[str, Any]:
    """Produce one measured run, with completion published last and no approval."""
    directory = review._directory(private, private=True)
    os.close(directory)
    common._validate_external_path([source], private / "complete.json", must_exist=False)
    if any(private.iterdir()):
        raise ValueError("preflight requires a new empty private directory")
    key = secrets.token_hex(32)
    review.write_checkpoint(private / "key.json", {"key": key})
    before_tools = measure_toolchain()
    snapshot = private / "snapshot"
    source_before = measure_tree(source, snapshot=snapshot)
    if measure_tree(snapshot) != source_before or measure_tree(source) != source_before:
        raise ValueError("source and exact snapshot differ")
    config = private / "gitleaks.toml"
    config.write_text("[extend]\nuseDefault = true\n")
    config.chmod(0o600)
    ignore = private / "gitleaks.ignore"
    ignore.touch(mode=0o600)
    configuration = {
        "gitleaks_config_sha256": hashlib.sha256(config.read_bytes()).hexdigest(),
        "ignore_sha256": hashlib.sha256(ignore.read_bytes()).hexdigest(),
        "gitleaks": ["dir", "--redact=100", "--ignore-gitleaks-allow", "--exit-code", "2"],
        "detect-secrets": ["scan", "--no-verify", "--all-files"],
        "environment": "isolated_home_cwd_no_pythonpath_no_user_site_no_inherited_credentials",
    }
    environment = {
        "PATH": os.environ["PATH"],
        "HOME": str(private),
        "LC_ALL": "C.UTF-8",
        "PYTHONNOUSERSITE": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    captured: dict[str, Any] = {}

    def capture(findings: list[dict[str, Any]], detector_report: dict[str, Any]) -> None:
        if (
            detector_report.get("version") != common.SECRET_SCANNER_VERSIONS["detect-secrets"]
            or not isinstance(detector_report.get("plugins_used"), list)
            or not detector_report["plugins_used"]
            or any(
                not isinstance(plugin, dict) or not isinstance(plugin.get("name"), str)
                for plugin in detector_report["plugins_used"]
            )
            or not isinstance(detector_report.get("filters_used"), list)
        ):
            raise ValueError("detector effective configuration is incomplete")
        captured.update(findings=findings, detector_report=detector_report)

    old_key = os.environ.get("CDX_FINDING_HMAC_KEY")
    os.environ["CDX_FINDING_HMAC_KEY"] = key
    try:
        try:
            common.run_secret_scanners(
                snapshot,
                inventory_path=private / "inventory.json",
                source_root=source,
                observation_sink=capture,
                scanner_environment=environment,
                scanner_directory=private,
                gitleaks_config=config,
                gitleaks_ignore=ignore,
            )
        except RuntimeError as exc:
            if str(exc) != "secret scan findings are unresolved or dispositions are stale":
                raise
    finally:
        if old_key is None:
            os.environ.pop("CDX_FINDING_HMAC_KEY", None)
        else:
            os.environ["CDX_FINDING_HMAC_KEY"] = old_key
    if (
        not captured
        or source_before != measure_tree(source)
        or source_before != measure_tree(snapshot)
        or before_tools != measure_toolchain()
        or hashlib.sha256(read_source_file(private, config.name)).hexdigest()
        != configuration["gitleaks_config_sha256"]
        or hashlib.sha256(read_source_file(private, ignore.name)).hexdigest()
        != configuration["ignore_sha256"]
    ):
        raise ValueError("preflight source, snapshot, configuration or tool drift")
    inventory, inventory_digest = review.read_private_json(private / "inventory.json")
    configuration["detector_plugins"] = captured["detector_report"].get("plugins_used")
    configuration["detector_filters"] = captured["detector_report"].get("filters_used")
    bindings = {
        "identity_version": common.FINDING_IDENTITY_VERSION,
        "run_namespace": secrets.token_hex(16),
        "source_sha256": source_before["sha256"],
        "selection_sha256": digest_document(FULL_SELECTION),
        "config_sha256": digest_document(configuration),
        "toolchain_sha256": digest_document(before_tools),
    }
    queue = review.build_queue(inventory, inventory_digest, bindings)
    provenance = {
        "purpose": "measured_local_producer_not_external_authentication",
        "source": source_before,
        "selection": FULL_SELECTION,
        "packer_selection": PACKER_SELECTION,
        "toolchain": before_tools,
        "configuration": configuration,
        "retention": "owner_only_session_nondurable",
        "quiescence": "endpoint_and_per_read_checks_not_os_snapshot_isolation",
    }
    captured.update(bindings=bindings, inventory_sha256=inventory_digest)
    artifacts = {}
    for name, document in (
        ("observations.json", captured),
        ("provenance.json", provenance),
        ("bindings.json", bindings),
        ("queue.json", queue),
    ):
        artifacts[name] = review.write_checkpoint(private / name, document)
    complete = {
        "bindings": bindings,
        "source": source_before,
        "inventory_sha256": inventory_digest,
        "artifacts": artifacts,
        "counts": review.queue_summary(queue),
        "scanner_execution": "both_completed",
        "clearance": "BLOCKED_FINDINGS" if inventory["findings"] else "clean_preflight_only",
        "archive_created": False,
    }
    review.write_checkpoint(private / "complete.json", complete)
    return complete


def load_preflight(source: Path, private: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    """Recheck a locally produced bundle; integrity never implies reviewer authority."""
    complete, _ = review.read_private_json(private / "complete.json")
    documents = {}
    for name in ("observations.json", "provenance.json", "bindings.json", "queue.json"):
        document, digest = review.read_private_json(private / name)
        if digest != complete["artifacts"][name]:
            raise ValueError("private artifact changed")
        documents[name] = document
    inventory, inventory_digest = review.read_private_json(private / "inventory.json")
    observations = documents["observations.json"]
    bindings = documents["bindings.json"]
    provenance = documents["provenance.json"]
    if (
        inventory_digest != complete["inventory_sha256"]
        or observations["inventory_sha256"] != inventory_digest
        or observations["bindings"] != bindings
        or complete["bindings"] != bindings
        or bindings["source_sha256"] != complete["source"]["sha256"]
        or bindings["selection_sha256"] != digest_document(FULL_SELECTION)
        or bindings["config_sha256"] != digest_document(provenance["configuration"])
        or hashlib.sha256(read_source_file(private, "gitleaks.toml")).hexdigest()
        != provenance["configuration"]["gitleaks_config_sha256"]
        or hashlib.sha256(read_source_file(private, "gitleaks.ignore")).hexdigest()
        != provenance["configuration"]["ignore_sha256"]
        or bindings["toolchain_sha256"] != digest_document(provenance["toolchain"])
        or bindings["toolchain_sha256"] != digest_document(measure_toolchain())
        or complete["source"] != measure_tree(source)
        or complete["source"] != measure_tree(private / "snapshot")
    ):
        raise ValueError("current private run binding mismatch")
    review.build_queue(inventory, inventory_digest, bindings, previous=documents["queue.json"])
    key_document, _ = review.read_private_json(private / "key.json")
    key = key_document["key"].encode()
    if len(key) < 32 or len(observations["findings"]) != len(inventory["findings"]):
        raise ValueError("missing exact private observation context")
    rows = {row["finding_id"]: row for row in review.validate_inventory(inventory)}
    seen = set()
    for finding in observations["findings"]:
        identity = common._finding_id(key, finding)
        if (
            identity in seen
            or identity not in rows
            or finding["finding_id"] != identity
            or {field: finding[field] for field in review.FINDING_FIELDS} != rows[identity]
        ):
            raise ValueError("stale or unmatched private observation")
        seen.add(identity)
    return complete, observations


def assess_batch(source: Path, private: Path) -> dict[str, Any]:
    """Inspect at most 16 observations per scanner offline; never assert harmlessness."""
    # Imports are lazy so preparation does not require optional scanner dependencies.
    from detect_secrets.settings import get_plugins, transient_settings

    complete, observations = load_preflight(source, private)
    selected = []
    for scanner in common.SECRET_SCANNER_VERSIONS:
        selected.extend([row for row in observations["findings"] if row["scanner"] == scanner][:16])
    assessments = []
    for finding in selected:
        raw = read_source_file(private / "snapshot", finding["path"])
        if hashlib.sha256(raw).hexdigest() != finding["file_sha256"]:
            raise ValueError("observation source changed")
        lines = raw.splitlines()
        start, end = finding["start_line"], finding["end_line"]
        if end > len(lines) or end - start > 100:
            raise ValueError("unavailable or oversized observation context")
        context = b"\n".join(lines[max(0, start - 3) : min(len(lines), end + 2)])
        if len(context) > 65536:
            raise ValueError("observation context exceeds private assessment budget")
        predicates: dict[str, Any] = {
            "credential_assignment_syntax": bool(
                re.search(rb"(?i)(?:token|secret|password|api[_-]?key)\s*[=:]", context)
            ),
            "private_key_structure": bool(
                re.search(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", context)
            ),
        }
        gap = "exact_harmlessness_and_authenticated_independent_review_unavailable"
        if finding["scanner"] == "detect-secrets":
            # Empty filters ensure analyze_line cannot call credential verification.
            with transient_settings(
                {
                    "plugins_used": observations["detector_report"]["plugins_used"],
                    "filters_used": [],
                }
            ):
                matches = []
                for plugin in get_plugins():
                    if plugin.secret_type == finding["rule"]:
                        matches.extend(
                            plugin.analyze_line(
                                filename=finding["path"],
                                line=lines[start - 1].decode("utf-8"),
                                line_number=start,
                            )
                        )
                predicates["detector_exact_replay_match"] = any(
                    match.secret_hash == finding["_record"].get("hashed_secret")
                    for match in matches
                )
                if not predicates["detector_exact_replay_match"]:
                    gap = "exact_detector_replay_unmatched_no_harmlessness_proof"
        else:
            record = finding["_record"]
            left, right = record.get("StartColumn"), record.get("EndColumn")
            supported = (
                start == end
                and type(left) is int
                and type(right) is int
                and 1 <= left <= right <= len(lines[start - 1])
                and lines[start - 1].isascii()
            )
            predicates["ascii_single_line_span_available"] = supported
            if not supported:
                gap = "redacted_or_multiline_span_requires_exact_private_detector_context"
        assessments.append(
            {
                "finding_id": finding["finding_id"],
                "scanner": finding["scanner"],
                "state": "indeterminate",
                "predicates": predicates,
                "evidence_gap": gap,
                "raw_context_status": "inspected_privately_not_exported",
                "exact_false_positive_evidence": "insufficient",
            }
        )
    # Revalidate after inspection, before recording any advisory state transition.
    load_preflight(source, private)
    batch = {
        "bindings": complete["bindings"],
        "inventory_sha256": complete["inventory_sha256"],
        "purpose": "private_assessment_not_approval",
        "selection": "first_16_per_scanner_in_bound_inventory_order",
        "assessments": assessments,
    }
    batch_digest = review.write_checkpoint(private / "batch-001.json", batch)
    queue, _ = review.read_private_json(private / "queue.json")
    assigned = {row["finding_id"] for row in assessments}
    for row in queue["observations"]:
        if row["finding_id"] in assigned:
            row["state"] = "indeterminate"
    inventory, inventory_digest = review.read_private_json(private / "inventory.json")
    queue = review.build_queue(inventory, inventory_digest, complete["bindings"], previous=queue)
    review.write_checkpoint(private / "queue-001.json", queue)
    return {
        "assigned": len(assessments),
        "assessed": len(assessments),
        "batch_sha256": batch_digest,
        "counts": review.queue_summary(queue),
        "accepted": 0,
        "semantic_false_positive_proofs": 0,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--private-directory", required=True, type=Path)
    parser.add_argument("--assess-first-batch", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = run_preflight(args.source, args.private_directory)
        if args.assess_first_batch:
            result["batch"] = assess_batch(args.source, args.private_directory)
    except Exception:
        # Scanner diagnostics, private paths and parsed values must not escape.
        print("BLOCKED: private preparation, scanner execution or binding verification failed")
        return 2
    print(json.dumps(result, sort_keys=True))
    return 2 if result["clearance"] == "BLOCKED_FINDINGS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
