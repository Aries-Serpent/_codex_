# Detectors Overview

Library detectors (planned) will expose checks for unified training, checkpoint
schema/digest, and env posture. Scripts should be thin wrappers over library code.

## CLI Usage

Run the bundled detectors and print a JSON scorecard:

```bash
python -m codex_ml.cli.detectors run
```

With a manifest and custom weights:

```bash
python -m codex_ml.cli.detectors run --manifest artifacts/manifest.json \
  --weight unified_training=2.0 --out reports/scorecard.json
```
