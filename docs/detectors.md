# Detectors Overview

Small, pluggable checks that emit findings and a bounded [0..1] score.
- Each detector returns: `{"name": str, "score": float, "details": dict}`
- Aggregator computes weighted mean + merges findings.

CLI:
```bash
python -m codex_ml.cli.detectors run
```
