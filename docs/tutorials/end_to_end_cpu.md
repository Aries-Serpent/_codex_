<!-- BEGIN: CODEX_DOCS_TUTORIALS_END_TO_END -->

# End-to-End CPU Training

**Last Updated:** 2026-06-22

Train, evaluate, and inspect a full Codex symbolic pipeline on CPU — no GPU or cloud required.

## Prerequisites

```bash
pip install -e ".[dev]"
```

## 1 — Prepare data

```bash
# Small sample datasets are included in data/
ls data/
# corpus.jsonl   demos.jsonl   prefs.jsonl
```

## 2 — Run the pipeline

```bash
python deploy/deploy_codex_pipeline.py \
  --corpus  data/corpus.jsonl \
  --demos   data/demos.jsonl \
  --prefs   data/prefs.jsonl \
  --output-dir runs/cpu_test
```

This executes three stages in sequence:

| Stage | Script section | Output |
|-------|---------------|--------|
| Pretraining | `pretrain()` | `runs/cpu_test/M0/` |
| SFT | `sft()` | `runs/cpu_test/M1/` |
| RLHF | `rlhf()` | `runs/cpu_test/M2/` |

## 3 — Evaluate

```bash
pytest tests/test_deploy_codex_pipeline.py -v
```

Expected: all assertions pass, reproducible outputs (seed=0).

## 4 — Inspect checkpoints

```bash
ls runs/cpu_test/
# M0/  M1/  M2/  metrics.json

python -c "import json; print(json.load(open('runs/cpu_test/metrics.json')))"
```

## 5 — Containerised run

```bash
docker compose run --rm trainer \
  python deploy/deploy_codex_pipeline.py \
    --corpus /data/corpus.jsonl \
    --output-dir /runs/exp1
```

Artifacts are written to the mounted volume at `/runs/`.

## Related guides

- [Deploy Pipeline reference](../deployment/deploy_pipeline.md)
- [Symbolic Training architecture](../training/symbolic_training.md)
- [Checkpointing](../guides/checkpointing.md)
