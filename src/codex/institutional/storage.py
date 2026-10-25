"""Previewed, local candidate persistence; never governance adoption."""

from __future__ import annotations

import os
import re
import secrets
from contextlib import ExitStack
from dataclasses import dataclass
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any, Literal, Protocol, cast

from . import admission
from .core import (
    MAX_BYTES,
    NAMESPACE,
    Clock,
    Rejected,
    canonical,
    contracts,
    digest,
    inspect_candidate,
    load,
    utc,
    validate,
    verify,
)

MAX_CHECKPOINTS = 128


@dataclass(frozen=True)
class CheckpointReference:
    """Caller-injected reference metadata; its claims are not authenticated here."""

    subject: str
    digest: str
    source: str
    scope: str
    context: str
    observed_at: datetime
    expires_at: datetime
    assurance: Literal["fixture", "externally-verified"]


@dataclass(frozen=True)
class ReferenceUnavailable:
    reason: Literal["unavailable", "unsupported"] = "unavailable"


class CheckpointReferenceProvider(Protocol):
    """Injected by application code; imported records cannot select provider code."""

    def resolve(
        self, *, subject: str, scope: str, context: str
    ) -> CheckpointReference | ReferenceUnavailable: ...


@dataclass(frozen=True)
class ReferenceEvaluation:
    status: Literal[
        "match", "mismatch", "unavailable", "unsupported", "malformed", "stale", "inapplicable"
    ]
    reference_digest: str | None
    reference_id: str | None
    source: str
    assurance: str
    authority: Literal["none"] = "none"
    limitations: tuple[str, ...] = ("Reference comparison is not authentication or approval.",)


def evaluate_checkpoint_reference(
    actual_digest: str,
    *,
    expected: str | None = None,
    provider: CheckpointReferenceProvider | None = None,
    subject: str | None = None,
    scope: str | None = None,
    context: str | None = None,
    clock: Clock = utc,
) -> ReferenceEvaluation:
    """Compare a current checkpoint to an explicit pin or injected provider result."""
    unavailable = ("No external continuity reference was established.",)
    if type(actual_digest) is not str or re.fullmatch(r"[a-f0-9]{64}", actual_digest) is None:
        return ReferenceEvaluation(
            "malformed", None, None, "none", "unknown", limitations=unavailable
        )
    if expected is not None and provider is not None:
        return ReferenceEvaluation("malformed", None, None, "none", "unknown")
    if expected is not None:
        if type(expected) is not str or re.fullmatch(r"[a-f0-9]{64}", expected) is None:
            return ReferenceEvaluation("malformed", None, None, "caller-pin", "caller-asserted")
        return ReferenceEvaluation(
            "match" if actual_digest == expected else "mismatch",
            expected,
            digest({"source": "caller-supplied-pin", "digest": expected}),
            "caller-supplied-pin",
            "caller-asserted",
            limitations=("The caller-supplied pin is compared, not independently authenticated.",),
        )
    if provider is None:
        return ReferenceEvaluation(
            "unavailable", None, None, "none", "unknown", limitations=unavailable
        )
    if any(
        type(item) is not str or not item.strip() or len(item) > 256
        for item in (subject, scope, context)
    ):
        return ReferenceEvaluation("malformed", None, None, "provider", "unknown")
    subject_value = cast(str, subject)
    scope_value = cast(str, scope)
    context_value = cast(str, context)
    try:
        reference = provider.resolve(
            subject=subject_value, scope=scope_value, context=context_value
        )
    except Exception:
        return ReferenceEvaluation("unavailable", None, None, "provider", "unknown")
    if isinstance(reference, ReferenceUnavailable):
        if type(reference.reason) is not str or reference.reason not in (
            "unavailable",
            "unsupported",
        ):
            return ReferenceEvaluation("malformed", None, None, "provider", "unknown")
        return ReferenceEvaluation(reference.reason, None, None, "provider", "unknown")
    if type(reference) is not CheckpointReference:
        return ReferenceEvaluation("malformed", None, None, "provider", "unknown")
    text_fields = (
        reference.subject,
        reference.source,
        reference.scope,
        reference.context,
    )
    if (
        not all(type(item) is str and item.strip() and len(item) <= 256 for item in text_fields)
        or type(reference.digest) is not str
        or re.fullmatch(r"[a-f0-9]{64}", reference.digest) is None
        or type(reference.assurance) is not str
        or reference.assurance not in ("fixture", "externally-verified")
        or type(reference.observed_at) is not datetime
        or type(reference.expires_at) is not datetime
    ):
        return ReferenceEvaluation("malformed", None, None, "provider", "unknown")
    if (reference.subject, reference.scope, reference.context) != (subject, scope, context):
        return ReferenceEvaluation(
            "inapplicable", reference.digest, None, reference.source, reference.assurance
        )
    try:
        now = clock()
    except Exception:
        return ReferenceEvaluation("malformed", reference.digest, None, reference.source, "unknown")
    if type(now) is not datetime:
        return ReferenceEvaluation("malformed", reference.digest, None, reference.source, "unknown")
    try:
        if any(
            moment.tzinfo is None or moment.utcoffset() is None
            for moment in (now, reference.observed_at, reference.expires_at)
        ):
            return ReferenceEvaluation(
                "malformed", reference.digest, None, reference.source, "unknown"
            )
        now = now.astimezone(timezone.utc)
        observed_at = reference.observed_at.astimezone(timezone.utc)
        expires_at = reference.expires_at.astimezone(timezone.utc)
    except Exception:
        return ReferenceEvaluation("malformed", reference.digest, None, reference.source, "unknown")
    if observed_at >= expires_at or observed_at > now or expires_at <= now:
        return ReferenceEvaluation(
            "stale", reference.digest, None, reference.source, reference.assurance
        )
    identity = digest(
        {
            "subject": reference.subject,
            "digest": reference.digest,
            "source": reference.source,
            "scope": reference.scope,
            "context": reference.context,
            "observed_at": observed_at.isoformat(),
            "expires_at": expires_at.isoformat(),
            "assurance": reference.assurance,
        }
    )
    return ReferenceEvaluation(
        "match" if actual_digest == reference.digest else "mismatch",
        reference.digest,
        identity,
        reference.source,
        reference.assurance,
        limitations=(
            "Provider provenance and asserted assurance are not independently authenticated.",
            "A match confers no approval or activation authority.",
        ),
    )


def _enforce_reference(
    value: dict[str, Any],
    *,
    expected: str | None,
    provider: CheckpointReferenceProvider | None,
    subject: str | None,
    scope: str | None,
    context: str | None,
    required: bool,
    clock: Clock,
) -> ReferenceEvaluation | None:
    if type(required) is not bool:
        raise Rejected("RECOVERY_ANCHOR_MALFORMED", 7)
    if not required and expected is None and provider is None:
        return None
    result = evaluate_checkpoint_reference(
        digest(value),
        expected=expected,
        provider=provider,
        subject=subject,
        scope=scope,
        context=context,
        clock=clock,
    )
    if result.status != "match":
        raise Rejected(f"RECOVERY_ANCHOR_{result.status.upper()}", 7)
    return result


def _reference_preview(value: ReferenceEvaluation | None) -> dict[str, Any] | None:
    if value is None:
        return None
    return {
        "status": value.status,
        "reference_digest": value.reference_digest,
        "reference_id": value.reference_id,
        "source": value.source,
        "assurance": value.assurance,
        "authority": value.authority,
    }


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


def plan(
    root: Path,
    value: dict[str, Any],
    expected: str | None = None,
    *,
    anchor_expected: str | None = None,
    anchor_provider: CheckpointReferenceProvider | None = None,
    anchor_subject: str | None = None,
    anchor_scope: str | None = None,
    anchor_context: str | None = None,
    require_anchor: bool = False,
    clock: Clock = utc,
) -> dict[str, Any]:
    if type(require_anchor) is not bool:
        raise Rejected("RECOVERY_ANCHOR_MALFORMED", 7)
    validate(value)
    findings = inspect_candidate(value)
    if findings:
        raise Rejected("INVALID_CANDIDATE:" + ",".join(findings))
    if value["payload"]["sequence"] > MAX_CHECKPOINTS:
        raise Rejected("BLOCKED_RESOURCE_LIMIT", 4)
    root = safe_root(root)
    admission.inspect_associations(value, root)
    ns = root / NAMESPACE
    checkpoint = ns / "checkpoint.json"
    marker = ns / "ownership.json"
    anchor = None
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
        old, anchor = _recover(
            root,
            expected=anchor_expected,
            provider=anchor_provider,
            subject=anchor_subject,
            scope=anchor_scope,
            context=anchor_context,
            require_anchor=require_anchor,
            clock=clock,
        )
        if expected != digest(old):
            raise Rejected("CONCURRENT_MODIFICATION", 7)
        admission.transition(old, value)
    elif anchor_expected is not None or anchor_provider is not None or require_anchor:
        raise Rejected("RECOVERY_ANCHOR_UNAVAILABLE", 7)
    elif expected is not None or value["payload"]["predecessor"] is not None:
        raise Rejected("MISSING_PREDECESSOR", 7)
    elif value["payload"]["sequence"] != 1:
        raise Rejected("SEQUENCE_MISMATCH", 7)
    return {
        "operation": "candidate-write",
        "paths": [str(marker), str(checkpoint)],
        "candidate_digest": digest(value),
        "expected": expected,
        "lifecycle": "Draft -> Draft",
        "authority": "explicit ordinary write only; no activation",
        "activation": "unsupported",
        "previous": digest(old) if old else None,
        "anchor": _reference_preview(anchor),
        "installation": installation(),
    }


def _recover(
    root: Path,
    *,
    expected: str | None,
    provider: CheckpointReferenceProvider | None,
    subject: str | None,
    scope: str | None,
    context: str | None,
    require_anchor: bool,
    clock: Clock,
) -> tuple[dict[str, Any], ReferenceEvaluation | None]:
    """Replay retained predecessors against an optional caller-supplied reference.

    Local digests alone cannot detect wholesale replacement of an entire chain.
    Recovery validates semantics/continuity, not current source applicability.
    """
    if type(require_anchor) is not bool:
        raise Rejected("RECOVERY_ANCHOR_MALFORMED", 7)
    root = safe_root(root)
    namespace = root / NAMESPACE
    current = load(namespace / "checkpoint.json")
    anchor = _enforce_reference(
        current,
        expected=expected,
        provider=provider,
        subject=subject,
        scope=scope,
        context=context,
        required=require_anchor,
        clock=clock,
    )
    child = current
    for _ in range(MAX_CHECKPOINTS):
        predecessor = child["payload"]["predecessor"]
        if predecessor is None:
            if child["payload"]["sequence"] != 1:
                raise Rejected("SEQUENCE_MISMATCH", 7)
            return current, anchor
        if re.fullmatch("[a-f0-9]{64}", predecessor) is None:
            raise Rejected("PREDECESSOR_MISMATCH", 7)
        path = namespace / f"previous-{predecessor}.json"
        if not path.is_file() or path.is_symlink():
            raise Rejected("MISSING_PREDECESSOR", 7)
        previous = load(path)
        admission.transition(previous, child)
        child = previous
    raise Rejected("BLOCKED_RESOURCE_LIMIT", 4)


def recover(
    root: Path,
    expected: str | None = None,
    *,
    provider: CheckpointReferenceProvider | None = None,
    subject: str | None = None,
    scope: str | None = None,
    context: str | None = None,
    require_anchor: bool = False,
    clock: Clock = utc,
) -> dict[str, Any]:
    """Replay retained predecessors; an injected anchor is comparison, not approval.

    Without an explicit pin/provider, legacy unanchored diagnostics remain available.
    """
    current, _ = _recover(
        root,
        expected=expected,
        provider=provider,
        subject=subject,
        scope=scope,
        context=context,
        require_anchor=require_anchor,
        clock=clock,
    )
    return current


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


def apply(
    root: Path,
    value: dict[str, Any],
    preview: dict[str, Any],
    *,
    anchor_expected: str | None = None,
    anchor_provider: CheckpointReferenceProvider | None = None,
    anchor_subject: str | None = None,
    anchor_scope: str | None = None,
    anchor_context: str | None = None,
    require_anchor: bool = False,
    clock: Clock = utc,
) -> None:
    """Recheck preview and drift, lock writers, preserve predecessor, replace atomically."""
    root = safe_root(root)
    if (
        plan(
            root,
            value,
            preview["expected"],
            anchor_expected=anchor_expected,
            anchor_provider=anchor_provider,
            anchor_subject=anchor_subject,
            anchor_scope=anchor_scope,
            anchor_context=anchor_context,
            require_anchor=require_anchor,
            clock=clock,
        )
        != preview
    ):
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
        if (
            plan(
                root,
                value,
                preview["expected"],
                anchor_expected=anchor_expected,
                anchor_provider=anchor_provider,
                anchor_subject=anchor_subject,
                anchor_scope=anchor_scope,
                anchor_context=anchor_context,
                require_anchor=require_anchor,
                clock=clock,
            )
            != preview
        ):
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
