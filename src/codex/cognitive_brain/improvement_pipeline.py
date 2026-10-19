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
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from codex.cognitive_brain.authority import AuthorityEnvelope

# The evidence contract ships in the codex-cognitive-sdk distribution; the
# source tree is used directly when running from a checkout.
try:
    from codex_cognitive_sdk.evidence import (
        EVIDENCE_SCHEMA_VERSION,
        DataAvailability,
        ImprovementEvent,
        PatternRef,
        PatchProposal,
        SignalEvidence,
        SignalSource,
        make_event_id,
    )
except ImportError:  # pragma: no cover - exercised only outside the repo
    _sdk_src = str(Path(__file__).resolve().parents[4] / "packages" / "cognitive_sdk" / "src")
    if _sdk_src not in sys.path:
        sys.path.append(_sdk_src)
    from codex_cognitive_sdk.evidence import (  # type: ignore[no-redef]
        EVIDENCE_SCHEMA_VERSION,
        DataAvailability,
        ImprovementEvent,
        PatternRef,
        PatchProposal,
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

    if record.get("type") != "failure":
        raise ValueError(f"expected a PDA failure record, got type={record.get('type')!r}")
    timestamp = str(record.get("timestamp", ""))
    if not timestamp:
        raise ValueError("PDA failure record is missing its timestamp")
    details = {
        "pattern_id": record.get("pattern_id"),
        "workflow": record.get("workflow"),
        "workflow_run_id": record.get("workflow_run_id"),
        "error_text": record.get("error_text"),
        "root_cause": record.get("root_cause"),
        "fix_template": record.get("fix_template"),
        "verification_cmd": record.get("verification_cmd"),
        "files": list(record.get("files") or []),
    }
    return SignalEvidence(
        source=SignalSource.PDA_FAILURE_LOG,
        kind="ci_job_failure",
        measured_at=timestamp,
        availability=DataAvailability.MEASURED,
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
    ) -> None:
        self.repo = repo
        self.ref = ref
        self.sha = sha
        self.brain = brain_interface
        self.authority = authority or AuthorityEnvelope()

    def process_signal(
        self,
        signal: SignalEvidence,
        *,
        human_approved: bool = False,
    ) -> ProposalDecision:
        """Run one signal through retrieval and bounded proposal.

        Returns a :class:`ProposalDecision` whose event is always valid
        under the evidence contract; ``actionable`` is False (with a
        reason) for no-match, non-actionable, and policy-denied cases.
        """

        signal.validate()

        if signal.availability is not DataAvailability.MEASURED:
            return self._inactionable(signal, f"signal not measured: {signal.availability.value}")
        if signal.kind in _NON_ACTIONABLE_KINDS:
            return self._inactionable(signal, f"non-actionable signal kind: {signal.kind}")

        symptoms = [signal.summary, signal.kind.replace("_", " "), *self._detail_terms(signal)]
        matches = self.brain.query_patterns(symptoms)
        if not matches:
            return self._inactionable(signal, "no pattern matched the signal")

        best = matches[0]
        pattern_ref = PatternRef(
            pattern_id=best.pattern_id,
            pattern_version=str(best.times_applied),
            success_rate=float(best.success_rate),
        )

        proposal = self._build_proposal(signal, best)
        if proposal is None:
            return self._inactionable(signal, "matched pattern carries no applicable fix", pattern_ref)

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
            if record.get("type") != "failure":
                continue
            signals.append(signal_from_pda_record(record))
    return signals
