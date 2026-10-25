"""Portable evidence records and deliberately non-activating candidate evaluation."""

from __future__ import annotations

import gzip
import hashlib
import json
import os
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from importlib.resources import files
from pathlib import Path
from typing import Any, Callable

from jsonschema import Draft202012Validator, FormatChecker

from .git_capture import CaptureLimit, capture

MAX_PATHS = 50000
MAX_BYTES = 64 * 1024 * 1024
NAMESPACE = ".codex/institutional"
Clock = Callable[[], datetime]


class Rejected(ValueError):
    """Stable CLI failure with a structured reason."""

    def __init__(self, reason: str, code: int = 2):
        super().__init__(reason)
        self.reason = reason
        self.code = code


def canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    ).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def utc() -> datetime:
    return datetime.now(timezone.utc)


def contracts() -> dict[str, Any]:
    return json.loads(files("codex.institutional").joinpath("contracts.json").read_text())


def record(
    schema: str,
    payload: dict[str, Any],
    clock: Clock = utc,
    evidence: list[str] | None = None,
) -> dict[str, Any]:
    now = clock()
    if now.tzinfo is None:
        raise Rejected("NAIVE_CLOCK", 5)
    result = {
        "schema": schema,
        "id": f"{schema}:{digest(payload)}",
        "created_at": now.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "producer": {"identity": "codex-institutional", "assurance": "unverified"},
        "evidence_refs": evidence or [],
        "authority_refs": [],
        "validation_state": "candidate",
        "lifecycle": "Draft",
        "supersedes": None,
        "extensions": {},
        "payload": payload,
    }
    result["integrity"] = digest(result)
    validate(result)
    return result


def validate(value: Any) -> None:
    """Validate local Draft 2020-12 resources; no remote references are resolved."""
    if not isinstance(value, dict):
        raise Rejected("MALFORMED_RECORD", 5)
    schema = contracts()["implemented"].get(value.get("schema"))
    if schema is None:
        raise Rejected("UNSUPPORTED_SCHEMA", 6)
    envelope = {
        "type": "object",
        "required": [
            "schema",
            "id",
            "created_at",
            "producer",
            "evidence_refs",
            "authority_refs",
            "validation_state",
            "lifecycle",
            "supersedes",
            "extensions",
            "payload",
            "integrity",
        ],
        "additionalProperties": False,
        "properties": {
            "schema": {"type": "string"},
            "id": {"type": "string"},
            "created_at": {"type": "string", "format": "date-time", "pattern": "Z$"},
            "producer": {
                "type": "object",
                "required": ["identity", "assurance"],
                "properties": {
                    "identity": {"type": "string", "minLength": 1},
                    "assurance": {"const": "unverified"},
                },
                "additionalProperties": False,
            },
            "evidence_refs": {"type": "array", "items": {"type": "string"}},
            "authority_refs": {"type": "array", "maxItems": 0},
            "validation_state": {"const": "candidate"},
            "lifecycle": {"const": "Draft"},
            "supersedes": {"type": ["string", "null"]},
            "extensions": {"type": "object"},
            "payload": schema,
            "integrity": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
        },
    }
    if not Draft202012Validator(envelope, format_checker=FormatChecker()).is_valid(value):
        raise Rejected("MALFORMED_RECORD", 5)
    if digest({k: v for k, v in value.items() if k != "integrity"}) != value["integrity"]:
        raise Rejected("INTEGRITY_MISMATCH")
    if value["id"] != f"{value['schema']}:{digest(value['payload'])}":
        raise Rejected("IDENTITY_MISMATCH")
    if value["schema"] == "codex.inventory.v1":
        payload = value["payload"]
        entries = payload["entries"]
        paths = [entry.get("path") for entry in entries]
        if any(
            not isinstance(path, str)
            or not path
            or path.startswith("/")
            or "\\" in path
            or ".." in Path(path).parts
            for path in paths
        ):
            raise Rejected("UNSAFE_INVENTORY_PATH", 5)
        if paths != sorted(set(paths)):
            raise Rejected("UNORDERED_OR_DUPLICATE_PATHS", 5)
        if payload["counts"] != dict(Counter(entry.get("kind") for entry in entries)):
            raise Rejected("CENSUS_RECONCILIATION_FAILED", 5)


def load(path: Path, *, inspection_only: bool = False) -> dict[str, Any]:
    """Load inert records; inspection_only preserves structural access to rejected legacy data."""
    if path.is_symlink() or not path.is_file():
        raise Rejected("UNSAFE_INPUT", 5)
    if path.stat().st_size > MAX_BYTES:
        raise Rejected("BLOCKED_RESOURCE_LIMIT", 4)

    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise Rejected("DUPLICATE_JSON_KEY", 5)
            result[key] = value
        return result

    try:
        if path.suffix == ".gz":
            with gzip.open(path, "rb") as stream:
                content = stream.read(MAX_BYTES + 1)
            if len(content) > MAX_BYTES:
                raise Rejected("BLOCKED_RESOURCE_LIMIT", 4)
        else:
            content = path.read_bytes()
        value = json.loads(content, object_pairs_hook=pairs)
    except Rejected:
        raise
    except (ValueError, RecursionError) as exc:
        raise Rejected("MALFORMED_JSON", 5) from exc
    validate(value)
    if not inspection_only:
        if value["schema"] == "codex.assurance.v1":
            from .assurance import validate_artifact

            validate_artifact(value)
        elif value["schema"] == "codex.continuation-state.v1":
            findings = inspect_candidate(value)
            if findings:
                raise Rejected("INVALID_CANDIDATE:" + ",".join(findings))
    return value


def classify(path: str) -> str:
    """Mutually exclusive primary classification, in precedence order."""
    low = path.lower()
    rules = [
        ("agent", (".github/agents/", "src/agents/", "src/agent/")),
        ("instruction", (".github/prompts/", ".github/instructions/")),
        ("workflow", (".github/workflows/", ".github/actions/")),
        ("governance", (".codex/governance/", "src/aries_serpent_core/governance/")),
    ]
    for kind, prefixes in rules:
        if low.startswith(prefixes):
            return kind
    for kind, words in [
        ("governance", ("authority", "governance")),
        ("knowledge", ("memory", "experience", "checkpoint", "continuation", "aftermath")),
        ("registry", ("registry", "orchestrat")),
        ("decision", ("/adr/", "decision", "dissent")),
        ("verification", ("security", "validation", "verification", "test")),
        ("packaging", ("pyproject.toml", "manifest.in", "setup.py", "packaging", "wheel")),
        ("instruction", ("agents.md", "copilot", "instruction")),
    ]:
        if any(word in low for word in words):
            return kind
    return "other"


def git(root: Path, *args: str) -> str | None:
    env = {
        "PATH": os.environ.get("PATH", os.defpath),
        "LC_ALL": "C",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_NO_LAZY_FETCH": "1",
        "GIT_ALLOW_PROTOCOL": "",
        "GIT_OPTIONAL_LOCKS": "0",
        "GIT_TERMINAL_PROMPT": "0",
    }
    try:
        result = capture(
            [
                "git",
                "-c",
                "core.fsmonitor=false",
                "-c",
                f"core.hooksPath={os.devnull}",
                "-C",
                str(root),
                *args,
            ],
            env=env,
        )
        return result.decode("utf-8", errors="surrogateescape").rstrip("\n")
    except CaptureLimit as exc:
        raise Rejected("BLOCKED_RESOURCE_LIMIT:" + str(exc), 4) from exc
    except (OSError, subprocess.SubprocessError):
        return None


def inventory(root: Path, clock: Clock = utc, source_ref: str | None = None) -> dict[str, Any]:
    """Census paths without executing or semantically interpreting their contents."""
    root = root.resolve(strict=True)
    is_root = git(root, "rev-parse", "--show-toplevel") == str(root)
    sha = (
        git(root, "rev-parse", "--verify", "--end-of-options", source_ref or "HEAD")
        if is_root
        else None
    )
    if sha and not re.fullmatch(r"[a-f0-9]{40,64}", sha):
        raise Rejected("INVALID_SOURCE_IDENTITY", 5)
    if source_ref and sha is None:
        raise Rejected("SOURCE_REFERENCE_UNAVAILABLE", 4)
    tracked = git(root, "ls-tree", "-r", "-z", sha) if sha else None
    blobs = {}
    if tracked is not None:
        for item in tracked.split("\0"):
            if item:
                metadata, path = item.split("\t", 1)
                blobs[path] = "git-object:" + metadata.split()[-1]
        paths = sorted(blobs)
        coverage = "git-tree"
    else:
        paths = []
        for directory, dirs, names in os.walk(root, followlinks=False):
            base = Path(directory)
            dirs[:] = sorted(
                d
                for d in dirs
                if d != ".git"
                and not (base / d).is_symlink()
                and (base / d).relative_to(root).as_posix() != NAMESPACE
            )
            paths.extend((base / name).relative_to(root).as_posix() for name in names)
            if len(paths) > MAX_PATHS:
                raise Rejected("BLOCKED_RESOURCE_LIMIT", 4)
        paths.sort()
        coverage = "filesystem"
    if len(paths) > MAX_PATHS:
        raise Rejected("BLOCKED_RESOURCE_LIMIT", 4)
    entries = []
    defaults = {
        "declared_purpose": "not_observed",
        "observed_behavior": "not_observed",
        "inputs": "unknown",
        "outputs": "unknown",
        "declared_authority": "unknown",
        "verified_authority": "not_observed",
        "effective_authority": {},
        "authority_evidence": [],
        "authority_scope": "unknown",
        "authority_expiry": "unknown",
        "revocation": "unknown",
        "artifact_digest": "not_observed",
        "authority_conflicts": ["authority not established"],
        "dependencies": "not_observed",
        "invoked_workflows": "not_observed",
        "memory_read": "not_observed",
        "memory_written": "not_observed",
        "verification": "not_observed",
        "package_inclusion": "not_observed",
        "overlap": "unknown",
        "tests": "not_observed",
        "execution": "not_observed",
        "gaps": ["metadata is not semantic evidence"],
        "contradictions": "not_observed",
        "disposition": "unknown",
        "confidence": "unknown",
        "evidence": [],
    }
    remaining_bytes = MAX_BYTES
    for path in paths:
        kind = classify(path)
        source_digest = blobs.get(path, "not_observed")
        local = root / path
        if coverage == "filesystem" and not path.startswith(".github/agents/"):
            if local.is_file() and not local.is_symlink():
                size = local.stat().st_size
                remaining_bytes -= size
                if remaining_bytes < 0:
                    raise Rejected("BLOCKED_RESOURCE_LIMIT", 4)
                source_digest = hashlib.sha256(local.read_bytes()).hexdigest()
        entries.append(
            {
                "id": "component:" + digest([str(root), path]),
                "path": path,
                "kind": kind,
                "source_digest": source_digest,
                "depth": "metadata_only",
                "inspection": "excluded" if kind == "other" else "unresolved",
                "rationale": (
                    "outside lexical scope" if kind == "other" else "semantic inspection pending"
                ),
                "tags": [tag for tag in ("archive", "vendor", "generated") if tag in path.lower()],
            }
        )
    return record(
        "codex.inventory.v1",
        {
            "source": {"identity": str(root), "sha": sha, "path_digest": digest(paths)},
            "entries": entries,
            "counts": dict(sorted(Counter(e["kind"] for e in entries).items())),
            "component_defaults": defaults,
            "coverage": coverage,
            "limitations": [
                "Path census only; no usage, effectiveness or permission conclusions.",
                "Git census describes the identified tree, not untracked or dirty content.",
                "Filesystem census excludes .git, symlink directories and framework state.",
            ],
        },
        clock,
    )


def assess(inv: dict[str, Any], clock: Clock = utc) -> dict[str, Any]:
    validate(inv)
    if inv["schema"] != "codex.inventory.v1":
        raise Rejected("EXPECTED_INVENTORY", 5)
    return record(
        "codex.audit-finding.v1",
        {
            "stage": "assessment",
            "findings": ["Authority, overlap, semantic usage and effectiveness remain unverified."],
            "semantic_review": "NOT_RUN",
            "independent_reproduction": "NOT_RUN",
        },
        clock,
        [inv["id"]],
    )


def inspect_candidate(value: dict[str, Any]) -> list[str]:
    validate(value)
    if value["schema"] != "codex.continuation-state.v1":
        raise Rejected("EXPECTED_CONTINUATION", 5)
    findings = []
    supported = []
    for index, child in enumerate(value["payload"]["records"]):
        try:
            validate(child)
            if child["schema"] == "codex.assurance.v1":
                from .assurance import validate_artifact

                validate_artifact(child)
            supported.append(child)
        except Rejected as exc:
            findings.append(f"record[{index}]:{exc.reason}")
    ids = [child["id"] for child in supported]
    if len(ids) != len(set(ids)):
        findings.append("DUPLICATE_RECORD_ID")
    known = set(ids)
    for child in supported:
        if any(ref not in known for ref in child["evidence_refs"]):
            findings.append("UNRESOLVED_EVIDENCE_REFERENCE")
    inventories = [r for r in supported if r["schema"] == "codex.inventory.v1"]
    if len(inventories) != 1:
        findings.append("REQUIRED_INVENTORY_MISSING")
    elif value["payload"]["candidate_ref"] != digest(inventories[0]):
        findings.append("CANDIDATE_BINDING_MISMATCH")
    evidence = [r for r in supported if r["schema"] == "codex.trust-evidence.v1"]
    if len(evidence) != 1:
        findings.append("REQUIRED_SINGLE_EVIDENCE")
    if len(inventories) == 1 and len(evidence) == 1:
        if evidence[0]["payload"]["digest"] != digest(inventories[0]["payload"]):
            findings.append("EVIDENCE_BINDING_MISMATCH")
    stages = {r["payload"]["stage"] for r in supported if r["schema"] == "codex.audit-finding.v1"}
    if stages != {"assessment", "challenge"}:
        findings.append("REQUIRED_REVIEW_MISSING")
    for schema in ("codex.experience.v1", "codex.trust-evidence.v1", "codex.agent-role.v1"):
        if not any(r["schema"] == schema for r in supported):
            findings.append(f"REQUIRED_RECORD_MISSING:{schema}")
    if not findings:
        from .admission import inspect_associations

        try:
            inspect_associations(value)
        except Rejected as exc:
            findings.append(exc.reason)
    return sorted(set(findings))


def candidate(
    root: Path,
    session: str,
    clock: Clock = utc,
    previous_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    inv = inventory(root, clock)
    evidence_payload = {
        "source_identity": str(root.resolve()),
        "location": "path-census",
        "source_sha": inv["payload"]["source"]["sha"],
        "digest": digest(inv["payload"]),
        "method": inv["payload"]["coverage"],
        "observation": f"{len(inv['payload']['entries'])} paths inventoried",
        "limitations": ["Metadata only; integrity is not authenticated provenance."],
        "predecessor": None,
    }
    if previous_evidence is not None:
        validate(previous_evidence)
        if previous_evidence["schema"] != "codex.trust-evidence.v1":
            raise Rejected("EXPECTED_EVIDENCE", 5)
        if previous_evidence["payload"]["digest"] != evidence_payload["digest"]:
            evidence_payload["predecessor"] = previous_evidence["id"]
        else:
            evidence_payload["predecessor"] = previous_evidence["payload"]["predecessor"]
    evidence = record(
        "codex.trust-evidence.v1",
        evidence_payload,
        clock,
    )
    inv["evidence_refs"] = [evidence["id"]]
    inv["integrity"] = digest({k: v for k, v in inv.items() if k != "integrity"})
    assessment = assess(inv, clock)
    challenge = record(
        "codex.audit-finding.v1",
        {
            "stage": "challenge",
            "findings": [
                "DETERMINISTIC_CHECK_ONLY",
                "Alternative cause: integration gap does not establish agent ineffectiveness.",
                "Contradiction search limited to structural checks; semantic review pending.",
                "Untrusted content and its digest can both be replaced; no authenticated approval.",
            ],
            "semantic_review": "NOT_RUN",
            "independent_reproduction": "NOT_RUN",
        },
        clock,
        [evidence["id"], assessment["id"]],
    )
    roles = [
        record(
            "codex.agent-role.v1",
            {
                "purpose": name,
                "capability": capability,
                "authority": "none",
            },
            clock,
        )
        for name, capability in [
            ("Architect: propose inactive candidate", "codex.institutional.core.candidate"),
            (
                "Auditor: deterministic checks, not independent approval",
                "codex.institutional.core.inspect_candidate",
            ),
        ]
    ]
    experience = record(
        "codex.experience.v1",
        {
            "problem": "Portable evidence-gated institutional candidate",
            "context": "Inactive development; imported records are inert data.",
            "environment": {"coverage": inv["payload"]["coverage"]},
            "hypotheses": ["Closed contracts and previews permit safe candidate development."],
            "support": [evidence["id"]],
            "against": ["Semantic review not performed."],
            "alternatives": [
                "Enhance existing script checkpoint manager after compatibility work."
            ],
            "decision": "Retain Draft candidate; do not activate.",
            "dissent": ["A separate installed adapter adds maintenance."],
            "uncertainty": ["Effectiveness and downstream outcomes unknown."],
            "implementation": ["codex.institutional"],
            "verification": [],
            "outcomes": "unknown",
            "failure_modes": challenge["payload"]["findings"],
            "applicability": "Local metadata inspection only",
            "confidence": "unknown",
            "next_review": "Independent reproduction or source/configuration drift",
        },
        clock,
        [evidence["id"], challenge["id"]],
    )
    return record(
        "codex.continuation-state.v1",
        {
            "session_id": session,
            "sequence": 1,
            "source_sha": inv["payload"]["source"]["sha"],
            "candidate_ref": digest(inv),
            "dirty_tree": worktree(root),
            "configuration": {"contracts_digest": digest(contracts()), "root": str(root.resolve())},
            "predecessor": None,
            "gates": {
                "G3": "NOT_RUN",
                "G4": "NOT_RUN",
                "G5": "NOT_RUN",
                "G6": "NOT_RUN",
                "G7": "NOT_RUN",
                "G8": "NOT_RUN",
            },
            "records": [evidence, inv, *roles, assessment, challenge, experience],
            "actors": {
                "implementer": "unverified",
                "independent_verifier": "unknown",
                "approval": "NOT_RUN",
                "activation": "unsupported",
            },
            "blockers": ["Independent reproduction and trusted authority unavailable."],
            "findings": challenge["payload"]["findings"],
            "rejected_hypotheses": ["A path census establishes semantic effectiveness."],
            "uncertainty": ["No operational authority can be derived from these records."],
            "next_action": {
                "action": "verify",
                "preconditions": ["Revalidate source tree and installed contract digests."],
                "acceptance_test": "Technical validation only; independent gates remain NOT_RUN.",
                "idempotency": "Fixed tree, configuration and clock produce identical bytes.",
            },
            "recovery": "Preserve original; regenerate stale previews. Never reset user work.",
        },
        clock,
    )


def authority_diagnostics(claim: dict[str, Any], artifact: str, target: str) -> list[str]:
    """Untrusted claims may explain denial, never establish authority."""
    reasons = ["TRUSTED_IDENTITY_UNAVAILABLE", "ACTIVATION_UNSUPPORTED"]
    actors = [claim.get(k) for k in ("proposer", "implementer", "verifier", "approver")]
    if any(a is None for a in actors):
        reasons.append("MISSING_ACTORS")
    if len(set(str(a) for a in actors)) != len(actors):
        reasons.append("ACTOR_COLLISION")
    if claim.get("artifact") != artifact:
        reasons.append("ARTIFACT_BINDING_MISMATCH")
    if claim.get("target") != target or claim.get("operation") != "activate":
        reasons.append("OPERATION_TARGET_MISMATCH")
    if claim.get("revoked") is not False:
        reasons.append("REVOCATION_UNVERIFIED")
    reasons.append("EXPIRY_UNVERIFIED")
    return sorted(reasons)


def verify(value: dict[str, Any], root: Path) -> list[str]:
    findings = inspect_candidate(value)
    if not findings:
        from .admission import inspect_associations

        try:
            inspect_associations(value, root)
        except Rejected as exc:
            findings.append(exc.reason)
    config = value["payload"]["configuration"]
    if config.get("contracts_digest") != digest(contracts()):
        findings.append("CONTRACT_DRIFT")
    if config.get("root") != str(root.resolve()):
        findings.append("TARGET_MISMATCH")
    if value["payload"]["dirty_tree"] != worktree(root):
        findings.append("WORKTREE_DRIFT")
    inv = inventory(root)
    expected = [r for r in value["payload"]["records"] if r.get("schema") == "codex.inventory.v1"]
    if len(expected) == 1 and inv["payload"] != expected[0]["payload"]:
        findings.append("STALE_CHECKPOINT")
    return sorted(set(findings))


def worktree(root: Path) -> str:
    """Bind dirty tracked content without external diff drivers or profile reads."""
    diff = git(
        root,
        "diff",
        "--no-ext-diff",
        "--no-textconv",
        "--binary",
        "HEAD",
        "--",
        ".",
        ":!.github/agents/**",
        f":!{NAMESPACE}/**",
    )
    return "not_applicable" if diff is None else digest(diff)
