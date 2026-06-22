# AAIS V4.0 Scoring Framework

**Last Updated:** 2026-06-22

> **Status**: Draft | **Version**: 4.0.0-draft | **Date**: 2026-06-22

## Overview

AAIS V4.0 evolves the scoring model from V3's 3-axis composite (ACE + MSV + Agentic)
to a **4-pillar model** with 16 sub-dimensions. This provides finer-grained measurement
of AI agent capabilities and enables cross-repository comparison.

## Migration from V3.4

| Aspect | V3.4 | V4.0 |
|--------|------|------|
| Axes | 3 (ACE, MSV, Agentic) | 4 pillars, 16 sub-dimensions |
| Scale | 0–100 | 0–100 per dimension |
| Grade | A+ at 97.0 | S at 98.0, S+ at 99.0 |
| Scope | Single repo | Multi-repo capable |

**V3.4 baseline (97.0) maps to approximately V4.0 baseline (~82.0)** due to expanded criteria.

## 4-Pillar Model

### Pillar 1: Technical Excellence (25%)

| Sub-dimension | Weight | Description |
|---------------|--------|-------------|
| Code Quality | 7% | Lint score, type coverage, complexity metrics |
| Test Robustness | 6% | Coverage %, mutation score, fragile test ratio |
| CI/CD Maturity | 6% | Pipeline reliability, cache efficiency, build speed |
| Security Posture | 6% | Vulnerability count, SAST coverage, secret hygiene |

### Pillar 2: Cognitive Sophistication (30%)

| Sub-dimension | Weight | Description |
|---------------|--------|-------------|
| Self-Awareness | 8% | MSV accuracy, error correlation, context retention |
| Adaptive Learning | 8% | Cross-session KT, pattern library growth, regression prevention |
| Reasoning Depth | 7% | Multi-step planning, dependency analysis, impact assessment |
| Ethical Alignment | 7% | Imperative compliance, bias detection, safety guard coverage |

### Pillar 3: Operational Maturity (25%)

| Sub-dimension | Weight | Description |
|---------------|--------|-------------|
| Automation Coverage | 7% | Workflow count, manual intervention rate |
| Reliability | 6% | Uptime, MTTR, healing loop convergence rate |
| Observability | 6% | Metric coverage, alert accuracy, trend tracking |
| Scalability | 6% | Multi-repo support, concurrent task handling |

### Pillar 4: Ecosystem Impact (20%)

| Sub-dimension | Weight | Description |
|---------------|--------|-------------|
| Documentation Quality | 5% | Coverage %, freshness, link validity |
| Knowledge Sharing | 5% | Pattern library size, cross-team reuse |
| Community Alignment | 5% | Standards compliance, interoperability |
| Innovation Rate | 5% | New capability velocity, improvement cadence |

## Grading Scale

| Grade | Score Range | Description |
|-------|-----------|-------------|
| S+ | 99.0–100 | Exemplary — reference implementation |
| S | 98.0–98.9 | Superior — industry-leading practices |
| A+ | 95.0–97.9 | Excellent — comprehensive coverage |
| A | 90.0–94.9 | Strong — well-established practices |
| B+ | 85.0–89.9 | Good — solid foundation with gaps |
| B | 80.0–84.9 | Adequate — functional but improvable |
| C | 70.0–79.9 | Developing — significant gaps |

## Automated Scoring

Use `scripts/ci/aais_scoring_pipeline.py` for V3.x scoring.
V4.0 scoring pipeline will extend this with the 16 sub-dimension model.

## Roadmap

1. **V4.0-alpha**: Define all 16 sub-dimension measurement methods
2. **V4.0-beta**: Implement automated data collection for each dimension
3. **V4.0-rc**: Cross-repo normalization and comparison
4. **V4.0-ga**: Production scoring with historical trend tracking
