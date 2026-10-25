"""Compose existing assurance validators with candidate and predecessor checks.

Bindings describe scoped technical observations, never approval. Missing bindings
mean historical/unbound data, not acceptance. No filesystem writes occur here.
"""

from __future__ import annotations

import copy
import hashlib
import os
import stat
from pathlib import Path
from typing import Any

from . import assurance, core, review
from .core import Rejected, digest


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise Rejected(reason, 4 if reason == "BLOCKED_RESOURCE_LIMIT" else 7)


def _plan(artifact: dict[str, Any]) -> dict[str, Any]:
    data = artifact["payload"]["data"]
    kind = artifact["payload"]["kind"]
    if kind == "plan":
        return artifact
    if kind == "history":
        return data["plan"]
    return data["history"]["payload"]["data"]["plan"]


def _history(artifact: dict[str, Any]) -> dict[str, Any] | None:
    kind = artifact["payload"]["kind"]
    if kind == "history":
        return artifact
    if kind == "recommendation":
        return artifact["payload"]["data"]["history"]
    return None


def _binding(value: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    payload = value["payload"]
    planned = _plan(artifact)["payload"]["data"]
    return {
        "artifact_digest": digest(artifact),
        "candidate_ref": payload["candidate_ref"],
        "source_sha": payload["source_sha"],
        "dirty_tree": payload["dirty_tree"],
        "configuration_digest": digest(payload["configuration"]),
        "review_binding": planned["binding"],
        "review_plan_digest": digest(planned["review_plan"]),
    }


def _check_files(manifest: dict[str, Any], root: Path) -> None:
    from .storage import _open_chain

    data = review._manifest(manifest)
    remaining = review.MAX_BYTES
    for entry in data["entries"]:
        relative = Path(entry["path"])
        _require(
            entry["path"] != ".github/agents"
            and not entry["path"].startswith(".github/agents/")
            and entry["path"] != core.NAMESPACE
            and not entry["path"].startswith(core.NAMESPACE + "/"),
            "ASSOCIATION_EXCLUDED_PATH",
        )
        try:
            parent = _open_chain(root / relative.parent)
            try:
                fd = os.open(
                    relative.name,
                    os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                    dir_fd=parent,
                )
                with os.fdopen(fd, "rb") as stream:
                    metadata = os.fstat(stream.fileno())
                    _require(stat.S_ISREG(metadata.st_mode), "ASSOCIATION_UNSAFE_PATH")
                    _require(metadata.st_size <= remaining, "BLOCKED_RESOURCE_LIMIT")
                    content = stream.read(remaining + 1)
            finally:
                os.close(parent)
        except OSError as exc:
            raise Rejected("ASSOCIATION_SOURCE_UNAVAILABLE", 7) from exc
        remaining -= len(content)
        _require(remaining >= 0, "BLOCKED_RESOURCE_LIMIT")
        _require(
            len(content) == entry["size"]
            and hashlib.sha256(content).hexdigest() == entry["sha256"]
            and stat.S_IMODE(metadata.st_mode) == entry["mode"],
            "ASSOCIATION_SOURCE_DRIFT",
        )


def inspect_associations(value: dict[str, Any], root: Path | None = None) -> list[dict[str, str]]:
    """Inspect a structurally/semantically checked candidate's scoped associations.

    With root, rehash only the explicit manifest files. Without root, checks
    establish internal association, not applicability to current filesystem bytes.
    Historical observations without bindings remain diagnostic, even with PASS.
    """
    artifacts = {
        digest(child): child
        for child in value["payload"]["records"]
        if child["schema"] == assurance.SCHEMA
    }
    histories: dict[str, dict[str, Any]] = {}
    for artifact in artifacts.values():
        history = _history(artifact)
        if history is None:
            continue
        data = history["payload"]["data"]
        key = digest(data["plan"])
        events = data["events"]
        previous = histories.get(key)
        if previous is not None:
            old = previous["payload"]["data"]["events"]
            count = min(len(old), len(events))
            _require(old[:count] == events[:count], "ASSURANCE_HISTORY_FORK")
            if len(events) < len(old):
                continue
        histories[key] = history
    bound = set()
    checked = set()
    for binding in value["payload"].get("assurance_bindings", []):
        key = binding["artifact_digest"]
        _require(key in artifacts and key not in bound, "ASSOCIATION_ARTIFACT_MISMATCH")
        artifact = artifacts[key]
        _require(binding == _binding(value, artifact), "ASSOCIATION_BINDING_MISMATCH")
        history = _history(artifact)
        if history is not None:
            _require(
                history["payload"] == histories[digest(_plan(artifact))]["payload"],
                "ASSOCIATION_STALE_HISTORY",
            )
        planned = _plan(artifact)["payload"]["data"]
        manifest = planned["review_plan"]["payload"]["data"]["manifest"]
        if artifact["payload"]["kind"] == "recommendation":
            _require(
                artifact["payload"]["data"]["current_manifest"] == manifest,
                "ASSOCIATION_STALE_CONTEXT",
            )
        if root is not None and digest(manifest) not in checked:
            _check_files(manifest, root)
            checked.add(digest(manifest))
        bound.add(key)
    return [
        {
            "artifact_digest": key,
            "association": "current-bound" if key in bound else "unbound-diagnostic",
            "authority": "none",
        }
        for key in artifacts
    ]


def bind(
    value: dict[str, Any],
    artifacts: list[dict[str, Any]],
    *,
    root: Path,
    replace: bool = False,
) -> dict[str, Any]:
    """Associate already attached observations after source/context validation.

    The inventory, configuration and dirty-tree identity exclude this checkpoint
    and its bindings. Review manifests must exclude framework state, avoiding
    circular self-binding. Context is bound by the review manifest/plan digest.
    """
    result = copy.deepcopy(value)
    if replace:
        result["payload"]["assurance_bindings"] = []
        result["id"] = f"{result['schema']}:{digest(result['payload'])}"
        result["integrity"] = digest({k: v for k, v in result.items() if k != "integrity"})
    findings = core.verify(result, root)
    _require(not findings, "INVALID_CANDIDATE:" + ",".join(findings))
    known = {digest(item) for item in result["payload"]["records"]}
    bindings = result["payload"].setdefault("assurance_bindings", [])
    for artifact in artifacts:
        assurance.validate_artifact(artifact)
        _require(digest(artifact) in known, "ASSOCIATION_ARTIFACT_MISMATCH")
        bindings.append(_binding(result, artifact))
    result["id"] = f"{result['schema']}:{digest(result['payload'])}"
    result["integrity"] = digest({k: v for k, v in result.items() if k != "integrity"})
    core.validate(result)
    inspect_associations(result, root)
    return result


def transition(previous: dict[str, Any], value: dict[str, Any]) -> None:
    """Validate supported extension/sequence and append-only observation retention."""
    old, new = previous["payload"], value["payload"]
    _require(new["predecessor"] == digest(previous), "PREDECESSOR_MISMATCH")
    _require(new["sequence"] == old["sequence"] + 1, "SEQUENCE_MISMATCH")
    _require(new["session_id"] == old["session_id"], "SESSION_MISMATCH")
    _require(previous["extensions"] == value["extensions"], "EXTENSION_LOSS_PROHIBITED")
    retained = {digest(child) for child in new["records"]}
    for child in old["records"]:
        if child["schema"] in (assurance.SCHEMA, review.SCHEMA):
            _require(digest(child) in retained, "REQUIRED_HISTORY_LOSS")
