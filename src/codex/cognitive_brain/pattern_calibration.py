"""Read-only, receipt-backed pattern diagnostics; never replace the legacy EMA.

The model is a Bernoulli rate with a uniform Beta(1, 1) prior, fitted on
SHA-256(event_id) % 5 != 0; the remaining events are held out. At least 20
training and 10 holdout events, and holdout Brier < 0.15, are required.
``calibrated`` is only a model diagnostic, NOT empirical assurance, causal
evidence, or authorization. The 95% equal-tail interval describes the training
posterior under the independent Bernoulli assumption, not deployment safety.

Only EvidenceStore-reconstructed production consumption receipts count. The
trusted-local-journal assumption of that store still applies. No verifier is
called, no learning occurs, and no files/locks are created. The older mutable
ConfidenceCalibrator is deliberately not instantiated: it silently ignores load
errors and writes naive timestamps. Its Brier formula is reproduced in stdlib.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Literal

from codex.cognitive_brain.evidence_store import EvidenceStore

MIN_TRAINING_SAMPLES = 20
MIN_HOLDOUT_SAMPLES = 10
BRIER_THRESHOLD = 0.15
MAX_EVIDENCE_AGE = timedelta(days=90)
CalibrationState = Literal["insufficient_samples", "holdout_overlap", "expired", "calibrated"]


@dataclass(frozen=True)
class PatternCalibration:
    """Immutable snapshot; posterior counts use training data only.

    ``sample_count`` counts deduplicated qualified events in both partitions.
    ``uncalibrated_ema`` is caller-supplied display context, never a forecast.
    Hashes commit to sorted event IDs in each partition, not evidence authenticity.
    Re-evaluate to observe expiry, new failures, or eligibility downgrades.
    """

    pattern_id: str
    state: CalibrationState
    reason: str
    sample_count: int
    training_count: int
    holdout_count: int
    alpha: int
    beta: int
    posterior_mean: float
    credible_interval: tuple[float, float]
    holdout_brier: float | None
    training_hash: str
    holdout_hash: str
    expires_at: datetime | None
    uncalibrated_ema: float | None
    diagnostic_only: bool = True


def event_partition(event_id: str) -> Literal["training", "holdout"]:
    """Stable event-level split; never split observations of one event."""
    digest = hashlib.sha256(event_id.encode("utf-8")).hexdigest()
    return "holdout" if int(digest, 16) % 5 == 0 else "training"


def _partition_hash(ids: list[str]) -> str:
    # Length framing avoids ambiguous joins for arbitrary event IDs.
    digest = hashlib.sha256()
    for event_id in sorted(ids):
        encoded = event_id.encode("utf-8")
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
    return digest.hexdigest()


def _beta_quantile(probability: float, alpha: int, beta: int) -> float:
    """Invert integer-shape Beta CDF via the binomial-tail identity.

    Log-space summation and bisection require only stdlib; no normal
    approximation is used, including for sparse/all-success observations.
    """
    n = alpha + beta - 1
    low, high = 0.0, 1.0
    for _ in range(64):
        x = (low + high) / 2
        terms = [
            math.lgamma(n + 1)
            - math.lgamma(k + 1)
            - math.lgamma(n - k + 1)
            + k * math.log(x)
            + (n - k) * math.log1p(-x)
            for k in range(alpha, n + 1)
        ]
        largest = max(terms)
        cdf = math.exp(largest) * math.fsum(math.exp(t - largest) for t in terms)
        if cdf < probability:
            low = x
        else:
            high = x
    return (low + high) / 2


def _aware(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("calibration timestamps must be timezone aware")
    return value.astimezone(timezone.utc)


def calibrate_pattern(
    store: EvidenceStore,
    pattern_id: str,
    *,
    now: datetime | None = None,
    uncalibrated_ema: float | None = None,
) -> PatternCalibration:
    """Reconstruct durable qualification, then compute a disposable diagnostic.

    Integrity/I/O errors propagate, never silently become empty evidence.
    Synthetic-mode stores are excluded entirely. Unknown production history or
    a disabled breaker blocks calibration. Provenance identity is
    (source, observation_id, merged_sha); aliases deduplicate within a partition
    and invalidate evaluation across partitions. Latest qualified measurement
    per event wins; ambiguous equal-time outcomes fail closed.
    """
    if not isinstance(store, EvidenceStore):
        raise TypeError("calibration requires an EvidenceStore")
    if not isinstance(pattern_id, str) or not pattern_id:
        raise ValueError("pattern_id must be nonempty")
    current = _aware(now if now is not None else datetime.now(timezone.utc))
    if uncalibrated_ema is not None and (
        not math.isfinite(uncalibrated_ema) or not 0 <= uncalibrated_ema <= 1
    ):
        raise ValueError("uncalibrated_ema must be finite and in [0, 1]")

    # A fresh concrete store avoids caller-mutated cached qualification flags.
    snapshot = EvidenceStore(store.path)
    trail = snapshot.audit_trail()
    # No public atomic qualification snapshot exists. Read only the state the
    # store just reconstructed, rather than duplicating its receipt validator.
    qualified = dict(snapshot._qualifications)
    breaker = snapshot._breakers.get(pattern_id)
    blocked = (
        store.allow_synthetic
        or pattern_id in snapshot._unknown_patterns
        or (breaker is not None and breaker.disabled)
    )
    reason = "production eligibility unconfirmed" if blocked else ""
    events: dict[str, tuple[datetime, bool, tuple[str, str, str]]] = {}
    if not blocked:
        for record in trail:
            if record["kind"] != "outcome":
                continue
            observation = record["payload"]
            if observation.get("pattern_id") != pattern_id:
                continue
            if qualified.get(snapshot.observation_key(observation)) != "production":
                continue
            provenance = observation.get("provenance", {})
            try:
                measured = _aware(
                    datetime.fromisoformat(provenance["measured_at"].replace("Z", "+00:00"))
                )
                source = provenance["source"]
                observation_id = observation["observation_id"]
                merged_sha = observation["merged_sha"]
                if not all(
                    isinstance(value, str) and value.strip()
                    for value in (source, observation_id, merged_sha)
                ):
                    raise ValueError("missing provenance identity")
                if measured > current:
                    raise ValueError("future measurement")
            except (KeyError, TypeError, AttributeError, ValueError):
                reason = "qualified receipt has unusable provenance"
                events.clear()
                break
            event_id = observation["event_id"]
            sample = (
                measured,
                observation["outcome"] == "success",
                (source, observation_id, merged_sha),
            )
            previous = events.get(event_id)
            if previous and previous[0] == measured and previous != sample:
                reason = "ambiguous simultaneous event measurements"
                events.clear()
                break
            if previous is None or measured > previous[0]:
                events[event_id] = sample

    training: list[str] = []
    holdout: list[str] = []
    identities: dict[tuple[str, str, str], tuple[str, bool]] = {}
    state: CalibrationState = "insufficient_samples"
    for event_id in sorted(events):
        _, success, identity = events[event_id]
        partition = event_partition(event_id)
        previous_identity = identities.get(identity)
        if previous_identity is not None:
            if previous_identity[0] != partition:
                state, reason = "holdout_overlap", "provenance reused across partitions"
                break
            if previous_identity[1] != success:
                reason = "conflicting outcomes for reused provenance"
                training.clear()
                holdout.clear()
                break
            continue
        identities[identity] = (partition, success)
        (training if partition == "training" else holdout).append(event_id)

    successes = sum(events[event_id][1] for event_id in training)
    alpha, beta = 1 + successes, 1 + len(training) - successes
    mean = alpha / (alpha + beta)
    brier = (
        math.fsum((mean - events[event_id][1]) ** 2 for event_id in holdout) / len(holdout)
        if holdout
        else None
    )
    selected = training + holdout
    expires = (
        min(events[event_id][0] for event_id in selected) + MAX_EVIDENCE_AGE if selected else None
    )
    if state != "holdout_overlap" and not reason:
        if expires is not None and current >= expires:
            state, reason = "expired", "selected evidence is at least 90 days old"
        elif len(training) < MIN_TRAINING_SAMPLES or len(holdout) < MIN_HOLDOUT_SAMPLES:
            reason = "requires at least 20 training and 10 holdout events"
        elif brier is not None and brier < BRIER_THRESHOLD:
            state, reason = "calibrated", "model diagnostic only; not empirical assurance"
        else:
            reason = "holdout Brier must be below 0.15"
    return PatternCalibration(
        pattern_id=pattern_id,
        state=state,
        reason=reason,
        sample_count=len(selected),
        training_count=len(training),
        holdout_count=len(holdout),
        alpha=alpha,
        beta=beta,
        posterior_mean=mean,
        credible_interval=(_beta_quantile(0.025, alpha, beta), _beta_quantile(0.975, alpha, beta)),
        holdout_brier=brier,
        training_hash=_partition_hash(training),
        holdout_hash=_partition_hash(holdout),
        expires_at=expires,
        uncalibrated_ema=uncalibrated_ema,
    )
