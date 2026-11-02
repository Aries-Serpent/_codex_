"""Recovery boundary for cooperating maintained AgentBrainInterface writers.

Only ``submit_pattern``, ``submit_learning``/``_update_pattern_stats``,
``_save_patterns`` and the full ``OutcomeTracker`` learning sequence participate.
Filesystem edits, other implementations and
older SDK processes are not excluded. The operator must explicitly attest that
this limited writer coverage fits the deployment; otherwise recovery is denied.
No pattern statistic is an observation-specific consumption receipt.
"""

from __future__ import annotations

import hashlib
import json
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Iterator

from codex.cognitive_brain.learning_reconciliation import (
    DecisionVerifier,
    ExternalSnapshot,
    LearningRecovery,
    pattern_store_lock,
)

if TYPE_CHECKING:
    from codex.cognitive_brain.evidence_store import EvidenceStore


class MaintainedWriterRecovery:
    """Inject trusted policy, consumption and measurement verifiers explicitly.

    Construction does no I/O. Inspection, denial and dry-run never create stores,
    directories or lock files. Missing/unreadable/malformed stores fail closed.
    Callbacks receive the evidence store's observation/decision-specific input;
    their absence never falls back to aggregate pattern statistics.
    """

    def __init__(
        self,
        pattern_store_path: Path,
        *,
        policy_verifier: DecisionVerifier | None = None,
        consumption_verifier: DecisionVerifier | None = None,
        measurement_verifier: DecisionVerifier | None = None,
        participating_writers_only: bool = False,
    ) -> None:
        self.path = Path(pattern_store_path)
        self.policy_verifier = policy_verifier
        self.consumption_verifier = consumption_verifier
        self.measurement_verifier = measurement_verifier
        self.participating_writers_only = participating_writers_only

    def _identity(self) -> str:
        raw = self.path.read_bytes()
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError("pattern store must be an object")
        patterns = data.get("patterns", {})
        if not isinstance(patterns, dict) or any(
            not isinstance(pattern, dict) for pattern in patterns.values()
        ):
            raise ValueError("pattern store patterns must be objects")
        for key in ("metadata", "statistics"):
            if key in data and not isinstance(data[key], dict):
                raise ValueError(f"pattern store {key} must be an object")
        location = str(self.path.resolve(strict=True)).encode()
        return hashlib.sha256(location + b"\0" + raw).hexdigest()

    @contextmanager
    def snapshot(self) -> Iterator[ExternalSnapshot]:
        """Hold external exclusion before the caller acquires the journal lock."""
        if self.participating_writers_only is not True:
            raise ValueError("complete maintained-writer coverage must be explicitly confirmed")
        with pattern_store_lock(self.path):
            yield ExternalSnapshot(self._identity(), self._identity)

    def inspect(self, store: EvidenceStore) -> list[LearningRecovery]:
        return store.inspect_learning(self.snapshot)

    def reconcile(
        self,
        store: EvidenceStore,
        identity: LearningRecovery,
        disposition: str,
        *,
        dry_run: bool = True,
    ) -> bool:
        return store.reconcile_learning(
            identity,
            disposition,
            snapshot_reader=self.snapshot,
            policy_verifier=self.policy_verifier,
            consumption_verifier=self.consumption_verifier,
            # Do not inherit an ambient store verifier at this explicit boundary.
            measurement_verifier=self.measurement_verifier or (lambda _: False),
            dry_run=dry_run,
        )
