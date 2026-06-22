# ADR-003: Event-Driven Continuous Learning via Drift → Trigger → EvalGate → Promote

**Last Updated:** 2026-06-22

**Status:** Accepted
**Date:** 2025-01-15
**Deciders:** codex-ml platform team
**Technical Story:** Gap 36/38/39 — continuous learning pipeline, automated retraining, feedback loop

---

## Context

ML models in production decay over time due to concept drift and data drift.
Without automated lifecycle management, quality degradation is invisible until
a human investigates a business metric anomaly — often days or weeks after the
root cause began.

The _codex_ platform required an automated model lifecycle system with the
following constraints:

1. **Trigger on evidence, not on schedule** — retraining should fire when drift
   signals exceed thresholds, not on a fixed calendar interval. This avoids both
   premature retraining (wasted compute) and delayed retraining (prolonged
   quality loss).
2. **Safety gate before promotion** — an automatically retrained model must meet
   quality thresholds before it replaces the production model. Blind auto-promotion
   is not acceptable.
3. **Loose coupling between stages** — each stage (drift monitoring, retraining,
   evaluation, promotion) must be independently replaceable without refactoring
   adjacent stages.
4. **Feedback from production** — production inference outcomes should flow back
   into the learning loop, not be discarded after the prediction is served.
5. **CI/CD integration** — the system must be operable via GitHub Actions
   `repository_dispatch` events so the full pipeline can be triggered, monitored,
   and audited within the existing CI infrastructure.

---

## Decision

We adopt a **four-stage event-driven pipeline** with an OODA-inspired feedback
overlay:

### Stage 1: Drift Detection (Observe)

`DriftMonitor` (ADR-001) continuously computes PSI / KL-div / JSD over a rolling
window. When any metric crosses its threshold, it emits a structured drift event:

```json
{ "type": "drift", "metric": "psi", "feature": "age_bucket", "value": 0.23 }
```

### Stage 2: RetrainingTrigger (Orient)

`RetrainingTrigger` subscribes to drift events and applies debounce logic:
- Multiple drift events within a configurable cooldown window are collapsed into
  a single retraining job, preventing repeated triggering during a transient
  distribution shift.
- Emits a `retrain_requested` event with the triggering evidence attached for
  audit logging.
- Can also be invoked programmatically (e.g., from a CI cron job or operator
  command) to support scheduled and manual retraining alongside event-driven.

### Stage 3: AutoRetrainPipeline + EvalGate (Decide)

`AutoRetrainPipeline` executes the full training workflow against the latest
available data, producing a candidate model artefact.

`EvalGate` applies a configurable quality threshold comparison:

```python
gate_pass = (
    candidate.accuracy >= production.accuracy - tolerance
    and candidate.f1 >= min_f1
    and candidate.latency_p99 <= max_latency_ms
)
```

If the gate fails, the candidate is archived with its evaluation report but
not promoted. The pipeline emits a `gate_failed` event so on-call engineers
are notified.

### Stage 4: Conditional Promotion (Act)

`ModelPromoter` triggers on `gate_passed` events and executes the promotion
sequence: update model registry pointer, warm up serving cache, emit
`model_promoted` event.

The `repository_dispatch` GitHub Actions event bridges the monitoring runtime
into CI: a `model_promoted` event fires `repository_dispatch` with the new
model version, triggering downstream smoke tests and canary deployment.

### Feedback Loop (OODA Overlay)

`FeedbackLoop` collects production inference outcomes (labels collected via
user interaction, downstream system signals, or delayed ground truth) and feeds
them back into the data pipeline used by `AutoRetrainPipeline`. This implements
the **Observe** and **Orient** phases of the OODA loop at the data level, not
just at the trigger level.

---

## Consequences

**Positive:**
- Decoupled stages: replacing the retraining framework (e.g., switching from
  scikit-learn to PyTorch Lightning) requires changes only to `AutoRetrainPipeline`,
  not to `DriftMonitor`, `EvalGate`, or `ModelPromoter`.
- `EvalGate` prevents regressions from reaching production; no human approval
  required for routine retraining, but automated safety is maintained.
- `repository_dispatch` provides a standards-compliant integration point that
  works with any CI system supporting GitHub webhooks.
- Feedback loop closes the production-training gap without requiring a separate
  online learning infrastructure.

**Negative / Trade-offs:**
- Event-driven systems are harder to trace than synchronous pipelines; distributed
  tracing (ADR-0001) is recommended to correlate drift event → retrain job → gate
  result → promotion.
- `EvalGate` thresholds must be calibrated per model family; a single global
  threshold will be either too strict (blocking valid retrains) or too loose
  (promoting degraded models) for heterogeneous model types.
- Feedback loop introduces a data-flywheel dependency: if production labels are
  noisy or delayed, the retrained model may regress. Label quality monitoring is
  a prerequisite for reliable continuous learning.

---

## Alternatives Considered

| Alternative | Reason Rejected |
|---|---|
| **Time-based retraining schedule (nightly/weekly)** | Does not respond to sudden distribution shifts; may retrain unnecessarily when the model is stable, wasting compute and introducing gratuitous version churn. |
| **Manual promotion only** | Does not scale; requires on-call engineer attention for every retraining cycle; defeats the purpose of automated monitoring. |
| **Online/incremental learning** | Requires the model architecture to support incremental updates (e.g., SGD with warm-start); most deployed _codex_ models are batch-trained. Online learning also complicates rollback. |
| **Shadow deployment with traffic split** | Valuable as a complementary canary strategy but does not replace the evaluation gate; both can coexist in a future iteration. |
