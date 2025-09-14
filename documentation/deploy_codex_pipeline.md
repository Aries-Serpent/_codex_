# Deploy Codex Symbolic Pipeline

Run the deterministic symbolic training pipeline and verify reproducibility.

## Install

```bash
pip install -r requirements.txt
```

## Run

```bash
python deploy/deploy_codex_pipeline.py \
  --corpus data/corpus.jsonl \
  --demos data/demos.jsonl \
  --prefs data/prefs.jsonl \
  --output-dir runs/exp1
```

## Validate

```bash
pytest tests/test_deploy_codex_pipeline.py -q
```
