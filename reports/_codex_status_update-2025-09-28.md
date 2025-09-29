## Addendum — Metrics & Audits @ S1
- Generated `artifacts/metrics/loc_by_dir.csv`, `docstring_coverage.json`, `import_graph.json`, `cycles.json`.
- Docs/link audit: `artifacts/docs_link_audit/links.json`.
- Notebook load audit: `artifacts/notebook_checks/nb_load_check.json`.
- Tokenizer tests expanded to target project classes; SentencePiece tiny-model round-trip added.
- MLflow file-backend guard wired into `src/codex_ml/training/__init__.py`.

## How to run locally (offline by default)
```bash
python tools/metrics/generate_repo_metrics.py
nox -s metrics
nox -s tests -- tests/tokenization/test_sentencepiece_roundtrip.py -q
```
