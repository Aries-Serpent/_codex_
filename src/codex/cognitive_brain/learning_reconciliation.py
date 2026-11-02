"""Read-only recovery identities, not credentials or evidence of consumption.

An injected snapshot context must yield an ExternalSnapshot of a present,
readable external store and exclude *all* external writers until it exits. Acquire it
before the evidence transaction, matching the tracker's external->journal order.
The tracker lock alone excludes tracker writers, not arbitrary SDK writers.
Neither a pattern's rate nor its application count proves which observation was
consumed. Independent consumption verification must consult a trusted receipt.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Callable, ContextManager, Mapping

DecisionVerifier = Callable[[Mapping[str, Any]], bool]


@dataclass(frozen=True)
class ExternalSnapshot:
    """Non-secret identity and a fresh read of that identity under the held lock.

    ``recheck`` must freshly read the same present, readable store, raising on
    missing/unreadable data, not return a cached identity. The caller supplies
    the locking protocol: this class cannot exclude arbitrary SDK writers.
    """

    identity: str
    recheck: Callable[[], str]


SnapshotReader = Callable[[], ContextManager[ExternalSnapshot]]


@dataclass(frozen=True)
class LearningRecovery:
    """Exact persisted identity plus the two snapshots inspected by the operator."""

    observation_key: str
    observation_id: str | None
    event_id: str
    pattern_id: str | None
    patch_hash: str | None
    merged_sha: str | None
    outcome: str
    attempt_id: str | None
    attempt_ids: tuple[str, ...]
    observation_hash: str
    state: str
    journal_sha256: str
    external_snapshot: str

    def as_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["attempt_ids"] = list(self.attempt_ids)
        return result
