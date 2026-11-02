"""Python-only vertical slice: signal -> pattern -> bounded patch proposal.

This module demonstrates the first measurable link of the recursive
self-improvement loop without network access or credentials:

1. Ingest a measured health signal (e.g. a PDA failure record).
2. Retrieve an evidence-backed pattern via the lexical matcher in
   :class:`~aries_serpent_core.cognitive.brain_interface.AgentBrainInterface`.
3. Produce a bounded, reviewable :class:`PatchProposal` governed by the
   :class:`~codex.cognitive_brain.authority.AuthorityEnvelope`.

Every emitted event carries the SDK evidence contract and a deterministic
idempotency key so replays of the same input produce the same event.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence, cast

from codex.cognitive_brain.authority import AuthorityEnvelope

# The evidence contract ships in the codex-cognitive-sdk distribution; the
# source tree is used directly when running from a checkout.
try:
    from codex_cognitive_sdk.evidence import (
        EVIDENCE_SCHEMA_VERSION,
        DataAvailability,
        ImprovementEvent,
        PatchProposal,
        PatternRef,
        SignalEvidence,
        SignalSource,
        make_event_id,
    )
except ImportError:  # pragma: no cover - exercised only outside the repo
    _repo_root = Path(__file__).resolve().parents[3]
    _sdk_src = str(_repo_root / "packages" / "cognitive_sdk" / "src")
    if _sdk_src not in sys.path:
        sys.path.append(_sdk_src)
    from codex_cognitive_sdk.evidence import (
        EVIDENCE_SCHEMA_VERSION,
        DataAvailability,
        ImprovementEvent,
        PatchProposal,
        PatternRef,
        SignalEvidence,
        SignalSource,
        make_event_id,
    )

logger = logging.getLogger(__name__)

# Signals that can never produce an actionable proposal on their own.
_NON_ACTIONABLE_KINDS = frozenset({"heartbeat", "metric_sample", "info_event"})


@dataclass(frozen=True, slots=True)
class ProposalDecision:
    """Outcome of running the vertical slice on one signal."""

    event: ImprovementEvent
    actionable: bool
    reason: str = ""


def signal_from_pda_record(record: Mapping[str, Any]) -> SignalEvidence:
    """Build a measured signal from a ``pda_failure_logger`` failure record.

    Raises ``ValueError`` when the record is not a failure record so
    malformed evidence fails closed instead of being treated as healthy.
    """

    if not isinstance(record, Mapping):
        raise ValueError("PDA record must be an object")
    if record.get("type") != "failure":
        raise ValueError(f"expected a PDA failure record, got type={record.get('type')!r}")
    timestamp = record.get("timestamp")
    if not isinstance(timestamp, str) or not timestamp.strip():
        raise ValueError("PDA failure record requires a timestamp")
    try:
        measured = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("PDA failure timestamp is invalid") from exc
    if measured.tzinfo is None:
        raise ValueError("PDA failure timestamp must be timezone aware")
    files = record.get("files") or []
    if not isinstance(files, (list, tuple)) or any(
        not isinstance(path, str) or not path.strip() for path in files
    ):
        raise ValueError("PDA failure files must be a sequence of nonempty paths")
    details = {
        "pattern_id": record.get("pattern_id"),
        "workflow": record.get("workflow"),
        "workflow_run_id": record.get("workflow_run_id"),
        "error_text": record.get("error_text"),
        "root_cause": record.get("root_cause"),
        "fix_template": record.get("fix_template"),
        "verification_cmd": record.get("verification_cmd"),
        "files": list(files),
    }
    # The SDK annotates its string-constant containers as field types. Keep the
    # canonical wire strings unchanged while satisfying that annotation.
    return SignalEvidence(
        source=cast(SignalSource, SignalSource.PDA_FAILURE_LOG),
        kind="ci_job_failure",
        measured_at=timestamp,
        availability=cast(DataAvailability, DataAvailability.MEASURED),
        summary=str(record.get("root_cause") or record.get("error_text") or ""),
        details=details,
    )


class ImprovementPipeline:
    """Signal -> pattern -> bounded proposal, all in the Python control plane."""

    def __init__(
        self,
        *,
        repo: str,
        ref: str,
        sha: str,
        brain_interface: Any,
        authority: Optional[AuthorityEnvelope] = None,
        evidence_store: Any = None,
    ) -> None:
        self.repo = repo
        self.ref = ref
        self.sha = sha
        self.brain = brain_interface
        self.authority = authority or AuthorityEnvelope()
        self.evidence_store = evidence_store

    def process_signal(
        self,
        signal: SignalEvidence,
        *,
        human_approved: bool = False,
        patch_bytes: Optional[bytes] = None,
        patch_hash: Optional[str] = None,
        base_sha: Optional[str] = None,
    ) -> ProposalDecision:
        """Run one signal through retrieval and bounded proposal.

        Returns a :class:`ProposalDecision` whose event is always valid
        under the evidence contract; ``actionable`` is False (with a
        reason) for no-match, non-actionable, and policy-denied cases.
        """

        signal.validate()
        actual_proposal = None
        if any(value is not None for value in (patch_bytes, patch_hash, base_sha)):
            actual_proposal = self.proposal_from_patch(
                patch_bytes=patch_bytes, patch_hash=patch_hash, base_sha=base_sha
            )

        if signal.availability != DataAvailability.MEASURED:
            return self._inactionable(signal, f"signal not measured: {signal.availability}")
        if signal.kind in _NON_ACTIONABLE_KINDS:
            return self._inactionable(signal, f"non-actionable signal kind: {signal.kind}")

        symptoms = [signal.summary, *self._detail_terms(signal)]
        matches = self.brain.query_patterns(symptoms)
        if self.evidence_store is not None:
            matches = [
                match for match in matches if self.evidence_store.pattern_enabled(match.pattern_id)
            ]
        if not matches:
            return self._inactionable(signal, "no pattern matched the signal")

        best = matches[0]
        pattern_ref = PatternRef(
            pattern_id=best.pattern_id,
            pattern_version=str(best.times_applied),
            success_rate=float(best.success_rate),
        )

        proposal = actual_proposal or self._build_proposal(signal, best)
        if proposal is None:
            return self._inactionable(
                signal, "matched pattern carries no applicable fix", pattern_ref
            )

        decision = self.authority.evaluate(
            paths=proposal.files,
            diff_lines=proposal.diff_lines,
            human_approved=human_approved,
        )
        if not decision.authorized:
            return self._inactionable(
                signal, f"authority denied: {'; '.join(decision.reasons)}", pattern_ref, proposal
            )

        event = self._make_event(signal, pattern_ref, proposal)
        return ProposalDecision(event=event, actionable=True, reason="matched and authorized")

    def proposal_from_patch(
        self,
        *,
        patch_bytes: Optional[bytes],
        patch_hash: Optional[str],
        base_sha: Optional[str],
    ) -> PatchProposal:
        """Describe actual canonical UTF-8 diff bytes, never render template text.

        Git's read-only inventory and the existing executor's inventory parser
        define the same files/size at preparation and execution. Application
        against the immutable base is still verified only by the executor.
        """
        from codex.cognitive_brain.isolated_execution import IsolatedExecutor, scrub_environment

        if (
            not isinstance(patch_bytes, bytes)
            or not 0 < len(patch_bytes) <= 1024 * 1024
            or not patch_bytes.endswith(b"\n")
            or b"\r" in patch_bytes
            or b"\0" in patch_bytes
        ):
            raise ValueError("actual patch requires canonical UTF-8 LF diff bytes")
        if (
            not isinstance(base_sha, str)
            or re.fullmatch(r"[0-9a-f]{40}", base_sha) is None
            or base_sha != self.sha
        ):
            raise ValueError("actual patch base must match the pipeline immutable SHA")
        if hashlib.sha256(patch_bytes).hexdigest() != patch_hash:
            raise ValueError("actual patch hash mismatch")
        try:
            patch_bytes.decode("utf-8")
            with tempfile.TemporaryDirectory(prefix="codex-patch-inventory-") as directory:
                inventory = subprocess.run(
                    ["git", "apply", "--numstat", "-z", "-"],
                    input=patch_bytes,
                    cwd=directory,
                    capture_output=True,
                    env={
                        **scrub_environment(),
                        "GIT_CEILING_DIRECTORIES": str(Path(directory).parent),
                    },
                    timeout=30,
                    check=True,
                )
            files, lines = IsolatedExecutor._patch_inventory(inventory.stdout.decode("utf-8"))
        except (UnicodeError, OSError, subprocess.SubprocessError) as exc:
            raise ValueError("malformed actual patch") from exc
        if not files or not lines:
            raise ValueError("no-op patch is not an executable repair")
        return PatchProposal(
            patch_hash=patch_hash,
            files=tuple(sorted(files)),
            diff_lines=lines,
            description="Actual caller-supplied local diff; template is advisory only",
        )

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _detail_terms(self, signal: SignalEvidence) -> list[str]:
        terms: list[str] = []
        for key in ("error_text", "root_cause", "workflow"):
            value = signal.details.get(key)
            if value:
                terms.append(str(value))
        return terms

    def _build_proposal(self, signal: SignalEvidence, match: Any) -> Optional[PatchProposal]:
        """Render the pattern's fix template into a bounded proposal."""

        fix_template = str(signal.details.get("fix_template") or "")
        solutions = list(getattr(match, "solutions", []) or [])
        content = fix_template or (str(solutions[0]) if solutions else "")
        if not content.strip():
            return None

        patch_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        files = tuple(sorted(self._candidate_files(signal)))
        diff_lines = content.count("\n") + 1
        return PatchProposal(
            patch_hash=patch_hash,
            files=files,
            diff_lines=diff_lines,
            description=str(getattr(match, "pattern_id", "")),
        )

    @staticmethod
    def _candidate_files(signal: SignalEvidence) -> Sequence[str]:
        files = signal.details.get("files")
        if isinstance(files, (list, tuple)) and files:
            return [str(f) for f in files]
        workflow = signal.details.get("workflow")
        if workflow:
            return [f".github/workflows/{workflow}.yml"]
        return ["src/"]

    def _make_event(
        self,
        signal: SignalEvidence,
        pattern: Optional[PatternRef],
        proposal: Optional[PatchProposal],
    ) -> ImprovementEvent:
        event_id = make_event_id(self.repo, self.sha, signal, pattern, proposal)
        return ImprovementEvent(
            schema_version=EVIDENCE_SCHEMA_VERSION,
            event_id=event_id,
            repo=self.repo,
            ref=self.ref,
            sha=self.sha,
            signal=signal,
            recorded_at=datetime.now(timezone.utc).isoformat(),
            pattern=pattern,
            proposal=proposal,
        )

    def _inactionable(
        self,
        signal: SignalEvidence,
        reason: str,
        pattern: Optional[PatternRef] = None,
        proposal: Optional[PatchProposal] = None,
    ) -> ProposalDecision:
        return ProposalDecision(
            event=self._make_event(signal, pattern, proposal),
            actionable=False,
            reason=reason,
        )


def load_pda_signals(jsonl_path: Path) -> list[SignalEvidence]:
    """Load measured failure signals from a PDA failure-log JSONL file."""

    signals: list[SignalEvidence] = []
    with open(jsonl_path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            if not isinstance(record, Mapping):
                raise ValueError("PDA record must be an object")
            if record.get("type") != "failure":
                continue
            signals.append(signal_from_pda_record(record))
    return signals
