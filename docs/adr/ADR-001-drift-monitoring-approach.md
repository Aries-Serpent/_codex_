# ADR-001: Use PSI + KL-Divergence for Data Drift, JSD for Model Drift

**Status:** Accepted
**Date:** 2025-01-15
**Deciders:** codex-ml platform team
**Technical Story:** Gap 17/18 — data and model drift monitoring implementation

---

## Context

Production ML models degrade silently when the statistical distribution of incoming
features or output probabilities shifts away from the training distribution. Without
automated detection, degraded model quality is only discovered after measurable
business harm — delayed fraud detections, wrong recommendations, or mislabelled
classifications.

The _codex_ platform needed a drift-monitoring subsystem with the following
non-negotiable properties:

1. **Feature drift** — detect when input feature distributions have shifted relative
   to a reference window (typically the training dataset).
2. **Model output drift** — detect when the model's predicted probability distributions
   have shifted, signalling potential concept drift even when feature distributions
   remain stable.
3. **Operational simplicity** — thresholds must be human-interpretable and map cleanly
   onto alerting rules without requiring statistical expertise to tune.
4. **Graceful degradation** — the monitoring module must remain importable and
   functionally no-op when the optional `prometheus-client` package is absent, so
   monitoring never blocks model serving.

Several divergence metrics exist; the decision required selecting the right one
for each use-case rather than applying a single metric everywhere.

---

## Decision

We adopt a **three-metric strategy** aligned to the statistical properties of each
drift signal type:

### 1. Population Stability Index (PSI) — categorical and binned continuous features

PSI is computed as:

```
PSI = Σ (actual_i − expected_i) × ln(actual_i / expected_i)
```

PSI was selected for feature drift because:
- Industry-standard thresholds are well understood: < 0.1 stable, 0.1–0.2 moderate
  shift, > 0.2 significant shift requiring investigation.
- Naturally handles binned continuous and categorical data, which make up the
  majority of _codex_ feature columns.
- Symmetric enough for monitoring purposes while remaining computationally cheap.

### 2. KL-Divergence — continuous unbinned distributions

For continuous feature streams where binning would introduce quantisation error,
KL-divergence (relative entropy) is used:

```
KL(P || Q) = Σ P(x) × ln(P(x) / Q(x))
```

KL-div is well-suited to continuous distributions and directly measures information
loss when using Q to approximate P.

### 3. Jensen-Shannon Divergence (JSD) — model output probability vectors

JSD is the **symmetric** version of KL-divergence:

```
JSD(P || Q) = ½ KL(P || M) + ½ KL(Q || M)   where M = ½(P + Q)
```

JSD was chosen for model output distributions because:
- Model predictions are probability vectors that do not have a natural asymmetric
  reference direction (unlike feature vs. training-window comparison).
- JSD is bounded in [0, 1] when computed with log₂, making threshold selection
  straightforward.
- JSD is the natural metric for comparing probability distributions in information
  theory and maps cleanly to the KL infrastructure already present.

### 4. Prometheus counter fallback (`NoopModCounter`)

A lightweight `NoopModCounter` stub is registered at import time so that all
counter increment calls succeed silently when `prometheus-client` is not installed.
This ensures the drift monitor module never raises `ImportError` in environments
that do not expose a Prometheus scrape endpoint.

---

## Consequences

**Positive:**
- Each metric is chosen for its mathematical fit to the data type it monitors,
  avoiding the "one size fits all" mistake.
- PSI threshold of 0.2 is an industry convention that maps directly to alerting
  rules without per-dataset calibration.
- JSD ∈ [0, 1] simplifies cross-model comparison of drift severity.
- Prometheus dependency is optional; the module is importable in any environment.

**Negative / Trade-offs:**
- Three metrics require three separate threshold configurations. Operators must
  understand which threshold applies to which signal.
- PSI requires binning, which introduces a hyperparameter (number of bins). The
  current implementation defaults to 10 bins; this may need tuning for heavy-tailed
  distributions.
- KL-divergence is asymmetric; if reference and current windows are accidentally
  swapped, drift direction is inverted.

---

## Alternatives Considered

| Alternative | Reason Rejected |
|---|---|
| **Kolmogorov-Smirnov (KS) test** | KS is a hypothesis test, not a divergence metric; it produces a p-value rather than a scalar drift magnitude, making threshold-based alerting less intuitive. |
| **Wasserstein distance (Earth Mover's Distance)** | More computationally expensive (O(n log n) sorting) for continuous distributions; better for image or high-dimensional embedding drift where exact optimal-transport is needed. |
| **Maximum Mean Discrepancy (MMD)** | Requires kernel selection (RBF, polynomial) which adds a hyperparameter that is hard to tune without domain knowledge; also more expensive to compute online. |
| **Single metric for all signals** | Using PSI alone for model output distributions loses the symmetry property needed; using JSD alone for features loses the industry-standard threshold convention. |
