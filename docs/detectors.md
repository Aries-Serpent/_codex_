# Detectors Overview
**Last Updated:** 2026-07-11
**Version:** v0.2.1

**Last Updated: 2026-06-22

Small, pluggable checks that emit findings and a bounded [0..1] score.
- Each detector returns: `{"name": str, "score": float, "details": dict}`
- Aggregator computes weighted mean + merges findings.

CLI:
```bash
python -m codex_ml.cli.detectors run
```text
