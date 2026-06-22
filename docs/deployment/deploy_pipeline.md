# Deploy Codex Symbolic Pipeline

**Last Updated:** 2026-06-22

Run the deterministic symbolic training pipeline and verify reproducibility across environments.

## Overview

The Codex symbolic pipeline trains a model using a corpus, preference data, and demonstration examples. The pipeline is fully deterministic: given identical inputs and a fixed random seed it produces bit-for-bit identical outputs.

## Prerequisites

```bash
pip install -r requirements/lock.txt
```

## Run

```bash
python deploy/deploy_codex_pipeline.py \
  --corpus data/corpus.jsonl \
  --demos data/demos.jsonl \
  --prefs data/prefs.jsonl \
  --output-dir runs/exp1
```

## Reproducibility Validation

After two independent runs, confirm canonical manifest equality:

```bash
pytest tests/test_deploy_codex_pipeline.py -q
python scripts/audit/build_integrity_chain.py
```

The audit chain hashes every output artifact and records them in `audit_artifacts/canonical_manifest.json`. Two runs producing identical manifests confirms full reproducibility.

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Non-deterministic outputs | Missing `--seed` flag | Add `--seed 42` |
| Missing corpus | Path error | Check `data/` exists |
| CUDA OOM | GPU memory | Use `--device cpu` |
