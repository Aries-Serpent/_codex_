"""Evidence contracts for the recursive self-improvement loop.

These frozen, stdlib-only dataclasses define the versioned event/result
schema that joins a measured health signal to a pattern, a bounded patch
proposal, gate results, merge state, and a post-merge confidence update.

The contract is deliberately transport-agnostic: producers and consumers
serialize with :func:`event_to_dict` / :func:`event_from_dict` (and the
matching result helpers) so fixtures can replay the same event into the
same result offline.

This module keeps the distribution dependency-light: digests use FNV-1a
(64-bit), which is sufficient for idempotency keys and content identity
within a trust boundary. It is not a cryptographic hash and must not be
used for tamper-evidence across trust boundaries.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Mapping, Optional, Tuple

# Bump when a breaking change is made to the event/result schema.
EVIDENCE_SCHEMA_VERSION = "1.0.0"

_SCHEMA_MAJOR = EVIDENCE_SCHEMA_VERSION.split(".", 1)[0]


class SchemaVersionError(ValueError):
    """Raised when a payload declares an incompatible schema version."""


class EvidenceValidationError(ValueError):
    """Raised when required evidence is missing or malformed.

    The loop fails closed: any validation error must prevent execution
    rather than silently substitute synthetic data.
    """


class SignalSource:
    """Origin of a measured health signal (string constants)."""

    LOCAL_TEST_RUN = "local_test_run"
    CI_WORKFLOW = "ci_workflow"
    PDA_FAILURE_LOG = "pda_failure_log"
    MANUAL = "manual"

    _VALUES = frozenset({LOCAL_TEST_RUN, CI_WORKFLOW, PDA_FAILURE_LOG, MANUAL})


class DataAvailability:
    """Whether an observation was measured, unavailable, or errored.

    Producers must use ``UNAVAILABLE``/``ERROR`` explicitly instead of
    inventing a "healthy" placeholder when a source cannot be read.
    (String constants.)
    """

    MEASURED = "measured"
    UNAVAILABLE = "unavailable"
    ERROR = "error"

    _VALUES = frozenset({MEASURED, UNAVAILABLE, ERROR})


class GateStatus:
    """Outcome of a single quality/security gate (string constants)."""

    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"

    _VALUES = frozenset({PASSED, FAILED, SKIPPED, ERROR})


class MergeState:
    """Lifecycle of the reviewable artifact (string constants)."""

    NOT_CREATED = "not_created"
    PR_OPEN = "pr_open"
    PR_CLOSED_UNMERGED = "pr_closed_unmerged"
    MERGED = "merged"
    REVERTED = "reverted"

    _VALUES = frozenset({NOT_CREATED, PR_OPEN, PR_CLOSED_UNMERGED, MERGED, REVERTED})


class PostMergeOutcome:
    """Measured outcome over the defined post-merge window (string constants)."""

    PENDING = "pending"
    SUCCESS = "success"
    REGRESSION = "regression"
    ROLLBACK = "rollback"
    INCONCLUSIVE = "inconclusive"

    _VALUES = frozenset({PENDING, SUCCESS, REGRESSION, ROLLBACK, INCONCLUSIVE})


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise EvidenceValidationError(message)


def _require_non_empty(value: str, field_name: str) -> None:
    _require(isinstance(value, str) and bool(value.strip()), f"{field_name} must be non-empty")


def check_schema_version(version: str) -> str:
    """Validate that *version* is major-compatible with this contract.

    Returns the version unchanged so callers can validate at boundaries.
    Raises :class:`SchemaVersionError` on missing or incompatible major.
    """

    if not isinstance(version, str) or not version:
        raise SchemaVersionError("schema_version is required")
    major = version.split(".", 1)[0]
    if major != _SCHEMA_MAJOR:
        raise SchemaVersionError(
            f"unsupported schema major version: {version!r} "
            f"(this contract understands {EVIDENCE_SCHEMA_VERSION!r})"
        )
    return version


def canonical_json(payload: Mapping[str, Any]) -> str:
    """Serialize *payload* deterministically for hashing and replay.

    Implemented without importing ``json`` so this contract module stays
    within the SDK's dependency-light import budget.
    """

    def _render(value: Any) -> str:
        if value is None:
            return "null"
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, (int, float)):
            return repr(value)
        if isinstance(value, str):
            return '"' + _escape(value) + '"'
        if isinstance(value, Mapping):
            items = sorted(value.items(), key=lambda kv: str(kv[0]))
            return "{" + ",".join(f"{_render(str(k))}:{_render(v)}" for k, v in items) + "}"
        if isinstance(value, (list, tuple)):
            return "[" + ",".join(_render(v) for v in value) + "]"
        return _render(str(value))

    return _render(payload)


def _escape(text: str) -> str:
    """Escape a string for inclusion in canonical JSON."""

    out = []
    for ch in text:
        code = ord(ch)
        if ch == '"':
            out.append('\\"')
        elif ch == "\\":
            out.append("\\\\")
        elif code < 0x20:
            out.append(f"\\u{code:04x}")
        else:
            out.append(ch)
    return "".join(out)


def content_hash(payload: Mapping[str, Any]) -> str:
    """Return a deterministic 64-bit FNV-1a digest of the canonical payload.

    Suitable for idempotency keys inside a trust boundary; not a
    cryptographic hash.
    """

    data = canonical_json(payload).encode("utf-8")
    digest = 0xCBF29CE484222325
    for byte in data:
        digest ^= byte
        digest = (digest * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
    return f"{digest:016x}"


@dataclass(frozen=True, slots=True)
class SignalEvidence:
    """A measured health signal with provenance.

    ``availability`` distinguishes a real measurement from missing data;
    a signal that is not ``MEASURED`` must not be treated as healthy.
    """

    source: SignalSource
    kind: str  # e.g. "failing_test", "ci_job_failure"
    measured_at: str  # ISO-8601 UTC timestamp supplied by the collector
    availability: DataAvailability = DataAvailability.MEASURED
    summary: str = ""
    details: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        _require(self.source in SignalSource._VALUES, f"unknown signal source: {self.source!r}")
        _require_non_empty(self.kind, "signal.kind")
        _require_non_empty(self.measured_at, "signal.measured_at")
        _require(
            self.availability in DataAvailability._VALUES,
            f"unknown availability: {self.availability!r}",
        )


@dataclass(frozen=True, slots=True)
class PatternRef:
    """Reference to the evidence-backed pattern that produced a proposal."""

    pattern_id: str
    pattern_version: str
    success_rate: float

    def validate(self) -> None:
        _require_non_empty(self.pattern_id, "pattern.pattern_id")
        _require_non_empty(self.pattern_version, "pattern.pattern_version")
        _require(
            0.0 <= float(self.success_rate) <= 1.0,
            "pattern.success_rate must be within [0, 1]",
        )


@dataclass(frozen=True, slots=True)
class PatchProposal:
    """A bounded, reviewable change proposal."""

    patch_hash: str  # SHA-256 of the canonical patch content
    files: Tuple[str, ...]
    diff_lines: int
    description: str = ""

    def validate(self) -> None:
        _require_non_empty(self.patch_hash, "proposal.patch_hash")
        _require(bool(self.files), "proposal.files must name at least one file")
        _require(int(self.diff_lines) >= 0, "proposal.diff_lines must be >= 0")


@dataclass(frozen=True, slots=True)
class GateResult:
    """Result of one quality or security gate."""

    name: str
    status: GateStatus
    output_hash: Optional[str] = None
    details: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        _require_non_empty(self.name, "gate.name")
        _require(self.status in GateStatus._VALUES, f"unknown gate status: {self.status!r}")


@dataclass(frozen=True, slots=True)
class ExecutionEnvironment:
    """Where a proposal was executed (for replay/audit)."""

    runner: str  # e.g. "local-worktree", "container", "ci"
    python_version: str = ""
    env_hash: Optional[str] = None

    def validate(self) -> None:
        _require_non_empty(self.runner, "environment.runner")


@dataclass(frozen=True, slots=True)
class ImprovementEvent:
    """Versioned event: measured signal + matched pattern + proposal.

    ``event_id`` is the auditable idempotency key; identical inputs must
    produce the same ``event_id`` so retries never create duplicate work.
    """

    schema_version: str
    event_id: str
    repo: str
    ref: str
    sha: str
    signal: SignalEvidence
    recorded_at: str  # ISO-8601 UTC timestamp supplied by the recorder
    pattern: Optional[PatternRef] = None
    proposal: Optional[PatchProposal] = None

    def validate(self) -> None:
        check_schema_version(self.schema_version)
        _require_non_empty(self.event_id, "event_id")
        _require_non_empty(self.repo, "repo")
        _require_non_empty(self.ref, "ref")
        _require_non_empty(self.sha, "sha")
        _require_non_empty(self.recorded_at, "recorded_at")
        self.signal.validate()
        if self.pattern is not None:
            self.pattern.validate()
        if self.proposal is not None:
            self.proposal.validate()
        # A proposal without a backing pattern breaks traceability.
        _require(
            self.proposal is None or self.pattern is not None,
            "proposal requires a matched pattern",
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to a plain dict with enum values as strings."""

        return _event_payload(self)


@dataclass(frozen=True, slots=True)
class ImprovementResult:
    """Versioned result: gates, artifact, merge, outcome, confidence delta."""

    schema_version: str
    event_id: str
    environment: ExecutionEnvironment
    gates: Tuple[GateResult, ...] = ()
    merge_state: MergeState = MergeState.NOT_CREATED
    post_merge_outcome: PostMergeOutcome = PostMergeOutcome.PENDING
    pr_number: Optional[int] = None
    artifact_ids: Tuple[str, ...] = ()
    workflow_run_id: Optional[str] = None
    confidence_update: Optional[Mapping[str, Any]] = None

    def validate(self) -> None:
        check_schema_version(self.schema_version)
        _require_non_empty(self.event_id, "event_id")
        self.environment.validate()
        for gate in self.gates:
            gate.validate()
        _require(self.merge_state in MergeState._VALUES, f"unknown merge_state: {self.merge_state!r}")
        _require(
            self.post_merge_outcome in PostMergeOutcome._VALUES,
            f"unknown post_merge_outcome: {self.post_merge_outcome!r}",
        )
        # A PR number is required once an artifact has been opened.
        if self.merge_state in (MergeState.PR_OPEN, MergeState.MERGED, MergeState.REVERTED):
            _require(
                self.pr_number is not None,
                f"pr_number is required when merge_state={self.merge_state}",
            )
        # Confidence updates are only meaningful after a measured outcome.
        if self.confidence_update is not None:
            _require(
                self.merge_state == MergeState.MERGED
                and self.post_merge_outcome
                in (
                    PostMergeOutcome.SUCCESS,
                    PostMergeOutcome.REGRESSION,
                    PostMergeOutcome.ROLLBACK,
                ),
                "confidence_update requires a merged event with a measured post-merge outcome",
            )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to a plain dict with enum values as strings."""

        return _result_payload(self)


def make_event_id(
    repo: str,
    sha: str,
    signal: SignalEvidence,
    pattern: Optional[PatternRef],
    proposal: Optional[PatchProposal],
) -> str:
    """Derive a deterministic idempotency key from the event's identity."""

    proposal_target = None
    if proposal is not None:
        files = tuple(proposal.files or ())
        proposal_target = files[0] if len(files) == 1 else tuple(files)

    return content_hash(
        {
            "repo": repo,
            "sha": sha,
            "signal": {
                "source": signal.source,
                "kind": signal.kind,
                "measured_at": signal.measured_at,
                "summary": signal.summary,
            },
            "pattern_id": pattern.pattern_id if pattern else None,
            "proposal_target": proposal_target,
            "patch_hash": proposal.patch_hash if proposal else None,
        }
    )


def _signal_payload(signal: SignalEvidence) -> Dict[str, Any]:
    return asdict(signal)


def _event_payload(event: ImprovementEvent) -> Dict[str, Any]:
    return {
        "schema_version": event.schema_version,
        "event_id": event.event_id,
        "repo": event.repo,
        "ref": event.ref,
        "sha": event.sha,
        "recorded_at": event.recorded_at,
        "signal": _signal_payload(event.signal),
        "pattern": asdict(event.pattern) if event.pattern else None,
        "proposal": asdict(event.proposal) if event.proposal else None,
    }


def _result_payload(result: ImprovementResult) -> Dict[str, Any]:
    return {
        "schema_version": result.schema_version,
        "event_id": result.event_id,
        "environment": asdict(result.environment),
        "gates": [asdict(g) for g in result.gates],
        "merge_state": result.merge_state,
        "post_merge_outcome": result.post_merge_outcome,
        "pr_number": result.pr_number,
        "artifact_ids": list(result.artifact_ids),
        "workflow_run_id": result.workflow_run_id,
        "confidence_update": (
            dict(result.confidence_update) if result.confidence_update is not None else None
        ),
    }


def event_to_dict(event: ImprovementEvent) -> Dict[str, Any]:
    """Serialize an event after validating it (fail closed)."""

    event.validate()
    return event.to_dict()


def event_from_dict(data: Mapping[str, Any]) -> ImprovementEvent:
    """Deserialize and validate an event (fail closed on bad input)."""

    check_schema_version(str(data.get("schema_version", "")))
    signal_raw = data.get("signal") or {}
    signal = SignalEvidence(
        source=str(signal_raw.get("source", "")),
        kind=str(signal_raw.get("kind", "")),
        measured_at=str(signal_raw.get("measured_at", "")),
        availability=str(signal_raw.get("availability", "measured")),
        summary=str(signal_raw.get("summary", "")),
        details=dict(signal_raw.get("details") or {}),
    )
    pattern_raw = data.get("pattern")
    pattern = PatternRef(**pattern_raw) if pattern_raw else None
    proposal_raw = data.get("proposal")
    proposal = None
    if proposal_raw:
        proposal = PatchProposal(
            patch_hash=str(proposal_raw.get("patch_hash", "")),
            files=tuple(proposal_raw.get("files") or ()),
            diff_lines=int(proposal_raw.get("diff_lines", 0)),
            description=str(proposal_raw.get("description", "")),
        )
    event = ImprovementEvent(
        schema_version=str(data["schema_version"]),
        event_id=str(data.get("event_id", "")),
        repo=str(data.get("repo", "")),
        ref=str(data.get("ref", "")),
        sha=str(data.get("sha", "")),
        recorded_at=str(data.get("recorded_at", "")),
        signal=signal,
        pattern=pattern,
        proposal=proposal,
    )
    event.validate()
    return event


def result_to_dict(result: ImprovementResult) -> Dict[str, Any]:
    """Serialize a result after validating it (fail closed)."""

    result.validate()
    return result.to_dict()


def result_from_dict(data: Mapping[str, Any]) -> ImprovementResult:
    """Deserialize and validate a result (fail closed on bad input)."""

    check_schema_version(str(data.get("schema_version", "")))
    env_raw = data.get("environment") or {}
    environment = ExecutionEnvironment(
        runner=str(env_raw.get("runner", "")),
        python_version=str(env_raw.get("python_version", "")),
        env_hash=env_raw.get("env_hash"),
    )
    gates = tuple(
        GateResult(
            name=str(g.get("name", "")),
            status=str(g.get("status", "")),
            output_hash=g.get("output_hash"),
            details=dict(g.get("details") or {}),
        )
        for g in (data.get("gates") or ())
    )
    result = ImprovementResult(
        schema_version=str(data["schema_version"]),
        event_id=str(data.get("event_id", "")),
        environment=environment,
        gates=gates,
        merge_state=str(data.get("merge_state", "not_created")),
        post_merge_outcome=str(data.get("post_merge_outcome", "pending")),
        pr_number=data.get("pr_number"),
        artifact_ids=tuple(data.get("artifact_ids") or ()),
        workflow_run_id=data.get("workflow_run_id"),
        confidence_update=data.get("confidence_update"),
    )
    result.validate()
    return result
