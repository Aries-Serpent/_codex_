"""Previewed, local candidate persistence; never governance adoption."""

from __future__ import annotations

import os
import re
import secrets
from contextlib import ExitStack
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

from .core import (
    MAX_BYTES,
    NAMESPACE,
    Rejected,
    canonical,
    contracts,
    digest,
    inspect_candidate,
    load,
    validate,
    verify,
)


def installation() -> dict[str, Any]:
    try:
        installed = version("codex-ml")
    except PackageNotFoundError:
        installed = "source-uninstalled"
    return {
        "namespace": NAMESPACE,
        "package": "codex-ml",
        "version": installed,
        "contracts_digest": digest(contracts()),
    }


def safe_root(root: Path) -> Path:
    root = root.resolve(strict=True)
    for path in (root / ".codex", root / NAMESPACE):
        if path.is_symlink():
            raise Rejected("UNSAFE_NAMESPACE", 7)
        if path.exists() and not path.is_dir():
            raise Rejected("NAMESPACE_COLLISION", 7)
    return root


def plan(root: Path, value: dict[str, Any], expected: str | None = None) -> dict[str, Any]:
    validate(value)
    findings = inspect_candidate(value)
    if findings:
        raise Rejected("INVALID_CANDIDATE:" + ",".join(findings))
    root = safe_root(root)
    ns = root / NAMESPACE
    checkpoint = ns / "checkpoint.json"
    marker = ns / "ownership.json"
    if ns.exists():
        if marker.is_symlink() or not marker.is_file():
            raise Rejected("AMBIGUOUS_OWNERSHIP", 7)
        expected_marker = canonical(installation())
        if marker.stat().st_size != len(expected_marker) or marker.read_bytes() != expected_marker:
            raise Rejected("OWNERSHIP_OR_VERSION_COLLISION", 7)
        allowed = {"ownership.json", "checkpoint.json", ".lock"}
        for child in ns.iterdir():
            historical = re.fullmatch(r"previous-([a-f0-9]{64})\.json", child.name)
            if child.is_symlink() or (child.name not in allowed and historical is None):
                raise Rejected("AMBIGUOUS_ARTIFACT", 7)
            if historical and digest(load(child)) != historical[1]:
                raise Rejected("HISTORY_COLLISION", 7)
    old = None
    if checkpoint.exists() or checkpoint.is_symlink():
        old = load(checkpoint)
        if expected != digest(old):
            raise Rejected("CONCURRENT_MODIFICATION", 7)
        if value["payload"]["predecessor"] != expected:
            raise Rejected("PREDECESSOR_MISMATCH", 7)
        if value["payload"]["sequence"] != old["payload"]["sequence"] + 1:
            raise Rejected("SEQUENCE_MISMATCH", 7)
        if value["payload"]["session_id"] != old["payload"]["session_id"]:
            raise Rejected("SESSION_MISMATCH", 7)
        if old["extensions"] != value["extensions"]:
            raise Rejected("EXTENSION_LOSS_PROHIBITED", 7)
    elif expected is not None or value["payload"]["predecessor"] is not None:
        raise Rejected("MISSING_PREDECESSOR", 7)
    return {
        "operation": "candidate-write",
        "paths": [str(marker), str(checkpoint)],
        "candidate_digest": digest(value),
        "expected": expected,
        "lifecycle": "Draft -> Draft",
        "authority": "explicit ordinary write only; no activation",
        "activation": "unsupported",
        "previous": digest(old) if old else None,
        "installation": installation(),
    }


def _open_chain(path: Path) -> int:
    """Anchor each directory component without following symlinks."""
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    fd = os.open("/", flags)
    try:
        for part in path.absolute().parts[1:]:
            if part in (".", ".."):
                raise Rejected("UNSAFE_PATH", 7)
            child = os.open(part, flags, dir_fd=fd)
            os.close(fd)
            fd = child
        return fd
    except BaseException:
        os.close(fd)
        raise


def _read_at(directory: int, name: str) -> bytes:
    fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
    with os.fdopen(fd, "rb") as stream:
        data = stream.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise Rejected("BLOCKED_RESOURCE_LIMIT", 4)
    return data


def _exclusive_at(directory: int, name: str, data: bytes) -> None:
    fd = os.open(
        name,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
        0o600,
        dir_fd=directory,
    )
    with os.fdopen(fd, "wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def _atomic_at(directory: int, name: str, data: bytes) -> None:
    pending = ".pending-" + secrets.token_hex(16)
    fd = os.open(
        pending,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
        0o600,
        dir_fd=directory,
    )
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(pending, name, src_dir_fd=directory, dst_dir_fd=directory)
    finally:
        if pending in os.listdir(directory):
            os.unlink(pending, dir_fd=directory)


def apply(root: Path, value: dict[str, Any], preview: dict[str, Any]) -> None:
    """Recheck preview and drift, lock writers, preserve predecessor, replace atomically."""
    root = safe_root(root)
    if plan(root, value, preview["expected"]) != preview:
        raise Rejected("STALE_PREVIEW", 7)
    if verify(value, root):
        raise Rejected("STALE_OR_INVALID_CANDIDATE", 7)
    data = canonical(value)
    if len(data) > MAX_BYTES:
        raise Rejected("BLOCKED_RESOURCE_LIMIT", 4)
    try:
        import fcntl
    except ImportError as exc:
        raise Rejected("LOCKING_UNSUPPORTED", 6) from exc
    with ExitStack() as stack:
        parent = _open_chain(root)
        stack.callback(os.close, parent)
        for component in NAMESPACE.split("/"):
            created = False
            try:
                os.mkdir(component, 0o700, dir_fd=parent)
                created = True
            except FileExistsError:
                pass
            parent = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
            stack.callback(os.close, parent)
        if created:
            _exclusive_at(parent, "ownership.json", canonical(installation()))
        if _read_at(parent, "ownership.json") != canonical(installation()):
            raise Rejected("OWNERSHIP_OR_VERSION_COLLISION", 7)
        fd = os.open(".lock", os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600, dir_fd=parent)
        stream = stack.enter_context(os.fdopen(fd, "r+b"))
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise Rejected("CONCURRENT_MODIFICATION", 7) from exc
        if plan(root, value, preview["expected"]) != preview:
            raise Rejected("STALE_PREVIEW", 7)
        if verify(value, root):
            raise Rejected("STALE_OR_INVALID_CANDIDATE", 7)
        names = os.listdir(parent)
        if "checkpoint.json" in names:
            original = _read_at(parent, "checkpoint.json")
            if original != canonical(load(root / NAMESPACE / "checkpoint.json")):
                raise Rejected("CONCURRENT_MODIFICATION", 7)
            previous = f"previous-{preview['expected']}.json"
            if previous in names:
                if _read_at(parent, previous) != original:
                    raise Rejected("HISTORY_COLLISION", 7)
            else:
                _exclusive_at(parent, previous, original)
        elif preview["expected"] is not None:
            raise Rejected("CONCURRENT_MODIFICATION", 7)
        _atomic_at(parent, "checkpoint.json", data)


def export_plan(
    value: dict[str, Any], destination: Path, classification: str, basis: str, assessor: str
) -> dict[str, Any]:
    if inspect_candidate(value):
        raise Rejected("INVALID_EXPORT_CANDIDATE")
    if classification != "Public" or not basis.strip() or not assessor.strip():
        raise Rejected("DISCLOSURE_DENIED", 3)
    if destination.exists() or destination.is_symlink():
        raise Rejected("EXPORT_COLLISION", 7)
    parent = destination.parent
    if not parent.is_dir() or parent.resolve() != parent.absolute():
        raise Rejected("UNSAFE_EXPORT_PATH", 7)
    return {
        "namespace": NAMESPACE,
        "destination": str(destination.absolute()),
        "artifacts": [
            {
                "name": "candidate.json",
                "id": value["id"],
                "digest": digest(value),
                "schema": value["schema"],
                "classification": classification,
                "basis": basis,
                "assessor": assessor,
                "lineage": value["supersedes"],
            }
        ],
        "authority": "explicit public disclosure assertion; not authenticated approval",
        "exclusions": [],
    }


def export(
    value: dict[str, Any], preview: dict[str, Any], *, write: bool = False
) -> dict[str, Any]:
    item = preview["artifacts"][0]
    destination = Path(preview["destination"])
    current = export_plan(
        value, destination, item["classification"], item["basis"], item["assessor"]
    )
    if current != preview:
        raise Rejected("STALE_EXPORT_PREVIEW", 7)
    if write:
        if len(canonical(value)) > MAX_BYTES:
            raise Rejected("BLOCKED_RESOURCE_LIMIT", 4)
        with ExitStack() as stack:
            parent = _open_chain(destination.parent)
            stack.callback(os.close, parent)
            os.mkdir(destination.name, 0o700, dir_fd=parent)
            directory = os.open(
                destination.name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent
            )
            stack.callback(os.close, directory)
            _exclusive_at(directory, "candidate.json", canonical(value))
            _exclusive_at(directory, "manifest.json", canonical(preview))
    return preview


def disengage(root: Path) -> dict[str, Any]:
    root = safe_root(root)
    ns = root / NAMESPACE
    artifacts = []
    if ns.exists():
        marker = ns / "ownership.json"
        expected_marker = canonical(installation())
        owned = (
            marker.is_file()
            and not marker.is_symlink()
            and marker.stat().st_size == len(expected_marker)
            and marker.read_bytes() == expected_marker
        )
        for path in sorted(ns.iterdir()):
            known = path.name in {"ownership.json", ".lock", "checkpoint.json"} or bool(
                re.fullmatch(r"previous-[a-f0-9]{64}\.json", path.name)
            )
            artifacts.append(
                {
                    "path": str(path),
                    "ownership": (
                        "manifest-claimed"
                        if owned and known and not path.is_symlink()
                        else "ambiguous"
                    ),
                    "kind": "historical" if path.name.startswith("previous-") else "current",
                    "action": "preserve",
                    "reason": "Historical evidence or user modifications must not be erased.",
                }
            )
    return {
        "operation": "non-destructive-disengagement-plan",
        "integrations_enabled": False,
        "artifacts": artifacts,
        "user_owned": "all paths outside the framework namespace",
        "shared": ".codex parent directory",
        "destructive_cleanup": "unsupported",
        "residuals": "All records preserved; package uninstall does not erase history.",
    }
